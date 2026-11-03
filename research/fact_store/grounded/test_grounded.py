import unittest
from .check import det_check
from .pipeline import decide

STORE={"sources":[{"source_id":"s1","publisher":"Viện Dữ liệu"}],"entities":[{"entity_id":"e1","name":"Núi An","aliases":["An"]}],"facts":[
 {"fact_id":"f1","subject":"e1","predicate":"height","quantity":{"value":100,"unit":"m"},"time":{"start":"2020"},"qualifiers":{},"evidence":[{"source_id":"s1"}]},
 {"fact_id":"f2","subject":"e1","predicate":"height","quantity":{"value":100,"unit":"m"},"time":{"start":"2020"},"qualifiers":{"modality":"legendary","condition":"theo truyện"},"evidence":[{"source_id":"s1"}]},
 {"fact_id":"f3","subject":"e1","predicate":"height","quantity":{"value":150,"unit":"m"},"time":{"start":"2020"},"qualifiers":{"attributed_to":"e1"},"evidence":[{"source_id":"s1"}]},
]}
VER={"results":[{"fact_id":"f1","status":"verified"},{"fact_id":"f2","status":"verified"},{"fact_id":"f3","status":"disputed"}]}
def package(text, claims=None):
 return {"title":text,"claims":claims or [],"thumbnail_text":"","first_frame_0_1s":"","voice_0_3s":"","escalation_3_10s":"","payoff":""}

class GroundedTests(unittest.TestCase):
 def test_year_word_not_quantity_but_duration_is(self):
  from .check import _numbers
  self.assertEqual(list(_numbers("năm 2019")),[(2019.0,"","2019")])
  self.assertEqual(list(_numbers("16 năm")),[(16.0,"năm","16 năm")])
 def test_evidence_text_grounds_number(self):
  store={"facts":[{"fact_id":"date","statement_vi":"Sự kiện diễn ra năm 1909","evidence":[{"span":"1909"}]}]}
  ver={"results":[{"fact_id":"date","status":"verified"}]}
  d=det_check(package("Sự kiện năm 1909"),store,ver)
  self.assertFalse(any(i.get("code")=="ungrounded_number" and "1909" in i.get("token","") for i in d["issues"]))
 def test_duration_grounded_by_quantity(self):
  store={"facts":[{"fact_id":"duration","quantity":{"value":16,"unit":"năm"}}]}
  ver={"results":[{"fact_id":"duration","status":"verified"}]}
  d=det_check(package("kéo dài 16 năm"),store,ver)
  self.assertFalse(any(i.get("code")=="ungrounded_number" for i in d["issues"]))
 def test_wrong_number_reject(self):
  store={**STORE,"facts":[{**f,"predicate":"cao","time":{"start":"2020"}} if f["fact_id"]=="f1" else f for f in STORE["facts"]]}
  d=det_check(package("Núi An cao 400 m năm 2020",[{"field":"title","span":"Núi An cao 400 m năm 2020","kind":"factual","fact_ids":["f1"]}]),store,VER)
  self.assertEqual(d["verdict_hint"],"REJECT")
 def test_rounding(self):
  d=det_check(package("Núi An cao khoảng 104 m"),STORE,VER)
  self.assertFalse(any(i["code"]=="ungrounded_number" for i in d["issues"]))
 def test_outside_name_review(self):
  d=det_check(package("Bình Sơn"),STORE,VER)
  self.assertEqual(d["verdict_hint"],"REVIEW")
 def test_disputed_attribution(self):
  d=det_check(package("Theo Viện Dữ liệu, Núi An cao 150 m",[{"field":"title","span":"Theo Viện Dữ liệu, Núi An cao 150 m","kind":"factual","fact_ids":["f3"]}]),STORE,VER)
  self.assertFalse(any(i["code"]=="unattributed_disputed" for i in d["issues"]))
 def test_unverified_reference_review(self):
  v={"results":[{"fact_id":"f1","status":"unverified"}]}
  d=det_check(package("Núi An cao 100 m",[{"field":"title","span":"Núi An cao 100 m","kind":"factual","fact_ids":["f1"]}]),STORE,v)
  self.assertIn("unverified_ref",[i["code"] for i in d["issues"]])
 def test_causal_needs_semantic(self):
  d=det_check(package("Vì vậy Núi An đổi khác.",[{"field":"title","span":"Vì vậy Núi An đổi khác.","kind":"factual","fact_ids":[]}]),STORE,VER)
  self.assertTrue(d["needs_semantic"])
 def test_det_only_approve(self):
  d=det_check(package("Núi An cao 100 m.",[{"field":"title","span":"Núi An cao 100 m.","kind":"factual","fact_ids":["f1"]}]),STORE,VER)
  self.assertEqual(d["verdict_hint"],"APPROVED")
  self.assertEqual(decide(d)["verdict"],"APPROVED")
 def test_review_decisions(self):
  d={"issues":[],"needs_semantic":[{"field":"title","span":"x"}]}
  self.assertEqual(decide(d,{"sentences":[{"field":"title","span":"x","verdict":"contradicted"}]})["verdict"],"REJECT")
  self.assertEqual(decide(d,{"sentences":[{"field":"title","span":"x","verdict":"needs_review"}]})["verdict"],"REVIEW")

if __name__=="__main__": unittest.main()
