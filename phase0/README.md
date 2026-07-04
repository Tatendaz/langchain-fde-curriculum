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

## Phase gate — pass this before Phase 1

Three checks: **build**, **concepts**, **application**. Write (or say out loud)
your answer to each question *before* expanding the answer — recalling from
memory is what makes it stick, and it's what an interview or client call
demands. Miss more than one concept question? Re-run the code tomorrow and
retake the gate. That's the system working, not failing.

### 1 · Build check

- [ ] `uv run python -m phase0.hello_agent` runs clean and prints the
      structured result.
- [ ] In the LangSmith trace you can point to: **both model calls**, the
      **tool invocation** with its input and output, and **token counts +
      latency** per step.
- [ ] `uv run pytest tests/test_phase0.py` passes.

### 2 · Concept check *(closed book — no peeking at the code)*

**Q1.** The starter makes **two** model calls — one with `bind_tools`, one with
`with_structured_output`. What does each do, and why can't it be a single call?

<details><summary>Answer</summary>

Call 1 (`bind_tools`) advertises the tool's JSON schema to the model so it can
*decide* to use it — the reply is an `AIMessage` whose `tool_calls` field says
"run `word_count` with these args." **Your code** then executes the tool and
appends the result as a `ToolMessage`. Call 2 (`with_structured_output`) sends
the updated conversation back and constrains the reply to the `Analysis`
schema, returning a validated Pydantic object instead of prose.

It can't be one call because one API round-trip produces one assistant turn:
the model cannot request a tool *and* see that tool's result in the same
request — the result has to travel back to it in a second call. (Forcing the
`Analysis` schema on the first call would also have prevented the tool call
from being emitted at all.)

</details>

**Q2.** In the trace, the tool-calling turn shows the AI message content as
`""` (empty). If the model "did something," where did that something go, if
not into the content?

<details><summary>Answer</summary>

Into the `tool_calls` field of the `AIMessage`. Tool-calling models answer on
a separate, structured channel — a list of `{name, args, id}` — rather than in
the prose `content`. An empty `content` plus a populated `tool_calls` list *is*
the answer: "run this tool and come back to me." This is the single most
common thing that confuses trace-readers, which is why it's worth seeing on
day one.

</details>

**Q3.** Tracing only works when certain env vars are set. Which ones — and if
`LANGSMITH_API_KEY` is wrong or missing, does the agent still produce an
answer, or does it crash? Why?

<details><summary>Answer</summary>

`LANGSMITH_TRACING=true` switches tracing on and `LANGSMITH_API_KEY`
authenticates it (`LANGSMITH_PROJECT` only names the destination project).
With a bad or missing key the agent **still answers** — tracing is a fail-open
background export: runs are batched and shipped by a background thread, and
delivery failures are swallowed rather than raised. The design lesson carries
to everything you'll build: observability must never be able to take
production down.

</details>

### 3 · Apply it — an FDE scenario

> A client says: *"Our app already logs every request to stdout — why would we
> pay for LangSmith?"* You have 60 seconds.

<details><summary>What a strong answer covers</summary>

Logs give you lines; traces give you the **tree**. For every request you get
the exact prompt after templating, each tool call's args and result, per-step
tokens/latency/cost, and errors — linked, searchable, and shareable per
user/session. That structure is what makes debugging *non-deterministic* LLM
behavior tractable. And it compounds: any bad production trace can be turned
into a test case in an evaluation dataset (Phase 4), so today's bug becomes
tomorrow's regression test. Rebuilding that on stdout means rebuilding
LangSmith, badly. (If the client's real concern is data residency, note that
self-hosted options exist.)

</details>

### ✅ Gate passed?

All build boxes ticked, at least 2 of 3 concept answers substantially right,
and a scenario answer you'd be comfortable saying to a client — tick Phase 0
off in the [progress checklist](../README.md#progress-checklist) and start
[Phase 1](../phase1/README.md).
