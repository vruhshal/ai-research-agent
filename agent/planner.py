"""
Planning step.

This is the "visible planning/orchestration structure" the assignment asks for:
before any tool is called, the agent commits to a written plan (sub-questions
+ tools it intends to use), which gets logged and shown in the final trace.
"""

from pydantic import ValidationError
from .schemas import Plan
from .llm_client import call_llm, extract_json
from .logger import log_event

PLANNER_SYSTEM_PROMPT = """You are the planning module of a research agent.
Given a user's research question, produce a plan as a single JSON object with
exactly these fields:
{
  "reasoning": "1-3 sentences on your approach",
  "sub_questions": ["2-4 concrete, web-searchable sub-questions"],
  "tools_needed": ["web_search", "fetch_url"]
}
Sub-questions should be specific enough to type directly into a search engine.
Return ONLY the JSON object. No prose, no markdown fences."""

MAX_REPAIR_ATTEMPTS = 2


def create_plan(question: str) -> Plan:
    user_prompt = f"User question: {question}"
    last_error = None

    for attempt in range(MAX_REPAIR_ATTEMPTS + 1):
        prompt = user_prompt
        if last_error:
            # Self-repair: feed the validation error back to the model.
            prompt += (
                f"\n\nYour previous response was invalid: {last_error}\n"
                "Return a corrected JSON object only."
            )
        raw = call_llm(PLANNER_SYSTEM_PROMPT, prompt, max_tokens=500)
        try:
            data = extract_json(raw)
            plan = Plan(**data)
            log_event("planner", "success", sub_questions=plan.sub_questions)
            return plan
        except (ValidationError, ValueError) as e:
            last_error = str(e)
            log_event("planner", "validation_failed", attempt=attempt, error=last_error)

    # Fallback: degrade gracefully instead of crashing the whole pipeline.
    log_event("planner", "fallback_used", question=question)
    return Plan(
        reasoning="Planner failed to produce valid structured output; falling back to a single direct search.",
        sub_questions=[question],
        tools_needed=["web_search", "fetch_url"],
    )
