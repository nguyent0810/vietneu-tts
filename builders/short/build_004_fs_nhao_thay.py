"""Build-only adapter for FS 004 compositions; reads timing artifacts, never TTS."""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

from shortbuild import month_sheet_html, validate, yeartable_html


def font_css_from_faces(faces_path: Path) -> str:
    faces = json.loads(Path(faces_path).read_text(encoding="utf-8"))
    out = []
    for face in faces:
        family, css = face.get("family"), face.get("css", "")
        if family == "Be Vietnam Pro" and re.search(r"font-weight:\s*(600|700|800|900)", css):
            out.append(css.replace("url('fonts/", "url('../studio/fonts/"))
        elif family == "JetBrains Mono" and "font-weight: 500" in css:
            out.append(css.replace("url('fonts/", "url('../studio/fonts/"))
    return "\n".join(out)


def _modules(modules_dir: Path, tools_dir: Path):
    for path in (str(Path(tools_dir)), str(Path(modules_dir))):
        if path not in sys.path:
            sys.path.insert(0, path)
    import canchi
    from fs_calendar import hoangdao_daily
    import saohan
    import tuvi_year
    return canchi, hoangdao_daily, saohan, tuvi_year


def source_rows(items, *, modules_dir: Path, tools_dir: Path):
    """Rebuild the FS year rows using the legacy calendar modules."""
    canchi, _, saohan, tuvi_year = _modules(modules_dir, tools_dir)
    years = range(1950, 2011)
    p27 = {y: tuvi_year.profile(y, start=2027, n_years=1) for y in years}
    p28 = {y: tuvi_year.profile(y, start=2028, n_years=1) for y in years}
    r27 = {y: p27[y]["cac_nam"][0] for y in years}
    r28 = {y: p28[y]["cac_nam"][0] for y in years}
    for item in items:
        rid = item["id"]
        if rid == "fs_nh_1109":
            item["rows"] = [(label, "HẠN THIÊN TINH", [y for y in years
                if saohan.han(y, label == "NAM MẠNG", at=2027) == "Thiên Tinh"])
                for label in ("NAM MẠNG", "NỮ MẠNG")]
        elif rid == "fs_nh_1110":
            tags = (("Kim Lâu Thân", "KIM LÂU THÂN", "KỴ BẢN THÂN"),
                    ("Kim Lâu Thê", "KIM LÂU THÊ", "KỴ BẠN ĐỜI"),
                    ("Kim Lâu Tử", "KIM LÂU TỬ", "KỴ CON CÁI"),
                    ("Kim Lâu Lục Súc", "KIM LÂU LỤC SÚC", "KỴ GIA SÚC"))
            item["rows"] = [(label, tag, [y for y in years if r28[y]["kim_lau"] == module_label])
                            for module_label, label, tag in tags]
        elif rid == "fs_nh_1111":
            item["rows"] = []
            for label, sex, term in (("NAM MẠNG", True, "Thiên La"), ("NỮ MẠNG", False, "Thiên La"),
                                     ("NAM VÀ NỮ", True, "Địa Võng")):
                ys = [y for y in years if (saohan.han(y, sex, at=2027) == term if term == "Thiên La"
                      else saohan.han(y, True, at=2027) == term and saohan.han(y, False, at=2027) == term)]
                item["rows"].append((label, f"HẠN {term.upper()}", ys))
        elif rid == "fs_nh_1112":
            item["rows"] = [(p27[y]["can_chi"].upper(), f"{r27[y]['tuoi']} TUỔI", [y]) for y in years
                if not r27[y]["kim_lau"] and not r27[y]["hoang_oc_xau"] and not r27[y]["tam_tai"]
                and r27[y]["quan_he_chi"] in ("bình thường", "lục hợp", "tam hợp")]
        elif rid == "fs_nh_1113":
            item["rows"] = [(label, "SAO THỦY DIỆU", [y for y in years
                if saohan.sao(y, label == "NAM MẠNG", at=2027) == "Thủy Diệu"])
                for label in ("NAM MẠNG", "NỮ MẠNG")]
        elif rid == "fs_nh_1114":
            canchi_2028 = " ".join(canchi.can_chi(2028))
            item["chip"] = f"TAM TAI 2028 · {canchi_2028.upper()}"
            item["script"][0] = f"Năm 2028 {canchi_2028}, tuổi Dần, Ngọ, Tuất bước vào năm đầu của hạn Tam Tai."
            item["rows"] = [(f"TUỔI {chi.upper()}", "NĂM ĐẦU TAM TAI", [y for y in years
                if p28[y]["chi"] == chi and r28[y]["tam_tai"]]) for chi in ("Dần", "Ngọ", "Tuất")]


def source_month_days(*, modules_dir: Path, tools_dir: Path):
    """Calculate January 2027's calendar cells with hoangdao_daily."""
    _, hoangdao_daily, _, _ = _modules(modules_dir, tools_dir)
    days = []
    for day in range(1, 32):
        data = hoangdao_daily.day_data(dt.date(2027, 1, day))
        lunar = data["ld"]
        bad = lunar in (3, 7, 13, 18, 22, 27) or lunar in (5, 14, 23)
        is_hoang = data["is_hoang"]
        kind = "gold-good" if is_hoang and not bad else "gold-tn" if is_hoang else "red-bad" if bad else "neutral-cell"
        days.append({"solar_day": day, "lunar_str": f"{lunar}/{data['lm']}", "cell_type": kind})
    return days


def load_golden_inputs(items, *, render_dir: Path):
    """Read real timing and display strings from saved render/TTS artifacts."""
    render_dir = Path(render_dir)
    for item in items:
        rid = item["id"]
        render_meta = json.loads((render_dir / f"{rid}.render.json").read_text(encoding="utf-8"))
        if render_meta.get("id") != rid or not render_meta.get("ok"):
            raise ValueError(f"{rid}: render manifest missing/mismatched or not successful")
        tts = json.loads((render_dir / f"{rid}.json").read_text(encoding="utf-8"))
        (render_dir / f"{rid}.srt").read_text(encoding="utf-8")
        (render_dir / f"{rid}.txt").read_text(encoding="utf-8")
        raw = tts["segments"]
        display = item.get("display_script") or item["script"]
        item["segs"] = [{"start": seg["start"], "end": seg["end"],
                         "text": display[i] if i < len(display) else seg["text"]}
                        for i, seg in enumerate(raw)]
        base_duration = 14.0 if item.get("style") == "month_sheet" else 11.5
        item["dur"] = round(max(base_duration, raw[-1]["end"] + 4.2, 11.5), 2)


def build(items, *, compositions_dir: Path, template_path: Path, font_css: str,
          month_days=None, month_offset=0, month_label="THÁNG 1/2027",
          total_days=0, good_days=0):
    compositions_dir = Path(compositions_dir)
    compositions_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for item in items:
        style = item.get("style", "yeartable")
        segs = item.get("segs", [])
        if style == "month_sheet":
            html = month_sheet_html(item, item["dur"], segs, fonts=font_css,
                                    days=month_days or [], offset=month_offset,
                                    month_label=month_label, total_days=total_days,
                                    good_days=good_days)
        else:
            html = yeartable_html(item, item["dur"], segs,
                                  template_path=Path(template_path), fonts=font_css)
        validate([item], html)
        path = compositions_dir / f"_tb_{item['id']}.html"
        path.write_text(html, encoding="utf-8")
        outputs.append(path)
    return outputs


def build_from_artifacts(*, plan_path: Path, render_dir: Path,
                         modules_dir: Path, tools_dir: Path, faces_path: Path,
                         compositions_dir: Path, template_path: Path):
    items = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    source_rows(items, modules_dir=modules_dir, tools_dir=tools_dir)
    load_golden_inputs(items, render_dir=render_dir)
    days = source_month_days(modules_dir=modules_dir, tools_dir=tools_dir)
    total = sum(day["cell_type"] in ("gold-good", "gold-tn") for day in days)
    good = sum(day["cell_type"] == "gold-good" for day in days)
    return build(items, compositions_dir=compositions_dir, template_path=template_path,
                 font_css=font_css_from_faces(faces_path), month_days=days,
                 month_offset=dt.date(2027, 1, 1).weekday(), total_days=total, good_days=good)
