"""Kiểm lỗi JavaScript của composition trước khi render; thiếu công cụ thì cảnh báo."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def find_tools():
    cache = Path(os.environ.get("LOCALAPPDATA", "")) / "npm-cache" / "_npx"
    modules = sorted(cache.glob("*/node_modules/puppeteer-core/package.json"))
    browsers = sorted((Path.home() / ".cache" / "puppeteer").glob("**/chrome.exe"))
    node = shutil.which("node")
    return (node, modules[-1].parent if modules else None, browsers[-1] if browsers else None)


def parse_result(stdout):
    """Đọc kết quả JSON một dòng từ tiến trình Node."""
    result = json.loads(stdout)
    if not isinstance(result, dict) or not isinstance(result.get("pageerrors"), list):
        raise ValueError("kết quả pagecheck không hợp lệ")
    return result


def check(composition, hf):
    node, puppeteer, chrome = find_tools()
    if not all((node, puppeteer, chrome)):
        print("  ! WARNING pagecheck: thiếu Node, puppeteer-core hoặc Chrome; bỏ qua", flush=True)
        return []
    temp = None
    try:
        fd, name = tempfile.mkstemp(prefix=f"_pagecheck_{composition.stem}_", suffix=".html", dir=hf)
        temp = Path(name)
        os.close(fd)
        shutil.copyfile(composition, temp)
        command = [node, str(Path(__file__).with_suffix(".cjs")), str(puppeteer), str(chrome), str(temp.resolve())]
        result = subprocess.run(command, cwd=hf, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
        data = parse_result(result.stdout)
        for message in data.get("console_errors", []):
            print(f"  ! WARNING console: {message}", flush=True)
        if data.get("fatal") or result.returncode:
            print(f"  ! WARNING pagecheck không hoàn tất: {data.get('fatal') or result.stderr}", flush=True)
        print(f"  pagecheck {composition.name}: timelines {data.get('timelines', {})}", flush=True)
        return [str(e) for e in data["pageerrors"]]
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        print(f"  ! WARNING không chạy được pagecheck: {e}", flush=True)
        return []
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
