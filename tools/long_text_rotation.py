"""Plan-level memory for existing text effects, shared across all chapters.

Explicit fx/preset choices are retained and audited. Locked kinetic presets
stay opt-in; automatic rotation uses the existing word effects/keycard styles.
"""
from __future__ import annotations

import copy
import hashlib
import math
import re
from collections import Counter

WORD = ("rise", "drop", "type", "sync", "flip", "wipe", "zoom", "slam")
VARIANTS = {"quote": ("page", "kinetic", "glass", "type", "rise"),
            "list": ("cascade", "stack", "spotlight")}
SEMANTIC = (
    ("dissolve", ("vô thường", "buông", "tan ", "qua đi", "biến mất")),
    ("rays", ("bình an", "ánh sáng", "an lạc", "tỉnh thức")),
    ("ripple", ("nước", "thủy", "sóng", "sông", "biển")),
    ("grow", ("mộc", "cây", "lớn lên", "bắt đầu")),
)


def beats(row):
    """Actual full-screen text only, with visual holds/media precedence."""
    import hf_batch_render as HBR
    import hyperframes_bridge as HB
    from tools.visual_mix import TEXT_KINDS
    segments, t = [], 0.
    for text in row.get("script", []):
        d = max(1., len(text.replace("**", "").split()) / 185 * 60)
        segments.append({"start": t, "end": t+d})
        t += d+.5
    lines, media = HBR._shot_plan(row, segments)
    holds = HB.media_holds(lines, {int(k) for k in media}, media_specs=media)
    owner = {k: i for i, j in holds.items() for k in range(i+1, j+1)}
    seen, out = set(), []
    for i, line in enumerate(lines):
        if HBR._plan_line_kind(i, line, lines, media, owner) not in TEXT_KINDS:
            continue
        sid = line.get("visual_cont", i+1)
        if sid in seen:
            continue
        seen.add(sid)
        source = lines[sid-1]
        original = source.get("source_sentence_id", sid)
        spec = source.get("visual") or {}
        # An actual keyword overlay on an image is not a text beat.
        if (str(i+1) in media or i in owner) and (not spec or HB.is_overlay_visual(spec)):
            continue
        out.append((str(original), spec, row["script"][original-1]))
    return out


def _explicit(spec):
    if spec.get("preset"):
        return "preset:" + spec["preset"]
    if spec.get("fx"):
        return "word:" + spec["fx"]
    if spec.get("type") in VARIANTS:
        return f"{spec['type']}:{spec['variant']}" if spec.get("variant") else None
    if spec.get("type") and spec["type"] != "word":
        return "visual:" + spec["type"]
    return None


def prepare(row):
    out = copy.deepcopy(row)
    items = beats(out)
    if not items:
        return out
    counts, last = Counter(), None
    cap = max(1, math.floor(len(items) * .25))
    choices = out.setdefault("text_effects", {})
    # Account for future editorial choices before using the remaining budget.
    for sid, spec, text in items:
        fixed = _explicit(spec) or (choices.get(sid) or {}).get("effect")
        if fixed:
            counts[fixed] += 1
    for sid, spec, text in items:
        fixed = _explicit(spec) or (choices.get(sid) or {}).get("effect")
        if fixed:
            last = fixed
            continue
        constrained = spec.get("type") in VARIANTS
        if constrained:
            options = [spec["type"] + ":" + x for x in VARIANTS[spec["type"]]]
            preferred = []
        elif spec.get("type") == "word" or not out.get("kinetic"):
            options = ["word:"+fx for fx in WORD]
            preferred = []
            raw = spec.get("text") or " ".join(re.findall(r"\*\*(.+?)\*\*", text)) or text
            for fx, keys in SEMANTIC:
                if any(k in raw.lower() for k in keys):
                    preferred.append("word:"+fx)
            if re.match(r"^(KHÔNG PHẢI|CHẲNG PHẢI|ĐỪNG|SAI)\b[^·]*·", raw.strip(), re.I):
                preferred.append("word:strike")
            options = preferred + options
        else:
            # Four variants work on both paper and dark themes, plus one
            # theme-specific variant. JS validates against its own palette.
            options = ["keycard:"+x for x in ("stamp", "cascade", "placard", "lens", "brush", "gold")]
            # Gold is only available for dark, brush for paper.
            paper = out.get("style") in {"inkwash_long", "dongho_long"}
            options.remove("keycard:" + ("gold" if paper else "brush"))
            preferred = []
        pool = [x for x in options if x != last and counts[x] < cap]
        if not pool and not constrained:
            # A short Long can need a sixth treatment even though each
            # keycard palette contains five. Reuse an existing word treatment.
            pool = ["word:"+x for x in WORD if "word:"+x != last and counts["word:"+x] < cap]
        if not pool:  # Incompatible explicit choices can exhaust the quota.
            pool = [x for x in options if x != last] or options
        seed = str(out.get("id", ""))
        chosen = min(pool, key=lambda x: (0 if x in preferred else 1, counts[x],
                     hashlib.sha256(f"{seed}:{sid}:{x}".encode()).hexdigest()))
        counts[chosen] += 1
        last = chosen
        family, name = chosen.split(":", 1)
        # Bare text uses keycards when kinetic=true. Otherwise the bridge
        # materializes an existing word visual, without inventing an effect.
        if family == "word":
            if not spec:
                out.setdefault("visuals", {})[sid] = {"type": "word", "fx": name}
        choices[sid] = {"effect": chosen, family: name}
    return out


def inventory(row):
    counts = Counter()
    sequence = []
    for sid, spec, text in beats(row):
        effect = _explicit(spec) or ((row.get("text_effects") or {}).get(sid) or {}).get("effect")
        if not effect:
            if not spec:
                effect = "keycard:auto" if row.get("kinetic") else "keyword:legacy"
            elif spec.get("type") in VARIANTS:
                effect = spec["type"] + ":auto"
            elif re.match(r"^(KHÔNG PHẢI|CHẲNG PHẢI|ĐỪNG|SAI)\b[^·]*·", str(spec.get("text", "")).strip(), re.I) and row.get("wordts"):
                effect = "word:strike(auto)"
            else:
                effect = "word:auto"
        counts[effect] += 1
        sequence.append((sid, effect))
    return counts, sequence


def issues(row):
    counts, seq = inventory(row)
    # Legacy runtime auto choices cannot be inferred without a render. Audit
    # only resolved choices, never claim an automatic family is one effect.
    findings = []
    for (a, x), (b, y) in zip(seq, seq[1:]):
        if x == y and not x.endswith((":auto", ":legacy")):
            findings.append(f"câu {a}/{b}: {x} liền hai beat")
    for effect, count in counts.items():
        if count > len(seq) * .25 and not effect.endswith((":auto", ":legacy")):
            findings.append(f"{effect}: {count}/{len(seq)} beat >25%")
    return ["!! chữ lặp hiệu ứng: " + x for x in findings]
