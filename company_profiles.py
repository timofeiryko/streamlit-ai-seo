from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import yaml


CONFIG_PATH = Path(__file__).parent / "config" / "companies.yaml"


@dataclass(frozen=True)
class CompanyProfile:
    key: str
    display_name: str
    product_name: str
    meta_brief: str
    article_instructions: str
    knowledge_base: Dict[str, List[str]]

    @property
    def category_tags(self) -> List[str]:
        return list(self.knowledge_base.keys())

    def knowledge_base_markdown(self) -> str:
        if not self.knowledge_base:
            return "—"
        lines: List[str] = []
        for category, snippets in self.knowledge_base.items():
            lines.append(f"- **{category}**")
            for snippet in snippets:
                lines.append(f"  - {snippet}")
        return "\n".join(lines)


class ConfigError(RuntimeError):
    """Raised when the company configuration file is invalid."""


def _normalize_list(value: Any, *, context: str) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    raise ConfigError(f"{context} must be a list of strings.")


def _load_company(key: str, raw: Dict[str, Any]) -> CompanyProfile:
    try:
        display_name = str(raw["display_name"])
        product_name = str(raw["product_name"])
        meta_brief = str(raw["meta_brief"])
        article_instructions = str(raw.get("article_instructions", "")).strip()
        knowledge_base_raw = raw.get("knowledge_base", {})
    except KeyError as exc:
        raise ConfigError(f"Missing required field {exc!s} for company '{key}'.") from exc

    if not isinstance(knowledge_base_raw, dict):
        raise ConfigError(f"'knowledge_base' for '{key}' must be a mapping.")

    knowledge_base: Dict[str, List[str]] = {}
    for category, snippets in knowledge_base_raw.items():
        knowledge_base[str(category)] = _normalize_list(
            snippets, context=f"knowledge_base['{category}']"
        )

    return CompanyProfile(
        key=key,
        display_name=display_name,
        product_name=product_name,
        meta_brief=meta_brief.strip(),
        article_instructions=article_instructions,
        knowledge_base=knowledge_base,
    )


@lru_cache(maxsize=1)
def load_company_profiles(
    path: Path | None = None,
) -> Tuple[Dict[str, CompanyProfile], str]:
    config_path = path or CONFIG_PATH
    if not config_path.exists():
        raise ConfigError(f"Company config file not found: {config_path}")

    raw_data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw_data, dict):
        raise ConfigError("Company config must be a mapping at the top level.")

    companies_raw = raw_data.get("companies")
    if not isinstance(companies_raw, dict) or not companies_raw:
        raise ConfigError("Company config must include a non-empty 'companies' mapping.")

    companies: Dict[str, CompanyProfile] = {}
    for key, value in companies_raw.items():
        if not isinstance(value, dict):
            raise ConfigError(f"Company '{key}' must be a mapping of attributes.")
        companies[key] = _load_company(str(key), value)

    default_key = raw_data.get("default_company")
    if default_key not in companies:
        default_key = next(iter(companies))

    return companies, str(default_key)
