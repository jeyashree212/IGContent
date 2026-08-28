#!/usr/bin/env python3
"""
Competitor radar — scores posts against each creator's own baseline.

The scoring is the valuable half of the original Competitor-Radar skill, and it
does not care where the numbers came from. Today they are typed in by hand from
the Instagram app; when the Meta token exists, the same scorer runs on
business_discovery output with nothing here changing.

Why score against each creator's OWN median rather than a fixed threshold: an
account with 1,200 followers and an account with 40,000 are not comparable in
absolute likes, but "three times their normal" means the same thing for both.
That is what tells you a FORMAT worked, rather than that an account is big.

    python3 research/radar.py                      # report from the log
    python3 research/radar.py --min-posts 4        # require more data per creator
"""

import argparse
import csv
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parent / "competitor_log.csv"

# A comment costs more effort than a like, so it says more about whether a post
# actually landed. Saves and shares would be better still, but they are not
# visible on other people's posts from outside.
COMMENT_WEIGHT = 3
OUTLIER = 2.0          # multiple of a creator's own median to count as a hit
STRONG = 3.0


def load(path):
    if not path.exists():
        raise SystemExit(f"No log at {path}. Copy the header row and start filling it in.")
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for i, r in enumerate(csv.DictReader(f), 2):
            if not (r.get("creator") or "").strip():
                continue
            try:
                r["likes"] = int(r.get("likes") or 0)
                r["comments"] = int(r.get("comments") or 0)
            except ValueError:
                print(f"  row {i}: non-numeric likes/comments, skipped")
                continue
            r["engagement"] = r["likes"] + r["comments"] * COMMENT_WEIGHT
            rows.append(r)
    return rows


def analyse(rows, min_posts):
    by_creator = defaultdict(list)
    for r in rows:
        by_creator[r["creator"].strip().lstrip("@")].append(r)

    scored, thin = [], []
    for creator, posts in by_creator.items():
        if len(posts) < min_posts:
            thin.append((creator, len(posts)))
            continue
        median = statistics.median(p["engagement"] for p in posts) or 1
        for p in posts:
            p["median"] = median
            p["multiple"] = p["engagement"] / median
            scored.append(p)
    return scored, thin, by_creator


def report(scored, thin, by_creator, min_posts):
    out = []
    w = out.append
    w("# Competitor radar")
    w("")
    w(f"Generated {datetime.now(timezone.utc):%Y-%m-%d}. "
      f"{len(scored)} scored posts across {len({p['creator'] for p in scored})} creators.")
    w("")
    w("Each post is scored against **its own creator's median**, so a hit means "
      "the format outperformed that account's normal — not that the account is big.")
    w("")

    hits = sorted([p for p in scored if p["multiple"] >= OUTLIER],
                  key=lambda p: -p["multiple"])
    if hits:
        w(f"## Outliers ({OUTLIER}x their own median or better)")
        w("")
        w("| Multiple | Creator | Format | Topic | Hook |")
        w("|---|---|---|---|---|")
        for p in hits[:25]:
            mark = " **" if p["multiple"] >= STRONG else " "
            w(f"|{mark}{p['multiple']:.1f}x{mark.strip()} | @{p['creator']} | "
              f"{p.get('format','')} | {p.get('topic','')} | "
              f"{(p.get('hook','') or '')[:60]} |")
        w("")
    else:
        w("## Outliers")
        w("")
        w("None yet — log more posts per creator.")
        w("")

    # what the outliers have in common, which is the actual question
    for dim, label in (("format", "Format"), ("topic", "Topic")):
        tally = defaultdict(lambda: [0, 0])
        for p in scored:
            k = (p.get(dim) or "").strip().lower()
            if not k:
                continue
            tally[k][0] += 1
            if p["multiple"] >= OUTLIER:
                tally[k][1] += 1
        if not tally:
            continue
        w(f"## {label}: hit rate")
        w("")
        w(f"| {label} | Posts | Outliers | Hit rate |")
        w("|---|---|---|---|")
        for k, (n, h) in sorted(tally.items(), key=lambda kv: -(kv[1][1] / kv[1][0])):
            w(f"| {k} | {n} | {h} | {h/n:.0%} |")
        w("")

    w("## Baselines")
    w("")
    w("| Creator | Posts logged | Median engagement |")
    w("|---|---|---|")
    for creator, posts in sorted(by_creator.items()):
        med = statistics.median(p["engagement"] for p in posts) if posts else 0
        flag = "" if len(posts) >= min_posts else "  *(too few to score)*"
        w(f"| @{creator} | {len(posts)}{flag} | {med:.0f} |")
    w("")

    if thin:
        w(f"**Needs more data** (under {min_posts} posts): "
          + ", ".join(f"@{c} ({n})" for c, n in sorted(thin)))
        w("")

    w("---")
    w("")
    w("**Read this carefully, not literally.** Engagement is likes plus comments "
      f"weighted {COMMENT_WEIGHT}x. It is a proxy for reach, not reach itself — "
      "Instagram does not show view counts on other people's posts to anyone "
      "outside their account. A format with a high hit rate is worth trying; it "
      "is not proof.")
    w("")
    w("**Never copy a competitor's post.** Use this to find which *formats and "
      "topics* earn attention in this market, then make the version only she can "
      "make. Copying on-screen text or captions is the thing that got the "
      "viral-reels skill cut.")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Score competitor posts against their own baselines.")
    ap.add_argument("--log", default=str(LOG))
    ap.add_argument("--min-posts", type=int, default=3,
                    help="posts needed before a creator gets a median (default 3)")
    ap.add_argument("--out", default="research/radar-report.md")
    args = ap.parse_args()

    rows = load(Path(args.log))
    scored, thin, by_creator = analyse(rows, args.min_posts)
    text = report(scored, thin, by_creator, args.min_posts)
    Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
