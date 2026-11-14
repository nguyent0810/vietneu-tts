"""Gán ảnh + sơ đồ tự động cho 9 Long ngắn tháng 11 âm (Tý…Thân). Chạy từ gốc repo:
    .venv/bin/python tools/long/month_tuoi_map.py ty [--dry]
Luật: ảnh theo từ khoá câu; không lặp ảnh trong cùng chương, không lặp câu kề;
bảng chỉ đặt sau câu 44 (~120s); panorama ở chương "ai cũng nhớ" và chương cuối."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "output/cl_staging/long/research/t11_12tuoi/nine"
FACTS = ROOT / "output/cl_staging/long/research/t11_12tuoi/facts9"
sys.path.insert(0, str(ROOT))
from tools.long.apply_lib import pano, apply, L, F, N, A, HAC  # noqa: E402
G = A + "t11_ngo/"
X = A + "t11_9/"

def _load_config(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data.get("T"), dict) or not isinstance(data.get("CMP"), dict):
        raise ValueError("config cần có hai bảng T và CMP")
    return data["T"], data["CMP"]

NUM = {"một": 1, "hai": 2, "ba": 3, "bốn": 4, "năm": 5, "sáu": 6, "bảy": 7}
FACT_KEY = {"ty": "Tý", "mao": "Mão", "hoi": "Hợi", "tuat": "Tuất", "dau": "Dậu", "suu": "Sửu", "thin": "Thìn", "ty2": "Tỵ", "than": "Thân"}

ELEM = {"Thổ": [F + "fs27_dat_thanh.png", F + "fs27_dat_nen.png", F + "fs27_dat_ven.png", F + "fs27_dat_cat.png"],
        "Mộc": [F + "fs27_go_rung.png", F + "fs27_go_dau.png", F + "fs27_go_luu.png", F + "fs27_moc_son.png"],
        "Thủy": [F + "fs27_nuoc_khe.png", F + "fs27_khe_lon.png", F + "fs27_nuoc_bien.png", F + "fs27_go_nuoc.png"],
        "Hỏa": [F + "fs27_lua_lo.png", F + "fs27_lua_troi.png", F + "fs27_lua_nui.png", F + "fs27_lua_den.png"],
        "Kim": [F + "fs27_vang_bac.png", F + "fs27_vang_kiem.png", F + "fs27_vang_bien.png", L + "lib01_trang_suc_vang_169.png"]}
# (regex, ảnh) theo thứ tự ưu tiên; ảnh X* chỉ dùng khi file đã về
KW = [
 (r"nữ mạng|\bNữ\b|nữ \*\*\d", [N + "mui_nguoi_lich.png", F + "fs27_ba_mau.png"]),
 (r"Noel", [N + "dan_noel_pho.jpg", X + "ty_cuoi_noel.png"]),
 (r"cưới|thiệp|cô dâu|chú rể", [N + "dan_thiep_cuoi.png", N + "dan_hai_ho.png", X + "ty_cuoi_noel.png", X + "ty_hai_nha.png"]),
 (r"Đông chí", [X + "ty_dong_chi.png", L + "fs_vt_wall_winter_gpt.png"]),
 (r"[Rr]ằm", [X + "suu_ram.png", L + "lib01_ho_sen_suong_som_169.png"]),
 (r"31 tháng 12|giao thừa|đón năm", [X + "dau_giao_thua.png", N + "mui_dem_3112.png"]),
 (r"1 tháng 1|năm mới|2027", [X + "tuat_binh_minh.png", X + "tuat_so_tay.png", N + "mui_lich_2027.png", L + "lib02_canh_mai_vang_tet_169.png"]),
 (r"[Tt]ết", [L + "lib02_banh_chung_tet_169.png", L + "lib02_mam_ngu_qua_tet_169.png", G + "ngo_cua_xuan.png"]),
 (r"tiệc|bạn bè", [X + "dau_tiec.png"]),
 (r"đi xa|xuất hành|di chuyển|chuyến", [X + "dau_ben_xe.png", X + "than_xuat_hanh.png", N + "dan_buoc_di.png", G + "ngo_vali.png"]),
 (r"chuyển nhà|nhập trạch|dọn về", [X + "hoi_chuyen_nha.png", X + "hoi_bep_moi.png", X + "hoi_nha_trong.png"]),
 (r"động thổ|làm nhà|xây|Hoang Ốc|Kim Lâu", [X + "thin_dong_tho.png", N + "mui_dong_tho.jpg", N + "dan_nha_dang_xay.png", X + "tyz_nha_do.png", X + "thin_ban_ve.png", L + "lib04_gach_xep_xay_nha_169_1_c8d0b4c4_2K.jpg", L + "lib03_nha_ba_gian_bac_bo_169_1_8e9fb5ac.jpg"]),
 (r"ký|hợp đồng|khai trương", [X + "than_ky_ket.png", G + "ngo_ky_giay.png", X + "tuat_khai_truong.png"]),
 (r"tiền|tiết kiệm|giữ của|chi tiêu|phong bì", [X + "mao_vi_tien.png", X + "mao_hop_go.png", L + "lib01_trang_suc_vang_169.png"]),
 (r"Bạch Hổ", [X + "than_bach_ho.png"]),
 (r"Kim Quỹ", [X + "than_kim_quy.png"]),
 (r"Thiên Lao", [X + "tuat_song_sat.png"]),
 (r"Thái Tuế|la bàn", [G + "ngo_la_ban.png", L + "lib02_la_ban_phong_thuy_169.png", L + "fs_compass_1_ed0ca288.jpg"]),
 (r"tam tai", [F + "fs27_ba_nam_tai.png", F + "fs27_ba_nam2.png"]),
 (r"tam hợp|lục hợp", [F + "fs27_ba_tuong_hop.png", X + "thin_tam_hop.png", F + "fs27_hop2.png"]),
 (r"hắc đạo|Nguyệt kỵ|Câu Trần|Chu Tước|Nguyên Vũ|Thiên Hình", [G + "ngo_hac_dao.png", F + "fs27_im_dem.png", F + "fs27_cua_kin.png"]),
 (r"hoàng đạo|Thanh Long|Minh Đường|Ngọc Đường|Kim Đường|Tư Mệnh", [G + "ngo_thanh_long.png", F + "fs27_ban_sang.png", F + "fs27_sang_san.png"]),
 (r"cúng|thắp hương|lễ", [L + "lib03_dinh_lang_bac_bo_ab_169_1_0102b197.jpg", L + "lib04_san_chua_gach_bat_trang_169_1_43452f16_2K.jpg"]),
 (r"lịch|ngày|tháng", [L + "lib01_lich_am_trang_cu_169.png", L + "lib02_lich_van_nien_treo_tuong_169.png", L + "fs_vt_co_calendar_gpt.png", G + "ngo_khoanh_ngay.png", X + "mao_mot_ngay.png", X + "hoi_trang_dau.png"]),
]
GENERIC = [L + "lib01_am_tra_chen_tra_169.png", L + "lib01_sach_xua_cuon_tre_169.png", L + "lib01_nghien_muc_but_long_169.png",
           F + "fs27_den_ban.png", F + "fs27_ban_giay.png", F + "fs27_hop_giay.png", F + "fs27_but_dung.png", L + "lib04_ban_tra_ghe_may_169_1_60740f3b_2K.jpg",
           L + "lib03_cua_chinh_nha_co_169_1_ae3c704d.jpg", F + "fs27_cua_mo.png", L + "lib01_tre_nang_som_169.png", F + "fs27_im_ban.png",
           L + "lib04_hien_nha_ngoi_mua_169_1_c1875f75_2K.jpg", L + "lib02_dong_ho_cat_169.png", F + "fs27_giay_gap.png", F + "fs27_ruong_xanh.png"]
DATE = re.compile(r"\b\d{1,2} tháng \d{1,2}\b")
TABLE_MIN = 50  # đo thực tế: mốc 120 giây rơi trong vùng câu 49–52


def ok(p):
    return Path(p).exists()


def fmt(d):
    y, m, dd = d["duong"].split("-")
    return f"{int(dd)}/{int(m)}"


def clamp_visual_spans(vis, heads, n):
    keys = sorted(vis)
    for a, b in zip(keys, keys[1:] + [n + 1]):
        next_head = min([h for h in heads if h > a] + [b])
        if "until" in vis[a]:
            vis[a]["until"] = max(a, min(int(vis[a]["until"]), b - 1, next_head - 1))
    return vis


def build(key, T, CMP):
    cfg = T[key]
    chi = cfg["chi"]
    facts = json.loads((FACTS / f"t11_{FACT_KEY[key]}_facts.json").read_text(encoding="utf-8"))
    tables = json.loads((FACTS / f"t11_{FACT_KEY[key]}_tables.json").read_text(encoding="utf-8"))
    plan = json.loads((ROOT / f"output/cl_staging/long/plan_L_fs_t11_{key}.json").read_text(encoding="utf-8"))[0]
    lines = plan["script"]
    n = len(lines)
    heads = [i for i, s in enumerate(lines, 1) if s.startswith("**") and s.endswith("**") and s.count("**") == 2]
    chap_of = {}
    c = 0
    for i in range(1, n + 1):
        if i in heads:
            c += 1
        chap_of[i] = c
    VIS, IMG = {}, {}

    def first(pred, lo=1, hi=None, avoid=()):
        for i in range(lo, (hi or n) + 1):
            if i in heads or i in VIS or i in avoid:
                continue
            if pred(lines[i - 1]):
                return i
        return None

    # 1) bánh xe xung: câu đầu sau mở đầu nói tới chi đối xung
    w = first(lambda s: cfg["pair"] in s and ("xung" in s or "Thái Tuế" in s), lo=(heads[0] if heads else 18))
    if w:
        VIS[w] = {"type": "wheel", "title": f"{chi.upper()} · {cfg['pair'].upper()}",
                  "steps": [{"at": w, "rel": "focus", "chi": [chi, cfg["pair"]], "label": "LỤC XUNG"}], "until": w}
    # 2) bảng ngày xung (sau 120s)
    xd = facts["xung_days"]
    last = heads[-1] if heads else n
    tight = {h - d for h in heads for d in (1, 2)}  # bảng cần ≥ 3 câu trước thẻ chương
    x = first(lambda s: "xung" in s and DATE.search(s) and (cfg["pair"] in s or chi in s), lo=TABLE_MIN, hi=last - 1, avoid=tight)
    if x:
        VIS[x] = {"type": "lookup", "title": f"NGÀY XUNG TUỔI {chi.upper()} · THÁNG 11 ÂM", "cols": ["ÂM", "DƯƠNG", "CAN CHI", "THẦN"],
                  "until": min(x + 2, n), "find": [],
                  "rows": [{"cells": [d["am"], fmt(d), d["ngay"], d["than"]], **HAC} for d in xd]}
    # 3) bảng ngày hợp
    gd = facts["good_days"]
    g = first(lambda s: "hợp" in s and "xung" not in s and DATE.search(s), lo=max(TABLE_MIN, (x or 0) + 4), hi=last - 1, avoid=tight)
    if g and gd:
        rows = []
        for d in gd[:7]:
            row = {"cells": [d["am"], fmt(d), d["ngay"], d["than"] + (" · " + d["dan"][0] if d["dan"] else "")]}
            row.update(HAC if d["dan"] or not d["hoang"] else {"good": [3]})
            rows.append(row)
        VIS[g] = {"type": "lookup", "title": f"NGÀY HỢP TUỔI {chi.upper()}", "cols": ["ÂM", "DƯƠNG", "CAN CHI", "THẦN"],
                  "until": min(g + (3 if len(rows) > 4 else 2), n), "find": [], "rows": rows}
    # 4) bảng năm sinh: câu đầu chương năm sinh
    yh = next((h for h in heads if re.search(r"người|câu chuyện|năm sinh", lines[h - 1])), None)
    if yh and "BẢNG NĂM SINH" in tables:
        y = first(lambda s: True, lo=yh + 1)
        t = dict(tables["BẢNG NĂM SINH"])
        t["until"] = min(y + 2, n)
        t["find"] = []
        VIS[y] = t
    # 5) chữ kết
    q = first(lambda s: "năm nào" in s, lo=n - 8)
    if q:
        VIS[q] = {"type": "word", "text": "Bạn sinh năm nào?"}
    # 5b) so sánh mâu thuẫn ở mở đầu (1 câu, ≤ 4s)
    if key in CMP:
        rx, lft, rgt = CMP[key]
        cm = first(lambda s: re.search(rx, s))
        if cm:
            VIS[cm] = {"type": "compare", "until": cm, "left": {**lft, "at": cm}, "right": {**rgt, "at": cm}}
        else:
            print("  !! không thấy câu so sánh", rx)
    # 5c) thẻ số: câu "**hai ngày**"… sau 120s
    near = {j for k2, v in VIS.items() if v.get("type") in ("lookup", "wheel") for j in range(k2 - 1, k2 + 5)}
    st = first(lambda s: re.search(r"\*\*(một|hai|ba|bốn|năm|sáu|bảy) ngày\*\*", s), lo=TABLE_MIN, avoid=near)
    if st:
        w = re.search(r"\*\*(một|hai|ba|bốn|năm|sáu|bảy) ngày\*\*", lines[st - 1]).group(1)
        lab = re.sub(r"\*\*", "", lines[st - 1]).rstrip(".").upper()
        VIS[st] = {"type": "stat", "value": NUM[w], "suffix": " NGÀY", "label": lab[:48], "at": st, "preset": "number_impact"}
    # 5d) trích câu chốt trước câu hỏi kết
    if q and q - 1 not in heads and q - 1 not in VIS:
        VIS[q - 1] = {"type": "quote"}
    # 5e) danh sách lời khuyên ở chương cuối (sau 2 câu panorama)
    if heads:
        lh = heads[-1]
        li = first(lambda s: True, lo=lh + 3, hi=min(lh + 6, n), avoid=(q,))
        clean = [d for d in facts["good_days"] if d["hoang"] and not d["dan"]][:4]
        if li and clean:
            VIS[li] = {"type": "list", "title": f"TUỔI {chi.upper()} · THÁNG 11 ÂM", "until": min(li + 2, n),
                       "items": [{"text": "Tránh việc lớn · " + " · ".join(fmt(d) for d in xd), "at": li},
                                 {"text": "Ngày sạch · " + " · ".join(fmt(d) for d in clean), "at": min(li + 1, n)}]}
    clamp_visual_spans(VIS, heads, n)  # không phủ visual kế tiếp / thẻ chương
    covered = set()
    for k, v in VIS.items():
        covered |= set(range(k, int(v.get("until", k)) + 1))
    # 6) panorama
    ah = next((h for h in heads if "ai cũng nhớ" in lines[h - 1]), None)
    if ah and ah + 2 <= n and not ({ah + 1, ah + 2} & covered):
        IMG[ah + 1] = pano("pano_t11_winter_wide_1080.jpg", [ah + 1, ah + 2])
        covered |= {ah + 1, ah + 2}
    if heads:
        lh = heads[-1]
        if lh + 2 <= n and not ({lh + 1, lh + 2} & covered):
            IMG[lh + 1] = pano("pano_p5_tet_wide_1080.jpg", [lh + 1, lh + 2], "rtl", "warm")
            covered |= {lh + 1, lh + 2}
    # 7) ảnh từng câu
    used_ch = {}
    prev = None
    hero = [X + h + ".png" for h in cfg["hero"] if ok(X + h + ".png")]
    hero_i = 0
    gen_i = 0
    first_head = heads[0] if heads else 18
    for i in range(1, n + 1):
        if i in heads or i in covered or i in IMG:
            continue
        s = lines[i - 1]
        ch = chap_of[i]
        used = used_ch.setdefault(ch, set())
        cands = []
        if i < first_head and hero_i < len(hero) and not any(re.search(r, s) for r, _ in KW[:3]):
            cands.append(hero[hero_i]); hero_i += 1
        for r, imgs in KW:
            if re.search(r, s):
                cands += imgs
        if re.search(rf"\b{chi}\b", s) and cfg["pair"] in s:
            cands = cfg["pairimg"] + cands
        elif re.search(rf"tuổi \**{chi}\b", s):
            cands += cfg["animal"]
        for e, imgs in ELEM.items():
            if re.search(rf"(Thượng|Trung|Hạ|Lưu|Lựu|Lâm|Đầu|Bàng|Khê|Bạch|Phong|Đăng|Lư|Trạch|Lịch|Hà|Bình Địa|Thoa Xuyến|Sơn|Tang|Hải|Giản|Đại|Kiếm|Tuyền|Sa|Ốc|Phú|Tích|Dương Liễu|Thạch|Tùng Bách|Kim Bạch|Trường) [^,.]*{e}\b", s):
                cands += imgs
        cands += hero + cfg["animal"] + GENERIC[gen_i:] + GENERIC[:gen_i]
        pick = next((p for p in cands if ok(p) and p not in used and p != prev), None)
        if pick in GENERIC:
            gen_i = (GENERIC.index(pick) + 1) % len(GENERIC)
        if pick:
            IMG[i] = pick
            used.add(pick)
            prev = pick
    years = cfg["years"]
    META = {"title": cfg["title"], "seo": {"keyword": f"Tuổi {chi} tháng 11"},
            "description": cfg["desc"] + f" Video đi từng ngày theo lịch pháp dân gian, so từng năm sinh tuổi {chi} {years}. Nội dung mang tính tham khảo theo quan niệm truyền thống.",
            "tags": [f"Tuổi {chi} tháng 11", f"tuổi {chi} tháng 11 âm lịch", f"tuổi {chi} 2026", "tháng 11 âm lịch 2026", f"ngày tốt tuổi {chi}",
                     f"tử vi tuổi {chi}", "ngày xung tuổi", "lịch âm tháng 11"] + [f"tuổi {chi} {y.strip()}" for y in years.split(",")[1:4]],
            "day": cfg["day"], "slot": "12:00", "hold": True, "kicker": f"TUỔI {chi.upper()} · THÁNG 11 ÂM",
            "thumbnail_brief": {"text": cfg["thumb"], "pal": "FS"}, "thumbnail": f"L_fs_t11_{key}/thumb_A.jpg",
            "bgm": f"bgm/{cfg['bgm'][0]}.mp3", "bgm_pin": True}
    return IMG, VIS, META, n, heads


def bgm_segments(key, n, heads, T):
    cfg = T[key]
    mid = heads[len(heads) // 2] if heads else n // 2
    cut = round(mid * 3.25, 1)
    return [{"start": 0.0, "end": cut, "mood": "neutral", "track": f"bgm/{cfg['bgm'][0]}.mp3"},
            {"start": cut, "end": round(n * 4.0, 1), "mood": "neutral", "track": f"bgm/{cfg['bgm'][1]}.mp3"}]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ánh xạ media/visual cho plan tháng 11 âm")
    parser.add_argument("key", choices=["ty", "mao", "hoi", "tuat", "dau", "suu", "thin", "ty2", "than"])
    parser.add_argument("--config", default=str(ROOT / "docs/examples/month_tuoi_t11.json"))
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("--reseg", action="store_true")
    args = parser.parse_args()
    key = args.key
    T, CMP = _load_config(args.config)
    IMG, VIS, META, n, heads = build(key, T, CMP)
    seg_p = HERE.parent / "bgm_segments.json"
    segs = json.loads(seg_p.read_text(encoding="utf-8"))
    if key not in segs or args.reseg:
        segs[key] = bgm_segments(key, n, heads, T)
        seg_p.write_text(json.dumps(segs, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.dry:
        print(json.dumps({"img": {k: (v if isinstance(v, str) else "PANO") for k, v in IMG.items()}, "vis": list(VIS)}, ensure_ascii=False, indent=0)[:3000])
    else:
        apply(f"L_fs_t11_{key}", IMG, VIS, META)
