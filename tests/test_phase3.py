"""Offline unit tests for Phase 3 (no model, embeddings, or MCP subprocess)."""

from phase3.agent import KB_DOCS, _chunk
from phase3.mcp_server import _office_status


def test_chunk_splits_into_more_pieces():
    chunks = _chunk(KB_DOCS, chunk_size=120, chunk_overlap=10)
    assert len(chunks) > len(KB_DOCS)
    assert all(isinstance(c, str) and c for c in chunks)


def test_office_status_known():
    assert "open" in _office_status("London").lower()


def test_office_status_unknown():
    assert "unknown" in _office_status("atlantis").lower()
