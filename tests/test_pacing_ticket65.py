"""Ticket 65: p50/p90 độ dài cảnh, nhịp phút đầu/cuối, cảnh giữ > 25 giây phải có lý do trong plan."""
import hf_batch_render as HBR


def _segs(durs):
    out, t = [], 0.0
    for d in durs:
        out.append({"start": t, "end": t + d - .2})
        t += d
    return out


def _row(n, **kw):
    return {"script": [f"Câu số {i}." for i in range(1, n + 1)], "kinetic": True, **kw}


def test_p50_p90_va_nhip_hai_dau():
    durs = [8.0] * 40                              # 320 giây, mỗi câu một cảnh 8 giây
    rep, _ = HBR.pacing(_row(40), _segs(durs))
    assert rep["p50 giây"] == 8.0 and rep["p90 giây"] == 8.0
    assert rep["TB phút đầu"] == 8.0 and rep["TB phút cuối"] == 8.0
    assert any(x.startswith("phút đầu 8.0s/cảnh") for x in rep["sàn"])
    assert any(x.startswith("phút cuối 8.0s/cảnh") for x in rep["sàn"])


def test_hai_dau_nhanh_thi_khong_bao():
    durs = [3.0] * 25 + [8.0] * 20 + [3.0] * 25
    rep, _ = HBR.pacing(_row(len(durs)), _segs(durs))
    assert rep["TB phút đầu"] <= 4 and rep["TB phút cuối"] <= 4
    assert not any("phút đầu" in x or "phút cuối" in x for x in rep["sàn"])


def test_video_ngan_khong_do_hai_dau():
    rep, _ = HBR.pacing(_row(5), _segs([8.0] * 5))
    assert "TB phút đầu" not in rep


def test_canh_dai_can_ly_do():
    durs = [6.0, 6.0, 30.0, 6.0]
    _, bad = HBR.pacing(_row(4), _segs(durs))
    assert any("cảnh đứng 30s từ câu 3" in x and '"slow_hold"' in x for x in bad)
    _, bad = HBR.pacing(_row(4, slow_hold={"3": "đọc nguyên văn bia"}), _segs(durs))
    assert not any("cảnh đứng" in x for x in bad)
