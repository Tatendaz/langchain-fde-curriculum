# Session: Agent-readable landing page

**Branch:** feat/agent-readiness
**Date:** 2026-08-22

## Prompts
Carried over from the Tatendaz/Tatendaz.github.io session that produced its PR #8:
1. "Improve how ready https://tatendaz.github.io is for agents. Current Is Agentic score:
   66/100 (Is Agentic readiness model based on Ora audit evidence). Implement the following
   fixes in priority order (failures first, then warnings): …" — nine audit items (content
   without JavaScript, agent-friendly 404s, Markdown content negotiation, agent instruction
   file, brand discoverability, JSON-LD, trust pages, developer-resource discoverability,
   MCP) with evidence and recommended fixes.
2. "can you also check subpages as well like yapui, claude-usage, etc.,"
3. Asked whether to fix the five project pages in their own repos; answer: "Yes, fix all
   five (Recommended)".

## Steps taken
- Probed https://tatendaz.github.io/langchain-fde-curriculum/ over HTTP: 200, title/description/canonical set,
  product JSON-LD complete, 4,000+ chars of static text, but no `<main>`, no Markdown twin,
  no `rel="alternate"`/`rel="describedby"`, no link to `llms.txt`.
- Read the page source through the GitHub API (no `<main>`/`<nav>`, H1 inside `<header>`,
  inline CSS with no child selectors) and this repo's docs gate, test runner and CI.
- Patched `docs/index.html` with a shared script (`<main>` wrapper, head links, footer
  links); generated `docs/index.md` with an HTML→Markdown converter and hand-checked it
  (the three stat tiles became a list).
- Added `tests/test_docs_site.py (pytest)` and ran `uv run --no-sync pytest -q`.

## Decisions
- `<main>` wraps the header as well as the sections: the H1 lives in the header and the
  scanner only credits an H1 inside `<main>`.
- The twin is generated from the page, not copied from `README.md`, so it mirrors the page
  exactly and the test can hold the two together (same H1, every H2 present).
- No per-project `llms.txt`; the root file covers the whole host and already lists this
  project with its description and links.
