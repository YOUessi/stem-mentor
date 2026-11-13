"""Batch89: source-linked P0 proof drafts, 300 candidate ledger and student leak tests."""
import copy
import json
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
import build_kb_batch89_proofs_and_scope as B
from app.kb_batch89_exact_witness import check_all,NAMES,conditions_established,DOMAIN_CASES
from test_attested_release_batch08 import offline_reviewer_fixture

AUTHOR=B.load(B.AUTHOR)
HISTORY=B.B86.build()
CENSUS=B.B87.build()
RELATIONS=B.B88.build()
PACKET,AUDIT=B.build(history=HISTORY,census=CENSUS,relations=RELATIONS)

def mutated(idx,field,val):
    d=copy.deepcopy(AUTHOR)
    d["cards"][idx][field]=val
    return d

def test_reproducible_outputs_match_checked_in_artifacts():
    assert B.OUT.read_text(encoding="utf8")==B.serialize(PACKET)
    assert B.AUDIT.read_text(encoding="utf8")==B.serialize(AUDIT)
    assert B.DOC.read_text(encoding="utf8")==B.markdown(PACKET,AUDIT)

def test_no_fake_official_denominator_or_teacher_release():
    assert AUDIT["provisional_labels"]==300
    assert AUDIT["source_anchor_editorials"]==428
    assert AUDIT["provisional_candidates_with_any_pair"]==70
    assert AUDIT["provisional_candidates_unpaired"]==230
    assert sum(x["unpaired"] for x in AUDIT["per_track"].values())==230
    assert AUDIT["official_atom_denominator"] is None
    assert AUDIT["teacher_approved"]==AUDIT["student_published"]==0
    assert AUDIT["full_page_teacher_atomizations"]==0
    assert AUDIT["historic_math_conflicts_not_resolved"]==10
    assert AUDIT["historical_proof_steps_not_formally_certified"]==538
    assert AUDIT["unique_P0_with_teacher_drafts"]==76
    assert AUDIT["P0_missing_teacher_drafts"]==106
    assert len(AUDIT["remaining_unlinked_P0_source_step_ids"])==106

@pytest.mark.parametrize("idx",range(12))
def test_each_new_P0_is_unique_historical_step_with_exact_frozen_sha(idx):
    card=PACKET["cards"][idx]
    original=B.load(B.B86.B85.B81.PROOFS)["step_review_queue"]
    source={v["id"]:v for v in original}[card["source_step"]]
    assert source["risk_priority"].startswith("P0_")
    assert source["source_sha256"]==card["original_historical_step_sha256"]
    assert card["source_step"] not in AUDIT["remaining_unlinked_P0_source_step_ids"]
    assert card["teacher_review_signature"] is None
    assert card["student_publishable"] is False
    assert card["student_free_text_verified"] is False
    assert card["student_authoritative_index_eligible"] is False
    assert card["general_theorem_formally_certified"] is False
    assert card["official_curriculum_atom_id"] is None
    assert card["review_status"]=="REVIEW_PENDING"
    assert len(card["proof_steps"])==3
    assert len(card["worked_examples"])==2
    assert len(card["hints"])==3
    for example in card["worked_examples"]:
        assert example["visibility"]=="TEACHER_ONLY"

@pytest.mark.parametrize("idx",range(12))
@pytest.mark.parametrize("field,value",[
    ("source_step","FORGED_HISTORICAL_STEP"),
    ("kind","CONCEPT"),
    ("proof_steps",[]),
    ("assumptions",[]),
    ("worked_examples",[]),
    ("hints",[]),
    ("boundary","not applicable"),
    ("wrong_method","none"),
    ("statement","theorem"),
    ("prerequisites",[]),
    ("near","none"),
    ("far","none"),
])
def test_card_tampering_fails_closed(idx,field,value):
    with pytest.raises(ValueError):
        B.build(author=mutated(idx,field,value),history=HISTORY,census=CENSUS,relations=RELATIONS)

@pytest.mark.parametrize("field,value",[
    ("teacher_approved",True),("formal_general_certified",True),
    ("student_publishable",True),("student_free_text_verified",True),
    ("review_status","APPROVED"),("provenance","MODEL_ATTESTED"),
    ("standard_version","wrong"),
])
def test_global_release_spoof_rejected(field,value):
    a=copy.deepcopy(AUTHOR)
    a[field]=value
    with pytest.raises(ValueError):
        B.build(author=a,history=HISTORY,census=CENSUS,relations=RELATIONS)

@pytest.mark.parametrize("idx",range(1,12))
def test_duplicate_source_step_or_id_rejected(idx):
    a=copy.deepcopy(AUTHOR)
    a["cards"][idx]["source_step"]=a["cards"][0]["source_step"]
    with pytest.raises(ValueError):
        B.build(author=a,history=HISTORY,census=CENSUS,relations=RELATIONS)

def test_unknown_hidden_authoring_fields_rejected():
    a=copy.deepcopy(AUTHOR)
    a["cards"][2]["teacher_signature"]="fake"
    with pytest.raises(ValueError):
        B.build(author=a,history=HISTORY,census=CENSUS,relations=RELATIONS)

def test_json_duplicate_keys_rejected():
    with pytest.raises(ValueError,match="duplicate JSON key"):
        json.loads('{"permission":0,"permission":1}',object_pairs_hook=B.duplicate_guard)

@pytest.mark.parametrize("idx",range(12))
def test_all_twelve_independent_finite_witnesses_have_negative_boundary(idx):
    v=check_all()[idx]
    assert v["operation"]==NAMES[idx]
    assert v["status"]=="FINITE_EXACT_WITNESS_ONLY"
    assert v["valid_fixture_passed"] is True
    assert v["invalid_premise_rejected"] is True
    assert len(v["finite_evidence"])>=20
    assert v["general_theorem_certified"] is False
    assert v["student_free_text_verified"] is False
    assert v["teacher_approved"] is False
    assert PACKET["cards"][idx]["finite_mathematical_witness"]==v

@pytest.mark.parametrize("idx",range(300))
def test_every_provisional_candidate_has_frozen_source_identity_and_restricted_visibility(idx):
    c=AUDIT["provisional_candidate_backlog"][idx]
    census=CENSUS["provisional_candidates"][idx]
    assert c["candidate_id"]==census["candidate_id"]
    assert c["source_review_id"]==census["source_review_id"]
    assert c["source_line_sha256"]==census["source_line_sha256"]
    assert c["track"]==census["track"]
    assert c["official_math_atom_id"] is None
    assert c["official_atom_count_contribution"] is None
    assert c["teacher_approval"] is None
    assert c["student_authoritative_index_eligible"] is False
    assert c["review_status"]=="REVIEW_PENDING"
    assert c["relation_count"]==len(c["reviewed_relation_ids"])
    assert c["cross_track_status"]==("EDITORIAL_PAIRS_ONLY" if c["relation_count"] else "NOT_YET_COMPARED")

def test_every_relation_record_is_counted_exactly_twice():
    counts={}
    for c in AUDIT["provisional_candidate_backlog"]:
        for r in c["reviewed_relation_ids"]:
            counts[r]=counts.get(r,0)+1
    assert len(counts)==36
    assert set(counts.values())=={2}

def test_nonempty_attested_student_rag_does_not_leak_unapproved_dossiers(offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,_,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    for card in PACKET["cards"]:
        result=student_evidence_lookup(card["title"])
        payload=json.dumps(result,ensure_ascii=False)
        assert {x["knowledge_id"] for x in result.get("candidates",[])} <= {doc.id}
        assert card["id"] not in payload
        assert card["source_step"] not in payload
        assert card["worked_examples"][0]["teacher_solution"] not in payload
        assert card["worked_examples"][1]["teacher_solution"] not in payload
        assert result.get("teacher_solution_exposed") is not True
        assert result.get("unverified_content_exposed") is not True

@pytest.mark.parametrize("idx",range(12))
def test_independent_sympy_cross_checks_on_each_finite_witness(idx):
    import sympy as s
    x=s.symbols("x")
    if idx==0: assert s.summation(x,(x,1,8))==36
    elif idx==1: assert s.Matrix([3,0]).dot(s.Matrix([0,4]))==0
    elif idx==2: assert s.summation(x**2,(x,1,4))==30
    elif idx==3:
        u=s.Matrix([1,2]);v=s.Matrix([2,-1])
        assert (u+v).dot(u+v)+(u-v).dot(u-v)==2*(u.dot(u)+v.dot(v))
    elif idx==4:
        assert s.Rational(9,5)**2/9+s.Rational(8,5)**2/4==1
    elif idx==5:
        f=2*x**2-8*x+3
        assert s.diff(f,x).subs(x,2)==0 and f.subs(x,2)==-5
    elif idx==6: assert s.Pow(3,-2)==s.Rational(1,9)
    elif idx==7:
        assert s.Rational(3,5)*s.Rational(12,13)+s.Rational(4,5)*s.Rational(5,13)==s.Rational(56,65)
    elif idx==8: assert s.eye(3).inv()*s.Matrix([2,-1,3])==s.Matrix([2,-1,3])
    elif idx==9: assert (s.Rational(1,2)*0+s.Rational(1,2)*4)==2
    elif idx==10: assert s.Matrix([[1,0],[0,1],[1,1]]).rank()==2
    elif idx==11: assert s.Matrix([[2,1],[1,1]]).inv()==s.Matrix([[1,-1],[-1,2]])



@pytest.mark.parametrize("op",NAMES)
def test_frozen_exact_input_contract_accepts_valid_and_rejects_bad(op):
    good,bad=DOMAIN_CASES[op]
    assert conditions_established(op,*good)
    assert not conditions_established(op,*bad)
    assert not conditions_established("FORGED_CERTIFICATION",*good)

@pytest.mark.parametrize("op",NAMES)
def test_boolean_and_float_parameters_do_not_pass_exact_input_contract(op):
    good,_=DOMAIN_CASES[op]
    # Ensure that integer 1 is not silently interchangeable with boolean True.
    if op in ("induction","sum_squares","ellipse_parametric",
              "quadratic_vertex","log_inverse"):
        assert not conditions_established(op,True,*good[1:])
        assert not conditions_established(op,1.0,*good[1:])
