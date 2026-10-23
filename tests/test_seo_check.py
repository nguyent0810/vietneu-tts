import seo_check


def test_clean_short_plan_has_no_issues():
    row = {
        "id": "s1", "series": "bud", "title": "Kinh Pháp Cú: Lời nhắc",
        "keyword": "Kinh Pháp Cú", "description": "Kinh Pháp Cú nhắc ta dừng lại.",
        "tags": ["Kinh Pháp Cú"] + [f"tag{i}" for i in range(7)],
        "hashtags": ["#Shorts", "#phatphap"],
        "script": ["Kinh Pháp Cú nhắc ta.", "Câu thứ hai.", "Câu thứ ba."],
    }
    assert seo_check.check_row(row) == []


def test_warns_for_long_title_missing_chapters_and_thin_tags():
    row = {
        "id": "L1", "series": "fs", "dur": 900,
        "seo": {}, "thumbnail": "l1.jpg",
        "title": "Từ khóa này không xuất hiện trong tiêu đề rất dài hơn sáu mươi ký tự",
        "keyword": "Trạng Trình", "description": "Mô tả không có từ khóa.",
        "tags": ["tag"], "script": ["Một câu mở đầu."] * 3,
    }
    codes = {x["code"] for x in seo_check.check_row(row)}
    assert {"TITLE_OVER_60", "KEYWORD_NOT_EARLY", "KEYWORD_NOT_IN_DESCRIPTION",
            "KEYWORD_NOT_SPOKEN", "CHAPTERS_MISSING", "TAGS_UNDER_8"} <= codes


def test_plan_file_accepts_list_and_checks_hashtag_cap(tmp_path):
    p = tmp_path / "short.json"
    p.write_text('[{"id":"s2","title":"Chủ đề","keyword":"Chủ đề",'
                 '"description":"Chủ đề #a #b #c #d #e #f","tags":[],"script":[]} ]',
                 encoding="utf-8")
    result = seo_check.check_plan(p)
    codes = {x["code"] for x in result[0]["issues"]}
    assert "HASHTAGS_OVER_5" in codes
    assert "TAGS_UNDER_8" in codes


def test_short_duration_does_not_trigger_long_chapter_rule():
    row = {"series": "bud", "dur": 28, "title": "Chủ đề", "tags": [], "script": []}
    codes = {x["code"] for x in seo_check.check_row(row)}
    assert "CHAPTERS_MISSING" not in codes
