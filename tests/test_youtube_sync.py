"""Test cho youtube_sync.py — phần logic thuần, không gọi mạng.

Tập trung vào những chỗ sai âm thầm: chuyển đổi dữ liệu YouTube, phân loại
cảnh báo (quyết định checkpoint có được tiến hay không), và hàng rào danh tính
kênh. Các phần cần mạng (OAuth, gọi API) không nằm ở đây; chúng được kiểm bằng
lần chạy thật trên 3 kênh.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load():
    # youtube_sync.py nằm ở gốc repo và import youtube_auth cạnh nó; pytest chạy
    # với pythonpath=["src"] nên phải thêm gốc repo vào sys.path thủ công.
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("youtube_sync", REPO_ROOT / "youtube_sync.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["youtube_sync"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ys = _load()


class TestDurationParsing:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("PT1H2M3S", 3723),
            ("PT45S", 45),
            ("PT3M", 180),
            ("PT2H", 7200),
            ("", None),
            ("bậy bạ", None),
        ],
    )
    def test_parses_iso8601(self, value: str, expected: int | None) -> None:
        assert ys._parse_iso8601_duration(value) == expected


class TestRowConversion:
    def test_maps_youtube_names_to_hub_fields(self) -> None:
        payload = {
            "columnHeaders": [
                {"name": "day"},
                {"name": "views"},
                {"name": "averageViewDuration"},
                {"name": "impressionClickThroughRate"},
            ],
            "rows": [["2026-07-01", 100, 42.5, 3.75]],
        }
        recs = ys._rows_to_records(payload, [])
        assert recs == [
            {
                "date": "2026-07-01",
                "views": 100,
                "averageViewDurationSeconds": 42.5,
                "impressionCtr": 3.75,
            }
        ]

    def test_drops_rows_without_a_date(self) -> None:
        payload = {
            "columnHeaders": [{"name": "video"}, {"name": "views"}],
            "rows": [["abc12345678", 10]],
        }
        assert ys._rows_to_records(payload, []) == []

    def test_handles_empty_and_null_rows(self) -> None:
        assert ys._rows_to_records({"columnHeaders": [], "rows": None}, []) == []
        assert ys._rows_to_records({}, []) == []

    def test_null_metric_is_omitted_not_zeroed(self) -> None:
        """Thiếu dữ liệu phải để trống, KHÔNG được biến thành 0 -- nếu không thì
        Phase 3 sẽ coi "không có số liệu" là "bằng 0" và tính sai."""
        payload = {
            "columnHeaders": [{"name": "day"}, {"name": "views"}, {"name": "impressions"}],
            "rows": [["2026-07-01", 5, None]],
        }
        rec = ys._rows_to_records(payload, [])[0]
        assert rec["views"] == 5
        assert "impressions" not in rec


class TestMergeRecords:
    def test_merges_optional_metrics_into_core(self) -> None:
        core = [{"date": "2026-07-01", "views": 10}]
        optional = [{"date": "2026-07-01", "impressions": 500}]
        merged = ys.merge_records(core, optional, ("date",))
        assert merged == [{"date": "2026-07-01", "views": 10, "impressions": 500}]

    def test_keeps_records_present_in_only_one_side(self) -> None:
        merged = ys.merge_records(
            [{"date": "2026-07-01", "views": 1}], [{"date": "2026-07-02", "impressions": 2}], ("date",)
        )
        assert len(merged) == 2

    def test_merges_on_composite_key(self) -> None:
        core = [{"youtubeVideoId": "a" * 11, "date": "2026-07-01", "views": 1}]
        opt = [{"youtubeVideoId": "a" * 11, "date": "2026-07-01", "impressions": 9}]
        merged = ys.merge_records(core, opt, ("youtubeVideoId", "date"))
        assert len(merged) == 1
        assert merged[0]["impressions"] == 9

    def test_does_not_merge_across_different_videos(self) -> None:
        core = [{"youtubeVideoId": "a" * 11, "date": "2026-07-01", "views": 1}]
        opt = [{"youtubeVideoId": "b" * 11, "date": "2026-07-01", "impressions": 9}]
        merged = ys.merge_records(core, opt, ("youtubeVideoId", "date"))
        assert len(merged) == 2


class TestWarningClassification:
    """Phân loại cảnh báo quyết định checkpoint có được tiến hay không.

    Nhầm lẫn ở đây gây một trong hai hậu quả nặng: hoặc checkpoint không bao giờ
    tiến (đồng bộ lại toàn bộ lịch sử mỗi lần chạy), hoặc checkpoint tiến qua dữ
    liệu còn thiếu và tạo lỗ hổng vĩnh viễn.
    """

    def test_notes_alone_do_not_block_checkpoint(self) -> None:
        stats = ys.SyncStats()
        stats.notes.append("Kênh không được cấp impressions/CTR")
        assert stats.gaps == []
        assert "impressions" in stats.warnings[0]

    def test_gaps_are_reported_before_notes(self) -> None:
        stats = ys.SyncStats()
        stats.notes.append("ghi chú")
        stats.gaps.append("LỖ HỔNG")
        # Lỗ hổng phải hiện trước để người đọc thấy ngay vấn đề thật.
        assert stats.warnings[0] == "LỖ HỔNG"

    def test_status_rule_matches_gaps_only(self) -> None:
        empty = ys.SyncStats()
        empty.notes.append("chỉ là ghi chú")
        assert ("PARTIAL" if empty.gaps else "SUCCEEDED") == "SUCCEEDED"

        gapped = ys.SyncStats()
        gapped.gaps.append("thiếu ngày")
        assert ("PARTIAL" if gapped.gaps else "SUCCEEDED") == "PARTIAL"


class TestTransientVsPermanentFailure:
    """Regression (Codex Phase 2 R3 HIGH): mọi lỗi chỉ số tuỳ chọn từng bị gộp
    thành "giới hạn cố định của kênh". Một lỗi 403/429/5xx tạm thời vì thế không
    chặn checkpoint, và các ngày đó khi trôi khỏi cửa sổ lùi sẽ mất vĩnh viễn."""

    @pytest.mark.parametrize("status", [403, 429, 500, 502, 503])
    def test_transient_statuses_hold_the_checkpoint(self, status: int) -> None:
        assert ys.is_transient_status(status) is True

    @pytest.mark.parametrize("status", [400, 404])
    def test_permanent_capability_limits_do_not_block(self, status: int) -> None:
        assert ys.is_transient_status(status) is False

    @pytest.mark.parametrize("status", [401, 408, 409, 418, 451, 599])
    def test_unlisted_statuses_default_to_transient(self, status: int) -> None:
        """Regression (Codex Phase 2 R4 HIGH): hàm này từng liệt kê các mã TẠM
        THỜI, nên mã chưa nghĩ tới (401 token hết hạn giữa chừng, 408 timeout)
        rơi vào nhánh "vĩnh viễn" — checkpoint vẫn tiến và dữ liệu mất luôn.
        Danh sách cho phép phải nằm ở nhánh VĨNH VIỄN, không phải ngược lại."""
        assert ys.is_transient_status(status) is True


class TestHubConfig:
    def test_rejects_missing_token(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        env = tmp_path / ".youtube_hub.env"
        env.write_text("HUB_API_BASE=http://x\n", encoding="utf-8")
        monkeypatch.setattr(ys, "HUB_ENV_FILE", env)
        with pytest.raises(ys.SyncError, match="HUB_WORKER_TOKEN"):
            ys.load_hub_config()

    def test_reads_config_and_strips_trailing_slash(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        env = tmp_path / ".youtube_hub.env"
        env.write_text(
            "# chú thích\nHUB_API_BASE=http://127.0.0.1:3000/\n"
            "HUB_WORKER_TOKEN=vhw_test\nHUB_WORKER_LABEL=máy-a\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(ys, "HUB_ENV_FILE", env)
        cfg = ys.load_hub_config()
        assert cfg.base_url == "http://127.0.0.1:3000"
        assert cfg.worker_label == "máy-a"

    def test_error_when_file_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(ys, "HUB_ENV_FILE", tmp_path / "khong-ton-tai.env")
        with pytest.raises(ys.SyncError, match="worker:token"):
            ys.load_hub_config()


class TestChannelIdentityGuard:
    """Hàng rào danh tính kênh.

    Ghi số liệu của kênh này vào bản ghi kênh khác là loại hỏng dữ liệu gần như
    không thể phát hiện về sau, nên phải chặn ở cả hai phía.
    """

    def test_refuses_when_token_points_at_another_channel(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_get(url, params, token):
            return 200, {"items": [{"id": "UCsaikhac0000000000000", "snippet": {"title": "Khác"}}]}, 1.0

        monkeypatch.setattr(ys, "youtube_get", fake_get)
        with pytest.raises(ys.SyncError, match="SAI KÊNH"):
            ys.verify_channel_identity("phong_thuy", "tok", "UCdungkenh00000000000")

    def test_accepts_matching_channel(self, monkeypatch: pytest.MonkeyPatch) -> None:
        expected = "UCdungkenh00000000000"

        def fake_get(url, params, token):
            return 200, {"items": [{"id": expected, "snippet": {"title": "Đúng"}}]}, 1.0

        monkeypatch.setattr(ys, "youtube_get", fake_get)
        assert ys.verify_channel_identity("phong_thuy", "tok", expected)["id"] == expected

    def test_refuses_when_token_has_no_channel(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(ys, "youtube_get", lambda *a: (200, {"items": []}, 1.0))
        with pytest.raises(ys.SyncError, match="không gắn với kênh"):
            ys.verify_channel_identity("phong_thuy", "tok", "UCx00000000000000000")


class TestVideoDiscoveryPagination:
    """Regression (Codex Phase 2 HIGH): trước đây chỉ lấy tối đa 200 video và
    không phân trang, nên kênh nhiều video sẽ bị bỏ sót âm thầm trong khi
    checkpoint vẫn tiến — lỗ hổng lịch sử vĩnh viễn."""

    def test_paginates_beyond_one_page(self, monkeypatch: pytest.MonkeyPatch) -> None:
        pages = {1: [[f"v{i:011d}"] for i in range(200)], 201: [[f"w{i:011d}"] for i in range(50)]}
        seen_indexes = []

        def fake_get(url, params, token):
            idx = params["startIndex"]
            seen_indexes.append(idx)
            return 200, {"columnHeaders": [{"name": "video"}], "rows": pages.get(idx, [])}, 1.0

        monkeypatch.setattr(ys, "youtube_get", fake_get)
        stats = ys.SyncStats()
        found = ys.discover_videos_with_data("l", "t", "UCx", "2026-01-01", "2026-01-31", 500, stats)

        assert seen_indexes == [1, 201]
        assert len(found) == 250
        assert stats.gaps == []

    def test_truncates_to_limit_without_claiming_a_gap(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Cắt bớt Ở ĐÂY không sinh gap.

        Độ phủ thật do HỢP của (top-video ∪ playlist uploads) quyết định trong
        `sync_channel`, và chính chỗ đó báo lỗ hổng nếu --max-videos còn thiếu.
        Báo gap ở cả hai nơi sẽ đếm trùng và giữ checkpoint một cách sai."""
        def fake_get(url, params, token):
            idx = params["startIndex"]
            rows = [[f"v{i:011d}"] for i in range(200)] if idx <= 201 else []
            return 200, {"columnHeaders": [{"name": "video"}], "rows": rows}, 1.0

        monkeypatch.setattr(ys, "youtube_get", fake_get)
        stats = ys.SyncStats()
        found = ys.discover_videos_with_data("l", "t", "UCx", "2026-01-01", "2026-01-31", 300, stats)

        assert len(found) == 300
        assert stats.gaps == []

    def test_still_requests_next_page_when_first_page_exactly_fills_limit(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Regression (Codex Phase 2 R2 HIGH): vòng lặp từng dừng ngay tại
        `limit`, nên một trang đầy vừa khít trông y hệt "đã hết dữ liệu". Phải
        hỏi thêm ít nhất một trang nữa để PHÂN BIỆT hai trường hợp đó."""
        seen = []

        def fake_get(url, params, token):
            idx = params["startIndex"]
            seen.append(idx)
            rows = [[f"v{i:011d}"] for i in range(200)] if idx <= 201 else []
            return 200, {"columnHeaders": [{"name": "video"}], "rows": rows}, 1.0

        monkeypatch.setattr(ys, "youtube_get", fake_get)
        stats = ys.SyncStats()
        ys.discover_videos_with_data("l", "t", "UCx", "2026-01-01", "2026-01-31", 200, stats)

        assert seen == [1, 201], "phải hỏi trang 2 dù trang 1 đã đầy đúng limit"

    def test_api_row_cap_is_a_note_not_a_gap(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Báo cáo top-video của YouTube chỉ trả tối đa 200 hàng; startIndex=201
        trả 400. Đó là TRẦN CỨNG của API, không phải lỗi — coi là lỗ hổng thì
        mọi kênh trên 200 video sẽ PARTIAL vĩnh viễn và checkpoint không bao giờ
        tiến. Phần thiếu được bù bằng playlist uploads."""
        def fake_get(url, params, token):
            idx = params["startIndex"]
            if idx == 1:
                return 200, {"columnHeaders": [{"name": "video"}],
                             "rows": [[f"v{i:011d}"] for i in range(200)]}, 1.0
            return 400, {"error": {"message": "startIndex too large"}}, 1.0

        monkeypatch.setattr(ys, "youtube_get", fake_get)
        stats = ys.SyncStats()
        found = ys.discover_videos_with_data("l", "t", "UCx", "2026-01-01", "2026-01-31", 1000, stats)

        assert len(found) == 200
        assert stats.gaps == [], "trần API không được coi là lỗ hổng dữ liệu"
        assert stats.notes and "trần 200" in stats.notes[0]

    def test_exact_total_without_truncation_records_no_gap(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Ngược lại: kênh có ĐÚNG 200 video và limit=200 thì không phải lỗ hổng."""
        def fake_get(url, params, token):
            idx = params["startIndex"]
            rows = [[f"v{i:011d}"] for i in range(200)] if idx == 1 else []
            return 200, {"columnHeaders": [{"name": "video"}], "rows": rows}, 1.0

        monkeypatch.setattr(ys, "youtube_get", fake_get)
        stats = ys.SyncStats()
        found = ys.discover_videos_with_data("l", "t", "UCx", "2026-01-01", "2026-01-31", 200, stats)

        assert len(found) == 200
        assert stats.gaps == [], "đủ đúng bằng limit thì không được báo lỗ hổng giả"

    def test_api_error_becomes_a_gap(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(ys, "youtube_get", lambda *a: (403, {}, 1.0))
        stats = ys.SyncStats()
        assert ys.discover_videos_with_data("l", "t", "UCx", "2026-01-01", "2026-01-31", 100, stats) == []
        assert stats.gaps


class TestPlaylistPagination:
    """Regression (Codex Phase 2 R6 HIGH): `fetch_recent_video_ids` dừng đúng
    tại `limit` dù còn `nextPageToken`, nên kênh có đúng limit+1 video trông y
    hệt kênh có đúng limit video — hợp hai nguồn vẫn bằng limit, không gap nào
    được ghi, và video thứ limit+1 mất vĩnh viễn.

    Cùng một lớp lỗi off-by-one đã sửa ở discover_videos_with_data (R2); chỗ này
    bị bỏ sót."""

    @staticmethod
    def _pages(monkeypatch: pytest.MonkeyPatch, total: int) -> None:
        def fake_get(url, params, token):
            start = int(params.get("pageToken") or 0)
            ids = [{"contentDetails": {"videoId": f"v{i:010d}"}} for i in range(start, min(start + 50, total))]
            nxt = str(start + 50) if start + 50 < total else ""
            return 200, {"items": ids, **({"nextPageToken": nxt} if nxt else {})}, 1.0

        monkeypatch.setattr(ys, "youtube_get", fake_get)

    def test_over_fetches_by_one_to_detect_more(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._pages(monkeypatch, total=201)
        got = ys.fetch_recent_video_ids("l", "t", "PL", 200)
        # 201 phải lộ ra ít nhất limit+1 để phía gọi biết là còn nữa.
        assert len(got) == 201

    def test_exact_limit_reports_exactly_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._pages(monkeypatch, total=200)
        got = ys.fetch_recent_video_ids("l", "t", "PL", 200)
        assert len(got) == 200, "đúng bằng limit thì không được báo dư"

    def test_small_channel_unaffected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._pages(monkeypatch, total=17)
        assert len(ys.fetch_recent_video_ids("l", "t", "PL", 200)) == 17


class TestProvenanceNeverLeaksCredentials:
    def test_api_call_log_has_no_authorization_header(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            ys, "youtube_get", lambda *a: (200, {"columnHeaders": [], "rows": []}, 1.0)
        )
        stats = ys.SyncStats()
        ys.discover_videos_with_data("l", "secret-token", "UCx", "2026-01-01", "2026-01-31", 10, stats)

        logged = repr(stats.api_calls)
        assert "secret-token" not in logged
        assert "Authorization" not in logged
