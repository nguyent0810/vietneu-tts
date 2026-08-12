# Version Manifest — Production Creator Prompt v1

**Status: FROZEN PRODUCTION VERSION — Codex-approved (3 rounds for the freeze action; the underlying §0-§6 rule content was separately Codex-approved across 3 earlier rounds before freezing).**

This manifest is the authoritative record of what went into `PRODUCTION_CREATOR_PROMPT_v1.md`'s frozen state. If any source artifact below is later found to have a different hash than recorded here, the frozen prompt's provenance should be treated as unverified until reconciled.

---

## Frozen artifact

| Field | Value |
|---|---|
| **Version** | v1 |
| **Build date** | 2026-07-27 |
| **File** | `creator_specs/PRODUCTION_CREATOR_PROMPT_v1.md` |
| **SHA-256 (full file, header + rule content — final, post-approval)** | `1a590e6e3d80cab37df48fe3859cb034fb41bc27225a8785b54c98d2a889f7da` |
| **SHA-256 (rule content only — from `## §0.` to end of file, excludes the freeze banner/header)** | `3f31b4124ec8d9751acc1fe6031a054878fbe447d6c752a069268ed4e846dbeb` |
| **Line count** | 163 |
| **Approval of rule content (§0-§6)** | Codex-approved, 3 rounds, prior to the freeze edit (see that document's own review history) |
| **Approval of the freeze action (header/banner edit only)** | Codex-approved, 3 rounds (this turn) |
| **Applied to production?** | No — not applied to `content_categories.py` or any generator; not used to generate any script or content |

**Why two hashes:** the full-file hash changes whenever the header/banner text changes (e.g. wording fixes). The rule-content-only hash is computed from `## §0.` onward and is unaffected by header edits. Demonstrated directly during this build: three successive header edits (initial freeze banner, two wording fixes, and the final approved-status update) each changed the full-file hash (`2aed3e70...` → `aa400b0f...` → `76bae6ee...` → `1a590e6e...`) while the rule-content hash stayed identical (`3f31b4124e...` all four times) — concrete evidence the two are actually independent, not just asserted to be.

**Known limitation, stated plainly rather than overclaimed (per Codex round 2 review):** the rule-content hash above proves the *current* §0-§6 text is internally self-consistent and stable across header edits made *during this build*. It does **not** independently prove this content is byte-identical to whatever Codex reviewed and approved in the 3 rounds *before* this freeze/build turn began — that would require an archived pre-freeze snapshot, and this workspace has no version control tracking for `creator_specs/` (confirmed: `git status` shows the whole directory as untracked). The claim that §0-§6 is unchanged from the Codex-approved version rests on this build's own conversation record (each edit in this and prior turns was a scoped, auditable string-replacement, never a full-file rewrite) — not on an independently reproducible cryptographic proof. Committing source files to version control before/after each future edit would close this gap; it has not been done here, since committing was not requested and is outside this turn's scope.

---

## Source artifacts

### Source Brand Manifesto

| Field | Value |
|---|---|
| **File** | `content_repo_clone/CORE_OS/BRAND_BIBLE.md` |
| **Document version** | None — the source file has no internal version field (checked directly: no "version" string anywhere in the file). SHA-256 is the only available identifier. |
| **SHA-256** | `51ace1c5d79405350986b996941018d73aa0864cee074719855353912864debb` |
| **Line count** | 5 |
| **Reproduced in frozen prompt** | §0, verbatim — independently diffed word-for-word against this file during Codex review of `PRODUCTION_CREATOR_PROMPT_v1.md` round 1 |

### Source Creator Specification

| Field | Value |
|---|---|
| **File** | `creator_specs/CREATOR_SPECIFICATION_v2.md` |
| **Document version** | v2 (document-level, per its own title and changelog) — the one rule it contains, `CR-1`, separately declares its own `Version: 1.0` |
| **SHA-256** | `1afbcb7cbe30110a81dbfcc56e25e4ccc86480aad32321ad68df2f4753983035` |
| **Line count** | 89 |
| **Approval status** | Codex-approved, 3 rounds |
| **Rule(s) merged into frozen prompt** | `CR-1` only (the sole Creator Rule in this document) |

### Source Prompt Delta

| Field | Value |
|---|---|
| **File** | `creator_specs/PROMPT_DELTA_v1.md` |
| **Document version** | 1.4 (document-internal `Version:` field) — note the filename says `v1` while the content declares `1.4`; both are recorded here to avoid the filename-vs-content-version ambiguity this workflow has previously run into |
| **SHA-256** | `39a1b2bf205dbbf0e75bd73e74f11ba8977877f0174ff1a0350618bd491be9a1` |
| **Line count** | 197 |
| **Approval status** | Codex-approved in full — Deltas 1-6 (3 rounds) + Deltas 7-9 (2 rounds) |
| **Deltas merged into frozen prompt** | All 9 (Deltas 1-6 → frozen prompt §2.1-§2.6; Delta 7 → §3; Delta 8 → §4; Delta 9 → §5) |

---

## What the frozen prompt declares as its inputs

**Corrected per Codex review — reworded from a process claim (which cannot be independently verified from the workspace alone) to a verifiable content claim:** the frozen prompt declares only these three artifacts as normative merge inputs (`PRODUCTION_CREATOR_PROMPT_v1.md`'s own header states this explicitly). No direct content attribution to the Pipeline Specification, any analytics review artifact, `PR5_AUDIT_REPORT_v1.md`, the candidate knowledge package, or any deferred/rejected proposal was identified in the frozen document's rule content (§0-§6). Where the Creator Specification or Prompt Delta themselves cite one of those documents (e.g. `CR-1`'s "Source" field naming a diagnosis file, or a delta's "Evidence" field naming the audit report), that citation is metadata already present inside a permitted source file — no new content was pulled from the cited document itself into the frozen prompt's rule text.

---

## Integrity and provenance verification note

**Corrected per Codex review — renamed from "Reproducibility note" and softened, since hashes alone don't make this rebuild-reproducible without an archived source bundle or build procedure, only identity-verifiable.** The five hashes above (three source-file hashes + the frozen prompt's full-file and rule-content-only hashes) let a future reader verify identity, not reconstruct the build from scratch. If a source file's current working-tree content no longer matches the hash recorded here, that means **the current working-tree copy no longer verifies against this manifest** — it does not by itself mean the original build was invalid; the historical bytes (if archived elsewhere, e.g. version control) may still be the valid provenance record. This manifest does not auto-update; it is a point-in-time record, taken 2026-07-27, of the exact source states used to build `PRODUCTION_CREATOR_PROMPT_v1.md`'s frozen state.
