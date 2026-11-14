"""Archive checks reject false command success, forged logs or source/data drift."""
from __future__ import annotations
import copy,hashlib,json,sys,shutil
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch157_execution_manifest as ev

@pytest.fixture(scope="module")
def manifest():
    data=json.loads(ev.OUT.read_text(encoding="utf-8"))
    assert data==ev.build()
    assert ev.REPORT.read_text(encoding="utf-8")==ev.markdown(data)
    return data

def test_report_generation_is_stable_under_canonical_json_roundtrip():
    """Archive report must not depend on insertion order vs JSON sort_keys."""
    fresh=ev.build()
    canonical=json.loads(ev.serialize(fresh))
    assert ev.markdown(fresh)==ev.markdown(canonical)

def test_archived_source_commit_and_nonpublication(manifest):
    assert manifest["source_commit"]==ev.SOURCE_COMMIT
    assert manifest["backend_passed"]==66293
    assert manifest["backend_skipped"]==5
    assert manifest["node_passed"]==111
    assert manifest["focused_passed"]==647
    assert manifest["focused_initial_errors"]==334
    assert manifest["independent_finite_math_witnesses"]==40
    assert manifest["general_proofs_certified"]==0
    assert manifest["teacher_approved"]==manifest["student_authoritative"]==0
    assert all(v is None for v in manifest["official_atom_denominators"].values())

@pytest.mark.parametrize("name",tuple(ev.CODE))
def test_every_mac_log_and_exit_sha256_are_real(name,manifest):
    r=manifest["runs"][name]
    original=ROOT/r["log_path"];exitfile=ROOT/r["exit_path"]
    assert original.is_file() and exitfile.is_file()
    assert len(original.read_bytes())==r["bytes"]
    assert hashlib.sha256(original.read_bytes()).hexdigest()==r["sha256"]
    assert hashlib.sha256(exitfile.read_bytes()).hexdigest()==r["exit_sha256"]
    assert int(exitfile.read_text().strip())==r["exit_code"]

@pytest.fixture(scope="module")
def copylogdir(tmp_path_factory):
    d=tmp_path_factory.mktemp("kb157_real_mac_forgeries")
    for kind in ev.CODE:
        for ext in ["log","exit"]:
            f=f"{ev.PREFIX}_{kind}.{ext}"
            shutil.copy2(ev.DIR/f,d/f)
    return d

@pytest.mark.parametrize("name",tuple(ev.CODE))
def test_corrupt_log_rejected(name,copylogdir):
    target=copylogdir/f"{ev.PREFIX}_{name}.log"
    old=target.read_bytes()
    try:
        target.write_bytes(b"FAKE PASS!\n")
        with pytest.raises(ValueError):ev.collect(copylogdir)
    finally:target.write_bytes(old)

@pytest.mark.parametrize("name",tuple(ev.CODE))
def test_false_command_exit_rejected(name,copylogdir):
    f=copylogdir/f"{ev.PREFIX}_{name}.exit"
    old=f.read_bytes()
    try:
        fake=(b"0\n" if ev.CODE[name]==1 else b"1\n")
        f.write_bytes(fake)
        with pytest.raises(ValueError):ev.collect(copylogdir)
    finally:f.write_bytes(old)

@pytest.mark.parametrize("name",tuple(ev.CODE))
def test_missing_stdout_rejected(name,copylogdir):
    f=copylogdir/f"{ev.PREFIX}_{name}.log"
    old=f.read_bytes()
    try:
        f.unlink()
        with pytest.raises(ValueError):ev.collect(copylogdir)
    finally:f.write_bytes(old)

@pytest.mark.parametrize("key,value",[
    ("backend_passed",0),
    ("focused_passed",9999),
    ("teacher_approved",165),
    ("general_proofs_certified",40),
    ("student_authoritative",1),
    ("official_atom_denominators",{"COMPULSORY":315}),
    ("source_commit","0"*40),
])
def test_mutated_json_manifest_not_accepted_as_current(key,value,manifest):
    altered=copy.deepcopy(manifest)
    altered[key]=value
    assert altered!=ev.build()

def test_all_five_archived_runs_present(manifest):
    assert set(manifest["runs"])==set(ev.CODE)
    assert manifest["runs"]["FOCUSED_INITIAL"]["exit_code"]==1
    assert all(x["exit_code"]==0 for key,x in manifest["runs"].items() if key!="FOCUSED_INITIAL")
