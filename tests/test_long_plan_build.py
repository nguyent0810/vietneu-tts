import importlib.util
import json
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "long_plan_build.py"
SPEC = importlib.util.spec_from_file_location("long_plan_build", MODULE)
long_plan_build = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(long_plan_build)


def test_build_new_parses_script_and_is_deterministic(tmp_path):
    script = tmp_path / "script.txt"
    script.write_text(
        "\n".join([
            "**Chương Một**",
            "Mở đầu.",
            "[im]",
            "[TA] Lời thoại thứ nhất.",
            "[KE] Lời kể tiếp theo.",
            "[ghi chú nội bộ]",
            "**Chương Hai**",
            "[cảnh C2] Một cảnh mở đầu chương hai.",
            "[hit]",
            "Kết lại bằng một câu.",
        ]),
        encoding="utf-8",
    )
    base = tmp_path / "base.json"
    base.write_text(json.dumps([{
        "style": "laban_long", "series": "bud", "lane": "long",
        "chapters": True, "tts": {"voice": "Binh"}, "sound": {},
    }]), encoding="utf-8")
    out_a = tmp_path / "a.json"
    out_b = tmp_path / "b.json"

    long_plan_build.build_new(script, "fixture_01", "bud", base, out_a)
    long_plan_build.build_new(script, "fixture_01", "bud", base, out_b)

    assert out_a.read_bytes() == out_b.read_bytes()
    row = json.loads(out_a.read_text(encoding="utf-8"))[0]
    assert len(row["script"]) == 7
    assert row["script"][0] == "**Chương Một**"
    assert row["script"][4] == "**Chương Hai**"
    assert row["voices"] == ["ke", "ke", "ta", "ke", "ke", "ke", "ke"]
    assert row["beats"] == {"3": "silence", "7": "hit"}
    assert row["silence"] == [3]
    assert row["clips"] == {"6": "C2"}
    assert sum(line.startswith("**") for line in row["script"]) == 2
