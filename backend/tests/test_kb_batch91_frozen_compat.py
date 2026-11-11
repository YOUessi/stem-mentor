"""Batch91: historical audit membership must survive new drafts without forgery.

The frozen Batch24 source ledger is immutable. A replacement set of the same
cardinality is NOT the original audit. New pending drafts remain separate.
"""
from __future__ import annotations

import json

import pytest

from app.deep_knowledge import lessons
from scripts import kb_frozen_batch24 as frozen


def test_original_historical_membership_exact_and_extra_drafts_not_backdated():
    old = frozen.frozen_batch24_lessons()
    live = {d.id: d for d in lessons()}
    old_ids = {d.id for d in old}
    new_ids = {f"math.hs.batch91.{n:02d}" for n in range(1, 21)}
    assert len(old) == len(old_ids) == 287
    assert not new_ids & old_ids
    assert new_ids <= live.keys()
    assert old_ids <= live.keys()
    assert all(live[i].review.status == "REVIEW_PENDING" for i in old_ids | new_ids)
    assert all(live[i].teacher_solution_visibility == "TEACHER_ONLY"
               for i in old_ids | new_ids)


@pytest.mark.parametrize("mutation", ["same_count_id_replacement", "silently_append_whitespace"])
def test_frozen_manifest_rejects_in_place_forgery(tmp_path, monkeypatch, mutation):
    raw = frozen.MANIFEST.read_bytes()
    if mutation == "same_count_id_replacement":
        document = json.loads(raw)
        # New draft is real, but cannot replace an original in a frozen audit.
        ids = document["courses"][0]["structured_draft_ids"]
        assert ids and "math.hs.batch91.01" not in ids
        ids[0] = "math.hs.batch91.01"
        raw = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode()
    else:
        raw += b"\n"
    replacement = tmp_path / "misleading_batch24.json"
    replacement.write_bytes(raw)
    monkeypatch.setattr(frozen, "MANIFEST", replacement)
    with pytest.raises(ValueError, match="matrix bytes changed"):
        frozen.frozen_batch24_lessons()


def test_frozen_manifest_rejects_missing_original_content(monkeypatch):
    old = frozen.frozen_batch24_lessons()
    missing = old[0].id
    original = frozen.lessons
    monkeypatch.setattr(
        frozen, "lessons", lambda: tuple(d for d in original() if d.id != missing)
    )
    with pytest.raises(ValueError, match="Missing frozen Batch24 lesson IDs"):
        frozen.frozen_batch24_lessons()
