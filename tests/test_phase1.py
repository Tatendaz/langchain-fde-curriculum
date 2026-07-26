"""Offline unit tests for Phase 1 tools (no model, no network).

`fetch_url` is the one tool in the curriculum that makes a real HTTP call, so
its tests replace the transport (`httpx.get`) with a stub instead of reaching
the network. Nothing here needs Ollama, an API key, or connectivity — that is
the standing rule for this repo's suite (see CONTRIBUTING.md).
"""

import httpx
import pytest

from phase1.agent import calculator, fetch_url, word_count


def _stub_get(monkeypatch, *, response=None, error=None):
    """Point `httpx.get` at a canned response (or error) and record the call.

    Returns the list of recorded calls so a test can assert *how* the request
    was made, not just what came back. A real `httpx.Response` is used rather
    than a mock, so `.status_code` / `.text` behave exactly as in production.
    """
    calls = []

    def fake_get(url, **kwargs):
        calls.append({"url": url, **kwargs})
        if error is not None:
            raise error
        return response

    monkeypatch.setattr(httpx, "get", fake_get)
    return calls


# --- calculator -----------------------------------------------------------


def test_calculator_basic():
    assert calculator.invoke({"expression": "23 * 19"}) == "437"


def test_calculator_handles_parentheses():
    assert calculator.invoke({"expression": "(2 + 3) * 4"}) == "20"


def test_calculator_rejects_non_arithmetic():
    out = calculator.invoke({"expression": "__import__('os').system('ls')"})
    assert out.startswith("error:")


def test_calculator_handles_division_and_negatives():
    assert calculator.invoke({"expression": "-10 / 4"}) == "-2.5"


def test_calculator_rejects_the_power_operator():
    # `**` is deliberately absent from _ALLOWED_BINOPS: `9**9**9` is a one-line
    # denial of service for a tool whose argument is written by a model.
    assert calculator.invoke({"expression": "9 ** 9"}).startswith("error:")


def test_calculator_reports_division_by_zero_instead_of_raising():
    # Tool errors must come back as text the model can read and recover from,
    # not as an exception that kills the agent loop.
    assert calculator.invoke({"expression": "1 / 0"}).startswith("error:")


# --- word_count -----------------------------------------------------------


def test_word_count():
    assert word_count.invoke({"text": "the quick brown fox"}) == 4


# --- fetch_url ------------------------------------------------------------


def test_fetch_url_returns_status_and_body(monkeypatch):
    _stub_get(monkeypatch, response=httpx.Response(200, text="hello world"))
    assert fetch_url.invoke({"url": "https://example.com"}) == "HTTP 200\nhello world"


def test_fetch_url_truncates_long_bodies_to_2000_chars(monkeypatch):
    # The cap exists so a large page cannot blow up the model's context window.
    _stub_get(monkeypatch, response=httpx.Response(200, text="x" * 5000))
    header, body = fetch_url.invoke({"url": "https://example.com"}).split("\n", 1)
    assert header == "HTTP 200"
    assert body == "x" * 2000


def test_fetch_url_reports_non_2xx_status_without_raising(monkeypatch):
    _stub_get(monkeypatch, response=httpx.Response(404, text="nope"))
    assert fetch_url.invoke({"url": "https://example.com/missing"}) == "HTTP 404\nnope"


def test_fetch_url_returns_an_error_string_on_network_failure(monkeypatch):
    _stub_get(monkeypatch, error=httpx.ConnectError("connection refused"))
    out = fetch_url.invoke({"url": "https://example.com"})
    assert out.startswith("error:")
    assert "connection refused" in out


def test_fetch_url_follows_redirects_and_sets_a_timeout(monkeypatch):
    # An agent tool with no timeout is how a run hangs forever; pin the contract.
    calls = _stub_get(monkeypatch, response=httpx.Response(200, text="ok"))
    fetch_url.invoke({"url": "https://example.com/redirect"})
    assert calls == [
        {"url": "https://example.com/redirect", "timeout": 15, "follow_redirects": True}
    ]


def test_fetch_url_makes_exactly_one_request(monkeypatch):
    calls = _stub_get(monkeypatch, response=httpx.Response(200, text="ok"))
    fetch_url.invoke({"url": "https://example.com"})
    assert len(calls) == 1


@pytest.mark.parametrize("scheme", ["http", "https"])
def test_fetch_url_passes_the_url_through_unmodified(monkeypatch, scheme):
    url = f"{scheme}://example.com/a/b?q=1&r=2"
    calls = _stub_get(monkeypatch, response=httpx.Response(200, text="ok"))
    fetch_url.invoke({"url": url})
    assert calls[0]["url"] == url
