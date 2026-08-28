"""Aggregate results and produce raw working charts (matplotlib defaults,
no styling/branding) plus a markdown summary of the key tables.

Usage: python analyze.py
Reads  results/results.csv
Writes charts/*.png and results/summary.md
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import MODELS

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "results", "results.csv")
CHARTS = os.path.join(HERE, "charts")
SUMMARY = os.path.join(HERE, "results", "summary.md")

ORDER = [m["label"] for m in MODELS]
STICKER_OUT = {m["label"]: m["sticker_out"] for m in MODELS}
STICKER_IN = {m["label"]: m["sticker_in"] for m in MODELS}


def bar_grouped(df: pd.DataFrame, value: str, title: str, fname: str, logy: bool = False):
    pivot = df.pivot_table(index="model_label", columns="lang", values=value, aggfunc="mean")
    pivot = pivot.reindex([m for m in ORDER if m in pivot.index])
    ax = pivot.plot(kind="bar", figsize=(10, 5), rot=20, logy=logy)
    ax.set_title(title)
    ax.set_xlabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS, fname), dpi=150)
    plt.close()


def main():
    os.makedirs(CHARTS, exist_ok=True)
    df = pd.read_csv(CSV_PATH)
    df["success"] = df["success"].astype(str).str.lower() == "true"

    # 1. The input meter: identical document, billed input token counts.
    docqa = df[df.task_type == "docqa"]
    bar_grouped(docqa, "prompt_tokens",
                "Same document, six meters: billed input tokens (doc Q&A task)",
                "1_input_meter.png")

    # 2. Cost per task (mean across runs), by task type, English tasks.
    for lang in ("en", "ar"):
        sub = df[df.lang == lang]
        pivot = sub.pivot_table(index="model_label", columns="task_type",
                                values="cost_usd", aggfunc="mean")
        pivot = pivot.reindex([m for m in ORDER if m in pivot.index])
        ax = pivot.plot(kind="bar", figsize=(11, 5), rot=20, logy=True)
        ax.set_title(f"Actual cost per task, USD (log scale) — {lang.upper()} tasks")
        ax.set_xlabel("")
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS, f"2_cost_per_task_{lang}.png"), dpi=150)
        plt.close()

    # 3. Sticker price vs actual cost share.
    total = df.groupby("model_label").cost_usd.sum().reindex(ORDER)
    sticker = pd.Series(STICKER_OUT).reindex(ORDER)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sticker.plot(kind="bar", ax=axes[0], rot=20, title="Sticker price (output, $/1M tokens)")
    total.plot(kind="bar", ax=axes[1], rot=20, title="Actual total spend in this experiment ($)")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS, "3_sticker_vs_actual.png"), dpi=150)
    plt.close()

    # 4. Language penalty: AR cost / EN cost per model per task type.
    pivot = df.pivot_table(index=["model_label", "task_type"], columns="lang",
                           values="cost_usd", aggfunc="mean").reset_index()
    if {"ar", "en"}.issubset(pivot.columns):
        pivot["ar_over_en"] = pivot["ar"] / pivot["en"]
        ratio = pivot.pivot_table(index="model_label", columns="task_type", values="ar_over_en")
        ratio = ratio.reindex([m for m in ORDER if m in ratio.index])
        ax = ratio.plot(kind="bar", figsize=(11, 5), rot=20)
        ax.axhline(1.0, color="black", linewidth=0.8)
        ax.set_title("Language penalty: Arabic cost / English cost (1.0 = parity)")
        ax.set_xlabel("")
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS, "4_language_penalty.png"), dpi=150)
        plt.close()

    # 5. Thinking share of output tokens.
    df["thinking_share"] = df.reasoning_tokens / df.completion_tokens.replace(0, pd.NA)
    share = df.groupby("model_label").thinking_share.mean().reindex(ORDER)
    ax = share.plot(kind="bar", figsize=(9, 5), rot=20)
    ax.set_title("Share of billed output tokens that are invisible thinking (mean)")
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS, "5_thinking_share.png"), dpi=150)
    plt.close()

    # 6. Run-to-run variance on the same task (max/min cost across runs).
    var = (df.groupby(["model_label", "task_id"]).cost_usd
             .agg(["min", "max", "count"]).reset_index())
    var = var[var["count"] > 1]
    var["max_over_min"] = var["max"] / var["min"].replace(0, pd.NA)
    worst = var.sort_values("max_over_min", ascending=False).head(15)


    # 7. Rank bump: sticker rank vs actual cost rank per task.
    sticker_rank = pd.Series(STICKER_OUT).rank()
    cols = {"Sticker
price": sticker_rank}
    for t, label in [("docqa", "Doc Q&A"), ("extract", "Invoice
extract"),
                     ("agentic", "Agentic"), ("roster", "Roster"),
                     ("sudoku_moderate", "Sudoku
(128K)")]:
        sub = df[df.task_type == t]
        if t == "sudoku_moderate" and "max_tokens" in df.columns:
            sub = pd.concat([sub[sub.max_tokens == 128000],
                             sub[sub.model_label == "Kimi K3"]])
        cols[label] = sub.groupby("model_label").cost_usd.mean().rank()
    ranks = pd.DataFrame(cols).reindex(ORDER)
    fig, ax = plt.subplots(figsize=(11, 6))
    xs = range(len(ranks.columns))
    for model in ranks.index:
        y = ranks.loc[model].values
        ax.plot(xs, y, marker="o", linewidth=2.5, alpha=0.85)
        ax.annotate(model, (xs[-1] + 0.08, y[-1]), fontsize=9, va="center")
        ax.annotate(model, (xs[0] - 0.08, y[0]), fontsize=9, va="center", ha="right")
    ax.set_xticks(list(xs)); ax.set_xticklabels(ranks.columns)
    ax.set_yticks(range(1, len(ranks) + 1)); ax.invert_yaxis()
    ax.set_xlim(-1.6, len(ranks.columns) + 0.8)
    ax.set_title("Rank by sticker price vs. rank by actual mean cost per task")
    ax.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS, "7_rank_bump.png"), dpi=150)
    plt.close()

    # ---- summary tables ----
    lines = ["# Results summary\n"]
    lines.append("## Totals per model\n")
    agg = df.groupby("model_label").agg(
        calls=("cost_usd", "size"), total_cost=("cost_usd", "sum"),
        success_rate=("success", "mean"),
        thinking_share=("thinking_share", "mean")).reindex(ORDER)
    agg["sticker_out_per_M"] = [STICKER_OUT.get(i) for i in agg.index]
    lines.append(agg.round(4).to_markdown())

    lines.append("\n\n## Cost per successful task (mean cost of successful runs; blank = never succeeded)\n")
    ok = df[df.success]
    cps = ok.groupby(["model_label", "task_type"]).cost_usd.mean().unstack()
    lines.append(cps.round(4).to_markdown())

    lines.append("\n\n## Success rate by model and task type\n")
    sr = df.groupby(["model_label", "task_type"]).success.mean().unstack()
    lines.append(sr.round(2).to_markdown())

    lines.append("\n\n## Largest run-to-run cost swings (same model, same task)\n")
    lines.append(worst[["model_label", "task_id", "min", "max", "max_over_min"]]
                 .round(4).to_markdown(index=False))

    with open(SUMMARY, "w", encoding="utf-8") as f:
        f.write("\n".join(str(x) for x in lines) + "\n")

    print(f"Charts written to {CHARTS}")
    print(f"Summary written to {SUMMARY}")


if __name__ == "__main__":
    main()
