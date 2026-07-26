# Feature: README routing cut + correctness pass

**Branch:** docs/readme-slim
**Date:** 2026-07-25

## Summary

Cuts README.md from 454 to 318 lines by *routing* rather than deleting:
"The curriculum" collapses from 862 words of prose into a 7-row table, and
three sections move into linked docs. Everything that left the README lives in
`docs/`. The savings are spent on a Getting started section that grew from 15
to 58 lines and now states every prerequisite *before* the command it gates.

Alongside the cut, a correctness pass: the license claim, the progress badge,
two self-contradictions, and eight smaller drifted facts.

## Motivation

Two problems, one file.

**Drift.** The README made claims the repo no longer backs. The most serious:
the license badge rendered `MIT + CC BY 4.0` while `LICENSE` was 21 lines of
unmodified MIT with zero occurrences of "CC", *and* the badge's alt text said
"License: MIT" — so screen-reader users got a different license claim than
sighted users. The README then invited organisations to "run it as a study
group or internal cohort," which asks a legal reviewer to rely on a CC BY 4.0
grant that existed only as a markdown sentence.

**Redundancy.** "The curriculum" (112 lines) restated seven phase READMEs that
were one click away, at 55–81% measured term overlap. A reader who clicked
through got the same content twice; a maintainer got two places to update.

## What changed

### Structural

- **"The curriculum" → a 7-row table** (phase · what you build · what you ship
  · when), each row linking the phase README. The full syllabus moved verbatim
  to `docs/curriculum.md`, which also absorbs the repo-layout tree (GitHub
  renders the same file list two inches above where the tree sat).
- **Three sections extracted:** the learning-science `<details>` block →
  `docs/evidence.md`; "After the curriculum" + "Curated resources" →
  `docs/resources.md`.
- **Operating principles 1–4 folded** into "Why this curriculum exists"
  (principles 2 and 3 already overlapped its two existing items). Principle 5
  (tiered model routing) moved to "Stack & versions".
- **Getting started rebuilt** with a prerequisites block, the `.env` surface
  including the previously undocumented `EMBED_MODEL`, and four troubleshooting
  entries.
- **`## Progress checklist` stays put, with that exact heading** — six phase
  READMEs link `../README.md#progress-checklist`. All boxes reset to unticked.

### Correctness

- **License.** Dropped the CC BY 4.0 claim from the badge, the README's sharing
  section and `CONTRIBUTING.md`, rather than granting a license on the owner's
  behalf. The repo is MIT, and MIT's own text covers "the Software **and
  associated documentation files**" — so the prose is licensed too. Badge alt
  text and badge image now agree. *(Supersedes the "MIT code / CC BY 4.0 prose"
  line in `docs/features/2026-07-05-...` and `docs/summaries/2026-07-05-...`,
  which recorded an intent the LICENSE file never carried.)*
- **Deleted the hardcoded `progress-3/7 phases` badge.** The curriculum is 7/7:
  worked code for phases 0–3, a 37-test suite (14 at the time of the original
  cut; PR #4's CI hardening expanded it), and 264/239/291-line build guides
  for 4/5/6. The badge read as "43% written" and pre-ticked three phases in
  every fork.
- **"Each phase folder ships working, commented code"** → phases 0–3 ship code,
  4–6 are build guides. The README used to contradict itself 104 lines later.
- **"Every phase folder stands alone"** → "each phase README is self-contained
  *as a document*", with the code dependency named (`phase2/agent.py:26`
  imports `phase1.agent`; phases 4–6 work against your Phase 3 agent). Same fix
  in `CONTRIBUTING.md`.
- **Badges 2 and 3** now point at `docs.langchain.com` (the same domain this
  README already used); `python.langchain.com` 308-redirects there and
  `langchain-ai.github.io/langgraph/` serves a "Documentation has moved" page.
  The LangChain badge reads `1.x` (the declared constraint) instead of `1.3`
  (a lockfile resolution).
- **`langgraph>=0.3,<2` → `>=1.0,<2`** in `pyproject.toml`, re-locked. The old
  floor contradicted the badge and the curriculum; `langchain` 1.3.9 requires
  `langgraph<1.3.0,>=1.2.4` anyway, so the floor was unreachable slack.
- **`EMBED_MODEL`** (read at `phase3/agent.py:74`) added to `.env.example` and
  named in the README. It was documented nowhere.
- **`ollama serve`** is now a stated prerequisite; it previously appeared in no
  README, only in an `.env.example` comment.
- **"the lockfile pins exact versions this repo was tested with"** sat under a
  list including `openevals`, `agentevals`, `pgvector`, FastAPI and Helm, none
  of which are in `uv.lock`. Those are now explicitly named as phase-4/5
  dependencies you install yourself.
- **"(Phase 6 drills all four)"** sat above a six-item list; the four drills map
  to three of those bullets. Now names the four drills.
- **"Two checkpoints:"** was followed by three bullets — the third is the
  non-negotiable spine, not a checkpoint. Now labelled as the rule.
- **`.python-version` pins 3.12** while `pyproject.toml` allows ≥3.11; both
  facts now stated, in Getting started and in Stack & versions.

### Sourcing

The evidence `<details>` block carried six real citations. The FDE section
carried none while making stronger claims ("filters out most candidates who
passed the coding rounds", "the #1 rejection reason"), under a promise that
"the sources are real 2025–26 interview loops and job postings". Softened to
reported experience with an explicit sourcing note, rather than inventing
citations. Same softening applied to the two matching claims in
`phase6/README.md`.

### Undersold, now surfaced

The README never stated its own most distinctive number: **32 closed-book
concept questions and 6 client-facing FDE scenarios across 7 gates, 38 hidden
answer keys**, with spaced review (Phase 4 re-asks Phases 2 and 3; Phase 5
re-asks 0, 1 and 4; Phase 6 asks one per phase). Verified by counting
`<details>` blocks. That machinery is the part that doesn't exist elsewhere;
the syllabus is the commodity.

### Contributing

`CONTRIBUTING.md` now documents the PR gate. `.github/workflows/pr-gate.yml`
hard-fails any PR missing `docs/features/*<slug>.md` and
`docs/summaries/*<slug>.md`, and that requirement appeared in zero user-facing
files — a contributor following the four numbered steps got a red X.

## Verification

- `uv run pytest` — **14 passed** at the original cut (Python 3.12.13, pytest
  9.1.0); **37 passed** re-run 2026-07-26 after the merges from `main`
  brought in PR #4's expanded suite.
- `uv sync --locked` clean after the re-lock (this is what CI runs; the
  original session used `--frozen`, before PR #4 switched CI to `--locked`).
- All relative links and heading anchors resolve — 53 across 15 markdown
  files at the original cut; 54 across 21 files re-checked 2026-07-26.
- All 33 external URLs return 200 except four academic publishers (SAGE ×3,
  Wiley) that 403 automated clients, and nabeelqu.co which rate-limited the
  check. All pre-existing links, all fine in a browser.
- `git grep "README.md#progress-checklist"` still returns the same six phase
  READMEs, all resolving.

## Review follow-up (2026-07-26)

An independent review pass over the merged branch fixed what the two merges
from `main` had left inconsistent, and closed out the review feedback fully:

- `docs/curriculum.md` repo layout said "14 offline unit tests"; the suite is
  37. Now 37.
- `docs/index.html` (merged in from PR #5) still claimed "MIT + CC BY 4.0"
  in three places, "Each phase folder ships working, commented code", "a
  mastery gate between each one", and the old `python.langchain.com` /
  `langchain-ai.github.io/langgraph/` doc links — all now aligned with this
  PR's corrections (MIT-only, 0–3 code / 4–6 build guides, "for each one",
  `docs.langchain.com`).
- Three of the five evidence-scope phrasings CodeRabbit flagged were still
  present ("Almost no popular free curriculum", "measurably improves",
  "exactly the ones drilled here"); all three are now softened.
- README's "Who this is for" still asserted "the actual interview loops at
  LangChain, OpenAI, and Anthropic" as fact — the one named-company claim the
  sourcing pass missed. Softened to reported experience.
- README and CONTRIBUTING quoted MIT as covering "the Software and associated
  documentation files"; the license's actual words are "this software and
  associated documentation files". Quotes now exact.
