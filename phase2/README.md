# Phase 2 — The agent, rebuilt in LangGraph

**Goal:** rebuild the Phase 1 agent as an explicit `StateGraph`, and add the two
things production agents need: **persistence** and a **human approval gate**.

## What's new vs Phase 1

Phase 1 used `create_agent` (the high-level wrapper). Phase 2 builds the same
model → tools → model loop by hand, so you can see and control the machinery:

- **Explicit graph** — an `agent` node and a custom tools node, wired with a
  conditional edge (`should_continue`) that loops until the model stops calling
  tools. (LangGraph ships a prebuilt `ToolNode`; we use a custom node here
  because it lets us gate writes — and because `interrupt()` inside a `ToolNode`
  has a known resume-routing bug.)
- **Persistence** — the graph is compiled with a **checkpointer** (`MemorySaver`)
  and invoked with a `thread_id`. State is saved per thread, so a follow-up
  question in the same thread *remembers* the conversation.
- **Human-in-the-loop** — the `save_note` **write** tool is gated behind
  `interrupt()`. The graph pauses, surfaces the pending write for approval, and
  only performs it after you resume with `Command(resume="approve")`.

## Run it

```bash
uv run python -m phase2.agent
```

Two runs share thread `demo-1`:
1. *"Save a note that says: Phase 2 works!"* → the graph **pauses** at the
   approval interrupt; the demo approves it and the write completes.
2. *"What did I just ask you to save?"* → answered from **persisted** thread
   state, with no re-prompting.

## Going to production

- **Postgres persistence:** swap `MemorySaver` for `PostgresSaver`
  (`pip install langgraph-checkpoint-postgres`) so state survives restarts and is
  shared across instances — `build_graph(checkpointer=...)` already accepts one.
- **Streaming:** use `graph.stream(..., stream_mode="updates")` to surface each
  node's output as it happens.
- **Reject path:** resume with `Command(resume="reject")` to watch the write get
  declined instead.

## Test

```bash
uv run pytest
```

## Check your understanding

Answer these without re-reading the code:

1. Run 2 "remembered" the conversation without you re-sending the history. What
   provided that, and what is the role of `thread_id`?
2. Where does `interrupt()` pause the graph, and what does
   `Command(resume="approve")` actually feed back into the paused node? Why is a
   checkpointer *required* for interrupts to work?
3. The approval gate used a **custom** tools node instead of the prebuilt
   `ToolNode`. Give one concrete reason that mattered here.
4. In the run, the interrupt fired twice. Why? And why must `interrupt()` be
   called *before* any side effect in the node (what happens to the node when you
   resume)?

## ✅ Done when

You can point to a trace where the write paused for approval, and a second run in
the same thread answered from memory.
