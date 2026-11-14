"""Negative tests for immutable archived Mac execution logs and non-authority policy."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
from shutil import copyfile
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch149_execution_manifest as archive

@pytest.fixture(scope="module")
def manifest():
    return json.loads(archive.OUT.read_text(encoding="utf-8"))

def stage_mac_log_pairs(tmp_path):
    d=tmp_path/"logs"
    d.mkdir()
    for label in archive.RUNS:
        for suffix in ("log","exit"):
            name=f"KB_BATCH149_{label}.{suffix}"
            copyfile(archive.LOG/name,d/name)
    return d

def test_original_four_mac_log_exit_sha_and_source_checks(manifest):
    assert manifest==archive.build()
    assert archive.render(manifest)==archive.REPORT.read_text(encoding="utf-8")
    assert len(manifest["logs"])==4
    assert manifest["source_git_commit"]==archive.SOURCE_SHA
    assert manifest["total_pending_teacher_drafts"]==105
    assert manifest["teacher_approved"]==manifest["student_authoritative"]==0
    assert all(x is None for x in manifest["official_atom_denominators"].values())

@pytest.mark.parametrize("label",list(archive.RUNS))
def test_log_and_exit_actual_sha256_match_archived_manifest(label,manifest):
    item=manifest["logs"][label]
    assert (ROOT/item["path"]).is_file() and (ROOT/item["exit_path"]).is_file()
    assert archive.sha((ROOT/item["path"]).read_bytes())==item["sha256"]
    assert archive.sha((ROOT/item["exit_path"]).read_bytes())==item["exit_sha256"]
    assert (ROOT/item["exit_path"]).read_text().strip()==str(item["exit"])

@pytest.mark.parametrize("label",list(archive.RUNS))
def test_missing_archived_log_rejected(label,tmp_path):
    stage_mac_log_pairs(tmp_path)
    (tmp_path/"logs"/f"KB_BATCH149_{label}.log").unlink()
    with pytest.raises(ValueError):
        archive.collect(tmp_path/"logs")

@pytest.mark.parametrize("label",list(archive.RUNS))
def test_false_exit_code_rejected(label,tmp_path):
    stage_mac_log_pairs(tmp_path)
    expected=archive.RUNS[label]
    (tmp_path/"logs"/f"KB_BATCH149_{label}.exit").write_text(str(1-expected)+"\n")
    with pytest.raises(ValueError):
        archive.collect(tmp_path/"logs")

@pytest.mark.parametrize("label,needle",[
    ("FOCUSED_INITIAL_FAILURE","1 failed, 404 passed"),
    ("FOCUSED","405 passed"),
    ("MAC_FULL","PASS Batch149 40/40 exact limited witnesses"),
    ("BROWSER","GREEN v0.7 Chrome test: 9 passed"),
])
def test_fake_positive_omitting_real_test_tag_rejected(label,needle,tmp_path):
    stage_mac_log_pairs(tmp_path)
    f=tmp_path/"logs"/f"KB_BATCH149_{label}.log"
    raw=f.read_text(encoding="utf-8")
    assert needle in raw
    f.write_text(raw.replace(needle,"FAKE_TEST_SUMMARY"),encoding="utf-8")
    with pytest.raises(ValueError):
        archive.collect(tmp_path/"logs")

@pytest.mark.parametrize("field,forged",[
    ("teacher_approved",1),("student_authoritative",1),
    ("general_formal_certifications",40),("full_official_census_completed",True),
    ("official_atom_denominators",{"ELECTIVE_E":1}),
    ("source_de_nonempty_lines",0),("independent_exact_math_witnesses",100),
    ("editorial_candidates_missing",0),("final_focused_passed",999),
])
def test_fake_manifest_scope_or_math_certification_rejected(field,forged,manifest):
    m=copy.deepcopy(manifest);m[field]=forged
    assert m!=archive.build()
