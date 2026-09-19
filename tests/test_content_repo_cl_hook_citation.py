"""Audit kênh Hình Sự (2026-08-14), Part 1 -- kênh CL đã có 1 ngân hàng hook
mở đầu chi tiết, đã tự kiểm tra an toàn
(`content_repo_clone/DOMAINS/CRIMINAL_LAW/CREATIVE_KNOWLEDGE/CK_CL_001_Hinh_Su.md`,
Phần 4, mã hook H1-H15+ theo 5 Pillar), nhưng KHÔNG CÓ cơ chế nào nhắc người
soạn episode planner thực sự dùng nó -- EP001 THẬT (tập giải thích quy tắc
kênh) không hề trích dẫn mã hook hay Phần 4 ở phần mở đầu, một phần lý do
khiến tập này "nặng giải thích, thiếu hook cuốn hút" như đã audit.

VÒNG 2 (Cursor review, vòng 1 kết luận "NEEDS REWRITE"): matcher vòng 1 chỉ
khớp substring "hook"/"ck_cl_001" bất kỳ đâu -- PASS IM LẶNG cho MỌI planner
thật, vì khung episode planner chuẩn Content-Creator LUÔN có sẵn heading
"Opening Hook"/"Hook Mở Đầu" (không liên quan Phần 4), và EP001 thật cũng
cite CK_CL_001 cho lý do KHÁC (§2.4, không phải hook Phần 4) -- false-negative
đúng chính failure mode Part 1. Matcher vòng 2 đòi hỏi tín hiệu CỤ THỂ hơn:
mã hook thật dạng "H"+số, hoặc cụm "CK_CL_001"+"Phần 4" GẦN NHAU (cùng câu/
đoạn). Cũng phát hiện thêm: `long_batch_runner.discover_ready_episodes()`
(đường dùng THẬT cho pipeline Long-form) trước đây bỏ hẳn `result.problems`
-- cảnh báo không bao giờ tới console thật -- đã nối lại, xem
`test_discover_ready_episodes_prints_problems` bên dưới.

`_check_cl_hook_bank_citation()` là 1 kiểm tra ADVISORY (không chặn
production, giống mọi mục khác trong `EpisodeGateResult.problems`)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import content_repo


def _write_planner(tmp_path, body: str) -> Path:
    internal = tmp_path / "_INTERNAL"
    internal.mkdir(exist_ok=True)
    manifest = internal / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    (internal / "02_EPISODE_PLANNER.md").write_text(body, encoding="utf-8")
    return manifest


def test_warns_when_planner_has_no_hook_code_or_phan4_citation(tmp_path):
    manifest = _write_planner(tmp_path, "## Episode Identity\nTập giải thích quy tắc kênh.\n")
    problems = content_repo._check_cl_hook_bank_citation(manifest)
    assert len(problems) == 1
    assert "Phần 4" in problems[0]


def test_generic_opening_hook_heading_alone_still_warns(tmp_path):
    """Regression guard for the round-1 false-negative: a planner that ONLY
    has the generic Content-Creator template heading ("Opening Hook"/"Hook
    Mở Đầu", present in essentially every real planner) but never cites an
    actual H-code or Phần 4 must STILL warn -- this is the exact failure
    mode round 1 missed."""
    manifest = _write_planner(tmp_path, "## Beat Structure (Opening Hook + Context)\n### Beat 0 — Hook Mở Đầu\nMột buổi sáng...\n")
    problems = content_repo._check_cl_hook_bank_citation(manifest)
    assert len(problems) == 1


def test_ck_cl_001_cited_for_unrelated_section_still_warns(tmp_path):
    """Regression guard: citing CK_CL_001 for an UNRELATED reason (e.g. its
    safety-technique bank, §2.x) must not be mistaken for a Phần 4 hook
    citation -- matches the real EP001 case (cites CK_CL_001 §2.4)."""
    manifest = _write_planner(
        tmp_path,
        "KHÔNG để Beat 7 kết luận thay khán giả -- đúng cấu trúc đã dựng sẵn ở CK_CL_001 §2.4.\n",
    )
    problems = content_repo._check_cl_hook_bank_citation(manifest)
    assert len(problems) == 1


def test_no_warning_when_planner_cites_a_real_hook_code(tmp_path):
    manifest = _write_planner(tmp_path, "Mở đầu dùng hook H9 (Pillar 3, vụ án chưa lời giải).\n")
    assert content_repo._check_cl_hook_bank_citation(manifest) == []


def test_no_warning_when_planner_cites_ck_cl_001_phan_4_together(tmp_path):
    manifest = _write_planner(tmp_path, "Mở đầu điều chỉnh từ CK_CL_001 Phần 4, Pillar 2.\n")
    assert content_repo._check_cl_hook_bank_citation(manifest) == []


def test_hook_code_matching_is_case_insensitive(tmp_path):
    manifest = _write_planner(tmp_path, "dùng h12 làm mở đầu.\n")
    assert content_repo._check_cl_hook_bank_citation(manifest) == []


def test_missing_planner_file_is_not_an_error():
    fake_manifest = Path("/nonexistent/_INTERNAL/manifest.json")
    assert content_repo._check_cl_hook_bank_citation(fake_manifest) == []


def test_real_ep001_planner_correctly_warns():
    """Real-world regression check: EP001's actual planner (the file that
    motivated this audit finding) cites CK_CL_001 only for an unrelated
    safety-technique reason (§2.4), never an H-code or "Phần 4" -- the
    stricter round-2 matcher correctly flags it (round 1's matcher did
    NOT, which was the core "NEEDS REWRITE" finding)."""
    import pytest
    real_planner_dir = Path(
        "content_repo_clone/DOMAINS/CRIMINAL_LAW/PRODUCTION_PACKAGES/HINH_SU/EP001/_INTERNAL"
    )
    if not (real_planner_dir / "02_EPISODE_PLANNER.md").exists():
        pytest.skip("EP001 planner không có sẵn trong checkout này")
    fake_manifest_path = real_planner_dir / "manifest.json"
    problems = content_repo._check_cl_hook_bank_citation(fake_manifest_path)
    assert len(problems) == 1


def test_discover_ready_episodes_prints_problems(monkeypatch, tmp_path, capsys):
    """Wiring guard for the second round-1 gap: discover_ready_episodes()
    (the real code path for the Long-form pipeline, distinct from
    content_repo.py's own stage_ready_episodes()) must actually print
    result.problems, not silently discard them."""
    import long_batch_runner as lbr
    from content_repo import EpisodePaths, EpisodeGateResult

    fake_episode = EpisodePaths(
        episode_dir=tmp_path / "EP999", long_txt=tmp_path / "long.txt",
        long_manifest=tmp_path / "manifest.json", short_txt=None, short_manifests=[],
    )
    fake_result = EpisodeGateResult(
        episode=fake_episode, domain_id="CL", long_ready=False, short_ready=False,
        problems=["CẢNH BÁO TEST: fixture advisory message"],
    )

    monkeypatch.setattr(lbr, "load_github_credentials", lambda: ("tok", "url"))
    monkeypatch.setattr(lbr, "ensure_content_repo", lambda token, url: tmp_path)
    monkeypatch.setattr(lbr, "discover_episodes", lambda repo_root: [fake_episode])
    monkeypatch.setattr(lbr, "gate_episode", lambda ep: fake_result)

    lbr.discover_ready_episodes("CL", "Hình Sự")
    captured = capsys.readouterr()
    assert "CẢNH BÁO TEST: fixture advisory message" in captured.out
