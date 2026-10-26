#!/usr/bin/env python3
"""Quét tri thức trong repo thành inventory tất định, chỉ dùng thư viện chuẩn."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "library/inventory/knowledge.json"
SOURCE = "output/cl_staging/grok/rules.md"


def slug(value):
    import unicodedata
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value[:64] or "muc"


def scan(usage_root=None):
    roots = []
    for candidate in (Path(usage_root).expanduser() if usage_root else None, ROOT):
        if candidate and candidate.is_dir() and candidate.resolve() not in [x.resolve() for x in roots]:
            roots.append(candidate)
    rows = {}

    def read(rel):
        for base in roots:
            p = base / rel
            if p.is_file():
                try:
                    return p.read_text(encoding="utf-8", errors="replace").splitlines()
                except OSError:
                    pass
        return []

    def add(rel, line, kind, title, *, description="", so_lieu=None, key=None):
        title = re.sub(r"\s+", " ", title).strip(" #\t-:")
        if not title:
            return
        ident = key or slug(title)
        # A stable source prefix prevents unrelated same-titled sections colliding.
        ident = slug(ident)
        if ident in rows:
            ident = slug(Path(rel).stem + "_" + ident)
        row = {"id": ident, "loai": kind, "ten": title,
               "nguon_su_that": [f"{rel}:{line}"], "mo_ta_nguon": description[:700]}
        if so_lieu:
            row["so_lieu"] = so_lieu
        rows[ident] = row

    def section_excerpt(lines, start):
        out=[]
        for line in lines[start:start+12]:
            if re.match(r"^#{1,6}\s", line) and out:
                break
            if line.strip(): out.append(line.strip())
        return " ".join(out)[:700]

    # Skills and their reference documents: only actionable headings are cards.
    skill_files=[]
    for base in roots:
        d=base/".claude/skills"
        if d.is_dir(): skill_files.extend(d.glob("*/SKILL.md")); skill_files.extend(d.glob("*/references/*.md"))
    seen=set()
    for p in sorted(skill_files, key=lambda x: str(x)):
        rel=p.relative_to(roots[0]).as_posix() if p.is_relative_to(roots[0]) else p.relative_to(roots[-1]).as_posix()
        if rel in seen: continue
        seen.add(rel); lines=read(rel)
        skill=rel.split("/")[2] if len(rel.split("/"))>2 else ""
        for i,line in enumerate(lines):
            m=re.match(r"^(#{1,4})\s+(.+?)\s*#*\s*$",line)
            if not m: continue
            title=m.group(2).strip()
            low=(title+" "+skill+" "+rel).lower()
            if any(w in low for w in ("template","khuôn","format","mẫu","form")): kind="khuon"
            elif any(w in low for w in ("script","kịch bản","story","narrat","format","format")): kind="kich_ban"
            else: kind="quy_trinh"
            if skill in ("long-video","long-script","shorts-studio") and any(x in low for x in ("short","long","video")) and any(x in low for x in ("format","script","khuôn","short","long")): kind="khuon"
            add(rel,i+1,kind,title,description=section_excerpt(lines,i+1),key=f"{Path(rel).parent.name}_{title}")

    # Numbered editorial/operating rules, one rule per card.
    for rel in ("output/cl_staging/grok/rules.md",):
        for i,line in enumerate(read(rel)):
            m=re.match(r"^\s*(\d+)\.\s+(.+)",line)
            if m: add(rel,i+1,"luat",f"Luật {m.group(1)} — {m.group(2)[:95]}",description=line.strip(),key=f"grok_luat_{m.group(1)}")

    # ADRs are individual decisions. Measurement/analytics decisions are tagged do_luong.
    adr_files=[]
    for base in roots:
        d=base/"docs/adr"
        if d.is_dir(): adr_files.extend(d.glob("*.md"))
    seen=set()
    for p in sorted(adr_files):
        rel=p.relative_to(roots[0]).as_posix() if p.is_relative_to(roots[0]) else p.relative_to(roots[-1]).as_posix()
        if rel in seen: continue
        seen.add(rel); lines=read(rel)
        title=next((re.sub(r"^#\s*", "",x).strip() for x in lines if x.startswith("# ")),p.stem)
        text=" ".join(lines[:80]).lower()
        kind="do_luong" if any(w in text for w in ("đo lường","analytics","scoreboard","chỉ số","đo số liệu")) else "luat"
        add(rel,next((i+1 for i,x in enumerate(lines) if x.startswith("# ")),1),kind,title,description=section_excerpt(lines,1),key=p.stem)

    # QA gates, lint entry points, and named guards.
    targets=[]
    for rel in ("hf_qa.py","long_script_lint.py","output/cl_staging/grok/build_r1026.py"):
        lines=read(rel)
        for i,line in enumerate(lines):
            m=re.match(r"\s*(?:def|async def)\s+([A-Za-z_]\w*)\s*\(",line)
            if m and ("gate" in m.group(1).lower() or "lint" in m.group(1).lower() or "guard" in m.group(1).lower() or "check" in m.group(1).lower()):
                targets.append((rel,i+1,m.group(1),line.strip()))
    for rel,line,name,desc in targets:
        add(rel,line,"cong_qa",name.replace("_"," ").capitalize(),description=desc,key=f"qa_{name}")

    # Root helper modules; curated data adapters are distinct from general tools.
    data_names={"hf_sutta","hf_kinhdich","hf_commons","hf_museum","fs_calendar"}
    modules={}
    for base in roots:
        for p in base.glob("hf_*.py"):
            rel=p.relative_to(base).as_posix()
            if rel not in modules: modules[rel]=read(rel)
    for rel,lines in sorted(modules.items()):
        stem=Path(rel).stem
        if stem in data_names: kind="du_lieu_nguon"
        else: kind="cong_cu"
        doc=""
        for line in lines[:8]:
            if line.strip() and not line.lstrip().startswith(('"""','\'\'\'')):
                doc=line.strip().strip('"\''); break
            if line.lstrip().startswith(('"""','\'\'\'')):
                doc=line.strip().strip('"\''); break
        add(rel,1,kind,stem.replace("_"," "),description=doc,key=stem)
    for rel in ("output/cl_staging/long/canchi.py","output/cl_staging/long/amlich.py"):
        lines=read(rel)
        if lines: add(rel,1,"du_lieu_nguon",Path(rel).stem+" — dữ liệu lịch",description=next((x.strip().strip('"\'') for x in lines[:8] if x.strip()),""),key=Path(rel).stem)

    # Measurement and experiment instruments.
    for rel in ("hf_brief.py","hf_coverage.py","hf_slots.py"):
        lines=read(rel)
        if lines: add(rel,1,"do_luong",Path(rel).stem.replace("_"," "),description=next((x.strip().strip('"\'') for x in lines[:8] if x.strip()),""),key=Path(rel).stem)
    seen_measure=set()
    for base in roots:
        board=base/"output/cl_staging/scoreboard"
        candidates=(list(board.rglob("*.py"))+list(board.rglob("*.md")) if board.is_dir() else [])
        candidates += list((base/"tests").glob("*scoreboard*.py")) if (base/"tests").is_dir() else []
        candidates += list((base/"experiments").glob("*.py"))+list((base/"experiments").glob("*.md")) if (base/"experiments").is_dir() else []
        for p in candidates:
            if not p.is_file() or p.suffix not in (".py",".md") or any(x in p.parts for x in (".git","node_modules","__pycache__")): continue
            rel=p.relative_to(base).as_posix(); lines=read(rel)
            if rel in seen_measure: continue
            seen_measure.add(rel)
            if lines: add(rel,1,"do_luong",p.stem.replace("_"," "),description=next((x.strip() for x in lines if x.strip()),""),key="measure_"+p.stem)

    # Defects are aggregated by production stage/topic, never emitted row-by-row.
    for rel in ("output/cl_staging/grok/improve/defects.jsonl",):
        groups={}
        for i,line in enumerate(read(rel),1):
            try: d=json.loads(line)
            except json.JSONDecodeError: continue
            topic=(d.get("khau") or "khac").strip().lower()
            groups.setdefault(topic,[]).append((i,d))
        for topic,items in sorted(groups.items()):
            dates=[str(d.get("ngay","")) for _,d in items if d.get("ngay")]
            latest=max(dates,default="")
            samples="; ".join(dict.fromkeys(str(d.get("loi","")).strip() for _,d in items if d.get("loi")))[:600]
            add(rel,items[0][0],"bai_hoc",f"Bài học khâu {topic}",description=samples,
                so_lieu={"so_lan":len(items),"ngay_gan_nhat":latest},key=f"bai_hoc_{topic}")
    retro_files=[]
    for base in roots:
        d=base/"output/cl_staging/retro"
        if d.is_dir(): retro_files.extend(d.glob("*.md"))
    # Retro docs contribute evidence/counts to stage themes, avoiding duplicate cards.
    seen_retro=set()
    for p in sorted(retro_files):
        rel=p.relative_to(roots[0]).as_posix() if p.is_relative_to(roots[0]) else p.relative_to(roots[-1]).as_posix()
        if rel in seen_retro: continue
        seen_retro.add(rel)
        lines=read(rel)
        for topic,row in list(rows.items()):
            if row["loai"]!="bai_hoc": continue
            if any(w in " ".join(lines).lower() for w in topic.split("_")):
                row.setdefault("nguon_su_that",[]).append(f"{rel}:1")
                row.setdefault("so_lieu",{}).setdefault("so_retro",0); row["so_lieu"]["so_retro"]+=1

    # Studio device cards (do not overwrite a device knowledge card if already found).
    for base in roots:
        for p in sorted((base/"hyperframes_short/studio/devices").glob("*.js")) if (base/"hyperframes_short/studio/devices").is_dir() else []:
            rel=p.relative_to(base).as_posix(); lines=read(rel); ident=slug(p.stem)
            if ident not in rows: add(rel,1,"thiet_bi",p.stem.replace("_"," "),description=next((x.strip() for x in lines if x.strip() and not x.strip().startswith("//")),""),key=ident)

    # External prompt/style references.
    refs=[]
    for base in roots:
        d=base/".claude/skills/motion-library/references/prompt_motion"
        if d.is_dir(): refs.extend(d.glob("*"))
        for p in base.rglob("opus55_styles.md"): refs.append(p)
    seen_ref=set()
    for p in sorted(set(refs),key=str):
        if not p.is_file(): continue
        base=next((b for b in roots if p.is_relative_to(b)),roots[0]); rel=p.relative_to(base).as_posix(); lines=read(rel)
        if rel in seen_ref: continue
        seen_ref.add(rel)
        title=next((re.sub(r"^#\s*", "",x).strip() for x in lines if x.startswith("# ")),p.stem.replace("_"," "))
        add(rel,next((i+1 for i,x in enumerate(lines) if x.startswith("# ")),1),"tham_khao",title,description=section_excerpt(lines,1),key="ref_"+p.stem)

    return {"version":1,"items":[rows[k] for k in sorted(rows)]}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--usage-root")
    args=ap.parse_args(); payload=scan(args.usage_root)
    DATA.parent.mkdir(parents=True,exist_ok=True)
    DATA.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"knowledge: {len(payload['items'])} mục → {DATA.relative_to(ROOT)}")


if __name__=="__main__": main()
