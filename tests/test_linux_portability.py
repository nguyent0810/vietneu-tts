"""Regression tests for Linux portability (Task 94a / Ticket #66).

Verify that:
1. Mac behavior is completely unchanged (sys.platform == 'darwin').
2. Linux branch only engages when sys.platform == 'linux' or via specific env vars.
3. Windows (sys.platform == 'win32') behavior is unchanged (no unintended fallthrough).
4. Shell scripts compute the repo root from their own location (no /Users/... path).
5. Font fallbacks keep Mac primary font first.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------- 1. external_bin.py ----------------
def test_external_bin_osascript_platforms(monkeypatch):
    import external_bin

    # Mac (darwin)
    monkeypatch.setattr(sys, "platform", "darwin")
    external_bin.get_osascript_bin.cache_clear()
    mac_bin = external_bin.get_osascript_bin()
    assert mac_bin is not None
    assert "osascript" in mac_bin

    # Linux: trả None rõ ràng, không crash
    monkeypatch.setattr(sys, "platform", "linux")
    external_bin.get_osascript_bin.cache_clear()
    assert external_bin.get_osascript_bin() is None

    # Win32: không rẽ vào nhánh Linux (cố resolve osascript như cũ)
    monkeypatch.setattr(sys, "platform", "win32")
    external_bin.get_osascript_bin.cache_clear()
    monkeypatch.setattr(external_bin, "resolve_bin", lambda name, hint: f"mock_{name}")
    assert external_bin.get_osascript_bin() == "mock_osascript"

    # Reset cache on current platform
    monkeypatch.undo()
    external_bin.get_osascript_bin.cache_clear()


# ---------------- 2. hf_depth.py ----------------
def test_hf_depth_linux_and_mac(monkeypatch, capsys, tmp_path):
    import hf_depth

    dummy_img = tmp_path / "test.jpg"
    dummy_img.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 20)

    # Linux: log 1 dòng stderr, trả None, không crash
    monkeypatch.setattr(sys, "platform", "linux")
    res = hf_depth.split_depth(dummy_img)
    assert res is None
    captured = capsys.readouterr()
    assert "[hf_depth]" in captured.err
    assert "Apple Vision" in captured.err

    # Linux _fgmask_bin raise RuntimeError
    with pytest.raises(RuntimeError, match="fgmask Swift binary chỉ chạy trên macOS"):
        hf_depth._fgmask_bin()

    # Mac + Win32: không rẽ vào nhánh Linux, giữ đường fgmask cũ
    # mock subprocess để không chạy swiftc thật
    monkeypatch.setattr(hf_depth.subprocess, "run", lambda *a, **kw: None)
    mock_bin = tmp_path / "mock_fgmask"
    mock_bin.write_text("dummy")
    monkeypatch.setattr(hf_depth, "FGMASK_BIN", mock_bin)
    monkeypatch.setattr(hf_depth, "FGMASK_SRC", tmp_path / "mock_src")
    (tmp_path / "mock_src").write_text("dummy_src")
    os.utime(mock_bin, (9999999999, 9999999999))
    os.utime(tmp_path / "mock_src", (1, 1))
    monkeypatch.setattr(hf_depth, "CACHE", tmp_path / "depth_cache")
    for platform in ("darwin", "win32"):
        monkeypatch.setattr(sys, "platform", platform)
        assert hf_depth._fgmask_bin() == mock_bin
        capsys.readouterr()
        # split_depth không in dòng báo Linux (đi tiếp vào đường cũ, ở đây ảnh giả nên có thể lỗi sau đó)
        try:
            hf_depth.split_depth(dummy_img)
        except Exception:
            pass
        assert "[hf_depth]" not in capsys.readouterr().err


# ---------------- 3. hf_cleanup.py ----------------
def test_hf_cleanup_trash_dir(monkeypatch, tmp_path):
    import hf_cleanup

    monkeypatch.setattr(hf_cleanup.Path, "home", classmethod(lambda cls: tmp_path / "fakehome"))
    monkeypatch.delenv("VIENEU_TRASH_DIR", raising=False)

    # Mac (darwin): ~/.Trash
    monkeypatch.setattr(sys, "platform", "darwin")
    assert hf_cleanup._trash_dir() == tmp_path / "fakehome" / ".Trash"

    # Linux: ~/.local/share/Trash/files
    monkeypatch.setattr(sys, "platform", "linux")
    assert hf_cleanup._trash_dir() == tmp_path / "fakehome" / ".local" / "share" / "Trash" / "files"

    # Win32: ~/.Trash (giữ y như cũ, không đổi)
    monkeypatch.setattr(sys, "platform", "win32")
    assert hf_cleanup._trash_dir() == tmp_path / "fakehome" / ".Trash"

    # VIENEU_TRASH_DIR override
    custom = tmp_path / "custom_trash"
    monkeypatch.setenv("VIENEU_TRASH_DIR", str(custom))
    assert hf_cleanup._trash_dir() == custom


# ---------------- 4. hyperframes_bridge.py ----------------
def test_hyperframes_bridge_platforms(monkeypatch, tmp_path):
    import hyperframes_bridge

    script_path = tmp_path / "script.txt"
    script_path.write_text("Dòng kiểm tra.\n", encoding="utf-8")
    wav_path = tmp_path / "audio.wav"
    wav_path.write_bytes(b"RIFF" + b"\x00" * 36)
    wav_manifest = wav_path.with_suffix(".json")
    wav_manifest.write_text(json.dumps({
        "segments": [{"start": 0.0, "end": 1.0, "words": []}],
        "duration_s": 1.0
    }), encoding="utf-8")
    out_path = tmp_path / "out.mp4"

    calls = []
    def mock_run(cmd, **kw):
        calls.append(cmd)
        silent_out = out_path.with_name(out_path.stem + "_silent.mp4")
        silent_out.write_bytes(b"fake_mp4")
        return type("Res", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(hyperframes_bridge.subprocess, "run", mock_run)

    for platform in ("darwin", "linux", "win32"):
        monkeypatch.setattr(sys, "platform", platform)

        # Với HYPERFRAMES_BROWSER_PATH
        monkeypatch.setenv("HYPERFRAMES_BROWSER_PATH", "/opt/custom/chrome")
        calls.clear()
        hyperframes_bridge.render(script_path, wav_path, "fs", out_path, opts={"skip_qa": True, "video_only": True})
        assert len(calls) > 0
        cmd_str = calls[0][2] if isinstance(calls[0], list) and len(calls[0]) > 2 else str(calls[0])
        assert "export HYPERFRAMES_BROWSER_PATH=/opt/custom/chrome" in cmd_str

        # Không có HYPERFRAMES_BROWSER_PATH
        monkeypatch.delenv("HYPERFRAMES_BROWSER_PATH", raising=False)
        calls.clear()
        hyperframes_bridge.render(script_path, wav_path, "fs", out_path, opts={"skip_qa": True, "video_only": True})
        assert len(calls) > 0
        cmd_str = calls[0][2] if isinstance(calls[0], list) and len(calls[0]) > 2 else str(calls[0])
        assert "HYPERFRAMES_BROWSER_PATH=" not in cmd_str


# ---------------- 5. studio.py ----------------
def test_studio_platforms(monkeypatch, tmp_path):
    import studio

    calls = []
    def mock_run(cmd, **kw):
        calls.append(cmd)
        return type("Res", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(studio.subprocess, "run", mock_run)

    for platform in ("darwin", "linux", "win32"):
        monkeypatch.setattr(sys, "platform", platform)

        # Với HYPERFRAMES_BROWSER_PATH
        monkeypatch.setenv("HYPERFRAMES_BROWSER_PATH", "/usr/bin/chromium-browser")
        calls.clear()
        studio.hf(tmp_path, "lint")
        assert len(calls) > 0
        cmd_str = calls[0][2] if isinstance(calls[0], list) and len(calls[0]) > 2 else str(calls[0])
        assert "export HYPERFRAMES_BROWSER_PATH=/usr/bin/chromium-browser" in cmd_str

        # Không có HYPERFRAMES_BROWSER_PATH
        monkeypatch.delenv("HYPERFRAMES_BROWSER_PATH", raising=False)
        calls.clear()
        studio.hf(tmp_path, "lint")
        assert len(calls) > 0
        cmd_str = calls[0][2] if isinstance(calls[0], list) and len(calls[0]) > 2 else str(calls[0])
        assert "HYPERFRAMES_BROWSER_PATH=" not in cmd_str


# ---------------- 6. Script không gõ cứng đường dẫn máy Mac ----------------
@pytest.mark.parametrize("script", ["scripts/daily_short_batch.sh", "scripts/twice_weekly_batch.sh"])
def test_scripts_root_from_own_location(script):
    text = (ROOT / script).read_text(encoding="utf-8")
    assert "/Users/" not in text
    assert 'ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"' in text


# ---------------- 7. Font fallbacks ----------------
def test_font_fallbacks():
    import json

    themes_dir = ROOT / "hyperframes_short" / "studio" / "themes"
    for name in ("saffron.json", "son-mai.json", "tet-poster.json"):
        theme_file = themes_dir / name
        assert theme_file.exists()
        data = json.loads(theme_file.read_text(encoding="utf-8"))
        font_cjk = data["vars"]["font-cjk"]
        # Phông đứng đầu trên Mac không đổi: "Songti SC"
        assert font_cjk.startswith('"Songti SC"')
        # Có fallback Noto Serif / Noto CJK đằng sau
        assert "Noto Serif" in font_cjk
