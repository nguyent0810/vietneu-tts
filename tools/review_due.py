"""Lead tự nhắc nhìn lại số liệu (không cron): chạy đầu mỗi phiên, in việc đã quá hạn.

    .venv/bin/python tools/review_due.py          # xem việc quá hạn
    .venv/bin/python tools/review_due.py done tuan  # ghi đã làm review tuần hôm nay
    .venv/bin/python tools/review_due.py done thang

Tuần (quá 7 ngày): hf_brief cả hai kênh -> đọc briefs/<kênh>.md, điểm rơi, số bài > 10k, tỉ lệ AVP >= 1,3× nhóm độ dài, nhân khuôn, luật dừng khuôn
    -> đề xuất chủ đề tuần (nhân khuôn theo mục "nên nhân khuôn", dừng khuôn bị báo DỪNG, cùng họ chưa làm, loại theo sổ thất bại) -> người dùng duyệt.
Tháng (đã sang tháng mới): phân tích theo dạng bài như docs/adr/0017 (scoreboard/top28.py, đổi cửa sổ),
    so 4 tuần, đề xuất mở/đóng chuỗi, thêm dòng sổ thất bại (ADR 0017), cập nhật Sổ tay.
Thí nghiệm (experiments/tn_*.json): in TN đã tới ngày đo mà chưa có "ket_qua".
Sổ: review_log.json cạnh file này. Không gọi API, không sửa gì ngoài sổ.
"""
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "output/cl_staging"
LOG = HERE / "review_log.json"
BRIEFS = HERE / "briefs"


def load() -> dict:
    return json.loads(LOG.read_text(encoding="utf-8")) if LOG.exists() else {}


def due(today: date, log: dict) -> list[str]:
    out = []
    last_w = date.fromisoformat(log["tuan"]) if log.get("tuan") else None
    if not last_w or (today - last_w).days > 7:
        ages = []
        for ch in ("bud", "fs"):
            f = BRIEFS / f"{ch}.md"
            ages.append(f"{ch} {(today - datetime.fromtimestamp(f.stat().st_mtime).date()).days} ngày" if f.exists() else f"{ch} chưa có")
        out.append(f"REVIEW TUẦN quá hạn (lần cuối {last_w or 'chưa có'}; bản tin: {', '.join(ages)})")
    last_m = date.fromisoformat(log["thang"]) if log.get("thang") else None
    if not last_m or (last_m.year, last_m.month) < (today.year, today.month):
        out.append(f"REVIEW THÁNG {today:%m/%Y} chưa làm (lần cuối {last_m or 'chưa có'})")
    for f in sorted((HERE / "experiments").glob("tn_*.json")):
        for t in json.loads(f.read_text(encoding="utf-8")).get("tn", []):
            if not t.get("ket_qua") and date.fromisoformat(t["ngay_do"]) <= today:
                out.append(f"ĐO {t['ma']} ({t['kenh']}) tới hạn {t['ngay_do']}: {t['do']} Thắng: {t['thang']}. ({f.name})")
    return out


def main(argv: list[str]) -> int:
    if argv == ["--help"]:
        import argparse
        argparse.ArgumentParser(description=__doc__).print_help()
        return 0
    health = ROOT / "scripts/agents/loop_health.py"
    python = ROOT / ".venv/bin/python"
    if health.exists() and python.exists():
        print("LOOP HEALTH", flush=True)
        subprocess.run([str(python), str(health)], check=False)
    log, today = load(), date.today()
    if argv[:1] == ["done"] and len(argv) == 2 and argv[1] in ("tuan", "thang"):
        log[argv[1]] = today.isoformat()
        LOG.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"ghi: review {argv[1]} {today}")
        return 0
    items = due(today, log)
    print("\n".join(items) if items else f"không có review quá hạn (tuần {log.get('tuan')}, tháng {log.get('thang')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
