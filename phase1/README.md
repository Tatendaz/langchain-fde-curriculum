# Phase 1 — Your first agent with `create_agent`

**Goal:** a single tool-calling **agent** that decides which tools to call (in a
loop) to finish a task — and shows up as **one nested trace** in LangSmith.

## What's different from Phase 0

Phase 0 wired the steps by hand, so you got *three separate* traces
(`ChatOllama`, `word_count`, `RunnableSequence`). Here, `create_agent` builds a
LangGraph agent that runs the model → tools → model loop for you, so the whole
run is **one nested trace**: agent → model → tool → model → … That tree is much
easier to debug, and seeing the contrast is the point of this phase.

## The agent

Three tools — two pure, one that makes a real HTTP call (no API key needed):

- `calculator(expression)` — evaluates basic arithmetic.
- `word_count(text)` — counts words.
- `fetch_url(url)` — real HTTP GET; returns status + first 2000 chars.

The sample task forces the agent to chain them:
> "Fetch https://example.com, count the words on the page, and compute 23 × 19."

## Run it

```bash
uv sync
uv run python -m phase1.agent
```

Uses the same repo-root `.env` as Phase 0 (local Ollama + your LangSmith key).
The model must support **tool calling**.

## What to look for in LangSmith

Find the single top-level agent run and expand it. You should see the model
deciding on tool calls, each tool execution nested underneath, and the model
being called again with the results — all in **one tree**, with per-step latency
and token counts.

## Test

```bash
uv run pytest
```

The tests cover the pure tools (`calculator`, `word_count`) offline; `fetch_url`
and the model call are verified by eye in the trace.

## ✅ Done when

You can point to one nested agent trace that shows the model calling
`fetch_url`, `word_count`, and `calculator` to complete the task.
