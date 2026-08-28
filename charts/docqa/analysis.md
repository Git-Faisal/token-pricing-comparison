# Report Q&A

Task types: docqa. Mirrored EN/AR prompts, repeated runs, machine-graded. Costs are provider-billed USD.

| model_label     |   runs |   solved |   mean_cost |   total_spend |   mean_thinking |   mean_latency_s |   cost_per_success |   ar_over_en_cost |
|:----------------|-------:|---------:|------------:|--------------:|----------------:|-----------------:|-------------------:|------------------:|
| Claude Fable 5  |      6 |        3 |      0.0049 |        0.0297 |          0      |           4.45   |             0.0099 |              0    |
| GPT-5.6 Sol     |      6 |        6 |      0.0018 |        0.0107 |          0      |           2.2    |             0.0018 |              1.25 |
| Kimi K3         |      6 |        6 |      0.0031 |        0.0187 |         85.1667 |           5.6167 |             0.0031 |              1.57 |
| Gemini 3.1 Pro  |      6 |        6 |      0.0097 |        0.058  |        648.333  |           7.6833 |             0.0097 |              1.31 |
| GLM-5.3         |      6 |        6 |      0.0009 |        0.0054 |         64.8333 |           3.9167 |             0.0009 |              1.6  |
| DeepSeek V4 Pro |      6 |        6 |      0.001  |        0.0057 |        124      |           4.15   |             0.001  |              2    |


- `cost_per_success` = total spend on the task (failures included) / number of successes; blank = never succeeded.
- `ar_over_en_cost` = mean Arabic cost / mean English cost.
