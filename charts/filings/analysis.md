# Tadawul filings

Task types: filing_extract, filing_multi. Mirrored EN/AR prompts, repeated runs, machine-graded. Costs are provider-billed USD.

| model_label     |   runs |   solved |   mean_cost |   total_spend |   mean_thinking |   mean_latency_s |   cost_per_success |   ar_over_en_cost |
|:----------------|-------:|---------:|------------:|--------------:|----------------:|-----------------:|-------------------:|------------------:|
| Claude Fable 5  |     16 |       14 |      0.9993 |       15.9882 |        135.875  |           8.2188 |             1.142  |              2.48 |
| GPT-5.6 Sol     |     16 |       16 |      0.0902 |        1.4429 |         72.5625 |           4.2188 |             0.0902 |              2.44 |
| Kimi K3         |     16 |       16 |      0.1267 |        2.027  |       1022.12   |          38.5812 |             0.1267 |              2.03 |
| Gemini 3.1 Pro  |     16 |       15 |      0.115  |        1.8399 |       1425.75   |          21.0062 |             0.1227 |              2.12 |
| GLM-5.3         |     16 |       15 |      0.0733 |        1.1723 |       2908      |          74.175  |             0.0782 |              2.43 |
| DeepSeek V4 Pro |     16 |       12 |      0.0289 |        0.4624 |       2944.88   |          72.45   |             0.0385 |              2.22 |


- `cost_per_success` = total spend on the task (failures included) / number of successes; blank = never succeeded.
- `ar_over_en_cost` = mean Arabic cost / mean English cost.
