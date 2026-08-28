# What does the same task actually cost?

An open, replicable experiment measuring what identical work actually costs
across six frontier models — in real billed dollars, not sticker prices.

Companion repository for a blog post on token pricing (link TBD).

## The question

Every lab prices its API in tokens, but a token is not a standard unit:
each lab designs its own tokenizer, so the same text is a different number
of tokens on every meter — and most meters cannot be independently checked.
If per-token prices were comparable, six models given identical work should
cost roughly in proportion to their sticker prices. Do they?

## Models (one flagship per lab, as listed on OpenRouter, Aug 2026)

| Lab | Model | Sticker in/out ($/1M tokens) | Public tokenizer? |
|---|---|---|---|
| Anthropic | claude-fable-5 | 10.00 / 50.00 | No |
| OpenAI | gpt-5.6-sol | 2.50 / 15.00 | Yes (tiktoken) |
| Moonshot AI | kimi-k3 | 3.00 / 15.00 | Weights open, billing tokenizer undocumented |
| Google | gemini-3.1-pro-preview | 2.00 / 12.00 | No |
| Zhipu (Z.ai) | glm-5.3 | 1.40 / 4.40 | Weights open |
| DeepSeek | deepseek-v4-pro-0813 | 1.06 / 3.17 | Yes (official package) |

Open-weight models are pinned to the lab's own hosting endpoint
(`provider.order`, no fallbacks) so every call is served and priced identically.

## The tests

Every test runs on all six models, in two mirrored versions (English and
Arabic), with 2-3 repeated runs per cell -- thinking length is
nondeterministic, so run-to-run cost variance is itself a measurement.
Every answer is machine-graded; no judgment calls. The test suite spans
three tiers: everyday office work, hard reasoning, and real enterprise
document work.

### Tier 1: office work (the baseline)

**1. Report Q&A** (`docqa`) -- A ~500-word synthetic logistics operations
report followed by three factual questions (revenue, a percentage, a date).
Every model reads the byte-identical document, so this isolates the *input
meter*: how many tokens each lab bills for the same text, and what a trivial
comprehension task costs. Graded by checking the three expected values
appear in the answer.

**2. Invoice extraction** (`extract`) -- A synthetic tax invoice to be
converted to a fixed-schema JSON object (invoice number, date, vendor,
total, line-item count). The most common enterprise LLM workload. Graded by
parsing the JSON and comparing each field.

**3. Flight search agent** (`agentic`) -- One tool-use loop: the model gets
a `search_flights` tool, must call it, receives a canned JSON result (three
flights), and must answer with the cheapest airline and price. Tests the
minimal agentic pattern -- tool call, context re-send, final answer -- and
its cost. Graded on tool use plus the correct airline/price in the answer.

### Tier 2: reasoning (where thinking burn lives)

**4. Sudoku** (`sudoku_moderate`, `sudoku_extreme`) -- Two puzzles from the
[Sudoku-Extreme benchmark](https://huggingface.co/datasets/sapientinc/sudoku-extreme)
test split, with the dataset's own solutions as ground truth: one from the
easiest tier (rating 1) and one from the "forum hardest" set (rating 60).
Sudoku is deliberately knowledge-free: no fact retrieval helps, only
sustained constraint propagation and search -- the computation shape that
token-by-token reasoning is worst at (and is billed for). Run twice: pass 1
under fixed budgets (16K/32K tokens) measuring behavior when a customer
budget binds; pass 2 at 128K measuring what happens when it doesn't.
Graded by exact match of the 81-digit solution grid.

**5. Driver roster** (`roster`) -- The enterprise version of the same
muscle: build a weekly shift roster for 5 named drivers, Sunday-Thursday,
day/night shifts, 2 drivers per shift, under 10 interlocking rules (exact
weekly quotas, a night-to-morning rest rule, refrigerated-cargo
certification coverage, a missing forklift licence, an availability gap, a
pairing ban, no double shifts, and two individual constraints). The
instance is constructed so that **exactly one valid roster exists** --
verified by exhaustive search in `tools/make_roster.py`, so grading equals
feasibility. Unlike Sudoku, no one can say their business does not do this.

### Tier 3: real enterprise documents

**6. Filing extraction** (`filing_extract`) -- Real interim financial
statements of three Tadawul-listed companies -- Al Moammar Information
Systems (7200), Saudi Aramco (2222), and Al Rajhi Bank (1120), all for the
six-month period ended 30 June 2026 -- in each company's own official
English and Arabic versions (see `corpus/MANIFEST.md` for provenance).
The model reads one full filing (14K-40K billed tokens) and extracts three
key figures (net income, EPS, plus one company-specific field) to
fixed-schema JSON. Because the same disclosure exists in both languages
*as published by the issuer*, the English/Arabic cost comparison has no
translation confound at all. Graded numerically against figures verified
in the filings and against the exchange's own data.

**7. Multi-filing analyst question** (`filing_multi`) -- All three filings
concatenated into one ~280K-character prompt (~75K+ billed tokens): rank
the companies by six-month net income and name the one with the highest
basic EPS. The trap is real analyst work: the three filings report in
**three different units** (riyals, millions of riyals, thousands of
riyals), so naive number comparison ranks a 13.8-billion-riyal bank above
a 244.6-billion-riyal oil company -- and the highest-EPS answer is not the
biggest company. This is also the input meter measured at enterprise
scale: the same document set bills as a different token count on all six
meters. Graded on the ranking order and the EPS answer.

## Protocol

- Default settings for everything: default thinking mode, no temperature or
  reasoning-effort overrides. We buy the models the way a normal customer does.
- Byte-identical prompts across models; full request/response JSON archived
  in `results/raw/` for audit.
- All token counts and dollar costs come from the provider-billed `usage`
  object returned by the OpenRouter API (`usage.include: true`) — never from
  local estimates.
- `reconcile.py` then attempts to reproduce the billed counts with public
  tokenizers. Where no public tokenizer exists, the bill cannot be
  independently verified — that result is part of the experiment.

## Replicate it

```bash
pip install -r requirements.txt
# put your OpenRouter key in .openrouter_key (gitignored) or OPENROUTER_API_KEY
python runner.py --plan        # see the full matrix, no spend
python runner.py               # run everything (~$30-60 in credits)
python analyze.py              # charts/ + results/summary.md
python reconcile.py            # billed counts vs public tokenizers
```

`runner.py` is resumable: completed (model, task, run) cells found in
`results/results.csv` are skipped.

## Outputs

- `results/results.csv` — one row per call: billed prompt/completion/reasoning
  tokens, cached tokens, dollar cost, latency, serving provider, task success
- `results/raw/*.json` — full API responses
- `results/summary.md` — totals, success rates, cost per successful task,
  run-to-run variance
- `charts/*.png` — working charts (unstyled)

## Results (run of 2026-08-19/20, 220 calls, $49.65)

Full data: `results/results.csv` (per-call billed tokens, costs, latency,
success), `results/summary.md`, `results/reconcile.csv`, `charts/`.

### Everyday tasks (doc Q&A, extraction, tool use): everyone passes, prices differ ~8x

All six models scored 18/18 on the office-work tier — except Claude Fable 5
(13/18), whose failures were all content-filter refusals of mundane business
documents (an Arabic logistics report, an English invoice), triggered
nondeterministically and in one case billed. Mean cost per call for the same
completed work: DeepSeek $0.0014, GLM $0.0016, Sol $0.0018, Kimi $0.0048,
Gemini $0.0105, Fable $0.0118.

### Driver roster (unique-solution constraint problem): all six solve it, at a 10x price spread

Cost per successful solve (mean): Sol $0.029, GLM $0.050, DeepSeek $0.081,
Gemini $0.153, Kimi $0.174, Fable $0.313. Same roster, same verified answer.
GLM also produced the experiment's starkest variance artifact: one run burned
its entire 128K budget and failed ($0.56); the identical next run solved it
for $0.06.

### Sudoku, moderate (rating 1): budgets, stopping policies, and a 15x spread per solve

Under pass-1 budgets (16K tokens), only Kimi K3 solved it (6/6), because its
host does not enforce the customer's token cap (it used up to 46K tokens on a
16K request). At pass-2 budgets (128K):

| Model | Condition | Runs | Solved | Mean thinking tokens | Mean cost/run |
|---|---|---|---|---|---|
| DeepSeek V4 Pro | pass 2, 128K budget | 4 | 4 | 50,290 | $0.10 |
| Claude Fable 5 | pass 2, 128K budget | 4 | 4 | 17,921 | $0.94 |
| GLM-5.3 | pass 2, 128K budget | 4 | 2 | 31,560 | $0.14 |
| Gemini 3.1 Pro | pass 2, 128K budget | 4 | 1 | 36,763 | $0.45 |
| GPT-5.6 Sol | pass 2, 128K budget | 4 | 0 | 11,532 | $0.17 |
| Kimi K3 | pass 1, cap ignored | 6 | 6 | 35,501 | $0.53 |

Why Kimi's row is different: its provider does not enforce the customer's
`max_tokens` on reasoning, so Kimi already ran effectively uncapped in
pass 1 (thinking 27K-46K tokens against a 16K request, all 6 runs). It was
therefore exempted from pass 2 -- a 128K request would re-measure the same
condition. Its 6 pass-1 runs are shown here as the equivalent unbounded
condition; the five cap-compliant models get 4 fresh pass-2 runs each.

Note the inversion: Fable needed the fewest thinking tokens of any solver and
still cost ~10x DeepSeek per solve, because its per-token price is ~16x
higher. Token efficiency and cost efficiency ranked in opposite order.
GPT-5.6 Sol never used the larger budget: it stopped at 8-13K thinking tokens
at every budget and submitted confidently wrong grids (finish_reason: stop).

### Sudoku, extreme (rating 60): 0 for 28, at every budget, ~$25 spent

No model solved it in any run, either language, at 16K, 32K, or 128K budgets.
GLM, DeepSeek, and Fable burned their full budgets (Fable: $6.40 per
128K-token failure); Sol and Gemini stopped early and submitted wrong grids.
Kimi thought 104K tokens on one attempt ($1.56) and still failed.

### The meter itself

- The two labs with public tokenizers reconcile exactly: on every
  single-turn call, billed input = local recount + a fixed template overhead
  (+6 tokens/call for OpenAI, +83 for DeepSeek, zero variance across 32
  calls each). The other four labs' billed counts cannot be independently
  checked at all.
- Only DeepSeek returns its raw reasoning text; its bills are auditable
  end-to-end. All other labs bill for thinking tokens the customer never sees.
- `max_tokens` is not enforced uniformly: Moonshot's endpoint exceeded the
  requested cap by up to 3.25x and billed the overage.
- OpenRouter's ledger vs our recorded results: an errored 50K-token Kimi
  generation was auto-refunded ($0.76 of upstream compute, $0 charged), but
  ~$1.59 was billed for generations whose connections dropped before any
  response was delivered.
- Unpinned, "Claude Fable 5" was served by Google Vertex with different
  content-filter behavior than Anthropic's own endpoint (see
  `results/quarantine_vertex_fable.csv`).

## Caveats

- One puzzle, one document, one invoice per task type: this measures cost
  structure, not model capability. Success rates on n=2-3 runs are indicative only.
- Arabic mirrors are natural translations, not word-for-word equivalents;
  language comparisons are directional.
- OpenRouter adds its own platform fee on credit purchases but passes through
  provider token pricing; costs recorded are what the API billed per call.
- Model lineups and prices change quickly; re-run `runner.py` to reproduce
  with current pricing and compare.

## Disclosures

- Sudoku as a reasoning task is a nod to
  [Pathway's Sudoku-Bench work](https://pathway.com/research/beyond-transformers-sudoku-bench)
  on post-transformer architectures. Pathway is a portfolio company of RBV,
  where the author works.
- One of the six models tested (Claude Fable 5) is the model that assisted
  in building and running this experiment. The protocol treats all six
  identically and all raw responses are archived.

## License

MIT
