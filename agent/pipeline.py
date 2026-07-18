"""
Top-level orchestration. This is the single entry point the CLI (and eval
harness) calls.
"""

import time
from .planner import create_plan
from .executor import gather_evidence, format_evidence_for_prompt
from .synthesizer import synthesize
from .schemas import FinalAnswer
from .logger import log_event, timed_step


def run_agent(question: str) -> dict:
    """
    Runs the full plan -> execute -> synthesize pipeline.
    Returns a dict with the FinalAnswer plus trace metadata (plan, timing).
    Never raises: any unhandled failure is caught and turned into a
    low-confidence structured answer, because a research assistant that
    crashes with a stack trace is worse than one that says "I don't know."
    """
    run_start = time.time()
    log_event("pipeline", "start", question=question)

    try:
        with timed_step("plan"):
            plan = create_plan(question)

        with timed_step("execute"):
            evidence = gather_evidence(plan)
            evidence_text = format_evidence_for_prompt(evidence)

        with timed_step("synthesize"):
            answer = synthesize(question, plan, evidence_text, evidence_count=len(evidence))

        result = {
            "final_answer": answer.model_dump(),
            "plan": plan.model_dump(),
            "evidence_count": len(evidence),
            "total_latency_ms": int((time.time() - run_start) * 1000),
            "pipeline_status": "ok",
        }
        log_event("pipeline", "success", total_latency_ms=result["total_latency_ms"])
        return result

    except Exception as e:
        # Global safety net -- covers e.g. missing API key, total LLM outage.
        log_event("pipeline", "fatal_error", error=str(e))
        fallback = FinalAnswer(
            user_question=question,
            short_answer=f"The agent could not complete this request due to a system error: {e}",
            confidence="low",
            limitations=["Pipeline raised an unhandled error; see run_logs.jsonl."],
            next_steps=["Check ANTHROPIC_API_KEY is set.", "Check network access.", "Re-run the query."],
        )
        return {
            "final_answer": fallback.model_dump(),
            "plan": None,
            "evidence_count": 0,
            "total_latency_ms": int((time.time() - run_start) * 1000),
            "pipeline_status": "fatal_error",
            "error": str(e),
        }
