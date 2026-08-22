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
4. "and make sure the subpages achieve pairity also and use subagents to not fill the context
   window here"

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
- Fetched https://tatendaz.github.io/langchain-fde-curriculum/does-not-exist: GitHub's generic 404
  (a real 404 status, but no links into the project and no Markdown guidance).
- Added `docs/404.html` from the landing page's head, styles and footer: `noindex`, no
  canonical/alternate link, absolute URLs only, a "Where to look next" list and a
  `<pre class="md">` block with the same pointers as Markdown.
- Added two 404 tests to `tests/test_docs_site.py`; ran `uv run --no-sync pytest -q`,
  `uvx ruff@0.14.5 check .` and the skill's coverage check.

## Decisions
- `<main>` wraps the header as well as the sections: the H1 lives in the header and the
  scanner only credits an H1 inside `<main>`.
- The twin is generated from the page, not copied from `README.md`, so it mirrors the page
  exactly and the test can hold the two together (same H1, every H2 present).
- No per-project `llms.txt`; the root file covers the whole host and already lists this
  project with its description and links.
- Every URL on the 404 page is absolute: GitHub Pages serves the one file for every missing
  path, however deep, so a relative link would resolve against the wrong directory. The
  favicon stays the landing page's `data:` SVG, which has no path to resolve.
- The 404 page is `noindex` with no canonical or alternate link: it is a dead end, not a
  document. Its CSS is inline because the landing page has no external stylesheet.
- The 404 work ran in a subagent, as the prompt asked, so the parent session's context stays
  small.
