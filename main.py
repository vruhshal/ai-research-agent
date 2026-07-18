#!/usr/bin/env python3
"""
CLI entry point.

Usage:
    python main.py "Compare the top 3 open-source vector databases for a startup building RAG products"
    python main.py "your question" --save sample_outputs/sample_4.json
"""

import sys
import json
import argparse
from agent.pipeline import run_agent


def main():
    parser = argparse.ArgumentParser(description="AI Research Agent")
    parser.add_argument("question", type=str, help="The research question to answer")
    parser.add_argument("--save", type=str, default=None, help="Optional path to save the raw JSON result")
    args = parser.parse_args()

    print(f"\n>> Question: {args.question}\n")
    print(">> Running plan -> search -> synthesize pipeline (this calls the LLM + web, may take 15-40s)...\n")

    result = run_agent(args.question)

    if result["plan"]:
        print("PLAN")
        print(f"  Reasoning: {result['plan']['reasoning']}")
        print(f"  Sub-questions: {result['plan']['sub_questions']}")
        print()

    answer = result["final_answer"]
    print("=" * 70)
    print("SHORT ANSWER")
    print(answer["short_answer"])
    print()
    print("KEY FINDINGS")
    for f in answer["key_findings"]:
        print(f"  - {f}")
    print()
    print("SOURCES")
    for s in answer["sources"]:
        print(f"  - {s['title']} ({s['url']})")
    print()
    print(f"CONFIDENCE: {answer['confidence']}")
    print(f"LIMITATIONS: {answer['limitations']}")
    print(f"ASSUMPTIONS: {answer.get('assumptions', [])}")
    print(f"NEXT STEPS: {answer['next_steps']}")
    print("=" * 70)
    print(f"\n(status={result['pipeline_status']}, evidence_count={result['evidence_count']}, "
          f"latency_ms={result['total_latency_ms']})")

    if args.save:
        with open(args.save, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved full result to {args.save}")


if __name__ == "__main__":
    main()
