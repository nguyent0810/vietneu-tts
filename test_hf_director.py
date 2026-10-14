"""HF Director — test cho các ràng buộc CỨNG và bất biến, không phải cho "gu".

Những gì file này bảo vệ là các quyết định đã chốt qua ba vòng thiết kế:
ràng buộc mật độ (Q10), bất biến trích-nguyên-văn (ADR-0002), quyền của
người duyệt (ADR-0003), và hợp đồng schema (ADR-0004). Việc rule đoán đúng
hay sai "gu" không thuộc phạm vi ở đây.
"""
import json

import pytest

import hf_figure_contract as contract
import hf_director as director


def _entry(lines, **extra):
    return {"id": "test", "script": lines, **extra}


def _run(lines, **kw):
    return director.direct_entry(_entry(lines), **kw)


# --- Ràng buộc cứng (Q10) -------------------------------------------------
def test_cau_cuoi_khong_bao_gio_co_figure():
    out = _run([
        "Câu mở đầu không có gì đặc biệt.",
        "Mốc khởi điểm là hai triệu đồng.",
        "Một câu dẫn dắt bình thường.",
        "Một câu nữa bình thường.",
        "Mốc khởi điểm cũng là năm mươi triệu đồng trở lên.",
    ])
    assert out["figures"]["5"]["type"] == "none"
    assert "câu chốt" in out["figures"]["5"]["reason"].lower()


def test_toi_da_ba_figure():
    out = _run([
        "Mốc khởi điểm là hai triệu đồng.",
        "Vụ án xảy ra năm 1892 và khép lại năm 1923.",
        "Bị cáo chịu mức phạt năm năm.",
        "Ngưỡng tiếp theo là năm mươi triệu đồng trở lên.",
        "Câu chốt không có gì.",
    ])
    n = sum(1 for f in out["figures"].values() if f["type"] != "none")
    assert n <= director.MAX_FIGURES_PER_SHORT


def test_khong_hai_cau_lien_ke_cung_type():
    out = _run([
        "Mốc khởi điểm là hai triệu đồng.",
        "Ngưỡng tiếp theo là năm mươi triệu đồng trở lên.",
        "Một câu bình thường.",
        "Một câu bình thường nữa.",
        "Câu chốt.",
    ])
    types = [out["figures"][str(i)]["type"] for i in range(1, 6)]
    for a, b in zip(types, types[1:]):
        assert not (a == b and a != "none"), f"hai câu liền kề cùng type: {types}"


# --- Bất biến trích nguyên văn (ADR-0002) ---------------------------------
def test_buoc_flow_luon_la_trich_doan_nguyen_van():
    line = "Người bán nhận tiền, rồi chuyển sang ngân hàng khác, dẫn tới mất dấu dòng tiền."
    out = _run(["Câu mở.", line, "Câu ba.", "Câu bốn.", "Câu chốt."])
    fig = out["figures"]["2"]
    if fig["type"] == "flow":
        for step in fig["data"]["steps"]:
            assert director._fold(step["text"]) in director._fold(line)


# --- Sửa tay vẫn được tôn trọng (ADR-0005 giữ lại từ ADR-0003) ------------
def test_khong_ghi_de_quyet_dinh_cua_nguoi():
    lines = ["Mốc khởi điểm là hai triệu đồng.", "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."]
    entry = _entry(lines, figures={"1": {"type": "none", "source": "human", "confidence": 1.0,
                                         "reason": "Người duyệt thấy không cần hình"}})
    out = director.direct_entry(entry)
    assert out["figures"]["1"] == {"type": "none", "source": "human", "confidence": 1.0,
                                   "reason": "Người duyệt thấy không cần hình"}

    forced = director.direct_entry(entry, force=True)
    assert forced["figures"]["1"]["source"] == "rule"


def test_khong_con_truong_needs_human_figure():
    out = _run(["Câu một.", "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."])
    assert "needs_human_figure" not in out


def test_dai_gia_tri_khong_bao_gio_bi_doc_thanh_nguong():
    """Hồi quy cho đúng lỗi khiến ADR-0005 phải thay ADR-0003: nếu lớp lỗi này
    quay lại, nó sẽ ra thẳng kênh vì không còn ai duyệt."""
    cases = [
        "Khung thấp nhất là phạt tiền từ mười đến năm mươi triệu đồng.",
        "Người đó bị phạt tù từ sáu tháng đến ba năm.",
        "Mức phạt dao động từ hai trăm đến năm trăm triệu đồng.",
    ]
    for line in cases:
        out = _run([line, "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."])
        fig = out["figures"]["1"]
        assert fig["type"] in ("range", "none"), f"{line!r} -> {fig['type']}"


def test_dai_gia_tri_doc_dung_hai_dau():
    out = _run(["Khung thấp nhất là phạt tiền từ mười đến năm mươi triệu đồng.",
                "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."])
    data = out["figures"]["1"]["data"]
    assert data["from"] == {"value": 10000000, "unit": "đồng"}
    assert data["to"] == {"value": 50000000, "unit": "đồng"}


def test_dai_khac_don_vi_giu_nguyen_ca_hai():
    out = _run(["Người đó bị phạt tù từ sáu tháng đến ba năm.",
                "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."])
    data = out["figures"]["1"]["data"]
    assert data["from"] == {"value": 6, "unit": "tháng"}
    assert data["to"] == {"value": 3, "unit": "năm"}


def test_nguong_that_van_la_nguong():
    out = _run(["Mốc khởi điểm là tài sản trị giá từ hai triệu đồng trở lên.",
                "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."])
    assert out["figures"]["1"]["type"] == "threshold"


# --- Hợp đồng (ADR-0004) ---------------------------------------------------
@pytest.mark.parametrize("lines", [
    ["Mốc khởi điểm là hai triệu đồng.", "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."],
    ["Vụ án năm 1892 và năm 1923.", "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."],
    ["Câu một.", "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."],
])
def test_output_luon_khop_hop_dong(lines):
    out = _run(lines)
    assert contract.validate({"figures": out["figures"]}) == []


def test_moi_cau_deu_co_figure_tuong_minh():
    """`none` là quyết định, không phải chỗ trống -- nên phải ghi ra."""
    out = _run(["Câu một.", "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."])
    assert sorted(out["figures"], key=int) == ["1", "2", "3", "4", "5"]


# --- Quan hệ liên câu ------------------------------------------------------
def test_cap_contrast_doi_xung_hoac_khong_ton_tai():
    out = _run([
        "Người mua trả tiền, rồi nhận hàng, dẫn tới giao dịch hoàn tất.",
        "Nếu ban đầu là thật, rồi sau đó bỏ trốn, thì chuyển sang tội khác.",
        "Câu ba.", "Câu bốn.", "Câu chốt.",
    ])
    for sid, fig in out["figures"].items():
        rel = fig.get("relation")
        if rel:
            other = out["figures"][str(rel["pairs_with"])]
            assert other["relation"]["pairs_with"] == int(sid), "relation phải đối xứng"
            assert other["type"] != "none", "không ghép cặp với câu đã bị bỏ hình"


def test_cau_co_ca_nguong_lan_dai_thi_lay_cai_dung_truoc():
    """'Mốc khởi điểm cũng là hai triệu đồng, ... tù từ sáu tháng đến ba năm'
    chứa hai sự thật độc lập. Ngưỡng đứng trước nên nó là ý chính."""
    line = ("Mốc khởi điểm cũng là hai triệu đồng, khung thấp nhất là cải tạo không giam giữ "
            "đến ba năm hoặc tù từ sáu tháng đến ba năm.")
    out = _run([line, "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."])
    fig = out["figures"]["1"]
    assert fig["type"] == "threshold"
    assert fig["data"]["value"] == 2000000


def test_so_tien_nam_trong_dai_khong_duoc_thanh_nguong():
    """Chốt chặt bất biến an toàn: '50 triệu' ở đây là một ĐẦU của dải, không
    phải ngưỡng -- dù câu có chữ 'từ' đúng kiểu dấu hiệu ngưỡng."""
    out = _run(["Khung thấp nhất là phạt tiền từ mười đến năm mươi triệu đồng.",
                "Câu hai.", "Câu ba.", "Câu bốn.", "Câu chốt."])
    assert out["figures"]["1"]["type"] == "range"


# --- Lớp lỗi phát hiện khi phủ 02-09/10 (không còn người duyệt để bắt) ------
def _decide(line, series="law"):
    scan = director.scan_script([line])
    return director.rule_decide(scan.sentences[0], scan, series)


def test_mot_la_mao_tu_khong_phai_so_lieu():
    """'một người', 'một vụ', 'một lần' -> KHÔNG được thành stat 1."""
    for line in ["Dùng hình ảnh của một người phải được người đó đồng ý.",
                 "Một vụ ẩu đả nơi công cộng có thể chạm tới hai điều luật.",
                 "Mỗi tháng một lần, hộp thư nhận một lá thư."]:
        assert _decide(line).type == "none", line


def test_manh_ngay_thang_khong_thanh_so_lieu():
    for line in ["Rạng sáng 11 tháng 12 năm 1978, một kho hàng bị cướp.",
                 "Tháng Một năm 1950, nhóm này lấy đi số tiền lớn nhất lịch sử.",
                 "Năm 1906, bản án bị huỷ hoàn toàn."]:
        d = _decide(line)
        assert d.type in ("none", "timeline"), f"{line} -> {d.type} {d.data}"


def test_so_nhieu_chu_doc_dung_gia_tri():
    """'Mười hai năm' phải là 12, không phải 2 (regex cũ chỉ bắt chữ cuối)."""
    d = _decide("Mười hai năm sau, vụ án được lật lại.")
    assert d.type == "stat" and d.data["value"] == 12


def test_lane_truyen_khong_bao_gio_co_figure():
    for line in ["Màn hình đêm đó lặp lại hai người.",
                 "Số đã ngừng hoạt động bốn năm trước.",
                 "Đường hầm dài khoảng mười lăm mét."]:
        assert _decide(line, series="tale").type == "none", line


def test_nguong_khong_chi_danh_cho_tien():
    d = _decide("Khởi điểm của khung cơ bản là tỷ lệ tổn thương từ mười một phần trăm trở lên.")
    assert d.type == "threshold"
    assert d.data == {"value": 11, "unit": "phần trăm", "direction": "at_or_above"}


def test_dau_hieu_nguong_phai_dung_gan_con_so():
    """'ba tấn vàng — nhiều hơn mọi tính toán' KHÔNG phải ngưỡng 'trên 3 tấn'."""
    d = _decide("Thứ họ tìm thấy là ba tấn vàng thỏi — nhiều hơn mọi tính toán ban đầu.", series="case")
    assert d.type == "stat" and d.data == {"value": 3, "unit": "tấn"}


def test_tro_len_dung_sau_con_so_van_la_nguong():
    d = _decide("Tỷ lệ tổn thương từ mười một phần trăm trở lên thì bị truy cứu.")
    assert d.type == "threshold" and d.data["direction"] == "at_or_above"


def test_timeline_gom_moc_nam_tu_nhieu_cau():
    """Mốc năm rải qua nhiều câu vẫn phải thành timeline (backlog #1)."""
    out = _run([
        "Năm 1894, một sĩ quan Pháp bị kết án phản quốc.",
        "Các chuyên gia kết luận nét chữ trên tài liệu mật là của ông.",
        "Mười hai năm sau, năm 1906, bản án bị huỷ hoàn toàn.",
        "Vụ án trở thành ví dụ kinh điển về giám định sai.",
        "Câu chốt.",
    ])
    fig = out["figures"]["3"]
    assert fig["type"] == "timeline"
    assert [p["year"] for p in fig["data"]["points"]] == [1894, 1906]


def test_timeline_khong_ghi_de_figure_da_co():
    out = _run([
        "Năm 1983, nhóm cướp đột nhập một kho hàng.",
        "Câu hai.",
        "Mốc khởi điểm là hai triệu đồng, và năm 1990 vụ án khép lại.",
        "Câu bốn.",
        "Câu chốt.",
    ])
    assert out["figures"]["3"]["type"] == "threshold", "câu đã có figure cụ thể thì giữ nguyên"


def test_lane_truyen_khong_co_timeline():
    out = director.direct_entry(_entry([
        "Tấm bản đồ in năm 1987 có một con đường nhỏ.",
        "Câu hai.",
        "Đến năm 1995 con đường biến mất khỏi mọi bản đồ.",
        "Câu bốn.", "Câu chốt."], series="tale"))
    assert all(f["type"] == "none" for f in out["figures"].values())


def test_timeline_thay_duoc_stat_thoi_gian():
    """'Mười hai năm sau' là cách nói khác của khoảng cách 1894-1906;
    timeline nói đủ hơn nên được phép thay."""
    out = _run([
        "Năm 1894, một sĩ quan Pháp bị kết án phản quốc.",
        "Câu hai bình thường.",
        "Mười hai năm sau, năm 1906, bản án bị huỷ hoàn toàn.",
        "Câu bốn.", "Câu chốt."])
    assert out["figures"]["3"]["type"] == "timeline"


def test_timeline_khong_gan_vao_cau_chot():
    """Gắn vào câu cuối là vứt đi trong im lặng, vì ràng buộc sẽ gỡ nó."""
    out = _run([
        "Năm 1950, nhóm này lấy đi số tiền lớn nhất lịch sử.",
        "Câu hai.", "Câu ba.", "Câu bốn.",
        "Tháng Một năm 1956, cảnh sát bắt được họ."])
    assert out["figures"]["5"]["type"] == "none"
    assert out["figures"]["1"]["type"] == "timeline"
