"""Batch115 source/lesson gating: editorial atoms remain nonauthoritative."""
import json,sys
from copy import deepcopy
from pathlib import Path
import pytest
from pydantic import ValidationError
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
import build_kb_batch115 as B
from kb_batch115_source import CANDIDATES,PARTITIONS
from kb_batch115_lessons import UNITS
from app.deep_knowledge import DeepLesson,lessons
from app.deep_retrieval import student_evidence_lookup,editor_draft_search,EditorOnlyError

@pytest.fixture(scope="module")
def built():
    s=B.source();d,a=B.lessons(scope=s);c=B.coverage(scope=s,ds=d)
    return s,d,a,c

def test_file_locks_and_source_page_denominator(built):
    s,_,_,c=built
    assert s["pages"]==[25,26,62,63] and s["line_counts"]=={"25":25,"26":29,"62":25,"63":23}
    assert s["source_lines_total"]==102 and s["editorial_candidate_count"]==24
    assert s["finite_exact_witnesses"]==8
    assert s["candidate_counts_by_track"]==dict(zip(B.TRACKS,(13,0,0,11,0,0,0)))
    assert c["source_structure_candidate_reviewed_pages"]==18
    assert len(c["source_structure_unreviewed_pages"])==43
    assert c["official_source_pdf_pages"]==61
    assert c["teacher_verified_atomized_pages"]==0
    assert all(z is None for z in c["seven_track_official_atom_denominator"].values())
    assert all(z is None for z in c["seven_track_certified_coverage"].values())
    assert all(p["official_math_atoms"] is None for p in c["per_page_denominator_status"])
    assert all(not p["teacher_verified_atomization"] for p in c["per_page_denominator_status"])

def test_immutable_local_source_when_present():
    if not B.PDF.is_file():pytest.skip("pinned source available only on Mac")
    s=B.source(verify_local_source=True)
    assert s["source_lines_total"]==102

@pytest.mark.parametrize("i",range(24))
def test_source_not_teacher_or_formally_proved(built,i):
    r=built[0]["candidates"][i]
    assert r["source_pdf_sha256"]==B.PDF_SHA
    assert r["official_atom_id"] is None and r["teacher_reviewer"] is None
    assert r["review_status"]=="REVIEW_PENDING"
    assert r["student_authoritative_release"] is False
    assert not r["math_witness"]["general_proof_certified"]
    assert r["math_witness"]==B.witness(r["key"])

@pytest.mark.parametrize("which",[
 "duplicate","page_shift","line_shift","kind_shift","fake_approval","fake_proof",
 "fake_teacher","fake_atom","missing_partition","overlap_partition","footnote_gap",
 "foreign_track_field","thin_precondition","invented_key","bad_kind","wrong_length"])
def test_bad_source_rejected(which):
    rows=deepcopy(CANDIDATES);parts=deepcopy(PARTITIONS)
    if which=="duplicate":rows[1]["key"]=rows[0]["key"]
    elif which=="page_shift":rows[0]["page"]=74
    elif which=="line_shift":rows[0]["start"]=5
    elif which=="kind_shift":rows[0]["kind"]="PEDAGOGY"
    elif which=="fake_approval":rows[0]["review_status"]="APPROVED"
    elif which=="fake_proof":rows[0]["general_proof_certified"]=True
    elif which=="fake_teacher":rows[0]["teacher_reviewer"]="fictional"
    elif which=="fake_atom":rows[0]["official_atom_id"]="madeup"
    elif which=="missing_partition":parts[25][0]=(2,3,"FUNCTION_ACHIEVEMENT_CONTINUED")
    elif which=="overlap_partition":parts[63][1]=(8,16,"LINEAR_MODELS")
    elif which=="footnote_gap":parts[62][-1]=(24,24,"FOOTER")
    elif which=="foreign_track_field":rows[0]["track_hint"]="ELECTIVE_E"
    elif which=="thin_precondition":rows[0]["mathematical_preconditions"]="bad"
    elif which=="invented_key":rows[0]["key"]="spoof"
    elif which=="bad_kind":rows[0]["kind"]="REVIEWED_THEOREM"
    elif which=="wrong_length":rows.pop()
    with pytest.raises((ValueError,KeyError,TypeError)):B.source(rows,parts)

@pytest.mark.parametrize("i",range(8))
def test_deep_unit_complete_not_approved(built,i):
    d=built[1][i]
    m=DeepLesson.model_validate(d)
    assert m.review.status=="REVIEW_PENDING" and m.review.reviewer_id is None
    assert m.teacher_solution_visibility=="TEACHER_ONLY"
    assert len(m.worked_examples)==2 and len(m.hint_ladder)==3
    assert len(m.counterexamples)==1 and len(m.misconceptions)==1
    assert m.transfer.near and m.transfer.far
    assert m.provenance.permission=="PROJECT_AUTHORED"
    assert m.id==f"math.hs.batch115.{i+1:02d}"
    if m.kind=="theorem":assert len(m.proof_steps)==3 and not m.rationale_steps
    else:assert len(m.rationale_steps)==3 and not m.proof_steps

@pytest.mark.parametrize("i",range(8))
def test_fake_review_strictly_refused(built,i):
    d=deepcopy(built[1][i])
    d["review"]={"status":"APPROVED","reviewer_id":"fabricated",
                 "reviewed_at":"2026-11-13","review_record":"fabricated"}
    with pytest.raises(ValidationError):DeepLesson.model_validate(d)

@pytest.mark.parametrize("i",range(8))
def test_fake_student_visibility_refused(built,i):
    d=deepcopy(built[1][i])
    d["teacher_solution_visibility"]="STUDENT_VISIBLE"
    with pytest.raises(ValidationError):DeepLesson.model_validate(d)

@pytest.mark.parametrize("i",range(8))
def test_author_input_truncation_refused(built,i):
    u=deepcopy(UNITS);u[i]["statement"]="too short"
    with pytest.raises(ValueError):B.lessons(units=u,scope=built[0])

@pytest.mark.parametrize("i",range(8))
def test_source_track_forgery_refused(built,i):
    sc=deepcopy(built[0])
    key=UNITS[i]["source_key"]
    next(r for r in sc["candidates"] if r["key"]==key)["track_hint"]="ELECTIVE_E"
    with pytest.raises(ValueError):B.lessons(scope=sc)

@pytest.mark.parametrize("i",range(8))
def test_student_no_teacher_solution_leak(built,i):
    d=built[1][i]
    r=student_evidence_lookup(d["title"])
    assert r["status"]=="NO_APPROVED_EVIDENCE"
    assert not r["teacher_solution_exposed"]
    s=json.dumps(r,ensure_ascii=False)
    for e in d["worked_examples"]:
        assert e["answer"] not in s and e["check"] not in s

def test_editor_gate_and_local_discovery():
    with pytest.raises(EditorOnlyError):
        editor_draft_search("非零平面向量垂直")
    results=editor_draft_search("非零平面向量垂直",scope="EDITOR_LOCAL")
    assert any(hit["knowledge_id"]=="math.hs.batch115.04" for hit in results)
    assert all("worked_examples" not in hit for hit in results)

def test_generated_files_and_census(built):
    s,d,a,c=built
    assert json.loads(B.SCOPE.read_text())==s
    assert json.loads(B.PACK.read_text())==d
    assert json.loads(B.AUDIT.read_text())==a
    assert json.loads(B.COVER.read_text())==c
    assert a["prior_deep_drafts"]==482 and a["total_deep_drafts"]==490
    assert a["new_deep_drafts"]==8 and a["new_teacher_worked_examples"]==16
    assert a["new_hint_levels"]==24 and a["new_counterexamples"]==8
    assert a["new_uncertified_proof_steps"]==9
    assert a["teacher_approvals"]==a["formal_proof_certificates"]==0
    all_ids=[x.id for x in lessons()]
    assert len(all_ids)==len(set(all_ids)) and all(f"math.hs.batch115.{i:02d}" in all_ids for i in range(1,9))
