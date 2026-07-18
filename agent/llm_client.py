"""
Thin wrapper around the Groq API (free tier, OpenAI-compatible, no card
required -- see console.groq.com). Chosen so this assignment can be built
and run entirely for free; the assignment explicitly allows "any LLM
provider," and Groq's hosted Llama models are more than capable for
planning/synthesis JSON tasks like this one.

Keeping this in one place means retry/timeout/model-selection logic isn't
duplicated across the planner and synthesizer. If you later want to switch
to Anthropic or OpenAI, this is the only file that needs to change --
planner.py and synthesizer.py just call call_llm()/extract_json().
"""

import os
import time
import json
from groq import Groq, RateLimitError, APIStatusError, APIConnectionError, APITimeoutError

# llama-3.3-70b-versatile is Groq's strong general-purpose model, free tier.
# llama-3.1-8b-instant is a smaller/faster fallback if you hit rate limits.
DEFAULT_MODEL = os.environ.get("AGENT_MODEL", "llama-3.3-70b-versatile")
MAX_RETRIES = 2
REQUEST_TIMEOUT = 30


def get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Get a free key at console.groq.com "
            "(API Keys -> Create API Key), then set it:\n"
            "  Windows PowerShell:  $env:GROQ_API_KEY=\"gsk_...\"\n"
            "  Mac/Linux:           export GROQ_API_KEY=gsk_..."
        )
    return Groq(api_key=api_key, timeout=REQUEST_TIMEOUT)


def call_llm(system: str, user: str, max_tokens: int = 1500, model: str = None) -> str:
    """
    Calls the LLM with retries on transient failures (rate limits, timeouts,
    5xx). Returns the raw text response. Raises after exhausting retries --
    callers decide how to degrade (e.g. lower confidence, partial answer).
    """
    client = get_client()
    model = model or DEFAULT_MODEL
    last_err = None

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            resp = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return resp.choices[0].message.content or ""
        except RateLimitError as e:
            last_err = e
            time.sleep(min(2 ** attempt, 10))
        except APIStatusError as e:
            last_err = e
            if e.status_code and e.status_code < 500:
                raise  # 4xx (bad request, auth) won't fix itself on retry
            time.sleep(min(2 ** attempt, 10))
        except (APIConnectionError, APITimeoutError) as e:
            last_err = e
            time.sleep(min(2 ** attempt, 10))

    raise RuntimeError(f"LLM call failed after {MAX_RETRIES + 1} attempts: {last_err}")


def extract_json(raw_text: str) -> dict:
    """
    LLMs sometimes wrap JSON in prose or code fences even when told not to.
    This pulls out the first {...} block rather than assuming raw_text is
    clean JSON.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"No JSON object found in LLM output: {raw_text[:200]}")
    return json.loads(text[start:end + 1])
