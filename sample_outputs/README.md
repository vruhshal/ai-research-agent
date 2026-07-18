# Sample Outputs

This folder is intentionally empty of pre-baked examples. Sample outputs
need to come from your own live run (real search results + real API key),
not fabricated JSON, since the assignment asks for genuine system outputs.

Once you've set `ANTHROPIC_API_KEY`, generate 2-3 samples with:

```bash
python main.py "Compare the top 3 open-source vector databases for a startup building RAG products." --save sample_outputs/sample_1.json
python main.py "Find 5 Indian B2B SaaS startups in HR tech and summarize their positioning." --save sample_outputs/sample_2.json
python main.py "Research the pros and cons of using a multi-agent architecture for customer support automation." --save sample_outputs/sample_3.json
```

Each `--save` writes the full pipeline result (plan + final structured
answer + timing) as JSON. Pick the 2-3 most illustrative ones for
submission — ideally one clean happy-path result and one that shows the
system handling thin/failed evidence gracefully (e.g. run the nonsense
query from `eval/eval_queries.md` Test 4).
