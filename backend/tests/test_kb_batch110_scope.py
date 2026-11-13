"""Batch110: independent source scope, no false teacher approval or official denominator."""
from copy import deepcopy
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch110_scope as B
from kb_batch110_source_authoring import CANDIDATES,PARTITIONS

@pytest.fixture(scope="module")
def artifact():
    return B.build()

def test_source_line_accounting(artifact):
    assert artifact["pages"]==[20,57]
    assert artifact["line_counts"]=={"20":35,"57":23}
    assert artifact["source_lines_total"]==58
    assert len(artifact["structural_partitions"])==15
    for page,limit in ((20,35),(57,23)):
        lines=[line for seg in artifact["structural_partitions"] if seg["page"]==page
               for line in range(seg["start"],seg["end"]+1)]
        assert lines==list(range(1,limit+1))

def test_seven_track_unknown_and_no_fake_approval(artifact):
    assert set(artifact["official_seven_track_atom_denominators"].values())=={None}
    assert artifact["new_editorial_candidates"]==20
    assert artifact["finite_exact_witnesses"]==14
    assert artifact["pedagogy_not_math_proofs"]==6
    assert artifact["candidate_counts_by_track"]=={
        "COMPULSORY":9,"SELECTIVE_COMPULSORY":0,"ELECTIVE_A":9,
        "ELECTIVE_B":2,"ELECTIVE_C":0,"ELECTIVE_D":0,"ELECTIVE_E":0}
    assert artifact["teacher_approvals"]==0
    assert artifact["student_authoritative_releases"]==0

@pytest.mark.parametrize("i",range(20))
def test_editorial_candidate_integrity(i,artifact):
    a=CANDIDATES[i];r=artifact["candidates"][i]
    assert a["key"]==r["key"] and a["title"]==r["title"]
    assert r["source_page_pdfkit_sha256"]
    assert len(r["source_page_pdfkit_sha256"])==64
    assert r["source_pdf_sha256"]==B.PDF_SHA
    assert r["official_atom_id"] is None
    assert r["review_status"]=="REVIEW_PENDING"
    assert r["teacher_reviewer"] is None
    assert r["student_authoritative_release"] is False
    assert r["math_witness"]["general_proof_certified"] is False
    assert r["track_hint"]==B.track(r)
    assert r["math_witness"]==B.exact_witness(r["key"])
    if a["kind"]=="PEDAGOGY":
        assert r["math_witness"]["status"]=="PEDAGOGY_NOT_A_MATH_PROOF"
    else:
        assert r["math_witness"]["finite_exact_positive_passed"]
        assert r["math_witness"]["invalid_generalization_rejected"]

@pytest.mark.parametrize("key",["power_functions","exp_monotonic","log_properties",
    "moment_estimation","maximum_likelihood","test_logic","least_squares"])
def test_math_witness_has_positive_and_negative_exact_instances(key):
    result=B.exact_witness(key)
    assert result["status"]=="FINITE_EXACT_INSTANCE_ONLY"
    assert result["invalid_generalization_rejected"]
    assert not result["general_proof_certified"]

@pytest.mark.parametrize("change",["missing","overlap","track-crossing","wrong-kind"])
def test_source_partition_and_schema_negative_gates(change):
    c=deepcopy(CANDIDATES);p=deepcopy(PARTITIONS)
    if change=="missing":
        p[20][2]=(6,11,"POWER_EXP_LOG_OVERVIEW")
    elif change=="overlap":
        p[57][4]=(15,19,"ELECTIVE_B_COURSE_BOUNDARY")
    elif change=="track-crossing":
        c[-1]["start"]=15
    else:
        c[3]["kind"]="PEDAGOGY"
    with pytest.raises(ValueError):
        B.build(candidates=c,partitions=p)

@pytest.mark.parametrize("field",["review_status","official_atom_id","teacher_approved",
                                   "student_authoritative_release","source_pdf_sha256"])
def test_forged_authoring_authority_refused(field):
    c=deepcopy(CANDIDATES)
    c[2][field]="APPROVED"
    with pytest.raises(ValueError):
        B.build(candidates=c)

def test_full_source_has_real_local_mac_evidence():
    # GitHub runners do not hold the legally accessed PDF. Only the Mac may
    # validate original bytes; CI still checks pinned page hashes and sources.
    if not B.PDF.is_file():
        pytest.skip("Original PDF held only on authorised Mac")
    obj=B.build(verify_local_source=True)
    assert obj["source_lines_total"]==58

def test_generated_files_frozen():
    obj=B.build()
    assert B.OUT.read_text(encoding="utf8")==B.serialize(obj)
    assert B.MD.read_text(encoding="utf8")==B.markdown(obj)
