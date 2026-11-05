"""One render entry point for an existing creator spec or batch plan.

This adapter does not build editorial inputs or upload. It keeps each existing
renderer in charge of its own voice, media, quality gates, and output paths.
"""
from __future__ import annotations

import argparse
import json
import importlib.util
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from library.tools import channel_profile


ROOT = Path(__file__).resolve().parent
CREATOR = ROOT / "creator_v2"
CODE = ROOT / "creator_v2"      # nơi có code renderer; CREATOR chỉ là nơi tìm data/output (test đổi được)
# Phải khớp hf_batch_render.PLACEHOLDER_SCRIPT (có test đối chiếu mã nguồn).
PLACEHOLDER_SCRIPT = ["(đã render trước, giữ nguyên file)"]
RENDERERS = {"casewide", "casefile", "hf_batch", "studio"}
LONG_STEPS = ("tts", "html", "render", "final")


@dataclass
class Plan:
    channel: str
    kind: str
    engine: str
    theme: str | None
    cwd: Path
    steps: list[list[str]]
    outdir: Path | None = None      # Long creator_v2: thư mục có final.run.json
    expect: Path | None = None      # hf_batch: file mp4 phải có sau khi chạy
    allow_existing: bool = False
    blockers: list[str] = field(default_factory=list)   # điều kiện renderer sẽ chặn; fail trước khi tốn TTS
    theme_spec: str | None = None
    theme_profile: str | None = None


def _long_module(name: str):
    path = CODE / "motion" / "long" / f"{name}.py"
    for p in (str(CODE), str(CODE / "motion" / "long")):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location(f"_make_video_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def long_blockers(topic: str) -> list[str]:
    """Những gì build_long sẽ chặn sau khi đã tốn TTS: dấu soát clip/ảnh (_refuse_unreviewed_sheets), chọn take."""
    data, out = CREATOR / "data" / "long" / topic, CREATOR / "output" / "long" / topic
    problems = []
    try:
        clip, img = _long_module("clip_sheet"), _long_module("img_sheet")
        checks = (("clip", clip.clip_uses(data), clip.uses_hash, clip.ok_path(out), f"python motion/long/clip_sheet.py {topic}"),
                  ("ảnh", img.image_uses(data), img.uses_hash, img.ok_path(out), f"python motion/long/img_sheet.py {topic}"))
        for kind, uses, hash_fn, mark, command in checks:
            if not uses:
                continue
            actual = mark.read_text(encoding="utf-8").strip() if mark.exists() else ""
            if actual != hash_fn(uses):
                state = "thiếu dấu" if not actual else "dấu đã cũ (cảnh đã đổi sau khi soát)"
                problems.append(f"{kind}: {state}. Chạy `{command}`, mở tờ soát, rồi chạy `{command} --ok`.")
    except Exception as exc:    # noqa: BLE001  (không kiểm được thì không cho chạy, đừng đoán)
        problems.append(f"không kiểm được dấu soát clip/ảnh ({type(exc).__name__}: {exc})")
    cache = out / "tts"
    if (cache / "takes.json").exists() and not (cache / "picks.json").exists():
        problems.append(f"đã có tts/takes.json nhưng chưa có tts/picks.json: chạy `build_long.py {topic} pick` "
                        "(nếu không, `tts` dùng take 0 cho mọi câu)")
    return problems


def final_problems(outdir: Path) -> list[str]:
    """Gọi cổng manifest Long (GH-170) của chính renderer, không tự đoán trạng thái."""
    path = CREATOR / "motion" / "long" / "long_output.py"
    spec = importlib.util.spec_from_file_location("_make_video_long_output", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.final_problems(outdir, full=True)


def _object(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Không đọc được JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: spec phải là object JSON")
    return value


def _input(kind: str, source: Path, only: str | None) -> tuple[dict, str | None]:
    if source.is_dir():
        if not only or not only.strip():
            raise ValueError("Thư mục plan cần --only <id> để không dựng cả lô")
        rows = []
        for path in sorted(source.glob("plan_*.json")):
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(f"Không đọc được plan {path}: {exc}") from exc
            if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
                raise ValueError(f"{path}: plan phải là list các object")
            rows.extend(value)
        matches = [row for row in rows if isinstance(row.get("id"), str) and row["id"].startswith(only)]
        if len(matches) != 1 or matches[0]["id"] != only:
            raise ValueError(f"--only {only!r} phải khớp đúng một id, không phải tiền tố của id khác")
        row = matches[0]
        if row.get("lane") != kind:
            raise ValueError(f"Plan {only!r}: lane phải là {kind!r}")
        return row, only
    if only:
        raise ValueError("--only chỉ dùng với thư mục plan")
    if not source.is_file():
        raise ValueError(f"Không có spec {source}")
    return _object(source), None


def plan(kind: str, source: Path, *, only: str | None = None, channel: str | None = None,
         slot: str | None = None, allow_existing: bool = False) -> Plan:
    """Validate the input and return what would run, without side effects."""
    source = source.resolve()
    item, selected = _input(kind, source, only)
    slug = item.get("id") or item.get("slug") or source.stem
    if not isinstance(slug, str):
        raise ValueError("id/slug của spec hoặc plan phải là chuỗi")
    ident_item = item
    if selected is not None and not (item.get("channel") or item.get("kenh")) and item.get("series"):
        ident_item = {**item, "channel": item["series"]}   # plan row: series chính là kênh
    ident = channel_profile.resolve(ident_item, channel=channel, slug=slug)
    profile = channel_profile.load(ident)
    if channel and channel_profile.resolve(channel=channel) != ident:
        raise ValueError("--channel không khớp channel/kenh của spec hoặc plan")
    dispatch = profile.get("dung")
    choice = dispatch.get(kind) if isinstance(dispatch, dict) else None
    if not isinstance(choice, dict) or choice.get("engine") not in RENDERERS:
        raise ValueError(f"{ident}: thiếu hoặc sai dung.{kind}.engine trong hồ sơ")
    engine = choice["engine"]
    themes = profile.get("theme") if isinstance(profile.get("theme"), dict) else {}
    theme = item.get("theme") or themes.get(kind)
    if slot is not None and engine != "casefile":
        raise ValueError("--slot chỉ dùng cho Short creator_v2 (casefile)")
    py = sys.executable

    def make(cwd: Path, *steps: list[str], outdir: Path | None = None) -> Plan:
        return Plan(ident, kind, engine, theme, cwd, [list(s) for s in steps], outdir,
                    allow_existing=allow_existing, theme_spec=item.get("theme"),
                    theme_profile=themes.get(kind))

    if selected is not None:
        if engine != "hf_batch":
            raise ValueError(f"{ident}: thư mục plan chỉ hợp với engine hf_batch")
        if channel_profile.resolve({"channel": item.get("series")}) != ident:
            raise ValueError(f"Plan {selected!r}: series phải là {ident!r}")
        # hf_batch's --only is a prefix filter; a second id sharing this prefix
        # would render too, so the exact-id check in _input is mandatory.
        script = item.get("script")
        if not isinstance(script, list) or not script or script == PLACEHOLDER_SCRIPT:
            raise ValueError(f"Plan {selected!r}: script rỗng hoặc là placeholder; hf_batch sẽ bỏ qua nhưng vẫn thoát 0")
        mp4 = source / "out" / f"{selected}.mp4"
        if mp4.exists() and not item.get("chapters") and not allow_existing:
            raise ValueError(f"Plan {selected!r}: {mp4} đã có, hf_batch sẽ không dựng lại; "
                             "xoá file hoặc truyền --allow-existing nếu chủ động muốn giữ")
        p = make(ROOT, [py, str(ROOT / "hf_batch_render.py"), str(source), "--only", selected])
        p.expect = mp4
        return p
    if engine == "hf_batch":
        raise ValueError("hf_batch cần thư mục plan và --only <id>")
    if engine == "casewide":
        if kind != "long":
            raise ValueError("casewide chỉ dựng Long")
        if not item.get("channel"):
            raise ValueError("casewide spec phải ghi channel để renderer đọc đúng hồ sơ")
        expected = CREATOR / "data" / "long" / source.parent.name / "spec.json"
        if source != expected.resolve():
            raise ValueError(f"casewide cần spec tại {expected}")
        topic = source.parent.name
        script = str(CREATOR / "motion/long/build_long.py")
        p = make(CREATOR, *([py, script, topic, step] for step in LONG_STEPS),
                 outdir=CREATOR / "output" / "long" / topic)
        p.blockers = long_blockers(topic)
        return p
    if engine == "casefile":
        expected = CREATOR / "data/stier/specs" / source.name
        if kind != "short" or source != expected.resolve():
            raise ValueError(f"casefile cần Short spec tại {expected}")
        if "theme" in item and (not isinstance(item["theme"], str) or not item["theme"].strip()):
            raise ValueError("casefile spec.theme phải là chuỗi không rỗng khi đã khai báo")
        default_theme = themes.get("short")
        allowed = themes.get("short_allowed") or []
        if item.get("theme") and item["theme"] != default_theme and item["theme"] not in allowed:
            raise ValueError(f"{ident}: spec.theme {item['theme']!r} không khớp theme Short của hồ sơ "
                             f"{default_theme!r} (cho phép thêm: {allowed or 'không'})")
        if not item.get("theme") and default_theme != "case":
            raise ValueError(
                f"{ident}: Short spec thiếu theme; casefile sẽ mặc định 'case' "
                f"thay vì theme hồ sơ {default_theme!r}"
            )
        if not item.get("theme") and item.get("mix"):
            raise ValueError("casefile với mix cần spec.theme vì renderer đọc trực tiếp spec['theme']")
        build = str(CREATOR / "motion/stier/build.py")
        extra = ["--slot", slot] if slot is not None else []
        return make(CREATOR, [py, build, source.stem, "--preflight"],
                    [py, build, source.stem, *extra])
    if kind != "short":
        raise ValueError("studio hiện chỉ có hợp đồng Short")
    if not item.get("channel"):
        raise ValueError("Studio spec phải ghi channel để renderer đọc đúng hồ sơ")
    if item.get("lane") not in (None, "short"):
        raise ValueError("Studio spec có lane không khớp short")
    if not item.get("theme"):
        raise ValueError("Studio spec thiếu theme; cần ghi theme trong spec trước khi dựng")
    return make(ROOT, [py, str(ROOT / "studio.py"), "build", str(source), "--render", "--qa", "--strict"])


def run(p: Plan) -> int:
    """Chạy lần lượt; bước đầu tiên lỗi thì dừng và trả nguyên exit code của nó."""
    if p.blockers:
        for blocker in p.blockers:
            print(f"make_video: CHẶN trước khi dựng: {blocker}", file=sys.stderr)
        return 1
    started = time.time()
    for step in p.steps:
        rc = subprocess.run(step, cwd=p.cwd, check=False).returncode
        if rc != 0:
            print(f"make_video: bước {' '.join(step[1:])[:200]} thoát mã {rc}; dừng", file=sys.stderr)
            return rc
    if p.expect is not None:
        if not p.expect.is_file():
            print(f"make_video: LỖI: renderer thoát 0 nhưng không có {p.expect}", file=sys.stderr)
            return 1
        if not p.allow_existing and p.expect.stat().st_mtime < started - 2:
            print(f"make_video: LỖI: {p.expect} không được dựng lại trong lượt này "
                  "(renderer bỏ qua?); truyền --allow-existing nếu chủ động giữ bản cũ", file=sys.stderr)
            return 1
    if p.outdir is not None:
        problems = final_problems(p.outdir)
        if problems:
            for problem in problems:
                print(f"make_video: LỖI final: {problem}", file=sys.stderr)
            return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("long", "short"))
    parser.add_argument("source", type=Path, help="Spec JSON hoặc thư mục chứa plan_*.json")
    parser.add_argument("--only", help="Id chính xác của một row trong plan")
    parser.add_argument("--channel", help="Kênh khi đầu vào không ghi channel/kenh")
    parser.add_argument("--slot", help="Giờ hẹn ISO của Short creator_v2 (chuyển cho build.py --slot)")
    parser.add_argument("--allow-existing", action="store_true",
                        help="hf_batch: chấp nhận mp4 đã có, không dựng lại")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ kiểm và in lệnh, không dựng")
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")   # console Windows cp1252 làm vỡ tiếng Việt
        except (AttributeError, ValueError, OSError):
            pass
    args = parser.parse_args(argv)
    try:
        p = plan(args.kind, args.source, only=args.only, channel=args.channel, slot=args.slot,
                 allow_existing=args.allow_existing)
    except ValueError as exc:
        parser.error(str(exc))
    if args.dry_run:
        print(json.dumps({"channel": p.channel, "kind": p.kind, "engine": p.engine, "theme": p.theme,
                          "theme_spec": p.theme_spec, "theme_profile": p.theme_profile,
                          "cwd": str(p.cwd), "commands": p.steps, "blockers": p.blockers,
                          "after": f"final_problems({p.outdir})" if p.outdir else None},
                         ensure_ascii=False))
        return 1 if p.blockers else 0
    return run(p)


if __name__ == "__main__":
    sys.exit(main())
