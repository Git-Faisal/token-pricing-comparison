# Invoice extraction

Task types: extract. Mirrored EN/AR prompts, repeated runs, machine-graded. Costs are provider-billed USD.

| model_label     |   runs |   solved |   mean_cost |   total_spend |   mean_thinking |   mean_latency_s |   cost_per_success |   ar_over_en_cost |
|:----------------|-------:|---------:|------------:|--------------:|----------------:|-----------------:|-------------------:|------------------:|
| Claude Fable 5  |      6 |        4 |      0.0078 |        0.0471 |          7.6667 |           6.3167 |             0.0118 |              2.26 |
| GPT-5.6 Sol     |      6 |        6 |      0.0016 |        0.0096 |          0      |           2.5    |             0.0016 |              1.02 |
| Kimi K3         |      6 |        6 |      0.0064 |        0.0383 |        298.333  |          11.85   |             0.0064 |              2.61 |
| Gemini 3.1 Pro  |      6 |        6 |      0.0141 |        0.0843 |       1018.67   |          10.25   |             0.0141 |              0.88 |
| GLM-5.3         |      6 |        6 |      0.0028 |        0.0166 |        491.667  |           8.3833 |             0.0028 |              3.35 |
| DeepSeek V4 Pro |      6 |        6 |      0.0022 |        0.0129 |        413.333  |          11.4333 |             0.0022 |              3.49 |


- `cost_per_success` = total spend on the task (failures included) / number of successes; blank = never succeeded.
- `ar_over_en_cost` = mean Arabic cost / mean English cost.
