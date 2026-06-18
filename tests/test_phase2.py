"""Offline unit tests for Phase 2 (no model, no graph execution)."""

from langchain_core.messages import AIMessage

from phase2.agent import _wants_tools, save_note


def test_save_note_confirms():
    assert save_note.invoke({"content": "hello"}) == "saved note: 'hello'"


def test_wants_tools_true_with_tool_calls():
    msg = AIMessage(
        content="",
        tool_calls=[{"name": "save_note", "args": {"content": "x"}, "id": "call_1"}],
    )
    assert _wants_tools(msg) is True


def test_wants_tools_false_without_tool_calls():
    assert _wants_tools(AIMessage(content="all done")) is False
