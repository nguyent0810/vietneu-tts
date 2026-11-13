"""Lô R27 (27/10/2026): mở lại sản xuất short theo đề xuất tuần 26/10 (briefs/de_xuat_tuan_2026-10-26.md).
Lấp khung trống 28/10–03/11 (giờ trong plan là UTC). Không thay bài nào đã hẹn.

    .venv/bin/python output/cl_staging/grok/build_r1027.py [--html-only] [--only=id1,id2]

FS (khuôn `tuoi`, bảng tự dò có mốc 2027): "Sinh năm 2000–2005 hợp tuổi nào?" — tam hợp, lục hợp, lục xung sinh bằng
canchi.py; năm người ấy là 2 năm gần nhất của chi đó; dòng mốc 2027 = nữ tuổi đó cưới năm Đinh Mùi có phạm Kim Lâu
không (tuổi mụ, dư 1/3/6/8). Luật 26/10: ghi đủ "KIM LÂU THÂN/TỬ…", không để chữ trùng tên chi đứng một mình.
Câu đọc năm gọn ("hai nghìn lẻ một"), không đọc trọn số (điểm rơi giây 5–7 của short mệnh).

BUD (đời thường của Đức Phật + Chú Đại Bi phần 8–9), 27–32 giây, câu 2 là chi tiết bất ngờ; nguồn:
  ngủ   Trung Bộ 107 (mn107:6.2)             dép   Luật tạng Đại phẩm 5 (pli-tv-kd5:1.29–1.30, Brahmali CC0)
  tắm   Trung Bộ 26 (mn26:3.6–3.11)          thuốc Luật tạng Đại phẩm 6 (pli-tv-kd6:1.1–1.3, Brahmali CC0)
  p8/p9 Lokesh Chandra 1988 (dhuru-dhuru vijayate mahāvijayate / dhara-dhara dharāṇi-rāja / cala-cala)
"""
from __future__ import annotations
from shortbuild import validate

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "output/cl_staging/long"))
import build_bud_1023r as B   # noqa: E402
import build_r1024 as R4      # noqa: E402
import build_r1025 as R5      # noqa: E402
import build_r1026 as R6      # noqa: E402
import canchi as K            # noqa: E402
import hf_music               # noqa: E402

D = B.D
FS_PLAN = ROOT / "output/cl_staging/fs/plan_fs_r1027.json"
BUD_PLAN = ROOT / "output/cl_staging/bud/plan_bud_r1027.json"

# ------------------------------------------------------------------ FS: dữ kiện sinh bằng code
LUC_XUNG = {a: b for p in K.LUC_XUNG for a, b in (p, p[::-1])}
WORD = {2000: "hai nghìn", 2001: "hai nghìn lẻ một", 2002: "hai nghìn lẻ hai", 2003: "hai nghìn lẻ ba",
        2004: "hai nghìn lẻ bốn", 2005: "hai nghìn lẻ năm"}
KL = {1: "KIM LÂU THÂN", 3: "KIM LÂU THÊ", 6: "KIM LÂU TỬ", 8: "KIM LÂU LỤC SÚC"}
KL_VI = {1: "Kim Lâu Thân", 3: "Kim Lâu Thê", 6: "Kim Lâu Tử", 8: "Kim Lâu Lục Súc"}


def near(chi: str, y: int) -> list[int]:
    ys = sorted((x for x in range(y - 14, y + 15) if K.can_chi(x)[1] == chi), key=lambda x: (abs(x - y), x))[:2]
    return sorted(ys)


def kimlau_2027(y: int) -> int | None:
    r = (2027 - y + 1) % 9
    return r if r in KL else None


def hop(y: int) -> dict:
    can, chi = K.can_chi(y)
    th = [c for c in K.tam_hop_of(chi) if c != chi]
    lh, xu = K.luc_hop_of(chi), LUC_XUNG[chi]
    return {"y": y, "can": can, "chi": chi, "th": th, "lh": lh, "xu": xu, "kl": kimlau_2027(y), "tuoi_mu": 2027 - y + 1}


assert hop(2001)["th"] == ["Dậu", "Sửu"] and hop(2001)["lh"] == "Thân" and hop(2001)["xu"] == "Hợi"
assert hop(2002)["kl"] == 8 and hop(2001)["kl"] is None and hop(2000)["kl"] == 1 and hop(2004)["kl"] == 6
assert near("Dậu", 2001) == [1993, 2005]

SLOTS_FS = {2000: ("2026-10-31", "12:00"), 2001: ("2026-11-01", "08:00"), 2002: ("2026-11-02", "08:00"),
            2003: ("2026-11-02", "12:00"), 2004: ("2026-11-03", "08:00"), 2005: ("2026-11-03", "12:00")}
THEMES = {2000: "amber", 2001: "red", 2002: "navy", 2003: "jade", 2004: "amber", 2005: "red"}  # ivory: dòng mốc 2027 màu vàng chìm trên nền ngà (QA 26/10)
FS_COMMON = {"series": "fs", "style": "yeartable", "mould": "A", "badge": "", "media": {}, "visuals": {}, "lane": "tuoi",
             "test_cell": "R27_hoptuoi", "figures": {str(i): {"type": "none", "source": "rule"} for i in range(1, 7)},
             "cta": "Bạn và người ấy sinh năm nào? Bình luận để mình xem giúp nhé."}
SRC = ("Quan hệ địa chi truyền thống (tính bằng canchi.py): tam hợp Thân-Tý-Thìn, Tỵ-Dậu-Sửu, Dần-Ngọ-Tuất, Hợi-Mão-Mùi; "
       "lục hợp Tý-Sửu, Dần-Hợi, Mão-Tuất, Thìn-Dậu, Tỵ-Thân, Ngọ-Mùi; lục xung Tý-Ngọ, Sửu-Mùi, Dần-Thân, Mão-Dậu, Thìn-Tuất, Tỵ-Hợi. "
       "Kim Lâu năm 2027: tuổi mụ chia 9 dư 1, 3, 6, 8. Năm âm lịch (sinh tháng 1–2 dương lịch có thể thuộc năm trước). Để tham khảo.")


def fs_item(y: int) -> dict:
    h = hop(y)
    a, b = h["th"]
    kl_line = (f"Sang năm Đinh Mùi, nữ {h['can']} {h['chi']} cưới hỏi **không phạm Kim Lâu**." if h["kl"] is None else
               f"Sang năm Đinh Mùi, nữ {h['can']} {h['chi']} cưới hỏi phạm **{KL_VI[h['kl']]}**, nên xem kỹ.")
    foot = (f"2027: NỮ {h['can'].upper()} {h['chi'].upper()} CƯỚI " + ("KHÔNG PHẠM KIM LÂU" if h["kl"] is None else "PHẠM " + KL[h["kl"]]))
    rows = [(a.upper(), "TAM HỢP", near(a, y)), (b.upper(), "TAM HỢP", near(b, y)),
            (h["lh"].upper(), "LỤC HỢP", near(h["lh"], y)), (h["xu"].upper(), "LỤC XUNG", near(h["xu"], y))]
    day, slot = SLOTS_FS[y]
    return {
        "id": f"r27_hop{y}", "day": day, "slot": slot, "replaces": None, "theme": THEMES[y],
        "chip": f"{h['can'].upper()} {h['chi'].upper()} · {y}",
        "title_html": f'<span class="l s">SINH NĂM {y}</span><span class="l gold">HỢP TUỔI NÀO?</span>',
        "title": f"Sinh năm {y} {h['can']} {h['chi']} hợp tuổi nào?",
        "script": [f"Sinh năm {WORD[y]}, tuổi {h['can']} {h['chi']}, hợp tuổi nào?",
                   f"Tam hợp là tuổi **{a}** và tuổi **{b}**, lục hợp là tuổi **{h['lh']}**.",
                   f"Tuổi **{h['xu']}** lục xung, nên cân nhắc.",
                   kl_line,
                   "Dừng hình tìm năm sinh người ấy nhé."],
        "rows": rows, "foot": foot,
        "css": ".years, .years.col4 { grid-template-columns: repeat(2, 1fr) !important; } .tag { white-space: normal !important; } "
               ".lab { flex: 0 0 250px !important; min-width: 0; } #subfoot { font-size: 30px !important; }",
        "insight": (f"Sinh năm {y} ({h['can']} {h['chi']}): tam hợp tuổi {a} ({', '.join(map(str, near(a, y)))}) và {b} "
                    f"({', '.join(map(str, near(b, y)))}), lục hợp tuổi {h['lh']} ({', '.join(map(str, near(h['lh'], y)))}), "
                    f"lục xung tuổi {h['xu']} ({', '.join(map(str, near(h['xu'], y)))}). Năm 2027 tuổi mụ {h['tuoi_mu']}: nữ cưới hỏi "
                    + ("không phạm Kim Lâu." if h["kl"] is None else f"phạm {KL_VI[h['kl']]}.") + " Theo truyền thống, để tham khảo."),
        "source": SRC,
        "tags": [f"{y} hop tuoi nao", f"sinh nam {y} hop tuoi nao", f"tuoi {h['chi'].lower()} hop tuoi nao", "hop tuoi vo chong", "tam hop"],
        "tags_vi": [f"{y} hợp tuổi nào", f"tuổi {h['can']} {h['chi']} hợp tuổi nào", "hợp tuổi vợ chồng"],
        "hashtags": ["#Shorts", "#hoptuoi", f"#tuoi{h['chi'].lower().replace('ỵ', 'y').replace('ợ', 'o')}", "#phongthuy"],
        **({"novelty_ok": "khác đề f41_d (mệnh, màu) — đây là hợp tuổi"} if y == 2000 else {}),
    }


FS_ITEMS = [fs_item(y) for y in sorted(SLOTS_FS)]
for it in FS_ITEMS:
    for k, v in FS_COMMON.items():
        it.setdefault(k, v)

# ------------------------------------------------------------------ BUD
SRC_DB = ("Chú Đại Bi (Nīlakaṇṭha Dhāraṇī), bản Già Phạm Đạt Ma (Bhagavaddharma, T.1060). Nghĩa theo bản phục hồi tiếng Phạn của "
          "Lokesh Chandra (1988), tóm tại https://en.wikipedia.org/wiki/N%C4%ABlaka%E1%B9%87%E1%B9%ADha_Dh%C4%81ra%E1%B9%87%C4%AB")
DB = {"lane": "niem", "test_cell": "R27_daibi", "style": "statue_cards", "novelty_ok": "series Chú Đại Bi, phần nối tiếp có chủ ý"}
DT = {"lane": "tuong", "test_cell": "R27_doithuong", "style": "statue_cards"}
BUD_ITEMS = [
    {"id": "r27_ngu", "day": "2026-10-28", "slot": "16:20", "replaces": None, **DT, "title": "Đức Phật dạy ngủ mấy tiếng mỗi đêm?",
     "script": ["Đức Phật dạy người tu ngủ mấy tiếng mỗi đêm?",
                "Chỉ **một phần ba** đêm, đúng vào **canh giữa**.",
                "Kinh Trung Bộ một trăm lẻ bảy dạy: canh đầu, đi kinh hành và ngồi thiền.",
                "Canh giữa, nằm nghiêng bên phải theo **thế sư tử**, chân này đặt lên chân kia.",
                "Vẫn giữ **chánh niệm**, nhớ giờ thức dậy, rồi canh cuối lại dậy tu tiếp.",
                "Bạn thường ngủ mấy tiếng mỗi đêm?"],
     "source": "Kinh Trung Bộ 107 (mn107:6.2), bản Bhikkhu Sujato (CC0): https://suttacentral.net/mn107/en/sujato — 'In the first watch of the night, "
               "continue to practice walking and sitting meditation. In the middle watch, lie down in the lion's posture—on the right side, placing one foot "
               "on top of the other—mindful and aware, and focused on the time of getting up. In the last watch, get up and continue…'",
     "insight": "Kinh Trung Bộ 107: người tu canh đầu kinh hành và ngồi thiền, canh giữa nằm nghiêng bên phải theo thế sư tử, chánh niệm, nhớ giờ dậy; "
                "canh cuối dậy tu tiếp — tức chỉ ngủ một phần ba đêm.",
     "tags": ["duc phat ngu", "the su tu", "kinh trung bo", "doi song duc phat", "nha su ngu"],
     "tags_vi": ["đức phật ngủ", "thế sư tử", "kinh trung bộ"], "hashtags": ["#Shorts", "#đứcphật", "#kinhtrungbộ", "#phậtpháp"]},
    {"id": "r27_dep", "day": "2026-10-31", "slot": "08:00", "replaces": None, **DT, "title": "Đức Phật cho phép đi dép loại nào?",
     "script": ["Đức Phật cho phép nhà sư đi dép loại nào?",
                "Chuyện bắt đầu từ một vị sư từng bỏ lại **tám mươi xe tiền vàng**.",
                "Ngài **Sô Na** xuất thân giàu sang, Đức Phật cho riêng ngài đi dép **một lớp đế**.",
                "Ngài thưa: nếu cả Tăng đoàn không được đi, con cũng **không đi**.",
                "Từ đó Đức Phật cho mọi vị tỳ kheo đi dép một lớp đế, và cấm dép **nhiều lớp**.",
                "Bạn nghĩ ngài Sô Na từ chối như vậy là vì sao?"],
     "source": "Luật tạng, Đại phẩm, chương Da (pli-tv-kd5:1.29–1.30), bản Bhikkhu Brahmali (CC0): https://suttacentral.net/pli-tv-kd5/en/brahmali — "
               "'Soṇa, you were brought up in great comfort. I allow you to use sandals with single-layered soles.' 'When I went forth … I left behind "
               "eighty cartloads of gold coins … If you allow them to the Sangha of monks, I too will use them.' 'I allow sandals with single-layered soles. "
               "But you shouldn't wear sandals with double-layered soles …'",
     "insight": "Luật tạng (Đại phẩm 5): ngài Soṇa Koḷivisa, người đã bỏ lại tám mươi xe tiền vàng, không nhận đặc ân đi dép riêng; Đức Phật bèn cho mọi tỳ kheo "
                "đi dép một lớp đế và cấm dép nhiều lớp.",
     "tags": ["nha su di dep", "luat tang", "doi song duc phat", "ngai sona", "tang doan"],
     "tags_vi": ["nhà sư đi dép", "luật tạng", "đời sống đức phật"], "hashtags": ["#Shorts", "#luậttạng", "#đứcphật", "#phậtpháp"]},
    {"id": "r27_tam", "day": "2026-11-01", "slot": "03:30", "replaces": None, **DT, "title": "Đức Phật có tắm sông không?",
     "script": ["Đức Phật có tắm sông không?",
                "Có, và kinh còn ghi Ngài **đứng chờ khô người** sau khi tắm.",
                "Kinh Trung Bộ hai mươi sáu kể: Đức Phật rủ ngài **A Nan** ra **cổng phía đông** để tắm.",
                "Tắm xong, Ngài bước lên, đứng trong **một tấm y**, chờ cho khô người.",
                "Ngài A Nan liền thưa: am của Bà la môn **Ram ma ca** ở gần đây, xin Ngài ghé qua.",
                "Bạn có biết hôm ấy ở am đó, Đức Phật đã giảng gì không?"],
     "source": "Kinh Trung Bộ 26 (mn26:3.6–3.11), bản Bhikkhu Sujato (CC0): https://suttacentral.net/mn26/en/sujato — 'Come, Ānanda, let's go to the eastern "
               "gate to bathe.' … 'When he had bathed and emerged from the water he stood in one robe drying his limbs.' … 'Sir, the hermitage of the brahmin "
               "Rammaka is nearby.'",
     "insight": "Kinh Trung Bộ 26 (Thánh Cầu): Đức Phật cùng ngài A Nan ra cổng phía đông tắm, tắm xong đứng trong một tấm y chờ khô người; ngài A Nan mời Ngài "
                "ghé am Bà la môn Rammaka gần đó, nơi chư tăng đang chờ nghe pháp.",
     "tags": ["duc phat tam", "kinh trung bo 26", "ngai a nan", "doi song duc phat", "kinh thanh cau"],
     "tags_vi": ["đức phật tắm", "kinh trung bộ", "ngài a nan"], "hashtags": ["#Shorts", "#đứcphật", "#kinhtrungbộ", "#phậtpháp"]},
    {"id": "r27_thuoc", "day": "2026-11-02", "slot": "12:30", "replaces": None, **DT, "title": "Đức Phật cho nhà sư dùng 5 thứ thuốc nào?",
     "script": ["Đức Phật cho nhà sư dùng năm thứ thuốc nào?",
                "Thật ra đó không phải thuốc đắng, mà là **bơ, dầu và mật**.",
                "Luật tạng kể: một mùa thu, chư tăng ốm, ăn cháo cũng **không giữ được**, người gầy rộc.",
                "Đức Phật nghĩ tới những thứ bồi bổ mà **không tính là bữa ăn**.",
                "Đó là **bơ lỏng**, **bơ** và **dầu**, thêm **mật ong** và **mật mía**.",
                "Trong nhà bạn, thứ nào luôn có sẵn?"],
     "source": "Luật tạng, Đại phẩm, chương Dược (pli-tv-kd6:1.1–1.3), bản Bhikkhu Brahmali (CC0): https://suttacentral.net/pli-tv-kd6/en/brahmali — "
               "'the monks were afflicted with autumn illness, and they could keep down neither congee nor other food … There are these five tonics—ghee, "
               "butter, oil, honey, and syrup—that are generally regarded as tonics, serve as nourishment, but aren't considered substantial food.'",
     "insight": "Luật tạng (Đại phẩm 6): khi chư tăng ốm mùa thu, ăn cháo không giữ được, Đức Phật cho dùng năm thứ bồi bổ không tính là bữa ăn: bơ lỏng, bơ, "
                "dầu, mật ong, mật mía.",
     "tags": ["nam thu thuoc", "luat tang", "doi song nha su", "duc phat", "bo dau mat"],
     "tags_vi": ["năm thứ thuốc", "luật tạng", "đời sống nhà sư"], "hashtags": ["#Shorts", "#luậttạng", "#đứcphật", "#phậtpháp"]},
    {"id": "r27_db8", "day": "2026-11-03", "slot": "08:00", "replaces": None, **DB, "title": "Câu thứ tám Chú Đại Bi nghĩa là gì?",
     "script": ["Câu thứ tám Chú Đại Bi nghĩa là gì?",
                "Trong câu này có một chữ nghĩa là **chiến thắng**.",
                "Câu đầy đủ là: **Độ lô độ lô phạt xà da đế, ma ha phạt xà da đế**.",
                "Theo bản tiếng Phạn phục hồi, **phạt xà da** là **vi gia da**, nghĩa là chiến thắng.",
                "Cả câu là: giữ vững, giữ vững, hỡi đấng chiến thắng, hỡi đấng **đại chiến thắng**.",
                "Bạn có muốn nghe tiếp câu thứ chín không?"],
     "source": SRC_DB + " — 'dhuru-dhuru vijayate mahāvijayate' (Chandra: 'Hold fast, hold fast, Victor, oh Great Victor'); 度盧度盧罰闍耶帝 摩訶罰闍耶帝.",
     "insight": "Câu thứ tám Chú Đại Bi (Độ lô độ lô phạt xà da đế, ma ha phạt xà da đế) theo bản tiếng Phạn phục hồi là dhuru-dhuru vijayate mahāvijayate: "
                "giữ vững, giữ vững, hỡi đấng chiến thắng, hỡi đấng đại chiến thắng.",
     "tags": ["chu dai bi", "y nghia chu dai bi", "phat xa da de", "quan the am", "phat phap"],
     "tags_vi": ["chú đại bi", "ý nghĩa chú đại bi", "quán thế âm"], "hashtags": ["#Shorts", "#chúđạibi", "#quánthếâm", "#phậtpháp"]},
    {"id": "r27_db9", "day": "2026-11-03", "slot": "23:00", "replaces": None, **DB, "title": "Câu thứ chín Chú Đại Bi nghĩa là gì?",
     "script": ["Câu thứ chín Chú Đại Bi nghĩa là gì?",
                "Câu này gọi Đức Quán Âm là **chúa tể của mặt đất**.",
                "Câu đầy đủ là: **Đà ra đà ra, địa rị ni, thất Phật ra da**.",
                "Theo bản tiếng Phạn phục hồi, nghĩa là: giữ lấy, giữ lấy, hỡi **chúa tể của mặt đất**.",
                "Rồi đến **giá ra giá ra**, nghĩa là: hãy chuyển động, hãy chuyển động.",
                "Bạn thường tụng Chú Đại Bi vào buổi sáng hay buổi tối?"],
     "source": SRC_DB + " — 'dhara-dhara dharāṇi-rāja | cala-cala' (Chandra: 'Hold on, hold on, oh Lord of the Earth. Move, move …'); 陀囉陀囉 地唎尼 室佛囉耶.",
     "insight": "Câu thứ chín Chú Đại Bi (Đà ra đà ra, địa rị ni, thất Phật ra da) theo bản tiếng Phạn phục hồi là dhara-dhara dharāṇi-rāja: giữ lấy, giữ lấy, "
                "hỡi chúa tể của mặt đất; tiếp theo 'giá ra giá ra' (cala-cala) là hãy chuyển động.",
     "tags": ["chu dai bi", "y nghia chu dai bi", "da ra da ra", "quan the am", "phat phap"],
     "tags_vi": ["chú đại bi", "ý nghĩa chú đại bi", "quán thế âm"], "hashtags": ["#Shorts", "#chúđạibi", "#quánthếâm", "#phậtpháp"]},
]
for it in BUD_ITEMS:
    it.update({"series": "bud", "badge": "", "cta": "Bạn nghĩ sao? Bình luận nhé."})

IMG = {"r27_ngu": "statue_japan_02", "r27_dep": "statue_gandhara_04", "r27_tam": "statue_india_03", "r27_thuoc": "statue_china_03",
       "r27_db8": "statue_vietnam_06", "r27_db9": "statue_vietnam_06"}
for rid, sid in IMG.items():
    R5.IMG[rid] = (R5.bank_path(sid), 250 if sid == "statue_vietnam_06" else 230, 0.9 if sid == "statue_vietnam_06" else 0.92)


def bank_credit(sid: str) -> tuple[str, str, str]:
    s = next(x for x in json.loads((ROOT / "output/cl_staging/bud/banks/statues.json").read_text(encoding="utf-8")) if x["id"] == sid)
    return (f"{s['title']} — {s.get('author') or 'Wikimedia Commons'}, {s['license']}", f"{s['title']} · {s['license']}", s["license"])


QA_CR = ("Tượng Quan Âm nghìn mắt nghìn tay (mẫu chùa Bút Tháp, 1656), Bảo tàng Lịch sử Quốc gia, ảnh Daderot — Wikimedia Commons, CC0",
         "Quan Âm nghìn mắt nghìn tay · mẫu chùa Bút Tháp · ảnh Daderot, CC0", "CC0")
for rid, sid in IMG.items():
    R5.CREDITS[rid] = QA_CR if sid == "statue_vietnam_06" else bank_credit(sid)
big = lambda s, fs=56: f'<div class="big warm" style="font-size:{fs}px">{s}</div>'
sub = lambda s: f'<div class="sub">{s}</div>'
R5.CARDS.update({
    "r27_ngu": [None, big("CHỈ 1/3 ĐÊM · CANH GIỮA", 52), sub("Kinh Trung Bộ 107") + big("CANH ĐẦU: KINH HÀNH<br>NGỒI THIỀN", 52),
                big("NẰM NGHIÊNG PHẢI<br>THẾ SƯ TỬ", 54), sub("canh cuối") + big("DẬY TU TIẾP"), None],
    "r27_dep": [None, sub("một vị sư từng bỏ lại") + big("80 XE TIỀN VÀNG", 56), sub("riêng ngài Sô Na") + big("DÉP MỘT LỚP ĐẾ", 56),
                sub("ngài thưa") + big("CẢ TĂNG ĐOÀN KHÔNG ĐI<br>CON CŨNG KHÔNG ĐI", 48), sub("Luật tạng · Đại phẩm 5") + big("MỌI TỲ KHEO: MỘT LỚP<br>CẤM DÉP NHIỀU LỚP", 48), None],
    "r27_tam": [None, big("CÓ · ĐỨNG CHỜ KHÔ NGƯỜI", 50), sub("Kinh Trung Bộ 26") + big("CÙNG NGÀI A NAN<br>RA CỔNG PHÍA ĐÔNG", 52),
                big("ĐỨNG TRONG MỘT TẤM Y", 54), sub("ngài A Nan thưa") + big("XIN GHÉ AM GẦN ĐÂY", 54), None],
    "r27_thuoc": [None, sub("không phải thuốc đắng") + big("BƠ · DẦU · MẬT"), sub("Luật tạng · Đại phẩm 6") + big("ỐM MÙA THU<br>ĂN CHÁO KHÔNG GIỮ ĐƯỢC", 48),
                  big("BỒI BỔ MÀ KHÔNG<br>TÍNH LÀ BỮA ĂN", 52), 'LIST', None],
    "r27_db8": [None, big("MỘT CHỮ = CHIẾN THẮNG", 52), sub("Câu thứ tám") + big("ĐỘ LÔ ĐỘ LÔ<br>PHẠT XÀ DA ĐẾ…", 50),
                sub("phạt xà da") + big("= VIJAYA · CHIẾN THẮNG", 50), sub("giữ vững, giữ vững") + big("HỠI ĐẤNG<br>ĐẠI CHIẾN THẮNG", 52), None],
    "r27_db9": [None, big("CHÚA TỂ CỦA MẶT ĐẤT", 52), sub("Câu thứ chín") + big("ĐÀ RA ĐÀ RA<br>ĐỊA RỊ NI · THẤT PHẬT RA DA", 46),
                sub("giữ lấy, giữ lấy") + big("HỠI CHÚA TỂ<br>CỦA MẶT ĐẤT", 54), sub("giá ra giá ra") + big("HÃY CHUYỂN ĐỘNG"), None],
})
R5.LISTS.update({"r27_thuoc": ["Bơ lỏng · bơ · dầu", "Mật ong · mật mía"]})
R5.HEAD.update({
    "r27_ngu": ("ĐỜI THƯỜNG CỦA ĐỨC PHẬT", "ĐỨC PHẬT DẠY NGỦ<br><span class=\"warm\">MẤY TIẾNG MỖI ĐÊM?</span>", "KINH TRUNG BỘ 107"),
    "r27_dep": ("ĐỜI THƯỜNG CỦA ĐỨC PHẬT", "ĐỨC PHẬT CHO PHÉP<br><span class=\"warm\">ĐI DÉP LOẠI NÀO?</span>", "LUẬT TẠNG · ĐẠI PHẨM 5"),
    "r27_tam": ("ĐỜI THƯỜNG CỦA ĐỨC PHẬT", "ĐỨC PHẬT CÓ<br><span class=\"warm\">TẮM SÔNG KHÔNG?</span>", "KINH TRUNG BỘ 26"),
    "r27_thuoc": ("ĐỜI THƯỜNG CỦA ĐỨC PHẬT", "5 THỨ THUỐC<br><span class=\"warm\">ĐỨC PHẬT CHO DÙNG</span>", "LUẬT TẠNG · ĐẠI PHẨM 6"),
    "r27_db8": ("CÂU CHÚ QUEN THUỘC · PHẦN 8", "CÂU THỨ TÁM <span class=\"warm\">CHÚ ĐẠI BI</span><br>NGHĨA LÀ GÌ?", "BẢN TIẾNG PHẠN · LOKESH CHANDRA 1988"),
    "r27_db9": ("CÂU CHÚ QUEN THUỘC · PHẦN 9", "CÂU THỨ CHÍN <span class=\"warm\">CHÚ ĐẠI BI</span><br>NGHĨA LÀ GÌ?", "BẢN TIẾNG PHẠN · LOKESH CHANDRA 1988"),
})
R5.ACCENT.update({"r27_ngu": ("#9fd3c7", "#0b2420"), "r27_dep": ("#f2b48a", "#2b1407"), "r27_tam": ("#9fd3c7", "#0b2420"),
                  "r27_thuoc": ("#f2b48a", "#2b1407"), "r27_db8": ("#f4cf6b", "#2a1a05"), "r27_db9": ("#f4cf6b", "#2a1a05")})

BGM = {}
for it in FS_ITEMS + BUD_ITEMS:
    hf_music.short_pick(it)
    BGM[it["id"]] = json.loads((ROOT / f"output/cl_staging/{it['series']}/bgm_shorts.json").read_text())[it["id"]]["file"]
R4.BGM.update(BGM)
R5.BGM.update(BGM)
R6.BGM.update(BGM)


def html_table(it: dict, dur: float) -> str:
    segs = json.loads((D / f"{it['id']}_final.json").read_text(encoding="utf-8"))["segments"]
    lines = [s.replace("**", "") for s in it["script"]]
    sg = [{"start": round(s["start"] + 0.3, 3), "end": round(s["end"] + 0.3, 3), "text": x} for s, x in zip(segs, lines)]
    data = {"dur": dur, "segs": sg, "theme": it["theme"], "rows": [{"chi": c, "tag": tag, "years": ys} for c, tag, ys in it["rows"]]}
    html = (R6.F.COMP / "review_yeartable.html").read_text(encoding="utf-8")
    amber = ('amber: { b1: "#d97706", b2: "#b45309", b3: "#78350f", b4: "#451a03", r1: "rgba(120,53,15,.94)", r2: "rgba(69,26,3,.94)", '
             'gold: "#fde68a", gold2: "#fef08a", chip: "#fffbeb", chipfg: "#78350f", chiptop: "#fde68a", chiptopfg: "#78350f" },')
    if "amber:" not in html:
        html = html.replace("const THEMES = {", "const THEMES = {\n    " + amber)
    css = ("#head { top: 90px; } #rows { top: 430px; bottom: 310px; gap: 16px; } #cap { bottom: 195px; font-size: 44px; }"
           " #subfoot { position: absolute; left: 50px; right: 50px; bottom: 120px; text-align: center; color: var(--gold2); font-weight: 800;"
           " font-size: 32px; letter-spacing: .05em; text-shadow: 0 2px 8px rgba(0,0,0,.6); } #foot { bottom: 65px; font-size: 24px; opacity: .82; }"
           " .tag { white-space: nowrap; } " + it.get("css", ""))
    html = html.replace("</style>", css + "</style>")
    html = html.replace('<div id="foot">', f'<div id="subfoot">{it["foot"]}</div>\n  <div id="foot">')
    return (html.replace("__DUR__", str(dur)).replace("__CHIP__", it["chip"]).replace("__TITLE__", it["title_html"])
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)))


def library_motion(h: str) -> str:
    old_show = 'tl.fromTo(id, {opacity: 0, y: 26, filter: "blur(8px)"}, {opacity: 1, y: 0, filter: "blur(0px)", duration: 0.7, ease: "power2.out"}, at)'
    assert old_show in h
    h = h.replace(old_show, 'tl.fromTo(id, {opacity: 0, y: 26}, {opacity: 1, y: 0, duration: 0.6, ease: "expo.out"}, at)')
    h = h.replace('ease:"back.out(1.8)"', 'ease:"expo.out"')
    assert "blur(" not in h.split("<script>")[-1] and "back.out" not in h
    return h


def list_stagger(rid: str, h: str) -> str:
    items = R5.LISTS.get(rid, [])
    if len(items) <= 1:
        return h
    i = R5.CARDS[rid].index("LIST")
    extra = "".join(f'tl.fromTo("#li{k}", {{opacity:0,x:-40}}, {{opacity:1,x:0,duration:0.5,ease:"expo.out"}}, T[{i}] + {0.9 * k:.1f});'
                    for k in range(1, len(items)))
    later = next((j for j in range(i + 1, len(R5.CARDS[rid])) if R5.CARDS[rid][j]), None)
    if later is not None:
        extra += f'tl.to("#list", {{opacity:0, y:-18, duration:0.45, ease:"power1.in"}}, T[{later}] - 0.45);'
    return h.replace("\n</script></body></html>", "\n" + extra + "\n</script></body></html>")


def main() -> int:
    html_only = "--html-only" in sys.argv
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
    R6.guards(FS_ITEMS + BUD_ITEMS)
    jobs = []
    for it in FS_ITEMS:
        R6.tts(it, None)
        it["dur"] = max(9.5, round(json.loads((D / f"{it['id']}_final.json").read_text())["duration_s"] + 0.3 + 3.2, 2))
        jobs.append((it, html_table(it, it["dur"]), R4.FS_OUT, 0.3, False))
    for it in BUD_ITEMS:
        R6.tts(it, (0.6, 0.8))
        it["dur"] = round(json.loads((D / f"{it['id']}_final.json").read_text())["duration_s"] + 0.5 + 3.6, 2)
        h = library_motion(list_stagger(it["id"], R5.html_statue(it["id"], R5.segs(it["id"], 0.5), it["dur"])))
        jobs.append((it, h, R4.BUD_OUT, 0.5, True))
    plan_fs = [{k: v for k, v in it.items() if k not in ("rows", "css")} | {"rows": [[c, t, y] for c, t, y in it["rows"]]} for it in FS_ITEMS]
    validate(plan_fs)
    validate(BUD_ITEMS)
    FS_PLAN.write_text(json.dumps(plan_fs, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    BUD_PLAN.write_text(json.dumps(BUD_ITEMS, ensure_ascii=False, indent=1), encoding="utf-8")
    for it, h, *_ in jobs:
        (B.COMP / f"_r_{it['id']}.html").write_text(h, encoding="utf-8")
        print(f"[{it['id']}] composition dur={it['dur']}s")
    if html_only:
        return 0
    for it, _, out_dir, dl, bell in jobs:
        rid = it["id"]
        if only and rid not in only:
            continue
        silent, mp4 = D / f"{rid}_silent.mp4", out_dir / f"{rid}.mp4"
        B.to_trash(silent); B.to_trash(mp4)
        print(f"[{rid}] render ...", flush=True)
        R4.render(f"_r_{rid}.html", silent)   # có cổng tràn chữ (hf_qa.gate_overflow)
        vl, gain, ml = R4.mix(rid, silent, D / f"{rid}_final.wav", mp4, it["dur"], dl, bell)
        B.to_trash(silent)
        cred = R5.CREDITS.get(rid)
        meta = {"ok": True, "output": str(mp4.relative_to(ROOT)), "duration_s": it["dur"], "style": it["style"], "lane": it["lane"],
                "replaces": None, "test_cell": it["test_cell"], "bgm": f"bgm/{BGM[rid]}", "bgm_title": hf_music.TITLES[BGM[rid]],
                "bgm_gain": round(gain, 4), "media_credits": ([{"id": rid, "kind": "commons", "license": cred[2], "credit": cred[0]}] if cred else []),
                "voice": "Sơn" if it["series"] == "fs" else "Binh", "lufs": {"voice": round(vl, 1), "mix": round(ml, 1), "offset_db": -20.0}}
        if bell:
            meta["sfx_credit"] = B.BELL_CREDIT
        (out_dir / f"{rid}.render.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{rid}] xong {mp4.name} | LUFS giọng {vl:.1f} mix {ml:.1f}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
