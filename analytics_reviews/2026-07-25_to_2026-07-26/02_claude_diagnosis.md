# Claude Diagnosis & Improvement Plan — 2026-07-25 to 2026-07-26

**Input:** `01_cursor_analytics_report.md` (Cursor CLI, real data from `00_raw_data_bundle.json`)
**Status:** DRAFT — pending Codex CLI critique (round 1) and user approval. **No production prompt or workflow has been modified.** Every recommendation below is a proposal only.
**Scope:** Phong Thủy (my pipeline, actionable) is the primary subject. Phật giáo is referenced only for cross-channel context — I do not have pipeline-internal visibility into how its videos were produced, so I make no prompt/workflow recommendations for it.

---

## 0. Brand Manifesto constraints (read before any recommendation below)

Checked against `content_repo_clone/CORE_OS/BRAND_BIBLE.md` and `DOMAINS/FENG_SHUI/DOMAIN_GUIDE.md`:

- Core rule: **"accurate, humane, evidence-aware, non-manipulative, clear about uncertainty."**
- Feng Shui-specific: **"calm, reverent, non-manipulative voice,"** must **"treat viewer anxiety about luck/fortune with compassion rather than exploiting it,"** and must **"never structure a video, title, or Short around a manufactured deadline or threat."**
- Governing principle for any risk/hook tension: **"Transform first, refuse only when transformation is impossible"** — preserve the hook's energy, never lose it to a blanket refusal, but never cross into manipulation to get it.

**Every recommendation in §3 has been checked against this. None proposes urgency-manufacturing, fear-based hooks, or absolutist claims — this is also already the standard `content_categories.py`'s rubrics enforce, so the two are already aligned by construction, not by coincidence.**

---

## 1. Root-cause analysis

### 1.1 Extreme within-category variance is the dominant signal, not category choice

Cursor's data: `western_zodiac_short_generator.py` produced both the weakest video in the set (Song Tử, 8 lifetime views) and a mid-strong one (Bạch Dương, 799 views) — a ~100x spread from the *same generator, same category, same day*. `iching_short_generator.py` shows the same pattern at smaller scale (Càn Vi Thiên 967 vs Tốn Vi Phong 307).

**Hypothesis [confidence: LOW — sample size]:** execution-level factors (specific sign/hexagram chosen that rotation cycle, title phrasing, thumbnail-adjacent title specificity) matter more than category-level choice. Category alone is a weak predictor here.
**Why low confidence:** 8 videos total, 1-2 days old, view counts still accumulating. A 100x gap on n=2 per category is exactly the kind of noise early view-count data produces regardless of true quality — I cannot rule out "Song Tử just hasn't been shown to enough people yet" vs. "Song Tử's hook genuinely underperforms."
**What would raise confidence:** retention data (not yet available) would immediately distinguish a discovery problem (low impressions/CTR) from a retention problem (people click, leave fast) from "just needs more time." This is the single highest-value data gap right now.

### 1.2 `hook_score_at_generation` is not persisted — a real, fixable pipeline gap

Every Phong Thủy generator already runs a fact-checked, category-aware judge panel (`short_judge_panel_engine.py`) that produces a real `hook_score` (1-10) at generation time. That score is **not currently written into the final registry entry** for videos that skip the Phật-giáo-specific hook-review step (see `short_batch_runner.py`'s `hook_score: null` for all 8 Phong Thủy entries).

**This is a fact, not a hypothesis:** I verified this directly by reading the registry — every one of the 8 entries shows `"hook_score": null`.

**Consequence:** there is currently no way to ever correlate the AI judge's own hook-quality assessment with real-world performance, for any video, ever — which defeats a large part of the point of having a scored judge panel at all. This is the clearest, lowest-risk, highest-leverage fix available (§3, P0-1).

### 1.3 Retention data unavailability is a timing artifact, not a pipeline defect

Verified directly (not from Cursor's report — I re-confirmed myself): querying `youtube_analytics.py` with an older date range (2026-07-10 to 07-24) returns full real rows; the exact window 07-25/07-26 returns zero rows on both channels' entire Analytics API surface (channel-level, per-video, traffic source). This is API processing lag (~3 days observed), not a bug in data collection. **Re-running this same review in ~24-48h will very likely unlock the single most requested-but-missing data point (retention / averageViewPercentage).**

### 1.4 Near-zero comment engagement may reflect a structural gap, not just small sample

1 comment across 8 videos. Looking at the 8 hooks/closes directly: **none of the 10 generators currently include an explicit comment-inviting close** (e.g., "which one are you," "do you agree," a direct question aimed at the *viewer's own identity/opinion* rather than at the topic). The Kinh Dịch and Western Zodiac categories are the most natural fit for this (audience self-identifies with a sign/hexagram) and currently end on category-explaining statements instead.
**Confidence: LOW-MEDIUM.** Comment counts are typically the lowest-volume, highest-variance engagement signal even at scale; 1-vs-0 across 8 videos is barely a signal at all. But the *structural absence* of any comment-inviting close across all 10 generators is a fact I can point to directly in the prompts, independent of whether this specific week's near-zero count means anything.

### 1.5 Evergreen content (no date/time anchor) is the weakest performer, but the reason is unconfirmed

`element_color_short_generator.py` (màu hợp mệnh, evergreen — no "hôm nay"/date framing) produced the lowest view count (79) among content that isn't an extreme single-sample outlier like Song Tử.
**Hypothesis [confidence: LOW]:** date/context-anchored titles ("...Ngày Canh Tý 25/07/2026") may read as more timely/relevant-right-now to a scrolling viewer than a timeless "màu hợp mệnh Kim" title, independent of retention quality.
**Brand Manifesto check:** this must NOT be solved by manufacturing urgency (explicitly forbidden). The legitimate version of this fix is specificity, not urgency — e.g. anchoring to a real, already-true detail (season, an actual upcoming event) rather than inventing a deadline.

---

## 2. Reusable patterns worth carrying into the system (not just this week's videos)

1. **Score-then-discard is a systemic pattern across the pipeline, not just this batch.** The judge panel computes a real quality signal and then nothing downstream persists it. Same root cause as several bugs fixed earlier this session (rotation-state committing before success, topic-bank resets) — a valuable computed result gets produced but not carried forward. Fixing this once, in the shared registry-write path, benefits every future batch permanently.
2. **Small-batch, high-variance categories need a bigger sample before category-level judgments are safe.** Any future "cut this category" or "double down on that category" decision needs n≥10-15 per category, not n=1-2. This is a process discipline recommendation, not a code change.
3. **The retention-rubric + hook-word-count-cap fix already built earlier this session (not yet field-tested)** is directly relevant to hypothesis 1.1/1.5 but was implemented *after* this batch was generated — none of these 8 videos benefited from it. This makes next week's batch a natural, already-in-place test of that fix's real-world effect, with no new prompt work needed to test it.

---

## 3. Prioritized improvement plan (proposals only — none applied)

Each item: **Priority · Effort · Risk · Confidence this addresses a real problem**

### P0 — do first (near-zero risk, unlocks all future analysis)

**P0-1. Persist `hook_score`, judge history, category, and generator name into every registry entry, including the Phong-Thủy skip-path.**
Effort: small (1 file, `short_batch_runner.py`, additive field only). Risk: none (pure logging, no content/behavior change). Confidence this is worth doing: HIGH — this is a fact-based gap (§1.2), not a hypothesis.

**P0-2. Re-run this same Review & Analytics process in ~24-48h** once Analytics API processes 07-25/07-26, specifically to get retention/`averageViewPercentage`/traffic-source data. Effort: near-zero (script already exists). Risk: none. This is the single highest-value next step — it directly tests hypotheses 1.1 and 1.5.

### P1 — safe to test in the next batch (low risk, moderate potential value)

**P1-1. Add an explicit, identity-based comment-inviting close to Western Zodiac and Kinh Dịch generators specifically** (e.g., ending on "which one sounds like you" rather than a category-explaining statement) — natural fit for these 2 categories, does not touch grounded-data categories where an invented "which one are you" framing wouldn't make sense. Must stay within the calm/non-manipulative voice (§0) — a genuine question, not a manufactured engagement-bait CTA.
Effort: small (2 prompt files). Risk: low — reversible, category-scoped, no factual claims affected.

**P1-2. Hold off on any category-level cuts or emphasis shifts until sample size reaches ~10-15 videos per category.** This is a *process* recommendation (wait, don't change code) rather than a pipeline change.

### P2 — needs more data before committing (do not start yet)

**P2-1. Investigate evergreen-content hook specificity** (§1.5) — but only after P0-2 provides retention data to distinguish a discovery problem from a retention problem. Acting on this now, with 1 data point and no retention signal, risks solving the wrong problem.

---

## 4. Explicit non-recommendations

To be clear about what I am **not** proposing, given Brand Manifesto constraints and data limitations:

- **Not** proposing to manufacture urgency/deadlines on evergreen content (§1.5) — forbidden by domain guide regardless of potential view-count upside.
- **Not** proposing to drop Category 4 (Creative Astrology) or Category 1 evergreen based on this week's numbers — sample size (§2.2) makes this premature and could discard a category that's actually fine.
- **Not** proposing any change to fact-check rigor, category rubrics, or the "calm/reverent" tone standard in pursuit of engagement — none of this week's findings implicate content *accuracy* as a problem; the gaps found are pipeline instrumentation (§1.2) and untested structural elements (§1.4), not a rigor/tone trade-off.

---

*Next: submit this diagnosis + Cursor's report to Codex CLI for independent critique (artifact 03).*
