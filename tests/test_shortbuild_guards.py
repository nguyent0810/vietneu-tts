import pytest

from shortbuild import GuardError, validate


def _row(script):
    return {
        "id": "test-short", "day": "2026-11-14", "series": "bud",
        "lane": "tuong", "style": "photo", "kicker": "Một câu chuyện",
        "title": "Một câu chuyện bình yên", "insight": "Lắng nghe và suy ngẫm",
        "source": "nguồn kiểm thử", "script": script,
    }


def test_validate_blocks_short_v2_violation():
    with pytest.raises(GuardError, match="short_v2_issues"):
        validate([_row(["Mở đầu ngắn.", "Định nghĩa là một thuật ngữ."])])


def test_validate_accepts_valid_v2_row():
    script = ["Một câu mở đầu nhẹ nhàng."] + ["Lắng nghe câu chuyện và thử nhìn lại điều mình đang trải qua hôm nay." for _ in range(6)]
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
