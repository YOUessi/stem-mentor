"""Regression: scope filtering cannot be truncated by global top-k FTS results."""
from __future__ import annotations
import sqlite3
from types import SimpleNamespace

import pytest
from app import deep_retrieval as dr


def test_filtered_lookup_returns_document_beyond_first_100_global_hits(monkeypatch):
    # All 140 documents share a term, but only item #140 has the requested
    # curriculum ID. A global FTS LIMIT 100 followed by scope filtering fails.
    docs = tuple(
        SimpleNamespace(
            id=f"math.hs.synthetic.test{i:03d}",
            title="函数",
            kind="theorem",
            curriculum_ids=[f"HS-MATH-{i:03d}"],
            review=SimpleNamespace(status="REVIEW_PENDING"),
        )
        for i in range(1,141)
    )
    db = sqlite3.connect(":memory:")
    db.execute('CREATE VIRTUAL TABLE evidence USING fts5(title, body, tokenize="unicode61")')
    db.executemany("INSERT INTO evidence(title,body) VALUES(?,?)",
                   [("函数", "函数") for _ in docs])
    db.commit()
    monkeypatch.setattr(dr,"lessons",lambda:docs)
    monkeypatch.setattr(dr,"_index",lambda:db)
    found=dr.editor_draft_search(
        "函数",scope="EDITOR_LOCAL",
        curriculum_ids=("HS-MATH-140",),limit=3)
    assert len(found)==1
    assert found[0]["knowledge_id"]=="math.hs.synthetic.test140"
    assert found[0]["condition_status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert not {"proof_steps","worked_examples","teacher_solution"} & set(found[0])


@pytest.mark.parametrize("bad_query",["", "\n", "\x00", "x"*161])
def test_scope_checked_before_any_full_draft_exposure(bad_query):
    with pytest.raises((ValueError, dr.EditorOnlyError)):
        dr.editor_draft_search(bad_query)
    with pytest.raises(ValueError):
        dr.student_evidence_lookup(bad_query)


def test_editor_scope_is_not_authentication_and_never_part_of_http_routes():
    from app.main import app
    assert not any("editor" in route.path.lower() for route in app.routes)
    with pytest.raises(dr.EditorOnlyError):
        dr.editor_draft_full("math.hs.sequence.recurrence-initial")
