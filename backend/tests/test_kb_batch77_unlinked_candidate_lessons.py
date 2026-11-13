"""Batch77 authored mathematics, source gate, bounded exact witnesses, RAG isolation."""
from __future__ import annotations
from copy import deepcopy
import json,sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch77_missing_lessons as B

@pytest.fixture(scope="module")
def pack():return B.build()

def test_reproducible_files_and_local_denominator(pack):
    assert B.OUT.read_text(encoding="utf8")==B.canonical(pack)
    assert B.MD.read_text(encoding="utf8")==B.markdown(pack)
    assert pack["local_denominator"]==26
    assert pack["local_candidates_with_drafts"]==26
    assert pack["remaining_local_candidates_without_drafts"]==0
    assert pack["new_review_only_drafts"]==11
    assert pack["teacher_full_page_reviews"]==0
    assert pack["teacher_approvals"]==pack["student_publications"]==pack["formal_math_certifications"]==0
    assert all(v is None for v in pack["official_denominators"].values())

@pytest.mark.parametrize("idx",range(11))
def test_all_eleven_real_source_links_full_draft_not_approved(idx,pack):
    r=pack["teacher_drafts"][idx]
    assert r["source_editorial_subspan_id"] in B.LINKS
    assert B.LINKS[r["source_editorial_subspan_id"]]["linked_teacher_draft_count"]==0
    assert r["source_subspan_sha256"]==B.LINKS[r["source_editorial_subspan_id"]]["source_sha256"]
    assert r["curriculum_track_hint"]==B.LINKS[r["source_editorial_subspan_id"]]["track_hint"]
    assert len(r["reasoning_steps"])>=4
    assert len(r["worked_examples"])==2 and len(r["graduated_hints"])==3
    assert r["counterexample"] and r["common_wrong_method"] and r["invalid_boundary"]
    assert r["teacher_review"]=="REVIEW_PENDING" and r["teacher_signature"] is None
    assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert r["mathematical_certification"]=="NOT_FORMALLY_CERTIFIED"
    assert not r["student_publishable"] and not r["independent_challenge_solution_reveal"]
    assert r["official_atom_count"] is None
    assert B.case_check(r["finite_case"])

@pytest.mark.parametrize("idx",range(26))
def test_exactly_one_local_candidate_lineage_without_fake_official_count(idx,pack):
    r=pack["candidates"][idx]
    assert r["review_only_teacher_draft_ids"]
    assert r["review_only_teacher_draft_count"]==len(r["review_only_teacher_draft_ids"])
    assert r["official_atom_id"] is None
    assert r["teacher_review"]=="REVIEW_PENDING" and not r["teacher_approved"]
    assert not r["source_certified"] and not r["student_publishable"]

@pytest.mark.parametrize("track",["COMPULSORY","SELECTIVE_COMPULSORY",
                                  "ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"])
def test_unknown_seven_track_denominators(track,pack):
    assert pack["by_track"][track]["official_denominator"] is None
    assert pack["official_denominators"][track] is None

@pytest.mark.parametrize("field,value",[
    ("teacher_review","APPROVED"),("teacher_signature","fake teacher"),
    ("teacher_solution_visibility","STUDENT"),("student_publishable",True),
    ("independent_challenge_solution_reveal",True),
    ("mathematical_certification","FORMALLY_CERTIFIED"),
    ("teacher_proof_review","COMPLETED"),("official_atom_count",1),
    ("source_subspan_sha256","0"*64),("source_license","COPYRIGHTED_TEXT"),
    ("prerequisite_ids_confirmed",True)])
def test_false_approval_math_certification_and_source_tamper_rejected(field,value,pack):
    invalid=deepcopy(pack);invalid["teacher_drafts"][0][field]=value
    with pytest.raises((AssertionError,ValueError)):
        B.validate(invalid)

@pytest.mark.parametrize("field,value",[
    ("local_denominator",2000),("local_candidates_with_drafts",0),
    ("remaining_local_candidates_without_drafts",1),
    ("teacher_approvals",11),("student_publications",11),
    ("formal_math_certifications",11),("teacher_full_page_reviews",61),
    ("source_queue_sha256","0"*64),("prior_local_coverage_sha256","0"*64)])
def test_header_falsification_rejected(field,value,pack):
    altered=deepcopy(pack);altered[field]=value
    with pytest.raises(AssertionError):B.validate(altered)

@pytest.mark.parametrize("idx,key,bad",[
 (0,"truths",[True,True,True]),(0,"forall",True),(0,"exists_not",False),
 (1,"reflected",[2,3]),(1,"rotated",[-2,3]),(1,"x",2.0),
 (2,"positive",[2,1,0]),(2,"negative",[0,1,2]),(2,"x",[0,0,0]),
 (3,"sigma",0),(3,"sigma",2.0),(3,"z",2),(3,"data",[1,1,3]),
 (4,"power",-1),(4,"point",1),(4,"integral",[1,2]),
 (5,"A",[[1,0],[2,0],[3,0]]),(5,"b",[2,3,6]),
 (5,"inconsistent_b",[2,3,5]),(5,"x",[3,2]),
 (6,"top",[5,4]),(6,"expected",[1,4]),(6,"left",0.5),
 (7,"assignments",[0,0,0,0]),(7,"points",[[0,0],[0,1],[0,0],[0,5]]),
 (7,"expected",2),(7,"assignments",[0,0,1,1.0]),
 (8,"xs",[0,0,2]),(8,"k",0),(8,"q",9),(8,"query",1),
 (9,"base",1),(9,"T",0),(9,"shifted",1),(9,"base",2.0),
 (10,"units",["元","元/件","元","件"]),(10,"quantity",9),
 (10,"price",5),(10,"below_profit",0),(10,"fixed",30.0)])
def test_exact_witness_malformed_domain_or_arithmetic_rejected(idx,key,bad,pack):
    invalid=deepcopy(pack["teacher_drafts"][idx]["finite_case"])
    invalid[key]=bad
    with pytest.raises((AssertionError,ValueError,TypeError,ZeroDivisionError,IndexError)):
        B.case_check(invalid)

def test_independent_sympy_spot_crosscheck():
    s=pytest.importorskip("sympy")
    x,t=s.symbols("x t",real=True)
    assert s.diff(x**3,x).subs(x,2)==12
    assert s.integrate(x**3,(x,0,2))==4
    assert s.integrate(4*x*t,(x,0,s.Rational(1,2)),(t,0,s.Rational(1,2)))==s.Rational(1,16)
    assert s.expand((x**2+x*(x-1)*(x-2))-x**2).subs(x,3)==6
    A=s.Matrix([[1,0],[0,1],[1,1]])
    assert A.rank()==2 and A*s.Matrix([2,3])==s.Matrix([2,3,5])
    assert s.simplify(s.sin(t+2*s.pi)-s.sin(t))==0

from test_attested_release_batch08 import offline_reviewer_fixture
@pytest.mark.parametrize("idx",range(11))
def test_student_search_nonempty_approved_index_does_not_include_teacher_draft(idx,pack,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    row=pack["teacher_drafts"][idx]
    response=student_evidence_lookup(row["title"])
    dumped=json.dumps(response,ensure_ascii=False)
    assert {x["knowledge_id"] for x in response["candidates"]}<={doc.id}
    assert row["id"] not in dumped
    assert row["worked_examples"][0][1] not in dumped
    assert row["reasoning_steps"][-1][1] not in dumped
    assert response["teacher_solution_exposed"] is False
    assert response["unverified_content_exposed"] is False
