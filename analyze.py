"""Aggregate results into per-experiment chart folders plus an overall
cross-experiment comparison, organized around the two research questions:

  1. The hypothesis: is sticker per-token price a good proxy for real cost?
  2. The Arabic impact: what does the same work cost in Arabic vs English?

Usage:  python analyze.py
Reads:  results/results.csv
Writes: charts/<experiment>/*.png + analysis.md   (one folder per experiment)
        charts/overall/*.png + analysis.md        (cross-experiment)
        results/summary.md                        (flat tables, unchanged)

Charts are working material (matplotlib defaults, no styling/branding).
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import MODELS

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "results", "results.csv")
CHARTS = os.path.join(HERE, "charts")
SUMMARY = os.path.join(HERE, "results", "summary.md")

ORDER = [m["label"] for m in MODELS]
STICKER_OUT = {m["label"]: m["sticker_out"] for m in MODELS}
STICKER_IN = {m["label"]: m["sticker_in"] for m in MODELS}

EXPERIMENTS = {
    "docqa": ("Report Q&A", ["docqa"]),
    "extract": ("Invoice extraction", ["extract"]),
    "agentic": ("Flight-search agent", ["agentic"]),
    "sudoku": ("Sudoku (moderate + extreme)", ["sudoku_moderate", "sudoku_extreme"]),
    "roster": ("Driver roster", ["roster"]),
    "filings": ("Tadawul filings", ["filing_extract", "filing_multi"]),
}


def _save(fig, folder, name):
    path = os.path.join(CHARTS, folder, name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _reindex(frame):
    return frame.reindex([m for m in ORDER if m in frame.index])


def sudoku_unbounded(df):
    """Sudoku rows in the unbounded condition: pass-2 (128K) for the five
    cap-compliant models, pass-1 for Kimi (its host ignores the cap)."""
    sub = df[df.task_type == "sudoku_moderate"]
    return pd.concat([sub[sub.max_tokens == 128000],
                      sub[sub.model_label == "Kimi K3"]])


def cost_per_success(sub):
    """Buyer-real metric: total spend on the task (failures included)
    divided by number of successes; NaN when never succeeded."""
    spent = sub.groupby("model_label").cost_usd.sum()
    wins = sub.groupby("model_label").success.sum()
    return spent / wins.replace(0, np.nan)


def per_experiment(df, key, title, types):
    folder = os.path.join(CHARTS, key)
    os.makedirs(folder, exist_ok=True)
    sub = df[df.task_type.isin(types)].copy()

    # Chart A: mean cost per run, EN vs AR.
    pivot = _reindex(sub.pivot_table(index="model_label", columns="lang",
                                     values="cost_usd", aggfunc="mean"))
    fig, ax = plt.subplots(figsize=(9, 5))
    pivot.plot(kind="bar", ax=ax, rot=20)
    ax.set_title(f"{title}: mean cost per run, USD (EN vs AR)")
    ax.set_xlabel("")
    _save(fig, key, "cost_per_run.png")

    # Chart B: token anatomy per model: billed input vs thinking vs visible output.
    anatomy = sub.groupby("model_label").agg(
        input=("prompt_tokens", "mean"), thinking=("reasoning_tokens", "mean"),
        completion=("completion_tokens", "mean"))
    anatomy["visible_output"] = (anatomy["completion"] - anatomy["thinking"]).clip(lower=0)
    anatomy = _reindex(anatomy[["input", "thinking", "visible_output"]])
    fig, ax = plt.subplots(figsize=(9, 5))
    anatomy.plot(kind="bar", stacked=True, ax=ax, rot=20, logy=True)
    ax.set_title(f"{title}: mean billed tokens per run (log scale)")
    ax.set_xlabel("")
    _save(fig, key, "token_anatomy.png")

    # Chart C (sudoku only): budget effect, pass 1 vs pass 2 solve rate.
    if key == "sudoku":
        mod = df[df.task_type == "sudoku_moderate"]
        p1 = mod[(mod.max_tokens == 16000)]
        p2 = sudoku_unbounded(df)
        rates = pd.DataFrame({
            "16K budget (pass 1)": p1.groupby("model_label").success.mean(),
            "unbounded (pass 2 / Kimi pass 1)": p2.groupby("model_label").success.mean(),
        })
        fig, ax = plt.subplots(figsize=(9, 5))
        _reindex(rates).plot(kind="bar", ax=ax, rot=20)
        ax.set_ylim(0, 1.05)
        ax.set_title("Moderate sudoku solve rate: customer budget vs unbounded")
        ax.set_xlabel("")
        _save(fig, key, "budget_effect.png")

    # analysis.md
    tbl = sub.groupby("model_label").agg(
        runs=("success", "size"), solved=("success", "sum"),
        mean_cost=("cost_usd", "mean"), total_spend=("cost_usd", "sum"),
        mean_thinking=("reasoning_tokens", "mean"),
        mean_latency_s=("latency_s", "mean"))
    tbl = _reindex(tbl).round(4)
    cps = cost_per_success(sub).astype(float).round(4)
    tbl["cost_per_success"] = cps

    ar_ratio = sub.pivot_table(index="model_label", columns="lang",
                               values="cost_usd", aggfunc="mean")
    if {"ar", "en"}.issubset(ar_ratio.columns):
        tbl["ar_over_en_cost"] = (ar_ratio["ar"] / ar_ratio["en"]).round(2)

    lines = [f"# {title}\n",
             f"Task types: {', '.join(types)}. Mirrored EN/AR prompts, "
             "repeated runs, machine-graded. Costs are provider-billed USD.\n",
             tbl.to_markdown(), "\n",
             "- `cost_per_success` = total spend on the task (failures "
             "included) / number of successes; blank = never succeeded.",
             "- `ar_over_en_cost` = mean Arabic cost / mean English cost.\n"]
    with open(os.path.join(folder, "analysis.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def overall(df):
    folder = os.path.join(CHARTS, "overall")
    os.makedirs(folder, exist_ok=True)

    bump_cols = [("docqa", "Doc Q&A", None), ("extract", "Invoice\nextract", None),
                 ("agentic", "Agentic", None), ("roster", "Roster", None),
                 ("sudoku_moderate", "Sudoku\n(unbounded)", "unbounded"),
                 ("filing_extract", "Filings\nextract", None),
                 ("filing_multi", "Filings\nmulti", None)]

    def bump_ranks(metric):
        cols = {"Sticker\nprice": pd.Series(STICKER_OUT).rank()}
        for t, label, special in bump_cols:
            sub = sudoku_unbounded(df) if special else df[df.task_type == t]
            if metric == "cost_per_task":
                r = sub.groupby("model_label").cost_usd.mean().rank()
            else:
                cps = cost_per_success(sub)
                r = cps.rank()
                r[sub.groupby("model_label").success.sum() == 0] = len(ORDER) + 1
            cols[label] = r
        return pd.DataFrame(cols).reindex(ORDER)

    # Hypothesis chart 1: rank bump, cost per task.
    for metric, fname, subtitle in [
            ("cost_per_task", "hypothesis_rank_bump.png",
             "rank by actual mean cost per task"),
            ("cost_per_success", "hypothesis_rank_bump_success.png",
             "rank by cost per SUCCESSFUL task (failure spend included)")]:
        ranks = bump_ranks(metric)
        never = len(ORDER) + 1
        fig, ax = plt.subplots(figsize=(12.5, 6.5))
        xs = range(len(ranks.columns))
        for model in ranks.index:
            y = ranks.loc[model].values
            ax.plot(xs, y, marker="o", linewidth=2.5, alpha=0.85)
            ax.annotate(model, (xs[-1] + 0.08, y[-1]), fontsize=9, va="center")
            ax.annotate(model, (xs[0] - 0.08, y[0]), fontsize=9,
                        va="center", ha="right")
        ax.set_xticks(list(xs))
        ax.set_xticklabels(ranks.columns, fontsize=9)
        yt = list(range(1, len(ORDER) + 1))
        if metric == "cost_per_success":
            yt.append(never)
            ax.axhspan(never - 0.5, never + 0.5, color="red", alpha=0.08)
            ax.set_yticks(yt)
            ax.set_yticklabels([str(i) for i in range(1, len(ORDER) + 1)]
                               + ["never\ndelivered"])
        else:
            ax.set_yticks(yt)
        ax.invert_yaxis()
        ax.set_xlim(-1.8, len(ranks.columns) + 0.9)
        ax.set_title("If the price sheet worked, these lines would be flat\n"
                     f"Rank by sticker output price vs. {subtitle}")
        ax.grid(axis="y", alpha=0.25)
        _save(fig, "overall", fname)

    # Hypothesis chart 2: sticker vs actual scatter (log-log), one point per
    # model per experiment.
    fig, ax = plt.subplots(figsize=(9, 6))
    for t, label, special in bump_cols:
        sub = sudoku_unbounded(df) if special else df[df.task_type == t]
        cost = sub.groupby("model_label").cost_usd.mean()
        for m in cost.index:
            ax.scatter(STICKER_OUT[m], cost[m], alpha=0.6)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Sticker output price, $/1M tokens (log)")
    ax.set_ylabel("Actual mean cost per task, $ (log)")
    ax.set_title("Sticker price vs. what tasks actually cost\n"
                 "(each dot: one model on one experiment)")
    _save(fig, "overall", "hypothesis_scatter.png")

    # Arabic impact 1: AR/EN cost ratio per model per experiment.
    ratio_rows = {}
    for t, label, special in bump_cols:
        sub = df[df.task_type == t]
        p = sub.pivot_table(index="model_label", columns="lang",
                            values="cost_usd", aggfunc="mean")
        if {"ar", "en"}.issubset(p.columns):
            ratio_rows[label.replace("\n", " ")] = p["ar"] / p["en"]
    ratios = _reindex(pd.DataFrame(ratio_rows))
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ratios.plot(kind="bar", ax=ax, rot=20)
    ax.axhline(1.0, color="black", linewidth=0.8)
    ax.set_title("The Arabic premium: mean Arabic cost / mean English cost "
                 "(1.0 = parity)")
    ax.set_xlabel("")
    _save(fig, "overall", "arabic_cost_ratio.png")

    # Arabic impact 2: success rates EN vs AR (all tasks pooled).
    sr = df.pivot_table(index="model_label", columns="lang", values="success",
                        aggfunc="mean")
    fig, ax = plt.subplots(figsize=(9, 5))
    _reindex(sr).plot(kind="bar", ax=ax, rot=20)
    ax.set_ylim(0, 1.05)
    ax.set_title("Success rate, English vs Arabic (all experiments pooled)")
    ax.set_xlabel("")
    _save(fig, "overall", "arabic_success_rate.png")

    # Meter behavior: input tokens for the identical document (docqa + MIS filing).
    rows = {}
    for tid, label in [("docqa_en", "Synthetic report (EN)"),
                       ("docqa_ar", "Synthetic report (AR)"),
                       ("filing_extract_mis_en", "MIS filing (EN)"),
                       ("filing_extract_mis_ar", "MIS filing (AR)")]:
        rows[label] = df[df.task_id == tid].groupby("model_label").prompt_tokens.first()
    meter = _reindex(pd.DataFrame(rows))
    fig, ax = plt.subplots(figsize=(11, 5.5))
    meter.plot(kind="bar", ax=ax, rot=20, logy=True)
    ax.set_title("Six meters, same documents: billed input tokens (log scale)\n"
                 "(0 = content-filter refusal, no tokens billed)")
    ax.set_xlabel("")
    _save(fig, "overall", "input_meter.png")

    # Cache effect: first run vs repeat runs of byte-identical prompts.
    firsts, repeats = [], []
    for (m, t), g in df.groupby(["model_label", "task_id"]):
        g = g.sort_values("timestamp")
        if len(g) >= 2:
            firsts.append((m, g.cost_usd.iloc[0]))
            repeats.append((m, g.cost_usd.iloc[1:].mean()))
    f1 = pd.DataFrame(firsts, columns=["m", "c"]).groupby("m").c.mean()
    f2 = pd.DataFrame(repeats, columns=["m", "c"]).groupby("m").c.mean()
    cache = _reindex(pd.DataFrame({"first run (cold)": f1, "repeat runs (warm)": f2}))
    fig, ax = plt.subplots(figsize=(9, 5))
    cache.plot(kind="bar", ax=ax, rot=20)
    ax.set_title("Cache economics: mean cost, first run vs byte-identical repeats")
    ax.set_xlabel("")
    _save(fig, "overall", "cache_effect.png")

    # analysis.md with the Spearman table.
    try:
        from scipy.stats import spearmanr
        lines_sp = ["| Experiment | sticker vs cost/task | sticker vs cost/success |",
                    "|---|---|---|"]
        for t, label, special in bump_cols:
            sub = sudoku_unbounded(df) if special else df[df.task_type == t]
            cost = sub.groupby("model_label").cost_usd.mean()
            models = [m for m in cost.index if m in STICKER_OUT]
            r1 = spearmanr([STICKER_OUT[m] for m in models],
                           [cost[m] for m in models]).statistic
            cps = cost_per_success(sub).dropna()
            ms = [m for m in cps.index if m in STICKER_OUT]
            r2 = (spearmanr([STICKER_OUT[m] for m in ms],
                            [cps[m] for m in ms]).statistic
                  if len(ms) > 2 else float("nan"))
            lines_sp.append(f"| {label.replace(chr(10), ' ')} | {r1:.2f} | {r2:.2f} |")
        spearman_md = "\n".join(lines_sp)
    except ImportError:
        spearman_md = "(scipy not installed; Spearman table skipped)"

    with open(os.path.join(folder, "analysis.md"), "w", encoding="utf-8") as f:
        f.write("# Overall: the hypothesis and the Arabic impact\n\n"
                "**Hypothesis** (see repo README): sticker per-token price is "
                "not a reliable proxy for real cost. Rank correlations between "
                "sticker output price and measured costs (1.0 = price sheet "
                "predicts the bill):\n\n" + spearman_md + "\n\n"
                "Charts: `hypothesis_rank_bump*.png` (rank trajectories), "
                "`hypothesis_scatter.png` (price vs bill, log-log), "
                "`arabic_cost_ratio.png` and `arabic_success_rate.png` (the "
                "Arabic premium in money and in reliability), "
                "`input_meter.png` (same documents, six billed token counts), "
                "`cache_effect.png` (cold vs warm identical requests).\n")


def flat_summary(df):
    lines = ["# Results summary\n"]
    df["thinking_share"] = df.reasoning_tokens / df.completion_tokens.replace(0, pd.NA)
    agg = df.groupby("model_label").agg(
        calls=("cost_usd", "size"), total_cost=("cost_usd", "sum"),
        success_rate=("success", "mean"),
        thinking_share=("thinking_share", "mean")).reindex(ORDER)
    agg["sticker_out_per_M"] = [STICKER_OUT.get(i) for i in agg.index]
    lines += ["## Totals per model\n", agg.round(4).to_markdown()]

    ok = df[df.success]
    cps = ok.groupby(["model_label", "task_type"]).cost_usd.mean().unstack()
    lines += ["\n\n## Mean cost of successful runs\n", cps.round(4).to_markdown()]

    sr = df.groupby(["model_label", "task_type"]).success.mean().unstack()
    lines += ["\n\n## Success rate by model and task type\n", sr.round(2).to_markdown()]

    var = (df.groupby(["model_label", "task_id"]).cost_usd
             .agg(["min", "max", "count"]).reset_index())
    var = var[var["count"] > 1]
    var["max_over_min"] = var["max"] / var["min"].replace(0, pd.NA)
    worst = var.sort_values("max_over_min", ascending=False).head(15)
    lines += ["\n\n## Largest run-to-run cost swings (same model, same task)\n",
              worst[["model_label", "task_id", "min", "max", "max_over_min"]]
              .round(4).to_markdown(index=False)]

    with open(SUMMARY, "w", encoding="utf-8") as f:
        f.write("\n".join(str(x) for x in lines) + "\n")


def main():
    df = pd.read_csv(CSV_PATH)
    df["success"] = df["success"].astype(str).str.lower() == "true"
    os.makedirs(CHARTS, exist_ok=True)

    for key, (title, types) in EXPERIMENTS.items():
        per_experiment(df, key, title, types)
    overall(df)
    flat_summary(df)

    print(f"Per-experiment folders + overall written under {CHARTS}")
    print(f"Summary written to {SUMMARY}")


if __name__ == "__main__":
    main()
