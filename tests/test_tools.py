"""
These tests mock the network entirely, so `pytest` should pass with zero
API key and zero internet access -- useful for CI, and for you to sanity
check the logic before spending API credits.
"""

from unittest.mock import patch, MagicMock
from agent.tools import fetch_url, web_search
from agent.executor import gather_evidence, _domain
from agent.schemas import Plan


def test_domain_extraction():
    assert _domain("https://www.example.com/a/b") == "example.com"
    assert _domain("https://sub.example.com") == "sub.example.com"


@patch("agent.tools.requests.get")
def test_fetch_url_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.text = "<html><body><script>bad()</script><p>Real content here</p></body></html>"
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    result = fetch_url("https://example.com")
    assert result["success"] is True
    assert "Real content here" in result["text"]
    assert "bad()" not in result["text"]  # script tags stripped


@patch("agent.tools.requests.get")
def test_fetch_url_handles_timeout(mock_get):
    mock_get.side_effect = Exception("timed out")
    result = fetch_url("https://example.com")
    assert result["success"] is False
    assert result["text"] == ""


@patch("agent.tools.DDGS")
def test_web_search_handles_failure(mock_ddgs_cls):
    mock_ddgs_cls.side_effect = Exception("network down")
    results = web_search("test query")
    assert results == []  # degrades to empty list, doesn't raise


@patch("agent.executor.fetch_url")
@patch("agent.executor.web_search")
def test_gather_evidence_skips_duplicate_domains(mock_search, mock_fetch):
    mock_search.return_value = [
        {"title": "A", "url": "https://x.com/1", "snippet": "s" * 50},
        {"title": "B", "url": "https://x.com/2", "snippet": "s" * 50},  # same domain, should be skipped
        {"title": "C", "url": "https://y.com/1", "snippet": "s" * 50},
    ]
    mock_fetch.return_value = {"success": True, "url": "u", "error": None, "text": "content"}

    plan = Plan(reasoning="test", sub_questions=["q1"], tools_needed=["web_search", "fetch_url"])
    evidence = gather_evidence(plan)
    domains = {_domain(e["url"]) for e in evidence}
    assert domains == {"x.com", "y.com"}  # only one from x.com despite 2 results


@patch("agent.executor.fetch_url")
@patch("agent.executor.web_search")
def test_gather_evidence_handles_empty_search(mock_search, mock_fetch):
    mock_search.return_value = []
    plan = Plan(reasoning="test", sub_questions=["q1"], tools_needed=["web_search"])
    evidence = gather_evidence(plan)
    assert evidence == []
