"""prompt_builder: tất định, đa kênh, không đoán câu lệch từ điển."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "prompt_builder", ROOT / "library" / "tools" / "prompt_builder.py")
pb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pb)

QUY = {
    "ngoai_le": ["edge to edge without borders or frames"],
    "cam_phu_dinh": [r"\bno\b", r"\bwithout\b", r"\bnot\b"],
    "cam_tu": ["artwork", "canvas", "painting", "gallery", "museum", "snow",
               "winter", "frame", "frames", "border", "borders"],
    "cam_cum": ["far right edge", "16:9", "1920x1080", "1920"],
    "tu_thay": {
        "painting": "full-bleed photograph",
        "artwork": "full-bleed photograph",
        "canvas": "tabletop photograph",
        "gallery": "sanctuary interior",
        "museum": "pagoda hall",
        "snow": "monsoon twilight",
        "winter": "peaceful morning",
        "far right edge": "comfortably positioned within the right third",
        "frames": "open photographic field",
        "frame": "open photographic field",
        "borders": "open photographic field",
        "border": "open photographic field",
    },
}


def _profile(token, kenh="thu"):
    return {
        "kenh": kenh,
        "assets": {
            "phong_cach": (
                "A full-bleed " + token
                + " {shot} photograph filling the entire frame, edge to edge without borders or frames, shot with a {lens}"
            ),
            "shot": ["tabletop", "macro"],
            "lens": ["50mm f/2.0 prime lens", "85mm f/1.8 prime lens"],
            "van_hoa": "culture " + token,
            "anh_sang": "warm amber light against {nen}",
            "nen": ["deep shadow"],
            "cum_khang_dinh": ["plain wood grain"],
            "cum_theo_nhom": {"la_ban": "brass dial in focus"},
            "nhom_canh": ["la_ban"],
        },
    }


def _plan(texts, durs, media_at=(1,)):
    t = 0.0
    segs = []
    for dur, text in zip(durs, texts):
        segs.append({"start": t, "end": round(t + dur, 3), "text": text})
        t += dur
    return {
        "id": "T",
        "series": "thu",
        "script": list(texts),
        "media": {str(i): {"kind": "image"} for i in media_at},
        "segments": segs,
    }


ENTRIES = [{"vi": "la bàn", "en": "an antique brass compass on dark wood", "nhom": "la_ban"}]


def _build(plan, profile=None, **kw):
    profile = profile or _profile("professional")
    return pb.assemble(plan, plan["id"], 8, profile, entries=ENTRIES, chan=[], quy=QUY, **kw)


def test_cong_thuc_so_anh_bu():
    assert pb.so_anh_bu(20, 8) == 2
    assert pb.so_anh_bu(8, 8) == 0
    assert pb.so_anh_bu(8.01, 8) == 1
    assert pb.so_anh_bu(16, 8) == 1
    assert pb.so_anh_bu(0, 8) == 0
    assert pb.so_anh_bu(25.41, 8) == 3
    assert pb.so_anh_bu(22.95, 8) == 2


def test_so_anh_bu_dung_khi_du_cau():
    texts = [f"Câu {i} có la bàn trên bàn." for i in range(1, 5)]
    plan = _plan(texts, [5, 5, 5, 5])
    matched, missed = _build(plan)
    assert [row["sid_chen"] for row in matched] == [3, 4]
    assert missed == []
    assert len(matched) == pb.so_anh_bu(20, 8)


def test_video_khong_tinh_va_canh_ngan_khong_bu():
    texts = ["la bàn một.", "la bàn hai.", "la bàn ba.", "la bàn bốn."]
    plan = _plan(texts, [3, 3, 10, 10], media_at=(1, 3))
    plan["media"]["3"] = {"kind": "video"}
    matched, missed = _build(plan)
    # Ảnh câu 1 giữ 6s → 0 ảnh bù. Video không sinh prompt.
    assert matched == [] and missed == []


def test_mot_cau_dai_khong_co_ranh_gioi():
    plan = _plan(["Chỉ một câu la bàn."], [20])
    matched, missed = _build(plan)
    assert matched == []
    assert missed and "ranh giới" in missed[0]["ly_do"]
    assert "2" in missed[0]["ly_do"]


def test_tat_dinh():
    texts = [f"Câu {i} có la bàn." for i in range(1, 5)]
    plan = _plan(texts, [5, 5, 5, 5])
    a, _ = _build(plan)
    b, _ = _build(plan)
    assert a == b
    assert a[0]["prompt"] == a[0]["prompt"]
    assert pb._chon_mau("T", 3, "shot", ["tabletop", "macro"]) == pb._chon_mau("T", 3, "shot", ["tabletop", "macro"])


def test_khong_tu_rui_ro_va_co_khoi_phong_cach():
    texts = [f"Câu {i} có la bàn." for i in range(1, 5)]
    plan = _plan(texts, [5, 5, 5, 5])
    matched, _ = _build(plan, _profile("professional", "fs"))
    for row in matched:
        assert pb.van_de(row["prompt"], QUY) == []
        assert "professional" in row["prompt"]
        assert "an antique brass compass on dark wood" in row["prompt"]
        assert "culture professional" in row["prompt"]
        assert "edge to edge without borders or frames" in row["prompt"]
        assert "brass dial in focus" in row["prompt"]
        assert "16:9" not in row["prompt"]


def test_painting_bi_thay_va_no_people_bi_loai():
    profile = _profile("professional")
    plan = _plan(["Một la bàn.", "Một la bàn nữa."], [5, 6])
    bad = [{"vi": "la bàn", "en": "a painting of a compass, no people", "nhom": "la_ban"}]
    matched, missed = pb.assemble(plan, "T", 8, profile, entries=bad, chan=[], quy=QUY)
    assert matched == []
    assert missed and "từ cấm" in missed[0]["ly_do"]
    clean = [{"vi": "la bàn", "en": "a painting of a brass compass", "nhom": "la_ban"}]
    matched, missed = pb.assemble(plan, "T", 8, profile, entries=clean, chan=[], quy=QUY)
    assert missed == []
    assert "painting" not in matched[0]["prompt"]
    assert "full-bleed photograph" in matched[0]["prompt"]


def test_cum_dai_uu_tien_va_khong_dau():
    entries = [
        {"vi": "nhà", "en": "a house", "nhom": "nha"},
        {"vi": "nhà ống", "en": "a tube house", "nhom": "nha"},
    ]
    hit, phrase = pb.match_sentence("Một nhà ống trong ngõ.", entries, [])
    assert phrase == "nhà ống" and hit["en"] == "a tube house"
    hit, phrase = pb.match_sentence("Mot nha ong trong ngo.", entries, [])
    assert phrase == "nhà ống"
    hit, _ = pb.match_sentence("Họ đi chợ.", [{"vi": "hồ", "en": "a pond", "nhom": "phong_canh"}], [])
    assert hit is None
    hit, phrase = pb.match_sentence("Họ ngồi bên hồ.", [{"vi": "hồ", "en": "a pond", "nhom": "phong_canh"}], [])
    assert phrase == "hồ"
    entries = [{"vi": "lịch", "en": "a calendar", "nhom": "lich"}]
    assert pb.match_sentence("Sách lịch sử kể chuyện.", entries, ["lịch sử"])[0] is None
    hit, phrase = pb.match_sentence("Sách lịch sử và một tờ lịch treo tường.", entries, ["lịch sử"])
    assert phrase == "lịch"


def test_khong_doan_khi_lech_tu_dien():
    # 9 giây → 1 ảnh bù, rơi vào câu 2, câu đó không có trong từ điển.
    plan = _plan(["Câu đầu có la bàn.", "Trời hôm nay trong."], [6, 5])
    matched, missed = _build(plan)
    assert matched == []
    assert len(missed) == 1 and missed[0]["sid_chen"] == 2
    assert missed[0]["ly_do"] == "không khớp từ điển"
    assert missed[0]["prompt"] == ""


def test_kenh_that_dung_khoi_rieng():
    fs = pb.load_profile(ROOT / "library/channels/fs.yaml")
    bud = pb.load_profile(ROOT / "library/channels/bud.yaml")
    lich = pb.load_profile(ROOT / "library/channels/_thu_lich_su.yaml")
    assert fs["assets"]["nhom_canh"] and bud["assets"]["phong_cach"] != fs["assets"]["phong_cach"]
    plan = _plan(["Câu đệm trong sân.", "Họ mở la bàn."], [4, 5])
    fs_rows, _ = pb.assemble(plan, "T", 8, fs)
    bud_plan = _plan(["Câu đệm.", "Trong chùa có tượng Phật."], [4, 5])
    bud_rows, _ = pb.assemble(bud_plan, "T", 8, bud)
    lich_plan = _plan(["Câu đệm.", "Thành Cổ Loa giữa đồng lúa."], [4, 5])
    lich_rows, _ = pb.assemble(lich_plan, "T", 8, lich)
    assert fs_rows and "professional" in fs_rows[0]["prompt"] and "compass" in fs_rows[0]["prompt"]
    assert bud_rows and "reverent" in bud_rows[0]["prompt"] and "Buddha" in bud_rows[0]["prompt"]
    assert "plain unadorned wooden pillars and beams, undecorated walls" in bud_rows[0]["prompt"]
    assert lich_rows and "documentary" in lich_rows[0]["prompt"] and "rampart" in lich_rows[0]["prompt"]
    assert "professional" not in bud_rows[0]["prompt"]
    assert "reverent" not in fs_rows[0]["prompt"]
    for row in fs_rows + bud_rows + lich_rows:
        assert pb.van_de(row["prompt"], pb.load_lexicon(fs)[0]) == []
    # Câu không dấu vẫn ra cùng chủ thể của kênh giả lập.
    nodau = _plan(["mot cau dem.", "thanh co loa giua dong."], [4, 5])
    rows, _ = pb.assemble(nodau, "T", 8, lich)
    assert rows and "rampart" in rows[0]["prompt"]


def test_moi_muc_tu_dien_sach():
    for name in ("fs.yaml", "bud.yaml", "_thu_lich_su.yaml"):
        profile = pb.load_profile(ROOT / "library/channels" / name)
        quy, entries, _chan = pb.load_lexicon(profile)
        assert entries, name
        for entry in entries:
            assert pb.van_de(str(entry.get("en") or ""), quy) == [], entry.get("vi")
            prompt = pb.ghep_prompt(profile, entry, "T", 1, quy)
            assert pb.van_de(prompt, quy) == [], (name, entry.get("vi"), pb.van_de(prompt, quy), prompt)


def test_code_khong_nhanh_kenh():
    src = (ROOT / "library/tools/prompt_builder.py").read_text(encoding="utf-8")
    assert not re.search(r"if\s+kenh\s*==", src)
    assert not re.search(r"""==\s*['"]fs['"]""", src)
    assert not re.search(r"""==\s*['"]bud['"]""", src)
    assert "openai" not in src and "anthropic" not in src


def test_cli_khuon_ten_va_prompt(tmp_path):
    texts = [f"Câu {i} mở la bàn." for i in range(1, 5)]
    plan = _plan(texts, [5, 5, 5, 5])
    plan["id"] = "L_thu"
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")
    out = tmp_path / "prompts.txt"
    code = pb.main([
        "--plan", str(path), "--id", "L_thu", "--N", "8",
        "--out", str(out), "--profile", str(ROOT / "library/channels/fs.yaml"),
    ])
    assert code == 0
    lines = [ln for ln in out.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    assert lines and all(" | " in ln for ln in lines)
    assert lines[0].startswith("L_thu_s")
    unmatched = (tmp_path / "unmatched.txt").read_text(encoding="utf-8")
    assert "không khớp" in unmatched or unmatched.startswith("#")


def test_scale_chon_shot():
    fs = pb.load_profile(ROOT / "library/channels/fs.yaml")
    quy = QUY
    vat_nho_entry = {"vi": "la bàn", "en": "a brass compass", "scale": "vat_nho", "khong_gian": "trong_nha"}
    nguoi_entry = {"vi": "con ngựa", "en": "a horse", "scale": "nguoi_vat", "khong_gian": "ngoai_troi"}
    kt_entry = {"vi": "chùa", "en": "a pagoda courtyard", "scale": "kien_truc", "khong_gian": "ngoai_troi"}
    pc_entry = {"vi": "sông", "en": "a river", "scale": "phong_canh", "khong_gian": "ngoai_troi"}

    p_vn = pb.ghep_prompt(fs, vat_nho_entry, "T", 1, quy)
    assert "tabletop" in p_vn or "macro" in p_vn

    p_ng = pb.ghep_prompt(fs, nguoi_entry, "T", 1, quy)
    assert "medium shot eye-level" in p_ng
    assert "tabletop" not in p_ng

    p_kt = pb.ghep_prompt(fs, kt_entry, "T", 1, quy)
    assert "wide architectural" in p_kt

    p_pc = pb.ghep_prompt(fs, pc_entry, "T", 1, quy)
    assert "wide landscape" in p_pc


def test_khong_gian_chon_anh_sang():
    fs = pb.load_profile(ROOT / "library/channels/fs.yaml")
    quy = QUY
    indoor = {"vi": "bàn thờ", "en": "an altar", "scale": "vat_nho", "khong_gian": "trong_nha"}
    outdoor = {"vi": "sông", "en": "a river", "scale": "phong_canh", "khong_gian": "ngoai_troi"}

    p_in = pb.ghep_prompt(fs, indoor, "T", 1, quy)
    assert "warm amber lantern light" in p_in

    p_out = pb.ghep_prompt(fs, outdoor, "T", 1, quy)
    assert "soft natural daylight" in p_out
    assert "amber lantern" not in p_out


def test_vung_ghi_de_van_hoa_va_anh_sang():
    fs = pb.load_profile(ROOT / "library/channels/fs.yaml")
    quy = QUY
    hue_entry = {
        "vi": "sông hương",
        "en": "a river past tiled roofs",
        "scale": "phong_canh",
        "khong_gian": "ngoai_troi",
        "vung": "trung",
    }
    p_hue = pb.ghep_prompt(fs, hue_entry, "T", 1, quy)
    assert "Hue" in p_hue or "central Vietnam" in p_hue
    assert "soft monsoon daylight under an overcast sky" in p_hue
    assert "warm amber" not in p_hue


def test_mau_so_co_luot_thieu_ranh_gioi():
    # Cảnh 20s chỉ có 1 câu -> cần 2 ảnh bù, nhưng 0 ranh giới câu -> thiếu 2 ranh giới
    plan = _plan(["Chỉ một câu dài hai mươi giây."], [20])
    profile = _profile("professional")
    matched, missed = pb.assemble(plan, "T", 8, profile, entries=ENTRIES, chan=[], quy=QUY)
    assert matched == []
    assert len(missed) == 2
    assert all("ranh giới" in m["ly_do"] for m in missed)
    summary1 = pb.tom_tat("T", 8, matched, missed)
    assert summary1["khong_ranh_gioi"] == 2
    assert summary1["can_chen"] == 2
    assert summary1["khop"] == 0
    assert summary1["ty_le"] == 0.0

    # Cảnh 20s gồm 2 câu (10s + 10s) -> cần 2 ảnh bù, chỉ có 1 ranh giới (câu 2 có la bàn khớp)
    plan2 = _plan(["Câu một mở đầu.", "Câu hai có la bàn."], [10, 10])
    matched2, missed2 = pb.assemble(plan2, "T", 8, profile, entries=ENTRIES, chan=[], quy=QUY)
    summary2 = pb.tom_tat("T", 8, matched2, missed2)
    assert summary2["khong_ranh_gioi"] == 1
    assert summary2["khop"] == 1
    assert summary2["can_chen"] == 2
    assert summary2["ty_le"] == 0.5
