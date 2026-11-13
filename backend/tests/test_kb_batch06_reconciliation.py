"""Batch06 independent provenance and non-overwrite regression."""
from __future__ import annotations
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import pytest
from app.deep_knowledge import lessons
from app.deep_retrieval import editor_draft_search, student_evidence_lookup, EditorOnlyError

ROOT = Path(__file__).resolve().parents[2]
ROOT_SOURCE = ROOT / "knowledge/deep/candidates/batch02"
REPORT = ROOT / "docs/evaluation/KB_BATCH02_RECONCILIATION.json"

def load():
    return json.loads(REPORT.read_text(encoding="utf-8"))

def sha(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()

def test_39_candidate_records_partition_into_29_and_10():
    r=load()
    assert r["scope"] == "EDITORIAL_CANDIDATE_MERGE_NOT_MATH_CERTIFICATION"
    assert r["summary"] == {
        "source_candidates":39,"nonconflicting_imports":29,"held_for_review":10,
        "published_active_lessons_after_import":159,"still_teacher_approved":0,
        "candidate_conflicts_automatically_resolved":0,
    }
    candidates=[x for f in ROOT_SOURCE.glob("*batch02.json") for x in json.loads(f.read_text())]
    assert len(candidates)==len({x["id"] for x in candidates})==39
    assert len(r["new_lesson_ids"])==29
    assert len(r["unresolved_conflicts"])==10
    assert not (set(r["new_lesson_ids"]) & {x["id"] for x in r["unresolved_conflicts"]})

@pytest.mark.parametrize("entry",load()["unresolved_conflicts"],ids=lambda x:x["id"])
def test_all_10_conflicts_are_held_and_preserve_source_proofs(entry):
    source=json.loads((ROOT/entry["candidate_source"]).read_text())
    original=next(x for x in source if x["id"]==entry["id"])
    existing=json.loads((ROOT/entry["existing_source"]).read_text())
    preserved=next(x for x in existing if x["id"]==entry["id"])
    assert sha(original)==entry["candidate_sha256"]
    assert sha(preserved)==entry["existing_sha256"]
    assert entry["status"]=="OPEN_EDITORIAL_CONFLICT_NOT_PROMOTED"
    assert original!=preserved and entry["differing_fields"]
    assert "review" not in entry.get("resolution",{})
    assert next(x for x in lessons() if x.id==entry["id"]).title==preserved["title"]

@pytest.mark.parametrize("lesson_id",load()["new_lesson_ids"])
def test_imported_is_unreviewed_has_proof_or_definition_and_teacher_only(lesson_id):
    doc=next(x for x in lessons() if x.id==lesson_id)
    assert doc.review.status=="REVIEW_PENDING"
    assert doc.teacher_solution_visibility=="TEACHER_ONLY"
    assert doc.provenance.permission=="PROJECT_AUTHORED"
    assert len(doc.worked_examples)>=2
    assert doc.counterexamples and doc.misconceptions and doc.hint_ladder
    if doc.kind=="theorem":
        assert doc.statement and len(doc.proof_steps)>=3
    else:
        assert doc.definition or doc.statement

@pytest.mark.parametrize("query",[
    "正弦定理", "独立事件", "线面平行", "正态分布", "三角函数振幅",
    "null", "' OR 1=1 --", "A⊥B", "数学模型验证"
])
def test_editor_draft_retrieval_never_exposes_teacher_proofs(query):
    with pytest.raises(EditorOnlyError):
        editor_draft_search(query)
    found=editor_draft_search(query,scope="EDITOR_LOCAL")
    assert all(set(hit).isdisjoint({"proof_steps","worked_examples","teacher_solution"}) for hit in found)
    assert all(hit["condition_status"]=="CONDITIONS_NOT_ESTABLISHED" for hit in found)
    result=student_evidence_lookup(query)
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert not result["candidates"] and result["teacher_solution_exposed"] is False

def test_reconciliation_build_reproducible_and_not_student_http_route():
    result=subprocess.run([sys.executable,str(ROOT/"scripts/reconcile_kb_batch02.py"),"--check"],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0, result.stderr+result.stdout
    from app.main import app
    paths={r.path for r in app.routes}
    assert "/api/knowledge/depth/coverage" in paths
    assert not any("editor" in p or "draft" in p and "knowledge" in p for p in paths)
