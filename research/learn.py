#!/usr/bin/env python3
"""
Learn what actually works on @truehomes.realty.

Reads own_posts.csv — her own posting history, with the metrics only she can
see (reach, saves, shares, follows) — and reports which features correlate with
performance. This is the evidence the content skills are supposed to be built
on, and until it has data they are running on assumption.

    python3 research/learn.py
    python3 research/learn.py --metric saves_per_reach

Deliberately simple statistics. With the sample sizes a single agent's account
produces, anything fancier would be false precision.
"""

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

LOG = Path(__file__).resolve().parent / "own_posts.csv"

# Features to test against performance. Each is a column in the CSV.
FEATURES = ["format", "pillar", "topic", "hook_type", "has_face",
            "cta_type", "posted_slot"]

# Reach-normalised, because a post that reached 4,000 people and a post that
# reached 400 cannot be compared on raw saves.
METRICS = {
    "saves_per_reach":  ("saves", "reach", "Saves per 1k reached"),
    "shares_per_reach": ("shares", "reach", "Shares per 1k reached"),
    "eng_per_reach":    (None, "reach", "Engagement per 1k reached"),
    "reach":            (None, None, "Raw reach"),
    "follows":          (None, None, "Follows from post"),
}

# Sample-size gates. Below these, report the number but refuse to call it a
# finding — the single most common way content "data" misleads.
MIN_POSTS_TOTAL = 12
MIN_PER_GROUP = 3


def load(path):
    if not path.exists():
        raise SystemExit(
            f"No log at {path}.\n"
            "Fill it from Instagram: Professional Dashboard -> Content you shared.\n"
            "Every row you add makes the content skills less of a guess.")
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for i, r in enumerate(csv.DictReader(f), 2):
            if not (r.get("date") or "").strip() or (r.get("notes") or "").startswith("example"):
                continue
            try:
                for k in ("reach", "likes", "comments", "saves", "shares", "follows"):
                    r[k] = int(r.get(k) or 0)
            except ValueError:
                print(f"  row {i}: non-numeric metric, skipped")
                continue
            r["engagement"] = r["likes"] + r["comments"] + r["saves"] + r["shares"]
            rows.append(r)
    return rows


def value(row, metric):
    num, denom, _ = METRICS[metric]
    n = row["engagement"] if num is None and denom else row.get(num or metric, 0)
    if metric == "reach":
        return row["reach"]
    if metric == "follows":
        return row["follows"]
    if not row.get(denom):
        return None
    return n / row[denom] * 1000


def main():
    ap = argparse.ArgumentParser(description="Find what correlates with performance.")
    ap.add_argument("--log", default=str(LOG))
    ap.add_argument("--metric", default="saves_per_reach", choices=list(METRICS))
    ap.add_argument("--out", default="research/what-works.md")
    args = ap.parse_args()

    rows = load(Path(args.log))
    label = METRICS[args.metric][2]
    out, w = [], None
    out = []
    w = out.append

    w("# What works on @truehomes.realty")
    w("")
    w(f"{len(rows)} posts logged. Ranking by **{label}**.")
    w("")

    if len(rows) < MIN_POSTS_TOTAL:
        w(f"> **Not enough data to conclude anything.** {len(rows)} posts logged, "
          f"{MIN_POSTS_TOTAL} is the minimum before any pattern here is worth "
          f"acting on. Numbers below are shown so you can watch them build, not "
          f"so you can decide from them.")
        w("")

    vals = [(r, value(r, args.metric)) for r in rows]
    vals = [(r, v) for r, v in vals if v is not None]
    if not vals:
        w("No usable rows — check that `reach` is filled in.")
        Path(args.out).write_text("\n".join(out)); print("\n".join(out)); return

    overall = statistics.median(v for _, v in vals)
    w(f"Median across all posts: **{overall:.1f}**")
    w("")

    w("## Top posts")
    w("")
    w(f"| {label} | Format | Topic | Hook type | Hook |")
    w("|---|---|---|---|---|")
    for r, v in sorted(vals, key=lambda t: -t[1])[:10]:
        w(f"| {v:.1f} | {r.get('format','')} | {r.get('topic','')} | "
          f"{r.get('hook_type','')} | {(r.get('hook','') or '')[:52]} |")
    w("")

    w("## Feature comparison")
    w("")
    w("Each group's median against the overall median. A group with fewer than "
      f"{MIN_PER_GROUP} posts is listed but not scored.")
    w("")
    for feat in FEATURES:
        groups = defaultdict(list)
        for r, v in vals:
            k = (r.get(feat) or "").strip().lower()
            if k:
                groups[k].append(v)
        if not groups:
            continue
        w(f"### {feat.replace('_', ' ')}")
        w("")
        w("| Value | Posts | Median | vs overall |")
        w("|---|---|---|---|")
        for k, vs in sorted(groups.items(), key=lambda kv: -statistics.median(kv[1])):
            med = statistics.median(vs)
            if len(vs) < MIN_PER_GROUP:
                w(f"| {k} | {len(vs)} | {med:.1f} | *too few* |")
            else:
                delta = (med / overall - 1) * 100 if overall else 0
                w(f"| {k} | {len(vs)} | {med:.1f} | {delta:+.0f}% |")
        w("")

    w("---")
    w("")
    w("## How to read this")
    w("")
    w("- **Correlation, small sample, her account only.** A format ahead by 40% "
      "across five posts is a hint worth testing, not a rule worth adopting.")
    w("- **Saves and shares beat likes.** A save means someone intends to come "
      "back; a share means they put their own name behind it. Likes are the "
      "cheapest signal and the least predictive of a call.")
    w("- **Reach-normalise everything.** Raw counts mostly measure how many "
      "people saw it, which mostly measures the algorithm's mood that day.")
    w("- **Published benchmarks are not a substitute for this file.** They "
      "disagree with each other by an order of magnitude because they use "
      "different denominators, and real estate is hyper-local. See "
      "`knowledge/content-evidence.md`.")
    Path(args.out).write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
