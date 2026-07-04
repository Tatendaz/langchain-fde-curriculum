# Feature: Mastery gates, phase 4–6 build guides, and 2026 ecosystem refresh

**Branch:** feat/mastery-gates-2026-refresh
**Date:** 2026-07-05

## Summary

Restructures the curriculum around per-phase mastery gates (closed-book
concept checks with hidden answer keys + FDE scenarios), adds build-guide
READMEs for phases 4–6, refreshes all content against the July 2026
LangChain ecosystem, and packages the repo for public sharing.

## Motivation

The curriculum had comprehension questions for phases 0–3 but no answer
keys (self-learners couldn't verify understanding), no material for phases
4–6 beyond one-paragraph summaries, some outdated product names, and no
licensing/contribution setup for sharing. Research across FDE hiring loops,
learning science, and comparable curricula showed that (a) gated
progression on demonstrated understanding is both rare and strongly
evidence-backed, and (b) evaluation skills and client-facing drills are
what FDE interviews actually test.

## What changed

- **Main README:** rewritten — mastery-gate protocol, 8-week schedule with
  a 2-month hard cap and triage checkpoints, updated 2026 product names
  (LangSmith Deployment/Studio), evidence-cited methodology section,
  "after the curriculum" section, refreshed resources, sharing/license
  section, mermaid roadmap.
- **Phases 0–3:** "Check your understanding" replaced by full phase gates:
  build checklists, collapsible answer keys written against the actual
  code, and one FDE scenario per phase; API-currency notes added
  (`create_agent` vs deprecated `create_react_agent`, `InMemorySaver`
  naming, streamable HTTP for remote MCP).
- **Phases 4–6 (new folders):** build guides with definition-of-done
  checklists and gates that include spaced-review questions from earlier
  phases. Phase 4: datasets, openevals/agentevals, CI regression gate,
  annotation-queue loop. Phase 5: middleware hardening, prompt-injection
  defense in depth, managed (LangSmith Deployment) vs DIY k8s paths.
  Phase 6: fictional client brief capstone, four FDE drills (discovery
  call, timed decomposition case, non-technical presentation, packaging
  one-pager), cumulative final gate, completions wall.
- **Repo packaging:** LICENSE (MIT code / CC BY 4.0 prose), CONTRIBUTING.md,
  `<2` upper bounds on langchain/langgraph in pyproject (lockfile metadata
  updated; no resolved versions changed).

## Notes

- Phases 4–6 are deliberately guides without solution code; CONTRIBUTING.md
  asks that solutions stay in learners' forks.
- No repo CI gate installed yet (`.github/workflows/pr-gate.yml` available
  from the tatendaz-github skill assets if wanted).
- Existing progress-checklist states preserved (phases 0–2 checked).
