"""Runner dựng loạt — test cho hai lớp lỗi IM LẶNG đã gặp thật.

Cả hai đều không làm chương trình báo lỗi: một cái cho ra video dài bất
thường, một cái cho ra video ghép tiếng cũ vào chữ mới. Không có test thì
chỉ phát hiện được bằng cách ngồi xem lại từng video.
"""
import json

import hf_batch_render as runner


def _manifest(tmp_path, segments, n_failed_qa=0):
    p = tmp_path / "x.json"
    p.write_text(json.dumps({"segments": segments, "n_failed_qa": n_failed_qa},
                            ensure_ascii=False), encoding="utf-8")
    return p


def test_phat_hien_cau_bi_doc_long(tmp_path):
    lines = ["Một câu ngắn.", "Câu thứ hai cũng ngắn."]
    m = _manifest(tmp_path, [{"start": 0.0, "end": 1.2},
                             {"start": 1.4, "end": 33.0}])   # 31.6s cho 1 câu ngắn
    assert runner.runaway_segments(m, lines) == [2]


def test_cau_doc_binh_thuong_khong_bi_bao_dong(tmp_path):
    lines = ["Mốc khởi điểm là tài sản trị giá từ hai triệu đồng trở lên.",
             "Dưới mức đó vẫn có thể bị xử lý hình sự trong một số trường hợp."]
    m = _manifest(tmp_path, [{"start": 0.0, "end": 4.6}, {"start": 4.8, "end": 9.9}])
    assert runner.runaway_segments(m, lines) == []


def test_qa_that_bai_cung_bi_coi_la_hong(tmp_path):
    lines = ["Một câu."]
    m = _manifest(tmp_path, [{"start": 0.0, "end": 1.0}], n_failed_qa=1)
    assert runner.runaway_segments(m, lines)


def test_nguong_doc_long_khop_toc_do_doc_tieng_viet():
    """13 ký tự/giây là mức đo được của giọng đang dùng; ngưỡng cảnh báo đặt
    ở 3 lần mức đó để không bắt nhầm câu đọc chậm có chủ ý."""
    assert 0.2 < runner.SEC_PER_CHAR_RUNAWAY < 0.3


def _short(script, **kw):
    return {"id": "t", "series": "bud", "lane": "niem", "day": "2026-11-20", "insight": "x", "script": script, **kw}


def test_short_v2_blocks_definition_in_line_two():
    """Bài yếu rơi người xem ở câu 2 khi câu 2 là định nghĩa (b30_e: "Nhà Phật gọi đó là tập khí")."""
    hook = "Hứa với mình sẽ không cáu nữa, vậy mà chuyện cũ lặp lại, ta vẫn phản ứng y hệt như lần trước đó."
    filler = ["một hai ba bốn năm sáu bảy tám chín mười mười một mười hai mười ba mười bốn mười lăm mười sáu"] * 3
    bad = runner.short_v2_issues(_short([hook, "Nhà Phật gọi đó là tập khí: nếp cũ thành đường mòn trong tâm."] + filler))
    assert any("câu 2" in x for x in bad)
    ok = runner.short_v2_issues(_short([hook, "Người kia có khi đã ngủ yên, còn mình thì nằm thức kể lại chuyện ấy."] + filler))
    assert not any("câu 2" in x for x in ok)


def test_short_v2_length_ignores_silent_ask_and_old_rows():
    words = ["ba " * 20] * 4                      # 80 tiếng đọc
    assert runner.short_v2_issues(_short(words + ["hỏi " * 30], silence=[5])) == []
    assert any("tiếng" in x for x in runner.short_v2_issues(_short(words[:2])))
    assert runner.short_v2_issues(_short(words[:1], day="2026-11-01")) == []   # short cũ (trước v2) không chặn
    assert any("insight" in x for x in runner.short_v2_issues(_short(words, insight="")))
