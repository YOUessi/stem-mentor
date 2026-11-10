"""Source-line evidence, math premise negatives, and teacher-only retrieval gates."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction as F
import json
import os
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch75_clause_splits as C
import build_kb_batch75_lessons as L

@pytest.fixture(scope="module")
def corpus():return C.build(C.B73.load(C.WITNESS))[0]

@pytest.fixture(scope="module")
def drafts():return L.build()

def test_frozen_generated_artifacts_reproducible(corpus,drafts):
 c,m=C.build(C.B73.load(C.WITNESS))
 assert C.OUT.read_text(encoding="utf8")==C.canon(c)
 assert C.MD.read_text(encoding="utf8")==m
 assert L.OUT.read_text(encoding="utf8")==L.canon(drafts)
 assert L.REPORT.read_text(encoding="utf8")==L.report(drafts)

def test_real_mac_pdfkit_subspan_sha_verification():
 if os.getenv("KB75_VERIFY_MAC_SOURCE")!="1":
  pytest.skip("Mac-only local official PDFKit source unavailable in CI")
 C.build(C.B73.load(C.WITNESS),verify_mac=True)

@pytest.mark.parametrize("i",range(60))
def test_every_editorial_subspan_has_frozen_source_and_unapproved_status(i,corpus):
 r=corpus["records"][i]
 w=C.B73.load(C.WITNESS)["subspans"][r["id"]]
 parent={x["segment_id"]:x for x in C.B73.load(C.PARENT)["records"]}[r["source_segment_id"]]
 assert r["source_pdf_sha256"]==C.B74.PDF_SHA
 assert r["local_source_subspan_sha256"]==w["sha256"]
 assert r["parent_span_sha256"]==parent["span_sha256"]
 assert parent["first_line"]<=r["first_line"]<=r["last_line"]<=parent["last_line"]
 assert r["track_hint"]==parent["track_hint"]
 assert r["teacher_review"]=="REVIEW_PENDING"
 assert r["mathematical_equivalence"]=="UNDETERMINED"
 assert r["official_atom_contribution"] is None
 assert not r["completed_full_clause_review"] and not r["student_publishable"]

@pytest.mark.parametrize("i",range(22))
def test_all_22_high_risk_parent_spans_accounted_for(i,corpus):
 chosen=[x for x in C.B73.load(C.PARENT)["records"] if x["classification"] in
         ("SUBSTANTIVE_UNNUMBERED","MIXED_REQUIRES_SPLIT")]
 s=chosen[i]
 assert any(x["source_segment_id"]==s["segment_id"] for x in corpus["records"])

@pytest.mark.parametrize("track",C.B73.TRACKS)
def test_no_fabricated_seven_track_denominators(track,corpus,drafts):
 assert corpus["official_denominators"][track] is None
 assert drafts["official_atom_denominators"][track] is None
 assert corpus["teacher_full_page_reviews"]==0
 assert drafts["teacher_approved"]==drafts["student_published"]==0

@pytest.mark.parametrize("field,value",[
 ("source_pdf_sha256","0"*64),("teacher_review","APPROVED"),
 ("student_publishable",True),("official_atom_contribution",1),
 ("mathematical_equivalence","ADJUDICATED"),("completed_full_clause_review",True)])
def test_falsifying_source_or_approval_fails_audit(field,value):
 w=C.B73.load(C.WITNESS)
 c,_=C.build(w)
 forged=deepcopy(c)
 forged["records"][0][field]=value
 with pytest.raises(AssertionError):C.validate_matrix(forged,w)

@pytest.mark.parametrize("field,value",[
 ("teacher_review","APPROVED"),("teacher_signature","fabricated-reviewer"),
 ("teacher_solution_visibility","STUDENT"),("student_publishable",True),
 ("independent_challenge_solution_reveal",True),("official_atom_count",1),
 ("mathematical_certification","FORMALLY_VERIFIED"),("teacher_proof_review","COMPLETED")])
def test_student_leak_or_forged_review_cannot_pass_teacher_packet_gate(field,value,drafts):
 forged=deepcopy(drafts)
 forged["teacher_drafts"][0][field]=value
 with pytest.raises(AssertionError):L.validate_teacher_pack(forged)

def test_source_line_drift_or_bad_parent_rejected():
 x=C.B73.load(C.WITNESS)
 altered=deepcopy(x)
 first=next(iter(altered["subspans"]))
 altered["subspans"][first]["last_line"]+=1
 with pytest.raises(AssertionError):C.build(altered)
 altered=deepcopy(x);altered["source_pdf_sha256"]="0"*64
 with pytest.raises(AssertionError):C.build(altered)

@pytest.mark.parametrize("i",range(8))
def test_eight_drafts_full_fields_and_finite_math(i,drafts,corpus):
 r=drafts["teacher_drafts"][i]
 assert r["source_editorial_subspan_id"] in {x["id"] for x in corpus["records"]}
 assert r["teacher_review"]=="REVIEW_PENDING"
 assert r["teacher_signature"] is None
 assert r["teacher_solution_visibility"]=="TEACHER_ONLY"
 assert r["mathematical_certification"]=="NOT_FORMALLY_CERTIFIED"
 assert not r["student_publishable"] and not r["independent_challenge_solution_reveal"]
 assert r["official_atom_count"] is None
 assert len(r["reasoning_steps"])>=3
 assert len(r["worked_examples"])==2 and len(r["graduated_hints"])==3
 assert r["counterexample"] and r["invalid_boundary"] and r["common_wrong_method"]
 assert L.verify_finite(r["finite_case"])

@pytest.mark.parametrize("i",range(8))
def test_wrong_claimed_answer_is_rejected(i,drafts):
 c=deepcopy(drafts["teacher_drafts"][i]["finite_case"])
 key={0:"expected",1:"expected_num",2:"expected",3:"expected",
      4:"expected_x",5:"expected",6:"expected",7:"expected"}[i]
 if i in (0,6):c[key]=not c[key]
 elif i==5:c[key][0]+=1
 elif i in (2,3):c[key][0]+=1
 elif i==7:c[key][0]+=1
 else:c[key]+=1
 with pytest.raises((AssertionError,ValueError)):L.verify_finite(c)

@pytest.mark.parametrize("i,modify",[
 (0,{"divisor":0}),(0,{"divisor":3}),(1,{"values":[]}),
 (1,{"values":[3,5,7.0]}),(2,{"condition":[0,1]}),
 (2,{"intersection":[3,5]}),(3,{"b":2}),
 (3,{"u":7,"v":3}),(4,{"x":2.0}),
 (5,{"A":[[1,0,0],[1,0,0],[0,0,1]]}),
 (5,{"A":[[1,0],[0,1]]}),(5,{"b":[4,9]}),
 (6,{"p":1}),(7,{"point":[2.0,3]}),(7,{"point":[2,3,4]})])
def test_dangerous_numeric_or_assumption_premises_rejected(i,modify,drafts):
 c=deepcopy(drafts["teacher_drafts"][i]["finite_case"])
 c.update(modify)
 with pytest.raises((AssertionError,ValueError,TypeError,IndexError)):
  L.verify_finite(c)

@pytest.mark.parametrize("x,y",[(0,0),(1,2),(-2,3),(5,-4),(-11,-9)])
def test_reflection_is_involution_and_isometry(x,y):
 c=dict(type="reflection_y",point=[x,y],expected=[-x,y])
 assert L.verify_finite(c)

@pytest.mark.parametrize("a,b,u,v",[
 (0,10,0,10),(0,10,0,5),(0,10,8,12),(0,10,-5,1),
 (-3,3,-1,1),(2,6,6,6),(2,6,20,30)])
def test_uniform_mass_is_exact_interval_intersection(a,b,u,v):
 expected=F(max(0,min(b,v)-max(a,u)),b-a)
 c=dict(type="uniform_interval",a=a,b=b,u=u,v=v,expected=[expected.numerator,expected.denominator])
 assert L.verify_finite(c)

@pytest.mark.parametrize("inter,cond",[
 (F(0),F(1)),(F(1,7),F(2,7)),(F(1,5),F(4,5)),(F(1,2),F(1,2))])
def test_conditionals_are_exact_fraction_ratios(inter,cond):
 got=inter/cond
 c=dict(type="conditional",intersection=[inter.numerator,inter.denominator],
        condition=[cond.numerator,cond.denominator],
        expected=[got.numerator,got.denominator])
 assert L.verify_finite(c)

@pytest.mark.parametrize("x,y",[(0,0),(2,1),(-3,4),(11,-5)])
def test_partial_polynomial_both_directions(x,y):
 assert L.verify_finite(dict(type="partial_polynomial",x=x,y=y,expected_x=2*x*y,expected_y=x*x+3))

def test_cramer_cannot_divide_by_zero_and_matches_independent_sympy():
 sympy=pytest.importorskip("sympy")
 for A,b in [([[2,0,0],[0,3,0],[0,0,5]],[4,9,10]),
             ([[2,1,0],[1,3,1],[0,1,2]],[3,5,2]),
             ([[1,2,0],[0,2,1],[1,0,3]],[3,4,2])]:
  M=sympy.Matrix(A)
  assert M.det()!=0
  expected=[int(v) if v.q==1 else [int(v.p),int(v.q)] for v in M.inv()*sympy.Matrix(b)]
  assert L.verify_finite(dict(type="cramer_3x3",A=A,b=b,expected=expected))

def test_complete_boolean_truth_table_independent():
 for p in [False,True]:
  for q in [False,True]:
   assert L.verify_finite(dict(type="contrapositive_truth",p=p,q=q,expected=(not p or q)))
 assert all(((not p) or q)==(q or (not p)) for p in [False,True] for q in [False,True])

from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.mark.parametrize("i",range(8))
def test_unapproved_teaching_explanations_and_solutions_never_in_student_rag(i,drafts,offline_reviewer_fixture):
 from app.attested_releases import approved_lesson_ids
 from app.deep_retrieval import student_evidence_lookup
 doc,reviewers,_,_,record,save=offline_reviewer_fixture
 save([record(0),record(1)])
 assert approved_lesson_ids()=={doc.id}
 r=drafts["teacher_drafts"][i]
 response=student_evidence_lookup(r["title"])
 raw=json.dumps(response,ensure_ascii=False)
 assert {z["knowledge_id"] for z in response["candidates"]}<={doc.id}
 assert r["id"] not in raw
 assert r["worked_examples"][0][1] not in raw
 assert r["reasoning_steps"][-1][1] not in raw
 assert response["teacher_solution_exposed"] is False
 assert response["unverified_content_exposed"] is False
