"""Offline unit tests for Phase 1 tools (no model, no network).

`fetch_url` is the one tool in the curriculum that makes a real HTTP call, so
its tests replace the transport (`httpx.get`) with a stub instead of reaching
the network. Nothing here needs Ollama, an API key, or connectivity — that is
the standing rule for this repo's suite (see CONTRIBUTING.md).
"""

import socket

import httpx
import pytest

from phase1.agent import calculator, fetch_url, word_count


def _stub_get(monkeypatch, *, response=None, error=None):
    """Point `httpx.Client.get` at a canned response (or error) and record the call.

    Returns the list of recorded calls so a test can assert *how* the request
    was made, not just what came back. A real `httpx.Response` is used rather
    than a mock, so `.status_code` / `.text` behave exactly as in production.
    """
    calls = []

    def fake_get(client, url, **kwargs):
        calls.append(
            {
                "url": str(url),
                "timeout": client.timeout.read,
                "follow_redirects": client.follow_redirects,
                **kwargs,
            }
        )
        if error is not None:
            raise error
        return response

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    return calls


@pytest.fixture(autouse=True)
def _offline_dns(monkeypatch):
    """Answer DNS without the network: localhost is loopback, every other name
    gets a public address (example.com's)."""

    def fake_getaddrinfo(host, port, *args, **kwargs):
        ip = "127.0.0.1" if host == "localhost" else "93.184.215.14"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)


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


def test_fetch_url_sets_a_timeout_and_does_not_follow_redirects(monkeypatch):
    # An agent tool with no timeout is how a run hangs forever; pin the contract.
    calls = _stub_get(monkeypatch, response=httpx.Response(200, text="ok"))
    fetch_url.invoke({"url": "https://example.com/redirect"})
    assert calls == [
        {
            "url": "https://93.184.215.14/redirect",
            "timeout": 15,
            "follow_redirects": False,
            "headers": {"Host": "example.com"},
            "extensions": {"sni_hostname": "example.com"},
        }
    ]


def test_fetch_url_hands_a_redirect_back_to_the_model(monkeypatch):
    # The new URL goes back to the model, so the next fetch_url call checks it too.
    _stub_get(monkeypatch, response=httpx.Response(302, headers={"location": "/next"}))
    out = fetch_url.invoke({"url": "https://example.com/start"})
    assert out == "HTTP 302\nredirects to https://example.com/next"


@pytest.mark.parametrize(
    "url",
    [
        "http://169.254.169.254/latest/meta-data/",  # cloud metadata
        "http://127.0.0.1:11434/api/tags",  # Ollama on this machine
        "http://[::1]/",
        "http://10.0.0.5/",
        "http://localhost:8080/",  # a name that resolves to loopback
        "file:///etc/passwd",
    ],
)
def test_fetch_url_refuses_non_public_addresses(monkeypatch, url):
    calls = _stub_get(monkeypatch, response=httpx.Response(200, text="secret"))
    assert fetch_url.invoke({"url": url}) == "error: only public http(s) addresses can be fetched"
    assert calls == []


def test_fetch_url_makes_exactly_one_request(monkeypatch):
    calls = _stub_get(monkeypatch, response=httpx.Response(200, text="ok"))
    fetch_url.invoke({"url": "https://example.com"})
    assert len(calls) == 1


@pytest.mark.parametrize("scheme", ["http", "https"])
def test_fetch_url_connects_to_the_checked_address(monkeypatch, scheme):
    # Path, query and port survive; only the host becomes the checked address,
    # and the name moves to the Host header (and to TLS SNI for https).
    calls = _stub_get(monkeypatch, response=httpx.Response(200, text="ok"))
    fetch_url.invoke({"url": f"{scheme}://example.com:8443/a/b?q=1&r=2"})
    assert calls[0]["url"] == f"{scheme}://93.184.215.14:8443/a/b?q=1&r=2"
    assert calls[0]["headers"] == {"Host": "example.com:8443"}
    expected_sni = {"sni_hostname": "example.com"} if scheme == "https" else {}
    assert calls[0]["extensions"] == expected_sni


def test_fetch_url_resolves_once_so_dns_cannot_change_under_it(monkeypatch):
    # DNS rebinding: a public answer for the check, a private one after it.
    answers = iter(["93.184.215.14", "127.0.0.1"])

    def rebinding_getaddrinfo(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (next(answers), 0))]

    monkeypatch.setattr(socket, "getaddrinfo", rebinding_getaddrinfo)
    calls = _stub_get(monkeypatch, response=httpx.Response(200, text="ok"))
    fetch_url.invoke({"url": "http://rebind.example/"})
    assert calls[0]["url"] == "http://93.184.215.14/"
