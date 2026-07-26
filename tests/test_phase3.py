"""Offline unit tests for Phase 3 (no model, embeddings, or MCP subprocess)."""

from phase3.agent import KB_DOCS, _chunk, _last_text
from phase3.mcp_server import _office_status


def test_chunk_splits_into_more_pieces():
    chunks = _chunk(KB_DOCS, chunk_size=120, chunk_overlap=10)
    assert len(chunks) > len(KB_DOCS)
    assert all(isinstance(c, str) and c for c in chunks)


def test_chunk_respects_the_requested_chunk_size():
    # Chunks larger than the embedding window are the classic silent RAG bug.
    chunks = _chunk(KB_DOCS, chunk_size=120, chunk_overlap=10)
    assert max(len(c) for c in chunks) <= 120


def test_chunk_of_no_documents_is_empty():
    assert _chunk([]) == []


def test_office_status_known():
    assert "open" in _office_status("London").lower()


def test_office_status_unknown():
    assert "unknown" in _office_status("atlantis").lower()


def test_office_status_answers_for_every_documented_office():
    # The tool docstring promises london, tokyo and nyc.
    for office in ("london", "tokyo", "nyc"):
        assert "unknown" not in _office_status(office).lower()


def test_office_status_normalises_case_and_surrounding_whitespace():
    assert _office_status("  LonDon  ") == _office_status("london")


def test_last_text_returns_the_stripped_final_message():
    class _Msg:
        content = "  the office is open  "

    assert _last_text({"messages": [_Msg()]}) == "the office is open"


def test_last_text_falls_back_when_the_model_returns_nothing():
    class _Msg:
        content = ""

    assert _last_text({"messages": [_Msg()]}) == "(no final text — see the trace)"
