"""Bố cục Long v2 (034): v1 giữ nguyên, v2 đạt tỉ lệ và luật chống nhàm, plan ghi tay được giữ."""
import copy
import json
from pathlib import Path

import hyperframes_bridge as HB
import hf_batch_render as HBR

ROOT = Path(__file__).resolve().parent
PLAN_DIR = ROOT.parents[1] / "cl_staging" / "long"
FRAMED = set(HB.LAYOUT_FRAMED)
PREF_CAMS = ("push_in", "pull_out", "dolly_parallax")
OTHER_CAMS = ("pan_left", "pan_right", "tilt_up", "rack_focus")


def _sentences(n: int) -> list[str]:
    out = []
    for i in range(1, n + 1):
        if i in (1, 40, 80, 120):
            out.append(f"**Chương {i}**")
        elif i % 17 == 0:
            out.append("Bà khóc và lặng người.")
        elif i % 19 == 0:
            out.append("Trái lại, vế này khác với vế kia.")
        elif i % 23 == 0:
            out.append("Tấm bia và chân dung hiện vật nằm trên trang sách.")
        else:
            out.append("Câu kể tiếp diễn biến trong ngày ấy.")
    return out


def _media150() -> dict:
    media = {}
    for i in range(1, 151):
        if i % 29 == 0:
            kind = "video"
        elif i % 31 == 0:
            kind = "pdvideo"
        else:
            kind = "image"
        spec = {"kind": kind, "query": f"cảnh {i}"}
        if i == 10:
            spec["layout"] = "pinned"
            spec["cine"] = {"cam": "tilt_up", "intensity": 0.5}
        if i == 50:
            spec["layout"] = "full"
            spec["cine"] = {
                "cam": "pan_left", "depth": False, "fx": [],
                "intensity": 0.42, "transition_in": "cut",
            }
        media[str(i)] = spec
    return media


def _segments(n: int, step: float = 4.0) -> list[dict]:
    return [{"start": i * step, "end": (i + 1) * step} for i in range(n)]


def _assign150(seed: str = "L_fs_v2_150"):
    script = _sentences(150)
    media = _media150()
    snapshot = copy.deepcopy(media)
    segments = _segments(150)
    visuals = {"6": {"type": "map", "until": 8}, "70": {"type": "compare", "until": 72}}
    chosen = HB.assign_layouts_v2(
        media, seed, script=script, visuals=visuals, segments=segments,
        series="fs", scene_decision={"19": {"scene": {"picked": {"type": "compare"}}}},
    )
    return chosen, media, snapshot, script, segments, visuals


def test_v1_khong_policy_trung_auto_layouts():
    media = {str(k): {"kind": "image", "query": "x"} for k in range(1, 25)}
    auto, cines = HB._resolve_render_layouts(
        media, "L_fs_04", "studio_long", {}, Path("x"), Path("x"), {}, "fs")
    assert cines == {}
    assert auto == HB.auto_layouts(media, "L_fs_04")
    assert auto == HB.auto_layouts(media, "L_fs_04")


def test_v1_plan_that_khop_auto_layouts():
    files = sorted(PLAN_DIR.glob("plan_*.json"))
    if not files:
        return
    checked = 0
    for path in files:
        if checked >= 4:
            break
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rows = data if isinstance(data, list) else [data]
        used = False
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("media"), dict) or not row["media"]:
                continue
            if row.get("layout_policy") == "v2":
                continue
            media = row["media"]
            if any(not str(k).isdigit() for k in media):
                continue
            seed = str(row.get("id") or path.stem)
            style = row.get("style") if row.get("style") in HB.LONG_STYLES else "studio_long"
            auto, cines = HB._resolve_render_layouts(
                media, seed, style, {}, Path("x"), Path("x"), {}, row.get("series") or "fs")
            assert cines == {}
            assert auto == HB.auto_layouts(media, seed)
            used = True
        if used:
            checked += 1
    assert checked >= 1


def test_v2_ti_le_mo_dau_chong_nham_va_tat_dinh():
    chosen, media, snapshot, script, segments, visuals = _assign150()
    again, _, _, _, _, _ = _assign150()
    assert chosen == again
    assert media == snapshot

    problems = HB.layout_v2_problems(
        chosen, script=script, visuals=visuals, segments=segments)
    assert problems == [], (problems, HB.layout_report(chosen))

    auto = [c for c in chosen.values() if c.get("image") and c.get("auto")]
    n = len(auto)
    assert 130 <= n <= 160
    full = sum(c.get("layout") == "full" for c in auto) / n
    depth = sum(c.get("layout") == "depth" for c in auto) / n
    framed = sum(c.get("layout") in FRAMED for c in auto) / n
    assert 0.48 <= full <= 0.72
    assert 0.03 <= depth <= 0.17
    assert 0.18 <= framed <= 0.42

    for sid, c in chosen.items():
        if not (c.get("image") and c.get("auto")):
            continue
        spec = media[str(sid)]
        assert "pan" not in spec
        if c["t"] < 120:
            assert c["layout"] in ("full", "depth")
        if c["layout"] == "full":
            cine = c["cine"]
            assert isinstance(cine, dict) and cine["cam"] in HB.CINE_CAMS
            assert cine["depth"] is False
            assert 0.40 <= cine["intensity"] <= 0.60
            assert set(cine["fx"]) <= {"dust", "mist_drift", "candle_flicker"}
            assert len(cine["fx"]) <= 1
        else:
            assert c["cine"] is None

    cams = [c["cine"]["cam"] for c in auto if c.get("layout") == "full"]
    pref = sum(cam in PREF_CAMS for cam in cams)
    rest = sum(cam in OTHER_CAMS for cam in cams)
    assert pref > rest and pref > 0 and rest > 0

    ordered = [chosen[sid] for sid in sorted(chosen)]
    prev_cam = ""
    prev_framed = False
    run: list[str] = []
    recent: list[str] = []
    for c in ordered:
        cam = (c.get("cine") or {}).get("cam") if isinstance(c.get("cine"), dict) else ""
        if cam:
            assert cam != prev_cam
        prev_cam = cam or ""
        layout = c.get("layout") or ""
        is_framed = layout in FRAMED
        if layout and is_framed:
            assert not prev_framed
        if layout:
            prev_framed = is_framed
        recent.append(layout if is_framed else "")
        window = [x for x in recent[-6:] if x]
        assert len(window) == len(set(window))
        if not c.get("image"):
            continue
        if layout == "full" and cam:
            run.append(cam)
            assert not (len(run) > 3 and len(set(run[-4:])) == 1)
        else:
            run = []

    assert chosen[10]["layout"] == "pinned"
    assert chosen[10]["cine"]["cam"] == "tilt_up"
    assert chosen[10]["auto"] is False
    assert chosen[50]["layout"] == "full"
    assert chosen[50]["cine"]["cam"] == "pan_left"
    assert chosen[50]["cine"]["intensity"] == 0.42
    assert chosen[50]["auto"] is False

    for sid, c in chosen.items():
        spec = media[str(sid)]
        if spec["kind"] in ("video", "pdvideo"):
            assert c["image"] is False and c["cine"] is None
            assert c["layout"] in ("full", "card3d", "frame")

    report = HB.layout_report(chosen)
    assert report.startswith("bố cục:") and "cam:" in report
    assert "full" in report and "depth" in report and "khung" in report


def test_ngu_canh_uu_tien_full_push_va_split():
    script = ["Bà khóc."] * 40
    media = {str(i): {"kind": "image", "query": "cảnh"} for i in range(1, 41)}
    segments = _segments(40, step=4.0)
    # Toàn bộ sau giây 120 để khung được phép, rồi so với plan trung tính cùng hạt.
    segments = [{"start": 130 + i * 4.0, "end": 134 + i * 4.0} for i in range(40)]
    emo = HB.assign_layouts_v2(media, "ctx", script=script, segments=segments, series="bud")
    neutral_script = ["Câu kể tiếp."] * 40
    neu = HB.assign_layouts_v2(media, "ctx", script=neutral_script, segments=segments, series="bud")
    emo_full = [c for c in emo.values() if c["auto"] and c["layout"] == "full" and c.get("cine")]
    neu_full = [c for c in neu.values() if c["auto"] and c["layout"] == "full" and c.get("cine")]
    emo_push = sum(c["cine"]["cam"] == "push_in" for c in emo_full) / len(emo_full)
    neu_push = sum(c["cine"]["cam"] == "push_in" for c in neu_full) / len(neu_full)
    assert emo_push > neu_push

    compare_script = ["Trái lại, vế này khác với vế kia."] * 40
    cmp_ = HB.assign_layouts_v2(media, "ctx", script=compare_script, segments=segments, series="fs")
    cmp_split = sum(c["layout"] in ("split", "split_r") for c in cmp_.values() if c["image"])
    neu_split = sum(c["layout"] in ("split", "split_r") for c in neu.values() if c["image"])
    assert cmp_split > neu_split

    assert HB._layout_context({"kind": "commons"}, "Câu thường.", None) == "archive"
    assert HB._layout_context(
        {"kind": "image"}, "Câu thường.",
        {"scene": {"picked": {"type": "compare"}}}) == "compare"


def test_clip_mo_dau_khong_khung_va_khong_cine():
    media = {str(i): {"kind": "video", "query": "c"} for i in range(1, 9)}
    media["3"] = {"query": "thiếu kind"}
    segments = _segments(8, step=10.0)
    chosen = HB.assign_layouts_v2(media, "clip", script=["Câu."] * 8, segments=segments, series="fs")
    for c in chosen.values():
        assert c["cine"] is None
        if c["t"] < 120:
            assert c["layout"] == "full"


def test_plan_moi_gan_v2_plan_cu_giu_nguyen():
    fresh = {
        "id": "L_fs_layout_v2", "lane": "long", "series": "fs", "style": "studio_long",
        "script": ["Một câu."],
        "tts": {"voice": "Thái Sơn", "style": "doc_truyen", "tempo": 0.96},
        "sound": {"reverb": 0.0},
    }
    assert HBR.wire_plan_row(fresh, legacy=False)["layout_policy"] == "v2"
    keep = dict(fresh, id="L_fs_keep_v1", layout_policy="v1")
    assert HBR.wire_plan_row(keep, legacy=False)["layout_policy"] == "v1"
    old = {
        "id": "L_bud_old", "lane": "long", "style": "inkwash_long", "series": "bud",
        "script": ["Lời."],
        "tts": {"voice": "Binh", "engine": "standard", "tempo": 0.91},
        "sound": {"reverb": 0.045},
    }
    assert "layout_policy" not in HBR.wire_plan_row(old)
    legacy = {
        "id": "L_legacy", "lane": "long", "series": "fs", "style": "studio_long",
        "legacy": True, "script": ["Một câu."],
        "tts": {"voice": "Thái Sơn"}, "sound": {},
    }
    assert "layout_policy" not in HBR.wire_plan_row(legacy)
    plain = {"id": "short", "series": "bud", "script": ["Câu."]}
    assert "layout_policy" not in HBR.wire_plan_row(plain, legacy=False)


def test_canh_bao_long_moi_thieu_v2(tmp_path, capsys):
    row = {"id": "L_new", "lane": "long"}
    HBR.warn_missing_layout_policy(row, tmp_path)
    assert "CẢNH BÁO layout_policy" in capsys.readouterr().out
    (tmp_path / "L_new.mp4").write_bytes(b"not-a-real-video")
    HBR.warn_missing_layout_policy(row, tmp_path)
    assert capsys.readouterr().out == ""
    (tmp_path / "L_new.mp4").unlink()
    HBR.warn_missing_layout_policy({"id": "L_new", "lane": "long", "layout_policy": "v2"}, tmp_path)
    assert capsys.readouterr().out == ""
    HBR.warn_missing_layout_policy({"id": "S", "lane": "niem"}, tmp_path)
    assert capsys.readouterr().out == ""


def test_layout_v2_opts_remap_chuong_va_seed():
    chosen = {
        4: {"layout": "full", "cine": {"cam": "push_in"}},
        5: {"layout": "depth", "cine": None},
        9: {"layout": "frame", "cine": None},
    }
    opts = HBR.layout_v2_opts({"video_only": True}, {"id": "L_film"}, chosen, shift=3, lo=3, hi=5)
    assert opts["layout_seed"] == "L_film"
    assert opts["layout_policy"] == "v2"
    assert set(opts["layout_v2"]) == {"1", "2"}
    assert opts["layout_v2"]["1"]["layout"] == "full"
    assert opts["layout_v2"]["1"]["cine"]["cam"] == "push_in"
    assert opts["layout_v2"]["2"]["cine"] is None
    assert HBR.layout_v2_choices({"id": "x", "media": {}}) is None
    empty = HBR.layout_v2_choices({"id": "x", "layout_policy": "v2", "media": {}, "script": []})
    assert empty == {}
    assert HB.layout_report(empty) == "bố cục: 0 ảnh; full 0% (cine 0%), depth 0%, khung 0%; cam: —"


def test_chapter_key_khong_doi_khi_thieu_layout_sig():
    row = {"script": ["**A**", "x", "y"], "style": "inkwash_long", "media": {}, "visuals": {}}
    assert HBR.chapter_key(row, 0, 2, 0.0, 4.0, "looks") == HBR.chapter_key(
        row, 0, 2, 0.0, 4.0, "looks", layout_sig=None)
    assert HBR.chapter_key(row, 0, 2, 0.0, 4.0, "looks", layout_sig="") == HBR.chapter_key(
        row, 0, 2, 0.0, 4.0, "looks")
    signed = HBR.chapter_key(row, 0, 2, 0.0, 4.0, "looks", layout_sig='{"1": "full"}')
    assert signed != HBR.chapter_key(row, 0, 2, 0.0, 4.0, "looks")


def test_preset_v2_khong_goi_lai_auto_layouts_deu():
    media = {str(k): {"kind": "image", "query": "x"} for k in range(1, 5)}
    preset = {"1": {"layout": "depth", "cine": None}, "2": {"layout": "full", "cine": {"cam": "push_in", "depth": False, "fx": [], "intensity": 0.5, "transition_in": "cut"}}}
    auto, cines = HB._resolve_render_layouts(
        media, "seed", "laban_long", {"layout_v2": preset, "layout_policy": "v2"},
        Path("x"), Path("x"), {}, "fs")
    assert auto[1] == "depth" and auto[2] == "full"
    assert 3 not in auto and cines[2]["cam"] == "push_in"
    assert auto != HB.auto_layouts(media, "seed")


def test_plan_cu_co_giong_d_khong_gan_v2():
    """P1–P3 đã có temperature/text_mode nhưng thiếu layout_policy: không đóng dấu v2."""
    old = {
        "id": "L_bud_P3_ananda", "lane": "long", "style": "studio_long", "series": "bud",
        "script": ["Lời."],
        "tts": {"voice": "Binh", "engine": "standard", "tempo": 0.91,
                "temperature": 0.7, "text_mode": "speech"},
        "sound": {"reverb": 0.045},
    }
    wired = HBR.wire_plan_row(old)
    assert "layout_policy" not in wired
    forced = HBR.wire_plan_row(dict(old), force=True)
    assert "layout_policy" not in forced
    assert HBR.layout_v2_choices(wired) is None


def test_plan_cu_thieu_policy_render_ra_v1():
    """Đường render thật (layout_v2_choices + _resolve_render_layouts) giữ auto_layouts v1."""
    media = {str(k): {"kind": "image", "query": "x"} for k in range(1, 9)}
    row = {
        "id": "L_bud_old_render", "lane": "long", "style": "inkwash_long", "series": "bud",
        "script": ["Câu."] * 8, "media": media,
        "tts": {"voice": "Binh", "engine": "standard", "tempo": 0.91,
                "temperature": 0.7, "text_mode": "speech"},
        "sound": {"reverb": 0.045},
    }
    wired = HBR.wire_plan_row(row)
    assert "layout_policy" not in wired
    assert HBR.layout_v2_choices(wired) is None
    auto, cines = HB._resolve_render_layouts(
        media, row["id"], row["style"], {}, Path("x"), Path("x"), {}, "bud")
    assert cines == {}
    assert auto == HB.auto_layouts(media, row["id"])


def test_ghi_tay_cine_van_chon_layout():
    media = {str(i): {"kind": "image", "query": "c"} for i in range(1, 21)}
    media["5"] = {"kind": "image", "query": "c", "cine": {"cam": "push_in", "intensity": 0.5}}
    media["4"] = {"kind": "image", "query": "c", "layout": "full"}
    media["6"] = {"kind": "image", "query": "c", "layout": "full"}
    segments = [{"start": 130 + i * 4.0, "end": 134 + i * 4.0} for i in range(20)]
    chosen = HB.assign_layouts_v2(
        media, "handcine", script=["Câu kể."] * 20, segments=segments, series="fs")
    assert chosen[5]["cine"]["cam"] == "push_in"
    assert chosen[5]["layout"]
    assert chosen[5]["layout"] in ("full", "depth", *HB.LAYOUT_FRAMED)
    assert chosen[5]["auto"] is True


def test_clip_khung_vao_cua_so_6():
    media = {str(i): {"kind": "image", "query": "c"} for i in range(1, 16)}
    media["7"] = {"kind": "video", "query": "c", "layout": "card3d"}
    media["6"] = {"kind": "image", "query": "c", "layout": "full"}
    media["8"] = {"kind": "image", "query": "c", "layout": "full"}
    segments = [{"start": 130 + i * 4.0, "end": 134 + i * 4.0} for i in range(15)]
    chosen = HB.assign_layouts_v2(
        media, "clipframe", script=["Câu kể."] * 15, segments=segments, series="fs")
    assert chosen[7]["layout"] == "card3d"
    assert chosen[7]["image"] is False
    recent = []
    for sid in sorted(chosen):
        layout = chosen[sid].get("layout") or ""
        recent.append(layout if layout in FRAMED else "")
        window = [x for x in recent[-6:] if x]
        assert len(window) == len(set(window)), (sid, window)
        prev = chosen[sid - 1].get("layout") if sid - 1 in chosen else ""
        if layout in FRAMED and prev in FRAMED:
            raise AssertionError(f"hai khung liền: {sid - 1}={prev} {sid}={layout}")


def test_anh_doc_vao_nhom_khung():
    media = {str(i): {"kind": "image", "query": "c", "w": 1920, "h": 1080} for i in range(1, 21)}
    media["10"] = {"kind": "image", "query": "chân dung", "w": 800, "h": 1600}
    media["9"] = {"kind": "image", "query": "c", "layout": "full", "w": 1920, "h": 1080}
    media["11"] = {"kind": "image", "query": "c", "layout": "full", "w": 1920, "h": 1080}
    segments = [{"start": 130 + i * 4.0, "end": 134 + i * 4.0} for i in range(20)]
    chosen = HB.assign_layouts_v2(
        media, "tall", script=["Câu kể."] * 20, segments=segments, series="fs")
    assert chosen[10]["layout"] in FRAMED
    assert chosen[10]["layout"] != "full"
    assert chosen[10]["cine"] is None
    assert HB._spec_portrait(media["10"]) is True
    assert HB._spec_portrait(media["1"]) is False


def test_pan_zoom_resolution_check_goi_khi_gan_va_luc_render(monkeypatch):
    called = []
    real = HB.pan_zoom_resolution_check

    def wrap(*a, **k):
        called.append(True)
        return real(*a, **k)

    monkeypatch.setattr(HB, "pan_zoom_resolution_check", wrap)
    pan = {"stops": [{"line": 1, "x": 0.0, "zoom": 1.0}, {"line": 2, "x": 1.0, "zoom": 1.2}]}
    media = {"1": {"kind": "image", "query": "c", "pan": pan, "w": 3840, "h": 1080}}
    HB.assign_layouts_v2(media, "pz", script=["Câu."], segments=[{"start": 0.0, "end": 4.0}])
    assert called, "assign_layouts_v2 phải gọi pan_zoom_resolution_check"
    import inspect
    src = inspect.getsource(HB.render)
    assert "pan_zoom_resolution_check(" in src
    assert "motion_layout(" in src


def test_layout_report_lay_media_khi_thieu_image():
    media = {
        "1": {"kind": "image", "query": "a"},
        "2": {"kind": "video", "query": "b"},
        "3": {"kind": "local", "query": "c"},
    }
    payload = {
        1: {"layout": "full", "cine": {"cam": "push_in"}},
        2: {"layout": "card3d", "cine": None},
        3: {"layout": "pinned", "cine": None},
    }
    line = HB.layout_report(payload, media)
    assert "2 ảnh" in line
    assert line.startswith("bố cục: 2 ảnh")
    empty = HB.layout_report(payload, {})
    assert empty.startswith("bố cục: 0 ảnh")


def test_cua_so_chong_120s_dau_khong_bao_oan():
    n = 32
    segments = [{"start": i * 4.0, "end": (i + 1) * 4.0} for i in range(n)]
    script = ["Câu kể tiếp."] * n
    media = {str(i): {"kind": "image", "query": "c"} for i in range(1, n + 1)}
    chosen = HB.assign_layouts_v2(media, "overlap30", script=script, segments=segments, series="fs")
    problems = HB.layout_v2_problems(chosen, script=script, segments=segments)
    assert not any("cửa sổ" in p for p in problems), problems

    chosen2 = {}
    segs2 = [{"start": 130.0 + i * 4.0, "end": 134.0 + i * 4.0} for i in range(50)]
    script2 = ["Câu."] * 50
    for i in range(1, 51):
        chosen2[i] = {"layout": "full", "cine": None, "auto": True,
                      "t": 130.0 + (i - 1) * 4.0, "image": True}
    problems2 = HB.layout_v2_problems(chosen2, script=script2, segments=segs2)
    assert any("thiếu 3 loại cảnh" in p for p in problems2), problems2


def test_dry_run_p3_ananda_sao_bo_layout():
    path = PLAN_DIR / "plan_P3_ananda.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    row = copy.deepcopy(data[0] if isinstance(data, list) else data)
    media = row.get("media") or {}
    for spec in media.values():
        if isinstance(spec, dict):
            spec.pop("layout", None)
            spec.pop("cine", None)
    chosen = HB.assign_layouts_v2(
        media, row.get("id") or "P3", script=row.get("script") or [],
        visuals=row.get("visuals") or {}, series=row.get("series"))
    report = HB.layout_report(chosen, media)
    payload = {sid: {"layout": c.get("layout"), "cine": c.get("cine")} for sid, c in chosen.items()}
    report_preset = HB.layout_report(payload, media)
    assert "0 ảnh" not in report
    assert report == report_preset
    problems = HB.layout_v2_problems(
        chosen, script=row.get("script") or [], visuals=row.get("visuals") or {})
    assert isinstance(report, str) and report.startswith("bố cục:")
    # problems có thể khác [] nếu plan thật lệch tỉ lệ; chỉ cần report đếm ảnh.
    assert sum(1 for c in chosen.values() if c.get("image")) >= 50
    print("P3_DRY", report)
    print("P3_PROBLEMS", problems)
