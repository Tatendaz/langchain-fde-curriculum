# Phase 3 — Knowledge base + long-term memory + an MCP tool

**Goal:** give the agent (1) a real **knowledge base** it can search, (2)
**long-term memory** that survives across threads, and (3) a tool served over
**MCP**.

## What's in the agent

- **RAG** — `KB_DOCS` (a tiny company handbook) is chunked, embedded with Ollama
  (`nomic-embed-text`), and stored in an `InMemoryVectorStore`. The
  `search_knowledge_base` tool retrieves the most relevant passages.
- **Long-term memory** — `save_memory` / `recall_memory` write to and read from a
  LangGraph **`Store`** via the injected `ToolRuntime`. Unlike Phase 2's
  checkpointer (scoped to one `thread_id`), the store is shared across threads —
  so a fact saved in one conversation is recalled in a brand-new one.
- **MCP** — `phase3/mcp_server.py` is a tiny stdio MCP server exposing
  `get_office_status`. `MultiServerMCPClient` launches it and converts its tools
  into LangChain tools. Because tool loading is async, the agent runs with
  `ainvoke`.

## Prerequisites

```bash
ollama pull nomic-embed-text     # embeddings for the knowledge base
# plus your usual tool-calling MODEL from the root .env
```

## Run it

```bash
uv run python -m phase3.agent
```

The demo asks a PTO question (RAG) and saves "I work in the London office"
(memory) on thread A, checks office status (MCP) on thread A, then on a **new
thread** asks "which office did I say I work in?" — answered from long-term
memory, across the thread boundary.

## Going to production

- **Vector store:** swap `InMemoryVectorStore` for `pgvector`
  (`langchain-postgres`); add hybrid search + a reranker for retrieval quality.
- **Memory store:** swap `InMemoryStore` for `PostgresStore`, and add a semantic
  index (`IndexConfig(embed=..., dims=...)`) so `store.search(query=...)` ranks
  memories by similarity instead of listing them.
- **MCP:** point `MultiServerMCPClient` at real servers (filesystem, GitHub, your
  own). stdio is for local subprocesses like this demo; **streamable HTTP** is
  the standard transport for remote servers (the older HTTP+SSE transport is
  deprecated).

## Test

```bash
uv run pytest
```

Offline tests cover the chunker and the MCP server's tool logic; the model,
embeddings, and MCP subprocess are exercised only when you run the agent.

## Phase gate — pass this before Phase 4

Write your answers *before* expanding the blocks. The scenario question here
is the one most likely to come up in a real engagement — don't skip it.

### 1 · Build check

- [ ] `uv run python -m phase3.agent` answers the PTO question **from the
      knowledge base**, calls the **MCP** office tool, and recalls the saved
      office **on a new thread**.
- [ ] In the LangSmith trace you can point to the `search_knowledge_base` call
      and show which retrieved chunks the answer came from.
- [ ] `uv run pytest tests/test_phase3.py` passes.
- [ ] *(Stretch)* You added a query that retrieval handles *badly* (wrong or
      irrelevant chunk retrieved) and can explain why — you'll measure exactly
      this in Phase 4.

### 2 · Concept check *(closed book)*

**Q1.** The checkpointer (Phase 2) and the `Store` (Phase 3) both "remember"
things. What's the difference in **scope**, and which one lets a brand-new
thread recall a fact saved earlier? Why?

<details><summary>Answer</summary>

The checkpointer is **short-term, per-thread**: state is keyed by `thread_id`,
so a new thread starts empty. The `Store` is **long-term, cross-thread**: a
namespaced key-value store attached to the whole graph, reachable from any
thread via the injected `ToolRuntime`. The new thread recalled the office
because `recall_memory` reads the Store — not the thread's message history.
Rule of thumb: conversation state → checkpointer; durable facts that should
outlive the conversation → Store.

</details>

**Q2.** Why does adding MCP force the whole agent to become **async**
(`await client.get_tools()`, `ainvoke`) when Phases 1–2 were synchronous?

<details><summary>Answer</summary>

Phases 1–2 tools were plain in-process Python functions. MCP tools live in a
**separate process** — here a stdio subprocess, in production often a remote
HTTP server. The MCP Python SDK is async-first: the session handshake, tool
discovery (`get_tools()`), and every tool invocation are awaitable I/O
operations. The adapter therefore surfaces async tools, and the agent must run
inside an event loop (`ainvoke`) so those awaits can actually happen. General
pattern: the moment tools cross a process boundary, your agent is a
distributed system — async, timeouts, and failures included.

</details>

**Q3.** `search_knowledge_base` can find a relevant passage even when the
query shares no exact words with the document. What makes that possible, and
what is `nomic-embed-text` actually producing to enable it?

<details><summary>Answer</summary>

Embeddings. `nomic-embed-text` maps each chunk — and, at query time, the
question — to a dense fixed-length vector (768 floats) positioned so that
semantically similar text lands close together. `similarity_search` returns
the nearest chunks by cosine similarity. "How many days off do I get?" sits
near the vacation-policy chunk in that space despite zero keyword overlap,
because the space encodes *meaning*, not spelling. The flip side — retrieval
can also surface something plausible-but-wrong — is why retrieval quality gets
measured, not assumed (Phase 4).

</details>

### 3 · Apply it — an FDE scenario

> You ship this agent to a client. Two weeks later they call: *"User A asked
> 'which office do I work in?' and the bot answered with **User B's**
> office."* What did you forget, and what's the fix?

<details><summary>What a strong answer covers</summary>

Memories were saved to a **global namespace** — `("memories",)` — which is
exactly what this phase's demo does as a simplification. Every user shares one
memory pool. The fix is to scope the namespace per user:
`("memories", user_id)` on both `put` and `search`, with `user_id` coming from
your **auth layer** (e.g. passed through the graph's config/context) — never
from the model, which can be talked into claiming to be someone else. The
generalization is the real lesson: *every* shared resource an agent touches —
memory store, vector DB, cache, files — needs a tenant key enforced outside
the prompt. Multi-tenant isolation is one of the first questions enterprise
clients ask.

</details>

### ✅ Gate passed?

Tick Phase 3 off in the [progress checklist](../README.md#progress-checklist)
and move to [Phase 4](../phase4/README.md) — proving the agent works.
