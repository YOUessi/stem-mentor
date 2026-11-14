"""KB156 authentic Mac execution artifacts: no fake green, test counts, or teacher approval."""
from __future__ import annotations
import copy,json,shutil,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch156_execution_manifest as archive

@pytest.fixture(scope="module")
def snapshot():
    obj=json.loads(archive.MANIFEST.read_text(encoding="utf-8"))
    assert archive.MANIFEST.read_text(encoding="utf-8")==(
        json.dumps(archive.build(),ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n")
    assert archive.REPORT.read_text(encoding="utf-8")==archive.render(obj)
    return obj

def test_mac_execution_manifest_includes_original_first_failure(snapshot):
    assert snapshot["source_commit"]==archive.SOURCE_COMMIT
    assert (snapshot["backend_passed"],snapshot["backend_skipped"],
            snapshot["node_passed"],snapshot["focused_passed"])==(66293,5,111,273)
    assert (snapshot["initial_focused_failed"],snapshot["initial_focused_passed"])==(10,263)
    assert snapshot["independent_bounded_sympy_cases"]==40
    assert snapshot["added_teacher_only_manuscripts"]==10
    assert snapshot["total_teacher_only_manuscripts"]==155
    assert (snapshot["editorial_with_teacher_draft"],
            snapshot["editorial_without_teacher_draft"])==(114,125)
    assert snapshot["real_teacher_approved"]==snapshot["student_authoritative_releases"]==0
    assert snapshot["formal_general_proof_certifications"]==0
    assert snapshot["official_course_completion_rate"] is None
    assert all(x is None for x in snapshot["official_atom_denominators"].values())
    assert set(snapshot["logs"])==set(archive.SUCCESS)|{archive.EXPECTED_FAILURE}
    for name,r in snapshot["logs"].items():
        assert r["exit_code"]==(1 if name==archive.EXPECTED_FAILURE else 0)
        assert len(r["sha256"])==len(r["exit_sha256"])==64

@pytest.mark.parametrize("label",archive.SUCCESS+(archive.EXPECTED_FAILURE,))
def test_each_original_log_sha_has_independent_exit_byte_hash(label,snapshot):
    rec=snapshot["logs"][label]
    raw=(ROOT/rec["path"]).read_bytes()
    exit_bytes=(ROOT/rec["exit_path"]).read_bytes()
    assert archive.sha(raw)==rec["sha256"]
    assert archive.sha(exit_bytes)==rec["exit_sha256"]
    assert raw and exit_bytes.strip() in (b"0",b"1")

@pytest.fixture()
def cloned_logs(tmp_path):
    for label in (*archive.SUCCESS,archive.EXPECTED_FAILURE):
        for suffix in ("log","exit"):
            f=archive.LOG_DIR/f"{archive.PREFIX}_{label}.{suffix}"
            shutil.copyfile(f,tmp_path/f.name)
    return tmp_path

@pytest.mark.parametrize("name",(*archive.SUCCESS,archive.EXPECTED_FAILURE))
def test_tampered_zero_exit_logs_or_missing_bytes_rejected(name,cloned_logs):
    f=cloned_logs/f"{archive.PREFIX}_{name}.log"
    f.write_bytes(b"PASS fake green\n")
    with pytest.raises(ValueError):
        archive.read_runs(cloned_logs)

@pytest.mark.parametrize("name",(*archive.SUCCESS,archive.EXPECTED_FAILURE))
def test_fake_success_or_failure_exit_codes_rejected(name,cloned_logs):
    f=cloned_logs/f"{archive.PREFIX}_{name}.exit"
    f.write_bytes(b"0\n" if name==archive.EXPECTED_FAILURE else b"1\n")
    with pytest.raises(ValueError):
        archive.read_runs(cloned_logs)

@pytest.mark.parametrize("name",(*archive.SUCCESS,archive.EXPECTED_FAILURE))
def test_missing_original_mac_log_rejected(name,cloned_logs):
    (cloned_logs/f"{archive.PREFIX}_{name}.log").unlink()
    with pytest.raises(ValueError):
        archive.read_runs(cloned_logs)

@pytest.mark.parametrize("name",(*archive.SUCCESS,archive.EXPECTED_FAILURE))
def test_fake_passed_test_counts_rejected(name,cloned_logs):
    f=cloned_logs/f"{archive.PREFIX}_{name}.log"
    raw=f.read_text(encoding="utf-8")
    if name=="NODE":raw=raw.replace("# pass 111","# pass 112")
    elif name=="FOCUSED":raw=raw.replace("273 passed","999 passed")
    elif name=="FOCUSED_INITIAL":raw=raw.replace("10 failed, 263 passed","0 failed, 273 passed")
    elif name=="BROWSER":raw=raw.replace("Chrome browser suite passed","Chrome browser suite FAILED")
    elif name=="MAC_FULL":raw=raw.replace("PASS KB156 ten source-locked deep drafts","NOT CHECKED")
    f.write_text(raw,encoding="utf-8")
    with pytest.raises(ValueError):
        archive.read_runs(cloned_logs)

@pytest.mark.parametrize("key,fake",[
 ("real_teacher_approved",1),
 ("student_authoritative_releases",1),
 ("formal_general_proof_certifications",40),
 ("official_course_completion_rate",0.99),
 ("total_teacher_only_manuscripts",315),
])
def test_false_approval_or_official_syllabus_denominator_in_report_detected(key,fake,snapshot):
    clone=copy.deepcopy(snapshot);clone[key]=fake
    assert clone!=archive.build()
