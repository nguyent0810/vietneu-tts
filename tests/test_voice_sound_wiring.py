"""Test wiring giọng D và preset âm thanh C cho plan Long (task 92c).

Kiểm tra:
1. Regression test 3 plan #72 thật (L_bud_14, L_fs_26, L_fs_27):
   - spec TTS ra đúng khoá cache CŨ (uses_new_cache == False).
   - mix đi nhánh legacy (không preset_long == 'C').
2. Plan mới giả lập:
   - spec TTS ra khoá cache D mới (temperature, donor, text_mode).
   - sound mang preset_long: C và mix đi nhánh preset C.
3. Builder/hàm dùng chung wire_plan_row:
   - Bảo toàn cấu hình cũ cho plan cũ (không tự thêm 3 khoá D / preset C).
   - Hỗ trợ cờ legacy=True và cờ force=True.
"""
import json
from pathlib import Path

import pytest

import hf_batch_render as HBR
import hf_foley
import hf_sound as HS
import hf_voice as V
import tts_lexicon

ROOT = Path(__file__).resolve().parents[1]
PLAN_72 = {
    "L_bud_14": ROOT / "output/cl_staging/long/plan_long_w50.json",
    "L_fs_26": ROOT / "output/cl_staging/long/plan_long_pilot.json",
    "L_fs_27": ROOT / "output/cl_staging/long/plan_long_cb.json",
}


def _load_plan_row(pid: str, path: Path) -> dict:
    if not path.exists():
        pytest.skip(f"Thiếu file plan trên đĩa: {path}")
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        pytest.skip(f"Không đọc được file plan {path}: {exc}")
    for r in rows:
        if isinstance(r, dict) and r.get("id") == pid:
            return r
    pytest.skip(f"Không tìm thấy row '{pid}' trong {path}")


@pytest.mark.parametrize("pid", ["L_bud_14", "L_fs_26", "L_fs_27"])
def test_plan_72_real_regression_keeps_legacy_cache_and_mix(pid):
    """3 plan #72 thật trên đĩa phải giữ nguyên khoá cache cũ và mix legacy."""
    fpath = PLAN_72[pid]
    row = _load_plan_row(pid, fpath)

    tts_spec = row.get("tts") or {}
    sound_spec = row.get("sound") or {}

    # 1. TTS: không có 3 khoá D -> uses_new_cache là False
    assert not V.uses_new_cache(tts_spec), f"{pid} có khoá D ngoài dự kiến: {tts_spec}"
    assert "temperature" not in tts_spec
    assert "donor" not in tts_spec
    assert "text_mode" not in tts_spec

    # Kiểm tra khoá cache câu đầu tiên của kịch bản
    line1 = V.clean(row["script"][0])
    spoken = V.spoken_text(line1, tts_spec)
    voice, style, k, engine = V.line_cfg(tts_spec, 1)
    key_gen = V.cache_key(engine, voice, style, k, spoken)
    # Xác nhận khoá cũ không chứa chuỗi tham số mở rộng
    assert len(key_gen) == 20

    # 2. Sound: không có preset_long == 'C' hay preset == 'C' -> nhánh legacy
    preset_long = sound_spec.get("preset_long")
    preset = sound_spec.get("preset")
    assert preset_long != "C", f"{pid} có preset_long='C'"
    assert preset != "C", f"{pid} có preset='C'"

    # Kiểm tra điều kiện nhánh rẽ của hf_foley.mix_long:
    is_branch_c = (sound_spec.get("preset_long") == "C" or sound_spec.get("preset") == "C")
    assert not is_branch_c, f"{pid} bị chuyển hướng sang mix_long_c"


def test_new_plan_wiring_generates_voice_d_and_sound_c():
    """Plan mới giả lập: sinh sẵn khoá giọng D và preset âm thanh C từ hồ sơ kênh."""
    # Cách 1: Nối trực tiếp qua builder dùng new_tts và new_sound
    row_direct = {
        "id": "L_fs_new_direct",
        "series": "fs",
        "script": ["Tháng 11 năm 2026, vận trình người tuổi Tý."],
        "tts": V.new_tts("fs", voice="Thái Sơn", style="doc_truyen", tempo=0.96),
        "sound": HS.new_sound("fs", reverb=0.0, music_from=1),
    }

    assert V.uses_new_cache(row_direct["tts"])
    assert row_direct["tts"]["temperature"] == 0.7
    assert row_direct["tts"]["donor"] == "Thanh Bình"
    assert row_direct["tts"]["text_mode"] == "speech"
    assert row_direct["sound"]["preset_long"] == "C"

    # Cách 2: Nối qua hàm builder dùng chung wire_plan_row (legacy=False)
    new_raw_row = {
        "id": "L_fs_new_test",
        "series": "fs",
        "script": ["Tháng 11 năm 2026, vận trình người tuổi Tý."],
        "tts": {"voice": "Thái Sơn", "style": "doc_truyen", "tempo": 0.96},
        "sound": {"reverb": 0.0, "music_from": 1},
    }
    wired = HBR.wire_plan_row(new_raw_row, legacy=False)

    # 1. TTS có đủ 3 khoá giọng D của FS
    tts = wired["tts"]
    assert V.uses_new_cache(tts)
    assert tts["temperature"] == 0.7
    assert tts["donor"] == "Thanh Bình"
    assert tts["text_mode"] == "speech"
    assert tts["voice"] == "Thái Sơn"

    line1 = V.clean(wired["script"][0])
    spoken = V.spoken_text(line1, tts)
    assert "hai nghìn không trăm hai mươi sáu" in spoken  # text_mode speech đã chạy

    voice, style, k, engine = V.line_cfg(tts, 1)
    donor = V.line_donor(tts, 1, engine)
    temp = V.line_temperature(tts, 1)
    key_d = V.cache_key(engine, voice, style, k, spoken, temperature=temp,
                        donor=donor, text_mode=tts.get("text_mode"))
    key_legacy = V.cache_key(engine, voice, style, k, spoken)
    assert key_d != key_legacy

    # 2. Sound có preset_long: C và nhánh rẽ đi vào C
    sound = wired["sound"]
    assert sound.get("preset_long") == "C"
    assert sound.get("bgm_mac_dinh") == "bgm/thinking_music.mp3"
    assert sound.get("reverb") == 0.0

    is_branch_c = (sound.get("preset_long") == "C" or sound.get("preset") == "C")
    assert is_branch_c


def test_wire_plan_row_preserves_old_plan_without_d_keys():
    """Khi build lại plan cũ có sẵn tts không có 3 khoá, không tự thêm khoá D/C."""
    old_row = {
        "id": "L_bud_old_rebuild",
        "series": "bud",
        "script": ["Lời kinh vô thường."],
        "tts": {"voice": "Binh", "engine": "standard", "tempo": 0.91},
        "sound": {"reverb": 0.045},
    }

    # Chạy qua wire_plan_row mà không có force=True
    preserved = HBR.wire_plan_row(old_row)

    assert not V.uses_new_cache(preserved["tts"])
    assert "temperature" not in preserved["tts"]
    assert "donor" not in preserved["tts"]
    assert "text_mode" not in preserved["tts"]
    assert preserved["sound"].get("preset_long") != "C"


def test_wire_plan_row_legacy_and_force_flags():
    """Kiểm tra cờ legacy=True và cờ force=True."""
    # 1. legacy=True giữ nguyên
    row1 = {
        "id": "L_fs_legacy_explicit",
        "series": "fs",
        "script": ["Lời mở đầu."],
        "tts": {"voice": "Thái Sơn"},
        "sound": {},
    }
    res_leg = HBR.wire_plan_row(row1, legacy=True)
    assert not V.uses_new_cache(res_leg["tts"])
    assert res_leg["sound"].get("preset_long") != "C"

    # 2. force=True nâng cấp plan cũ lên D + C
    row2 = {
        "id": "L_fs_upgrade",
        "series": "fs",
        "script": ["Nâng cấp lên giọng D."],
        "tts": {"voice": "Thái Sơn", "style": "doc_truyen"},
        "sound": {"reverb": 0.0},
    }
    res_upg = HBR.wire_plan_row(row2, force=True)
    assert V.uses_new_cache(res_upg["tts"])
    assert res_upg["tts"]["temperature"] == 0.7
    assert res_upg["tts"]["donor"] == "Thanh Bình"
    assert res_upg["sound"]["preset_long"] == "C"


def test_real_builder_main_preserves_legacy_row_and_wires_new_row(monkeypatch, tmp_path):
    """Test đường thật (task 92d): chạy main() của builder thật trong thư mục tạm.
    - plan có sẵn row cùng id với tts/sound legacy -> sau khi chạy, tts/sound của row đó trùng byte bản cũ.
    - row id mới ra giọng D + preset C.
    """
    import sys
    sys.path.insert(0, str(ROOT / "output/cl_staging/long"))
    b_top3 = pytest.importorskip("build_T10_top3", reason="builder nằm trong output/ (gitignore)")

    tmp_plan_file = tmp_path / "plan_long_t10_top3.json"
    legacy_tts = {
        "voice": "Thái Sơn", "style": "doc_truyen", "tempo": 0.96, "pause": 0.46,
        "pauses": {"14": 2.0, "92": 2.0}, "tempos": {},
    }
    legacy_sound = {
        "reverb": 0.0, "music_from": 14, "drops": [], "amb": [{"from": 1, "to": 520, "kind": "room"}],
        "fx": [], "motif": [14, 520], "voice_eq": True, "music_gap": 18, "sfx_peak": 0.32,
    }
    legacy_row = {
        "id": "L_fs_t10_top3",
        "series": "fs",
        "script": ["Tháng 10 âm lịch 2026."],
        "tts": legacy_tts,
        "sound": legacy_sound,
    }
    tmp_plan_file.write_text(json.dumps([legacy_row], ensure_ascii=False, indent=1), encoding="utf-8")
    legacy_tts_bytes = json.dumps(legacy_tts, ensure_ascii=False, indent=1)
    legacy_sound_bytes = json.dumps(legacy_sound, ensure_ascii=False, indent=1)

    # Monkeypatch đường dẫn plan sang thư mục tạm
    monkeypatch.setattr(b_top3, "PLAN_PATH", tmp_plan_file)

    # Chạy main() của builder thật
    exit_code = b_top3.main()
    assert exit_code == 0

    # Sau khi chạy, row cùng id TRÙNG BYTE bản cũ
    rows_after = json.loads(tmp_plan_file.read_text(encoding="utf-8"))
    assert len(rows_after) == 1
    row_updated = rows_after[0]
    assert row_updated["id"] == "L_fs_t10_top3"
    assert json.dumps(row_updated["tts"], ensure_ascii=False, indent=1) == legacy_tts_bytes
    assert json.dumps(row_updated["sound"], ensure_ascii=False, indent=1) == legacy_sound_bytes
    assert not V.uses_new_cache(row_updated["tts"])
    assert row_updated["sound"].get("preset_long") != "C"

    # Row có ID mới ghi vào plan -> tự động ra giọng D + preset C
    new_raw_row = {
        "id": "L_fs_brand_new_ep",
        "series": "fs",
        "script": ["Tập mới sản xuất năm 2026."],
        "tts": {"voice": "Thái Sơn", "style": "doc_truyen", "tempo": 0.96},
        "sound": {"reverb": 0.0},
    }
    HBR.save_plan_rows(tmp_plan_file, new_raw_row)

    rows_with_new = json.loads(tmp_plan_file.read_text(encoding="utf-8"))
    assert len(rows_with_new) == 2
    r_old = next(r for r in rows_with_new if r["id"] == "L_fs_t10_top3")
    r_new = next(r for r in rows_with_new if r["id"] == "L_fs_brand_new_ep")

    assert json.dumps(r_old["tts"], ensure_ascii=False, indent=1) == legacy_tts_bytes
    assert json.dumps(r_old["sound"], ensure_ascii=False, indent=1) == legacy_sound_bytes

    assert V.uses_new_cache(r_new["tts"])
    assert r_new["tts"]["temperature"] == 0.7
    assert r_new["tts"]["donor"] == "Thanh Bình"
    assert r_new["tts"]["text_mode"] == "speech"
    assert r_new["sound"]["preset_long"] == "C"


@pytest.mark.parametrize("pid", ["L_bud_14", "L_fs_26", "L_fs_27"])
def test_plan_72_rerun_in_temp_dir_keeps_cache_and_mix(pid, tmp_path):
    """3 plan #72 (L_bud_14, L_fs_26, L_fs_27): chạy lại đường ghi plan vào thư mục tạm -> khoá cache + mix không đổi."""
    import shutil
    import sys
    sys.path.insert(0, str(ROOT / "output/cl_staging/long"))

    fpath = PLAN_72[pid]
    if not fpath.exists():
        pytest.skip(f"Thiếu file plan {fpath}")

    # Tạo bản sao trong thư mục tạm
    tmp_file = tmp_path / fpath.name
    shutil.copy2(fpath, tmp_file)

    before_rows = json.loads(tmp_file.read_text(encoding="utf-8"))
    row_before = next(r for r in before_rows if r.get("id") == pid)
    tts_before = json.loads(json.dumps(row_before["tts"]))
    sound_before = json.loads(json.dumps(row_before["sound"]))

    # Lấy cache key của câu 1 trước khi chạy
    line1 = V.clean(row_before["script"][0])
    spoken_before = V.spoken_text(line1, tts_before)
    voice, style, k, engine = V.line_cfg(tts_before, 1)
    key_before = V.cache_key(engine, voice, style, k, spoken_before)

    # Chạy đường ghi plan (save_plan_rows) với row từ builder
    if pid == "L_bud_14":
        import build_B10
        HBR.save_plan_rows(tmp_file, build_B10.row)
    elif pid == "L_fs_26":
        import build_F26
        HBR.save_plan_rows(tmp_file, build_F26.row)
    elif pid == "L_fs_27":
        cb_plan = ROOT / "output/cl_staging/long/research/long_test/plan_cb_long.json"
        cb_row = json.loads(cb_plan.read_text(encoding="utf-8"))[0]
        cb_row["id"] = "L_fs_27"
        HBR.save_plan_rows(tmp_file, cb_row)

    after_rows = json.loads(tmp_file.read_text(encoding="utf-8"))
    row_after = next(r for r in after_rows if r.get("id") == pid)

    # 1. diff tts và sound trước/sau == 0
    assert row_after["tts"] == tts_before
    assert row_after["sound"] == sound_before

    # 2. khoá cache câu 1 không đổi và là khoá cũ (legacy)
    spoken_after = V.spoken_text(line1, row_after["tts"])
    voice_a, style_a, k_a, engine_a = V.line_cfg(row_after["tts"], 1)
    key_after = V.cache_key(engine_a, voice_a, style_a, k_a, spoken_after)
    assert key_after == key_before
    assert not V.uses_new_cache(row_after["tts"])

    # 3. mix vẫn là legacy (không C)
    assert row_after["sound"].get("preset_long") != "C"
    assert row_after["sound"].get("preset") != "C"


@pytest.mark.parametrize("b_mod,p_name,rid", [
    ("build_BT04", "plan_long_tt4.json", "L_bud_tt04"),
    ("build_T10_top3", "plan_long_t10_top3.json", "L_fs_t10_top3"),
    ("build_T10_mao", "plan_long_t10_mao.json", "L_fs_t10_mao"),
    ("build_T10_ngaytot", "plan_long_t10_ngaytot.json", "L_fs_t10_ngaytot"),
])
def test_four_builders_rerun_preserves_legacy_tts_and_sound(b_mod, p_name, rid, tmp_path):
    """4 builder chạy lại với plan đã có -> diff tts/sound trước sau = 0."""
    import shutil
    import sys
    sys.path.insert(0, str(ROOT / "output/cl_staging/long"))

    src = ROOT / "output/cl_staging/long" / p_name
    if not src.exists():
        pytest.skip(f"Thiếu file plan {src}")

    tmp_file = tmp_path / p_name
    shutil.copy2(src, tmp_file)

    before_rows = json.loads(tmp_file.read_text(encoding="utf-8"))
    row_before = next(r for r in before_rows if r.get("id") == rid)
    tts_before = json.loads(json.dumps(row_before["tts"]))
    sound_before = json.loads(json.dumps(row_before["sound"]))

    mod = __import__(b_mod)
    HBR.save_plan_rows(tmp_file, mod.row)

    after_rows = json.loads(tmp_file.read_text(encoding="utf-8"))
    row_after = next(r for r in after_rows if r.get("id") == rid)

    # diff tts/sound trước/sau == 0
    assert row_after["tts"] == tts_before
    assert row_after["sound"] == sound_before
    assert not V.uses_new_cache(row_after["tts"])
    assert row_after["sound"].get("preset_long") != "C"
