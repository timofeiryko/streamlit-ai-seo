from __future__ import annotations

import logging
import os
import sys

import dotenv
import streamlit as st
import io

from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import re

# ──────────────── logging ────────────────────────────────────────────── #
_level = logging.DEBUG if os.getenv("DEBUG") else logging.INFO
logging.basicConfig(
    stream=sys.stdout,
    level=_level,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("seo_app")

dotenv.load_dotenv(override=True)          # reads OPENAI_API_KEY / USER / PASSWORD

# ─────────────── 1. Context data ─────────────────────────────────────── #

KNOWLEDGE_BASE: dict[str, list[str]] | None = None
CATEGORIES = ["Transportation", "Trends in logistics", "Carriers", "USA", "Mexico"]


def _kb_as_md() -> str:
    """Flatten KNOWLEDGE_BASE into markdown; dash when empty."""
    if not KNOWLEDGE_BASE:
        return "—"
    return "\n".join(
        f"- **{cat}**\n  " + "\n  ".join(items) for cat, items in KNOWLEDGE_BASE.items()
    )


META_INFO = """
Product:
GetTransport — an online platform for booking and managing cargo
transportation by land, sea, and air. The marketplace connects shippers and
carriers via smart tendering, transparent pricing and digital paperwork.

Audience segmentation (pains & goals)

1. The SMB Owner / Operations Manager – wants cheaper rates & automation.
2. The Carrier / Independent Trucker – wants to avoid dead-head miles, fast pay.
3. The Corporate Logistics Manager – needs visibility, analytics, scalability.
4. The Individual Shipper (B2C) – wants simplicity, fair price, peace of mind.

Typical segment keywords:
SMB: “affordable freight for small business”, “shipping rates e-commerce”
Carrier: “find loads for my truck”, “load board Europe”
Corporate: “digital freight management”, “multimodal shipping TMS”
Individual: “ship a car across country cost”, “move furniture to Spain”
"""

# ─────────────── 2. LLM helpers ──────────────────────────────────────── #

llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0.7)

# dedicated model for article writing (kept; search-tool binding removed for simplicity)
article_llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0.7)


def _chain(template: str, use_article_llm: bool = False) -> LLMChain:
    """Return an LLMChain with the standard SEO fields."""
    prompt = PromptTemplate(
        template=template.strip(),
        input_variables=[
            "meta",
            "segment",
            "keywords",
            "topic",
            "kb",
            "instructions",
            "article",
        ],
    )
    return LLMChain(llm=article_llm if use_article_llm else llm, prompt=prompt)

# ── 2.1 Semantic core --------------------------------------------------- #
keyword_core_chain = _chain(
    """
You are an award-winning SEO strategist in logistics SaaS.

INPUT BRIEF:
{meta}

TASK
Detect each distinct audience segment in the brief, then provide a long,
diverse list of 2-4-word keywords that segment would search to find a
solution like GetTransport.

FORMAT (strict)
## <Audience name>
keyword 1, keyword 2, keyword 3, …   (ONE line per audience)

Rules
• Include commercial, informational and pain-point queries.
• ≥50 keywords per segment, no duplicates.
• No commentary.

Extra snippets you may reuse:
{kb}
"""
)

# ── 2.2 Keyword clustering --------------------------------------------- #
cluster_chain = _chain(
    """
Act as an SEO content planner.

Cluster the following keywords into intent-cohesive groups suitable for one
article each:

{keywords}

FORMAT (strict)
## <Group name>
- Meta information (target audience, key tips to write the article)
- Keywords: keyword 1, keyword 2, …   (one line)

Rules
• 10-20 groups if possible.
• No commentary.
{kb}
"""
)

# ── 2.3 Topic ideas ----------------------------------------------------- #
topic_chain = _chain(
    """
You are a senior logistics content editor.

For each keyword GROUP below, propose 3-6 engaging, SEO-optimised article
titles (60-70 characters).

Return STRICTLY:
## <Group name>
- Title 1
- Title 2
…

KEYWORD GROUPS
{keywords}

{kb}
"""
)

# ── 2.4 Article writer -------------------------------------------------- #
article_prompt = PromptTemplate.from_template(
    """
As a professional SEO copywriter and logistics expert, write a unique,
high-quality markdown article on "{topic}".

Requirements
• ~1500 words, use ALL keywords naturally (~1 % density)
• Structure: H1, H2/H3, bullet lists, conclusion, FAQ (if applicable)
• Mention GetTransport benefits organically, avoid hard sell (only if relevant)
• Use markdown formatting (headings, lists, links, etc.)
• Include a 155-character meta description, focus keyphrase, 3 slug ideas (as a markwodn list with 3 points)
• Include category tag. You should define it, based on the knowledge base, strictly use only the tags mentioned in the knowledge base.
• Meta description, focus keyphrase, slug ideas, categiory tag should be in the beginning of the article, before the main text, strictly with first level header "# Meta information". Than the article itself.
IMPORTANT: your article should be original, not a copy of existing articles.

TARGET KEYWORDS
{keywords}

Knowledge base
{kb}

Pay attention to the following instructions:
{instructions}
"""
)
article_chain = _chain(article_prompt.template, use_article_llm=True)

# ── 2.5 Image-prompt generator ----------------------------------------- #
image_prompt_chain = _chain(
    """
Generate 5 diverse prompts (one per line, ≤300 chars) for an AI image
generator to create an image for the article below:

{article}
"""
)

# ─────────────── 3. Gradio callbacks ─────────────────────────────────── #

def _log(name: str, txt: str, preview: int = 160) -> None:
    log.debug("%s → %s…", name, txt.replace("\n", " ")[:preview])


def _invoke(chain: LLMChain, **fields) -> str:
    """Predict with defaults and return plain string."""
    base = {k: "" for k in (
        "meta", "segment", "keywords", "topic",
        "kb", "instructions", "article"
    )}
    base.update(fields)
    return chain.predict(**base)


def gen_semantic_core(meta: str) -> str:
    log.info("Semantic core requested (%d chars)", len(meta))
    out = _invoke(keyword_core_chain, meta=meta, kb=_kb_as_md())
    _log("semantic_core", out)
    return out


def cluster_keywords(keywords: str) -> str:
    log.info("Clustering (%d chars)", len(keywords))
    if not keywords.strip():
        return "⚠️ Please paste keywords first."
    out = _invoke(cluster_chain, keywords=keywords, kb=_kb_as_md())
    _log("cluster", out)
    return out


def gen_topics(groups: str) -> str:
    log.info("Generating topics (%d chars)", len(groups))
    out = _invoke(topic_chain, keywords=groups, kb=_kb_as_md())
    _log("topics", out)
    return out


def gen_article(keywords: str, topic: str, instr: str) -> str:
    return _invoke(
        article_chain,
        keywords=keywords,
        topic=topic,
        instructions=instr,
        kb=_kb_as_md(),
    )


def gen_image_prompts(article_md: str) -> str:
    if not article_md.strip():
        return "⚠️ Paste article markdown first."
    return _invoke(image_prompt_chain, article=article_md, kb=_kb_as_md())

# --------------------------------------------------------------------- #
# 4. Streamlit UI                                                       #
# --------------------------------------------------------------------- #
st.set_page_config(page_title="AI SEO Content Suite", layout="wide")
st.title("🚀 AI SEO Content Generator")


def md_output(label: str, state_key: str, file_stub: str, height: int = 300) -> None:
    """
    Splits the markdown into two parts:
    1. Meta information (the first "# " header and its content until the second header)
    2. Article (from the second "# " header onward)
    
    Renders each section separately and adds a download button for the full markdown.
    """
    md_txt = st.session_state.get(state_key, "")
    if not md_txt:
        return

    # Find all headers that start with "# " (assuming they are at the beginning of a line)
    headers = list(re.finditer(r"^# .+", md_txt, re.MULTILINE))
    if len(headers) >= 2:
        meta_info = md_txt[headers[0].start():headers[1].start()].strip()
        article = md_txt[headers[1].start():].strip()
    else:
        # Fallback: if not splitable, treat all as meta information
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


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["1️⃣ Semantic Core", "2️⃣ Keyword Clustering", "3️⃣ Topic Ideas",
     "✍️ Article Writer", "✨ Image Prompts"]
)

# 1️⃣ Semantic core ----------------------------------------------------- #
with tab1:
    meta = st.text_area("Meta / Brief", META_INFO, height=320)
    if st.button("Generate Semantic Core"):
        st.session_state["semantic_core"] = gen_semantic_core(meta)
    md_output("Semantic Core", "semantic_core", "semantic_core")

# 2️⃣ Keyword clustering ------------------------------------------------ #
with tab2:
    kw_input = st.text_area(
        "Keywords (comma or line separated)",
        placeholder="Paste keywords from tab 1",
        height=220,
    )
    if st.button("Cluster Keywords"):
        st.session_state["clusters"] = cluster_keywords(kw_input)
    md_output("Clusters", "clusters", "clusters")

# 3️⃣ Topic ideas ------------------------------------------------------- #
with tab3:
    groups_in = st.text_area("Keyword groups (tab 2 output)", height=260)
    if st.button("Generate Topics"):
        st.session_state["topics"] = gen_topics(groups_in)
    md_output("Proposed Topics", "topics", "topics")

# ✍️ Article writer ----------------------------------------------------- #
with tab4:
    kw_for_article = st.text_area("Target keywords", height=120)
    topic_in = st.text_input("Chosen topic")
    instr_box = st.text_area("Custom instructions (optional)", height=120)
    if st.button("Write Article"):
        st.session_state["article"] = gen_article(kw_for_article, topic_in, instr_box)
    md_output("Generated Article", "article", "article", height=600)

# ✨ Image prompts ------------------------------------------------------ #
with tab5:
    art_in = st.text_area("Article markdown", height=260)
    if st.button("Generate Image Prompts"):
        st.session_state["img_prompts"] = gen_image_prompts(art_in)
    md_output("Image-generation Prompts", "img_prompts", "image_prompts")


# --------------------------------------------------------------------- #
# 5. Optional basic auth (for HF Spaces private mode)                   #
# --------------------------------------------------------------------- #
# Streamlit does not support built-in basic auth. On HuggingFace you can
# enable "Space secrets" / "HF Space login" instead. Nothing to do here.