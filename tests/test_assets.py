"""tests/test_assets.py: Kiểm thử danh mục và tra cứu kho tài sản đa kênh (#47, #95, #95b, #142)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("assets_mod", ROOT / "library" / "tools" / "assets.py")
assets_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets_mod)


def _make_png(w: int, h: int) -> bytes:
    """Tạo header PNG tối thiểu có w, h."""
    import struct
    header = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    ihdr = struct.pack(">I", len(ihdr_data)) + b"IHDR" + ihdr_data + b"\x00\x00\x00\x00"
    return header + ihdr + b"\x00\x00\x00\x00IEND\xaeB`\x82"


def _setup_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Tạo cấu trúc thư mục giả lập không dùng media lớn."""
    repo = tmp_path / "repo"
    repo.mkdir()

    # Kênh giả lập
    channels_dir = repo / "library" / "channels"
    channels_dir.mkdir(parents=True)
    (channels_dir / "fs.yaml").write_text(json.dumps({
        "kenh": "fs",
        "ngach": ["phong_thuy", "tu_vi"],
        "assets": {"nhom_canh": ["la_ban", "ban_tho"]}
    }), encoding="utf-8")
    (channels_dir / "bud.yaml").write_text(json.dumps({
        "kenh": "bud",
        "ngach": ["phat_phap", "loi_phat_day"],
        "assets": {"nhom_canh": ["chua", "tuong_phat"]}
    }), encoding="utf-8")

    # Lexicon
    lex_dir = repo / "library" / "assets" / "lexicon"
    lex_dir.mkdir(parents=True)
    (lex_dir / "chung.json").write_text(json.dumps({
        "muc": [
            {"vi": "chùa", "en": "pagoda", "nhom": "chua"},
            {"vi": "mây", "en": "clouds", "nhom": "may"},
        ]
    }), encoding="utf-8")
    (lex_dir / "fs.json").write_text(json.dumps({
        "muc": [
            {"vi": "la bàn", "en": "compass", "nhom": "la_ban"}
        ]
    }), encoding="utf-8")

    # Taxonomy
    tax_path = repo / "library" / "inventory" / "taxonomy.json"
    tax_path.parent.mkdir(parents=True)
    tax_path.write_text(json.dumps([
        {"id": "kien_truc", "group": "canh", "keywords": ["chùa", "pagoda"]}
    ]), encoding="utf-8")

    # Media dirs
    media_dir = repo / "chunks_cache" / "commons"
    media_dir.mkdir(parents=True)

    # 1. File chùa
    f1 = media_dir / "chua_mot_cot.png"
    f1.write_bytes(_make_png(1920, 1080) + b"_content1")
    (media_dir / "chua_mot_cot.png.json").write_text(json.dumps({
        "file": "File:Chùa Một Cột.png",
        "license": "CC BY-SA 4.0",
        "credit": "Wikimedia Commons"
    }), encoding="utf-8")

    # 2. File la bàn (kênh fs)
    f_fs = media_dir / "la_ban_co.png"
    f_fs.write_bytes(_make_png(1920, 1080) + b"_content_fs")
    (media_dir / "la_ban_co.png.json").write_text(json.dumps({
        "file": "File:La bàn cổ.png",
        "license": "CC BY-SA 4.0",
        "credit": "Wikimedia Commons"
    }), encoding="utf-8")

    # 3. File mây
    f2 = media_dir / "may_troi.png"
    f2.write_bytes(_make_png(1280, 720) + b"_content2")
    (media_dir / "may_troi.png.json").write_text(json.dumps({
        "file": "File:Mây trôi.png",
        "license": "CC0 1.0",
        "credit": "Public Domain"
    }), encoding="utf-8")

    # 4. File trùng nội dung với f1 nhưng ở thư mục khác
    dup_dir = repo / "chunks_cache" / "museum"
    dup_dir.mkdir(parents=True)
    f3 = dup_dir / "chua_mot_cot_dup.png"
    f3.write_bytes(f1.read_bytes())

    # 5. File AI chưa strip_mark
    ai_dir = repo / "output" / "cl_staging" / "grok" / "samples" / "packaging" / "flow_raw"
    ai_dir.mkdir(parents=True)
    f4 = ai_dir / "monk_raw.png"
    f4.write_bytes(_make_png(1080, 1920) + b"_ai_raw")

    manifest = repo / "library" / "assets" / "manifest.jsonl"
    return repo, manifest, f1


def test_scan_tat_dinh(tmp_path: Path):
    """Scan chạy 2 lần ra byte-for-byte trùng nhau hoàn toàn (tính tất định)."""
    repo, manifest, _ = _setup_fixture(tmp_path)
    dirs = [
        "chunks_cache/commons",
        "chunks_cache/museum",
        "output/cl_staging/grok/samples/packaging/flow_raw",
    ]

    stats1 = assets_mod.scan_assets(root=repo, manifest_path=manifest, dirs=dirs)
    content1 = manifest.read_bytes()

    stats2 = assets_mod.scan_assets(root=repo, manifest_path=manifest, dirs=dirs)
    content2 = manifest.read_bytes()

    assert content1 == content2, "Hai lần scan phải ra byte-for-byte trùng nhau"
    assert stats1["total_files"] == 5
    assert stats1["total_assets"] == 4


def test_gop_trung_noi_dung(tmp_path: Path):
    """File trùng nội dung (sha256) ở nhiều thư mục được gộp thành 1 asset với danh sách paths."""
    repo, manifest, f1 = _setup_fixture(tmp_path)
    dirs = [
        "chunks_cache/commons",
        "chunks_cache/museum",
    ]

    stats = assets_mod.scan_assets(root=repo, manifest_path=manifest, dirs=dirs)
    assert stats["duplicate_groups"] == 1

    records = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    f1_sha = hashlib.sha256(f1.read_bytes()).hexdigest()
    f1_rec = next(r for r in records if r["sha256"] == f1_sha)

    # Kiểm tra gộp trùng đường dẫn
    assert len(f1_rec["paths"]) == 2
    assert "chunks_cache/commons/chua_mot_cot.png" in f1_rec["paths"]
    assert "chunks_cache/museum/chua_mot_cot_dup.png" in f1_rec["paths"]
    assert f1_rec["path"] == f1_rec["paths"][0]


def test_find_loc_va_xep_hang(tmp_path: Path):
    """find lọc theo tag, pham_vi, kind, min_w và xếp hạng tất định."""
    repo, manifest, _ = _setup_fixture(tmp_path)
    dirs = ["chunks_cache/commons", "chunks_cache/museum"]
    assets_mod.scan_assets(root=repo, manifest_path=manifest, dirs=dirs)

    # Tìm "chùa", loại img, min-w 1920 cho kênh bud
    res = assets_mod.find_assets(pham_vi="bud", tag="chùa", kind="img", min_w=1920, manifest_path=manifest)
    assert len(res) == 1
    assert "chua" in res[0]["tags"]["core"]
    assert res[0]["w"] == 1920

    # Tìm "la bàn" cho kênh fs
    res_fs = assets_mod.find_assets(pham_vi="fs", tag="la bàn", kind="img", manifest_path=manifest)
    assert len(res_fs) == 1
    assert "la_ban" in res_fs[0]["tags"]["domain"]

    # Tìm với min-w quá lớn -> không có kết quả
    res_empty = assets_mod.find_assets(pham_vi="bud", tag="chùa", kind="img", min_w=3840, manifest_path=manifest)
    assert len(res_empty) == 0

    # Tìm "mây"
    res_may = assets_mod.find_assets(tag="mây", manifest_path=manifest)
    assert len(res_may) == 1
    assert res_may[0]["w"] == 1280


def test_check_bat_file_mat_va_sha_lech(tmp_path: Path):
    """check bắt đúng file mất, sha lệch, giấy phép unknown, ảnh AI chưa strip_mark."""
    repo, manifest, f1 = _setup_fixture(tmp_path)
    dirs = [
        "chunks_cache/commons",
        "chunks_cache/museum",
        "output/cl_staging/grok/samples/packaging/flow_raw",
    ]
    assets_mod.scan_assets(root=repo, manifest_path=manifest, dirs=dirs)

    # Ban đầu: không có file mất, có 1 ảnh AI chưa strip_mark
    rep1 = assets_mod.check_assets(manifest_path=manifest, root=repo)
    assert rep1["missing_files_count"] == 0
    assert rep1["sha_mismatches_count"] == 0
    assert rep1["ai_unstripped_count"] == 1

    # Tạo file mất: xoá file f1
    f1.unlink()
    rep2 = assets_mod.check_assets(manifest_path=manifest, root=repo)
    assert rep2["missing_files_count"] == 1
    assert rep2["status"] == "FAIL"

    # Tạo sha lệch: sửa nội dung file f3 (bản duplicate)
    f3 = repo / "chunks_cache" / "museum" / "chua_mot_cot_dup.png"
    f3.write_bytes(b"corrupted_content")
    rep3 = assets_mod.check_assets(manifest_path=manifest, root=repo)
    assert rep3["sha_mismatches_count"] >= 1
    assert rep3["status"] == "FAIL"


def test_giay_phep_thieu_sidecar_unknown(tmp_path: Path):
    """Kiểm tra quy tắc giấy phép: thiếu sidecar và không có fetcher_policy -> unknown (#95b)."""
    repo = tmp_path / "repo_lic"
    repo.mkdir()

    # 1. beat_assets KHÔNG có sidecar -> unknown
    beat_dir = repo / "chunks_cache" / "beat_assets"
    beat_dir.mkdir(parents=True)
    f_no_sc = beat_dir / "stock_no_sidecar.jpg"
    f_no_sc.write_bytes(_make_png(1280, 720) + b"_nosc")

    # 2. beat_assets CÓ sidecar provider: pexels -> Pexels License (basis: sidecar)
    f_sc = beat_dir / "stock_with_sidecar.jpg"
    f_sc.write_bytes(_make_png(1280, 720) + b"_sc")
    (beat_dir / "stock_with_sidecar.source.json").write_text(json.dumps({
        "provider": "pexels",
        "author": "Test Author",
        "id": "12345"
    }), encoding="utf-8")

    # 3. relic không có sidecar giấy phép và không có fetcher_policy -> unknown
    relic_dir = repo / "chunks_cache" / "relic"
    relic_dir.mkdir(parents=True)
    f_relic = relic_dir / "relic_item_fg.png"
    f_relic.write_bytes(_make_png(1280, 720) + b"_relic")

    # 4. museum: thiếu sidecar -> unknown; có sidecar từ fetcher -> CC0 1.0 (basis: fetcher_policy)
    mus_dir = repo / "chunks_cache" / "museum"
    mus_dir.mkdir(parents=True)
    f_mus_nosc = mus_dir / "cma_artwork_nosc.jpg"
    f_mus_nosc.write_bytes(_make_png(1280, 720) + b"_mus_nosc")

    f_mus_sc = mus_dir / "cma_artwork_sc.jpg"
    f_mus_sc.write_bytes(_make_png(1280, 720) + b"_mus_sc")
    (mus_dir / "cma_artwork_sc.json").write_text(json.dumps({
        "credit": "Sun Bodhisattva — Cleveland Museum of Art (CC0)",
        "img": "https://openaccess-cdn.clevelandart.org/print.jpg",
        "title": "Sun Bodhisattva"
    }), encoding="utf-8")

    manifest = repo / "manifest.jsonl"
    assets_mod.scan_assets(root=repo, manifest_path=manifest, dirs=[
        "chunks_cache/beat_assets",
        "chunks_cache/relic",
        "chunks_cache/museum",
    ])

    records = {r["path"]: r for r in [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]}

    # Kiểm tra 1: beat_assets thiếu sidecar
    r_nosc = records["chunks_cache/beat_assets/stock_no_sidecar.jpg"]
    assert r_nosc["license"]["type"] == "unknown"
    assert r_nosc["license"]["basis"] == "unknown"
    assert r_nosc["license"]["basis_ref"] is None

    # Kiểm tra 2: beat_assets có sidecar
    r_sc = records["chunks_cache/beat_assets/stock_with_sidecar.jpg"]
    assert r_sc["license"]["type"] == "Pexels License"
    assert r_sc["license"]["basis"] == "sidecar"
    assert r_sc["license"]["commercial_allowed"] is True

    # Kiểm tra 3: relic thiếu metadata giấy phép
    r_relic = records["chunks_cache/relic/relic_item_fg.png"]
    assert r_relic["license"]["type"] == "unknown"
    assert r_relic["license"]["basis"] == "unknown"

    # Kiểm tra 4a: museum thiếu sidecar -> unknown (không suy từ thư mục)
    r_mus_nosc = records["chunks_cache/museum/cma_artwork_nosc.jpg"]
    assert r_mus_nosc["license"]["type"] == "unknown"
    assert r_mus_nosc["license"]["basis"] == "unknown"
    assert r_mus_nosc["license"]["basis_ref"] is None

    # Kiểm tra 4b: museum có sidecar từ fetcher -> CC0 1.0 (basis: fetcher_policy)
    r_mus_sc = records["chunks_cache/museum/cma_artwork_sc.jpg"]
    assert r_mus_sc["license"]["type"] == "CC0 1.0"
    assert r_mus_sc["license"]["basis"] == "fetcher_policy"
    assert r_mus_sc["license"]["basis_ref"] == "hf_museum.py:115-128"


def test_manifest_for_plan_mau(tmp_path: Path):
    """manifest-for gom đủ file của plan và xuất định dạng rsync + sha256sum."""
    repo, _, _ = _setup_fixture(tmp_path)
    plan_id = "L_test_01"

    out_dir = repo / "output" / "cl_staging" / "long" / "out"
    out_dir.mkdir(parents=True)
    p_json = out_dir / f"{plan_id}.json"
    p_json.write_text(json.dumps({"id": plan_id, "script": ["Câu 1"]}), encoding="utf-8")
    p_txt = out_dir / f"{plan_id}.txt"
    p_txt.write_text("Câu 1", encoding="utf-8")
    p_wav = out_dir / f"{plan_id}.wav"
    p_wav.write_bytes(b"RIFF_FAKE_WAV")

    hf_assets = repo / "hyperframes_short" / "assets"
    hf_assets.mkdir(parents=True)
    img_asset = hf_assets / f"precheck_{plan_id}_s1.jpg"
    img_asset.write_bytes(b"FAKE_IMG_JPG")

    bgm_dir = repo / "bgm"
    bgm_dir.mkdir(parents=True)
    bgm_file = bgm_dir / "ambient.mp3"
    bgm_file.write_bytes(b"FAKE_BGM_MP3")

    p_render = out_dir / f"{plan_id}.render.json"
    p_render.write_text(json.dumps({
        "bgm_used": ["ambient.mp3"]
    }), encoding="utf-8")

    # Gọi manifest_for
    items = assets_mod.manifest_for_plan(plan_id, root=repo)
    paths = [it["path"] for it in items]
    assert f"output/cl_staging/long/out/{plan_id}.json" in paths
    assert f"output/cl_staging/long/out/{plan_id}.txt" in paths
    assert f"output/cl_staging/long/out/{plan_id}.wav" in paths
    assert f"output/cl_staging/long/out/{plan_id}.render.json" in paths
    assert f"hyperframes_short/assets/precheck_{plan_id}_s1.jpg" in paths
    assert "bgm/ambient.mp3" in paths

    # Kiểm tra sha256
    for it in items:
        actual_sha = hashlib.sha256((repo / it["path"]).read_bytes()).hexdigest()
        assert it["sha256"] == actual_sha

    # Kiểm tra xuất file sha256 và files
    out_sha = tmp_path / "plan.sha256"
    assets_mod.manifest_for_plan(plan_id, root=repo, out_format="sha256", out_path=out_sha)
    assert len(out_sha.read_text().splitlines()) == len(items)

    out_files = tmp_path / "plan.files"
    assets_mod.manifest_for_plan(plan_id, root=repo, out_format="files", out_path=out_files)
    assert len(out_files.read_text().splitlines()) == len(items)


def test_manifest_for_phu_thuoc_render(tmp_path: Path):
    """manifest-for gom đầy đủ phụ thuộc render: TTS chunks, cache 2.5D, fonts, SFX/channel, composition (#95b)."""
    repo = tmp_path / "repo_full_plan"
    repo.mkdir()

    plan_id = "L_fs_full01"
    out_dir = repo / "output" / "cl_staging" / "long" / "out"
    out_dir.mkdir(parents=True)

    # 1. Output files
    (out_dir / f"{plan_id}.json").write_text(json.dumps({
        "id": plan_id,
        "style": "studio_long",
        "theme": "son-mai",
        "series": "fs",
        "script": ["Câu đầu tiên", "Câu thứ hai"],
        "tts": {"voice": "Tuyen", "tempo": 1.0}
    }), encoding="utf-8")
    (out_dir / f"{plan_id}.txt").write_text("Câu đầu tiên\nCâu thứ hai\n", encoding="utf-8")
    (out_dir / f"{plan_id}.wav").write_bytes(b"WAV_DATA")
    (out_dir / f"{plan_id}.render.json").write_text(json.dumps({
        "bgm_used": ["deliberate_thought.mp3"],
        "sound": "foley-v1"
    }), encoding="utf-8")

    # 2. TTS chunk cache
    voice_cache_dir = repo / "chunks_cache" / "voice_lines"
    voice_cache_dir.mkdir(parents=True)
    # Giả lập chunk key
    import hf_voice
    spec = {"voice": "Tuyen", "tempo": 1.0}
    k1 = hf_voice.cache_key("v3", "Tuyen", "doc_truyen", 1.0, hf_voice.spoken_text("Câu đầu tiên", spec))
    k2 = hf_voice.cache_key("v3", "Tuyen", "doc_truyen", 1.0, hf_voice.spoken_text("Câu thứ hai", spec))
    chunk1 = voice_cache_dir / f"{k1}.wav"
    chunk2 = voice_cache_dir / f"{k2}.wav"
    chunk1.write_bytes(b"TTS_CHUNK_1")
    chunk2.write_bytes(b"TTS_CHUNK_2")

    # 3. Media precheck + Depth 2.5D cache
    hf_assets = repo / "hyperframes_short" / "assets"
    hf_assets.mkdir(parents=True)
    img_pre = hf_assets / f"precheck_full01_s1.jpg"
    img_content = _make_png(1920, 1080) + b"_depth_target"
    img_pre.write_bytes(img_content)

    depth_dir = repo / "chunks_cache" / "depth"
    depth_dir.mkdir(parents=True)
    mkey = hashlib.sha1(img_content).hexdigest()[:16]
    (depth_dir / f"{mkey}_bg.jpg").write_bytes(b"DEPTH_BG")
    (depth_dir / f"{mkey}_fg.png").write_bytes(b"DEPTH_FG")
    (depth_dir / f"{mkey}.cover").write_text("0.45", encoding="utf-8")

    # 4. BGM
    bgm_dir = repo / "bgm"
    bgm_dir.mkdir(parents=True)
    (bgm_dir / "deliberate_thought.mp3").write_bytes(b"BGM_MUSIC")

    # 5. Channel sound & foley config
    ch_dir = repo / "library" / "channels"
    ch_dir.mkdir(parents=True)
    (ch_dir / "fs.yaml").write_text(json.dumps({"kenh": "fs", "sound": {"preset_long": "C"}}), encoding="utf-8")

    # 6. Fonts & Composition
    comp_dir = repo / "hyperframes_short" / "compositions"
    comp_dir.mkdir(parents=True)
    (comp_dir / "studio_long.html").write_text("<html><!--HFS-HEAD--></html>", encoding="utf-8")

    theme_dir = repo / "hyperframes_short" / "studio" / "themes"
    theme_dir.mkdir(parents=True)
    (theme_dir / "son-mai.json").write_text(json.dumps({
        "id": "son-mai",
        "vars": {"font-display": '"Playfair Display", serif'}
    }), encoding="utf-8")

    fonts_dir = repo / "hyperframes_short" / "studio" / "fonts"
    fonts_dir.mkdir(parents=True)
    (fonts_dir / "faces.json").write_text(json.dumps([
        {"family": "Playfair Display", "file": "fonts/Playfair_Display/font1.woff2"}
    ]), encoding="utf-8")
    (fonts_dir / "Playfair_Display").mkdir(parents=True)
    (fonts_dir / "Playfair_Display" / "font1.woff2").write_bytes(b"WOFF2_FONT")

    studio_dir = repo / "hyperframes_short" / "studio"
    (studio_dir / "kit.css").write_text("/* kit */", encoding="utf-8")
    (studio_dir / "core.js").write_text("// core", encoding="utf-8")
    dev_dir = studio_dir / "devices"
    dev_dir.mkdir(parents=True)
    (dev_dir / "card.js").write_text("// card", encoding="utf-8")

    # Thu thập manifest
    items = assets_mod.manifest_for_plan(plan_id, root=repo)
    paths = {it["path"] for it in items}

    # Kiểm tra đủ 7 nhóm phụ thuộc
    assert f"output/cl_staging/long/out/{plan_id}.json" in paths
    assert f"chunks_cache/voice_lines/{k1}.wav" in paths
    assert f"chunks_cache/voice_lines/{k2}.wav" in paths
    assert "hyperframes_short/assets/precheck_full01_s1.jpg" in paths
    assert f"chunks_cache/depth/{mkey}_bg.jpg" in paths
    assert f"chunks_cache/depth/{mkey}_fg.png" in paths
    assert f"chunks_cache/depth/{mkey}.cover" in paths
    assert "bgm/deliberate_thought.mp3" in paths
    assert "library/channels/fs.yaml" in paths
    assert "hyperframes_short/compositions/studio_long.html" in paths
    assert "hyperframes_short/studio/themes/son-mai.json" in paths
    assert "hyperframes_short/studio/fonts/Playfair_Display/font1.woff2" in paths
    assert "hyperframes_short/studio/kit.css" in paths
    assert "hyperframes_short/studio/core.js" in paths
    assert "hyperframes_short/studio/devices/card.js" in paths


def test_manifest_for_tts_missing_raises(tmp_path: Path):
    """TTS cache key thiếu -> ghi vào missing và manifest_for_plan raise MissingAssetsError / CLI exit 1 (#95c)."""
    repo = tmp_path / "repo_missing_tts"
    repo.mkdir()

    plan_id = "L_fs_test_missing"
    out_dir = repo / "output" / "cl_staging" / "long" / "out"
    out_dir.mkdir(parents=True)

    (out_dir / f"{plan_id}.json").write_text(json.dumps({
        "id": plan_id,
        "style": "studio_long",
        "theme": "son-mai",
        "series": "fs",
        "script": ["Câu số một", "Câu số hai"],
        "tts": {"voice": "Tuyen", "tempo": 1.0}
    }), encoding="utf-8")
    (out_dir / f"{plan_id}.txt").write_text("Câu số một\nCâu số hai\n", encoding="utf-8")
    (out_dir / f"{plan_id}.wav").write_bytes(b"WAV_DATA")

    voice_cache_dir = repo / "chunks_cache" / "voice_lines"
    voice_cache_dir.mkdir(parents=True)
    import hf_voice
    spec = {"voice": "Tuyen", "tempo": 1.0}
    k1 = hf_voice.cache_key("v3", "Tuyen", "doc_truyen", 1.0, hf_voice.spoken_text("Câu số một", spec))
    k2 = hf_voice.cache_key("v3", "Tuyen", "doc_truyen", 1.0, hf_voice.spoken_text("Câu số hai", spec))

    # Chỉ ghi chunk 1, cố tình thiếu chunk 2
    (voice_cache_dir / f"{k1}.wav").write_bytes(b"TTS_CHUNK_1")

    # manifest_for_plan phải ném MissingAssetsError, danh sách missing chứa đúng key thiếu
    with pytest.raises(assets_mod.MissingAssetsError) as exc_info:
        assets_mod.manifest_for_plan(plan_id, root=repo)

    missing_list = exc_info.value.missing
    assert len(missing_list) == 1
    assert missing_list[0]["type"] == "tts_chunk"
    assert missing_list[0]["key"] == k2
    assert f"{k2}.wav" in missing_list[0]["path"]
    assert missing_list[0]["line"] == 2

    # CLI manifest-for phải exit code 1
    ret = assets_mod.main(["manifest-for", plan_id, "--root", str(repo)])
    assert ret == 1


def test_manifest_for_depth_transformed_local_image(tmp_path: Path):
    """Manifest tính đúng key depth cho ảnh local đã qua biến đổi _frame_local_image (Ticket #95d)."""
    import hyperframes_bridge as HB
    from PIL import Image

    repo = tmp_path / "repo_depth_transform"
    repo.mkdir()

    plan_id = "L_fs_depth_trans"
    out_dir = repo / "output" / "cl_staging" / "long" / "out"
    out_dir.mkdir(parents=True)

    ai_media_dir = repo / "output" / "cl_staging" / "long" / "research" / "ai_media"
    ai_media_dir.mkdir(parents=True)
    src_img = ai_media_dir / "portrait_raw.jpg"

    # Tạo ảnh dọc 600x1000
    im = Image.new("RGB", (600, 1000), color=(180, 120, 80))
    im.save(src_img, "JPEG")
    raw_key = hashlib.sha1(src_img.read_bytes()).hexdigest()[:16]

    # Biến đổi qua _frame_local_image
    framed_tmp = tmp_path / "framed.jpg"
    HB._frame_local_image(src_img, framed_tmp, crop=[0.1, 0.2, 0.7], landscape=True)
    transformed_key = hashlib.sha1(framed_tmp.read_bytes()).hexdigest()[:16]
    assert transformed_key != raw_key, "Ảnh biến đổi phải có SHA1 khác ảnh gốc"

    # Lưu cache depth theo transformed_key
    depth_dir = repo / "chunks_cache" / "depth"
    depth_dir.mkdir(parents=True)
    (depth_dir / f"{transformed_key}_bg.jpg").write_bytes(b"TRANS_BG")
    (depth_dir / f"{transformed_key}_fg.png").write_bytes(b"TRANS_FG")
    (depth_dir / f"{transformed_key}.cover").write_text("0.35", encoding="utf-8")

    # Plan khai báo layout: depth và path tới ảnh local
    (out_dir / f"{plan_id}.json").write_text(json.dumps({
        "id": plan_id,
        "style": "studio_long",
        "theme": "son-mai",
        "series": "fs",
        "script": ["Một câu thử nghiệm"],
        "tts": {"voice": "Tuyen", "tempo": 1.0},
        "media": {
            "1": {
                "kind": "local",
                "path": "output/cl_staging/long/research/ai_media/portrait_raw.jpg",
                "layout": "depth",
                "crop": [0.1, 0.2, 0.7]
            }
        }
    }), encoding="utf-8")
    (out_dir / f"{plan_id}.txt").write_text("Một câu thử nghiệm\n", encoding="utf-8")
    (out_dir / f"{plan_id}.wav").write_bytes(b"WAV_DATA")

    voice_cache_dir = repo / "chunks_cache" / "voice_lines"
    voice_cache_dir.mkdir(parents=True)
    import hf_voice
    spec = {"voice": "Tuyen", "tempo": 1.0}
    k1 = hf_voice.cache_key("v3", "Tuyen", "doc_truyen", 1.0, hf_voice.spoken_text("Một câu thử nghiệm", spec))
    (voice_cache_dir / f"{k1}.wav").write_bytes(b"TTS_CHUNK_1")

    items = assets_mod.manifest_for_plan(plan_id, root=repo)
    paths = {it["path"] for it in items}

    # Manifest phải gom đúng cache depth của transformed_key
    assert f"chunks_cache/depth/{transformed_key}_bg.jpg" in paths
    assert f"chunks_cache/depth/{transformed_key}_fg.png" in paths
    assert f"chunks_cache/depth/{transformed_key}.cover" in paths


def test_manifest_for_stock_cache(tmp_path: Path):
    """Manifest gom đủ stock image + sidecar json và stock video (Ticket #95e)."""
    import hyperframes_bridge as HB
    import stock_image
    import asset_generation

    repo = tmp_path / "repo_stock"
    repo.mkdir()

    plan_id = "L_fs_stock_test"
    out_dir = repo / "output" / "cl_staging" / "long" / "out"
    out_dir.mkdir(parents=True)

    img_q = "rice field peaceful"
    vid_q = "rain falling on rice field"

    domain = "FS"
    orientation = "landscape"

    clean_img_q = HB.sanitize_query(img_q, domain)
    img_key = f"{clean_img_q}|{orientation}"
    img_h = stock_image._query_hash(img_key)

    clean_vid_q = HB.sanitize_query(vid_q, domain)
    vid_h = asset_generation._prompt_hash(clean_vid_q)

    beat_dir = repo / "chunks_cache" / "beat_assets"
    beat_dir.mkdir(parents=True)

    img_file = beat_dir / f"img_{img_h}.jpg"
    meta_file = beat_dir / f"img_{img_h}.source.json"
    vid_file = beat_dir / f"vid_{vid_h}.mp4"

    img_file.write_bytes(b"STOCK_IMAGE_DATA")
    meta_file.write_text(json.dumps({"url": "http://example.com/img.jpg", "query": img_q}), encoding="utf-8")
    vid_file.write_bytes(b"STOCK_VIDEO_DATA")

    (out_dir / f"{plan_id}.json").write_text(json.dumps({
        "id": plan_id,
        "style": "studio_long",
        "theme": "son-mai",
        "series": "fs",
        "script": ["Câu một", "Câu hai"],
        "tts": {"voice": "Tuyen", "tempo": 1.0},
        "media": {
            "1": {"kind": "image", "query": img_q},
            "2": {"kind": "video", "query": vid_q},
        }
    }), encoding="utf-8")
    (out_dir / f"{plan_id}.txt").write_text("Câu một\nCâu hai\n", encoding="utf-8")
    (out_dir / f"{plan_id}.wav").write_bytes(b"WAV_DATA")

    voice_cache_dir = repo / "chunks_cache" / "voice_lines"
    voice_cache_dir.mkdir(parents=True)
    import hf_voice
    spec = {"voice": "Tuyen", "tempo": 1.0}
    k1 = hf_voice.cache_key("v3", "Tuyen", "doc_truyen", 1.0, hf_voice.spoken_text("Câu một", spec))
    k2 = hf_voice.cache_key("v3", "Tuyen", "doc_truyen", 1.0, hf_voice.spoken_text("Câu hai", spec))
    (voice_cache_dir / f"{k1}.wav").write_bytes(b"TTS_1")
    (voice_cache_dir / f"{k2}.wav").write_bytes(b"TTS_2")

    items = assets_mod.manifest_for_plan(plan_id, root=repo)
    paths = {it["path"] for it in items}

    assert f"chunks_cache/beat_assets/img_{img_h}.jpg" in paths
    assert f"chunks_cache/beat_assets/img_{img_h}.source.json" in paths
    assert f"chunks_cache/beat_assets/vid_{vid_h}.mp4" in paths


def test_resolve_stock_cache_real_function(tmp_path: Path):
    """Kiểm tra resolve_stock_image_cache và resolve_stock_video_cache gọi hàm thật (Ticket #95f)."""
    import stock_image
    import asset_generation

    repo = tmp_path / "repo_cache_test"
    beat_dir = repo / "chunks_cache" / "beat_assets"
    beat_dir.mkdir(parents=True)

    img_q = "temple lotus sunrise"
    vid_q = "drone water fall vietnam"

    key = f"{img_q}|landscape"
    h_img = stock_image._query_hash(key)
    h_vid = asset_generation._prompt_hash(vid_q)

    img_p = beat_dir / f"img_{h_img}.jpg"
    meta_p = beat_dir / f"img_{h_img}.source.json"
    vid_p = beat_dir / f"vid_{h_vid}.mp4"

    # Khi file chưa có -> is_hit = False
    p_img, p_meta, hit_img = assets_mod.resolve_stock_image_cache(img_q, orientation="landscape", root=repo)
    assert not hit_img
    assert p_img == img_p
    assert p_meta == meta_p

    p_vid, hit_vid = assets_mod.resolve_stock_video_cache(vid_q, root=repo)
    assert not hit_vid
    assert p_vid == vid_p

    # Khi file có sẵn -> tra qua get_or_fetch thật (is_hit = True)
    img_p.write_bytes(b"TEST_IMG")
    meta_p.write_text("{}", encoding="utf-8")
    vid_p.write_bytes(b"TEST_VID")

    p_img, p_meta, hit_img = assets_mod.resolve_stock_image_cache(img_q, orientation="landscape", root=repo)
    assert hit_img
    assert p_img == img_p
    assert p_meta == meta_p

    p_vid, hit_vid = assets_mod.resolve_stock_video_cache(vid_q, root=repo)
    assert hit_vid
    assert p_vid == vid_p

    # Khi module có cache_path_for (mô phỏng sau khi Lead gộp hàm)
    orig_img_cpf = getattr(stock_image, "cache_path_for", None)
    orig_vid_cpf = getattr(asset_generation, "cache_path_for", None)
    try:
        stock_image.cache_path_for = lambda q, orientation="portrait": stock_image.CACHE_DIR / f"img_{stock_image._query_hash(q if orientation=='portrait' else f'{q}|{orientation}')}.jpg"
        asset_generation.cache_path_for = lambda q: asset_generation.ASSET_CACHE_DIR / f"vid_{asset_generation._prompt_hash(q)}.mp4"

        p_img, p_meta, hit_img = assets_mod.resolve_stock_image_cache(img_q, orientation="landscape", root=repo)
        assert hit_img
        assert p_img == img_p

        p_vid, hit_vid = assets_mod.resolve_stock_video_cache(vid_q, root=repo)
        assert hit_vid
        assert p_vid == vid_p
    finally:
        if orig_img_cpf is not None:
            stock_image.cache_path_for = orig_img_cpf
        else:
            delattr(stock_image, "cache_path_for")
        if orig_vid_cpf is not None:
            asset_generation.cache_path_for = orig_vid_cpf
        else:
            delattr(asset_generation, "cache_path_for")


def test_code_khong_nhanh_kenh():
    """Kiểm tra luật thiết kế: code không được gõ cứng if kenh == 'fs' hay 'bud'."""
    src = (ROOT / "library" / "tools" / "assets.py").read_text(encoding="utf-8")
    assert not re.search(r"if\s+kenh\s*==", src)
    assert not re.search(r"""==\s*['"]fs['"]""", src)
    assert not re.search(r"""==\s*['"]bud['"]""", src)
    assert "openai" not in src and "anthropic" not in src


def _write_channels(repo: Path) -> None:
    ch = repo / "library" / "channels"
    ch.mkdir(parents=True, exist_ok=True)
    (ch / "mim.yaml").write_text(json.dumps({"kenh": "mim", "kho_loc": {
        "license_cho_phep": ["PD", "CC0", "CC BY"], "tag_cam": ["khung hình phim"]}}, ensure_ascii=False), encoding="utf-8")
    (ch / "ck.yaml").write_text(json.dumps({"kenh": "ck", "kho_loc": {
        "tag_cam": ["logo", "chữ thương hiệu", "biển hiệu", "ngân hàng", "chứng khoán", "hãng xe", "mã cổ phiếu"]}}, ensure_ascii=False), encoding="utf-8")
    (ch / "_mau.yaml").write_text("{}", encoding="utf-8")
    (ch / "lich_su.yaml").write_text(json.dumps({"kenh": "lich_su", "ngach": ["lich_su"]}), encoding="utf-8")


def test_pham_vi_tu_channels(tmp_path: Path):
    """pham_vi = id kênh yaml (bỏ file mẫu bắt đầu bằng _) + chung."""
    repo, _, _ = _setup_fixture(tmp_path)
    _write_channels(repo)
    channels = assets_mod.load_channels(repo / "library" / "channels")
    ids = assets_mod.pham_vi_hop_le(channels)
    assert "fs" in ids
    assert "bud" in ids
    assert "mim" in ids
    assert "ck" in ids
    assert "chung" in ids
    assert "lich_su" in ids
    assert "ten_kenh" not in ids
    stems = {ch.get("stem") for ch in channels}
    assert "_mau" not in stems
    assert all(not str(ch.get("stem") or "").startswith("_") for ch in channels)


def test_find_kenh_truoc_chung_fallback(tmp_path: Path):
    """find --pham-vi kênh trả ảnh kênh trước, rồi chung; ghi hang_pham_vi."""
    repo, manifest, _ = _setup_fixture(tmp_path)
    dirs = ["chunks_cache/commons", "chunks_cache/museum"]
    assets_mod.scan_assets(root=repo, manifest_path=manifest, dirs=dirs)

    res = assets_mod.find_assets(pham_vi="bud", manifest_path=manifest, root=repo)
    hangs = [r["hang_pham_vi"] for r in res]
    assert "kenh" in hangs
    assert "chung" in hangs
    first_chung = next(i for i, h in enumerate(hangs) if h == "chung")
    last_kenh = max(i for i, h in enumerate(hangs) if h == "kenh")
    assert last_kenh < first_chung
    assert all(r["pham_vi"] == "bud" or "chung" in str(r["pham_vi"]) for r in res)


def test_grokbot_chi_nhan_lead_da_xem(tmp_path: Path):
    """Scan GrokBot: chỉ lô có LEAD_DA_XEM; source=grokbot; lưu prompt; kênh từ tên lô."""
    repo, manifest, _ = _setup_fixture(tmp_path)
    ok = repo / "output" / "cl_staging" / "grokbot" / "bud_ok_lo"
    (ok / "out").mkdir(parents=True)
    (ok / "LEAD_DA_XEM").write_text("ok\n", encoding="utf-8")
    (ok / "out" / "ai_01.png").write_bytes(_make_png(1080, 1920) + b"_gb_ok")
    (ok / "prompts.md").write_text(
        "## ai_01.png — Đức Phật ngồi dưới cây\n"
        "Prompt (EN): The Buddha seated under a bodhi tree, painterly editorial illustration, 9:16.\n"
        "Khung: dọc 9:16.\n",
        encoding="utf-8",
    )
    skip = repo / "output" / "cl_staging" / "grokbot" / "bud_skip_lo"
    (skip / "out").mkdir(parents=True)
    (skip / "out" / "ai_01.png").write_bytes(_make_png(1080, 1920) + b"_gb_skip")
    (skip / "prompts.md").write_text("## ai_01.png\nPrompt (EN): skipped\n", encoding="utf-8")

    stats = assets_mod.scan_assets(
        root=repo,
        manifest_path=manifest,
        dirs=["chunks_cache/commons", "output/cl_staging/grokbot"],
    )
    assert "bud_skip_lo" in stats["grokbot_skipped_batches"]
    assert stats["grokbot_files"] == 1
    records = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    gb = [r for r in records if (r.get("source") or {}).get("type") == "grokbot"]
    assert len(gb) == 1
    rec = gb[0]
    assert rec["ai_generated"] is True
    assert rec["source"]["type"] == "grokbot"
    assert "Buddha seated" in (rec.get("prompt") or "")
    assert rec["pham_vi"] == "bud"
    skip_paths = " ".join(p for r in records for p in (r.get("paths") or [r.get("path")]))
    assert "bud_skip_lo" not in skip_paths


def test_add_va_mark_used_exclude_days(tmp_path: Path):
    """add nhập 1 ảnh; mark-used + find --exclude-used-days 7 loại đúng kênh trong cửa sổ."""
    repo, manifest, _ = _setup_fixture(tmp_path)
    assets_mod.scan_assets(root=repo, manifest_path=manifest, dirs=["chunks_cache/commons"])
    new_dir = repo / "output" / "cl_staging" / "grokbot" / "fs_new" / "out"
    new_dir.mkdir(parents=True)
    (new_dir.parent / "LEAD_DA_XEM").write_text("ok\n", encoding="utf-8")
    fnew = new_dir / "la_ban_moi.png"
    fnew.write_bytes(_make_png(800, 600) + b"_add_new")

    from PIL import Image
    Image.new("RGB", (800, 600), "red").save(fnew)
    rec = assets_mod.add_asset(
        fnew,
        pham_vi="fs",
        prompt="A Vietnamese geomantic compass on dark wood, photograph",
        tags=["la_ban"],
        root=repo,
        manifest_path=manifest,
    )
    assert rec["pham_vi"] == "fs"
    assert rec["ai_generated"] is True
    aid = rec["asset_id"]

    today = date(2026, 11, 4)
    assets_mod.mark_used(aid, "V_fs_test1", "fs", "2026-11-03", manifest_path=manifest)

    gone = assets_mod.find_assets(
        pham_vi="fs",
        tag="la_ban",
        exclude_used_days=7,
        channel="fs",
        today=today,
        manifest_path=manifest,
        root=repo,
    )
    assert all(r["asset_id"] != aid for r in gone)

    still = assets_mod.find_assets(
        pham_vi="fs",
        tag="la_ban",
        exclude_used_days=7,
        channel="bud",
        today=today,
        manifest_path=manifest,
        root=repo,
    )
    assert any(r["asset_id"] == aid for r in still)

    old_ok = assets_mod.find_assets(
        pham_vi="fs",
        tag="la_ban",
        exclude_used_days=7,
        channel="fs",
        today=date(2026, 11, 20),
        manifest_path=manifest,
        root=repo,
    )
    assert any(r["asset_id"] == aid for r in old_ok)


def test_kho_loc_mim_license_va_ck_tag(tmp_path: Path):
    """find --pham-vi mim|ck tự áp kho_loc, kể cả khi fallback sang chung."""
    repo, manifest, _ = _setup_fixture(tmp_path)
    _write_channels(repo)
    records = [
        {
            "asset_id": "a" * 16,
            "kind": "img",
            "path": "x/pd.png",
            "paths": ["x/pd.png"],
            "sha256": "a" * 64,
            "byte": 1,
            "w": 1920,
            "h": 1080,
            "pham_vi": "chung",
            "tags": {"core": ["may"], "domain": []},
            "source": {"type": "commons", "ref": "pd.png"},
            "license": {"type": "CC0 1.0", "commercial_allowed": True, "basis": "sidecar"},
            "ai_generated": False,
            "video_da_dung": [],
        },
        {
            "asset_id": "b" * 16,
            "kind": "img",
            "path": "x/bysa.png",
            "paths": ["x/bysa.png"],
            "sha256": "b" * 64,
            "byte": 1,
            "w": 1920,
            "h": 1080,
            "pham_vi": "chung",
            "tags": {"core": ["may"], "domain": []},
            "source": {"type": "commons", "ref": "bysa.png"},
            "license": {"type": "CC BY-SA 4.0", "commercial_allowed": True, "basis": "sidecar"},
            "ai_generated": False,
            "video_da_dung": [],
        },
        {
            "asset_id": "c" * 16,
            "kind": "img",
            "path": "x/logo.png",
            "paths": ["x/logo.png"],
            "sha256": "c" * 64,
            "byte": 1,
            "w": 1920,
            "h": 1080,
            "pham_vi": "chung",
            "tags": {"core": ["logo", "bien_hieu"], "domain": []},
            "source": {"type": "internal", "ref": "logo.png"},
            "license": {"type": "CC0 1.0", "commercial_allowed": True, "basis": "sidecar"},
            "ai_generated": False,
            "video_da_dung": [],
        },
        {
            "asset_id": "d" * 16,
            "kind": "img",
            "path": "x/film.png",
            "paths": ["x/film.png"],
            "sha256": "d" * 64,
            "byte": 1,
            "w": 1920,
            "h": 1080,
            "pham_vi": "chung",
            "tags": {"core": ["khung_hinh_phim"], "domain": []},
            "source": {"type": "internal", "ref": "film.png"},
            "license": {"type": "Public Domain", "commercial_allowed": True, "basis": "sidecar"},
            "ai_generated": False,
            "video_da_dung": [],
        },
    ]
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")

    mim = assets_mod.find_assets(pham_vi="mim", manifest_path=manifest, root=repo)
    mim_ids = {r["asset_id"] for r in mim}
    assert "a" * 16 in mim_ids
    assert "b" * 16 not in mim_ids
    assert "d" * 16 not in mim_ids

    ck = assets_mod.find_assets(pham_vi="ck", manifest_path=manifest, root=repo)
    ck_ids = {r["asset_id"] for r in ck}
    assert "a" * 16 in ck_ids
    assert "c" * 16 not in ck_ids


def test_merge_external_gop_sha_khong_nhan_doi(tmp_path: Path):
    """merge-external: remote + host, giữ license/source, trùng sha256 thì gộp."""
    repo, manifest, f1 = _setup_fixture(tmp_path)
    _write_channels(repo)
    assets_mod.scan_assets(root=repo, manifest_path=manifest, dirs=["chunks_cache/commons"])
    local = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    local_one = local[0]
    sha_dup = local_one["sha256"]
    n_before = len(local)

    ext = tmp_path / "mim_manifest.jsonl"
    new_sha = "e" * 64
    incoming = [
        {
            "asset_id": sha_dup[:16],
            "kind": "img",
            "path": "D:/Mimck/assets/dup.png",
            "paths": ["D:/Mimck/assets/dup.png"],
            "sha256": sha_dup,
            "byte": 10,
            "w": 100,
            "h": 100,
            "pham_vi": "mim",
            "tags": {"core": [], "domain": []},
            "source": {"type": "commons", "ref": "keep-me"},
            "license": {"type": "CC0 1.0", "commercial_allowed": True, "basis": "sidecar"},
            "ai_generated": False,
            "video_da_dung": [],
        },
        {
            "asset_id": new_sha[:16],
            "kind": "img",
            "path": "D:/Mimck/assets/new.png",
            "paths": ["D:/Mimck/assets/new.png"],
            "sha256": new_sha,
            "byte": 20,
            "w": 640,
            "h": 480,
            "pham_vi": "mim",
            "tags": {"core": ["sen"], "domain": []},
            "source": {"type": "museum", "ref": "ext-new"},
            "license": {"type": "CC0 1.0", "commercial_allowed": True, "basis": "sidecar"},
            "ai_generated": False,
            "video_da_dung": [],
        },
    ]
    ext.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in incoming), encoding="utf-8")

    stats = assets_mod.merge_external(ext, pham_vi="mim", host="windows", manifest_path=manifest, root=repo)
    assert stats["added"] == 1
    assert stats["merged"] == 1
    assert stats["total"] == n_before + 1

    after = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_sha = {r["sha256"]: r for r in after}
    merged = by_sha[sha_dup]
    assert "D:/Mimck/assets/dup.png" in merged["paths"]
    assert merged["source"]["ref"] == local_one["source"]["ref"]
    remote = by_sha[new_sha]
    assert remote["host"] == "windows"
    assert remote["path_kind"] == "remote"
    assert remote["source"]["type"] == "museum"
    assert remote["ai_generated"] is False
    assert remote["license"]["type"] == "CC0 1.0"
    assert not (repo / "D:/Mimck/assets/new.png").exists()

    rep = assets_mod.check_assets(manifest_path=manifest, root=repo)
    assert all(m["path"] != "D:/Mimck/assets/new.png" for m in rep["missing_files"])


def test_add_anh_that_co_prompt_khong_thanh_ai(tmp_path: Path):
    """Ảnh thật nhập kèm prompt mô tả + --real: không bị gắn ai_generated."""
    repo, manifest, _ = _setup_fixture(tmp_path)
    d = repo / "output" / "cl_staging" / "anh_that"
    d.mkdir(parents=True)
    f = d / "tuong.png"
    f.write_bytes(_make_png(640, 480) + b"_real")
    from PIL import Image
    Image.new("RGB", (640, 480), "red").save(f)
    rec = assets_mod.add_asset(f, pham_vi="bud", prompt="tượng Phật ngồi thiền", ai=False,
                               root=repo, manifest_path=manifest)
    assert rec["ai_generated"] is False


def test_find_tag_co_dau_cach_khop_gach_duoi(tmp_path: Path):
    """'nghiên mực' (dấu cách, có dấu) phải khớp đường dẫn/tag nghien_muc."""
    repo, manifest, _ = _setup_fixture(tmp_path)
    d = repo / "output" / "cl_staging" / "anh_that"
    d.mkdir(parents=True)
    f = d / "lib01_nghien_muc_but_long.png"
    f.write_bytes(_make_png(640, 480) + b"_nm")
    from PIL import Image
    Image.new("RGB", (640, 480), "red").save(f)
    assets_mod.add_asset(f, pham_vi="chung", ai=False, root=repo, manifest_path=manifest)
    hits = assets_mod.find_assets(pham_vi="chung", tag="nghiên mực", manifest_path=manifest, root=repo)
    assert any("nghien_muc" in (h.get("path") or "") for h in hits)


def test_kho_loc_anh_ai_bo_qua_license_va_cam_anh_ai():
    ai = {"license": {"type": "AI Generated (Internal License)"}, "tags": {"core": ["robot"]}, "path": "a.png", "ai_generated": True}
    real_bysa = {"license": {"type": "CC BY-SA 4.0"}, "tags": {"core": []}, "path": "b.jpg", "ai_generated": False}
    mim = {"license_cho_phep": ["PD", "CC0", "CC BY"]}
    assert assets_mod.passes_kho_loc(ai, mim) is True
    assert assets_mod.passes_kho_loc(real_bysa, mim) is False
    assert assets_mod.passes_kho_loc(ai, {"cam_anh_ai": True}) is False
    assert assets_mod.passes_kho_loc(real_bysa, {"cam_anh_ai": True}) is True


def test_scan_lo_ai_bo_loai_bo_va_nap_flow(tmp_path: Path):
    """scan: bỏ file trong LOAI_BO.txt; nạp lô Flow raw/*.jpg có LEAD_DA_XEM, source=flow, strip_mark=crop."""
    repo, manifest, _ = _setup_fixture(tmp_path)
    gb = repo / "output" / "cl_staging" / "grokbot" / "lo_t"
    (gb / "out").mkdir(parents=True)
    (gb / "out" / "lib_dat.png").write_bytes(_make_png(640, 360) + b"_ok")
    (gb / "out" / "lib_loai.png").write_bytes(_make_png(640, 360) + b"_bo")
    (gb / "LEAD_DA_XEM").write_text("ok\n", encoding="utf-8")
    (gb / "LOAI_BO.txt").write_text("lib_loai.png\n", encoding="utf-8")
    fl = repo / "output" / "cl_staging" / "flow" / "lo_f"
    (fl / "raw").mkdir(parents=True)
    (fl / "raw" / "lib_canh_169_1_abcd.jpg").write_bytes(_make_png(1136, 634) + b"_fl")
    (fl / "prompts_16x9.txt").write_text("lib_canh_169 | a quiet village\n", encoding="utf-8")
    (fl / "LEAD_DA_XEM").write_text("ok\n", encoding="utf-8")
    (repo / "output" / "cl_staging" / "flow" / "lo_chua_xem" / "raw").mkdir(parents=True)
    (repo / "output" / "cl_staging" / "flow" / "lo_chua_xem" / "raw" / "x.jpg").write_bytes(_make_png(10, 10))
    assets_mod.scan_assets(root=repo, manifest_path=manifest,
                           dirs=["output/cl_staging/grokbot", "output/cl_staging/flow"])
    recs = [json.loads(l) for l in manifest.read_text(encoding="utf-8").splitlines() if l.strip()]
    paths = " ".join(r["path"] for r in recs)
    assert "lib_dat.png" in paths and "lib_loai.png" not in paths and "x.jpg" not in paths
    fr = [r for r in recs if "lib_canh_169" in r["path"]][0]
    assert fr["source"]["type"] == "flow" and fr["ai_generated"] is True and fr["strip_mark"] == "crop"
    assert "village" in (fr.get("prompt") or "")


def test_gh198_near_add_scan_and_listing(tmp_path):
    from PIL import Image, ImageDraw
    repo, manifest, _ = _setup_fixture(tmp_path)
    folder = repo / "pictures"
    folder.mkdir()
    image = Image.new("RGB", (120, 120), "white")
    ImageDraw.Draw(image).rectangle((10, 20, 80, 70), fill="black")
    a, b = folder / "a.png", folder / "b.jpg"
    image.save(a)
    image.save(b, quality=85)
    first = assets_mod.add_asset(a, "chung", root=repo, manifest_path=manifest)
    with pytest.raises(ValueError, match=first["asset_id"]):
        assets_mod.add_asset(b, "chung", root=repo, manifest_path=manifest)
    second = assets_mod.add_asset(b, "chung", root=repo, manifest_path=manifest, allow_near=True)
    assert assets_mod.near_dups([first, second], root=repo)
    manifest.unlink()
    stats = assets_mod.scan_assets(root=repo, manifest_path=manifest, dirs=["pictures"])
    assert len(stats["near_rejected"]) == 1
    assert stats["near_rejected"][0]["near_id"]


def test_gh198_remote_and_prune(tmp_path, monkeypatch):
    from PIL import Image
    import subprocess
    repo, manifest, _ = _setup_fixture(tmp_path)
    local = repo / "picture.png"
    Image.new("RGB", (10, 10), "blue").save(local)
    rec = assets_mod.add_asset(local, "chung", root=repo, manifest_path=manifest)
    remote = {}
    monkeypatch.setenv("ASSET_REMOTE", "test:")
    monkeypatch.setenv("ASSET_CACHE", str(repo / "cache"))
    def fake_run(args, **kwargs):
        if args[1] == "copyto":
            src, dst = args[2:]
            if src.startswith("test:"):
                Path(dst).write_bytes(remote[src])
            else:
                remote[dst] = Path(src).read_bytes()
            return subprocess.CompletedProcess(args, 0, stdout=b"")
        digest = hashlib.sha256(remote[args[-1]]).hexdigest()
        return subprocess.CompletedProcess(args, 0, stdout=digest + "  file\n")
    monkeypatch.setattr(assets_mod.subprocess, "run", fake_run)
    assets_mod.push_assets([rec["asset_id"]], False, manifest, repo)
    rec = assets_mod.load_manifest(manifest)[0]
    assert ":" not in rec["remote_path"]   # repo public: manifest không chứa tên remote
    url = assets_mod.remote_url(rec["remote_path"])
    assert url in remote
    assert Path(assets_mod.pull_assets([rec["asset_id"]], None, manifest, repo)[0]).read_bytes() == local.read_bytes()
    remote[url] = b"bad"
    with pytest.raises(ValueError, match="SHA"):
        assets_mod.pull_assets([rec["asset_id"]], None, manifest, repo)
    rec["video_da_dung"] = [{"kenh": "fs", "video_id": "v", "ngay": "2026-01-01", "ngay_public": "2026-01-01"}]
    assets_mod.write_manifest(manifest, [rec])
    assert not assets_mod.prune_assets(manifest, repo, yes=True, today=date(2026, 2, 1))
    assert local.exists()
    remote[url] = local.read_bytes()
    plan = repo / "output" / "plan_test.json"
    plan.parent.mkdir(exist_ok=True)
    plan.write_text(json.dumps({"media": ["picture.png"]}))
    assert not assets_mod.prune_assets(manifest, repo, yes=True, today=date(2026, 2, 1))
    assert local.exists()
    plan.write_text("{}")
    assert assets_mod.prune_assets(manifest, repo, today=date(2026, 2, 1))[0]["deleted"] is False
    assert local.exists()
    assert assets_mod.prune_assets(manifest, repo, yes=True, today=date(2026, 2, 1))[0]["deleted"] is True
    assert not local.exists()


def test_gh198_usage_and_cl(tmp_path):
    repo, manifest, _ = _setup_fixture(tmp_path)
    (repo / "library" / "channels" / "fs.yaml").write_text(json.dumps({"kenh": "fs", "kho_loc": {"max_dung": 2, "cach_ngay": 5}}))
    rec = {"asset_id": "test", "path": "x", "pham_vi": "chung", "tags": {"core": [], "domain": []}, "video_da_dung": []}
    assets_mod.write_manifest(manifest, [rec])
    assets_mod.mark_used("test", "v1", "fs", "2026-01-10", manifest)
    assert not assets_mod.find_assets(pham_vi="fs", root=repo, manifest_path=manifest, today=date(2026, 1, 12))
    assert assets_mod.find_assets(pham_vi="fs", root=repo, manifest_path=manifest, today=date(2026, 1, 20))
    assets_mod.mark_used("test", "v2", "fs", "2026-01-15", manifest)
    assert not assets_mod.find_assets(pham_vi="fs", root=repo, manifest_path=manifest, today=date(2026, 2, 1))
    assert assets_mod.find_assets(pham_vi="fs", root=repo, manifest_path=manifest, today=date(2026, 2, 1), max_uses=3)
    cl = assets_mod.kho_loc_for("cl", assets_mod.load_channels(ROOT / "library" / "channels"))
    ai = {"ai_generated": True, "tags": {"core": []}}
    assert not assets_mod.passes_kho_loc(ai, cl)
    ai["tags"]["core"] = ["minh_hoa_chung"]
    assert assets_mod.passes_kho_loc(ai, cl)


def test_gh198_prune_unused_and_public_date(tmp_path, monkeypatch):
    from PIL import Image
    import subprocess
    repo, manifest, _ = _setup_fixture(tmp_path)
    local = repo / "unused.png"
    Image.new("RGB", (10, 10), "green").save(local)
    rec = assets_mod.add_asset(local, "chung", root=repo, manifest_path=manifest)
    remote = {}
    monkeypatch.setenv("ASSET_REMOTE", "test:")
    def fake_run(args, **kwargs):
        if args[1] == "copyto":
            remote[args[3]] = Path(args[2]).read_bytes()
            return subprocess.CompletedProcess(args, 0, stdout=b"")
        return subprocess.CompletedProcess(args, 0, stdout=hashlib.sha256(remote[args[-1]]).hexdigest() + "  f")
    monkeypatch.setattr(assets_mod.subprocess, "run", fake_run)
    assets_mod.push_assets([rec["asset_id"]], False, manifest, repo)
    # đã dùng nhưng chưa có ngày public -> giữ
    assets_mod.mark_used(rec["asset_id"], "v1", "mim", "2026-01-01", manifest)
    assert not assets_mod.prune_assets(manifest, repo, yes=True, today=date(2026, 3, 1))
    # có ngày public, chưa quá 7 ngày -> giữ; quá 7 ngày -> xóa
    assets_mod.mark_used(rec["asset_id"], "v1", "mim", "2026-01-01", manifest, ngay_public="2026-02-25")
    assert not assets_mod.prune_assets(manifest, repo, yes=True, today=date(2026, 3, 1))
    assert assets_mod.prune_assets(manifest, repo, yes=True, today=date(2026, 3, 10))[0]["deleted"] is True
    # asset chưa dùng lần nào: Drive có bản khớp là xóa được bản trên máy
    other = repo / "fresh.png"
    Image.new("RGB", (10, 10), "yellow").save(other)
    rec2 = assets_mod.add_asset(other, "chung", root=repo, manifest_path=manifest, allow_near=True)
    assets_mod.push_assets([rec2["asset_id"]], False, manifest, repo)
    assert [d["asset_id"] for d in assets_mod.prune_assets(manifest, repo, yes=True, today=date(2026, 3, 10))] == [rec2["asset_id"]]
    assert not other.exists()


def test_gh198_ingest_dir_prompts_dry_run_and_push(tmp_path, monkeypatch, capsys):
    from PIL import Image, ImageDraw
    repo, manifest, _ = _setup_fixture(tmp_path)
    folder = repo / "batch"
    folder.mkdir()
    image = Image.new("RGB", (120, 120), "white")
    ImageDraw.Draw(image).rectangle((10, 20, 80, 70), fill="black")
    image.save(folder / "ai_01.png")
    image.save(folder / "ai_02.jpg", quality=85)
    (folder / "ignore.txt").write_text("ignore", encoding="utf-8")
    prompts = repo / "ai_prompts.md"
    prompts.write_text("## ai_01.png — MIM\n- Prompt (tiếng Anh): A small robot\n"
                       "## ai_02.jpg — CK\n- Prompt (tiếng Anh): Money\n", encoding="utf-8")
    pushed = []
    def fake_push(ids, all_local, manifest_path, root):
        pushed.extend(ids)
        return ids
    monkeypatch.setattr(assets_mod, "push_assets", fake_push)
    args = ["ingest-dir", str(folder), "--pham-vi", "chung", "--ai", "--tags", "extra",
            "--tags-from-prompts", str(prompts), "--push", "--root", str(repo),
            "--manifest", str(manifest)]
    assert assets_mod.main(args + ["--dry-run"]) == 0
    dry = json.loads(capsys.readouterr().out)
    assert len(dry["added"]) == 1 and len(dry["near_duplicates"]) == 1
    assert dry["near_duplicates"][0]["near_id"] == dry["added"][0]["asset_id"]
    assert not manifest.exists() and not pushed and not dry["pushed"]
    assert assets_mod.main(args) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["added"] == dry["added"]
    assert result["pushed"] == pushed == [result["added"][0]["asset_id"]]
    record = assets_mod.load_manifest(manifest)[0]
    assert record["prompt"] == "A small robot"
    assert {"mim", "cong_nghe", "extra"} <= set(record["tags"]["core"])
    assert record["ai_generated"] is True
    before = manifest.read_bytes()
    again = assets_mod.ingest_dir(folder, "chung", root=repo, manifest_path=manifest)
    assert not again["added"] and len(again["near_duplicates"]) == 2
    assert manifest.read_bytes() == before


def test_gh198_ingest_prompt_groups_and_errors(tmp_path, monkeypatch):
    repo, manifest, _ = _setup_fixture(tmp_path)
    folder = repo / "batch"
    folder.mkdir()
    (folder / "a.png").write_bytes(b"invalid image")
    (folder / "b.png").write_bytes(b"also invalid")
    prompts = repo / "prompts.md"
    prompts.write_text("## a.png — CK\n- Prompt (tiếng Anh): first\n"
                       "## b.png — CL\n- Prompt (tiếng Anh): second\n", encoding="utf-8")
    parsed = assets_mod.parse_ingest_prompts(prompts)
    assert parsed["a.png"] == {"prompt": "first", "tags": ["ck", "tien_bac"]}
    assert parsed["b.png"] == {"prompt": "second", "tags": ["cl", "hinh_su", "minh_hoa_chung"]}
    result = assets_mod.ingest_dir(folder, "chung", root=repo, manifest_path=manifest)
    assert len(result["errors"]) == 2 and not result["added"]


def test_place_long_image_and_force(tmp_path, monkeypatch):
    from PIL import Image
    repo, manifest, _ = _setup_fixture(tmp_path)
    source = repo / "portrait.png"
    Image.new("RGBA", (30, 60), "red").save(source)
    rec = assets_mod.add_asset(source, "chung", ai=True, root=repo, manifest_path=manifest)
    creator = repo / "creator_v2"
    args = ["place", "topic", "hero", rec["asset_id"], "--creator-root", str(creator),
            "--root", str(repo), "--manifest", str(manifest)]
    assert assets_mod.main(args) == 0
    jpg = creator / "output/long/topic/img/hero.jpg"
    sidecar = jpg.with_suffix(".json")
    with Image.open(jpg) as im:
        assert im.mode == "RGB" and im.size == (1920, 1080)
    meta = json.loads(sidecar.read_text(encoding="utf-8"))
    assert meta == {"file": "EXT:ai:hero", "license": "no restrictions", "artist": "",
                    "asset_id": rec["asset_id"], "ai_generated": True}
    original = jpg.read_bytes(), sidecar.read_bytes()
    assert assets_mod.main(args) == 1
    assert (jpg.read_bytes(), sidecar.read_bytes()) == original
    assert assets_mod.main(args + ["--force"]) == 0


def test_place_pulls_missing_asset(tmp_path, monkeypatch):
    from PIL import Image
    repo, manifest, _ = _setup_fixture(tmp_path)
    source = repo / "source.png"
    Image.new("RGB", (40, 20), "blue").save(source)
    rec = assets_mod.add_asset(source, "chung", root=repo, manifest_path=manifest)
    data = source.read_bytes()
    source.unlink()
    calls = []
    def fake_pull(ids, plan, manifest_path, root):
        calls.append(ids)
        cache = root / "download.png"
        cache.write_bytes(data)
        return [str(cache)]
    monkeypatch.setattr(assets_mod, "pull_assets", fake_pull)
    assets_mod.place_asset("topic", "key", rec["asset_id"], repo / "creator_v2",
                           manifest_path=manifest, root=repo)
    assert calls == [[rec["asset_id"]]]
