# IGContent

Instagram content system for **@truehomes.realty** (Jeyashree Haridoss, True Homes Realty,
brokered by eXp Realty — Triangle, NC).

Adapted from 10 skills in the shared Drive folder "Claude Content Creation System".
Full audit and build plan: `content-system-plan.html`.

## Status

Planning complete. Nothing built yet.

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

    brand/     Source brand assets pulled from Drive
    config/    brand.json (tokens, disclosure, hard rules), competitors.json

## Guardrails

`config/brand.json` carries four non-negotiable rules — Fair Housing language,
brokerage attribution, no invented property facts, no client detail without
permission. Every skill reads them.
