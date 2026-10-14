"""Real incident (2026-08-11): CONTENT_TOOL_REPO pointed at a repo whose
main branch was later replaced with unrelated pipeline code (not this
project's fault -- an explicit, confirmed user action on that repo) --
ensure_content_repo() kept succeeding (git fetch/clone itself works fine
against any repo), and discover_episodes() then silently returned an
empty list instead of surfacing a clear error, because it merely checks
`if not domains_root.exists(): return []`.

_validate_content_repo_structure() closes this gap: fail closed
immediately after fetch/clone if the repo doesn't actually look like a
content repo (no DOMAINS/, or an empty DOMAINS/), rather than letting a
wrong-repo-content situation masquerade as "no episodes ready today"."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_repo import ContentRepoUnavailableError, _validate_content_repo_structure


def test_passes_when_domains_has_real_subdirectories(tmp_path):
    (tmp_path / "DOMAINS" / "BUDDHISM").mkdir(parents=True)
    _validate_content_repo_structure(tmp_path)  # must not raise


def test_raises_when_domains_directory_is_entirely_missing(tmp_path):
    """Reproduces the real incident shape: repo fetched fine, but its
    root now has code files instead of a DOMAINS/ tree."""
    (tmp_path / "creative_director.py").write_text("# pipeline code, not content", encoding="utf-8")
    with pytest.raises(ContentRepoUnavailableError, match="KHÔNG có thư mục DOMAINS/"):
        _validate_content_repo_structure(tmp_path)


def test_raises_when_domains_exists_but_is_empty(tmp_path):
    (tmp_path / "DOMAINS").mkdir()
    with pytest.raises(ContentRepoUnavailableError, match="rỗng"):
        _validate_content_repo_structure(tmp_path)


def test_raises_when_domains_contains_only_files_no_subdirectories(tmp_path):
    domains = tmp_path / "DOMAINS"
    domains.mkdir()
    (domains / "README.md").write_text("not a domain folder", encoding="utf-8")
    with pytest.raises(ContentRepoUnavailableError, match="rỗng"):
        _validate_content_repo_structure(tmp_path)
