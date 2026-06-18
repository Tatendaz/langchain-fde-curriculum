"""Offline unit tests for Phase 0.

These cover the pure logic only — no API key or network required — so they run
fast and in CI. The LLM call itself is verified by eye via the LangSmith trace.
"""

from phase0.hello_agent import Analysis, word_count


def test_word_count_counts_words():
    assert word_count.invoke({"text": "the quick brown fox"}) == 4


def test_word_count_collapses_whitespace():
    assert word_count.invoke({"text": "  spaced   out  words "}) == 3


def test_word_count_empty_string():
    assert word_count.invoke({"text": ""}) == 0


def test_analysis_schema_validates():
    analysis = Analysis(word_count=9, summary="The sentence has nine words.")
    assert analysis.word_count == 9
    assert analysis.summary == "The sentence has nine words."
