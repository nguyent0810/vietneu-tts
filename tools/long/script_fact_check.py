#!/usr/bin/env python3
"""Validate calendar and birth-year claims against a supplied facts directory."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CAN = "Giáp|Ất|Bính|Đinh|Mậu|Kỷ|Canh|Tân|Nhâm|Quý"
CHI = "Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi"
THAN = "Thanh Long|Minh Đường|Thiên Hình|Chu Tước|Kim Quỹ|Kim Đường|Bạch Hổ|Ngọc Đường|Thiên Lao|Nguyên Vũ|Tư Mệnh|Câu Trần"
SAO = ["La Hầu", "Kế Đô", "Thái Dương", "Thái Âm", "Thái Bạch", "Thủy Diệu", "Mộc Đức", "Vân Hớn", "Thổ Tú"]
HOANG_OC = ["Ngũ Thọ Tử", "Lục Hoang Ốc", "Tam Địa Sát", "Nhất Cát", "Nhì Nghi", "Tứ Tấn Tài"]


def _facts(facts_dir: Path):
    day_map = {}
    years = {}
    for path in sorted(facts_dir.glob("*_facts.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for day in data.get("days", []):
            y, m, d = map(int, day["duong"].split("-"))
            day_map[(d, m)] = day
        for birth in data.get("birth_years", []):
            for year in birth.get("cac_nam", []):
                years.setdefault(str(birth["nam_sinh"]), (birth, {}))[1][year["nam"]] = year
    return day_map, years


def _negated(text: str, start: int) -> bool:
    prefix = text[max(0, start - 24):start].lower()
    return bool(re.search(r"(?:không|chưa)\s+(?:phạm\s+)?$", prefix))


def check_text(text: str, facts_dir: str | Path) -> list[str]:
    day_map, year_info = _facts(Path(facts_dir))
    errors = []
    for line_no, raw in enumerate(text.splitlines(), 1):
        s = raw.replace("**", "").strip()
        dates = [(int(a), int(b), m.start()) for m in re.finditer(r"\b(\d{1,2}) tháng (\d{1,2})\b(?! âm)", s) for a,b in [(m.group(1),m.group(2))] if int(b) in (12,1)]
        canchis = list(re.finditer(rf"\b({CAN}) ({CHI})\b", s))
        spirits = list(re.finditer(THAN, s))
        if dates and (canchis or spirits) and len(dates) == 1:
            d, m, _ = dates[0]
            fact = day_map.get((d,m))
            if not fact:
                errors.append(f"{line_no}: ngày ngoài facts {d}/{m}: {s}")
            elif len(canchis) == 1 and canchis[0].group(0) != fact["ngay"]:
                errors.append(f"{line_no}: CAN CHI sai {d}/{m}: ghi {canchis[0].group(0)}, đúng {fact['ngay']}: {s}")
            elif len(spirits) == 1 and spirits[0].group(0) != fact["than"]:
                errors.append(f"{line_no}: THẦN sai {d}/{m}: ghi {spirits[0].group(0)}, đúng {fact['than']}: {s}")
        birth_years = [y for y in re.findall(r"\b(19[5-9]\d|20[01]\d)\b", s) if y in year_info]
        targets = [y for y in (2026, 2027) if str(y) not in s]
        if not birth_years: continue
        for sao in SAO:
            m = re.search(re.escape(sao), s)
            if not m: continue
            for birth_year in birth_years:
                birth, data = year_info[birth_year]
                if not data: continue
                year = 2027 if "sang năm" in s.lower() else 2026
                fact = data.get(year)
                if not fact: continue
                female = "nữ" in s.lower()
                expected = fact["sao_nu" if female else "sao_nam"]
                if sao != expected and len(birth_years) == 1:
                    errors.append(f"{line_no}: SAO {birth_year}: ghi {sao}, đúng {expected}: {s}")
        for m in re.finditer(r"Kim Lâu(?:\s+(Thân|Thê|Tử|Lục Súc))?", s):
            if _negated(s, m.start()): continue
            if len(birth_years) != 1: continue
            birth, data = year_info[birth_years[0]]
            fact = data.get(2027 if "sang năm" in s.lower() else 2026)
            if fact and (not fact.get("kim_lau") or (m.group(1) and m.group(1) not in fact["kim_lau"])):
                errors.append(f"{line_no}: KIM LÂU {birth_years[0]} ghi {m.group(0)}, đúng {fact.get('kim_lau')}: {s}")
        for name in HOANG_OC:
            m = re.search(re.escape(name), s)
            if m and len(birth_years) == 1:
                fact = year_info[birth_years[0]][1].get(2027 if "sang năm" in s.lower() else 2026)
                if fact and fact.get("hoang_oc") != name:
                    errors.append(f"{line_no}: HOANG ỐC {birth_years[0]} ghi {name}, đúng {fact.get('hoang_oc')}: {s}")
        # Nạp âm phải có tiền tố tên nạp âm; "Kim Lâu Thân" tự nó không phải nạp âm.
        nap = re.search(r"\b(Bích Thượng|Thiên Hà|Lư Trung|Đại Hải|Sa Trung|Kiếm Phong|Sơn Đầu|Tích Lịch|Bạch Lạp|Thành Đầu|Ốc Thượng|Dương Liễu|Tuyền Trung|Trường Lưu|Kim Bạch|Phú Đăng|Thoa Xuyến|Tang Đố|Đại Lâm|Lộ Bàng|Bình Địa|Giản Hạ|霹雳)\s+(Thổ|Thủy|Mộc|Hỏa|Kim)\b", s)
        if nap and len(birth_years) == 1 and nap.group(0) != year_info[birth_years[0]][0].get("nap_am"):
            errors.append(f"{line_no}: NẠP ÂM {birth_years[0]} ghi {nap.group(0)}, đúng {year_info[birth_years[0]][0].get('nap_am')}: {s}")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scripts", nargs="+")
    parser.add_argument("--facts", required=True, help="Thư mục chứa *_facts.json")
    args = parser.parse_args(argv)
    failed = False
    for name in args.scripts:
        for error in check_text(Path(name).read_text(encoding="utf-8"), args.facts):
            print(f"{name}:{error}")
            failed = True
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
