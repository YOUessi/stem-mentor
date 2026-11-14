"""K00 historical candidate alias and official-denominator negative regression."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import audit_kb_batch146_source_aliases as alias

@pytest.fixture(scope="module")
def report():
    return json.loads(alias.OUT.read_text(encoding="utf-8"))

def test_report_generated_from_frozen_historical_source(report):
    assert report==alias.audit()
    assert alias.REPORT.read_text(encoding="utf-8")==alias.render(report)
    assert report["historical_editorial_candidate_count"]==239
    assert report["shared_source_span_group_count"]==7
    assert report["candidate_count_in_shared_source_span_groups"]==19
    assert report["shared_cue_group_count"]==17
    assert report["cross_page_shared_cue_group_count"]==0
    assert not any(g["cross_page_evidence"] for g in report["shared_cue_review_groups"])
    assert report["source_cue_memberships_with_shared_marker"]==40
    assert report["source_aliases_auto_merged"]==0
    assert report["human_approved_semantic_merges"]==0
    assert report["teacher_approved"]==report["student_authoritative"]==0

@pytest.mark.parametrize("i",range(7))
def test_same_span_does_not_imply_semantic_equivalence(i,report):
    group=report["exact_span_review_groups"][i]
    assert len(group["candidate_ids"])>=2
    assert group["human_review_status"]=="REVIEW_PENDING"
    assert group["semantic_merge_decision"]=="UNDECIDED"
    assert group["source_span_sha256"]
    assert all(x.startswith("hs-semantic-pilot-") for x in group["candidate_ids"])

@pytest.mark.parametrize("i",range(17))
def test_shared_layout_cue_not_approved_atom(i,report):
    group=report["shared_cue_review_groups"][i]
    assert len(group["candidate_ids"])>=2
    assert group["semantic_merge_decision"]=="UNDECIDED"

@pytest.mark.parametrize("track",[
    "COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
    "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"
])
def test_no_track_can_claim_national_official_denominator(track,report):
    assert report["by_track"][track]["official_atom_denominator"] is None
    assert report["official_seven_track_atom_denominators"][track] is None
    assert report["by_track"][track]["missing_official_review"]
    assert report["by_track"][track]["teacher_approved"]==0

@pytest.mark.parametrize("field,bad",[
    ("official_census_complete",True),("source_aliases_auto_merged",7),
    ("human_approved_semantic_merges",7),("teacher_approved",19),
    ("student_authoritative",239),("shared_source_span_group_count",0),
    ("shared_cue_group_count",0),("official_seven_track_atom_denominators",{"COMPULSORY":113}),
])
def test_forged_alias_or_curriculum_claim_does_not_match_audit(field,bad,report):
    altered=copy.deepcopy(report);altered[field]=bad
    assert altered!=alias.audit()

@pytest.mark.parametrize("field,bad",[
    ("teacher_approved",True),("needs_human_semantic_check",False),
    ("student_authoritative",True),("official_atom_id","fake-national-id")
])
def test_forged_source_approval_does_not_pass_fresh_audit(tmp_path,monkeypatch,field,bad):
    x=json.loads(alias.SOURCE.read_text(encoding="utf-8"))
    x["records"][0][field]=bad
    fake=tmp_path/"forged.json"
    fake.write_text(json.dumps(x,ensure_ascii=False),encoding="utf-8")
    monkeypatch.setattr(alias,"SOURCE",fake)
    with pytest.raises(ValueError,match="falsified approval"):
        alias.audit()
