# Phase 0 — Traced "hello world"

**Goal:** prove the whole loop works end to end — a chat call that **calls one
tool** and returns **structured output**, with the run **fully traced in
LangSmith**.

## What `hello_agent.py` does

1. Defines a tiny pure tool, `word_count(text)`.
2. Asks the model a question that needs the tool; the model emits a tool call.
3. Runs the tool and feeds the result back into the conversation.
4. Asks the model for a final answer as a typed `Analysis` (Pydantic) object.
5. Because `LANGSMITH_TRACING=true`, every step is captured as a trace.

## Run it

```bash
uv sync                         # from the repo root: create the venv + install deps
cp .env.example .env            # then fill in ANTHROPIC_API_KEY + LANGSMITH_API_KEY
uv run python -m phase0.hello_agent
```

Expected output: the tool result, then a structured `word_count` + `summary`,
then a link to LangSmith.

## What to look for in LangSmith

Open <https://smith.langchain.com>, pick the project named in
`LANGSMITH_PROJECT`, and open the latest run. You should see:

- the **two model calls** (the tool-calling turn and the structured-output turn),
- the **tool invocation** with its inputs and outputs,
- **token counts and latency** for each step.

Reading this trace fluently is the core skill — you'll lean on it in every phase
after this one.

## Test

```bash
uv run pytest
```

The tests cover the pure logic (`word_count`, the `Analysis` schema) without
calling the API, so they run offline and in CI.

## ✅ Done when

You can point to a LangSmith trace that shows the tool call and the structured
result.
