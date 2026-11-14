"""Byte-level tamper rejection for archived genuine Mac KB151 evidence and authority gates."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
from shutil import copyfile
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch151_execution_manifest as archive

@pytest.fixture(scope="module")
def actual():
    return json.loads(archive.OUT.read_text(encoding="utf-8"))

def copy_logs(tmp_path):
    d=tmp_path/"archived-mac"
    d.mkdir()
    for name in archive.RUNS:
        for extension in ("log","exit"):
            orig=archive.LOG/f"KB_BATCH151_{name}.{extension}"
            copyfile(orig,d/orig.name)
    return d

def test_manifest_genuinely_replays_all_recorded_logs(actual):
    assert actual==archive.build()
    assert archive.render(actual)==archive.REPORT.read_text(encoding="utf-8")
    assert len(actual["logs"])==4
    assert actual["source_git_commit"]==archive.SOURCE_COMMIT
    assert actual["total_pending_teacher_manuscripts"]==115
    assert actual["teacher_approved"]==actual["student_authoritative"]==0
    assert all(x is None for x in actual["official_atom_denominators"].values())

@pytest.mark.parametrize("label",list(archive.RUNS))
def test_each_mac_stdout_and_exit_hash_replays(label,actual):
    row=actual["logs"][label]
    assert archive.sha((ROOT/row["path"]).read_bytes())==row["sha256"]
    assert archive.sha((ROOT/row["exit_path"]).read_bytes())==row["exit_sha256"]
    assert (ROOT/row["exit_path"]).read_text().strip()==str(row["exit"])

@pytest.mark.parametrize("label",list(archive.RUNS))
def test_missing_log_cannot_pass(label,tmp_path):
    d=copy_logs(tmp_path)
    (d/f"KB_BATCH151_{label}.log").unlink()
    with pytest.raises(ValueError):archive.collect(d)

@pytest.mark.parametrize("label",list(archive.RUNS))
def test_nonzero_exit_cannot_be_reported_green(label,tmp_path):
    d=copy_logs(tmp_path)
    (d/f"KB_BATCH151_{label}.exit").write_text("1\n")
    with pytest.raises(ValueError):archive.collect(d)

@pytest.mark.parametrize("label,needle",[
    ("FOCUSED","256 passed"),
    ("NODE","# pass 111"),
    ("BROWSER","GREEN v0.7 Chrome test: 9 passed"),
    ("MAC_FULL","PASS KB151 40/40 finite exact conditions"),
])
def test_forged_pass_tag_rejected(label,needle,tmp_path):
    d=copy_logs(tmp_path)
    f=d/f"KB_BATCH151_{label}.log"
    orig=f.read_text(encoding="utf-8")
    assert needle in orig
    f.write_text(orig.replace(needle,"UNVERIFIED_RESULT"),encoding="utf-8")
    with pytest.raises(ValueError):archive.collect(d)

@pytest.mark.parametrize("field,value",[
    ("teacher_approved",1),("student_authoritative",10),
    ("official_census_certified",True),("official_atom_denominators",{"ELECTIVE_E":115}),
    ("general_formal_proofs_certified",40),("finite_exact_math_cases",1),
    ("editorial_candidates_unlinked",0),("focused_python_passed",999),
    ("full_python_passed",0),("historical_math_conflicts_pending",0),
])
def test_fake_report_counts_cannot_be_reconstructed(field,value,actual):
    forged=copy.deepcopy(actual);forged[field]=value
    assert forged != archive.build()
