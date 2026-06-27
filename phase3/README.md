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
  own) over stdio or HTTP.

## Test

```bash
uv run pytest
```

Offline tests cover the chunker and the MCP server's tool logic; the model,
embeddings, and MCP subprocess are exercised only when you run the agent.

## Check your understanding

Answer these without re-reading the code — they test whether the phase landed:

1. The checkpointer (Phase 2) and the `Store` (Phase 3) both "remember" things.
   What's the difference in **scope**, and which one lets a brand-new thread
   recall a fact saved earlier? Why?
2. Why does adding MCP force the whole agent to become **async** (`await
   client.get_tools()`, `ainvoke`) when Phases 1–2 were synchronous?
3. `search_knowledge_base` can find a relevant passage even when the query shares
   no exact words with the document. What makes that possible, and what is
   `nomic-embed-text` actually producing to enable it?

## ✅ Done when

You can run the agent and watch it answer a policy question from the knowledge
base, call the MCP office tool, and recall the saved office on a new thread.
