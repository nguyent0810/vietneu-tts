# Verified fact: YouTube Analytics `day` dimension buckets by Pacific Time, not UTC

**Status: CONFIRMED, not a hypothesis.** Established via direct A/B API testing, not documentation lookup or assumption.

## Why this matters

Cycle 1 (`analytics_reviews/2026-07-25_to_2026-07-26/`) queried Analytics with UTC-labeled date strings (`startDate=2026-07-25&endDate=2026-07-26`) and got zero rows, which was attributed entirely to a ~3-day API processing lag. That framing was incomplete: part of the "missing data" was really a **day-boundary mismatch**, not lag. YouTube Analytics silently interprets `startDate`/`endDate` as Pacific Time calendar days. A video published at `2026-07-25T05:00:31Z` (UTC) falls at `2026-07-24T22:00:31` Pacific Time (UTC-7, PDT in July) — i.e. its entire first day of activity is bucketed under Analytics date `"2026-07-24"`, not `"2026-07-25"`.

## Evidence

Video `uHwa6nFBtkc`, confirmed `snippet.publishedAt = 2026-07-25T05:00:31Z` via `videos.list` (authoritative source):

| Query range (UTC-labeled) | Result |
|---|---|
| `2026-07-01` to `2026-07-10` | all-zero (correctly — video didn't exist) |
| `2026-07-23` to `2026-07-24` | **853 views, 91.9% average view percentage, 5 likes, 1 comment** — a full, real, processed day of data |
| `2026-07-25` to `2026-07-26` | all-zero (still within the processing backlog for that PT day) |

Per-day breakdown (`dimensions=day`) confirms all of this video's currently-visible activity sits in the single bucket `"2026-07-24"` — there is no `"2026-07-25"` row yet, consistent with PT-day `2026-07-25` still being unprocessed, not with the video's activity being genuinely absent.

## Consequence for this and future reviews

- The real constraint is **"the current PT calendar day and the day or two before it are typically unprocessed"** — not a fixed "wait 3 days" rule referenced to UTC dates.
- Because Phong Thủy publishes on a fixed UTC slot schedule (05:00/08:00/11:00/14:00), only the **05:00 UTC slot** shifts into the previous PT calendar day; the 08:00/11:00/14:00 UTC slots stay on the same PT calendar date as their UTC date. This is why, in this cycle's pull, only the four videos published at the earliest UTC slots each day (or published early enough in UTC to fall on an already-processed PT day) show real retention data, while same-day siblings published a few hours later do not.
- **Practical fix going forward:** when pulling Analytics data for "the last N days," query on a rolling window (e.g. the last 7-10 calendar days) with `dimensions=day` per video, rather than a fixed 1-2 day UTC-labeled window — then read off whichever days actually returned non-zero rows, rather than assuming a fixed lag offset from UTC "today."

## Self-caught error while establishing this

The first pass at reading the corrected data bundle computed `has_real_retention_data` as `row[0] != 0`, where `row[0]` is the **date string** (e.g. `"2026-07-24"`), not a metric — a string is never equal to the integer `0` in Python, so this was `True` for every row regardless of whether the day actually had data. This produced a false "REAL DATA" label for all 17 videos on first pass. Caught before use by manually inspecting the raw rows; fixed to check `row[1]` (views) instead. Recorded here because that's exactly the kind of self-check this whole review process depends on — flagged rather than silently corrected.

## What this actually unlocks for this cycle

Only **2 of 17 videos** have a sample size large enough to draw any conclusion from: `uHwa6nFBtkc` (Phong Thủy, 853 views, 91.9% avg view percentage) and `YStIdWWuXcU` (Phật giáo, 586 views, 35.13% avg view percentage). A handful of other videos show real but tiny (1-3 view) rows with `averageViewPercentage` above 100% — this is a genuine, expected phenomenon for YouTube Shorts (which loop/autoplay, so total watch time can exceed one full playthrough) and not a data error, but at n=1-3 views these numbers carry no statistical weight and should not be interpreted. The remaining videos still show all-zero rows — their PT calendar day has not been processed by Analytics yet.
