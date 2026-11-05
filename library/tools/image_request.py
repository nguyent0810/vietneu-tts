"""Resolve a requested image from the shared asset catalog or build a prompt.

This module never contacts an image service. A prompt result includes a stable
snapshot suitable for review and for the later asset provenance record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from . import assets, prompt_builder
except ImportError:  # direct-file loading in lightweight test/tooling contexts
    import sys
    _TOOLS = str(Path(__file__).resolve().parent)
    if _TOOLS not in sys.path:
        sys.path.insert(0, _TOOLS)
    import assets  # type: ignore[no-redef]
    import prompt_builder  # type: ignore[no-redef]


def resolve_image(need: str, channel: str, *, manifest_path: Path | None = None,
                  root: Path | None = None, today=None) -> dict[str, Any]:
    """Find a recent image in channel/shared scope, else return a prompt snapshot."""
    root = Path(root or assets.REPO_ROOT)
    # A caller may point at a separate checkout/catalog; keep the implicit
    # manifest aligned with that root rather than this module's checkout.
    manifest_path = Path(manifest_path or (root / "library" / "assets" / "manifest.jsonl"))
    # find_assets orders channel hits before shared fallback and applies the
    # channel's kho_loc to both groups; passing "chung" here would lose that.
    hits = assets.find_assets(
        pham_vi=channel, tag=need, kind="img", exclude_used_days=7,
        channel=channel, manifest_path=manifest_path, root=root, today=today,
    )
    if hits:
        hit = hits[0]
        return {"asset": hit, "scope": hit.get("hang_pham_vi"), "prompt": None, "snapshot": None}

    profile_path = root / "library" / "channels" / f"{channel}.yaml"
    if not profile_path.is_file():
        profile_path = root / "library" / "channels" / f"{channel}.json"
    profile = prompt_builder.load_profile(profile_path)
    _rules, entries, _blocked = prompt_builder.load_lexicon(profile, root / "library" / "assets" / "lexicon")
    entry, phrase = prompt_builder.match_sentence(need, entries, [])
    fallback = entry is None
    if fallback:
        # Preserve the caller's scene description as the subject while still
        # applying channel style, cultural guidance, lighting, and safeguards.
        entry = {"en": " ".join(str(need).split())}
    # The deterministic ID is derived from the request and profile, not runtime randomness.
    sid = 1
    prompt = prompt_builder.ghep_prompt(profile, entry, "image_request", sid, _rules)
    snapshot_payload = {
        "channel": channel,
        "need": need,
        "matched_phrase": phrase,
        "entry": entry,
        "fallback": fallback,
        "prompt": prompt,
    }
    canonical = json.dumps(snapshot_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    snapshot = {**snapshot_payload, "sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest()}
    return {"asset": None, "scope": None, "prompt": prompt, "snapshot": snapshot}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tra kho ảnh hoặc dựng prompt; không gọi dịch vụ tạo ảnh")
    parser.add_argument("--need", required=True, help="Câu hoặc mô tả cảnh cần tra cứu")
    parser.add_argument("--channel", required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args(argv)
    result = resolve_image(args.need, args.channel, manifest_path=args.manifest, root=args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
