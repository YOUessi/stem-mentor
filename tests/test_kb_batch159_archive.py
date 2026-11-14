"""KB159 actual Mac test evidence: archive integrity and fail-closed controls.

The archived stdout/exit pairs are factual evidence, not proof of math or approval.
Tests deliberately alter isolated *copies* and never touch the Mac originals.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch159_execution_manifest as audit

NAMES = tuple(audit.REQUIRED)


@pytest.fixture
def archive(tmp_path):
    for name in NAMES:
        for suffix in (".stdout.log", ".exit"):
            src = audit.LOGDIR / f"{name}{suffix}"
            assert src.is_file(), f"actual Mac evidence missing: {src}"
            shutil.copy2(src, tmp_path / src.name)
    return tmp_path


def test_byte_exact_mac_manifest_and_no_false_course_or_teacher_completion():
    frozen = json.loads(audit.OUT.read_text(encoding="utf-8"))
    assert frozen == audit.build()
    assert frozen["source_commit"] == "fd10511c80d284a72be11fcc936a310704271603"
    assert frozen["python_full_passed"] == 66418
    assert frozen["python_full_skipped"] == 5
    assert frozen["node_full_passed"] == 111
    assert frozen["official_atom_denominators_known"] is False
    assert frozen["general_proof_certified"] is False
    assert frozen["teacher_approved"] == 0
    assert frozen["student_authoritative"] == 0
    assert frozen["test_suites_overlap_not_additive"] is True
    assert len(frozen["logs"]) == 5


@pytest.mark.parametrize("name", NAMES)
def test_missing_stdout_rejected(name, archive):
    (archive / f"{name}.stdout.log").unlink()
    with pytest.raises(ValueError, match="missing stdout"):
        audit.build(archive)


@pytest.mark.parametrize("name", NAMES)
def test_nonzero_exit_rejected(name, archive):
    (archive / f"{name}.exit").write_bytes(b"1\\n")
    with pytest.raises(ValueError, match="nonzero/forged exit"):
        audit.build(archive)


@pytest.mark.parametrize("name", NAMES)
def test_empty_or_truncated_stdout_rejected(name, archive):
    (archive / f"{name}.stdout.log").write_bytes(b"PASS\\n")
    with pytest.raises(ValueError, match="missing/truncated stdout"):
        audit.build(archive)


@pytest.mark.parametrize("name", NAMES)
def test_forged_test_count_or_pass_sentinel_rejected(name, archive):
    replacements = {
        "FOCUSED": (b"125 passed", b"124 passed"),
        "PDFKIT": (b"PASS KB159 10 full compulsory function drafts", b"FAIL KB159 10 full compulsory function drafts"),
        "MATH": (b"PASS KB159 20 independently calculated", b"FAIL KB159 20 independently calculated"),
        "BROWSER": (b"Chrome PASS", b"Chrome FAIL"),
        "MAC_FULL": (b"66418 passed", b"66417 passed"),
    }
    needle, forged = replacements[name]
    target = archive / f"{name}.stdout.log"
    original = target.read_bytes()
    assert needle in original, f"actual sentinel absent: {name}"
    target.write_bytes(original.replace(needle, forged))
    with pytest.raises(ValueError, match="missing required real PASS/test count"):
        audit.build(archive)


@pytest.mark.parametrize("bad", [
    {"teacher_approved": 1},
    {"student_authoritative": 1},
    {"official_atom_denominators_known": True},
    {"general_proof_certified": True},
    {"python_full_passed": 999999},
])
def test_forged_review_coverage_or_results_not_equal_to_frozen_manifest(bad):
    frozen = audit.build()
    forged = frozen | bad
    assert forged != audit.build()
