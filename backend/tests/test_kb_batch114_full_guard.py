"""Batch114 independent-source and math regression; never certify student solutions."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import json,sys
import pytest
import sympy as sp
from pydantic import ValidationError
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
import build_kb_batch114 as B
from kb_batch114_source import CANDIDATES,PARTITIONS
from kb_batch114_authoring import UNITS
from app.deep_knowledge import DeepLesson,lessons
from app.deep_retrieval import student_evidence_lookup

@pytest.fixture(scope="module")
def built():
    sc=B.source();ds,au=B.lessons(scope=sc);co=B.coverage(scope=sc,ds=ds)
    return sc,ds,au,co

def test_exact_pdfkit_and_page_partition(built):
    s=built[0]
    assert s["pages"]==[24,61] and s["line_counts"]=={"24":29,"61":26}
    assert s["source_lines_total"]==55 and len(s["structural_partitions"])==19
    assert s["editorial_candidate_count"]==21 and s["finite_exact_witnesses"]==19
    assert s["source_candidate_counts_by_track"]==dict(zip(B.TRACKS,(10,0,0,11,0,0,0)))
    for p,n in B.LIMITS.items():
        assert [k for z in s["structural_partitions"] if z["page"]==p
                for k in range(z["start"],z["end"]+1)]==list(range(1,n+1))

def test_pinned_mac_source_when_available():
    if not B.PDF.is_file(): pytest.skip("official source file intentionally Mac only")
    assert B.source(verify_local_source=True)["source_lines_total"]==55

@pytest.mark.parametrize("i",range(21))
def test_source_candidate_finite_not_formal(built,i):
    s=built[0]["candidates"][i]
    assert s["source_pdf_sha256"]==B.PDF_SHA
    assert s["track_hint"]==B.track(s)
    assert s["math_witness"]==B.witness(s["key"])
    assert not s["math_witness"]["general_proof_certified"]
    assert s["official_atom_id"] is None and s["teacher_reviewer"] is None
    assert not s["student_authoritative_release"] and s["review_status"]=="REVIEW_PENDING"

@pytest.mark.parametrize("which",[
    "duplicate","foreign_page","source_shift","category_shift","fake_approval",
    "fake_teacher","fake_proof","fake_official_id","missing_lines","overlap",
    "footer_missing","key_spoof","short_precondition","wrong_partition","other_type"])
def test_fake_or_invalid_source_rejected(which):
    rows=deepcopy(CANDIDATES);parts=deepcopy(PARTITIONS)
    if which=="duplicate": rows[1]["key"]=rows[0]["key"]
    elif which=="foreign_page":rows[0]["page"]=74
    elif which=="source_shift":rows[0]["start"]=3
    elif which=="category_shift":rows[0]["kind"]="PEDAGOGY"
    elif which=="fake_approval":rows[0]["review_status"]="APPROVED"
    elif which=="fake_teacher":rows[0]["teacher_reviewer"]="fictional teacher"
    elif which=="fake_proof":rows[0]["proof_certified"]=True
    elif which=="fake_official_id":rows[0]["official_atom_id"]="fake"
    elif which=="missing_lines":parts[24][1]=(3,3,"LOG_INVERSE")
    elif which=="overlap":parts[61][3]=(13,16,"CONTINUOUS_RANDOM_VARIABLE")
    elif which=="footer_missing":parts[61][-1]=(25,25,"FOOTER")
    elif which=="key_spoof":rows[2]["key"]="other"
    elif which=="short_precondition":rows[0]["mathematical_preconditions"]="bad"
    elif which=="wrong_partition":rows[0]["start"]=4
    else:rows[0]["kind"]="APPROVED_THEOREM"
    with pytest.raises((ValueError,KeyError,TypeError)):B.source(rows,parts)

@pytest.mark.parametrize("i",range(8))
def test_deep_draft_schema_and_teacher_only(built,i):
    sc,ds,au,co=built
    obj=DeepLesson.model_validate(ds[i])
    assert obj.id==f"math.hs.batch114.{i+1:02d}"
    assert obj.title==UNITS[i]["title"]
    assert obj.review.status=="REVIEW_PENDING" and obj.review.reviewer_id is None
    assert obj.provenance.permission=="PROJECT_AUTHORED"
    assert obj.teacher_solution_visibility=="TEACHER_ONLY"
    assert len(obj.worked_examples)==2 and len(obj.hint_ladder)==3
    assert obj.counterexamples and obj.misconceptions and obj.transfer.near and obj.transfer.far
    if obj.kind=="theorem":
        assert len(obj.proof_steps)==3 and not obj.rationale_steps
    else: assert len(obj.rationale_steps)==3 and not obj.proof_steps
    assert au["source_links"][i]["source_printed_page"]==(24 if i<4 else 61)
    assert not au["source_links"][i]["teacher_approved"]

@pytest.mark.parametrize("i",range(8))
def test_fake_approved_rejected(built,i):
    doc=deepcopy(built[1][i])
    doc["review"]=dict(status="APPROVED",reviewer_id="not-authenticated",
                       reviewed_at="2026-11-12",review_record="forged")
    with pytest.raises(ValidationError):DeepLesson.model_validate(doc)

@pytest.mark.parametrize("i",range(8))
def test_teacher_solution_not_student_visible(built,i):
    doc=deepcopy(built[1][i])
    doc["teacher_solution_visibility"]="STUDENT_VISIBLE"
    with pytest.raises(ValidationError):DeepLesson.model_validate(doc)

@pytest.mark.parametrize("i",range(8))
def test_unreviewed_evidence_not_retrieved_as_authority(built,i):
    doc=built[1][i]
    result=student_evidence_lookup(doc["title"])
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["teacher_solution_exposed"] is False
    visible=json.dumps(result,ensure_ascii=False)
    for e in doc["worked_examples"]:
        assert e["answer"] not in visible and e["check"] not in visible

@pytest.mark.parametrize("i",range(8))
def test_authoring_tamper_rejected(built,i):
    altered=deepcopy(UNITS)
    altered[i]["statement"]="SHORT"
    with pytest.raises(ValueError):B.lessons(units=altered,scope=built[0])

@pytest.mark.parametrize("i",range(8))
def test_source_track_tamper_rejected(built,i):
    src=deepcopy(built[0])
    key=UNITS[i]["source_key"]
    next(r for r in src["candidates"] if r["key"]==key)["track_hint"]="ELECTIVE_D"
    with pytest.raises(ValueError):B.lessons(scope=src)

def test_machine_auditable_page_vs_atom_denominator(built):
    sc,ds,au,cov=built
    assert cov["official_source_pdf_pages"]==61
    assert cov["source_structure_candidate_reviewed_pages"]==14
    assert len(cov["per_page_denominator_status"])==61
    assert len(cov["source_structure_unreviewed_pages"])==47
    assert len(cov["source_structure_reviewed_pages"])==14
    assert all(x["teacher_review_record"] is None for x in cov["per_page_denominator_status"])
    assert all(x["official_math_atoms"] is None for x in cov["per_page_denominator_status"])
    assert all(x is None for x in cov["seven_track_official_atom_denominator"].values())
    assert all(x is None for x in cov["seven_track_certified_coverage"].values())
    assert cov["teacher_verified_atomized_pages"]==0

def test_history_and_all_lesson_ids_distinct():
    all_lessons=lessons()
    ids=[x.id for x in all_lessons]
    assert len(ids)==len(set(ids))
    assert all(f"math.hs.batch114.{i:02d}" in ids for i in range(1,9))

@pytest.mark.parametrize("i",range(8))
def test_independent_lesson_example_arithmetic(built,i):
    doc=built[1][i]
    assert all(e["answer"] and e["steps"] and e["check"] for e in doc["worked_examples"])
    # This checks integrity, not a generic proof of the Chinese natural-language answers.
    assert doc["counterexamples"][0]["false_claim"] != doc["counterexamples"][0]["explanation"]

def test_log_inverse_domain_and_base_counterexample():
    assert sp.log(8,2)==3
    assert sp.log(-4,2).is_real is False
    assert 1**0==1**3

def test_trig_difference_symbolic_identity_and_sign_trap():
    a,b=sp.symbols("a b",real=True)
    assert sp.trigsimp(sp.cos(a-b)-(sp.cos(a)*sp.cos(b)+sp.sin(a)*sp.sin(b)))==0
    assert sp.trigsimp(sp.cos(a-b)-(sp.cos(a)*sp.cos(b)-sp.sin(a)*sp.sin(b))).subs({a:sp.pi/4,b:sp.pi/4})==1

def test_bisection_real_exact_intervals_and_noncontinuous_counterexample():
    f=lambda z:z*z-2
    assert f(Fraction(5,4))<0 and f(Fraction(3,2))>0
    assert Fraction(2,16)/2==Fraction(1,16)
    assert sp.simplify(1/sp.Symbol("x")).subs("x",0)==sp.zoo

def test_density_and_uniform_exact_moments():
    x=sp.symbols("x",real=True)
    assert sp.integrate(2*x,(x,0,1))==1
    assert sp.integrate(2*x,(x,sp.Rational(1,2),1))==sp.Rational(3,4)
    assert sp.integrate((x-5)**2,(x,2,8))/6==3
    assert sp.integrate(x,(x,-1,1))/2==0

def test_joint_probability_uncorrelated_but_dependent():
    vals=(-1,0,1)
    EX=sum(sp.Rational(v,3) for v in vals)
    EY=sum(sp.Rational(v*v,3) for v in vals)
    EXY=sum(sp.Rational(v*v*v,3) for v in vals)
    assert EXY-EX*EY==0
    assert sp.Rational(1,3)!=sp.Rational(1,3)*sp.Rational(1,3)

def test_student_free_steps_never_certified(built):
    assert built[2]["student_free_text_proof_certificates"]==0
    assert built[2]["formal_proof_certificates"]==0
    assert built[2]["teacher_approvals"]==0
    assert built[3]["teacher_approved_drafts"]==0
