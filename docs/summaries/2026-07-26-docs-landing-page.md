# Session: Landing page so the curriculum can be indexed

**Branch:** feat/docs-landing-page
**Date:** 2026-07-26

## Prompts
1. "can you remind me to submit all pages to google seo vergence, claude-usage and my
   own github page. yapui is already submitted."
2. "and any page I may have forgotten in my github pages"
3. "submit to bing as well"
4. "promptups and langchain fde curricilum?"
5. "do both"
6. "Vergance, promptups, langchain-fde-curriculum . Later today I will do the demo gif"

## Steps taken
- Audited every repo on the account for a live GitHub Pages site. This repo had none —
  `https://tatendaz.github.io/langchain-fde-curriculum/` returned 404 and Pages was never
  enabled, so there was nothing to submit to Google or Bing.
- Read `yapui/docs/index.html` as the reference implementation and reused its structure.
- Pulled every factual claim on the page out of this repo's README — the 8-week table,
  the ~60–70 hour estimate, the ~$0 cost breakdown, the phase anatomy, the pass rule.
- Wrote `docs/index.html` and `docs/.nojekyll`.

## Decisions
- **Reused the house pattern rather than designing something new.** `yapui` and
  `claude-usage` already share a single-file layout with inline CSS and
  `prefers-color-scheme` theming. Matching it keeps the sites recognisably one family and
  means no build step, no dependencies, and nothing to break later.
- **`Course` structured data, not `SoftwareApplication`.** The other two pages describe
  tools; this one describes a curriculum, so `Course` (with `isAccessibleForFree`, a
  `provider`, and a `PT65H` workload) is the type search engines actually have handling
  for. `FAQPage` is kept in common with the others.
- **Wrote the FAQ answers to match the visible copy verbatim.** Structured data that
  disagrees with what's on the page is a manual-action risk, not a ranking trick.
- **Left `og:image` out.** The other two pages ship a `social-preview.png`; this repo has
  none, and generating one wasn't part of the ask. Noted as a follow-up instead of
  pointing the tag at a file that doesn't exist.
