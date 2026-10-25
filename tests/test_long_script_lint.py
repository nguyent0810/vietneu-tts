"""long_script_lint -- soát kịch bản video dài trước TTS.

Các ca thử lấy từ lỗi thật của kênh (xem .claude/skills/long-script/references/evidence.md): câu đọc 5 năm sinh
(F6 rơi 4-7 điểm mỗi lần), "Video này sẽ..." ở giây 12-35 (B3, B5, F6), chương định nghĩa thứ hai (F1, F3, F6),
"1-3" bị TTS đọc thành ngày tháng.
"""
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hf_batch_render as HBR  # noqa: E402
import long_script_lint as LL  # noqa: E402

PLAN_W41 = Path(__file__).resolve().parents[1] / "output/cl_staging/long/plan_long_w41.json"


def codes(rep):
    return {c for _, c, _ in rep["issues"]}


@pytest.mark.parametrize("n,words", [
    (1983, "một nghìn chín trăm tám mươi ba"),
    (2027, "hai nghìn không trăm hai mươi bảy"),
    (2008, "hai nghìn không trăm lẻ tám"),
    (1068, "một nghìn không trăm sáu mươi tám"),
    (105, "một trăm lẻ năm"),
    (15, "mười lăm"),
    (21, "hai mươi mốt"),
    (24, "hai mươi tư"),
    (2500, "hai nghìn năm trăm"),
])
def test_doc_so_nhu_tts(n, words):
    # khớp cách vieneu_utils.phonemize_text đọc (đo 14/10/2026: "1.068" -> một nghìn không trăm sáu mươi tám)
    assert LL.read_int(n) == words


def test_dem_tieng_doc_tinh_ca_chu_so():
    s = "Tuổi Tý gồm những người sinh năm âm lịch 1960, 1972, 1984, 1996 và 2008."
    assert LL.tokens(s) == 15            # runner đếm 15 -> không bao giờ báo
    assert LL.syllables(s) == 9 + 6 + 7 + 7 + 7 + 1 + 6  # đọc ra 43 tiếng


def test_tieu_de_chuong():
    assert LL.is_heading("**Tuổi Tý**")
    assert not LL.is_heading("Năm nay **Tý** gặp lục hại.")
    assert not LL.is_heading("**Một** câu có **hai** chữ khoá")


def test_doan_khong_ngat_nhip_khop_runner():
    """Lint dùng ĐÚNG định nghĩa của retention_issues: đoạn dài nhất phải ra cùng con số."""
    filler = "Người ta thường nghĩ rằng mọi chuyện đều đã được sắp đặt sẵn từ trước và mình chẳng thể làm gì khác được nữa"
    row = {"script": ["Một câu mở có con số 2027."] + [filler + "."] * 20 + ["**Chương hai**", "Câu hỏi?"]}
    worst = LL.beat_stretches(row)[0][0]
    msg = next(m for m in HBR.retention_issues(row) if "không ngắt nhịp" in m)
    assert f"~{worst:.0f} giây" in msg


@pytest.mark.skipif(not PLAN_W41.exists(), reason="plan thật không có trong máy này")
def test_doan_khong_ngat_nhip_khop_runner_tren_plan_that():
    for row in json.loads(PLAN_W41.read_text(encoding="utf-8")):
        worst = LL.beat_stretches(row)[0][0]
        msgs = [m for m in HBR.retention_issues(row) if "không ngắt nhịp" in m]
        if worst > 90:
            assert msgs and f"~{worst:.0f} giây" in msgs[0]
        else:
            assert not msgs


@pytest.mark.parametrize("sent", [
    "Rồi tham ái, uể oải, sợ hãi, hoài nghi, và cả danh vọng có được bằng cách sai trái.",
    "Tuổi Tý gồm những người sinh năm âm lịch 1960, 1972, 1984, 1996 và 2008.",
    "Ngài đi qua Lâm Tì Ni, Bồ Đề Đạo Tràng, Lộc Uyển, Câu Thi Na và Vương Xá.",
])
def test_bat_liet_ke_4_muc(sent):
    assert LL.list_issues(sent)


@pytest.mark.parametrize("sent", [
    "Lần thứ nhất, ngài gặp một người già, lưng còng, tóc bạc.",
    "Nghe xong, một người trong năm vị, Kiều Trần Như, bừng hiểu ra một điều.",
    "Hắn đứng lại, hét lớn: dừng lại, sa môn!",
    "Sinh, già và chết.",
])
def test_khong_bat_nham_dong_vi(sent):
    assert LL.list_issues(sent) is None


def test_phan_loai_cau():
    assert LL.kind_of("Bây giờ là giờ gì?") == "question"
    assert LL.kind_of("Video này sẽ đi cùng bạn qua đủ mười hai con giáp.") == "meta"
    assert LL.kind_of("Đêm ấy, bên bờ sông, một người đàn ông ngồi xuống dưới gốc cây.") == "story"
    assert LL.kind_of("Nghiệp được hiểu là hành động có tác ý.") == "abstract"
    assert LL.kind_of("Năm 2027, người sinh năm 1984 bước sang tuổi âm bốn mươi tư.") == "concrete"


def _row(lines, **kw):
    return {"id": "t", "script": lines, **kw}


def test_90_giay_dau_bat_meta_som_va_chuong_dinh_nghia():
    lines = ["Video này sẽ nói về năm tuổi.", "Năm tuổi được hiểu là năm gặp lại địa chi của mình.",
             "**Năm tuổi là gì?**", "Năm tuổi là năm Thái Tuế đóng ở cung tuổi mình."] + \
            ["Người sinh năm 1991 mang mệnh Thổ, gặp năm nước là năm hao sức."] * 30
    rep = LL.lint(_row(lines))
    c = codes(rep)
    assert {"mo_dau_khong_cu_the", "meta_som", "chuong_dinh_nghia_som"} <= c


def test_mo_dau_tot_khong_bi_bat():
    lines = ["Đêm ấy, bên bờ sông Ni Liên Thiền, một người đàn ông ba mươi lăm tuổi ngồi xuống dưới một gốc cây.",
             "Ông đã đói đến mức da bọc lấy xương.", "Vì sao ông ngồi đó?",
             "Sáu năm trước, ông còn là một thái tử.", "**Khu vườn Lâm Tì Ni**"] + \
            ["Hoàng hậu Ma Da đi qua khu vườn, tay vịn một cành cây sa la trổ hoa."] * 20
    c = codes(LL.lint(_row(lines)))
    assert not c & {"mo_dau_khong_cu_the", "cau2_khong_cu_the", "meta_som", "chuong_dinh_nghia_som", "chua_tra_som"}


def test_cau_dai_theo_tieng_doc_la_loi():
    rep = LL.lint(_row(["Tuổi Tý gồm những người sinh năm âm lịch 1960, 1972, 1984, 1996 và 2008."]))
    assert any(lv == LL.ERROR and c == "cau_dai" for lv, c, _ in rep["issues"])


def test_bay_tts():
    # lexicon tắt: lint cảnh báo đủ bốn bẫy như trước
    row = _row(["Mỗi ngày tụng 1-3 lần theo DN 16.", "Ông Sāriputta (Xá Lợi Phất) đến."])
    row["tts"] = {"lexicon": False}
    c = codes(LL.lint(row))
    assert {"tts_gach_noi", "tts_viet_tat", "tts_dau_la", "tts_ky_hieu"} <= c


def test_tts_lexicon_tu_sua_nen_lint_chi_goi_y():
    c = codes(LL.lint(_row(["Mỗi ngày tụng 1-3 lần theo DN 16.", "Ông Sāriputta (Xá Lợi Phất) đến."])))
    assert "tts_tu_sua" in c
    assert not c & {"tts_gach_noi", "tts_viet_tat", "tts_dau_la", "tts_ky_hieu"}
    # tên Pali chưa có trong lexicon vẫn bị cảnh báo
    assert "tts_dau_la" in codes(LL.lint(_row(["Jāṇussoṇi đến gặp Ngài."])))


def test_ket_chuong_bang_tom_tat():
    lines = ["Câu mở có năm 2027.", "Tóm lại, năm nay cần cẩn trọng.", "**Chương sau**", "Một câu khác có số 3."]
    assert "ket_chuong_tom_tat" in codes(LL.lint(_row(lines)))


def test_ket_chuong_bang_nhu_vay():
    lines = ["Vì sao năm nay khác?", "Như vậy, năm nay cần cẩn trọng.", "**Chương sau**", "Một câu khác có số 3."]
    hit = [x for x in LL.lint(_row(lines))["issues"] if x[1] == "ket_chuong_tom_tat"]
    assert hit and hit[0][0] == LL.WARN


def test_cau_dai_va_liet_ke_dung_muc():
    dai = "Tuổi Tý gồm những người sinh năm âm lịch 1960, 1972, 1984, 1996 và 2008."
    rep = LL.lint(_row([dai, "Bạn giữ câu hỏi này không?"]))
    assert any(lv == LL.ERROR and c == "cau_dai" for lv, c, _ in rep["issues"])
    assert any(lv == LL.WARN and c == "liet_ke" for lv, c, _ in rep["issues"])


def test_quy_vi_la_canh_bao():
    rep = LL.lint(_row(["Quý vị hãy ngồi xuống.", "Bạn hãy ngồi xuống lắng nghe?"]))
    assert any(lv == LL.WARN and c == "quy_vi" for lv, c, _ in rep["issues"])
    assert "quy_vi" not in codes(LL.lint(_row(["Bạn hãy ngồi xuống và lắng nghe?"])))


def test_cold_open_co_loi_chao():
    chao = LL.lint(_row(["Xin chào các bạn, hôm nay là một câu chuyện.", "Vì sao cánh cửa không mở?"]))
    assert any(lv == LL.WARN and c == "cold_open_chao" for lv, c, _ in chao["issues"])
    sach = LL.lint(_row(["Một người đứng trước cổng năm 2027.", "Vì sao cánh cửa không mở?"]))
    assert "cold_open_chao" not in codes(sach)


def test_chuong_mo_khong_co_cau_hoi_hay_moc():
    lines = ["Anh đứng trước cổng.", "Chị nhìn ra sân.", "**Chương sau**", "Vì sao họ dừng lại?"]
    assert any(lv == LL.WARN and c == "chuong_mo_khong_moc" for lv, c, _ in LL.lint(_row(lines))["issues"])
    hoi = ["Anh đứng trước cổng.", "Vì sao cánh cửa không mở?", "**Chương sau**", "Năm 2027."]
    assert "chuong_mo_khong_moc" not in codes(LL.lint(_row(hoi)))
    moc = ["Anh đứng trước cổng.", "Lát nữa ta sẽ quay lại cánh cửa ấy.", "**Chương sau**", "Năm 2027."]
    assert "chuong_mo_khong_moc" not in codes(LL.lint(_row(moc)))


def test_khong_ngat_qua_90_giay_la_canh_bao():
    filler = "Người ta thường nghĩ rằng mọi chuyện đều đã được sắp đặt sẵn từ trước và mình chẳng thể làm gì khác được nữa."
    rep = LL.lint(_row([filler] * 16))
    assert any(lv == LL.WARN and c == "khong_ngat_nhip" for lv, c, _ in rep["issues"])


def test_vong_mo_khong_dong_khi_plan_co_bang():
    script = ["Vì sao cánh cửa không mở?", "Năm 2027 họ vẫn đứng đó.", "**Chương bốn**", "Đài Loan cắt viện trợ năm ấy."]
    mo = _row(script, vong=[{"mo": "vì sao đứng lại", "dong": "Đài Loan cắt viện trợ"},
                            {"mo": "ai giữ con đường", "dong": ""}])
    msgs = [m for lv, c, m in LL.lint(mo)["issues"] if c == "vong_khong_dong"]
    assert len(msgs) == 1 and msgs[0] and LL.WARN == next(lv for lv, c, _ in LL.lint(mo)["issues"] if c == "vong_khong_dong")
    mat = _row(script, vong=[{"mo": "ai giữ con đường", "dong": "thuế quá cảnh năm nay"}])
    assert "vong_khong_dong" in codes(LL.lint(mat))
    dong = _row(script, vong=[{"mo": "vì sao đứng lại", "dong": "Đài Loan cắt viện trợ"}])
    assert "vong_khong_dong" not in codes(LL.lint(dong))
    assert "vong_khong_dong" not in codes(LL.lint(_row(script)))


def test_fs_ten_con_vat_va_nhieu_chi_la_loi():
    lines = ["Nếu bạn tuổi Chuột thì đừng lo.", "Tý, Sửu, Dần, Mão đều được nhắc."]
    rep = LL.lint(_row(lines, series="fs"))
    errs = {c for lv, c, _ in rep["issues"] if lv == LL.ERROR}
    assert {"ten_con_vat", "nhieu_chi"} <= errs


def test_che_do_dem_nghe_bo_luat_moc():
    lines = ["Video này là một buổi nghe lời Phật dạy trước khi ngủ.", "Hãy thả lỏng đôi vai."] * 40
    c = codes(LL.lint(_row(lines), kind="night"))
    assert not c & {"meta_som", "mo_dau_khong_cu_the", "it_vong_mo", "thieu_rehook", "it_cau_ngan", "chuong_mo_khong_moc"}


def test_cli_strict_va_ban_nhap_txt(tmp_path, capsys):
    ok = tmp_path / "ok.txt"
    ok.write_text("Đêm ấy, một người đàn ông ngồi dưới gốc cây.\n**Chương một**\nÔng ngồi đến sáng.\n", encoding="utf-8")
    assert LL.main([str(ok), "--strict"]) == 0
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([{"id": "x", "script": ["Tuổi Tý gồm 1960, 1972, 1984, 1996 và 2008, còn tuổi Sửu gồm 1961."]},
                               {"id": "y", "script": ["Câu."]}], ensure_ascii=False), encoding="utf-8")
    assert LL.main([str(bad), "--only", "x", "--strict"]) == 1
    out = capsys.readouterr().out
    assert "cau_dai" in out and re.search(r"== x ·", out)
    with pytest.raises(SystemExit):
        LL.main([str(bad)])  # nhiều mục mà không --only


def test_thoi_gian_that_neu_co_segments(tmp_path):
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps([{"id": "z", "script": ["Câu một.", "Câu hai."]}]), encoding="utf-8")
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "z.json").write_text(json.dumps({"segments": [{"start": 0, "end": 2}, {"start": 2.5, "end": 100}]}),
                                             encoding="utf-8")
    rep = LL.lint(LL.load_row(plan, "z"), plan)
    assert rep["stats"]["thời gian"].startswith("giây thật") and rep["stats"]["phút"] == round(100 / 60, 1)


# ---------------------------------------------------------------- khuôn nhân vật (format nhan_vat)


@pytest.mark.parametrize("sent,nums", [
    ("Vì sao ông đi, lời đáp ở chương sáu?", [6]),
    ("Lời đáp ở chương mười hai?", [12]),
    ("Lời đáp ở chương 6?", [6]),
    ("Lời đáp ở chương mười?", [10]),
    ("Lời đáp ở chương hai mươi?", [20]),
    ("Lời đáp ở chương mười lăm?", [15]),
    ("Chương mười hai hay chương 4?", [12, 4]),
    ("Để chương sau mới nói.", []),
    ("Chương II mới kể.", []),
])
def test_doc_so_chuong_trong_cau(sent, nums):
    assert LL.chapter_refs(sent) == nums


def _pad_tokens(lines, target):
    have = sum(LL.tokens(x) for x in lines)
    if have > target:
        raise AssertionError(f"khung đã {have} token, lớn hơn đích {target}")
    if have < target:
        lines.append("đi " * (target - have))
    return lines


def _nv_row(*, n=12, tokens=None, name="Đường Tăng", protagonist="Đường Tăng", cold_has_name=True,
            name_until=None, q_lines=None, questions=None, answers=None, format="nhan_vat"):
    who = name if cold_has_name else "một nhà sư"
    lines = [f"Năm sáu trăm hai mươi bảy, tại Trường An, {who} đứng trước cửa ải."]
    if q_lines is None:
        q_lines = [
            "Vì sao ông một mình đi về phía tây, lời đáp ở chương sáu?",
            "Điều gì khiến ông không quay lại, lời đáp ở chương mười hai?",
        ]
    lines.extend(q_lines)
    if name_until is None:
        name_until = n
    for i in range(1, n + 1):
        lines.append(f"**Chặng {i}**")
        lines.append(f"{name} gặp một bước ngoặt mới." if i <= name_until else "Một người khác giữ việc này.")
    if tokens is not None:
        _pad_tokens(lines, tokens)
    row = {"id": "nv", "script": lines}
    if format is not None:
        row["format"] = format
    if protagonist is not None:
        row["protagonist"] = protagonist
    if format == "nhan_vat":
        if questions is None:
            questions = [{"id": "q1", "chapter": 6}, {"id": "q2", "chapter": 12}]
        if answers is None:
            answers = [{"chapter": 6, "answers": ["q1"]}, {"chapter": 12, "answers": ["q2"]}]
    if questions is not None:
        row["questions"] = questions
    if answers is not None:
        row["answers"] = answers
    return row


def _nv(row):
    return LL.lint(row)["issues"]


def test_nhan_vat_du_khuon_khong_bi_bat():
    row = _nv_row(n=12, tokens=5550)
    assert sum(LL.tokens(x) for x in row["script"]) == 5550
    c = codes(LL.lint(row))
    assert not c & {"CAU_HOI_HEN_CHUONG", "SO_CHUONG", "THOI_LUONG", "NHAN_VAT", "so_chuong"}


def test_nhan_vat_16_chuong_khong_ap_dich_12_14_cu():
    """16 thẻ + cold open = 17 chương theo cách đếm cũ. Đích 12–14 không được bật thêm."""
    row = _nv_row(n=16, tokens=5550)
    c = codes(LL.lint(row))
    assert "SO_CHUONG" not in c and "so_chuong" not in c and "THOI_LUONG" not in c


@pytest.mark.parametrize("n", [11, 17])
def test_so_chuong_ngoai_12_16(n):
    rep = LL.lint(_nv_row(n=n, tokens=5550))
    hit = [(lv, m) for lv, c, m in rep["issues"] if c == "SO_CHUONG"]
    assert len(hit) == 1 and hit[0][0] == LL.WARN and hit[0][1].startswith(f"{n} thẻ")
    # 17 thẻ + cold open nằm ngoài đích 12–14 cũ; mã so_chuong không được bật thêm.
    assert "so_chuong" not in codes(rep)


def test_thoi_luong_dung_30_phut_va_thieu_mot_token():
    du = _nv_row(tokens=5550)
    thieu = _nv_row(tokens=5549)
    assert "THOI_LUONG" not in codes(LL.lint(du))
    hit = [(lv, m) for lv, c, m in _nv(thieu) if c == "THOI_LUONG"]
    assert len(hit) == 1 and hit[0][0] == LL.WARN and hit[0][1].startswith("29:")


def test_cau_hoi_hen_chuong_du_va_thieu():
    assert "CAU_HOI_HEN_CHUONG" not in codes(LL.lint(_nv_row()))
    mot = _nv_row(q_lines=["Vì sao ông đi, lời đáp ở chương sáu?", "Ông vẫn đi."],
                  questions=[{"id": "q1", "chapter": 6}],
                  answers=[{"chapter": 6, "answers": ["q1"]}])
    assert any("có 1 câu hỏi" in m for lv, c, m in _nv(mot) if c == "CAU_HOI_HEN_CHUONG")
    khong_hoi = _nv_row(q_lines=["Lời đáp ở chương sáu sẽ đến sau.", "Lời đáp ở chương mười hai sẽ đến sau."])
    assert any("có 0 câu hỏi" in m for lv, c, m in _nv(khong_hoi) if c == "CAU_HOI_HEN_CHUONG")


def test_cau_hoi_sau_90_giay_khong_tinh():
    first = "Tại Trường An, Đường Tăng đứng trước cửa ải."
    lines = [first, "đi " * (278 - LL.tokens(first))]
    lines += [
        "Vì sao ông đi, lời đáp ở chương sáu?",
        "Vì sao ông không quay lại, lời đáp ở chương mười hai?",
    ]
    for i in range(1, 13):
        lines += [f"**Chặng {i}**", "Đường Tăng gặp một bước ngoặt mới."]
    row = {"id": "nv", "format": "nhan_vat", "protagonist": "Đường Tăng", "script": lines,
           "questions": [{"id": "q1", "chapter": 6}, {"id": "q2", "chapter": 12}],
           "answers": [{"chapter": 6, "answers": ["q1"]}, {"chapter": 12, "answers": ["q2"]}]}
    msgs = [m for lv, c, m in _nv(row) if c == "CAU_HOI_HEN_CHUONG"]
    assert any("có 0 câu hỏi" in m for m in msgs)


def test_chuong_hen_khong_ton_tai_va_thieu_loi_dap():
    mat_chuong = _nv_row(
        q_lines=["Vì sao ông đi, lời đáp ở chương sáu?", "Vì sao ông không về, lời đáp ở chương 99?"],
        questions=[{"id": "q1", "chapter": 6}, {"id": "q2", "chapter": 99}],
        answers=[{"chapter": 6, "answers": ["q1"]}, {"chapter": 99, "answers": ["q2"]}])
    assert any("chương 99" in m and "12 thẻ" in m for lv, c, m in _nv(mat_chuong) if c == "CAU_HOI_HEN_CHUONG")
    thieu_id = _nv_row(questions=[{"id": "q1", "chapter": 6}],
                       answers=[{"chapter": 6, "answers": ["q1"]}])
    assert any("chương 12" in m and "questions" in m for lv, c, m in _nv(thieu_id) if c == "CAU_HOI_HEN_CHUONG")
    thieu_dap = _nv_row(answers=[{"chapter": 6, "answers": ["q1"]}, {"chapter": 12, "answers": []}])
    assert any("q2" in m for lv, c, m in _nv(thieu_dap) if c == "CAU_HOI_HEN_CHUONG")
    sai_chuong = _nv_row(answers=[{"chapter": 7, "answers": ["q1"]}, {"chapter": 12, "answers": ["q2"]}])
    assert any("chương 6" in m and "q1" in m for lv, c, m in _nv(sai_chuong) if c == "CAU_HOI_HEN_CHUONG")


@pytest.mark.parametrize("kwargs,expect", [
    ({"protagonist": None}, "thiếu protagonist"),
    ({"protagonist": "  "}, "thiếu protagonist"),
    ({"cold_has_name": False}, "cold open không có tên"),
    ({"name_until": 8}, "8/12"),
    ({"protagonist": "Duong Tang"}, "cold open không có tên"),
])
def test_nhan_vat_truot(kwargs, expect):
    msgs = [m for lv, c, m in _nv(_nv_row(**kwargs)) if c == "NHAN_VAT"]
    assert msgs and any(expect in m for m in msgs)
    assert all(lv == LL.WARN for lv, c, _ in _nv(_nv_row(**kwargs)) if c == "NHAN_VAT")


def test_nhan_vat_du_70_phan_tram():
    assert "NHAN_VAT" not in codes(LL.lint(_nv_row(n=12, name_until=9)))
    assert "NHAN_VAT" not in codes(LL.lint(_nv_row(n=10, name_until=7)))
    assert "NHAN_VAT" in codes(LL.lint(_nv_row(n=10, name_until=6)))
    assert "NHAN_VAT" not in codes(LL.lint(_nv_row(protagonist="đường tăng")))


def test_khong_format_thi_khong_bat_khuon_nhan_vat():
    row = _nv_row(n=3, format=None, protagonist=None, q_lines=["Ông đi."], questions=None, answers=None)
    assert not codes(LL.lint(row)) & {"CAU_HOI_HEN_CHUONG", "SO_CHUONG", "THOI_LUONG", "NHAN_VAT"}
