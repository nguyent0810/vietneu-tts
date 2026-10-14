"""hf_slots: giờ yếu kéo dài mới đổi, mỗi lần một giờ, có thời gian chờ, giờ mới cách >= 90 phút."""
from datetime import date

import hf_slots as S


def _rows(hour_vn, rank, weeks=4, per_week=2):
    return [{"vn": f"2026-11-0{w + 1} {hour_vn}:00", "week": f"2026-W4{w}", "rank": rank, "views": 900, "clean": True}
            for w in range(weeks) for _ in range(per_week)]


def test_weak_slot_replaced_by_proven_good_hour():
    rows = _rows("15", .2) + _rows("23", .8) + _rows("10", .6) + _rows("21", .7)
    stats = S.hour_stats(rows)
    d = S.decide(["03:30", "08:00", "16:20"], stats, [], date(2026, 12, 1))   # 10:30, 15:00, 23:20 VN
    assert d["from"] == "08:00" and d["kind"] == "dùng giờ tốt" and S.utc_to_vn(d["to"]) == "21:00"


def test_one_bad_week_is_not_enough_and_cooldown():
    rows = _rows("15", .2, weeks=1, per_week=8) + _rows("23", .8)
    assert S.decide(["08:00", "16:20"], S.hour_stats(rows), [], date(2026, 12, 1)) is None
    rows = _rows("15", .2) + _rows("23", .8) + _rows("21", .7)
    hist = [{"date": "2026-11-28", "from": "x", "to": "y"}]
    assert S.decide(["08:00", "16:20"], S.hour_stats(rows), hist, date(2026, 12, 1)) is None


def test_explore_when_no_good_hour():
    rows = _rows("15", .2) + _rows("23", .6)
    d = S.decide(["08:00", "16:20"], S.hour_stats(rows), [], date(2026, 12, 1))
    assert d and d["kind"] == "thử giờ mới" and all(S._apart(d["to"], o) >= 90 for o in ["16:20"])
