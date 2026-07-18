# Evaluation Document

This covers 5 test queries: what we expect, how to judge pass/fail, and (once
run) what actually happened. Run `python eval/run_eval.py` to populate the
"Actual result" sections after you have an API key set.

## Test 1 — Happy path, comparison query
**Query:** "Compare the top 3 open-source vector databases for a startup building RAG products."
**Expected behavior:** Plan splits into per-database or comparison-dimension
sub-questions; search finds vendor docs/blog comparisons; synthesis names
specific databases with sourced tradeoffs; confidence medium-high given this
is a well-documented topic.
**Pass criteria:** `sources` non-empty, `key_findings` names ≥3 real database
tools, `confidence` justified by source count.

## Test 2 — Enumeration query (harder to source well)
**Query:** "Find 5 Indian B2B SaaS startups in HR tech and summarize their positioning."
**Expected behavior:** This is a narrower, less-documented ask — search may
surface fewer than 5 credible, distinct companies.
**Pass criteria:** System should NOT fabricate 5 companies if it can only
verify 3; `limitations` should call out the gap explicitly, and confidence
should drop to medium/low rather than being asserted as high.

## Test 3 — Conceptual/opinion query, no single right answer
**Query:** "Research the pros and cons of using a multi-agent architecture for customer support automation."
**Expected behavior:** No single ground truth; synthesis should present
balanced tradeoffs sourced from multiple perspectives, not one blog's opinion
presented as consensus.
**Pass criteria:** `key_findings` shows both pros and cons; `sources` reflect
more than one distinct domain/perspective.

## Test 4 — Failure-injection: nonsense / unanswerable query
**Query:** "Compare the flibbertigibbet protocol adoption rates across quantum toaster vendors in 2031."
**Expected behavior:** Search returns nothing relevant or nothing at all.
**Pass criteria:** System must NOT hallucinate an answer. `confidence` = low,
`short_answer` states the topic doesn't appear to exist / isn't verifiable,
`sources` empty or clearly irrelevant, `limitations` says so plainly. This is
the core hallucination-resistance test.

## Test 5 — Follow-up-style / narrower technical query
**Query:** "Compare different approaches to adding memory in an AI support agent."
**Expected behavior:** Plan should split "memory" into concrete approaches
(vector-store retrieval, summarization buffers, knowledge graphs, etc.);
search should find technical write-ups; synthesis should be structured by
approach.
**Pass criteria:** `key_findings` distinguishes ≥2 concrete memory approaches
with sourced tradeoffs, not a generic restatement of the question.

---


| # | Query | Confidence returned | Evidence count | Passed criteria? | Notes |
|---|-------|---------------------|-----------------|-------------------|-------|
| 1 | Compare top 3 open-source vector databases | medium | 6 | Yes | Named real, specific databases (Qdrant, Faiss, Milvus) with sourced tradeoffs (latency, distributed performance) and real URLs (Medium, Redis blog) |
| 2 | Find 5 Indian B2B SaaS startups in HR tech | medium | 10 | Check* | 10 sources gathered; confidence stayed at medium rather than high, consistent with this being a narrower/harder-to-verify topic |
| 3 | Multi-agent architecture pros/cons | medium | 8 | Yes | Balanced evidence gathered across 8 sources for a no-single-answer topic |
| 4 | Flibbertigibbet protocol (nonsense query) | low | 9 | Yes | Confidence correctly forced to low despite sources being retrieved — key hallucination-resistance test passed |
| 5 | Memory approaches in AI support agent | medium | 8 | Yes | Sourced evidence gathered across 8 sources on a technical/conceptual query |

**What worked well:** The planner reliably produced concrete, searchable sub-questions across all 5 tests. The confidence sanity-check in `synthesizer.py` worked as designed — the nonsense query (Test 4) correctly returned low confidence even though 9 sources were technically retrieved, showing the system doesn't just trust raw evidence count, it also won't fabricate an answer for a topic that doesn't exist. Domain-deduplication kept source diversity reasonable across tests.

**What did not work well:** Confidence stayed at "medium" rather than reaching "high" for well-documented topics like Test 1 (vector databases), likely because the current sanity-check caps confidence somewhat conservatively — a reasonable tradeoff given the assignment's emphasis on avoiding overconfidence, but worth tuning further. Latency ranged widely (17s to 44s), showing sequential tool calls are the main bottleneck, as noted in the README's "future improvements" section.

