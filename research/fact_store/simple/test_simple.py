import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from .pipeline import certain_checks, decide, review_batch, run_items


BASE = {"package_id":"p1", "title":"", "thumbnail_text":"", "first_frame_0_1s":"", "voice_0_3s":"", "escalation_3_10s":"", "payoff":"", "series_context":"", "claims":[]}


def setup_fact(value=3147.3, unit="m", status="verified"):
    return ({"facts":[{"fact_id":"f1","subject":"x","quantity":{"value":value,"unit":unit},"statement_vi":"Độ dài 3147,3 m.","evidence":[{"source_id":"s1","span":"exact evidence"}]}],"entities":[]}, {"results":[{"fact_id":"f1","status":status,"certainty":"established"}]})


class SimpleTests(unittest.TestCase):
    def test_vietnamese_number_matching_and_unit_conversion(self):
        store, ver = setup_fact()
        pkg = {**BASE, "title":"3.147,3 m"}
        self.assertFalse(certain_checks(pkg,store,ver)["flags"])
        pkg["title"]="5 m"
        self.assertEqual(certain_checks(pkg,store,ver)["flags"][0]["code"],"number_not_found")
        store,ver=setup_fact(5,"km")
        pkg["title"]="5 m"
        self.assertEqual(certain_checks(pkg,store,ver)["flags"][0]["code"],"number_not_found")

    def test_claim_id_unverified(self):
        store,ver=setup_fact(status="unverified")
        pkg={**BASE,"claims":[{"fact_ids":["f1"]}]}
        self.assertEqual(certain_checks(pkg,store,ver)["flags"][0]["code"],"unverified_fact_id")
        self.assertEqual(decide(certain_checks(pkg,store,ver),{"verdict":"ACCEPT","citations":[{}]})["verdict"],"HUMAN_REVIEW")

    def test_accept_requires_citation_and_number_clean(self):
        c={"flags":[]}
        self.assertEqual(decide(c,{"verdict":"ACCEPT","citations":[]})["verdict"],"HUMAN_REVIEW")
        self.assertEqual(decide({"flags":[{"code":"number_not_found"}]},{"verdict":"ACCEPT","citations":[{}]})["verdict"],"HUMAN_REVIEW")
        self.assertEqual(decide(c,{"verdict":"REJECT","reasons":["contradiction"]})["verdict"],"REJECT")
        self.assertEqual(decide(c,None)["verdict"],"HUMAN_REVIEW")

    def test_bad_replay_json(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"bad.json"; p.write_text("{",encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError): review_batch([], replay=str(p))

    def test_replay_missing_entries_and_duplicate_unknown_ids_are_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"replay.json"
            # Empty entry array simulates a missing response; duplicate ids are validated by the batch runner.
            p.write_text("[]",encoding="utf-8")
            self.assertEqual(review_batch([{"package_id":"p1"}],replay=str(p))["entries"],[])
            dup=[{"package_id":"p1","verdict":"ACCEPT","citations":[{}]},{"package_id":"p1","verdict":"ACCEPT","citations":[{}]},{"package_id":"outside","verdict":"ACCEPT","citations":[{}]}]
            p.write_text(json.dumps(dup),encoding="utf-8")
            result=review_batch([{"package_id":"p1"}],replay=str(p))
            self.assertEqual(sum(x["package_id"]=="p1" for x in result["entries"]),2)

    def test_missing_store_does_not_crash(self):
        self.assertTrue(certain_checks(BASE,{}, {})["ok"])
        self.assertEqual(decide({"flags":[]},None)["verdict"],"HUMAN_REVIEW")

    def test_timeout_becomes_human_review(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); item=root/"item.json"; out=root/"out.json"
            item.write_text(json.dumps(BASE),encoding="utf-8")
            with patch("research.fact_store.simple.pipeline._run_batch",side_effect=__import__("subprocess").TimeoutExpired("codex",1)):
                result=run_items(str(item),str(root),str(out))
            self.assertEqual(result["items"][0]["decision"]["verdict"],"HUMAN_REVIEW")


if __name__ == "__main__": unittest.main()
