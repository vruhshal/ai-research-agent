"""
Minimal structured logger.

Production systems would use OpenTelemetry/Langfuse/Helicone. For a take-home,
a JSON-lines file that records every step, its latency, and its outcome is
enough to demonstrate the *habit* of tracing without pulling in infra.
"""

import json
import time
from pathlib import Path
from contextlib import contextmanager

LOG_PATH = Path(__file__).parent.parent / "run_logs.jsonl"


def log_event(step: str, status: str, **fields):
    record = {
        "ts": time.time(),
        "step": step,
        "status": status,
        **fields,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")


@contextmanager
def timed_step(step_name: str):
    """Wraps a pipeline step, logging start/success/failure + latency automatically."""
    start = time.time()
    log_event(step_name, "start")
    try:
        yield
    except Exception as e:
        log_event(step_name, "error", latency_ms=int((time.time() - start) * 1000), error=str(e))
        raise
    else:
        log_event(step_name, "success", latency_ms=int((time.time() - start) * 1000))
