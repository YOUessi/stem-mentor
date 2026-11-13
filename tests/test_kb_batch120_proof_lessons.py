"""Independent editorial-proof and problem-family integrity checks; never auto-certify."""
from __future__ import annotations
import copy, json, sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch120_proof_lessons as proof
import build_kb_batch120_semantic_expansion as candidates
from app.deep_knowledge import public_summary
ROWS=json.loads(proof.OUT.read_text(encoding="utf-8"))
ATOMS={r["id"]:r for r in json.loads(candidates.OUT.read_text(encoding="utf-8"))["candidates"]}
MATH=json.loads(proof.MATH.read_text(encoding="utf-8"))

@pytest.mark.parametrize("row",ROWS,ids=lambda r:r["review_id"])
def test_six_condition_complete_teacher_only_proofs(row):
    assert row["candidate_id"] in ATOMS
    assert row["source"]==ATOMS[row["candidate_id"]]["source"]
    assert row["course_track"]==ATOMS[row["candidate_id"]]["course_track"]
    assert row["review_status"]=="REVIEW_PENDING"
    assert row["teacher_evidence"] is None
    assert row["general_formal_proof_certified"] is False
    assert row["student_authoritative"] is False
    assert row["visibility"]=="TEACHER_ONLY"
    assert len(row["hypotheses"])>=2
    assert len(row["proof_steps"])>=3
    assert all(len(s["justification"])>=17 for s in row["proof_steps"])
    assert len(row["boundary"])>=20 and len(row["counterexample"])>=25
    assert len(row["teacher_examples"])==2
    assert len(row["hint_ladder"])==3 and len(set(row["hint_ladder"]))==3
    assert "near" in row["transfer"] and "far" in row["transfer"]

@pytest.mark.parametrize("row",ROWS,ids=lambda r:r["review_id"])
def test_two_independently_checked_worked_examples_per_family(row):
    key=row["review_id"].rsplit("-",1)[1].upper()
    assert MATH["examples_by_candidate"][key]==2
    assert all(len(e["steps"])>=2 and len(e["check"])>=12 for e in row["teacher_examples"])
    assert proof.exact_examples()["examples_by_candidate"][key]==2

ATTACKS=[
    lambda r:r[0].update(review_status="APPROVED"),
    lambda r:r[0].update(teacher_evidence="fabricated"),
    lambda r:r[0].update(general_formal_proof_certified=True),
    lambda r:r[0].update(student_authoritative=True),
    lambda r:r[0].update(visibility="STUDENT"),
    lambda r:r[0].update(candidate_id="nonexistent"),
    lambda r:r[0].update(course_track="ELECTIVE_E"),
    lambda r:r[0].update(source={"tampered":True}),
    lambda r:r[0].update(hypotheses=[]),
    lambda r:r[0].update(proof_steps=[]),
    lambda r:r[0]["proof_steps"][0].update(justification="trust me"),
    lambda r:r[0].update(counterexample=""),
    lambda r:r[0].update(boundary=""),
    lambda r:r[0].update(teacher_examples=[]),
    lambda r:r[0]["teacher_examples"][0].update(check=""),
    lambda r:r[0].update(hint_ladder=["answer"]),
    lambda r:r[0].update(transfer={"near":"","far":""}),
    lambda r:r[0].update(claim="false mathematical claim"),
    lambda r:r[0]["proof_steps"][1].update(claim="altered"),
    lambda r:r.append(copy.deepcopy(r[0])),
]
@pytest.mark.parametrize("attack",ATTACKS,ids=[f"proof-tamper-{i:02d}" for i in range(len(ATTACKS))])
def test_incomplete_forged_or_rewritten_proof_rejected(attack):
    damaged=copy.deepcopy(ROWS)
    attack(damaged)
    with pytest.raises(ValueError):
        proof.validate(damaged)

def test_teacher_only_proofs_are_reproducible_and_not_in_student_authority():
    assert proof.validate(ROWS)
    assert proof.build()==ROWS
    assert proof.render(ROWS)==proof.MD.read_text(encoding="utf-8")
    assert proof.exact_examples()==MATH
    assert MATH["exact_teacher_example_checks"]==12
    assert MATH["general_formal_proofs_certified"]==MATH["teacher_approved"]==0
    summary=json.dumps(public_summary(),ensure_ascii=False)
    assert "kb120-proof-family" not in summary
    assert "kb_batch120_six_proof_families" not in summary
