"""Reject forged approval, forged counts, missing bytes, or misleading Mac test claims."""
import copy
import json
import sys
from pathlib import Path
from shutil import copyfile
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch153_execution_manifest as evidence

@pytest.fixture(scope="module")
def manifest():
    return json.loads(evidence.MANIFEST.read_text(encoding="utf-8"))

def clone_logs(tmp_path):
    dest = tmp_path / "source-byte-evidence"
    dest.mkdir()
    for name in evidence.LOG_NAMES:
        for suffix in ("log", "exit"):
            file = evidence.LOGDIR / f"KB_BATCH153_{name}.{suffix}"
            copyfile(file, dest / file.name)
    return dest

def test_mac_attestation_and_exact_log_digest(manifest):
    assert evidence.build() == manifest
    assert evidence.render(manifest) == evidence.REPORT.read_text(encoding="utf-8")
    assert manifest["source_commit"] == evidence.SOURCE_COMMIT
    assert manifest["teacher_only_pending_drafts"] == 135
    assert manifest["teacher_approved"] == manifest["student_authoritative"] == 0
    assert manifest["official_completion_rate"] is None
    assert all(v is None for v in manifest["official_atom_denominators"].values())
    assert set(manifest["logs"]) == set(evidence.LOG_NAMES)

@pytest.mark.parametrize("name", evidence.LOG_NAMES)
def test_original_log_exit_byte_hashes_match(name, manifest):
    r = manifest["logs"][name]
    assert evidence.sha((ROOT / r["path"]).read_bytes()) == r["sha256"]
    assert evidence.sha((ROOT / r["exit_path"]).read_bytes()) == r["exit_sha256"]
    assert (ROOT / r["exit_path"]).read_bytes().strip() == b"0"

@pytest.mark.parametrize("name", evidence.LOG_NAMES)
def test_missing_original_log_fails_closed(name, tmp_path):
    d = clone_logs(tmp_path)
    (d / f"KB_BATCH153_{name}.log").unlink()
    with pytest.raises(ValueError):
        evidence.read_runs(d)

@pytest.mark.parametrize("name", evidence.LOG_NAMES)
def test_nonzero_exit_fails_closed(name, tmp_path):
    d = clone_logs(tmp_path)
    (d / f"KB_BATCH153_{name}.exit").write_text("1\n")
    with pytest.raises(ValueError):
        evidence.read_runs(d)

@pytest.mark.parametrize("name, phrase", [
    ("FOCUSED", "262 passed"),
    ("NODE", "# pass 111"),
    ("BROWSER", "GREEN v0.7 Chrome test: 9 passed"),
    ("MAC_FULL", "PASS KB153 finite exact math witnesses: 40/40"),
    ("MAC_FULL", "66293 passed, 5 skipped"),
])
def test_fake_green_claim_cannot_pass(name, phrase, tmp_path):
    d = clone_logs(tmp_path)
    f = d / f"KB_BATCH153_{name}.log"
    text = f.read_text(encoding="utf-8")
    assert phrase in text
    f.write_text(text.replace(phrase, "UNVERIFIED"), encoding="utf-8")
    with pytest.raises(ValueError):
        evidence.read_runs(d)

@pytest.mark.parametrize("key, value", [
    ("teacher_approved", 1),
    ("student_authoritative", 135),
    ("official_completion_rate", 1.0),
    ("official_atom_denominators", {"COMPULSORY": 135}),
    ("formal_general_proofs", 40),
    ("arbitrary_student_steps_certified", 262),
    ("historical_proof_steps_unverified", 0),
    ("mathematical_conflicts_pending", 0),
    ("source_gaps", 0),
    ("full_backend_passed", 99999),
])
def test_forged_manifest_not_reproducible(key, value, manifest):
    forged = copy.deepcopy(manifest)
    forged[key] = value
    assert forged != evidence.build()
