---
name: carousel
description: Write and render a branded Instagram carousel for True Homes Realty, output at both Instagram (1080x1350) and TikTok (1080x1920) sizes. Use when planning a carousel, turning a topic or neighborhood into slides, or repurposing a post into swipeable content.
---

# True Homes carousel

One config file in, branded PNGs out at both aspect ratios. The look lives in
`render/carousel.py` and `config/brand.json` — never restyle per carousel.

    python3 render/carousel.py workspace/<slug> --validate
    python3 render/carousel.py workspace/<slug>
    python3 render/carousel.py workspace/<slug> --slide 3     # re-render one

## Pipeline

1. **Pick the pillar.** Every carousel is `reach` or `convert`.
   - **reach** — walkable and bikeable Triangle life, neighborhoods, greenways,
     parks. Aimed at strangers. This is the differentiator; lead with it.
   - **convert** — sellers and buyers ready to move. Aimed at the ICP.
2. **Draft the slide plan as text and stop.** Show the user a numbered plan
   before writing any config. Iterate on words, not pixels.
3. **Write `workspace/<slug>/config.json`.** Schema below.
4. **List every factual claim in `verify`.** See Facts.
5. **Validate, render, show the slides.**

## Config

```json
{
  "title": "internal reference only",
  "pillar": "reach",
  "verify": ["each factual claim, one per line"],
  "slides": [
    { "type": "hook", "eyebrow": "Neighborhood notes",
      "text": "Headline with *accent words*.",
      "subtitle": "One supporting line.",
      "image": "brand:raleigh-skyline.png" },
    { "type": "body", "eyebrow": "Section label", "title": "Short title",
      "text": "One idea.", "bullets": ["max four", "each one line"],
      "image": "listing-front.jpg" },
    { "type": "cta", "text": "The ask.", "button_text": "Follow for more" }
  ]
}
```

- 5–10 slides. First is `hook`, last is `cta`. Enforced by `--validate`.
- `*asterisks*` colour a phrase brick. One or two per slide, never more.
- `image`: a filename in `workspace/<slug>/images/`, or `brand:<file>` for a
  shared asset in `brand/`. A missing image degrades to the blush ground.
- Drop her photos into `images/`. **iPhone HEIC will not open** — export as JPEG
  first, or convert on the way in.

## Voice

- Short, complete sentences. One idea per sentence. Written as she'd say it.
- Specific over vague. "Fifteen minutes on foot", not "close to everything".
- **No emoji** unless a single one is genuinely elegant in context. Never as
  bullets, never as decoration, never more than one on a slide.
- No hype words: unlock, elevate, seamless, game-changer, dive in.
- Sentence case in body copy. The renderer handles all display styling.

## Hard rules

These come from `config/brand.json` and are not negotiable per-carousel.

- **Fair Housing.** Never state or imply who a home or neighborhood is *for*.
  No "perfect for families", no "safe", no school-quality claims, no language
  about who lives somewhere. Amenities, distances, and infrastructure only.
  The walkable angle sits close to this line — keep it on greenways, transit,
  distances, and parks.
- **Attribution.** The CTA slide carries `True Homes Realty · Brokered by eXp
  Realty`. The renderer draws it automatically. Never remove it.
- **No invented property facts.** Price, square footage, status, days on
  market — only from what she supplied. Never web-searched into a slide.
- **No client detail** — names, messages, transaction specifics — without her
  written confirmation of permission.
- **No AI likeness.** Never generate, suggest, or script a synthetic version of
  her face or voice. Her likeness is her own.

## Facts

Every factual claim goes in `verify`, phrased so she can check it in one
search. Mileages, neighborhood names, amenity claims, anything numeric. The
renderer prints the list after each run. **She verifies before posting** —
carousels state things about her market under her license.

## Cross-posting

`--format both` (the default) writes `ig/` at 1080x1350 and `tiktok/` at
1080x1920. Post from the rendered files. Never save a Reel down and repost it
— TikTok suppresses reach on clips carrying a visible Instagram watermark.
