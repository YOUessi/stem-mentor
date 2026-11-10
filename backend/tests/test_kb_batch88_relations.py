"""Batch88 math-relationship provenance and finite-witness regression (Mac-authored)."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"backend"))
import build_kb_batch87_candidate_census as B87
import build_kb_batch88_relations as B88
from app.kb_batch88_relation_oracles import evaluate, SUPPORTED
from test_attested_release_batch08 import offline_reviewer_fixture

BASE=B87.build()
ORIGINAL=B88.load()
RESULT=B88.build(ORIGINAL, BASE)

def altered(i, field, value):
    raw=copy.deepcopy(ORIGINAL)
    raw["relations"][i][field]=value
    return raw

def test_frozen_provisional_denominator_not_official():
    assert RESULT["reviewed_relation_count"]==36
    assert RESULT["source_anchor_editorials"]==428
    assert RESULT["provisional_candidate_count"]==300
    assert RESULT["unique_provisional_candidate_ids_seen"]>=55
    assert RESULT["relation_counts"]["POSSIBLE_OVERLAP"]>=20
    assert RESULT["relation_counts"]["RELATED_DISTINCT"]>=6
    assert RESULT["official_curriculum_atom_denominator"] is None
    assert RESULT["semantic_equivalence_adjudicated_count"]==0
    assert RESULT["teacher_pending_relation_count"]==36
    assert RESULT["teacher_approved_atoms"]==0
    assert RESULT["student_published_atoms"]==0

def test_generated_results_are_deterministic_and_versioned():
    assert B88.OUT.read_text(encoding="utf-8")==B88.dump(RESULT)
    assert B88.MARKDOWN.read_text(encoding="utf-8")==B88.markdown(RESULT)
    assert B88.OUT.name.startswith("KB_BATCH88")
    assert len(RESULT["reviewed_relations"])==36

@pytest.mark.parametrize("index",range(36))
def test_each_relation_has_source_sha_and_rejects_student_authority(index):
    r=RESULT["reviewed_relations"][index]
    l,rgt=r["left"],r["right"]
    source={x["candidate_id"]:x for x in BASE["provisional_candidates"]}
    for row in (l,rgt):
        src=source[row["candidate_id"]]
        assert row["source_line_sha256"] == src["source_line_sha256"]
        assert row["source_review_id"] == src["source_review_id"]
        assert row["track"] == src["track"]
        assert len(row["source_line_sha256"])==64
    assert r["review_state"]=="REVIEW_PENDING"
    assert r["teacher_approved"] is False
    assert r["math_equivalence_certified"] is False
    assert r["student_publishable"] is False
    assert r["final_atom_id"] is None
    assert r["evidence_status"]=="EDITOR_EXAMPLE_NOT_GENERAL_MATH_CERTIFICATION"
    assert r["needs_human_adjudication"] is True

@pytest.mark.parametrize("index",range(36))
@pytest.mark.parametrize("field,bad",[
    ("teacher_approved",True),
    ("math_equivalence_certified",True),
    ("student_publishable",True),
    ("review_state","APPROVED"),
    ("final_atom_id","FAKE-CERTIFIED-ATOM"),
    ("relation_proposal","EXACT_EQUIVALENCE_APPROVED"),
    ("shared_maths","same"),
    ("worked_witness","nice"),
    ("failure_or_boundary","fine"),
    ("distinguishing_conditions",""),
])
def test_relation_mutation_fail_closed(index,field,bad):
    with pytest.raises(ValueError):
        B88.build(altered(index,field,bad),BASE)

@pytest.mark.parametrize("index",range(36))
def test_candidate_identity_must_exist(index):
    with pytest.raises(ValueError):
        B88.build(altered(index,"left_candidate_id","FAKE-UNSOURCED-CANDIDATE"),BASE)

@pytest.mark.parametrize("field",["schema_version","provenance","decision_authority"])
def test_wrong_editorial_origin_rejected(field):
    bad=copy.deepcopy(ORIGINAL)
    bad[field]="spoof"
    with pytest.raises(ValueError):
        B88.build(bad,BASE)

@pytest.mark.parametrize("field",["teacher_approved_complete_lessons","source_editorials_completed","semantic_equivalence_adjudicated_count"])
def test_wrong_census_is_not_silently_promoted(field):
    bad=copy.deepcopy(BASE)
    bad[field]=1
    with pytest.raises(ValueError):
        B88.build(ORIGINAL,bad)

def test_duplicate_relationship_and_shortened_material_rejected():
    bad=copy.deepcopy(ORIGINAL)
    bad["relations"][1]["left_candidate_id"]=bad["relations"][0]["left_candidate_id"]
    bad["relations"][1]["right_candidate_id"]=bad["relations"][0]["right_candidate_id"]
    with pytest.raises(ValueError,match="duplicate or swapped"):
        B88.build(bad,BASE)

def test_unrecognized_extra_json_keys_rejected():
    bad=copy.deepcopy(ORIGINAL)
    bad["relations"][0]["unreviewed_authority_spoof"]=True
    with pytest.raises(ValueError):
        B88.build(bad,BASE)

def test_duplicate_json_keys_rejected():
    with pytest.raises(ValueError,match="duplicate JSON object key"):
        json.loads('{"a":1,"a":2}',object_pairs_hook=B88.unique_pairs)

@pytest.mark.parametrize("op,values,expected",[
    ("MVT_QUADRATIC",(1,3,2), (Q(4),Q(4))),
    ("RIEMANN_RIGHT_SUM",(2,), (Q(3,4),Q(1,2))),
    ("SIGNED_VS_UNSIGNED_AREA",(), (0,1)),
    ("MATRIX_MULTIPLICATION_SHAPE",(2,3,3,1), (2,1)),
    ("LINEAR_SUBSPACE_AFFINE",(0,), {"contains_origin":True,"is_subspace":True}),
    ("UNIFORM_VARIANCE",(0,2), Q(1,3)),
    ("COVARIANCE_2D_POSITIVE_DEFINITE",(1,0,4), {"determinant":4,"positive_definite":True}),
    ("JOINT_DISTRIBUTION_INDEPENDENCE",(1,1,1,1), {
        "row_marginal":(Q(1,2),Q(1,2)),
        "col_marginal":(Q(1,2),Q(1,2)),
        "independent":True,
    }),
    ("CRAMER_DIAGONAL",(2,3,4,1,2,2), (Q(1),Q(2),Q(2))),
    ("SUFFICIENT_NOT_NECESSARY",(4,), {"divisible_by_4":True,"even":True}),
    ("STATIONARY_NONEXTREMUM",(0,), {"derivative_at_t":0,"x_cubed_has_local_extremum_at_t":False}),
])
def test_independent_exact_positive_witness(op,values,expected):
    result=evaluate(op,*values)
    assert result["status"]=="FINITE_EXACT_WITNESS"
    assert result["value"]==expected
    assert result["general_theorem_certified"] is False
    assert result["teacher_approved"] is False

@pytest.mark.parametrize("op,values,expected",[
    ("MVT_QUADRATIC",(1,3,0), "CONDITIONS_NOT_ESTABLISHED"),
    ("RIEMANN_RIGHT_SUM",(0,), "CONDITIONS_NOT_ESTABLISHED"),
    ("SIGNED_VS_UNSIGNED_AREA",(1,), "CONDITIONS_NOT_ESTABLISHED"),
    ("MATRIX_MULTIPLICATION_SHAPE",(2,3,2,1), "CONDITIONS_NOT_ESTABLISHED"),
    ("UNIFORM_VARIANCE",(1,1), "CONDITIONS_NOT_ESTABLISHED"),
    ("UNIFORM_VARIANCE",(2,1), "CONDITIONS_NOT_ESTABLISHED"),
    ("JOINT_DISTRIBUTION_INDEPENDENCE",(-1,0,0,1), "CONDITIONS_NOT_ESTABLISHED"),
    ("JOINT_DISTRIBUTION_INDEPENDENCE",(0,0,0,0), "CONDITIONS_NOT_ESTABLISHED"),
    ("CRAMER_DIAGONAL",(2,0,4,1,2,2), "CONDITIONS_NOT_ESTABLISHED"),
    ("MVT_QUADRATIC",(1,2,1), "CONDITIONS_NOT_ESTABLISHED"),
    ("MATRIX_MULTIPLICATION_SHAPE",(0,1,1,2), "CONDITIONS_NOT_ESTABLISHED"),
])
def test_guarded_negative_numeric_witness(op,values,expected):
    result=evaluate(op,*values)
    assert result["status"]==expected

@pytest.mark.parametrize("op,values",[
    ("COVARIANCE_2D_POSITIVE_DEFINITE",(1,2,1)),
    ("JOINT_DISTRIBUTION_INDEPENDENCE",(2,0,0,2)),
    ("RIEMANN_RIGHT_SUM",(5,)),
    ("SIGNED_VS_UNSIGNED_AREA",()),
    ("STATIONARY_NONEXTREMUM",(1,)),
])
def test_exact_witness_can_be_negative_without_claiming_general_proof(op,values):
    r=evaluate(op,*values)
    assert r["status"]=="FINITE_EXACT_WITNESS"
    assert r["comparison_result"] is False
    assert not r["general_theorem_certified"]

@pytest.mark.parametrize("op",SUPPORTED)
def test_bool_or_float_cannot_enter_exact_integer_witness(op):
    if op=="SIGNED_VS_UNSIGNED_AREA":
        assert evaluate(op,True)["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:
        assert evaluate(op,True)["status"]=="CONDITIONS_NOT_ESTABLISHED"
        assert evaluate(op,1.0)["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_unknown_or_injected_operation_is_not_a_model_verdict():
    assert evaluate("APPROVE_TEACHER",1)["status"]=="UNSUPPORTED"

def test_provisional_cross_track_editorials_never_enter_attested_student_rag(
        offline_reviewer_fixture):
    """A nonempty synthetic attested corpus still cannot leak editor-only comparisons."""
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc, _, _, _, record, save = offline_reviewer_fixture
    save([record(0), record(1)])
    assert approved_lesson_ids() == {doc.id}
    # Probe each of the 36 editorial pairs with its own original topic.
    for row in RESULT["reviewed_relations"]:
        response = student_evidence_lookup(row["left"]["topic"])
        payload = json.dumps(response, ensure_ascii=False)
        assert {h["knowledge_id"] for h in response.get("candidates", [])} <= {doc.id}
        assert row["review_id"] not in payload
        assert row["left_candidate_id"] not in payload
        assert row["right_candidate_id"] not in payload
        assert row["worked_witness"] not in payload
        assert row["failure_or_boundary"] not in payload
        assert response.get("teacher_solution_exposed") is not True
        assert response.get("unverified_content_exposed") is not True


@pytest.mark.parametrize("case", range(6))
def test_external_sympy_cross_checks_finite_examples(case):
    """Independently recompute six exact examples, not a general theorem proof."""
    import sympy as sp
    x = sp.symbols("x", real=True)
    if case == 0:
        assert sp.diff(x**2, x).subs(x, 2) == (3**2 - 1**2) / sp.Integer(3-1)
    elif case == 1:
        n = sp.symbols("n", integer=True, positive=True)
        assert sp.simplify(sp.summation(sp.Symbol("k"), (sp.Symbol("k"), 1, n))/n**2 - (n+1)/(2*n)) == 0
    elif case == 2:
        assert sp.integrate(sp.Abs(x), (x, -1, 1)) == 1
    elif case == 3:
        sigma = sp.Matrix([[1, 0], [0, 4]])
        assert sigma.det() == 4 and list(sigma.eigenvals()) == [1, 4]
    elif case == 4:
        A = sp.diag(2, 3, 4)
        b = sp.Matrix([2, 6, 8])
        assert list(A.inv() * b) == [1, 2, 2]
    elif case == 5:
        assert sp.diff(x**3, x).subs(x, 0) == 0
        assert sp.Rational(-1, 8) < 0 < sp.Rational(1, 8)
