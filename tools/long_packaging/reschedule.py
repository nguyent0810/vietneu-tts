#!/usr/bin/env python3
"""Dời lịch phát hành video Long theo bảng ngày định trước.

Xử lý chuỗi ô bị chiếm (topological order) để tránh đè slot.
Mặc định chạy khô (dry-run). Ghi sổ khôi phục.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

DEFAULT_CREDS = {
    "fs": ".youtube_channels/phong_thuy.json",
    "bud": ".youtube_channels/phat_giao.json",
}


def normalize_target_time(target_str: str, year: int = 2026, time_utc: str = "13:00") -> str:
    """Chuẩn hoá chuỗi ngày tháng (vd '11-12' hoặc '2026-11-12T13:00') thành 'YYYY-MM-DDTHH:MM'."""
    s = target_str.strip()
    if "T" in s:
        return s[:16]
    if len(s) == 5 and s[2] == "-":
        return f"{year}-{s}T{time_utc}"
    if len(s) == 10 and s[4] == "-":
        return f"{s}T{time_utc}"
    return s


def reschedule_channel(
    ch: str,
    target_map: dict[str, str],
    current_rows: dict[str, dict[str, Any]],
    creds_path: str,
    confirm: bool = False,
    year: int = 2026,
    time_utc: str = "13:00",
    update_fn: Optional[Callable[..., Any]] = None,
) -> list[dict[str, Any]]:
    """Xử lý dời lịch cho một kênh với giải thuật gỡ ô bị chiếm và phá vòng lặp."""
    unknown = set(target_map) - set(current_rows)
    if unknown:
        raise ValueError(f"Có video trong target_map không tồn tại ở kênh {ch}: {unknown}")

    pos: dict[str, str] = {k: current_rows[k]["when"][:16] for k in current_rows}
    todo: dict[str, str] = {}
    for k, d in target_map.items():
        tgt = normalize_target_time(d, year=year, time_utc=time_utc)
        if pos[k] != tgt:
            todo[k] = tgt

    log: list[dict[str, Any]] = []
    cycle_hop_count = 0

    while todo:
        progressed = False
        # Ưu tiên dời các mốc xa hơn trước
        for k, tgt in sorted(todo.items(), key=lambda x: x[1], reverse=True):
            # Kiểm tra xem ô đích có đang bị video khác chiếm không
            holder = [o for o, p in pos.items() if p == tgt and o != k]
            fixed = [o for o in holder if o not in todo]
            if fixed:
                raise ValueError(f"Không dời được {k} sang {tgt}: ô đang có video không nằm trong danh sách dời {fixed}")
            if holder:
                continue

            v_info = current_rows[k]
            v_id = v_info.get("id") or v_info.get("video_id")
            v_title = v_info.get("title", "")[:40]

            mode_str = "DỜI" if confirm else "[DRY]"
            print(f"{mode_str} {ch} {k}: {pos[k]} -> {tgt}  {v_title}")

            if confirm and update_fn:
                update_fn(v_id, creds_path, publish_at=tgt + ":00Z")

            log.append({
                "ch": ch,
                "key": k,
                "id": v_id,
                "old": pos[k] + ":00Z",
                "new": tgt + ":00Z",
            })
            pos[k] = tgt
            del todo[k]
            progressed = True
            break

        if not progressed:
            # Phát hiện kẹt vòng: chuyển một video tạm thời sang slot phụ
            cycle_hop_count += 1
            if cycle_hop_count > 50:
                raise RuntimeError(f"Kẹt vòng không thể giải quyết ở kênh {ch}: {todo}")

            hop_k = sorted(todo.keys())[0]
            temp_slot = f"{year}-12-31T23:{cycle_hop_count:02d}"
            v_info = current_rows[hop_k]
            v_id = v_info.get("id") or v_info.get("video_id")

            print(f"[CYCLE-HOP] {ch} {hop_k}: {pos[hop_k]} -> {temp_slot} (chờ giải phóng)")
            if confirm and update_fn:
                update_fn(v_id, creds_path, publish_at=temp_slot + ":00Z")

            log.append({
                "ch": ch,
                "key": hop_k,
                "id": v_id,
                "old": pos[hop_k] + ":00Z",
                "new": temp_slot + ":00Z",
                "is_temp": True,
            })
            pos[hop_k] = temp_slot

    return log


def reschedule_videos(
    schedule_data: dict[str, dict[str, str]],
    current_data: dict[str, list[dict[str, Any]]],
    confirm: bool = False,
    recovery_file: Optional[Path | str] = None,
    creds_map: Optional[dict[str, str]] = None,
    year: int = 2026,
    time_utc: str = "13:00",
    update_fn: Optional[Callable[..., Any]] = None,
) -> list[dict[str, Any]]:
    """Dời lịch toàn bộ các kênh theo kế hoạch."""
    creds = creds_map or DEFAULT_CREDS

    if confirm and update_fn is None:
        try:
            from youtube_upload import update_video  # type: ignore
            update_fn = update_video
        except ImportError:
            raise

    all_logs: list[dict[str, Any]] = []

    for ch, target_map in schedule_data.items():
        if ch not in current_data:
            continue
        rows_list = current_data[ch]
        rows_dict = {r.get("key", r.get("id")): r for r in rows_list}
        cred_path = creds.get(ch, "")

        ch_log = reschedule_channel(
            ch=ch,
            target_map=target_map,
            current_rows=rows_dict,
            creds_path=cred_path,
            confirm=confirm,
            year=year,
            time_utc=time_utc,
            update_fn=update_fn,
        )
        all_logs.extend(ch_log)

    if confirm and all_logs:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d")
        out_recovery = (
            Path(recovery_file)
            if recovery_file
            else Path(f"output/cl_staging/long/resched_long_{now_str}.json")
        )
        out_recovery.parent.mkdir(parents=True, exist_ok=True)
        with out_recovery.open("w", encoding="utf-8") as f:
            json.dump(all_logs, f, ensure_ascii=False, indent=2)
        print(f"Đã ghi sổ khôi phục: {out_recovery}")

    return all_logs


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dời lịch Long theo bảng ngày định trước (mặc định dry-run)."
    )
    parser.add_argument("current", help="File JSON chứa lịch hiện tại của kênh (vd: current_schedule.json)")
    parser.add_argument("--schedule", help="File JSON chứa bảng lịch mới theo kênh (ch -> key -> target)")
    parser.add_argument("--confirm", action="store_true", help="Thực thi gọi API dời lịch thật")
    parser.add_argument("--recovery-file", help="File ghi sổ khôi phục (JSON)")
    parser.add_argument("--year", type=int, default=2026, help="Năm áp dụng (mặc định 2026)")
    parser.add_argument("--time", default="13:00", help="Giờ UTC (mặc định 13:00 = 20:00 VN)")

    args = parser.parse_args(argv)

    current_data = json.load(open(args.current, encoding="utf-8"))

    if args.schedule:
        schedule_data = json.load(open(args.schedule, encoding="utf-8"))
    else:
        # Bảng lịch mặc định theo quyết định PO 11/11 nếu không chỉ định file
        schedule_data = {
            "fs": {
                "L_fs_26": "11-12", "L_fs_17": "11-14", "L_fs_tv06": "11-17", "L_fs_18": "11-19",
                "L_fs_19": "11-21", "L_fs_27": "11-23", "L_fs_20": "11-25", "L_fs_21": "11-27",
                "L_fs_22": "11-29", "L_fs_12": "12-01", "L_fs_15": "12-03", "L_fs_13": "12-05",
                "L_fs_14": "12-07", "L_fs_16": "12-09"
            },
            "bud": {
                "L_bud_25": "11-14", "L_bud_16": "11-18", "L_bud_26": "11-20", "L_bud_17": "11-24",
                "L_bud_18": "11-26", "L_bud_11": "11-30", "L_bud_20": "12-02", "L_bud_21": "12-04",
                "L_bud_09": "12-06", "L_bud_23": "12-08", "L_bud_10": "12-10", "L_bud_15": "12-12",
                "L_bud_13": "12-14"
            },
        }

    reschedule_videos(
        schedule_data=schedule_data,
        current_data=current_data,
        confirm=args.confirm,
        recovery_file=args.recovery_file,
        year=args.year,
        time_utc=args.time,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
