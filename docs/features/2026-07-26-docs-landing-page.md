# Feature: Landing page at docs/index.html

**Branch:** feat/docs-landing-page
**Date:** 2026-07-26

## Summary
Adds a self-contained `docs/index.html` landing page (plus `docs/.nojekyll`) so the
curriculum can be published on GitHub Pages at
`https://tatendaz.github.io/langchain-fde-curriculum/` and submitted to search engines.

## Motivation
The repo had no web page at all — `https://tatendaz.github.io/langchain-fde-curriculum/`
returned 404, and Pages was never enabled. That left the README as the only entry point,
which GitHub does not let search engines treat as a landing page: no canonical URL, no
structured data, no social preview.

Of all the repos without a page, this one has the most to gain. Seven phases of long-form
written curriculum is exactly the kind of content that ranks, and the audience searches
for it in words ("how do you evaluate an LLM agent", "LangGraph human in the loop") rather
than by repo name.

## What changed
- `docs/index.html` — single file, no build step, no external assets at all: CSS is
  inline, the favicon is an inline SVG data URI, and there are no web-font or script
  requests.
  - SEO head: `<title>`, meta description, `rel=canonical`, Open Graph, Twitter card.
  - Structured data: `Course` (free, provider, workload `PT65H`) + `FAQPage` with five
    questions mirroring the visible FAQ.
  - Content: hero, what-it-is, the 8-week map table, how each phase works, who it's for,
    getting-started commands, FAQ, footer.
- `docs/.nojekyll` — skip Jekyll processing, matching the `yapui` and `claude-usage` setup.

## Notes
- **Follows the existing house pattern** from `yapui/docs/index.html` and
  `claude-usage/docs/index.html`: same CSS skeleton and dark/light `prefers-color-scheme`
  handling, different accent colour and favicon.
- **Every claim on the page is taken from the README** — hours, cost, the 8-week table,
  the spine, the pass rule — so the two can't drift into contradicting each other.
- **No `og:image`.** `yapui` and `claude-usage` each ship a `social-preview.png`; this
  repo has none, and inventing one was out of scope. Link previews will fall back to the
  page title and description until one is added. For the same reason `twitter:card` is
  `summary` rather than `summary_large_image` — declaring the large card with no image
  just degrades to a plain card anyway. Flip it when an image ships.
- **Pages still needs enabling** (Settings → Pages → `main` / `/docs`) after this merges.
  The URL is already baked into the canonical tag and structured data.
