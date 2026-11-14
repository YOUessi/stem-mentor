"""Mac log archive negative controls; source/test success must not be forged."""
from pathlib import Path
import copy
import json
import shutil
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch158_execution_manifest as audit

@pytest.fixture
def archive(tmp_path):
    for name in audit.KIND:
        for src in audit.paths(name):
            assert src.exists()
            shutil.copy2(src,tmp_path/src.name)
    return tmp_path

def test_real_manifest_binds_byte_exact_logs_and_source():
    frozen=json.loads(audit.OUT.read_text(encoding="utf-8"))
    assert frozen==audit.build()
    assert frozen["source_commit"]==audit.SOURCE_COMMIT
    assert frozen["python_backend_full_passed"]>=66000
    assert frozen["pending_drafts"]==175
    assert frozen["teacher_approved"]==frozen["student_authoritative"]==0
    assert all(x is None for x in frozen["official_atom_denominators"].values())
    assert audit.REPORT.read_text(encoding="utf-8")==audit.markdown(frozen)

@pytest.mark.parametrize("kind",tuple(audit.KIND))
def test_forged_nonzero_exit_rejected(kind,archive):
    f=audit.paths(kind,archive)[1]
    f.write_bytes(b"1\n")
    with pytest.raises(ValueError,match="nonzero exit"):
        audit.read_logs(archive)

@pytest.mark.parametrize("kind",tuple(audit.KIND))
def test_missing_stdout_rejected(kind,archive):
    audit.paths(kind,archive)[0].unlink()
    with pytest.raises(ValueError,match="missing paired stdout"):
        audit.read_logs(archive)

@pytest.mark.parametrize("kind",tuple(audit.KIND))
def test_truncated_stdout_rejected(kind,archive):
    f=audit.paths(kind,archive)[0]
    f.write_bytes(b"passing\n")
    with pytest.raises(ValueError):
        audit.read_logs(archive)

@pytest.mark.parametrize("kind",tuple(audit.KIND))
def test_fake_positive_outcome_rejected(kind,archive):
    f=audit.paths(kind,archive)[0]
    raw=f.read_bytes()
    if kind=="NODE": raw=raw.replace(b"# pass 111",b"# pass 110")
    elif kind=="FOCUSED":raw=raw.replace(b"728 passed",b"727 passed")
    elif kind=="COMBINED":raw=raw.replace(b"769 passed",b"768 passed")
    elif kind=="BROWSER":raw=raw.replace(b"Chrome browser suite passed",b"Chrome browser suite failed")
    elif kind=="MAC_FULL":
        # remove source check sentinel, and leave successful test count intact
        raw=raw.replace(b"PASS KB158",b"FAIL KB158")
    f.write_bytes(raw)
    with pytest.raises(ValueError,match="verified outcome|private source"):
        audit.read_logs(archive)

@pytest.mark.parametrize("field,bad",[
    ("teacher_approved",1),("student_authoritative",1),
    ("official_atom_denominators",{"COMPULSORY":315}),
    ("remote_ci_final_result","success"),("pending_drafts",999)])
def test_manifest_fake_review_or_ci_claim_rejected(field,bad):
    frozen=audit.build()
    frozen[field]=bad
    assert frozen!=audit.build()
