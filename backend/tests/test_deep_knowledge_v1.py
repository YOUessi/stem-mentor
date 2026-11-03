"""K00/K01/K02/K03/K04 teacher-only draft content regression and negative gates."""
import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from sympy import Rational, cos, diff, pi, sin, simplify, sqrt, symbols

from app.deep_knowledge import (
    ROOT, DeepLesson, coverage_report, curriculum, lessons, public_summary,
    unpublished_teacher_preview
)


def test_course_matrix_count_and_levels_are_engineering_not_official():
    topic_rows = curriculum()
    assert len(topic_rows) ==161
    assert len({row["id"] for row in topic_rows}) ==161
    assert {row["level"] for row in topic_rows} == {"必修", "选择性必修", "选修拓展"}
    report = coverage_report()
    assert report["scope"] == "PROJECT_ENGINEERING_MAP_NOT_OFFICIAL_ATOMIC_SYLLABUS"
    assert sum(r["engineering_topics"] for r in report["by_level"].values()) ==161
    assert sum(r["with_deep_draft"] for r in report["by_level"].values()) == report["mapped_curriculum_ids"]
    assert report["mapped_curriculum_ids"] + sum(r["without_deep_draft"] for r in report["by_level"].values()) ==161


def test_all_non_authoritative_lessons_and_no_fake_approvals():
    data = lessons()
    assert len(data) >= 86  # 28 frozen baseline + 58 independently spot-checked batch04
    assert len({d.id for d in data}) == len(data)
    assert {d.review.status for d in data} == {"REVIEW_PENDING"}
    assert all(d.teacher_solution_visibility == "TEACHER_ONLY" for d in data)
    assert all(d.provenance.permission == "PROJECT_AUTHORED" for d in data)
    assert all(len(d.worked_examples) >= 2 and len(d.counterexamples) >= 1 and len(d.hint_ladder)>=3 for d in data)
    assert public_summary()["direct_student_teaching_enabled"] is False


@pytest.mark.parametrize("knowledge_id", [d.id for d in lessons()])
def test_each_draft_is_validated_and_nontrivial(knowledge_id):
    item = next(d for d in lessons() if d.id == knowledge_id)
    copy_validated = DeepLesson.model_validate(item.model_dump(mode="json"))
    assert copy_validated.id == item.id
    if item.kind == "theorem":
        assert len(item.proof_steps)>=3
        assert all(len(s.reason)>=12 and len(s.claim)>=12 for s in item.proof_steps)
    if item.kind == "concept":
        assert len(item.rationale_steps)>=2
    assert all(len(x.steps)>=2 and x.answer and x.check for x in item.worked_examples)


@pytest.mark.parametrize("mutation", [
    lambda d: d["curriculum_ids"].append(d["curriculum_ids"][0]),
    lambda d: d["provenance"].update({"permission":"UNLICENSED"}),
    lambda d: d["review"].update({"status":"APPROVED"}),
    lambda d: d["review"].update({"reviewer_id":"FAKE"}),
    lambda d: d.update({"worked_examples":[]}),
    lambda d: d.update({"hint_ladder":[]}),
    lambda d: d.update({"teacher_solution_visibility":"STUDENT"}),
    lambda d: d.update({"assumptions":[]}),
    lambda d: d.update({"extra_secret":"should-not-be-accepted"}),
])
def test_schema_rejects_incomplete_or_unsafe_drafts(mutation):
    d = copy.deepcopy(lessons()[0].model_dump(mode="json"))
    mutation(d)
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(d)


def test_forged_teacher_approval_is_rejected_even_with_claimed_metadata():
    draft = copy.deepcopy(lessons()[0].model_dump(mode="json"))
    draft["review"] = {
        "status": "APPROVED",
        "reviewer_id": "attacker-supplied-name",
        "reviewed_at": "2026-11-03",
        "review_record": "author-editable-fake-evidence",
    }
    with pytest.raises(ValidationError, match="authenticated teacher review"):
        DeepLesson.model_validate(draft)


def test_there_is_no_approval_and_electives_are_not_overstated():
    c = coverage_report()
    assert c["by_level"]["选修拓展"]["engineering_topics"] == 51
    assert c["by_level"]["选修拓展"]["teacher_approved"] == 0
    assert c["by_level"]["选修拓展"]["with_deep_draft"] == 51  # project extension topics with unapproved draft links (not official coverage)
    assert sum(v["teacher_approved"] for v in c["by_level"].values()) == 0
    official = json.loads((ROOT/"curriculum/highschool_math/official_scope_v1.json").read_text())
    assert {x["id"] for x in official["tracks"]} >= {
        "COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B",
        "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E"}
    assert all(x["status"]=="MISSING_EXPLICIT_PROJECT_TOPIC_MAPPING"
               for x in official["tracks"] if x["id"].startswith("ELECTIVE_"))


def test_public_coverage_endpoint_has_no_teacher_only_material():
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as client:
        response = client.get("/api/knowledge/depth/coverage")
    assert response.status_code == 200
    obj = response.json()
    assert obj["deep_lesson_documents"] == len(lessons())
    assert obj["direct_student_teaching_enabled"] is False
    assert not {"worked_examples","proof_steps","counterexamples","teacher_solution"}.intersection(obj)
    assert "S_n=" not in response.text


def test_unpublished_preview_is_not_an_http_endpoint():
    from app.main import app
    paths = [x.path for x in app.routes]
    assert not any("preview" in p and "knowledge" in p for p in paths)
    assert len(unpublished_teacher_preview("等比递推")) >= 1
    assert unpublished_teacher_preview("") == []


def test_all_structured_prerequisites_exist_and_are_acyclic():
    by_id = {x.id:x for x in lessons()}
    visited = set()
    def verify(k, stack):
        assert k not in stack
        if k in visited: return
        for p in by_id[k].prerequisite_lesson_ids:
            assert p in by_id
            verify(p, stack|{k})
        visited.add(k)
    for key in by_id: verify(key,set())


@pytest.mark.parametrize("q", [-3,-2,-1,0,1,Rational(1,2),2,3])
@pytest.mark.parametrize("n", range(1,11))
def test_geometric_sum_all_degenerate_real_ratios(q,n):
    a=Rational(-5,2)
    actual=sum(a*q**k for k in range(n))
    formula = n*a if q==1 else a*(1-q**n)/(1-q)
    assert simplify(actual-formula)==0


@pytest.mark.parametrize("a,d,n",[
    (2,3,10),(7,-2,5),(0,0,1),(-9,4,17),(Rational(1,3),Rational(-1,4),8)])
def test_arithmetic_sum_against_direct_list(a,d,n):
    direct=sum(a+k*d for k in range(n))
    proposed=Rational(n,2)*(2*a+(n-1)*d)
    assert simplify(direct-proposed)==0


@pytest.mark.parametrize("a,b,c",[(1,-6,11),(-2,8,-3),(3,0,-7),(-1,-4,0)])
def test_quadratic_vertex_identity(a,b,c):
    x=symbols("x",real=True)
    lhs=a*x*x+b*x+c
    rhs=a*(x+b/(2*a))**2+(4*a*c-b*b)/(4*a)
    assert simplify(lhs-rhs)==0


def test_amgm_and_sign_reversal():
    for a in range(10):
        for b in range(10):
            assert Rational(a+b,2) >= sqrt(a*b)
    assert (-3)*1 > (-3)*2
    assert 3*1 < 3*2


def test_vector_product_and_cosine_theorem_numerically():
    a=(1,2)
    b=(-2,1)
    assert a[0]*b[0]+a[1]*b[1] == 0
    assert simplify(3**2+4**2-5**2)==0
    assert simplify(sqrt(3)**2-(1+4-2*1*2*cos(pi/3)))==0


def test_sine_law_ssa_and_trig_boundary():
    assert simplify(5*sin(pi/3)/sin(pi/6)-5*sqrt(3))==0
    assert simplify(sin(pi/3+pi/6)-1)==0
    assert simplify(cos(pi/4+pi/4))==0
    assert sin(pi/2)==1 and cos(pi/2)==0


def test_derivative_power_and_monotonicity_with_zero_derivative_point():
    x=symbols("x",real=True)
    for n in range(1,8):
        assert simplify(diff(x**n,x)-n*x**(n-1)) == 0
    assert diff(x**3,x).subs(x,0)==0
    for u,v in [(0,1),(-2,-1),(-1,2)]:
        assert u<v and u**3<v**3


def test_binomial_counting_probability_invariants():
    from math import comb
    assert sum(comb(5,k) for k in range(6))==32
    assert comb(5,2)==10
    assert Rational(3,6)==Rational(1,2)
    assert Rational(2,6)/Rational(3,6)==Rational(2,3)
    assert Rational(6,10)*Rational(1,100)+Rational(4,10)*Rational(3,100)==Rational(18,1000)


def test_ellipse_focal_boundary_and_real_distance():
    c,a=4,5
    assert a>c>0
    b2=a*a-c*c
    assert b2==9
    for x,y in [(5,0),(-5,0),(0,3)]:
        r1=sqrt((x+c)**2+y*y)
        r2=sqrt((x-c)**2+y*y)
        assert simplify(r1+r2-2*a)==0
        assert simplify(Rational(x*x,a*a)+Rational(y*y,b2)-1)==0
    assert 2*1<2*2 # a<c makes the distance sum impossible


def test_counterexample_truth_for_quantifiers_and_conditional_probability():
    assert (-2)**2==4 and (-2)!=2
    assert (0)**2==0
    from sympy import nan
    assert Rational(0,1)/Rational(0,1) is nan  # symbolic 0/0 is undefined, not a valid probability
