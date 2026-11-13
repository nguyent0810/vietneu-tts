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
    assert row["layout_policy"] == "v2"
    assert {"temperature", "text_mode"} <= set(row["tts"])
    assert row["sound"].get("preset_long") == "C"
    assert row["tts"].get("voice")  # wire_plan_row nạp giọng kênh
    assert row["silence"] == [3]
    assert row["clips"] == {"6": "C2"}
    assert sum(line.startswith("**") for line in row["script"]) == 2


def test_builder_does_not_embed_mui_birth_years():
    source = MODULE.read_text(encoding="utf-8")
    assert "1967" not in source
    assert "1979" not in source
    assert "1991" not in source
    assert "2003" not in source
    assert "2015" not in source
    assert "NĂM ĐINH MÙI 2027" not in source
    assert "flap_label" not in source


def test_heading_rule_matches_engine():
    assert long_plan_build.is_heading("**Chương Một**")
    assert not long_plan_build.is_heading("**Năm tuổi** của anh.")
    assert not long_plan_build.is_heading("Một tờ **đơn** nằm trên bàn.")


def test_cli_runs_from_repo_root(tmp_path):
    import subprocess
    import sys
    root = MODULE.resolve().parents[1]
    script = tmp_path / "s.txt"
    script.write_text("**Chương Một**\n**Năm tuổi** của anh.\nKết lại bằng một câu.\n", encoding="utf-8")
    base = tmp_path / "base.json"
    base.write_text(json.dumps([{"style": "studio_long", "series": "fs", "lane": "long"}]), encoding="utf-8")
    out = tmp_path / "plan.json"
    r = subprocess.run([sys.executable, str(MODULE), "--script", str(script), "--id", "L_cli", "--series", "fs",
                        "--base", str(base), "--out", str(out)], cwd=root, capture_output=True, text=True,
                       env={k: v for k, v in __import__("os").environ.items() if k != "PYTHONPATH"})
    assert r.returncode == 0, r.stderr[-800:]
    row = json.loads(out.read_text(encoding="utf-8"))[0]
    assert [a["chapter"] for a in row["ambience"]] == [1]  # code cũ đếm cả "**Năm tuổi** của anh." -> 2 chương
