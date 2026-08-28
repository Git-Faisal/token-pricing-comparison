# Sudoku (moderate + extreme)

Task types: sudoku_moderate, sudoku_extreme. Mirrored EN/AR prompts, repeated runs, machine-graded. Costs are provider-billed USD.

| model_label     |   runs |   solved |   mean_cost |   total_spend |   mean_thinking |   mean_latency_s |   cost_per_success |   ar_over_en_cost |
|:----------------|-------:|---------:|------------:|--------------:|----------------:|-----------------:|-------------------:|------------------:|
| Claude Fable 5  |     16 |        4 |      1.7367 |       27.7877 |         34480.1 |          338.869 |             6.9469 |              1.01 |
| GPT-5.6 Sol     |     16 |        0 |      0.1776 |        2.8422 |         11746.5 |          184.6   |           nan      |              0.89 |
| Kimi K3         |      8 |        6 |      0.5954 |        4.7636 |         45918.2 |         1578.89  |             0.7939 |              0.61 |
| Gemini 3.1 Pro  |     16 |        1 |      0.344  |        5.5045 |         28138.9 |          189.719 |             5.5045 |              1.04 |
| GLM-5.3         |     16 |        2 |      0.167  |        2.6713 |         37888.8 |          402.413 |             1.3356 |              0.96 |
| DeepSeek V4 Pro |     16 |        4 |      0.1122 |        1.7949 |         42572.4 |          452.863 |             0.4487 |              1.08 |


- `cost_per_success` = total spend on the task (failures included) / number of successes; blank = never succeeded.
- `ar_over_en_cost` = mean Arabic cost / mean English cost.
