"""Read exactly the frozen Batch24 draft IDs, not later additions.

Do not reinterpret a historical 287-draft audit as a live 307+ draft audit.
The versioned course matrix pins the original membership (including
multi-topic association duplicates). If an original draft goes missing, fail.
"""
from __future__ import annotations

import json
from pathlib import Path

from app.deep_knowledge import lessons

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/evaluation/KB_BATCH24_COURSE_PROGRESS_MATRIX.json"


def frozen_batch24_lessons():
    snapshot = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if snapshot["schema_version"] != "batch24-course-completeness-v1":
        raise ValueError("Unknown historical Batch24 manifest version")
    rows = snapshot["courses"]
    ids = {doc_id for row in rows for doc_id in row["structured_draft_ids"]}
    if len(rows) != 178 or len(ids) != 287:
        raise ValueError("Historical Batch24 manifest membership drift")
    live = {doc.id: doc for doc in lessons()}
    missing = ids - live.keys()
    if missing:
        raise ValueError(f"Missing frozen Batch24 lesson IDs: {sorted(missing)[:5]}")
    return tuple(doc for doc in lessons() if doc.id in ids)
