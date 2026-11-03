from research.narrative.fact_gate import extract_claims, match, gate
from research.narrative.fact_gate.core import _norm_number

def test_vietnamese_numeric_formats():
    texts=[c.text for c in extract_claims("1,5 tỷ USD; 3.147,3 m; 47,67%; 2025")]
    assert any("1,5 tỷ" in x for x in texts)
    assert any("3.147,3" in x for x in texts)
    assert any("47,67%" in x for x in texts)

def test_number_and_date_match():
    facts=[{"fact_id":"x","value":"3.147,3 m; 21/02/2025","statement":"Đo đạt", "source_url":"u","certainty":"verified"}]
    topic={"slug":"fansipan"}
    facts[0]["statement"] += " Fansipan"
    assert match("Fansipan cao 3.147,3 m",facts,topic=topic).fact_id=="x"
    assert match("Fansipan năm 21/02/2025",facts,topic=topic).match_kind=="date"

def test_bybit_wrong_compromised_entity_rejected_and_loss_passes():
    facts=[{"fact_id":"F1","value":"1,5 tỷ USD","statement":"Bybit mất tài sản","certainty":"verified","source_url":"u"},
           {"fact_id":"F2","value":"04/02/2025","statement":"Safe{Wallet} bị xâm nhập","certainty":"verified","source_url":"u"}]
    topic={"entity_roles":{"compromised_system":"Safe{Wallet}: service","harmed_org":"Bybit"},"fact_table":facts}
    bad=gate({"title":"Bybit bị hack","thumbnail_text":"","voice_0_3s":"","escalation_3_10s":""},topic)
    assert bad["verdict"]=="REJECT"
    good=gate({"title":"Bybit mất 1,5 tỷ USD","thumbnail_text":"","voice_0_3s":"","escalation_3_10s":""},topic)
    assert good["verdict"]=="PASS"

def test_contested_title_rejected_and_qualitative_review():
    topic={"fact_table":[{"fact_id":"f","value":"1990/1991","statement":"Ngày phát hiện","certainty":"contested","source_url":"u"}]}
    assert gate({"title":"Phát hiện năm 1991","thumbnail_text":"","voice_0_3s":"","escalation_3_10s":""},topic)["verdict"]=="REVIEW"
    assert gate({"title":"Một câu chuyện kỳ lạ","thumbnail_text":"","voice_0_3s":"","escalation_3_10s":""},topic)["verdict"]=="REVIEW"

def test_money_promise_rejected():
    result=gate({"title":"Giữ vàng có lãi chắc chắn","thumbnail_text":"","voice_0_3s":"","escalation_3_10s":""},{"fact_table":[]})
    assert result["verdict"]=="REJECT"

def test_unrelated_fact_same_number_does_not_pass():
    facts=[{"fact_id":"x","statement":"Núi khác cao 4,3 m","value":"4,3 m","certainty":"verified"}]
    topic={"slug":"fansipan","fact_table":facts}
    result=gate({"title":"Fansipan cao 4,3 m","thumbnail_text":"","voice_0_3s":"","escalation_3_10s":""},topic)
    assert result["verdict"]=="REVIEW"

def test_declared_claim_alone_is_review():
    topic={"slug":"fansipan","fact_table":[{"fact_id":"x","statement":"Other mountain is 4,3 m","value":"4,3 m","certainty":"verified"}]}
    level={"title":"Fansipan cao 4,3 m","thumbnail_text":"","voice_0_3s":"","escalation_3_10s":"","claims":[{"text":"Fansipan cao 4,3 m","fact_id":"x"}]}
    assert gate(level,topic)["verdict"]=="REVIEW"

def test_fansipan_growth_claim_is_review():
    topic={"slug":"fansipan","fact_table":[{"fact_id":"f","statement":"Hai con số chênh 4,3 m; không khẳng định núi cao thêm","value":"4,3 m","certainty":"verified"}]}
    result=gate({"title":"Fansipan cao thêm 4,3 m","thumbnail_text":"","voice_0_3s":"","escalation_3_10s":""},topic)
    assert result["verdict"]=="REVIEW"

def test_unit_mismatch_is_review():
    topic={"slug":"fansipan","fact_table":[{"fact_id":"f","statement":"Fansipan cao 4,3 năm","value":"4,3 năm","certainty":"verified"}]}
    result=gate({"title":"Fansipan cao 4,3 m","thumbnail_text":"","voice_0_3s":"","escalation_3_10s":""},topic)
    assert result["verdict"]=="REVIEW"

def test_spoken_vietnamese_numbers_parse():
    assert _norm_number("hai nghìn không trăm mười chín") == 2019
    assert _norm_number("ba nghìn một trăm bốn mươi bảy phẩy ba") == 3147.3

def test_bybit_relations_compare_roles():
    facts=[{"fact_id":"x","certainty":"verified","relations":[["Bybit","lost_asset","1,5 tỷ USD"]]}]
    topic={"entity_roles":{"harmed_org":"Bybit","compromised_system":"Safe{Wallet}: system"},"fact_table":facts}
    assert gate({"title":"Bybit mất 1,5 tỷ USD","thumbnail_text":"","voice_0_3s":"","escalation_3_10s":""},topic)["verdict"]=="PASS"
    assert gate({"title":"Bybit bị hack","thumbnail_text":"","voice_0_3s":"","escalation_3_10s":""},topic)["verdict"]=="REJECT"
