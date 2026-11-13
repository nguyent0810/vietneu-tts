"""Sinh spec.json + hud/bgm/scenes của từng chNN.json cho CK bài 10 "Mở tài khoản chứng khoán: mất những khoản phí nào?".

    python data/long/ck-c7-mo-tai-khoan-phi/gen_scenes.py     # giữ nguyên "lines" + "title" (do motion/long/script_lines.py ghi)

Kịch bản: script.md (8 chương, 128 câu, 2.571 âm tiết). Dữ kiện: factcheck.md. Phép tính (đã chạy lại bằng Python, ghi ở cuối script.md):
  mua 1.000 cp x 50.000 đ = 50.000.000 đ; phí môi giới GIẢ ĐỊNH 0,15%/chiều = 75.000 đ mỗi chiều, 150.000 đ hai chiều;
  phí Sở ~0,027% x 50.000.000 = 13.500 đ/chiều; thuế GIẢ ĐỊNH 0,1% = 50.000 đ (bán 45 triệu: 45.000 đ);
  lưu ký 0,27 đ x 1.000 cp = 270 đ/tháng, 3.240 đ/năm (~2% của 150.000 đ); ứng trước GIẢ ĐỊNH 12%/năm, 2 ngày ≈ 33.000 đ (0,066%);
  phiếu hòa vốn: chi 50.075.000 đ; bán đúng giá còn 49.875.000 đ, thiếu 200.000 đ (0,4%); hòa vốn ≈ 50.200 đ (+0,401%);
  phí 0,25%: ≈ 50.300 đ (+0,602%); phí Sở hai chiều 0,054%; mười vòng giữ nguyên giá còn ≈ 48,04 triệu đồng.
Luật kênh: chỉ giáo dục; chị Hạnh và mọi con số của chị là VÍ DỤ GIẢ ĐỊNH (nhãn trên màn hình ở mọi cảnh có số của chị);
thuế 0,1% hiện rõ là GIẢ ĐỊNH; không tên công ty chứng khoán, ngân hàng, ứng dụng hay mã cổ phiếu trên màn hình.
Ghi file: UTF-8 (Codex làm hỏng dấu tiếng Việt khi ghi bằng PowerShell, nên script này ghi bằng Path.write_text(encoding="utf-8")).
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent
HYP = "VÍ DỤ GIẢ ĐỊNH"
HYPS = "VÍ DỤ GIẢ ĐỊNH · CHỊ HẠNH LÀ NHÂN VẬT GIẢ ĐỊNH"
ILL = "ẢNH MINH HỌA"
VM = "VIDEO MINH HỌA"
TAXG = "GIẢ ĐỊNH · THUẾ 0,1% TRÊN GIÁ TRỊ BÁN · CHƯA XÁC NHẬN NGUYÊN VĂN ĐIỀU KHOẢN"


# ---------------- helper mốc neo ----------------
def O(at, x):
    """Mốc cách mốc `at` của cảnh x giây (để phần tử con thứ hai hiện trong 1 giây đầu cảnh)."""
    if isinstance(at, int):
        return [at, None, 0, x]
    i, w = at[0], at[1]
    n = at[2] if len(at) > 2 else 0
    if w is None:
        return [i, None, 0, (at[3] if len(at) > 3 else 0.0) + x]
    return [i, w, n, x]


def W(i, w, n=0):
    return [i, w, n]


# ---------------- helper cảnh ----------------
def kin(*items):
    """("CHỮ", mốc, cờ?) — cờ: acc | sm."""
    out = []
    for t, a, *f in items:
        e = {"text": t, "at": a}
        for x in f:
            e[x] = True
        out.append(e)
    return out


def hyp(s, text=HYP):
    """Nhãn VÍ DỤ GIẢ ĐỊNH: biểu đồ/sổ ghi ở srcnote (góc dưới phải), cảnh ảnh/chữ ghi ở tag (thẻ trên trái)."""
    if s["type"] in ("bars", "ledger", "counter", "units", "timeline", "source", "split", "stack", "waterfall", "myth", "date"):
        s["srcnote"] = text
    else:
        s["tag"] = text
    return s


def chap(no, k, title, sub, word, bg):
    return {"type": "chapter", "no": no, "k": k, "title": title, "sub": sub, "titleAt": [0, word], "bg": bg, "illus": ILL}


def broll(at, vid, items, ms=None, tag=None):
    s = {"type": "broll", "at": at, "vid": vid, "loop": True, "veil": 0.56, "illus": VM, "kin": kin(*items)}
    if ms is not None:
        s["ms"] = ms
    if tag:
        s["tag"] = tag
    return s


def photo(at, img, items=None, focus=None, ai=True, tag=None):
    s = {"type": "photo", "at": at, "img": img, "illus": ILL}
    if ai:
        s["credit"] = False
    if focus:
        s["focus"] = focus
    if items:
        s["veil"] = 0.52
        s["kin"] = kin(*items)
    if tag:
        s["tag"] = tag
    return s


def kinetic(at, bg, items, tag=None):
    s = {"type": "kinetic", "at": at, "bg": bg, "items": kin(*items)}
    if tag:
        s["tag"] = tag
    return s


def slam(at, bg, text, sub, hit=None, tag=None):
    s = {"type": "slam", "at": at, "bg": bg, "text": text, "sub": sub}
    if hit is not None:
        s["hitAt"] = hit
    if tag:
        s["tag"] = tag
    return s


def question(at, bg, text, show=None, tag=None):
    s = {"type": "question", "at": at, "text": text}
    s["vid" if bg.startswith("9000") else "bg"] = bg
    if show is not None:
        s["showAt"] = show
    if tag:
        s["tag"] = tag
    return s


def ledger(at, title, rows, total=None, bg=None, src=None):
    s = {"type": "ledger", "at": at, "title": title, "rows": [{"k": k, "v": v, "at": a} for k, v, a in rows]}
    if total:
        s["total"] = {"k": total[0], "v": total[1], "at": total[2]}
    if bg:
        s["bg"] = bg
    if src:
        s["srcnote"] = src
    return s


def bars(at, title, unit, items, src=None, bg=None):
    s = {"type": "bars", "at": at, "title": title, "unit": unit,
         "items": [{"k": k, "v": v, "lbl": l, "at": a, **({"acc": True} if acc else {})} for k, v, l, a, acc in items]}
    if src:
        s["srcnote"] = src
    if bg:
        s["bg"] = bg
    return s


def counter(at, to, label, bg, frm=0, prefix="", suffix="", sub=None, dec=None, src=None):
    s = {"type": "counter", "at": at, "from": frm, "to": to, "label": label, "bg": bg}
    if prefix:
        s["prefix"] = prefix
    if suffix:
        s["suffix"] = suffix
    if sub:
        s["sub"] = {"text": sub[0], "at": sub[1]}
    if src:
        s["srcnote"] = src
    return s


def timeline(at, title, items, src=None, bg=None):
    s = {"type": "timeline", "at": at, "items": [{"year": y, "text": t, "at": a} for y, t, a in items]}
    if title:
        s["title"] = title
    if src:
        s["srcnote"] = src
    if bg:
        s["bg"] = bg
    return s


def units(at, title, total, lit, lit_at, label, bg, cols=None):
    s = {"type": "units", "at": at, "title": title, "total": total, "lit": lit, "litAt": lit_at, "unitLabel": label, "bg": bg}
    if cols:
        s["cols"] = cols
    return s


def myth(at, bg, mythlab, m, truthlab, truth, strike, truth_at):
    return {"type": "myth", "at": at, "bg": bg, "mythLab": mythlab, "myth": m, "truthLab": truthlab, "truth": truth, "strikeAt": strike, "truthAt": truth_at}


def source(at, bg, src, ref, snippet, hl, seal, seal_at):
    return {"type": "source", "at": at, "bg": bg, "source": src, "ref": ref, "snippet": snippet, "hlAt": hl, "seal": seal, "sealAt": seal_at}


def date(at, bg, day, dt):
    return {"type": "date", "at": at, "bg": bg, "day": day, "date": dt}


def split(at, title, a, b, sign):
    """a, b: (img, nhãn, mốc)"""
    return {"type": "split", "at": at, "title": title, "a": {"img": a[0], "label": a[1], "at": a[2]}, "b": {"img": b[0], "label": b[1], "at": b[2]}, "sign": sign, "signAt": O(at, 1.1)}


def card(at, style, name, desc, rows, img=None, total=None):
    r = [{"k": k, "v": v, "at": a} for k, v, a in rows]
    if total:
        r.append({"k": total[0], "v": total[1], "at": total[2], "total": True})
    s = {"type": "file", "at": at, "style": style, "name": name, "desc": desc, "rows": r}
    if img:
        s["img"] = img
    return s


def stack(at, title, keys, groups, calls):
    return {"type": "stack", "at": at, "title": title, "range": "NGHÌN ĐỒNG · " + HYP, "unit": "NGHÌN Đ", "keys": [{"k": k} for k in keys],
            "groups": [{"k": k, "vals": v, "at": a} for k, v, a in groups],
            "calls": [{"i": i, "text": t, "at": a} for i, t, a in calls]}


def waterfall(at, title, start, steps, end, calls=()):
    return {"type": "waterfall", "at": at, "title": title, "range": "NGHÌN ĐỒNG · " + HYP, "unit": "NGHÌN Đ",
            "start": {"k": start[0], "v": start[1], "at": start[2]},
            "steps": [{"k": k, "v": v, "at": a} for k, v, a in steps],
            "end": {"k": end[0], "at": end[1], **({"tone": end[2]} if len(end) > 2 else {})},
            "calls": [{"i": i, "text": t, "at": a} for i, t, a in calls]}


# ---------------- ảnh ----------------
IMGS = {f"ai{i:02d}": f"EXT:ai:ai_{i:02d}" for i in range(1, 17)}
IMGS.update({
    "hose1": "File:HOSE.JPG",
    "hose2": "File:Hochiminh Stock Exchange.png",
    "hose3": "File:Ho Chi Minh stock exchange.jpg",
    "hose4": "File:Streets and buildings in district 1 Saigon 3.jpg",
    "hnx": "File:Hanoi Stock Exchange (18780216822).jpg",
    "sky1": "File:Ho Chi Minh City Skyline.jpg",
    "sky2": "File:Ho Chi Minh City Skyline at Night.jpg",
    "sky3": "File:Ho Chi Minh City during sunset (50332857462).jpg",
    "vault1": "File:Bank vault at Porecelanosa jeh.jpg",
    "vault2": "File:NTS - Bank Vault - after 2.jpg",
    "vault3": "File:Four Corners Bank Vault.jpg",
    "hn1": "File:Yên Lãng Street, Hanoi 01.jpg",
    "hn2": "File:Hoàng Cầu Street, Hanoi 04.jpg",
    "hn3": "File:Street in Hanoi, Vietnam-1.png",
    "hn4": "File:Yên Lãng Street, Hanoi 03.jpg",
    "hn5": "File:Hoàng Cầu Street, Hanoi 11.jpg",
    "hn6": "File:Street in Hanoi, Vietnam-2.png",
    "sky4": "File:Ho Chi Minh City, Nguyen Hue Street, 2020-01 CN-02.jpg",
})

CH = {}

# ======================= CH00 · cold open =======================
CH["ch00"] = {"hud": {"k": "MỞ ĐẦU", "t": "HƠN 252 NGHÌN LẦN CHẠM MÀN HÌNH"}, "bgm": {"mood": "curious", "gain": 0.10}, "scenes": [
    {**date(0, "hose2", "NHÀ ĐẦU TƯ TRONG NƯỚC MỞ THÊM TRONG THÁNG", "10.2026"), "vid": "900003"},   # cổng mở đầu: hình/clip trong 5s đầu (Lead 13/11)
    counter(W(0, "mở"), 252000, "TÀI KHOẢN CHỨNG KHOÁN MỞ MỚI · THÁNG 10/2026", "ai01", prefix="HƠN ", src="NHÀ ĐẦU TƯ TRONG NƯỚC · THEO BÁO CHÍ 11/2026"),
    date(1, "sky1", "TÍNH ĐẾN NGÀY", "31.10.2026"),
    counter(W(1, "mười", 1), 14384902, "TÀI KHOẢN TRÊN TOÀN THỊ TRƯỜNG · DỮ LIỆU LƯU KÝ", "sky2", src="THEO BÁO CHÍ 05/11/2026"),
    question(2, "ai13", "Khi nạp tiền để giao dịch,\ntiền của bạn sẽ đi đâu?"),
    broll(3, "900002", [("CHỊ HẠNH", [3, "chị"], "acc"), ("vừa mở tài khoản · chuẩn bị nạp tiền", [3, "người"], "sm")], tag=HYP),
    hyp(counter(4, 50, "CHỊ HẠNH NẠP · NHÂN VẬT VÀ CON SỐ ĐỀU GIẢ ĐỊNH", "ai04", suffix=" TRIỆU Đ"), HYPS),
    slam(5, "ai15", "VÍ DỤ GIẢ ĐỊNH", "NHÃN NÀY HIỆN Ở MỌI CẢNH CÓ SỐ CỦA CHỊ HẠNH", hit=[5, "nhãn"]),
    photo(6, "ai16", [("NẠP TIỀN TỪ NGÂN HÀNG", [6, "nạp"], "acc"), ("số dư hiện lên", [6, "số"], "sm")], tag=HYP),
    ledger(7, "HAI CÂU HỎI SAU CON SỐ ĐÓ", [("1", "TIỀN ĐƯỢC GIỮ Ở ĐÂU?", O(7, 0.2)), ("2", "MỘT VÒNG MUA RỒI BÁN PHÁT SINH KHOẢN NÀO?", O(7, 0.8))],
           src="CHỊ HẠNH LÀ NHÂN VẬT GIẢ ĐỊNH"),
    broll(8, "900003", [("HAI TẤM BẢN ĐỒ", [8, "hai"], "acc"), ("một con đường · một tờ hóa đơn", [9, "theo"], "sm")]),
    hyp(timeline(W(9, "ngân"), "BẢN ĐỒ 1 · ĐƯỜNG TIỀN", [("1", "NGÂN HÀNG", O(W(9, "ngân"), 0.1)), ("2", "NƠI GIỮ TIỀN GIAO DỊCH", W(9, "qua")),
                                                        ("3", "LỆNH MUA BÁN", W(9, "lệnh")), ("4", "TIỀN BÁN VỀ SAU T+2", W(9, "T"))])),
    hyp(ledger(10, "BẢN ĐỒ 2 · TỜ HÓA ĐƠN BỐN DÒNG", [("1", "PHÍ MÔI GIỚI", O(10, 0.2)), ("2", "THUẾ", O(10, 0.8)),
                                                               ("3", "PHÍ LƯU KÝ", W(10, "lưu")), ("4", "PHÍ ỨNG TRƯỚC", W(10, "ứng"))])),
    card(11, "receipt", "TỜ PHIẾU CỦA CHỊ HẠNH", HYP + " · TÍNH Ở CUỐI VIDEO",
         [("PHÍ MÔI GIỚI", "?", O(11, 0.3)), ("THUẾ", "?", O(11, 0.8)), ("PHÍ LƯU KÝ", "?", W(11, "đặt")), ("PHÍ ỨNG TRƯỚC", "?", W(11, "cùng"))],
         total=("TỔNG · GIÁ HÒA VỐN", "= ?", W(11, "tính"))),
    {"type": "brand", "at": 12, "name": "BIỂU ĐỒ BIẾT NÓI", "sub": "TIỀN BẠC · GIẢI THÍCH BẰNG DỮ LIỆU"},
    question(13, "900006", "Tiền của chị\nđang nằm trong tay ai?"),
]}

# ======================= CH01 · tiền nằm ở đâu =======================
CH["ch01"] = {"hud": {"k": "CHẶNG 01", "t": "TIỀN CỦA CHỊ NẰM Ở ĐÂU"}, "bgm": {"mood": "calm", "gain": 0.11}, "scenes": [
    chap("1", "CHẶNG MỘT", "TIỀN CỦA CHỊ\nNẰM Ở ĐÂU", "QUY ĐỊNH VỀ TIỀN GIAO DỊCH", "tiền", "ai02"),
    photo(1, "hose4", [("QUY ĐỊNH VỀ TIỀN KHÁCH HÀNG", [1, "quy"], "acc"), ("điểm bắt đầu để lần theo", [1, "điểm"], "sm")], ai=False),
    source(2, "ai12", "BỘ TÀI CHÍNH · THÔNG TƯ 121/2020/TT-BTC", "QUẢN LÝ TIỀN CỦA KHÁCH HÀNG", "Bộ Tài chính quy định việc [[quản lý tiền của khách hàng]]",
           [2, "quản"], "THÔNG TƯ 121/2020", [2, "tiền"]),
    kinetic(3, "ai03", [("TIỀN GIAO DỊCH CỦA TỪNG NGƯỜI", 3, "sm"), ("QUẢN LÝ TÁCH BẠCH", [3, "quản"], "acc")]),
    ledger(4, "CÔNG TY KHÔNG ĐƯỢC", [("1", "TRỰC TIẾP NHẬN, CHI TIỀN MẶT", O(4, 0.2)), ("2", "ĐỂ GIAO DỊCH CHỨNG KHOÁN CỦA KHÁCH", O(4, 0.8))]),
    photo(W(4, "cũng"), "vault2", [("KHÔNG LẠM DỤNG TIỀN KHÁCH", [4, "cũng"], "acc"), ("dưới mọi hình thức", [4, "dưới"], "sm")], ai=False),
    kinetic(5, "ai16", [("TIỀN ĐƯỢC GIỮ Ở NGÂN HÀNG", 5, "sm"), ("MỘT TRONG HAI CÁCH", [5, "một"], "acc")]),
    photo(6, "vault1", [("CÁCH MỘT", [6, "khách"], "acc"), ("khách mở tài khoản trực tiếp tại ngân hàng", [6, "mở"], "sm")], ai=False),
    card(7, "lower_third", "CÁCH HAI", "TÀI KHOẢN CHUYÊN DỤNG CỦA CÔNG TY",
         [("TÀI KHOẢN", "RIÊNG BIỆT", O(7, 0.3)), ("VỚI TÀI KHOẢN CỦA CHÍNH CÔNG TY", "TÁCH BẠCH", O(7, 0.8))], img="ai10"),
    hyp(timeline(8, "ĐƯỜNG ĐI CỦA TIỀN CHỊ HẠNH", [("1", "TÀI KHOẢN NGÂN HÀNG", O(8, 0.1)), ("2", "NƠI GIỮ TIỀN GIAO DỊCH", O(8, 0.8)),
                                                           ("3", "CHỜ LỆNH MUA", W(8, "chờ"))])),
    question(9, "ai02", "Tiền ấy\nthuộc về ai?"),
    source(10, "ai03", "LUẬT CHỨNG KHOÁN 2019 · ĐIỀU 88", "QUẢN LÝ TÀI SẢN CỦA KHÁCH HÀNG", "tiền gửi giao dịch chứng khoán là [[tài sản thuộc quyền sở hữu của khách hàng]]",
           [10, "nêu"], "ĐIỀU 88", [10, "tiền"]),
    kinetic(W(10, "nêu"), "ai10", [("TIỀN GỬI GIAO DỊCH", [10, "tiền"], "sm"), ("THUỘC QUYỀN SỞ HỮU CỦA KHÁCH HÀNG", [10, "thuộc"], "acc")]),
    myth(W(10, "không", 1), "vault3", "KHÔNG PHẢI", "TÀI SẢN CỦA CÔNG TY CHỨNG KHOÁN", "MÀ LÀ", "TÀI SẢN CỦA KHÁCH HÀNG", [10, "phải"], [10, "chứng", 1]),
    ledger(11, "QUY ĐỊNH NÀY CHƯA TRẢ LỜI", [("QUYỀN SỞ HỮU", "THUỘC KHÁCH HÀNG · TÁCH BẠCH", O(11, 0.2)), ("KHI CÔNG TY GẶP SỰ CỐ NGHIÊM TRỌNG", "VIDEO KHÔNG KẾT LUẬN", O(11, 0.8))],
           bg="ai03"),
    photo(12, "ai16", [("ĐIỀU TA VỪA XÁC ĐỊNH", 12, "sm"), ("TIỀN GIAO DỊCH THUỘC KHÁCH HÀNG", [12, "tiền"], "acc")]),
    broll(13, "900005", [("CHỊ HẠNH BẤM MUA", [13, "chị"], "acc"), ("trạm thu đầu tiên bật sáng", [14, "trạm"], "sm")], tag=HYP),
]}

# ======================= CH02 · phí môi giới =======================
CH["ch02"] = {"hud": {"k": "DÒNG 01", "t": "PHÍ MÔI GIỚI"}, "bgm": {"mood": "curious", "gain": 0.11}, "scenes": [
    chap("2", "DÒNG MỘT", "PHÍ MÔI GIỚI", "DÒNG ĐẦU CỦA TỜ HÓA ĐƠN", "mua", "ai05"),
    hyp(counter(W(0, "công"), 1000, "CỔ PHIẾU CỦA CÔNG TY HƯ CẤU · GIÁ 50.000 Đ MỖI CỔ PHIẾU", "sky3", suffix=" CỔ PHIẾU"), HYPS),
    hyp(ledger(1, "LỆNH MUA CỦA CHỊ HẠNH", [("1.000 CỔ PHIẾU × 50.000 Đ", "= 50.000.000 Đ", O(1, 0.2)), ("PHÍ MUA", "CHƯA TÍNH · CẦN DỰ TRÙ", O(1, 0.8))])),
    photo(2, "ai05", [("DÒNG 1 · PHÍ MÔI GIỚI", [2, "dòng"], "acc"), ("phí tính lúc chị mua", [3, "phí"], "sm")], tag=HYP),
    hyp(units(W(3, "lúc"), "HAI CHIỀU TÍNH PHÍ · " + HYP, 2, 2, [3, "thêm"], "CHIỀU: MUA VÀ BÁN", "ai14", cols=2)),
    source(4, "ai12", "THÔNG TƯ 102/2021/TT-BTC", "KHUNG GIÁ DỊCH VỤ CHỨNG KHOÁN", "từng có một [[thông tư đặt khung giá]] cho dịch vụ này", [4, "thông"], "ĐÃ BỊ BÃI BỎ", [5, "bãi"]),
    timeline(5, "THÔNG TƯ 102/2021 ĐÃ KHÔNG CÒN", [("2021", "TT 102/2021 · KHUNG GIÁ", O(5, 0.1)), ("TT 42/2025", "BÃI BỎ NÓ", O(5, 0.8))],
             src="THEO NGUỒN ĐÃ XEM · 06/2025"),
    date(W(5, "từ"), "ai12", "BÃI BỎ TỪ NGÀY", "02.08.2025"),
    myth(6, "ai08", "KHÔNG THỂ", "LẤY MỨC TRẦN THÔNG TƯ CŨ LÀM MỨC HIỆN NAY", "VÌ NÓ ĐÃ", "BỊ BÃI BỎ", [6, "lấy"], [6, "khẳng"]),
    kinetic(7, "hn1", [("TỪNG CÔNG TY", 7, "sm"), ("TỰ QUY ĐỊNH MỨC PHÍ", [7, "tự"], "acc")]),
    photo(8, "ai15", [("BIỂU PHÍ CÓ THỂ KHÁC NHAU", [8, "biểu"], "acc"), ("xem biểu phí nơi mình chọn", [8, "nên"], "sm")]),
    hyp(counter(9, 0.15, "PHÍ MÔI GIỚI GIẢ ĐỊNH · MỖI CHIỀU", "hose1", suffix="%"), HYPS),
    slam(10, "vault2", "KHÔNG PHẢI MỨC PHỔ BIẾN", "CŨNG KHÔNG PHẢI MỨC ĐỀ XUẤT", hit=[10, "không"], tag=HYP),
    hyp(counter(11, 75, "PHÍ MUA · 0,15% × 50 TRIỆU", "hose3", suffix=" NGHÌN Đ")),
    stack(12, "PHÍ MÔI GIỚI HAI CHIỀU (NGHÌN ĐỒNG)", ["PHÍ MUA", "PHÍ BÁN"], [("HAI CHIỀU", [75, 75], O(12, 0.2))], [(0, "TỔNG 150 NGHÌN Đ", W(12, "tổng"))]),
    hyp(ledger(13, "HAI CHIỀU · GIÁ TRỊ MUA VÀ BÁN BẰNG NHAU", [("MUA 50 TRIỆU", "PHÍ 75.000 Đ", O(13, 0.2)), ("BÁN 50 TRIỆU", "PHÍ 75.000 Đ", O(13, 0.8))],
               total=("HAI CHIỀU", "150.000 Đ", W(13, "một")))),
    photo(14, "ai08", [("TĂNG · GIẢM · ĐỨNG YÊN", [14, "dù"], "acc"), ("phí vẫn có trong phép tính", 14, "sm")], tag=HYP),
    question(15, "ai14", "“Miễn phí giao dịch”\ncó nghĩa là về không?"),
]}

# ======================= CH03 · hai chữ miễn phí =======================
CH["ch03"] = {"hud": {"k": "CHẶNG PHỤ", "t": "HAI CHỮ MIỄN PHÍ"}, "bgm": {"mood": "calm", "gain": 0.11}, "scenes": [
    chap("3", "CHẶNG BA", "HAI CHỮ\nMIỄN PHÍ", "“MIỄN PHÍ GIAO DỊCH” LÀ MIỄN GÌ?", "miễn", "hose1"),
    myth(1, "hnx", "NGHE CÓ VẺ", "MIỄN PHÍ MÔI GIỚI = MIỄN MỌI KHOẢN", "NHƯNG VẪN CẦN", "XEM CÁC KHOẢN KHÁC ĐI KÈM", [1, "bạn"], [1, "xem"]),
    photo(2, "hnx", [("MỘT LỆNH KHỚP", [2, "một"], "acc"), ("còn đi qua Sở giao dịch · biểu giá dịch vụ riêng", [2, "nơi"], "sm")], ai=False),
    source(3, "ai07", "QUYẾT ĐỊNH 1541/QĐ-BTC · 29/04/2025", "GIÁ DỊCH VỤ TẠI SỞ HÀ NỘI", "mức khoảng [[0,027% giá trị giao dịch]] cổ phiếu", [3, "khoảng"], "THEO NGUỒN ĐÃ XEM", [3, "giá"]),
    counter(W(3, "có"), 0.027, "KHOẢNG · GIÁ TRỊ GIAO DỊCH CỔ PHIẾU TẠI SỞ HÀ NỘI", "hose4", suffix="%"),
    kinetic(4, "ai07", [("KHOẢN DỊCH VỤ ẤY", 4, "sm"), ("DO SỞ THU TỪ CÔNG TY CHỨNG KHOÁN", [4, "do"], "acc")]),
    ledger(5, "BIỂU PHÍ KHÁCH HÀNG", [("GỘP HAY TÁCH KHOẢN NÀY?", "XEM TẠI NƠI MÌNH CHỌN", O(5, 0.2)), ("ĐỂ TRÁNH", "TÍNH HAI LẦN", O(5, 0.8))], bg="hose2"),
    hyp(timeline(6, "PHÉP NHÂN GIẢ ĐỊNH · MỖI CHIỀU", [("1", "TIỀN GIAO DỊCH 50.000.000 Đ", O(6, 0.1)), ("2", "× 0,027%", O(6, 0.8)), ("3", "= 13.500 Đ MỖI CHIỀU", W(6, "mười"))])),
    hyp(myth(7, "hn5", "PHÉP NHÂN NÀY", "= KHOẢN CHỊ HẠNH PHẢI TRẢ RIÊNG", "THỰC RA", "CHƯA BIẾT CÓ TRẢ RIÊNG HAY KHÔNG", [7, "chưa"], [7, "hoặc"])),
    question(8, "ai04", "Tổng tiền bị trừ\ncho cả mua lẫn bán là bao nhiêu?"),
    photo(9, "ai15", [("KHOẢN NÀO ĐÃ GỘP", [9, "khoản"], "acc"), ("khoản nào còn tính riêng", [9, "khoản", 1], "sm")]),
    broll(10, "900002", [("MỤC PHÍ KHÁC", [10, "mục"], "acc"), ("đọc từng dòng một", [10, "đọc"], "sm")]),
    hyp(units(11, "TỜ HÓA ĐƠN CỦA CHỊ HẠNH · " + HYP, 4, 1, [11, "một"], "DÒNG ĐÃ CÓ SỐ · DÒNG THỨ HAI LÀ THUẾ", "sky4")),
]}

# ======================= CH04 · thuế khi bán =======================
CH["ch04"] = {"hud": {"k": "DÒNG 02", "t": "THUẾ KHI BÁN"}, "bgm": {"mood": "mystery", "gain": 0.11}, "scenes": [
    chap("4", "DÒNG HAI", "THUẾ KHI BÁN", "GIẢ ĐỊNH 0,1% TRÊN GIÁ TRỊ BÁN", "thuế", "ai12"),
    ledger(1, "CÁCH TÍNH GIẢ ĐỊNH", [("THUẾ TÍNH TRÊN", "GIÁ TRỊ CỦA LẦN BÁN", O(1, 0.2)), ("KHÔNG PHẢI", "CHỈ TRÊN PHẦN LÃI", O(1, 0.8))], src=TAXG),
    date(2, "ai11", "LUẬT THUẾ TNCN CÓ HIỆU LỰC TỪ", "01.07.2026"),
    source(W(2, "luật"), "sky1", "LUẬT THUẾ THU NHẬP CÁ NHÂN 109/2025/QH15", "HIỆU LỰC TỪ 01/07/2026", "Luật số 109 năm 2025 [[bắt đầu có hiệu lực]] từ ngày 01/07/2026",
           [2, "bắt"], "NGUỒN ĐÃ XEM", [2, "hiệu"]),
    kinetic(3, "hn5", [("NGHỊ ĐỊNH 253/2026/NĐ-CP", 3, "acc"), ("hướng dẫn thi hành Luật Thuế thu nhập cá nhân", [3, "nghị"], "sm")]),
    ledger(W(3, "thông"), "CÙNG CÓ HIỆU LỰC", [("THÔNG TƯ 87/2026/TT-BTC", "HƯỚNG DẪN THI HÀNH", O(W(3, "thông"), 0.2)), ("NGHỊ ĐỊNH 253/2026/NĐ-CP", "HƯỚNG DẪN THI HÀNH", O(W(3, "thông"), 0.8))],
           total=("NGÀY HIỆU LỰC", "01/07/2026", W(3, "cùng"))),
    timeline(4, "GIAI ĐOẠN DỰ THẢO · 2025", [("2025", "giai đoạn dự thảo", O(4, 0.1)), ("RÚT", "đề xuất thu 20% trên phần lãi", O(4, 0.8)), ("BỘ TÀI CHÍNH", "không giữ đề xuất ấy", W(4, "rút"))],
             src="THEO BÁO CHÍ 09/2025", bg="sky2"),
    source(5, "ai12", "CỤC THUẾ · NHẬN XÉT 11/2025", "0,1% TRÊN GIÁ TRỊ CHUYỂN NHƯỢNG", "được xem là [[phương án thu thuận tiện]]", [5, "phương"], "NHẬN XÉT, CHƯA PHẢI ĐIỀU KHOẢN", [5, "nhưng"]),
    myth(W(5, "nhưng"), "ai02", "Ý KIẾN CỦA CƠ QUAN THUẾ", "= ĐIỀU KHOẢN HIỆN HÀNH", "THỰC RA", "CHƯA THAY CHO ĐIỀU KHOẢN HIỆN HÀNH", [5, "chưa"], [5, "điều"]),
    slam(6, "ai02", "CHƯA XÁC NHẬN ĐƯỢC", "NGUYÊN VĂN ĐIỀU KHOẢN VỀ MỨC THUẾ NÀY CHO CỔ PHIẾU NIÊM YẾT", hit=[6, "chưa"]),
    hyp(counter(7, 0.1, "THUẾ GIẢ ĐỊNH · TRÊN GIÁ TRỊ BÁN · KHÔNG PHẢI MỨC ĐÃ XÁC NHẬN", "hose2", suffix="%"), TAXG),
    card(8, "callout", "ĐỐI CHIẾU TRƯỚC KHI BÁN", "QUY ĐỊNH HIỆN HÀNH VÀ BIỂU THUẾ PHÍ CỦA BẠN",
         [("1", "QUY ĐỊNH HIỆN HÀNH", O(8, 0.3)), ("2", "BIỂU THUẾ PHÍ ÁP DỤNG CHO MÌNH", O(8, 0.8))], img="hose3"),
    hyp(ledger(9, "THUẾ GIẢ ĐỊNH 0,1% · CHỊ HẠNH BÁN 50 TRIỆU", [("GIÁ TRỊ BÁN", "50.000.000 Đ", O(9, 0.2)), ("THUẾ GIẢ ĐỊNH 0,1%", "50.000 Đ", O(9, 0.8))]), TAXG),
    hyp(bars(10, "THUẾ GIẢ ĐỊNH 0,1% TRÊN GIÁ TRỊ BÁN (NGHÌN Đ)", "GIẢ ĐỊNH · " + HYP,
             [("BÁN 50 TRIỆU", 50, "50", [10, "nếu"], False), ("BÁN 45 TRIỆU", 45, "45", [10, "bốn"], True)], src=TAXG), TAXG),
    slam(11, "hn2", "BÁN LỖ VẪN CÓ THUẾ", "TRONG CÁCH TÍNH GIẢ ĐỊNH TRÊN GIÁ TRỊ BÁN", hit=[11, "ngay"], tag="GIẢ ĐỊNH · CÁCH TÍNH TRÊN GIÁ TRỊ BÁN"),
    hyp(units(12, "THUẾ GIẢ ĐỊNH CHỈ Ở CHIỀU BÁN · " + HYP, 2, 1, [12, "ta"], "CHIỀU CÓ THUẾ TRÊN TỜ PHIẾU", "ai05", cols=2), TAXG),
    hyp(ledger(13, "TỜ HÓA ĐƠN CỦA CHỊ HẠNH · HAI DÒNG ĐẦU", [("DÒNG 1 · PHÍ MÔI GIỚI", "150.000 Đ", O(13, 0.2)), ("DÒNG 2 · THUẾ GIẢ ĐỊNH", "50.000 Đ", O(13, 0.8))],
               total=("CÒN LẠI", "HAI DÒNG NỮA", W(14, "còn")))),
    hyp(split(W(14, "và"), "HAI DÒNG CÒN LẠI KHÁC NHAU VỀ TÍNH CHẤT", ("ai08", "NHỎ ĐẾN MỨC KHÓ THẤY", O(W(14, "và"), 0.2)), ("ai13", "CHỈ XUẤT HIỆN KHI SỐT RUỘT", O(W(14, "và"), 0.9)), "≠")),
]}

# ======================= CH05 · phí lưu ký =======================
CH["ch05"] = {"hud": {"k": "DÒNG 03", "t": "PHÍ LƯU KÝ"}, "bgm": {"mood": "calm", "gain": 0.11}, "scenes": [
    chap("5", "DÒNG BA", "PHÍ LƯU KÝ", "MƯỜI HAI THÁNG GIỮ CỔ PHIẾU", "phí", "ai09"),
    source(1, "ai03", "QUYẾT ĐỊNH 1541/QĐ-BTC · 29/04/2025", "PHÍ LƯU KÝ HẰNG THÁNG", "[[0,27 đồng]] trên mỗi đơn vị chứng khoán", [1, "không"], "THEO NGUỒN ĐÃ XEM", [1, "cho"]),
    kinetic(2, "sky1", [("THÔNG TƯ 83/2024", 2, "acc"), ("thay thế thông tư trước đó", [2, "đã"], "sm")]),
    date(W(2, "từ"), "ai11", "THAY THẾ TỪ NGÀY", "10.01.2025"),
    broll(3, "900004", [("QUY ĐỊNH CHUYỂN TIẾP 2026", [3, "quy"], "acc"), ("theo nguồn đã xem", 3, "sm")]),
    ledger(W(3, "tiếp", 1), "TIẾP TỤC ÁP DỤNG", [("MỨC GIÁ", "CỦA QUYẾT ĐỊNH 1541", O(W(3, "tiếp", 1), 0.2)), ("CHO ĐẾN KHI", "CÓ VĂN BẢN MỚI", O(W(3, "tiếp", 1), 0.8))], bg="sky3"),
    photo(4, "hose3", [("CHỊ HẠNH · 1.000 CỔ PHIẾU", [4, "ví"], "acc"), ("giữ đủ mười hai tháng", [5, "trong"], "sm")], ai=False, tag=HYP),
    hyp(units(W(5, "trong"), "12 THÁNG × 1.000 CỔ PHIẾU · " + HYP, 12, 12, [5, "mười"], "THÁNG GIỮ CỔ PHIẾU · MỖI THÁNG 270 Đ", "ai09", cols=6), HYPS),
    hyp(counter(6, 3240, "CẢ 12 THÁNG · 270 Đ × 12", "hose1", suffix=" Đ")),
    hyp(bars(7, "PHÍ LƯU KÝ SO VỚI PHÍ MÔI GIỚI (Đ)", "CHỪNG 2% · " + HYP,
             [("PHÍ MÔI GIỚI HAI CHIỀU", 150000, "150.000 Đ", [7, "một"], False), ("PHÍ LƯU KÝ CẢ NĂM", 3240, "3.240 Đ", [7, "ba"], True)])),
    kinetic(8, "hn1", [("BIỂU PHÍ CỦA BẠN", 8, "sm"), ("CÓ THỂ KHÁC", [8, "có"], "acc")]),
    ledger(W(8, "do"), "VÍ DỤ VÌ SAO CÓ THỂ KHÁC", [("CÁCH THỂ HIỆN", "THUẾ GIÁ TRỊ GIA TĂNG", O(W(8, "do"), 0.2)), ("VIỆC CẦN LÀM", "KIỂM TRA ĐIỀU KIỆN NƠI BẠN CHỌN", O(W(8, "do"), 0.8))],
           bg="hn6"),
    split(9, "HAI CÁCH TÍNH PHÍ KHÁC NHAU", ("ai09", "PHÍ LƯU KÝ · THEO THÁNG", O(9, 0.2)), ("ai14", "PHÍ MÔI GIỚI · THEO TỪNG LƯỢT", O(9, 0.9)), "≠"),
    kinetic(10, "ai08", [("BA DÒNG ĐÃ ĐỦ", 10, "acc"), ("nhưng còn dòng thứ tư", [10, "nhưng"], "sm")], tag=HYP),
    photo(11, "ai13", [("DÒNG THỨ TƯ", [11, "dòng"], "acc"), ("chỉ bật lên khi chị muốn có tiền trước", [11, "chỉ"], "sm")], tag=HYP),
]}

# ======================= CH06 · phí ứng trước =======================
CH["ch06"] = {"hud": {"k": "DÒNG 04", "t": "MÓN QUÀ CỦA SỰ SỐT RUỘT"}, "bgm": {"mood": "curious", "gain": 0.11}, "scenes": [
    chap("6", "DÒNG BỐN", "ỨNG TRƯỚC\nTIỀN BÁN", "MÓN QUÀ CỦA SỰ SỐT RUỘT", "tiền", "ai11"),
    hyp(timeline(1, "CHỊ HẠNH SỐT RUỘT", [("1", "BÁN XONG", O(1, 0.1)), ("2", "MUỐN DÙNG TIỀN", O(1, 0.8)), ("3", "SỚM HƠN", W(1, "sớm"))])),
    ledger(2, "DỊCH VỤ ỨNG TRƯỚC", [("MỘT SỐ CÔNG TY", "CÓ DỊCH VỤ ỨNG TRƯỚC", O(2, 0.2)), ("ĐIỀU KIỆN VÀ CHI PHÍ", "XEM TRÊN BIỂU PHÍ NƠI ĐÓ", O(2, 0.8))]),
    hyp(counter(3, 12, "LÃI HOÀN TOÀN GIẢ ĐỊNH · MỘT NĂM · TÍNH THEO NGÀY", "ai04", suffix="%"), HYPS),
    hyp(units(4, "ỨNG 50 TRIỆU ĐỒNG TRONG HAI NGÀY · " + HYP, 2, 2, [4, "trong"], "NGÀY ỨNG TRƯỚC", "ai11", cols=2)),
    slam(5, "sky2", "KHÔNG PHẢI BIỂU PHÍ", "HAY MỨC LÃI ÁP DỤNG CHUNG", hit=[5, "không"], tag=HYP),
    hyp(counter(6, 6, "50 TRIỆU × 12% · MỘT NĂM", "hn4", suffix=" TRIỆU Đ")),
    kinetic(7, "hn3", [("CHIA 365 NGÀY · NHÂN 2 NGÀY", 7, "sm"), ("KHOẢNG 33 NGHÌN ĐỒNG", [7, "ra"], "acc")], tag=HYP),
    hyp(counter(8, 33, "CHI PHÍ ỨNG TRƯỚC · GIẢ ĐỊNH", "hose1", prefix="≈ ", suffix=" NGHÌN Đ"), HYPS),
    kinetic(W(8, "tương"), "hose2", [("TƯƠNG ĐƯƠNG CHỪNG", [8, "tương"], "sm"), ("0,066% SỐ TIỀN ỨNG", [8, "không"], "acc")], tag=HYP),
    hyp(bars(9, "CHI PHÍ ỨNG TRƯỚC (NGHÌN Đ)", "GIẢ ĐỊNH · " + HYP, [("CHỌN ỨNG TRƯỚC", 33, "≈ 33", [9, "nếu"], True), ("KHÔNG ỨNG TRƯỚC", 0.5, "0", [9, "trong"], False)])),
    photo(10, "hn2", [("CÁC KHOẢN VÀ ĐIỀU KIỆN KHÁC", [10, "các"], "acc"), ("xem theo biểu phí thực tế", [10, "vẫn"], "sm")], ai=False),
    kinetic(11, "sky3", [("NẾU CHỌN ỨNG TRƯỚC", 11, "sm"), ("CỘNG CHI PHÍ ẤY VÀO GIAO DỊCH", [11, "chị"], "acc")], tag=HYP),
    hyp(ledger(12, "BỐN DÒNG CỦA CHỊ HẠNH", [("1 · PHÍ MÔI GIỚI", "150.000 Đ", O(12, 0.2)), ("2 · THUẾ GIẢ ĐỊNH", "50.000 Đ", O(12, 0.8)),
                                          ("3 · PHÍ LƯU KÝ", "3.240 Đ / NĂM", W(12, "có")), ("4 · ỨNG TRƯỚC", "≈ 33.000 Đ", W(12, "trong"))], bg="sky4")),
    question(W(13, "đặt"), "ai04", "Chị Hạnh quan tâm nhất:\ngiá phải tăng bao nhiêu mới hòa vốn?", tag=HYP),
]}

# ======================= CH07 · phiếu hòa vốn =======================
CH["ch07"] = {"hud": {"k": "PHIẾU HÒA VỐN", "t": "GIÁ PHẢI TĂNG BAO NHIÊU"}, "bgm": {"mood": "mystery", "gain": 0.11}, "scenes": [
    chap("7", "PHIẾU HÒA VỐN", "GIÁ PHẢI TĂNG\nBAO NHIÊU?", "VÍ DỤ GIẢ ĐỊNH · KHÔNG PHẢI DỰ BÁO", "đây", "ai04"),
    hyp(ledger(1, "PHIẾU HÒA VỐN · CHỊ HẠNH MUA", [("SỐ CỔ PHIẾU", "1.000", O(1, 0.2)), ("GIÁ MUA", "50.000 Đ", O(1, 0.8))], total=("TRỊ GIÁ", "50.000.000 Đ", W(1, "trị")))),
    hyp(counter(2, 75, "PHÍ MUA GIẢ ĐỊNH 0,15%", "hose2", suffix=" NGHÌN Đ")),
    hyp(ledger(3, "TỔNG TIỀN CHỊ HẠNH ĐÃ CHI", [("TIỀN MUA", "50.000.000 Đ", O(3, 0.2)), ("PHÍ MUA", "75.000 Đ", O(3, 0.8))], total=("TỔNG ĐÃ CHI", "50.075.000 Đ", W(3, "năm")))),
    kinetic(4, "ai06", [("BÁN ĐÚNG GIÁ MUA", 4, "acc"), ("50.000 đồng · không hơn không kém", [4, "năm"], "sm")], tag=HYP),
    hyp(waterfall(5, "BÁN ĐÚNG GIÁ · TIỀN CÒN LẠI (NGHÌN ĐỒNG)", ("TIỀN BÁN", 50000, O(5, 0.3)),
                  [("PHÍ BÁN", -75, W(5, "phí")), ("THUẾ GIẢ ĐỊNH", -50, W(5, "thuế"))], ("CÒN LẠI", W(5, "nghìn", 1), "gold"))),
    hyp(counter(6, 49875000, "CHỊ HẠNH CÒN LẠI SAU KHI BÁN", "ai06", suffix=" Đ")),
    slam(7, "vault3", "THIẾU 200.000 ĐỒNG", "SO VỚI SỐ ĐÃ CHI", hit=[7, "thiếu"], tag=HYP),
    hyp(stack(8, "GIÁ ĐỨNG YÊN VẪN MẤT (NGHÌN ĐỒNG)", ["PHÍ MUA", "PHÍ BÁN", "THUẾ GIẢ ĐỊNH"], [("GIÁ ĐỨNG YÊN", [75, 75, 50], O(8, 0.2))],
              [(0, "TỔNG 200 NGHÌN Đ = 0,4%", W(8, "không"))])),
    hyp(counter(9, 50200, "GIÁ BÁN HÒA VỐN · KHOẢNG · PHÍ MÔI GIỚI VÀ THUẾ GIẢ ĐỊNH", "hose3", suffix=" Đ")),
    hyp(bars(10, "MỨC TĂNG ĐỂ HÒA VỐN ≈ 0,401% SO VỚI GIÁ MUA", "ĐỒNG MỖI CỔ PHIẾU · " + HYP,
             [("GIÁ MUA", 50000, "50.000 Đ", [10, "mức"], False), ("GIÁ HÒA VỐN", 50200, "≈ 50.200 Đ", [10, "chừng"], True)])),
    hyp(ledger(11, "NẾU PHÍ GIẢ ĐỊNH 0,25% MỖI CHIỀU", [("PHÍ MÔI GIỚI", "0,25% MỖI CHIỀU", O(11, 0.2)), ("GIÁ HÒA VỐN", "≈ 50.300 Đ", O(11, 0.8))])),
    hyp(bars(12, "MỨC TĂNG HÒA VỐN SO VỚI GIÁ MUA (%)", "GIẢ ĐỊNH · " + HYP, [("PHÍ 0,15%", 0.401, "≈ 0,401%", O(12, 0.2), False), ("PHÍ 0,25%", 0.602, "≈ 0,602%", [12, "sáu"], True)])),
    hyp(counter(13, 0.054, "PHÍ SỞ TÁCH RIÊNG · HAI CHIỀU · ƯỚC TÍNH THÊM", "hnx", suffix="%")),
    kinetic(14, "hose4", [("ỨNG TRƯỚC THEO GIẢ ĐỊNH", 14, "sm"), ("≈ 0,066% SỐ TIỀN ỨNG", [14, "khoảng"], "acc")], tag=HYP),
    ledger(15, "PHƯƠNG TRÌNH HÒA VỐN", [("ĐƯA TỪNG KHOẢN VÀO", "PHÍ · THUẾ · LƯU KÝ · ỨNG TRƯỚC", O(15, 0.2)), ("TRÁNH", "CỘNG TRÙNG", O(15, 0.8))], bg="hn4"),
    photo(16, "ai09", [("GIÁ ĐỨNG YÊN · TÁI ĐẦU TƯ", 16, "acc"), ("kể cả phần lẻ của một cổ phiếu", [16, "kể"], "sm")], tag=HYP),
    hyp(counter(17, 48.04, "SAU MƯỜI VÒNG · GIÁ ĐỨNG YÊN · KHOẢNG", "ai01", frm=50, suffix=" TRIỆU Đ")),
    ledger(18, "PHÉP TÍNH CHƯA XÉT", [("RÀNG BUỘC LÔ GIAO DỊCH", "CHƯA XÉT", O(18, 0.2)), ("CÁC KHOẢN KHÁC", "CHƯA XÉT", O(18, 0.8))], bg="sky2"),
    myth(W(19, "không"), "ai10", "ĐÂY KHÔNG PHẢI", "LỜI KHUYÊN GIAO DỊCH ÍT HAY NHIỀU", "MÀ LÀ", "MỘT PHÉP TÍNH VỀ CHI PHÍ", [19, "không"], [19, "nên"]),
    hyp(timeline(20, "HAI TẤM BẢN ĐỒ · ĐƯỜNG TIỀN", [("1", "NGÂN HÀNG CỦA CHỊ", O(20, 0.1)), ("2", "CHỖ CÓ TÊN CHỊ", O(20, 0.8))])),
    photo(W(21, "qua"), "ai16", [("QUA MỘT CHỖ CÓ TÊN CHỊ", [21, "qua"], "acc"), ("tới sàn · rồi về lại sau T+2", [21, "tới"], "sm")], tag=HYP),
    hyp(units(22, "BỐN KHOẢN CÓ THỂ PHÁT SINH · " + HYP, 4, 4, [22, "phí"], "PHÍ MÔI GIỚI · THUẾ · LƯU KÝ · ỨNG TRƯỚC", "vault1")),
    photo(23, "hn3", [("KIỂM BIỂU PHÍ VÀ QUY ĐỊNH THUẾ", 23, "acc"), ("tính đủ các khoản theo điều kiện của bạn", [23, "rồi"], "sm")], ai=False),
    question(24, "ai10", "Bạn đã đọc dòng phí nào trong biểu phí\ncủa mình, và dòng nào khiến bạn bất ngờ nhất?", show=[25, "bạn"], tag="NỘI DUNG GIÁO DỤC · KHÔNG PHẢI TƯ VẤN ĐẦU TƯ"),
    kinetic(26, "ai01", [("HÃY VIẾT VÀO", 26, "sm"), ("PHẦN BÌNH LUẬN", [26, "phần"], "acc")]),
    hyp(counter(W(27, "nếu"), 10, "NẾU CHỈ CÓ 10 TRIỆU · TRÊN BẢNG ĐIỆN MUA ĐƯỢC GÌ?", "ai07", suffix=" TRIỆU Đ")),
    question(W(27, "vì"), "ai05", "Vì sao một lệnh mua có thể\nbị từ chối hai lần liên tiếp?", tag=HYP),
]}


# ---------------- spec ----------------
TITLE = "Mua 50 Triệu Cổ Phiếu: Giá Phải Tăng Bao Nhiêu Mới Hòa Vốn?"
TITLES = [TITLE,
          "Giữ 50 Triệu Cổ Phiếu 12 Tháng: Phí Và Thuế Là Bao Nhiêu?",   # khoản tiền + mốc thời gian (luật #337)
          "Giá Đứng Yên Vẫn Lỗ 200 Nghìn: Bốn Khoản Phí Ở Đâu Ra?"]       # rủi ro (luật #337)
SOURCES = [
    "https://thoibaotaichinhvietnam.vn/so-luong-tai-khoan-nha-dau-tu-dat-14-4-trieu-tai-khoan-tinh-den-cuoi-thang-10-2026-206477.html",
    "https://doanhnhan.baophapluat.vn/nha-dau-tu-trong-nuoc-mo-them-hon-252-000-tai-khoan-chung-khoan-trong-thang-10.html",
    "https://cafef.vn/viet-nam-co-them-25-trieu-tai-khoan-chung-khoan-tu-dau-nam-188261105151047551.chn",
    "https://ketoananpha.vn/thong-tu-121-2020-tt-btc",
    "https://hethongphapluat.com/luat-chung-khoan-2019/khoan-1-dieu-88",
    "https://nguoiquansat.vn/tu-2-8-bo-tai-chinh-bai-bo-16-thong-tu-ve-gia-dau-gia-chung-khoan-226754.html",
    "https://lsvn.vn/bo-tai-chinh-bai-bo-toan-bo-16-thong-tu-a159422.html",
    "https://thoibaotaichinhvietnam.vn/doi-moi-co-che-dinh-gia-dich-vu-tren-thi-truong-chung-khoan-viet-nam-174902.html",
    "https://thoibaotaichinhvietnam.vn/ban-hanh-quy-dinh-ve-muc-gia-dich-vu-trong-linh-vuc-chung-khoan-175987.html",
    "https://cafeland.vn/tin-tuc/bo-tai-chinh-ban-hanh-muc-gia-dich-vu-moi-trong-linh-vuc-chung-khoan-138022.html",
    "https://luatvietnam.vn/tin-van-ban-moi/muc-gia-dich-vu-trong-linh-vuc-chung-khoan-tai-so-giao-dich-chung-khoan-viet-nam-186-101997-article.html",
    "https://thoibaotaichinhvietnam.vn/bo-tai-chinh-ban-hanh-thong-tu-sua-doi-bo-sung-2-thong-tu-trong-linh-vuc-chung-khoan-202912.html",
    "https://www.ey.com/vi_vn/technical/tax/tax-and-law-updates/luat-thue-thu-nhap-ca-nhan-109-2025-qh15",
    "https://lsvn.vn/bo-tai-chinh-rut-de-xuat-ap-thue-20-tren-lai-ban-chung-khoan-a162771.html",
    "https://vcci.com.vn/tin-tuc/muc-thue-chuyen-nhuong-chung-khoan-hien-hanh-van-phu-hop",
]
SPEC = {
    "title": TITLE, "channel": "CK", "accent": "#fbbf24", "master": True, "endcard": 20, "endcardSub": "VIDEO TIẾP THEO", "beat2": True,
    "opening_gate": True, "craft": True,
    "acc": ["phí", "thuế", "hòa", "vốn", "lưu", "ký", "ứng", "trước"],
    "say": {}, "imgs": IMGS, "chapters": [f"ch{i:02d}" for i in range(8)],
    "youtube": {
        "titles": TITLES,
        "summary": ("Chị Hạnh là nhân vật giả định vừa nạp năm mươi triệu đồng vào tài khoản chứng khoán. Tiền của chị nằm ở đâu, thuộc về ai, và một vòng mua rồi "
                    "bán phát sinh những khoản nào? Video vẽ hai tấm bản đồ: đường đi của tiền và tờ hóa đơn bốn dòng (phí môi giới, thuế khi bán, phí lưu ký, "
                    "phí ứng trước), rồi đặt tất cả lên một tờ phiếu để tính giá bán hòa vốn theo các giả định đã nêu."),
        "more": [
            "Nội dung giáo dục, không phải tư vấn đầu tư. Chị Hạnh, số tiền năm mươi triệu đồng, mức phí môi giới 0,15% mỗi chiều, thuế 0,1% trên giá trị bán, lãi "
            "ứng trước 12% một năm và mọi con số tính toán trong video là VÍ DỤ GIẢ ĐỊNH, không phải biểu phí, mức thuế hay mức lãi áp dụng chung, cũng không phải "
            "khuyến nghị mua hay bán. Giọng đọc tổng hợp; nội dung do kênh biên soạn từ nguồn công khai.",
            "Lưu ý nguồn: mức thuế 0,1% khi bán cổ phiếu niêm yết chưa được đối chiếu với nguyên văn điều khoản hiện hành nên chỉ dùng như một giả định để tính. "
            "Mức khoảng 0,027% giá trị giao dịch có nguồn cho Sở giao dịch chứng khoán Hà Nội; cách thu về nhà đầu tư tùy biểu phí của từng công ty. Phí môi giới do "
            "từng công ty tự quy định. Quy định có thể thay đổi: hãy kiểm tra biểu phí và quy định thuế hiện hành trước khi giao dịch.",
        ],
        "chapter_titles": {"ch00": "Mở đầu: hơn 252 nghìn tài khoản mới và hai tấm bản đồ", "ch01": "Tiền của chị nằm ở đâu, thuộc về ai",
                           "ch02": "Dòng 1: phí môi giới", "ch03": "Hai chữ “miễn phí”", "ch04": "Dòng 2: thuế khi bán (giả định 0,1%)",
                           "ch05": "Dòng 3: phí lưu ký mười hai tháng", "ch06": "Dòng 4: phí ứng trước tiền bán", "ch07": "Phiếu hòa vốn: giá phải tăng bao nhiêu"},
        "sources": SOURCES,
        "hashtags": ["TàiChínhCáNhân", "ChứngKhoán", "PhíGiaoDịch", "BiểuĐồBiếtNói"],
        "tags": ["phí mở tài khoản chứng khoán", "phí môi giới chứng khoán", "thuế bán cổ phiếu", "phí lưu ký", "giá hòa vốn cổ phiếu",
                 "chứng khoán cho người mới", "chi phí giao dịch cổ phiếu", "tài chính cá nhân", "biểu đồ biết nói"],
        "category": "27", "thumb": "t1.jpg",
        "data_credit": "📊 SỐ LIỆU: số tài khoản theo báo chí tổng hợp (VSDC, 11/2026); văn bản pháp luật và biểu giá dịch vụ theo nguồn công khai ghi ở phần nguồn; phép tính hóa đơn và hòa vốn do kênh tự lập (ví dụ giả định).",
        "video_credits": "Ảnh và video minh họa chung do AI tạo (không mô tả người hay sự kiện thật). Ảnh tư liệu: Wikimedia Commons, giấy phép ghi trong phần ghi công.",
    },
}


def main():
    (D / "spec.json").write_text(json.dumps(SPEC, ensure_ascii=False, indent=1), encoding="utf-8")
    for name, c in CH.items():
        p = D / f"{name}.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d.update(c)
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("spec +", len(CH), "chương")


if __name__ == "__main__":
    main()
