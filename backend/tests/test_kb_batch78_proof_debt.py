"""538 frozen natural-language proof obligations; guarded math and student RAG."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch78_proof_review as B
from app.kb_batch78_math import CASE_OPS,GOOD,BAD,check

@pytest.fixture(scope="module")
def pack():
    return B.build()

def test_source_review_matrix_is_deterministic_and_not_approved(pack):
    assert B.OUT.read_text(encoding="utf8")==B.serialize(pack)
    assert B.CARDS.read_text(encoding="utf8")==B.serialize(pack["review_cards"])
    assert B.MD.read_text(encoding="utf8")==B.markdown(pack)
    x=pack["summary"]
    assert x["historical_proof_steps"]==x["claim_and_reason_sha_verified"]==538
    assert x["source_counts"]=={"BATCH18":451,"BATCH21":23,"BATCH22":23,"BATCH23":22,"BATCH24":19}
    assert x["p0_unverified_steps"]==127
    assert x["new_teacher_review_cards"]==16 and x["new_teacher_only_example_tasks"]==32
    assert x["bounded_exact_positive_witnesses"]==x["bounded_invalid_assumptions_rejected"]==16
    assert x["formally_certified_steps"]==x["whole_theorem_certifications"]==0
    assert x["teacher_approvals"]==x["free_text_student_steps_verified"]==x["student_published"]==0
    assert x["full_page_human_atomizations"]==0
    assert x["historical_conflicts_unresolved"]==10
    assert len(x["official_atomic_denominators"])==7
    assert all(v is None for v in x["official_atomic_denominators"].values())

@pytest.mark.parametrize("idx",range(538))
def test_every_one_of_538_source_proofs_is_reconciled_but_uncertified(idx,pack):
    row=pack["proof_obligations"][idx]
    assert row["status"]=="NOT_FORMALLY_VERIFIED" and row["teacher_review"]=="PENDING"
    assert not row["student_publishable"] and not row["student_step_verified"] and not row["whole_proof_certified"]
    assert len(row["original_step_sha256"])==64 and len(row["source_file_sha256"])==64
    assert row["original_step_sha256"]!=row["source_file_sha256"]

@pytest.mark.parametrize("idx",range(16))
def test_each_real_high_risk_step_has_complete_distinct_guard_card(idx,pack):
    card=pack["review_cards"][idx]
    assert card["id"]==f"KB78-P{idx+1:02}"
    assert len(card["assumptions"])>=2 and len(card["proof_steps"])==3
    assert len(card["worked_examples"])==2 and len(card["hint_ladder"])==3
    assert card["invalid_boundary"] and card["common_wrong_method"]
    assert card["near_transfer"] and card["far_transfer"]
    assert card["review_status"]=="REVIEW_PENDING"
    assert card["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert card["formal_math_certification"]=="NOT_FORMALLY_VERIFIED"
    assert card["reviewer_id"] is None and card["official_curriculum_atom_id"] is None
    assert not card["student_publishable"] and not card["student_free_text_verified"]
    assert all(z["visibility"]=="TEACHER_ONLY" for z in card["worked_examples"])
    source={r["id"]:r for r in pack["proof_obligations"]}[card["linked_historical_step_id"]]
    assert source["origin"]=="BATCH18" and source["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE"
    assert source["original_step_sha256"]==card["original_step_sha256"]

@pytest.mark.parametrize("op",CASE_OPS)
def test_independent_exact_math_fixtures_accept_supported_valid_case(op):
    status,evidence=check(op,GOOD[op])
    assert status=="VERIFIED_FINITE_INSTANCE" and evidence

@pytest.mark.parametrize("op",CASE_OPS)
def test_illegal_math_assumptions_do_not_pass(op):
    status,evidence=check(op,BAD[op])
    assert status=="CONDITIONS_NOT_ESTABLISHED"
    assert evidence["failed_condition"]

@pytest.mark.parametrize("op",CASE_OPS)
def test_no_float_or_bool_can_masquerade_as_exact_input(op):
    x=deepcopy(GOOD[op])
    first=next(iter(x))
    x[first]=1.0
    with pytest.raises(ValueError):check(op,x)
    x=deepcopy(GOOD[op])
    x[first]=True
    with pytest.raises(ValueError):check(op,x)

@pytest.mark.parametrize("idx",range(16))
@pytest.mark.parametrize("field,value",[
 ("teacher_solution_visibility","STUDENT"),
 ("formal_math_certification","FORMALLY_VERIFIED"),
 ("reviewer_id","fake_teacher"),
 ("student_publishable",True),
 ("student_free_text_verified",True),
 ("official_curriculum_atom_id","FAKE-001"),
 ("original_step_sha256","0"*64),
 ("invalid_boundary",""),
 ("near_transfer",""),
 ])
def test_unapproved_teacher_cards_and_lineage_reject_mutations(idx,field,value,pack):
    cards=deepcopy(pack["review_cards"])
    cards[idx][field]=value
    with pytest.raises(ValueError):B.validate_cards(cards,pack["proof_obligations"])

@pytest.mark.parametrize("idx",range(16))
def test_mathematical_probe_cannot_be_swapped_or_invalid_case_relabelled(idx,pack):
    cards=deepcopy(pack["review_cards"])
    cards[idx]["bounded_invalid_input"]=deepcopy(GOOD[CASE_OPS[idx]])
    with pytest.raises(ValueError):B.validate_cards(cards,pack["proof_obligations"])
    cards=deepcopy(pack["review_cards"])
    cards[idx]["bounded_valid_input"]=deepcopy(BAD[CASE_OPS[idx]])
    with pytest.raises(ValueError):B.validate_cards(cards,pack["proof_obligations"])

@pytest.mark.parametrize("batch",["BATCH18","BATCH21","BATCH22","BATCH23","BATCH24"])
def test_historical_step_hash_tampering_rejected(batch):
    rel,key=next((r,k) for n,r,k,_ in B.PARTS if n==batch)
    tampered=B.read(ROOT/rel)
    attr="content_sha256" if batch=="BATCH23" else "claim_reason_sha256"
    tampered[key][0][attr]="0"*64
    with pytest.raises(ValueError):B.ledger(parts_override={batch:tampered})

@pytest.mark.parametrize("batch",["BATCH18","BATCH21","BATCH22","BATCH23","BATCH24"])
def test_removed_historical_step_or_forged_approval_rejected(batch):
    rel,key=next((r,k) for n,r,k,_ in B.PARTS if n==batch)
    tampered=B.read(ROOT/rel)
    tampered[key].pop()
    with pytest.raises(ValueError):B.ledger(parts_override={batch:tampered})
    tampered=B.read(ROOT/rel)
    tampered[key][0]["student_publishable"]=True
    with pytest.raises(ValueError):B.ledger(parts_override={batch:tampered})

@pytest.mark.parametrize("case,expected",[
 ({"a":2,"b":1,"x":8},"CONDITIONS_NOT_ESTABLISHED"),
 ({"a":2,"b":4,"x":1},"VERIFIED_FINITE_INSTANCE"),
 ])
def test_change_base_extreme_parameters(case,expected):
    assert check("change_base",case)[0]==expected

@pytest.mark.parametrize("case,count",[
 ({"r":5,"y":-6},0),({"r":5,"y":-5},1),({"r":5,"y":0},2),
 ({"r":5,"y":5},1),({"r":5,"y":6},0)])
def test_circle_endpoint_and_tangent_completeness(case,count):
    state,ev=check("circle",case)
    assert state=="VERIFIED_FINITE_INSTANCE" and ev["intersection_count"]==count

@pytest.mark.parametrize("case,expect",[
 ({"a":1,"b":-2,"c":1},1),({"a":1,"b":0,"c":1},0),
 ({"a":1,"b":0,"c":-1},2)])
def test_quadratic_distinct_real_roots_by_discriminant(case,expect):
    state,ev=check("quadratic",case)
    assert state=="VERIFIED_FINITE_INSTANCE" and ev["distinct_real_roots"]==expect

@pytest.mark.parametrize("bad",[
 {"A":[[1,2],[3,4.0]]}, {"A":[[1,2],[3]]}, {"A":[[1,2,3],[3,4,5]]}])
def test_invalid_matrix_shapes_and_floats_fail_closed(bad):
    with pytest.raises(ValueError):check("inverse2",bad)

from test_attested_release_batch08 import offline_reviewer_fixture
@pytest.mark.parametrize("idx",range(16))
def test_teacher_proof_cards_never_enter_nonempty_student_approved_index(idx,pack,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    card=pack["review_cards"][idx]
    response=student_evidence_lookup(card["mathematical_topic"])
    output=json.dumps(response,ensure_ascii=False)
    assert {r["knowledge_id"] for r in response["candidates"]}<={doc.id}
    assert card["id"] not in output
    assert card["worked_examples"][0]["teacher_solution"] not in output
    assert card["worked_examples"][1]["teacher_solution"] not in output
    assert response["teacher_solution_exposed"] is False
    assert response["unverified_content_exposed"] is False


# Independent combinatorial ground truth: enumerate actual draw sets rather than
# reusing the implementation's binomial-coefficient formula.
from itertools import combinations
from fractions import Fraction

@pytest.mark.parametrize("N,K,n",[
    (5,2,2), (5,0,3), (5,5,4), (6,3,3),
    (7,2,4), (8,4,3), (8,1,7), (9,5,2),
])
def test_hypergeometric_matches_exhaustive_unordered_draw_enumeration(N,K,n):
    draws=list(combinations(range(N),n))
    for k in range(max(0,n-N+K),min(n,K)+1):
        expected=Fraction(sum(sum(item<K for item in d)==k for d in draws),len(draws))
        status,proof=check("hypergeometric",{"N":N,"K":K,"n":n,"k":k})
        assert status=="VERIFIED_FINITE_INSTANCE"
        assert Fraction(proof["probability"])==expected
    assert sum(Fraction(check("hypergeometric",{"N":N,"K":K,"n":n,"k":k})[1]["probability"])
               for k in range(max(0,n-N+K),min(n,K)+1))==1

@pytest.mark.parametrize("op",["conditional","complement"])
@pytest.mark.parametrize("duplicate_field",["A","B"])
def test_probability_events_reject_duplicate_outcomes(op,duplicate_field):
    case=deepcopy(GOOD[op])
    case[duplicate_field].append(case[duplicate_field][0])
    result,evidence=check(op,case)
    assert result=="CONDITIONS_NOT_ESTABLISHED"
    assert evidence["failed_condition"]=="duplicated_event_outcome"

@pytest.mark.parametrize("op",["conditional","complement"])
def test_probability_event_fields_reject_non_lists(op):
    case=deepcopy(GOOD[op])
    case["A"]=tuple(case["A"])
    with pytest.raises(ValueError,match="enumerated lists"):check(op,case)

@pytest.mark.parametrize("a,b",[(2,4),(3,9),(4,2),(5,25)])
def test_log_change_of_base_at_one_is_exact(a,b):
    status,evidence=check("change_base",{"a":a,"b":b,"x":1})
    assert status=="VERIFIED_FINITE_INSTANCE" and evidence["difference"]=="0"



@pytest.mark.parametrize("idx,notation",[(8,"||n||"),(12,"P(B|A)"),(15,"|u·n|")])
def test_mathematical_absolute_values_norms_and_conditional_bar_survive_serialization(idx,notation,pack):
    steps=[r["claim_and_reason"] for r in pack["review_cards"][idx]["proof_steps"]]
    assert len(steps)==3 and notation in "".join(steps)
    assert all(len(r)>=10 for r in steps)

@pytest.mark.parametrize("idx",range(16))
def test_partial_or_corrupt_proof_step_cannot_be_accepted(idx,pack):
    rows=pack["proof_obligations"]
    cards=deepcopy(pack["review_cards"])
    cards[idx]["proof_steps"][0]["claim_and_reason"]=""
    with pytest.raises(ValueError):B.validate_cards(cards,rows)
    cards=deepcopy(pack["review_cards"])
    cards[idx]["proof_steps"].pop()
    with pytest.raises(ValueError):B.validate_cards(cards,rows)
