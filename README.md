# LLM Unit Economics: what does the same task actually cost?

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

## Tasks (5 types x 2 languages, English and Arabic mirrors)

| Task | What it isolates |
|---|---|
| `docqa` | The input meter: identical ~500-word report, 3 factual questions |
| `extract` | Structured output: invoice -> fixed-schema JSON |
| `sudoku_moderate` | Reasoning burn on a solvable puzzle (Sudoku-Extreme test split, rating 1) |
| `sudoku_extreme` | Reasoning burn at the frontier (Sudoku-Extreme "forum hardest", rating 60) |
| `roster` | An enterprise constraint problem: a driver shift roster with 10 interlocking rules and a provably unique solution (see `tools/make_roster.py`) |
| `filing_extract` | Real bilingual filings from the Saudi Exchange (MIS, Aramco, Al Rajhi H1-2026 interims; see `corpus/MANIFEST.md`): extract key figures to fixed-schema JSON |
| `filing_multi` | All three filings in one ~70-90K-token prompt: rank companies by net income across three different reporting units and name the highest EPS |
| `agentic` | A tool-use loop: flight search with a canned tool result |

Sudoku puzzles and reference solutions come from the
[Sudoku-Extreme benchmark](https://huggingface.co/datasets/sapientinc/sudoku-extreme)
test split. See `tasks.py` for the exact prompts and design choices
(Western digits in Arabic mirrors; English tool schema in both mirrors).

Each (model, task) cell runs 3 times (2 for `sudoku_extreme`) because
thinking length is nondeterministic — the run-to-run cost variance is
itself one of the measurements.

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

| Model | Solved | Mean thinking tokens | Mean cost/run |
|---|---|---|---|
| DeepSeek V4 Pro | 4/4 | 50,290 | $0.10 |
| Claude Fable 5 | 4/4 | 17,921 | $0.94 |
| GLM-5.3 | 2/4 | 31,560 | $0.14 |
| Gemini 3.1 Pro | 1/4 | 36,763 | $0.45 |
| GPT-5.6 Sol | 0/4 | 11,532 | $0.17 |
| Kimi K3 (pass 1, uncapped) | 6/6 | 35,501 | $0.53 |

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
