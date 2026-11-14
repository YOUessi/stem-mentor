"""KB155 field presence / historical lineage: safety and source integrity tests."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import audit_kb_batch155_draft_readiness as audit
import build_kb_batch155_eight_line_locks as eight

@pytest.fixture(scope="module")
def census():
    j=json.loads(audit.OUT.read_text(encoding="utf-8"))
    assert j==audit.build()
    assert audit.validate(j)
    assert audit.REPORT.read_text(encoding="utf-8")==audit.render(j)
    return j

def test_compact_145_field_presence_is_not_teacher_approval(census):
    assert census["all_drafts_with_full_field_presence"]==145
    assert census["all_pending_manuscripts"]==145
    assert census["legacy_source_lock_shapes"]==6
    assert census["inherited_41_proposal_line_locks"]==35
    assert census["rehashed_eight_missing_line_locks"]==8
    assert census["direct_source_span_shapes"]==96
    assert census["historical_audit_rows_with_null_source_sha"]==41
    assert census["teacher_approved"]==census["student_authoritative"]==0
    assert census["theoretical_proof_certifications"]==0

@pytest.mark.parametrize("i",range(145))
def test_per_draft_carries_fields_provenance_review_status_not_approval(i,census):
    r=census["per_draft_rows"][i]
    assert r["structural_fields_present"]==9
    assert r["reasoned_step_count"]>=4 and r["teacher_example_count"]>=2
    assert r["student_hint_level_count"]>=3
    assert r["near_transfer_present"] and r["far_transfer_present"]
    assert r["teacher_review_status"]=="REVIEW_PENDING"
    assert r["proof_status"]=="NOT_FORMALLY_CERTIFIED"
    assert r["source_semantics_status"]=="PENDING_HUMAN_REVIEW"
    assert len(r["provenance_span_sha256"])==64
    assert r["student_publishable"] is False

@pytest.mark.parametrize("i",range(8))
def test_new_mac_source_hashes_are_frozen_and_unapproved(i):
    saved=json.loads(eight.OUT.read_text(encoding="utf-8"))
    assert eight.validate(saved)
    assert len(saved["locks"])==8
    x=saved["locks"][i]
    assert x["teacher_review"]=="REVIEW_PENDING"
    assert not x["formal_general_proof_certified"]
    assert not x["student_authoritative"]
    assert len(x["source_line_sha256"])==x["end_line"]-x["start_line"]+1
    assert all(len(h)==64 for h in x["source_line_sha256"])

@pytest.mark.parametrize("field,bad",[
    ("all_pending_manuscripts",144),
    ("all_drafts_with_full_field_presence",144),
    ("inherited_41_proposal_line_locks",34),
    ("rehashed_eight_missing_line_locks",7),
    ("theoretical_proof_certifications",1),
    ("teacher_approved",1),
    ("student_authoritative",1),
    ("teacher_review_complete",True),
    ("completeness_meaning","FULLY_MATH_CERTIFIED"),
])
def test_shallow_presence_cannot_be_promoted_to_teacher_approval(field,bad,census):
    c=copy.deepcopy(census);c[field]=bad
    with pytest.raises(ValueError):audit.validate(c)

@pytest.mark.parametrize("field,bad",[
    ("teacher_review_status","APPROVED"),
    ("proof_status","GENERAL_THEOREM_PROVED"),
    ("source_semantics_status","HUMAN_APPROVED"),
    ("student_publishable",True),
    ("provenance_span_sha256","0"),
    ("reasoned_step_count",0),
    ("teacher_example_count",0),
    ("student_hint_level_count",0),
])
def test_individual_manuscript_forged_fields_rejected(field,bad,census):
    c=copy.deepcopy(census);c["per_draft_rows"][23][field]=bad
    with pytest.raises(ValueError):audit.validate(c)


def test_forged_precise_original_pdf_line_hash_is_detected_offline():
    x=json.loads(eight.OUT.read_text(encoding="utf-8"))
    x["locks"][0]["source_line_sha256"][0]="0"*64
    with pytest.raises(ValueError,match="altered"):
        eight.validate(x)
