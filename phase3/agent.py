"""Phase 3 — a knowledge-base agent with long-term memory and an MCP tool.

Three production building blocks on top of the Phase 1/2 agent:

  * RAG — a tiny company handbook is chunked, embedded with Ollama, and stored in
    a vector store; `search_knowledge_base` retrieves the relevant passages.
  * Long-term memory — durable facts about the user are written to a LangGraph
    `Store` and recalled across threads (unlike the per-thread checkpointer).
  * MCP — tools served by a local MCP server (phase3/mcp_server.py) are loaded
    with langchain-mcp-adapters and handed to the agent like any other tool.

MCP tool loading is async, so the agent runs async (`ainvoke`).

Run from the repo root (needs `ollama pull nomic-embed-text` first):
    uv run python -m phase3.agent
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

# A tiny "company handbook" used as the RAG knowledge base.
KB_DOCS = [
    "Vacation policy: full-time employees accrue 25 days of paid time off per "
    "year. PTO must be requested at least two weeks in advance through the HR "
    "portal. Unused days roll over up to a maximum of 5 days into the next year.",
    "Remote work: employees may work remotely up to three days per week. A fully "
    "remote arrangement requires director approval and a signed remote-work "
    "agreement on file with HR.",
    "Expenses: reimbursable expenses include travel, client meals, and home-office "
    "equipment up to $500 per year. Submit receipts within 30 days through the "
    "finance portal or they will not be reimbursed.",
]

SYSTEM_PROMPT = (
    "You are a company assistant. Use search_knowledge_base for policy questions, "
    "save_memory to remember durable facts about the user, recall_memory to look "
    "them up, and the office-status tool for office hours. After using tools, "
    "give a short final answer."
)


def _chunk(docs: list[str], *, chunk_size: int = 200, chunk_overlap: int = 20) -> list[str]:
    """Split raw documents into overlapping chunks for embedding/retrieval."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks: list[str] = []
    for doc in docs:
        chunks.extend(splitter.split_text(doc))
    return chunks


async def build_agent():
    """Construct the async agent. Heavy imports live here so the module and its
    pure helpers import without a model, vector store, or MCP server running."""
    from langchain.agents import create_agent
    from langchain.tools import ToolRuntime, tool
    from langchain_core.vectorstores import InMemoryVectorStore
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_ollama import ChatOllama, OllamaEmbeddings
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.store.memory import InMemoryStore

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    api_key = os.getenv("OLLAMA_API_KEY")
    client_kwargs = {"headers": {"Authorization": f"Bearer {api_key}"}} if api_key else {}
    embeddings = OllamaEmbeddings(model=os.getenv("EMBED_MODEL", "nomic-embed-text"), base_url=base_url)

    # --- RAG: chunk -> embed -> store -> retrieve -------------------------
    vector_store = InMemoryVectorStore.from_texts(_chunk(KB_DOCS), embedding=embeddings)

    @tool
    def search_knowledge_base(query: str) -> str:
        """Search the company handbook for relevant policy text."""
        hits = vector_store.similarity_search(query, k=2)
        return "\n\n".join(d.page_content for d in hits) or "no matching policy found"

    # --- Long-term memory: durable, cross-thread facts about the user -----
    @tool
    def save_memory(content: str, runtime: ToolRuntime) -> str:
        """Save a durable fact about the user for future conversations."""
        runtime.store.put(("memories",), str(uuid.uuid4()), {"text": content})
        return "saved to long-term memory"

    @tool
    def recall_memory(runtime: ToolRuntime) -> str:
        """List durable facts previously saved about the user."""
        items = runtime.store.search(("memories",))
        return "\n".join(i.value["text"] for i in items) or "no memories saved yet"

    # --- MCP: tools served by a local stdio MCP server --------------------
    mcp_client = MultiServerMCPClient(
        {
            "office": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(Path(__file__).with_name("mcp_server.py"))],
            }
        }
    )
    mcp_tools = await mcp_client.get_tools()

    llm = ChatOllama(
        model=os.getenv("MODEL", "llama3.1"),
        temperature=0,
        base_url=base_url,
        client_kwargs=client_kwargs,
    )

    return create_agent(
        llm,
        tools=[search_knowledge_base, save_memory, recall_memory, *mcp_tools],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=MemorySaver(),  # per-thread short-term memory
        store=InMemoryStore(),       # cross-thread long-term memory
    )


def _last_text(state) -> str:
    msg = state["messages"][-1]
    return (getattr(msg, "content", "") or "").strip() or "(no final text — see the trace)"


async def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    agent = await build_agent()

    thread_a = {"configurable": {"thread_id": "user-jo"}}

    print("=== 1: policy question (RAG) + save a durable fact ===")
    state = await agent.ainvoke(
        {"messages": [{"role": "user", "content":
            "How many PTO days do I get? Also remember that I work in the London office."}]},
        thread_a,
    )
    print("final:", _last_text(state))

    print("\n=== 2: office hours (MCP tool) ===")
    state = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Is the London office open today?"}]},
        thread_a,
    )
    print("final:", _last_text(state))

    # Brand-new thread: the checkpointer can't help here, but the Store can.
    thread_b = {"configurable": {"thread_id": "user-jo-day2"}}
    print("\n=== 3: NEW thread — recall across the thread boundary (long-term memory) ===")
    state = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Which office did I tell you I work in?"}]},
        thread_b,
    )
    print("final:", _last_text(state))

    if os.getenv("LANGSMITH_TRACING", "").lower() == "true":
        print(f"\n✅ Traced — see project '{os.getenv('LANGSMITH_PROJECT', 'default')}' in LangSmith.")


if __name__ == "__main__":
    asyncio.run(main())
