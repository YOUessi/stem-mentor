"""Do not trust fabricated Mac test green text, staged byte hashes, or teacher approvals."""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
from shutil import copyfile
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch150_execution_manifest as archive

@pytest.fixture(scope="module")
def evidence():
    d=json.loads(archive.OUT.read_text(encoding="utf-8"))
    assert d==archive.build()
    return d

def stage(tmp_path):
    folder=tmp_path/"logs"
    folder.mkdir()
    for name in archive.RUNS:
        for ext in ("log","exit"):
            filename=f"KB_BATCH150_{name}.{ext}"
            copyfile(archive.LOG/filename,folder/filename)
    return folder

def test_exact_mac_original_evidence_matches_versioned_report(evidence):
    assert archive.REPORT.read_text(encoding="utf-8")==archive.render(evidence)
    assert evidence["source_line_count"]==122
    assert evidence["provisional_semantic_topics"]==32
    assert evidence["source_line_owner_counts"]["ELECTIVE_E"]==10
    assert evidence["new_finished_manuscripts"]==0
    assert evidence["pending_teacher_drafts_from_upstream"]==105
    assert not evidence["teacher_approved"] and not evidence["student_authoritative"]
    assert all(v is None for v in evidence["approved_official_atom_denominators"].values())

@pytest.mark.parametrize("name",archive.RUNS)
def test_archived_real_log_exit_bytes_and_sha(evidence,name):
    r=evidence["logs"][name]
    log=ROOT/r["log_file"];ex=ROOT/r["exit_file"]
    assert archive.hashbytes(log.read_bytes())==r["log_sha256"]
    assert archive.hashbytes(ex.read_bytes())==r["exit_sha256"]
    assert ex.read_text(encoding="utf-8").strip()=="0"

@pytest.mark.parametrize("name",archive.RUNS)
def test_missing_mac_log_rejected(name,tmp_path):
    d=stage(tmp_path)
    (d/f"KB_BATCH150_{name}.log").unlink()
    with pytest.raises(ValueError):
        archive.collect(d)

@pytest.mark.parametrize("name",archive.RUNS)
def test_nonzero_exit_rejected_even_if_stdout_claims_green(name,tmp_path):
    d=stage(tmp_path)
    (d/f"KB_BATCH150_{name}.exit").write_text("1\n",encoding="utf-8")
    with pytest.raises(ValueError):
        archive.collect(d)

@pytest.mark.parametrize("name,needle",[
    ("FOCUSED","36 passed"),
    ("MAC_FULL","KB150 original Mac PDFKit SHA replay PASS"),
    ("MAC_FULL","66293 passed, 5 skipped"),
    ("MAC_FULL","# pass 111"),
    ("BROWSER","GREEN v0.7 Chrome test: 9 passed"),
    ("BROWSER","Chrome browser suite passed"),
])
def test_forged_success_summary_rejected(name,needle,tmp_path):
    d=stage(tmp_path)
    f=d/f"KB_BATCH150_{name}.log"
    data=f.read_text(encoding="utf-8")
    assert needle in data
    f.write_text(data.replace(needle,"FAKE_GREEN"),encoding="utf-8")
    with pytest.raises(ValueError):
        archive.collect(d)

@pytest.mark.parametrize("field,forged",[
    ("teacher_approved",32),("student_authoritative",1),
    ("general_formal_proofs_certified",32),
    ("new_finished_manuscripts",32),
    ("approved_official_atom_denominators",{"ELECTIVE_E":13}),
    ("provisional_semantic_topics",500),
])
def test_false_manifest_authority_or_scope_rejected(field,forged,evidence):
    modified=copy.deepcopy(evidence)
    modified[field]=forged
    assert modified!=archive.build()
