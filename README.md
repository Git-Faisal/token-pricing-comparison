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
