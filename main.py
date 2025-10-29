from __future__ import annotations

import io
import logging
import os
import re
import sys

import dotenv

dotenv.load_dotenv(override=True)  # reads OPENAI_API_KEY / USER / PASSWORD

import streamlit as st

from company_profiles import ConfigError, load_company_profiles
from services import digest as digest_service
from services import llm as llm_service

# ──────────────── logging ────────────────────────────────────────────── #
_level = logging.DEBUG if os.getenv("DEBUG") else logging.INFO
logging.basicConfig(
    stream=sys.stdout,
    level=_level,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("seo_app")

# ──────────────── data bootstrap ─────────────────────────────────────── #
try:
    COMPANY_PROFILES, DEFAULT_COMPANY_KEY = load_company_profiles()
except ConfigError as exc:  # pragma: no cover - configuration errors are fatal
    raise RuntimeError(f"Failed to load company configuration: {exc}") from exc


# --------------------------------------------------------------------- #
# Streamlit helpers                                                     #
# --------------------------------------------------------------------- #
def md_output(label: str, state_key: str, file_stub: str, height: int = 300) -> None:
    """
    Render markdown output split into meta block and article body, providing a download control.
    """
    md_txt = st.session_state.get(state_key, "")
    if not md_txt:
        return

    headers = list(re.finditer(r"^# .+", md_txt, re.MULTILINE))
    if len(headers) >= 2:
        meta_info = md_txt[headers[0].start():headers[1].start()].strip()
        article = md_txt[headers[1].start():].strip()
    else:
        meta_info = md_txt
        article = ""

    st.markdown(meta_info, unsafe_allow_html=True)

    if article:
        st.markdown(f"#### {label}")
        st.code(article, language="markdown")

    st.download_button(
        "📋 Download markdown",
        data=io.StringIO(md_txt).getvalue(),
        file_name=f"{file_stub}.md",
        mime="text/markdown",
        key=f"copy_{state_key}",
    )


# --------------------------------------------------------------------- #
# 1. Layout & state initialisation                                     #
# --------------------------------------------------------------------- #
st.set_page_config(page_title="AI SEO Content Suite", layout="wide")
st.title("🚀 AI SEO Content Generator")

if "company_key" not in st.session_state:
    st.session_state["company_key"] = DEFAULT_COMPANY_KEY
if "meta_brief" not in st.session_state:
    st.session_state["meta_brief"] = COMPANY_PROFILES[DEFAULT_COMPANY_KEY].meta_brief
if "article_custom_instructions" not in st.session_state:
    st.session_state["article_custom_instructions"] = ""
if "enhanced_mode" not in st.session_state:
    st.session_state["enhanced_mode"] = False
if "daily_digest_text" not in st.session_state:
    st.session_state["daily_digest_text"] = ""
if "daily_digest_meta" not in st.session_state:
    st.session_state["daily_digest_meta"] = {}
if "daily_digest_error" not in st.session_state:
    st.session_state["daily_digest_error"] = ""

company_options = list(COMPANY_PROFILES.keys())

with st.sidebar:
    st.header("Company profile")
    selected_company_key = st.selectbox(
        "Choose configuration",
        options=company_options,
        key="company_key",
        format_func=lambda key: COMPANY_PROFILES[key].display_name,
    )

current_profile = COMPANY_PROFILES.get(
    selected_company_key, COMPANY_PROFILES[DEFAULT_COMPANY_KEY]
)

if st.session_state.get("_prev_company_key") != selected_company_key:
    st.session_state["_prev_company_key"] = selected_company_key
    st.session_state["meta_brief"] = current_profile.meta_brief
    st.session_state["article_custom_instructions"] = ""
    st.session_state["enhanced_mode"] = False
    st.session_state["daily_digest_text"] = ""
    st.session_state["daily_digest_meta"] = {}
    st.session_state["daily_digest_error"] = ""
    for key in ("semantic_core", "clusters", "topics", "article", "img_prompts"):
        st.session_state.pop(key, None)

with st.sidebar:
    st.markdown(f"**Product**: {current_profile.product_name}")
    category_line = ", ".join(current_profile.category_tags) or "—"
    st.markdown(f"**Category tags**: {category_line}")
    with st.expander("Knowledge base", expanded=False):
        st.markdown(current_profile.knowledge_base_markdown())


# --------------------------------------------------------------------- #
# 2. Workflow tabs                                                     #
# --------------------------------------------------------------------- #
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["1️⃣ Semantic Core", "2️⃣ Keyword Clustering", "3️⃣ Topic Ideas",
     "✍️ Article Writer", "✨ Image Prompts", "🗞️ Daily Digest"]
)

# 1️⃣ Semantic core ----------------------------------------------------- #
with tab1:
    meta = st.text_area("Meta / Brief", key="meta_brief", height=320)
    if st.button("Generate Semantic Core"):
        st.session_state["semantic_core"] = llm_service.gen_semantic_core(
            meta, current_profile
        )
    md_output("Semantic Core", "semantic_core", "semantic_core")

# 2️⃣ Keyword clustering ------------------------------------------------ #
with tab2:
    kw_input = st.text_area(
        "Keywords (comma or line separated)",
        placeholder="Paste keywords from tab 1",
        height=220,
    )
    if st.button("Cluster Keywords"):
        st.session_state["clusters"] = llm_service.cluster_keywords(
            kw_input, current_profile
        )
    md_output("Clusters", "clusters", "clusters")

# 3️⃣ Topic ideas ------------------------------------------------------- #
with tab3:
    groups_in = st.text_area("Keyword groups (tab 2 output)", height=260)
    if st.button("Generate Topics"):
        st.session_state["topics"] = llm_service.gen_topics(groups_in, current_profile)
    md_output("Proposed Topics", "topics", "topics")

# ✍️ Article writer ----------------------------------------------------- #
with tab4:
    kw_for_article = st.text_area("Target keywords", height=120)
    topic_in = st.text_input("Chosen topic")
    instr_box = st.text_area(
        "Custom instructions (optional)", height=120, key="article_custom_instructions"
    )
    enhanced_mode_flag = st.checkbox("Enhanced creativity mode", key="enhanced_mode")
    if st.button("Write Article"):
        st.session_state["article"] = llm_service.gen_article(
            kw_for_article,
            topic_in,
            instr_box,
            current_profile,
            enhanced_mode_flag,
        )
    md_output("Generated Article", "article", "article", height=600)

# ✨ Image prompts ------------------------------------------------------ #
with tab5:
    art_in = st.text_area("Article markdown", height=260)
    if st.button("Generate Image Prompts"):
        st.session_state["img_prompts"] = llm_service.gen_image_prompts(
            art_in, current_profile
        )
    md_output("Image-generation Prompts", "img_prompts", "image_prompts")

# 🗞️ Daily digest ------------------------------------------------------- #
with tab6:
    window = digest_service.compute_digest_window()
    st.markdown(f"**Дайджест за окно:** {window.label}")
    st.caption("Собираем новости с 04:00 прошлого дня до 03:59 сегодняшнего (GMT+3).")

    with st.expander("📡 RSS-источники", expanded=False):
        for category, urls in digest_service.RSS_SOURCES.items():
            st.markdown(f"- **{category.title()}**")
            for url in urls:
                st.markdown(f"  - {url}")

    if st.button("Сформировать дайджест", key="generate_digest"):
        st.session_state["daily_digest_error"] = ""
        with st.spinner("Парсим ленты и готовим дайджест..."):
            try:
                digest_text, metadata = digest_service.generate_daily_digest(current_profile)
            except ValueError as err:
                st.session_state["daily_digest_error"] = str(err)
            except Exception as exc:  # pragma: no cover - defensive UI
                st.session_state["daily_digest_error"] = f"Не удалось сформировать дайджест: {exc}"
            else:
                st.session_state["daily_digest_text"] = digest_text
                st.session_state["daily_digest_meta"] = metadata

    if st.session_state.get("daily_digest_error"):
        st.error(st.session_state["daily_digest_error"])

    digest_txt = st.session_state.get("daily_digest_text")
    digest_meta = st.session_state.get("daily_digest_meta") or {}
    if digest_txt:
        st.markdown("### 📝 Готовый дайджест")
        st.markdown(digest_txt)

        if digest_meta.get("article_count", 0) > 0:
            st.download_button(
                "⬇️ Скачать дайджест",
                data=io.StringIO(digest_txt).getvalue(),
                file_name="daily_digest.md",
                mime="text/markdown",
                key="download_daily_digest",
            )

        st.markdown("### 📊 Метаинформация")
        digest_window_label = digest_meta.get("window_label", window.label)
        st.write(
            {
                "Окно": digest_window_label,
                "Новостей обработано": digest_meta.get("article_count", 0),
                "Сгенерирован": digest_meta.get("generated_at", ""),
            }
        )

        articles = digest_meta.get("articles") or []
        if articles:
            st.markdown("### 🗂️ Использованные события")
            for article in articles:
                st.markdown(
                    f"- [{article['title']}]({article['link']}) — {article['source']} "
                    f"({article['published']})"
                )
        elif digest_meta.get("article_count", 0) == 0:
            st.info("На выбранный промежуток новостей не найдено — дайджест не записан в журнал.")

# --------------------------------------------------------------------- #
# 3. Optional basic auth (for HF Spaces private mode)                   #
# --------------------------------------------------------------------- #
# Streamlit does not support built-in basic auth. On HuggingFace you can
# enable "Space secrets" / "HF Space login" instead. Nothing to do here.
