#!/usr/bin/env python3
"""Kiểm tra lời hứa của tiêu đề / câu hỏi thumbnail trong kịch bản Long.

Với mỗi tiêu đề hoặc câu hỏi trên thumbnail, tìm đoạn trả lời trong script[] của plan:
- Đoạn khớp (matching passage / sentences)
- Số câu trả lời
- Chương chứa đoạn trả lời
Báo CẢNH BÁO khi phần trả lời quá mỏng (< 3 câu).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VIETNAMESE_STOPWORDS = {
    "và", "hoặc", "của", "ở", "trong", "là", "với", "có", "thể", "cho",
    "thì", "mà", "bạn", "này", "đó", "những", "các", "được", "ra", "vào",
    "lại", "đến", "sẽ", "đã", "gì", "sao", "ai", "thế", "nào", "đang",
    "từ", "làm", "một", "hai", "ba", "bốn", "năm", "sau", "trước", "khi",
    "như", "vậy", "cũng", "để", "thật", "vì", "về", "ta", "tôi", "mình",
    "phải", "hay", "hãy", "chỉ", "cả", "quá", "rất", "cùng", "không"
}

SYNONYMS: dict[str, list[str]] = {
    "người nhà": [
        "người thân",
        "vợ chồng",
        "anh em",
        "bố mẹ",
        "con cái",
        "người trong nhà",
        "trong một nhà",
        "trong nhà",
    ],
    "khắc": ["khắc nhau", "khác mệnh", "xung khắc", "hành khắc"],
}


def resolve_plan_path(path: Path | str) -> Path:
    """Tìm đường dẫn plan thực tế (hỗ trợ khi chạy từ thư mục gốc hoặc worktree)."""
    p = Path(path)
    if p.exists():
        return p
    cur = Path.cwd()
    for parent in [cur, *cur.parents]:
        cand = parent / path
        if cand.exists():
            return cand
    return p


def is_heading(line: str) -> bool:
    """Kiểm tra dòng có phải tiêu đề chương (in đậm trọn câu)."""
    s = line.strip()
    return s.startswith("**") and s.endswith("**") and s.count("**") == 2


def plain(text: str) -> str:
    """Bỏ định dạng markdown bold."""
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", text).strip()


def split_sentences(text: str) -> list[str]:
    """Tách câu theo dấu chấm, hỏi, than; làm sạch markdown."""
    clean = plain(text)
    raw = [re.sub(r"\s+", " ", x).strip() for x in re.findall(r"[^.!?]+[.!?]?", clean) if x.strip()]
    return [r for r in raw if len(r) > 3]


def parse_chapters(script: list[str]) -> list[dict[str, Any]]:
    """Phân tách kịch bản thành danh sách các chương có tiêu đề và câu đọc."""
    heads = [i for i, x in enumerate(script) if is_heading(x)]
    chapters: list[dict[str, Any]] = []

    # Chương mở đầu / cold open nếu có dòng trước heading đầu
    if not heads or heads[0] > 0:
        end = heads[0] if heads else len(script)
        sents: list[str] = []
        for l in script[:end]:
            sents.extend(split_sentences(l))
        chapters.append({
            "index": 0,
            "title": "Mở đầu / Cold open",
            "sentences": sents,
            "lines": script[:end],
            "line_span": (1, end),
        })

    for k, idx in enumerate(heads):
        next_idx = heads[k + 1] if k + 1 < len(heads) else len(script)
        raw_title = plain(script[idx])
        m = re.match(r"^\s*Chương\s+(\d+)\s*[:.-]\s*", raw_title, re.IGNORECASE)
        if m:
            chap_num = int(m.group(1))
            title = raw_title[m.end():].strip()
        else:
            m2 = re.search(r"\bChương\s+(\d+)\b", raw_title, re.IGNORECASE)
            chap_num = int(m2.group(1)) if m2 else (k + 1)
            title = raw_title

        sents = []
        for l in script[idx + 1:next_idx]:
            sents.extend(split_sentences(l))
        chapters.append({
            "index": chap_num,
            "title": title,
            "sentences": sents,
            "lines": script[idx:next_idx],
            "line_span": (idx + 1, next_idx),
        })

    return chapters


def extract_keywords(query: str) -> list[str]:
    """Tách từ khoá quan trọng từ câu hỏi/tiêu đề và chuẩn hoá đồng nghĩa."""
    text_lower = query.lower()
    syn_pairs = []
    for canon, aliases in SYNONYMS.items():
        canon_norm = canon.replace(" ", "_")
        for phrase in [canon, *aliases]:
            syn_pairs.append((phrase, canon_norm))
    syn_pairs.sort(key=lambda x: len(x[0]), reverse=True)

    for phrase, canon_norm in syn_pairs:
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        text_lower = re.sub(pattern, f" {canon_norm} ", text_lower)

    clean = re.sub(r"[^\w\s]", " ", text_lower)
    tokens: list[str] = []
    for w in clean.split():
        if not w:
            continue
        if "_" in w:
            tokens.append(w)
        elif w not in VIETNAMESE_STOPWORDS:
            tokens.append(w)
    return tokens


def find_promise_answer(query: str, script: list[str]) -> dict[str, Any]:
    """Tìm đoạn trả lời cho query trong script[].

    Trả về:
    - query: câu hỏi gốc
    - chapter_num: số chương
    - chapter_title: tên chương
    - sentences: danh sách câu trả lời khớp
    - count: số câu trả lời
    - status: PASS / WARN
    - verdict: ĐẠT / CẢNH BÁO
    """
    chapters = parse_chapters(script)
    q_tokens = extract_keywords(query)
    q_concepts = {
        canon.replace(" ", "_")
        for canon in SYNONYMS
        if canon.replace(" ", "_") in q_tokens
    }
    min_overlap = 1 if len(q_tokens) <= 2 else 2

    # Nếu tiêu đề chương trực tiếp trả lời câu hỏi (vd: "Vì sao hoàng tử giả câm?")
    for chap in chapters:
        title_tokens = extract_keywords(chap["title"])
        overlap_tokens = set(q_tokens) & set(title_tokens)
        title_overlap_ratio = len(overlap_tokens) / max(1, len(title_tokens))
        if len(overlap_tokens) >= 2 and title_overlap_ratio >= 0.5:
            cnt = len(chap["sentences"])
            status = "PASS" if cnt >= 3 else "WARN"
            verdict = (
                f"ĐẠT ({cnt} câu trả lời)"
                if status == "PASS"
                else f"CẢNH BÁO: phần trả lời quá mỏng ({cnt} câu < 3 câu)"
            )
            return {
                "query": query,
                "chapter_num": chap["index"],
                "chapter_title": chap["title"],
                "sentences": chap["sentences"],
                "count": cnt,
                "status": status,
                "verdict": verdict,
            }

    best_chap = None
    best_score = -1.0
    matched_passage: list[str] = []

    for chap in chapters:
        title_tokens = extract_keywords(chap["title"])
        overlap_title = set(q_tokens) & set(title_tokens)
        c_title_overlap = q_concepts & set(title_tokens)
        score = len(overlap_title) * 3.0 + len(c_title_overlap) * 5.0

        seed_indices = []
        for i, sent in enumerate(chap["sentences"]):
            s_tokens = extract_keywords(sent)
            overlap = set(q_tokens) & set(s_tokens)
            c_overlap = q_concepts & set(s_tokens)

            is_match = False
            if q_concepts:
                if c_overlap and len(overlap) >= min_overlap:
                    is_match = True
                    score += 5.0 + len(c_overlap) * 3.0
            else:
                if len(overlap) >= min_overlap:
                    is_match = True
                    score += 5.0 + len(overlap)

            if is_match:
                seed_indices.append(i)

        if seed_indices and score > best_score:
            best_score = score
            best_chap = chap
            matched_passage = [chap["sentences"][i] for i in seed_indices]

    if not best_chap or best_score <= 0 or not matched_passage:
        return {
            "query": query,
            "chapter_num": 0,
            "chapter_title": "Không tìm thấy",
            "sentences": [],
            "count": 0,
            "status": "WARN",
            "verdict": "CẢNH BÁO: không tìm thấy câu trả lời nào trong kịch bản",
        }

    count = len(matched_passage)
    status = "PASS" if count >= 3 else "WARN"
    verdict = (
        f"ĐẠT ({count} câu trả lời)"
        if status == "PASS"
        else f"CẢNH BÁO: phần trả lời quá mỏng ({count} câu < 3 câu)"
    )

    return {
        "query": query,
        "chapter_num": best_chap["index"],
        "chapter_title": best_chap["title"],
        "sentences": matched_passage,
        "count": count,
        "status": status,
        "verdict": verdict,
    }


def load_plan_rows(plan_path: Path | str, only: Optional[str] = None) -> list[dict[str, Any]]:
    """Tải một hoặc nhiều row từ file plan JSON."""
    resolved_path = resolve_plan_path(plan_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file plan: {plan_path} (đã thử resolve: {resolved_path})")

    data = json.load(resolved_path.open(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        if "script" in data:
            rows = [data]
        else:
            for k, v in data.items():
                if isinstance(v, dict):
                    if "id" not in v and "key" not in v:
                        v["id"] = k
                    rows.append(v)

    if only:
        rows = [r for r in rows if r.get("id") == only or r.get("key") == only]
    return rows


def check_plan(
    plan_path: Path | str,
    only: Optional[str] = None,
    question: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Kiểm tra lời hứa cho plan file."""
    rows = load_plan_rows(plan_path, only=only)
    if not rows:
        raise ValueError(f"Không tìm thấy row nào trong {plan_path} (bộ lọc: only={only})")

    results: list[dict[str, Any]] = []

    for row in rows:
        row_id = row.get("id") or row.get("key") or "unknown"
        script = row.get("script", [])
        if not script:
            results.append({
                "row_id": row_id,
                "query": question or "(không có script)",
                "chapter_num": 0,
                "chapter_title": "",
                "sentences": [],
                "count": 0,
                "status": "WARN",
                "verdict": "CẢNH BÁO: kịch bản trống",
            })
            continue

        queries_to_check: list[str] = []
        if question:
            queries_to_check.append(question)
        else:
            title = row.get("title", "")
            if title:
                queries_to_check.append(title)

            cand_q = row.get("candidate_questions") or row.get("questions") or []
            if isinstance(cand_q, list):
                for q_item in cand_q:
                    if isinstance(q_item, str):
                        queries_to_check.append(q_item)
                    elif isinstance(q_item, dict):
                        q_text = q_item.get("text") or q_item.get("question") or q_item.get("q")
                        if q_text and isinstance(q_text, str):
                            queries_to_check.append(q_text)

        for q in queries_to_check:
            res = find_promise_answer(q, script)
            res["row_id"] = row_id
            results.append(res)

    return results


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Kiểm tra độ dày lời hứa của tiêu đề / thumbnail trong kịch bản Long."
    )
    parser.add_argument("plan", help="Đường dẫn tới file plan JSON")
    parser.add_argument("question", nargs="?", default=None, help="Câu hỏi hoặc lời hứa cần kiểm")
    parser.add_argument("--only", help="Chỉ kiểm video ID / key cụ thể")
    parser.add_argument("--question", dest="opt_question", help="Câu hỏi hoặc lời hứa cần kiểm")
    parser.add_argument("--strict", action="store_true", help="Báo lỗi exit 1 nếu có CẢNH BÁO")

    args = parser.parse_args(argv)
    q = args.question or args.opt_question

    results = check_plan(args.plan, only=args.only, question=q)

    has_warn = False
    print(f"\n=== PROMISE CHECK: {args.plan} (only={args.only}) ===")
    for r in results:
        status_tag = "[ĐẠT]" if r["status"] == "PASS" else "[CẢNH BÁO]"
        if r["status"] == "WARN":
            has_warn = True
        print(f"\n{status_tag} Video: {r.get('row_id')}")
        print(f"  Câu hỏi / Lời hứa: \"{r['query']}\"")
        print(f"  Chương chứa: Chương {r['chapter_num']}: {r['chapter_title']}")
        print(f"  Số câu trả lời: {r['count']} câu")
        print(f"  Kết luận: {r['verdict']}")
        if r["sentences"]:
            print("  Trích dẫn câu trả lời:")
            for s in r["sentences"][:3]:
                print(f"    • {s}")
            if len(r["sentences"]) > 3:
                print(f"    ... (và {len(r['sentences']) - 3} câu khác)")

    print()
    if has_warn and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
