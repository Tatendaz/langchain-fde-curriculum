# Feature: Phase 4 eval-harness scaffold

**Branch:** feat/phase4-eval-harness-scaffold
**Date:** 2026-09-17

## Summary

Adds a runnable scaffold for the Phase 4 evaluation harness under `phase4/`:
the offline dataset as reproducible Python data, the evaluator wiring, an
eval runner, and the pure CI regression-gate logic — all backed by offline
unit tests. It stops short of the graded Phase 4 solution: no live judge
alignment, no two-experiment comparison, and no production-loop work. Nothing
in this change executes against a live service.

## Motivation

Phase 4 is a build guide, and its definition of done opens with *"`phase4/`
contains a dataset-builder script, evaluator definitions, and an eval-runner —
reproducible by `uv run`, not UI clicks."* Before this change `phase4/` held
only the README, so there was no skeleton to build against and no offline test
coverage for the harness's pure logic (the dataset contract and the regression
gate). This scaffold provides that starting structure and locks its invariants
down with tests.

## What changed

- **`phase4/dataset.py`** — the eval dataset as 12 `EvalExample` rows (7
  policy incl. one keyword-mismatch retrieval case, 3 expected-trajectory, 2
  out-of-scope/adversarial), grounded in Phase 3's `KB_DOCS` and the MCP
  `get_office_status` tool. `to_langsmith_payload` is a pure transform to the
  SDK shape; `build_langsmith_dataset` is the live upload seam (lazy `langsmith`
  import, never run by tests).
- **`phase4/evaluators.py`** — `DEFAULT_THRESHOLDS` and `check_thresholds`, the
  pure core of the CI regression gate (fails closed on a missing metric), plus
  `build_evaluators` wiring correctness / groundedness / trajectory evaluators
  behind a lazy `openevals` / `agentevals` import.
- **`phase4/run_eval.py`** — `summarise_results`, the pure per-metric score
  reducer, and `run_eval_suite`, the single live seam that runs the dataset
  through the Phase 3 agent under `evaluate()`.
- **`tests/test_phase4.py`** — 16 offline tests over the dataset contract, the
  payload transform, the threshold gate, and the score reducer. No model, key,
  or network.

## What is deliberately left to the learner

The live seams carry `TODO(learner)` markers: aligning the LLM-as-judge against
hand labels, producing the two comparable experiments, and closing the
production trace → annotation → dataset loop. This keeps the change a scaffold,
consistent with `CONTRIBUTING.md`'s rule that full Phase 4–6 solutions stay in
a fork.
