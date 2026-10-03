"""Cấp lại quyền OAuth cho một kênh YouTube, thêm scope youtube.force-ssl (đọc/trả lời bình luận, tải phụ đề).

Dùng client_id/client_secret đã lưu trong .youtube_channels/<label>.json, mở trình duyệt xin quyền, rồi
CHỈ thay file cũ khi kênh vừa đăng nhập đúng là kênh cũ (cùng channel_id). File cũ được giữ lại thành
<label>.json.bak. Chọn nhầm tài khoản -> không ghi đè, báo lỗi.

    .venv/bin/python scripts/reauth_youtube_scope.py phat_giao
    .venv/bin/python scripts/reauth_youtube_scope.py phong_thuy
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import youtube_auth as YA  # noqa: E402

FORCE_SSL = "https://www.googleapis.com/auth/youtube.force-ssl"


def main(label: str) -> int:
    old_path = YA.CREDENTIALS_DIR / f"{label}.json"
    old = json.loads(old_path.read_text(encoding="utf-8"))
    scopes = list(dict.fromkeys(old.get("scopes", YA.DEFAULT_SCOPES) + [FORCE_SSL]))
    tmp_label = f"{label}__reauth"
    new_path = YA.bootstrap(old["client_id"], old["client_secret"], tmp_label, scopes=scopes)
    new = json.loads(new_path.read_text(encoding="utf-8"))
    if new.get("channel_id") != old.get("channel_id"):
        print(f"KHÔNG THAY: vừa đăng nhập kênh '{new.get('channel_title')}' ({new.get('channel_id')}), "
              f"không phải '{old.get('channel_title')}' ({old.get('channel_id')}). Giữ nguyên file cũ.", file=sys.stderr)
        new_path.rename(new_path.with_suffix(".json.wrong_channel"))
        return 1
    new["channel_label"] = label
    old_path.rename(old_path.with_suffix(".json.bak"))
    old_path.write_text(json.dumps(new, ensure_ascii=False, indent=2), encoding="utf-8")
    old_path.chmod(0o600)
    new_path.rename(new_path.with_suffix(".json.used"))
    print(f"OK -- '{label}' ({new.get('channel_title')}) đã có thêm quyền youtube.force-ssl.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
