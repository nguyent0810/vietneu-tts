import json
from pathlib import Path
import pytest
from tools.long_packaging.promise_check import (
    check_plan,
    find_promise_answer,
    is_heading,
    parse_chapters,
    resolve_plan_path,
    split_sentences,
)


def test_is_heading():
    assert is_heading("**Chương 1: Mở đầu**")
    assert not is_heading("Không phải tiêu đề")
    assert not is_heading("**Từ khoá** trong câu")
    assert not is_heading("**Chương 1** và **Chương 2**")


def test_split_sentences():
    text = "Câu thứ nhất. Câu thứ hai! Câu thứ ba?"
    sents = split_sentences(text)
    assert len(sents) == 3
    assert sents[0] == "Câu thứ nhất."
    assert sents[1] == "Câu thứ hai!"
    assert sents[2] == "Câu thứ ba?"


def test_promise_check_thin_warning():
    """Kiểm tra khi câu trả lời mỏng (< 3 câu) thì báo WARN / CẢNH BÁO."""
    script = [
        "Mở đầu câu chuyện.",
        "**Chương 1: Thử nghiệm**",
        "Câu nói về chủ đề khác 1.",
        "Câu nói về chủ đề khác 2.",
        "Nếu hai người khắc nhau trong nhà, hãy dùng hành đứng giữa.",
        "Đó là cách hóa giải khác mệnh duy nhất.",
        "Câu kết thúc chương.",
    ]
    res = find_promise_answer("Khắc nhau với người nhà?", script)
    assert res["chapter_num"] == 1
    assert res["count"] == 2
    assert res["status"] == "WARN"
    assert "CẢNH BÁO: phần trả lời quá mỏng" in res["verdict"]


def test_promise_check_pass_thick():
    """Kiểm tra khi câu trả lời dày (>= 3 câu) thì ĐẠT."""
    script = [
        "**Chương 1: Vì sao hoàng tử giả câm?**",
        "Hoàng tử không muốn làm vua.",
        "Ngài nhớ lại kiếp trước từng làm vua và phạm tội.",
        "Vì vậy ngài quyết định im lặng suốt mười sáu năm.",
        "Đây là lời dạy sâu sắc về nghiệp quả.",
    ]
    res = find_promise_answer("Vì sao hoàng tử giả câm để không làm vua?", script)
    assert res["chapter_num"] == 1
    assert res["count"] >= 3
    assert res["status"] == "PASS"
    assert "ĐẠT" in res["verdict"]


def test_promise_check_chapter_title_match_thin():
    """Khi tiêu đề chương khớp câu hỏi nhưng chỉ có < 3 câu thì báo WARN mỏng (Point 4)."""
    script = [
        "**Chương 1: Vì sao hoàng tử giả câm?**",
        "Ngài quyết định giữ im lặng không mở miệng nói một lời nào.",
    ]
    res = find_promise_answer("Vì sao hoàng tử giả câm để không làm vua?", script)
    assert res["chapter_num"] == 1
    assert res["count"] == 1
    assert res["status"] == "WARN"
    assert "CẢNH BÁO: phần trả lời quá mỏng (1 câu < 3 câu)" in res["verdict"]


def test_check_plan_auto_reads_questions_field(tmp_path: Path):
    """check_plan tự động đọc danh sách câu hỏi trong trường 'questions' (Point 3)."""
    fixture_data = [{
        "id": "test_doc",
        "title": "Tiêu Đề Video Mẫu",
        "questions": [
            "Câu hỏi chuỗi 1?",
            {"id": "q2", "text": "Câu hỏi trong dict 2?"},
            {"id": "q3", "question": "Câu hỏi trong dict 3?"},
        ],
        "script": [
            "**Chương 1: Mở đầu**",
            "Nội dung câu 1.",
            "Nội dung câu 2.",
            "Nội dung câu 3.",
        ],
    }]
    plan_file = tmp_path / "plan_test.json"
    with plan_file.open("w", encoding="utf-8") as f:
        json.dump(fixture_data, f, ensure_ascii=False)

    results = check_plan(plan_file)
    queries = [r["query"] for r in results]
    assert "Tiêu Đề Video Mẫu" in queries
    assert "Câu hỏi chuỗi 1?" in queries
    assert "Câu hỏi trong dict 2?" in queries
    assert "Câu hỏi trong dict 3?" in queries


def test_promise_check_fixtures_p1_p2_p3():
    """Kiểm tra P1, P2, P3 từ fixture độc lập tests/fixtures/ (Point 2)."""
    fixture_path = resolve_plan_path("tests/fixtures/long_packaging_plans.json")
    assert fixture_path.exists(), f"Không tìm thấy fixture {fixture_path}"

    # P1: Temiya
    res_p1 = check_plan(fixture_path, only="L_bud_P1_temiya")
    assert len(res_p1) >= 1
    p1_check = [r for r in res_p1 if "Vì sao hoàng tử giả câm" in r["query"]][0]
    assert p1_check["chapter_num"] == 1
    assert p1_check["count"] >= 3
    assert p1_check["status"] == "PASS"

    # P2: Kisa Gotami
    res_p2 = check_plan(fixture_path, only="L_bud_P2_kisagotami")
    assert len(res_p2) >= 1
    p2_check = [r for r in res_p2 if "hạt cải" in r["query"]][0]
    assert p2_check["chapter_num"] == 5
    assert p2_check["count"] >= 3
    assert p2_check["status"] == "PASS"

    # P3: Ananda
    res_p3 = check_plan(fixture_path, only="L_bud_P3_ananda")
    assert len(res_p3) >= 1
    p3_check = [r for r in res_p3 if "Đêm cuối cùng" in r["query"]][0]
    assert p3_check["chapter_num"] == 5
    assert p3_check["count"] >= 3
    assert p3_check["status"] == "PASS"


def test_promise_check_fs18_fixture():
    """Kiểm tra L_fs_18 từ fixture độc lập tests/fixtures/ (Point 2 & 5: không hardcode, báo WARN 2 câu)."""
    fixture_path = resolve_plan_path("tests/fixtures/long_packaging_plans.json")
    assert fixture_path.exists(), f"Không tìm thấy fixture {fixture_path}"

    results = check_plan(
        fixture_path,
        only="L_fs_18",
        question="Màu Hợp Với Bạn Có Thể Khắc Với Người Nhà?",
    )
    assert len(results) == 1
    r = results[0]
    assert r["chapter_num"] == 14
    assert r["count"] == 2
    assert r["status"] == "WARN"
    assert "CẢNH BÁO" in r["verdict"]


def test_synonyms_generic_no_false_positive():
    """Kiểm tra Point 5: SYNONYMS dùng tổng quát, câu chứa từ 'khắc' không khớp ngữ cảnh không bị nhận nhầm."""
    script = [
        "**Chương 1: Khắc phục sự cố phong thủy**",
        "Có nhiều cách khắc phục vị trí bàn thờ bị xấu.",
        "Chúng ta có thể dùng vách ngăn hoặc bình phong.",
        "Đây là biện pháp hiệu quả cho nhà chung cư.",
    ]
    # Câu hỏi về người nhà và vợ chồng khác mệnh, script chỉ có 'khắc phục'
    res = find_promise_answer("Vợ chồng khác mệnh nên chọn màu gì?", script)
    # Không được nhận nhầm câu "Có nhiều cách khắc phục..."
    assert res["status"] == "WARN"


def test_chuong_tieu_de_trung_mot_phan_nhung_rong_khong_thang():
    """Tiêu đề trùng vài từ (dưới ngưỡng tắt) nhưng không câu nào khớp -> không được chọn."""
    script = [
        "**Chương 1: Hoàng tử, cơn mưa đêm và kinh thành rất xa xôi**",
        "Trời hôm ấy mưa rất to trên mái ngói.",
        "**Chương 2: Mười sáu năm im lặng**",
        "Hoàng tử giả câm vì sợ phải làm vua.",
    ]
    res = find_promise_answer("Vì sao hoàng tử giả câm?", script)
    assert res["chapter_num"] == 2
