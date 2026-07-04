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
- **Naming note:** docs now call the in-memory checkpointer `InMemorySaver`
  (`MemorySaver` remains as an alias). And the packaged
  `HumanInTheLoopMiddleware` (Phase 5) does what your custom gate does here —
  you build it by hand once so the packaged version is never magic.

## Test

```bash
uv run pytest
```

## Phase gate — pass this before Phase 3

This is the most important gate in the curriculum: everything you ship later
sits on this machinery. Write your answers *before* expanding the blocks.

### 1 · Build check

- [ ] `uv run python -m phase2.agent` shows the write **pausing** for
      approval, completing after approve, and Run 2 answering **from memory**
      in the same thread.
- [ ] You ran the **reject** path (`Command(resume="reject")`) and watched the
      model receive the refusal instead of the write happening.
- [ ] In LangSmith you can point to the interrupt pause and the resumed
      completion.
- [ ] `uv run pytest tests/test_phase2.py` passes.
- [ ] *(Stretch)* You swapped `MemorySaver` for `PostgresSaver` (Docker
      Postgres is fine) and state survived a process restart.

### 2 · Concept check *(closed book)*

**Q1.** Run 2 "remembered" the conversation without you re-sending the
history. What provided that, and what is the role of `thread_id`?

<details><summary>Answer</summary>

The **checkpointer**. After every step LangGraph checkpoints the graph state
(here, the message list) keyed by `thread_id`; invoking the same thread loads
that saved state, so the new question is appended to the existing
conversation. `thread_id` is just the lookup key that selects which
conversation to resume — a different id starts from a blank slate. This is
"short-term memory," and its scope boundary (per-thread) is exactly what
Phase 3's `Store` exists to cross.

</details>

**Q2.** Where does `interrupt()` pause the graph, and what does
`Command(resume="approve")` actually feed back into the paused node? Why is a
checkpointer *required* for interrupts to work?

<details><summary>Answer</summary>

It pauses inside the `tools_with_approval` node, at the `interrupt()` call —
the graph checkpoints its exact state and returns control to you with
`__interrupt__` in the result. `Command(resume="approve")` re-invokes the
thread; the node **re-runs from the top**, and this time `interrupt()`
*returns* your resume value (`"approve"`) instead of pausing, so execution
proceeds to the write. A checkpointer is mandatory because "pausing" *is*
persisting: the saved checkpoint is the only thing that lets the graph be
reloaded and replayed later — no checkpoint, nothing to resume from.

</details>

**Q3.** The approval gate used a **custom** tools node instead of the prebuilt
`ToolNode`. Give one concrete reason that mattered here.

<details><summary>Answer</summary>

The policy lives *inside* tool execution, so we needed control there: call
`interrupt()` per write-tool call *before* executing anything, inject a
`"rejected by human"` `ToolMessage` on decline (so the model hears the refusal
and can react), and leave read-only tools ungated. (This repo also avoids a
known resume-routing bug with `interrupt()` inside the prebuilt `ToolNode`.)
The transferable lesson: prebuilt components are fine until you need *policy*
inside the node — then you write the node yourself.

</details>

**Q4.** When you resume an interrupted run, the `interrupt()` line executes
**again**. Explain why — and therefore why `interrupt()` must come *before*
any side effect in the node. (Depending on the model, you may also see the
pause fire more than once per request — why?)

<details><summary>Answer</summary>

Resuming does not continue the node mid-function — the node **re-runs from the
top**, and `interrupt()` returns the injected resume value on the replay
instead of raising. That replay semantics is the whole answer: any code placed
*before* `interrupt()` executes once when the node first runs and **again** on
resume. Put a database write before the interrupt and you've written twice —
before approval was even granted. Hence: gate first, act second. And if the
model batches or retries multiple write calls, each unapproved call raises its
own interrupt — one `Command(resume=...)` answers exactly one pending
approval, so you loop until the state has no `__interrupt__` left (which is
why the demo uses a `while` loop).

</details>

### 3 · Apply it — an FDE scenario

> A client says: *"The agent must never email a customer without human
> sign-off — and approvals can take hours, people go to lunch."* What do you
> propose? And what breaks if the server restarts while an approval is
> pending?

<details><summary>What a strong answer covers</summary>

Gate the email tool behind `interrupt()`. A pending approval is just a
checkpoint row — no process sits blocked, so an approval that takes four hours
costs nothing; the approve/reject button in their UI simply calls resume on
that thread. The restart question is the trap: with `MemorySaver` the paused
state lives in process memory, so a restart **loses the pending approval**.
Production uses `PostgresSaver`: the thread and its pending interrupt survive
restarts and any replica can resume it. One precision worth volunteering: the
persisted thread shows each pending write and the decision it got, but it does
**not** record *who* approved or when — approver identity and timestamps come
from your app's auth layer and get logged alongside. This — durable approval
workflows, not chat memory — is why enterprises treat checkpointing as
non-negotiable.

</details>

### ✅ Gate passed?

Tick Phase 2 off in the [progress checklist](../README.md#progress-checklist)
and move to [Phase 3](../phase3/README.md) — knowledge and memory.
