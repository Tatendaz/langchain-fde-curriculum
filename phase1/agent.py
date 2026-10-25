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
import ipaddress
import operator
import os
import socket
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


# The model picks the URL, and it composes tool arguments from text it read,
# so a fetched page can ask it to fetch http://169.254.169.254/ (cloud
# metadata) or a service on localhost. Only public addresses are allowed. The
# request goes to the exact address that was checked (the name stays in the
# Host header and the TLS certificate check), so a DNS answer that changes
# after the check cannot swap in a private address. Redirects are not
# followed: a redirect comes back to the model as a new URL, which goes
# through the same check on the next call.
def _public_addresses(host: str) -> list[str]:
    """Return every address of `host` if all of them are public, else []."""
    try:
        addrs = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        except OSError:
            return []
        addrs = [ipaddress.ip_address(info[4][0]) for info in infos]
    if not addrs or not all(addr.is_global for addr in addrs):
        return []
    return list(dict.fromkeys(str(addr) for addr in addrs))


@tool
def fetch_url(url: str) -> str:
    """HTTP GET a public http(s) URL and return its status code plus the first 2000 characters."""
    try:
        parsed = httpx.URL(url)
        # raw_host is the ASCII (punycode) form; headers and SNI must be ASCII.
        host = parsed.raw_host.decode("ascii")
        addresses = _public_addresses(host) if parsed.scheme in ("http", "https") else []
        if not addresses:
            return "error: only public http(s) addresses can be fetched"
        name = f"[{host}]" if ":" in host else host
        host_header = f"{name}:{parsed.port}" if parsed.port else name
        extensions = {"sni_hostname": host} if parsed.scheme == "https" else {}
        # trust_env=False: through an HTTPS_PROXY tunnel, httpx checks the
        # certificate against the IP and ignores sni_hostname, so every https
        # fetch would fail. It also skips SSL_CERT_FILE and NETRC.
        # Try each checked address in order, like a normal connect would, so a
        # host whose first answer is unreachable (say, IPv6 with no route)
        # still works.
        with httpx.Client(timeout=15, follow_redirects=False, trust_env=False) as client:
            for i, address in enumerate(addresses):
                try:
                    resp = client.get(
                        parsed.copy_with(host=address),
                        headers={"Host": host_header},
                        extensions=extensions,
                    )
                    break
                except httpx.ConnectError:
                    if i == len(addresses) - 1:
                        raise
        if resp.is_redirect:
            target = parsed.join(resp.headers.get("location", ""))
            return f"HTTP {resp.status_code}\nredirects to {target}"
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
