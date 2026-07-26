# Session: Social preview image for the landing page

**Branch:** feat/docs-social-preview
**Date:** 2026-07-26

## Prompts
1. "generate the cards and tell me where to put them."
2. "The demo gif I will do later"
3. "added pictures for vergance and promptups they were already there in github"
4. "do 3 pushes demo.gif I will do later lets update the repos"

## Steps taken
- Found an existing card system at `github-social-kit/social-previews/` (template + Chrome
  headless render script) rather than building a new one. It already held cards for the
  sibling projects.
- Rendered the card, exported a 1× copy at 1280×640, and copied it to
  `docs/social-preview.png`.
- Added `og:image` (+ width/height/alt) and `twitter:image` to `docs/index.html`, and
  flipped `twitter:card` to `summary_large_image`, deleting the comment that explained the
  old `summary` value.
- Verified against the live pages that the GitHub Settings social preview was already set
  for every repo, and that the landing pages were the half still missing an image.

## Decisions
- **Two destinations, not one.** A repo's GitHub Settings social preview and a landing
  page's `og:image` are independent; setting the first does nothing for the second. The
  repo cards were already uploaded, which is exactly why the gap was easy to miss.
- **Served the 1× export, not the retina render.** `og:image:width`/`height` are hints the
  scraper uses to reserve layout, so the served bytes have to actually be that size.
  `render.sh` now emits both sizes in one pass so they can't drift apart.
- **Wrote `og:image:alt` as a real description**, including the text rendered inside the
  card's terminal strip, since that string is the image-description metadata consumers can
  expose assistively for a shared link — repeating the page title there would waste it.
