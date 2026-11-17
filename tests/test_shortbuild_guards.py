import pytest

from shortbuild import GuardError, validate


def _row(script):
    return {
        "id": "test-short", "day": "2026-11-14", "series": "bud",
        "lane": "tuong", "style": "photo", "kicker": "Một câu chuyện",
        "title": "Một câu chuyện bình yên", "insight": "Lắng nghe và suy ngẫm",
        "source": "nguồn kiểm thử", "script": script,
    }


def test_validate_warns_short_v2_style(capsys):
    validate([_row(["Mở đầu ngắn.", "Định nghĩa là một thuật ngữ."])])
    assert "CẢNH BÁO" in capsys.readouterr().out


def test_validate_accepts_valid_v2_row():
    script = ["Một câu mở đầu nhẹ nhàng."] + [f"Lắng nghe câu chuyện thứ {i} và thử nhìn lại điều mình đang trải qua hôm nay." for i in range(6)]
    validate([_row(script)])


def test_validate_exempts_daily_daytable_from_v2_and_hook():
    row = _row(["Hôm nay ngày Canh Ngọ.", "Hoàng đạo Tư Mệnh."])
    row.update(series="fs", lane="hoangdao", style="daytable", source="")
    validate([row])


def test_daily_exemption_keeps_zodiac_naming_gate():
    row = _row(["Người tuổi Lợn hôm nay nên nghỉ.", "Hoàng đạo Tư Mệnh."])
    row.update(series="fs", lane="hoangdao", style="daytable", source="")
    with pytest.raises(GuardError, match="zodiac_naming"):
        validate([row])


# ---- PO 16/11: kể cho tai nghe (Short)
def _story(script, **kw):
    row = _row(script)
    row.update(day="2026-12-01", lane="truyen", **kw)
    return row


def test_cau_tach_doi_bi_chan_o_moi_short():
    import hf_batch_render as H
    row = _row(["Ở đó, Đức Phật đang ngồi,", "cùng các vị tăng."])
    row["day"] = "2026-12-01"
    assert any("tách giữa chừng" in x for x in H.short_story_issues(row))


def test_short_truyen_rao_nguon_qua_1_cau_chi_canh_bao():
    import hf_batch_render as H
    row = _story(["Luật tạng ghi, vua hỏi con.", "Chú giải kể, vua bị giam.", "Ông nhìn ra cửa sổ."])
    assert H.short_story_issues(row) == []
    assert any("rào nguồn" in x for x in H.short_source_warnings(row))
    row = _story(["Luật tạng ghi, vua hỏi con.", "Ông nhìn ra cửa sổ."])
    assert H.short_story_issues(row) == []


def test_dang_thang_khong_bi_luat_rao_nguon():
    import hf_batch_render as H
    row = _row(["Kinh kể ba việc.", "Theo kinh, Ngài đứng dậy."])
    row["day"] = "2026-12-01"
    assert H.short_story_issues(row) == []


def test_pd_scenes_can_chip_phong_dung_trong_html():
    from shortbuild.guards import validate as V
    import hf_batch_render as H
    row = _row(["x"])
    row.update(pd_scenes=[2])
    orig = (H.short_v2_issues, H.short_tone_issues, H.short_hook_hints)
    H.short_v2_issues = H.short_tone_issues = H.short_hook_hints = lambda r: []
    try:
        import studio
        he = studio.hook_errors
        studio.hook_errors = lambda r: []
        with pytest.raises(GuardError, match="PHỎNG DỰNG"):
            V([row], "<html><body>không có nhãn</body></html>")
        V([row], '<html><body><div class="pdtag">PHỎNG DỰNG</div></body></html>')
    finally:
        H.short_v2_issues, H.short_tone_issues, H.short_hook_hints = orig
        studio.hook_errors = he
