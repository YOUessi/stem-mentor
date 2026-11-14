"""K00 source boundary triage cannot silently certify/de-duplicate official atoms."""
import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import audit_kb_batch147_source_edges as a
@pytest.fixture(scope="module")
def audit():
    return a.make()
def test_hash_locked_complete_replay(audit):
    assert json.loads(a.OUT.read_text(encoding="utf-8"))==audit
    assert a.REPORT.read_text(encoding="utf-8")==a.render(audit)
    assert len(audit["candidates"])==239
    assert len({x["id"] for x in audit["candidates"]})==239
    assert audit["linked_leads"]==54 and audit["unmatched_leads"]==185
    assert audit["teacher_pending_manuscripts"]==95
@pytest.mark.parametrize("track",["COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"])
def test_all_seven_track_denominators_unknown(track,audit):
    t=audit["by_track"][track]
    assert t["source_leads"]==t["manuscript_linked"]+t["manuscript_missing"]
    assert t["official_atom_denominator"] is None
    assert t["teacher_approved"]==t["student_authoritative"]==0
@pytest.mark.parametrize("field,value",[
    ("official_atom_census_completed",True),
    ("automatically_merged_atoms",1),("teacher_approved_atoms",1),
    ("student_authoritative_atoms",1),("official_denominators",{"COMPULSORY":239}),
    ("linked_leads",239),("unmatched_leads",0)])
def test_false_official_coverage_would_drift(field,value,audit):
    changed=copy.deepcopy(audit);changed[field]=value
    assert changed!=a.make()
def test_edges_never_auto_certify(audit):
    assert all(e["human_decision"]=="REVIEW_PENDING" and
        e["semantic_equivalence"]=="UNDETERMINED" and
        not e["auto_merge_allowed"] for e in audit["candidate_relation_edges"])
    assert all(not c["teacher_approved"] and c["official_atom_id"] is None for c in audit["candidates"])
def test_original_metadata_without_copyright_body(audit):
    assert all("raw_text" not in c and "source_pdf_text" not in c for c in audit["candidates"])
    assert all(len(c["span_sha"])==64 for c in audit["candidates"])
    assert all(c["start"]<=c["end"] for c in audit["candidates"])
