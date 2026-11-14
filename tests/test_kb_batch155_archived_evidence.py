"""KB155 authentic Mac evidence: log hashes, exit codes, and nonapproval."""
from __future__ import annotations
import copy,json,shutil,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch155_execution_manifest as ev
@pytest.fixture(scope="module")
def verified():
    raw=ev.OUT.read_text(encoding="utf-8")
    data=json.loads(raw)
    assert raw==ev.encode(ev.build())
    assert ev.REPORT.read_text(encoding="utf-8")==ev.render(data)
    assert data["source_commit"]==ev.SOURCE_COMMIT
    assert data["mac_backend_passed"]==66293 and data["mac_backend_skipped"]==5
    assert data["focused_passed"]==917 and data["node_passed"]==111
    assert data["independently_checked_exact_math_cases"]==30
    assert data["teacher_approved"]==data["student_authoritative"]==0
    assert data["official_course_completion_rate"] is None
    return data
@pytest.fixture
def copied_logs(tmp_path):
    for name in ev.LOG_NAMES:
        for suffix in ("log","exit"):
            path=ev.LOG_DIR/f"{ev.PREFIX}_{name}.{suffix}"
            shutil.copyfile(path,tmp_path/path.name)
    return tmp_path
@pytest.mark.parametrize("name",ev.LOG_NAMES)
def test_original_stdout_and_exit_sha256(name,verified):
    r=verified["logs"][name]
    assert ev.sha((ROOT/r["path"]).read_bytes())==r["sha256"]
    assert ev.sha((ROOT/r["exit_path"]).read_bytes())==r["exit_sha256"]
    assert r["exit_code"]==0
@pytest.mark.parametrize("name",ev.LOG_NAMES)
def test_missing_log_rejected(name,copied_logs):
    (copied_logs/f"{ev.PREFIX}_{name}.log").unlink()
    with pytest.raises(ValueError):ev.read_runs(copied_logs)
@pytest.mark.parametrize("name",ev.LOG_NAMES)
def test_fake_green_rejected(name,copied_logs):
    (copied_logs/f"{ev.PREFIX}_{name}.log").write_text("PASS forged\n")
    with pytest.raises(ValueError):ev.read_runs(copied_logs)
@pytest.mark.parametrize("name",ev.LOG_NAMES)
def test_nonzero_exit_rejected(name,copied_logs):
    (copied_logs/f"{ev.PREFIX}_{name}.exit").write_text("1\n")
    with pytest.raises(ValueError):ev.read_runs(copied_logs)
@pytest.mark.parametrize("name",ev.LOG_NAMES)
def test_fake_counts_or_pdf_replay_rejected(name,copied_logs):
    path=copied_logs/f"{ev.PREFIX}_{name}.log"
    s=path.read_text(encoding="utf-8")
    edits={
      "FOCUSED":("917 passed","999 passed"),
      "NODE":("# pass 111","# pass 112"),
      "BROWSER":("Chrome browser suite passed","Chrome browser suite FAILED"),
      "MAC_FULL":("Mac PDFKit source rehash PASS","not validated"),
    }
    old,new=edits[name];assert old in s
    path.write_text(s.replace(old,new),encoding="utf-8")
    with pytest.raises(ValueError):ev.read_runs(copied_logs)
@pytest.mark.parametrize("key,val",[
    ("teacher_approved",1),("student_authoritative",1),
    ("general_formal_theorem_certificates",30),("official_course_completion_rate",1.0)])
def test_forgeries_must_not_equal_verified_record(key,val,verified):
    clone=copy.deepcopy(verified);clone[key]=val
    assert clone!=ev.build()

