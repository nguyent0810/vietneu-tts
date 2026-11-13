"""Sinh spec.json + scenes/hud/bgm của từng chNN.json cho video dài MIM "20 phút mất 6,3 tỷ đô trên Binance" (chuỗi Công nghệ quanh ta).

    python data/long/mim-binance-6-3-ty-20-phut/gen_scenes.py     # giữ nguyên "lines" + "title" (do motion/long/script_lines.py ghi)

Kịch bản + nguồn: script.md, factcheck.md. Sự kiện còn đang điều tra (13/11/2026): mọi con số trên hình ghi rõ của hãng nào (TRM Labs, Elliptic,
CoinDesk, Halborn, The Block, TechCrunch, VnExpress, Reuters qua NBC, Binance). Giờ trên hình là giờ UTC (ghi "UTC"); 3 giờ sáng 30/10 ở Hà Nội = 20:05 UTC 29/10.
Ảnh: chỉ Wikimedia Commons PD / CC0 / CC BY (tên "File:…" trong IMGS, ghi công tự động ở khung hình + video_credits). Không logo Binance/Tether/Circle, không
ảnh người thật (Richard Teng, Kim Yo Jong, Jonathan Levin hiện bằng thẻ chữ). Ảnh/clip minh hoạ chung có nhãn `illus` ở góc khung, không phải hiện trường.
Clip: Pexels (ngang), gắn "VIDEO MINH HỌA". Ba câu [TRÍCH DỊCH] dùng cảnh quote (giọng Ngọc Huyền, nhãn "GIỌNG ĐỌC MINH HỌA").
"""
import json
import urllib.parse
from pathlib import Path

D = Path(__file__).resolve().parent
SAY = {
    "binance": "Bai-nân", "=TRM": "ti a em", "labs": "Láp", "halborn": "Han-bon", "elliptic": "I-líp-tích", "tether": "Tê-thơ", "circle": "Xơ-cồ",
    "ripple": "Rịp-pồ", "world": "Oơn", "liberty": "Líp-bơ-ti", "stablecoin": "xtây-bồ-coin", "=XRP": "ếch a pê", "=USDT": "u ét đi ti",
    "=USDC": "u ét đi xi", "=ETH": "i-thơ", "=BTC": "bi ti xi", "bitcoin": "Bít-coin", "ether": "I-thơ", "ethereum": "I-thi-ri-âm",
    "solana": "Xô-la-na", "optimism": "Óp-ti-mích", "base": "Bây", "arbitrum": "A-bi-trum", "avalanche": "A-va-lanh", "polygon": "Pô-li-gôn",
    "tornado": "Tooc-nây-đô", "cash": "Két", "pectra": "Péc-tra", "immunefi": "I-miu-phai", "reuters": "Roi-tơ", "techcrunch": "Téc-crăn",
    "coindesk": "Coin-đét", "vnexpress": "Vi-en-ếch-prét", "the": "Đờ", "block": "Blóc", "bybit": "Bai-bít", "=FBI": "ép bi ai",
    "tradertraitor": "trây-đơ trây-tơ", "lazarus": "La-da-rút", "kim": "Kim", "yo": "Yô", "jong": "Giong", "chainalysis": "Chen-ná-li-xít",
    "jonathan": "Giô-na-than", "levin": "Lê-vin", "richard": "Ri-chớt", "teng": "Tâng", "=SAFU": "xa-phu", "=UTC": "u ti xi",
    "bình": "Bình", "nhưỡng": "Nhưỡng",
}

# ---- ảnh Commons (PD / CC0 / CC BY). Khoá -> tên tệp; credit (tác giả, giấy phép) chép ở CREDITS cho video_credits.
IMGS = {
    "hanoi": "File:Hanoi at night.jpg",
    "hanoi2": "File:Night in Hanoi, Vietnam.jpg",
    "tech": "File:Technician with laptop working on server rack at NERSC.jpg",
    "rack": "File:Rear of rack at NERSC data center - closeup.jpg",
    "dc": "File:Datacenter Server Racks (22370909788).jpg",
    "vault": "File:Bank vault at a Goodwill - February 2022 - Sarah Stierch.jpg",
    "vaultOld": "File:Bank of Gage (Oklahoma) vault door 1.JPG",
    "safeBox": "File:Safe deposit boxes in Japan 2024-12-19.jpg",
    "typing": "File:Typing on a laptop (Unsplash).jpg",
    "coin": "File:Casascius coin.jpg",
    "seal": "File:1842 wax seal of hat maker guild in Sombor.jpg",
    "padlock": "File:Padlock and chain 0675.jpg",
    "brake": "File:Close view of a bicycle brake lever and handle grip against a background of wooden logs.jpg",
    "fbi": "File:FBI Headquarters - J. Edgar Hoover Building (53840035941).jpg",
    "stopwatch": "File:Stoppuhr hanhart.jpg",
}
CC0 = ("CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/")
BY20 = ("CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/")
CREDITS = {  # khoá: (tác giả, (giấy phép, URL giấy phép))
    "hanoi": ("cloud.shepherd", BY20), "hanoi2": ("cloud.shepherd", BY20),
    "tech": ("Derrick Coetzee", CC0), "rack": ("Derrick Coetzee", CC0), "dc": ("Carl Lender", BY20),
    "vault": ("Missvain", ("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/")), "vaultOld": ("Ammodramus", CC0), "safeBox": ("Asanagi", CC0),
    "typing": ("Simon Hattinga Verschure (webmarbles)", CC0), "coin": ("Steve Jurvetson", BY20),
    "seal": ("Ravnoplov (bản quét)", ("Public domain", "")), "padlock": ("Dori", ("CC BY 2.5", "https://creativecommons.org/licenses/by/2.5/")),
    "brake": ("Shixart1985", BY20), "fbi": ("ajay_suresh", BY20), "stopwatch": ("StefanPohl", ("Public domain", "")),
}
# Nhãn góc khung (kiểu phụ đề phim): ảnh/clip minh hoạ chung không phải hiện trường vụ việc.
ILL = {
    "hanoi": "HÀ NỘI BAN ĐÊM · ẢNH MINH HỌA", "hanoi2": "HÀ NỘI BAN ĐÊM · ẢNH MINH HỌA",
    "tech": "PHÒNG MÁY CHỦ · ẢNH MINH HỌA, KHÔNG PHẢI BINANCE", "rack": "TỦ MÁY CHỦ · ẢNH MINH HỌA, KHÔNG PHẢI BINANCE",
    "dc": "TRUNG TÂM DỮ LIỆU · ẢNH MINH HỌA, KHÔNG PHẢI BINANCE", "vault": "KÉT SẮT · ẢNH MINH HỌA", "vaultOld": "CỬA KÉT NGÂN HÀNG CŨ · ẢNH MINH HỌA",
    "safeBox": "KÉT SẮT NGÂN HÀNG · ẢNH MINH HỌA", "typing": "ẢNH MINH HỌA", "coin": "ĐỒNG BITCOIN VẬT LÝ · ẢNH MINH HỌA",
    "seal": "CON DẤU SÁP NĂM 1842 · ẢNH MINH HỌA", "padlock": "Ổ KHÓA · ẢNH MINH HỌA", "brake": "TAY PHANH XE ĐẠP · ẢNH MINH HỌA",
    "fbi": "TRỤ SỞ FBI, WASHINGTON · ẢNH TƯ LIỆU", "stopwatch": "ĐỒNG HỒ BẤM GIỜ · ẢNH MINH HỌA",
}
VM = "VIDEO MINH HỌA · KHÔNG PHẢI HIỆN TRƯỜNG VỤ VIỆC"
# Clip Pexels (ngang): id -> (tác giả, giây)
CLIPS = {
    "9160920": ("emirkhan bal", 32), "34796502": ("Nothing Ahead", 28), "35008786": ("Nicola Narracci", 10), "5909916": ("cottonbro studio", 22),
    "6266262": ("Tima Miroshnichenko", 11), "5028622": ("ALL IZ Well", 32), "30263260": ("aksinfo7 universe", 34), "854323": ("Pixabay", 30),
    "7849220": ("Ron Lach", 33),
}
# Lead 13/11: máy sản xuất không có Pexels key -> thay bằng clip Pexels đã có sẵn trên đĩa (Long khác).
CLOCK, HACK, FLOW, VAULTV, CHAIN, CITY, CODE, GLITCH, CIRCUIT, NODES, STAMPS = "9160920", "34796502", "35008786", "5909916", "5028622", "30263260", "5028622", "854323", "7849220", "35008786", "6266262"


def A(line, word=None, n=0, off=0.0):
    """Mốc neo: câu `line` (từ `word`, lần thứ n+1, lệch off giây); không có word/off thì đầu câu."""
    if word is None and not off:
        return line
    return [line, word, n, off] if (n or off or word is None) else [line, word]


def S(line, off):
    """Mốc cách đầu câu `off` giây (cho phần tử con thứ nhất/thứ hai: phải hiện trong 1 giây đầu cảnh)."""
    return [line, None, 0, off]


CH = {}

# ---------------------------------------------------------------- CH00 · Ba giờ sáng ở Hà Nội
CH["ch00"] = {"hud": {"k": "MỞ ĐẦU", "t": "BA GIỜ SÁNG Ở HÀ NỘI"}, "bgm": {"mood": "mystery", "gain": 0.10}, "scenes": [
    {"type": "photo", "at": 0, "img": "hanoi", "cam": "push_in", "veil": 0.35,
     "label": {"k": "HÀ NỘI · 03:00 SÁNG", "v": "NGÀY 30.10.2026", "s": "= 20:05 UTC · 29.10", "at": A(0, "Ba")}},
    {"type": "counter", "at": 1, "from": 0, "to": 233.46, "suffix": " TRIỆU XRP", "label": "NĂM VÍ · MỘT ĐỊA CHỈ · BỐN PHÚT",
     "sub": {"text": "THEO VNEXPRESS · HALBORN", "at": S(1, 2.2)}, "vid": FLOW},
    {"type": "kinetic", "at": 2, "items": [{"text": "NHIỀU CHUỖI KHỐI", "at": 2, "acc": True}, {"text": "cùng một đêm", "at": S(2, 1.2), "sm": True}], "vid": CIRCUIT},
    {"type": "counter", "at": 3, "from": 0, "to": 20, "suffix": " PHÚT", "label": "PHẦN LỚN SỐ TIỀN RỜI ĐI · THEO TRM LABS", "vid": CLOCK, "ms": 4},
    {"type": "counter", "at": 4, "from": 0, "to": 6.3, "suffix": " TỶ USD", "label": "TÀI SẢN BỊ ẢNH HƯỞNG · THEO BINANCE", "bg": "dc"},
    {"type": "question", "at": 5, "text": "Một sàn nhiều lớp khóa,\nsao kho mở toang trong 20 phút?", "bg": "vault"},
    {"type": "myth", "at": 6, "mythLab": "TƯỞNG LÀ", "myth": "20 PHÚT LÀ CHI TIẾT LẠ NHẤT", "truthLab": "TRM LABS NÓI", "truth": "CHUẨN BỊ TỪ 36 GIỜ TRƯỚC",
     "strikeAt": A(6, "phút"), "truthAt": A(7, "ít"), "bg": "rack"},
    {"type": "kinetic", "at": 8, "items": [{"text": "DƯỚI MỘT GIỜ", "at": 8, "acc": True}, {"text": "stablecoin đã bị khóa phần rất lớn", "at": A(8, "phát"), "sm": True}], "vid": CHAIN},
    {"type": "slam", "at": 9, "text": "KHÔNG AI KHÓA NỔI?", "sub": "VẬY HỌ LÀM BẰNG CÁCH NÀO?", "vid": VAULTV},
    {"type": "timeline", "at": 11, "title": "THEO ĐÚNG ĐỒNG HỒ CỦA ĐÊM ẤY", "items": [
        {"year": "36 GIỜ TRƯỚC", "text": "dàn dựng", "at": S(11, 0.2)}, {"year": "20:05 UTC", "text": "tiền rời ví nóng", "at": S(11, 0.8)},
        {"year": "SAU 20 PHÚT", "text": "phần lớn đã đi", "at": A(11, "đêm")}, {"year": "DƯỚI 1 GIỜ", "text": "stablecoin bị khóa", "at": A(12, "bắt")},
        {"year": "01.11", "text": "sàn mở lại việc rút", "at": S(12, 1.3)}]},
]}

# ---------------------------------------------------------------- CH01 · Một con số, ba cách đếm
CH["ch01"] = {"hud": {"k": "CHƯƠNG 01", "t": "MỘT CON SỐ, BA CÁCH ĐẾM"}, "bgm": {"mood": "curious", "gain": 0.11}, "scenes": [
    {"type": "chapter", "no": "1", "k": "CHƯƠNG MỘT", "title": "MỘT CON SỐ,\nBA CÁCH ĐẾM", "sub": "TRM LABS · ELLIPTIC · BINANCE", "bg": "safeBox", "focus": [0.5, 0.4], "titleAt": A(0, "Trước")},
    {"type": "bars", "at": 1, "title": "BYBIT 2025 · BINANCE 2026", "unit": "TỶ USD · THE BLOCK · VNEXPRESS",
     "label": {"k": "NHƯNG", "v": "QUY MÔ ĐƯỢC CÁC BÊN CÔNG BỐ KHÁC NHAU", "at": A(3, "Nhưng")},
     "items": [{"k": "BYBIT · 2025", "v": 1.5, "lbl": "1,5", "at": S(1, 0.3)}, {"k": "BINANCE · 2026", "v": 6.3, "lbl": "6,3", "acc": True, "at": A(2, "Lần")}]},
    {"type": "bars", "at": 4, "title": "BA CÁCH ĐẾM MỘT VỤ", "unit": "TỶ USD · THEO TỪNG BÊN",
     "items": [{"k": "TRM LABS", "v": 6.36, "lbl": "6,36", "at": S(4, 0.3)}, {"k": "ELLIPTIC", "v": 6.43, "lbl": "6,43", "at": S(5, 0.3)},
               {"k": "BINANCE (KHOẢNG)", "v": 6.3, "lbl": "6,3", "acc": True, "at": A(6, "khoảng")}]},
    {"type": "slam", "at": A(6, "và"), "text": "6,34 TỶ ĐỂ BÙ", "sub": "TIỀN CỦA CÔNG TY · THEO BINANCE"},
    {"type": "kinetic", "at": 7, "items": [{"text": "KHOẢNG 6,3 TỶ ĐÔ", "at": 7, "acc": True}, {"text": "mức mình dùng cho cả video", "at": S(7, 1.8), "sm": True}], "vid": CIRCUIT},
    {"type": "source", "at": 8, "source": "TRM LABS · TIÊU ĐỀ BÀI VIẾT", "ref": "CÁCH TRM GỌI VỤ NÀY (DIỄN Ý)",
     "snippet": "Binance, 6,36 tỷ USD · [[vụ hack lớn nhất lịch sử]]", "hlAt": A(8, "lớn"), "seal": "LÀ CÁCH GỌI CỦA TRM", "sealAt": A(8, "cách")},
    {"type": "question", "at": 9, "text": "Tiền nằm ở đâu\nmà bị rút nhanh thế?", "bg": "dc"},
    {"type": "org", "at": 11, "nodes": [
        {"id": "kho", "t": "KHO TIỀN KHÁCH", "s": "CỦA MỘT SÀN", "at": S(11, 0.2), "cls": "top"},
        {"id": "lanh", "t": "VÍ LẠNH", "s": "TẮT MẠNG", "p": "kho", "at": S(11, 0.7)},
        {"id": "nong", "t": "VÍ NÓNG", "s": "NỐI MẠNG · TRẢ LỆNH RÚT", "p": "kho", "at": A(11, "nóng"), "cls": "acc"}]},
    {"type": "split", "at": 12, "title": "ĐÁNH ĐỔI", "sign": "CÀNG TIỆN, CÀNG DỄ BỊ NHẮM", "signAt": A(12, "càng"),
     "a": {"img": "safeBox", "label": "VÍ LẠNH · TẮT MẠNG", "tone": "color", "at": S(12, 0.2)},
     "b": {"img": "rack", "label": "VÍ NÓNG · NỐI MẠNG", "tone": "color", "at": S(12, 0.5)}},
    {"type": "slam", "at": 13, "text": "VÍ NÓNG BỊ RÚT", "sub": "ĐÊM ẤY", "vid": CITY, "ms": 4},
    {"type": "photo", "at": 14, "img": "padlock", "cam": "dolly", "label": {"k": "BẢO VỆ VÍ LUÔN KẾT NỐI", "v": "CÂU HỎI MÀ VỤ TRỘM ĐẶT RA", "at": A(14, "cách")}},
    {"type": "kinetic", "at": 15, "items": [{"text": "ĐẰNG SAU CÚ RÚT", "at": 15, "acc": True}, {"text": "là một giai đoạn chuẩn bị", "at": S(15, 1.2), "sm": True}], "vid": CODE, "ms": 2},
]}

# ---------------------------------------------------------------- CH02 · Ba mươi sáu tiếng trước giờ G
CH["ch02"] = {"hud": {"k": "CHƯƠNG 02", "t": "BA MƯƠI SÁU TIẾNG TRƯỚC GIỜ G"}, "bgm": {"mood": "calm", "gain": 0.11}, "scenes": [
    {"type": "chapter", "no": "2", "k": "CHƯƠNG HAI", "title": "BA MƯƠI SÁU TIẾNG\nTRƯỚC GIỜ G", "sub": "TRM LABS · GIAI ĐOẠN DÀN DỰNG", "vid": CLOCK, "ms": 12, "titleAt": A(0, "Theo")},
    {"type": "ledger", "at": 2, "title": "DÀN DỰNG · 36 GIỜ TRƯỚC", "rows": [
        {"k": "VÍ ĐIỀU HÀNH", "v": "NẠP BẰNG KHOẢN NHỎ", "at": S(2, 0.3)}, {"k": "NGUỒN", "v": "TORNADO CASH", "at": S(2, 0.8)}],
     "total": {"k": "TORNADO CASH", "v": "DỊCH VỤ TRỘN TIỀN", "at": A(3, "dịch")}},
    {"type": "org", "at": 4, "nodes": [
        {"id": "g", "t": "DÀN DỰNG", "s": "TRƯỚC KHI TIỀN RỜI VÍ NÓNG", "at": S(4, 0.2), "cls": "top"},
        {"id": "op", "t": "VÍ ĐIỀU HÀNH", "s": "NẠP TIỀN TỪ TORNADO CASH", "p": "g", "at": S(4, 0.7)},
        {"id": "ba", "t": "BA VÍ KHÁC", "s": "CÀI VÀ CHẠY THỬ MÃ", "p": "g", "at": A(4, "ba"), "cls": "acc"}]},
    {"type": "myth", "at": 6, "mythLab": "TƯỞNG LÀ", "myth": "SÀN ĐÃ BỊ THỬ KHÓA", "truthLab": "THỰC RA", "truth": "CHỈ LÀ GIAO DỊCH THỬ",
     "strikeAt": S(6, 0.3), "truthAt": A(6, "không"), "bg": "tech"},
    {"type": "date", "at": 7, "day": "ĐÊM · THEO HALBORN", "date": "28-29.10", "sub": {"text": "NẠP TIỀN VÀ THỬ MỘT HỢP ĐỒNG THÔNG MINH", "at": A(7, "ví")}, "vid": HACK, "ms": 2},
    {"type": "kinetic", "at": 8, "items": [{"text": "HỢP ĐỒNG THÔNG MINH", "at": 8, "acc": True}, {"text": "đoạn mã chạy ngay trên chuỗi khối", "at": A(8, "đoạn"), "sm": True}], "vid": CODE, "ms": 6},
    {"type": "ledger", "at": 9, "title": "DẤU VẾT CÔNG KHAI", "rows": [
        {"k": "TRƯỚC VỤ TRỘM", "v": "GIAO DỊCH THỬ", "at": S(9, 0.3)}, {"k": "SAU VỤ TRỘM", "v": "DẤU VẾT ĐỂ XEM LẠI", "at": S(9, 0.8)}],
     "total": {"k": "AI XEM LẠI?", "v": "CÁC HÃNG PHÂN TÍCH", "at": A(10, "hãng")}},
    {"type": "photo", "at": 11, "img": "rack", "focus": [0.5, 0.4], "cam": "tilt_up", "label": {"k": "DỮ LIỆU CÔNG KHAI", "v": "CÁC HÃNG LẦN LẠI TRÌNH TỰ ĐÊM ẤY", "at": A(11, "các")}},
    {"type": "question", "at": 12, "text": "Binance chưa công bố báo cáo cuối.\nĐiều bạn nghe chưa phải toàn bộ.", "vid": CIRCUIT, "ms": 4},
]}

# ---------------------------------------------------------------- CH03 · Hai mươi phút
CH["ch03"] = {"hud": {"k": "CHƯƠNG 03", "t": "HAI MƯƠI PHÚT"}, "bgm": {"mood": "mystery", "gain": 0.11}, "scenes": [
    {"type": "chapter", "no": "3", "k": "CHƯƠNG BA", "title": "HAI MƯƠI PHÚT", "sub": "29.10.2026 · TỪ 20:05 UTC", "bg": "hanoi2", "titleAt": A(0, "Hai")},
    {"type": "date", "at": 1, "day": "UTC · NGÀY 29.10.2026", "date": "20:05", "sub": {"text": "NĂM VÍ XRP · MỘT ĐỊA CHỈ", "at": A(1, "gửi")}, "vid": FLOW, "ms": 0},
    {"type": "org", "at": 2, "nodes": [
        {"id": "v", "t": "VÍ NÓNG BINANCE", "s": "XUẤT PHÁT 20:05 UTC", "at": S(2, 0.2), "cls": "top"},
        {"id": "sol", "t": "SOLANA", "s": "20:10 UTC", "p": "v", "at": S(2, 0.7)},
        {"id": "op", "t": "OPTIMISM", "s": "CÙNG ĐỢT", "p": "v", "at": S(2, 1.6)},
        {"id": "ba", "t": "BASE", "s": "CÙNG ĐỢT", "p": "v", "at": S(2, 2.0)},
        {"id": "ar", "t": "ARBITRUM", "s": "VÀ TIẾP TỤC", "p": "v", "at": S(2, 2.4)}]},
    {"type": "counter", "at": 3, "from": 0, "to": 18270, "suffix": " BTC", "label": "20:20 UTC · MỘT VÍ BITCOIN GỬI ĐI", "sub": {"text": "THEO HALBORN", "at": A(3, "một")}, "bg": "coin"},
    {"type": "kinetic", "at": 4, "items": [{"text": "CHIA THÀNH NHIỀU PHẦN NHỎ", "at": 4, "acc": True}, {"text": "để khó lần theo · VnExpress", "at": A(4, "để"), "sm": True}], "vid": NODES, "ms": 1},
    {"type": "slam", "at": 5, "text": "ỦY QUYỀN", "sub": "MỘT CƠ CHẾ TRÊN ETHEREUM", "bg": "typing"},
    {"type": "timeline", "at": 6, "title": "TỪ PECTRA ĐẾN VỤ TRỘM", "items": [
        {"year": "05.2025", "text": "nâng cấp Pectra", "at": S(6, 0.3)}, {"year": "SAU ĐÓ", "text": "ví thường ủy quyền cho mã chạy thay", "at": S(6, 0.8)},
        {"year": "EIP-7702", "text": "tên kỹ thuật · theo Halborn", "at": A(6, "một")}]},
    {"type": "counter", "at": 7, "from": 0, "to": 50, "suffix": " CHỮ KÝ", "label": "CHUẨN BỊ SẴN · THEO THE BLOCK"},
    {"type": "units", "at": 8, "title": "50 CHỮ KÝ ỦY QUYỀN SOẠN SẴN", "total": 50, "cols": 10, "lit": 1, "litAt": A(8, "ít"), "unitLabel": "ÍT NHẤT MỘT CÒN HIỆU LỰC · THE BLOCK"},
    {"type": "counter", "at": 9, "from": 0, "to": 130, "suffix": " DÒNG MÃ", "label": "ĐOẠN MÃ HÚT TIỀN · THEO IMMUNEFI", "vid": HACK, "ms": 8},
    {"type": "org", "at": 10, "nodes": [
        {"id": "w", "t": "VÍ NÓNG", "s": "CHỦ SỞ HỮU CỦA MÃ", "at": S(10, 0.2), "cls": "top"},
        {"id": "u", "t": "ỦY QUYỀN", "s": "50 CHỮ KÝ SOẠN SẴN", "p": "w", "at": S(10, 0.7)},
        {"id": "m", "t": "MÃ HÚT TIỀN", "s": "CHẠY NHƯ CHÍNH VÍ · HALBORN", "p": "u", "at": A(10, "khiến"), "cls": "acc"}]},
    {"type": "ledger", "at": 11, "title": "20:24 UTC · LẦN QUÉT ĐẦU TIÊN", "rows": [
        {"k": "USDT", "v": "KHOẢNG 1,6 TỶ", "at": S(11, 0.3)}, {"k": "ETH", "v": "167.464", "at": S(11, 0.9)}],
     "total": {"k": "NGUỒN", "v": "DÒNG THỜI GIAN HALBORN", "at": A(11, "cùng")}},
    {"type": "source", "at": 12, "source": "HALBORN · PHÂN TÍCH VỤ BINANCE", "ref": "DÒNG THỜI GIAN · GIỜ UTC",
     "snippet": "[[20:24 UTC]] · lần quét đầu tiên lấy khoảng 1,6 tỷ USDT và 167.464 ETH", "hlAt": A(12, "dòng"), "seal": "SỐ LIỆU CỦA HALBORN", "sealAt": A(12, "phân")},
    {"type": "myth", "at": 13, "mythLab": "TƯỞNG LÀ", "myth": "20 PHÚT LÀ TOÀN BỘ", "truthLab": "THỰC RA", "truth": "20 PHÚT LÀ PHẦN LỚN", "strikeAt": A(13, "khung"), "truthAt": A(13, "chỉ"),
     "vid": GLITCH},
    {"type": "date", "at": 14, "day": "ĐỢT HAI · AVALANCHE · POLYGON", "date": "23:05", "sub": {"text": "UTC · THEO HALBORN", "at": A(14, "sau")}, "bg": "hanoi"},
    {"type": "timeline", "at": 15, "title": "NGÀY 29–30.10 · GIỜ UTC", "items": [
        {"year": "20:05 UTC", "text": "bắt đầu rút", "at": S(15, 0.3)}, {"year": "23:05 UTC", "text": "đợt hai", "at": S(15, 0.8)},
        {"year": "23:56 UTC", "text": "kết thúc · theo Elliptic", "at": A(15, "gần")}, {"year": "00:10 UTC", "text": "gỡ ủy quyền · 30.10", "at": A(16, "gỡ")}]},
    {"type": "slam", "at": A(16, "khỏi"), "text": "GẦN BỐN TIẾNG", "sub": "TỪ LÚC CÀI ĐẾN LÚC GỠ", "bg": "stopwatch"},
]}

# ---------------------------------------------------------------- CH04 · Cánh cửa nào đã mở
CH["ch04"] = {"hud": {"k": "CHƯƠNG 04", "t": "CÁNH CỬA NÀO ĐÃ MỞ"}, "bgm": {"mood": "mystery", "gain": 0.11}, "scenes": [
    {"type": "chapter", "no": "4", "k": "CHƯƠNG BỐN", "title": "CÁNH CỬA NÀO\nĐÃ MỞ", "sub": "BINANCE NÓI GÌ · TRM NÓI GÌ", "bg": "vaultOld", "focus": [0.5, 0.4], "titleAt": A(0, "Vậy")},
    {"type": "photo", "at": 2, "img": "tech", "cam": "push_in", "label": {"k": "BINANCE NÓI · ĐIỀU TRA BAN ĐẦU", "v": "LAPTOP CỦA KỸ SƯ VẬN HÀNH BỊ CHIẾM QUYỀN", "at": A(2, "một")}},
    {"type": "ledger", "at": 3, "title": "BINANCE NÓI · ĐIỀU TRA BAN ĐẦU", "rows": [
        {"k": "VÙNG CHỨA DỊCH VỤ", "v": "TRUY CẬP TRÁI PHÉP", "at": S(3, 0.3)}, {"k": "MÁY KỸ SƯ", "v": "BỊ CHIẾM QUYỀN", "at": S(3, 0.8)}],
     "total": {"k": "KHÓA RIÊNG", "v": "CHƯA THẤY LỘ", "at": A(4, "chưa")}},
    {"type": "kinetic", "at": 5, "items": [{"text": "CÒN THÊM ĐIỂM XÂM NHẬP KHÁC", "at": 5, "acc": True}, {"text": "Binance · điều tra sau đó", "at": A(5, "điều"), "sm": True}], "bg": "typing"},
    {"type": "source", "at": 6, "source": "REUTERS · 31.10.2026", "ref": "RICHARD TENG · NGƯỜI ĐỨNG ĐẦU BINANCE", "snippet": "gọi đây là [[một cuộc tấn công phức tạp]]",
     "hlAt": A(6, "tấn"), "seal": "DIỄN Ý · KHÔNG PHẢI NGUYÊN VĂN", "sealAt": A(6, "phức")},
    {"type": "kinetic", "at": 7, "items": [{"text": "PHẦN MỀM ĐỘC HẠI", "at": 7, "acc": True}, {"text": "dùng để xóa dấu vết · theo Reuters", "at": A(7, "độc"), "sm": True}], "vid": GLITCH},
    {"type": "org", "at": 8, "nodes": [
        {"id": "t", "t": "TRM LABS", "s": "NHÌN TỪ CHUỖI KHỐI", "at": S(8, 0.2), "cls": "top"},
        {"id": "h", "t": "HỆ THỐNG KÝ", "s": "CỦA VÍ NÓNG", "p": "t", "at": S(8, 0.7)},
        {"id": "x", "t": "BỊ XÂM PHẠM", "s": "THEO DẤU HIỆU TRM NÊU", "p": "h", "at": A(9, "xâm"), "cls": "acc"}]},
    {"type": "photo", "at": 10, "img": "seal", "cam": "push_in", "label": {"k": "HỆ THỐNG KÝ", "v": "GIỐNG CON DẤU CỦA SÀN", "s": "CHỮ KÝ HỢP LỆ = MẠNG CHO QUA", "at": A(10, "con")}},
    {"type": "myth", "at": 12, "mythLab": "TƯỞNG LÀ", "myth": "CHỮ KÝ GIẢ", "truthLab": "HALBORN NÓI", "truth": "CHỮ KÝ HỢP LỆ", "strikeAt": A(12, "phân"), "truthAt": A(12, "hợp"), "bg": "seal"},
    {"type": "org", "at": 13, "nodes": [
        {"id": "a", "t": "LỆNH RÚT", "s": "CỦA KẺ TẤN CÔNG", "at": S(13, 0.2), "cls": "top"},
        {"id": "b", "t": "HỆ THỐNG KÝ CỦA SÀN", "s": "CON DẤU", "p": "a", "at": S(13, 0.7)},
        {"id": "c", "t": "CHỮ KÝ HỢP LỆ", "s": "DO CHÍNH SÀN TẠO RA", "p": "b", "at": A(13, "chính")},
        {"id": "d", "t": "MẠNG CHẤP NHẬN", "s": "GIAO DỊCH", "p": "c", "at": A(13, "cho"), "cls": "acc"}]},
    {"type": "kinetic", "at": 14, "items": [{"text": "CHỮ KÝ ĐÚNG LUẬT", "at": 14, "acc": True}, {"text": "do chính hệ thống ký tạo ra", "at": A(14, "ngay"), "sm": True},
                                         {"text": "VẤN ĐỀ: HỆ THỐNG QUANH CHÌA KHÓA", "at": A(15, "hệ"), "sm": True}], "bg": "padlock"},
    {"type": "ledger", "at": 16, "title": "HAI VỤ · MỘT THẤT BẠI · THEO HALBORN", "rows": [
        {"k": "BYBIT · 2025", "v": "1,5 TỶ USD", "at": S(16, 0.3)}, {"k": "BINANCE · 2026", "v": "6,3 TỶ USD", "at": S(16, 0.8)}],
     "total": {"k": "TRM", "v": "LIÊN HỆ NHÓM SAU BYBIT", "at": A(17, "nhóm")}},
    {"type": "question", "at": 18, "text": "Nhóm ấy là ai?\nNhìn cả cáo buộc lẫn phủ nhận", "bg": "fbi"},
]}

# ---------------------------------------------------------------- CH05 · Chiếc phanh trong stablecoin
CH["ch05"] = {"hud": {"k": "CHƯƠNG 05", "t": "CHIẾC PHANH TRONG STABLECOIN"}, "bgm": {"mood": "curious", "gain": 0.11}, "scenes": [
    {"type": "chapter", "no": "5", "k": "CHƯƠNG NĂM", "title": "CHIẾC PHANH\nTRONG STABLECOIN", "sub": "TỪ 21:01 UTC · LỆNH KHÓA", "bg": "brake", "focus": [0.5, 0.4], "titleAt": A(0, "Theo")},
    {"type": "counter", "at": 1, "from": 0, "to": 971, "suffix": " TRIỆU USDT", "label": "21:01 UTC · TETHER KHÓA TRÊN ETHEREUM", "sub": {"text": "THEO HALBORN", "at": A(1, "khóa")}, "vid": CHAIN, "ms": 3},
    {"type": "ledger", "at": 2, "title": "KHÓA TRONG DƯỚI MỘT GIỜ · UTC", "rows": [
        {"k": "21:04 UTC · CIRCLE", "v": "823 TRIỆU USDC", "at": S(2, 0.3)}, {"k": "TETHER RA TAY", "v": "SAU 37 PHÚT", "at": S(2, 0.8)},
        {"k": "CIRCLE", "v": "SAU 41 PHÚT", "at": A(3, "còn")}]},
    {"type": "kinetic", "at": 4, "items": [{"text": "RIPPLE · WORLD LIBERTY", "at": 4, "acc": True}, {"text": "cũng khóa đồng tiền do họ phát hành", "at": A(4, "cũng"), "sm": True}], "bg": "padlock"},
    {"type": "slam", "at": 5, "text": "DANH SÁCH ĐEN", "sub": "VÍ NÓNG CỦA CHÍNH BINANCE · TETHER", "vid": STAMPS, "ms": 2},
    {"type": "ledger", "at": 6, "title": "AI KHÓA ĐƯỢC SỐ DƯ?", "rows": [
        {"k": "BITCOIN · ETHER", "v": "KHÔNG CÓ NHÀ PHÁT HÀNH", "at": S(6, 0.3)}, {"k": "USDT · USDC", "v": "CÓ NHÀ PHÁT HÀNH", "at": S(6, 0.9)}], "bg": "coin"},
    {"type": "kinetic", "at": 9, "items": [{"text": "STABLECOIN", "at": 9, "acc": True}, {"text": "tiền số do một công ty phát hành, neo giá vào đô la", "at": A(9, "tiền"), "sm": True}]},
    {"type": "org", "at": 10, "nodes": [
        {"id": "c", "t": "HỢP ĐỒNG THÔNG MINH", "s": "CỦA USDT · USDC", "at": S(10, 0.2), "cls": "top"},
        {"id": "f", "t": "MỘT HÀM CÓ SẴN", "s": "ĐƯA ĐỊA CHỈ VÀO DANH SÁCH ĐEN", "p": "c", "at": S(10, 0.7)},
        {"id": "i", "t": "NHÀ PHÁT HÀNH", "s": "ĐƯỢC PHÉP GỌI HÀM ẤY", "p": "f", "at": A(10, "cho"), "cls": "acc"}]},
    {"type": "slam", "at": 11, "text": "VÍ VẪN CÒN ĐÓ", "sub": "NHƯNG SỐ DƯ KHÔNG CHUYỂN ĐI ĐƯỢC NỮA", "bg": "vault"},
    {"type": "split", "at": 12, "title": "HAI QUYỀN KHÁC NHAU", "sign": "QUYỀN KHÓA = CÁI PHANH", "signAt": A(13, "quyền"),
     "a": {"img": "seal", "label": "QUYỀN KÝ · CỦA SÀN", "tone": "color", "at": S(12, 0.2)},
     "b": {"img": "brake", "label": "QUYỀN KHÓA · NHÀ PHÁT HÀNH", "tone": "color", "at": S(12, 0.5)}},
    {"type": "bars", "at": 14, "title": "BỊ KHÓA: MỖI BÊN ĐẾM MỘT KHÁC", "unit": "TỶ USD · THEO TỪNG NGUỒN",
     "items": [{"k": "COINDESK (HƠN)", "v": 2.4, "lbl": "2,4", "at": S(15, 0.3)}, {"k": "TRM LABS", "v": 2.7, "lbl": "2,7", "at": S(16, 0.3)}]},
    {"type": "bars", "at": 17, "title": "BA CON SỐ VỀ PHẦN BỊ KHÓA", "unit": "TỶ USD · COINDESK · TRM · ELLIPTIC",
     "label": {"k": "GẦN MỘT NỬA", "v": "44% SỐ TIỀN BỊ TRỘM · THEO ELLIPTIC", "at": A(18, "gọn")},
     "items": [{"k": "COINDESK (HƠN)", "v": 2.4, "lbl": "2,4", "at": S(17, 0.3)}, {"k": "TRM LABS", "v": 2.7, "lbl": "2,7", "at": S(17, 0.7)},
               {"k": "ELLIPTIC", "v": 2.84, "lbl": "2,84", "acc": True, "at": A(17, "khoảng")}]},
    {"type": "slam", "at": 19, "text": "ĐÓNG BĂNG KHÔNG PHẢI LÀ LẤY LẠI", "sub": "HALBORN NHẤN MẠNH", "vid": VAULTV},
    {"type": "photo", "at": 21, "img": "safeBox", "focus": [0.5, 0.5], "cam": "tilt_up", "label": {"k": "SAU KHI ĐÓNG BĂNG", "v": "NẰM YÊN TRONG VÍ KẺ TRỘM", "s": "CHỜ NHÀ PHÁT HÀNH XỬ LÝ THEO TRÌNH TỰ PHÁP LÝ", "at": A(21, "nằm")}},
]}

# ---------------------------------------------------------------- CH06 · Chạy đua với lệnh khóa
CH["ch06"] = {"hud": {"k": "CHƯƠNG 06", "t": "CHẠY ĐUA VỚI LỆNH KHÓA"}, "bgm": {"mood": "mystery", "gain": 0.11}, "scenes": [
    {"type": "chapter", "no": "6", "k": "CHƯƠNG SÁU", "title": "CHẠY ĐUA VỚI\nLỆNH KHÓA", "sub": "ĐÊM 29.10 · THEO GIỜ UTC", "bg": "hanoi", "titleAt": A(0, "Trong")},
    {"type": "bars", "at": 2, "title": "ĐỔI STABLECOIN SANG ETHER", "unit": "TRIỆU USD · THEO ELLIPTIC",
     "items": [{"k": "STABLECOIN ĐỔI RA", "v": 325, "lbl": "325", "at": S(2, 0.5)}, {"k": "ETHER NHẬN VỀ", "v": 285, "lbl": "285", "acc": True, "at": A(3, "nhận")}]},
    {"type": "ledger", "at": 4, "title": "ĐỔI ĐỂ TRÁNH BỊ KHÓA", "rows": [
        {"k": "STABLECOIN", "v": "NHÀ PHÁT HÀNH KHÓA ĐƯỢC", "at": S(4, 0.3)}, {"k": "ETHER", "v": "KHÔNG CÓ AI ĐỂ KHÓA", "at": S(4, 0.8)}],
     "total": {"k": "THE BLOCK", "v": "ĐỔI CÓ VẺ ĐỂ TRÁNH KHÓA", "at": A(4, "có")}, "bg": "stopwatch"},
    {"type": "counter", "at": 6, "from": 0, "to": 26, "suffix": "%", "label": "MỨC LỖ CÓ THỂ LÊN TỚI · THEO THE BLOCK",
     "sub": {"text": "SO VỚI GIÁ THỊ TRƯỜNG · CÁI GIÁ CỦA VIỆC ĐỔI", "at": A(7, "cho")}},
    {"type": "kinetic", "at": 8, "items": [{"text": "ĐỔI ĐỂ TRÁNH BỊ KHÓA", "at": 8, "acc": True}, {"text": "có vẻ nhằm vậy · theo The Block", "at": A(8, "việc"), "sm": True}], "bg": "coin"},
    {"type": "org", "at": 9, "nodes": [
        {"id": "r", "t": "PHẦN CÒN LẠI", "s": "THEO TRM VÀ ELLIPTIC", "at": S(9, 0.2), "cls": "top"},
        {"id": "e", "t": "ETH", "s": "KHÔNG CÓ NHÀ PHÁT HÀNH", "p": "r", "at": S(9, 0.7)},
        {"id": "b", "t": "BTC", "s": "CŨNG KHÔNG AI KHÓA ĐƯỢC", "p": "r", "at": A(9, "BTC"), "cls": "acc"}]},
    {"type": "bars", "at": 10, "title": "KẺ TẤN CÔNG CÒN GIỮ", "unit": "TỶ USD · THEO TRM · ELLIPTIC",
     "items": [{"k": "TRM LABS", "v": 2.4, "lbl": "2,4", "at": S(10, 0.3)}, {"k": "ELLIPTIC", "v": 3.0, "lbl": "3,0", "acc": True, "at": A(10, "ba")}]},
    {"type": "date", "at": 11, "day": "FBI RA THÔNG BÁO", "date": "31.10.2026", "sub": {"text": "THEO COINDESK · NBC (REUTERS)", "at": A(11, "ra")}, "bg": "fbi"},
    {"type": "source", "at": 12, "source": "FBI · QUA COINDESK · 31.10.2026", "ref": "VỤ BINANCE · 29.10.2026", "snippet": "Triều Tiên chịu trách nhiệm về [[vụ trộm hơn 6 tỷ USD]] tài sản số",
     "hlAt": A(12, "trách"), "seal": "KẾT LUẬN CỦA FBI", "sealAt": A(12, "hơn")},
    {"type": "org", "at": 13, "nodes": [
        {"id": "l", "t": "NHÓM LAZARUS", "s": "THEO FBI QUA COINDESK", "at": S(13, 0.2), "cls": "top"},
        {"id": "t", "t": "TRADERTRAITOR", "s": "MỘT ĐƠN VỊ THUỘC NHÓM", "p": "l", "at": S(13, 0.7), "cls": "acc"}]},
    {"type": "ledger", "at": 14, "title": "FBI NÓI GÌ", "rows": [{"k": "ĐANG ĐỔI SANG", "v": "ETHER", "at": S(14, 0.3)}, {"k": "CÒN", "v": "RỬA TIẾP", "at": S(14, 0.8)}]},
    {"type": "bars", "at": 15, "title": "ĐỊA CHỈ TRONG DANH SÁCH", "unit": "THEO COINDESK",
     "items": [{"k": "ETHEREUM", "v": 600, "lbl": "HƠN 600", "at": S(15, 0.3)}, {"k": "BITCOIN", "v": 20, "lbl": "GẦN 20", "at": A(15, "gần")}, {"k": "SOLANA", "v": 1, "lbl": "1", "at": A(15, "một")}]},
    {"type": "photo", "at": 16, "img": "dc", "cam": "dolly", "label": {"k": "FBI ĐỀ NGHỊ KHU VỰC TƯ NHÂN", "v": "CHẶN GIAO DỊCH LIÊN QUAN CÁC ĐỊA CHỈ ẤY", "at": A(16, "chặn")}},
    {"type": "quote", "at": 18, "text": "Hãy chặn các giao dịch với, hoặc bắt nguồn từ, những địa chỉ mà các nhân vật TraderTraitor đang dùng để rửa số tài sản bị đánh cắp này.",
     "who": "FBI · QUA COINDESK", "note": "TRÍCH DỊCH · 31.10.2026"},
    {"type": "counter", "at": 19, "from": 0, "to": 3, "suffix": " HÃNG", "label": "TRM · ELLIPTIC · CHAINALYSIS", "sub": {"text": "ĐÃ GÁN CHO TIN TẶC TRIỀU TIÊN TRƯỚC ĐÓ", "at": A(19, "gán")}},
    {"type": "ledger", "at": 20, "title": "MỨC ĐỘ CHẮC CHẮN", "rows": [{"k": "TRM LABS", "v": "TIN Ở MỨC CAO", "at": S(20, 0.3)}, {"k": "ELLIPTIC", "v": "“NHIỀU KHẢ NĂNG”", "at": S(20, 0.8)}]},
    {"type": "date", "at": 22, "day": "KIM YO JONG BÁC BỎ", "date": "02.11.2026", "sub": {"text": "PHÍA BÌNH NHƯỠNG PHỦ NHẬN CÁO BUỘC", "at": A(23, "bác")}},
    {"type": "source", "at": 24, "source": "KIM YO JONG · 02.11.2026 · QUA THE BLOCK", "ref": "TUYÊN BỐ VỀ CÁO BUỘC CỦA FBI",
     "snippet": "FBI đang cố [[gán nhãn “quốc gia tội phạm mạng”]] cho Triều Tiên", "hlAt": A(24, "gán"), "seal": "DIỄN Ý", "sealAt": A(24, "tội")},
    {"type": "ledger", "at": 25, "title": "HAI PHÍA", "rows": [{"k": "FBI", "v": "TRIỀU TIÊN CHỊU TRÁCH NHIỆM", "at": S(25, 0.3)}, {"k": "BÌNH NHƯỠNG", "v": "BÁC BỎ CÁO BUỘC", "at": S(25, 0.8)}]},
    {"type": "slam", "at": 26, "text": "HÀNG NGHÌN ĐỊA CHỈ", "sub": "ĐÃ DÙNG · THEO JONATHAN LEVIN, CHAINALYSIS", "bg": "hanoi2"},
    {"type": "slam", "at": 27, "text": "HÀNG CHỤC NGHÌN", "sub": "DỰ ĐOÁN TRONG NHỮNG TUẦN TỚI", "fx": "punch"},
    {"type": "quote", "at": 28, "text": "Họ có quá nhiều tiền, nên các điểm rửa tiền quen của họ không xử lý kịp.", "who": "JONATHAN LEVIN · CHAINALYSIS", "note": "TRÍCH DỊCH · QUA COINDESK"},
]}

# ---------------------------------------------------------------- CH07 · Ai trả tiền, và ba ngày sau
CH["ch07"] = {"hud": {"k": "CHƯƠNG 07", "t": "AI TRẢ TIỀN, VÀ BA NGÀY SAU"}, "bgm": {"mood": "calm", "gain": 0.11}, "scenes": [
    {"type": "chapter", "no": "7", "k": "CHƯƠNG BẢY", "title": "AI TRẢ TIỀN,\nVÀ BA NGÀY SAU", "sub": "29.10 → 01.11.2026", "bg": "vaultOld", "focus": [0.5, 0.4], "titleAt": A(0, "Còn")},
    {"type": "counter", "at": 2, "from": 0, "to": 6.34, "suffix": " TỶ USD", "label": "TIỀN CÔNG TY ĐỂ RIÊNG ĐỂ BÙ · BINANCE", "sub": {"text": "THEO REUTERS (QUA NBC NEWS)", "at": A(2, "dùng")}},
    {"type": "org", "at": 3, "nodes": [
        {"id": "b", "t": "NGUỒN BÙ", "s": "THEO REUTERS", "at": S(3, 0.2), "cls": "top"},
        {"id": "s", "t": "QUỸ SAFU", "s": "KHOẢNG 1 TỶ USD BITCOIN", "p": "b", "at": S(3, 0.7)},
        {"id": "i", "t": "QUỸ BẢO HIỂM", "s": "HỢP ĐỒNG TƯƠNG LAI · MỘT PHẦN", "p": "b", "at": A(4, "phần")},
        {"id": "k", "t": "KHO BẠC", "s": "CỦA CÔNG TY", "p": "b", "at": A(4, "kho")}]},
    {"type": "bars", "at": 5, "title": "TỈ LỆ ĐÃ BÙ LẠI", "unit": "% TÀI SẢN BỊ TRỘM · BINANCE · TECHCRUNCH", "max": 100,
     "items": [{"k": "31.10 · BINANCE", "v": 90, "lbl": "90%", "at": S(5, 0.4)}, {"k": "01.11 · TECHCRUNCH", "v": 95, "lbl": "95%", "acc": True, "at": A(6, "tỷ")}]},
    {"type": "quote", "at": 7, "text": "Người dùng của chúng tôi sẽ không phải gánh tác động tài chính của sự cố này.", "who": "RICHARD TENG · TRÊN X", "note": "TRÍCH DỊCH · QUA NBC NEWS"},
    {"type": "date", "at": 9, "day": "BINANCE MỞ LẠI VIỆC RÚT TIỀN", "date": "01.11.2026", "sub": {"text": "THEO TỪNG GIAI ĐOẠN · THEO TECHCRUNCH", "at": A(9, "theo")}, "vid": CITY, "ms": 6},
    {"type": "counter", "at": 10, "from": 0, "to": 4.6, "suffix": " TỶ USD", "label": "TIỀN RÚT · 06:00–15:30 UTC · 01.11", "sub": {"text": "THEO TECHCRUNCH", "at": A(10, "xử")}},
    {"type": "bars", "at": 11, "title": "01.11 · 06:00–15:30 UTC", "unit": "TỶ USD · THEO TECHCRUNCH",
     "items": [{"k": "TIỀN RÚT", "v": 4.6, "lbl": "4,6", "at": S(11, 0.2)}, {"k": "TIỀN NẠP", "v": 1.0, "lbl": "1,0", "at": A(11, "một")},
               {"k": "CHÊNH RÒNG", "v": 3.6, "lbl": "3,6", "acc": True, "at": A(12, "ba")}]},
    {"type": "counter", "at": 13, "from": 0, "to": 2.1, "suffix": "%", "label": "CHÊNH RÒNG · TỔNG TÀI SẢN SÀN QUẢN LÝ", "sub": {"text": "THEO TECHCRUNCH", "at": S(13, 1.0)}},
    {"type": "myth", "at": 14, "mythLab": "KHÔNG PHẢI", "myth": "TỔNG SỐ TIỀN BỊ HACK", "truthLab": "MÀ LÀ", "truth": "RÚT TRỪ NẠP TRONG KHUNG GIỜ ẤY",
     "strikeAt": A(14, "phản"), "truthAt": A(14, "giữa"), "bg": "stopwatch"},
    {"type": "source", "at": 15, "source": "BINANCE · BẰNG CHỨNG DỰ TRỮ MỚI", "ref": "BẢN CHỤP ĐÃ CÔNG BỐ", "snippet": "bảo chứng tối thiểu [[một đổi một]] cho Bitcoin, Ether, USDT",
     "hlAt": A(15, "chụp"), "seal": "BẢN ĐẦY ĐỦ CHƯA CÔNG BỐ", "sealAt": A(15, "mới")},
    {"type": "kinetic", "at": A(16, "người"), "items": [{"text": "TỐI THIỂU MỘT ĐỔI MỘT", "at": A(16, "người"), "acc": True}, {"text": "người giữ có thể kiểm chứng · theo Binance", "at": A(16, "có"), "sm": True}], "bg": "typing"},
    {"type": "kinetic", "at": 17, "items": [{"text": "KHÔNG BÀN CHUYỆN\nNÊN GIỮ TIỀN Ở ĐÂU", "at": 17, "acc": True}, {"text": "đó không phải việc của một video giải thích công nghệ", "at": A(18, "Đó"), "sm": True}],
     "bg": "vaultOld"},
]}

# ---------------------------------------------------------------- CH08 · Ai giữ chìa khóa
CH["ch08"] = {"hud": {"k": "CHƯƠNG 08", "t": "AI GIỮ CHÌA KHÓA"}, "bgm": {"mood": "calm", "gain": 0.11}, "scenes": [
    {"type": "chapter", "no": "8", "k": "CHƯƠNG TÁM", "title": "AI GIỮ\nCHÌA KHÓA", "sub": "TRỞ LẠI CÂU HỎI ĐẦU TIÊN", "bg": "vault", "focus": [0.5, 0.4], "titleAt": A(0, "Giờ")},
    {"type": "ledger", "at": 2, "title": "NGHỊCH LÝ THỨ NHẤT", "rows": [
        {"k": "NGHỊCH LÝ 1", "v": "RÚT NHANH TRONG 20 PHÚT", "at": S(2, 0.3)}, {"k": "TRM LABS", "v": "KÝ GIAO DỊCH BỊ XÂM PHẠM", "at": S(2, 0.8)}]},
    {"type": "kinetic", "at": 3, "items": [{"text": "CHÍNH HỆ THỐNG KÝ", "at": 3, "acc": True}, {"text": "tạo chữ ký hợp lệ cho giao dịch của kẻ tấn công", "at": A(3, "chính", 0, 0.9), "sm": True}], "vid": STAMPS, "ms": 4},
    {"type": "units", "at": 4, "title": "NGHỊCH LÝ THỨ HAI · ĐÓNG BĂNG", "total": 100, "cols": 20, "lit": 44, "litAt": A(5, "gần"), "unitLabel": "44% SỐ TIỀN BỊ TRỘM · THEO ELLIPTIC"},
    {"type": "photo", "at": 6, "img": "brake", "focus": [0.55, 0.3], "cam": "push_in", "label": {"k": "STABLECOIN", "v": "CÓ SẴN MỘT CÁI PHANH", "at": A(6, "giữ")}},
    {"type": "ledger", "at": 7, "title": "KẺ TẤN CÔNG CÒN GIỮ", "rows": [{"k": "PHẦN LỚN", "v": "BITCOIN VÀ ETHER", "at": S(7, 0.3)}, {"k": "NHÀ PHÁT HÀNH", "v": "KHÔNG CÓ ĐỂ KHÓA", "at": S(7, 0.8)}]},
    {"type": "org", "at": 8, "nodes": [
        {"id": "h", "t": "HAI QUYỀN KHÁC NHAU", "s": "NGƯỜI GIỮ KHÁC NHAU", "at": S(8, 0.2), "cls": "top"},
        {"id": "k", "t": "QUYỀN KÝ", "s": "CỦA SÀN · CON DẤU", "p": "h", "at": S(8, 0.7)},
        {"id": "l", "t": "QUYỀN KHÓA", "s": "CỦA NHÀ PHÁT HÀNH · PHANH", "p": "h", "at": A(8, "khóa"), "cls": "acc"}]},
    {"type": "kinetic", "at": 9, "items": [{"text": "VỤ NÀY CHƯA KẾT THÚC", "at": 9, "acc": True}, {"text": "báo cáo điều tra chi tiết của Binance chưa công bố", "at": A(10, "báo"), "sm": True}], "bg": "hanoi2"},
    {"type": "ledger", "at": 11, "title": "VỤ ĐANG ĐIỀU TRA", "rows": [{"k": "FBI", "v": "CẢNH BÁO TIỀN CÓ THỂ BỊ RỬA TIẾP", "at": S(11, 0.3)}, {"k": "TRIỀU TIÊN", "v": "PHỦ NHẬN CÁO BUỘC", "at": S(11, 0.8)}]},
    {"type": "kinetic", "at": 12, "items": [{"text": "AI KIỂM SOÁT\nCHIẾC CHÌA KHÓA?", "at": 12, "acc": True}, {"text": "với dịch vụ giữ tài sản cho bạn", "at": A(13, "với"), "sm": True}], "bg": "tech"},
    {"type": "myth", "at": 14, "mythLab": "KHÔNG PHẢI", "myth": "AI ĐÓ CÓ BỊ HACK KHÔNG?", "truthLab": "MÀ LÀ", "truth": "CHÌA KHÓA NẰM TRONG TAY AI?", "strikeAt": A(14, "ai"), "truthAt": A(14, "hack")},
    {"type": "question", "at": 15, "text": "Chiếc chìa khóa của bạn\nđang nằm trong tay ai?"},
]}

PARAS = []

TITLES = ["20 phút mất 6,3 tỷ đô: đêm kho tiền số Binance bị rút cạn",
          "Thử ngầm 36 giờ, rút 6,3 tỷ đô: vụ hack Binance",
          "Vì sao 2,8 tỷ đô bị đóng băng ngay trong đêm hack Binance?"]


def commons_page(file):
    return "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(file.replace(" ", "_"))


def credits():
    out = []
    for key, file in IMGS.items():
        who, (lic, lic_url) = CREDITS[key]
        name = file.removeprefix("File:").rsplit(".", 1)[0]
        out.append(f"Ảnh: {name} — {who}, {lic}{' (' + lic_url + ')' if lic_url else ''}, via Wikimedia Commons: {commons_page(file)}")
    out.append("Video: Pexels (pexels.com) — giấy phép Pexels, dùng tự do. Tác giả: " + ", ".join(sorted({u for u, _ in CLIPS.values()})))
    return out


SPEC = {
    "title": TITLES[0],
    "channel": "MIM", "theme": "lab", "accent": "#22d3ee", "master": True, "endcard": 20, "autoTr": True, "beat2": True, "craft": True,
    "acc": ["binance", "khóa", "chìa", "ký", "phanh", "đóng", "băng", "stablecoin"],
    "say": SAY, "imgs": IMGS, "chapters": [f"ch{i:02d}" for i in range(9)],
    "youtube": {
        "titles": TITLES,
        "summary": "Ngày 29/10/2026, kho ví nóng của sàn Binance bị rút khoảng 6,3 tỷ đô la, phần lớn trong khoảng hai mươi phút theo TRM Labs. Video kể theo đúng "
                   "đồng hồ của đêm ấy (giờ UTC): ba mươi sáu tiếng dàn dựng, hệ thống ký giao dịch của ví nóng, chiếc phanh của các nhà phát hành stablecoin giúp "
                   "đóng băng gần một nửa số tiền, cuộc chạy đua với lệnh khóa, thông báo của FBI và lời phủ nhận của Triều Tiên. Mỗi con số đều ghi rõ của hãng nào: "
                   "TRM Labs, Elliptic, Halborn, CoinDesk, The Block, TechCrunch, VnExpress, Reuters hay chính Binance.",
        "more": ["Sự việc còn đang được điều tra (đến 13/11/2026); số liệu có thể thay đổi. Các hãng đếm quy mô vụ trộm và số tiền bị đóng băng khác nhau nên video nêu cả khoảng. "
                 "Ba lời trích (FBI, Jonathan Levin, Richard Teng) được dịch từ nguồn tiếng Anh và đọc bằng giọng máy. Ảnh và video làm nền là hình minh hoạ chung, "
                 "không phải hiện trường vụ việc. Video không đưa ra lời khuyên đầu tư và không hướng dẫn cách tấn công."],
        "chapter_titles": {"ch00": "Mở đầu: ba giờ sáng ở Hà Nội", "ch01": "Một con số, ba cách đếm", "ch02": "Ba mươi sáu tiếng trước giờ G", "ch03": "Hai mươi phút",
                           "ch04": "Cánh cửa nào đã mở", "ch05": "Chiếc phanh trong stablecoin", "ch06": "Chạy đua với lệnh khóa",
                           "ch07": "Ai trả tiền, và ba ngày sau", "ch08": "Ai giữ chìa khóa"},
        "playlist": "Công Nghệ Quanh Ta",
        "sources": ["https://vnexpress.net/hacker-thu-nghiem-truoc-36-tieng-rut-6-3-ty-usd-tu-vi-binance-trong-20-phut-5139116.html",
                    "https://www.halborn.com/blog/post/binance-hack-explained-what-it-means-for-bank-custody",
                    "https://www.theblock.co/news/business/2026-10-30-binance-hack-largest-crypto-hack-north-korea-432225",
                    "https://www.nbcnews.com/business/business-news/fbi-says-north-korea-was-6-billion-binance-crypto-hack-rcna606758",
                    "https://techcrunch.com/2026/11/01/binance-resumes-withdrawals-following-6-3-billion-breach/",
                    "https://www.coindesk.com/policy/2026/10/31/fbi-confirms-north-korea-s-role-in-usd6-billion-binance-hack-asks-defi-community-to-block-btc-eth-sol-addresses",
                    "https://www.theblock.co/news/regulation/2026-11-02-kim-jong-un-sister-rejects-fbi-claims-linking-north-korea-binance-hack-432344",
                    "https://www.trmlabs.com/resources/blog/north-korea-steals-usd-6-36-billion-from-binance-in-the-largest-hack-in-history",
                    "https://www.fbi.gov/investigate/cyber/alerts/2026/north-korea-responsible-for-6-billion-binance-attack",
                    "https://www.elliptic.co/insights/binance-largest-hack-in-history/"],
        "hashtags": ["Binance", "TiềnMãHóa", "AnNinhMạng", "CôngNghệ", "MindInTheMachine"],
        "tags": ["binance", "vụ hack binance", "binance bị rút 6,3 tỷ đô", "hack tiền mã hóa", "ví nóng", "hệ thống ký giao dịch", "stablecoin bị đóng băng",
                 "tether đóng băng", "an ninh tiền mã hóa", "fbi triều tiên binance", "trm labs", "công nghệ quanh ta"],
        "category": "28", "thumb": "t2.jpg",  # Lead 13/11: t2 đọc gọn hơn ở cỡ nhỏ
        "video_credits": credits(),
    },
}


def decorate():
    """Nhãn `illus` cho ảnh/clip minh hoạ chung (không phải hiện trường), đặt đúng từ ILL/VM."""
    for c in CH.values():
        for sc in c["scenes"]:
            if "illus" in sc:
                continue
            key = sc.get("img") or sc.get("bg")
            if sc.get("vid"):
                sc["illus"] = VM
            elif key in ILL:
                sc["illus"] = ILL[key]


def main():
    decorate()
    # Lead 13/11: duyệt plan 13/11 tối; slot MIM Long Thứ Hai/Tư/Sáu 20:00 VN kín tới 01/12 -> Thứ Tư 02/12.
    SPEC["approved"] = "13/11/2026 — duyet, ban tu dieu phoi theo cach tot nhat nhe, toi di ngu"
    SPEC.setdefault("youtube", {}).update({"publish_at": "2026-12-02T13:00:00Z"})
    (D / "spec.json").write_text(json.dumps(SPEC, ensure_ascii=False, indent=1), encoding="utf-8")
    for name, c in CH.items():
        p = D / f"{name}.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        for sc in c["scenes"]:              # quote: "who" + "note" -> "by"; "qline" = dòng lời trích (dòng "at" hoặc dòng ngay sau)
            if sc["type"] == "quote" and "who" in sc:
                k = sc["at"]
                is_q = lambda i: isinstance(d["lines"][i], dict) and d["lines"][i].get("q")
                sc["qline"] = k if is_q(k) else k + 1
                assert is_q(sc["qline"]), (name, k)
                sc["by"] = f'{sc.pop("who")} · {sc.pop("note")}'
        d.update(c)
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("spec +", len(CH), "chương")


if __name__ == "__main__":
    main()
