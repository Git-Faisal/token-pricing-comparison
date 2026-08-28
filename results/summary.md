# Results summary

## Totals per model

| model_label     |   calls |   total_cost |   success_rate |   thinking_share |   sticker_out_per_M |
|:----------------|--------:|-------------:|---------------:|-----------------:|--------------------:|
| Claude Fable 5  |      54 |      45.241  |         0.6481 |         0.561566 |               50    |
| GPT-5.6 Sol     |      54 |       4.4332 |         0.7037 |         0.488278 |               15    |
| Kimi K3         |      46 |       7.572  |         0.9565 |         0.802186 |               15    |
| Gemini 3.1 Pro  |      54 |       8.1441 |         0.7037 |         0.948254 |               12    |
| GLM-5.3         |      54 |       4.5869 |         0.7037 |         0.862589 |                4.4  |
| DeepSeek V4 Pro |      54 |       2.6089 |         0.7037 |         0.860739 |                1.98 |


## Cost per successful task (mean cost of successful runs; blank = never succeeded)

| model_label     |   agentic |   docqa |   extract |   filing_extract |   filing_multi |   roster |   sudoku_moderate |
|:----------------|----------:|--------:|----------:|-----------------:|---------------:|---------:|------------------:|
| Claude Fable 5  |    0.0225 |  0.0099 |    0.0106 |           0.6698 |         1.1416 |   0.3133 |            0.9407 |
| DeepSeek V4 Pro |    0.0012 |  0.001  |    0.0022 |           0.0144 |         0.033  |   0.0814 |            0.0997 |
| GLM-5.3         |    0.001  |  0.0009 |    0.0028 |           0.0544 |         0.1304 |   0.0505 |            0.154  |
| GPT-5.6 Sol     |    0.002  |  0.0018 |    0.0016 |           0.0602 |         0.1802 |   0.029  |          nan      |
| Gemini 3.1 Pro  |    0.0079 |  0.0097 |    0.0141 |           0.0719 |         0.2063 |   0.1525 |            0.4999 |
| Kimi K3         |    0.0048 |  0.0031 |    0.0064 |           0.0902 |         0.2361 |   0.174  |            0.5335 |


## Success rate by model and task type

| model_label     |   agentic |   docqa |   extract |   filing_extract |   filing_multi |   roster |   sudoku_extreme |   sudoku_moderate |
|:----------------|----------:|--------:|----------:|-----------------:|---------------:|---------:|-----------------:|------------------:|
| Claude Fable 5  |         1 |     0.5 |      0.67 |             1    |           0.5  |     1    |                0 |               0.4 |
| DeepSeek V4 Pro |         1 |     1   |      1    |             0.83 |           0.5  |     1    |                0 |               0.4 |
| GLM-5.3         |         1 |     1   |      1    |             0.92 |           1    |     0.75 |                0 |               0.2 |
| GPT-5.6 Sol     |         1 |     1   |      1    |             1    |           1    |     1    |                0 |               0   |
| Gemini 3.1 Pro  |         1 |     1   |      1    |             1    |           0.75 |     1    |                0 |               0.1 |
| Kimi K3         |         1 |     1   |      1    |             1    |           1    |     1    |                0 |               1   |


## Largest run-to-run cost swings (same model, same task)

| model_label     | task_id                   |    min |    max |   max_over_min |
|:----------------|:--------------------------|-------:|-------:|---------------:|
| DeepSeek V4 Pro | filing_multi_ar           | 0.0109 | 0.135  |       12.43    |
| GPT-5.6 Sol     | filing_extract_alrajhi_ar | 0.0231 | 0.2849 |       12.3131  |
| DeepSeek V4 Pro | filing_extract_aramco_ar  | 0.0037 | 0.0454 |       12.286   |
| GPT-5.6 Sol     | filing_multi_ar           | 0.04   | 0.4714 |       11.77    |
| GPT-5.6 Sol     | filing_extract_alrajhi_en | 0.0057 | 0.0667 |       11.7389  |
| GPT-5.6 Sol     | filing_extract_mis_ar     | 0.004  | 0.046  |       11.5506  |
| GPT-5.6 Sol     | filing_extract_aramco_ar  | 0.0124 | 0.1412 |       11.4015  |
| GPT-5.6 Sol     | filing_multi_en           | 0.0171 | 0.1923 |       11.2154  |
| GPT-5.6 Sol     | filing_extract_mis_en     | 0.0031 | 0.0346 |       11.1121  |
| GPT-5.6 Sol     | filing_extract_aramco_en  | 0.0083 | 0.0919 |       11.0467  |
| GLM-5.3         | roster_en                 | 0.0585 | 0.5637 |        9.6392  |
| DeepSeek V4 Pro | filing_multi_en           | 0.0064 | 0.0596 |        9.299   |
| Kimi K3         | filing_extract_alrajhi_ar | 0.0371 | 0.3062 |        8.24554 |
| Kimi K3         | filing_multi_ar           | 0.0742 | 0.5856 |        7.89783 |
| Kimi K3         | filing_extract_mis_ar     | 0.0113 | 0.0811 |        7.15772 |
