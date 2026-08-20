# Results summary

## Totals per model

| model_label     |   calls |   total_cost |   success_rate |   thinking_share |   sticker_out_per_M |
|:----------------|--------:|-------------:|---------------:|-----------------:|--------------------:|
| Claude Fable 5  |      38 |      29.2529 |         0.5526 |         0.616609 |               50    |
| GPT-5.6 Sol     |      38 |       2.9903 |         0.5789 |         0.516773 |               15    |
| Kimi K3         |      30 |       5.545  |         0.9333 |         0.734233 |               15    |
| Gemini 3.1 Pro  |      38 |       6.3042 |         0.6053 |         0.945488 |               12    |
| GLM-5.3         |      38 |       3.4146 |         0.6053 |         0.819959 |                4.4  |
| DeepSeek V4 Pro |      38 |       2.1465 |         0.6842 |         0.812433 |                1.98 |


## Cost per successful task (mean cost of successful runs; blank = never succeeded)

| model_label     |   agentic |   docqa |   extract |   roster |   sudoku_moderate |
|:----------------|----------:|--------:|----------:|---------:|------------------:|
| Claude Fable 5  |    0.0225 |  0.0099 |    0.0106 |   0.3133 |            0.9407 |
| DeepSeek V4 Pro |    0.0012 |  0.001  |    0.0022 |   0.0814 |            0.0997 |
| GLM-5.3         |    0.001  |  0.0009 |    0.0028 |   0.0505 |            0.154  |
| GPT-5.6 Sol     |    0.002  |  0.0018 |    0.0016 |   0.029  |          nan      |
| Gemini 3.1 Pro  |    0.0079 |  0.0097 |    0.0141 |   0.1525 |            0.4999 |
| Kimi K3         |    0.0048 |  0.0031 |    0.0064 |   0.174  |            0.5335 |


## Success rate by model and task type

| model_label     |   agentic |   docqa |   extract |   roster |   sudoku_extreme |   sudoku_moderate |
|:----------------|----------:|--------:|----------:|---------:|-----------------:|------------------:|
| Claude Fable 5  |         1 |     0.5 |      0.67 |     1    |                0 |               0.4 |
| DeepSeek V4 Pro |         1 |     1   |      1    |     1    |                0 |               0.4 |
| GLM-5.3         |         1 |     1   |      1    |     0.75 |                0 |               0.2 |
| GPT-5.6 Sol     |         1 |     1   |      1    |     1    |                0 |               0   |
| Gemini 3.1 Pro  |         1 |     1   |      1    |     1    |                0 |               0.1 |
| Kimi K3         |         1 |     1   |      1    |     1    |                0 |               1   |


## Largest run-to-run cost swings (same model, same task)

| model_label     | task_id            |    min |    max |   max_over_min |
|:----------------|:-------------------|-------:|-------:|---------------:|
| GLM-5.3         | roster_en          | 0.0585 | 0.5637 |        9.6392  |
| DeepSeek V4 Pro | extract_ar         | 0.0008 | 0.0054 |        6.85548 |
| GLM-5.3         | sudoku_extreme_en  | 0.1408 | 0.5634 |        4.00024 |
| GLM-5.3         | sudoku_extreme_ar  | 0.1409 | 0.5634 |        3.99896 |
| Claude Fable 5  | sudoku_extreme_en  | 1.6017 | 6.4017 |        3.99685 |
| Claude Fable 5  | sudoku_extreme_ar  | 1.6024 | 6.4024 |        3.99543 |
| DeepSeek V4 Pro | docqa_ar           | 0.0007 | 0.0025 |        3.7079  |
| DeepSeek V4 Pro | docqa_en           | 0.0004 | 0.0011 |        2.8704  |
| Kimi K3         | extract_ar         | 0.0055 | 0.015  |        2.74556 |
| GPT-5.6 Sol     | sudoku_moderate_ar | 0.0766 | 0.2069 |        2.7032  |
| Gemini 3.1 Pro  | sudoku_moderate_ar | 0.1856 | 0.4999 |        2.69328 |
| GLM-5.3         | sudoku_moderate_en | 0.0704 | 0.1775 |        2.51963 |
| Gemini 3.1 Pro  | sudoku_moderate_en | 0.1922 | 0.4464 |        2.32226 |
| GLM-5.3         | docqa_en           | 0.0005 | 0.001  |        2.13412 |
| GLM-5.3         | docqa_ar           | 0.0008 | 0.0017 |        2.06466 |
