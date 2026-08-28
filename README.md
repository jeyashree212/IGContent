# IGContent

Instagram content system for **@truehomes.realty** (Jeyashree Haridoss, True Homes Realty,
brokered by eXp Realty — Triangle, NC).

Adapted from 10 skills in the shared Drive folder "Claude Content Creation System".
Full audit and build plan: `content-system-plan.html`.

## Status

Carousel renderer built and rendering. Strategy docs, radar, tracker, and
story sequences still to come.

| | |
|---|---|
| Posture | Draft only — nothing auto-publishes |
| Budget | $0/month |
| Credentials | One free Meta Graph API token (not yet created) |

## Verdict on the source skills

**Build (4):** instagramcarousel, Story-Sequences, CONTENT-STRATEGY-SKILL,
SCRIPTED-REELS-PIPELINE (deferred until recording starts).

**Rewrite (2):** Competitor-Radar and instagram-post-tracker — sound methods, but both
run on paid APIs. Swap in the free Graph API.

**Cut (4):** InstagramResearch (duplicates Competitor-Radar, paid scrapers),
Instagram scheduling (paid, and uploads video to an anonymous public host),
AI-Reels-Pipeline (~$24/mo + per-clip video generation),
VIRAL-REELS-PIPELINE (rips and republishes other creators' audio — the eXp ICA makes
the agent personally liable for third-party IP infringement).

## Layout

    .claude/skills/carousel/   The carousel skill
    brand/                     Brand assets + extracted headshot and skyline
    config/brand.json          Tokens, disclosure, voice, hard rules
    config/competitors.json    Radar cohort
    render/carousel.py         Renderer — IG 1080x1350 + TikTok 1080x1920
    workspace/<slug>/          One carousel: config.json, images/, ig/, tiktok/

## Positioning

Walkable and bikeable Triangle expertise is the **reach** engine — it is the
differentiator none of the eight tracked competitors claim. Luxury is the
**convert** engine.

## Rendering a carousel

    python3 render/carousel.py workspace/walkable-triangle --validate
    python3 render/carousel.py workspace/walkable-triangle

Every factual claim in a config's `verify` list prints after each run and must
be checked before posting.

## Guardrails

`config/brand.json` carries five non-negotiable rules — Fair Housing language,
brokerage attribution, no invented property facts, no client detail without
permission, and no AI likeness (no synthetic face or voice, ever). Every skill
reads them.
