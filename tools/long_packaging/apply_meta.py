#!/usr/bin/env python3
"""Áp tiêu đề, 2 câu đầu mô tả và tag cho video đã hẹn giờ trên YouTube.

Mặc định chạy khô (dry-run). Ghi bản sao lưu trước khi áp.
Giữ nguyên mục lục chương, lời miễn trừ và lịch hẹn (không truyền publish_at).
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

DEFAULT_CREDS = {
    "fs": ".youtube_channels/phong_thuy.json",
    "bud": ".youtube_channels/phat_giao.json",
}


def prepare_metadata_update(
    current_snippet: dict[str, Any],
    new_title: str,
    desc_head: str,
    new_tags: list[str],
) -> tuple[str, str, list[str]]:
    """Tính toán tiêu đề, mô tả mới (thay đoạn mở đầu) và gộp tags."""
    if len(new_title) > 100:
        raise ValueError(f"Tiêu đề vượt quá 100 ký tự ({len(new_title)}): {new_title}")
    if "<" in new_title or ">" in new_title:
        raise ValueError(f"Tiêu đề chứa ký tự không hợp lệ '<' hoặc '>': {new_title}")

    current_desc = (current_snippet.get("description") or "")
    parts = current_desc.split("\n\n", 1)
    if len(parts) > 1:
        updated_desc = desc_head.strip() + "\n\n" + parts[1]
    else:
        updated_desc = desc_head.strip() + "\n\n" + current_desc

    if len(updated_desc) > 5000:
        raise ValueError(f"Mô tả mới vượt quá 5000 ký tự ({len(updated_desc)})")

    # Gộp tags giữ nguyên thứ tự ưu tiên tag mới, sau đó tag cũ
    combined_tags = list(dict.fromkeys([*(new_tags or []), *(current_snippet.get("tags") or [])]))
    while len(",".join(combined_tags)) > 480 and combined_tags:
        combined_tags.pop()

    return new_title, updated_desc, combined_tags


def apply_metadata(
    items: list[dict[str, Any]],
    confirm: bool = False,
    backup_file: Optional[Path | str] = None,
    creds_map: Optional[dict[str, str]] = None,
    fetch_fn: Optional[Callable[[str, Any], dict[str, Any]]] = None,
    update_fn: Optional[Callable[..., Any]] = None,
    refresh_fn: Optional[Callable[[str], Any]] = None,
) -> dict[str, Any]:
    """Áp dụng metadata cho danh sách video.

    items: danh sách dict chứa:
      - key: mã video (vd: L_fs_18)
      - video_id: id YouTube
      - title: tiêu đề mới
      - desc_head: 2 câu đầu mở đầu mô tả
      - tags: danh sách tags mới
    """
    creds = creds_map or DEFAULT_CREDS

    # Trì hoãn import để dễ dàng mock trong unit test
    if fetch_fn is None or update_fn is None or refresh_fn is None:
        try:
            from youtube_upload import (  # type: ignore
                _fetch_video_snippet_status,
                _refresh_or_raise,
                update_video,
            )
            fetch_fn = fetch_fn or _fetch_video_snippet_status
            update_fn = update_fn or update_video
            refresh_fn = refresh_fn or _refresh_or_raise
        except ImportError:
            if not confirm:
                # Trong chế độ dry-run nếu chưa cài/thiếu youtube_upload thì dùng hàm giả lập
                pass
            else:
                raise

    backups: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []

    for item in items:
        k = item["key"]
        v_id = item["video_id"]
        title = item["title"]
        desc_head = item["desc_head"]
        tags_input = item.get("tags", [])
        ch = item.get("channel") or ("fs" if k.startswith("L_fs") else "bud")
        cred_path = creds.get(ch, "")

        if fetch_fn and refresh_fn:
            service_or_cred = refresh_fn(cred_path) if refresh_fn else cred_path
            raw_data = fetch_fn(v_id, service_or_cred)
            current_snippet = raw_data.get("snippet", raw_data)
        else:
            current_snippet = item.get("current_snippet", {})

        cur_title = current_snippet.get("title", "")
        cur_desc = (current_snippet.get("description") or "")
        cur_tags = current_snippet.get("tags") or []

        # Lưu bản sao lưu
        backups.append({
            "key": k,
            "id": v_id,
            "title": cur_title,
            "description": cur_desc,
            "tags": cur_tags,
        })

        final_title, final_desc, final_tags = prepare_metadata_update(
            current_snippet, title, desc_head, tags_input
        )

        mode_str = "ÁP" if confirm else "[DRY]"
        print(
            f"{mode_str} {k} ({v_id}): {final_title} | mô tả mở: {desc_head[:60]}… | {len(final_tags)} tags"
        )

        if confirm and update_fn:
            update_fn(v_id, cred_path, title=final_title, description=final_desc, tags=final_tags)

        actions.append({
            "key": k,
            "video_id": v_id,
            "title": final_title,
            "description": final_desc,
            "tags": final_tags,
        })

    if confirm and backups:
        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_backup = (
            Path(backup_file)
            if backup_file
            else Path(f"output/cl_staging/long/backup_before_seo_{now_str}.json")
        )
        out_backup.parent.mkdir(parents=True, exist_ok=True)
        with out_backup.open("w", encoding="utf-8") as f:
            json.dump(backups, f, ensure_ascii=False, indent=2)
        print(f"Đã lưu bản sao lưu vào: {out_backup}")

    return {
        "confirm": confirm,
        "count": len(actions),
        "actions": actions,
        "backups": backups,
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Áp tiêu đề, mở đầu mô tả và tags cho video đã hẹn (mặc định dry-run)."
    )
    parser.add_argument("--meta", help="File JSON chứa toàn bộ metadata (key, video_id, title, desc_head, tags)")
    parser.add_argument("--titles", help="File JSON mapping key -> title hoặc chuỗi JSON")
    parser.add_argument("--draft", help="File draft.json (chứa desc_head, tags)")
    parser.add_argument("--current", help="File current.json (chứa key, video_id)")
    parser.add_argument("--confirm", action="store_true", help="Thực thi áp thật (mặc định chỉ dry-run)")
    parser.add_argument("--backup-file", help="Đường dẫn file lưu bản backup")

    args = parser.parse_args(argv)

    items: list[dict[str, Any]] = []

    if args.meta:
        meta_path = Path(args.meta)
        items = json.load(meta_path.open(encoding="utf-8"))
    elif args.titles and args.draft and args.current:
        # Hỗ trợ dạng rời như script lead
        titles_data = (
            json.load(open(args.titles, encoding="utf-8"))
            if Path(args.titles).exists()
            else json.loads(args.titles)
        )
        raw_current = json.load(open(args.current, encoding="utf-8"))
        if isinstance(raw_current, dict):
            flat_list = [
                item for items in raw_current.values() if isinstance(items, list) for item in items
            ]
        else:
            flat_list = raw_current
        current_data = {
            o.get("key", o.get("id")): o for o in flat_list if isinstance(o, dict)
        }

        t_text = open(args.draft, encoding="utf-8").read()
        match = re.search(r"\[.*\]", t_text, re.S)
        draft_list = json.loads(match.group(0)) if match else json.loads(t_text)
        draft_data = {d["key"]: d for d in draft_list}

        for k, title in titles_data.items():
            if k in current_data and k in draft_data:
                items.append({
                    "key": k,
                    "video_id": current_data[k].get("video_id") or current_data[k].get("id"),
                    "title": title,
                    "desc_head": draft_data[k].get("desc_head", ""),
                    "tags": draft_data[k].get("tags", []),
                })
    else:
        parser.print_help()
        return 1

    apply_metadata(items, confirm=args.confirm, backup_file=args.backup_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
