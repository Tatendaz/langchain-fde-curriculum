"""Offline unit tests for Phase 2 (no model, no graph execution)."""

from langchain_core.messages import AIMessage, HumanMessage

from phase2.agent import (
    _TOOLS_BY_NAME,
    _WRITE_TOOLS,
    TOOLS,
    _last_text,
    _wants_tools,
    save_note,
)


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


def test_wants_tools_false_for_an_empty_tool_call_list():
    assert _wants_tools(AIMessage(content="", tool_calls=[])) is False


def test_wants_tools_false_when_the_message_has_no_tool_calls_attribute():
    # should_continue() runs on whatever the last message happens to be; a
    # message type without the attribute must route to END, not blow up.
    assert _wants_tools(HumanMessage(content="hi")) is False


def test_last_text_returns_the_stripped_final_message():
    state = {"messages": [AIMessage(content="first"), AIMessage(content="  done  ")]}
    assert _last_text(state) == "done"


def test_last_text_falls_back_when_the_model_returns_nothing():
    # Small local models often finish with empty content after a tool call.
    assert _last_text({"messages": [AIMessage(content="   ")]}) == (
        "(no final text — see the trace)"
    )


def test_write_tools_are_all_registered_tools():
    # The human-in-the-loop interrupt only fires for names in _WRITE_TOOLS. If a
    # write tool is added to TOOLS but not here (or is renamed on one side
    # only), the approval gate silently stops covering it.
    assert set(_TOOLS_BY_NAME) == {t.name for t in TOOLS}
    assert _WRITE_TOOLS <= set(_TOOLS_BY_NAME)
    assert "save_note" in _WRITE_TOOLS
