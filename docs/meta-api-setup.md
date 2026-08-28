# Getting the Meta token

One credential, free, no card, **no App Review**. About 20 minutes.

It unlocks two things: her own post insights (for the tracker) and public data on
competitor business accounts (for the radar). Until it exists, neither can be
built — Instagram blocks everything else.

> Written August 2026. Meta renames things in this console often. If a button
> name below doesn't match what you see, the *sequence* still holds — look for
> the nearest equivalent.

---

## Blocked as of August 2026

Her personal Facebook account has been disabled since 2022, and a Meta developer
app requires a working Facebook login. **Everything below is on hold until that
is resolved.** See `docs/facebook-appeal.md` for the appeal routes, and
`research/radar.py` for the manual path that runs in the meantime.

Two things worth checking while the appeal runs, because either could unblock
this sooner:

1. **Which Facebook account admins the True Homes Realty Page?** If it is a
   different profile from the disabled one, that account can create the
   developer app today and none of this waits.
2. **Is the Page reachable at all** through Meta Business Suite? If the disabled
   profile was its only admin, the Page may need recovering too — a separate
   and slower problem worth discovering now rather than later.

**Do not create a new Facebook account to get around the ban.** Meta links
accounts by device, IP and identity; a replacement profile is likely to be
disabled too, and it puts the Page and the Instagram account at risk. Appeal
the real one, or use a different account that legitimately already exists.

## Before you start

Three things must already be true. All three are, for @truehomes.realty:

1. Instagram account is **Business or Creator** — not personal.
2. It is **linked to a Facebook Page**.
3. She is an **admin of that Page**, with the Facebook login to hand.

One more thing to check: some Instagram insight endpoints return nothing for
accounts under **100 followers**. If @truehomes.realty is below that, the
competitor radar still works but her own insights may come back empty until she
crosses it.

---

## Why no App Review

This is the part that saves days.

A Meta app in **Development mode** can call the API at full strength, but only
for accounts connected to people with a role on the app (admin, developer,
tester). Since she is the admin and the only account being read is her own, that
is all she needs. **App Review is only required to access accounts belonging to
people who are not on your app** — which we never do.

So: leave the app in Development mode. Do not submit for review. Do not switch
it Live.

---

## Steps

### 1. Create the app

Go to **developers.facebook.com** → log in with the Facebook account that
administers the Page → **My Apps** → **Create App**.

- Use case: **Other** → app type **Business**
- Name it something plain: `True Homes Content`
- Attach the Business Portfolio if it offers one

### 2. Add the Instagram product

On the app dashboard, find **Instagram** in the product list → **Set up**.
Choose the option for **Instagram API with Facebook Login** (sometimes shown as
Instagram Graph API), *not* Instagram Basic Display — that one was retired in
December 2024 and no longer works.

### 3. Note the App ID and App Secret

**App settings → Basic.** The App ID is fine to keep in a config file. **The App
Secret is a password** — treat it like one. It is only needed once, in step 6.

### 4. Generate a user token

Open the **Graph API Explorer** (Tools → Graph API Explorer).

- **Meta App**: the app just created
- **User or Page**: *User Token*
- Add these permissions:

      instagram_basic
      instagram_manage_insights
      pages_show_list
      pages_read_engagement

- **Generate Access Token** → log in → grant.

This token is **short-lived — about an hour.** That is expected; step 6 fixes it.

### 5. Find the Instagram account ID

Still in the Explorer, run:

    me/accounts?fields=name,id,instagram_business_account

The response lists her Pages. Find True Homes Realty and copy the
`instagram_business_account.id` — a long number. **That ID, not the handle, is
what every later call uses.**

Sanity check it works:

    <IG_ID>?fields=username,followers_count,media_count

It should come back with `truehomes.realty`.

### 6. Trade up to a 60-day token

The short-lived token dies in an hour. Exchange it in a browser tab:

    https://graph.facebook.com/v21.0/oauth/access_token
      ?grant_type=fb_exchange_token
      &client_id=<APP_ID>
      &client_secret=<APP_SECRET>
      &fb_exchange_token=<SHORT_LIVED_TOKEN>

The response contains a **long-lived token, good for 60 days.**

Check the expiry at **Tools → Access Token Debugger** — paste the token, confirm
it says roughly 60 days and lists the four permissions.

### 7. Store it

Put it in `config/credentials.json`, which is already in `.gitignore`:

```json
{
  "ig_user_id": "17841400000000000",
  "access_token": "EAAG...",
  "app_id": "1234567890",
  "token_obtained": "2026-08-28",
  "token_expires": "2026-10-27"
}
```

**Never commit this file. Never paste the token into a chat, an email, or a
screenshot.** Anyone holding it can read her account's data. If it leaks, go to
App settings → Basic → **Reset App Secret**, which invalidates every token.

### 8. Diary the renewal

60 days is not long and there is no warning. Put a calendar reminder at **day
50** to repeat steps 4 and 6. Two minutes when you remember; a broken radar and
a confusing morning when you don't.

---

## What the token can and cannot do

**Her own account — good coverage.** Impressions, reach, profile views, follower
count, and per-post likes, comments, saves, shares and — on her own reels —
plays. This is what the tracker snapshots daily.

**Competitors — public data, and less of it.** `business_discovery` returns, for
a *public Business or Creator* account: `followers_count`, `media_count`,
`biography`, `username`, and for recent posts `caption`, `like_count`,
`comments_count`, `media_url`, `permalink`, `timestamp`.

**The gap, stated plainly:** it does **not** return view or play counts on other
people's reels. So the radar scores competitor posts on engagement (likes +
comments against that creator's own median), not on views. Same method as the
original skill, noisier signal. That is the honest price of not paying for a
scraper, and it is still a fair trade at zero dollars.

Two more limits: a competitor whose account is **personal rather than
Business/Creator** returns nothing at all, and Meta caps how much
business-discovery data can be pulled per account per week — fine for eight
competitors checked daily, not fine for scraping hundreds.

## Call shape

    GET https://graph.facebook.com/v21.0/<IG_USER_ID>
        ?fields=business_discovery.username(gretchencoleygroup){
                  followers_count,media_count,
                  media{caption,like_count,comments_count,timestamp,permalink}}
        &access_token=<TOKEN>

## If it breaks

| Symptom | Cause |
|---|---|
| `(#10) requires instagram_basic` | A permission was missed in step 4. Regenerate. |
| `Error validating access token: expired` | Past day 60. Repeat steps 4 and 6. |
| `business_discovery` returns nothing for one competitor | That account is personal, or private. Not fixable from our side — note the gap. |
| Own insights are empty | Under 100 followers, or the account was switched to Business too recently. |
| `Unsupported get request` on the IG ID | Using the Page ID instead of the `instagram_business_account.id`. |

## Sources

Meta's own developer docs are unreachable from this environment, so the details
above come from secondary sources and should be treated as `[G]` — the sequence
is right, exact button names may have drifted.

- [Overview of the Instagram API — Meta](https://developers.facebook.com/docs/instagram-platform/overview/)
- [Instagram API integration guide 2026 — Phyllo](https://www.getphyllo.com/post/instagram-api-integration-101-for-developers-of-the-creator-economy)
- [Instagram Graph API developer guide 2026 — Elfsight](https://elfsight.com/blog/instagram-graph-api-complete-developer-guide-for-2026/)
- [Instagram Basic Display API deprecation](https://www.keyapi.ai/blog/instagram-basic-display-api/)
- [Business discovery endpoint walkthrough](https://medium.com/@ritikkhndelwal/get-other-instagram-users-data-using-the-python-and-instagram-graph-api-business-discovery-807ba4a9ad91)
