"""GH-458 / 081: real upload entry points, fake auth and HTTP only."""
import argparse
import copy
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

import short_upload
import youtube_upload as upload
from pipelines.vsd import pipeline as vsd
from tools.publish import upload_bud, upload_fs, upload_long


NOTICE = "Một số hình là phỏng dựng bằng AI dựa trên tư liệu."
MISSING = object()


@pytest.fixture
def fake_youtube(monkeypatch, tmp_path):
    """Capture actual serialized resumable/update bodies; no credentials or sockets."""
    bodies = []

    def urlopen(req, **kwargs):
        assert req.method in {"POST", "PUT"}
        assert req.full_url.startswith((upload.UPLOAD_INIT_URL, upload.VIDEOS_URL))
        bodies.append(req.data)
        response = io.BytesIO(b'{"id": "fake-video"}')
        response.headers = {"Location": "https://fake.invalid/session"}
        return response

    monkeypatch.setattr(upload.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(upload, "_refresh_or_raise", lambda *_: "fake-token")
    monkeypatch.setattr(upload, "_upload_chunks", lambda *a, **k: {"id": "fake-video"})
    monkeypatch.setattr(upload, "UPLOAD_LOG", tmp_path / "fake-upload-log.json")
    from library.tools import lib
    monkeypatch.setattr(lib, "enforce_lane", lambda *a, **k: None)
    return bodies


def legacy_body(title, description, tags, publish_at=None, language=None):
    """Pre-081 field order and values, independent of VideoMetadata.to_api_body."""
    snippet = {"title": title, "description": description, "tags": tags, "categoryId": "22"}
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
    if publish_at:
        status["publishAt"] = publish_at
    if language:
        snippet.update(defaultLanguage=language, defaultAudioLanguage=language)
    return {"snippet": snippet, "status": status}


def assert_upload_body(raw, legacy, enabled):
    expected = copy.deepcopy(legacy)
    if enabled:
        expected["status"]["containsSyntheticMedia"] = True
        desc = json.loads(raw)["snippet"]["description"]
        assert desc.count(NOTICE) == 1
        assert desc.splitlines()[-1] == NOTICE
        expected["snippet"]["description"] = legacy["snippet"]["description"] + "\n" + NOTICE
    # The comparison covers actual request bytes, including order and whitespace.
    assert raw == json.dumps(expected).encode("utf-8")


@pytest.mark.parametrize("flag", [None, False, True])
def test_metadata_optional_status_and_legacy_bytes(flag):
    actual = upload.VideoMetadata(title="Tiêu đề", contains_synthetic_media=flag).to_api_body()
    expected = legacy_body("Tiêu đề", "", [])
    if flag is not None:
        expected["status"]["containsSyntheticMedia"] = flag
    assert json.dumps(actual).encode() == json.dumps(expected).encode()


@pytest.mark.parametrize("existing", [MISSING, False, True])
@pytest.mark.parametrize("requested", [None, False, True])
def test_update_preserves_or_explicitly_sets_flag(fake_youtube, monkeypatch, existing, requested):
    current = {"id": "fake-video", **legacy_body("Tiêu đề", "Mô tả", ["tag"])}
    if existing is not MISSING:
        current["status"]["containsSyntheticMedia"] = existing
    expected = copy.deepcopy(current)
    expected["snippet"]["title"] = "Đổi tiêu đề"
    if requested is not None:
        expected["status"]["containsSyntheticMedia"] = requested
    monkeypatch.setattr(upload, "_fetch_video_snippet_status", lambda *a: current)
    upload.update_video("fake-video", "/fake/not-read.json", title="Đổi tiêu đề",
                        contains_synthetic_media=requested)
    assert fake_youtube == [json.dumps(expected).encode("utf-8")]


@pytest.mark.parametrize("description", ["", "Mô tả  \n", NOTICE, f"{NOTICE}\nNguồn",
                                            f"Mô tả\n{NOTICE}\n{NOTICE}", f"Mô tả: {NOTICE}\nNguồn"])
def test_notice_is_unique_final_line_and_idempotent(description):
    actual = upload.synthetic_media_description(description, True)
    assert actual.count(NOTICE) == 1
    assert actual.splitlines()[-1] == NOTICE
    assert upload.synthetic_media_description(actual, True) == actual
    assert upload.synthetic_media_description(description) == description


@pytest.mark.parametrize("flag", [MISSING, False, None, "true", 1, True])
def test_short_upload_fake_body(fake_youtube, tmp_path, flag):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake-video")
    kwargs = {} if flag is MISSING else {"ai_faces": flag}
    assert short_upload.upload_short(str(video), "Tiêu đề", "Mô tả", ["tag"], None,
                                     "/fake/not-read.json", channel="bud", lane="jataka", **kwargs) == "fake-video"
    assert_upload_body(fake_youtube[0], legacy_body("Tiêu đề", "Mô tả", ["tag"]), flag is True)


def test_short_fake_upload_deduplicates_notice(fake_youtube, tmp_path):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake-video")
    description = f"Mô tả\n{NOTICE}\nNguồn\n{NOTICE}"
    short_upload.upload_short(str(video), "Tiêu đề", description, [], None, "/fake/not-read.json",
                              channel="bud", lane="jataka", ai_faces=True)
    body = json.loads(fake_youtube[0])
    assert body["status"]["containsSyntheticMedia"] is True
    assert body["snippet"]["description"] == f"Mô tả\n\nNguồn\n{NOTICE}"


@pytest.mark.parametrize("module", [upload_bud, upload_fs, upload_long])
def test_description_moves_existing_notice_to_final_line(monkeypatch, module):
    row = {"id": "sample", "title": "Tiêu đề", "script": ["Lời kể."], "series": "bud",
           "ai_faces": True, "source": NOTICE, "seo": {"summary": NOTICE}}
    if module is upload_long:
        monkeypatch.setattr(module, "chapters", lambda *a: ["0:00 Mở đầu"])
        monkeypatch.setattr(module, "credits", lambda *a, **k: "")
        monkeypatch.setattr(module, "music_line", lambda *a: "Nhạc thử")
    else:
        monkeypatch.setattr(module, "credits_for", lambda *a: "")
        monkeypatch.setattr(module, "music_cc", lambda *a: "Nhạc thử")
    description = module.description(row)
    assert description.count(NOTICE) == 1
    assert description.splitlines()[-1] == NOTICE
    assert "Nhạc thử" in description


@pytest.mark.parametrize("module,series", [(upload_bud, "bud"), (upload_fs, "fs"),
                                          (upload_long, "bud"), (upload_long, "fs")])
@pytest.mark.parametrize("flag", [MISSING, False, True])
def test_plan_to_actual_upload_body(fake_youtube, monkeypatch, tmp_path, module, series, flag):
    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    here = tmp_path / "plans"
    out = here / "out"
    out.mkdir(parents=True)
    (here / "thumbs").mkdir()
    (here / "thumbs" / "thumb.jpg").write_bytes(b"fake-image")
    (out / "sample.mp4").write_bytes(b"fake-video")
    publish = datetime.now(timezone.utc) + timedelta(days=1)
    row = {"id": "sample", "title": "Tiêu đề", "tags": ["tag"], "day": publish.date().isoformat(),
           "slot": "12:00", "style": "studio", "series": series, "script": ["Lời kể."],
           "thumbnail": "thumb.jpg", "lane": "jataka" if series == "bud" else "tuoi"}
    if flag is not MISSING:
        row["ai_faces"] = flag
    (here / "plan_test.json").write_text(json.dumps([row]), encoding="utf-8")
    monkeypatch.setattr(module, "HERE", here)
    monkeypatch.setattr(module, "OUT", out)
    monkeypatch.setattr(module, "LEDGER", here / "uploaded.json")
    # Exercise the real upload branch without invoking any CLI confirmation command.
    args = SimpleNamespace(confirm=True, day=None, only=None, playlist=False, seo_ok=True, show=False)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda *a, **k: args)
    import hf_coverage
    monkeypatch.setattr(hf_coverage, "occupied_slots", lambda *a: set())
    disclaimer = {"bud": "Nội dung suy ngẫm, không thay cho việc học Phật pháp trực tiếp với thầy và tăng đoàn.",
                  "fs": "Kiến thức truyền thống, để tham khảo — không phải kết luận khoa học."}[series]
    if module is upload_long:
        import seo_check
        monkeypatch.setattr(seo_check, "check_row", lambda *a: [])
        monkeypatch.setattr(module, "chapters", lambda *a: ["0:00 Mở đầu"])
        monkeypatch.setattr(module, "credits", lambda *a, **k: "")
        monkeypatch.setattr(module, "music_line", lambda *a: "Nhạc thử")
        monkeypatch.setattr(module, "upload_thumbnail", lambda *a: None)
        hashtags = {"bud": "#LoiPhatDay #PhatPhap #ChuaLanh", "fs": "#12ConGiap #PhamThaiTue #PhongThuy"}[series]
        description = f"Tiêu đề\n\nLời kể.\n\nMục lục:\n0:00 Mở đầu\n\n{disclaimer}\n\nNhạc thử\n\n{hashtags}"
    else:
        monkeypatch.setattr(module, "credits_for", lambda *a: "")
        monkeypatch.setattr(module, "music_cc", lambda *a: "Nhạc thử")
        monkeypatch.setattr(module.time, "sleep", lambda *a: None)
        description = f"Tiêu đề\n\n{disclaimer}\n\nNhạc thử\n\n#Shorts"
    assert module.main() == 0
    assert len(fake_youtube) == 1
    expected = legacy_body("Tiêu đề", description, ["tag"], f"{row['day']}T12:00:00Z", "vi")
    assert_upload_body(fake_youtube[0], expected, flag is True)


@pytest.mark.parametrize("flag", [MISSING, False, True])
def test_vsd_spec_render_queue_to_actual_upload_body(fake_youtube, monkeypatch, tmp_path, flag):
    monkeypatch.setattr(vsd, "BASE", tmp_path)
    monkeypatch.setattr(vsd, "QUEUED", tmp_path / "queue")
    monkeypatch.setattr(vsd, "LOG", tmp_path / "pipeline.jsonl")
    monkeypatch.setattr(vsd, "LEDGER", tmp_path / "uploaded.json")
    monkeypatch.setenv("VSD_CREDS", "/fake/not-read.json")
    monkeypatch.setattr(vsd, "_remote_uploads", lambda *a: [])
    monkeypatch.setattr(vsd, "resolve_occupied", lambda *a: set())
    publish = (datetime.now(timezone.utc) + timedelta(days=1)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"fake-video")
    item = {"id": "sample", "channel": "vsd", "lane": "vsd_su", "lines": [], "scenes": [], "out": str(video),
            "packaging": {"title": "Tiêu đề", "description_first_line": "Mô tả", "hashtags": ["#vsd"],
                          "sources": ["Nguồn"], "publish_slot_utc": publish}}
    if flag is not MISSING:
        item["ai_faces"] = flag
    vsd._atomic_json(vsd._state_dir("ready") / "sample.json", item)
    def fake_render(*args, **kwargs):
        spec = json.loads((vsd.QUEUED / "rendering" / "sample.studio.json").read_text())
        assert spec.get("ai_faces", MISSING) is flag
        return SimpleNamespace(pid=1, returncode=0, communicate=lambda **kw: ("", ""))
    monkeypatch.setattr(vsd.subprocess, "Popen", fake_render)
    monkeypatch.setattr(vsd, "qa_render", lambda *a: None)
    assert vsd.next_render() == vsd.EXIT_OK
    assert vsd.next_upload() == vsd.EXIT_OK
    assert len(fake_youtube) == 1
    expected = legacy_body("Tiêu đề", "Mô tả\n#vsd\nNguồn\n#vsd:sample", ["#vsd", "vsd-sample"], publish, "vi")
    assert_upload_body(fake_youtube[0], expected, flag is True)


def test_long_notice_counts_towards_description_limit(monkeypatch):
    monkeypatch.setattr(upload_long, "chapters", lambda *a: ["0:00 Mở đầu"])
    monkeypatch.setattr(upload_long, "credits", lambda *a, **k: "")
    monkeypatch.setattr(upload_long, "music_line", lambda *a: "Nhạc thử")
    row = {"id": "sample", "title": "Tiêu đề", "script": ["Lời kể."], "series": "bud",
           "seo": {"summary": "x"}}
    size = len(upload_long.description(row).encode("utf-8"))
    row["seo"]["summary"] = "x" * (5001 - size)
    assert len(upload_long.description(row).encode("utf-8")) == 5000
    row["ai_faces"] = True
    with pytest.raises(SystemExit, match="byte > 5000"):
        upload_long.description(row)


def test_long_compact_credits_keeps_notice(monkeypatch):
    monkeypatch.setattr(upload_long, "chapters", lambda *a: ["0:00 Mở đầu"])
    monkeypatch.setattr(upload_long, "credits", lambda rid, compact=False: "Nguồn" if compact else "x" * 5000)
    monkeypatch.setattr(upload_long, "music_line", lambda *a: "Nhạc thử")
    row = {"id": "sample", "title": "Tiêu đề", "script": ["Lời kể."], "series": "bud", "ai_faces": True}
    description = upload_long.description(row)
    assert "Nguồn" in description
    assert len(description.encode("utf-8")) <= 5000
    assert description.count(NOTICE) == 1
    assert description.splitlines()[-1] == NOTICE


def test_upload_long_nhac_khi_co_anh_ai_ma_thieu_khoa():
    import importlib
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/publish"))
    ul = importlib.import_module("upload_long")
    ai = {"3": {"kind": "local", "path": "output/cl_staging/long/research/ai_media/L01/a.png"}}
    cut = {"5": {"kind": "stock", "query": "x", "cuts": [{"at": "bà", "kind": "local", "path": "output/cl_staging/grokbot/b.png"}]}}
    assert ul.ai_media_missing_flag({"id": "x", "media": ai})
    assert ul.ai_media_missing_flag({"id": "x", "media": cut})
    assert not ul.ai_media_missing_flag({"id": "x", "media": ai, "ai_faces": False})
    assert not ul.ai_media_missing_flag({"id": "x", "media": {"1": {"kind": "stock", "query": "chùa"}}})
