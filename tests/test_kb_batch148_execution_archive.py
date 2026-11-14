"""Batch148 immutable Mac logs/exit tamper negatives, without opening licensed PDF."""
from __future__ import annotations
import hashlib,json,shutil,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch148_execution_manifest as archive

@pytest.fixture(scope="module")
def evidence():
    return archive.build()

def test_original_byte_logs_manifest_and_human_report_match(evidence):
    assert json.loads(archive.OUT.read_text(encoding="utf-8"))==evidence
    assert archive.REPORT.read_text(encoding="utf-8")==archive.render(evidence)
    assert len(evidence["logs"])==3
    assert evidence["focused_python_passed"]==730
    assert evidence["full_backend_python_passed"]==66293
    assert evidence["node_passed"]==111
    assert evidence["math_finite_oracles_passed"]==40
    assert evidence["teacher_approved"]==0
    assert all(x is None for x in evidence["official_atom_denominators"].values())

@pytest.mark.parametrize("name",archive.NAMES)
def test_real_logs_and_exits_sha_are_recomputed(name,evidence):
    rec=evidence["logs"][name]
    src=ROOT/rec["path"];ex=ROOT/rec["exit_path"]
    assert ex.read_text(encoding="utf-8").strip()=="0"
    assert hashlib.sha256(src.read_bytes()).hexdigest()==rec["sha256"]
    assert hashlib.sha256(ex.read_bytes()).hexdigest()==rec["exit_sha256"]
    assert src.stat().st_size==rec["bytes"]

@pytest.mark.parametrize("name",archive.NAMES)
@pytest.mark.parametrize("mutation",("truncate","fake_success","bad_exit","missing_exit"))
def test_fake_or_mutated_mac_log_cannot_pass_archive_check(name,mutation,tmp_path):
    for file in archive.LOG.glob("KB_BATCH148_*.*"):
        if file.suffix in (".log",".exit") and any("_"+n+"." in file.name for n in archive.NAMES):
            shutil.copy2(file,tmp_path/file.name)
    log=tmp_path/f"KB_BATCH148_{name}.log";ex=tmp_path/f"KB_BATCH148_{name}.exit"
    if mutation=="truncate":log.write_text("730 passed; 66293 passed; 111 passed",encoding="utf-8")
    elif mutation=="fake_success":log.write_text(log.read_text(encoding="utf-8")+"\nFAKE 999 PASSED\n",encoding="utf-8")
    elif mutation=="bad_exit":ex.write_text("1\n",encoding="utf-8")
    elif mutation=="missing_exit":ex.unlink()
    # For fake-success that preserves all original lines, collector passes; immutable SHA must fail.
    if mutation=="fake_success":
        mutated=archive.build(tmp_path)
        assert mutated!=json.loads(archive.OUT.read_text(encoding="utf-8"))
        assert mutated["logs"][name]["sha256"]!=archive.build()["logs"][name]["sha256"]
    else:
        with pytest.raises(ValueError):archive.collect(tmp_path)

@pytest.mark.parametrize("field,value",[
  ("teacher_approved",1),("official_atomic_census_complete",True),
  ("unresolved_version_conflicts",0),("math_finite_oracles_passed",999),
  ("new_deep_manuscripts",95)])
def test_archive_authority_and_count_forgery_changes_record(field,value,evidence):
    clone=dict(evidence);clone[field]=value
    assert clone!=archive.build()
