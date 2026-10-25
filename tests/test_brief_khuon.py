"""ADR 0017 (sửa 24/10): AVP so theo nhóm độ dài, nhân khuôn cần cả hạng cao, luật dừng khuôn."""
import hf_brief as B


def _r(vid, dur, avp, views, rank=.5, lane="a", day="2026-10-20", week="2026-W43"):
    return {"vid": vid, "dur": dur, "averageViewPercentage": avp, "views": views, "rank": rank,
            "lane": lane, "day_pt": day, "week": week, "title": vid}


def test_avp_lift_theo_nhom_do_dai():
    rows = [_r("s1", 10, 130, 1), _r("s2", 12, 130, 1), _r("s3", 14, 260, 1),
            _r("l1", 30, 70, 1), _r("l2", 30, 70, 1), _r("l3", 31, 105, 1)]
    lift = B.avp_lift(rows)
    assert lift["s3"] == 2.0 and lift["s1"] == 1.0      # 130% ở bài 10 giây chỉ là mức nền
    assert round(lift["l3"], 2) == 1.5


def test_nhan_khuon_can_ca_hang_cao():
    rows = [_r("a", 10, 130, 900, rank=.95), _r("b", 10, 130, 800), _r("c", 10, 300, 70000, rank=.99),
            _r("d", 10, 300, 500, rank=.3)]
    rows += [_r("e", 10, 130, 700), _r("f", 10, 130, 600),
             _r("cu", 12, 300, 90000, rank=1, day="2026-09-01")]                # quá 14 ngày: không nhắc lại
    text = "\n".join(B.replicate_section(rows))
    assert "70000" in text and "— a" not in text and "— d" not in text and "90000" not in text


def test_dung_khuon():
    rows = [_r(f"x{i}", 25, 70, 300 + i, lane="nguhanh") for i in range(6)]
    rows += [_r(f"y{i}", 25, 70, 300, lane="tuoi") for i in range(5)] + [_r("y5", 25, 70, 5000, lane="tuoi")]
    rows += [_r(f"z{i}", 25, 70, 200, lane="it") for i in range(3)]
    rows += [_r("cu", 25, 70, 10, lane="nguhanh", day="2026-09-01")]   # ngoài 14 ngày
    text = "\n".join(B.stop_section("fs", rows))
    assert "| `nguhanh` | 6 |" in text and "**DỪNG**" in text.split("`nguhanh`")[1].split("\n")[0]
    assert "giữ" in text.split("`tuoi`")[1].split("\n")[0]          # có một bài vượt 3× sàn
    assert "chưa đủ bài" in text.split("`it`")[1].split("\n")[0]


def test_bai_trung_moi_tuan():
    rows = [_r("a", 10, 300, 12000), _r("b", 10, 100, 500), _r("c", 10, 100, 400)]
    assert "| 2026-W43 | 3 | 1 | 1 (33%) |" in "\n".join(B.week_hits(rows))
