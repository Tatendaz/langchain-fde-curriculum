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

## Prerequisites

You need an Ollama model that supports **tool calling**, plus a LangSmith key
for tracing.

- **Local Ollama:** install from <https://ollama.com>, then
  `ollama pull llama3.1` (or `qwen2.5`). No API key needed; `OLLAMA_BASE_URL`
  defaults to `http://localhost:11434`.
- **Ollama Cloud / remote:** set `OLLAMA_BASE_URL=https://ollama.com` and
  `OLLAMA_API_KEY=<your key>` in `.env` (sent as a Bearer token), and set
  `MODEL` to a cloud model such as `gpt-oss:20b`.

## Run it

```bash
uv sync                         # from the repo root: create the venv + install deps
cp .env.example .env            # then set your Ollama + LangSmith values
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

## Check your understanding

Answer these without re-reading the code:

1. The starter makes **two** model calls — one with `bind_tools`, one with
   `with_structured_output`. What does each do, and why not a single call?
2. In the trace, the tool-calling turn shows the AI message content as `""`
   (empty). If the model "did something," where did that something go, if not
   into the content?
3. Tracing only works when certain env vars are set. Which ones — and if
   `LANGSMITH_API_KEY` is wrong or missing, does the agent still produce an
   answer, or does it crash? Why?

## ✅ Done when

You can point to a LangSmith trace that shows the tool call and the structured
result.
