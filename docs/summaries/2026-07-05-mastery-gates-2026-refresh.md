# Session: Curriculum optimization — mastery gates + 2026 refresh

**Branch:** feat/mastery-gates-2026-refresh
**Date:** 2026-07-05

## Prompts

1. "can you go through my FDE curricullum and optimize it add some
   questions to make sure I have understood the phase before I can move to
   the next part. Do some research online to make it more robust so that I
   can share it with people and they can learn and get value out of it. It
   should still be completeable within 2 months maximum."
2. "did you open a pr to merge changes?"

## Steps taken

- Read the full repo (README, phase 0–3 READMEs and code, tests,
  pyproject).
- Ran three parallel web-research agents: FDE role expectations / interview
  loops (2026), LangChain–LangGraph–LangSmith ecosystem state (July 2026),
  and comparable curricula + learning-science practices for self-study.
- Rewrote the main README around mastery gates, an 8-week / 2-month-capped
  schedule, and current ecosystem naming; added sharing + licensing.
- Upgraded phase 0–3 READMEs: gates with build checks, collapsible answer
  keys (written against the actual code), FDE scenarios, currency notes.
- Created phase4/, phase5/, phase6/ build-guide READMEs with
  definition-of-done checklists, gates (including spaced-review questions),
  a capstone client brief, four FDE drills, and a completions wall.
- Added LICENSE (MIT + CC BY 4.0 prose note), CONTRIBUTING.md; bounded
  langchain/langgraph `<2` in pyproject; `uv sync` + full test suite green
  (14/14).
- Second session: branched to feat/mastery-gates-2026-refresh, ran the
  pre-push gate (tests, coverage check, docs entries, local CodeRabbit
  review), pushed, opened this PR.

## Decisions

- Phases 4–6 ship as build guides (specs + gates), not solution code — by
  that point learners should build, not copy; keeps the shared repo honest.
- Answer keys hidden behind `<details>` blocks (retrieval practice needs
  generation before feedback).
- MIT for code + CC BY 4.0 for prose (Carpentries convention for mixed
  curricula repos).
- Kept Ollama as the zero-cost default provider; kept the existing
  progress-checklist states untouched.
- Left `.github/workflows/pr-gate.yml` uninstalled pending user decision
  (public curriculum repo — strict docs CI may deter outside contributors).
