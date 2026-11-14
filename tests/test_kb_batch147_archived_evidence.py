"""Mutation regressions for four authentic Mac archived execution logs."""
import shutil,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch147_execution_manifest as manifest
@pytest.fixture()
def cloned(tmp_path,monkeypatch):
    for label in ("FOCUSED","K00_FOCUSED","MAC_FULL","BROWSER"):
        for suffix in ("log","exit"):
            s=manifest.LOG/f"KB_BATCH147_{label}.{suffix}"
            shutil.copy2(s,tmp_path/s.name)
    monkeypatch.setattr(manifest,"LOG",tmp_path)
    return tmp_path
def test_bounded_archive_identity(cloned):
    d=manifest.build()
    assert d["focused_tests_passed"]==283 and d["independent_k00_tests_passed"]==17
    assert d["linked_teacher_drafts"]==54 and d["unlinked_historical_leads"]==185
    assert d["k00_source_boundary_relation_records"]==89
    assert d["k00_source_boundary_distinct_pairs"]==69
    assert all(x is None for x in d["official_atom_denominators"].values())
    assert d["teacher_approvals"]==d["authoritative_student_publications"]==0
    assert d["general_formal_proof_certifications"]==0
def test_nonzero_mac_exit_fails_closed(cloned):
    (cloned/"KB_BATCH147_MAC_FULL.exit").write_text("1\n")
    with pytest.raises(ValueError,match="MAC_FULL execution nonzero"):
        manifest.build()
def test_missing_browser_log_fails_closed(cloned):
    (cloned/"KB_BATCH147_BROWSER.log").unlink()
    with pytest.raises(ValueError,match="BROWSER log or exit missing"):
        manifest.build()
def test_forged_focused_pass_count_fails(cloned):
    p=cloned/"KB_BATCH147_FOCUSED.log"
    t=p.read_text(); assert "283 passed" in t
    p.write_text(t.replace("283 passed","999 passed"))
    with pytest.raises(ValueError,match="283 combined focused passes"):
        manifest.build()
def test_fake_pdf_rehash_marker_fails(cloned):
    p=cloned/"KB_BATCH147_MAC_FULL.log"
    t=p.read_text(); assert "PDF REHASHED original lines PASS" in t
    p.write_text(t.replace("PDF REHASHED original lines PASS","PDF REHASHED original lines UNKNOWN"))
    with pytest.raises(ValueError,match="PDF REHASHED"):
        manifest.build()
def test_false_browser_fixtures_fail(cloned):
    p=cloned/"KB_BATCH147_BROWSER.log"
    t=p.read_text(); assert "GREEN v0.7 Chrome test: 9 passed" in t
    p.write_text(t.replace("GREEN v0.7 Chrome test: 9 passed","GREEN v0.7 Chrome test: 0 passed"))
    with pytest.raises(ValueError,match="nine Chrome interactive"):
        manifest.build()
