"""Independent negative regressions for Batch113; never conflate finite tests and formal proof.

Teacher approval remains disabled and the official 7-track denominator is unknown.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from fractions import Fraction
import json,sys
import pytest
import sympy as sp
from pydantic import ValidationError
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch113 as B
from kb_batch113_source import CANDIDATES,PARTITIONS
from kb_batch113_lesson_authoring import UNITS
from app.deep_knowledge import DeepLesson,lessons
from app.deep_retrieval import student_evidence_lookup

@pytest.fixture(scope="module")
def built():
    src=B.source();drafts,audit=B.lessons(scope=src);cover=B.coverage(sc=src,a=audit)
    return src,drafts,audit,cover

def test_source_anchored_page_count_exact(built):
    s=built[0]
    assert s["pages"]==[23,60] and s["line_counts"]=={"23":28,"60":27}
    assert s["source_lines_total"]==55 and len(s["structural_partitions"])==11
    assert s["new_editorial_candidates"]==22 and s["finite_exact_witnesses"]==20
    assert s["pedagogy_not_math_proofs"]==2
    assert s["candidate_counts_by_track"]==dict(zip(B.TRACKS,(11,0,0,11,0,0,0)))
    assert all(v is None for v in s["official_seven_track_atom_denominators"].values())
    assert s["teacher_approvals"]==s["teacher_full_page_atomizations"]==0
    for p,n in B.LIMITS.items():
        assert [i for r in s["structural_partitions"] if r["page"]==p
                for i in range(r["start"],r["end"]+1)]==list(range(1,n+1))

@pytest.mark.parametrize("i",range(22))
def test_source_candidate_non_authoritative_and_finite_witness(built,i):
    r=built[0]["candidates"][i];original=CANDIDATES[i]
    assert r["key"]==original["key"] and B.track(r)==r["track_hint"]
    assert r["source_pdf_sha256"]==B.PDF_SHA
    assert len(r["source_page_pdfkit_sha256"])==64
    assert r["official_atom_id"] is None
    assert r["review_status"]=="REVIEW_PENDING" and r["teacher_reviewer"] is None
    assert not r["student_authoritative_release"]
    assert r["math_witness"]==B.witness(r["key"])
    assert not r["math_witness"]["general_proof_certified"]

@pytest.mark.parametrize("mutation",[
 "skip_line","overlap","foreign_page","change_track","duplicate","fake_approval",
 "fake_certificate","fake_atom","rename_kind","thin_precondition","missing_footer",
 "wrong_source_span","bad_negative","fake_teacher","shift_partition"])
def test_malformed_source_rejected(mutation):
    cc=deepcopy(CANDIDATES);pp=deepcopy(PARTITIONS)
    if mutation=="skip_line":pp[23][1]=(3,11,"FUNCTION_MODELLING")
    elif mutation=="overlap":pp[60][2]=(12,16,"THREE_BY_THREE_MATRIX")
    elif mutation=="foreign_page":cc[0]["page"]=13
    elif mutation=="change_track":cc[0]["page"]=60
    elif mutation=="duplicate":cc[1]["key"]=cc[0]["key"]
    elif mutation=="fake_approval":cc[0]["review_status"]="APPROVED"
    elif mutation=="fake_certificate":cc[0]["math_witness"]={"general_proof_certified":True}
    elif mutation=="fake_atom":cc[0]["official_atom_id"]="CERTIFIED"
    elif mutation=="rename_kind":cc[0]["kind"]="THEOREM"
    elif mutation=="thin_precondition":cc[0]["mathematical_preconditions"]="ok"
    elif mutation=="missing_footer":pp[60][-1]=(26,26,"FOOTER_NOT_CONTENT")
    elif mutation=="wrong_source_span":cc[0]["start"]=20
    elif mutation=="bad_negative":cc[1]["invalid_generalization"]="x"
    elif mutation=="fake_teacher":cc[1]["teacher_reviewer"]="fictional"
    else:pp[23][0]=(1,2,"BISECTION_FROM_22")
    with pytest.raises((ValueError,KeyError,TypeError)):
        B.source(candidates=cc,partitions=pp)

def test_local_official_pdf_raw_line_verification():
    if not B.PDF.is_file():pytest.skip("Official copyrighted PDF only on Mac")
    assert B.source(verify_local_source=True)["source_lines_total"]==55

@pytest.mark.parametrize("i",range(9))
def test_complete_lesson_typed_assumption_and_teacher_only(built,i):
    s,docs,audit,_=built
    m=DeepLesson.model_validate(docs[i])
    assert m.id==f"math.hs.batch113.{i+1:02d}"
    assert m.title==UNITS[i]["title"]
    assert m.provenance.permission=="PROJECT_AUTHORED"
    assert m.review.status=="REVIEW_PENDING"
    assert m.review.reviewer_id is None
    assert m.teacher_solution_visibility=="TEACHER_ONLY"
    assert len(m.worked_examples)==2
    assert len(m.hint_ladder)==3 and len(set(m.hint_ladder))==3
    assert m.counterexamples and m.misconceptions
    assert m.transfer.near and m.transfer.far
    if m.kind=="theorem":
        assert len(m.proof_steps)>=3 and not m.rationale_steps
        assert all(p.claim and p.reason for p in m.proof_steps)
    else:
        assert len(m.rationale_steps)>=3 and not m.proof_steps
    link=audit["source_links"][i]
    assert link["source_key"]==UNITS[i]["source_key"]
    assert link["source_track_hint"]==("COMPULSORY" if i<4 else "ELECTIVE_B")
    assert link["official_math_atom_id"] is None
    assert not link["teacher_approved"] and not link["general_proof_certified"]
    assert (i==5)==link["engineering_mapping_is_only_prerequisite"]

@pytest.mark.parametrize("i",range(9))
def test_unapproved_cannot_leak_student_solution(built,i):
    d=built[1][i]
    out=student_evidence_lookup(d["title"])
    assert out["status"]=="NO_APPROVED_EVIDENCE"
    assert out["teacher_solution_exposed"] is False
    visible=json.dumps(out,ensure_ascii=False)
    for worked in d["worked_examples"]:
        assert worked["answer"] not in visible and worked["check"] not in visible

@pytest.mark.parametrize("i",range(9))
def test_fake_teacher_approval_cannot_enter_schema(built,i):
    d=deepcopy(built[1][i])
    d["review"]=dict(status="APPROVED",reviewer_id="some-teacher",
                     reviewed_at="2026-11-12",review_record="forged")
    with pytest.raises(ValidationError):DeepLesson.model_validate(d)

@pytest.mark.parametrize("i",range(9))
def test_cannot_promote_teacher_solution_to_student(built,i):
    d=deepcopy(built[1][i])
    d["teacher_solution_visibility"]="STUDENT_VISIBLE"
    with pytest.raises(ValidationError):DeepLesson.model_validate(d)

@pytest.mark.parametrize("i",range(9))
def test_invalid_extra_teacher_field_rejected(built,i):
    d=deepcopy(built[1][i]);d["human_approved"]=True
    with pytest.raises(ValidationError):DeepLesson.model_validate(d)

@pytest.mark.parametrize("i",range(9))
def test_authoring_modifications_are_rejected_by_guard(built,i):
    xs=deepcopy(UNITS)
    xs[i]["statement"]="very short"
    with pytest.raises(ValueError):B.lessons(units=xs,scope=built[0])

def test_ellipse_backfill_not_claimed_as_new_official_source(built):
    s,docs,a,cover=built
    assert a["source_links"][8]["source_printed_page"]==59
    assert a["source_links"][8]["backfilled_from_batch112"]
    assert not a["source_links"][8]["teacher_approved"]
    assert [r["page"] for r in s["candidates"]].count(59)==0
    assert cover["recent_source_pages_fraction"]==pytest.approx(10/61)
    assert len(cover["recent_source_pages"])==10
    assert cover["teacher_certified_full_pages"]==0
    assert all(v["total"] is None and v["coverage_fraction"] is None
               for v in cover["official_atom_coverage_by_track"].values())
    assert all(v["editorial_field_fraction"]==1 for v in cover["new_lesson_field_checks"])
    assert cover["unreviewed_legacy_prerequisites"]==172
    assert cover["uncertified_legacy_proof_steps"]==538
    assert cover["unresolved_legacy_math_conflicts"]==10

def test_independent_exponential_integer_bound_and_counter_domain():
    for n in range(4,25):
        assert sp.binomial(n,3)<=2**n
        assert sp.Rational(n,2**n)<=sp.Rational(6,(n-1)*(n-2))
    assert sp.log(16,2)==4
    assert sp.log(-1,2).is_real is False
    assert sp.Pow(2,sp.Rational(1,2))>0

def test_independent_time_conversion_exact():
    assert sp.Rational(11,10)**3==sp.Rational(1331,1000)
    assert sp.Rational(12,10)**2==sp.Rational(36,25)
    assert sp.Rational(3,60)==sp.Rational(1,20)
    assert sp.Rational(11,10)!=sp.Rational(1331,1000)

def test_projection_residual_and_zero_vector_rejection():
    u=sp.Matrix([2,0,0]);v=sp.Matrix([1,1,0])
    proj=(u.dot(v)/v.dot(v))*v
    assert proj==sp.Matrix([1,1,0])
    assert (u-proj).dot(v)==0
    zero=sp.zeros(3,1);assert zero.dot(zero)==0
    assert (u.dot(zero)/zero.dot(zero)) is sp.nan  # SymPy represents 0/0 as nan, not an exception

def test_skew_distance_exact_and_parallel_failure():
    u=sp.Matrix([1,0,0]);v=sp.Matrix([0,1,0])
    q=sp.Matrix([0,2,-4]);n=u.cross(v)
    d=sp.Abs(q.dot(n))/sp.sqrt(n.dot(n))
    assert d==4
    parallel=u.cross(2*u)
    assert parallel==sp.zeros(3,1)
    assert parallel.dot(parallel)==0
    assert q.dot(parallel)==0

def test_determinant_zero_not_same_as_inconsistent_system():
    A=sp.diag(1,1,0)
    assert A.det()==0 and A.rank()==2
    b=sp.Matrix([1,1,0])
    assert A.row_join(b).rank()==2
    assert A*sp.Matrix([1,1,8])==b
    bad=sp.Matrix([1,1,1])
    assert A.row_join(bad).rank()>A.rank()

def test_gaussian_zero_multiply_changes_solution():
    x=sp.symbols("x")
    original=sp.Eq(x,1);lost=sp.Eq(0*x,0)
    assert bool(original.subs(x,2)) is False
    assert bool(lost.subs(x,2)) is True

def test_ellipse_symbolic_interior_boundary_and_nonpolytope_gap():
    t=sp.symbols("t",real=True)
    x,y=sp.symbols("x y",real=True)
    f=x*x+4*y*y
    assert [sp.diff(f,z) for z in (x,y)]==[2*x,8*y]
    g=sp.trigsimp(f.subs({x:sp.cos(t),y:sp.sin(t)}))
    assert sp.simplify(g-(1+3*sp.sin(t)**2))==0
    assert g.subs(t,0)==1 and g.subs(t,sp.pi/2)==4
    h=x*x-y*y
    gh=sp.trigsimp(h.subs({x:2*sp.cos(t),y:sp.sin(t)}))
    assert sp.simplify(gh-(5*sp.cos(t)**2-1))==0
    assert gh.subs(t,0)==4 and gh.subs(t,sp.pi/2)==-1
    assert f.subs({x:0,y:0})==0
    # The candidate closed disk contains infinitely many boundary points,
    # so the finite-vertex affine-polytope extremum theorem cannot certify it.
    assert sp.simplify(f.subs({x:0,y:1}))==4

def test_batch_source_files_deterministic_and_generated_artifacts_current(built):
    for p in (B.SOURCE_OUT,B.PACK,B.AUDIT,B.COVER,B.MD):
        assert p.is_file() and p.stat().st_size>200
    assert json.loads(B.SOURCE_OUT.read_text())==built[0]
    assert json.loads(B.PACK.read_text())==built[1]
    assert json.loads(B.AUDIT.read_text())==built[2]
    assert json.loads(B.COVER.read_text())==built[3]
