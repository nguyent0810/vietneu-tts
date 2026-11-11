import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motion" / "long"))
import describe as D


def test_two_authors_credit_each_track_and_license(monkeypatch):
    tracks = {
        "a": {"file": "a.mp3", "title": "First", "author": "Scott Buckley", "license": "CC BY 4.0",
              "license_url": "https://creativecommons.org/licenses/by/4.0/"},
        "b": {"file": "b.mp3", "title": "Second", "author": "Chris Zabriskie", "license": "CC BY 4.0",
              "license_url": "https://creativecommons.org/licenses/by/4.0/"},
    }
    monkeypatch.setattr(D.variety, "catalog", lambda: {"tracks": tracks})
    assert D.music_credit(["a.mp3", "b.mp3"]) == [
        '"First" by Scott Buckley (scottbuckley.com.au), licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)',
        '"Second" by Chris Zabriskie (chriszabriskie.com), licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)',
    ]


def test_legacy_macleod_credit_and_license_change(monkeypatch):
    entry = {"file": "a.mp3", "title": "Crypto", "author": "Kevin MacLeod", "license": "CC BY 4.0"}
    monkeypatch.setattr(D.variety, "catalog", lambda: {"tracks": {"a": entry}})
    old = ['"Crypto" by Kevin MacLeod (incompetech.com)',
           'Licensed under Creative Commons: By Attribution 4.0 License — http://creativecommons.org/licenses/by/4.0/']
    assert D.music_credit(["a.mp3"]) == old
    entry["license"] = "CC BY 3.0"
    assert D.music_credit(["a.mp3"]) == [old[0], old[1].replace("4.0", "3.0")]


def test_kai_tracks_keep_individual_sources_and_licenses(monkeypatch):
    tracks = {str(i): {"file": f"{i}.mp3", "title": f"Title {i}", "author": "Kai Engel",
                       "license": f"CC BY {i}.0", "license_url": f"https://license/{i}",
                       "source_url": f"https://source/{i}"} for i in (3, 4)}
    monkeypatch.setattr(D.variety, "catalog", lambda: {"tracks": tracks})
    result = D.music_credit(["3.mp3", "4.mp3"])
    assert result == [f'"Title {i}" by Kai Engel (https://source/{i}), licensed under CC BY {i}.0 (https://license/{i})'
                      for i in (3, 4)]


def test_original_legacy_capitalization_from_real_catalog():
    assert D.music_credit(["despair_and_triumph.mp3", "heart_of_nowhere.mp3"])[0] == (
        '"Despair and Triumph", "Heart of Nowhere" by Kevin MacLeod (incompetech.com)')
