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

## Actual results (fill in after running `eval/run_eval.py`)

| # | Query | Confidence returned | Evidence count | Passed criteria? | Notes |
|---|-------|---------------------|-----------------|-------------------|-------|
| 1 |       |                     |                 |                   |       |
| 2 |       |                     |                 |                   |       |
| 3 |       |                     |                 |                   |       |
| 4 |       |                     |                 |                   |       |
| 5 |       |                     |                 |                   |       |

**What worked well:** (fill in after real runs — e.g. "planner reliably
produces 3-4 concrete sub-questions", "duplicate-domain filtering kept source
diversity reasonable")

**What did not work well:** (fill in — e.g. "DuckDuckGo results are sometimes
thin for very narrow/regional queries like Test 2, so confidence correctly
dropped but findings were sparse", "fetch_url occasionally hits paywalled
pages and falls back to snippet-only, which is handled but lowers depth")
