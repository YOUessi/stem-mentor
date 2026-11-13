"""Review-only proofs: all hypotheses required and no automatic certification."""
import copy
import json
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch119_proof_reviews as b
import build_kb_batch119_semantic_pilot as sem
PROOFS=json.loads(b.OUT.read_text())
CANDIDATES={r["id"]:r for r in json.loads(sem.OUT.read_text())["candidates"]}

@pytest.mark.parametrize("proof",PROOFS,ids=lambda x:x["proof_review_id"])
def test_review_manuscript_is_linked_complete_unapproved(proof):
    assert proof["candidate_id"] in CANDIDATES
    assert proof["source"]==CANDIDATES[proof["candidate_id"]]["source"]
    assert proof["review_status"]=="REVIEW_PENDING"
    assert not proof["machine_general_proof_certified"]
    assert not proof["student_authoritative"]
    assert proof["solution_visibility"]=="TEACHER_ONLY"
    assert len(proof["hypotheses"])>=2
    assert len(proof["proof_steps"])>=3
    assert len(proof["boundary"])>=20
    assert len(proof["counterexample"])>=20

@pytest.mark.parametrize("edit",[
    lambda x:x[0].update(review_status="APPROVED"),
    lambda x:x[0].update(teacher_evidence="fabricated"),
    lambda x:x[0].update(machine_general_proof_certified=True),
    lambda x:x[0].update(student_authoritative=True),
    lambda x:x[0].update(solution_visibility="STUDENT"),
    lambda x:x[0].update(hypotheses=[]),
    lambda x:x[0].update(proof_steps=[]),
    lambda x:x[0].update(counterexample=""),
    lambda x:x[0].update(candidate_id="forged"),
    lambda x:x.append(copy.deepcopy(x[0])),
])
def test_proof_gate_rejects_forgery_and_missing_math(edit):
    data=copy.deepcopy(PROOFS)
    edit(data)
    with pytest.raises(ValueError):b.check(data)

def test_exact_witnesses_not_confused_with_universal_proofs():
    oracle=b.exact_oracles()
    assert oracle["finite_checks"]==17
    assert oracle["general_formal_proofs_certified"]==0
    assert PROOFS==b.generate()
    assert b.MD.read_text()==b.markdown(PROOFS)
