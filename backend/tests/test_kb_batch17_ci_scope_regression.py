"""Batch17 official-scope guard regression: editorial tags must not become certified themes."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import build_kb_coverage as audit


def test_pending_cross_track_editors_are_listed_without_fake_official_theme():
    report = audit.build()
    rows = {row["curriculum_id"]: row for row in report["curriculum"]}
    assert report["totals"]["legacy_engineering_topics"] == 161
    for index in range(151, 162):
        row = rows[f"HS-MATH-{index:03}"]
        assert row["editorial_theme_uncertified"] is True
        assert row["theme_high_level_match"] == "UNVERIFIED_EDITORIAL_CANDIDATE"
        assert row["official_atom_mapping_review"] == "PENDING"
        assert row["not_officially_verified_atom"] is True
    assert report["totals"]["official_explicit_elective_tracks_with_atom_mapping"] == 0


@pytest.mark.parametrize(
    "change",
    [
        {"status": "APPROVED"},
        {"editorial_objective_id": ""},
        {"source": {"mapping_type": "OFFICIAL", "teacher_review": "PENDING"}},
        {"source": {"mapping_type": "ENGINEERING_INTERPRETATION", "teacher_review": "APPROVED"}},
    ],
)
def test_untrusted_editorial_candidates_fail_closed(monkeypatch, change):
    original = audit.curriculum()
    subject = next(row for row in original if row["id"] == "HS-MATH-151")
    monkeypatch.setattr(audit, "curriculum", lambda: [dict(subject, **change)])
    with pytest.raises(ValueError, match="untrusted editorial curriculum candidate"):
        audit.build()


def test_unknown_non_editorial_compulsory_theme_is_still_rejected(monkeypatch):
    original = audit.curriculum()
    subject = next(row for row in original if row["id"] == "HS-MATH-151")
    monkeypatch.setattr(audit, "curriculum", lambda: [dict(subject, theme="编造的课标单元")])
    with pytest.raises(ValueError, match="unknown legacy level/theme"):
        audit.build()
