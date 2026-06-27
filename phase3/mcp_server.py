"""A minimal local MCP server (stdio) for Phase 3 — exposes one tool.

`MultiServerMCPClient` in phase3/agent.py launches this file as a subprocess and
turns `get_office_status` into a LangChain tool the agent can call.

Run directly to sanity-check it speaks MCP over stdio:
    uv run python phase3/mcp_server.py   # (it will wait for an MCP client)
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("phase3-office")


def _office_status(office: str) -> str:
    """Pure helper (unit-tested) — today's open/closed status for an office."""
    statuses = {
        "london": "open until 6pm GMT",
        "tokyo": "closed today (public holiday)",
        "nyc": "open 24/7",
    }
    return statuses.get(office.strip().lower(), f"unknown office: {office!r}")


@mcp.tool()
def get_office_status(office: str) -> str:
    """Return today's open/closed status for a named office (london, tokyo, nyc)."""
    return _office_status(office)


if __name__ == "__main__":
    mcp.run(transport="stdio")
