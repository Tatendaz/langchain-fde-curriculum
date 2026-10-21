"""Offline unit tests for the Phase 4 eval harness (no model, key, or network).

These cover the pure pieces: the dataset's shape, the LangSmith payload
transform, the CI regression gate, and the score reducer. The live seams
(`build_evaluators`, `build_langsmith_dataset`, `run_eval_suite`) are not
imported here — they need a judge model and a LangSmith key.
"""

from phase4.dataset import (
    CATEGORIES,
    EvalExample,
    count_by_category,
    dataset_examples,
    to_langsmith_payload,
)
from phase4.evaluators import DEFAULT_THRESHOLDS, check_thresholds
from phase4.run_eval import summarise_results

# --- dataset: the harness contract the build guide asks for ----------------


def test_dataset_meets_the_definition_of_done_minimums():
    counts = count_by_category(dataset_examples())
    total = sum(counts.values())
    # DoD: >=12 examples, >=2 expected-trajectory, >=2 out-of-scope/adversarial.
    assert total >= 12
    assert counts["trajectory"] >= 2
    assert counts["adversarial"] >= 2


def test_every_example_has_a_known_category():
    assert all(ex.category in CATEGORIES for ex in dataset_examples())


def test_policy_and_trajectory_examples_carry_a_reference_answer():
    # Correctness is judged against a reference, so these categories need one.
    for ex in dataset_examples():
        if ex.category in ("policy", "trajectory"):
            assert ex.reference, f"missing reference: {ex.inputs!r}"


def test_expected_trajectory_cases_name_the_tools_that_should_run():
    trajectory = [ex for ex in dataset_examples() if ex.category == "trajectory"]
    assert all(ex.expected_tools for ex in trajectory)


def test_dataset_includes_a_keyword_mismatch_retrieval_case():
    # The README requires >=1 question sharing no keywords with its source chunk.
    assert any(ex.keyword_mismatch for ex in dataset_examples())


def test_dataset_inputs_are_unique():
    inputs = [ex.inputs for ex in dataset_examples()]
    assert len(inputs) == len(set(inputs))


def test_dataset_examples_returns_a_fresh_list():
    first = dataset_examples()
    first.clear()
    assert len(dataset_examples()) >= 12


# --- to_langsmith_payload: the pure SDK transform --------------------------


def test_payload_omits_outputs_when_there_is_no_reference():
    example = EvalExample("hi", "adversarial")
    (payload,) = to_langsmith_payload([example])
    assert payload["inputs"] == {"question": "hi"}
    assert payload["outputs"] == {}


def test_payload_carries_reference_and_metadata():
    example = EvalExample(
        "q", "trajectory", reference="a", expected_tools=("get_office_status",)
    )
    (payload,) = to_langsmith_payload([example])
    assert payload["outputs"] == {"reference": "a"}
    assert payload["metadata"]["category"] == "trajectory"
    assert payload["metadata"]["expected_tools"] == ["get_office_status"]
    assert payload["metadata"]["keyword_mismatch"] is False


# --- check_thresholds: the CI regression gate ------------------------------


def test_gate_passes_when_every_metric_meets_its_band():
    scores = {"correctness": 0.9, "groundedness": 0.85, "trajectory": 0.95}
    assert check_thresholds(scores, DEFAULT_THRESHOLDS).passed


def test_gate_fails_and_reports_the_metric_below_its_band():
    scores = {"correctness": 0.5, "groundedness": 0.85, "trajectory": 0.95}
    result = check_thresholds(scores, DEFAULT_THRESHOLDS)
    assert not result.passed
    assert result.failures["correctness"] == (0.5, 0.80)


def test_gate_fails_closed_on_a_missing_metric():
    # A dropped evaluator must never launder a green gate.
    result = check_thresholds({"correctness": 0.99}, DEFAULT_THRESHOLDS)
    assert not result.passed
    assert "trajectory" in result.missing
    assert "groundedness" in result.missing


def test_gate_honours_a_custom_threshold_map():
    assert check_thresholds({"correctness": 0.6}, {"correctness": 0.5}).passed


# --- summarise_results: the score reducer ----------------------------------


def test_summarise_averages_each_metric_across_rows():
    rows = [
        {"correctness": 1.0, "trajectory": 1.0},
        {"correctness": 0.0, "trajectory": 1.0},
    ]
    assert summarise_results(rows) == {"correctness": 0.5, "trajectory": 1.0}


def test_summarise_averages_a_metric_only_over_rows_that_reported_it():
    rows = [{"correctness": 1.0}, {"trajectory": 0.0}]
    assert summarise_results(rows) == {"correctness": 1.0, "trajectory": 0.0}


def test_summarise_of_no_rows_is_empty():
    assert summarise_results([]) == {}
