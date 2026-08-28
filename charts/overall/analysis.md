# Overall: the hypothesis and the Arabic impact

**Hypothesis** (see repo README): sticker per-token price is not a reliable proxy for real cost. Rank correlations between sticker output price and measured costs (1.0 = price sheet predicts the bill):

| Experiment | sticker vs cost/task | sticker vs cost/success |
|---|---|---|
| Doc Q&A | 0.58 | 0.75 |
| Invoice extract | 0.29 | 0.29 |
| Agentic | 0.75 | 0.75 |
| Roster | 0.35 | 0.35 |
| Sudoku (unbounded) | 0.90 | 0.70 |
| Filings extract | 0.90 | 0.90 |
| Filings multi | 0.81 | 0.81 |

Charts: `hypothesis_rank_bump*.png` (rank trajectories), `hypothesis_scatter.png` (price vs bill, log-log), `arabic_cost_ratio.png` and `arabic_success_rate.png` (the Arabic premium in money and in reliability), `input_meter.png` (same documents, six billed token counts), `cache_effect.png` (cold vs warm identical requests).
