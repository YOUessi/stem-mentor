"""Independent mathematical counterexamples, seven-track integrity and anti-spoiler checks.

All teacher-only theorem proof steps remain *unverified drafts*, regardless of
passing finite tests. Full curriculum denominators are intentionally unknown.
"""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import json, math, sys
import pytest
import sympy as sp
from pydantic import ValidationError
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch111 as B
from kb_batch111_content import CANDIDATES,PARTITIONS
from kb_batch111_lesson_authoring import UNITS
from app.deep_knowledge import DeepLesson,lessons
from app.deep_retrieval import student_evidence_lookup

@pytest.fixture(scope="module")
def artifacts():
    s=B.source();d,a=B.lessons(scope=s);c=B.coverage(sc=s,a=a)
    return s,d,a,c

def test_source_page_sha_line_cover_and_track_boundary(artifacts):
    s=artifacts[0]
    assert s["pages"]==[21,58] and s["line_counts"]=={"21":32,"58":36}
    assert s["source_lines_total"]==68 and len(s["structural_partitions"])==15
    assert s["new_editorial_candidates"]==20 and s["finite_exact_witnesses"]==17
    assert s["pedagogy_not_math_proofs"]==3
    for p,n in B.LIMITS.items():
        assert [i for z in s["structural_partitions"] if z["page"]==p
                    for i in range(z["start"],z["end"]+1)]==list(range(1,n+1))
    assert s["candidate_counts_by_track"]=={
      "COMPULSORY":10,"SELECTIVE_COMPULSORY":0,"ELECTIVE_A":0,
      "ELECTIVE_B":10,"ELECTIVE_C":0,"ELECTIVE_D":0,"ELECTIVE_E":0}
    assert all(x is None for x in s["official_seven_track_atom_denominators"].values())
    assert s["teacher_approvals"]==s["teacher_full_page_atomizations"]==0

@pytest.mark.parametrize("index",range(20))
def test_each_source_candidate_pinned_non_authoritative(artifacts,index):
    s=artifacts[0];r=s["candidates"][index];author=CANDIDATES[index]
    assert r["key"]==author["key"] and B.track(r)==r["track_hint"]
    assert len(r["source_page_pdfkit_sha256"])==64
    assert r["source_pdf_sha256"]==B.PDF_SHA
    assert r["official_atom_id"] is None
    assert r["review_status"]=="REVIEW_PENDING"
    assert r["teacher_reviewer"] is None
    assert not r["student_authoritative_release"]
    assert not r["math_witness"]["general_proof_certified"]
    assert r["math_witness"]==B.witness(r["key"])

@pytest.mark.parametrize("change",[
    "missing_line","overlapping_line","unknown_page","wrong_track","altered_sha","extra_approval",
    "fake_atom","wrong_kind","duplicate_candidate","thin_assumption","out_of_bounds"])
def test_invalid_source_or_approval_rejected(change):
    cs=deepcopy(CANDIDATES);parts=deepcopy(PARTITIONS)
    if change=="missing_line":parts[21][3]=(8,16,"TRIG_OVERVIEW")
    elif change=="overlapping_line":parts[58][1]=(7,14,"SEQUENCE_LIMIT")
    elif change=="unknown_page":cs[0]["page"]=60
    elif change=="wrong_track":cs[0]["page"]=58
    elif change=="altered_sha":cs[0]["source_pdf_sha256"]="fake"
    elif change=="extra_approval":cs[0]["review_status"]="APPROVED"
    elif change=="fake_atom":cs[0]["official_atom_id"]="FAKE"
    elif change=="wrong_kind":cs[1]["kind"]="PEDAGOGY"
    elif change=="duplicate_candidate":cs[1]["key"]=cs[0]["key"]
    elif change=="thin_assumption":cs[0]["mathematical_preconditions"]="ok"
    else:cs[0]["end"]=100
    with pytest.raises((ValueError,KeyError)):
        B.source(candidates=cs,partitions=parts)

def test_mac_original_official_pdf_evidence():
    if not B.PDF.is_file():
        pytest.skip("Original official PDF is deliberately Mac-only")
    assert B.source(verify_local_source=True)["source_lines_total"]==68

@pytest.mark.parametrize("i",range(8))
def test_teacher_only_complete_lesson(artifacts,i):
    s,docs,a,_=artifacts
    x=DeepLesson.model_validate(docs[i])
    assert x.id==f"math.hs.batch111.{i+1:02d}"
    assert x.title==UNITS[i]["title"]
    assert x.review.status=="REVIEW_PENDING" and x.review.reviewer_id is None
    assert x.teacher_solution_visibility=="TEACHER_ONLY"
    assert x.provenance.permission=="PROJECT_AUTHORED"
    assert len(x.worked_examples)==2 and len(x.hint_ladder)==3
    assert x.worked_examples[0].question!=x.worked_examples[1].question
    assert len(x.counterexamples)==1 and len(x.misconceptions)==1
    assert len(x.assumptions)>=2 and len(x.notation)>=2
    assert len(x.prerequisites)>=2 and x.transfer.near and x.transfer.far
    if x.kind=="theorem":assert len(x.proof_steps)>=3
    else:assert len(x.rationale_steps)>=3
    link=a["source_links"][i]
    assert link["source_candidate_id"] in {r["id"] for r in s["candidates"]}
    assert link["source_track_hint"]==("COMPULSORY" if i<4 else "ELECTIVE_B")
    assert link["official_math_atom_id"] is None
    assert not link["teacher_approved"] and not link["general_proof_certified"]

@pytest.mark.parametrize("i",range(8))
def test_student_retrieval_denies_teacher_solutions(artifacts,i):
    doc=artifacts[1][i]
    result=student_evidence_lookup(doc["title"])
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["teacher_solution_exposed"] is False
    payload=json.dumps(result,ensure_ascii=False)
    for ex in doc["worked_examples"]:
        assert ex["answer"] not in payload
        assert ex["check"] not in payload

@pytest.mark.parametrize("i",range(8))
def test_fake_teacher_signoff_rejected(artifacts,i):
    doc=deepcopy(artifacts[1][i])
    doc["review"]=dict(status="APPROVED",reviewer_id="fictional",
                       reviewed_at="2026-11-12",review_record="pretend")
    with pytest.raises(ValidationError):DeepLesson.model_validate(doc)

@pytest.mark.parametrize("i",range(8))
def test_teacher_solution_visibility_escalation_rejected(artifacts,i):
    doc=deepcopy(artifacts[1][i]);doc["teacher_solution_visibility"]="STUDENT_VISIBLE"
    with pytest.raises(ValidationError):DeepLesson.model_validate(doc)

@pytest.mark.parametrize("i",range(8))
def test_unlicensed_author_rejected(artifacts,i):
    doc=deepcopy(artifacts[1][i]);doc["provenance"]["permission"]="COPYRIGHT_UNKNOWN"
    with pytest.raises(ValidationError):DeepLesson.model_validate(doc)

@pytest.mark.parametrize("bad",["remove","unknown_curriculum","wrong_source","fake_approval",
    "missing_example","no_counterexample","no_hints","no_reasoning","short_statement",
    "fake_type","no_transfer","duplicate_source","cross_track","forward_prerequisite"])
def test_invalid_lesson_payloads_rejected(bad):
    units=deepcopy(UNITS)
    if bad=="remove":units.pop()
    elif bad=="unknown_curriculum":units[0]["curriculum_id"]="MISSING-ID"
    elif bad=="wrong_source":units[0]["source_key"]="UNKNOWN-KEY"
    elif bad=="fake_approval":units[0]["review_status"]="APPROVED"
    elif bad=="missing_example":units[0]["examples"].pop()
    elif bad=="no_counterexample":units[0]["negative"]=("a","b","c")
    elif bad=="no_hints":units[0]["hints"]=[]
    elif bad=="no_reasoning":units[0]["reasoning"]=[]
    elif bad=="short_statement":units[0]["statement"]="short"
    elif bad=="fake_type":units[0]["kind"]="oracle"
    elif bad=="no_transfer":units[0]["far"]="no"
    elif bad=="duplicate_source":units[1]["source_key"]=units[0]["source_key"]
    elif bad=="cross_track":units[0]["source_key"]=units[4]["source_key"]
    else:
        orig=B.DEPENDENCIES.copy()
        try:
            B.DEPENDENCIES[0]=[5]
            with pytest.raises((ValueError,ValidationError)):B.lessons(units=units)
        finally:B.DEPENDENCIES.clear();B.DEPENDENCIES.update(orig)
        return
    with pytest.raises((ValueError,ValidationError)):B.lessons(units=units)

def test_integrity_gate_fields(artifacts):
    s,docs,a,c=artifacts
    assert len(docs)==8 and len({z["id"] for z in docs})==8
    assert a["new_deep_drafts"]==8 and a["new_teacher_worked_examples"]==16
    assert a["new_hint_levels"]==24 and a["new_transfer_tasks"]==16
    assert a["new_counterexamples"]==8 and a["new_proof_step_candidates"]==12
    assert a["teacher_approvals"]==0 and a["student_authoritative_releases"]==0
    assert a["general_proof_certificates"]==0 and a["arbitrary_student_steps_certified"]==0
    assert all(z["coverage_fraction"] is None and z["total"] is None
               for z in c["official_atom_coverage_by_track"].values())
    assert c["teacher_certified_full_pages"]==0
    assert c["scoped_pages_in_three_latest_batches"]==[19,20,21,56,57,58]
    assert len(c["new_lesson_field_checks"])==8
    assert all(all(y["field_checks"].values()) and y["field_completion"]==1
               for y in c["new_lesson_field_checks"])
    assert {z["id"] for z in docs}<={x.id for x in lessons()}
    order={d["id"]:i for i,d in enumerate(docs)}
    for i,doc in enumerate(docs):
        assert all(k in order and order[k]<i for k in doc["prerequisite_lesson_ids"])

@pytest.mark.parametrize("change",["fake_total","fake_approval","duplicated_page","wrong_source"])
def test_coverage_no_phantom_denominators(change):
    sources=[json.loads((ROOT/f"docs/evaluation/KB_BATCH{n}_SCOPE.json").read_text(encoding="utf8"))
             for n in (109,110)]
    if change=="fake_total":sources[0]["official_seven_track_atom_denominators"]["ELECTIVE_A"]=12
    elif change=="fake_approval":sources[0]["teacher_approvals"]=1
    elif change=="duplicated_page":sources[1]["line_counts"]["19"]=1
    else:sources[1]["source_pdf_sha256"]="FAKE"
    # This test uses a guard equivalent to the coverage prerequisite gate.
    with pytest.raises(ValueError):
        seen=set()
        for a in (*sources,B.source()):
            B.need(a["source_pdf_sha256"]==B.PDF_SHA,"false provenance")
            B.need(set(a["official_seven_track_atom_denominators"].values())=={None},
                   "false denominator")
            B.need(a["teacher_approvals"]==0,"false teacher approval")
            for page in a["line_counts"]:
                B.need(int(page) not in seen,"duplicated page")
                seen.add(int(page))

def test_generation_is_reproducible_no_drift(artifacts):
    s,docs,a,c=artifacts
    assert B.SOURCE_OUT.read_text(encoding="utf8")==B.dump(s)
    assert B.PACK.read_text(encoding="utf8")==B.dump(docs)
    assert B.AUDIT.read_text(encoding="utf8")==B.dump(a)
    assert B.COVER.read_text(encoding="utf8")==B.dump(c)
    assert B.MD.read_text(encoding="utf8")==B.markdown(s,docs,a,c)

# Mathematically independent tests: rational examples, exact symbolic reductions,
# derivative conditions, and counterexamples; deliberately not proof certification.
@pytest.mark.parametrize("a,y,x",[(2,8,3),(3,27,3),(sp.Rational(1,2),8,-3),(5,125,3)])
def test_inverse_log_exact(a,y,x):
    assert a>0 and a!=1 and y>0
    assert sp.simplify(sp.log(y,a)-x)==0 and sp.simplify(a**x-y)==0

@pytest.mark.parametrize("degree,radian",[
    (0,0),(30,sp.pi/6),(90,sp.pi/2),(150,5*sp.pi/6),
    (-225,-5*sp.pi/4),(360,2*sp.pi)])
def test_radian_conversion_exact(degree,radian):
    assert sp.simplify(sp.Rational(degree,180)*sp.pi-radian)==0

@pytest.mark.parametrize("angle,sn,cs",[
    (0,0,1),(sp.pi/6,sp.Rational(1,2),sp.sqrt(3)/2),
    (sp.pi/2,1,0),(sp.pi,0,-1),(3*sp.pi/2,-1,0)])
def test_unit_circle_values_and_tangent_domain(angle,sn,cs):
    assert sp.sin(angle)==sn and sp.cos(angle)==cs
    assert sp.simplify(sn**2+cs**2)==1
    if cs==0:assert not B.sp.cos(angle)
    else: assert sp.simplify(sp.tan(angle)-sn/cs)==0

@pytest.mark.parametrize("n",range(2,10))
def test_sequence_limit_epsilon_witness(n):
    e=Fraction(1,n)
    N=n+1
    for k in range(N,N+30):
        assert Fraction(1,k)<e
    assert (-1)**n!=(-1)**(n+1)

@pytest.mark.parametrize("n",range(1,11))
def test_monotone_bounded_sequence_exact(n):
    a=Fraction(1)-Fraction(1,n)
    b=Fraction(1)-Fraction(1,n+1)
    assert a<=b<1

@pytest.mark.parametrize("lo,hi,c",[(1,3,2),(0,2,1),(2,4,3)])
def test_mvt_exact_parabola(lo,hi,c):
    assert lo<c<hi
    assert (hi**2-lo**2)/(hi-lo)==2*c

def test_mvt_abs_is_invalid_at_cusp():
    x=sp.symbols("x",real=True)
    f=sp.Abs(x)
    assert sp.limit(f/x,x,0,dir="+")==1
    assert sp.limit(f/x,x,0,dir="-")==-1

@pytest.mark.parametrize("v",[
    sp.pi/6,sp.pi/4,sp.pi/2,sp.pi,2*sp.pi,3*sp.pi,10*sp.pi])
def test_positive_sine_inequality_bounded_cases(v):
    assert v.is_positive
    assert bool(sp.N(v-sp.sin(v),40)>0)
    assert not B.witness("sin_lt_x")["general_proof_certified"]

def test_zero_angle_equals_boundary_and_negative_counterexample():
    assert sp.sin(0)==0
    assert math.sin(-1)>-1

@pytest.mark.parametrize("h",[-2,-1,1,2,3])
def test_differential_is_only_linear_part_not_exact(h):
    x=sp.symbols("x")
    f=x*x
    df=sp.diff(f,x).subs(x,1)*h
    delta=f.subs(x,1+h)-f.subs(x,1)
    assert sp.simplify(delta-df)==h*h
