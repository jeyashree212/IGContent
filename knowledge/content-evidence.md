# What we actually know about what works

**Status: we don't, yet.** This file exists to keep that honest, and to stop
content skills from presenting taste as evidence.

Read it before writing content. Anything in the "assumed" column is a **guess
that has never been tested against a real post's numbers** and should be labelled
as such when it drives a decision.

---

## The uncomfortable finding

Published Instagram benchmarks disagree with each other by more than an order of
magnitude. Researched August 2026:

| Source | Claim |
|---|---|
| Socialinsider 2026 | Carousels top the engagement leaderboard, and have since 2023 |
| TrueFuture Media, Jan 2026 | Carousels **10.15%**, Reels ~**6%** |
| Another 2026 analysis | Reels **1.23%**, the best-performing format |
| Real-estate specific | Reels **3.7%**, "2.7x more engaging than carousels" |
| Dash Social | Real estate on Instagram: **0.30%** |

These cannot all be true. They use different denominators — some divide by
followers, some by reach, some by impressions — and they sample different
account sizes. **A number without its denominator is not data.**

Two things follow:

1. **Generic benchmarks cannot settle a strategy question.** Anyone citing "10%
   engagement for carousels" to justify a content plan is quoting a number whose
   basis they have not checked.
2. **Real estate is hyper-local.** National figures are averaged across markets
   that share nothing. Her audience is southwest Wake County. The only reliable
   evidence about that audience is that audience.

So: her own account first, competitors in her actual market second, published
benchmarks a distant third and only as hypotheses.

---

## What is assumed right now

Everything below drives content already produced. **None of it has been tested.**

| Assumption | Where it came from | Status |
|---|---|---|
| A personal story out-performs a market update | My judgement | **Untested** |
| Named specifics ("Parkside at 55 and 540") beat general claims | Widely believed, plausible | **Untested** |
| Varied slide layouts hold a swipe better than uniform ones | Design reasoning | **Untested** |
| A full-bleed photo is a stronger opener than type on blush | Design reasoning | **Untested** |
| 7–8 slides is the right carousel length | Convention | **Untested** |
| No emoji suits her brand | Her stated preference | Preference, not performance |
| 5–7 hyperlocal hashtags beat mega-tags | Reasoning about tag size | **Untested** |
| Reach content should lead with neighborhoods, convert with luxury | Positioning logic | **Untested** |
| Saves and shares predict enquiries better than likes | Standard, and mechanically sensible | **Untested here** |

That is nine assumptions underneath one carousel. The Highway 55 post is a
reasonable first hypothesis. It is not a proven format, and it should not be
copied eight more times before anything is measured.

---

## Closing the gap

Three sources, in order of how much they are worth.

### 1. Her own posting history — currently zero

**@truehomes.realty has no posts.** So there is nothing to learn from yet, and
`research/own_posts.csv` and `research/learn.py` are scaffolding waiting for a
first month of posting rather than a source we can use now.

Two consequences worth being clear about:

- **Competitors are the only evidence available.** Not the best source, the
  only one.
- **The blocked Meta token costs almost nothing right now.** It would return her
  own insights, and there are none; and accounts under 100 followers get empty
  insights anyway. Resolve the Facebook account when convenient, not urgently.

Start logging from her first post. Twelve is the floor before any pattern is
worth acting on; thirty is where it gets genuinely useful. Log the weak posts
too — a file of only winners cannot show what separates them.

### 2. Competitors in her market — the only source today

`research/competitor_log.csv` and `research/radar.py`, fed by screenshots via
the `swipe-file` skill. Scores each post against its own creator's median, so it
detects formats rather than account size.

**Screenshots beat the API here.** The Instagram app shows view counts on reel
tiles in a profile grid; `business_discovery` does not return those for other
accounts at all. Her scrolling captures more than the token would.

The limits are still real: a screenshot is one moment rather than a trend, and
this is other people's audiences rather than hers. It tells us which formats and
topics earn attention in this market. It cannot tell us what converts for her.

### 3. Published benchmarks

Hypotheses to test, never conclusions. See the table above for why.

---

## The rule this file exists to enforce

**Do not present a content decision as evidence-based until it appears in
`research/what-works.md`.**

When a skill makes a call that rests on something in the assumed table, say so
in the carousel's `verify` list. "I chose a photo opener because I think it
holds attention better" is honest. "Photo openers perform better" is not, until
the log says so.

## Sources

- [What the latest data reveals about social media engagement — Inman](https://www.inman.com/2026/07/06/latest-data-reveals-social-media-engagement/)
- [Instagram for real estate agents 2026 — TrueFuture Media](https://www.truefuturemedia.com/articles/instagram-for-real-estate-agents-2026)
- [Instagram engagement rate benchmarks by industry and format — Apaya](https://apaya.com/blog/social-media-benchmarks-instagram)
- [Instagram engagement rate statistics and benchmarks — Colorlib](https://colorlib.com/wp/instagram-engagement-rate/)
- [What each Instagram format is actually for now — The Simple Touches](https://www.thesimpletouches.com/post/what-each-instagram-format-is-actually-for-now-late-2026-guide-for-real-estate-agents)
