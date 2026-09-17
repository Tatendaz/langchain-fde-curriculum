"""Phase 4 — the eval runner (scaffold).

Wires the dataset and evaluators into a single `evaluate()` experiment and
reduces the per-example results to one mean score per metric, which the CI
regression gate then checks against `DEFAULT_THRESHOLDS`.

The reducer (`summarise_results`) is pure and offline-tested. The runner
(`run_eval_suite`) is the one live seam: it needs LANGSMITH_API_KEY, a judge
model, and a running Phase 3 agent, so it is never exercised by the offline
suite.

Run an experiment (needs live config) with:
    uv run python -m phase4.run_eval
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from phase4.dataset import dataset_examples
from phase4.evaluators import DEFAULT_THRESHOLDS, ThresholdResult, build_evaluators, check_thresholds


def summarise_results(results: Iterable[Mapping[str, float]]) -> dict[str, float]:
    """Average each metric across per-example score rows.

    `results` is an iterable of {metric: score} mappings (one per example). A
    metric is averaged only over the rows that reported it, so an evaluator
    that skipped a row does not drag its mean toward zero. Returns {} for no
    rows.
    """
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}
    for row in results:
        for metric, score in row.items():
            totals[metric] = totals.get(metric, 0.0) + score
            counts[metric] = counts.get(metric, 0) + 1
    return {metric: totals[metric] / counts[metric] for metric in totals}


def run_eval_suite(experiment_prefix: str = "phase4", judge_model: str | None = None) -> dict[str, float]:
    """Run the offline dataset through the Phase 3 agent under `evaluate()`.

    Live seam. Returns the mean score per metric, ready for `check_thresholds`.

    TODO(learner): to produce the two comparable experiments the phase gate
    asks for, run this once, change one real thing (retrieval k, MODEL, or the
    system prompt), run it again with a different `experiment_prefix`, and open
    both side by side in LangSmith.
    """
    import asyncio

    from langsmith import Client

    from phase3.agent import build_agent

    agent = asyncio.run(build_agent())

    def target(inputs: dict) -> dict:
        state = asyncio.run(
            agent.ainvoke(
                {"messages": [{"role": "user", "content": inputs["question"]}]},
                {"configurable": {"thread_id": "eval"}},
            )
        )
        return {"messages": state["messages"]}

    client = Client()
    experiment = client.evaluate(
        target,
        data="phase4-fde-eval",
        evaluators=build_evaluators(judge_model),
        experiment_prefix=experiment_prefix,
    )

    rows = [
        {r["key"]: r["score"] for r in record["evaluation_results"]["results"] if r["score"] is not None}
        for record in experiment
    ]
    return summarise_results(rows)


def main() -> None:
    print(f"Dataset: {len(dataset_examples())} examples")
    scores = run_eval_suite()
    print("Mean scores:", scores)
    result: ThresholdResult = check_thresholds(scores, DEFAULT_THRESHOLDS)
    if result.passed:
        print("Gate PASSED.")
    else:
        print("Gate FAILED.")
        for metric, (score, threshold) in result.failures.items():
            print(f"  {metric}: {score:.3f} < {threshold:.3f}")
        for metric in result.missing:
            print(f"  {metric}: missing from results")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
