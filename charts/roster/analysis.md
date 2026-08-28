# Driver roster

Task types: roster. Mirrored EN/AR prompts, repeated runs, machine-graded. Costs are provider-billed USD.

| model_label     |   runs |   solved |   mean_cost |   total_spend |   mean_thinking |   mean_latency_s |   cost_per_success |   ar_over_en_cost |
|:----------------|-------:|---------:|------------:|--------------:|----------------:|-----------------:|-------------------:|------------------:|
| Claude Fable 5  |      4 |        4 |      0.3133 |        1.2532 |         5926.75 |           73.8   |             0.3133 |              0.78 |
| GPT-5.6 Sol     |      4 |        4 |      0.029  |        0.116  |         1757.25 |           41.175 |             0.029  |              0.98 |
| Kimi K3         |      4 |        4 |      0.174  |        0.6958 |        11416.2  |          387.9   |             0.174  |              0.93 |
| Gemini 3.1 Pro  |      4 |        4 |      0.1525 |        0.6102 |        12417    |           91.85  |             0.1525 |              1.08 |
| GLM-5.3         |      4 |        3 |      0.1788 |        0.7151 |        40416    |          489.1   |             0.2384 |              0.15 |
| DeepSeek V4 Pro |      4 |        4 |      0.0814 |        0.3257 |        20331.8  |          321.725 |             0.0814 |              0.75 |


- `cost_per_success` = total spend on the task (failures included) / number of successes; blank = never succeeded.
- `ar_over_en_cost` = mean Arabic cost / mean English cost.
