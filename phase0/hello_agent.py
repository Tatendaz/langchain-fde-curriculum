"""Phase 0 — a traced "hello world".

A single run that (1) calls **one tool** and (2) returns **structured output**,
fully captured as a LangSmith trace.

Run it from the repo root:

    uv run python -m phase0.hello_agent

Then open https://smith.langchain.com and find the run under your
LANGSMITH_PROJECT to inspect every step.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field


# --- The tool -------------------------------------------------------------
# A pure, deterministic function so it's trivial to unit-test (see tests/).
@tool
def word_count(text: str) -> int:
    """Count the number of whitespace-separated words in `text`."""
    return len(text.split())


# --- The structured output schema -----------------------------------------
class Analysis(BaseModel):
    """The final, machine-readable answer the model must return."""

    word_count: int = Field(description="The word count returned by the tool.")
    summary: str = Field(description="A one-sentence, human-friendly summary.")


def main() -> None:
    load_dotenv()

    # Imported here (not at module top) so the module can be imported by the
    # tests without the provider package being installed.
    from langchain_ollama import ChatOllama

    # Local Ollama needs no key; Ollama Cloud / remote endpoints do. When a key
    # is present it's sent as a bearer token via the client's request headers.
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    api_key = os.getenv("OLLAMA_API_KEY")
    client_kwargs = {"headers": {"Authorization": f"Bearer {api_key}"}} if api_key else {}

    model_name = os.getenv("MODEL", "llama3.1")
    llm = ChatOllama(
        model=model_name,
        temperature=0,
        base_url=base_url,
        client_kwargs=client_kwargs,
    )

    question = (
        "How many words are in this sentence: "
        "'the quick brown fox jumps over the lazy dog'? "
        "Use the tool, then give me a short summary."
    )
    messages = [
        SystemMessage("You are a precise assistant. Use tools when they help."),
        HumanMessage(question),
    ]

    # --- Step 1: let the model decide to call the tool --------------------
    llm_with_tools = llm.bind_tools([word_count])
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)

    if not ai_msg.tool_calls:
        print("note: the model answered without calling the tool this time.")
    for call in ai_msg.tool_calls:
        result = word_count.invoke(call["args"])
        print(f"  tool: word_count({call['args']}) -> {result}")
        messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    # --- Step 2: ask for the final answer as a typed object ---------------
    structured_llm = llm.with_structured_output(Analysis)
    analysis = structured_llm.invoke(messages)

    print("\nStructured result:")
    print(f"  word_count = {analysis.word_count}")
    print(f"  summary    = {analysis.summary}")

    project = os.getenv("LANGSMITH_PROJECT", "default")
    if os.getenv("LANGSMITH_TRACING", "").lower() == "true":
        print(
            f"\n✅ Traced. Open https://smith.langchain.com and look in project "
            f"'{project}' to inspect the run."
        )
    else:
        print("\n⚠️  LANGSMITH_TRACING is not 'true' — set it in .env to capture traces.")


if __name__ == "__main__":
    main()
