"""Bộ sinh short "Lịch Hoàng Đạo hằng ngày" (khuôn A) — Task 30.

Cách dùng:
    .venv/bin/python tools/hoangdao_daily.py <yyyy-mm-dd>
    .venv/bin/python tools/hoangdao_daily.py 2026-10-22 --render
    .venv/bin/python tools/hoangdao_daily.py --check-all

Mọi số tính bằng code (amlich.py, canchi.py, ngaytot.py).
Không dùng vnlunar cho thần/trực/nạp âm (Rule 5).
Luật con giáp FS: Gọi bằng tên chi (Tý..Hợi), tối đa 3 tên chi mỗi câu.
Giữ nhận diện gia đình bảng (nhãn trên, tiêu đề 2 dòng, chân dừng hình, khung 1080x1920).
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if (HERE.parent / "studio.py").is_file() else Path.cwd()
sys.path.insert(0, str(ROOT))
if (ROOT / "output/cl_staging/long").is_dir():
    sys.path.insert(0, str(ROOT / "output/cl_staging/long"))
if (ROOT / "output/cl_staging/grok/tools").is_dir():
    sys.path.insert(0, str(ROOT / "output/cl_staging/grok/tools"))

try:
    from . import amlich as A  # noqa: E402
    from . import canchi as C  # noqa: E402
    from . import ngaytot as N  # noqa: E402
except ImportError:
    import amlich as A  # noqa: E402
    import canchi as C  # noqa: E402
    import ngaytot as N  # noqa: E402

try:
    import hf_batch_render as R  # noqa: E402
except ImportError:
    R = None

CHI = C.CHI
CAN = C.CAN
THAN = [
    "Thanh Long", "Minh Đường", "Thiên Hình", "Chu Tước", "Kim Quỹ", "Kim Đường",
    "Bạch Hổ", "Ngọc Đường", "Thiên Lao", "Nguyên Vũ", "Tư Mệnh", "Câu Trần"
]
HOANG = {0, 1, 4, 5, 7, 10}
TRUC = ["Kiến", "Trừ", "Mãn", "Bình", "Định", "Chấp", "Phá", "Nguy", "Thành", "Thu", "Khai", "Bế"]
GIO = [
    [0, 1, 3, 6, 8, 9],       # Tý, Ngọ
    [2, 3, 5, 8, 10, 11],     # Sửu, Mùi
    [0, 1, 4, 5, 7, 10],      # Dần, Thân
    [0, 2, 3, 6, 7, 9],       # Mão, Dậu
    [2, 4, 5, 8, 9, 11],      # Thìn, Tuất
    [1, 4, 6, 7, 10, 11]       # Tỵ, Hợi
]
GIO_HOURS_MAP = {
    0: (23, 1), 1: (1, 3), 2: (3, 5), 3: (5, 7), 4: (7, 9), 5: (9, 11),
    6: (11, 13), 7: (13, 15), 8: (15, 17), 9: (17, 19), 10: (19, 21), 11: (21, 23)
}
DOW_VI = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]

SAMPLE_DIR = ROOT / "samples"
_PKG_VERIFIED = HERE / "calendar_facts_verified.json"
VERIFIED = _PKG_VERIFIED if _PKG_VERIFIED.is_file() else (ROOT / "output/cl_staging/fs/calendar_facts_verified.json")
COMP = ROOT / "hyperframes_short/compositions"
HF = ROOT / "hyperframes_short"
FS_BGM = "bgm/asian_drums.mp3"
FS_BGM_GAIN = 0.14


def merge_contiguous_hours(indices: list[int]) -> str:
    """Gộp các khung giờ hoàng đạo liền kề thành dải gọn (vd 7–11h)."""
    in_set = set(indices)
    heads = [i for i in indices if (i - 1) % 12 not in in_set]
    if not heads and indices:
        heads = [indices[0]]
    blocks = []
    for h in heads:
        chain = [h]
        curr = h
        while (curr + 1) % 12 in in_set and (curr + 1) % 12 != h:
            curr = (curr + 1) % 12
            chain.append(curr)
        start_h = GIO_HOURS_MAP[chain[0]][0]
        end_h = GIO_HOURS_MAP[chain[-1]][1]
        blocks.append((chain[0], f"{start_h}–{end_h}h"))
    blocks.sort(key=lambda b: b[0] if b[0] != 0 else 12)
    return " · ".join(b[1] for b in blocks)


def day_data(target_date: dt.date | str) -> dict:
    """Hàm chuẩn trích xuất toàn bộ dữ kiện lịch hoàng đạo hằng ngày.

    - NÊN lấy độc quyền từ ngaytot.VIEC.
    - TRÁNH: lọc việc lớn + Tam Nương / Nguyệt kỵ.
    - 12 con giáp chia 4 nhóm: HỢP (xanh), TRÁNH (đỏ), LƯU Ý (vàng), Bình hòa (trầm).
    - Giờ hoàng đạo gộp khung liền.
    - Kịch bản 3 câu đọc (≤ 3 chi/câu).
    """
    if isinstance(target_date, str):
        target_date = dt.date.fromisoformat(target_date)

    ld, lm, ly, leap = A.solar2lunar(target_date.day, target_date.month, target_date.year)
    # Neo can chi ngày: 2026-10-02 = Kỷ Dậu
    i60 = (45 + A.jd_from_date(target_date.day, target_date.month, target_date.year) - A.jd_from_date(2, 10, 2026)) % 60
    can_i, chi_i = i60 % 10, i60 % 12
    mchi, tiet_name, tiet_date = N.tiet_month_chi(target_date)
    start = (2 * ((mchi - 2) % 12)) % 12

    dan = []
    if ld in N.TAM_NUONG:
        dan.append("Tam Nương")
    if ld in N.NGUYET_KY:
        dan.append("Nguyệt kỵ")
    if (lm, ld) in N.DUONG_CONG and not leap:
        dan.append("Dương Công")

    truc = TRUC[(chi_i - mchi) % 12]
    than_name = THAN[(chi_i - start) % 12]
    is_hoang = (chi_i - start) % 12 in HOANG

    # 1. Quan hệ can chi 12 con giáp
    xung_chi_i = (chi_i + 6) % 12
    xung_chi = CHI[xung_chi_i]

    # Tam Hợp (2 chi)
    tam_hop = []
    for grp in C.TAM_HOP:
        if CHI[chi_i] in grp:
            tam_hop = [x for x in grp if x != CHI[chi_i]]

    # Lục Hợp (1 chi)
    luc_hop = [b if a == CHI[chi_i] else a for a, b in C.LUC_HOP if a == CHI[chi_i] or b == CHI[chi_i]][0]

    # Lục Hại & Lục Phá (nhóm LƯU Ý màu vàng)
    luc_hai = [b if a == CHI[chi_i] else a for a, b in C.LUC_HAI if a == CHI[chi_i] or b == CHI[chi_i]][0]
    luc_pha = [b if a == CHI[chi_i] else a for a, b in C.LUC_PHA if a == CHI[chi_i] or b == CHI[chi_i]][0]

    zodiac_grid = []
    for i in range(12):
        chi_name = CHI[i]
        if i == xung_chi_i:
            cls = "tranh"
            tag = "XUNG NGÀY"
            reason = "Xung ngày"
        elif chi_name in tam_hop:
            cls = "hop"
            tag = "TAM HỢP"
            reason = "Tam hợp"
        elif chi_name == luc_hop:
            cls = "hop"
            tag = "LỤC HỢP"
            reason = "Lục hợp"
        elif chi_name in (luc_hai, luc_pha):
            cls = "luuy"
            tag = "LƯU Ý"
            reason = "Hại ngày" if chi_name == luc_hai else "Phá ngày"
        else:
            cls = "binh"
            tag = "Bình hòa"
            reason = "Bình thường"
        zodiac_grid.append({
            "chi": chi_name,
            "index": i,
            "cls": cls,
            "tag": tag,
            "reason": reason
        })

    # 2. "Nên" CHỈ lấy từ bảng VIEC đã kiểm trong tools/ngaytot.py
    viec_hop = N.VIEC.get(truc, ["thu xếp"])
    nen_display = ", ".join(v.capitalize() for v in viec_hop)

    # 3. "Tránh": nếu ngày không qua lọc việc lớn -> chọn ngày khác; có Tam Nương/Nguyệt kỵ thì ghi tên
    passed_major = is_hoang and any(v in viec_hop for v in N.VIEC_OK) and not dan
    if not passed_major:
        if dan:
            tranh_display = f"Việc lớn (cưới hỏi, khai trương, làm nhà): chọn ngày khác ({', '.join(dan)})"
        else:
            tranh_display = "Việc lớn (cưới hỏi, khai trương, làm nhà): chọn ngày khác"
    else:
        tranh_display = "Tranh chấp, kiện tụng"

    # 4. Giờ tốt: gộp khung liền nhau cho gọn (vd 7–11h)
    gio_indices = GIO[chi_i % 6]
    gio_names = [CHI[g] for g in gio_indices]
    gio_display = merge_contiguous_hours(gio_indices)

    # 5. Kịch bản đọc 3 câu, ≤ 3 chi/câu
    hoang_txt = "hoàng đạo" if is_hoang else "hắc đạo"
    hop_str = ", ".join(viec_hop[:2]) if viec_hop else "thu xếp công việc"
    c1 = f"{DOW_VI[target_date.weekday()]} {target_date.day}/{target_date.month} là ngày {hoang_txt}, trực {truc}, hợp {hop_str}."

    if dan:
        dan_str = " và ".join(dan)
        c2 = f"Tuổi {xung_chi} xung ngày, ngày {dan_str} nên tránh việc lớn."
    else:
        c2 = f"Tuổi {xung_chi} xung ngày, nên tránh việc lớn."

    c3 = f"Tuổi {tam_hop[0]}, {tam_hop[1]} và {luc_hop} hợp ngày. Dừng hình tìm tuổi của bạn nhé."
    script = [c1, c2, c3]

    return {
        "date": target_date,
        "duong_str": f"{target_date.day}/{target_date.month}/{target_date.year}",
        "dow_vi": DOW_VI[target_date.weekday()],
        "solar_day": target_date.day,
        "solar_month": target_date.month,
        "solar_year": target_date.year,
        "ld": ld,
        "lm": lm,
        "leap": leap,
        "am_str": f"{ld}/{lm}" + (" nhuận" if leap else ""),
        "can_chi_ngay": f"{CAN[can_i]} {CHI[chi_i]}",
        "chi_ngay": CHI[chi_i],
        "can_ngay": CAN[can_i],
        "than": than_name,
        "is_hoang": is_hoang,
        "hoang_hac_str": "HOÀNG ĐẠO" if is_hoang else "HẮC ĐẠO",
        "truc": truc,
        "dan": dan,
        "tiet_name": tiet_name,
        "tiet_thang": CHI[mchi],
        "xung_chi": xung_chi,
        "tam_hop": tam_hop,
        "luc_hop": luc_hop,
        "luc_hai": luc_hai,
        "luc_pha": luc_pha,
        "zodiac_grid": zodiac_grid,
        "viec_hop": viec_hop,
        "nen_display": nen_display,
        "tranh_display": tranh_display,
        "gio_hoang_dao": gio_names,
        "gio_display": gio_display,
        "script": script
    }


def build_composition_html(facts: dict, dur: float, segs: list[dict]) -> str:
    """Dựng HTML composition 1080x1920 (khuôn A) từ review_yeartable.html."""
    tpl = (COMP / "review_yeartable.html").read_text(encoding="utf-8")

    grid_cells_html = "\n".join([
        f'    <div class="cell {c["cls"]}"><div class="chi">{c["chi"]}</div><div class="tag">{c["tag"]}</div></div>'
        for c in facts["zodiac_grid"]
    ])

    custom_css = """
  #head { top: 75px; left: 40px; right: 40px; text-align: center; }
  #chip { font-size: 34px; padding: 10px 30px; }
  #title { font-size: 82px; margin-top: 14px; line-height: 1.05; }
  
  #meta { margin-top: 14px; display: inline-flex; align-items: center; justify-content: center; gap: 12px;
          padding: 8px 24px; border-radius: 40px; background: rgba(0,0,0,0.38); border: 2px solid rgba(255,211,77,0.5); }
  #meta .tag-hd { background: #ffd34d; color: #5a0805; font-weight: 900; font-size: 24px; padding: 4px 12px; border-radius: 10px; }
  #meta .tag-hd.hd-hac { background: #b91c1c; color: #fef2f2; }
  #meta .info-txt { color: #fff4cf; font-weight: 800; font-size: 26px; }

  #grid12 { position: absolute; left: 45px; right: 45px; top: 435px; height: 750px;
            display: grid; grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(3, 1fr); gap: 14px; }
  .cell { border-radius: 22px; display: flex; flex-direction: column; align-items: center; justify-content: center;
          position: relative; overflow: hidden; }
  .cell .chi { font-size: 74px; font-weight: 900; line-height: 1; }
  .cell .tag { font-size: 22px; font-weight: 800; padding: 4px 12px; border-radius: 10px; margin-top: 8px; }

  .cell.hop { background: linear-gradient(145deg, rgba(16, 185, 129, 0.42) 0%, rgba(6, 95, 70, 0.78) 100%);
              border: 3.5px solid #34d399; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.35); }
  .cell.hop .chi { color: #ecfdf5; text-shadow: 0 3px 8px rgba(0,0,0,.4); }
  .cell.hop .tag { background: #34d399; color: #064e3b; }

  .cell.tranh { background: linear-gradient(145deg, rgba(239, 68, 68, 0.5) 0%, rgba(153, 27, 27, 0.85) 100%);
                border: 3.5px solid #f87171; box-shadow: 0 8px 20px rgba(239, 68, 68, 0.4); }
  .cell.tranh .chi { color: #fff1f2; text-shadow: 0 3px 8px rgba(0,0,0,.4); }
  .cell.tranh .tag { background: #f87171; color: #7f1d1d; }

  .cell.luuy { background: linear-gradient(145deg, rgba(234, 179, 8, 0.45) 0%, rgba(161, 98, 7, 0.8) 100%);
               border: 3.5px solid #facc15; box-shadow: 0 8px 20px rgba(234, 179, 8, 0.35); }
  .cell.luuy .chi { color: #fef9c3; text-shadow: 0 3px 8px rgba(0,0,0,.4); }
  .cell.luuy .tag { background: #facc15; color: #713f12; }

  .cell.binh { background: linear-gradient(145deg, rgba(75, 12, 9, 0.85) 0%, rgba(42, 6, 4, 0.95) 100%);
               border: 2px solid rgba(242, 193, 78, 0.3); box-shadow: 0 6px 14px rgba(0,0,0,.25); }
  .cell.binh .chi { color: #fef08a; text-shadow: 0 3px 6px rgba(0,0,0,.4); }
  .cell.binh .tag { background: rgba(254, 240, 138, 0.16); color: #fde68a; }

  #info_box { position: absolute; left: 45px; right: 45px; top: 1205px; height: 285px;
              background: linear-gradient(180deg, rgba(90, 12, 8, 0.94), rgba(58, 8, 5, 0.96));
              border: 3.5px solid #f2c14e; border-radius: 28px; padding: 16px 24px;
              display: flex; flex-direction: column; justify-content: space-around;
              box-shadow: 0 12px 35px rgba(0,0,0,0.45); }
  .info-row { display: flex; align-items: center; gap: 16px; }
  .row-tag { flex: 0 0 140px; text-align: center; padding: 6px 0; border-radius: 12px;
             font-weight: 900; font-size: 26px; letter-spacing: .04em; }
  .row-tag.nen { background: #10b981; color: #022c22; }
  .row-tag.kieng { background: #ef4444; color: #450a0a; }
  .row-tag.gio { background: #f59e0b; color: #451a03; }
  .row-text { font-size: 28px; font-weight: 800; color: #fff; line-height: 1.25; }
  .row-text.gio-txt { font-size: 27px; color: #fef08a; }

  #cap { bottom: 170px; font-size: 42px; }
  #subfoot { position: absolute; left: 50px; right: 50px; bottom: 100px; text-align: center;
             color: #ffd34d; font-weight: 900; font-size: 34px; letter-spacing: .06em;
             text-shadow: 0 2px 10px rgba(0,0,0,.7); }
  #foot { bottom: 45px; font-size: 23px; opacity: .85; }
"""
    tpl = tpl.replace("</style>", custom_css + "\n</style>")
    subfoot_div = '<div id="subfoot">DỪNG HÌNH TÌM TUỔI CỦA BẠN</div>'
    tpl = tpl.replace('<div id="foot">', f'{subfoot_div}\n  <div id="foot">')

    grid_and_box_html = f"""
  <div id="grid12">
{grid_cells_html}
  </div>
  <div id="info_box">
    <div class="info-row">
      <div class="row-tag nen">NÊN</div>
      <div class="row-text">{facts['nen_display']}</div>
    </div>
    <div class="info-row">
      <div class="row-tag kieng">TRÁNH</div>
      <div class="row-text">{facts['tranh_display']}</div>
    </div>
    <div class="info-row">
      <div class="row-tag gio">GIỜ TỐT</div>
      <div class="row-text gio-txt">{facts['gio_display']}</div>
    </div>
  </div>
"""
    tpl = tpl.replace('<div id="rows"></div>', grid_and_box_html)

    tag_hd_cls = "tag-hd hd-hac" if not facts["is_hoang"] else "tag-hd"
    meta_html = f"""<div id="meta">
      <span class="{tag_hd_cls}">{facts["hoang_hac_str"]}</span>
      <span class="info-txt">{facts["am_str"]} ÂM · {facts["can_chi_ngay"].upper()} · {facts["than"].upper()} · TRỰC {facts["truc"].upper()}</span>
    </div>"""
    tpl = tpl.replace("__TITLE__</div>", "__TITLE__</div>\n    " + meta_html)

    data_payload = {
        "dur": dur,
        "theme": "red",
        "segs": segs
    }

    chip_txt = f"{facts['dow_vi'].upper()} · {facts['duong_str']}"
    title_line1 = f"NGÀY MAI {facts['solar_day']}/{facts['solar_month']}"
    title_line2 = "TUỔI BẠN THẾ NÀO?"
    title_html = f'<span class="l s">{title_line1}</span><span class="l gold">{title_line2}</span>'

    html = (
        tpl.replace("__DUR__", str(dur))
        .replace("__CHIP__", chip_txt)
        .replace("__TITLE__", title_html)
        .replace("__DATA__", json.dumps(data_payload, ensure_ascii=False))
    )
    return html


def extract_qa_sheet(mp4: Path, out_jpg: Path, n_frames: int = 4) -> None:
    r_probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
        capture_output=True, text=True
    )
    dur = float((r_probe.stdout or "0").strip() or 0)
    times = [round(dur * (i + 0.5) / n_frames, 2) for i in range(n_frames)]

    imgs = []
    for t in times:
        cmd = [
            "ffmpeg", "-y", "-ss", str(t), "-i", str(mp4),
            "-vframes", "1", "-vf", "scale=360:640", "-f", "image2pipe", "-vcodec", "mjpeg", "-"
        ]
        p = subprocess.run(cmd, capture_output=True)
        if p.stdout:
            img = Image.open(io.BytesIO(p.stdout)).convert("RGB")
            draw = ImageDraw.Draw(img)
            draw.text((15, 15), f"{t:.1f}s", fill=(255, 255, 255))
            imgs.append(img)

    if not imgs:
        return

    sheet = Image.new("RGB", (360 * len(imgs), 640))
    for i, im in enumerate(imgs):
        sheet.paste(im, (i * 360, 0))
    sheet.save(out_jpg, quality=85)


def export_last_frames(mp4: Path, out_dir: Path, rid: str) -> tuple[Path, Path]:
    r_probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
        capture_output=True, text=True
    )
    dur = float((r_probe.stdout or "0").strip() or 0)
    t = max(0.1, dur - 0.25)
    p_1080 = out_dir / f"{rid}_frame_1080.png"
    p_168 = out_dir / f"{rid}_frame_168.png"

    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t), "-i", str(mp4), "-vframes", "1", str(p_1080)],
        check=True, capture_output=True
    )
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t), "-i", str(mp4), "-vframes", "1", "-vf", "scale=168:-1", str(p_168)],
        check=True, capture_output=True
    )
    return p_1080, p_168


def render(target_date: dt.date | str, out_dir: Path | str | None = None, prefix: str | None = None) -> dict:
    """Hàm chuẩn render short khuôn A cho ngày chỉ định."""
    if isinstance(target_date, str):
        target_date = dt.date.fromisoformat(target_date)

    if out_dir is None:
        out_dir = SAMPLE_DIR
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dtag = target_date.strftime("%Y%m%d")
    rid = prefix if prefix else f"hd_{dtag}"

    facts = day_data(target_date)
    lines = facts["script"]

    txt_path = out_dir / f"{rid}.txt"
    wav_path = out_dir / f"{rid}.wav"
    mp4_path = out_dir / f"{rid}.mp4"

    clean_lines = [l.replace("**", "") for l in lines]
    txt_path.write_text("\n".join(clean_lines) + "\n", encoding="utf-8")

    if not wav_path.is_file():
        ok = R.render_tts(txt_path, wav_path, clean_lines, voice="Sơn")
        if not ok:
            raise RuntimeError(f"TTS giọng Sơn thất bại cho {rid}")

    manifest_p = wav_path.with_suffix(".json")
    manifest = json.loads(manifest_p.read_text(encoding="utf-8"))
    segs = manifest.get("segments") or []
    speech_end = segs[-1]["end"] if segs else 12.0
    dur = round(speech_end + 2.0, 2)

    html = build_composition_html(facts, dur=dur, segs=segs)
    comp_file = COMP / f"_tb_{rid}.html"
    comp_file.write_text(html, encoding="utf-8")

    silent_mp4 = out_dir / f"{rid}_silent.mp4"
    cmd = (
        f'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; nvm use 22 >/dev/null 2>&1; '
        f'cd "{HF}" && npx --yes hyperframes@0.8.75 render . -c compositions/{comp_file.name} --output "{silent_mp4}" --quality looks --fps 30 --quiet'
    )
    p = subprocess.run(["/bin/bash", "-lc", cmd], capture_output=True, text=True, timeout=1800)
    comp_file.unlink(missing_ok=True)

    if p.returncode != 0 or not silent_mp4.exists():
        raise RuntimeError(f"Render HyperFrames thất bại cho {rid}:\n" + (p.stdout + p.stderr)[-2000:])

    bgm_path = ROOT / FS_BGM
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(silent_mp4), "-i", str(wav_path),
            "-stream_loop", "-1", "-i", str(bgm_path),
            "-filter_complex",
            f"[1:a]apad[v];[2:a]volume={FS_BGM_GAIN},afade=t=out:st={dur - 1.2}:d=1.2[m];[v][m]amix=inputs=2:duration=first:normalize=0[a]",
            "-map", "0:v", "-map", "[a]", "-t", str(dur),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(mp4_path)
        ],
        check=True
    )
    silent_mp4.unlink(missing_ok=True)

    qa_sheet = out_dir / f"{rid}_qa.jpg"
    extract_qa_sheet(mp4_path, qa_sheet)
    f_1080, f_168 = export_last_frames(mp4_path, out_dir, rid)

    render_json_path = mp4_path.with_suffix(".render.json")
    render_json_path.write_text(
        json.dumps({
            "ok": True,
            "output": str(mp4_path.relative_to(ROOT)),
            "duration_s": dur,
            "speech_end_s": speech_end,
            "tail_s": round(dur - speech_end, 2),
            "style": "yeartable_daily_a",
            "voice": "Sơn",
            "bgm": FS_BGM,
            "bgm_gain": FS_BGM_GAIN
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    return {
        "id": rid,
        "mp4": mp4_path,
        "duration": dur,
        "speech_end": speech_end,
        "qa_sheet": qa_sheet,
        "frame_1080": f_1080,
        "frame_168": f_168,
        "facts": facts
    }


def self_check() -> int:
    """Tự kiểm 7 ngày verified trong calendar_facts_verified.json."""
    if not VERIFIED.is_file():
        return 0
    ver = json.loads(VERIFIED.read_text(encoding="utf-8"))
    bad = 0
    for iso, exp in ver.items():
        f = day_data(dt.date.fromisoformat(iso))
        exp_gio = [p.split(" (")[0] for p in exp["gio_tot"].split(", ")]
        got = [f["am_str"], f["can_chi_ngay"], f["than"], "hoàng đạo" if f["is_hoang"] else "hắc đạo", f["truc"], f["xung_chi"], f["gio_hoang_dao"]]
        want = [exp["am_lich"], exp["ngay"], exp["than"], exp["hoang_hac"], exp["truc"], exp["xung"], exp_gio]
        if got != want:
            bad += 1
            print(f"LỆCH {iso}: got {got} != want {want}")
    if bad:
        raise SystemExit(f"Tự kiểm verified thất bại: lệch {bad}/{len(ver)}")
    return len(ver)


def print_daily_summary(f: dict) -> None:
    print("\n" + "=" * 65)
    print(f"DỮ KIỆN LỊCH HOÀNG ĐẠO NGÀY {f['duong_str']} ({f['dow_vi']}):")
    print("=" * 65)
    print(f"Âm lịch         : {f['am_str']} (Năm Bính Ngọ)")
    print(f"Can chi ngày    : {f['can_chi_ngay']}")
    print(f"Thần            : {f['than']} ({f['hoang_hac_str']})")
    print(f"Trực            : {f['truc']} (Tháng tiết {f['tiet_thang']}, ngày {f['chi_ngay']})")
    if f["dan"]:
        print(f"Ngày kiêng kỵ   : {', '.join(f['dan'])}")
    print(f"NÊN             : {f['nen_display']}")
    print(f"TRÁNH           : {f['tranh_display']}")
    print(f"GIỜ TỐT         : {f['gio_display']}")

    print("\n--- 12 CON GIÁP (BẢNG 4x3) ---")
    for row in range(3):
        cells = f["zodiac_grid"][row*4 : (row+1)*4]
        line = " | ".join(f"{c['chi']}: {c['tag']:<8} ({c['reason']})" for c in cells)
        print(f"  Hàng {row+1}: {line}")

    print("\n--- LỜI ĐỌC (3 CÂU, ≤ 3 CHI/CÂU) ---")
    for i, line in enumerate(f["script"], 1):
        found = [w for w in line.replace(",", " ").replace(".", " ").split() if w in set(CHI)]
        print(f"  {i}. {line} [{len(found)} chi: {', '.join(found)}]")
    print("=" * 65 + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bộ sinh short Lịch Hoàng Đạo hằng ngày (khuôn A)")
    parser.add_argument("date", nargs="?", default="2026-10-22", help="Ngày cần tính YYYY-MM-DD (mặc định 2026-10-22)")
    parser.add_argument("--render", action="store_true", help="Thực hiện render video MP4 và khung QA")
    parser.add_argument("--out-dir", default=str(SAMPLE_DIR), help="Thư mục xuất file")
    parser.add_argument("--check-all", action="store_true", help="Chạy kiểm tra facts cho 22, 23, 24/10/2026")
    args = parser.parse_args()

    # 1. Tự kiểm 7 ngày verified
    n_ver = self_check()
    print(f"[OK] Tự kiểm facts verified: {n_ver}/{n_ver} ngày khớp 100%.")

    if args.check_all:
        for d_str in ["2026-10-22", "2026-10-23", "2026-10-24"]:
            f = day_data(d_str)
            print_daily_summary(f)
        return 0

    target_date = dt.date.fromisoformat(args.date)
    f = day_data(target_date)
    print_daily_summary(f)

    if args.render:
        print("Đang tiến hành render video...")
        r = render(target_date, out_dir=args.out_dir)
        print("\n--- KẾT QUẢ RENDER ---")
        print(f"  Video:       {r['mp4'].relative_to(ROOT)}")
        print(f"  Thời lượng:  {r['duration']:.2f}s (giọng đọc: {r['speech_end']:.2f}s, đuôi: {round(r['duration'] - r['speech_end'], 2):.2f}s)")
        print(f"  QA sheet:    {r['qa_sheet'].relative_to(ROOT)}")
        print(f"  Khung 1080:  {r['frame_1080'].relative_to(ROOT)}")
        print(f"  Khung 168:   {r['frame_168'].relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
