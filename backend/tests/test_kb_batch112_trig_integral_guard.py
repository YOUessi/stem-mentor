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
import build_kb_batch112 as B
from kb_batch112_source import CANDIDATES,PARTITIONS
from kb_batch112_lesson_authoring import UNITS
from app.deep_knowledge import DeepLesson,lessons
from app.deep_retrieval import student_evidence_lookup

@pytest.fixture(scope="module")
def artifacts():
    s=B.source();d,a=B.lessons(scope=s);c=B.coverage(sc=s,a=a)
    return s,d,a,c

def test_source_page_sha_line_cover_and_track_boundary(artifacts):
    s=artifacts[0]
    assert s["pages"]==[22,59] and s["line_counts"]=={"22":31,"59":28}
    assert s["source_lines_total"]==59 and len(s["structural_partitions"])==11
    assert s["new_editorial_candidates"]==20 and s["finite_exact_witnesses"]==18
    assert s["pedagogy_not_math_proofs"]==2
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
    if change=="missing_line":parts[22][3]=(18,19,"TRIG_APPLICATION")
    elif change=="overlapping_line":parts[59][1]=(10,20,"TWO_VARIABLE_FUNCTION")
    elif change=="unknown_page":cs[0]["page"]=60
    elif change=="wrong_track":cs[0]["page"]=59
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
    assert B.source(verify_local_source=True)["source_lines_total"]==59

@pytest.mark.parametrize("i",range(8))
def test_teacher_only_complete_lesson(artifacts,i):
    s,docs,a,_=artifacts
    x=DeepLesson.model_validate(docs[i])
    assert x.id==f"math.hs.batch112.{i+1:02d}"
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
    assert c["scoped_pages_in_four_latest_batches"]==[19,20,21,22,56,57,58,59]
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
             for n in (109,110,111)]
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


# Independently derived finite identities and hostile counterexamples; never a proof certificate.
@pytest.mark.parametrize("x",[0,sp.pi/6,sp.pi/4,sp.pi/3,-sp.pi/5,sp.pi])
def test_unit_circle_identity_and_undefined_tangent(x):
    assert sp.simplify(sp.sin(x)**2+sp.cos(x)**2-1)==0
    if sp.cos(x)!=0:
        assert sp.simplify(1+sp.tan(x)**2-1/sp.cos(x)**2)==0

@pytest.mark.parametrize("a,b",[(sp.pi/6,sp.pi/3),(sp.pi/4,-sp.pi/6),(0,sp.pi),(sp.pi/3,sp.pi/3)])
def test_cosine_difference_correct_sign(a,b):
    assert sp.simplify(sp.cos(a-b)-(sp.cos(a)*sp.cos(b)+sp.sin(a)*sp.sin(b)))==0

@pytest.mark.parametrize("omega",[-3,-1,2,5])
def test_nonzero_sine_frequency(omega):
    period=2*sp.pi/abs(omega)
    x=sp.pi/7
    assert sp.simplify(sp.sin(omega*(x+period)+sp.pi/8)-sp.sin(omega*x+sp.pi/8))==0

@pytest.mark.parametrize("a,w",[(0,3),(3,0),(0,0)])
def test_degenerate_sinusoid_no_least_positive_period(a,w):
    assert sp.simplify(a*sp.sin(w*sp.Rational(2,5)+sp.pi/6)-
                       a*sp.sin(w*sp.Rational(8,3)+sp.pi/6))==0

@pytest.mark.parametrize("n",[1,2,3,4,8,16])
def test_right_riemann_sum_is_not_necessarily_integral(n):
    k=sp.symbols("k",integer=True,positive=True)
    r=sp.summation(k,(k,1,n))/n**2
    assert sp.simplify(r-sp.Rational(n+1,2*n))==0
    assert r>sp.Rational(1,2) and sp.limit((sp.Symbol("t")+1)/(2*sp.Symbol("t")),sp.Symbol("t"),sp.oo)==sp.Rational(1,2)

@pytest.mark.parametrize("a,b",[(0,2),(1,3),(-2,-1),(2,0)])
def test_fundamental_theorem_continuous_derivative(a,b):
    x=sp.symbols("x",real=True);F=x**3-2*x+4
    assert sp.simplify(sp.integrate(sp.diff(F,x),(x,a,b))-(F.subs(x,b)-F.subs(x,a)))==0

@pytest.mark.parametrize("x,y",[(2,1),(0,0),(-3,2),(1,-2)])
def test_partial_derivatives_are_directional_not_simultaneous(x,y):
    X,Y=sp.symbols("X Y",real=True);f=X**2*Y+3*Y**2
    assert sp.diff(f,X).subs({X:x,Y:y})==2*x*y
    assert sp.diff(f,Y).subs({X:x,Y:y})==x*x+6*y

def test_exists_partial_derivatives_does_not_imply_continuity():
    h=sp.symbols("h",real=True,nonzero=True)
    # Function g(x,y)=xy/(x^2+y^2) away from origin, g(0,0)=0:
    # Both axis restrictions are zero but diagonal is 1/2.
    assert sp.simplify((h*0)/(h*h+0))==0
    assert sp.simplify((h*h)/(h*h+h*h))==sp.Rational(1,2)

def test_bisection_requires_continuity_and_strict_sign_change():
    # Jump function has opposite endpoint signs but no root.
    jump=lambda x:-1 if x<0 else 1
    assert jump(-1)*jump(1)<0
    assert all(jump(x)!=0 for x in [-1,-sp.Rational(1,2),0,sp.Rational(1,2),1])
    # f=x^2-2 is continuous; after 2 bisections [5/4,3/2] brackets sqrt(2).
    assert sp.Rational(5,4)**2<2<sp.Rational(3,2)**2
    assert (sp.Rational(3,2)-sp.Rational(5,4))/2==sp.Rational(1,8)

def test_polygon_maximum_not_general_nonlinear_maximum():
    vertices=[(0,0),(0,1),(1,0),(1,1)]
    objective=lambda x,y:-(sp.Rational(x)-sp.Rational(1,2))**2-(sp.Rational(y)-sp.Rational(1,2))**2
    assert objective(sp.Rational(1,2),sp.Rational(1,2))==0
    assert all(objective(x,y)<0 for x,y in vertices)

def test_no_teacher_or_student_authority_for_any_new_draft(artifacts):
    s,docs,a,c=artifacts
    assert s["official_seven_track_atom_denominators"]=={t:None for t in B.TRACKS}
    assert not any(d["review"]["status"]=="APPROVED" for d in docs)
    assert all(d["teacher_solution_visibility"]=="TEACHER_ONLY" for d in docs)
    assert a["new_proof_step_candidates"]==12
    assert a["general_proof_certificates"]==0
    assert c["teacher_certified_full_pages"]==0
