"""Experiment runner.

Executes every (model x task x run) cell, records the provider-billed token
counts and dollar cost for each call, grades task success, and writes:

  results/results.csv   one row per (model, task, run)
  results/raw/*.json    full API responses, for audit and replication

Usage:
  python runner.py --plan                 # show what would run, no spend
  python runner.py --models deepseek,glm  # only these models (substring match)
  python runner.py --tasks docqa          # only these tasks (substring match)
  python runner.py --runs 1               # override runs per cell
  python runner.py                        # full matrix

The API key is read from OPENROUTER_API_KEY or a .openrouter_key file
(this directory or its parent). The key is never written to any output.
"""

import argparse
import csv
import json
import os
import re
import time

import requests

from config import (API_URL, APP_HEADERS, DEFAULT_RUNS, KEY_PATHS, MAX_RETRIES,
                    MODELS, REQUEST_TIMEOUT_S, RUNS_OVERRIDE)
from tasks import TASKS

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")
RAW_DIR = os.path.join(RESULTS_DIR, "raw")
CSV_PATH = os.path.join(RESULTS_DIR, "results.csv")

CSV_FIELDS = [
    "timestamp", "model_label", "model_id", "task_id", "task_type", "lang", "run",
    "provider", "prompt_tokens", "completion_tokens", "reasoning_tokens",
    "cached_tokens", "total_tokens", "cost_usd", "latency_s", "finish_reason",
    "turns", "tool_used", "success", "answer_excerpt", "raw_file",
]

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def load_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    for rel in KEY_PATHS:
        path = os.path.join(HERE, rel)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read().strip()
    raise SystemExit("No API key: set OPENROUTER_API_KEY or create a .openrouter_key file.")


def post_chat(key: str, body: dict) -> dict:
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", **APP_HEADERS}
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(API_URL, headers=headers, json=body, timeout=REQUEST_TIMEOUT_S)
            if resp.status_code == 200:
                data = resp.json()
                if "error" in data and not data.get("choices"):
                    raise RuntimeError(f"API error: {data['error']}")
                return data
            if resp.status_code in (408, 429, 500, 502, 503, 524):
                last_err = f"HTTP {resp.status_code}: {resp.text[:200]}"
                time.sleep(5 * attempt)
                continue
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:500]}")
        except requests.RequestException as e:
            last_err = str(e)
            time.sleep(5 * attempt)
    raise RuntimeError(f"Request failed after {MAX_RETRIES} attempts: {last_err}")


# ---------------- grading ----------------

def _norm(text: str) -> str:
    return (text or "").translate(ARABIC_DIGITS)


def _extract_json(text: str):
    text = _norm(text)
    text = re.sub(r"```(?:json)?", "", text)
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None


def _num(value) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    m = re.findall(r"[\d.]+", str(value).replace(",", ""))
    return float(m[0]) if m else float("nan")


def grade(task: dict, final_text: str, tool_used: bool) -> bool:
    spec = task["grade"]
    text = _norm(final_text)
    kind = spec["kind"]
    if kind == "contains_all":
        return all(any(opt in text for opt in group) for group in spec["expected"])
    if kind == "json_fields":
        obj = _extract_json(text)
        if not isinstance(obj, dict):
            return False
        for field, want in spec["expected"].items():
            got = obj.get(field)
            if got is None:
                return False
            if isinstance(want, (int, float)):
                if abs(_num(got) - float(want)) > 0.01:
                    return False
            elif str(want).lower() not in str(got).lower():
                return False
        return True
    if kind == "sudoku":
        matches = re.findall(r"FINAL:\s*([1-9]{81})", text) or re.findall(r"([1-9]{81})", text)
        return bool(matches) and matches[-1] == spec["expected"]
    if kind == "agentic":
        return tool_used and all(exp in text for exp in spec["expected"])
    if kind == "roster":
        obj = _extract_json(text)
        if not isinstance(obj, dict):
            return False
        want = spec["expected"]
        if set(obj.keys()) != set(want.keys()):
            return False
        return all(
            isinstance(obj[k], list) and
            sorted(str(x).strip().lower() for x in obj[k]) ==
            sorted(n.lower() for n in want[k])
            for k in want
        )
    raise ValueError(f"Unknown grade kind {kind}")


# ---------------- execution ----------------

def run_cell(key: str, model: dict, task: dict, run_idx: int) -> dict:
    messages = [{"role": "user", "content": task["prompt"]}]
    body = {
        "model": model["id"],
        "messages": messages,
        "max_tokens": task["max_tokens"],
        "usage": {"include": True},
    }
    if model.get("provider_pin"):
        body["provider"] = {"order": [model["provider_pin"]], "allow_fallbacks": False}
    if task.get("tools"):
        body["tools"] = task["tools"]

    turns, tool_used, raw_responses = 0, False, []
    totals = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0,
              "cached_tokens": 0, "total_tokens": 0, "cost_usd": 0.0}
    t0 = time.time()
    final_text, finish_reason, provider = "", "", ""

    while True:
        data = post_chat(key, body)
        turns += 1
        raw_responses.append(data)
        provider = data.get("provider", provider)
        usage = data.get("usage", {}) or {}
        totals["prompt_tokens"] += usage.get("prompt_tokens", 0) or 0
        totals["completion_tokens"] += usage.get("completion_tokens", 0) or 0
        totals["total_tokens"] += usage.get("total_tokens", 0) or 0
        totals["cost_usd"] += usage.get("cost", 0) or 0
        totals["reasoning_tokens"] += (usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0) or 0
        totals["cached_tokens"] += (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0

        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message", {}) or {}
        finish_reason = choice.get("finish_reason", "") or finish_reason
        tool_calls = msg.get("tool_calls")

        if tool_calls and task.get("tool_result") and turns < 4:
            tool_used = True
            messages.append({"role": "assistant", "content": msg.get("content") or "",
                             "tool_calls": tool_calls})
            for tc in tool_calls:
                messages.append({"role": "tool", "tool_call_id": tc.get("id", "tool_1"),
                                 "content": task["tool_result"]})
            body["messages"] = messages
            continue

        final_text = msg.get("content") or ""
        break

    latency = time.time() - t0
    success = grade(task, final_text, tool_used)

    raw_name = f"{model['id'].replace('/', '_')}__{task['id']}__run{run_idx}.json"
    with open(os.path.join(RAW_DIR, raw_name), "w", encoding="utf-8") as f:
        json.dump({"model": model["id"], "task": task["id"], "run": run_idx,
                   "request_messages": messages, "responses": raw_responses}, f,
                  ensure_ascii=False, indent=1)

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model_label": model["label"], "model_id": model["id"],
        "task_id": task["id"], "task_type": task["type"], "lang": task["lang"],
        "run": run_idx, "provider": provider,
        **{k: totals[k] for k in ("prompt_tokens", "completion_tokens", "reasoning_tokens",
                                  "cached_tokens", "total_tokens")},
        "cost_usd": round(totals["cost_usd"], 8),
        "latency_s": round(latency, 1), "finish_reason": finish_reason,
        "turns": turns, "tool_used": tool_used, "success": success,
        "answer_excerpt": (final_text or "")[-160:].replace("\n", " "),
        "raw_file": f"results/raw/{raw_name}",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="", help="comma-separated substrings of model ids/labels")
    ap.add_argument("--tasks", default="", help="comma-separated substrings of task ids")
    ap.add_argument("--runs", type=int, default=0, help="override runs per cell")
    ap.add_argument("--plan", action="store_true", help="print the plan and exit (no API calls)")
    args = ap.parse_args()

    models = MODELS
    if args.models:
        wants = [w.strip().lower() for w in args.models.split(",")]
        models = [m for m in MODELS if any(w in m["id"].lower() or w in m["label"].lower() for w in wants)]
    tasks = TASKS
    if args.tasks:
        wants = [w.strip().lower() for w in args.tasks.split(",")]
        tasks = [t for t in TASKS if any(w in t["id"].lower() for w in wants)]

    plan = []
    for m in models:
        for t in tasks:
            runs = args.runs or RUNS_OVERRIDE.get(t["type"], DEFAULT_RUNS)
            for r in range(1, runs + 1):
                plan.append((m, t, r))

    print(f"Plan: {len(plan)} calls ({len(models)} models x {len(tasks)} tasks)")
    if args.plan:
        for m, t, r in plan:
            print(f"  {m['label']:<18} {t['id']:<22} run {r}")
        return

    os.makedirs(RAW_DIR, exist_ok=True)
    key = load_key()
    exists = os.path.exists(CSV_PATH)
    done = set()
    if exists:
        with open(CSV_PATH, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.add((row["model_id"], row["task_id"], row["run"]))

    spent = 0.0
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not exists:
            writer.writeheader()
        for i, (m, t, r) in enumerate(plan, 1):
            if (m["id"], t["id"], str(r)) in done:
                print(f"[{i}/{len(plan)}] skip (done): {m['label']} / {t['id']} / run {r}")
                continue
            print(f"[{i}/{len(plan)}] {m['label']} / {t['id']} / run {r} ...", flush=True)
            try:
                row = run_cell(key, m, t, r)
            except Exception as e:
                print(f"    FAILED: {e}")
                continue
            writer.writerow(row)
            f.flush()
            spent += row["cost_usd"]
            print(f"    ${row['cost_usd']:.4f} | {row['prompt_tokens']}p/{row['completion_tokens']}c "
                  f"({row['reasoning_tokens']} thinking) | success={row['success']} "
                  f"| session total ${spent:.2f}")

    print(f"\nDone. Session spend: ${spent:.2f}. Results: {CSV_PATH}")


if __name__ == "__main__":
    main()
