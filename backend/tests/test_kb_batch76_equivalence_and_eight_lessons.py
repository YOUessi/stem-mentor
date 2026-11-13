"""Frozen 26 source comparisons, eight independent authored lessons, exact guards and RAG isolation."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch76_equivalence as E
import build_kb_batch76_eight_lessons as L

@pytest.fixture(scope="module")
def comparisons():return E.audit()
@pytest.fixture(scope="module")
def pack():return L.build()

def test_all_generated_outputs_reproducible(comparisons,pack):
 assert E.OUT.read_text(encoding="utf8")==E.canon(comparisons)
 assert E.MD.read_text(encoding="utf8")==E.markdown(comparisons)
 assert L.OUT.read_text(encoding="utf8")==L.canon(pack)
 assert L.MD.read_text(encoding="utf8")==L.markdown(pack)

@pytest.mark.parametrize("i",range(26))
def test_each_candidate_source_and_no_fabricated_equivalence(i,comparisons):
 row=comparisons["cases"][i]
 original={x["id"]:x for x in json.loads(E.MATRIX.read_text(encoding="utf8"))["records"]}[row["source_editorial_subspan_id"]]
 assert row["source_pdf_sha256"]==original["source_pdf_sha256"]
 assert row["source_subspan_sha256"]==original["local_source_subspan_sha256"]
 assert row["source_segment_id"]==original["source_segment_id"]
 assert row["teacher_only"] and not row["student_publishable"]
 assert row["review_status"]=="REVIEW_PENDING"
 assert row["relation_not_teacher_certified"] and not row["mathematical_equivalence_certified"]
 assert row["official_count_contribution"] is None
 assert len(row["mathematical_boundary"])>15
 assert len(row["separating_counterexample"])>14

@pytest.mark.parametrize("track",["COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"])
def test_all_seven_denominators_still_unknown(track,comparisons,pack):
 assert comparisons["official_denominators"][track] is None
 assert pack["official_denominators"][track] is None
 assert comparisons["teacher_full_page_reviews"]==0
 assert comparisons["teacher_approved"]==pack["teacher_approved"]==0
 assert comparisons["student_published"]==pack["student_published"]==0

@pytest.mark.parametrize("field,value",[
 ("source_pdf_sha256","0"*64),("source_subspan_sha256","0"*64),
 ("source_segment_id","FORGED"),("printed_page",1),("track_hint","ELECTIVE_E"),
 ("comparison_existing_draft_id","FORGED"),("proposed_relation","EQUIVALENT_CERTIFIED"),
 ("official_count_contribution",1),("review_status","APPROVED"),
 ("teacher_signature","FAKE"),("mathematical_equivalence_certified",True),
 ("relation_not_teacher_certified",False),("student_publishable",True),("teacher_only",False)])
def test_forged_source_certification_or_release_rejected(field,value,comparisons):
 cloned=deepcopy(comparisons);cloned["cases"][0][field]=value
 with pytest.raises((AssertionError,KeyError)):E.validate(cloned)

@pytest.mark.parametrize("field,value",[
 ("source_editorial_matrix_sha256","0"*64),
 ("previous_review_queue_sha256","0"*64),
 ("source_pdf_sha256","0"*64),
 ("all_26_candidates_audited",False),
 ("student_published",1),("teacher_approved",1),
 ("teacher_full_page_reviews",61)])
def test_audit_header_falsification_rejected(field,value,comparisons):
 cloned=deepcopy(comparisons);cloned[field]=value
 with pytest.raises(AssertionError):E.validate(cloned)

@pytest.mark.parametrize("i",range(8))
def test_new_teacher_draft_full_reasoning_and_bounded_evidence(i,pack):
 r=pack["teacher_drafts"][i]
 assert len(r["worked_examples"])==2 and len(r["reasoning_steps"])>=4
 assert len(r["graduated_hints"])==3
 assert r["counterexample"] and r["common_wrong_method"] and r["invalid_boundary"]
 assert r["teacher_review"]=="REVIEW_PENDING" and r["teacher_signature"] is None
 assert r["mathematical_certification"]=="NOT_FORMALLY_CERTIFIED"
 assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
 assert not r["student_publishable"] and not r["independent_challenge_solution_reveal"]
 assert r["official_atom_count"] is None
 assert L.verify_case(r["finite_case"])

@pytest.mark.parametrize("field,value",[
 ("teacher_review","APPROVED"),("teacher_signature","fake"),
 ("teacher_solution_visibility","STUDENT"),("student_publishable",True),
 ("independent_challenge_solution_reveal",True),
 ("mathematical_certification","FORMALLY_VERIFIED"),
 ("teacher_proof_review","COMPLETED"),("official_atom_count",1),
 ("source_license","UNKNOWN")])
def test_teacher_gate_rejects_forgery(field,value,pack):
 cloned=deepcopy(pack);cloned["teacher_drafts"][0][field]=value
 with pytest.raises(AssertionError):L.validate(cloned)

@pytest.mark.parametrize("i,key,value",[
 (0,"epsilon",[0,1]),(0,"epsilon",[-1,4]),(0,"N",0),(0,"N",4),(0,"N",5.0),
 (1,"center_value",0),(1,"sample_y",[0,4]),(1,"sample_x",[0,2]),
 (2,"power",-1),(2,"a",3),(2,"expected",5),(2,"scale",2.0),
 (3,"cells",[[1,2],[1,2],[1,2],[1,2]]),(3,"rows",[[1,2],[1,4]]),
 (3,"independent",True),(3,"cells",[[1,8],[3,8],[-1,4],[1,4]]),
 (4,"x",[1,1,1]),(4,"y",[1,2]),(4,"slope",5),(4,"x",[0,1.0,2]),
 (5,"a",[1,2]),(5,"expected",[1,1,1]),(5,"a",[1.0,1,0]),
 (6,"t",0),(6,"t",1.0),(6,"expected",[3,1]),
 (7,"lower",[-1,2]),(7,"upper",[2,1]),(7,"expected",[1,2]),(7,"upper",0.5)])
def test_exact_witness_wrong_domain_boundary_and_arithmetic_rejected(i,key,value,pack):
 item=deepcopy(pack["teacher_drafts"][i]["finite_case"]);item[key]=value
 with pytest.raises((AssertionError,ValueError,TypeError,IndexError,ZeroDivisionError)):
  L.verify_case(item)

@pytest.mark.parametrize("numerator,eps,N",[(1,[1,2],3),(2,[1,4],9),(3,[1,5],16),(7,[1,2],15)])
def test_sequence_threshold_finite_guard(numerator,eps,N):
 assert L.verify_case(dict(type="sequence_threshold",numerator=numerator,epsilon=eps,N=N))

@pytest.mark.parametrize("a,b,expected",[(0,1,1),(0,2,4),(-1,1,0),(-2,3,9-4)])
def test_calculus_antiderivative_exact_guard(a,b,expected):
 assert L.verify_case(dict(type="fundamental_calculus",scale=2,power=1,a=a,b=b,expected=expected))

@pytest.mark.parametrize("x,y,slope,intercept",[
 ([0,1,2],[1,3,5],2,1),([1,2,3],[5,5,5],0,5),
 ([0,2,4],[3,5,7],1,3),([1,2,3],[2,4,6],2,0)])
def test_ols_finite_optimum(x,y,slope,intercept):
 assert L.verify_case(dict(type="ols_line",x=x,y=y,slope=slope,intercept=intercept))

@pytest.mark.parametrize("a,b,e",[
 ([1,0,0],[0,1,0],[0,0,1]),
 ([0,1,0],[1,0,0],[0,0,-1]),
 ([1,1,0],[0,1,1],[1,-1,1]),
 ([1,2,3],[2,4,6],[0,0,0])])
def test_cross_product_finite_orthogonality(a,b,e):
 assert L.verify_case(dict(type="cross_product",a=a,b=b,expected=e))

def test_independent_sympy_limited_symbolic_crosscheck():
 sympy=pytest.importorskip("sympy")
 x,t=sympy.symbols("x t",real=True)
 assert sympy.limit(x*x,x,0)==0
 assert sympy.diff(x*x,x)==2*x
 assert sympy.integrate(2*x,(x,0,2))==4
 assert sympy.integrate(2*x,(x,0,sympy.Rational(1,2)))==sympy.Rational(1,4)
 assert sympy.simplify(sympy.diff(t**3,t)/sympy.diff(t**2,t)).subs(t,1)==sympy.Rational(3,2)
 a=sympy.Matrix([1,1,0]);b=sympy.Matrix([0,1,1])
 assert a.cross(b)==sympy.Matrix([1,-1,1])

from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.mark.parametrize("i",range(8))
def test_student_nonempty_approved_index_does_not_leak_new_drafts(i,pack,offline_reviewer_fixture):
 from app.attested_releases import approved_lesson_ids
 from app.deep_retrieval import student_evidence_lookup
 doc,reviewers,_,_,record,save=offline_reviewer_fixture
 save([record(0),record(1)])
 assert approved_lesson_ids()=={doc.id}
 row=pack["teacher_drafts"][i]
 response=student_evidence_lookup(row["title"])
 text=json.dumps(response,ensure_ascii=False)
 assert {entry["knowledge_id"] for entry in response["candidates"]}<={doc.id}
 assert row["id"] not in text
 assert row["worked_examples"][0][1] not in text
 assert row["reasoning_steps"][-1][1] not in text
 assert response["teacher_solution_exposed"] is False
 assert response["unverified_content_exposed"] is False
