"""Dựng cả loạt Short từ một thư mục plan: kịch bản -> TTS -> HyperFrames.

Thay cho bản `run_batch.py` vẫn được sao chép theo từng đợt (tháng 9 một bản,
tháng 10 một bản) -- hai bản đã kịp lệch nhau: bản tháng 10 biết truyền
`--figures`, bản tháng 9 thì chưa. Một script trong repo, nhận thư mục plan
làm tham số, là hết chuyện lệch.

Chạy lại được nhiều lần: mục nào đã có .mp4 ĐỌC ĐƯỢC (ffprobe, duration > 0) thì bỏ qua,
nên dừng giữa chừng rồi chạy tiếp không tốn lại công render. File hỏng (thiếu moov,
duration không đọc được) không tính là xong: chuyển vào ~/.Trash/ rồi làm lại.

Usage:
    python3 hf_batch_render.py output/cl_staging/hyperframes_sept
    python3 hf_batch_render.py <thư mục> --only d26_a --quality draft
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from final_mix_lock import FinalMixLockTimeout, final_mix_lock
from final_mix_lock import available_gb as mix_available_gb, fmt_gb as mix_fmt_gb, log as mix_log

PROJECT_ROOT = Path(__file__).parent
# Giọng suy ra từ topic của kênh (topic_voices.json), không hardcode: kênh
# Phật giáo dùng giọng khác kênh Hình Sự.
SERIES_TOPIC = {"law": "Hình Sự", "scam": "Hình Sự", "case": "Hình Sự", "tale": "Hình Sự",
                "bud": "Phật giáo", "fs": "Phong Thủy"}


def voice_for(series: str) -> str:
    topic = SERIES_TOPIC.get(series, "Hình Sự")
    cfg = json.loads((PROJECT_ROOT / "topic_voices.json").read_text(encoding="utf-8"))
    return cfg["voices"].get(topic, cfg.get("_default", "Binh"))
TTS_HELPER = PROJECT_ROOT / "_short_tts_render.py"
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"

BGM = {"law": ("bgm/deliberate_thought.mp3", 0.17),
       "scam": ("bgm/thinking_music.mp3", 0.24),
       "case": ("bgm/deliberate_thought.mp3", 0.17),
       "tale": ("bgm/thinking_music.mp3", 0.20),
       # gain_db -9.7 của meditation_impromptu_01 trong bgm_tracks.py
       "bud": ("bgm/meditation_impromptu_01.mp3", 0.33),
       "fs": ("bgm/asian_drums.mp3", 0.2)}
FOOTER = {"law": "Phổ biến kiến thức pháp luật",
          "scam": "Nhận ra kịch bản trước khi chuyển tiền",
          "case": "Dẫn theo hồ sơ công khai",
          "tale": "Truyện hư cấu — nhân vật và tình tiết do tưởng tượng",
          "bud": "Nội dung suy ngẫm — không thay cho việc học Phật pháp trực tiếp",
          "fs": "Kiến thức truyền thống — để tham khảo"}

PLACEHOLDER_SCRIPT = ["(đã render trước, giữ nguyên file)"]
MAX_TTS_ATTEMPTS = 3
# Giọng đọc tiếng Việt rơi vào khoảng 13-19 ký tự/giây. Một câu dài hơn 3 lần
# mức đó là dấu hiệu TTS "đọc lồng" -- đã gặp thật: một câu ngắn bị đọc thành
# 32 giây, kéo cả video thành 55 giây và runner cũ chỉ lặng lẽ bỏ qua cả mục.
SEC_PER_CHAR_RUNAWAY = 3 / 13


def load_rows(plan_dir: Path) -> list[dict]:
    rows = []
    for f in sorted(glob.glob(str(plan_dir / "plan_*.json"))):
        rows += json.loads(Path(f).read_text(encoding="utf-8"))
    return rows


def wire_plan_row(row: dict, channel: str | None = None, legacy: bool | None = None, force: bool = False) -> dict:
    """Nối cấu hình giọng D và preset âm thanh C cho plan Long MỚI (task 92c).

    Quy tắc an toàn:
    - Nếu legacy=True hoặc row.get("legacy") is True: giữ nguyên cấu hình cũ (không D, không C).
    - Nếu legacy is None (mặc định) và not force:
      Nếu row đã có "tts" mà không có bất kỳ khoá nào trong 3 khoá giọng D
      (temperature, donor, text_mode): coi là plan CŨ (vd plan #72 hoặc build lại
      để cập nhật SEO/xem tiếp) -> lý do giữ nguyên: không tự thêm để không đổi cache/mix.
    - Plan MỚI (legacy=False, hoặc row chưa có tts, hoặc force=True):
      nạp sẵn 3 khoá giọng D từ hf_voice.new_tts(channel) và
      sound.preset_long = 'C' từ hf_sound.new_sound(channel).
    """
    ch = channel or row.get("series") or row.get("channel") or row.get("kenh")
    tts = row.get("tts")
    sound = row.get("sound")

    if legacy is True or bool(row.get("legacy")):
        return row

    # Nhận diện plan cũ: đã có tts nhưng thiếu cả 3 khoá giọng D
    has_d_keys = bool(tts and any(k in tts for k in ("temperature", "donor", "text_mode")))
    if legacy is None and tts is not None and not has_d_keys and not force:
        # Lý do rõ: plan cũ đã có tts thiếu 3 khoá -> không tự thêm để bảo vệ cache & mix cũ
        return row

    # Nối cho plan MỚI
    if ch:
        import hf_voice  # noqa: PLC0415
        import hf_sound  # noqa: PLC0415
        row["tts"] = hf_voice.new_tts(ch, **(tts or {}))
        row["sound"] = hf_sound.new_sound(ch, **(sound or {}))
    # Chỉ plan MỚI (builder truyền legacy=False). force=True là nâng giọng plan cũ:
    # không đóng dấu v2. Render không gọi hàm này — plan thiếu khoá giữ v1.
    if legacy is False and not force:
        _stamp_layout_policy(row, legacy=legacy)
    return row


def _stamp_layout_policy(row: dict, legacy: bool | None = None) -> None:
    """Plan Long mới chưa khai khoá thì mặc định v2. Đã khai (kể cả v1) thì giữ."""
    if legacy or row.get("legacy"):
        return
    if row.get("layout_policy"):
        return
    style = str(row.get("style") or "")
    if row.get("lane") == "long" or style.endswith("_long"):
        row["layout_policy"] = "v2"


def warn_missing_style(row: dict, out_dir: Path) -> None:
    """Long mới chưa render, 0 cảnh style: cảnh báo nhẹ, không chặn, không ghi plan."""
    import hf_style_suggest as HSS  # noqa: PLC0415
    if not HSS.is_long_row(row):
        return
    if (out_dir / f"{row.get('id')}.mp4").is_file():
        return
    if line := HSS.warning_line(row):
        print(line, flush=True)


def warn_missing_layout_policy(row: dict, out_dir: Path) -> None:
    """Long mới (chưa có mp4) thiếu layout_policy v2: cảnh báo, không chặn."""
    if row.get("lane") != "long" or row.get("layout_policy") == "v2":
        return
    if (out_dir / f"{row.get('id')}.mp4").is_file():
        return
    print(f"    CẢNH BÁO layout_policy: Long mới {row.get('id')} chưa có file mp4 và thiếu "
          f"layout_policy \"v2\". Bố cục sẽ chạy v1 (chia đều 8 kiểu, ảnh tràn khung chỉ khoảng 1/8). "
          f"Thêm \"layout_policy\": \"v2\" vào plan.", flush=True)


def layout_v2_choices(row: dict, segments: list | None = None) -> dict | None:
    """Tính bố cục v2 cho cả video. Plan không khai v2 thì trả None (giữ v1)."""
    if row.get("layout_policy") != "v2":
        return None
    import hyperframes_bridge as HB  # noqa: PLC0415
    return HB.assign_layouts_v2(
        row.get("media") or {}, row.get("id") or "video",
        script=row.get("script") or [], visuals=row.get("visuals") or {},
        segments=segments, series=row.get("series"),
        scene_decision=row.get("scene_decision") or {}, figures=row.get("figures") or {})


def layout_v2_opts(opts: dict, row: dict, chosen: dict, shift: int = 0,
                   lo: int | None = None, hi: int | None = None) -> dict:
    """Nhét map đã tính vào opts. Khoá câu trong một chương bị trừ `shift`."""
    out = dict(opts)
    out["layout_policy"] = "v2"
    out["layout_seed"] = row.get("id") or ""
    payload = {}
    for sid, choice in chosen.items():
        if lo is not None and not (lo < int(sid) <= hi):
            continue
        payload[str(int(sid) - shift)] = {"layout": choice.get("layout") or "", "cine": choice.get("cine")}
    out["layout_v2"] = payload
    return out


def save_plan_rows(plan_file: Path | str, rows: list[dict] | dict, channel: str | None = None,
                   legacy: bool | None = None, force: bool = False) -> Path:
    """Builder dùng chung: chuẩn hoá tts/sound qua wire_plan_row rồi ghi JSON đẹp vào đĩa.

    Quy tắc an toàn (task 92d sửa theo Codex review):
    - Đọc file plan hiện có trên đĩa (nếu tồn tại).
    - Row cùng `id` đã có trong plan: GIỮ NGUYÊN `tts` và `sound` cũ (không nâng lên D/C).
    - Chỉ row mới (id chưa có trong plan) mới được tự động nạp giọng D và preset C.
    - Hỗ trợ truyền `rows` dạng dict (1 row) hoặc list[dict].
    """
    p = Path(plan_file)
    existing_rows: list[dict] = []
    existing_by_id: dict[str, dict] = {}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                existing_rows = data
            elif isinstance(data, dict):
                existing_rows = [data]
            for r in existing_rows:
                if isinstance(r, dict) and "id" in r:
                    existing_by_id[r["id"]] = r
        except Exception:
            existing_rows = []
            existing_by_id = {}

    if isinstance(rows, dict):
        target_id = rows.get("id")
        if existing_rows:
            found = False
            merged = []
            for er in existing_rows:
                if isinstance(er, dict) and er.get("id") == target_id:
                    merged.append(rows)
                    found = True
                else:
                    merged.append(er)
            if not found:
                merged.append(rows)
            row_list = merged
        else:
            row_list = [rows]
    else:
        row_list = list(rows)

    wired = []
    for r in row_list:
        rid = r.get("id") if isinstance(r, dict) else None
        if rid and rid in existing_by_id:
            old_r = existing_by_id[rid]
            if not force:
                # Row đã có trong plan: GIỮ NGUYÊN tts và sound cũ (không nâng lên D/C)
                if "tts" in old_r:
                    r["tts"] = json.loads(json.dumps(old_r["tts"]))
                    # Plan cũ chưa có vân tay thì giữ nguyên từng byte: thêm metadata vào tts
                    # sẽ đổi hash kịch bản -> xoá wav và đọc lại cả Long (05/11).
                    if isinstance(r["tts"], dict) and "_line_fingerprints" in r["tts"]:
                        _refresh_tts_line_fingerprints(r)
                if "sound" in old_r:
                    r["sound"] = json.loads(json.dumps(old_r["sound"]))
                wired.append(r)
                continue
        # Row mới (hoặc force=True): nạp sẵn giọng D và preset C
        ch = channel or r.get("series") or r.get("channel") or r.get("kenh")
        w = wire_plan_row(r, channel=ch, legacy=False if legacy is None else legacy, force=force)
        _refresh_tts_line_fingerprints(w)
        # Style #258: chỉ plan Long mới (id chưa có trên đĩa). Plan cũ giữ nguyên visuals.
        if not w.get("legacy") and w.get("style_suggest") is not False:
            import hf_style_suggest as HSS  # noqa: PLC0415
            if HSS.is_long_row(w):
                HSS.apply_suggestions(w, adopt=True)
        wired.append(w)

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(wired, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def _tts_line_fingerprint(line: str) -> str:
    """Dấu vân tay ổn định của đúng văn bản một dòng kịch bản."""
    return hashlib.sha1(line.strip().encode("utf-8")).hexdigest()[:8]


def _refresh_tts_line_fingerprints(row: dict) -> list[str]:
    """Gắn fingerprint cho khoá pauses/tempos và bỏ khoá đã trỏ nhầm câu."""
    tts = row.get("tts")
    if not isinstance(tts, dict):
        return []
    script = row.get("script") or []
    fingerprints = tts.setdefault("_line_fingerprints", {})
    removed = []
    for kind in ("pauses", "tempos"):
        kind_fp = fingerprints.setdefault(kind, {})
        values = tts.get(kind) or {}
        for key in list(values):
            if not str(key).isdigit():
                continue
            idx = int(key)
            current = _tts_line_fingerprint(script[idx - 1]) if 1 <= idx <= len(script) else None
            previous = kind_fp.get(str(key))
            if previous is not None and previous != current:
                del values[key]
                kind_fp.pop(str(key), None)
                removed.append(f"{kind}[{key}]")
            elif current is not None:
                kind_fp[str(key)] = current
            else:
                kind_fp.pop(str(key), None)
        # Metadata chỉ mô tả các override còn tồn tại.
        for key in list(kind_fp):
            if key not in values:
                kind_fp.pop(key, None)
    if not any(fingerprints.values()):
        tts.pop("_line_fingerprints", None)
    if removed:
        print(f"CẢNH BÁO {row.get('id')}: bỏ override TTS cũ vì câu đã đổi: {', '.join(removed)}", file=sys.stderr)
    return removed


def runaway_segments(manifest_path: Path, script_lines: list[str]) -> list[int]:
    """Trả về chỉ số (1-based) các câu bị đọc dài bất thường."""
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    segments = data.get("segments") or []
    bad = []
    for i, seg in enumerate(segments, start=1):
        if i > len(script_lines):
            break
        expected = max(1.5, len(script_lines[i - 1]) * SEC_PER_CHAR_RUNAWAY)
        if (seg["end"] - seg["start"]) > expected:
            bad.append(i)
    if data.get("n_failed_qa"):
        bad = bad or [0]
    return bad


def render_tts(txt: Path, wav: Path, script_lines: list[str], voice: str = "Tuyen",
              mode: str = "standard", device: str = "mps") -> bool:
    """TTS kèm thử lại khi phát hiện đọc lồng. Trả False nếu vẫn hỏng."""
    for attempt in range(1, MAX_TTS_ATTEMPTS + 1):
        for stale in (wav, wav.with_suffix(".json")):
            stale.unlink(missing_ok=True)
        proc = subprocess.run(
            [str(VENV_PYTHON), str(TTS_HELPER), "--text-file", str(txt),
             "--voice", voice, "--mode", mode, "--device", device,
             "--output-wav", str(wav)],
            cwd=PROJECT_ROOT, capture_output=True, text=True)
        manifest = wav.with_suffix(".json")
        if not manifest.is_file():
            print(f"    TTS lỗi (lần {attempt}): {proc.stderr[-200:]}", file=sys.stderr, flush=True)
            continue
        bad = runaway_segments(manifest, script_lines)
        if not bad:
            return True
        print(f"    TTS đọc lồng ở câu {bad} (lần {attempt}/{MAX_TTS_ATTEMPTS}) -- render lại",
              file=sys.stderr, flush=True)
    return False


# Video dài xoay vòng nhạc theo tâm trạng kênh -- một track chạy mọi video
# thì người xem quen tai. Chọn theo hash id (tất định, không cần sổ trạng thái):
# render lại cùng một video luôn ra cùng một track, nên ghi nguồn không lệch.
LONG_BGM_POOL = {"bud": ["bgm/meditation_impromptu_01.mp3", "bgm/meditation_impromptu_02.mp3",
                         "bgm/meditation_impromptu_03.mp3"],
                 "fs": ["bgm/clean_soul.mp3", "bgm/thinking_music.mp3",
                        "bgm/deliberate_thought.mp3"]}


def pick_bgm(row: dict, wav: Path) -> tuple[str, float]:
    """(track, hệ số) cho một mục. Short giữ bảng BGM cố định như cũ; video dài
    chọn track trong pool và tính hệ số theo loudness đo thật của giọng đọc."""
    bgm, gain = BGM[row["series"]]
    if row.get("lane") != "long":
        if not row.get("bgm") and row["series"] in ("bud", "fs"):
            import hf_music  # noqa: PLC0415 -- mỗi short một bài (chính sách Spam: cùng nhạc nền trên nhiều video)
            if row.get("day", "") >= hf_music.SHORT_FROM:
                return hf_music.short_pick(row, PROJECT_ROOT)
        return row.get("bgm", bgm), row.get("bgm_gain", gain)
    if long_pool(row):
        bgm = long_pool(row)[0]   # sổ nhạc: mỗi video một bộ bài khác video gần nó
    elif row.get("bgm"):
        bgm = row["bgm"]
    else:
        pool = LONG_BGM_POOL.get(row["series"]) or [bgm]
        bgm = pool[int(hashlib.sha1(row["id"].encode()).hexdigest(), 16) % len(pool)]
    if row.get("bgm_gain") is not None:
        return bgm, row["bgm_gain"]
    from hyperframes_bridge import relative_bgm_gain  # noqa: PLC0415
    return bgm, relative_bgm_gain(wav, PROJECT_ROOT / bgm)


def long_pool(row: dict) -> list[str] | None:
    """Thứ tự bài từ sổ nhạc cho video dài theo chương BUD/FS. "bgm" cũ trong plan bị bỏ qua (mọi build trước 04/10 ghim
    một bài Meditation/Deliberate...) trừ khi plan ghi "bgm_pin": true."""
    if not row.get("chapters") or row.get("bgm_pin") or row["series"] not in ("bud", "fs"):
        return None
    import hf_music  # noqa: PLC0415
    return hf_music.pool_for(row, PROJECT_ROOT)


def note_bgm(row: dict, mixed: Path) -> list[str]:
    """Bài nhạc nền mix_long thực sự đã phát -> sổ nhạc + cảnh báo trùng với video gần đó."""
    side = mixed.with_suffix(".bgm.json")
    used = json.loads(side.read_text(encoding="utf-8")) if side.exists() else []
    if used and long_pool(row):
        import hf_music  # noqa: PLC0415
        hf_music.record(row["id"], used)
        for x in hf_music.audit(row["id"]):
            print(f"    !! nhạc nền: {x}", flush=True)
    return used


def remix_long(row: dict, out_dir: Path) -> tuple[bool, str]:
    """Video dài theo chương: trộn lại 4 lớp tiếng (hf_foley.mix_long) trên hình đã nối (silent.mp4), không render lại."""
    import hyperframes_bridge as HB  # noqa: PLC0415
    import hf_foley  # noqa: PLC0415
    rid = row["id"]
    txt, wav, mp4 = out_dir / f"{rid}.txt", out_dir / f"{rid}.wav", out_dir / f"{rid}.mp4"
    cdir = out_dir / f"{rid}_chapters"
    silent = cdir / "silent.mp4"
    if not (wav.exists() and txt.exists() and silent.exists()):
        return True, "bỏ qua (thiếu wav/txt/silent.mp4 -- render lại)"
    total = float(json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))["duration_s"])
    bgm, _ = pick_bgm(row, wav)
    try:
        with final_mix_lock(rid):   # nạp tiếng cả video vào RAM (~11 GB với Long 30 phút): mỗi máy một job một lúc
            glines = HB.build_lines(txt, wav.with_suffix(".json"), align_audio=wav)
            HB.apply_visuals(glines, row.get("visuals") or {}, row.get("media") or {})
            for ln in glines:
                if str(ln["sentence_id"]) in (row.get("media") or {}):
                    ln["media"] = {"query": ""}
            mixed = cdir / "mix.wav"
            sound_spec = row.get("sound") or {}
            if row.get("ambience") or row.get("beats"):
                import hf_ambience  # noqa: PLC0415
                sound_spec = hf_ambience.sound_spec(row)
            hf_foley.mix_long(glines, row["series"], wav, PROJECT_ROOT / bgm if bgm else None, total, sound_spec,
                              {int(x) for x in row.get("silence") or []}, mixed, seed=hashlib.sha1(rid.encode()).digest()[0],
                              pool=long_pool(row))
            mix_log(f"{rid}: trộn xong | RAM trống {mix_fmt_gb(mix_available_gb())}")
            used = note_bgm(row, mixed)
            tmp = mp4.with_name(f"{rid}.remix.mp4")
            HB.mux_audio(silent, mixed, tmp, duration=total, loudness=HB.LOUD_TARGET["long"])
            tmp.replace(mp4)
            rj = out_dir / f"{rid}.render.json"
            if rj.exists():
                meta = json.loads(rj.read_text(encoding="utf-8"))
                meta.update(bgm=str(PROJECT_ROOT / bgm) if bgm else "", bgm_used=used)
                rj.write_text(json.dumps(meta, ensure_ascii=False) + "\n", encoding="utf-8")
    except FinalMixLockTimeout as exc:
        return False, str(exc)
    return True, "trộn lại tiếng 4 lớp: " + " -> ".join(used)


def remix_audio(row: dict, out_dir: Path) -> tuple[bool, str]:
    """Trộn lại tiếng cho video đã render (giữ nguyên hình, chép luồng video) --
    đổi nhạc/âm lượng mất vài giây thay vì render lại 10 phút."""
    if row.get("chapters"):        # video dài: đường cũ (mux_audio + bgm) sẽ làm mất lớp không khí/tiếng động
        return remix_long(row, out_dir)
    rid = row["id"]
    mp4, wav = out_dir / f"{rid}.mp4", out_dir / f"{rid}.wav"
    if not mp4.exists() or not wav.exists():
        return True, "bỏ qua (chưa render)"
    from hyperframes_bridge import LOUD_TARGET, mux_audio  # noqa: PLC0415
    bgm, gain = pick_bgm(row, wav)
    dur = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))["duration_s"]
    tmp = mp4.with_name(f"{rid}.remix.mp4")
    mux_audio(mp4, wav, tmp, bgm=PROJECT_ROOT / bgm, bgm_gain=gain, duration=dur,
              loudness=LOUD_TARGET["long" if row.get("lane") == "long" else "short"])
    tmp.replace(mp4)
    rj = out_dir / f"{rid}.render.json"
    if rj.exists():
        meta = json.loads(rj.read_text(encoding="utf-8"))
        meta.update(bgm=str(PROJECT_ROOT / bgm), bgm_gain=gain)
        rj.write_text(json.dumps(meta, ensure_ascii=False) + "\n", encoding="utf-8")
    return True, f"trộn lại: {Path(bgm).name} x{gain}"


# Kênh Phong Thuỷ gọi con giáp bằng TÊN CHI của 12 con giáp Việt Nam (Tý, Sửu,
# Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi) -- không dịch ra con vật.
# "Tuổi Lợn", "tuổi Dê" lọt vào L_fs_01 và bị người xem chê. Tên con vật viết
# HOA giữa câu chỉ xuất hiện khi dùng làm tên tuổi, nên bắt theo cách đó.
# "Bạch Hổ" là linh vật trấn phương Tây (tứ linh), không phải cách gọi tuổi -> không chặn.
ZODIAC_ANIMAL = re.compile(r"(?<![.!?:]\s)(?<!^)(?<!Bạch\s)\b(Chuột|Trâu|Hổ|Cọp|Mèo|Rồng|Rắn|Ngựa|Dê|Khỉ|Gà|Chó|Lợn|Heo)\b")


def zodiac_naming_errors(lines: list[str]) -> list[str]:
    """Các câu gọi con giáp bằng tên con vật thay vì tên chi."""
    bad = []
    for n, line in enumerate(lines, 1):
        text = line.replace("**", "")
        if ZODIAC_ANIMAL.search(text) or re.search(r"(?i)\btuổi (chuột|trâu|hổ|cọp|mèo|rồng|rắn|ngựa|dê|khỉ|gà|chó|lợn|heo)\b", text):
            bad.append(f"câu {n}: {text[:70]}")
    return bad


CHI_NAME = re.compile(r"\b(Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi)\b")


def crowded_chi_lines(lines: list[str], limit: int = 4) -> list[str]:
    """Câu nhắc >= 4 tên chi: TTS đọc lồng, hỏng cả 3 lần thử (f35_a, f36_a, f36_e ngày
    30/09/2026 -- mỗi lần mất 5-11 phút). Chặn trước khi tốn TTS: tách câu, tối đa 3 tên."""
    return [f"câu {n}: {l[:60]}" for n, l in enumerate(lines, 1)
            if len(CHI_NAME.findall(l.replace("**", ""))) >= limit]


def bare_lines(row: dict) -> list[int]:
    """Video dài: câu không sơ đồ, không ảnh (kể cả ảnh giữ từ câu trước), không chữ khoá **...**.
    Engine sẽ lấy mấy chữ ĐẦU câu làm tiêu đề lớn ("CÓ HAI CHIẾC CHÌA") -- lỗi F1/B1 01/10/2026."""
    import hyperframes_bridge as HB  # noqa: PLC0415
    script = row.get("script") or []
    lines = [{"sentence_id": i + 1, "start": i * 3.0, "end": i * 3.0 + 2.5, "words": [],
              "heading": t.startswith("**") and t.endswith("**") and t.count("**") == 2} for i, t in enumerate(script)]
    media = row.get("media") or {}
    HB.apply_visuals(lines, row.get("visuals") or {}, media)
    holds = HB.media_holds(lines, {int(k) for k in media})
    held = {k for i, j in holds.items() for k in range(i + 1, j + 1)}
    return [i + 1 for i, ln in enumerate(lines)
            if not ln.get("visual") and not ln.get("visual_cont") and str(i + 1) not in media
            and i not in held and not ln["heading"] and "**" not in script[i]]


def style_scene_issues(row: dict) -> list[str]:
    """Bộ style bổ sung (#258: woodcut, papercut, oneline, film16, blueprint, pencil) là điểm nhấn: CẢ VIDEO
    tối đa 3 cảnh, không hai cảnh liền nhau. Bridge chỉ thấy từng chương khi render theo chương nên
    cổng này soi cả plan. Không plan nào gọi tên thì danh sách rỗng, không đụng gì."""
    import hyperframes_bridge as HB  # noqa: PLC0415
    spans = []
    for k, v in (row.get("visuals") or {}).items():
        if not isinstance(v, dict) or v.get("type") not in HB.STYLE_VISUAL_TYPES:
            continue
        sid = int(k)
        spans.append((sid, HB.style_until(sid, v), v["type"]))
    return HB.style_scene_issues(spans)


def reveal_issues(row: dict) -> list[str]:
    """Sơ đồ hiện từng dòng theo {at, word}: engine bắt LẦN ĐẦU từ ấy xuất hiện trong câu. Lỗi F10 03/10/2026:
    "cửa nhà" (dòng 2) có chữ "nhà" sớm hơn "ngõ" (dòng 1) -> dòng 2 hiện trước; bảng có dòng đầu ở câu sau
    -> khung trống cả một câu. Chỉ cảnh báo, không chặn."""
    script = row.get("script") or []

    def pos(at: int, word: str | None) -> tuple[int, int]:
        if not word or not 0 < at <= len(script):
            return at, 0
        t = re.findall(r"\w+", script[at - 1].replace("**", "").lower())
        w = re.findall(r"\w+", word.lower())
        return at, next((i for i in range(len(t)) if t[i:i + len(w)] == w), 999)

    out = []
    for k, v in sorted((row.get("visuals") or {}).items(), key=lambda x: int(x[0])):
        seq = next((v[key] for key in ("rows", "items", "steps", "turns", "pins") if isinstance(v.get(key), list)), [])
        seq = [x for x in seq if isinstance(x, dict) and isinstance(x.get("at"), int)]
        seq += [v[s] for s in ("left", "right") if isinstance(v.get(s), dict) and isinstance(v[s].get("at"), int)]
        if not seq:
            continue
        ps = [pos(x["at"], x.get("word")) for x in seq]
        if any(p[1] == 999 for p in ps):
            out.append(f"câu {k} ({v.get('type')}): không thấy chữ {[x.get('word') for x in seq if pos(x['at'], x.get('word'))[1] == 999]}")
        elif ps != sorted(ps):
            out.append(f"câu {k} ({v.get('type')}): dòng hiện sai thứ tự {[x.get('word') for x in seq]}")
        if min(ps)[0] > int(k) and len(script[int(k) - 1].split()) > 14:
            out.append(f"câu {k} ({v.get('type')}): khung trống cả câu, dòng đầu ở câu {min(ps)[0]}")
    return out


# Công thức short v2 (đánh giá 28 ngày tới 03/10/2026, hf_shorts_report.py): short nào cũng dừng ở ~900-1.000 view
# (vòng thử của feed Shorts); bài bứt lên là bài xem hết > 90%. Bài yếu rơi người xem ở 20-50% thời lượng, đúng câu 2
# khi câu 2 là định nghĩa/thuật ngữ ("Nhà Phật gọi đó là tập khí", "Thái cực sinh lưỡng nghi"). Bài < 20 giây
# (FS) chỉ trung vị 122 view; 21-27 giây tốt nhất. Áp cho short lên lịch từ ngày dưới (short cũ đã đăng hết).
SHORT_V2_FROM = "2026-11-14"
# Giọng FS đọc chậm hơn: f40 102 tiếng = 33 giây; BUD b44 99 tiếng = 28 giây.
SHORT_V2_SYLLABLES = {"bud": (80, 102), "fs": (68, 88)}
DEFINE_OPENER = re.compile(r"(?i)^(\*\*)?(nhà phật|đạo phật|kinh [^ ]+|phật giáo|người xưa|phong thủy|kinh dịch)?\s*(gọi (đó|nó|đây) là|gọi là|được gọi là|nghĩa là|có nghĩa là|là (một|tên)|định nghĩa)")
DEFINE_IN2 = re.compile(r"(?i)\b(gọi (đó|nó|đây|là)|được gọi là|có nghĩa là|nghĩa là gì)\b")


# Cổng toàn vẹn văn bản (mượn factory/integrity.py của Youtube_Creator_V2, 04/10/2026): soi đúng chữ SẼ ĐƯỢC ĐỌC
# (đã bóc **), chặn ký hiệu/markup sót (mọi video) và câu lặp nguyên văn (chỉ short) -- những lỗi "chắc chắn sai" mà TTS đọc thành tiếng.
INTEGRITY_MARKUP = [("dấu *", re.compile(r"\*")), ("ngoặc vuông", re.compile(r"[\[\]]")), ("ngoặc nhọn", re.compile(r"[{}]")),
                    ("dấu #", re.compile(r"#")), ("dấu `", re.compile(r"`")), ("URL", re.compile(r"(?i)https?://|www\.")),
                    ("khoá JSON", re.compile(r'"\w+"\s*:')), ("nhãn phương án", re.compile(r"(?i)\bphương án\s+[A-D]\b"))]


def integrity_issues(row: dict) -> list[str]:
    out, seen = [], {}
    script = row.get("script") or []
    if "voices" in row:
        voices = row.get("voices")
        if not isinstance(voices, list):
            out.append("khoá 'voices' phải là danh sách")
        elif len(voices) != len(script):
            out.append(f"khoá 'voices' có độ dài {len(voices)}, không khớp kịch bản ({len(script)})")
        else:
            invalid_tags = {v for v in voices if v not in ("ke", "ta")}
            if invalid_tags:
                out.append(f"khoá 'voices' chứa nhãn không hợp lệ: {sorted(invalid_tags)} (chỉ chấp nhận 'ke' hoặc 'ta')")
    for n, line in enumerate(script, 1):
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
        for name, pat in INTEGRITY_MARKUP:
            if pat.search(text):
                out.append(f"câu {n}: còn {name} -- TTS sẽ đọc: {text[:50]}")
        for sent in re.findall(r"[^.!?…]+[.!?…]*", text):
            key = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", sent.lower())).strip()
            # video dài lặp có chủ đích (điệp khúc kệ, motif, callback) -> chỉ chặn lặp ở short
            if len(key.split()) >= 4 and row.get("lane") != "long":
                if key in seen:
                    out.append(f"câu {n}: lặp nguyên văn câu {seen[key]}: {sent.strip()[:50]}")
                seen.setdefault(key, n)
    return out


def short_v2_issues(row: dict) -> list[str]:
    """Lỗi công thức short v2 (chặn render): câu 2 là định nghĩa, độ dài lệch SHORT_V2_SYLLABLES (~21-27 giây;
    b28_c 101 tiếng = 26 giây, short Phase D ~63 tiếng = 17 giây), thiếu `insight` (dòng đầu mô tả)."""
    if row.get("lane") == "long" or row.get("series") not in ("bud", "fs") or row.get("day", "") < SHORT_V2_FROM:
        return []
    script = [x.replace("**", "") for x in row.get("script") or []]
    out = []
    if len(script) >= 2 and (DEFINE_OPENER.search(script[1]) or DEFINE_IN2.search(script[1])):
        out.append(f"câu 2 là định nghĩa/thuật ngữ (người xem rơi ở đây) -- đưa thuật ngữ xuống câu 3: {script[1][:60]}")
    mute = set(row.get("silence") or [])   # câu hỏi lặng (ask) không có tiếng đọc
    n = sum(len(x.split()) for i, x in enumerate(script, 1) if i not in mute)
    lo, hi = SHORT_V2_SYLLABLES[row["series"]]
    if not lo <= n <= hi:
        out.append(f"{n} tiếng -- cần {lo}-{hi} (~21-27 giây; < 20 giây không được feed đẩy)")
    if len(script[0].split()) > 22 if script else False:
        out.append(f"câu 1 dài {len(script[0].split())} tiếng -- móc câu <= 22 tiếng")
    if not row.get("insight"):
        out.append("thiếu `insight` (câu trả lời một câu, dòng đầu mô tả)")
    if not row.get("novelty_ok"):   # đã soát tay thấy khác chủ đề -> ghi lý do vào novelty_ok
        import hf_novelty  # noqa: PLC0415
        if (dup := hf_novelty.duplicates(row["series"], row.get("title", ""), self_id=row.get("id"))):
            out.append("trùng chủ đề trên kênh (hf_novelty): " + " ; ".join(f"{k} {t}" for k, t in dup[:3]))
    return out


# Short v3 (06/10/2026, bài học kênh CL của V2: short "neo" vào vụ án có tên riêng hồi từ 0 lên ~1.000 view trong vài giờ),
# nhưng GIỮ HỒN RIÊNG: BUD hiền, chữa lành, có kinh; FS kiến thức truyền thống để tham khảo, thực tế. Không giật gân.
SHORT_V3_FROM = "2026-11-18"
SENSATIONAL = re.compile(r"(?i)chấn động|rợn người|rùng mình|sốc|kinh hoàng|tiền về ồ ạt|tiền vàng|giàu to|giàu bất ngờ|đổi đời|"
                         r"phát tài lớn|trúng lớn|tiên tri|tận thế|đại họa|xui tận mạng|quỷ dữ|vận đen")
SUTTA_CITE = re.compile(r"(?i)\b(trung bộ|trường bộ|tương ưng|tăng chi|pháp cú|kinh tập|tiểu tụng|phật tự thuyết|trưởng lão)\b")


def short_tone_issues(row: dict) -> list[str]:
    """CHẶN: lời lẽ giật gân trong tiêu đề/kịch bản short BUD/FS (từ lịch SHORT_V3_FROM)."""
    if row.get("lane") == "long" or row.get("series") not in ("bud", "fs") or row.get("day", "") < SHORT_V3_FROM:
        return []
    text = " ".join([row.get("title", "")] + list(row.get("script") or [])).replace("**", "")
    return [f"giật gân '{m}' -- không hợp hồn kênh" for m in dict.fromkeys(SENSATIONAL.findall(text))]


def short_hook_hints(row: dict) -> list[str]:
    """NHẮC (không chặn): tiêu đề có 'neo' (tên riêng, con số, chi tiết cụ thể; builder ghi ở row['anchor']),
    short BUD dẫn kinh thì mô tả có link SuttaCentral (row['source'])."""
    if row.get("lane") == "long" or row.get("series") not in ("bud", "fs") or row.get("day", "") < SHORT_V3_FROM:
        return []
    out, title = [], row.get("title", "")
    a = row.get("anchor")
    if not a:
        out.append("chưa ghi 'anchor' (tên riêng / con số / chi tiết cụ thể làm neo)")
    elif a.lower() not in (title + " " + ((row.get("script") or [""])[0])).replace("**", "").lower():
        out.append(f"neo '{a}' không có trong tiêu đề hay câu đầu")
    if row.get("series") == "bud" and SUTTA_CITE.search(" ".join(row.get("script") or [])) and "suttacentral" not in row.get("source", ""):
        out.append("có dẫn kinh mà 'source' chưa có link SuttaCentral (hf_sutta.link)")
    return out


def retention_issues(row: dict, rate: float = 185 / 60) -> list[str]:
    """Video dài, theo sổ tay giữ chân của Youtube_Creator_V2 (motion/long/RETENTION.md), đo trên CÂU NÓI (tách
    theo . ! ?): câu > 35 tiếng (TTS hụt hơi, người nghe mất mạch); câu ngắn <= 6 tiếng (nhịp đỉnh) ít hơn 1/8
    số câu; đoạn > 90 giây không ngắt nhịp (câu hỏi, con số, câu ngắn, trích kinh, thẻ chương). Chỉ cảnh báo.
    Đo 04/10/2026: F10-B14 đạt 2 luật sau, thiếu câu ngắn (F14 1/48, F10 1/43)."""
    vis, sents, cur, worst, at = row.get("visuals") or {}, [], 0.0, 0.0, 0
    for i, line in enumerate(row.get("script") or [], 1):
        if line.startswith("**") and line.endswith("**"):
            cur = 0.0
            continue
        t = line.replace("**", "")
        ss = [x.strip() for x in re.findall(r"[^.!?]+[.!?]?", t) if x.strip()]
        sents += [(i, len(x.split())) for x in ss]
        hit = ("?" in t or re.search(r"\d", t) or any(len(x.split()) <= 6 for x in ss)
               or (vis.get(str(i)) or {}).get("type") in ("quote", "ask", "stamp"))
        cur = 0.0 if hit else cur + len(t.split()) / rate
        if cur > worst:
            worst, at = cur, i
    out = []
    if (long_ := [i for i, n in sents if n > 35]):
        out.append(f"{len(long_)} câu nói > 35 tiếng (câu {sorted(set(long_))[:6]}) -- tách đôi")
    punch = sum(n <= 6 for _, n in sents)
    if sents and punch < len(sents) / 8:
        out.append(f"câu ngắn <= 6 tiếng: {punch}/{len(sents)} -- nên ~1 câu mỗi 4-6 câu (câu đỉnh, tách dòng)")
    if worst > 90:
        out.append(f"~{worst:.0f} giây liền không ngắt nhịp (tới câu {at}) -- chèn câu hỏi/con số/câu ngắn")
    return out


def probe_duration_s(path: Path) -> float | None:
    """Thời lượng giây nếu ffprobe đọc được và > 0. None khi file hỏng (thiếu moov, duration 0/âm/inf/nan, không phải số)."""
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    try:
        dur = float((proc.stdout or "").strip())
    except ValueError:
        return None
    if not math.isfinite(dur) or not (dur > 0):
        return None
    return dur


def _broken_trash_dir() -> Path:
    return Path.home() / ".Trash"


def quarantine_broken_mp4(path: Path) -> Path:
    """Chuyển mp4 hỏng vào ~/.Trash/ với hậu tố .broken_<giờ>. Không xoá."""
    trash = _broken_trash_dir()
    trash.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    dest = trash / f"{path.name}.broken_{stamp}"
    n = 2
    while dest.exists():
        dest = trash / f"{path.name}.broken_{stamp}_{n}"
        n += 1
    shutil.move(str(path), str(dest))
    return dest


def classify_mp4(path: Path) -> str:
    """'ok' nếu ffprobe đọc được duration > 0; 'missing' nếu không có file.
    'broken': đã chuyển vào Trash -- file dở không giữ tên thật."""
    if not path.is_file():
        return "missing"
    if probe_duration_s(path) is not None:
        return "ok"
    dest = quarantine_broken_mp4(path)
    print(f"    CẢNH BÁO: {path.name} hỏng (ffprobe không đọc được duration > 0) -- "
          f"chuyển vào {dest}, render lại", flush=True)
    return "broken"


def dest_free_bytes(path: Path) -> int:
    """Byte trống trên ổ chứa path. Path chưa có thì đi lên thư mục cha tới khi tồn tại."""
    target = path
    while not target.exists():
        parent = target.parent
        if parent == target:
            break
        target = parent
    return shutil.disk_usage(target).free


# mix_long ghi PCM_24 stereo 48 kHz (hf_foley / hf_sfx.SR). Ước khi mix.wav chưa có.
MIX_WAV_SR = 48000
MIX_WAV_CHANNELS = 2
MIX_WAV_BYTES_PER_SAMPLE = 3  # PCM_24
MIX_WAV_HEADER = 44


def mix_wav_expected_bytes(duration_s: float, mix: Path) -> int:
    """Byte mix.wav: cỡ file thật nếu đã có, không thì ước PCM_24 stereo 48 kHz."""
    if mix.is_file():
        return mix.stat().st_size
    n = max(0, int(float(duration_s) * MIX_WAV_SR))
    return MIX_WAV_HEADER + n * MIX_WAV_CHANNELS * MIX_WAV_BYTES_PER_SAMPLE


def disk_shortfall_message(expected_bytes: int, free_bytes: int) -> str | None:
    """None nếu còn >= 2 lần kích thước dự kiến (chương + mix.wav). Ngược lại câu lỗi, dừng trước khi ghép."""
    need = expected_bytes * 2
    if free_bytes >= need:
        return None
    free_gb = f"{free_bytes / (1024 ** 3):.2f}"
    need_gb = f"{need / (1024 ** 3):.2f}"
    return f"đĩa không đủ chỗ: còn {free_gb} GB, cần ~{need_gb} GB"


def newer_than_inputs(output: Path, inputs: list[Path]) -> bool:
    """True nếu output có mặt và mtime > mọi input đang có. Input vắng thì bỏ qua."""
    if not output.is_file():
        return False
    out_m = output.stat().st_mtime
    for p in inputs:
        if p.is_file() and p.stat().st_mtime >= out_m:
            return False
    return True


def done_mp4_count(out_dir: Path) -> int:
    """Số file .mp4 xong trong out/. Bỏ qua .part.mp4 (bản ghép dở)."""
    return sum(1 for p in out_dir.glob("*.mp4") if ".part." not in p.name)


def render_one(row: dict, out_dir: Path, quality: str, allow_lint_fail: bool = False) -> tuple[bool, str]:
    rid = row["id"]
    try:
        from library.tools.production_gates import hook_lint_issues, long_script_report
        if row.get("lane") == "long" and row.get("series") in ("fs", "bud"):
            gate_name = "long_script_lint"
            gate_issues, retention_warnings = long_script_report(row)
        elif row.get("series") in ("fs", "bud"):
            gate_name, gate_issues = "hook_lint", hook_lint_issues(row)
            retention_warnings = []
        else:
            gate_name, gate_issues = "hook_lint", []  # hook rules are scoped to FS/BUD shorts
            retention_warnings = []
    except Exception as exc:  # fail-closed: missing/broken gate is itself a finding
        gate_issues = [f"không chạy được cổng: {exc}"]
        gate_name = "long_script_lint" if row.get("lane") == "long" and row.get("series") in ("fs", "bud") else "hook_lint"
        retention_warnings = []
    if gate_issues:
        reason = f"{gate_name}: " + " | ".join(gate_issues)
        if not allow_lint_fail:
            return False, reason
        print(f"    CẢNH BÁO: --allow-lint-fail bỏ qua {reason}", flush=True)
    if row.get("lane") == "long":
        for w in reveal_issues(row):
            print(f"    !! sơ đồ: {w}", flush=True)
        for w in retention_warnings:
            print(f"    !! giữ chân: {w}", flush=True)
    if row.get("lane") == "long" and (row.get("ambience") or row.get("beats")):
        import hf_ambience  # noqa: PLC0415
        if (amb_bad := hf_ambience.issues(row)):
            return False, "lỗi ambience/beats: " + " | ".join(amb_bad[:3])
    if row.get("lane") == "long" and (style_bad := style_scene_issues(row)):
        return False, "bộ style bổ sung (#258): " + " | ".join(style_bad[:3])
    if row.get("lane") == "long" and (bare := bare_lines(row)):
        return False, (f"{len(bare)} câu trần (không sơ đồ/ảnh/chữ khoá) -- engine sẽ lấy chữ đầu câu làm tiêu đề: "
                       f"câu {bare[:12]} -- đánh **chữ khoá** hoặc gắn sơ đồ")
    if row.get("series") == "fs" and (bad := zodiac_naming_errors(row.get("script") or [])):
        return False, "gọi con giáp bằng tên con vật (phải dùng tên chi): " + " | ".join(bad[:3])
    if (bad_text := integrity_issues(row)):
        return False, "toàn vẹn văn bản: " + " | ".join(bad_text[:3])
    if (v2 := short_v2_issues(row)):
        return False, "công thức short v2: " + " | ".join(v2)
    if (tone := short_tone_issues(row)):
        return False, "hồn kênh: " + " | ".join(tone)
    for w in short_hook_hints(row):
        print(f"    !! neo short: {w}", flush=True)
    if (crowded := crowded_chi_lines(row.get("script") or [])):
        return False, "câu có >= 4 tên chi (TTS sẽ đọc lồng) -- tách câu: " + " | ".join(crowded[:3])
    mp4 = out_dir / f"{rid}.mp4"
    # Video theo chương: từng chương và file cuối tự quyết trong render_chapters.
    # File không đọc được thì classify_mp4 chuyển vào Trash rồi render lại -- không báo "đã có".
    if not row.get("chapters") and classify_mp4(mp4) == "ok":
        return True, "đã có"
    warn_missing_layout_policy(row, out_dir)
    warn_missing_style(row, out_dir)
    lines = row.get("script") or []
    if not lines or lines == PLACEHOLDER_SCRIPT:
        return True, "bỏ qua (không có kịch bản)"

    txt = out_dir / f"{rid}.txt"
    txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    wav = out_dir / f"{rid}.wav"

    # Kịch bản đổi mà wav cũ còn đó là cái bẫy im lặng: số câu vẫn bằng số
    # segment nên không có lỗi nào nổ ra, video ra đời với TIẾNG CŨ ghép vào
    # CHỮ MỚI. Ghim hash kịch bản cạnh wav để bắt việc đó.
    # _line_fingerprints chỉ là metadata kiểm khoá dòng, không đổi tiếng: bỏ khỏi hash để không đọc lại oan.
    tts_effective = row.get("tts")
    if row.get("beats") and tts_effective:
        import hf_ambience  # noqa: PLC0415
        tts_effective = hf_ambience.tts_with_beats(row) or tts_effective
    tts_for_hash = {k: v for k, v in (tts_effective or {}).items() if k != "_line_fingerprints"}
    if "voices" in row:
        tts_for_hash["voices"] = row["voices"]
    digest = hashlib.sha1(("\n".join(lines) + json.dumps(tts_for_hash, sort_keys=True)).encode("utf-8")).hexdigest()
    stamp = out_dir / f"{rid}.script.sha1"
    if wav.exists() and (not stamp.exists() or stamp.read_text(encoding="utf-8").strip() != digest):
        print(f"    kịch bản đã đổi kể từ lần TTS trước -- đọc lại", flush=True)
        wav.unlink(missing_ok=True)
    if not wav.exists() and row.get("tts"):
        # Video dài: TTS từng câu (hf_voice) -- giọng/tốc độ/khoảng nghỉ theo câu, giọng thứ hai cho lời trích / 2 giọng.
        tts_spec = dict(tts_effective or row["tts"])
        if "voices" in row and "voices" not in tts_spec:
            tts_spec["voices"] = row["voices"]
        side = out_dir / f"{rid}.tts.json"
        side.write_text(json.dumps(tts_spec, ensure_ascii=False), encoding="utf-8")
        proc = subprocess.run([str(VENV_PYTHON), "hf_voice.py", str(txt), str(side), str(wav)],
                              cwd=PROJECT_ROOT, capture_output=True, text=True)
        for qa_line in proc.stderr.splitlines():
            if qa_line.startswith("CẢNH BÁO QA"):
                print(f"    {qa_line}", flush=True)     # câu nghi lỗi sau mọi lần thử: báo, không im lặng
        if proc.returncode != 0 or not wav.exists():
            return False, f"TTS từng câu lỗi: {(proc.stdout + proc.stderr)[-300:]}"
    if not wav.exists() and not render_tts(txt, wav, lines, voice_for(row["series"])):
        return False, "TTS hỏng sau nhiều lần thử"
    stamp.write_text(digest + "\n", encoding="utf-8")

    bgm, gain = pick_bgm(row, wav)
    if row.get("chapters"):
        return render_chapters(row, out_dir, quality, txt, wav, bgm)
    layout_chosen = None
    if row.get("lane") == "long" and wav.with_suffix(".json").is_file():
        segs = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))["segments"]
        rep, bad = pacing(row, segs)
        print(f"    nhịp hình: {rep}", flush=True)
        for x in bad:
            print(f"    !! nhịp hình: {x}", flush=True)
        layout_chosen = layout_v2_choices(row, segs)
        if bad and (row.get("pacing") == "strict" or any(x.startswith("120s đầu:") for x in bad)):
            return False, "nhịp hình chưa đạt: " + "; ".join(bad)
    elif row.get("layout_policy") == "v2":
        layout_chosen = layout_v2_choices(row, None)
    if layout_chosen is not None:
        import hyperframes_bridge as HB  # noqa: PLC0415
        print("    " + HB.layout_report(layout_chosen, row.get("media") or {}), flush=True)
    cmd = [sys.executable, "hyperframes_bridge.py",
           "--script", str(txt), "--wav", str(wav), "--series", row["series"],
           "--style", row["style"], "--badge", row.get("badge", ""),
           "--footer", FOOTER[row["series"]], "--bgm", bgm, "--bgm-gain", str(gain),
           "--output", str(mp4), "--quality", quality]
    if row.get("lane"):
        cmd += ["--lane", row["lane"]]
    if row.get("kicker"):
        cmd += ["--kicker", row["kicker"]]
    # Figure và media do plan ghi sẵn -- runner chỉ chuyển tiếp nguyên vẹn,
    # không tự quyết định gì (ADR-0001).
    for key, flag in (("figures", "--figures"), ("figure_labels", "--figure-labels"),
                      ("media", "--media"), ("visuals", "--visuals")):
        if row.get(key):
            side = out_dir / f"{rid}.{key}.json"
            side.write_text(json.dumps(row[key], ensure_ascii=False), encoding="utf-8")
            cmd += [flag, str(side)]

    # Phase D (tiếng động bám cảnh, phụ đề cụm chữ, kết vòng lặp, câu hỏi lặng).
    opts = {k: row[k] for k in ("caps", "subs", "loop", "silence", "sfx", "sfx_gain", "sound", "kinetic", "wordts", "theme") if k in row}
    if layout_chosen is not None:
        opts = layout_v2_opts(opts, row, layout_chosen)
    if opts:
        side = out_dir / f"{rid}.opts.json"
        side.write_text(json.dumps(opts, ensure_ascii=False), encoding="utf-8")
        cmd += ["--opts", str(side)]

    # Video dài: HyperFrames nhiều worker mặc định ghi TỪNG khung hình ra đĩa rồi
    # mới mã hoá -- 5 phút cần hơn 8 GB tạm, đĩa gần đầy là hỏng (L_bud_03,
    # 29/09/2026). Bật luồng thẳng vào bộ mã hoá: không tốn đĩa, và nhanh hơn
    # (4,5 phút so với ~10 phút cho cùng video).
    env = dict(os.environ)
    if row.get("lane") == "long":
        env.setdefault("HF_CAPTURE_PARALLEL_STREAM", "true")
    proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        return False, f"render lỗi: {(proc.stdout + proc.stderr)[-300:]}"

    # Ghi công nguồn ảnh chỉ tồn tại trong kết quả của bridge. Không giữ lại
    # thì lúc soạn mô tả video phải dựng lại từ đầu -- mà dựng lại nghĩa là
    # viết lần thứ hai cùng một logic, rồi hai bản lệch nhau.
    for line in reversed((proc.stdout or "").strip().splitlines()):
        if line.startswith("{"):
            try:
                (out_dir / f"{rid}.render.json").write_text(line + "\n", encoding="utf-8")
            except OSError:
                pass
            break
    return True, "xong"


FPS = 30


def _engine_sig() -> str:
    """Băm mã dựng hình: sửa engine/longform/CSS/style thì mọi chương render lại (không đoán tay)."""
    comp = PROJECT_ROOT / "hyperframes_short" / "compositions"
    h = hashlib.sha1()
    st = PROJECT_ROOT / "hyperframes_short" / "studio"      # skin studio_long + visual "studio" dùng engine Shorts Studio
    for f in (sorted(comp.glob("*.js")) + sorted(comp.glob("*.css")) + sorted(comp.glob("*_long.html"))
              + sorted(st.glob("*.js")) + sorted(st.glob("*.css")) + sorted((st / "devices").glob("*.js")) + sorted((st / "themes").glob("*.json"))):
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def _remap_at(spec, shift: int):
    """Đổi số câu tuyệt đối (at/until) trong một sơ đồ sang số câu trong chương."""
    if isinstance(spec, dict):
        return {k: (v - shift if k in ("at", "until") and isinstance(v, int) else _remap_at(v, shift)) for k, v in spec.items()}
    if isinstance(spec, list):
        return [_remap_at(x, shift) for x in spec]
    return spec


def chapter_spans(lines: list[str], segs: list[dict], total: float) -> list[tuple[int, int, float, float]]:
    """[(câu đầu, câu sau cuối, giây đầu, giây cuối)] -- cắt ở tiêu đề chương (câu in đậm trọn câu),
    mốc cắt nằm giữa khoảng lặng trước tiêu đề và ĐÚNG khung hình (1/30 s) để nối không lệch tiếng."""
    heads = [i for i, l in enumerate(lines) if i and l.startswith("**") and l.endswith("**") and l.count("**") == 2]
    firsts = [0] + heads
    out = []
    for c, a in enumerate(firsts):
        b = firsts[c + 1] if c + 1 < len(firsts) else len(lines)
        t0 = 0.0 if a == 0 else round((segs[a - 1]["end"] + segs[a]["start"]) / 2 * FPS) / FPS
        t1 = (round((segs[b - 1]["end"] + segs[b]["start"]) / 2 * FPS) / FPS) if b < len(lines) else int(total * FPS) / FPS
        out.append((a, b, t0, t1))
    return out


# Nhãn báo cáo nhịp hình theo loại media (resolve_media mặc định kind "video" = stock), để đo tỉ lệ
# tư liệu thật / stock / ảnh AI. Kind lạ vẫn gộp "ảnh/clip".
MEDIA_LABEL = {**dict.fromkeys(("commons", "museum", "ext", "openverse", "pdvideo"), "tư liệu"),
               **dict.fromkeys(("image", "video"), "stock"), "local": "ảnh AI", "asset": "sơ đồ vẽ sẵn"}
PHOTO_LABELS = ("ảnh/clip", *sorted(set(MEDIA_LABEL.values())))


def media_label(m: dict | None) -> str:
    return MEDIA_LABEL.get(((m or {}).get("kind") or "video").lower(), "ảnh/clip")


# Sàn loại cảnh, ý từ floor.py của V2 (sàn 14 loại; chữ không ảnh không b-roll ≤ 12%).
# Chỉ cảnh báo: chuỗi này KHÔNG vào `bad`, nên pacing=="strict" không chặn render.
_FLOOR_MIN_TYPES = 14
_FLOOR_MAX_NAKED = 0.12
# Chữ trên nền trống: thẻ chữ khoá, và sơ đồ thuần chữ (không ảnh, không clip).
_NAKED_KINDS = {"chữ khoá", "card", "quote", "ask", "word", "stamp", "stat", "endcard", "teaser"}
# Ảnh/tư liệu mỗi lần một hình khác: không tính là "3 cảnh cùng loại".
_RUN_OK = {*PHOTO_LABELS, "chương", "photo", "museum", "napam", "doc", "relic"}

# Cổng nhịp cắt 120s đầu (010): mọi cảnh <= 4.0s, chữ trên nền trống liên tục <= 1.5s.
# Cờ plan `pace_gate: off` để tắt cho Long cũ. Sau 120s giữ luật cũ.
PACE_GATE_S = 120.0
PACE_GATE_MAX_SHOT = 4.0
PACE_GATE_MAX_NAKED = 1.5


def _pace_gate_on(row: dict) -> bool:
    v = row.get("pace_gate")
    if v is False:
        return False
    return str(v or "on").strip().lower() not in ("off", "false", "0", "none")


def _plan_line_kind(i: int, ln: dict, lines: list[dict], media: dict, owner: dict | None = None) -> str:
    """Loại cảnh theo khai báo trong plan (card/word không có ảnh/clip nền).
    Hỗ trợ overlay: true cho ask/timeline/stat/list phủ lên ảnh đang chạy (Task 026)."""
    import hyperframes_bridge as HB  # noqa: PLC0415
    if ln.get("heading"):
        return "chương"
    owner = owner or {}
    has_media = str(i + 1) in media or (i + 1) in media or i in owner
    vspec = ln.get("visual") or (lines[ln["visual_cont"] - 1].get("visual") if ln.get("visual_cont") else None)
    if vspec:
        if HB.is_overlay_visual(vspec) and has_media:
            oid = str(owner[i] + 1) if i in owner else (str(i + 1) if (str(i + 1) in media or (i + 1) in media) else i + 1)
            return media_label(media.get(oid))
        return vspec.get("type", "visual")
    if has_media:
        oid = str(owner[i] + 1) if i in owner else (str(i + 1) if (str(i + 1) in media or (i + 1) in media) else i + 1)
        return media_label(media.get(oid))
    if (ln.get("figure") or {}).get("type", "none") != "none":
        return "figure"
    return "chữ khoá"


def _pan_stop_lines(media: dict) -> set[int]:
    """Câu là điểm dừng `pan` (không tính câu mang ảnh): máy lia sang khung mới ở đó, cổng nhịp tính như một lần cắt."""
    out: set[int] = set()
    for key, m in (media or {}).items():
        pan = m.get("pan") if isinstance(m, dict) else None
        for st in (pan or {}).get("stops") or []:
            if isinstance(st, dict) and st.get("line") and int(st["line"]) != int(key):
                out.add(int(st["line"]))
    return out


def pace_gate_issues(row: dict, segs: list[dict]) -> list[str]:
    """Cổng nhịp cắt 120s đầu: MỌI cảnh <= 4,0s và chữ trên nền trống liên tục <= 1,5s (mức ERROR)."""
    if not _pace_gate_on(row):
        return []
    import hyperframes_bridge as HB  # noqa: PLC0415
    script, n = row["script"], len(row["script"])
    lines = [{"sentence_id": i + 1, "start": segs[i]["start"], "end": segs[i]["end"], "words": [],
              "heading": script[i].startswith("**") and script[i].endswith("**") and script[i].count("**") == 2} for i in range(n)]
    media = row.get("media") or {}
    HB.apply_visuals(lines, row.get("visuals") or {}, media)
    holds = HB.media_holds(lines, {int(k) for k in media})
    owner = {k: i for i, j in holds.items() for k in range(i + 1, j + 1)}
    pan_cuts = _pan_stop_lines(media)
    shots, shot_kinds, starts, prev, cur, t_first = [], [], [], None, 0.0, 0.0
    for i, ln in enumerate(lines):
        d = (segs[i + 1]["start"] if i + 1 < n else segs[i]["end"]) - ln["start"]
        k = _plan_line_kind(i, ln, lines, media, owner)
        is_cont = bool(ln.get("visual_cont") or (i in owner and (owner[i] == i - 1 or owner[i] == owner.get(i - 1))))
        if i in owner and ln["sentence_id"] in pan_cuts:
            is_cont = False   # điểm dừng pan = máy đổi khung (028), tính là nhịp cắt
        if not is_cont or k != prev:
            if prev is not None:
                shots.append(cur)
                shot_kinds.append(prev)
                starts.append(t_first)
            cur, t_first = 0.0, ln["start"]
        cur += d
        prev = k
    if prev is not None:
        shots.append(cur)
        shot_kinds.append(prev)
        starts.append(t_first)
    errs = []
    for sec_len, k, t0 in zip(shots, shot_kinds, starts):
        if t0 < PACE_GATE_S and sec_len > PACE_GATE_MAX_SHOT + 1e-6:
            sid = next(ln["sentence_id"] for ln in lines if ln["start"] >= t0 - 1e-6)
            errs.append(f"120s đầu: cảnh '{k}' dài {sec_len:.1f}s từ câu {sid} (> {PACE_GATE_MAX_SHOT:.1f}s)")
    naked_run, naked_sid = 0.0, None
    for i, ln in enumerate(lines):
        if ln["start"] >= PACE_GATE_S:
            break
        d = (segs[i + 1]["start"] if i + 1 < n else segs[i]["end"]) - ln["start"]
        pk = _plan_line_kind(i, ln, lines, media, owner)
        if pk in _NAKED_KINDS:
            if naked_sid is None:
                naked_sid = ln["sentence_id"]
            naked_run += d
        else:
            if naked_run > PACE_GATE_MAX_NAKED + 1e-6:
                errs.append(f"120s đầu: chữ trên nền trống {naked_run:.1f}s liên tục từ câu {naked_sid} (> {PACE_GATE_MAX_NAKED:.1f}s)")
            naked_run, naked_sid = 0.0, None
    if naked_run > PACE_GATE_MAX_NAKED + 1e-6:
        errs.append(f"120s đầu: chữ trên nền trống {naked_run:.1f}s liên tục từ câu {naked_sid} (> {PACE_GATE_MAX_NAKED:.1f}s)")
    # Áp lại luật chữ khoá > 15% cho 120s đầu kể cả khi kinetic: true (Task 026)
    tot_120 = sum((segs[i + 1]["start"] if i + 1 < n else segs[i]["end"]) - ln["start"]
                  for i, ln in enumerate(lines) if ln["start"] < PACE_GATE_S)
    ck_120 = sum((segs[i + 1]["start"] if i + 1 < n else segs[i]["end"]) - ln["start"]
                 for i, ln in enumerate(lines)
                 if ln["start"] < PACE_GATE_S and _plan_line_kind(i, ln, lines, media, owner) == "chữ khoá")
    ck_share_120 = (ck_120 / tot_120) if tot_120 > 0 else 0.0
    if ck_share_120 > 0.15 + 1e-6:
        errs.append(f"120s đầu: chữ khoá {ck_share_120 * 100:.0f}% (> 15%) -- kinetic không miễn trừ 120s đầu, cần thêm hình")
    return errs


def floor_warnings(shot_kinds: list[str], share: dict[str, float]) -> list[str]:
    """Sàn cảnh: dưới 14 loại; chữ trên nền trống quá 12%; 3 cảnh liền cùng loại. Chỉ cảnh báo."""
    n_types = len({k for k in shot_kinds if k != "chương"})
    naked = sum(share.get(k, 0.0) for k in _NAKED_KINDS)
    out = []
    if n_types < _FLOOR_MIN_TYPES:
        out.append(f"chỉ {n_types} loại cảnh, sàn {_FLOOR_MIN_TYPES} (cảnh báo, không chặn)")
    if naked > _FLOOR_MAX_NAKED:
        out.append(f"chữ trên nền trống {naked * 100:.0f}% (trần {_FLOOR_MAX_NAKED:.0%}; cảnh báo, không chặn)")
    run, hits = 1, []
    for i in range(1, len(shot_kinds)):
        if shot_kinds[i] == shot_kinds[i - 1] and shot_kinds[i] not in _RUN_OK:
            run += 1
            if run == 3:
                hits.append(f"3 cảnh liền cùng loại '{shot_kinds[i]}' (cảnh {i - 1}-{i + 1})")
        else:
            run = 1
    if len(hits) > 6:
        out.extend(hits[:6])
        out.append(f"còn {len(hits) - 6} chỗ 3 cảnh liền cùng loại")
    else:
        out.extend(hits)
    return out


def pacing(row: dict, segs: list[dict]) -> tuple[dict, list[str]]:
    """Nhịp hình (SS-tier): % thời lượng theo kiểu cảnh, độ dài cảnh. Ngưỡng rút từ đo F1/B1 01/10/2026
    (68% ba sơ đồ lặp khuôn; 35% chữ khoá trên nền trơn; cảnh đứng 64 giây).
    `rep["sàn"]` là cảnh báo sàn (14 loại, chữ nền trống ≤ 12%, 3 cảnh liền) — không nằm trong danh sách chặn."""
    import collections  # noqa: PLC0415
    import hyperframes_bridge as HB  # noqa: PLC0415
    script, n = row["script"], len(row["script"])
    lines = [{"sentence_id": i + 1, "start": segs[i]["start"], "end": segs[i]["end"], "words": [],
              "heading": script[i].startswith("**") and script[i].endswith("**") and script[i].count("**") == 2} for i in range(n)]
    media = row.get("media") or {}
    HB.apply_visuals(lines, row.get("visuals") or {}, media)
    holds = HB.media_holds(lines, {int(k) for k in media})
    owner = {k: i for i, j in holds.items() for k in range(i + 1, j + 1)}   # dòng ảnh còn hiện -> dòng mang ảnh
    sec, shots, shot_kinds, prev, cur = collections.Counter(), [], [], None, 0.0
    starts, t_first = [], 0.0             # giây bắt đầu của từng cảnh
    for i, ln in enumerate(lines):
        d = (segs[i + 1]["start"] if i + 1 < n else segs[i]["end"]) - ln["start"]
        k = _plan_line_kind(i, ln, lines, media, owner)
        sec[k] += d
        is_cont = bool(ln.get("visual_cont") or (i in owner and (owner[i] == i - 1 or owner[i] == owner.get(i - 1))))
        if not is_cont or k != prev:
            if prev is not None:
                shots.append(cur)
                shot_kinds.append(prev)
                starts.append(t_first)
            cur, t_first = 0.0, ln["start"]
        cur += d
        prev = k
    shots.append(cur)
    if prev is not None:
        shot_kinds.append(prev)
        starts.append(t_first)
    tot = sum(sec.values()) or 1
    edge = tempo_edges(shots, starts, tot)
    share = {k: v / tot for k, v in sec.items()}
    san = floor_warnings(shot_kinds, share)
    rep = {"phút": round(tot / 60, 1), "cảnh": len(shots), "TB giây/cảnh": round(tot / len(shots), 1),
           "dài nhất": round(max(shots), 1), "loại cảnh": len({k for k in shot_kinds if k != "chương"}),
           "chữ nền trống": round(sum(share.get(k, 0.0) for k in _NAKED_KINDS) * 100, 1),
           "p50 giây": _pct(shots, 50), "p90 giây": _pct(shots, 90), **edge["rep"],
           "tỉ lệ": {k: round(v * 100, 1) for k, v in sorted(share.items(), key=lambda x: -x[1])},
           "sàn": san + edge["warn"]}
    # Cảnh mang ẢNH khác nhau (bảo tàng, nạp âm, tư liệu) không phải "lặp khuôn" -- mỗi lần một hình mới.
    bad = [f"{k} chiếm {v * 100:.0f}% (> 25%)" for k, v in share.items()
           if v > .25 and k not in (*PHOTO_LABELS, "museum", "napam", "doc", "photo", "relic")]
    if share.get("chữ khoá", 0) > .15 and not row.get("kinetic"):
        bad.append(f"chữ khoá đứng yên {share['chữ khoá'] * 100:.0f}% (> 15%) -- bật \"kinetic\" hoặc thêm hình")
    # Ticket 65: cảnh giữ > 25 giây chỉ được khi plan ghi lý do (`slow_hold`: {câu đầu cảnh: "lý do"}).
    reasons = {int(k): v for k, v in (row.get("slow_hold") or {}).items()}
    for sec_len, t0 in zip(shots, starts):
        if sec_len > 25:
            sid = next(ln["sentence_id"] for ln in lines if ln["start"] >= t0 - 1e-6)
            if sid not in reasons:
                bad.append(f"cảnh đứng {sec_len:.0f}s từ câu {sid} (> 25s) -- chèn nhịp cắt, "
                           f"hoặc ghi lý do: \"slow_hold\": {{\"{sid}\": \"...\"}}")
    bad.extend(pace_gate_issues(row, segs))
    o_errs, o_warns = opening_gate(row, segs)
    bad.extend(o_errs)
    san.extend(o_warns)
    return rep, bad



# ==============================================================================
# CỔNG MỞ ĐẦU 40S (OPENING GATE - TASK 026 THEO BÁO CÁO 025)
# O1: câu 1 có hình (không thẻ chương/thẻ chữ ở giây 0) [ERROR]
# O2: 0–40 s không chữ-trên-nền-trống > 1,5 s [ERROR]
# O3: ≥ 8 hình khác nhau trong 0–40 s [ERROR]
# O4: từ khoá chính của title được nói trước giây 15 [WARN]
# O5: cấm ảnh ref nhân vật (/refs/, REF_) làm hình [ERROR]
# O6: cảnh báo lời meta ("video này", "chương N", "đăng ký") trong 0–40 s [WARN]
# O7: câu hỏi hẹn/lộ trình không nằm trong 0–40 s [WARN]
# O8: xuất tờ khung 0–40 s (1 khung/2 s) ra output/cl_staging/long/review_<id>/first40.jpg.
# ==============================================================================

OPENING_GATE_S = 40.0
OPENING_GATE_MAX_NAKED = 1.5
OPENING_GATE_MIN_IMAGES = 8
OPENING_GATE_MAX_SOLID_S = 0.3
OPENING_GATE_SOLID_STD_THRESH = 20.0

_META_PHRASES = (
    "video này", "clip này", "kênh này", "hồ sơ này", "đăng ký", "subscribe",
    "trước hết", "cảnh vừa rồi", "chúng ta sẽ"
)
_META_CHAP_RE = re.compile(r"\bchương\s+(\d+|[0-9]+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\b", re.IGNORECASE)
_ROADMAP_RE = re.compile(r"\bchương\s+\w+\s+(sẽ|chúng ta|nói về|tìm hiểu|giải mã)\b", re.IGNORECASE)
_ROADMAP_PHRASES = ("ở phần sau", "lộ trình của video", "lộ trình")

_STOP_TITLE_WORDS = {
    "vì", "sao", "để", "không", "phải", "cho", "của", "và", "ở", "trong", "là", "ai", "gì", "nào",
    "được", "bị", "bảo", "đi", "xin", "vẫn", "chưa", "đêm", "về", "các", "những", "phim", "trọn",
    "bộ", "tích", "truyện", "pháp", "cú", "video", "tập"
}

_NUM_WORD_VARIANTS = {
    "12": ["12", "mười hai"],
    "16": ["16", "mười sáu"],
    "2027": ["2027", "hai nghìn không trăm hai mươi bảy", "hai không hai bảy"],
    "25": ["25", "hai mươi lăm", "hai lăm"],
    "4": ["4", "bốn"],
}


def _opening_gate_on(row: dict) -> bool:
    v = row.get("opening_gate")
    if v is False:
        return False
    return str(v or "on").strip().lower() not in ("off", "false", "0", "none")


def _clean_vi_text(s: str) -> str:
    s = s.lower().replace("**", " ")
    s = re.sub(r"[^\w\s]", " ", s)
    return " ".join(s.split())


def _check_meta_text(text: str) -> str | None:
    t_clean = text.lower()
    for p in _META_PHRASES:
        if p in t_clean:
            return p
    m = _META_CHAP_RE.search(t_clean)
    if m:
        return m.group(0)
    return None


def _check_roadmap_text(text: str) -> str | None:
    t_clean = text.lower()
    for p in _ROADMAP_PHRASES:
        if p in t_clean:
            return p
    m = _ROADMAP_RE.search(t_clean)
    if m:
        return m.group(0)
    return None


def _check_ref_asset(spec: dict | str) -> str | None:
    if isinstance(spec, str):
        if "/refs/" in spec.lower() or "ref_" in spec.upper():
            return spec
        return None
    if isinstance(spec, dict):
        for field in ("path", "src", "ref", "name"):
            val = str(spec.get(field) or "")
            if "/refs/" in val.lower() or "ref_" in val.upper():
                return val
    return None


def _extract_title_candidates(title: str, thumb_text: str = "") -> list[str]:
    cands = []
    if thumb_text:
        cands.extend([_clean_vi_text(w) for w in re.split(r"[|\n,]", thumb_text) if len(w.strip()) > 2])
    parts = re.split(r"[|:–\-\?]", title)
    for p in parts:
        cleaned = _clean_vi_text(p)
        words = cleaned.split()
        for num, variants in _NUM_WORD_VARIANTS.items():
            if num in words:
                cands.extend(variants)
        for i in range(len(words)):
            w = words[i]
            if w not in _STOP_TITLE_WORDS and len(w) > 2:
                cands.append(w)
            if i + 1 < len(words):
                bigram = f"{words[i]} {words[i+1]}"
                if words[i] not in _STOP_TITLE_WORDS or words[i+1] not in _STOP_TITLE_WORDS:
                    cands.append(bigram)
            if i + 2 < len(words):
                trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
                cands.append(trigram)
    cands = [c for c in cands if c and c not in _STOP_TITLE_WORDS and len(c) > 2]
    return sorted(list(set(cands)), key=lambda x: -len(x))


def _match_title_keywords(title: str, thumb_text: str, spoken_15_clean: str) -> bool:
    if not title:
        return True
    cands = _extract_title_candidates(title, thumb_text)
    if not cands:
        return True
    for c in cands:
        if f" {c} " in f" {spoken_15_clean} " or c == spoken_15_clean:
            return True
    return False


def _get_title_keywords_sample(title: str, thumb_text: str) -> str:
    cands = _extract_title_candidates(title, thumb_text)
    return ", ".join(f"\x27{c}\x27" for c in cands[:3]) if cands else title[:30]


def _build_lines_for_gate(row: dict, segs: list[dict] | None = None) -> tuple[list[dict], list[dict], dict, dict]:
    import hyperframes_bridge as HB  # noqa: PLC0415
    script = row.get("script") or []
    n = len(script)
    if segs is None or len(segs) < n:
        rid = row.get("id")
        out_json = Path("output/cl_staging/long/out") / f"{rid}.json"
        if rid and out_json.exists():
            try:
                segs = json.load(out_json.open(encoding="utf-8")).get("segments", [])
            except Exception:
                segs = []
        if not segs or len(segs) < n:
            segs = []
            t = 0.0
            for s in script:
                wc = len(s.replace("**", "").split())
                d = max(1.0, wc / 185.0 * 60.0)
                segs.append({"start": round(t, 3), "end": round(t + d, 3)})
                t += d + 0.5
    n = min(n, len(segs))
    lines = [{"sentence_id": i + 1, "start": segs[i]["start"], "end": segs[i]["end"], "words": [],
              "heading": script[i].startswith("**") and script[i].endswith("**") and script[i].count("**") == 2}
             for i in range(n)]
    media = row.get("media") or {}
    visuals = row.get("visuals") or {}
    try:
        HB.apply_visuals(lines, visuals, media)
    except Exception:
        pass
    holds = HB.media_holds(lines, {int(k) for k in media if str(k).isdigit()})
    owner = {k: i for i, j in holds.items() for k in range(i + 1, j + 1)}
    return lines, segs[:n], media, owner


def check_opening_solid_frames(video_path: Path | str, max_sec: float = OPENING_GATE_S,
                               fps: int = 10, std_thresh: float = OPENING_GATE_SOLID_STD_THRESH,
                               max_dur: float = OPENING_GATE_MAX_SOLID_S,
                               theme: str | None = None,
                               theme_ref_path: Path | str | None = None) -> list[dict]:
    """O9: Quét video mp4 trong 0–max_sec, phát hiện mọi chuỗi khung vi phạm:
    (1) Khung đồng màu (std < std_thresh), HOẶC
    (2) Khung giống nền theme trống (pearson correlation > 0.90), HOẶC
    (3) Khung có độ chi tiết thấp (Laplacian variance) trên >= 70% diện tích;
    kéo dài liên tục > max_dur (> 0.3s)."""
    import subprocess
    import numpy as np
    from PIL import Image

    vp = Path(video_path)
    if not vp.exists():
        return []

    ref_arr = None
    if theme_ref_path and Path(theme_ref_path).exists():
        try:
            im = Image.open(theme_ref_path).resize((320, 180)).convert("RGB")
            ref_arr = np.array(im, dtype=np.float32)
        except Exception:
            ref_arr = None
    if ref_arr is None:
        th_name = theme or "saffron"
        cands = [
            Path(f"hyperframes_short/studio/themes/blank_{th_name}.png"),
            Path(__file__).parent / f"hyperframes_short/studio/themes/blank_{th_name}.png",
            Path(f"output/cl_staging/grok/render_029/frames/f_04_4s.png") if th_name == "saffron" else None,
        ]
        for c in cands:
            if c and c.exists():
                try:
                    im = Image.open(c).resize((320, 180)).convert("RGB")
                    ref_arr = np.array(im, dtype=np.float32)
                    break
                except Exception:
                    continue
    if ref_arr is None:
        th_json_paths = [
            Path(f"hyperframes_short/studio/themes/{theme or 'saffron'}.json"),
            Path(__file__).parent / f"hyperframes_short/studio/themes/{theme or 'saffron'}.json",
        ]
        ground_rgb = [236, 230, 216]
        for jp in th_json_paths:
            if jp.exists():
                try:
                    import json as _json
                    dat = _json.loads(jp.read_text(encoding="utf-8"))
                    g_hex = dat.get("vars", {}).get("ground", "").lstrip("#")
                    if len(g_hex) == 6:
                        ground_rgb = [int(g_hex[i:i+2], 16) for i in (0, 2, 4)]
                        break
                except Exception:
                    pass
        ref_arr = np.zeros((180, 320, 3), dtype=np.float32)
        ref_arr[:, :] = ground_rgb

    def _pearson_sim(a: np.ndarray, b: np.ndarray) -> float:
        a_c = a.astype(np.float32) - np.mean(a)
        b_c = b.astype(np.float32) - np.mean(b)
        den = float(np.linalg.norm(a_c) * np.linalg.norm(b_c))
        return float(np.dot(a_c.flatten(), b_c.flatten()) / den) if den > 0 else 0.0

    def _low_detail_ratio(arr: np.ndarray, patch_size: int = 16, var_thresh: float = 55.0) -> float:
        gray = np.mean(arr, axis=2).astype(np.float32)
        top = gray[:-2, 1:-1]
        bottom = gray[2:, 1:-1]
        left = gray[1:-1, :-2]
        right = gray[1:-1, 2:]
        center = gray[1:-1, 1:-1]
        lap = top + bottom + left + right - 4.0 * center
        H, W = lap.shape
        bh, bw = patch_size, patch_size
        n_h, n_w = H // bh, W // bw
        if n_h == 0 or n_w == 0:
            return 0.0
        low_cnt = 0
        total = n_h * n_w
        for r in range(n_h):
            for c in range(n_w):
                patch = lap[r*bh:(r+1)*bh, c*bw:(c+1)*bw]
                if float(np.var(patch)) < var_thresh:
                    low_cnt += 1
        return float(low_cnt) / float(total)

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(vp),
        "-t", str(max_sec),
        "-vf", f"fps={fps},scale=320:180",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        w, h = 320, 180
        bytes_per_frame = w * h * 3
        idx = 0
        runs = []
        current_run = []
        while True:
            raw = proc.stdout.read(bytes_per_frame)
            if len(raw) < bytes_per_frame:
                break
            arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w, 3))
            std = float(np.std(arr))
            mean = np.mean(arr, axis=(0, 1))
            sec = idx / float(fps)
            is_solid = (std < std_thresh)
            psim = _pearson_sim(arr, ref_arr) if ref_arr is not None else 0.0
            is_theme_match = (psim > 0.90)
            ldr = _low_detail_ratio(arr, patch_size=16, var_thresh=55.0)
            is_low_detail = (ldr >= 0.70)
            is_blank = is_solid or is_theme_match or is_low_detail
            if is_blank:
                current_run.append((idx, sec, std, mean, psim, ldr))
            else:
                if current_run:
                    runs.append(current_run)
                    current_run = []
            idx += 1
        if current_run:
            runs.append(current_run)
        proc.wait()

        violations = []
        for r in runs:
            dur = len(r) / float(fps)
            if dur > max_dur + 1e-6:
                start_sec = r[0][1]
                end_sec = r[-1][1]
                avg_std = float(np.mean([x[2] for x in r]))
                avg_mean = np.mean([x[3] for x in r], axis=0).astype(int).tolist()
                avg_sim = float(np.mean([x[4] for x in r]))
                avg_ldr = float(np.mean([x[5] for x in r]))
                violations.append({
                    "start": start_sec,
                    "end": end_sec,
                    "dur": dur,
                    "std": avg_std,
                    "mean": avg_mean,
                    "sim": avg_sim,
                    "low_detail_ratio": avg_ldr,
                    "frames": len(r),
                })
        return violations
    except Exception:
        return []


def opening_gate(row: dict, segs: list[dict] | None = None, video_path: Path | str | None = None) -> tuple[list[str], list[str]]:
    """Cổng mở đầu 40s (Task 026, theo báo cáo 025):
    O1: câu 1 có hình (không thẻ chương/thẻ chữ ở giây 0) [ERROR]
    O2: 0–40 s không chữ-trên-nền-trống > 1,5 s [ERROR]
    O3: ≥ 8 hình khác nhau trong 0–40 s [ERROR]
    O4: từ khoá chính của title được nói trước giây 15 [WARN]
    O5: cấm ảnh ref nhân vật (/refs/, REF_) làm hình [ERROR]
    O6: cảnh báo lời meta (\"video này\", \"chương N\", \"đăng ký\") trong 0–40 s [WARN]
    O7: câu hỏi hẹn/lộ trình không nằm trong 0–40 s [WARN]
    O8: xuất tờ khung 0–40 s (1 khung/2 s) ra output/cl_staging/long/review_<id>/first40.jpg.
    O9: không khung đồng màu > 0,3 s trong 0–40 s của mp4 đã render [ERROR]
    """
    if not _opening_gate_on(row):
        return [], []

    import hyperframes_bridge as HB  # noqa: PLC0415
    script = row.get("script") or []
    if not script:
        return ["O1: plan không có kịch bản"], []

    lines, segs, media, owner = _build_lines_for_gate(row, segs)
    n = len(lines)
    errs, warns = [], []

    # O1: câu 1 có hình (không thẻ chương/thẻ chữ ở giây 0)
    has_media_1 = "1" in media or 1 in media
    is_heading_1 = lines[0]["heading"]
    vspec_1 = lines[0].get("visual")
    is_naked_visual_1 = bool(vspec_1 and not HB.is_overlay_visual(vspec_1))
    if not has_media_1:
        if is_heading_1:
            errs.append("O1: câu 1 (giây 0) là thẻ chương -- mở đầu phải bằng hình, không thẻ chương ở giây 0")
        elif is_naked_visual_1:
            errs.append(f"O1: câu 1 (giây 0) là thẻ chữ \x27{vspec_1.get('type')}\x27 trên nền trống -- mở đầu phải bằng hình")
        else:
            errs.append("O1: câu 1 (giây 0) không có hình -- mở đầu phải có hình ảnh/clip, không thẻ chương/thẻ chữ ở giây 0")
    elif is_heading_1:
        errs.append("O1: câu 1 (giây 0) là thẻ chương -- mở đầu phải bằng hình")
    elif is_naked_visual_1:
        errs.append(f"O1: câu 1 (giây 0) có thẻ chữ \x27{vspec_1.get('type')}\x27 trên nền trống")

    # O2: 0–40 s không chữ-trên-nền-trống > 1,5 s
    naked_run, naked_sid = 0.0, None
    for i, ln in enumerate(lines):
        if ln["start"] >= OPENING_GATE_S:
            break
        t_next = segs[i + 1]["start"] if i + 1 < n else segs[i]["end"]
        d = max(0.0, min(OPENING_GATE_S, t_next) - ln["start"])
        pk = _plan_line_kind(i, ln, lines, media, owner)
        if pk in _NAKED_KINDS:
            if naked_sid is None:
                naked_sid = ln["sentence_id"]
            naked_run += d
        else:
            if naked_run > OPENING_GATE_MAX_NAKED + 1e-6:
                errs.append(f"O2: 0–40s có chữ trên nền trống {naked_run:.1f}s liên tục từ câu {naked_sid} (> {OPENING_GATE_MAX_NAKED:.1f}s)")
            naked_run, naked_sid = 0.0, None
    if naked_run > OPENING_GATE_MAX_NAKED + 1e-6:
        errs.append(f"O2: 0–40s có chữ trên nền trống {naked_run:.1f}s liên tục từ câu {naked_sid} (> {OPENING_GATE_MAX_NAKED:.1f}s)")

    # O3: ≥ 8 hình khác nhau trong 0–40 s
    unique_images = set()
    for i, ln in enumerate(lines):
        if ln["start"] >= OPENING_GATE_S:
            break
        sid = ln["sentence_id"]
        m = media.get(str(sid)) or media.get(sid)
        if m:
            if isinstance(m, dict):
                sig = m.get("path") or m.get("src") or m.get("ref") or m.get("query") or m.get("prompt") or str(m)
            else:
                sig = str(m)
            unique_images.add(sig)
    if len(unique_images) < OPENING_GATE_MIN_IMAGES:
        errs.append(f"O3: 0–40s chỉ có {len(unique_images)} hình khác nhau (yêu cầu ≥ {OPENING_GATE_MIN_IMAGES} hình khác nhau)")

    # O4: từ khoá chính của title được nói trước giây 15
    title = row.get("title") or ""
    thumb = row.get("thumbnail"); thumb_text = (thumb.get("text") or "") if isinstance(thumb, dict) else (thumb if isinstance(thumb, str) else "")
    spoken_15 = " ".join(script[i] for i, ln in enumerate(lines) if ln["start"] < 15.0)
    spoken_15_clean = _clean_vi_text(spoken_15)
    matched_kw = _match_title_keywords(title, thumb_text, spoken_15_clean)
    if not matched_kw:
        kws_hint = _get_title_keywords_sample(title, thumb_text)
        warns.append(f"O4: Chưa thấy từ khoá chính của title ({kws_hint}) được nói trước giây 15 (cảnh báo)")

    # O5: cấm ảnh ref nhân vật (/refs/, REF_) làm hình
    for k, spec in media.items():
        ref_hit = _check_ref_asset(spec)
        if ref_hit:
            errs.append(f"O5: media câu {k} dùng ảnh ref nhân vật (\x27{ref_hit}\x27) -- cấm ảnh ref (/refs/, REF_) làm hình")

    # O6: cảnh báo lời meta ("video này", "chương N", "đăng ký") trong 0–40 s
    for i, ln in enumerate(lines):
        if ln["start"] >= OPENING_GATE_S:
            break
        st = ln["start"]
        sid = ln["sentence_id"]
        meta_hit = _check_meta_text(script[i])
        if meta_hit:
            warns.append(f"O6: câu {sid} (~{st:.1f}s) có lời meta \x27{meta_hit}\x27 trong 0–40s (cảnh báo)")

    # O7: câu hỏi hẹn/lộ trình không nằm trong 0–40 s (cảnh báo)
    visuals = row.get("visuals") or {}
    for i, ln in enumerate(lines):
        if ln["start"] >= OPENING_GATE_S:
            break
        st = ln["start"]
        sid = ln["sentence_id"]
        v = visuals.get(str(sid)) or visuals.get(sid)
        if v and isinstance(v, dict):
            vtype = v.get("type")
            if vtype in ("ask", "timeline", "roadmap", "agenda"):
                warns.append(f"O7: câu {sid} (~{st:.1f}s) có thẻ visual \x27{vtype}\x27 trong 0–40s -- nên dời câu hỏi hẹn/lộ trình sang sau 40s (cảnh báo)")
        rm_hit = _check_roadmap_text(script[i])
        if rm_hit:
            warns.append(f"O7: câu {sid} (~{st:.1f}s) có lời hẹn/lộ trình \x27{rm_hit}\x27 trong 0–40s -- nên dời sang sau 40s (cảnh báo)")

    # O9: không khung đồng màu > 0,3 s trong 0–40 s của mp4 đã render
    v_cand = Path(video_path) if video_path else None
    if not v_cand or not v_cand.exists():
        rid = str(row.get("id") or "")
        cand_paths = [
            row.get("rendered_mp4"),
            row.get("video_path"),
            f"output/cl_staging/long/out/{rid}.mp4" if rid else None,
            f"output/long/{rid}.mp4" if rid else None,
            f"out/{rid}.mp4" if rid else None,
        ]
        for cp in cand_paths:
            if cp and Path(cp).exists():
                v_cand = Path(cp)
                break
    if v_cand and v_cand.exists():
        theme_id = row.get("theme") or (row.get("opts") or {}).get("theme") or "saffron"
        solid_violations = check_opening_solid_frames(
            v_cand, max_sec=OPENING_GATE_S, fps=10,
            std_thresh=OPENING_GATE_SOLID_STD_THRESH,
            max_dur=OPENING_GATE_MAX_SOLID_S,
            theme=theme_id,
        )
        for v in solid_violations:
            errs.append(
                f"O9: 0–40s có khung đồng màu hoặc nền theme trống {v['dur']:.2f}s (> {OPENING_GATE_MAX_SOLID_S:.1f}s) "
                f"tại {v['start']:.1f}s–{v['end']:.1f}s (std={v['std']:.1f}, sim={v.get('sim', 0):.2f}) trong video đã render"
            )

    return errs, warns


def opening_gate_issues(row: dict, segs: list[dict] | None = None,
                        video_path: Path | str | None = None) -> list[str]:
    """Chỉ trả về các lỗi ERROR của opening_gate (chặn render)."""
    errs, _ = opening_gate(row, segs, video_path=video_path)
    return errs


def opening_gate_warnings(row: dict, segs: list[dict] | None = None,
                          video_path: Path | str | None = None) -> list[str]:
    """Chỉ trả về cảnh báo (O4, O6, O7) của opening_gate."""
    _, warns = opening_gate(row, segs, video_path=video_path)
    return warns


def export_first40(row: dict, segs: list[dict] | None = None, out_path: Path | str | None = None,
                   video_path: Path | str | None = None) -> Path:
    """O8: Xuất tờ khung 0–40 s (1 khung/2 s) ra output/cl_staging/long/review_<id>/first40.jpg.
    Lưới 5 cột x 4 hàng (20 khung tại t = 0, 2, 4, ..., 38s)."""
    import subprocess
    from PIL import Image, ImageDraw, ImageFont

    rid = str(row.get("id") or "review")
    if out_path is None:
        out_dir = Path("output/cl_staging/long") / f"review_{rid}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "first40.jpg"
    else:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Thử ffmpeg nếu có file video mp4 thật
    v_cand = Path(video_path) if video_path else None
    if not v_cand or not v_cand.exists():
        for cand in [Path(f"output/cl_staging/long/out/{rid}.mp4"),
                     Path(f"output/long/{rid}.mp4"),
                     Path(f"out/{rid}.mp4")]:
            if cand.exists():
                v_cand = cand
                break

    if v_cand and v_cand.exists():
        try:
            cmd = [
                "ffmpeg", "-y", "-v", "error",
                "-ss", "0", "-t", "40", "-i", str(v_cand),
                "-vf", "fps=1/2,scale=384:216,tile=5x4",
                "-frames:v", "1", str(out_path)
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 0:
                return out_path
        except Exception:
            pass

    # 2. Dựng tờ khung 5x4 bằng PIL từ tài sản trong plan
    cell_w, cell_h, cols, rows = 384, 216, 5, 4
    canvas = Image.new("RGB", (cell_w * cols, cell_h * rows), color="#0c1020")
    draw = ImageDraw.Draw(canvas)

    lines, segs, media, owner = _build_lines_for_gate(row, segs)
    script = row.get("script") or []
    n = len(lines)

    font_ts = None
    font_lbl = None
    for f in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
              "/Library/Fonts/Arial Unicode.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        if Path(f).exists():
            try:
                font_ts = ImageFont.truetype(f, 20)
                font_lbl = ImageFont.truetype(f, 16)
                break
            except Exception:
                pass
    if font_ts is None:
        font_ts = ImageFont.load_default()
        font_lbl = ImageFont.load_default()

    for idx in range(20):
        t = idx * 2.0
        c = idx % cols
        r = idx // cols
        x0, y0 = c * cell_w, r * cell_h

        sid = 1
        ln_cur = lines[0] if lines else None
        for i, ln in enumerate(lines):
            t_end = segs[i + 1]["start"] if i + 1 < n else segs[i]["end"]
            if ln["start"] <= t < t_end:
                sid = ln["sentence_id"]
                ln_cur = ln
                break
            if ln["start"] > t:
                break

        cell_img = None
        m_spec = media.get(str(sid)) or media.get(sid)
        if not m_spec and ln_cur and (sid - 1) in owner:
            oid = owner[sid - 1] + 1
            m_spec = media.get(str(oid)) or media.get(oid)

        if m_spec and isinstance(m_spec, dict):
            p_str = m_spec.get("path") or m_spec.get("src")
            if p_str:
                p_path = Path(p_str)
                if not p_path.is_absolute():
                    for root in (Path("."), Path("output/cl_staging/long")):
                        if (root / p_str).exists():
                            p_path = root / p_str
                            break
                if p_path.exists():
                    try:
                        if p_path.suffix.lower() in (".mp4", ".mov", ".webm"):
                            raw = subprocess.run([
                                "ffmpeg", "-v", "error", "-ss", "0.5", "-i", str(p_path),
                                "-frames:v", "1", "-vf", f"scale={cell_w}:{cell_h}:force_original_aspect_ratio=increase,crop={cell_w}:{cell_h}",
                                "-f", "image2pipe", "-vcodec", "mjpeg", "-"
                            ], capture_output=True).stdout
                            if raw:
                                import io
                                cell_img = Image.open(io.BytesIO(raw)).convert("RGB")
                        else:
                            im = Image.open(p_path).convert("RGB")
                            w, h = im.size
                            target_ratio = cell_w / cell_h
                            im_ratio = w / h
                            if im_ratio > target_ratio:
                                new_w = int(h * target_ratio)
                                left = (w - new_w) // 2
                                im = im.crop((left, 0, left + new_w, h))
                            else:
                                new_h = int(w / target_ratio)
                                top = (h - new_h) // 2
                                im = im.crop((0, top, w, top + new_h))
                            cell_img = im.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
                    except Exception:
                        cell_img = None

        if cell_img:
            canvas.paste(cell_img, (x0, y0))
        else:
            cell_box = Image.new("RGB", (cell_w - 4, cell_h - 4), color="#151b2e")
            cdraw = ImageDraw.Draw(cell_box)
            pk = _plan_line_kind(sid - 1, ln_cur, lines, media, owner) if ln_cur else "trống"
            cdraw.rectangle([(0, 0), (cell_w - 5, cell_h - 5)], outline="#2b3552", width=2)
            label_text = f"[{pk.upper()}]"
            cdraw.text((16, 50), label_text, fill="#d4a93a", font=font_ts)
            if ln_cur and sid - 1 < len(script):
                s_txt = script[sid - 1].replace("**", "")[:28]
                cdraw.text((16, 90), s_txt, fill="#c0c7dc", font=font_lbl)
            canvas.paste(cell_box, (x0 + 2, y0 + 2))

        badge_text = f"{int(t):02d}s (câu {sid})"
        draw.rectangle([(x0 + 6, y0 + 6), (x0 + 115, y0 + 34)], fill="rgba(0,0,0,180)")
        draw.text((x0 + 12, y0 + 9), badge_text, fill="#ffffff", font=font_lbl)

    canvas.save(out_path, format="JPEG", quality=90)
    return out_path


def _pct(xs: list[float], q: float) -> float:
    s = sorted(xs)
    return round(s[min(len(s) - 1, int(len(s) * q / 100))], 1) if s else 0.0


# Ticket 65 (đề xuất a, chưa A/B): phút đầu và phút cuối đổi hình nhanh (2-4 giây/cảnh), giữa 5-8 giây.
# Chỉ cảnh báo (vào rep["sàn"]); mẫu đo của báo cáo là của nhà cung cấp, chưa có số kênh xác nhận.
EDGE_S = 60.0
EDGE_MAX_AVG = 4.0


def tempo_edges(shots: list[float], starts: list[float], total: float) -> dict:
    head = [d for d, t in zip(shots, starts) if t < EDGE_S]
    tail = [d for d, t in zip(shots, starts) if t >= total - EDGE_S]
    rep, warn = {}, []
    for name, xs in (("phút đầu", head), ("phút cuối", tail)):
        if not xs or total < 3 * EDGE_S:
            continue
        avg = round(sum(xs) / len(xs), 1)
        rep[f"TB {name}"] = avg
        if avg > EDGE_MAX_AVG:
            warn.append(f"{name} {avg}s/cảnh (mục tiêu 2-{EDGE_MAX_AVG:.0f}s; cảnh báo, không chặn)")
    return {"rep": rep, "warn": warn}


def _local_sig(spec: dict) -> str:
    """Dấu nội dung file media kind "local": thay ảnh mà giữ tên (24/10: buddha_face.jpg) thì chương render lại.
    Ảnh băm cả file; clip chỉ lấy cỡ + mtime cho nhanh. Kind mạng (commons/stock) không đổi: giữ cache cũ."""
    p = PROJECT_ROOT / (spec.get("path") or "")
    if not p.is_file():
        return "?"
    if p.suffix.lower() in (".mp4", ".mov", ".webm"):
        st = p.stat()
        return f"{st.st_size}:{int(st.st_mtime)}"
    return hashlib.sha1(p.read_bytes()).hexdigest()[:16]


def chapter_key(row: dict, a: int, b: int, t0: float, t1: float, quality: str,
                layout_sig: str | None = None) -> str:
    """Băm đầu vào một chương (câu a+1..b): đổi chữ/sơ đồ/ảnh (cả nội dung file local)/khung giờ/engine thì render lại."""
    subs = {kind: {str(int(k) - a): _remap_at(v, a) for k, v in (row.get(kind) or {}).items() if a < int(k) <= b}
            for kind in ("media", "visuals")}
    for v in subs["media"].values():
        if isinstance(v, dict) and v.get("kind") == "local":
            v["_sig"] = _local_sig(v)
    return hashlib.sha1(json.dumps([row["script"][a:b], subs, row["style"], round(t0, 3), round(t1, 3), quality, _engine_sig()]
                                   + ([True] if row.get("kinetic") else [])
                                   + ([{"kicker": row["kicker"]}] if row.get("kicker") else [])
                                   + ([{"theme": row["theme"]}] if row.get("theme") else [])
                                   + ([{"subs": row["subs"]}] if row.get("subs") and row.get("subs") != "off" else [])
                                   + ([layout_sig] if layout_sig else []),
                                   ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def render_chapters(row: dict, out_dir: Path, quality: str, txt: Path, wav: Path, bgm: str) -> tuple[bool, str]:
    """Video 30+ phút: render từng chương (chạy lại được từng chương), nối hình, trộn tiếng MỘT lần."""
    import soundfile as sf  # noqa: PLC0415
    rid = row["id"]
    lines = row["script"]
    man = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))
    segs, total = man["segments"], float(man["duration_s"])
    layout_chosen = layout_v2_choices(row, segs)
    if layout_chosen is not None:
        import hyperframes_bridge as HB  # noqa: PLC0415
        print("    " + HB.layout_report(layout_chosen, row.get("media") or {}), flush=True)
    audio, sr = sf.read(wav, dtype="float32")
    cdir = out_dir / f"{rid}_chapters"
    cdir.mkdir(exist_ok=True)
    spans = chapter_spans(lines, segs, total)
    rep, bad = pacing(row, segs)
    print(f"    nhịp hình: {rep}", flush=True)
    for x in bad:
        print(f"    !! nhịp hình: {x}", flush=True)
    for x in rep.get("sàn") or []:
        print(f"    !! sàn (cảnh báo, không chặn): {x}", flush=True)
    if bad and (row.get("pacing") == "strict" or any(x.startswith("120s đầu:") for x in bad)):
        return False, "nhịp hình chưa đạt: " + "; ".join(bad)
    silence = [int(x) for x in row.get("silence") or []]
    credits, parts = [], []
    changed = False
    env = dict(os.environ, HF_CAPTURE_PARALLEL_STREAM="true")
    for c, (a, b, t0, t1) in enumerate(spans):
        name = f"ch{c:02d}"
        mp4 = cdir / f"{name}.mp4"
        parts.append(mp4)
        meta = cdir / f"{name}.render.json"
        layout_sig = None
        if layout_chosen is not None:
            layout_sig = json.dumps(
                {str(int(sid) - a): {"layout": choice.get("layout") or "", "cine": choice.get("cine")}
                 for sid, choice in layout_chosen.items() if a < int(sid) <= b},
                sort_keys=True, ensure_ascii=False)
        key = chapter_key(row, a, b, t0, t1, quality, layout_sig=layout_sig)
        if classify_mp4(mp4) == "ok" and meta.exists():
            m0 = json.loads(meta.read_text(encoding="utf-8"))
            if m0.get("input_sha1") == key:
                credits += m0.get("media_credits", [])
                continue
            print(f"    {name}: nội dung/engine đã đổi -- render lại", flush=True)
        changed = True
        ctxt, cwav = cdir / f"{name}.txt", cdir / f"{name}.wav"
        ctxt.write_text("\n".join(lines[a:b]) + "\n", encoding="utf-8")
        sf.write(cwav, audio[int(round(t0 * sr)):int(round(t1 * sr))], sr)
        cman = dict(man, duration_s=round(t1 - t0, 4), output_file=cwav.name,
                    segments=[dict(sg, start=round(sg["start"] - t0, 3), end=round(sg["end"] - t0, 3)) for sg in segs[a:b]])
        cwav.with_suffix(".json").write_text(json.dumps(cman, ensure_ascii=False), encoding="utf-8")
        cmd = [sys.executable, "hyperframes_bridge.py", "--script", str(ctxt), "--wav", str(cwav), "--series", row["series"],
               "--style", row["style"], "--badge", row.get("badge", ""), "--footer", FOOTER[row["series"]],
               "--bgm", bgm, "--bgm-gain", "0", "--output", str(mp4), "--quality", quality, "--lane", "long"]
        if row.get("kicker"):   # nhãn góc riêng của video (mặc định theo lane: "12 CON GIÁP · 2027" chỉ hợp F2/F3)
            cmd += ["--kicker", row["kicker"]]
        for kind, flag in (("media", "--media"), ("visuals", "--visuals")):   # KHÔNG dùng tên `key` -- đè băm chương
            sub = {str(int(k) - a): _remap_at(v, a) for k, v in (row.get(kind) or {}).items() if a < int(k) <= b}
            if sub:
                side = cdir / f"{name}.{kind}.json"
                side.write_text(json.dumps(sub, ensure_ascii=False), encoding="utf-8")
                cmd += [flag, str(side)]
        base = sum(1 for l in lines[:a] if l.startswith("**") and l.endswith("**") and l.count("**") == 2)
        opts = {"video_only": True, "seg_off": t0, "seg_total": total, "chapter_base": base, "kinetic": bool(row.get("kinetic")), "wordts": bool(row.get("wordts")),
                "theme": row.get("theme"), "silence": [x - a for x in silence if a < x <= b]}
        if row.get("subs"):
            opts["subs"] = row["subs"]
        if row.get("caps"):
            opts["caps"] = row["caps"]
        if layout_chosen is not None:
            opts = layout_v2_opts(opts, row, layout_chosen, shift=a, lo=a, hi=b)
        side = cdir / f"{name}.opts.json"
        side.write_text(json.dumps(opts), encoding="utf-8")
        cmd += ["--opts", str(side)]
        t = time.time()
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, env=env)
        if proc.returncode != 0 or not mp4.exists():
            return False, f"chương {name} lỗi: {(proc.stdout + proc.stderr)[-400:]}"
        for ln in reversed((proc.stdout or "").strip().splitlines()):
            if ln.startswith("{"):
                res = json.loads(ln)
                res["input_sha1"] = key
                meta.write_text(json.dumps(res, ensure_ascii=False) + "\n", encoding="utf-8")
                credits += res.get("media_credits", [])
                break
        print(f"    {name}: câu {a + 1}-{b}, {t1 - t0:.0f}s, render {time.time() - t:.0f}s", flush=True)

    final_mp4 = out_dir / f"{rid}.mp4"
    silent = cdir / "silent.mp4"
    mixed = cdir / "mix.wav"
    # File cuối cũ còn đọc được không có nghĩa là đã ghép bản chương mới.
    # Chỉ "đã có" khi mtime file cuối > mọi chương và > mix.wav/silent.mp4 nếu chúng có.
    if changed:
        classify_mp4(final_mp4)   # file cuối hỏng không được mang tên thật trong lúc ghép lại
    elif classify_mp4(final_mp4) == "ok" and newer_than_inputs(final_mp4, [*parts, mixed, silent]):
        return True, "đã có"
    # Nối hình + trộn tiếng cả video: nạp WAV cả video vào RAM (~11 GB với Long 30 phút) -> khoá toàn máy.
    try:
        with final_mix_lock(rid):
            # Ước file cuối ~ tổng các chương (chép luồng). Cần chỗ cho bản nối câm, mix.wav và bản cuối cùng.
            expected = sum(p.stat().st_size for p in parts) + mix_wav_expected_bytes(total, mixed)
            short = disk_shortfall_message(expected, dest_free_bytes(out_dir))
            if short:
                return False, short
            # Nối hình (cùng bộ mã hoá, cùng thông số -> chép luồng), rồi trộn tiếng cả video một lần.
            lst = cdir / "concat.txt"
            lst.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
            res = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)],
                                 capture_output=True, text=True)
            if res.returncode != 0:
                extra = ""
                if silent.is_file():
                    dest = quarantine_broken_mp4(silent)
                    extra = f" -- {silent.name} đã chuyển vào {dest}"
                return False, f"nối chương lỗi: {res.stderr[-300:]}{extra}"
            if probe_duration_s(silent) is None:
                extra = ""
                if silent.is_file():
                    dest = quarantine_broken_mp4(silent)
                    extra = f" -- chuyển vào {dest}"
                return False, (f"nối chương ra file hỏng ({silent.name}: ffprobe không đọc được duration > 0)"
                               f"{extra}")
            import hyperframes_bridge as HB  # noqa: PLC0415
            import hf_foley  # noqa: PLC0415
            glines = HB.build_lines(txt, wav.with_suffix(".json"), align_audio=wav)
            HB.apply_visuals(glines, row.get("visuals") or {}, row.get("media") or {})
            for ln in glines:
                if str(ln["sentence_id"]) in (row.get("media") or {}):
                    ln["media"] = {"query": ""}
            sound_spec = row.get("sound") or {}
            if row.get("ambience") or row.get("beats"):
                import hf_ambience  # noqa: PLC0415
                sound_spec = hf_ambience.sound_spec(row)
            hf_foley.mix_long(glines, row["series"], wav, PROJECT_ROOT / bgm if bgm else None, total, sound_spec,
                              set(silence), mixed, seed=hashlib.sha1(rid.encode()).digest()[0], pool=long_pool(row))
            mix_log(f"{rid}: trộn xong | RAM trống {mix_fmt_gb(mix_available_gb())}")
            used = note_bgm(row, mixed)
            # Tên tạm. File dở (đĩa đầy, thiếu moov) không bao giờ mang tên .mp4 thật.
            part = out_dir / f"{rid}.part.mp4"
            HB.mux_audio(silent, mixed, part, duration=total, loudness=HB.LOUD_TARGET["long"])
            if probe_duration_s(part) is None:
                extra = " -- chưa đổi tên thành .mp4"
                if part.is_file():
                    dest = quarantine_broken_mp4(part)
                    extra += f" -- chuyển vào {dest}"
                return False, (f"{part.name} hỏng sau khi ghép (ffprobe không đọc được duration > 0)"
                               f"{extra}")
            part.replace(final_mp4)
            (out_dir / f"{rid}.render.json").write_text(json.dumps(
                {"ok": True, "output": str(final_mp4), "duration_s": total, "style": row["style"], "chapters": len(spans),
                 "media_credits": list(dict.fromkeys(c for c in credits if c)), "bgm": str(PROJECT_ROOT / bgm) if bgm else "",
                 "bgm_used": used, "sound": "foley-v1"}, ensure_ascii=False) + "\n", encoding="utf-8")
    except FinalMixLockTimeout as exc:
        return False, str(exc)
    return True, "xong"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_dir", help="Thư mục chứa plan_*.json (và thư mục out/)")
    ap.add_argument("--only", default=None, help="Chỉ dựng mục có id bắt đầu bằng chuỗi này")
    ap.add_argument("--quality", default="looks", choices=["draft", "looks", "delivery"])
    ap.add_argument("--remix-audio", action="store_true",
                    help="Chỉ trộn lại tiếng (nhạc nền theo chính sách hiện tại) cho video đã render")
    ap.add_argument("--cho-phep-retire", action="store_true", help="Lead vượt khuôn retire có lý do")
    ap.add_argument("--allow-lint-fail", action="store_true", help="Lead bỏ qua lỗi cổng lint; ghi log rõ ràng")
    args = ap.parse_args()

    plan_dir = Path(args.plan_dir)
    out_dir = plan_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [r for r in load_rows(plan_dir) if not args.only or r["id"].startswith(args.only)]
    print(f"{len(rows)} mục trong {plan_dir}\n", flush=True)

    long_rows = [r for r in rows if r.get("lane") == "long"]
    if long_rows and all(not r.get("scene_decision") for r in long_rows):
        print("CẢNH BÁO: plan lane=long thiếu scene_decision ở mọi cảnh.", flush=True)

    from library.tools.lib import enforce_lane
    channel_by_series = {"fs": "fs", "bud": "bud"}
    for row in rows:
        channel = channel_by_series.get(row.get("series"))
        if channel:
            enforce_lane(channel, row.get("lane"), args.cho_phep_retire)

    failed = []
    for i, row in enumerate(rows, start=1):
        t0 = time.time()
        ok, note = (remix_audio(row, out_dir) if args.remix_audio
                    else render_one(row, out_dir, args.quality, args.allow_lint_fail))
        nfig = sum(1 for f in (row.get("figures") or {}).values() if f.get("type") != "none")
        mark = "✓" if ok else "✗"
        print(f"[{i}/{len(rows)}] {mark} {row['id']:8s} {row.get('style','?'):13s} "
              f"{time.time()-t0:5.1f}s {nfig} fig  {note if note != 'xong' else row.get('title','')[:42]}",
              flush=True)
        if not ok:
            failed.append((row["id"], note))

    done = done_mp4_count(out_dir)
    print(f"\nXong: {done} video trong {out_dir}", flush=True)
    for rid, note in failed:
        print(f"  HỎNG {rid}: {note}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
