#!/usr/bin/env python3
"""
Runs the 5 queries from eval_queries.md through the pipeline and dumps
results to eval/eval_results.json for manual review against the pass
criteria documented there.

Usage: python eval/run_eval.py   (requires ANTHROPIC_API_KEY to be set)
"""

import sys
import json
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.pipeline import run_agent

QUERIES = [
    "Compare the top 3 open-source vector databases for a startup building RAG products.",
    "Find 5 Indian B2B SaaS startups in HR tech and summarize their positioning.",
    "Research the pros and cons of using a multi-agent architecture for customer support automation.",
    "Compare the flibbertigibbet protocol adoption rates across quantum toaster vendors in 2031.",
    "Compare different approaches to adding memory in an AI support agent.",
]


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: set ANTHROPIC_API_KEY before running the eval.")
        sys.exit(1)

    results = []
    for i, q in enumerate(QUERIES, 1):
        print(f"\n[{i}/{len(QUERIES)}] Running: {q}")
        result = run_agent(q)
        results.append({"query": q, "result": result})
        print(f"  -> status={result['pipeline_status']}, "
              f"confidence={result['final_answer']['confidence']}, "
              f"evidence_count={result['evidence_count']}, "
              f"latency_ms={result['total_latency_ms']}")

    out_path = os.path.join(os.path.dirname(__file__), "eval_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved detailed results to {out_path}")
    print("Now fill in the 'Actual results' table in eval_queries.md by hand.")


if __name__ == "__main__":
    main()
