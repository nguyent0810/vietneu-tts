#!/usr/bin/env python3
"""Sổ ghi chép thử nghiệm A/B tiêu đề và thumbnail (Test & Compare).

Đọc và ghi sổ packaging_ab.jsonl:
- Video ID / Key
- Các phương án A/B (tiêu đề, thumbnail)
- Ngày bắt đầu, ngày kết thúc
- Impressions, CTR từng phương án
- Bên thắng (winner)
Sổ dữ liệu nằm ngoài git (output/cl_staging/long/packaging_ab.jsonl), mã nằm trong git.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_LEDGER_FILE = "output/cl_staging/long/packaging_ab.jsonl"


def get_default_ledger_path() -> Path:
    env_path = os.environ.get("PACKAGING_AB_LEDGER_PATH")
    if env_path:
        return Path(env_path)
    return Path(DEFAULT_LEDGER_FILE)


def load_ledger(ledger_path: Optional[Path | str] = None) -> list[dict[str, Any]]:
    """Đọc toàn bộ bản ghi từ file jsonl."""
    p = Path(ledger_path) if ledger_path else get_default_ledger_path()
    if not p.exists():
        return []
    entries = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def save_ledger(entries: list[dict[str, Any]], ledger_path: Optional[Path | str] = None) -> None:
    """Lưu toàn bộ bản ghi vào file jsonl."""
    p = Path(ledger_path) if ledger_path else get_default_ledger_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def add_entry(entry: dict[str, Any], ledger_path: Optional[Path | str] = None) -> dict[str, Any]:
    """Thêm một cuộc thử nghiệm A/B mới vào sổ."""
    if not entry.get("video_id") and not entry.get("key"):
        raise ValueError("Bản ghi A/B phải có video_id hoặc key.")

    now_iso = datetime.datetime.now().isoformat()
    record = {
        "video_id": entry.get("video_id", ""),
        "key": entry.get("key", ""),
        "variants": entry.get("variants", {}),
        "start_date": entry.get("start_date") or datetime.date.today().isoformat(),
        "end_date": entry.get("end_date"),
        "impressions": entry.get("impressions", {}),
        "ctr": entry.get("ctr", {}),
        "winner": entry.get("winner", "PENDING"),
        "rule": entry.get("rule", ""),
        "notes": entry.get("notes", ""),
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    entries = load_ledger(ledger_path)
    # Nếu đã có bản ghi cùng video_id và đang PENDING, cập nhật thay vì nhân đôi
    updated = False
    for i, e in enumerate(entries):
        if (record["video_id"] and e.get("video_id") == record["video_id"]) or (
            record["key"] and e.get("key") == record["key"]
        ):
            if e.get("winner") == "PENDING":
                record["created_at"] = e.get("created_at", now_iso)
                entries[i] = record
                updated = True
                break

    if not updated:
        entries.append(record)

    save_ledger(entries, ledger_path)
    return record


def update_entry(
    video_or_key: str, updates: dict[str, Any], ledger_path: Optional[Path | str] = None
) -> dict[str, Any]:
    """Cập nhật kết quả thử nghiệm A/B (impressions, ctr, winner, end_date...)."""
    entries = load_ledger(ledger_path)
    target_idx = -1
    for i, e in enumerate(entries):
        if e.get("video_id") == video_or_key or e.get("key") == video_or_key:
            target_idx = i
            break

    if target_idx == -1:
        raise KeyError(f"Không tìm thấy bản ghi cho {video_or_key} trong sổ A/B.")

    rec = entries[target_idx]
    for k, v in updates.items():
        if k in ("impressions", "ctr", "variants") and isinstance(v, dict):
            rec.setdefault(k, {}).update(v)
        else:
            rec[k] = v

    rec["updated_at"] = datetime.datetime.now().isoformat()
    entries[target_idx] = rec
    save_ledger(entries, ledger_path)
    return rec


def get_entry(video_or_key: str, ledger_path: Optional[Path | str] = None) -> Optional[dict[str, Any]]:
    """Lấy bản ghi A/B theo video_id hoặc key."""
    entries = load_ledger(ledger_path)
    for e in entries:
        if e.get("video_id") == video_or_key or e.get("key") == video_or_key:
            return e
    return None


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Quản lý sổ A/B testing packaging_ab.jsonl")
    subparsers = parser.add_subparsers(dest="command")

    # list
    p_list = subparsers.add_parser("list", help="Liệt kê các cuộc thử nghiệm A/B")
    p_list.add_argument("--file", help="Đường dẫn file jsonl")
    p_list.add_argument("--active", action="store_true", help="Chỉ liệt kê bản ghi đang PENDING")

    # add
    p_add = subparsers.add_parser("add", help="Thêm cuộc thử nghiệm A/B mới")
    p_add.add_argument("--video", required=True, help="Video ID")
    p_add.add_argument("--key", default="", help="Video key (vd: L_fs_tv06)")
    p_add.add_argument("--var-a", required=True, help="Mô tả phương án A (title/thumb)")
    p_add.add_argument("--var-b", required=True, help="Mô tả phương án B (title/thumb)")
    p_add.add_argument("--start", help="Ngày bắt đầu (YYYY-MM-DD)")
    p_add.add_argument("--rule", default="", help="Mã luật thử nghiệm (vd: L1, L2)")
    p_add.add_argument("--notes", default="", help="Ghi chú thêm")
    p_add.add_argument("--file", help="Đường dẫn file jsonl")

    # close
    p_close = subparsers.add_parser("close", help="Đóng cuộc thử nghiệm và ghi nhận kết quả")
    p_close.add_argument("--video", required=True, help="Video ID hoặc key")
    p_close.add_argument("--winner", required=True, choices=["A", "B", "DRAW"], help="Bên thắng")
    p_close.add_argument("--imp-a", type=int, help="Impressions của A")
    p_close.add_argument("--imp-b", type=int, help="Impressions của B")
    p_close.add_argument("--ctr-a", type=float, help="CTR % của A")
    p_close.add_argument("--ctr-b", type=float, help="CTR % của B")
    p_close.add_argument("--end", help="Ngày kết thúc (YYYY-MM-DD)")
    p_close.add_argument("--notes", default="", help="Ghi chú kết quả")
    p_close.add_argument("--file", help="Đường dẫn file jsonl")

    args = parser.parse_args(argv)

    if args.command == "list" or not args.command:
        file_path = getattr(args, "file", None)
        active_only = getattr(args, "active", False)
        entries = load_ledger(file_path)
        if active_only:
            entries = [e for e in entries if e.get("winner") == "PENDING"]

        print(f"\n=== SỔ A/B PACKAGING ({len(entries)} bản ghi) ===")
        print(f"{'VIDEO/KEY':<18} | {'NGÀY BẮT ĐẦU':<12} | {'THẮNG':<7} | {'CTR A / B':<14} | {'GHI CHÚ'}")
        print("-" * 75)
        for e in entries:
            v_id = e.get("key") or e.get("video_id")
            s_date = e.get("start_date", "")[:10]
            winner = e.get("winner", "PENDING")
            ctr = e.get("ctr", {})
            ctr_str = f"{ctr.get('A', '-'):.2f}% / {ctr.get('B', '-'):.2f}%" if "A" in ctr and "B" in ctr else "Chưa có"
            notes = e.get("notes", "")[:25]
            print(f"{v_id:<18} | {s_date:<12} | {winner:<7} | {ctr_str:<14} | {notes}")
        print()
        return 0

    elif args.command == "add":
        entry = {
            "video_id": args.video,
            "key": args.key,
            "variants": {"A": args.var_a, "B": args.var_b},
            "start_date": args.start,
            "rule": args.rule,
            "notes": args.notes,
        }
        res = add_entry(entry, args.file)
        print(f"[OK] Đã ghi nhận thử nghiệm A/B cho {res.get('key') or res.get('video_id')}")
        return 0

    elif args.command == "close":
        updates: dict[str, Any] = {
            "winner": args.winner,
            "end_date": args.end or datetime.date.today().isoformat(),
        }
        if args.imp_a is not None or args.imp_b is not None:
            updates["impressions"] = {}
            if args.imp_a is not None:
                updates["impressions"]["A"] = args.imp_a
            if args.imp_b is not None:
                updates["impressions"]["B"] = args.imp_b

        if args.ctr_a is not None or args.ctr_b is not None:
            updates["ctr"] = {}
            if args.ctr_a is not None:
                updates["ctr"]["A"] = args.ctr_a
            if args.ctr_b is not None:
                updates["ctr"]["B"] = args.ctr_b

        if args.notes:
            updates["notes"] = args.notes

        res = update_entry(args.video, updates, args.file)
        print(f"[OK] Đã đóng thử nghiệm A/B cho {res.get('key') or res.get('video_id')}: bên thắng = {args.winner}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
