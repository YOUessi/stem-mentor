"""GitHub CI checks the committed evidence without pretending to possess the private syllabus PDF."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_kb_batch127_129_offline as checker

FILES = [
    "curriculum/highschool_math/k00_batch117_source_triage.json",
]
for batch, mod, data, locks, report in checker.BATCHES:
    FILES.extend([
        f"docs/evaluation/{data}",
        f"curriculum/highschool_math/{locks}",
        f"docs/evaluation/{report}",
    ])


@pytest.fixture
def snapshot(tmp_path: Path) -> Path:
    for name in FILES:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return tmp_path


def corrupt_json(base: Path, name: str, mutate) -> None:
    file = base / name
    data = json.loads(file.read_text(encoding="utf-8"))
    mutate(data)
    file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_committed_offline_gate_is_explicitly_non_source_replay(snapshot):
    result = checker.check(snapshot)
    assert result["all_committed_source_records"] == 84
    assert result["source_pdf_recomputed_in_ci"] is False
    assert result["source_hashes_recomputed_in_ci"] is False
    assert result["teacher_approvals"] == 0


def test_private_pdfkit_cache_is_not_required_for_offline_gate(snapshot, monkeypatch):
    monkeypatch.setattr(checker.syllabus, "CACHE", snapshot / "private-cache-does-not-exist.json")
    assert checker.check(snapshot)["all_committed_source_records"] == 84


@pytest.mark.parametrize("batch,filename", [
    (127, "KB_BATCH127_SOURCE_REVIEW.json"),
    (128, "KB_BATCH128_SEMANTIC_SPLIT_LEDGER.json"),
    (129, "KB_BATCH129_SCOPE_REVIEWS.json"),
])
def test_forged_teacher_approval_rejected(snapshot, batch, filename):
    name = f"docs/evaluation/{filename}"
    corrupt_json(snapshot, name, lambda x: x["records"][0].update({"teacher_status": "APPROVED"}))
    with pytest.raises((ValueError, AssertionError, KeyError)):
        checker.check(snapshot)


def test_forged_official_denominator_rejected(snapshot):
    name = "docs/evaluation/KB_BATCH129_SCOPE_REVIEWS.json"
    corrupt_json(snapshot, name, lambda x: x.update({"official_atom_denominator": 104}))
    with pytest.raises(ValueError):
        checker.check(snapshot)


def test_student_authoritative_rejected(snapshot):
    name = "docs/evaluation/KB_BATCH128_SEMANTIC_SPLIT_LEDGER.json"
    corrupt_json(snapshot, name, lambda x: x["records"][0].update({"student_authoritative": True}))
    with pytest.raises(ValueError):
        checker.check(snapshot)


def test_missing_line_lock_rejected(snapshot):
    name = "curriculum/highschool_math/k00_batch127_source_line_locks.json"
    corrupt_json(snapshot, name, lambda x: x.pop(next(iter(x))))
    with pytest.raises((ValueError, KeyError)):
        checker.check(snapshot)


def test_malformed_source_line_hash_rejected_even_if_same_in_record_and_lock(snapshot):
    lock_name = "curriculum/highschool_math/k00_batch129_source_line_locks.json"
    json_name = "docs/evaluation/KB_BATCH129_SCOPE_REVIEWS.json"
    lock = json.loads((snapshot / lock_name).read_text())
    key = next(iter(lock))
    lock[key]["line_sha256"][0] = "not-a-real-hash"
    (snapshot / lock_name).write_text(json.dumps(lock, ensure_ascii=False), encoding="utf-8")
    corrupt_json(snapshot, json_name,
                 lambda x: next(r for r in x["records"] if r["candidate_id"] == key)
                 ["source"]["line_sha256"].__setitem__(0, "not-a-real-hash"))
    with pytest.raises(ValueError):
        checker.check(snapshot)


def test_unlocked_source_reference_rejected(snapshot):
    name = "docs/evaluation/KB_BATCH127_SOURCE_REVIEW.json"
    corrupt_json(snapshot, name, lambda x: x["records"][0]["source"].update({"start_line": 900}))
    with pytest.raises(ValueError):
        checker.check(snapshot)


def test_pdf_fingerprint_rejected(snapshot):
    name = "docs/evaluation/KB_BATCH128_SEMANTIC_SPLIT_LEDGER.json"
    corrupt_json(snapshot, name, lambda x: x["records"][0].update({"source_pdf_sha256": "a" * 64}))
    with pytest.raises(ValueError):
        checker.check(snapshot)


def test_markdown_evidence_drift_rejected(snapshot):
    name = snapshot / "docs/evaluation/KB_BATCH129_SCOPE_REVIEWS.md"
    name.write_text(name.read_text(encoding="utf-8") + "\nAPPROVED\n", encoding="utf-8")
    with pytest.raises(ValueError):
        checker.check(snapshot)


def test_unexpected_extra_lock_rejected(snapshot):
    name = "curriculum/highschool_math/k00_batch129_source_line_locks.json"
    corrupt_json(snapshot, name, lambda x: x.update({"ghost-ID": next(iter(x.values()))}))
    with pytest.raises(ValueError):
        checker.check(snapshot)


def test_missing_committed_artifact_rejected(snapshot):
    (snapshot / "docs/evaluation/KB_BATCH128_SEMANTIC_SPLIT_LEDGER.json").unlink()
    with pytest.raises(ValueError):
        checker.check(snapshot)


def test_manifest_digest_drift_rejected(snapshot):
    name = "curriculum/highschool_math/k00_batch117_source_triage.json"
    corrupt_json(snapshot, name, lambda x: x.update({"source_pdf_sha256": "b" * 64}))
    with pytest.raises(ValueError):
        checker.check(snapshot)


def test_batch127_math_oracles_and_teacher_drafts_replayed_without_source_pdf():
    import build_kb_batch127_deep_lessons as deep
    records = json.loads(deep.OUT.read_text(encoding="utf-8"))
    frozen = json.loads(deep.CHECKS.read_text(encoding="utf-8"))
    assert deep.validate(records, regen=False)
    assert deep.build() == records
    assert deep.exact_checks() == frozen
    assert frozen["exact_worked_examples"] == 16
    assert frozen["independent_negative_cases"] == 8
    assert frozen["cross_topic_checks"] == 8
    assert frozen["general_theorems_formally_certified"] == 0


def test_batch128_p0_proof_guards_have_bounded_witnesses_not_certificates():
    import build_kb_batch128_p0_proof_guards as proof
    frozen = json.loads(proof.OUT.read_text(encoding="utf-8"))
    assert proof.validate(frozen, compare=False)
    assert proof.build() == frozen
    assert frozen["historical_formally_verified_steps"] == 0
    assert frozen["finite_exact_positive_cases"] == 20
    assert frozen["finite_exact_invalid_boundary_cases"] == 20
    assert all(not r["general_quantified_proof_certified"] and
               r["teacher_status"] == "REVIEW_PENDING" for r in frozen["records"])


def test_math_proof_promotion_mutations_fail():
    import copy
    import build_kb_batch128_p0_proof_guards as proof
    frozen = json.loads(proof.OUT.read_text(encoding="utf-8"))
    forged = copy.deepcopy(frozen)
    forged["records"][0]["historical_step_formally_certified"] = True
    with pytest.raises(ValueError):
        proof.validate(forged, compare=False)


def test_batch129_offline_math_works_when_private_replay_is_disabled(monkeypatch):
    import check_kb_batch129_offline_lessons as verifier
    import build_kb_batch129_scope_reviews as scope
    def private_unavailable():
        raise AssertionError("GitHub CI has no licensed syllabus cache")
    monkeypatch.setattr(scope, "build", private_unavailable)
    assert verifier.check()["independent_examples"] == 18
