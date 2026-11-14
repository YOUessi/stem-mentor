"""Regression for archived Mac-only evidence replay (not Mac PDF re-extraction)."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch146_execution_manifest as manifest


@pytest.fixture()
def copied_archive(tmp_path, monkeypatch):
    """Use a scratch copy so tamper tests never mutate the original Mac logs."""
    for label in ("FOCUSED", "K00_FOCUSED", "MAC_FULL", "BROWSER"):
        for suffix in ("log", "exit"):
            source = manifest.LOG / f"KB_BATCH146_{label}.{suffix}"
            shutil.copyfile(source, tmp_path / source.name)
    monkeypatch.setattr(manifest, "LOG", tmp_path)
    return tmp_path


def test_archive_replay_proves_only_bounded_results(copied_archive):
    result = manifest.build()
    assert result["k00_alias_focused_tests_passed"] == 44
    assert result["cross_page_shared_cue_groups"] == 0
    assert result["official_atom_denominators"]
    assert all(v is None for v in result["official_atom_denominators"].values())
    assert result["teacher_approvals"] == 0
    assert result["student_authoritative_publications"] == 0
    assert result["general_formal_proof_certifications"] == 0


def test_nonzero_exit_is_never_accepted(copied_archive):
    (copied_archive / "KB_BATCH146_MAC_FULL.exit").write_text("1\n")
    with pytest.raises(ValueError, match="Mac run failed"):
        manifest.build()


def test_empty_k00_log_is_never_accepted(copied_archive):
    (copied_archive / "KB_BATCH146_K00_FOCUSED.log").write_text("")
    with pytest.raises(ValueError, match="truncated K00_FOCUSED"):
        manifest.build()


def test_forged_k00_pass_count_is_never_accepted(copied_archive):
    target = copied_archive / "KB_BATCH146_K00_FOCUSED.log"
    original = target.read_text()
    assert "44 passed" in original
    target.write_text(original.replace("44 passed", "43 passed"))
    with pytest.raises(ValueError, match="K00 alias 44 PASS absent"):
        manifest.build()


def test_fake_pdf_source_replay_marker_is_never_accepted(copied_archive):
    target = copied_archive / "KB_BATCH146_MAC_FULL.log"
    original = target.read_text()
    assert "PDF REHASHED original lines PASS" in original
    target.write_text(original.replace("PDF REHASHED original lines PASS", "PDF REHASHED original lines UNKNOWN"))
    with pytest.raises(ValueError, match="licensed original PDFKit SHA replay missing"):
        manifest.build()
