"""Chuẩn bị, theo dõi, soát và nhập lô ảnh AI vào kho tài sản."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
# webauto trong repo (creator_v2/webauto, có --strip-mark/--headless); repo V2 cũ chỉ là dự phòng.
DEFAULT_V2 = ROOT / "creator_v2" if (ROOT / "creator_v2" / "webauto" / "flow.py").exists() \
    else Path.home() / "Documents" / "Local AI" / "Youtube_Creator_V2"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def batch_dir(name: str, backend: str) -> Path:
    if not name or Path(name).name != name or name in {".", ".."}:
        raise ValueError("Tên lô phải là một tên thư mục đơn")
    parent = "grokbot" if backend == "chatgpt" else "flow"
    return ROOT / "output" / "cl_staging" / parent / name


RATIOS = ("16:9", "9:16", "1:1", "4:3", "3:4")


def _khung(value: Any) -> str:
    """'16:9 (1920x1080)' -> '16:9'; rỗng nếu không nhận ra (Flow dùng mặc định)."""
    text = str(value)
    return next((r for r in RATIOS if r in text), "")


def _items(data: Any) -> list[dict]:
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("items", data.get("assets", []))
    else:
        items = []
    if not isinstance(items, list) or not items:
        raise ValueError("asset_needs.json cần là danh sách hoặc có khóa items/assets")
    out = []
    for i, raw in enumerate(items, 1):
        if not isinstance(raw, dict):
            raise ValueError(f"Mục {i} phải là object")
        prompt = str(raw.get("prompt") or raw.get("mo_ta") or raw.get("description") or "").strip()
        if not prompt:
            raise ValueError(f"Mục {i} thiếu prompt")
        filename = str(raw.get("filename") or raw.get("file") or f"{i:03}.png")
        if Path(filename).name != filename or Path(filename).suffix.lower() not in IMAGE_SUFFIXES:
            raise ValueError(f"Tên file ảnh không hợp lệ ở mục {i}: {filename}")
        out.append({"id": str(raw.get("id") or f"{i:03}"), "filename": filename,
                    "prompt": prompt, "pham_vi": str(raw.get("pham_vi") or "chung"),
                    "tags": raw.get("tags") if isinstance(raw.get("tags"), list) else [],
                    "khung": _khung(raw.get("khung") or raw.get("ratio") or ""),
                    "backend": ""})
    return out


def plan(needs: Path, name: str, backend: str) -> Path:
    items = _items(json.loads(needs.read_text(encoding="utf-8")))
    if backend not in {"chatgpt", "flow", "both"}:
        raise ValueError("backend phải là chatgpt, flow hoặc both")
    dest = batch_dir(name, "chatgpt" if backend in {"chatgpt", "both"} else "flow")
    dest.mkdir(parents=True, exist_ok=True)
    for item in items:
        item["backend"] = backend
    (dest / "lo.json").write_text(json.dumps({"name": name, "backend": backend, "items": items}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md, txt = [], []
    for item in items:
        md.extend([f"## {item['filename']}", f"Prompt (EN): {item['prompt']}"]
                  + ([f"Khung: {item['khung']}"] if item.get("khung") else []) + [""])
        # Flow đặt tên file tải về theo tên dòng: dùng stem của filename để wait/ingest khớp được
        txt.append(f"{Path(item['filename']).stem} | {item['prompt']}")
    (dest / "prompts.md").write_text("\n".join(md), encoding="utf-8")
    (dest / "prompts.txt").write_text("\n".join(txt) + "\n", encoding="utf-8")
    return dest


def _load_batch(path: Path) -> dict:
    data = json.loads((path / "lo.json").read_text(encoding="utf-8"))
    if not isinstance(data.get("items"), list):
        raise ValueError("lo.json không hợp lệ")
    return data


def _source_dirs(path: Path, backend: str) -> list[tuple[Path, str]]:
    if backend == "both":
        return [(path / "out", "chatgpt"), (path / "raw", "flow")]
    return [(path / ("out" if backend == "chatgpt" else "raw"), backend)]


def _bot_instructions(data: dict) -> str:
    """Lời dặn bot đủ cụ thể như các lô chạy tốt (lib48, lib142): số ảnh, tên file, khung, luật cấm."""
    n = len(data["items"])
    return (f"Tạo đúng {n} ảnh theo prompts.md bằng ChatGPT, mỗi ảnh một chat mới, tên file đúng tiêu đề mục "
            "và đúng khung ghi ở dòng Khung (16:9 = 1920x1080, 9:16 = 1080x1920, 1:1 = 1080x1080). "
            "Không chữ, số, logo, watermark, chữ Hán/Nôm, biển hiệu hay tên thương hiệu trên ảnh; mặt người và tượng không méo. "
            "Ghi out/PROGRESS.txt mỗi 10 ảnh, out/DONE.txt khi xong. KHÔNG dùng credit video Flow.")


def send_chatgpt(path: Path, run: bool = False) -> str:
    url, key = os.environ.get("GROKBOT_WEBHOOK_URL"), os.environ.get("GROKBOT_WEBHOOK_KEY")
    if not url or not key:
        raise RuntimeError("Thiếu GROKBOT_WEBHOOK_URL hoặc GROKBOT_WEBHOOK_KEY")
    payload = {"task": "generate_images", "prompt_file": str(path / "prompts.md"),
               "output_dir": str(path / "out"), "instructions": _bot_instructions(_load_batch(path))}
    curl = ["curl", "-X", "POST", "${GROKBOT_WEBHOOK_URL}", "-H", "Content-Type: application/json",
            "-H", "Authorization: Bearer ${GROKBOT_WEBHOOK_KEY}", "-H", "X-Webhook-Secret: ${GROKBOT_WEBHOOK_KEY}",
            "-d", json.dumps(payload, ensure_ascii=False)]
    command = " ".join('"' + arg + '"' if "${GROKBOT_WEBHOOK_" in arg else shlex.quote(arg) for arg in curl)
    print(command)
    if run:
        import urllib.request
        request = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                     headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}",
                              "X-Webhook-Secret": key})
        with urllib.request.urlopen(request, timeout=60) as response:
            response.read()
        (path / "DA_GUI.txt").write_text(datetime.now(timezone.utc).isoformat() + "\n", encoding="utf-8")
    return command


def run_flow(path: Path, headless: bool = False, runner=subprocess.run) -> list[list[str]]:
    """Một lần `webauto flow generate` cho mỗi khung (Flow chỉ nhận một --ratio mỗi lần)."""
    data = _load_batch(path)
    v2 = Path(os.environ.get("WEBAUTO_REPO", str(DEFAULT_V2))).expanduser()
    # webauto cần playwright/opencv: venv repo chính có thể thiếu -> WEBAUTO_PYTHON (vd venv V2)
    py = os.environ.get("WEBAUTO_PYTHON") or sys.executable
    groups: dict[str, list[dict]] = {}
    for item in data["items"]:
        groups.setdefault(item.get("khung") or "", []).append(item)
    calls = []
    for khung, items in groups.items():
        tag = khung.replace(":", "x") or "macdinh"
        pf = path / f"prompts_{tag}.txt"
        pf.write_text("".join(f"{Path(i['filename']).stem} | {i['prompt']}\n" for i in items), encoding="utf-8")
        argv = [py, "-m", "webauto", "flow", "generate", "--prompts-file", str(pf),
                "--strip-mark", "crop", "--out", str(path / "raw")]
        if khung:
            argv += ["--ratio", khung]
        if headless:
            argv.append("--headless")
        runner(argv, cwd=v2, check=True)
        calls.append(argv)
    return calls


def wait_batch(path: Path, timeout: int = 1800, interval: float = 2) -> bool:
    data = _load_batch(path)
    deadline = time.monotonic() + max(0, timeout)
    while True:
        # backend both: mỗi mục phải có ảnh ở CẢ out/ (ChatGPT) lẫn raw/ (Flow)
        ready = all(all(any(p.suffix.lower() in IMAGE_SUFFIXES and (p.name == item["filename"] or p.name.startswith(Path(item["filename"]).stem + "_")) for p in directory.glob("*")) for directory, _ in _source_dirs(path, data["backend"])) for item in data["items"])
        if ready:
            print("XONG")
            return True
        if time.monotonic() >= deadline:
            print("HẾT HẠN")
            return False
        time.sleep(min(interval, max(0, deadline - time.monotonic())))


def make_sheet(path: Path) -> Path:
    from PIL import Image, ImageDraw, ImageFont
    data = _load_batch(path)
    thumbs = []
    for item in data["items"]:
        for source, backend in _source_dirs(path, data["backend"]):
            candidates = [p for p in source.glob(Path(item["filename"]).stem + "*") if p.suffix.lower() in IMAGE_SUFFIXES]
            for p in candidates:
                with Image.open(p) as im:
                    im = im.convert("RGB"); im.thumbnail((168, 168))
                    thumbs.append((f"{backend}: {p.name}", item["id"], im.copy()))
    cell_w, cell_h, cols = 220, 210, 3
    sheet = Image.new("RGB", (cell_w * cols, cell_h * max(1, (len(thumbs) + cols - 1) // cols)), "white")
    draw = ImageDraw.Draw(sheet)
    for i, (filename, item_id, im) in enumerate(thumbs):
        x, y = (i % cols) * cell_w, (i // cols) * cell_h
        sheet.paste(im, (x, y + 30)); draw.text((x + 4, y + 4), f"{filename} | mục {item_id}", fill="black")
    out = path / "sheet.jpg"; sheet.save(out, quality=90); return out


def ingest(path: Path) -> int:
    if not (path / "LEAD_DA_XEM").is_file():
        raise RuntimeError("Thiếu LEAD_DA_XEM; từ chối ingest")
    from library.tools import assets
    data = _load_batch(path)
    excluded = {line.strip() for line in (path / "LOAI_BO.txt").read_text(encoding="utf-8").splitlines() if line.strip()} if (path / "LOAI_BO.txt").exists() else set()
    by_filename = {item["filename"]: item for item in data["items"]}
    count = 0
    for source_dir, provider in _source_dirs(path, data["backend"]):
        if not source_dir.is_dir():
            continue
        for file in sorted(source_dir.iterdir()):
            if not file.is_file() or file.suffix.lower() not in IMAGE_SUFFIXES or file.name in excluded:
                continue
            item = by_filename.get(file.name)
            if item is None:
                item = next((it for it in data["items"] if file.stem.startswith(Path(it["filename"]).stem)), None)
            if item is None:
                continue
            rec = assets.add_asset(file, pham_vi=item["pham_vi"], prompt=item["prompt"], tags=item["tags"], root=ROOT, manifest_path=assets.DEFAULT_MANIFEST, ai=True)
            records = assets.load_manifest(assets.DEFAULT_MANIFEST)
            for record in records:
                if record.get("sha256") == rec.get("sha256"):
                    record["source"]["type"] = "grokbot" if provider == "chatgpt" else "flow"
                    if provider == "flow":
                        record["strip_mark"] = "crop"
                    break
            assets.write_manifest(assets.DEFAULT_MANIFEST, records)
            count += 1
    return count


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__); sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan"); p.add_argument("asset_needs", type=Path); p.add_argument("--lo", required=True); p.add_argument("--backend", choices=["chatgpt", "flow", "both"], required=True)
    p = sub.add_parser("send-chatgpt"); p.add_argument("batch", type=Path); p.add_argument("--run", action="store_true")
    p = sub.add_parser("run-flow"); p.add_argument("batch", type=Path); p.add_argument("--headless", action="store_true")
    p = sub.add_parser("wait"); p.add_argument("batch", type=Path); p.add_argument("--timeout", type=int, default=1800)
    p = sub.add_parser("sheet"); p.add_argument("batch", type=Path)
    p = sub.add_parser("ingest"); p.add_argument("batch", type=Path)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "plan": print(plan(a.asset_needs, a.lo, a.backend))
        elif a.cmd == "send-chatgpt": send_chatgpt(a.batch, a.run)
        elif a.cmd == "run-flow": print(shlex.join(run_flow(a.batch, a.headless)))
        elif a.cmd == "wait": return 0 if wait_batch(a.batch, a.timeout) else 1
        elif a.cmd == "sheet": print(make_sheet(a.batch))
        elif a.cmd == "ingest": print(f"Đã nạp {ingest(a.batch)} ảnh")
    except Exception as exc:
        print(f"Lỗi: {exc}", file=sys.stderr); return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
