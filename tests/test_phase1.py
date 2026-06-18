"""Offline unit tests for Phase 1 tools (no model, no network)."""

from phase1.agent import calculator, word_count


def test_calculator_basic():
    assert calculator.invoke({"expression": "23 * 19"}) == "437"


def test_calculator_handles_parentheses():
    assert calculator.invoke({"expression": "(2 + 3) * 4"}) == "20"


def test_calculator_rejects_non_arithmetic():
    out = calculator.invoke({"expression": "__import__('os').system('ls')"})
    assert out.startswith("error:")


def test_word_count():
    assert word_count.invoke({"text": "the quick brown fox"}) == 4
