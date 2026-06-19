"""
FactLayer – AI Fact-Checking Web App
Powered by Agno (Claude + DuckDuckGo web search)
"""

import streamlit as st
import pdfplumber
import json
import io
import time
import os
import traceback
from datetime import datetime
from typing import Optional

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FactLayer – AI Fact Checker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

:root {
    --bg: #0d0f14;
    --surface: #161b25;
    --surface2: #1e2535;
    --border: #2a3347;
    --text: #e8eaf0;
    --muted: #7b8499;
    --accent: #4f8ef7;
    --verified: #22c55e;
    --inaccurate: #f59e0b;
    --false: #ef4444;
    --verified-bg: rgba(34,197,94,0.08);
    --inaccurate-bg: rgba(245,158,11,0.08);
    --false-bg: rgba(239,68,68,0.08);
}

* { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding: 2rem 3rem !important; max-width: 1100px !important; }

.hero { text-align: center; padding: 3rem 0 2rem; }
.hero-label { font-family:'Space Mono',monospace; font-size:0.7rem; letter-spacing:0.25em; color:var(--accent); text-transform:uppercase; margin-bottom:1rem; }
.hero-title { font-size:3rem; font-weight:700; line-height:1.1; margin:0 0 1rem; background:linear-gradient(135deg,#e8eaf0 0%,#4f8ef7 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero-sub { font-size:1.05rem; color:var(--muted); max-width:540px; margin:0 auto; line-height:1.6; }

[data-testid="stFileUploader"] { background:var(--surface) !important; border:1.5px dashed var(--border) !important; border-radius:12px !important; padding:1.5rem !important; }
[data-testid="stFileUploader"]:hover { border-color:var(--accent) !important; }
[data-testid="stFileUploader"] label { color:var(--text) !important; }

.stButton > button { background:var(--accent) !important; color:#fff !important; border:none !important; border-radius:8px !important; font-family:'Inter',sans-serif !important; font-weight:600 !important; font-size:0.95rem !important; padding:0.65rem 2rem !important; cursor:pointer !important; transition:opacity 0.2s !important; width:100% !important; }
.stButton > button:hover { opacity:0.88 !important; }
.stButton > button:disabled { opacity:0.4 !important; cursor:not-allowed !important; }

.status-box { background:var(--surface); border:1px solid var(--border); border-left:3px solid var(--accent); border-radius:8px; padding:1rem 1.25rem; font-family:'Space Mono',monospace; font-size:0.78rem; color:var(--muted); margin:1rem 0; }
.error-box { background:rgba(239,68,68,0.07); border:1px solid rgba(239,68,68,0.3); border-left:3px solid var(--false); border-radius:8px; padding:1rem 1.25rem; font-size:0.85rem; color:#fca5a5; margin:0.5rem 0; }
.warn-box  { background:rgba(245,158,11,0.07); border:1px solid rgba(245,158,11,0.3); border-left:3px solid var(--inaccurate); border-radius:8px; padding:1rem 1.25rem; font-size:0.85rem; color:#fcd34d; margin:0.5rem 0; }

.summary-bar { display:flex; gap:1rem; margin:1.5rem 0 1rem; }
.summary-pill { flex:1; border-radius:10px; padding:1rem; text-align:center; border:1px solid; }
.pill-v { background:var(--verified-bg); border-color:var(--verified); }
.pill-i { background:var(--inaccurate-bg); border-color:var(--inaccurate); }
.pill-f { background:var(--false-bg); border-color:var(--false); }
.pill-count { font-size:2rem; font-weight:700; line-height:1; }
.pill-v .pill-count { color:var(--verified); }
.pill-i .pill-count { color:var(--inaccurate); }
.pill-f .pill-count { color:var(--false); }
.pill-label { font-size:0.72rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.1em; margin-top:0.25rem; font-family:'Space Mono',monospace; }

.claim-card { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:1.25rem 1.5rem; margin-bottom:1rem; position:relative; }
.claim-card-verified  { border-left:4px solid var(--verified); }
.claim-card-inaccurate { border-left:4px solid var(--inaccurate); }
.claim-card-false     { border-left:4px solid var(--false); }
.claim-card-error     { border-left:4px solid #6b7280; }

.claim-header { display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; margin-bottom:0.75rem; }
.claim-text { font-size:0.95rem; font-weight:500; color:var(--text); line-height:1.5; flex:1; }
.verdict-badge { font-family:'Space Mono',monospace; font-size:0.65rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; padding:0.3rem 0.75rem; border-radius:20px; white-space:nowrap; flex-shrink:0; }
.badge-verified  { background:var(--verified-bg);  color:var(--verified);  border:1px solid var(--verified); }
.badge-inaccurate { background:var(--inaccurate-bg); color:var(--inaccurate); border:1px solid var(--inaccurate); }
.badge-false     { background:var(--false-bg);     color:var(--false);     border:1px solid var(--false); }
.badge-error     { background:rgba(107,114,128,0.1); color:#9ca3af; border:1px solid #374151; }

.evidence-block { margin-top:0.75rem; padding-top:0.75rem; border-top:1px solid var(--border); }
.evidence-label { font-family:'Space Mono',monospace; font-size:0.65rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.35rem; }
.evidence-text  { font-size:0.85rem; color:var(--muted); line-height:1.55; }
.correct-fact   { font-size:0.85rem; color:var(--verified); margin-top:0.4rem; }
.sources        { margin-top:0.5rem; font-size:0.75rem; color:#4f8ef7; word-break:break-all; }

hr { border-color:var(--border) !important; margin:2rem 0 !important; }
[data-testid="stMarkdownContainer"] p { color:var(--text); }
.stSpinner > div { color:var(--accent) !important; }
[data-testid="stProgress"] > div > div { background:var(--accent) !important; }
[data-testid="stTabs"] button { color:var(--muted) !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color:var(--text) !important; }
</style>
""", unsafe_allow_html=True)


# ── Agno imports (lazy, with clear error) ─────────────────────────────────────
# @st.cache_resource(show_spinner=False)
# def get_agno_classes():
#     """Import agno lazily so missing-package errors surface clearly."""
#     try:
from agno.agent import Agent
from agno.models.groq import Groq
# from agno.tools.webSearch import WebSearchTools
    #     return Agent, Groq, DuckDuckGoTools
    # except ImportError as e:
    #     return None, None, str(e)


# ── PDF helpers ────────────────────────────────────────────────────────────────
MAX_PDF_SIZE_MB = 50
MAX_PAGES = 100
MAX_CHARS =  15000 # ~110k tokens
groq_api_key = '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'

def extract_pdf_text(file_bytes: bytes, filename: str) -> tuple[str, list[str]]:
    """
    Extract text from a PDF. Returns (text, warnings).
    Handles: encrypted PDFs, scanned-only PDFs, partial extraction,
    oversized files, page limits, and corrupt files.
    """
    warnings = []

    # Size guard
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_PDF_SIZE_MB:
        raise ValueError(f"PDF is {size_mb:.1f} MB. Maximum allowed is {MAX_PDF_SIZE_MB} MB.")

    try:
        pdf = pdfplumber.open(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"Cannot open PDF — it may be corrupt or password-protected. ({e})")

    pages_text = []
    empty_pages = 0

    try:
        total_pages = len(pdf.pages)
        if total_pages == 0:
            raise ValueError("PDF has no pages.")

        pages_to_read = min(total_pages, MAX_PAGES)
        if total_pages > MAX_PAGES:
            warnings.append(f"PDF has {total_pages} pages; only the first {MAX_PAGES} were read.")

        for i in range(pages_to_read):
            try:
                page = pdf.pages[i]
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(f"[Page {i+1}]\n{text.strip()}")
                else:
                    empty_pages += 1
            except Exception:
                empty_pages += 1  # skip unreadable page silently

    finally:
        pdf.close()

    if empty_pages > 0 and not pages_text:
        raise ValueError(
            "No readable text found. The PDF may be scanned (image-only). "
            "Try an OCR-processed version."
        )

    if empty_pages > 0:
        warnings.append(
            f"{empty_pages} page(s) had no extractable text (possibly images or blank pages)."
        )

    full_text = "\n\n".join(pages_text)

    if len(full_text) > MAX_CHARS:
        full_text = full_text[:MAX_CHARS]
        warnings.append(
            f"Document truncated to {MAX_CHARS:,} characters for processing "
            f"(~{MAX_CHARS//4} tokens). Very long documents may miss later claims."
        )

    if len(full_text.strip()) < 100:
        raise ValueError("Extracted text is too short to fact-check (under 100 characters).")

    return full_text, warnings


# ── Agno agent helpers ─────────────────────────────────────────────────────────

def build_extractor_agent(Agent):
    """Agent that extracts verifiable claims from text — no web search needed."""
    return Agent(
        model=Groq(id = 'groq/compound', api_key = groq_api_key),
        name="ClaimExtractor",
        description="Extracts specific, verifiable factual claims from documents.",
        # tools = [WebSearchTools(backend = 'google')],
        instructions=[
            "You are a precise fact-extraction specialist.",
            "Extract ONLY specific, verifiable claims such as: statistics/percentages, "
            "dates/timelines, financial figures, technical rankings, named attributions.",
            "Do NOT extract opinions, vague assertions, or unverifiable statements.",
            "Return ONLY valid JSON with no markdown, no preamble, no explanation.",
        ],
        use_json_mode=True,
        retries=2,
        delay_between_retries=2,
        exponential_backoff=True,
    )


def build_verifier_agent(Agent):
    """Agent that verifies a single claim using DuckDuckGo web search."""
    return Agent(
        model=Groq(id = 'groq/compound',api_key = groq_api_key),
        name="ClaimVerifier",
        # tools=[WebSearchTools(backend = 'google')],
        description="Verifies factual claims against live web data.",
        instructions=[
            "You are a rigorous fact-checker. Always search the web before rendering a verdict.",
            "Compare search results carefully against the claim.",
            "Return ONLY valid JSON with no markdown, no preamble, no explanation.",
            "Verdicts: VERIFIED (matches evidence), INACCURATE (partially wrong/outdated), FALSE (fabricated/no evidence).",
        ],
        use_json_mode=True,
        tool_call_limit=4,
        retries=2,
        delay_between_retries=3,
        exponential_backoff=True,
    )


def extract_claims(agent, pdf_text: str) -> list[dict]:
    """
    Run the extractor agent and parse the JSON response.
    Returns a list of claim dicts, or raises with a clear message.
    """
    prompt = f"""From the document below, extract 8–15 specific verifiable factual claims.

Return ONLY this exact JSON structure (no markdown):
{{
  "claims": [
    {{
      "claim": "exact claim text",
      "category": "statistic|date|financial|ranking|attribution",
      "context": "brief surrounding context"
    }}
  ]
}}

DOCUMENT:
{pdf_text}"""

    try:
        output = agent.run(prompt)
    except Exception as e:
        raise RuntimeError(f"Claim extraction agent failed: {e}")

    raw = _get_content(output)
    if not raw:
        raise RuntimeError("Extractor agent returned empty response.")

    return _parse_json_claims(raw)


def verify_claim(agent, claim: dict, max_retries: int = 2) -> dict:
    """
    Run the verifier agent for one claim. Returns enriched claim dict.
    Retries on transient failures; returns a safe fallback on total failure.
    """
    prompt = f"""Verify this claim by searching the web:

CLAIM: {claim['claim']}
CATEGORY: {claim.get('category', 'unknown')}
CONTEXT: {claim.get('context', '')}

Search for authoritative current information, then return ONLY this JSON:
{{
  "verdict": "VERIFIED"|"INACCURATE"|"FALSE",
  "confidence": "HIGH"|"MEDIUM"|"LOW",
  "explanation": "1-2 sentence explanation with what you found",
  "correct_fact": "correct/current fact if INACCURATE or FALSE, else empty string",
  "sources": ["source name or URL", "..."]
}}"""

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            output = agent.run(prompt)
            raw = _get_content(output)
            if not raw:
                raise ValueError("Empty response from verifier.")
            result = _parse_json_verdict(raw)
            return {**claim, **result}
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(2 ** attempt)  # exponential backoff

    # Graceful degradation — mark as unverifiable rather than crashing
    return {
        **claim,
        "verdict": "FALSE",
        "confidence": "LOW",
        "explanation": f"Verification failed after {max_retries + 1} attempts: {last_error}",
        "correct_fact": "",
        "sources": [],
        "_error": True,
    }


# ── JSON parsing helpers ───────────────────────────────────────────────────────

def _get_content(output) -> str:
    """Extract text content from an agno RunOutput object."""
    if output is None:
        return ""
    # RunOutput.content may be str, dict, or list
    content = getattr(output, "content", None)
    if content is None:
        # Try get_content_as_string
        try:
            return output.get_content_as_string() or ""
        except Exception:
            return ""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return json.dumps(content)
    if isinstance(content, list):
        # Some models return list of message dicts
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
        return "\n".join(parts)
    return str(content)


def _clean_json(raw: str) -> str:
    """Strip markdown fences and leading/trailing whitespace."""
    raw = raw.strip()
    # Remove ```json ... ``` or ``` ... ``` fences
    if raw.startswith("```"):
        lines = raw.splitlines()
        start = 1 if lines[0].startswith("```") else 0
        end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        raw = "\n".join(lines[start:end]).strip()
    return raw


def _parse_json_claims(raw: str) -> list[dict]:
    """Parse claim-extraction JSON, with fallback strategies."""
    raw = _clean_json(raw)
    try:
        data = json.loads(raw)
        claims = data.get("claims", [])
        if not isinstance(claims, list):
            raise ValueError("'claims' is not a list")
        # Validate each entry minimally
        valid = []
        for c in claims:
            if isinstance(c, dict) and c.get("claim"):
                valid.append({
                    "claim": str(c["claim"]),
                    "category": str(c.get("category", "unknown")),
                    "context": str(c.get("context", "")),
                })
        return valid
    except json.JSONDecodeError as e:
        # Try to salvage: find the first {...} block
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                data = json.loads(raw[start:end])
                return data.get("claims", [])
            except Exception:
                pass
        raise RuntimeError(
            f"Could not parse claim JSON from model response. "
            f"JSON error: {e}. Raw (first 300 chars): {raw[:300]}"
        )


def _parse_json_verdict(raw: str) -> dict:
    """Parse claim-verification JSON, with fallback strategies."""
    raw = _clean_json(raw)
    valid_verdicts = {"VERIFIED", "INACCURATE", "FALSE"}

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Try to find embedded JSON object
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                data = json.loads(raw[start:end])
            except Exception:
                data = {}
        else:
            data = {}

    verdict = str(data.get("verdict", "")).upper()
    if verdict not in valid_verdicts:
        # Try to infer from text
        raw_lower = raw.lower()
        if "verified" in raw_lower:
            verdict = "VERIFIED"
        elif "inaccurate" in raw_lower or "outdated" in raw_lower:
            verdict = "INACCURATE"
        else:
            verdict = "FALSE"

    confidence = str(data.get("confidence", "LOW")).upper()
    if confidence not in {"HIGH", "MEDIUM", "LOW"}:
        confidence = "LOW"

    sources = data.get("sources", [])
    if not isinstance(sources, list):
        sources = [str(sources)] if sources else []

    return {
        "verdict": verdict,
        "confidence": confidence,
        "explanation": str(data.get("explanation", "No explanation provided.")),
        "correct_fact": str(data.get("correct_fact", "")),
        "sources": [str(s) for s in sources[:5]],
    }


# ── Rendering helpers ──────────────────────────────────────────────────────────

def verdict_class(verdict: str) -> str:
    return {"VERIFIED": "verified", "INACCURATE": "inaccurate", "FALSE": "false"}.get(verdict, "error")


def verdict_icon(verdict: str) -> str:
    return {"VERIFIED": "✓", "INACCURATE": "⚠", "FALSE": "✗"}.get(verdict, "?")


def render_claim_card(result: dict, index: int):
    v = result.get("verdict", "FALSE")
    is_error = result.get("_error", False)
    cls = "error" if is_error else verdict_class(v)
    icon = "⚡" if is_error else verdict_icon(v)
    label = "ERROR" if is_error else v

    sources_html = ""
    if result.get("sources"):
        s_parts = []
        for s in result["sources"][:3]:
            s_safe = str(s).replace("<", "&lt;").replace(">", "&gt;")
            s_parts.append(s_safe)
        sources_html = f'<div class="sources">Sources: {" · ".join(s_parts)}</div>'

    correct_html = ""
    cf = result.get("correct_fact", "")
    if cf and v != "VERIFIED":
        cf_safe = str(cf).replace("<", "&lt;").replace(">", "&gt;")
        correct_html = f'<div class="correct-fact">✦ Correct fact: {cf_safe}</div>'

    confidence = result.get("confidence", "")
    conf_label = f" ({confidence.lower()} confidence)" if confidence else ""

    claim_safe = str(result.get("claim", "")).replace("<", "&lt;").replace(">", "&gt;")
    expl_safe  = str(result.get("explanation", "")).replace("<", "&lt;").replace(">", "&gt;")
    cat_safe   = str(result.get("category", "")).upper()

    st.markdown(f"""
<div class="claim-card claim-card-{cls}">
  <div class="claim-header">
    <div class="claim-text">{index}. {claim_safe}</div>
    <span class="verdict-badge badge-{cls}">{icon} {label}</span>
  </div>
  <div style="font-family:'Space Mono',monospace;font-size:0.65rem;color:var(--muted);margin-bottom:0.4rem;">
    {cat_safe}{conf_label}
  </div>
  <div class="evidence-block">
    <div class="evidence-label">Evidence</div>
    <div class="evidence-text">{expl_safe}</div>
    {correct_html}
    {sources_html}
  </div>
</div>
""", unsafe_allow_html=True)


def show_error(msg: str):
    st.markdown(f'<div class="error-box">⛔ {msg}</div>', unsafe_allow_html=True)


def show_warning(msg: str):
    st.markdown(f'<div class="warn-box">⚠ {msg}</div>', unsafe_allow_html=True)


# ── API key resolution ─────────────────────────────────────────────────────────

# def resolve_api_key() -> Optional[str]:
#     """Check secrets then env for the Anthropic API key."""
#     # Streamlit Cloud secrets
#     try:
#         key = st.secrets.get("ANTHROPIC_API_KEY", "")
#         if key:
#             return key
#     except Exception:
#         pass
#     # Environment variable
#     return os.environ.get("ANTHROPIC_API_KEY", "")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero">
  <div class="hero-label">Agno · Claude · Live Web Search</div>
  <h1 class="hero-title">FactLayer</h1>
  <p class="hero-sub">Upload any PDF — marketing copy, reports, press releases — and watch every claim get cross-referenced against live web data in real time.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Check dependencies ────────────────────────────────────────────────────────
# Agent, Claude, DuckDuckGoTools_or_err = get_agno_classes()
# if Agent is None:
#     show_error(f"Missing dependency: {DuckDuckGoTools_or_err}. Run: pip install agno ddgs")
#     st.stop()
# DuckDuckGoTools = DuckDuckGoTools_or_err

# ── Check API key ─────────────────────────────────────────────────────────────
# api_key = resolve_api_key()
# if not api_key:
#     show_error(
#         "ANTHROPIC_API_KEY not found. "
#         "Set it in Streamlit Cloud Secrets or as an environment variable."
#     )
#     st.info("Go to app settings → Secrets and add: `ANTHROPIC_API_KEY = \"sk-ant-...\"`")
#     st.stop()

# os.environ["ANTHROPIC_API_KEY"] = api_key  # ensure agno picks it up

# ── Layout ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Drop your PDF here",
        type=["pdf"],
        help=f"Text-based PDFs up to {MAX_PDF_SIZE_MB} MB and {MAX_PAGES} pages",
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1.2rem;">
  <div style="font-family:'Space Mono',monospace;font-size:0.65rem;color:var(--accent);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.75rem;">How it works</div>
  <div style="font-size:0.82rem;color:var(--muted);line-height:1.8;">
    <b style="color:var(--text)">1 · Extract</b> — Agno agent identifies verifiable claims<br>
    <b style="color:var(--text)">2 · Search</b> — DuckDuckGo live search cross-references each one<br>
    <b style="color:var(--text)">3 · Verdict</b> — Flags as Verified, Inaccurate, or False
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

run_btn = st.button(
    "🔍 Run Fact-Check",
    disabled=(uploaded_file is None),
    use_container_width=True,
)

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn and uploaded_file:
    st.markdown("---")
    status = st.empty()
    progress_bar = st.progress(0)

    # ── Step 1: Read & validate PDF ────────────────────────────────────────
    status.markdown('<div class="status-box">📄 Reading PDF…</div>', unsafe_allow_html=True)
    try:
        file_bytes = uploaded_file.read()
        pdf_text, pdf_warnings = extract_pdf_text(file_bytes, uploaded_file.name)
    except ValueError as e:
        progress_bar.empty()
        status.empty()
        show_error(str(e))
        st.stop()
    except Exception as e:
        progress_bar.empty()
        status.empty()
        show_error(f"Unexpected error reading PDF: {e}")
        with st.expander("Technical details"):
            st.code(traceback.format_exc())
        st.stop()

    for w in pdf_warnings:
        show_warning(w)

    word_count = len(pdf_text.split())
    status.markdown(
        f'<div class="status-box">✓ Extracted {word_count:,} words from {uploaded_file.name}</div>',
        unsafe_allow_html=True,
    )
    progress_bar.progress(0.1)

    # ── Step 2: Extract claims with Agno ──────────────────────────────────
    status.markdown('<div class="status-box">🧠 Identifying verifiable claims…</div>', unsafe_allow_html=True)
    try:
        extractor = build_extractor_agent(Agent)
        claims = extract_claims(extractor, pdf_text)
    except RuntimeError as e:
        progress_bar.empty()
        status.empty()
        show_error(str(e))
        st.stop()
    except Exception as e:
        progress_bar.empty()
        status.empty()
        show_error(f"Claim extraction failed: {e}")
        with st.expander("Technical details"):
            st.code(traceback.format_exc())
        st.stop()

    if not claims:
        progress_bar.empty()
        status.empty()
        show_warning(
            "No specific verifiable claims were found in this document. "
            "The PDF may contain only opinions, descriptions, or non-quantifiable content."
        )
        st.stop()

    status.markdown(
        f'<div class="status-box">✓ Found {len(claims)} verifiable claims — beginning live verification…</div>',
        unsafe_allow_html=True,
    )
    progress_bar.progress(0.2)

    # ── Step 3: Verify each claim ──────────────────────────────────────────
    verifier = build_verifier_agent(Agent)
    results = []
    live_container = st.empty()
    n = len(claims)

    for i, claim in enumerate(claims):
        truncated_claim = claim["claim"][:80] + ("…" if len(claim["claim"]) > 80 else "")
        live_container.markdown(
            f'<div class="status-box">🔎 Verifying {i+1}/{n}: <em>{truncated_claim}</em></div>',
            unsafe_allow_html=True,
        )
        result = verify_claim(verifier, claim, max_retries=2)
        results.append(result)
        progress_bar.progress(0.2 + 0.8 * (i + 1) / n)

    live_container.empty()
    status.empty()
    progress_bar.empty()

    # ── Results ────────────────────────────────────────────────────────────
    verified   = [r for r in results if r.get("verdict") == "VERIFIED"   and not r.get("_error")]
    inaccurate = [r for r in results if r.get("verdict") == "INACCURATE" and not r.get("_error")]
    false_     = [r for r in results if r.get("verdict") == "FALSE"      and not r.get("_error")]
    errors     = [r for r in results if r.get("_error")]

    st.markdown(f"""
<div class="summary-bar">
  <div class="summary-pill pill-v">
    <div class="pill-count">{len(verified)}</div>
    <div class="pill-label">Verified</div>
  </div>
  <div class="summary-pill pill-i">
    <div class="pill-count">{len(inaccurate)}</div>
    <div class="pill-label">Inaccurate</div>
  </div>
  <div class="summary-pill pill-f">
    <div class="pill-count">{len(false_)}</div>
    <div class="pill-label">False</div>
  </div>
</div>
""", unsafe_allow_html=True)

    if errors:
        show_warning(
            f"{len(errors)} claim(s) could not be verified due to network or API errors. "
            "They appear in the 'All claims' tab marked with ⚡."
        )

    problem_count = len(inaccurate) + len(false_)
    tab1, tab2, tab3 = st.tabs([
        f"All claims ({len(results)})",
        f"⚠ Problems ({problem_count})",
        f"✓ Verified ({len(verified)})",
    ])

    with tab1:
        for i, r in enumerate(results, 1):
            render_claim_card(r, i)

    with tab2:
        problems = inaccurate + false_
        if not problems:
            st.markdown(
                '<p style="color:var(--verified);font-weight:600;padding:1rem 0;">✓ No problems detected!</p>',
                unsafe_allow_html=True,
            )
        else:
            for i, r in enumerate(problems, 1):
                render_claim_card(r, i)

    with tab3:
        if not verified:
            st.markdown(
                '<p style="color:var(--muted);padding:1rem 0;">No verified claims in this document.</p>',
                unsafe_allow_html=True,
            )
        else:
            for i, r in enumerate(verified, 1):
                render_claim_card(r, i)

    # ── Download report ────────────────────────────────────────────────────
    st.markdown("---")
    report = {
        "tool": "FactLayer (agno + Claude + DuckDuckGo)",
        "file": uploaded_file.name,
        "checked_at": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total": len(results),
            "verified": len(verified),
            "inaccurate": len(inaccurate),
            "false": len(false_),
            "errors": len(errors),
        },
        "results": results,
    }
    st.download_button(
        "⬇ Download full JSON report",
        data=json.dumps(report, indent=2, default=str),
        file_name=f"factcheck_{uploaded_file.name.replace('.pdf', '')}.json",
        mime="application/json",
        use_container_width=True,
    )

elif not run_btn:
    st.markdown("""
<div style="text-align:center;padding:3rem 0;color:var(--muted);">
  <div style="font-size:3rem;margin-bottom:1rem;">📄</div>
  <p>Upload a PDF above to get started</p>
</div>
""", unsafe_allow_html=True)
