"""Pilot #131 overnight preview: sinh plan Long (hf_batch_render) + spec short (studio.py) từ kịch bản Lead.
Chạy trên Oracle: ~/vietneu-tts/.venv/bin/python ~/pilot131/build.py
Chỉ ghi vào ~/pilot131 (không đụng plan/ledger production)."""
import json, re, sys, unicodedata
from pathlib import Path

R = Path("/home/ubuntu/pilot131")
A = R / "assets"


def norm(w):
    return re.sub(r"[^\w]", "", w.replace("**", "")).lower()


def has_word(line, word):
    toks = [norm(t) for t in line.replace("**", "").split()]
    return any(t.startswith(norm(word)) for t in toks)


def check_anchor(lines, li, word):
    if not has_word(lines[li], word):
        raise SystemExit(f"mốc '{word}' không có trong câu {li}: {lines[li]}")


def img(topic, key):
    cred = json.loads((A / topic / "credits.json").read_text())
    hits = [c for c in cred if key in c["title"]]
    if len(hits) != 1:
        raise SystemExit(f"ảnh {topic}/{key}: {len(hits)} kết quả")
    return hits[0]


def credit_line(c):
    return c["credit"][:150]


# ---------------------------------------------------------------- SHORT
def short_spec(sid, channel, theme, kicker, foot, lines, scenes, voice_series=None):
    for s in scenes:
        for k, v in list(s.items()):
            if k.endswith("At") or k == "at":
                if isinstance(v, list) and len(v) >= 2 and isinstance(v[1], str):
                    check_anchor(lines, v[0], v[1])
        for st in s.get("stops", []):
            check_anchor(lines, st["at"][0], st["at"][1])
        for it in s.get("items", []):
            if isinstance(it.get("at"), list):
                check_anchor(lines, it["at"][0], it["at"][1])
        for side in ("a", "b"):
            if isinstance(s.get(side), dict) and isinstance(s[side].get("at"), list):
                check_anchor(lines, s[side]["at"][0], s[side]["at"][1])
        for stp in s.get("stamps", []):
            check_anchor(lines, stp["at"][0], stp["at"][1])
    spec = {"id": sid, "channel": channel, "theme": theme, "kicker": kicker, "foot": foot,
            "lines": lines, "scenes": scenes, "tail": 3.0, "loop": False,
            "out": str(R / "out" / sid / "final_preview.mp4")}
    return spec


def pan(topic, stem, line, label, stops, ghost=""):
    c = img(topic, stem)
    return {"device": "pan_tour", "line": line, "img": c["local"], "w": c["w"], "h": c["h"],
            # short: nhãn trên cùng đè kicker của spec (QA 03/11) -> đưa nhãn xuống dòng ghi công
            "label": "", "credit": (label + " · " + credit_line(c))[:170], "stops": stops, "ghost": ghost}


shorts = {}

# --- Thẻ 2 · BUD · Angulimala c1 v1 (APPROVED) ---
L = [
    "“Ta đã dừng rồi, **Angulimala**. Ngươi hãy dừng lại.”",
    "Câu ấy được nói với một tên cướp đang đuổi theo sau lưng.",
    "Theo kinh Trung Bộ số 86, ở xứ Kiều Tát La của vua Ba Tư Nặc, có một tên cướp tên là Angulimala.",
    "Hắn giết người, và đeo ngón tay của họ làm **vòng cổ**.",
    "Những người chăn bò, người làm ruộng can ngăn. Đức Phật vẫn im lặng, đi trên con đường dẫn đến chỗ hắn.",
    "Angulimala thấy Ngài, liền đuổi theo.",
    "Kinh kể: Đức Phật dùng **thần thông**, khiến hắn chạy hết sức vẫn không đuổi kịp, dù Ngài chỉ đi bình thường.",
    "Hắn gọi: ngài đang đi, sao lại bảo đã dừng?",
    "Đức Phật đáp: Ta đã dừng rồi. Ta đã buông bỏ **bạo lực** với mọi loài.",
    "Còn ngươi, chưa dừng làm hại chúng sinh.",
    "Dừng ở đây không phải dừng đôi chân. Mà là dừng **làm hại**.",
    "Angulimala quăng gươm và vũ khí xuống vực, đảnh lễ chân Phật, xin xuất gia.",
    "Đức Phật nói: Hãy đến, tỳ khưu. Và hắn trở thành một vị **tỳ khưu**.",
    "Về sau vua Ba Tư Nặc nói: người trẫm không thu phục được bằng gậy và gươm, Đức Phật đã thu phục mà **không cần gậy, không cần gươm**.",
    "Vậy, ai mới thật sự **đã dừng**?",
]
shorts["bud_angulimala_c1v1"] = short_spec(
    "p131_bud_angulimala_c1v1", "bud", "saffron", "KINH TRUNG BỘ 86 · ANGULIMALA", "Theo MN 86 · bản dịch Sujato, Thanissaro",
    L, [
        pan("angulimala", "054 Angulimala", 0, "TRANH CHÙA THÁI · ANGULIMALA ĐUỔI THEO ĐỨC PHẬT",
            [{"x": .45, "y": .42, "z": 1.0, "at": [0, "Ta"], "note": "", "r": 0},
             {"x": .3, "y": .42, "z": 1.8, "at": [1, "đuổi"], "note": "Kẻ cầm gươm đuổi theo", "r": 170}], ghost=""),
        {"device": "source_card", "line": 2, "source": "KINH TRUNG BỘ · MN 86 · SUJATO (CC0)", "ref": "Aṅgulimāla Sutta",
         "snippet": "Ở xứ Kiều Tát La có một tên cướp tên là [[Aṅgulimāla]].", "hlAt": [2, "Angulimala"], "ghost": "86"},
        {"device": "hook_poster", "line": 3, "num": "86", "kick": "THEO KINH · KHÔNG PHẢI TRUYỀN THUYẾT", "big": "Vòng cổ **ngón tay**", "markAt": [3, "vòng"], "ghost": ""},
        {"device": "time_spine", "line": 4, "kick": "TRÊN CON ĐƯỜNG", "items": [
            {"yr": "1", "label": "Người dân can ngăn", "at": [4, "can"]},
            {"yr": "2", "label": "Đức Phật im lặng đi tiếp", "at": [4, "im"]},
            {"yr": "3", "label": "Angulimala đuổi theo", "at": [5, "đuổi"]}], "ghost": ""},
        pan("angulimala", "File:Angulimala.jpg", 6, "BÍCH HOẠ · ĐI BÌNH THƯỜNG, CHẠY KHÔNG KỊP",
            [{"x": .5, "y": .5, "z": 1.0, "at": [6, "Kinh"], "note": "", "r": 0},
             {"x": .25, "y": .45, "z": 1.7, "at": [6, "thần"], "note": "Đức Phật đi bình thường", "r": 170},
             {"x": .72, "y": .4, "z": 1.7, "at": [6, "chạy"], "note": "Chạy hết sức vẫn không kịp", "r": 170}]),
        {"device": "quote", "line": 7, "mode": "karaoke", "source": "ANGULIMALA HỎI", "sourceAt": [7, "Hắn"], "ghost": ""},
        {"device": "split", "line": 8, "a": {"lab": "ĐỨC PHẬT", "val": "**Đã dừng**", "num": "1", "at": [8, "buông"]},
         "b": {"lab": "ANGULIMALA", "val": "**Chưa dừng**", "num": "2", "at": [9, "chưa"]}, "ghost": ""},
        {"device": "myth_strike", "line": 10, "mythLab": "KHÔNG PHẢI", "myth": "Dừng đôi chân", "truthLab": "MÀ LÀ", "truth": "Dừng **làm hại**",
         "strikeAt": [10, "Mà"], "truthAt": [10, "làm"], "ghost": ""},
        pan("angulimala", "060 Blessings", 11, "TRANH CHÙA THÁI · QUĂNG GƯƠM, XIN XUẤT GIA",
            [{"x": .5, "y": .45, "z": 1.0, "at": [11, "Angulimala"], "note": "", "r": 0},
             {"x": .4, "y": .62, "z": 1.7, "at": [11, "quăng"], "note": "Gươm rơi xuống đất", "r": 160},
             {"x": .62, "y": .45, "z": 1.6, "at": [12, "Hãy"], "note": "“Hãy đến, tỳ khưu”", "r": 160}]),
        {"device": "quote", "line": 13, "mode": "rise", "text": "Đức Phật thu phục mà **không cần gậy, không cần gươm**.", "source": "VUA BA TƯ NẶC · MN 86", "sourceAt": [13, "Về"], "ghost": ""},
        {"device": "close", "line": 14, "q": "Ai mới thật sự **đã dừng**?", "markSpan": 2, "ghost": "?"},
    ])

# --- Thẻ 4 · FS · Quét nhà c1 v2 (PENDING_APPROVAL) ---
L = [
    "Mồng 1 Tết, người lái buôn nổi giận. Cô hầu sợ hãi, chui vào **đống rác** rồi biến mất.",
    "Đó là một điển tích Trung Quốc, ghi trong sách **Sưu thần ký**.",
    "Lái buôn Âu Minh đi qua hồ Thanh Thảo, được thủy thần cho một người hầu tên là **Như Nguyệt**.",
    "Vài năm sau, Âu Minh làm ăn phát đạt, trở nên **giàu có**.",
    "Rồi mồng 1 Tết năm ấy, ông nổi giận đánh Như Nguyệt.",
    "Bản này kể cô tự chui vào đống rác rồi biến mất.",
    "Bản khác kể đống rác bị **đổ đi**, cô mất theo.",
    "Từ đó, nhà Âu Minh **nghèo dần**.",
    "Và người ta kiêng quét nhà, đổ rác trong mấy ngày Tết.",
    "Theo quan niệm xưa, quét nhà ngày Tết là quét đi **may mắn, tài lộc**.",
    "Nhà bạn còn giữ tục kiêng quét nhà **mùng 1** không?",
]
shorts["fs_quet_nha_c1v2"] = short_spec(
    "p131_fs_quet_nha_c1v2", "fs", "tet-poster", "ĐIỂN TÍCH · KIÊNG QUÉT NHÀ NGÀY TẾT", "Điển tích · theo quan niệm xưa · để tham khảo",
    L, [
        {"device": "hook_slam", "line": 0, "kick": "MỒNG 1 TẾT", "groups": [
            {"text": "Cô hầu", "at": [0, "Cô"]}, {"text": "chui vào **đống rác**", "big": True, "at": [0, "đống"]},
            {"text": "rồi biến mất", "at": [0, "biến"]}], "markAt": [0, "biến"], "ghost": ""},
        {"device": "source_card", "line": 1, "source": "ĐIỂN TÍCH TRUNG QUỐC · THEO GIÁO DỤC & THỜI ĐẠI", "ref": "Sưu thần ký",
         "snippet": "Chuyện người lái buôn [[Âu Minh]] và người hầu Như Nguyệt.", "hlAt": [1, "Sưu"], "ghost": ""},
        {"device": "time_spine", "line": 2, "kick": "CHUYỆN ÂU MINH", "items": [
            {"yr": "1", "label": "Thủy thần cho người hầu", "at": [2, "thủy"]},
            {"yr": "2", "label": "Làm ăn phát đạt", "at": [3, "phát"]},
            {"yr": "3", "label": "Mồng 1 Tết nổi giận", "at": [4, "nổi"]}], "ghost": ""},
        {"device": "split", "line": 5, "a": {"lab": "BẢN A · GIÁO DỤC & THỜI ĐẠI", "val": "**Tự** chui vào", "num": "", "at": [5, "tự"]},
         "b": {"lab": "BẢN B · ZNEWS, PHÁP LUẬT", "val": "Rác **đổ đi**", "num": "", "at": [6, "đổ"]}, "ghost": ""},
        {"device": "stamp", "line": 7, "han": "貧", "kick": "TỪ ĐÓ · NHÀ ÂU MINH", "big": "Nghèo", "stamps": [
            {"text": "KIÊNG QUÉT", "x": 140, "y": 900, "at": [8, "kiêng"]},
            {"text": "KIÊNG ĐỔ RÁC", "x": 480, "y": 1030, "at": [8, "đổ"], "rot": 5}], "ghost": ""},
        {"device": "myth_strike", "line": 9, "mythLab": "QUÉT NHÀ NGÀY TẾT", "myth": "Chỉ là dọn dẹp", "truthLab": "THEO QUAN NIỆM XƯA",
         "truth": "Quét đi **tài lộc**", "strikeAt": [9, "quét"], "truthAt": [9, "may"], "ghost": ""},
        {"device": "close", "line": 10, "q": "Nhà bạn còn kiêng quét nhà **mùng 1**?", "markSpan": 2, "ghost": "?"},
    ])

# --- Thẻ 5 · VSD · Thành nhà Hồ c3 v1 (Lead chọn · PENDING_APPROVAL) ---
L = [
    "Năm 1397, người quyết định xây thành mang chức **Thái sư** của triều Trần.",
    "Ông là **Hồ Quý Ly**.",
    "Chức đầy đủ của ông lúc ấy: Nhập nội Phụ chính Thái sư Bình chương quân quốc trọng sự.",
    "Thành được dựng ở vùng **Vĩnh Lộc**, Thanh Hóa.",
    "Theo sử sách, thành khởi công vào tháng Giêng năm Đinh Sửu.",
    "Tháng Ba năm sau, 1398, Hồ Quý Ly dời đô từ Thăng Long vào **kinh đô mới**.",
    "Năm 1400, ông cướp ngôi nhà Trần, đổi quốc hiệu Đại Việt thành **Đại Ngu**.",
    "Từ lúc khởi công tới lúc đổi triều: chỉ **ba năm**.",
    "Bức tường đá ấy được dựng lên khi triều Trần vẫn còn.",
    "Năm 2011, UNESCO ghi danh Thành nhà Hồ là **Di sản văn hóa thế giới**.",
    "Bạn đã từng đi qua **cổng Nam** thành nhà Hồ chưa?",
]
shorts["vsd_thanh_nha_ho_c3v1"] = short_spec(
    "p131_vsd_thanh_nha_ho_c3v1", "vsd", "archive", "SỬ · THÀNH NHÀ HỒ · 1397", "Theo VGP, Cục Di sản văn hóa, ĐVSKTT (qua Đỗ Quang Trọng)",
    L, [
        pan("thanh_nha_ho", "South gate", 0, "THÀNH NHÀ HỒ · CỔNG NAM",
            [{"x": .5, "y": .5, "z": 1.0, "at": [0, "Năm"], "note": "", "r": 0},
             {"x": .5, "y": .45, "z": 1.4, "at": [0, "Thái"], "note": "Dựng năm 1397", "r": 170}]),
        {"device": "hook_poster", "line": 1, "num": "1397", "kick": "NGƯỜI QUYẾT ĐỊNH XÂY THÀNH", "big": "**Hồ Quý Ly**", "markAt": [1, "Hồ"], "ghost": ""},
        {"device": "source_card", "line": 2, "source": "CHỨC VỊ NĂM 1397 · THEO WIKIPEDIA TIẾNG VIỆT", "ref": "Thái sư triều Trần",
         "snippet": "Nhập nội Phụ chính [[Thái sư]] Bình chương quân quốc trọng sự", "hlAt": [2, "Thái"], "ghost": ""},
        pan("thanh_nha_ho", "Ho dynasty", 3, "VĨNH LỘC · THANH HÓA",
            [{"x": .5, "y": .5, "z": 1.0, "at": [3, "Thành"], "note": "", "r": 0},
             {"x": .45, "y": .4, "z": 1.3, "at": [4, "khởi"], "note": "Khởi công tháng Giêng", "r": 160}]),
        {"device": "time_spine", "line": 5, "kick": "BA NĂM", "items": [
            {"yr": "1397", "label": "Khởi công · tháng Giêng", "at": [5, "Tháng"]},
            {"yr": "1398", "label": "Dời đô vào kinh đô mới", "at": [5, "dời"]},
            {"yr": "1400", "label": "Cướp ngôi · quốc hiệu Đại Ngu", "at": [6, "cướp"]}], "ghost": ""},
        {"device": "count_ring", "line": 7, "label": "Từ khởi công tới đổi triều", "value": 3, "from": 0, "suffix": "NĂM",
         "at": [7, "ba"], "pct": 0.3, "ghost": ""},
        pan("thanh_nha_ho", "Cổng Bắc", 8, "THÀNH NHÀ HỒ · CỔNG BẮC",
            [{"x": .5, "y": .5, "z": 1.0, "at": [8, "Bức"], "note": "", "r": 0},
             {"x": .5, "y": .5, "z": 1.3, "at": [9, "UNESCO"], "note": "UNESCO · 2011", "r": 150}]),
        {"device": "close", "line": 10, "q": "Bạn đã đi qua **cổng Nam** chưa?", "markSpan": 2, "ghost": "?"},
    ])

# --- Thẻ 6 · VSD · Bạch Đằng c1 v1 (Lead chọn · PENDING_APPROVAL) ---
L = [
    "Nước lớn, thuyền vào sông. Nước rút, **cọc nhô lên**.",
    "Đó là cái bẫy trên sông Bạch Đằng, năm **1288**.",
    "Trần Hưng Đạo nghiên cứu quy luật **thủy triều** để bố trí thế trận cọc.",
    "Cọc gỗ đầu bịt sắt được đóng ngầm dưới nước, ở các sông Chanh, Kênh, Rút.",
    "Theo hai nhà khảo cổ Tống Trung Tín và Lê Thị Liên, cọc nằm ở các **nhánh cổ**, thu hẹp dòng chảy, không cắm ngang dòng Bạch Đằng.",
    "Gặp lúc triều lên ngập bãi cọc, Nguyễn Khoái dùng thuyền nhẹ khiêu chiến, **giả thua**.",
    "Ô Mã Nhi thúc quân đuổi theo.",
    "Rồi **triều rút**.",
    "Cọc lộ ra, chặn thuyền Nguyên.",
    "Theo Nguyên sử, triều sông Bạch Đằng xuống, thuyền của Phàn Tiếp **mắc cạn**.",
    "Trận đánh diễn ra trong một ngày, ngày 9 tháng 4 năm 1288.",
    "Ô Mã Nhi và Phàn Tiếp bị **bắt sống**.",
    "Bạn đã từng thấy những chiếc cọc Bạch Đằng ở **bảo tàng** chưa?",
]
shorts["vsd_bach_dang_c1v1"] = short_spec(
    "p131_vsd_bach_dang_c1v1", "vsd", "archive", "SỬ · BẠCH ĐẰNG · 1288", "Theo Bảo tàng LSQG, Viện Khảo cổ học, Wikipedia (Nguyên sử)",
    L, [
        pan("bach_dang", "Bãi cọc cửa sông", 0, "ẢNH MINH HOẠ · BÃI CỌC TRÊN SÔNG",
            [{"x": .5, "y": .5, "z": 1.0, "at": [0, "Nước"], "note": "", "r": 0},
             {"x": .45, "y": .6, "z": 1.6, "at": [0, "cọc"], "note": "Nước rút · cọc nhô lên", "r": 170}]),
        {"device": "hook_poster", "line": 1, "num": "1288", "kick": "SÔNG BẠCH ĐẰNG", "big": "Cái bẫy **thủy triều**", "markAt": [1, "bẫy"], "ghost": ""},
        {"device": "split", "line": 2, "a": {"lab": "TRIỀU LÊN", "val": "Cọc **chìm**", "num": "↑", "at": [2, "thủy"]},
         "b": {"lab": "TRIỀU RÚT", "val": "Cọc **nhô lên**", "num": "↓", "at": [3, "Cọc"]}, "ghost": ""},
        {"device": "source_card", "line": 4, "source": "VIỆN KHẢO CỔ HỌC · QUA BẢO TÀNG LSQG", "ref": "Tống Trung Tín – Lê Thị Liên",
         "snippet": "Cọc ở các [[nhánh cổ]], thu hẹp dòng chảy, không cắm ngang dòng Bạch Đằng.", "hlAt": [4, "nhánh"], "ghost": ""},
        {"device": "time_spine", "line": 5, "kick": "MỘT NGÀY · 9/4/1288", "items": [
            {"yr": "1", "label": "Triều lên · giả thua", "at": [5, "giả"]},
            {"yr": "2", "label": "Ô Mã Nhi đuổi theo", "at": [6, "đuổi"]},
            {"yr": "3", "label": "Triều rút · cọc lộ", "at": [7, "triều"]}], "ghost": ""},
        pan("bach_dang", "Repel Mongol", 8, "TRANH MINH HOẠ TRẬN BẠCH ĐẰNG · BẢO TÀNG",
            [{"x": .5, "y": .5, "z": 1.0, "at": [8, "Cọc"], "note": "", "r": 0},
             {"x": .5, "y": .5, "z": 1.4, "at": [8, "chặn"], "note": "Chặn thuyền Nguyên", "r": 160}]),
        {"device": "quote", "line": 9, "mode": "rise", "text": "Triều xuống, thuyền Phàn Tiếp **mắc cạn**.", "source": "NGUYÊN SỬ · QUA WIKIPEDIA", "sourceAt": [9, "Theo"], "ghost": ""},
        {"device": "stamp", "line": 11, "han": "擒", "kick": "9 THÁNG 4 NĂM 1288", "big": "Bắt sống", "stamps": [
            {"text": "Ô MÃ NHI", "x": 160, "y": 640, "at": [11, "Ô"]},
            {"text": "PHÀN TIẾP", "x": 520, "y": 760, "at": [11, "Phàn"], "rot": 5}], "ghost": ""},
        {"device": "close", "line": 12, "q": "Bạn đã thấy cọc Bạch Đằng ở **bảo tàng**?", "markSpan": 2, "ghost": "?"},
    ])

for k, s in shorts.items():
    (R / "shorts").mkdir(exist_ok=True)
    (R / "shorts" / f"{s['id']}.json").write_text(json.dumps(s, ensure_ascii=False, indent=1))
    print("short", s["id"], len(s["lines"]), "câu", len(s["scenes"]), "cảnh")


# ---------------------------------------------------------------- LONG
def V(lines, at_line, word):
    """mốc {"at": n(1-based), "word": w} có kiểm."""
    check_anchor(lines, at_line - 1, word)
    return {"at": at_line, "word": word}


def long_row(rid, series, theme, kicker, title, lines, visuals, tts, media=None):
    media = media or {}
    clash = sorted(set(media) & set(visuals))
    if clash:
        raise SystemExit(f"{rid}: câu vừa có visual vừa có media {clash}")
    for k, v in visuals.items():
        for key, val in list(v.items()):
            if isinstance(val, str) and val.startswith("@"):
                check_anchor(lines, int(k) - 1, val[1:])
    pauses = {str(i + 1): 2.0 for i, l in enumerate(lines) if l.startswith("**") and l.endswith("**")}
    tts = dict(tts, pauses=pauses)
    return {"id": rid, "day": "2099-01-01", "slot": "00:00", "style": "studio_long", "theme": theme, "series": series,
            "lane": "long", "badge": "", "kicker": kicker, "chapters": True, "pacing": "warn", "title": title,
            "tags": [], "script": lines, "visuals": visuals, "media": media, "captions": True, "tts": tts}


# --- Thẻ 1 · BUD · Vessantara c3 v2 (APPROVED) · bản preview: mở đầu + 2 chương ---
LV = [
    "Đúng ngày hoàng tử chào đời, một con voi cái bay đến, mang theo voi con **trắng**.",
    "Theo truyện Tiền Thân số 547, con voi non ấy trắng toàn thân, được xem là **điềm lành**, và được để lại trong chuồng voi hoàng gia.",
    "Người ta đặt tên cho nó là **Paccaya**.",
    "Còn hoàng tử, vì sinh ra ở phố Vessa, được đặt tên là **Vessantara**.",
    "Nhiều năm sau, chính con voi trắng này sẽ rời kinh thành, theo tám người lạ đến từ một xứ đang **hạn hán**.",
    "Nhưng con voi chỉ là khởi đầu của câu chuyện.",
    "Theo kinh điển, truyện này do chính **Đức Phật** kể lại.",
    "Lúc ấy Ngài đang ở gần thành Ca Tỳ La Vệ, trong Rừng Đa, nhân một trận mưa.",
    "Và ở cuối truyện, Ngài nói ra một điều khiến người nghe lặng đi: những người trong truyện **là ai**.",
    "Hôm nay, ta bắt đầu từ **con voi trắng** ấy.",
    "**Đứa trẻ tặng vòng cổ**",
    "Khi còn nhỏ, chỉ khoảng bốn, năm tuổi, cậu bé có một chiếc vòng cổ trị giá **một trăm nghìn** đồng tiền.",
    "Cậu tháo ra, tặng cho các bà vú nuôi.",
    "Người ta làm vòng mới. Cậu lại tặng.",
    "Truyện ghi: như thế đến **chín lần**.",
    "Đứa trẻ ấy **lớn lên**.",
    "Ông cưới người em họ là nàng **Maddi** làm hoàng hậu, rồi nhận ngôi vua.",
    "Từ ngày nhận ngôi, mỗi ngày ông bố thí **sáu trăm nghìn** đồng tiền.",
    "Hoàng hậu Maddi sinh một con trai. Cậu bé được đặt nằm trong võng vàng, nên có tên là **Jali**.",
    "Rồi một con gái, được đặt nằm trên tấm da đen, nên gọi là **Kanhajina**.",
    "Một gia đình đủ đầy. Và trong chuồng voi, con voi trắng **vẫn ở đó**.",
    "**Tám người từ xứ hạn hán**",
    "Lúc ấy, ở xứ Kalinga, trời **hạn hán**.",
    "Lúa không mọc. Nạn đói lan rộng.",
    "Vua Kalinga chọn ra **tám** vị bà la môn.",
    "Và sai họ đi một chuyến xa, chỉ để xin một thứ: con voi trắng của **Vessantara**.",
    "Tám người tìm đến Vessantara và **ngỏ lời xin**.",
    "Vessantara trao **con voi**.",
    "Không chỉ con voi. Ông trao cả đồ trang sức trên mình voi, và **năm trăm** người theo hầu, cùng những người giữ voi và coi chuồng.",
    "Con voi được xem là điềm lành của hoàng gia, rời kinh thành theo những người lạ.",
    "Đến đây, truyện Tiền Thân đặt ra một **câu hỏi** không dễ.",
    "Truyện không kể Vessantara cho đi vì **giàu có thừa thãi**.",
    "Truyện kể một người **tập cho đi** từ khi còn là đứa trẻ, chín lần với một chiếc vòng cổ.",
    "Câu chuyện mời người nghe nhìn vào **hạnh bố thí**: cho mà không do dự, cho mà không đòi lại.",
    "Nhưng truyện **không dừng** ở con voi.",
    "Phía trước còn một **lễ đại thí**: bảy trăm voi, bảy trăm ngựa, bảy trăm cỗ xe, và nhiều thứ khác.",
    "Phía trước còn vị trời **Sakka**, hoá thành một người bà la môn, đến thử lòng ông.",
    "Và ở cuối truyện, Đức Phật nói ra **kiếp trước** của từng người.",
    "Người bà la môn Jujaka, sẽ xuất hiện ở phần sau, là **Đề Bà Đạt Đa**.",
    "Maddi là tiền thân của **mẹ La Hầu La**.",
    "Còn vua Vessantara, Ngài nói, chính là **Ta**.",
    "Đây là **phần mở đầu**. Bản đầy đủ sẽ đi tiếp cùng Vessantara, qua lễ đại thí và lần thử lòng của Sakka.",
]
vis = {
    "1": {"type": "studio", "device": "pan_tour", "file": "File:Thai - Vessantara Jataka, Chapter 2 - Kalinga Brahmins are Given the White Elephant - Walters 35232.jpg",
          "by": False, "until": 2, "label": "TRANH THÁI · BẢO TÀNG WALTERS · CON VOI TRẮNG",
          "credit": "Walters Art Museum · Public domain · Wikimedia Commons",
          "stops": [{"x": .5, "y": .5, "z": 1.0, "at": V(LV, 1, "voi"), "note": "", "r": 0},
                    {"x": .55, "y": .55, "z": 1.6, "at": V(LV, 2, "trắng"), "note": "Voi trắng · điềm lành", "r": 170}]},
    "4": {"type": "studio", "device": "hook_poster", "num": "547", "kick": "TRUYỆN TIỀN THÂN · JĀTAKA", "big": "**Vessantara**", "markAt": "@Vessantara"},
    "5": {"type": "studio", "device": "split", "a": {"lab": "KINH THÀNH", "val": "Voi **trắng**", "num": "1", "at": "@voi"},
          "b": {"lab": "XỨ HẠN HÁN", "val": "**Tám** người lạ", "num": "8", "at": "@tám"}},
    "7": {"type": "studio", "device": "source_card", "until": 8, "source": "JĀTAKA 547 · BẢN COWELL", "ref": "Đức Phật kể tại Rừng Đa, gần Ca Tỳ La Vệ",
          "snippet": "Truyện do chính [[Đức Phật]] kể lại, nhân một trận mưa.", "hlAt": "@Đức"},
    "12": {"type": "studio", "device": "count_ring", "until": 15, "label": "Chiếc vòng cổ tặng đi", "value": 9, "from": 1, "suffix": "LẦN",
           "at": V(LV, 15, "chín"), "pct": 0.9},
    "17": {"type": "studio", "device": "pan_tour", "file": "File:Thai - Vessantara Jataka, Chapter 11 (Maharaja) - Walters 35249 - A T Front.jpg",
           "by": False, "until": 18, "label": "TRANH THÁI · WALTERS · MINH HOẠ CẢNH CUNG ĐÌNH",
           "credit": "Walters Art Museum · Public domain · Wikimedia Commons",
           "stops": [{"x": .5, "y": .5, "z": 1.0, "at": V(LV, 17, "cưới"), "note": "", "r": 0},
                     {"x": .45, "y": .55, "z": 1.5, "at": V(LV, 18, "bố"), "note": "Bố thí mỗi ngày", "r": 160}]},
    "19": {"type": "studio", "device": "list_build", "until": 20, "title": "HAI NGƯỜI CON", "items": [
        {"text": "Jali", "sub": "nằm trong võng vàng", "at": "@Jali"},
        {"text": "Kanhajina", "sub": "nằm trên tấm da đen", "at": V(LV, 20, "Rồi")}]},
    "23": {"type": "studio", "device": "window", "until": 24, "word": "HẠN", "lab": "XỨ KALINGA", "fill": "solid", "sub": "Lúa không mọc · nạn đói", "subAt": V(LV, 24, "Lúa")},
    "25": {"type": "studio", "device": "count_ring", "until": 26, "label": "Bà la môn được sai đi", "value": 8, "from": 0, "suffix": "NGƯỜI", "at": "@tám", "pct": 0.8},
    "28": {"type": "studio", "device": "pan_tour", "file": "File:Prince Vessantara Gives Away His White Elephant, Scene from Vessantara Jataka on Generosity LACMA M.76.112.20.jpg",
           "by": False, "until": 30, "label": "LACMA · VESSANTARA TRAO VOI TRẮNG",
           "credit": "LACMA · Public domain · Wikimedia Commons",
           "stops": [{"x": .5, "y": .5, "z": 1.0, "at": V(LV, 28, "trao"), "note": "", "r": 0},
                     {"x": .5, "y": .4, "z": 1.5, "at": V(LV, 29, "năm"), "note": "Voi · trang sức · 500 tuỳ tùng", "r": 170}]},
    "34": {"type": "studio", "device": "quote", "text": "Cho mà không do dự, cho mà không đòi lại.", "source": "HẠNH BỐ THÍ · DĀNA", "sourceAt": "@hạnh"},
    "36": {"type": "studio", "device": "list_build", "until": 37, "title": "PHÍA TRƯỚC", "items": [
        {"text": "Lễ đại thí", "sub": "bảy trăm voi · ngựa · xe", "at": "@lễ"},
        {"text": "Sakka thử lòng", "sub": "hoá thành bà la môn", "at": V(LV, 37, "Sakka")}]},
    "39": {"type": "studio", "device": "ledger", "until": 41, "title": "AI LÀ AI · THEO JĀTAKA 547", "head": ["TRONG TRUYỆN", "KIẾP SAU"],
           "rows": [{"y": "Jujaka", "at": "@Jujaka", "cells": [{"k": "BÀ LA MÔN", "v": "Đề Bà Đạt Đa"}]},
                    {"y": "Maddi", "at": V(LV, 40, "Maddi"), "cells": [{"k": "HOÀNG HẬU", "v": "Mẹ La Hầu La"}]},
                    {"y": "Vessantara", "at": V(LV, 41, "Còn"), "cells": [{"k": "NHÀ VUA", "v": "Đức Phật"}]}]},
}
MEDIA_V = {
    "3": {"kind": "commons", "file": "File:010 Generosity, King Vessantara gives away his White Elephant but later returns Triumphant (9270909883).jpg", "by": True, "tagged": True, "label": "TRANH CHÙA THÁI · VOI TRẮNG", "layout": "frame"},
    "6": {"kind": "commons", "file": "File:Thai - Narrative Scroll - Vessantara Jataka - Walters 35289.jpg", "by": False, "tagged": True, "label": "CUỘN TRANH VESSANTARA · BẢO TÀNG WALTERS", "layout": "full"},
    "9": {"kind": "commons", "file": "File:Rail post depicting the Vessantara Jataka, Bharhut Stupa, circa 2nd century BCE, Allahabad Museum, Uttar Pradesh.jpg", "by": True, "tagged": True, "label": "TRỤ LAN CAN BHARHUT · TK 2 TCN · TRUYỆN VESSANTARA", "layout": "frame"},
    "10": {"kind": "image", "query": "elephant forest", "tagged": True, "label": "ẢNH MINH HOẠ"},
    "21": {"kind": "commons", "file": "File:Thai - Vessantara Jataka, Chapter 2 (Himavanta Forest) - Walters 35265 - A T Front.jpg", "by": False, "tagged": True, "label": "TRANH THÁI · BẢO TÀNG WALTERS", "layout": "frame"},
    "27": {"kind": "image", "query": "dusty road walking sunset", "tagged": True, "label": "ẢNH MINH HOẠ"},
    "32": {"kind": "commons", "file": "File:Thai - Vessantara Jataka, Chapter 4 - Vessantara, Maddi, Jali, and Kanha Enter the Forest - Walters 35234.jpg", "by": False, "tagged": True, "label": "TRANH THÁI · BẢO TÀNG WALTERS", "layout": "frame"},
    "35": {"kind": "commons", "file": "File:Thai - Vessantara Jataka, Chapter 3 (The Gift) - Walters 35266 - A T Front.jpg", "by": False, "tagged": True, "label": "TRANH THÁI · CHƯƠNG ĐẠI THÍ · WALTERS", "layout": "frame"},
    "38": {"kind": "commons", "file": "File:Thai - Vessantara Jataka, Chapter 5 (Jujaka) - Walters 35250 - A T Front.jpg", "by": False, "tagged": True, "label": "TRANH THÁI · CHƯƠNG JUJAKA · WALTERS", "layout": "full"},
    "42": {"kind": "commons", "file": "File:Thai - Vessantara Jataka, Chapter 3 - Vessantara Gives Away the Chariot - Walters 35233.jpg", "by": False, "tagged": True, "label": "TRANH THÁI · BẢO TÀNG WALTERS", "layout": "frame"},
}
rows = [long_row("L_p131_bud_vessantara_c3v2", "bud", "saffron", "TRUYỆN TIỀN THÂN · JĀTAKA 547 · PREVIEW",
                 "Con voi trắng xuất hiện đúng ngày Vessantara ra đời", LV, vis,
                 {"voice": "Binh", "engine": "standard", "tempo": 0.9, "pause": 0.55, "temperature": 0.9, "text_mode": "production"}, MEDIA_V)]

# --- Thẻ 3 · FS · Mậu Thân c2 v2 (APPROVE? KHÔNG — chờ duyệt lại) ---
LM = [
    "Bạn sinh năm **1968**, tuổi Mậu Thân?",
    "Theo quan niệm truyền thống, tam tai năm 2027 **không rơi** vào tuổi bạn.",
    "Theo quan niệm ấy, tam tai năm 2027 thuộc nhóm **Hợi, Mão, Mùi**.",
    "Nhóm tam hợp của bạn, **Thân, Tý, Thìn**, gặp tam tai vào những năm khác.",
    "Nhưng không phạm tam tai chưa phải là **hết**.",
    "Quan niệm truyền thống còn nhắc **một tháng** cần để ý.",
    "Hôm nay ta đi qua từng lớp, theo đúng những gì các nguồn tra cứu ghi lại.",
    "Và nhớ cho: tất cả là **quan niệm**, không phải dự báo.",
    "**Năm 2027 và tuổi của bạn**",
    "Năm âm lịch 2027 là năm **Đinh Mùi**.",
    "Người sinh năm 1968, theo lịch can chi, là tuổi **Mậu Thân**.",
    "Cách tính **tuổi mụ**: lấy năm đang xét, trừ năm sinh âm lịch, rồi cộng một.",
    "Hai nghìn không trăm hai mươi bảy, trừ một nghìn chín trăm sáu mươi tám, cộng một: bạn bước vào **sáu mươi** tuổi mụ.",
    "Sang năm 2028, lịch can chi lại quay về **Mậu Thân**.",
    "Một vòng sáu mươi năm **hoa giáp** sắp khép lại.",
    "**Lớp thứ nhất: tam tai**",
    "Tam là ba, tai là tai họa. Theo quan niệm này, mỗi người có **ba năm liền** cần thận trọng.",
    "Vòng tam tai dài **mười hai năm**, theo mười hai con giáp.",
    "Tam tai không tính riêng từng tuổi, mà tính theo **nhóm tam hợp**: ba tuổi cùng nhóm chịu chung một hạn.",
    "Nhóm của bạn gặp tam tai vào ba năm **Dần, Mão, Thìn**.",
    "Còn ba năm **Tỵ, Ngọ, Mùi** là lượt của một nhóm khác.",
    "Năm 2027 thuộc lượt ấy, nên theo quan niệm này, tam tai rơi vào nhóm **Hợi, Mão, Mùi**.",
    "Tuổi Mậu Thân **không phạm**.",
    "**Lớp thứ hai: thiên can**",
    "Mỗi năm có một can và một chi. Can của năm 2027 là **Đinh**, can của tuổi bạn là **Mậu**.",
    "Theo ngũ hành, Đinh thuộc **Hỏa**, Mậu thuộc **Thổ**.",
    "Và theo vòng tương sinh, Hỏa sinh Thổ.",
    "Tức là can của năm sinh cho can của tuổi. Theo cách xem truyền thống, đó là thế **thuận**.",
    "**Lớp thứ ba: tháng cần để ý**",
    "Tháng Giêng âm lịch năm 2027 mang chi **Dần**.",
    "Theo quan niệm truyền thống, chi Thân **xung** chi Dần.",
    "Vì vậy, tháng Giêng được xem là tháng nên cẩn trọng với người tuổi Thân.",
    "Cẩn trọng ở đây không có nghĩa là lo sợ. Chỉ là một lời nhắc: đầu năm, **chậm lại một nhịp**.",
    "Theo cùng nguồn, chi **Thân** còn xung **Dần** và hại **Hợi**.",
    "**Tóm lại**",
    "Theo quan niệm truyền thống, người sinh năm 1968 bước vào năm Đinh Mùi 2027 với ba điều.",
    "Một, **không phạm** tam tai.",
    "Hai, can năm **sinh** can tuổi, được coi là thuận.",
    "Ba, **tháng Giêng** âm lịch là tháng cần để ý.",
    "Tất cả là quan niệm **để tham khảo**, không phải lời dự báo cho riêng ai.",
    "Bạn sinh năm 1968, hay có người thân tuổi Mậu Thân? Hãy để lại một dòng ở phần **bình luận**.",
]
vis = {
    "1": {"type": "studio", "device": "hook_poster", "until": 2, "num": "1968", "kick": "TUỔI MẬU THÂN · NĂM 2027 · THEO QUAN NIỆM", "big": "**Không phạm** tam tai",
          "markAt": V(LM, 2, "không")},
    "3": {"type": "studio", "device": "wheel", "until": 4, "target": "Mùi", "tag": "Năm 2027", "kick": "TAM TAI NĂM MÙI",
          "links": [["Hợi", "Mão"], ["Mão", "Mùi"], ["Mùi", "Hợi"]], "linkAt": "@Hợi"},
    "6": {"type": "studio", "device": "calendar", "pages": [{"head": "THÁNG GIÊNG · ĐINH MÙI", "day": "1", "wd": "CHI DẦN", "lun": "THÁNG CẦN ĐỂ Ý"}],
          "stamp": "DẦN", "stampAt": "@tháng", "side": "Tuổi **Thân** · theo quan niệm", "sideAt": "@Quan"},
    "8": {"type": "studio", "device": "myth_strike", "mythLab": "KHÔNG PHẢI", "myth": "Lời dự báo", "truthLab": "MÀ LÀ", "truth": "**Quan niệm** truyền thống",
          "strikeAt": "@nhớ", "truthAt": "@quan"},
    "13": {"type": "studio", "device": "count_ring", "until": 14, "label": "Tuổi mụ năm 2027 của người sinh 1968", "value": 60, "suffix": "tuổi mụ",
           "pct": 0.6, "at": "@bước", "note": "2027 − 1968 + 1"},
    "17": {"type": "studio", "device": "list_build", "until": 19, "title": "TAM TAI · THEO QUAN NIỆM", "items": [
        {"text": "Ba năm liền", "sub": "cần thận trọng", "at": "@ba"},
        {"text": "Vòng 12 năm", "sub": "theo 12 con giáp", "at": V(LM, 18, "Vòng")},
        {"text": "Tính theo nhóm tam hợp", "sub": "ba tuổi chung một hạn", "at": V(LM, 19, "Tam")}]},
    "20": {"type": "chiwheel", "title": "TAM TAI THEO NHÓM TAM HỢP", "until": 22,
           "groups": [["Thân", "Tý", "Thìn"], ["Tỵ", "Dậu", "Sửu"], ["Dần", "Ngọ", "Tuất"], ["Hợi", "Mão", "Mùi"]],
           "group_labels": ["THỦY CỤC", "KIM CỤC", "HỎA CỤC", "MỘC CỤC"], "focus": ["Hợi", "Mão", "Mùi"],
           "arc": {"from": "Tỵ", "n": 3, "labels": ["2025", "2026", "2027"], "label": "BA NĂM TAM TAI CỦA HỢI · MÃO · MÙI"},
           "steps": [{"at": 21, "word": "Tỵ", "arc": True}, {"at": 22, "word": "Hợi", "focus": True}]},
    "23": {"type": "studio", "device": "stamp", "han": "申", "kick": "TUỔI MẬU THÂN · NĂM 2027", "big": "KHÔNG PHẠM",
           "stamps": [{"text": "TAM TAI", "x": 160, "y": 560, "at": "@Mậu"}]},
    "25": {"type": "studio", "device": "split", "until": 26, "a": {"lab": "CAN NĂM 2027", "val": "Đinh · **Hỏa**", "num": "丁", "at": "@Đinh"},
           "b": {"lab": "CAN TUỔI BẠN", "val": "Mậu · **Thổ**", "num": "戊", "at": V(LM, 26, "Mậu")}},
    "27": {"type": "studio", "device": "cycle_draw", "until": 28, "kick": "NGŨ HÀNH TƯƠNG SINH · THEO QUAN NIỆM",
           "nodes": [{"id": "hoa", "label": "Hỏa", "tone": "accent", "at": "@Hỏa"}, {"id": "tho", "label": "Thổ", "tone": "accent", "at": "@Thổ"},
                     {"id": "kim", "label": "Kim"}, {"id": "thuy", "label": "Thủy"}, {"id": "moc", "label": "Mộc"}],
           "edges": [{"from": "hoa", "to": "tho", "at": "@sinh"}]},
    "30": {"type": "studio", "device": "wheel", "until": 32, "target": "Dần", "tag": "Tháng Giêng", "kick": "THÂN XUNG DẦN · THEO QUAN NIỆM",
           "links": [["Thân", "Dần"]], "linkAt": V(LM, 31, "xung")},
    "34": {"type": "studio", "device": "list_build", "title": "CHI THÂN · THEO NGUỒN TRA CỨU", "items": [
        {"text": "Xung Dần", "sub": "tháng Giêng · chi Dần", "at": "@xung"}, {"text": "Hại Hợi", "sub": "", "at": "@hại"}]},
    "36": {"type": "studio", "device": "list_build", "until": 39, "title": "1968 · NĂM ĐINH MÙI 2027 · THEO QUAN NIỆM", "items": [
        {"text": "Không phạm tam tai", "sub": "", "at": V(LM, 37, "Một")},
        {"text": "Can năm sinh can tuổi", "sub": "thế thuận", "at": V(LM, 38, "Hai")},
        {"text": "Tháng Giêng âm lịch", "sub": "cần để ý", "at": V(LM, 39, "Ba")}]},
}
MEDIA_M = {
    "5": {"kind": "image", "query": "incense smoke temple dark", "tagged": True, "label": "ẢNH MINH HOẠ"},
    "7": {"kind": "image", "query": "old book candle light table", "tagged": True, "label": "ẢNH MINH HOẠ", "layout": "frame"},
    "10": {"kind": "commons", "file": "File:1. Bảo Đại 19 calendar (1944) Bùi Quang Tuấn.jpg", "by": False, "tagged": True, "label": "TƯ LIỆU · LỊCH TRIỀU NGUYỄN NĂM 1944", "layout": "frame"},
    "11": {"kind": "image", "query": "elderly man reading by window morning light", "tagged": True, "label": "ẢNH MINH HOẠ"},
    "15": {"kind": "image", "query": "sunrise mountains clouds", "tagged": True, "label": "ẢNH MINH HOẠ"},
    "33": {"kind": "image", "query": "pouring tea clay teapot", "tagged": True, "label": "ẢNH MINH HOẠ", "layout": "card3d"},
    "40": {"kind": "image", "query": "incense smoke black background", "tagged": True, "label": "ẢNH MINH HOẠ"},
}
rows.append(long_row("L_p131_fs_mauthan_c2v2", "fs", "son-mai", "TUỔI MẬU THÂN 1968 · NĂM 2027 · PREVIEW",
                     "Sinh năm 1968 Mậu Thân: 2027 không phạm tam tai, lưu ý gì?", LM, vis,
                     {"voice": "Thái Sơn", "style": "doc_truyen", "tempo": 0.96, "pause": 0.46, "temperature": 0.7,
                      "donor": "Thanh Bình", "text_mode": "speech"}, MEDIA_M))

(R / "long").mkdir(exist_ok=True)
sys.path.insert(0, "/home/ubuntu/vietneu-tts")
import hf_batch_render as HB  # noqa: E402 -- chuẩn hoá giọng D + âm thanh preset C như plan Long mới
pf = R / "long" / "plan_p131.json"
pf.unlink(missing_ok=True)
HB.save_plan_rows(pf, rows)
rows = json.loads(pf.read_text())
for r in rows:
    print("  tts", {k: v for k, v in r["tts"].items() if k != "pauses"}, "sound", (r.get("sound") or {}).get("preset_long"))
for r in rows:
    print("long", r["id"], len(r["script"]), "câu", len(r["visuals"]), "visual")
