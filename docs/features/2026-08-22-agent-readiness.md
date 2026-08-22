# Feature: Agent-readable landing page — `<main>`, Markdown twin, llms.txt links

**Branch:** feat/agent-readiness
**Date:** 2026-08-22

## Summary
Makes `docs/index.html` (the GitHub Pages landing page at https://tatendaz.github.io/langchain-fde-curriculum/)
readable for AI agents the same way the root site is: the page content sits inside `<main>`,
a Markdown twin lives at `docs/index.md`, and the page advertises it with
`<link rel="alternate" type="text/markdown" href="/langchain-fde-curriculum/index.md">` plus
`<link rel="describedby" href="/llms.txt">`. Nothing visible changes apart from an llms.txt link
in the footer.

## Motivation
An Is Agentic audit of tatendaz.github.io (2026-08-22) showed the scanner counts text and the
H1 only inside `<main>`. This page had no `<main>`, so its 4,000+ characters of static text and
its H1 did not count. The root site's `llms.txt` (Tatendaz/Tatendaz.github.io PR #8) lists
this page; the page now points back at it and ships the Markdown twin that the
[llmstxt.org](https://llmstxt.org/) spec recommends (`index.md` next to `index.html`,
`rel="alternate"` to the twin, `rel="describedby"` to the covering `llms.txt`).

## What changed
- `docs/index.html`: `<main>` wraps the hero and every content section (the footer stays
  outside). The hero was a `<header>`; it is now `<div class="hero">` (CSS selector renamed,
  same rules) because boilerplate-stripping extractors drop `<header>` elements and would
  lose the H1 with it. The two `<link>` tags sit after the canonical; the footer gains an llms.txt link.
  No CSS change, no layout change (the stylesheet has no child selectors or `main` rules).
- `docs/index.md`: Markdown twin of the page content, generated from the HTML and then
  hand-checked (the three stat tiles became a list). It ends with links back to the HTML version, the
  source, the root site and `llms.txt`.
- `tests/test_docs_site.py (pytest)`: one `<main>`, one `<h1>` inside it, 500+ characters of text; the head links
  are present; the twin starts with the same H1, contains every H2 of the page, and is plain
  Markdown. Run with `uv run --no-sync pytest -q`.

## Notes
- When the landing page changes, update `docs/index.md` too; the test fails if an H2 goes
  missing from the twin or the H1 drifts.
- Real `Accept: text/markdown` negotiation is not possible on GitHub Pages (no custom
  headers); the twin plus the two links are the static equivalent.
- No per-project `llms.txt`: the root `/llms.txt` covers every path on the host and already
  describes this project.
