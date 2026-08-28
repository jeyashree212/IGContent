# Getting the Facebook account back

The Meta token — and therefore the competitor radar and the post tracker — is
blocked behind a Facebook account disabled since 2022. This is the path back.

*Researched August 2026. Sources at the end.*

## The honest expectation

A four-year-old disablement is a hard case. Appeals are reviewed largely by
automated systems, and the window Meta normally offers for appealing is long
past. It may work; it may not. **Plan the content system as though it might
not**, which is why `research/radar.py` reads a hand-kept log rather than the
API.

## Step 1 — check whether it even matters

Before spending effort, answer one question: **which Facebook account admins the
True Homes Realty Page?**

If it is any account other than the disabled one, that account can create the
developer app and everything is unblocked today. Check in Meta Business Suite,
or ask whoever set the Page up.

## Step 2 — the official appeal

The real form:

    facebook.com/help/contact/260749603972907

It asks for the email or phone on the disabled account, the full real name as it
appeared, and a government ID. Nothing else.

**Any site offering a different "official recovery form", or asking for the
account password to submit on her behalf, is phishing.** The genuine form never
needs a password.

## Step 3 — the realistic route to a human

**Meta Verified**, about **$14.99/month**, includes direct chat support inside
the Facebook and Instagram apps and priority review on appeals. As of mid-2026
this is the most reliable way to reach a person rather than an automated
rejection.

Two caveats worth knowing before paying:

- There is **no public phone line** and no paid shortcut that skips the identity
  check. Meta Verified gets the case in front of a human faster; it does not
  guarantee the outcome.
- It can be subscribed **through the Instagram account**, which still works. She
  does not need the disabled Facebook profile to buy it.

If she already runs an active Meta ad account anywhere, **Meta Business Support
chat** is another route to a person.

## Step 4 — while it runs

Nothing in the content system waits on this except the radar's data source and
the tracker's automation.

- **Competitor research**: `research/competitor_log.csv` plus
  `research/radar.py`. She logs eight competitors from her phone; the scorer
  does the same median-based outlier maths the API version would.
- **Her own numbers**: Instagram's in-app Professional Dashboard shows reach,
  impressions, saves and shares. Same numbers, read by hand.
- **Everything else** — carousels, stories, strategy, the knowledge base — never
  needed the token at all.

## Sources

- [Facebook disabled account appeal guide 2026](https://youreputationsolution.com/blog/facebook-disabled-account-recovery/)
- [Recovering a disabled Facebook account in 2026](https://www.technerdiness.com/facebook/recover-disabled-facebook-account/)
- [Facebook account disabled — appeal and restore](https://www.dialhelpusa.com/guides/facebook-account-disabled-appeal/)
