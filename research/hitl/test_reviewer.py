import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research.hitl import reviewer


class ReviewerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.stores = self.root / "stores"
        self.stores.mkdir()
        store = {"entities": [{"entity_id": "e", "name": "Entity", "aliases": []}], "facts": [
            {"fact_id": "a", "entity_ids": ["e"], "statement_vi": "A", "variant_group": "v", "evidence": [{"source_id": "s1", "span": "quote A"}]},
            {"fact_id": "b", "entity_ids": [], "statement_vi": "B", "variant_group": "v", "evidence": [{"source_id": "s2", "span": "quote B"}]},
            {"fact_id": "c", "entity_ids": [], "statement_vi": "C", "conflicts_with": ["a"], "evidence": [{"source_id": "s3", "span": "quote C"}]},
        ]}
        (self.stores / "t.json").write_text(json.dumps(store), encoding="utf-8")
        (self.stores / "t.verification.json").write_text(json.dumps({"results": [{"fact_id": "a", "status": "verified"}]}), encoding="utf-8")
        self.input = self.root / "candidates.json"
        self.output = self.root / "out.json"

    def tearDown(self): self.tmp.cleanup()

    def _videos(self, n=1):
        return [{"video_id": f"v{i}", "topic_id": "t", "channel": "x", "publish_date": "2026-01-01", "candidates": [{"candidate_id": f"c{i}", "title": "Entity"}]} for i in range(n)]

    def _go(self, replay, rows=None):
        self.input.write_text(json.dumps(rows if rows is not None else self._videos()), encoding="utf-8")
        rp = self.root / "replay.json"
        rp.write_text(json.dumps(replay), encoding="utf-8")
        return reviewer.run(self.input, self.stores, self.output, batch=1, replay=rp)

    def test_replay_and_no_verdict_fields(self):
        result = self._go({"videos": [{"video_id": "v0", "candidates": [{"candidate_id": "c0", "flags": [], "note": "ok"}]}]})
        self.assertEqual(result[0]["review_status"], "ok")
        self.assertNotIn("verdict", json.dumps(result).lower())

    def test_invalid_replay_json_reported(self):
        self.input.write_text(json.dumps(self._videos()), encoding="utf-8")
        replay = self.root / "broken.json"; replay.write_text("{", encoding="utf-8")
        result = reviewer.run(self.input, self.stores, self.output, replay=replay)
        self.assertEqual(result[0]["review_status"], "review_failed")

    def test_timeout_is_reported_without_crash(self):
        self.input.write_text(json.dumps(self._videos()), encoding="utf-8")
        with patch.object(reviewer, "_run_batch", side_effect=__import__("subprocess").TimeoutExpired("codex", 2)):
            result = reviewer.run(self.input, self.stores, self.output)
        self.assertIn("timeout", result[0]["failure_reason"])

    def test_non_dict_and_id_errors_are_isolated(self):
        rows = self._videos(4)
        rows[0] = "bad"
        rows[1]["candidates"][0].pop("candidate_id")
        rows[2]["candidates"].append(dict(rows[2]["candidates"][0]))
        rows[3]["video_id"] = "v2"
        result = self._go({"videos": []}, rows)
        self.assertTrue(all(x["review_status"] == "review_failed" for x in result))

    def test_missing_response_candidate_gets_flag(self):
        result = self._go({"videos": [{"video_id": "v0", "candidates": []}]})
        self.assertIn("review_failed", [x["code"] for x in result[0]["candidates"][0]["flags"]])

    def test_no_sources_adds_high_missing_flag(self):
        self.input.write_text(json.dumps([{**self._videos()[0], "topic_id": "absent"}]), encoding="utf-8")
        rp = self.root / "r.json"; rp.write_text(json.dumps({"videos": [{"video_id": "v0", "candidates": [{"candidate_id": "c0", "flags": [], "note": ""}]}]}), encoding="utf-8")
        result = reviewer.run(self.input, self.stores, self.output, replay=rp)
        flags = result[0]["candidates"][0]["flags"]
        flag = next(x for x in flags if x["code"] == "missing_source")
        self.assertEqual(flag["severity"], "high")

    def test_conflict_unverified_facts_are_sent_and_labeled(self):
        selected = reviewer.select_reviewer_sources({"title": "Entity", "claims": [{"fact_ids": ["a"]}]}, json.loads((self.stores / "t.json").read_text()), json.loads((self.stores / "t.verification.json").read_text()))
        facts = {x["fact_id"]: x for x in selected["sources"]}
        self.assertEqual(set(facts), {"a", "b", "c"})
        self.assertEqual(facts["b"]["status"], "unverified")
        self.assertTrue(facts["b"]["conflicting"])

    def test_batch_does_not_leak_video_reviews(self):
        rows = self._videos(2)
        self.input.write_text(json.dumps(rows), encoding="utf-8")
        rp = self.root / "r.json"; rp.write_text(json.dumps({"videos": [{"video_id": "v0", "candidates": [{"candidate_id": "c0", "flags": [], "note": "first"}]}]}), encoding="utf-8")
        result = reviewer.run(self.input, self.stores, self.output, batch=2, replay=rp)
        self.assertEqual(result[0]["candidates"][0]["note"], "first")
        self.assertEqual(result[1]["candidates"][0]["flags"][0]["code"], "review_failed")

    def test_malformed_response_candidate_records_fail_video(self):
        for bad in ("bad", {}, {"candidate_id": ""}):
            with self.subTest(record=bad):
                result = self._go({"videos": [{"video_id": "v0", "candidates": [bad]}]})
                self.assertEqual(result[0]["review_status"], "review_failed")
                self.assertIn("candidate record", result[0]["failure_reason"])

    def test_duplicate_and_unknown_response_candidate_ids_fail_video(self):
        for reply_candidates, expected in [
            ([{"candidate_id": "c0"}, {"candidate_id": "c0"}], "duplicate candidate_id"),
            ([{"candidate_id": "other"}], "unknown candidate_id"),
        ]:
            with self.subTest(expected=expected):
                result = self._go({"videos": [{"video_id": "v0", "candidates": reply_candidates}]})
                self.assertEqual(result[0]["review_status"], "review_failed")
                self.assertIn(expected, result[0]["failure_reason"])

    def test_batch_tokens_are_evenly_allocated_and_batch_total_recorded_once(self):
        rows = self._videos(2)
        self.input.write_text(json.dumps(rows), encoding="utf-8")
        parsed = {"videos": [{"video_id": f"v{i}", "candidates": [{"candidate_id": f"c{i}", "flags": [], "note": ""}]} for i in range(2)]}
        with patch.object(reviewer, "_run_batch", return_value=(parsed, 17, 10, 4, 3, 2, 8.0, "m")):
            result = reviewer.run(self.input, self.stores, self.output, batch=2)
        self.assertEqual([x["tokens"] for x in result], [9, 8])
        self.assertEqual([x["cached_input_tokens"] for x in result], [1, 1])
        self.assertEqual(result[0]["batch_tokens_total"], 17)
        self.assertIsNone(result[1].get("batch_tokens_total"))

    def test_usage_is_read_from_turn_completed(self):
        lines = [
            {"type": "item.completed", "item": {"type": "agent_message", "text": '{"videos":[]}'}},
            {"type": "turn.completed", "model": "m", "usage": {"input_tokens": 10, "output_tokens": 4, "reasoning_output_tokens": 3, "cached_input_tokens": 2}},
        ]
        fake = type("Proc", (), {"returncode": 0, "stdout": "\n".join(json.dumps(x) for x in lines), "stderr": ""})()
        with patch.object(reviewer.subprocess, "run", return_value=fake):
            _, tokens, inp, out, reasoning, cached, _, model = reviewer._run_batch([], timeout=1)
        self.assertEqual((tokens, inp, out, reasoning, cached, model), (17, 10, 4, 3, 2, "m"))


if __name__ == "__main__": unittest.main()


def test_missing_candidate_marks_whole_video_failed():
    from research.hitl.reviewer import _review_one
    video = {"video_id": "v1", "candidates": [{"candidate_id": "c1"}, {"candidate_id": "c2"}]}
    sourceinfo = {"sources": [], "sources_truncated": [], "sources_missing": False}
    reply = {"video_id": "v1", "candidates": [{"candidate_id": "c1", "flags": [], "note": ""}]}
    out = _review_one(video, sourceinfo, reply, (0, 0, 0, 0, 0, 0, "m"))
    assert out["review_status"] == "review_failed"
    assert "c2" in out["failure_reason"]


def test_sources_collected_from_candidates_and_string_fact_ids():
    from research.hitl.reviewer import select_reviewer_sources
    store = {"entities": [{"entity_id": "fansipan", "name": "Fansipan", "aliases": []}],
             "facts": [{"fact_id": "f1", "subject": "fansipan", "predicate": "measured_as", "evidence": [{"source_id": "s1", "span": "Fansipan is 3,147.3 m"}]},
                       {"fact_id": "f2", "subject": "other", "predicate": "other", "evidence": [{"source_id": "s1", "span": "unrelated text here"}]}]}
    ver = {"results": [{"fact_id": "f1", "status": "verified"}, {"fact_id": "f2", "status": "verified"}]}
    video = {"video_id": "v", "candidates": [{"candidate_id": "c1", "title": "Đỉnh núi", "claims": [{"field": "title", "span": "x", "fact_ids": "f2"}]},
                                              {"candidate_id": "c2", "title": "Fansipan cao bao nhiêu?"}]}
    sent = {s["fact_id"] for s in select_reviewer_sources(video, store, ver)["sources"]}
    assert {"f1", "f2"} <= sent
