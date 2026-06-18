"""Phase 1 — your first real agent with `create_agent`.

Where Phase 0 wired the steps by hand (and produced three *separate* traces),
this builds a single tool-calling agent that decides which tools to call, in a
loop, until the task is done. The whole run shows up as ONE nested trace in
LangSmith: agent -> model -> tool -> model -> ...

Run from the repo root:

    uv run python -m phase1.agent

Then open https://smith.langchain.com and expand the single agent trace.
"""

from __future__ import annotations

import ast
import operator
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool


# --- Tools ----------------------------------------------------------------
# Two pure/deterministic tools (easy to unit-test) and one that makes a real
# HTTP call (no API key needed) to show a genuinely external tool.

# A safe arithmetic evaluator: parse the expression to an AST and walk only a
# whitelist of numeric/operator nodes. This deliberately avoids eval(), which
# would let an LLM-supplied string execute arbitrary code.
_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}
_ALLOWED_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        return _ALLOWED_UNARYOPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("only numbers and + - * / // % operators are allowed")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '23 * 19' or '(2 + 3) / 4'."""
    try:
        return str(_eval_node(ast.parse(expression, mode="eval").body))
    except Exception as exc:  # surface the error back to the model
        return f"error: {exc}"


@tool
def word_count(text: str) -> int:
    """Count the number of whitespace-separated words in `text`."""
    return len(text.split())


@tool
def fetch_url(url: str) -> str:
    """HTTP GET a URL and return its status code plus the first 2000 characters."""
    try:
        resp = httpx.get(url, timeout=15, follow_redirects=True)
        return f"HTTP {resp.status_code}\n{resp.text[:2000]}"
    except Exception as exc:  # surface the error back to the model
        return f"error: {exc}"


def build_agent():
    """Build the agent. Kept separate from main() so tests can import the tools
    without constructing a model."""
    from langchain.agents import create_agent
    from langchain_ollama import ChatOllama

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

    return create_agent(
        llm,
        tools=[calculator, word_count, fetch_url],
        system_prompt=(
            "You are a helpful assistant. Use the provided tools when they help "
            "answer the question. Once you have the information you need, reply "
            "with a short final answer in plain text and do NOT call more tools."
        ),
    )


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    agent = build_agent()

    task = (
        "Fetch https://example.com, tell me how many words are in the page text, "
        "and also compute 23 * 19. Give me a short final answer."
    )
    result = agent.invoke({"messages": [{"role": "user", "content": task}]})
    messages = result["messages"]

    # Print a compact transcript of the loop so each tool call is visible even
    # when the model's final text is terse or empty.
    print("\n=== Agent steps ===")
    for m in messages:
        for call in getattr(m, "tool_calls", None) or []:
            print(f"  model -> tool: {call['name']}({call['args']})")
        if m.__class__.__name__ == "ToolMessage":
            preview = " ".join(str(m.content).split())[:80]
            print(f"  tool:{getattr(m, 'name', '?')} -> {preview}")

    final = messages[-1]
    answer = (getattr(final, "content", "") or "").strip()
    print("\n=== Final answer ===")
    print(answer or "(model returned no final text — open the trace to see the full loop)")

    project = os.getenv("LANGSMITH_PROJECT", "default")
    if os.getenv("LANGSMITH_TRACING", "").lower() == "true":
        print(
            f"\n✅ Traced as ONE nested run. Open https://smith.langchain.com, project "
            f"'{project}', and expand the agent trace to see every model + tool step."
        )


if __name__ == "__main__":
    main()
