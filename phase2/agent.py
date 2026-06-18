"""Phase 2 — the agent rebuilt as an explicit LangGraph StateGraph.

Phase 1 used `create_agent` (the high-level wrapper). Phase 2 builds the same
model -> tools -> model loop by hand, so the machinery is visible, and adds two
things production agents need:

  * Persistence — a checkpointer stores state per `thread_id`, so the agent
    remembers across separate invocations (see the follow-up question below).
  * Human-in-the-loop — the `save_note` WRITE tool is gated behind an
    `interrupt()`; the graph pauses for approval before performing the write.

Run from the repo root:
    uv run python -m phase2.agent
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.tools import tool

# Reuse the read-only tools from Phase 1.
from phase1.agent import calculator, fetch_url, word_count

SYSTEM_PROMPT = (
    "You are a helpful assistant. Use the provided tools when they help. Once "
    "you have what you need, reply with a short final answer and do not call "
    "more tools."
)


# --- A WRITE tool, gated behind human approval ----------------------------
@tool
def save_note(content: str) -> str:
    """Save a note to the user's notebook. This is a WRITE action."""
    # In a real app this would persist to a DB/file; here we just confirm.
    return f"saved note: {content!r}"


TOOLS = [calculator, word_count, fetch_url, save_note]
_TOOLS_BY_NAME = {t.name: t for t in TOOLS}
_WRITE_TOOLS = {"save_note"}


def _wants_tools(message) -> bool:
    """True when the model's latest message has pending tool calls."""
    return bool(getattr(message, "tool_calls", None))


def build_graph(checkpointer=None):
    """Build and compile the agent graph. langgraph and the model are imported
    here so the module (and its pure helpers) import without them configured."""
    from langchain_ollama import ChatOllama
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import END, START, MessagesState, StateGraph
    from langgraph.types import interrupt

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    api_key = os.getenv("OLLAMA_API_KEY")
    client_kwargs = {"headers": {"Authorization": f"Bearer {api_key}"}} if api_key else {}
    model_name = os.getenv("MODEL", "llama3.1")
    llm = ChatOllama(model=model_name, temperature=0, base_url=base_url, client_kwargs=client_kwargs)
    llm_with_tools = llm.bind_tools(TOOLS)

    def agent(state):
        # Prepend the system prompt for the model call without storing it in state.
        response = llm_with_tools.invoke([SystemMessage(SYSTEM_PROMPT), *state["messages"]])
        return {"messages": [response]}

    def tools_with_approval(state):
        calls = state["messages"][-1].tool_calls

        # Request approval for any WRITE calls FIRST. interrupt() must come
        # before side effects, because the node re-runs from the top on resume.
        approvals = {
            tc["id"]: interrupt({"tool": tc["name"], "args": tc["args"]})
            for tc in calls
            if tc["name"] in _WRITE_TOOLS
        }

        out = []
        for tc in calls:
            if tc["name"] in _WRITE_TOOLS and approvals.get(tc["id"]) != "approve":
                result = "rejected by human; write not performed"
            else:
                result = _TOOLS_BY_NAME[tc["name"]].invoke(tc["args"])
            out.append(ToolMessage(content=str(result), tool_call_id=tc["id"], name=tc["name"]))
        return {"messages": out}

    def should_continue(state):
        return "tools" if _wants_tools(state["messages"][-1]) else END

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent)
    builder.add_node("tools", tools_with_approval)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, ["tools", END])
    builder.add_edge("tools", "agent")

    return builder.compile(checkpointer=checkpointer or MemorySaver())


def _last_text(state) -> str:
    msg = state["messages"][-1]
    return (getattr(msg, "content", "") or "").strip() or "(no final text — see the trace)"


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    from langgraph.types import Command

    graph = build_graph()
    thread = {"configurable": {"thread_id": "demo-1"}}

    # --- Run 1: a write that must be approved -----------------------------
    print("=== Run 1: ask the agent to save a note (write -> approval gate) ===")
    state = graph.invoke(
        {"messages": [{"role": "user", "content": "Save a note that says: Phase 2 works!"}]},
        thread,
    )

    while "__interrupt__" in state:
        request = state["__interrupt__"][0].value
        print(f"PAUSED — approval needed: {request}")
        print("   -> approving")
        state = graph.invoke(Command(resume="approve"), thread)

    print("final:", _last_text(state))

    # --- Run 2: same thread -> the agent remembers (persistence) ----------
    print("\n=== Run 2: follow-up in the SAME thread (persistence) ===")
    state = graph.invoke(
        {"messages": [{"role": "user", "content": "What did I just ask you to save?"}]},
        thread,
    )
    print("final:", _last_text(state))

    if os.getenv("LANGSMITH_TRACING", "").lower() == "true":
        project = os.getenv("LANGSMITH_PROJECT", "default")
        print(f"\n✅ Traced. See project '{project}' at https://smith.langchain.com — the two")
        print("   runs share one thread, and the write paused at the approval interrupt.")


if __name__ == "__main__":
    main()
