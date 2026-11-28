from pathlib import Path

import numpy as np
from PIL import Image

from library.tools.image_similarity import near_duplicate
from long_script_lint import lint, media_plan_warnings


def test_near_duplicate_uses_grayscale_thumbnail_threshold(tmp_path: Path):
    a = np.full((90, 160, 3), 100, dtype=np.uint8)
    close = np.full((90, 160, 3), 110, dtype=np.uint8)
    far = np.full((90, 160, 3), 140, dtype=np.uint8)
    paths = [tmp_path / f"{i}.png" for i in range(3)]
    for path, pixels in zip(paths, (a, close, far)):
        Image.fromarray(pixels).save(path)
    assert near_duplicate(paths[0], paths[1])
    assert not near_duplicate(paths[0], paths[2])


def test_lint_warns_for_short_cuts_and_adjacent_similar_images(tmp_path: Path):
    image1, image2 = tmp_path / "a.png", tmp_path / "b.png"
    Image.fromarray(np.full((36, 64, 3), 80, dtype=np.uint8)).save(image1)
    Image.fromarray(np.full((36, 64, 3), 90, dtype=np.uint8)).save(image2)
    words = " ".join(f"tiếng{i}" for i in range(185))
    row = {
        "script": [words, "Ảnh tiếp theo."],
        "media": {
            "1": {"path": str(image1), "cuts": [{"at": "tiếng1"}]},
            "2": {"path": str(image2)},
        },
    }
    warnings = media_plan_warnings(row, [(0.0, 60.0), (60.0, 61.0)])
    codes = [code for code, _ in warnings]
    assert "cut_ngan" in codes
    assert "anh_lap_ke" in codes
    issues = lint(row)["issues"]
    assert any(level == "CẢNH BÁO" and code == "cut_ngan" for level, code, _ in issues)
    assert any(level == "CẢNH BÁO" and code == "anh_lap_ke" for level, code, _ in issues)
