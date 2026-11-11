from scripts.kb_frozen_batch24 import frozen_batch24_lessons
"""Independent Batch24 source integrity, mathematical boundaries, and anti-leak regression."""
import copy
import importlib.util
import json
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from math import comb

import pytest
import sympy as sp
from pydantic import ValidationError
from app.deep_knowledge import DeepLesson, curriculum, lessons
from app.deep_retrieval import student_evidence_lookup, editor_draft_search, EditorOnlyError
from app.kb_batch24_math import SUPPORTED, evaluate

ROOT=Path(__file__).resolve().parents[2]
DATA=json.loads((ROOT/"knowledge/deep/v1/core_foundation_batch24.json").read_text())
SCOPE=json.loads((ROOT/"docs/evaluation/KB_BATCH24_SOURCE_CROSSWALK.json").read_text())
AUDIT=json.loads((ROOT/"docs/evaluation/KB_BATCH24_INTEGRITY_AND_PROOFS.json").read_text())
def load_script(name):
    spec=importlib.util.spec_from_file_location("kb24_"+name,ROOT/"scripts"/name)
    module=importlib.util.module_from_spec(spec)
    # author/integrity scripts rely on import path; import package normally via injected path below
    spec.loader.exec_module(module)
    return module
def test_machine_readable_course_matrix_separates_project_drafts_from_official_atoms():
    progress=load_script("build_kb_batch24_progress.py")
    path=ROOT/"docs/evaluation/KB_BATCH24_COURSE_PROGRESS_MATRIX.json"
    obj=json.loads(path.read_text())
    assert json.loads(progress.build())==obj
    assert len(obj["courses"])==178 and len(obj["tracks"])==8
    assert obj["summary"]["linked_draft_documents"]==287
    assert obj["summary"]["draft_course_associations"]==338
    assert obj["summary"]["worked_example_count"]==574
    assert obj["summary"]["unverified_proof_steps"]==538
    assert obj["summary"]["teacher_approved_lessons"]==0
    assert obj["summary"]["officially_verified_atomic_denominator"] is None
    assert all(r["official_unit_coverage"] is None and r["approved_lesson_count"]==0
        and r["mathematical_full_proofs_certified"]==0 for r in obj["courses"])
    assert {r["track"] for r in obj["tracks"]}=={
        "COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
        "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E","ELECTIVE_UNASSIGNED"}

def test_full_source_lesson_authoring_and_proof_union():
    author=load_script("author_kb_batch24.py")
    scope=load_script("build_kb_batch24_scope.py")
    assert json.loads(author.build())==DATA
    assert json.loads(scope.build())==SCOPE
    assert len(DATA)==20 and len(frozen_batch24_lessons())==287 and len(curriculum())==178
    assert AUDIT["summary"]["all_unverified_proof_steps"]==538
    assert AUDIT["summary"]["new_unverified_proof_steps"]==19
    assert AUDIT["summary"]["new_teacher_side_examples"]==40
    assert AUDIT["summary"]["new_by_kind"]=={"concept":5,"method":9,"theorem":6}
    assert AUDIT["summary"]["approved_teacher_lessons"]==0
    assert AUDIT["summary"]["verified_official_atomic_denominator"] is None
    assert all(x["official_verified_atom_denominator"] is None for x in AUDIT["official_tracks"])

def test_source_marker_non_equivalence_and_full_provisional_track_matrix():
    assert SCOPE["summary"]["numbered_marker_occurrences"]==315
    assert SCOPE["summary"]["distinct_marker_text_hashes"]==293
    assert SCOPE["summary"]["repeated_text_hash_across_pages_groups"]==22
    assert SCOPE["summary"]["editorial_sample_objectives"]==132
    assert SCOPE["summary"]["unnumbered_de_headings"]==23
    assert SCOPE["summary"]["open_editorial_gap_tickets"]==28
    assert len(SCOPE["source_markers"])==315
    assert len(SCOPE["project_objective_page_proximities"])==132
    assert len(SCOPE["unnumbered_de_headings"])==23
    assert len(SCOPE["editorial_gap_tickets"])==28
    assert len(SCOPE["by_track"])==7
    assert all(x["official_coverage_rate"] is None for x in SCOPE["by_track"])
    assert all(x["counts_as_official_atom"] is False for x in SCOPE["source_markers"])
    assert all(x["verified_official_atom_id"] is None for x in SCOPE["project_objective_page_proximities"])
    assert SCOPE["summary"]["undocumented_historical_248_marker_claim"]=="NOT_REPRODUCED_FROM_THIS_SOURCE"

def test_scope_rejects_source_hash_and_teacher_forgery():
    s=load_script("build_kb_batch24_scope.py")
    source=s.load(s.SRC);o=s.load(s.OBJECTIVES);u=s.load(s.UNNUMBERED);g=s.load(s.TICKETS)
    old=s.load(s.OLD);course=s.load(s.COURSE)
    for op in ("pdf_sha","page_sha","approved_marker","duplicate_marker",
               "approve_objective","forge_gap","forged_line_sha","forged_marker_track",
               "modified_editorial_objective"):
        a,b,c,d,e,f=map(copy.deepcopy,(source,o,u,g,old,course))
        if op=="pdf_sha":a["source"]["sha256"]="f"*64
        elif op=="page_sha":c["items"][0]["page_text_sha256"]="f"*64
        elif op=="approved_marker":a["enumerated_source_anchors"][0]["teacher_review"]="APPROVED"
        elif op=="duplicate_marker":a["enumerated_source_anchors"][1]["id"]=a["enumerated_source_anchors"][0]["id"]
        elif op=="approve_objective":b["items"][0]["verified_official_atom_id"]="fake"
        elif op=="forge_gap":d["tickets"][0]["source_page_text_sha256"]="0"*64
        elif op=="forged_line_sha":a["enumerated_source_anchors"][0]["line_sha256"]="f"*64
        elif op=="forged_marker_track":a["enumerated_source_anchors"][0]["track"]="ELECTIVE_E"
        elif op=="modified_editorial_objective":b["items"][0]["editorial_learning_objective"]="Unreviewed replacement text"
        with pytest.raises(ValueError):
            s.reconcile(a,b,c,d,e,f)

def test_all_20_drafts_structural_and_retrieval_policy():
    for row in DATA:
        doc=DeepLesson.model_validate(row)
        assert doc.review.status=="REVIEW_PENDING"
        assert not doc.review.reviewer_id
        assert doc.teacher_solution_visibility=="TEACHER_ONLY"
        assert len(doc.worked_examples)==2
        assert doc.hint_ladder and len(doc.hint_ladder)==3
        assert row["counterexamples"] and row["misconceptions"]
        assert row["boundaries"] and row["prerequisites"]
        assert student_evidence_lookup(row["title"])["status"]=="NO_APPROVED_EVIDENCE"
    with pytest.raises(EditorOnlyError):
        editor_draft_search("等比数列 量词 双曲线")
    for field,value in [
      ("teacher_solution_visibility","STUDENT_VISIBLE"),
      ("worked_examples",[]),
      ("proof_steps",[]),
      ("review",dict(status="APPROVED",reviewer_id="fake",reviewed_at="2026-11-08",review_record="fake")),
    ]:
        bad=copy.deepcopy(DATA[0])
        bad[field]=value
        with pytest.raises(ValidationError):
            DeepLesson.model_validate(bad)

def test_proof_sha256_tampering_not_certified():
    from hashlib import sha256
    claims={}
    for x in DATA:
        for i,step in enumerate(x["proof_steps"],1):
            claims[x["id"]+"#"+str(i)]=sha256((step["claim"]+"\x00"+step["reason"]).encode()).hexdigest()
    assert len(claims)==19
    assert {x["id"]:x["claim_reason_sha256"] for x in AUDIT["new_unverified_proof_review_queue"]}==claims
    assert all(x["status"]=="NOT_FORMALLY_VERIFIED" and not x["whole_theorem_certified"] and not x["student_publishable"]
        for x in AUDIT["new_unverified_proof_review_queue"])

@pytest.mark.parametrize("op",sorted(SUPPORTED))
def test_all_exact_oracles_fail_closed_spoofing(op):
    for input in ({},None,{"payload":"__import__('os').system('id')"}):
        result=evaluate(op,input)
        assert result["status"]=="CONDITIONS_NOT_ESTABLISHED"
        assert result["student_step_verified"] is False
        assert result["teacher_approved"] is False
        assert result["complete_theorem_certified"] is False
assert evaluate("arbitrary_student_proof",{"proof":"because I said so"})["status"]=="UNSUPPORTED"

@pytest.mark.parametrize("a,b,c",product((-3,-1,0,1,5),(-3,0,2,5),(Q(-2),Q(0),Q(3))))
def test_inequality_multiply_sign_exact(a,b,c):
    r=evaluate("strict_inequality_scale",{"a":a,"b":b,"c":str(c)})
    ok=a<b and c!=0
    assert (r["status"]=="VERIFIED_FINITE_INSTANCE")==ok
    if ok:
        assert Q(r["witness"]["scaled_left"])==a*c
        assert Q(r["witness"]["scaled_right"])==b*c
        assert r["witness"]["reversed"]==(c<0)

@pytest.mark.parametrize("a,b,c",product((-4,-1,0,1,3),(-2,0,3),(-4,0,5)))
def test_quadratic_discriminant_vs_sympy(a,b,c):
    r=evaluate("quadratic_discriminant",{"a":a,"b":b,"c":c})
    if a==0:assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:
        assert r["status"]=="VERIFIED_FINITE_INSTANCE"
        x=sp.symbols("x",real=True)
        d=sp.discriminant(a*x*x+b*x+c,x)
        assert Q(r["witness"]["discriminant"])==d
        assert r["witness"]["real_root_count"]==(2 if d>0 else 1 if d==0 else 0)

@pytest.mark.parametrize("a,b",product(range(-1,15),repeat=2))
def test_am_gm_square_identity_and_boundaries(a,b):
    r=evaluate("am_gm_nonnegative",{"a":a,"b":b})
    if a<0 or b<0:assert r["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:
        assert r["status"]=="VERIFIED_FINITE_INSTANCE"
        assert Q(r["witness"]["squared_gap"])==Q((a-b)**2,4)
        assert r["witness"]["equality"]==(a==b)

@pytest.mark.parametrize("a,q,n",product((-4,0,3),(Q(-2),Q(0),Q(1),Q(2),Q(1,2)),range(1,20)))
def test_finite_geometric_sum_independently_enumerated(a,q,n):
    r=evaluate("finite_geometric_sum",{"a1":a,"q":str(q),"n":n})
    assert r["status"]=="VERIFIED_FINITE_INSTANCE"
    assert Q(r["witness"]["sum"])==sum((a*q**j for j in range(n)),Q(0))
assert evaluate("finite_geometric_sum",{"a1":3,"q":1,"n":0})["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("N,K,n",[(5,2,2),(7,0,4),(6,6,6),(9,3,4),(20,5,6)])
def test_hypergeometric_support_and_full_normalization(N,K,n):
    low=max(0,n-(N-K)); high=min(n,K); ps=[]
    for k in range(low,high+1):
        r=evaluate("hypergeometric_point_mass",{"N":N,"K":K,"n":n,"k":k})
        assert r["status"]=="VERIFIED_FINITE_INSTANCE"
        p=Q(r["witness"]["probability"])
        assert p==Q(comb(K,k)*comb(N-K,n-k),comb(N,n))
        ps.append(p)
    assert sum(ps)==1

@pytest.mark.parametrize("x1,x2,y1,y2",product((-2,0,3),(-2,0,5),(-3,0,4),(-4,0,6)))
def test_slope_finite_and_vertical_refusal(x1,x2,y1,y2):
    r=evaluate("slope_nonvertical",{"x1":x1,"x2":x2,"y1":y1,"y2":y2})
    assert (r["status"]=="VERIFIED_FINITE_INSTANCE")==(x1!=x2)
    if x1!=x2:assert Q(r["witness"]["slope"])==Q(y2-y1,x2-x1)

@pytest.mark.parametrize("vals",[[True],[False],[True,True],[False,True],[False,False,True],[True,True,False]])
def test_finite_quantifiers_and_dual_negation(vals):
    r=evaluate("finite_quantifier_negation",{"truth_values":vals})
    assert r["status"]=="VERIFIED_FINITE_INSTANCE"
    w=r["witness"]
    assert w["not_forall"]==w["exists_counterexample"]
    assert w["not_exists"]==w["forall_negated"]
assert evaluate("finite_quantifier_negation",{"truth_values":[]})["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("row,col,total",product((0,1,5,20),(0,1,8,20),(1,10,30)))
def test_expected_cell_exact_with_zero_guards(row,col,total):
    r=evaluate("two_by_two_expected_cell",{"row":row,"column":col,"total":total})
    ok=0<row<=total and 0<col<=total
    assert (r["status"]=="VERIFIED_FINITE_INSTANCE")==ok
    if ok:assert Q(r["witness"]["expected"])==Q(row*col,total)
