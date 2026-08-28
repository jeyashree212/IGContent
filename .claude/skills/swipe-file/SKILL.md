---
name: swipe-file
description: Turn Instagram screenshots into competitor performance data. Use when she has dropped screenshots of other creators' posts, profile grids, or reels into research/screenshots/, or asks what is working for other accounts.
---

# Swipe file

She scrolls Instagram and screenshots what is performing. I read the images and
turn them into rows in `research/competitor_log.csv`, then `research/radar.py`
scores them.

**Why screenshots rather than the API:** the app shows **view counts on reels**
in a profile grid. `business_discovery` does not return those for other people's
accounts. Screenshots capture more than the token would, not less.

## Reading a screenshot

Extract only what is actually visible. **Never estimate a number** — an empty
cell is fine, a guessed one poisons the analysis.

From a **profile grid**: handle, follower count, and per-tile view counts on
reels. The fastest way to spot outliers, because the grid shows a creator's
whole recent range at once.

From a **single post**: likes, comments, caption, the hook line, format, whether
a face is in frame, the CTA.

From a **reel**: views, likes, comments, the on-screen hook text, whether it
opens on a face or a place.

## Fill these columns

`creator, date, format, topic, hook_type, hook, has_face, likes, comments, url, notes`

- **format** — reel / carousel / photo
- **topic** — neighborhood, market update, listing, how-to, day in the life,
  personal story, client win
- **hook_type** — question, number, contrarian, problem, curiosity-gap,
  place-name, personal
- **has_face** — yes / no, on the first frame or first slide
- **notes** — put `views=N` here when a grid shows reel views, and `screenshot`
  so the row's provenance is clear

## Then

1. Append rows to `research/competitor_log.csv`.
2. Run `python3 research/radar.py`.
3. Report what the data says **and what it does not**. Under three posts for a
   creator there is no baseline, so there is no outlier — say that rather than
   ranking noise.

## Rules

- **Describe, never copy.** The point is to learn which formats and topics earn
  attention here, then build the version only she can build. Copying on-screen
  text or captions is what got the viral-reels skill cut, and her eXp agreement
  makes her personally liable for third-party IP.
- **Do not read demographics out of images.** Who appears in a competitor's
  photos is not data, and inferring an audience from it walks straight into the
  Fair Housing problem this project is careful about everywhere else.
- **A screenshot is a moment, not a trend.** A reel three days old and one three
  months old are not comparable. Log the date.
