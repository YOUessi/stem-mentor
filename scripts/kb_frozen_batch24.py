"""Read exactly the frozen Batch24 draft IDs, not later additions.

Do not reinterpret a historical 287-draft audit as a live 307+ draft audit.
The versioned course matrix pins the original membership (including
multi-topic association duplicates). If an original draft goes missing, fail.
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

from app.deep_knowledge import lessons

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/evaluation/KB_BATCH24_COURSE_PROGRESS_MATRIX.json"
FROZEN_MANIFEST_SHA256 = "416961454ed515e7a80d0daafd382bc9d746eee93cc7f498f513eb506193d377"


def frozen_batch24_lessons():
    raw = MANIFEST.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FROZEN_MANIFEST_SHA256:
        raise ValueError("Frozen Batch24 course matrix bytes changed")
    snapshot = json.loads(raw.decode("utf-8"))
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
