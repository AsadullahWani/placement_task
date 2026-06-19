# FactLayer — AI Fact-Checking Web App

> Powered by **Agno** framework · **Claude claude-sonnet-4-6** · **DuckDuckGo** live web search

Upload any PDF and every verifiable claim gets cross-referenced against live web data in real time.

## What it does

1. **Extract** — Agno agent (Claude) reads your PDF and identifies specific verifiable claims (stats, dates, financial figures, rankings)
2. **Verify** — Each claim is verified by a second Agno agent using DuckDuckGo live web search
3. **Report** — Claims are flagged as **Verified**, **Inaccurate** (outdated/wrong), or **False** (fabricated/no evidence), with the correct fact shown

## Deploy on Streamlit Cloud (free, ~5 min)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "FactLayer"
git remote add origin https://github.com/YOUR_USER/factlayer.git
git push -u origin main
```

### Step 2 — Deploy
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. **New app** → pick your repo → `app.py`
3. **Advanced settings → Secrets** → add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-YOUR_KEY"
   ```
4. **Deploy** — live URL in ~60 seconds

## Local Development

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
streamlit run app.py
```

## Edge Cases Handled

| Scenario | Behaviour |
|---|---|
| Encrypted / corrupt PDF | Clear error message, app doesn't crash |
| Scanned (image-only) PDF | Detected and user is told to use OCR version |
| PDF > 50 MB | Rejected with size guidance |
| PDF > 100 pages | Only first 100 pages read; user warned |
| No extractable text | Graceful error, not a traceback |
| Document too short | Rejected with helpful message |
| Model returns malformed JSON | Fallback parsing extracts what it can |
| Markdown-fenced JSON | Stripped automatically |
| Invalid verdict string | Inferred from response text |
| Network error during verification | Retried up to 2× with backoff; marked ⚡ if all fail |
| Missing API key | Clear instructions shown before any API call |
| Missing dependencies | Caught at startup with install instructions |

## Stack

| Component | Library |
|---|---|
| Framework | [Agno](https://github.com/agno-agi/agno) |
| LLM | Claude claude-sonnet-4-6 (via Agno) |
| Web search | DuckDuckGo (via `agno.tools.duckduckgo`) |
| PDF parsing | pdfplumber |
| UI | Streamlit |
