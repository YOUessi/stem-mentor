"""Negative and audit tests for Batch154 immutable real-Mac evidence; no synthetic success logs."""
import copy
import json
import sys
from pathlib import Path
from shutil import copyfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch154_execution_manifest as evidence

@pytest.fixture(scope="module")
def manifest():
    return json.loads(evidence.MANIFEST.read_text(encoding="utf-8"))

def clone_logs(tmp_path):
    output = tmp_path / "bytes"
    output.mkdir()
    for n in evidence.LOG_NAMES:
        for ext in ("log", "exit"):
            src = evidence.LOGDIR / f"KB_BATCH154_{n}.{ext}"
            copyfile(src, output / src.name)
    return output

def test_actual_manifest_matches_recomputed_evidence(manifest):
    assert evidence.build() == manifest
    assert evidence.render(manifest) == evidence.REPORT.read_text(encoding="utf-8")
    assert manifest["source_commit"] == evidence.SOURCE_COMMIT
    assert manifest["pending_teacher_manuscripts"] == 145
    assert manifest["source_links"] + manifest["source_gaps"] == 239
    assert manifest["teacher_approved"] == manifest["student_authoritative"] == 0
    assert all(v is None for v in manifest["official_atom_denominators"].values())
    assert manifest["official_completion_rate"] is None

@pytest.mark.parametrize("n", evidence.LOG_NAMES)
def test_original_logs_and_exit_sha256_immutable(n, manifest):
    item = manifest["logs"][n]
    assert (ROOT / item["exit_path"]).read_bytes().strip() == b"0"
    assert evidence.digest((ROOT / item["exit_path"]).read_bytes()) == item["exit_sha256"]
    assert evidence.digest((ROOT / item["path"]).read_bytes()) == item["sha256"]

@pytest.mark.parametrize("n", evidence.LOG_NAMES)
def test_missing_log_or_exit_fails_closed(n, tmp_path):
    d = clone_logs(tmp_path)
    (d / f"KB_BATCH154_{n}.log").unlink()
    with pytest.raises(ValueError):
        evidence.read_runs(d)

@pytest.mark.parametrize("n", evidence.LOG_NAMES)
def test_failed_exit_fails_closed(n, tmp_path):
    d = clone_logs(tmp_path)
    (d / f"KB_BATCH154_{n}.exit").write_text("1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        evidence.read_runs(d)

@pytest.mark.parametrize("n,pattern", [
    ("FOCUSED", "828 passed"),
    ("NODE", "# pass 111"),
    ("BROWSER", "IPAD PILOT CHROME PASS 9"),
    ("MAC_FULL", "PASS KB154 exact bounded math witnesses 40/40"),
    ("MAC_FULL", "66293 passed, 5 skipped"),
])
def test_claim_without_original_success_is_rejected(n, pattern, tmp_path):
    d = clone_logs(tmp_path)
    p = d / f"KB_BATCH154_{n}.log"
    s = p.read_text(encoding="utf-8")
    assert pattern in s
    p.write_text(s.replace(pattern, "UNVERIFIED"), encoding="utf-8")
    with pytest.raises(ValueError):
        evidence.read_runs(d)

@pytest.mark.parametrize("key,false_value", [
    ("teacher_approved", 1),
    ("student_authoritative", 145),
    ("official_completion_rate", 1.0),
    ("official_atom_denominators", {"COMPULSORY": 145}),
    ("historical_uncertified_proof_steps", 0),
    ("pending_math_conflicts", 0),
    ("general_formal_proof_certificates", 40),
    ("arbitrary_student_proof_steps_certified", 40),
    ("source_gaps", 0),
    ("backend_passed", 99999),
])
def test_forged_manifest_cannot_match_actual_source(key, false_value, manifest):
    altered = copy.deepcopy(manifest)
    altered[key] = false_value
    assert altered != evidence.build()
