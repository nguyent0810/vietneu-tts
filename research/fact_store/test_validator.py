import hashlib, json
from pathlib import Path
import pytest
from research.fact_store import _norm, span_match, validate_store, compute_verification

BASE=Path(__file__).parent

def _store():
    return {"schema_version":"0.2","topic_id":"demo","sources":[{"source_id":"s1","url":"x","kind":"press","publisher":"A","snapshot_sha256":""}],"entities":[{"entity_id":"e","name":"E","type":"place"}],"facts":[{"fact_id":"f1","kind":"assertion","subject":"e","predicate":"measured_as","quantity":{"measure":"height","value":1,"unit":"m"},"evidence":[{"source_id":"s1","span":"A sufficiently long span"}],"qualifiers":{"negated":False,"modality":"asserted"},"extraction":{"by":"model-a","at":"2026-01-01T00:00:00Z","prompt_version":"v1"}}]}

def test_span_normalizes_unicode_quotes_whitespace(tmp_path):
    text='He said “A sufficiently\nlong span” here.'
    p=tmp_path/'s1.txt'; p.write_text(text,encoding='utf8')
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    (tmp_path/'sources_index.json').write_text(json.dumps([{"source_id":"s1","snapshot_path":"s1.txt","snapshot_sha256":h}]))
    f={"evidence":[{"source_id":"s1","span":"A sufficiently long span"}]}
    assert span_match(f,tmp_path)[0]["result"]=="supports"
    assert _norm('e\u0301  x')=='é x'

def test_sha_mismatch_is_not_found(tmp_path):
    (tmp_path/'s1.txt').write_text('A sufficiently long span')
    (tmp_path/'sources_index.json').write_text(json.dumps([{"source_id":"s1","snapshot_path":"s1.txt","snapshot_sha256":"bad"}]))
    assert span_match({"evidence":[{"source_id":"s1","span":"A sufficiently long span"}]},tmp_path)[0]["result"]=="not_found"

def test_rejects_llm_self_verification():
    s=_store()
    with pytest.raises(ValueError,match="must differ"):
        compute_verification(s,[{"fact_id":"f1","method":"independent_llm","result":"supports","model":"model-a","extraction_model":"model-a","prompt_sha256":"x","at":"now"}])

def test_rejects_mismatched_extraction_model():
    s=_store()
    with pytest.raises(ValueError,match="extraction_model must equal"):
        compute_verification(s,[{"fact_id":"f1","method":"independent_llm","result":"supports","model":"model-b","extraction_model":"wrong","prompt_sha256":"x","at":"now"}])

def test_fansipan_comparable_group_not_contested():
    s=_store(); f=s['facts'][0]; f['comparable_group']='height'; f['quantity']['measure']='height'
    g={**f,'fact_id':'f2','time':{'start':'2019','granularity':'year'}}; s['facts'].append(g)
    out=compute_verification(s)
    assert {r['certainty'] for r in out['results']}=={'unknown'}

def test_variant_group_contested():
    s=_store(); f=s['facts'][0]; f['variant_group']='v'
    g={**f,'fact_id':'f2'}; s['facts'].append(g)
    out=compute_verification(s)
    assert {r['certainty'] for r in out['results']}=={'contested'}

def test_legend_missing_edition_and_bad_predicate():
    s=_store(); f=s['facts'][0]; f['kind']='legend'; f['predicate']='no_such_predicate'; f['qualifiers']['modality']='legendary'
    errs=validate_store(s)
    assert any('according_to_edition' in e for e in errs)
    assert any('unknown predicate' in e for e in errs)
