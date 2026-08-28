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
    { "type": "photo", "eyebrow": "Label", "text": "Type over the photo.",
      "caption": "Optional supporting line.", "image": "cary-downtown.heic",
      "frame": { "zoom": 1.0, "x": 0.36 } },
    { "type": "index", "eyebrow": "Label", "title": "Named places",
      "entries": [ { "name": "Parkside Town Commons",
                     "detail": "What it is, in one line" } ] },
    { "type": "split", "eyebrow": "Label", "title": "Headline",
      "text": "Body copy in the brick panel.", "image": "street.jpg" },
    { "type": "stat", "eyebrow": "Label", "stat": "55",
      "title": "Short title", "text": "What the number means." },
    { "type": "cta", "text": "The ask.", "button_text": "Follow for more" }
  ]
}
```

- 5–10 slides. First is `hook` or `photo`, last is `cta`. Enforced by `--validate`.
- **`photo`** is the flair slide: full-bleed image, scrim, white type over it.
  Use it for real city photos. Falls back to `body` if the image is missing.
- **`stat`** sets one number huge in brick with the corner wedge. Use it for a
  road number, a year, a distance — something concrete and checkable.
- **`index`** is a directory: up to five named places, each with a one-line
  detail, hairline-separated. **Reach for this instead of `bullets` whenever
  the slide is a list of real places** — it is denser, more editorial, and it
  forces specificity.
- **`split`** puts a photo across the top with the copy in a brick panel
  overlapping its lower edge. Good for one strong statement over one image.
- **Vary the types.** Three `body` slides in a row is the single fastest way to
  make a carousel look machine-made. Aim for no two adjacent slides sharing a
  layout, and put a `photo`, `stat` or `index` between every pair of `body`
  slides.
- **`frame`** on a photo slide controls composition: `zoom` tightens, `x`/`y`
  pan (0 = left/top, 1 = right/bottom). Use it to compose something **out of
  frame** rather than blurring it — a blur reads as censorship, a crop reads as
  a choice. Blur only genuine privacy items: house numbers, faces of people who
  did not consent.
- `*asterisks*` colour a phrase brick. One or two per slide, never more.
- `image`: a filename in `workspace/<slug>/images/`, or `brand:<file>` for a
  shared asset in `brand/`. A missing image degrades to the blush ground.
- **Drop iPhone photos in as-is.** `.HEIC` opens natively via `pillow-heif`, and
  EXIF rotation is baked in so portrait shots are never sideways.

## Where she actually works

Core: **Cary, Morrisville, Raleigh, Holly Springs, Fuquay-Varina, Garner.**

- **Downtown Raleigh** is her specialty — she lives there.
- **Cary and Morrisville** — she grew up in both and can speak first-hand to
  how they changed.
- **The Highway 55 corridor** — her parents moved from West Cary out to
  Fuquay-Varina/Holly Springs, the same move many families she grew up with
  made. This is the strongest reach angle she has.

**Never write Durham, Carrboro, or Chapel Hill content.** Not her market, not
her expertise. Naming her as a guide there is worse than saying nothing.

Get granular. "West Cary" beats "Cary". A named road, intersection, or park
beats a town. If you do not know the specific, **ask her** — do not fill the
gap with something plausible.

## Local knowledge

**Read `knowledge/triangle-development.md` before writing any content that
touches a place.** It carries named projects, dates, dollar figures and job
numbers for all six of her markets, so a slide can cite Complete 540 or the
Morrisville Town Center instead of saying "the area is growing."

Every claim in it is tagged `[V]` (verified, source listed) or `[G]` (general
background, verify first). Anything `[G]`, and anything dated within the last
year, goes in the carousel's `verify` list.

Two rules when using it:

- **A project is never a promise.** "A BRT station is planned two blocks away"
  is a fact. "This will raise your home value" is a prediction she should not
  make in a caption.
- **Date the claim** — "as of August 2026" — so it ages honestly instead of
  quietly becoming wrong.

## Never talk down an area

Every place she serves gets its pros highlighted on their own terms. **Cary is
high quality, high cost and highly coveted — especially West Cary — and she
wants Cary clients.** No town is ever the consolation prize for another, and no
migration story is an escape: people move for a different stage or a different
fit, and two places can both be excellent for different reasons.

Banned framings: "priced out", "can't afford X so settle for Y", "X is
overrated", "the smart money left X", "better value than X" used as a knock.

This is a business rule first — she wants clients in all six markets — and a
Fair Housing one second: running down whole areas by comparison edges toward
steering.

## Hashtags

5–7, never more. At least three hyperlocal to the exact place in the post.
Pull from the pool in `config/brand.json`. Skip #realestate, #realtor,
#dreamhome and anything else sitting on 50M+ posts — they return bot follows,
not buyers. The pool is reasoned, not measured; the post tracker settles it
once it has a few weeks of data.

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
