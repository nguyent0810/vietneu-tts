"""Harness đo C4 cấp câu (ticket 08): nạp corpus đã commit, confusion matrix
đúng với scorer giả, báo cáo ghi rõ đơn vị là câu. Không gọi Codex thật."""
import json

import pytest

import c4_sentence_harness as h


def test_loads_all_three_committed_corpora():
    fixtures = h.load_corpora()
    by_corpus = {name: sum(1 for f in fixtures if f.corpus == name) for name in h.DEFAULT_CORPORA}
    assert by_corpus == {"golden_v1": 35, "holdout_v1": 24, "holdout_v2": 30}
    assert all(f.expected in {"PASS", "BLOCK"} for f in fixtures)
    # holdout v2 không có materiality -> None, không đoán.
    assert all(f.materiality is None for f in fixtures if f.corpus == "holdout_v2")


@pytest.mark.parametrize("mutate,needle", [
    (lambda d: d.pop("fixtures"), "fixtures"),
    (lambda d: d["fixtures"][0].pop("sentence"), "sentence"),
    (lambda d: d["fixtures"][0].update(expected="MAYBE"), "PASS hoặc BLOCK"),
    (lambda d: d["fixtures"][0].update(materiality="yes"), "materiality"),
    (lambda d: d["fixtures"].append(dict(d["fixtures"][0])), "trùng"),
])
def test_malformed_corpus_fails_with_clear_error(tmp_path, mutate, needle):
    data = json.loads(h.DEFAULT_CORPORA["golden_v1"].read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(h.CorpusError, match=needle):
        h.load_corpus("bad", path)


def _fx(id, expected, category="paraphrase", materiality=True, corpus="c"):
    return h.Fixture(corpus=corpus, id=id, excerpt="e", sentence="s", expected=expected, category=category,
                     materiality=materiality, topic=None)


def test_confusion_matrix_cells_with_fake_scorer():
    fixtures = [
        _fx("1", "BLOCK", "invented_motive"),            # chặn đúng
        _fx("2", "PASS", "paraphrase"),                   # chặn nhầm
        _fx("3", "BLOCK", "changed_number", corpus="d"),  # bỏ sót
        _fx("4", "PASS", "paraphrase", materiality=False),  # cho qua đúng
        _fx("5", "PASS", "harmless_connective", materiality=None),  # scorer lỗi -> fail-closed chặn
    ]
    decisions = {"1": h.ScorerOutcome(True), "2": h.ScorerOutcome(True), "3": h.ScorerOutcome(False),
                 "4": h.ScorerOutcome(False), "5": h.ScorerOutcome(True, "fail-closed", scorer_error=True)}
    rows = h.run(fixtures, lambda fx: decisions[fx.id])
    m = h.confusion(rows)
    assert m["unit"] == h.UNIT_LABEL
    assert m["overall"] == {h.TRUE_BLOCK: 1, h.FALSE_BLOCK: 2, h.MISSED_BLOCK: 1, h.TRUE_PASS: 1, "n": 5,
                            "scorer_error": 1}
    assert m["by_corpus"]["d"][h.MISSED_BLOCK] == 1
    assert m["by_category"]["paraphrase"] == {h.TRUE_BLOCK: 0, h.FALSE_BLOCK: 1, h.MISSED_BLOCK: 0, h.TRUE_PASS: 1,
                                              "n": 2, "scorer_error": 0}
    assert set(m["by_materiality"]) == {"True", "False", "None"}


def test_report_records_versions_corpora_commit_and_unit():
    rows = h.run(h.load_corpora(), lambda fx: h.ScorerOutcome(fx.expected == "BLOCK"))
    report = h.build_report(rows, scorer_version="sv1", judge_model="jm", corpora=h.DEFAULT_CORPORA)
    assert report["unit"] == h.UNIT_LABEL and "cấp Short" in report["unit"]
    assert report["scorer_version"] == "sv1" and report["judge_model"] == "jm"
    assert set(report["corpora"]) == set(h.DEFAULT_CORPORA)
    assert all(v["sha256"] for v in report["corpora"].values())
    assert report["created_at"] and "git_commit" in report
    overall = report["confusion"]["overall"]
    assert overall[h.FALSE_BLOCK] == overall[h.MISSED_BLOCK] == 0 and overall["n"] == 89


def test_adapter_wraps_excerpt_as_the_only_fact_and_sentence_as_draft():
    pytest.importorskip("fcntl", reason="adapter dựng CandidateCase của code CL (cần fcntl)")
    fx = h.load_corpus("golden_v1", h.DEFAULT_CORPORA["golden_v1"])[0]
    cand = h.build_candidate(fx)
    assert cand.risk_review_draft == fx.sentence
    assert [cf.statement for cf in cand.core_facts] == [fx.excerpt]
    import cl_risk_gate_verification as v
    block = v._facts_block_for_draft(cand)
    assert fx.excerpt in block


def test_production_scorer_maps_blocked_and_fail_closed(monkeypatch):
    pytest.importorskip("fcntl", reason="scorer C4 production nằm trong code CL (cần fcntl)")
    import cl_risk_gate_verification as v
    fx = h.load_corpus("golden_v1", h.DEFAULT_CORPORA["golden_v1"])[0]
    monkeypatch.setattr(v, "_run_codex", lambda prompt: json.dumps(
        {"claims": [{"sentence": fx.sentence, "verdict": "UNSUPPORTED", "materiality": True, "reason": "x"}]}))
    out = h.production_scorer(fx)
    assert out.blocked and not out.scorer_error
    monkeypatch.setattr(v, "_run_codex", lambda prompt: json.dumps(
        {"claims": [{"sentence": fx.sentence, "verdict": "ENTAILED", "materiality": True, "reason": "x"}]}))
    assert h.production_scorer(fx).blocked is False
    monkeypatch.setattr(v, "_run_codex", lambda prompt: "không phải json")
    out = h.production_scorer(fx)
    assert out.blocked and out.scorer_error
