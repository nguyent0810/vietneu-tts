"""Sinh spec.json + hud/bgm/scenes của từng chNN.json cho CK bài 11 "Có 10 triệu mua được gì trên sàn chứng khoán?" (#377).

    python data/long/ck-c8-10-trieu-mua-duoc-gi/gen_scenes.py     # giữ nguyên "lines" + "title" (do motion/long/script_lines.py ghi)

Kịch bản: script.md (8 chương, 146 câu). Dữ kiện: factcheck.md. Phép tính (VÍ DỤ GIẢ ĐỊNH, khối "Ghi chú kiểm chứng" cuối script.md):
  cổ phiếu B giá 60.000 đ: 10.000.000 / 60.000 = 166,7; 160 cp không phải bội của 100 và lớn hơn 99; 200 cp x 60.000 = 12.000.000 > 10.000.000;
  một lô = 6.000.000, phí mua giả định 0,15% = 9.000, dư 3.991.000; biên độ 7%: trần 64.200, sàn 55.800; nấc 100 đ -> 60.100;
  A 15.000: lô 1.500.000, 6 lô = 600 cp = 9.000.000, dư 1.000.000; C 120.000: lô 12.000.000 (không đủ); giá 50.000: 200 cp = 10.000.000, phí 15.000;
  lô lẻ: 160 = 100 + 60, 9.600.000 + phí 14.400 = 9.614.400; C: 83 cp = 9.960.000 + phí 14.940 = 9.974.940; bán thấp 2 nấc = 200 x 83 = 16.600;
  chia ba: 3.333.333/phần, ≈ 33.300 đ/cp; 20k/25k/30k: lô 2 / 2,5 / 3 triệu = 7,5 triệu, còn 2,5 triệu; phí 0,15% x 10 triệu = 15.000;
  ETF giả định 18.000 đ: lô 1.800.000, 5 lô = 500 chứng chỉ = 9.000.000, còn 1.000.000; 1,8/12 = 0,15; nấc 10 đ -> 18.010.
Luật kênh: chỉ giáo dục; chị Hạnh và mọi con số của chị là VÍ DỤ GIẢ ĐỊNH (nhãn trên màn hình ở mọi cảnh có số); không tên công ty chứng khoán, ngân hàng,
ứng dụng hay mã cổ phiếu trên màn hình; ảnh chỉ PD/CC0/CC BY (CK cấm ShareAlike); ảnh/clip AI chỉ minh họa chung từ kho chung.
Ghi file: UTF-8 (Codex làm hỏng dấu tiếng Việt khi ghi bằng PowerShell, nên script này ghi bằng Path.write_text(encoding="utf-8")).
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent
HYP = "VÍ DỤ GIẢ ĐỊNH"
HYPS = "VÍ DỤ GIẢ ĐỊNH · CHỊ HẠNH LÀ NHÂN VẬT GIẢ ĐỊNH"
ILL = "ẢNH MINH HỌA"
VM = "VIDEO MINH HỌA"


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
# Kho ảnh đã soát mắt ở bài 10 (Lead 13/11): không logo/chữ/ticker; kênh CK cấm ShareAlike (CHAN no_sa) -> chỉ CC0/PD/CC BY.
#   ai01..ai16 = ảnh AI minh họa chung (EXT:ai, "no restrictions", kho chung, không người thật)
#   hose1-3, hnx, sky1/2, hn5/6 = CC0 · hose4/sky3, vault1/2/3 = Public domain · hn1/hn3/hn4/sky4 = CC BY 2.0 · hn2 = CC BY 4.0
IMGS_ALL = {f"ai{i:02d}": f"EXT:ai:ai_{i:02d}" for i in range(1, 17)}
IMGS_ALL.update({
    "hose1": "File:Ho Chi Minh stock exchange.jpg",
    "hose2": "File:Ho Chi Minh stock exchange.jpg",
    "hose3": "File:Ho Chi Minh stock exchange.jpg",
    "hose4": "File:Ho Chi Minh City during sunset (50332857462).jpg",
    "hnx": "File:Ho Chi Minh City Skyline.jpg",
    "sky1": "File:Ho Chi Minh City Skyline.jpg",
    "sky2": "File:Ho Chi Minh City Skyline at Night.jpg",
    "sky3": "File:Ho Chi Minh City during sunset (50332857462).jpg",
    "vault1": "File:Bank vault 1901.jpg",
    "vault2": "File:NTS - Bank Vault - after 2.jpg",
    "vault3": "File:Ocean National Bank vault door.png",
    "hn1": "File:Ho Chi Minh City panorama 2019 (cropped).jpg",
    "hn2": "File:ThuDauMot six-way intersection at Christmas.jpg",
    "hn3": "File:Ben Thanh Market (5461278547).jpg",
    "hn4": "File:Ho Chi Minh City Opera House (53668610660).jpg",
    "hn5": "File:20190923 Independence Palace-13.jpg",
    "hn6": "File:Ho Chi Minh City Skyline at Night.jpg",
    "sky4": "File:DJI 0212-HDR-Pano (cropped).jpg",
})

CH = {}

# ======================= CH00 · hai lần bị từ chối =======================
CH["ch00"] = {"hud": {"k": "MỞ ĐẦU", "t": "HAI LẦN BỊ TỪ CHỐI"}, "bgm": {"mood": "curious", "gain": 0.10}, "scenes": [
    broll(0, "900002", [("CÓ 10 TRIỆU ĐỒNG", O(0, 0.2), "acc"), ("mua được gì trên bảng điện?", [0, "bạn"], "sm")], tag=HYP),   # cổng mở đầu: clip trong 5s đầu
    photo(2, "ai07", [("CỔ PHIẾU B · BẢNG ĐIỆN HIỆN 60", O(2, 0.3), "acc"), ("chị Hạnh chọn một mức giá giả định", [2, "chị"], "sm")], tag=HYP),
    hyp(ledger(3, "CHỊ HẠNH NHẨM", [("10.000.000 Đ ÷ 60.000 Đ", "HƠN 160 CỔ PHIẾU", O(3, 0.2)), ("CHỊ GÕ", "160 CỔ PHIẾU", O(3, 0.8))], bg="ai04")),
    broll(4, "900005", [("LỆNH 1 · 160 CỔ PHIẾU", O(4, 0.2), "acc"), ("ứng dụng báo: khối lượng không hợp lệ", [4, "ứng"], "sm")], tag=HYP),
    slam(5, "ai05", "LỆNH 2 · KHÔNG ĐỦ TIỀN", "SỬA THÀNH 200 CỔ PHIẾU · THỬ LẠI", hit=[5, "lần"], tag=HYP),
    question(6, "ai08", "Cùng 10 triệu,\nvì sao lệnh đầu sai, lệnh sau thiếu?"),
    hyp(counter(W(7, "chị"), 600, "Ở MỘT MỨC GIÁ RẺ HƠN · CHỊ MUA ĐƯỢC", "ai14", suffix=" CỔ PHIẾU"), HYPS),
    broll(W(8, "nhân"), "900003", [("NHÂN VẬT GIẢ ĐỊNH", W(8, "nhân"), "acc"), ("10 triệu đồng và các mức giá cũng là giả định", [8, "còn"], "sm")]),
    slam(9, "ai15", "VÍ DỤ GIẢ ĐỊNH", "NHÃN NÀY HIỆN MỖI KHI TA TÍNH", hit=[9, "nhãn"]),
    counter(10, 14384902, "TÀI KHOẢN CHỨNG KHOÁN TRÊN THỊ TRƯỜNG · CUỐI THÁNG 10/2026", "sky2", src="DỮ LIỆU LƯU KÝ · THEO BÁO CHÍ 05/11/2026"),
    myth(11, "sky1", "KHÔNG PHẢI", "SỐ NGƯỜI ĐỨNG TRƯỚC BẢNG ĐIỆN", "MÀ LÀ", "SỐ TÀI KHOẢN", [11, "không"], [11, "đứng"]),
    photo(12, "ai01", [("10 TRIỆU: ĐỦ BẮT ĐẦU?", O(12, 0.3), "acc"), ("hay chỉ là tiền lẻ của thị trường?", [12, "hay"], "sm")], tag=HYP),
    hyp(timeline(13, "10 TRIỆU LÊN BÀN CÂN · 3 MỨC GIÁ · 3 LỐI ĐI", [("3", "MỨC GIÁ", O(13, 0.1)), ("1", "LÔ CHẴN", O(13, 0.8)), ("2", "LÔ LẺ", [13, "lẻ"]),
                                                                  ("3", "QUỸ ETF", [13, "quỹ"])], bg="ai06")),
    question(14, "900006", "Vì sao con số 60\nkhông có nghĩa là 60 đồng?"),
]}

# ======================= CH01 · con số không phải là đồng =======================
CH["ch01"] = {"hud": {"k": "CHẶNG 01", "t": "CON SỐ KHÔNG PHẢI LÀ ĐỒNG"}, "bgm": {"mood": "calm", "gain": 0.11}, "scenes": [
    chap("1", "CHẶNG MỘT", "CON SỐ KHÔNG PHẢI\nLÀ ĐỒNG", "ĐỌC BẢNG GIÁ TRƯỚC KHI ĐẶT LỆNH", "bảng", "ai06"),
    source(1, "ai15", "HƯỚNG DẪN XEM BẢNG GIÁ · MỘT CÔNG TY CHỨNG KHOÁN", "GIÁ HIỂN THỊ THEO NGHÌN ĐỒNG",
           "giá cổ phiếu và chứng chỉ quỹ hiển thị [[theo nghìn đồng]]", [1, "nghìn"], "NGUỒN CÔNG TY · CHƯA ĐỐI CHIẾU SỞ", [1, "hiển"]),
    hyp(ledger(2, "ĐỌC GIÁ TRÊN BẢNG", [("CON SỐ TRÊN BẢNG", "60", O(2, 0.2)), ("NHÂN VỚI", "1.000", O(2, 0.8))], total=("CỔ PHIẾU B", "60.000 Đ MỖI CỔ PHIẾU", [3, "vậy"]), bg="ai04")),
    hyp(counter(4, 25500, "GIÁ 25,5 TRÊN BẢNG = ĐỒNG MỖI CỔ PHIẾU", "ai12", suffix=" Đ")),
    photo(5, "ai01", [("ĐỌC SAI MỘT BẬC", O(5, 0.2), "acc"), ("tưởng cổ phiếu rẻ gấp một nghìn lần", [5, "đã"], "sm")], tag=HYP),
    kinetic(6, "hose4", [("ĐẶT GIÁ ĐÚNG MỘT NẤC", 6, "acc"), ("Sở giao dịch gọi là đơn vị yết giá", [7, "sở"], "sm")]),
    bars(8, "ĐƠN VỊ YẾT GIÁ · CỔ PHIẾU (ĐỒNG)", "NẤC GIÁ THEO MỨC GIÁ",
         [("DƯỚI 10.000 Đ", 10, "10 Đ", O(8, 0.4), False), ("10.000 – 49.950 Đ", 50, "50 Đ", [9, "mỗi"], True)]),
    hyp(ledger(10, "TỪ 50.000 Đ · NẤC GIÁ 100 Đ", [("TỪ 50.000 Đ TRỞ LÊN", "MỖI NẤC 100 Đ", O(10, 0.2)), ("CỔ PHIẾU B", "GIÁ HIỆN TẠI 60.000 Đ", O(10, 0.8))],
               total=("GIÁ KẾ TIẾP", "60.100 Đ", [11, "kế"]), bg="ai15")),
    photo(12, "ai09", [("GIÁ 15.000 Đ", O(12, 0.2), "acc"), ("nhích từng nấc 50 đồng", [12, "thì"], "sm")], tag=HYP),
    slam(13, "ai03", "QUỸ ETF · NẤC 10 ĐỒNG", "Ở MỌI MỨC GIÁ", hit=[13, "mười"]),
    counter(14, 7, "BIÊN ĐỘ THÔNG THƯỜNG Ở SỞ NÀY · CỘNG TRỪ", "sky4", suffix="%"),
    hyp(ledger(15, "GIÁ THAM CHIẾU GIẢ ĐỊNH 60.000 Đ", [("GIÁ THAM CHIẾU", "60.000 Đ", O(15, 0.2)), ("GIÁ TRẦN · + 7%", "64.200 Đ", O(15, 0.8))],
               total=("GIÁ SÀN · − 7%", "55.800 Đ", [16, "giá"]), bg="ai07")),
    slam(17, "ai06", "HAI MỨC ĐỀU ĐÚNG NẤC 100 Đ", "XÉT RIÊNG QUY TẮC VỀ GIÁ", hit=[17, "đều"], tag=HYP),
    question(19, "ai02", "Lệnh đầu của chị Hạnh\nvấp ngã ở đâu?"),
]}

# ======================= CH02 · lô một trăm =======================
CH["ch02"] = {"hud": {"k": "CHẶNG 02", "t": "LÔ MỘT TRĂM"}, "bgm": {"mood": "curious", "gain": 0.11}, "scenes": [
    chap("2", "CHẶNG HAI", "LÔ MỘT TRĂM", "KHỐI LƯỢNG KHÔNG ĐẶT TÙY Ý", "khối", "ai03"),
    source([1, "nhà"], "ai12", "SỞ GIAO DỊCH TP.HCM · TÀI LIỆU HƯỚNG DẪN NHÀ ĐẦU TƯ", "ĐƠN VỊ GIAO DỊCH LÔ CHẴN",
           "đơn vị giao dịch lô chẵn là [[100 cổ phiếu]]", [1, "một"], "THEO NGUỒN ĐÃ XEM", [1, "cổ"]),
    hyp(units(2, "LỆNH LÔ CHẴN · BỘI CỦA 100 · " + HYP, 3, 3, [2, "ba"], "100 · 200 · 300 · LỆNH HỢP LỆ", "ai03", cols=3)),
    hyp(ledger(3, "LỆNH ĐẦU CỦA CHỊ HẠNH · 160 CỔ PHIẾU", [("160 ÷ 100", "KHÔNG CHIA HẾT", O(3, 0.2)), ("160 LỚN HƠN 99", "VƯỢT TỐI ĐA LÔ LẺ", O(3, 0.8))])),
    broll(5, "900005", [("KHỐI LƯỢNG KHÔNG HỢP LỆ", O(5, 0.2), "acc"), ("cả lô chẵn lẫn lô lẻ · ứng dụng từ chối", [6, "ứng"], "sm")], tag=HYP),
    hyp(ledger(7, "LỆNH THỨ HAI · 200 CỔ PHIẾU", [("200 CỔ PHIẾU", "HỢP LỆ · BỘI CỦA 100", O(7, 0.2)), ("GIÁ MỖI CỔ PHIẾU", "60.000 Đ", O(7, 0.8))],
               total=("TỔNG CẦN CÓ", "12.000.000 Đ", [8, "mười"]), bg="ai04")),
    hyp(bars(9, "TIỀN CẦN SO VỚI TIỀN CÓ (TRIỆU ĐỒNG)", "GIẢ ĐỊNH · " + HYP, [("CẦN", 12, "12", O(9, 0.4), True), ("CÓ", 10, "10", [9, "khoản"], False)])),
    split(10, "HAI LẦN TỪ CHỐI · HAI LÝ DO", ("ai05", "LÝ DO 1 · KHỐI LƯỢNG", O(10, 0.2)), ("ai04", "LÝ DO 2 · TIỀN", O(10, 0.9)), "+"),
    hyp(timeline(11, "TIỀN TỐI THIỂU CHO MỘT LÔ CHẴN", [("1", "GIÁ MỘT CỔ PHIẾU", O(11, 0.1)), ("2", "× 100 CỔ PHIẾU", O(11, 0.8)), ("3", "= TIỀN TỐI THIỂU", [12, "bằng"])])),
    hyp(counter(13, 6, "60.000 Đ × 100 · MỘT LÔ CỔ PHIẾU B", "hose4", suffix=" TRIỆU Đ")),
    hyp(ledger(14, "PHÍ MUA GIẢ ĐỊNH · 0,15%", [("GIÁ TRỊ MỘT LÔ", "6.000.000 Đ", O(14, 0.2)), ("PHÍ MUA 0,15%", "9.000 Đ", O(14, 0.8))])),
    hyp(waterfall(15, "CHỊ HẠNH · 10 TRIỆU ĐỒNG CÒN LẠI (NGHÌN ĐỒNG)", ("TIỀN CÓ", 10000, O(15, 0.3)),
                  [("MỘT LÔ", -6000, [15, "một"]), ("PHÍ MUA", -9, [15, "còn"])], ("CÒN DƯ", [15, "gần"], "gold"))),
    slam(17, "ai06", "BA MỨC GIÁ", "CÙNG MỘT KHOẢN 10 TRIỆU", hit=[17, "ba"], tag=HYP),
]}

# ======================= CH03 · ba mức giá, một khoản mười triệu =======================
CH["ch03"] = {"hud": {"k": "CHẶNG 03", "t": "BA MỨC GIÁ, MỘT KHOẢN MƯỜI TRIỆU"}, "bgm": {"mood": "calm", "gain": 0.11}, "scenes": [
    chap("3", "CHẶNG BA", "BA MỨC GIÁ\nMỘT KHOẢN 10 TRIỆU", "CÙNG SỐ TIỀN · MỖI MỨC GIÁ MỘT KẾT QUẢ", "triệu", "sky2"),
    slam(1, "ai15", "TOÀN BỘ LÀ GIẢ ĐỊNH", "KHÔNG PHẢI GIÁ CỦA MÃ CÓ THẬT", hit=[1, "đều"], tag=HYP),
    hyp(ledger(2, "CỔ PHIẾU A · GIÁ 15.000 Đ", [("GIÁ MỘT CỔ PHIẾU", "15.000 Đ", O(2, 0.2)), ("MỘT LÔ · × 100", "1.500.000 Đ", O(2, 0.8))],
               total=("10 TRIỆU ÷ 1,5 TRIỆU", "6 LÔ · CÒN LẺ", [3, "mười"]), bg="ai04")),
    hyp(waterfall(4, "CỔ PHIẾU A · 10 TRIỆU ĐỒNG (NGHÌN ĐỒNG)", ("TIỀN CÓ", 10000, O(4, 0.3)), [("600 CỔ PHIẾU", -9000, [4, "tốn"])], ("CÒN DƯ", [5, "chị"], "gold"))),
    hyp(bars(6, "SỐ TIỀN SO VỚI TIỀN CÓ (TRIỆU Đ)", "GIẢ ĐỊNH · " + HYP,
             [("MỘT LÔ", 6, "6", [6, "một"], False), ("HAI LÔ", 12, "12", [7, "hai"], True), ("TIỀN CÓ", 10, "10", [7, "số"], False)], bg="ai07")),
    hyp(counter(8, 12, "CỔ PHIẾU C · MỘT LÔ CẦN", "sky3", suffix=" TRIỆU Đ")),
    slam(9, "ai02", "KHÔNG ĐỦ MỘT LÔ CHẴN", "10 TRIỆU THẤP HƠN 12 TRIỆU", hit=[9, "không"], tag=HYP),
    hyp(ledger(11, "GIÁ 50.000 Đ · 200 CỔ PHIẾU", [("2 LÔ × 100 × 50.000 Đ", "10.000.000 Đ", O(11, 0.2)), ("SỐ TIỀN CÓ", "10.000.000 Đ", O(11, 0.8))])),
    hyp(ledger(13, "NẾU PHÍ TÍNH VÀO SỨC MUA", [("TIỀN CẦN", "10.000.000 Đ + 15.000 Đ", O(13, 0.2)), ("TIỀN CÓ", "10.000.000 Đ", O(13, 0.8))],
               total=("KẾT QUẢ", "THIẾU 15.000 Đ", [13, "làm"]))),
    photo(14, "ai15", [("ĐỌC CÁCH TÍNH SỨC MUA", O(14, 0.2), "acc"), ("của nơi bạn mở tài khoản", [14, "của"], "sm")]),
    hyp(bars(15, "CÙNG 10 TRIỆU · SỐ LÔ CHẴN MUA ĐƯỢC", "GIẢ ĐỊNH · " + HYP,
             [("GIÁ 15.000 Đ", 6, "6 LÔ", [15, "sáu"], False), ("GIÁ 60.000 Đ", 1, "1 LÔ", [15, "và"], False), ("GIÁ 120.000 Đ", 0.25, "0 LÔ", [15, "không"], True)])),
    question(17, "ai10", "Với cổ phiếu C,\nchị Hạnh còn cánh cửa nào khác?"),
]}

# ======================= CH04 · lô lẻ =======================
CH["ch04"] = {"hud": {"k": "CHẶNG 04", "t": "LÔ LẺ: CÁNH CỬA CÓ GIÁ"}, "bgm": {"mood": "mystery", "gain": 0.11}, "scenes": [
    chap("4", "CHẶNG BỐN", "LÔ LẺ:\nCÁNH CỬA CÓ GIÁ", "TỪ 1 ĐẾN 99 CỔ PHIẾU MỖI LỆNH", "lô", "ai14"),
    date(1, "ai11", "LÔ LẺ BẮT ĐẦU GIAO DỊCH TỪ", "12.09.2022"),
    source(2, "ai03", "SỞ GIAO DỊCH TP.HCM · TÀI LIỆU HƯỚNG DẪN NHÀ ĐẦU TƯ", "THỜI GIAN VÀ PHƯƠNG THỨC LÔ LẺ",
           "Thời gian và phương thức giao dịch lô lẻ [[áp dụng tương tự]] lô chẵn", [2, "cũng"], "THEO NGUỒN ĐÃ XEM", [2, "giống"]),
    photo(3, "ai14", [("MỞ THÊM MỘT CÁCH ĐẶT LỆNH", O(3, 0.2), "acc"), ("trong ví dụ của chị Hạnh", [3, "trong"], "sm")], tag=HYP),
    hyp(split(4, "CHIA 160 CỔ PHIẾU B THÀNH HAI LỆNH", ("ai03", "LÔ CHẴN · 100 CỔ PHIẾU", O(4, 0.2)), ("ai14", "LÔ LẺ · 60 CỔ PHIẾU", O(4, 0.9)), "+")),
    hyp(counter(5, 160, "100 LÔ CHẴN + 60 LÔ LẺ · CỔ PHIẾU B", "sky3", suffix=" CỔ PHIẾU")),
    hyp(ledger(6, "CỔ PHIẾU B · 160 CỔ PHIẾU", [("160 × 60.000 Đ", "9.600.000 Đ", O(6, 0.2)), ("PHÍ MUA GIẢ ĐỊNH 0,15%", "14.400 Đ", O(6, 0.8))],
               total=("TỔNG", "9.614.400 Đ · DƯỚI 10 TRIỆU", [7, "tổng"]), bg="ai04")),
    hyp(counter(8, 83.3, "10 TRIỆU ÷ 120.000 Đ · CỔ PHIẾU C", "sky2", suffix=" CỔ PHIẾU")),
    hyp(ledger(9, "CỔ PHIẾU C · TỐI ĐA 83 CỔ PHIẾU", [("SỐ CỔ PHIẾU", "83 · LÔ LẺ", O(9, 0.2)), ("83 × 120.000 Đ", "9.960.000 Đ", O(9, 0.8))])),
    hyp(bars(10, "TỔNG TIỀN SO VỚI 10 TRIỆU (NGHÌN ĐỒNG)", "GIẢ ĐỊNH · " + HYP,
             [("TỔNG PHẢI TRẢ", 9975, "9.974,9", O(10, 0.4), False), ("TIỀN CÓ", 10000, "10.000", [10, "tổng"], True)])),
    source(12, "ai12", "BÀI HƯỚNG DẪN CỦA MỘT CÔNG TY CHỨNG KHOÁN · 10/2026", "LƯU Ý VỀ GIAO DỊCH LÔ LẺ",
           "bài đăng tháng 10 năm 2026 [[đưa ra lưu ý]] về lô lẻ", [12, "đưa"], "NGUỒN THỨ CẤP · CHƯA ĐỐI CHIẾU SỞ", [12, "lưu"]),
    ledger(13, "BÀI HƯỚNG DẪN ẤY MÔ TẢ", [("BẢNG LÔ LẺ", "RIÊNG BIỆT", O(13, 0.2)), ("LOẠI LỆNH", "CHỈ LỆNH GIỚI HẠN", O(13, 0.8))], bg="ai15"),
    broll([14, "nên"], "900004", [("LỆNH BÁN CÓ THỂ NẰM CHỜ CẢ PHIÊN", [14, "nên"], "acc"), ("hoặc bán thấp hơn giá lô chẵn một hai nấc", [14, "hoặc"], "sm")]),
    hyp(timeline(15, "GIẢ SỬ BÁN THẤP HƠN HAI NẤC", [("1", "MỖI NẤC Ở MỨC GIÁ NÀY = 100 Đ", O(15, 0.1)), ("2", "HAI NẤC = 200 Đ MỖI CỔ PHIẾU", O(15, 0.8))])),
    hyp(ledger(16, "BÁN THẤP HƠN HAI NẤC · 83 CỔ PHIẾU", [("200 Đ × 83", "16.600 Đ", O(16, 0.2)), ("PHÍ MUA MỘT CHIỀU GIẢ ĐỊNH", "14.940 Đ", O(16, 0.8))])),
    hyp(bars(17, "PHÍ MỘT CHIỀU SO VỚI BÁN THẤP (Đ)", "GIẢ ĐỊNH · " + HYP,
             [("PHÍ MUA MỘT CHIỀU", 14940, "14.940 Đ", O(17, 0.4), False), ("BÁN THẤP HƠN 2 NẤC", 16600, "16.600 Đ", [17, "nhỉnh"], True)])),
    kinetic(18, "ai09", [("LÔ LẺ MỞ THÊM LỰA CHỌN", 18, "acc"), ("nhưng lệnh có thể chờ · giá bán có thể thấp hơn", [18, "nhưng"], "sm")]),
    hyp(counter(19, 99.6, "83 CỔ PHIẾU C · PHẦN CỦA 10 TRIỆU NẰM Ở MỘT CÔNG TY", "ai02", suffix="%")),
]}

# ======================= CH05 · bỏ trứng vào giỏ nào =======================
CH["ch05"] = {"hud": {"k": "CHẶNG 05", "t": "BỎ TRỨNG VÀO GIỎ NÀO"}, "bgm": {"mood": "calm", "gain": 0.16}, "scenes": [
    chap("5", "CHẶNG NĂM", "BỎ TRỨNG\nVÀO GIỎ NÀO", "10 TRIỆU ĐỒNG CÓ CHIA NHỎ ĐƯỢC KHÔNG", "công", "ai09"),
    photo(1, "ai14", [("KHÔNG BỎ HẾT TRỨNG VÀO MỘT GIỎ", O(1, 0.2), "acc"), ("chia nhỏ để bớt phụ thuộc", [1, "chia"], "sm")]),
    hyp(units(2, "10 TRIỆU ĐỒNG CHIA LÀM BA PHẦN · " + HYP, 3, 3, [2, "ba"], "PHẦN BẰNG NHAU", "ai03", cols=3)),
    hyp(counter(3, 3333333, "MỖI PHẦN · 10 TRIỆU ÷ 3", "hn4", suffix=" Đ")),
    hyp(ledger(W(4, "giá"), "BỎ QUA PHÍ · ĐỂ MỘT PHẦN ĐỦ MUA MỘT LÔ", [("TIỀN MỖI PHẦN", "3.333.333 Đ", O(W(4, "giá"), 0.2)),
                                                                   ("CHIA 100 CỔ PHIẾU", "≈ 33.300 Đ MỖI CỔ PHIẾU", O(W(4, "giá"), 0.8))], bg="ai04")),
    hyp(bars(5, "GIÁ SO VỚI MỨC TỐI ĐA (NGHÌN Đ)", "GIẢ ĐỊNH · " + HYP,
             [("MỨC TỐI ĐA MỖI PHẦN", 33.3, "≈ 33,3", O(5, 0.4), False), ("CỔ PHIẾU B", 60, "60", [5, "sáu"], True), ("CỔ PHIẾU C", 120, "120", [5, "một"], True)])),
    hyp(timeline(6, "BA MÃ GIẢ ĐỊNH · MỖI MÃ MỘT LÔ CHẴN", [("20", "GIÁ 20.000 Đ · MỘT LÔ 2 TRIỆU", O(6, 0.1)), ("25", "GIÁ 25.000 Đ · MỘT LÔ 2,5 TRIỆU", O(6, 0.8)),
                                                       ("30", "GIÁ 30.000 Đ · MỘT LÔ 3 TRIỆU", [6, "và"])])),
    hyp(waterfall(8, "BA LÔ CHẴN · 10 TRIỆU ĐỒNG (NGHÌN ĐỒNG)", ("TIỀN CÓ", 10000, O(8, 0.3)),
                  [("LÔ 20 NGHÌN", -2000, [8, "cộng"]), ("LÔ 25 NGHÌN", -2500, [8, "bảy"]), ("LÔ 30 NGHÌN", -3000, [8, "trước"])], ("CÒN LẠI", [8, "chị"], "gold"))),
    slam([9, "không"], "ai10", "CHIA NHỎ KHÔNG BẢO ĐẢM", "SẼ KHÔNG LỖ", hit=[9, "không"]),
    myth(10, "ai12", "KHÔNG PHẢI", "GIÁ THẤP = DOANH NGHIỆP TỐT", "THỰC RA", "CHƯA NÓI GÌ VỀ CHẤT LƯỢNG", [10, "chưa"], [10, "gì"]),
    photo([11, "chỉ"], "ai12", [("MỘT LÔ CHẴN ĐỦ NHỎ", [11, "chỉ"], "acc"), ("để lọt vào phần tiền của chị", [11, "đủ"], "sm")]),
    hyp(units(12, "BA LỆNH THAY VÌ MỘT LỆNH · " + HYP, 3, 3, [12, "ba"], "LỆNH MUA · PHÍ TÍNH TRÊN TỔNG GIÁ TRỊ", "ai07", cols=3)),
    hyp(counter(14, 15, "PHÍ GIẢ ĐỊNH 0,15% × 10 TRIỆU", "hn6", suffix=" NGHÌN Đ")),
    kinetic([15, "nên"], "ai04", [("MỨC TỐI THIỂU CHO MỖI LỆNH?", [15, "nên"], "acc"), ("nơi bạn chọn có hay không", [15, "hay"], "sm")]),
    hyp(counter(16, 25, "KHOẢN TIỀN CÒN LẠI TRƯỚC PHÍ · 2,5 TRIỆU ÷ 10 TRIỆU", "ai06", suffix="%")),
    question(17, "900006", "Có cách nào để một lệnh duy nhất\nchạm tới nhiều doanh nghiệp?"),
]}

# ======================= CH06 · quỹ ETF =======================
CH["ch06"] = {"hud": {"k": "CHẶNG 06", "t": "QUỸ ETF, MỘT LỆNH CHẠM NHIỀU MÃ"}, "bgm": {"mood": "curious", "gain": 0.11}, "scenes": [
    chap("6", "CHẶNG SÁU", "QUỸ ETF\nMỘT LỆNH CHẠM NHIỀU MÃ", "ETF TRONG LUẬT CHỨNG KHOÁN 2019", "chứng", "ai07"),
    source(1, "ai12", "LUẬT CHỨNG KHOÁN 2019 · KHOẢN 42 ĐIỀU 4 (QUA NGUỒN THỨ CẤP)", "QUỸ HOÁN ĐỔI DANH MỤC (ETF)",
           "quỹ mở hình thành từ việc tiếp nhận, [[hoán đổi danh mục chứng khoán cơ cấu]] lấy chứng chỉ quỹ", [1, "danh"], "NGUỒN THỨ CẤP TRÍCH LUẬT", [1, "đổi"]),
    photo(2, "ai06", [("CHỨNG CHỈ QUỸ ETF · NIÊM YẾT", O(2, 0.2), "acc"), ("giao dịch như chứng khoán niêm yết", [2, "giao"], "sm")]),
    counter(3, 100, "LÔ CHẴN CHỨNG CHỈ QUỸ ETF · THEO SỞ GIAO DỊCH", "sky1", suffix=" CHỨNG CHỈ"),
    kinetic(4, "ai07", [("ETF THƯỜNG PHẢN ÁNH", 4, "acc"), ("một chỉ số hoặc một nhóm tài sản", [4, "một"], "sm")]),
    slam(5, "ai09", "CHỮ “THƯỜNG” QUAN TRỌNG", "MỖI QUỸ CÓ ĐIỀU LỆ VÀ DANH MỤC RIÊNG", hit=[5, "quan"]),
    hyp(ledger(6, "QUỸ GIẢ ĐỊNH · MỘT LÔ", [("GIÁ MỖI CHỨNG CHỈ", "18.000 Đ", O(6, 0.2)), ("SỐ CHỨNG CHỈ MỖI LÔ", "100", O(6, 0.8))],
               total=("MỘT LÔ", "1.800.000 Đ", [7, "là"]), bg="ai07")),
    hyp(waterfall(8, "QUỸ GIẢ ĐỊNH · 10 TRIỆU ĐỒNG (NGHÌN ĐỒNG)", ("TIỀN CÓ", 10000, O(8, 0.3)), [("5 LÔ · 500 CHỨNG CHỈ", -9000, [8, "tốn"])], ("CÒN LẠI", [9, "trước"], "gold"))),
    hyp(bars(10, "MỘT LÔ QUỸ SO VỚI LÔ CỔ PHIẾU C (TRIỆU Đ)", "GIẢ ĐỊNH · " + HYP,
             [("MỘT LÔ QUỸ", 1.8, "1,8", O(10, 0.4), False), ("MỘT LÔ CỔ PHIẾU C", 12, "12", [10, "cổ"], True)])),
    hyp(ledger(12, "ĐỌC GIÁ CHỨNG CHỈ QUỸ", [("CON SỐ TRÊN BẢNG", "18,0", O(12, 0.2)), ("NHÂN VỚI", "1.000", O(12, 0.8))], total=("GIÁ", "18.000 Đ", [13, "mười"]))),
    hyp(counter(14, 18010, "NẤC GIÁ QUỸ 10 Đ · GIÁ KẾ TIẾP", "sky3", frm=18000, suffix=" Đ")),
    myth(15, "ai02", "KHÔNG PHẢI", "MUA ETF = HẾT RỦI RO", "MÀ LÀ", "GIÁ VẪN LÊN XUỐNG · QUỸ CÓ PHÍ RIÊNG", [15, "không"], [16, "giá"]),
    photo(17, "ai15", [("ĐỌC KỸ TÀI LIỆU CỦA QUỸ", O(17, 0.2), "acc"), ("trước khi đặt lệnh · 18 nghìn chỉ là giả định", [17, "nên"], "sm")], tag=HYP),
    question(18, "ai10", "Gom mọi phép tính về một tờ phiếu:\n10 triệu đồng đứng ở đâu?"),
]}

# ======================= CH07 · phiếu mười triệu =======================
CH["ch07"] = {"hud": {"k": "PHIẾU 10 TRIỆU", "t": "10 TRIỆU ĐỒNG ĐỨNG Ở ĐÂU"}, "bgm": {"mood": "mystery", "gain": 0.16}, "scenes": [
    chap("7", "PHIẾU 10 TRIỆU", "10 TRIỆU ĐỒNG\nĐỨNG Ở ĐÂU", "VÍ DỤ GIẢ ĐỊNH · KHÔNG PHẢI DỰ BÁO", "tờ", "ai04"),
    hyp(units(1, "CỔ PHIẾU A · GIÁ 15.000 Đ · " + HYP, 6, 6, [1, "sáu"], "LÔ CHẴN · 600 CỔ PHIẾU · CÒN 1 TRIỆU TRƯỚC PHÍ", "ai03", cols=6)),
    hyp(ledger(2, "CỔ PHIẾU B · GIÁ 60.000 Đ", [("1 LÔ", "100 CỔ PHIẾU", O(2, 0.2)), ("DƯ", "GẦN 4 TRIỆU Đ", O(2, 0.8))], bg="ai07")),
    hyp(bars(3, "CỔ PHIẾU C · SỐ CỔ PHIẾU (10 TRIỆU ĐỒNG)", "GIẢ ĐỊNH · " + HYP, [("MỘT LÔ CẦN", 100, "100 CP", O(3, 0.4), False), ("MUA TỐI ĐA", 83, "83 CP", [3, "chỉ"], True)])),
    hyp(units(4, "QUỸ GIẢ ĐỊNH · GIÁ 18.000 Đ · " + HYP, 5, 5, [4, "năm"], "LÔ CHẴN · 500 CHỨNG CHỈ · CÒN 1 TRIỆU TRƯỚC PHÍ", "ai15", cols=5)),
    kinetic(5, "ai06", [("CÙNG 10 TRIỆU · SỐ LƯỢNG KHÁC NHAU", 5, "acc"), ("tùy mức giá · loại lô · chi phí", [6, "mua"], "sm")], tag=HYP),
    hyp(split(7, "HAI LẦN BỊ TỪ CHỐI", ("ai05", "LỆNH 1 · KHỐI LƯỢNG KHÔNG HỢP LỆ", O(7, 0.2)), ("ai04", "LỆNH 2 · KHÔNG ĐỦ TIỀN", O(7, 0.9)), "+")),
    hyp(ledger(9, "ĐỌC ĐƯỢC TRƯỚC KHI BẤM", [("160 CỔ PHIẾU", "KHÔNG LÀ BỘI CỦA 100", O(9, 0.2)), ("200 CỔ PHIẾU", "CẦN 12 TRIỆU · CÓ 10 TRIỆU", O(9, 0.8))], bg="ai10")),
    kinetic(11, "ai01", [("BA PHÉP TÍNH TRƯỚC MỖI LỆNH", 11, "acc"), ("1 · giá thật sau khi nhân 1.000", [12, "giá"], "sm")]),
    timeline([12, "một", 1], "HAI PHÉP TÍNH CÒN LẠI", [("2", "MỘT LÔ CẦN BAO NHIÊU TIỀN", O(W(12, "một", 1), 0.1)), ("3", "TRỪ PHÍ CÒN DƯ BAO NHIÊU", O(W(12, "một", 1), 0.8))], bg="ai01"),
    kinetic(13, "ai01", [("NỘI DUNG GIÁO DỤC", 13, "acc"), ("không phải tư vấn đầu tư", [13, "không"], "sm")]),
    question([14, "ấy"], "ai10", "Làm ba phép tính ấy với số tiền của bạn:\ncon số nào khiến bạn bất ngờ nhất?", tag="NỘI DUNG GIÁO DỤC · KHÔNG PHẢI TƯ VẤN ĐẦU TƯ"),
]}


# ---------------- spec ----------------
TITLE = "Có 10 Triệu Mua Được Gì Trên Sàn Chứng Khoán?"
TITLES = [TITLE,
          "10 Triệu Đầu Tiên: Mua Được Bao Nhiêu Cổ Phiếu Trên Sàn?",
          "Vì Sao Lệnh Mua 10 Triệu Bị Từ Chối Hai Lần Liên Tiếp?"]
SOURCES = [
    "https://staticfile.hsx.vn/Uploads/UploadDocuments/2453338/HTGD_Quy%20dinh%20can%20biet%20khi%20GDCK%20tren%20HOSE_T2.2026.pdf",
    "https://mbs.com.vn/files/uploads/2025/04/352_qd-sgdhcm_quy-che-giao-dich-ck-tai-hsx.pdf",
    "https://lsvn.vn/nhung-luu-y-can-biet-khi-giao-dich-lo-le-tu-ngay-1291662431365-a123478.html",
    "https://luatvietnam.vn/linh-vuc-khac/quy-dinh-ban-can-biet-ve-quy-etf-883-96256-article.html",
    "https://thoibaotaichinhvietnam.vn/so-luong-tai-khoan-nha-dau-tu-dat-14-4-trieu-tai-khoan-tinh-den-cuoi-thang-10-2026-206477.html",
    "https://simplize.vn/learn/doc-bang-gia-chung-khoan",
    "https://www.finhay.com.vn/en/lo-chan-lo-le-chung-khoan",
    "https://masvn.com/api/attachment/file/1601459300799-H%C6%AF%E1%BB%9ANGD%E1%BA%AANXEMB%E1%BA%A2NGGI%C3%81CH%E1%BB%A8NGKHO%C3%81N.pdf",
]


# ---------------- rải ảnh ----------------
# Các cảnh trên chọn ảnh theo ý nghĩa; hàm này chỉ chống lặp: mỗi khóa ảnh tối đa CAP lần cả video, không trùng ảnh của 3 cảnh liền trước.
# Cảnh photo/split chỉ dùng ảnh AI minh họa chung (credit False); nền ledger/bars/counter... dùng thêm ảnh Commons đã soát (CC0/PD/CC BY).
CAP = 3
POOL_AI = [f"ai{i:02d}" for i in range(1, 17)]
POOL_BG = POOL_AI + ["sky1", "sky2", "sky3", "sky4", "hose1", "hose2", "hose3", "hose4", "hn4", "hn5", "hn6", "hnx", "vault2"]


def spread_images(chapters):
    refs = []   # (container, key, only_ai)

    def walk(o, only_ai=False):
        if isinstance(o, dict):
            ai = only_ai or o.get("type") in ("photo", "split")
            for k, v in o.items():
                if k in ("img", "bg") and isinstance(v, str):
                    refs.append((o, k, ai or k == "img" and o.get("type") == "file"))
                elif isinstance(v, (dict, list)):
                    walk(v, ai)
        elif isinstance(o, list):
            for x in o:
                walk(x, only_ai)
    for c in chapters.values():
        walk(c["scenes"])
    use = {}
    done = {}    # chỉ số ref -> khóa đã gán
    # lượt 1: cảnh photo/split (chỉ ảnh AI) lấy trước, lượt 2: các nền còn lại, ưu tiên ảnh Commons khi phải đổi
    for only in (True, False):
        for n, (o, k, only_ai) in enumerate(refs):
            if only_ai != only:
                continue
            pool = POOL_AI if only_ai else POOL_BG
            near = {done[m] for m in range(n - 3, n + 4) if m in done}
            bad = lambda x: use.get(x, 0) >= CAP or x in near
            if o[k] in pool and not bad(o[k]) and (only_ai or o[k] not in POOL_AI or use.get(o[k], 0) < 1):
                key = o[k]
            else:
                cands = [x for x in pool if not bad(x)]
                key = min(cands, key=lambda x: (use.get(x, 0), x in POOL_AI and not only_ai, pool.index(x)))
            o[k] = key
            use[key] = use.get(key, 0) + 1
            done[n] = key


def _used_imgs():
    keys = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("img", "bg") and isinstance(v, str):
                    keys.add(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(CH)
    return keys


SPEC = {
    "title": TITLE, "channel": "CK", "accent": "#fbbf24", "master": True, "endcard": 20, "endcardSub": "VIDEO TIẾP THEO", "beat2": True,
    "opening_gate": True, "craft": True,
    "acc": ["lô", "chẵn", "lẻ", "giá", "nấc", "phí", "ETF", "triệu"],
    "say": {}, "imgs": {k: v for k, v in IMGS_ALL.items() if k in _used_imgs()}, "chapters": [f"ch{i:02d}" for i in range(8)],
    "youtube": {
        "titles": TITLES,
        "summary": ("Chị Hạnh là nhân vật giả định có mười triệu đồng và hai lệnh mua bị từ chối liên tiếp: một lệnh sai khối lượng, một lệnh thiếu tiền. Video đọc con số "
                    "trên bảng điện (nhân một nghìn), nấc giá, lô chẵn một trăm cổ phiếu và lô lẻ từ một đến chín mươi chín, rồi đặt mười triệu đồng lên bàn cân ở ba mức giá "
                    "giả định, thử chia nhỏ vốn và xem một quỹ ETF giả định, để thấy mười triệu đồng mua được những gì và vì sao hai lệnh đầu bị từ chối."),
        "more": [
            "Nội dung giáo dục, không phải tư vấn đầu tư. Chị Hạnh, khoản mười triệu đồng, các mức giá cổ phiếu A, B, C, quỹ giả định giá mười tám nghìn đồng, mức phí môi giới "
            "0,15% và mọi con số tính toán trong video là VÍ DỤ GIẢ ĐỊNH, không phải giá của mã có thật, không phải biểu phí áp dụng chung, cũng không phải khuyến nghị mua hay bán. "
            "Giọng đọc tổng hợp; nội dung do kênh biên soạn từ nguồn công khai.",
            "Lưu ý nguồn: quy tắc lô chẵn, lô lẻ, nấc giá và biên độ lấy từ tài liệu hướng dẫn của Sở giao dịch chứng khoán TP.HCM (tháng 2/2026). Cách đọc bảng giá theo nghìn đồng "
            "và lưu ý về bảng lô lẻ lấy từ bài hướng dẫn của công ty chứng khoán, chưa đối chiếu văn bản của Sở. Cách tính sức mua và phí tối thiểu mỗi lệnh tùy từng nơi mở tài khoản. "
            "Quy định có thể thay đổi: hãy kiểm tra quy định và biểu phí hiện hành trước khi giao dịch.",
        ],
        "chapter_titles": {"ch00": "Mở đầu: hai lần bị từ chối", "ch01": "Con số trên bảng không phải là đồng",
                           "ch02": "Lô một trăm cổ phiếu", "ch03": "Ba mức giá, một khoản mười triệu",
                           "ch04": "Lô lẻ: cánh cửa có giá", "ch05": "Bỏ trứng vào giỏ nào",
                           "ch06": "Quỹ ETF: một lệnh chạm nhiều mã", "ch07": "Phiếu mười triệu đồng"},
        "sources": SOURCES,
        "hashtags": ["TàiChínhCáNhân", "ChứngKhoán", "LôChẵn", "BiểuĐồBiếtNói"],
        "tags": ["10 triệu mua được gì", "lô chẵn lô lẻ", "mua cổ phiếu bằng 10 triệu", "quỹ ETF cho người mới", "đơn vị yết giá",
                 "chứng khoán cho người mới", "vốn nhỏ chứng khoán", "tài chính cá nhân", "biểu đồ biết nói"],
        "category": "27", "thumb": "t1.jpg",
        "data_credit": "📊 SỐ LIỆU: số tài khoản theo báo chí tổng hợp (VSDC, 11/2026); quy tắc lô, nấc giá, biên độ theo tài liệu hướng dẫn của Sở giao dịch (2/2026); phép tính sức mua do kênh tự lập (ví dụ giả định).",
        "video_credits": "Ảnh và video minh họa chung do AI tạo (không mô tả người hay sự kiện thật). Ảnh tư liệu: Wikimedia Commons, giấy phép ghi trong phần ghi công.",
    },
}


def main():
    spread_images(CH)
    SPEC["imgs"] = {k: v for k, v in IMGS_ALL.items() if k in _used_imgs()}
    # Lead 13/11: cổng mức nhạc final — nhạc dưới giọng > 18 dB ở mọi chương (như bài 10).
    SPEC["mix_levels"] = {"CK": {"gain": 0.35, "threshold": 0.08, "ratio": 3.0}}
    SPEC["approved"] = "13/11/2026 — rule chủ kênh: video xong tự chọn khung giờ thích hợp, scheduled public, không cần đợi"
    # Lead chọn lại khung giờ khi đăng: Thứ Hai 07/12/2026 20:00 VN (slot CK Long Hai/Tư/Sáu) — kiểm lịch trước khi upload.
    SPEC.setdefault("youtube", {}).update({"publish_at": "2026-12-07T13:00:00Z", "playlist": "Chứng Khoán Từ Số 0", "thumb": "t1.jpg"})
    (D / "spec.json").write_text(json.dumps(SPEC, ensure_ascii=False, indent=1), encoding="utf-8")
    for name, c in CH.items():
        p = D / f"{name}.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d.update(c)
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("spec +", len(CH), "chuong")


if __name__ == "__main__":
    main()
