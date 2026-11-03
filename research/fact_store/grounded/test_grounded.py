import hashlib,json,tempfile,unittest
from pathlib import Path
from .check import det_check,spans_for
from .pipeline import decide
from .review import relevant_facts,_usage

STORE={"sources":[{"source_id":"s1","publisher":"Viện Dữ liệu"}],"entities":[{"entity_id":"e1","name":"Núi An","aliases":["An"]}],"facts":[
 {"fact_id":"f1","subject":"e1","predicate":"height","quantity":{"value":5,"unit":"km"},"time":{"start":"2020"},"qualifiers":{},"statement_vi":"Núi An cao 5 km","evidence":[{"source_id":"s1"}]},
 {"fact_id":"f2","subject":"e1","predicate":"height","quantity":{"value":100,"unit":"m"},"time":{"start":"2020"},"qualifiers":{"condition":"theo truyện"},"statement_vi":"Núi An cao 100 m","evidence":[{"source_id":"s1"}]},
]}
VER={"results":[{"fact_id":"f1","status":"verified"},{"fact_id":"f2","status":"verified"}]}
def package(text,claims=None): return {"title":text,"claims":claims or [],"thumbnail_text":"","first_frame_0_1s":"","voice_0_3s":"","escalation_3_10s":"","payoff":""}

class GroundedTests(unittest.TestCase):
 def test_span_id_is_stable_and_sentence_scoped(self):
  s=spans_for(package("First. Second!")); self.assertEqual(s[0]["span_id"],"title:0:"+hashlib.sha1(b"First.").hexdigest()[:8]); self.assertEqual(len(s),2)
 def test_empty_field_no_span_nonempty_has_span(self):
  self.assertEqual(spans_for(package("")),[]); self.assertGreaterEqual(len(spans_for(package("x"))),1)
 def test_unit_identity_km_does_not_support_m(self):
  d=det_check(package("Núi An cao 5 m."),STORE,VER)
  self.assertTrue(any(i["code"]=="ungrounded_number" and i["token"]=="5 m" for i in d["issues"]))
 def test_wrong_number_contradiction_reject(self):
  p=package("Núi An height 400 m năm 2020",[{"field":"title","span":"Núi An height 400 m năm 2020","kind":"factual","fact_ids":["f2"]}]); d=det_check(p,STORE,VER)
  self.assertEqual(decide(d)["verdict"],"REJECT")
 def test_issue_without_span_not_cleared(self):
  d={"spans":[{"span_id":"title:0:abc","field":"title","sentence":"A sentence"}],"issues":[{"code":"dropped_qualifier","severity":"review"}],"needs_semantic":[]}
  self.assertEqual(decide(d,{"sentences":[{"span_id":"title:0:abc","verdict":"supported","fact_ids":[],"reason":"ok"}]})["verdict"],"REVIEW")
 def test_short_span_cannot_approve_long_span(self):
  d={"spans":[{"span_id":"title:0:a","field":"title","sentence":"This is a long factual statement"}],"issues":[],"needs_semantic":[{"span_id":"title:0:a"}]}
  row={"span_id":"title:0:short","verdict":"supported","fact_ids":[],"reason":"short"}
  self.assertEqual(decide(d,{"sentences":[row]})["verdict"],"REVIEW")
 def test_duplicate_and_missing_span_rows_review(self):
  d={"spans":[{"span_id":"a"},{"span_id":"b"}],"issues":[],"needs_semantic":[{"span_id":"a"}]}
  row=lambda sid:{"span_id":sid,"verdict":"supported","fact_ids":[],"reason":"ok"}
  self.assertEqual(decide(d,{"sentences":[row("a"),row("a")]})["verdict"],"REVIEW")
  self.assertEqual(decide(d,{"sentences":[row("a")]})["verdict"],"REVIEW")
 def test_deterministic_issue_never_cleared(self):
  d={"spans":[{"span_id":"a"}],"issues":[{"code":"ungrounded_number","span_id":"a","severity":"review"}],"needs_semantic":[]}
  self.assertEqual(decide(d,{"sentences":[{"span_id":"a","verdict":"supported","fact_ids":[],"reason":"ok"}]})["verdict"],"REVIEW")
 def test_reviewer_contradiction_rejects(self):
  d={"spans":[{"span_id":"a"}],"issues":[],"needs_semantic":[]}
  self.assertEqual(decide(d,{"sentences":[{"span_id":"a","verdict":"contradicted","fact_ids":[],"reason":"conflict"}]})["verdict"],"REJECT")
 def test_evidence_missing_detected_per_span(self):
  p=package("Núi An có 3 nguy cơ."); by,missing=relevant_facts(p,{"entities":STORE["entities"],"facts":[]},{"results":[]},spans_for(p))
  self.assertEqual(len(missing),1); self.assertEqual(by[missing[0]],[])
 def test_list_item_topic_mapping(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); (root/"items").mkdir(); (root/"stores").mkdir()
   (root/"items"/"batch.json").write_text(json.dumps([{"topic_id":"topic-a"},{"topic_id":"topic-b"}]))
   for topic in ("topic-a","topic-b"):
    (root/"stores"/(topic+".json")).write_text(json.dumps({"facts":[],"entities":[],"sources":[]}))
    (root/"stores"/(topic+".verification.json")).write_text(json.dumps({"results":[]}))
   from .pipeline import main
   out=root/"out.json"; main(["eval-adversarial",str(root/"items"),"--stores",str(root/"stores"),"--out",str(out)])
   got=json.loads(out.read_text()); self.assertEqual([x["topic_id"] for x in got["items"]],["topic-a","topic-b"])
 def test_codex_jsonl_cumulative_usage_shape(self):
  self.assertEqual(_usage({"type":"event_msg","payload":{"type":"token_count","info":{"total_token_usage":{"input_tokens":9,"output_tokens":2,"total_tokens":11}}}}),11)
  self.assertEqual(_usage({"type":"turn.completed","usage":{"input_tokens":9,"output_tokens":2}}),11)
 def test_semantic_resolvable_requires_own_span_support(self):
  d={"spans":[{"span_id":"a"},{"span_id":"b"}],"issues":[{"code":"dropped_qualifier","severity":"review","span_id":"a"}],"needs_semantic":[]}
  rows=[{"span_id":x,"verdict":"supported","fact_ids":[],"reason":"ok"} for x in ("a","b")]
  self.assertEqual(decide(d,{"sentences":rows})["verdict"],"APPROVED")

if __name__=="__main__": unittest.main()
