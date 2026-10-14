# Creator Specification — v2

**Status: Codex-APPROVED (3 rounds). Nothing in this document has been applied to any production prompt, generator, or rubric — awaiting your explicit approval before implementation.**

**Scope of this document:** content-generation rules only — what a generator/judge-panel prompt must produce or check in the text of a Short. Analytics, data pipeline, registry/schema, validation-process, and engineering rules have been moved out to `PIPELINE_SPECIFICATION_v1.md` (see that document's changelog for the split rationale).

**Rule status semantics (apply throughout this document):**
- **ACTIVE** — currently enforced in a production prompt/rubric today.
- **EXPERIMENTAL** — proposed and evidence-backed, not yet implemented in production.
- **DEPRECATED** — formerly active, now retired (with the reason).

---

## 1. Universal Creator Rules (apply to every channel)

### 1.1 Hook
No rule. No approved finding from either review cycle addressed hook construction.

### 1.2 Story structure
No rule. No approved finding from either review cycle addressed story structure.

### 1.3 Pacing
No rule. The only pacing-adjacent idea this cycle (duration-shortening, based on the `uHwa6nFBtkc` vs `YStIdWWuXcU` duration/retention comparison) was explicitly deferred, not approved — the causal "duration is a confound" framing was retracted during Codex review (n=1 per channel; `averageViewPercentage` is duration-normalized by definition, so it cannot demonstrate causation on its own). Excluded per the instruction to ignore unapproved suggestions.

### 1.4 Typography
No rule. Not in scope of either review cycle.

### 1.5 CTA
No rule. The only CTA idea from this review process (an identity-based comment-inviting close for Western Zodiac content) is listed as Deferred in the approved plan, gated on unresolved KPI-priority and brand-tone review — neither condition met. Not converted into a rule.

### 1.6 Tone & certainty

#### CR-1 — Uncertainty-hedging is mandatory for future-outcome and belief-based claims

> Any script sentence that (a) states a future outcome as certain, or (b) presents a belief/tradition-based claim as flat fact, must use hedge language appropriate to the domain (e.g. "có thể," "thường," "theo quan niệm," "theo truyền thống") rather than unqualified certainty.

- **Version:** 1.0
- **Source:** Cycle 1 §1.6 finding (`analytics_reviews/2026-07-25_to_2026-07-26/06_claude_diagnosis_v3.md`), independently re-verified in Cycle 2 (`analytics_reviews/cycle2_2026-07-27/04_claude_diagnosis_v4.md` §1.6, both Codex-approved).
- **Scope — split into three distinct layers per Codex round-1 review, since collapsing them caused confusion between "the rule is valid everywhere" and "the rule is currently only enforced in one place":**
  - **Normative scope (the obligation itself):** Universal — derived from the Core Brand Bible, which applies to every domain.
  - **Initial enforcement scope (where a concrete prompt change is proposed right now):** `GROUNDED_DATA` (Category 1) only — the only category with confirmed violation evidence. See `PROMPT_DELTA_v1.md` for the specific per-generator changes.
  - **Expansion gate:** Pipeline Spec `PR-5`'s audit result should inform whether enforcement widens to other categories — it does not gate whether the rule is *valid* (see Status note below), only how broadly it is *actively checked for* beyond Grounded Data.
- **Status:** EXPERIMENTAL — not yet implemented in any production prompt/rubric.
- **Evidence:** two live, uploaded Phong Thủy scripts, independently re-verified against the real registry (not taken from either Cursor's or Codex's report on faith): *"Mọi việc ... hứa hẹn diễn ra vô cùng thuận lợi," "vận khí đại cát"* (`CONGIAP20260726_ConGiap_01`), and *"gây khắc chế và làm năng lượng của bạn mất cân bằng"* stated as unhedged causal fact, with a caution-framed title (`MENH_Kim_MauSacHopMenh_01`). Both entries are tagged `GROUNDED_DATA` (Category 1) in `content_categories.py`.
- **Relationship to the Brand Manifesto:** this rule does **not** change the Brand Manifesto. It operationalizes an existing, unmodified line from `content_repo_clone/CORE_OS/BRAND_BIBLE.md`: *"Core brand rules: be accurate, humane, evidence-aware, non-manipulative, and clear about uncertainty."* CR-1 turns that line into a checkable judge-panel criterion; the Manifesto text itself is untouched.
- **Proposed prompt change:** recorded separately as a delta, not a rewrite — see `PROMPT_DELTA_v1.md` (revised to per-generator deltas after a real implementation gap was discovered during Codex review — `content_categories.py`'s shared rubric constant is not actually wired into any Grounded Data generator's judge prompt; see that document for the corrected approach).
- **Enforcement expansion informed by:** Pipeline Spec `PR-5` (accuracy/tone audit) — corrected wording per Codex round-1 review, since the rule's *validity* does not depend on that audit (the two violations are already confirmed facts); only the *breadth of active enforcement* beyond Grounded Data should wait on its result.

---

## 2. Brand-specific Rules

### 2.1 Buddhist (Phật giáo)
No new rule. Both review cycles explicitly excluded Phật giáo from pipeline recommendations (no internal pipeline visibility). Existing Buddhist Domain Manifest (`content_repo_clone/DOMAINS/BUDDHISM/DOMAIN_MANIFEST.md`, risk_level=high) is unchanged.

### 2.2 Feng Shui / Tử Vi (Phong Thủy)
No new distinct rule beyond CR-1 (§1.6) — noted here only as a priority flag: the confirmed CR-1 violations were both found in Phong Thủy content, so Pipeline Spec `PR-5`'s audit should run against the Phong Thủy content population first. This does not change or override the existing Feng Shui Domain Guide (`content_repo_clone/DOMAINS/FENG_SHUI/DOMAIN_GUIDE.md` §9 Anti-Fear-Sales Standard, §14 "Transform first, refuse only when transformation is impossible") — CR-1 is downstream of and consistent with those, not a replacement.

### 2.3 Crime (Hình Sự)
No rule proposed — no data. No evidence of an active, content-producing Crime/Hình Sự channel exists in either review cycle ("Hình Sự" appears only as an example string in `short_batch_runner.py`'s `--topic` CLI help text). Left empty rather than populated with invented rules.

### 2.4 Other channels
None identified with approved findings.

---

## 3. Rules to Remove

None identified. Neither review cycle's approved findings propose removing, contradicting, or obsoleting any existing creator rule or Domain Guide provision.

---

## 4. Changelog

**v2 vs. v1 (`CREATOR_SPECIFICATION_v1.md`):**

| Change | Reason |
|---|---|
| Removed former "Rule U-1" (persist generation-time quality score) | Not a content-generation rule — moved to Pipeline Spec `PR-4`, per the new requirement to separate Creator rules from Pipeline/Engineering rules |
| Removed former "Rule U-3" (AVD/AVP reconciliation in reporting) | Analytics-reporting rule, not content generation — moved to Pipeline Spec `PR-3` |
| Removed former "Rule U-4" (PT-day quarantine before using Analytics) | Data-validation rule, not content generation — moved to Pipeline Spec `PR-1`/`PR-2` |
| Former "Rule U-2" retained, renamed `CR-1` | The only genuine content-generation rule from either cycle — stays in the Creator Specification. Added full Version/Source/Scope/Status metadata per the new requirement |
| Added explicit rule-status semantics (ACTIVE/EXPERIMENTAL/DEPRECATED) | New requirement — all rules in this document are currently EXPERIMENTAL (not yet implemented) |
| Added `PROMPT_DELTA_v1.md` cross-reference for CR-1 | New requirement to record prompt changes as deltas, not full rewrites |
| Removed v1's entire "§3 Experiment Package" section (Experiments E/A/D/C, Reporting Control B, and the excluded-CTA note) | **Corrected per Codex round-1 review** — the original changelog line ("§2-4 unchanged in substance") was inaccurate and used a stale section-numbering scheme. What actually happened: v1's former §3 was removed wholesale from the Creator Specification (none of those items are content-generation rules) and its contents now live in `PIPELINE_SPECIFICATION_v1.md` §§1-3 (`PR-1` through `PR-5`) — see that document's own changelog for the item-by-item mapping. The Brand Rules and Rules-to-Remove *sections* (not v1's §2/§4 by number, which no longer align after the restructure) are unchanged in content. |

**Round-1 Codex review fixes (this revision):** the `CR-1` scope note above was split into normative/initial-enforcement/expansion-gate layers (previously conflated), the `Depends on` line was reworded to `Enforcement expansion informed by` (previously implied the rule's validity depended on the audit, which is not what was intended), and this changelog entry was corrected to accurately describe what moved rather than claim "unchanged."

**v1 vs. no prior document:** see `CREATOR_SPECIFICATION_v1.md`'s own changelog for that history — unchanged, not repeated here.
