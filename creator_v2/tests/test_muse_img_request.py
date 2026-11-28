import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import muse_img_request as M  # noqa: E402

DOC = """# Ảnh
## Phong cách chung (mọi ảnh)
Painterly, warm light.

## ai_01.png — sàn giao dịch
Dùng ở: CH00.
- Prompt: Empty trading hall at dawn.

## ai_02.png · ai_pad — chị Hạnh
- Prompt (tiếng Anh): Woman at kitchen table.
"""


def test_sections_and_prompt():
    s = M.sections(DOC)
    assert list(s) == ["ai_01.png", "ai_02.png"]
    p = M.prompt_for(s["ai_01.png"], M.common_style(DOC))
    assert "Empty trading hall at dawn." in p and "Painterly, warm light." in p
    assert "16:9" in p and "No text" in p
    assert "Dùng ở" not in p          # chỉ gửi dòng Prompt, không gửi ghi chú tiếng Việt


def test_newest_image(tmp_path):
    assert M.newest_image(tmp_path) is None
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "media-generation-1.png").write_bytes(b"png")
    assert M.newest_image(tmp_path).name == "media-generation-1.png"


def test_wait_new_image_returns_unseen(monkeypatch):
    rows = [{"seq": 1, "kind": "image", "message_id": "a"}, {"seq": 2, "kind": "file"}, {"seq": 3, "kind": "image", "message_id": "b"}]
    monkeypatch.setattr(M, "thread_images", lambda th: [r for r in rows if r["kind"] == "image"])
    assert M.wait_new_image("t", {1}, wait=5, poll=0)["message_id"] == "b"
    assert M.wait_new_image("t", {1, 3}, wait=0.01, poll=0) is None


def test_newest_image_skips_empty(tmp_path):
    (tmp_path / "media-generation-1.png").write_bytes(b"")
    assert M.newest_image(tmp_path) is None
    (tmp_path / "media-generation-2.png").write_bytes(b"png")
    assert M.newest_image(tmp_path).name == "media-generation-2.png"
