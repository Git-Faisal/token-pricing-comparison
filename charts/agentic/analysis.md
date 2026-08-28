# Flight-search agent

Task types: agentic. Mirrored EN/AR prompts, repeated runs, machine-graded. Costs are provider-billed USD.

| model_label     |   runs |   solved |   mean_cost |   total_spend |   mean_thinking |   mean_latency_s |   cost_per_success |   ar_over_en_cost |
|:----------------|-------:|---------:|------------:|--------------:|----------------:|-----------------:|-------------------:|------------------:|
| Claude Fable 5  |      6 |        6 |      0.0225 |        0.1353 |          0      |          11.8667 |             0.0225 |              1.08 |
| GPT-5.6 Sol     |      6 |        6 |      0.002  |        0.0118 |          0      |           8.45   |             0.002  |              1.1  |
| Kimi K3         |      6 |        6 |      0.0048 |        0.0287 |        107.833  |          11.5833 |             0.0048 |              1.1  |
| Gemini 3.1 Pro  |      6 |        6 |      0.0079 |        0.0472 |        528.167  |           9.9667 |             0.0079 |              1.26 |
| GLM-5.3         |      6 |        6 |      0.001  |        0.0062 |         64.8333 |          12.25   |             0.001  |              1.17 |
| DeepSeek V4 Pro |      6 |        6 |      0.0012 |        0.0073 |         60.3333 |           5.95   |             0.0012 |              0.87 |


- `cost_per_success` = total spend on the task (failures included) / number of successes; blank = never succeeded.
- `ar_over_en_cost` = mean Arabic cost / mean English cost.
