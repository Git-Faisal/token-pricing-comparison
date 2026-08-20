"""Auditability check: can the provider's billed token counts be reproduced
with a publicly available tokenizer?

For each result row, re-tokenize the exact prompt text (and the visible
output text) with the lab's public tokenizer, where one exists:

  - OpenAI  : tiktoken o200k_base (assumed encoding for current models)
  - DeepSeek: official `deepseek-tokenizer` package

For labs with no public tokenizer (Anthropic, Google, Moonshot*, Zhipu*),
no independent recount is possible — which is itself a finding.
(*weights are open but the billing tokenizer is not documented.)

Notes:
  - Billed prompt tokens include the provider's chat-template overhead
    (role markers, special tokens), so a small constant gap above the raw
    text count is expected. Large or proportional gaps are not.
  - Reasoning tokens can only be recounted when the raw reasoning text is
    returned by the API (DeepSeek does; most labs do not).

Usage: python reconcile.py     ->  results/reconcile.csv + console table
"""

import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "results", "results.csv")
OUT_PATH = os.path.join(HERE, "results", "reconcile.csv")

COUNTERS = {}
try:
    import tiktoken
    _enc = tiktoken.get_encoding("o200k_base")
    COUNTERS["openai/"] = ("tiktoken o200k_base", lambda s: len(_enc.encode(s)))
except ImportError:
    pass
try:
    from deepseek_tokenizer import ds_token
    COUNTERS["deepseek/"] = ("deepseek-tokenizer", lambda s: len(ds_token.encode(s)))
except ImportError:
    pass


def texts_from_raw(raw_path: str):
    with open(os.path.join(HERE, raw_path.replace("results/", "results" + os.sep)),
              encoding="utf-8") as f:
        blob = json.load(f)
    prompt_text = "".join(m.get("content") or "" for m in blob["request_messages"]
                          if m["role"] in ("user", "tool"))
    output_text, reasoning_text = "", ""
    for resp in blob["responses"]:
        msg = (resp.get("choices") or [{}])[0].get("message", {}) or {}
        output_text += msg.get("content") or ""
        reasoning_text += msg.get("reasoning") or ""
    return prompt_text, output_text, reasoning_text


def main():
    df = pd.read_csv(CSV_PATH)
    rows = []
    for _, r in df.iterrows():
        prefix = next((p for p in COUNTERS if str(r.model_id).startswith(p)), None)
        if prefix is None:
            rows.append({"model_label": r.model_label, "task_id": r.task_id, "run": r.run,
                         "tokenizer": "NONE PUBLIC", "billed_prompt": r.prompt_tokens,
                         "recount_prompt": None, "prompt_gap": None,
                         "billed_completion": r.completion_tokens, "recount_visible_output": None,
                         "reasoning_recountable": False})
            continue
        name, count = COUNTERS[prefix]
        try:
            prompt_text, output_text, reasoning_text = texts_from_raw(r.raw_file)
        except (FileNotFoundError, KeyError):
            continue
        recount_prompt = count(prompt_text)
        recount_out = count(output_text) + (count(reasoning_text) if reasoning_text else 0)
        rows.append({
            "model_label": r.model_label, "task_id": r.task_id, "run": r.run,
            "tokenizer": name,
            "billed_prompt": r.prompt_tokens, "recount_prompt": recount_prompt,
            "prompt_gap": int(r.prompt_tokens) - recount_prompt,
            "billed_completion": r.completion_tokens,
            "recount_visible_output": recount_out,
            "reasoning_recountable": bool(reasoning_text),
        })

    out = pd.DataFrame(rows)
    out.to_csv(OUT_PATH, index=False)
    print(out.groupby(["model_label", "tokenizer"])
          .agg(rows=("task_id", "size"),
               mean_prompt_gap=("prompt_gap", "mean"),
               reasoning_recountable=("reasoning_recountable", "mean"))
          .round(1))
    print(f"\nWritten: {OUT_PATH}")


if __name__ == "__main__":
    main()
