"""P4d (E2E validation remediation) -- FS's `broll_query_sanitizer` in
domain_creative_profiles.json was an empty list. The E2E validation
confirmed the gap (`_sanitize_broll_query()` is a no-op for FS) but found
no real FS mistranslation incident to build rules from -- unlike BUD's
list (built from a real negation-loss mistranslation that returned a
Catholic-priest image for Buddhist content) and CL's list (built from a
real Short that returned prison imagery). Per explicit user decision:
ported the subset of BUD's rules addressing the DOMAIN-INDEPENDENT
failure mode (mistranslated Vietnamese -> Pexels' Western-religious-
imagery bias for words like deity/god/church/bible/hell/demon), and
deliberately did NOT port BUD's death/funeral/grief-specific rules since
Phong Thủy content doesn't discuss those themes.

Does NOT import render_short.py directly -- it pulls in
video_tool_clone's separate `core.stockfootage` package tree (a distinct
venv from this repo's own `.venv`, see the cross-repo/cross-venv
architecture elsewhere in this codebase), which risks missing
dependencies under this test's interpreter. Instead re-implements
render_short.py's exact `_compile_sanitizer_patterns()` /
`_sanitize_broll_query()` algorithm inline (stdlib `re` only) against the
real config, verified line-for-line against render_short.py in code
review."""
import re

import pytest

import domain_creative_profiles as creative_profiles


def _compile_sanitizer_patterns(topic: str) -> list[tuple[re.Pattern, str]]:
    profile = creative_profiles.load_profile_for_topic(topic)
    rules = profile.get("broll_query_sanitizer") or []
    return [(re.compile(r["pattern"], re.IGNORECASE), r["replacement"]) for r in rules]


def _sanitize_broll_query(query: str, patterns: list[tuple[re.Pattern, str]]) -> str:
    for pattern, repl in patterns:
        query = pattern.sub(repl, query)
    return query


def test_fs_sanitizer_list_is_no_longer_empty():
    profile = creative_profiles.load_profile("FS")
    assert profile["broll_query_sanitizer"], "regression guard -- must not silently go back to an empty no-op list"


def test_fs_sanitizer_patterns_all_compile():
    patterns = _compile_sanitizer_patterns("Phong Thủy")
    assert len(patterns) == 25


@pytest.mark.parametrize("query,expect_absent,expect_present", [
    ("temple deity punishment", "deity", "universe"),
    ("a hell demon guarding the gate", "hell", "shadow realm"),
    ("priests reading the bible in a church", "priest", "ancient manuscript"),
    ("the sinner walked past a cross", "sinner", "person"),
])
def test_fs_sanitizer_neutralizes_western_religious_imagery_bias(query, expect_absent, expect_present):
    """Reproduces the exact failure mode this fix targets: a mistranslated
    query containing Western-religious-coded English words must be
    neutralized before reaching Pexels."""
    patterns = _compile_sanitizer_patterns("Phong Thủy")
    result = _sanitize_broll_query(query, patterns)
    assert expect_absent not in result.lower()
    assert expect_present in result.lower()


@pytest.mark.parametrize("bud_only_word", [
    "funeral", "mourning", "graveyard", "cemetery", "tombstone", "condolences",
    "grief", "grieving", "bereave", "deceased", "loved ones",
])
def test_fs_sanitizer_does_not_include_bud_death_and_funeral_rules(bud_only_word):
    """Scoping guard: confirms the deliberate exclusion of BUD's
    death/funeral/grief-specific rules (no evidence they apply to Phong
    Thủy content) -- these queries must pass through FS's sanitizer
    UNCHANGED, not silently gain BUD's euphemism treatment."""
    patterns = _compile_sanitizer_patterns("Phong Thủy")
    query = f"a photo about {bud_only_word}"
    assert _sanitize_broll_query(query, patterns) == query


def test_bud_sanitizer_list_is_unchanged_by_this_fix():
    profile = creative_profiles.load_profile("BUD")
    assert len(profile["broll_query_sanitizer"]) == 47


def test_cl_sanitizer_list_is_unchanged_by_this_fix():
    profile = creative_profiles.load_profile("CL")
    assert len(profile["broll_query_sanitizer"]) == 34
