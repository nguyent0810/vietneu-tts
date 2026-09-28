"""Đo scorer C4 của CL ở CẤP CÂU trên các corpus đã commit (ticket 08, D29/D43).

Corpus: `handoff/c4_freeze/c4_golden_corpus_v1.json` (35 fixture),
`c4_holdout_corpus_v1.json` (24), `c4_holdout_corpus_v2.json` (30). Mỗi
fixture là MỘT câu + excerpt căn cứ + nhãn kỳ vọng PASS/BLOCK.

Đầu ra là confusion matrix cấp câu (chặn đúng, chặn nhầm, bỏ sót, cho qua
đúng), chia theo corpus, category, materiality. ĐƠN VỊ ĐO LÀ CÂU -- KHÔNG
phải False Reject cấp Short (một Short bị chặn khi BẤT KỲ câu nào bị chặn;
không suy tỷ lệ cấp Short từ số liệu ở đây, D43).

Scorer là tham số: test dùng scorer giả; chạy thật với Codex là lệnh thủ
công (`python c4_sentence_harness.py run`), không chạy trong CI vì tốn phí
và không deterministic. Module này không import code CL (cần fcntl) ở cấp
module -- adapter scorer thật import trễ.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

REPO_ROOT = Path(__file__).parent
CORPUS_DIR = REPO_ROOT / "handoff" / "c4_freeze"
DEFAULT_CORPORA = {
    "golden_v1": CORPUS_DIR / "c4_golden_corpus_v1.json",
    "holdout_v1": CORPUS_DIR / "c4_holdout_corpus_v1.json",
    "holdout_v2": CORPUS_DIR / "c4_holdout_corpus_v2.json",
}
DEFAULT_REPORT_DIR = REPO_ROOT / "output" / "c4_reports"
UNIT_LABEL = "câu (sentence-level) -- KHÔNG phải False Reject cấp Short"
# C4 gọi Codex qua content_seo._run_codex: `codex exec` (model mặc định CLI),
# fallback cursor-agent --model auto. CLI không trả model thật từng lần gọi.
C4_JUDGE_MODEL = "codex exec (model mặc định CLI; fallback cursor-agent --model auto)"

EXPECTED_VALUES = frozenset({"PASS", "BLOCK"})
_REQUIRED_KEYS = ("id", "excerpt", "sentence", "expected", "category")

# Ô của confusion matrix (dương tính = "chặn").
TRUE_BLOCK = "chan_dung"        # expected BLOCK, scorer chặn
FALSE_BLOCK = "chan_nham"       # expected PASS, scorer chặn
MISSED_BLOCK = "bo_sot"         # expected BLOCK, scorer cho qua
TRUE_PASS = "cho_qua_dung"      # expected PASS, scorer cho qua
CELLS = (TRUE_BLOCK, FALSE_BLOCK, MISSED_BLOCK, TRUE_PASS)


class CorpusError(ValueError):
    """Fixture/corpus sai cấu trúc -- báo rõ file và fixture nào."""


@dataclass(frozen=True)
class Fixture:
    corpus: str
    id: str
    excerpt: str
    sentence: str
    expected: str
    category: str
    materiality: bool | None
    topic: str | None


@dataclass(frozen=True)
class ScorerOutcome:
    blocked: bool
    detail: str = ""
    scorer_error: bool = False  # scorer lỗi và fail-closed (bị tính là chặn như production)


Scorer = Callable[[Fixture], ScorerOutcome]


def load_corpus(name: str, path: Path) -> list[Fixture]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CorpusError(f"{path}: không đọc được corpus ({exc})") from exc
    if not isinstance(data, dict) or not isinstance(data.get("fixtures"), list) or not data["fixtures"]:
        raise CorpusError(f"{path}: thiếu danh sách 'fixtures' không rỗng")
    fixtures, seen = [], set()
    for i, raw in enumerate(data["fixtures"]):
        where = f"{path} fixture #{i}"
        if not isinstance(raw, dict):
            raise CorpusError(f"{where}: không phải object")
        missing = [k for k in _REQUIRED_KEYS if not isinstance(raw.get(k), str) or not raw[k].strip()]
        if missing:
            raise CorpusError(f"{where} (id={raw.get('id')!r}): thiếu/sai kiểu trường {missing}")
        if raw["expected"] not in EXPECTED_VALUES:
            raise CorpusError(f"{where} (id={raw['id']}): expected={raw['expected']!r} phải là PASS hoặc BLOCK")
        materiality = raw.get("materiality")
        if materiality is not None and not isinstance(materiality, bool):
            raise CorpusError(f"{where} (id={raw['id']}): materiality phải là bool nếu có")
        if raw["id"] in seen:
            raise CorpusError(f"{where}: id trùng {raw['id']!r}")
        seen.add(raw["id"])
        fixtures.append(Fixture(corpus=name, id=raw["id"], excerpt=raw["excerpt"], sentence=raw["sentence"],
                                expected=raw["expected"], category=raw["category"], materiality=materiality,
                                topic=raw.get("topic") or raw.get("episode")))
    return fixtures


def load_corpora(corpora: dict[str, Path] | None = None) -> list[Fixture]:
    out: list[Fixture] = []
    for name, path in (corpora or DEFAULT_CORPORA).items():
        out.extend(load_corpus(name, path))
    return out


def cell(expected: str, blocked: bool) -> str:
    if expected == "BLOCK":
        return TRUE_BLOCK if blocked else MISSED_BLOCK
    return FALSE_BLOCK if blocked else TRUE_PASS


def run(fixtures: Iterable[Fixture], scorer: Scorer) -> list[dict]:
    rows = []
    for fx in fixtures:
        outcome = scorer(fx)
        rows.append({
            "corpus": fx.corpus, "id": fx.id, "category": fx.category,
            "materiality": fx.materiality, "expected": fx.expected,
            "blocked": outcome.blocked, "scorer_error": outcome.scorer_error,
            "cell": cell(fx.expected, outcome.blocked), "detail": outcome.detail,
        })
    return rows


def _matrix(rows: list[dict]) -> dict:
    counts = Counter(r["cell"] for r in rows)
    return {c: counts.get(c, 0) for c in CELLS} | {"n": len(rows),
                                                    "scorer_error": sum(1 for r in rows if r["scorer_error"])}


def confusion(rows: list[dict]) -> dict:
    """Confusion matrix cấp câu: tổng, theo corpus, category, materiality."""
    def group(key):
        buckets: dict[str, list[dict]] = {}
        for r in rows:
            buckets.setdefault(str(r[key]), []).append(r)
        return {k: _matrix(v) for k, v in sorted(buckets.items())}
    return {"unit": UNIT_LABEL, "overall": _matrix(rows), "by_corpus": group("corpus"),
            "by_category": group("category"), "by_materiality": group("materiality")}


# --------------------------------------------------------------------------
# Adapter scorer C4 production (import trễ: code CL cần fcntl)
# --------------------------------------------------------------------------

def build_candidate(fx: Fixture):
    """Bọc excerpt của fixture thành đầu vào mà scorer C4 production cần:
    excerpt là căn cứ duy nhất (1 CoreFact), câu cần chấm là bản nháp."""
    import cl_risk_gate as g
    return g.CandidateCase(
        case_id=f"c4fixture-{fx.corpus}-{fx.id}",
        case_key=f"c4fixture-{fx.corpus}-{fx.id}",
        working_title=fx.topic or fx.id,
        core_facts=[g.CoreFact(fact_id="F001", statement=fx.excerpt, fact_type="excerpt")],
        risk_review_draft=fx.sentence,
    )


def production_scorer(fx: Fixture) -> ScorerOutcome:
    import cl_risk_gate_verification as v
    result = v.score_c4_adversarial(build_candidate(fx))
    error = "fail-closed" in (result.evidence or "")
    return ScorerOutcome(blocked=not result.passed, detail=result.evidence, scorer_error=error)


def production_scorer_version() -> str:
    import cl_risk_gate_verification as v
    blob = v._C4_ADVERSARIAL_PROMPT + "|" + ",".join(sorted(v._C4_MATERIAL_BLOCKING_VERDICTS))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def _git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def build_report(rows: list[dict], *, scorer_version: str, judge_model: str, corpora: dict[str, Path]) -> dict:
    return {
        "report_version": 1,
        "unit": UNIT_LABEL,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "scorer_version": scorer_version,
        "judge_model": judge_model,
        "corpora": {name: {"path": str(Path(p).relative_to(REPO_ROOT)) if Path(p).is_relative_to(REPO_ROOT) else str(p),
                           "sha256": hashlib.sha256(Path(p).read_bytes()).hexdigest()[:12]}
                    for name, p in corpora.items()},
        "confusion": confusion(rows),
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Đo C4 cấp câu trên golden/holdout corpus (chạy Codex thật, thủ công).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="Chạy scorer C4 production (Codex thật) và ghi báo cáo")
    r.add_argument("--out", default=None, help="đường dẫn báo cáo JSON (mặc định output/c4_reports/<thời điểm>.json)")
    r.add_argument("--corpus", action="append", choices=sorted(DEFAULT_CORPORA), help="chỉ chạy corpus này (lặp được)")
    args = ap.parse_args(argv)

    corpora = {k: v for k, v in DEFAULT_CORPORA.items() if not args.corpus or k in args.corpus}
    fixtures = load_corpora(corpora)
    rows = run(fixtures, production_scorer)
    report = build_report(rows, scorer_version=production_scorer_version(), judge_model=C4_JUDGE_MODEL,
                          corpora=corpora)
    out = Path(args.out) if args.out else DEFAULT_REPORT_DIR / f"c4_sentence_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    overall = report["confusion"]["overall"]
    print(f"Đơn vị: {UNIT_LABEL}")
    print(f"n={overall['n']} chặn đúng={overall[TRUE_BLOCK]} chặn nhầm={overall[FALSE_BLOCK]} "
          f"bỏ sót={overall[MISSED_BLOCK]} cho qua đúng={overall[TRUE_PASS]} lỗi scorer={overall['scorer_error']}")
    print(f"Báo cáo: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
