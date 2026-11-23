"""Đo số ngày Short đã phủ liên tục cho FS và BUD."""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import importlib.util
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/cl_staging/short_runway.json"
CHANNELS = {"FS": ".youtube_channels/phong_thuy.json",
            "BUD": ".youtube_channels/phat_giao.json"}


def summarize(coverage: dict[str, int], start: dt.date, days: int, target: int) -> dict:
    dates = [(start + dt.timedelta(days=i)).isoformat() for i in range(days)]
    table = {day: int(coverage.get(day, 0)) for day in dates}
    consecutive = 0
    for n in table.values():
        if n < target:
            break
        consecutive += 1
    gap = next((day for day, n in table.items() if n < target), None)
    return {"days_covered": consecutive, "first_missing_day": gap,
            "coverage": table}


def coverage_from_hf(credentials: str, start: dt.date, days: int, target: int) -> dict[str, int]:
    spec = importlib.util.spec_from_file_location("hf_coverage", ROOT / "hf_coverage.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = module.main(["--credentials", credentials, "--from", start.isoformat(),
                            "--days", str(days), "--target", str(target), "--json"])
    if code:
        raise RuntimeError(f"hf_coverage thất bại ({code}) cho {credentials}")
    result = json.loads(output.getvalue())
    return {str(day): int(n) for day, n in result["coverage"].items()}


def measure(target: int = 5, days: int = 14, today: dt.date | None = None,
            coverage_loader=coverage_from_hf) -> dict:
    today = today or dt.date.today()
    channels = {}
    for name, credential in CHANNELS.items():
        counts = coverage_loader(str(ROOT / credential), today, days, target)
        channels[name] = summarize(counts, today, days, target)
    return {"measured_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "start_date": today.isoformat(), "target": target, "days": days,
            "channels": channels}


def print_report(data: dict) -> None:
    print(f"Đo lúc: {data.get('measured_at', 'UNKNOWN')} | đích {data.get('target', '?')} video/ngày")
    for name, channel in data.get("channels", {}).items():
        print(f"\n{name}: còn {channel.get('days_covered', 0)} ngày phủ liên tục; "
              f"ngày đầu thiếu: {channel.get('first_missing_day') or 'không thiếu trong bảng'}")
        print("ngày         số video")
        for day, count in channel.get("coverage", {}).items():
            print(f"{day}   {count}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=int, default=5)
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--offline", action="store_true", help="chỉ đọc cache, không gọi API")
    args = parser.parse_args(argv)
    if args.target < 1 or args.days < 1:
        parser.error("--target và --days phải >= 1")
    if args.offline:
        try:
            data = json.loads(CACHE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Không đọc được cache {CACHE}: {exc}", file=sys.stderr)
            return 1
    else:
        data = measure(args.target, args.days)
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print_report(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
