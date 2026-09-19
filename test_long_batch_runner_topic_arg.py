"""P4c (E2E validation remediation) -- long_batch_runner.py's `--topic`
CLI flag used to default STATICALLY to "Phật giáo" (BUD's topic name)
regardless of `--domain`. Calling `--domain FS` or `--domain CL` without
also remembering to pass `--topic` silently processed the WRONG
registry/output directory (BUD's) while every OTHER step of the same run
(creative_director.py's profile selection, B-roll sanitizer, etc.) still
used the correctly-passed `--domain` -- channels get mixed within a
single run. Real footgun: `--domain` and `--topic` were two independent,
manually-kept-in-sync flags with no cross-check.

Fixed by making `--topic` default to None and resolving it from
`--domain` via the existing domain_topics.json mapping (new forward
lookup `domain_creative_profiles.topic_for_domain_id()`, mirroring the
existing reverse `domain_id_for_topic()`) ONLY when `--topic` is actually
omitted -- an explicitly-passed `--topic` (including a deliberately
mismatched one, as used by other tests in this suite) is never
overridden or validated against the domain."""
import json

import pytest

import domain_creative_profiles as creative_profiles
import long_batch_runner as lbr


# --- topic_for_domain_id() -- pure lookup, real domain_topics.json ----------
# (small, stable production config -- same rationale as P4a's full-pipeline
# tests against the real sea_g2p dependency: testing against the real file
# is more meaningful than a mocked stand-in for a 4-line static mapping.)


@pytest.mark.parametrize("domain_id,expected_topic", [
    ("BUD", "Phật giáo"),
    ("FS", "Phong Thủy"),
    ("CL", "Hình Sự"),
])
def test_topic_for_domain_id_matches_real_mapping(domain_id, expected_topic):
    assert creative_profiles.topic_for_domain_id(domain_id) == expected_topic


def test_topic_for_domain_id_unknown_domain_returns_none_not_a_guess():
    assert creative_profiles.topic_for_domain_id("NOT_A_REAL_DOMAIN") is None


def test_topic_for_domain_id_is_the_true_inverse_of_domain_id_for_topic():
    data = json.loads(creative_profiles.DOMAIN_TOPICS_FILE.read_text(encoding="utf-8"))
    for domain_id, topic in data["domains"].items():
        assert creative_profiles.topic_for_domain_id(domain_id) == topic
        assert creative_profiles.domain_id_for_topic(topic) == domain_id


# --- main()'s CLI wiring -----------------------------------------------------


@pytest.fixture(autouse=True)
def _isolated_registry(tmp_path, monkeypatch):
    fake_root = tmp_path / "output" / "long"
    monkeypatch.setattr(lbr, "_REGISTRY_PRODUCTION_ROOT", fake_root)
    monkeypatch.setattr(lbr, "_registry_path", lambda topic: fake_root / topic / "registry.json")
    return fake_root


def _run_main(monkeypatch, argv_extra):
    calls = {}

    def fake_run_audio_stage(topic):
        calls["run_audio_stage_topic"] = topic

    def fake_discover_ready_episodes(domain_id, topic):
        calls["discover_domain"] = domain_id
        calls["discover_topic"] = topic
        return []  # empty -- main() returns right after the "no pending" print, no further mocking needed

    monkeypatch.setattr(lbr, "run_audio_stage", fake_run_audio_stage)
    monkeypatch.setattr(lbr, "discover_ready_episodes", fake_discover_ready_episodes)
    monkeypatch.setattr("sys.argv", ["long_batch_runner.py", "--count", "1", "--dry-run"] + argv_extra)

    exit_code = lbr.main()
    return exit_code, calls


@pytest.mark.parametrize("domain_id,expected_topic", [
    ("BUD", "Phật giáo"),
    ("FS", "Phong Thủy"),
    ("CL", "Hình Sự"),
])
def test_omitted_topic_resolves_to_the_correct_domain_specific_topic(monkeypatch, domain_id, expected_topic):
    exit_code, calls = _run_main(monkeypatch, ["--domain", domain_id])
    assert exit_code == 0
    assert calls["run_audio_stage_topic"] == expected_topic
    assert calls["discover_domain"] == domain_id
    assert calls["discover_topic"] == expected_topic


def test_omitting_domain_and_topic_together_still_defaults_to_bud_as_before():
    """Regression guard: the OLD static default ('Phật giáo' when nothing
    is passed at all) must keep working -- this fix only changes what
    happens when --domain is given WITHOUT --topic, not the fully-bare
    invocation BUD operators already rely on."""
    assert creative_profiles.topic_for_domain_id("BUD") == "Phật giáo"


def test_explicit_topic_is_never_overridden_even_when_it_does_not_match_the_domain(monkeypatch):
    """A deliberately mismatched --topic (e.g. test fixtures using "Test
    Topic" with an unrelated --domain, as elsewhere in this suite) must be
    respected verbatim -- this fix closes the OMISSION footgun, it does
    not add mismatch validation on top."""
    exit_code, calls = _run_main(monkeypatch, ["--domain", "CL", "--topic", "Some Unrelated Topic"])
    assert exit_code == 0
    assert calls["run_audio_stage_topic"] == "Some Unrelated Topic"
    assert calls["discover_domain"] == "CL"
    assert calls["discover_topic"] == "Some Unrelated Topic"


def test_omitted_topic_with_unknown_domain_fails_closed_without_guessing(monkeypatch, capsys):
    """No entry for the domain in domain_topics.json -- must not guess a
    topic name, must not proceed and touch any registry, must return a
    non-zero exit code."""
    exit_code, calls = _run_main(monkeypatch, ["--domain", "NOT_A_REAL_DOMAIN"])
    assert exit_code == 1
    assert "run_audio_stage_topic" not in calls, "must not proceed to the audio stage with a guessed topic"
    assert "domain_topics.json" in capsys.readouterr().err
