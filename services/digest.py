from __future__ import annotations

import calendar
import hashlib
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from html import unescape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import feedparser

from company_profiles import CompanyProfile
from services import llm as llm_service

log = logging.getLogger("seo_app.digest")

RSS_SOURCES: Dict[str, List[str]] = {
    "news": [
        "https://forklog.com/feed",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://www.theblockcrypto.com/rss.xml",
        "https://incrypted.com/feed/",
    ],
    "social": [
        "https://nitter.net/WatcherGuru/rss",
        "https://nitter.net/rektcapital/rss",
        "https://nitter.net/gagarin_crypto/rss",
        "https://nitter.net/itangooz/rss",
        "https://nitter.net/minkov_crypto/rss",
    ],
}

DIGEST_LOG_PATH = Path("logs/daily_digests.jsonl")
GMT3 = timezone(timedelta(hours=3))


@dataclass
class DigestWindow:
    start_local: datetime
    end_local: datetime

    @property
    def start_utc(self) -> datetime:
        return self.start_local.astimezone(timezone.utc)

    @property
    def end_utc(self) -> datetime:
        return self.end_local.astimezone(timezone.utc)

    @property
    def label(self) -> str:
        start_str = self.start_local.strftime("%d %b %Y, %H:%M")
        end_str = (self.end_local - timedelta(minutes=1)).strftime("%d %b %Y, %H:%M")
        return f"{start_str} – {end_str} (GMT+3)"


def compute_digest_window(now: Optional[datetime] = None) -> DigestWindow:
    now_local = (now or datetime.now(timezone.utc)).astimezone(GMT3)
    target_date = now_local.date() - timedelta(days=1)
    start_local = datetime.combine(target_date, time(4, 0), tzinfo=GMT3)
    end_local = start_local + timedelta(days=1)
    return DigestWindow(start_local=start_local, end_local=end_local)


def _normalize_summary(text: str) -> str:
    decoded = unescape(text or "")
    cleaned = re.sub(r"<[^>]+>", " ", decoded)
    return re.sub(r"\s+", " ", cleaned).strip()


def _entry_datetime(entry: Any) -> Optional[datetime]:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        struct = entry.get(key)
        if struct:
            timestamp = calendar.timegm(struct)
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return None


def fetch_articles_for_window(window: DigestWindow, max_items_per_feed: int = 25) -> List[Dict[str, str]]:
    articles: List[Dict[str, str]] = []
    seen_links: set[str] = set()

    for category, feed_urls in RSS_SOURCES.items():
        for url in feed_urls:

            try:
                feed = feedparser.parse(url)
            except Exception as exc:  # pragma: no cover - defensive
                log.warning("RSS fetch failed (%s): %s", url, exc)
                continue

            feed_title = getattr(feed.feed, "title", None) or url
            entries = getattr(feed, "entries", [])[:max_items_per_feed]

            for entry in entries:
                dt = _entry_datetime(entry)
                if dt is None:
                    continue
                if not (window.start_utc <= dt < window.end_utc):
                    continue

                link = entry.get("link") or entry.get("id") or ""
                if not link or link in seen_links:
                    continue
                seen_links.add(link)

                title = entry.get("title", "Без названия")
                summary = _normalize_summary(entry.get("summary", ""))
                local_dt = dt.astimezone(GMT3)

                articles.append(
                    {
                        "category": category,
                        "source": feed_title,
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "published": local_dt.strftime("%Y-%m-%d %H:%M"),
                        "published_iso": dt.isoformat(),
                    }
                )

    articles.sort(key=lambda item: item["published_iso"], reverse=True)
    return articles


def _ensure_log_path() -> None:
    DIGEST_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_digest_logs() -> List[Dict[str, Any]]:
    if not DIGEST_LOG_PATH.exists():
        return []
    entries: List[Dict[str, Any]] = []
    with DIGEST_LOG_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                log.warning("Skipping corrupt digest log line.")
    return entries


def _save_digest_log(entry: Dict[str, Any]) -> None:
    _ensure_log_path()
    with DIGEST_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False))
        fh.write("\n")


def _signature_from_links(links: Iterable[str]) -> str:
    payload = "|".join(sorted(set(links)))
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def _recent_digest_notes(logs: List[Dict[str, Any]], *, limit: int = 2) -> str:
    snippets = []
    for entry in logs[-limit:]:
        digest = entry.get("digest", "")
        if digest:
            snippets.append(digest.strip().splitlines()[0][:200])
    return " | ".join(snippets)


def generate_daily_digest(
    profile: CompanyProfile,
    now: Optional[datetime] = None,
) -> Tuple[str, Dict[str, Any]]:
    window = compute_digest_window(now)
    articles = fetch_articles_for_window(window)
    links = [a["link"] for a in articles]
    signature = _signature_from_links(links)

    logs = _load_digest_logs()
    recent_signatures = {entry.get("signature") for entry in logs[-2:]}
    if signature and signature in recent_signatures:
        raise ValueError("🚫 Дайджест с идентичным набором ссылок уже выпускался в последние два дня.")

    recent_notes = _recent_digest_notes(logs, limit=2)

    metadata = {
        "window_start": window.start_local.isoformat(),
        "window_end": window.end_local.isoformat(),
        "window_label": window.label,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "signature": signature,
        "article_count": len(articles),
        "links": links,
    }

    if not articles:
        return (
            "⚠️ За выбранный период не найдено свежих новостей. Проверьте позже.",
            {**metadata, "articles": []},
        )

    digest_text = llm_service.generate_daily_digest(
        articles=articles,
        window_label=window.label,
        profile=profile,
        recent_digest_notes=recent_notes,
    )

    _save_digest_log({**metadata, "digest": digest_text})
    return digest_text, {**metadata, "articles": articles}


__all__ = [
    "RSS_SOURCES",
    "DigestWindow",
    "compute_digest_window",
    "fetch_articles_for_window",
    "generate_daily_digest",
]
