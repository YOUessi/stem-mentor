"""Independent boundary checks of the source-page-anchored editorial checklist."""
import copy
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "curriculum/highschool_math/source_anchored_skill_candidates_batch12.json"
MODULE = ROOT / "scripts/build_kb_batch12_source_crosswalk.py"

@pytest.fixture(scope="module")
def inventory():
    return json.loads(SOURCE.read_text(encoding="utf-8"))

def test_reproducible_source_candidate_build():
    result = subprocess.run(
        [sys.executable, str(MODULE), "--check"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

def test_sample_does_not_claim_official_completeness(inventory):
    assert inventory["is_complete_official_atomic_inventory"] is False
    assert inventory["verified_official_atomic_denominator"] is None
    assert inventory["summary"]["remaining_official_coverage_unknown"] is True
    assert inventory["summary"]["teacher_approved"] == 0
    assert inventory["summary"]["active_deep_lesson_links"] == 0

@pytest.mark.parametrize("track,low,high", [
    ("COMPULSORY",13,35),("SELECTIVE_COMPULSORY",36,50),
    ("ELECTIVE_A",51,57),("ELECTIVE_B",58,63),
    ("ELECTIVE_C",64,68),("ELECTIVE_D",69,72),
    ("ELECTIVE_E",73,73),
])
def test_each_track_has_correct_printed_page_scope(inventory,track,low,high):
    items = [x for x in inventory["items"] if x["track"] == track]
    assert items and all(low <= x["source"]["printed_page"] <= high for x in items)
    assert inventory["summary"]["by_track"][track] == len(items)

def test_editorial_ids_are_unique_and_not_approved(inventory):
    items = inventory["items"]
    assert len(items) == 132
    assert len({v["id"] for v in items}) == len(items)
    assert all(v["teacher_review"] == "PENDING" for v in items)
    assert all(v["linked_deep_lesson_ids"] == [] for v in items)
    assert all(v["verified_official_atom_id"] is None for v in items)

@pytest.mark.parametrize("term", [
  "集合","导数","数列","ε","矩阵","逻辑","统计","音乐","体育","概率",
])
def test_cross_track_objectives_have_specific_content(inventory,term):
    assert any(term in x["editorial_learning_objective"] or term in x["section"]
               for x in inventory["items"])

from app.standard_scope import validate_source_inventory, public_progress
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.parametrize("modifier",[
  lambda d:d.update(is_complete_official_atomic_inventory=True),
  lambda d:d.update(verified_official_atomic_denominator=86),
  lambda d:d["items"][0].update(teacher_review="APPROVED"),
  lambda d:d["items"][0].update(verified_official_atom_id="unverified-claim"),
  lambda d:d["items"][0].update(linked_deep_lesson_ids=["math.hs.proof.induction"]),
  lambda d:d["items"][0].update(content_status="APPROVED_DEEP_LESSON"),
  lambda d:d["items"][0]["source"].update(printed_page=999),
  lambda d:d["items"][0]["source"].update(passage_review="TEACHER_REVIEW_DONE"),
  lambda d:d["items"][1].update(id=d["items"][0]["id"]),
  lambda d:d["items"][0].update(track="ELECTIVE_A"),
  lambda d:d["summary"].update(candidate_learning_objectives=999),
  lambda d:d["summary"].update(teacher_approved=1),
  lambda d:d["summary"].update(remaining_official_coverage_unknown=False),
],ids=[f"false-claim-{n:02d}" for n in range(13)])
def test_reject_fabricated_scope_review_or_approval(inventory,modifier):
    forged=copy.deepcopy(inventory)
    modifier(forged)
    with pytest.raises(ValueError):
        validate_source_inventory(forged)

def test_public_progress_only_counts_not_content():
    with TestClient(app) as client:
        result=client.get("/api/knowledge/standard-progress")
        assert result.status_code==200
        assert result.json()==public_progress()
        assert result.json()["official_atomic_denominator"] is None
        assert result.json()["teacher_approved"]==0
        assert result.json()["student_knowledge_released"]==0
        assert result.json()["complete_curriculum"] is False
        assert "editorial_learning_objective" not in result.text
        assert "proof_steps" not in result.text
        assert client.post("/api/knowledge/standard-progress").status_code==405
