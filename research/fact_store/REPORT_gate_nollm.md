# Ticket #123 — Fact Gate v2 + NO_LLM v2

Research-only implementation. No network or LLM calls were used, and no production data was changed.

## Implementation map

| File:line | Responsibility |
|---|---|
| `gate.py:8` | `ParsedClaim`, `Unparsed`, and pluggable `ClaimParser` interface. |
| `gate.py:36` | Sentence splitting, alias matching with case/diacritic folding, gate verb detection, quantity/time/polarity/modality extraction. Ambiguous or incomplete analysis yields `Unparsed`. |
| `gate.py:80` | Fact comparison and PASS/REVIEW/REJECT evaluation using verification results. |
| `nollm.py:18` | Verified-only template fill, slot-to-fact provenance, gate recheck, deterministic history rotation. |
| `templates_vi.json:1` | 24 Vietnamese templates: three each for the eight requested predicates, across title/hook/thumb sentence styles. |
| `__main__.py:12` | `gate` CLI and explicit experimental `--assume-verified` warning. |
| `test_gate_nollm.py:1` | Eight offline regression tests. |

## Gate results

Counts are claims extracted from `title`, `thumbnail_text`, and `voice_0_3s`; verdict is the package verdict. `--assume-verified` promotes only facts with a supporting `span_match` for this invocation.

### Verification status as stored

| Topic | Level | Verdict | PASS | REVIEW | REJECT |
|---|---|---:|---:|---:|---:|
| Temiya | safe | REJECT | 0 | 3 | 1 |
| Temiya | max_defensible | REVIEW | 0 | 5 | 0 |
| Temiya | invalid | REVIEW | 0 | 3 | 0 |
| Fansipan | safe | REVIEW | 0 | 4 | 0 |
| Fansipan | max_defensible | REVIEW | 0 | 4 | 0 |
| Fansipan | invalid | REVIEW | 0 | 3 | 0 |
| Bybit | safe | REJECT | 0 | 2 | 1 |
| Bybit | max_defensible | REJECT | 0 | 2 | 1 |
| Bybit | invalid | REVIEW | 0 | 4 | 0 |
| Huế phong thủy | safe | REVIEW | 0 | 4 | 0 |
| Huế phong thủy | max_defensible | REVIEW | 0 | 4 | 0 |
| Huế phong thủy | invalid | REVIEW | 0 | 4 | 0 |
| Ngày tốt cuối | safe | REVIEW | 0 | 4 | 0 |
| Ngày tốt cuối | max_defensible | REVIEW | 0 | 3 | 0 |
| Ngày tốt cuối | invalid | REVIEW | 0 | 3 | 0 |

### Experimental `--assume-verified`

| Topic | Level | Verdict | PASS | REVIEW | REJECT |
|---|---|---:|---:|---:|---:|
| Temiya | safe | REVIEW | 0 | 4 | 0 |
| Temiya | max_defensible | REVIEW | 0 | 5 | 0 |
| Temiya | invalid | REVIEW | 0 | 3 | 0 |
| Fansipan | safe | REVIEW | 0 | 4 | 0 |
| Fansipan | max_defensible | REVIEW | 0 | 4 | 0 |
| Fansipan | invalid | REVIEW | 0 | 3 | 0 |
| Bybit | safe | REJECT | 0 | 2 | 1 |
| Bybit | max_defensible | REJECT | 0 | 2 | 1 |
| Bybit | invalid | REVIEW | 0 | 4 | 0 |
| Huế phong thủy | safe | REVIEW | 0 | 4 | 0 |
| Huế phong thủy | max_defensible | REVIEW | 0 | 4 | 0 |
| Huế phong thủy | invalid | REVIEW | 0 | 4 | 0 |
| Ngày tốt cuối | safe | REVIEW | 0 | 4 | 0 |
| Ngày tốt cuối | max_defensible | REVIEW | 0 | 3 | 0 |
| Ngày tốt cuối | invalid | REVIEW | 0 | 3 | 0 |

No title/hook claim achieved PASS in the benchmark audit. The hand-built regression set exercises positive matches separately from these legacy package texts.

## NO_LLM output

| Topic | Candidates | Abstains |
|---|---:|---:|
| Temiya | 1 | 0 |
| Fansipan | 1 | 0 |
| Bybit | 1 | 0 |
| Huế phong thủy | 1 | 0 |
| Ngày tốt cuối | 4 | 0 |

Examples:

- Temiya: “Tương truyền Temiya tên là Temiyakumāra.” (`tt05_temiya_f05`)
- Fansipan: “Fansipan cao 3.147,3 m.” (`vsd_fansipan_f01`)
- Bybit: “Bybit mất 400.000 ETH vào 2025-02-21.” (`ck_bybit_2025_f06`)
- Huế: “Núi Ngự Bình cao 105 m.” (`f19_hue_phong_thuy_f12`)
- Ngày tốt cuối: “Theo quan niệm, Ngày Tam Nương: mùng 3, 7, 13, 18, 22, 27 âm lịch hằng tháng: kiêng làm việc lớn…” (`fs_short_ngay_tot_cuoi_f01`)

Abstain count is zero because each store currently has at least one eligible verified fact with a complete supported template. The generator returns a reason when it cannot produce any candidate; facts without a matching verified template are simply ineligible and never emitted.

## Verification data note

The checked-in `stores_fixed/*.verification.json` files are not all unverified: the five files contain numerous `verified` results, plus `disputed` results in Bybit and Ngày tốt cuối. Gate and generation read these statuses as stored; the experimental flag does not alter the files. Unverified fixture behavior is covered by tests that reset statuses in memory.

## Verification run

`python3 -m pytest research/fact_store/test_gate_nollm.py -q` — 8 passed. No network access used.
