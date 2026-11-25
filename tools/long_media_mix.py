"""Offline, conservative stock lane for new FS/BUD Long plans.

AI stills with a documented, character-free scene may be replaced. Targets
are soft: protected scenes are never sacrificed to fill a stock quota.
Only query construction happens here; resolution and safety stay in the bridge.
"""
from __future__ import annotations

import copy
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
import math
import re
from pathlib import Path

# Mốc 40 giây đầu tính trên timing ƯỚC lúc enrich -> chừa biên an toàn (review 537).
OPENING_GUARD_S = 50.0
DEFAULTS = {"enabled": True, "stock_video_share": .15, "stock_image_share": .15, "concept_broll": True}
# Literal subjects, not translations of abstract fortunes or religious teaching.
SUBJECTS = (
    (("hoa sen", "đầm sen"), "lotus pond", "nature"),
    (("ngọn đèn", "đèn bàn", "ánh đèn"), "desk lamp light", "object"),
    (("đồng hồ",), "clock close up", "object"),
    (("trang giấy", "tờ giấy", "sổ tay", "cuốn sổ"), "paper notebook desk", "object"),
    (("bàn thờ", "đồ thờ"), "buddhist altar incense", "altar"),
    (("nén hương", "nén nhang", "khói hương"), "buddhist incense smoke", "altar"),
    (("sân chùa", "ngôi chùa", "mái chùa", "cổng chùa"), "vietnam buddhist temple exterior", "temple"),
    (("bình minh",), "sunrise landscape", "nature"),
    (("hoàng hôn",), "sunset landscape", "nature"),
    (("dòng sông", "bờ sông", "con sông"), "vietnam river landscape", "nature"),
    (("ngọn núi", "núi rừng", "dãy núi"), "vietnam mountain forest", "nature"),
    (("khu rừng", "cánh rừng", "rừng cây"), "tropical forest trees", "nature"),
    (("mặt biển", "bờ biển", "sóng biển"), "vietnam ocean waves", "nature"),
    (("giọt mưa", "cơn mưa", "mưa rơi"), "rain drops leaves", "nature"),
    (("vườn cây", "mầm cây", "lá cây", "cây xanh"), "green garden leaves", "nature"),
    (("mặt trăng", "ánh trăng", "trăng tròn"), "moon night sky", "nature"),
    (("khu chợ", "phiên chợ", "chợ quê"), "vietnam asian street market", "people"),
    (("đường phố", "phố xá", "con phố"), "vietnam asian street", "people"),
    (("ngôi nhà", "mái nhà", "căn nhà"), "vietnam traditional house exterior", "place"),
    (("bàn làm việc", "bàn thợ", "bàn gỗ", "workbench"), "old wooden workbench lamp", "object"),
    (("đèn dầu", "đèn lồng", "đèn bàn", "desk lamp", "lamp"), "old wooden workbench lamp", "object"),
    (("lư hương", "bát hương", "incense smoke", "khói nhang"), "incense smoke altar", "altar"),
    (("sạp hàng", "quầy hàng", "market stall", "chợ"), "vietnam asian street market", "people"),
)
CHARACTERS = re.compile(
    r"\b(?:ông|bà|anh|chị|cô|cậu|chú|bác|vua|hoàng hậu|thái tử|đức phật|"
    r"bồ tát|nhà sư|tỳ kheo|tỳ kheo ni|đệ tử|người thợ|nhân vật)\b", re.I)
OTHER_RELIGION = re.compile(r"\b(?:hindu|jesus|christ|church|cross|shiva|vishnu|nhà thờ|thánh giá)\b", re.I)
PEOPLE = re.compile(r"\b(?:người|gia đình|đôi tay|bàn tay|khách|dân|trẻ|phụ nữ|đàn ông)\b", re.I)


def query_for(text, channel):
    channel = str(channel).lower()
    raw = str(text).replace("**", "").lower()
    if channel not in {"fs", "bud"} or CHARACTERS.search(raw) or OTHER_RELIGION.search(raw):
        return None
    # Named subjects in custom plans can also be explicitly excluded by caller.
    for keys, query, category in SUBJECTS:
        if any(re.search(rf"\b{re.escape(k)}\b", raw) for k in keys):
            if channel == "bud":
                if category not in {"nature", "temple", "altar"} or PEOPLE.search(raw):
                    return None
                query += " no people"
            elif PEOPLE.search(raw) or category == "people":
                if "vietnam" not in query:
                    query = "vietnam asian " + query
            from hyperframes_bridge import sanitize_query
            query = sanitize_query(query, channel.upper())
            return query if query and not OTHER_RELIGION.search(query) else None
    return None


# Strip only known continuity templates. Unknown prose is scanned in full.
_CAST_START = re.compile(r"(?:The same Vietnamese|[A-Z][a-z]+ is the same Vietnamese)\b")
_PREFIX_END = "Lower fifth quiet for subtitles."
# Lead 25/11 (vòng 2): câu GIẢI THÍCH khái niệm không nhắc nhân vật thì B-roll stock hợp
# nghĩa thay được cả ảnh AI có người (ảnh nhân vật ở các câu này chỉ để lấp chỗ). Mục tiêu PO:
# ~15% video + ~15% ảnh Pexels để giảm tải ảnh AI. Thứ tự: khái niệm cụ thể trước.
CONCEPT_BROLL = {
    "fs": (
        (r"nạp âm|ngũ hành|thủy sinh|khắc thủy|thiên hà thủy", "flowing river water close up"),
        (r"\bsao\b|cửu diệu|la hầu|kế đô|thái bạch|thái dương|thái âm|mộc đức|vân hớn|thổ tú|thủy diệu", "night sky stars timelapse"),
        (r"thái tuế|xung|hình|phá|hại|trực", "incense smoke temple vietnam"),
        (r"tam tai", "hourglass sand"),
        (r"kim lâu|hoang ốc|làm nhà|dựng nhà|xây nhà|động thổ", "house construction vietnam"),
        (r"tết|giao thừa|năm âm|lịch âm|mùng một|năm mới", "lunar new year vietnam street"),
        (r"tuổi mụ|năm sinh|ngày sinh", "old wooden house window asia"),
        (r"\bhạn\b|vận hạn|tháng", "red lanterns night"),
    ),
    "bud": (
        (r"vô thường|sinh diệt|hơi thở", "lotus pond nature no people"),
        (r"chùa|tu viện|thiền", "vietnam buddhist temple exterior no people"),
        (r"khói hương|nén hương|cúng dường", "buddhist incense smoke no people"),
        (r"rừng|núi|sông|biển|trăng|mây", "misty mountain forest no people"),
    ),
}


# Lead 25/11: một Long không được lặp một truy vấn stock quá N lần (16/33 cảnh 1965 cùng "blank paper").
ALTERNATES = {
    # Chủ đề KHÔNG CHỮ (giấy/sổ/lịch hay dính chữ tiếng Anh — tờ 1965, 25/11).
    "blank paper sheets desk": ("tea cup steam wooden table", "incense coil smoke", "candle flame dark",
                                "bamboo leaves wind", "rain on window night", "old wooden door asia"),
    "night sky stars timelapse": ("milky way night sky", "starry sky over mountains", "moon behind clouds night",
                                  "aurora night sky"),
    "lunar calendar close up": ("red lanterns night", "peach blossom branch", "kumquat tree pot"),
    "incense smoke temple vietnam": ("vietnam pagoda roof", "temple bell close up", "candle light altar",
                                     "incense coil smoke"),
    "flowing river water close up": ("waterfall slow motion", "rain on water surface", "mountain stream rocks"),
    "desk lamp warm light": ("warm lamp evening room", "oil lamp flame close up", "lantern light night"),
    "house construction vietnam": ("brick wall construction", "roof tiles close up", "wooden house frame"),
    "old calendar pages turning": ("clock hands moving", "hourglass sand", "sunrise timelapse"),
    "lunar new year vietnam street": ("peach blossom tet vietnam", "kumquat tree tet", "red lanterns street"),
    "old family photo album": ("old wooden house window asia", "family dinner table food asia"),
}


def diversify_queries(candidates, cap=3):
    """Giữ thứ tự; truy vấn thứ cap+1 trở đi xoay sang truy vấn thay thế cùng nghĩa, hết thì bỏ cảnh."""
    seen = Counter()
    out = []
    for line, cut, query, ref in candidates:
        q = query
        if seen[q] >= cap:
            q = next((alt for alt in ALTERNATES.get(query, ()) if seen[alt] < cap), None)
            if q is None:
                continue
        seen[q] += 1
        out.append((line, cut, q, ref))
    return out


def concept_query(text, channel):
    raw = str(text).replace("**", "").lower()
    if OTHER_RELIGION.search(raw):
        return None
    for pattern, query in CONCEPT_BROLL.get(str(channel).lower(), ()):
        if re.search(pattern, raw):
            from hyperframes_bridge import sanitize_query
            q = sanitize_query(query, str(channel).upper())
            return q if q and not OTHER_RELIGION.search(q) else None
    return None


_PERSON = re.compile(
    r"\b(?:person|people|man|woman|men|women|faces?|hands?|family|child|children|"
    r"portrait|apprentice|worker|repairer|monk|husband|wife|sister|brother|recipient|"
    r"supervisor|member|fingers?|sleeves?|shoulders?|seated|sitting|standing|"
    r"customers?|adults?|boys?|girls?|silhouettes?|crowds?|crowded|families|someone|"
    r"her|his|he|she|holding|held|reaching|stands|sits|walks|two-person|three-person|two-shot)s?\b", re.I)
_AI = re.compile(r"ai_\d+\.png", re.I)
# A small noun lexicon: actual scene objects/places, never abstract fortunes.
_EN_SUBJECTS = (
    (r"desk lamp|oil lamp|lamp", "desk lamp warm light", "object"),
    (r"watch (?:dial|gear|movement)|opened watch|mechanical movement|tiny gears", "watch mechanism close up", "object"),
    (r"magnif(?:ier|ying glass)", "magnifying glass workbench", "object"),
    (r"compartment (?:box|parts)|parts (?:box|tray)", "small parts storage box workbench", "object"),
    (r"(?:reference |ruled |blank |paper |date )*(?:sheets?|papers?|cards?)", "blank paper sheets desk", "object"),
    (r"notebooks?|booklets?|reference book", "blank notebook wooden desk", "object"),
    (r"(?:design |reference |closed |open )?folder", "paper folder wooden table", "object"),
    (r"(?:ballpoint )?pen|pencil|ruler", "pen notebook desk", "object"),
    (r"(?:tea ?cups?|teapot|coaster)", "ceramic tea cup wooden table", "object"),
    (r"smartphone|phone|screen", "blank smartphone screen desk", "object"),
    (r"(?:swivel |plastic |empty )?chairs?", "empty office chair", "object"),
    (r"workbench|wooden bench", "old wooden workbench lamp", "object"),
    (r"steel desk|wooden (?:desk|table)", "desk still life daylight", "object"),
    (r"woven|sedge|yarn|craft sample", "woven craft material close up", "object"),
    (r"storeroom|storage shelves|steel shelves|parcels", "vietnam storeroom shelves", "place"),
    (r"workshop|lathe", "vietnam workshop machinery", "place"),
    (r"street market|market stall|market", "vietnam street market", "place"),
    (r"street|house|living room|neighborhood|activity room|office doorway", "vietnam traditional house interior", "place"),
    (r"incense|altar", "incense smoke altar", "altar"),
    (r"temple|pagoda", "vietnam buddhist temple exterior", "temple"),
    (r"river|mountain|forest|ocean|sunrise|sunset|lotus|garden", None, "nature"),
)


def _fold(text):
    return "".join(c for c in unicodedata.normalize("NFD", str(text).lower())
                   if unicodedata.category(c) != "Mn").replace("đ", "d")


def _scene(prompt):
    raw = str(prompt or "").strip()
    # 1977: cast and room continuity precede the unique scene, then style.
    if raw.startswith("The same Vietnamese"):
        if _PREFIX_END not in raw:
            return raw  # Unrecognized template: fail closed on its cast.
        raw = raw.split(_PREFIX_END, 1)[1].strip()
        return re.split(r"\bPhotorealistic\b", raw, maxsplit=1)[0].strip()
    cast = _CAST_START.search(raw)
    return raw[:cast.start()].strip() if cast else raw


def _cast_names(descriptions):
    names = set()
    for desc in descriptions.values():
        for match in re.finditer(r"(?:The same Vietnamese|([A-Z][a-z]+) is the same Vietnamese)([^.;]*)", desc):
            if match.group(1):
                names.add(_fold(match.group(1)))
            # Cast names immediately precede the age clause (Bao, Huong, ...).
            head = match.group(2).split(",", 1)[0]
            names.update(_fold(n) for n in re.findall(r"\b[A-Z][a-z]+\b", head))
    return names


def prompt_query(prompt, channel, character_names=()):
    """Scan the whole unique shot, including background people; ignore known boilerplate."""
    channel = str(channel).lower()
    scene = _scene(prompt)
    if not scene or channel not in {"fs", "bud"}:
        return None
    # Explicit negative constraints describe absence; keep all positive mentions.
    visible = re.sub(r"\b(?:no|without) (?:extra )?(?:people|persons?|characters?|hands?|faces?)\b", "", scene, flags=re.I)
    if (_PERSON.search(visible) or CHARACTERS.search(visible) or PEOPLE.search(visible)
            or OTHER_RELIGION.search(scene)):
        return None
    names = {_fold(n) for n in character_names} | _cast_names({"prompt": str(prompt)})
    if any(re.search(rf"\b{re.escape(n)}\b", _fold(scene)) for n in names if n):
        return None
    # Select the earliest concrete noun: props in later clauses cannot override it.
    hits = [(m.start(), order, query, category, m.group())
            for order, (pattern, query, category) in enumerate(_EN_SUBJECTS)
            if (m := re.search(rf"\b(?:{pattern})\b", scene, re.I))]
    if not hits:
        return query_for(scene, channel)
    _, _, query, category, noun = min(hits)
    if channel == "bud" and category not in {"nature", "temple", "altar"}:
        return None
    query = query or f"{noun.lower()} landscape"
    if re.search(r"\b(?:street|market|house|home|living room|shop|storeroom|office|workshop)\b", scene, re.I) and "vietnam" not in query:
        query = "vietnam " + query
    if channel == "bud":
        query += " no people"
    from hyperframes_bridge import sanitize_query
    query = sanitize_query(query, channel.upper())
    return query if query and not OTHER_RELIGION.search(query) else None


def _data_root(project_root=None):
    if project_root is not None:
        return Path(project_root)
    repo = Path(__file__).resolve().parents[1]
    # Linked worktrees use the existing, ignored media in the main checkout.
    return next((p for p in (repo, *repo.parents)
                 if (p / "output/cl_staging/grokbot").is_dir()), repo)


def _context_dirs(plan, project_root=None):
    root = _data_root(project_root)
    jobs = {str(plan.get("id") or "").removeprefix("L_")}
    for spec in (plan.get("media") or {}).values():
        for shot in [spec, *spec.get("cuts", [])]:
            path = Path(str(shot.get("path", "")))
            if _AI.fullmatch(path.name) or path.suffix.lower() == ".mp4":
                jobs.add(path.parent.name)
    prompts, research = [], []
    for job in sorted(jobs):
        folder = root / "output/cl_staging/grokbot" / job
        if folder.is_dir():
            prompts.append(folder)
        match = re.fullmatch(r"fs_d25_(\d{4})", job)
        if match:
            research.append(root / "output/cl_staging/long/research/d25" / match.group(1))
    return prompts, research


def prompt_descriptions(plan, project_root=None):
    """Read both Prompt (EN) sections and the longest prose paragraph (1977)."""
    folders, research = _context_dirs(plan, project_root)
    out = {}
    for folder in folders:
        path = folder / "prompt.md"
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for match in re.finditer(r"(?ms)^##\s+(ai_\d+\.png)\b[^\n]*\n(.*?)(?=^##\s|\Z)", content):
            body = match.group(2)
            explicit = re.search(r"(?ms)^- Prompt \(EN\):\s*(.*?)(?=\n\s*- [^\n]+:|\Z)", body)
            paragraphs = [x.strip() for x in re.split(r"\n\s*\n", body) if x.strip()]
            out[match.group(1)] = explicit.group(1).strip() if explicit else max(paragraphs, key=len, default="")
    # Some map revisions carry shot descriptions directly; current maps carry paths only.
    for folder in research:
        path = folder / "150_media_map.json"
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            for spec in data.get("mapped_media", []):
                for shot in [spec, *spec.get("cuts", [])]:
                    name = Path(str(shot.get("path", ""))).name
                    desc = shot.get("prompt") or shot.get("description")
                    if _AI.fullmatch(name) and desc:
                        out.setdefault(name, str(desc))
    return out


def flow_first_frames(plan, project_root=None):
    """Protect source stills even if they are also used later as normal media."""
    prompts, research = _context_dirs(plan, project_root)
    frames = set()
    def collect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"first_frame", "first_frame_path", "start_image", "input_image"} and isinstance(item, str):
                    frames.add(Path(item).name)
                else:
                    collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)
    collect(plan.get("clips") or {})
    collect(plan.get("media") or {})
    for spec in (plan.get("media") or {}).values():
        for shot in [spec, *spec.get("cuts", [])]:
            if shot.get("flow_first_frame") is True or shot.get("first_frame") is True:
                frames.add(Path(str(shot.get("path", ""))).name)
    for folder in research:
        for path in sorted(folder.glob("*clips_manifest.json")):
            collect(json.loads(path.read_text(encoding="utf-8")))
    for folder in prompts:
        path = folder / "clips.md"
        if path.is_file():
            frames.update(re.findall(r"Khung đầu[^\n]*?`(ai_\d+\.png)`", path.read_text(encoding="utf-8")))
    return frames


def _ai_refs(value):
    """Actual remaining references, excluding audit/rollback data."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key not in {"replaced_ai", "replaced_media", "media_mix_report"}:
                yield from _ai_refs(item)
    elif isinstance(value, list):
        for item in value:
            yield from _ai_refs(item)
    elif isinstance(value, str) and _AI.fullmatch(Path(value).name):
        yield str(Path(value))


def _get_shot(media, line, cut):
    head = media.get(str(line), {})
    return head if cut is None else head["cuts"][cut]


def _set_shot(media, line, cut, spec):
    if cut is None:
        media[str(line)] = spec
    else:
        media[str(line)]["cuts"][cut] = spec


def _stock_spec(original, kind, query):
    out = {"kind": kind, "provider": "pexels", "query": query,
           "mix_auto": True, "layout": "full", "hold": bool(original.get("hold", False))}  # review 537: không tràn sang câu sau
    # Cut timing and later shots must survive replacement of the first shot.
    for key in ("at", "cuts"):
        if key in original:
            out[key] = copy.deepcopy(original[key])
    if original.get("kind") == "local":
        out.update(replaced_ai=Path(original["path"]).name,
                   replaced_media=copy.deepcopy({k: v for k, v in original.items() if k != "cuts"}))
    return out


def _scenes(row, spans):
    from hf_batch_render import visual_mix_scenes
    return visual_mix_scenes(row, [{"start": a, "end": b} for a, b in spans])


def enrich_stock(row, channel, spans, scene_descriptions=None, *, project_root=None, first_frames=()):
    """Offline stock selection; never fetch, render, or change protected shots."""
    if "media_mix" not in row:
        return  # opt-in theo plan (review 537): plan cũ không khai báo giữ nguyên
    config = row.get("media_mix", {})
    if config is False:
        return
    if not isinstance(config, dict):
        raise ValueError("media_mix phải là object hoặc false")
    config = {**DEFAULTS, **config}
    if not config["enabled"] or str(channel).lower() not in {"fs", "bud"}:
        return
    targets = {}
    for kind in ("video", "image"):
        value = float(config[f"stock_{kind}_share"])
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"media_mix.stock_{kind}_share phải trong [0,1]")
        targets[kind] = value
    if sum(targets.values()) > 1:
        raise ValueError("media_mix tổng mục tiêu phải ≤ 1")
    media = row.setdefault("media", {})
    before_refs = set(_ai_refs(row))
    descriptions = prompt_descriptions(row, project_root) if scene_descriptions is None else scene_descriptions
    names = set(config.get("character_names", [])) | _cast_names(descriptions)
    script = row.get("script") or []
    names.update(re.findall(r"\b(?:[Ôô]ng|[Bb]à|[Aa]nh|[Cc]hị|[Cc]ô|[Cc]ậu|[Vv]ua)\s+([A-ZĐ][^\W\d_]*)", " ".join(script)))
    protected = flow_first_frames(row, project_root) | {Path(str(x)).name for x in first_frames}
    locks = row.get("media_locks") or {}
    occupied = {int(k) for mapping in (row.get("figures") or {}, row.get("clips") or {})
                for k, spec in mapping.items() if str(k).isdigit()
                and isinstance(spec, dict) and spec.get("type", "none") != "none"}
    for key, spec in (row.get("visuals") or {}).items():
        if not str(key).isdigit() or not isinstance(spec, dict):
            continue
        ats = [int(x["at"]) for field in ("items", "steps", "pins", "rows", "notes", "bars")
               for x in spec.get(field, []) if isinstance(x, dict) and str(x.get("at", "")).isdigit()]
        occupied.update(range(int(key), int(spec.get("until") or max([int(key), *ats])) + 1))
    candidates = []
    for i, (text, (a, b)) in enumerate(zip(script, spans), 1):
        if a < OPENING_GUARD_S or str(text).strip().startswith("**") and str(text).strip().endswith("**"):
            continue
        head = media.get(str(i))
        if head is not None:
            if head.get("lock") or locks.get(str(i)) or locks.get(i):
                continue
            for cut, shot in [(None, head), *enumerate(head.get("cuts", []))]:
                name = Path(str(shot.get("path", ""))).name
                if (shot.get("kind") != "local" or not _AI.fullmatch(name) or shot.get("lock")
                        or shot.get("first_frame") or shot.get("flow_first_frame") or name in protected):
                    continue
                query = prompt_query(descriptions.get(name), channel, names)
                if (not query and config.get("concept_broll") and cut is None
                        and not CHARACTERS.search(str(text)) and not PEOPLE.search(str(text))
                        and not any(re.search(rf"\b{re.escape(_fold(n))}\b", _fold(text)) for n in names if n)):
                    # Opt-in (Lead 25/11): câu giải thích khái niệm không nhắc nhân vật -> B-roll hợp nghĩa
                    # thay ảnh nhân vật lấp chỗ. Mặc định tắt; bật bằng media_mix.concept_broll = true.
                    query = concept_query(text, channel)
                if query:
                    candidates.append((i, cut, query, str(Path(shot["path"]))))
        elif i not in occupied and not any(re.search(rf"\b{re.escape(_fold(n))}\b", _fold(text)) for n in names if n):
            query = query_for(text, channel)
            if query:
                candidates.append((i, None, query, None))
    candidates = diversify_queries(candidates, int(config.get("max_query_repeat", 3)))
    # Measure every proposed shot through the actual hold/cut/visual adapter.
    # Marker paths exist only in this in-memory probe, never in exported plans.
    probe = copy.deepcopy(row)
    markers = {}
    for index, (line, cut, query, _) in enumerate(candidates):
        spec = _stock_spec(_get_shot(probe["media"], line, cut), "image", query)
        marker = f"mix_probe_{index}.png"
        spec["path"] = marker
        _set_shot(probe["media"], line, cut, spec)
        markers[marker] = index
    seconds = Counter()
    for scene in _scenes(probe, spans):
        if scene.get("image") in markers:
            seconds[markers[scene["image"]]] += scene["t1"] - scene["t0"]
    initial = _scenes(row, spans)
    total = sum(s["t1"] - s["t0"] for s in initial)
    used = {k: sum(s["t1"] - s["t0"] for s in initial if s.get("stock_kind") == k) for k in targets}
    groups = defaultdict(list)
    for index, candidate in enumerate(candidates):
        if seconds[index] > 0:
            groups[candidate[3] or f"line:{candidate[0]}"].append(index)
    ref_counts = Counter(_ai_refs(row))
    # Prefer removing every use of a still, so savings refer to files, not uses.
    def rank(group):
        ref, indices = group
        removable = ref in ref_counts and len(indices) == ref_counts[ref] and Path(ref).name not in protected
        return (not removable, hashlib.sha256(f"{row.get('id')}:{ref}".encode()).hexdigest())
    added = {k: 0 for k in targets}
    for _, indices in sorted(groups.items(), key=rank):
        for index in sorted(indices, key=lambda j: (-seconds[j], j)):
            line, cut, query, ref = candidates[index]
            kind = max(targets, key=lambda k: targets[k] * total - used[k])
            deficit = targets[kind] * total - used[kind]
            if deficit <= 0 or abs(deficit - seconds[index]) >= deficit:
                continue
            spec = _stock_spec(_get_shot(media, line, cut), kind, query)
            _set_shot(media, line, cut, spec)
            used[kind] += seconds[index]
            added[kind] += 1
    final = _scenes(row, spans)
    used = {k: sum(s["t1"] - s["t0"] for s in final if s.get("stock_kind") == k) for k in targets}
    after_refs = set(_ai_refs(row))
    remaining_names = {Path(p).name for p in after_refs}
    removed = sorted({Path(p).name for p in before_refs - after_refs} - remaining_names - protected)
    # Idempotent reports retain the savings of earlier replacement passes.
    previous_removed = (row.get("media_mix_report") or {}).get("ai_removed", [])
    removed = sorted(set(removed) | (set(previous_removed) - {Path(p).name for p in after_refs} - protected))
    row["media_mix_report"] = {"timing": "ước theo spans; cùng adapter hold/cut/visual của runner",
                               "eligible": sum(v > 0 for v in seconds.values()), "added": added,
                               "ai_removed": removed, "ai_images_saved": len(removed),
                               "protected_flow_frames": sorted(protected),
                               "estimated_shares": {k: used[k] / total if total else 0 for k in used}}
    for kind in targets:
        if total and used[kind] / total < targets[kind] - .05:
            print(f"!! media_mix {row.get('id')}: stock {kind} {used[kind]/total:.1%}; thiếu câu phù hợp, không ép mục tiêu {targets[kind]:.0%}")


def main():
    import argparse
    from library.tools.plan_enrich import line_spans
    parser = argparse.ArgumentParser(description="Xuất plan .mix.json ngoại tuyến; không ghi đè plan thật")
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--years", nargs="+", type=int, default=[1965, 1977, 1959, 1962, 1974])
    parser.add_argument("--concept-broll", action="store_true", help="bật B-roll khái niệm (thay ảnh nhân vật lấp chỗ ở câu giải thích)")
    args = parser.parse_args()
    for year in args.years:
        path = args.data_root / f"output/cl_staging/long/plan_L_fs_d25_{year}.json"
        original_bytes = path.read_bytes()
        trial = json.loads(original_bytes)
        for row in trial if isinstance(trial, list) else [trial]:
            spans, timing = line_spans(row)
            row.setdefault("media_mix", {})  # CLI xuất bản thử = bật rõ ràng
            if args.concept_broll:
                row["media_mix"] = {**(row.get("media_mix") or {}), "concept_broll": True}
            enrich_stock(row, row.get("series"), spans, project_root=args.data_root)
            report = row["media_mix_report"]
            report["timing"] = timing + "; cùng adapter hold/cut/visual của runner"
            print(f"{year} | {report['estimated_shares']['video']:.2%} | {report['estimated_shares']['image']:.2%} | {report['ai_images_saved']}")
            print(f"{year} AI không còn dùng: " + ", ".join(report["ai_removed"]))
        path.with_suffix(".mix.json").write_text(json.dumps(trial, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if path.read_bytes() != original_bytes:
            raise RuntimeError(f"Plan gốc thay đổi trong lúc xuất: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
