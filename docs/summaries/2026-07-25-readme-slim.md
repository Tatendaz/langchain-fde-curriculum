# Session: README routing cut + correctness pass

**Branch:** docs/readme-slim
**Date:** 2026-07-25

## Prompts

1. A prior session slimmed README.md from 454 to 113 lines and relocated
   `## Progress checklist` into `docs/progress.md`, rewriting six inbound
   links. That draft was rejected as an overcut.
2. This session: reset to `origin/main` and redo it as a **routing** cut to
   ~280 lines, keeping `## Progress checklist` in README.md with that exact
   heading, plus a list of correctness fixes to verify individually against
   source.

## Steps taken

- `git reset --hard origin/main` (draft 1 recoverable at `f0027dd`; its
  `docs/setup.md` prose was partly reused in the new Getting started).
- Verified every claim in the fix list against source before editing:
  `LICENSE` (21 lines, zero "CC"), `phase2/agent.py:26`, `phase3/agent.py:74`,
  `.python-version`, `pyproject.toml:12`, `uv.lock` (no `openevals` /
  `agentevals` / `pgvector` / `fastapi`), `phase6/README.md` drill list.
- Counted the gate machinery by `<details>` block: 32 concept-question answer
  keys + 6 FDE-scenario keys = 38, across 7 gates.
- Probed the two badge URLs and the LangSmith ingest endpoint directly rather
  than trusting the audit: `python.langchain.com` 308s to `docs.langchain.com`;
  `langchain-ai.github.io/langgraph/` serves a "moved" page;
  `POST api.smith.langchain.com/runs/multipart` with the literal `lsv2_...`
  placeholder returns `403 {"error":"Forbidden"}`, and
  `langsmith/client.py:3273` logs that as a warning rather than raising — which
  is what makes the troubleshooting entry accurate.
- Rewrote README.md in place from `origin/main`: collapsed the curriculum,
  extracted three docs, folded the operating principles, rebuilt Getting
  started, applied the correctness fixes.
- Fixed the same claims where they recurred outside README.md
  (`CONTRIBUTING.md`, `phase6/README.md`, `.env.example`).
- Tightened `pyproject.toml`'s langgraph floor and re-locked; `uv sync
  --frozen` and the full suite stay green.
- Wrote a link checker over all 15 markdown files (53 relative links and
  anchors) and a status check over all 33 external URLs.

## Decisions

- **Dropped the CC BY 4.0 claim rather than adding CC BY 4.0 text to
  `LICENSE`.** Granting a license is the owner's call, not a doc fix. The
  README now states MIT and notes that MIT's own text covers documentation
  files, which is true of the file that ships.
- **`## Progress checklist` stays in README.md**, boxes reset, with "these are
  yours — tick them as you go." Six phase READMEs depend on that anchor and
  none of them were touched.
- **Kept a `docs/curriculum.md` copy of the full syllabus** rather than
  deleting the collapsed prose. The overlap with the phase READMEs is high but
  not total, and the repo's convention is that content moves rather than
  vanishes.
- **Used "Week N · ~Nh" in the curriculum table** rather than a separate hours
  column. The 8-week map two sections up is the single source for hours
  (it sums to the 70 the lead advertises); a second independent hours column
  would be a drift source.
- **Softened the FDE claims instead of citing them.** Inventing a citation for
  "the #1 rejection reason" would be worse than admitting it's a
  practitioner's read.
- **Landed at 318 lines, not ~280.** See below.

## The line-count arithmetic

The ~280 target and "spend ~145 lines back on Getting started" are not jointly
satisfiable. Fixed costs:

| Block | Lines | Why fixed |
|---|---|---|
| Preserve list (Who this is for, What it costs, mastery-gate protocol, 8-week map) | 90 | Named as must-preserve |
| Lead + badges + time/cost block + mermaid | 33 | Named as the strongest lead of its cohort |
| Progress checklist | 14 | Hard constraint |
| Getting started | 58 | Mandated to grow from 15 |
| **Subtotal** | **195** | |

That leaves 85 lines for Why / the curriculum table / the FDE layer / Stack &
versions / Using or sharing / footer — currently 123. Hitting 280 means cutting
those six by 31%, which lands on the FDE section (the repo's actual
differentiator) and the folded operating principles. 318 is a 30% cut with
nothing good removed, and the target was described as a ceiling rather than a
goal.

## Verification

`uv run pytest` → **14 passed** (Python 3.12.13, pytest 9.1.0). `uv sync
--frozen` clean. 53/53 relative links and anchors resolve. 33 external URLs
checked; the only non-200s are four academic publishers that 403 automated
clients and one host that rate-limited, all pre-existing links.

Nothing pushed; no PR opened.

## Post-merge re-verification (2026-07-26)

After `main` was merged in twice (PR #4 expanded the test suite from 14 to 37
and switched CI to `uv sync --locked`; PR #5 added `docs/index.html`), an
independent review re-ran the checks on the merged branch: `uv run pytest` →
**37 passed**; `uv sync --locked` clean; 54/54 relative links and anchors
across 21 markdown files resolve. The same pass reconciled the merge leftovers
— `docs/curriculum.md`'s "14 offline unit tests" comment, `docs/index.html`'s
"MIT + CC BY 4.0" / "every phase folder ships code" / "gate between each one"
claims and stale doc-domain links — and finished the softening CodeRabbit
asked for (three of its five flagged phrasings were still present), including
the "Who this is for" claim naming LangChain/OpenAI/Anthropic loops as fact
and the misquoted MIT phrase in README and CONTRIBUTING.
