"""Phase 4 — evaluator wiring and the pure threshold gate (scaffold).

Two halves, deliberately split by whether they touch a live service:

  * `build_evaluators` constructs the openevals / agentevals evaluators. They
    call a judge model, so it imports lazily and the offline tests never run it.
  * `check_thresholds` is the pure core of the CI regression gate: given a
    scores dict it decides pass/fail against per-metric bands. Fully offline
    and unit-tested — that is what the `New code has new tests` gate covers.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

# Gate on bands, not exact scores (an eval suite that cries wolf gets deleted).
# These mirror the thresholds suggested in the phase 4 README; tune them once
# the judge is aligned against your own labels.
DEFAULT_THRESHOLDS: dict[str, float] = {
    "correctness": 0.80,
    "groundedness": 0.80,
    "trajectory": 0.90,
}


@dataclass(frozen=True)
class ThresholdResult:
    """Outcome of the regression gate.

    passed    True only when every required metric meets its threshold.
    failures  metric -> (score, threshold) for each metric below its band.
    missing   required metrics that were absent from the scores dict.
    """

    passed: bool
    failures: dict[str, tuple[float, float]] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)


def check_thresholds(
    scores: Mapping[str, float],
    thresholds: Mapping[str, float] = DEFAULT_THRESHOLDS,
) -> ThresholdResult:
    """Compare mean scores against thresholds; a missing metric fails closed.

    A metric that the suite was supposed to produce but didn't is treated as a
    failure, not a pass — silently dropping the trajectory evaluator should
    never turn the gate green.
    """
    failures: dict[str, tuple[float, float]] = {}
    missing: list[str] = []
    for metric, threshold in thresholds.items():
        if metric not in scores:
            missing.append(metric)
            continue
        if scores[metric] < threshold:
            failures[metric] = (scores[metric], threshold)
    return ThresholdResult(passed=not failures and not missing, failures=failures, missing=missing)


def build_evaluators(judge_model: str | None = None) -> list:
    """Construct the correctness / groundedness / trajectory evaluators.

    Live seam — the returned evaluators call a judge model, so this is never
    run by the offline suite.

    TODO(learner): before trusting these, align the judge — label ~5 outputs by
    hand and confirm the judge agrees on at least 4. An unaligned judge is
    worse than none. Use your strongest available model as the judge, never a
    weaker one than the agent under test.
    """
    from agentevals.trajectory.match import create_trajectory_match_evaluator
    from openevals.llm import create_llm_as_judge
    from openevals.prompts import CORRECTNESS_PROMPT, RAG_GROUNDEDNESS_PROMPT

    judge = judge_model or "openai:o3-mini"

    correctness = create_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        feedback_key="correctness",
        model=judge,
    )
    groundedness = create_llm_as_judge(
        prompt=RAG_GROUNDEDNESS_PROMPT,
        feedback_key="groundedness",
        model=judge,
    )
    # `superset`: assert the required tools ran, tolerating harmless reordering
    # or extra calls. `strict` breaks on both and is too brittle to gate on.
    trajectory = create_trajectory_match_evaluator(trajectory_match_mode="superset")

    return [correctness, groundedness, trajectory]
