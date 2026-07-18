"""
Tools available to the agent.

Both tools are deliberately defensive: network calls fail in the real world
(timeouts, rate limits, 403s, garbage HTML), and a "production-minded" agent
has to treat every tool result as untrusted and possibly broken.
"""

import time
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from .logger import log_event

REQUEST_TIMEOUT = 10
MAX_RETRIES = 2
FETCH_MAX_CHARS = 4000


def _retry(fn, tool_name: str, *args, **kwargs):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_err = e
            log_event(tool_name, "retry", attempt=attempt, error=str(e))
            time.sleep(min(2 ** attempt, 5))  # exponential backoff, capped
    raise last_err


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Free web search via DuckDuckGo. Returns a list of
    {"title": ..., "url": ..., "snippet": ...} or an empty list on failure
    (never raises past this point -- a failed search is a signal, not a crash).
    """
    def _do_search():
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return [
            {
                "title": r.get("title", "").strip(),
                "url": r.get("href", "").strip(),
                "snippet": r.get("body", "").strip(),
            }
            for r in results
            if r.get("href")
        ]

    try:
        results = _retry(_do_search, "tool:web_search")
        log_event("tool:web_search", "result", query=query, n_results=len(results))
        return results
    except Exception as e:
        log_event("tool:web_search", "failed", query=query, error=str(e))
        return []


def fetch_url(url: str) -> dict:
    """
    Fetches a URL and extracts readable text.
    Always returns a dict with a `success` flag -- callers should check it
    rather than assume content is present.
    """
    def _do_fetch():
        resp = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (research-agent/0.1)"},
        )
        resp.raise_for_status()
        return resp

    try:
        resp = _retry(_do_fetch, "tool:fetch_url")
    except Exception as e:
        log_event("tool:fetch_url", "failed", url=url, error=str(e))
        return {"success": False, "url": url, "error": str(e), "text": ""}

    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        text = text[:FETCH_MAX_CHARS]
        if not text:
            log_event("tool:fetch_url", "empty_content", url=url)
            return {"success": False, "url": url, "error": "empty content after parsing", "text": ""}
        log_event("tool:fetch_url", "result", url=url, chars=len(text))
        return {"success": True, "url": url, "error": None, "text": text}
    except Exception as e:
        log_event("tool:fetch_url", "parse_failed", url=url, error=str(e))
        return {"success": False, "url": url, "error": f"parse error: {e}", "text": ""}
