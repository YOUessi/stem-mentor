"""K00/K07: no teacher approval, no fake official denominator or proof certification."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch18_source_register as k00
import build_kb_batch18_k07_review as k07

@pytest.fixture(scope="module")
def scope_snapshot():
    return json.loads(k00.OUTPUT.read_text(encoding="utf8"))

@pytest.fixture(scope="module")
def risk_snapshot():
    return json.loads(k07.OUTPUT.read_text(encoding="utf8"))

def test_source_inventory_is_provisional(scope_snapshot):
    assert k00.verify_document(scope_snapshot)
    assert scope_snapshot["verified_official_atomic_denominator"] is None
    assert scope_snapshot["official_atom_coverage_rate"] is None
    assert scope_snapshot["human_confirmed_source_atoms"]==0

def test_standard_pdf_hash_is_frozen(scope_snapshot):
    assert len(scope_snapshot["standard_pdf_sha256"])==64
    assert scope_snapshot["standard_pdf_sha256"]=="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"

def test_26_source_topic_headings_cover_all_tracks(scope_snapshot):
    assert set(scope_snapshot["source_markers_by_track"]) == set(k00.TRACKS)
    assert scope_snapshot["project_topic_index_count"] == 26
    assert len(scope_snapshot["source_topics"]) == 7
    assert scope_snapshot["printed_pages_examined"] == {"first":13,"last":73,"count":61}

@pytest.mark.parametrize("track",list(k00.TRACKS))
def test_each_track_remains_unapproved(scope_snapshot,track):
    assert scope_snapshot["source_markers_by_track"][track]>0
    assert next(row for row in scope_snapshot["source_topics"] if row["track"]==track)["official_atomic_denominator"] is None
    assert all(row["teacher_review"]=="PENDING" for row in scope_snapshot["markers"] if row["track"]==track)

def test_unrepresented_pages_risk_is_retained(scope_snapshot):
    assert ( "ELECTIVE_A",56) in {(x["track"],x["printed_page"]) for x in scope_snapshot["unrepresented_source_pages"]}
    assert ( "ELECTIVE_A",57) in {(x["track"],x["printed_page"]) for x in scope_snapshot["unrepresented_source_pages"]}

@pytest.mark.parametrize("fake_denominator", [1, 132, 248, 9999])
def test_official_denominator_cannot_be_invented(scope_snapshot,fake_denominator):
    bad=copy.deepcopy(scope_snapshot)
    bad["verified_official_atomic_denominator"]=fake_denominator
    with pytest.raises(ValueError):k00.verify_document(bad)

def test_source_marker_never_auto_maps_to_lesson(scope_snapshot):
    bad=copy.deepcopy(scope_snapshot)
    bad["markers"][0]["linked_editorial_objective_ids"]=["HS-STD2020-COMPULSORY-001"]
    with pytest.raises(ValueError):k00.verify_document(bad)

def test_source_marker_never_auto_approved(scope_snapshot):
    bad=copy.deepcopy(scope_snapshot)
    bad["markers"][0]["teacher_review"]="APPROVED"
    with pytest.raises(ValueError):k00.verify_document(bad)

def test_source_page_provenance_enforced(scope_snapshot):
    bad=copy.deepcopy(scope_snapshot)
    bad["markers"][0]["printed_page"]=999
    with pytest.raises(ValueError):k00.verify_document(bad)

def test_k07_all_open_issues_maintained(risk_snapshot):
    assert k07.validate(risk_snapshot)
    s=risk_snapshot["summary"]
    assert s["conflicts_unresolved"]==10 and s["semantic_depth_gaps"]==23
    assert s["proof_step_obligations_unverified"]==451
    assert s["whole_proofs_certified"]==s["teacher_approved"]==s["verified_student_steps"]==0
    assert sum(s["by_priority"].values())==451

@pytest.mark.parametrize("conflict_id",[
    "math.hs.function.composition-domain",
    "math.hs.function.parity",
    "math.hs.function.piecewise",
    "math.hs.function.zero-ivt",
    "math.hs.geometry.point-line-distance",
    "math.hs.probability.binomial-distribution",
    "math.hs.probability.hypergeometric",
    "math.hs.statistics.correlation-regression",
    "math.hs.triangle.area-sine",
    "math.hs.vector.linear-operations",
])
def test_every_conflict_has_independent_boundary_check(risk_snapshot,conflict_id):
    checks=[x for x in risk_snapshot["curated_boundary_cases"] if x["conflict_id"]==conflict_id]
    assert checks and all(x["passed"] for x in checks)
    entry=next(x for x in risk_snapshot["conflict_reviews"] if x["lesson_id"]==conflict_id)
    assert entry["adjudication"]=="OPEN_REQUIRES_INDEPENDENT_TEACHER"
    assert entry["new_exact_boundary_cases"]==len(checks)

def test_k07_snapshot_reproducible(risk_snapshot):
    assert k07.build()==risk_snapshot

@pytest.mark.parametrize("bad_field,bad_value",[
    ("whole_proofs_certified",1),
    ("teacher_approved",1),
    ("verified_student_steps",1),
    ("semantic_gaps_closed",23),
])
def test_k07_cannot_invent_certification(risk_snapshot,bad_field,bad_value):
    bad=copy.deepcopy(risk_snapshot)
    bad["summary"][bad_field]=bad_value
    with pytest.raises(ValueError):k07.validate(bad)

def test_k07_false_case_rejected(risk_snapshot):
    bad=copy.deepcopy(risk_snapshot)
    bad["curated_boundary_cases"][0]["passed"]=False
    with pytest.raises(ValueError):k07.validate(bad)

def test_k07_forged_step_certification_rejected(risk_snapshot):
    bad=copy.deepcopy(risk_snapshot)
    bad["proof_step_queue"][0]["verification_status"]="VERIFIED"
    with pytest.raises(ValueError):k07.validate(bad)

def test_all_frozen_inputs_are_identical(risk_snapshot):
    assert risk_snapshot["source_sha256"]=={
        "conflicts":k07.sha(k07.CONFLICT),
        "proof_obligations":k07.sha(k07.PROOF),
        "semantic_gaps":k07.sha(k07.GAPS),
    }

def test_curated_checks_exact_case_count(risk_snapshot):
    assert risk_snapshot["summary"]["curated_cases"]==len(k07.limited_checks())
    assert risk_snapshot["summary"]["curated_cases"]>=300
    assert all(x["scope"]=="CURATED_EXACT_SUBCLAIM_NOT_A_WHOLE_PROOF" for x in risk_snapshot["curated_boundary_cases"])

def test_k00_identified_ten_new_missing_objectives():
    import build_kb_batch18_gap_candidates as gap
    report=json.loads(gap.OUT.read_text(encoding="utf8"))
    assert gap.validate(report)
    assert gap.build()==report
    assert report["summary"]["new_gap_candidates"]==10
    assert report["summary"]["by_track"]=={"SELECTIVE_COMPULSORY":1,"ELECTIVE_A":9}
    assert all(x["status"]=="OPEN" and x["verified_official_atom_id"] is None for x in report["items"])

def test_k00_new_gap_candidates_are_not_published():
    import build_kb_batch18_gap_candidates as gap
    report=gap.build()
    report["items"][0]["student_content_available"]=True
    with pytest.raises(ValueError):gap.validate(report)

def test_k00_new_gap_candidates_must_not_certify_official_total():
    import build_kb_batch18_gap_candidates as gap
    report=gap.build()
    report["official_atomic_denominator"]=258
    with pytest.raises(ValueError):gap.validate(report)

def test_k00_missing_curriculum_a_statistics_scope():
    import build_kb_batch18_gap_candidates as gap
    report=gap.build()
    names=[x["project_topic"] for x in report["items"] if x["track"]=="ELECTIVE_A"]
    assert {"参数估计","正态假设检验","分布拟合优度检验",
            "二元线性回归模型","连续随机变量与密度"}.issubset(names)
