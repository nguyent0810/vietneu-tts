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


def test_fs_ten_con_vat_va_nhieu_chi_la_loi():
    lines = ["Nếu bạn tuổi Chuột thì đừng lo.", "Tý, Sửu, Dần, Mão đều được nhắc."]
    rep = LL.lint(_row(lines, series="fs"))
    errs = {c for lv, c, _ in rep["issues"] if lv == LL.ERROR}
    assert {"ten_con_vat", "nhieu_chi"} <= errs


def test_che_do_dem_nghe_bo_luat_moc():
    lines = ["Video này là một buổi nghe lời Phật dạy trước khi ngủ.", "Hãy thả lỏng đôi vai."] * 40
    c = codes(LL.lint(_row(lines), kind="night"))
    assert not c & {"meta_som", "mo_dau_khong_cu_the", "it_vong_mo", "thieu_rehook", "it_cau_ngan"}


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
