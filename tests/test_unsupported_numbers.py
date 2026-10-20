import short_judge_panel_engine as E


def test_unsupported_numbers_flags_only_new_digits():
    facts = {"day": "Giáp Tý", "hours": ["23", "1"], "year": 2027}
    assert E.unsupported_numbers(facts, "Năm 2027 giờ 23 là tốt.") == []
    assert E.unsupported_numbers(facts, "Năm 2027 có 12 con giáp và 365 ngày.") == ["12", "365"]
    assert E.unsupported_numbers(facts, "Không có số nào.") == []


def test_validate_verdict_records_warning_without_blocking():
    cands = [{"strategy": s, "script": "Hôm nay có 99 điều thú vị. Hãy nghe tiếp."} for s in "ABC"]
    verdict = {"winner": "A", "winner_script": "Hôm nay có 99 điều thú vị. Hãy nghe tiếp.", "hook_score": 9,
               "fact_check": {"A": "PASS", "B": "PASS", "C": "PASS"}}
    out = E._validate_verdict(verdict, cands, facts={"original_script": "Hôm nay thú vị. Hãy nghe tiếp."})
    assert out["hook_score"] == 9                       # không ép điểm
    assert out["deterministic_warnings"] and "99" in out["deterministic_warnings"][0]
