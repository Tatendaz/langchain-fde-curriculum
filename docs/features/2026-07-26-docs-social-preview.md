# Feature: Social preview image for the landing page

**Branch:** feat/docs-social-preview
**Date:** 2026-07-26

## Summary
Adds `docs/social-preview.png` and wires it up as `og:image` / `twitter:image`, so links
to `https://tatendaz.github.io/langchain-fde-curriculum/` let consumers that support it render a large
image card instead of a bare title-and-description card. Support varies by platform —
X and Slack honour it; others fall back to the title and description, which is what was
rendering before.

## Motivation
The repo already had a custom social preview configured in GitHub Settings, but that only
covers links to `github.com/Tatendaz/langchain-fde-curriculum`. The landing page is a
different URL with its own metadata and had no `og:image` at all. That matters more here
than for the sibling projects: this is long-form written material whose audience finds it
through shared links and search rather than by repo name, so the link preview is often the
entire first impression.

## What changed
- `docs/social-preview.png` — 1280×640, the Obsidian-system card generated from
  `github-social-kit/social-previews/template.html#langchain-fde-curriculum`.
- `docs/index.html`
  - `og:image`, `og:image:width`, `og:image:height`, `og:image:alt`.
  - `twitter:image`.
  - `twitter:card` flipped from `summary` to `summary_large_image`, and the comment
    explaining why it was `summary` is removed — its condition no longer holds.

## Notes
- **The card's tagline is shorter than the page's.** The page reads "Seven phases. Seven
  shipped artifacts. A mastery gate between each one."; the card stops after the first two
  sentences. At 1280×640 the full line wrapped to two rows and, under a two-line title,
  left the layout with no slack — the accent rule ended up against the kicker and the
  artifact strip against the footer. The mastery gate still reads on the card: it is the
  payload of the terminal strip (`phase 5/7 eval suite + CI regression gate → gate passed`).
- **The file is 1280×640, matching the declared `og:image:width`/`height`.** The card is
  rendered at 2560×1280 for the GitHub Settings upload; the copy served here is the 1×
  export, because declaring dimensions that don't match the bytes misleads the scraper.
- Matches the setup `yapui` and `claude-usage` already use, down to the filename.
