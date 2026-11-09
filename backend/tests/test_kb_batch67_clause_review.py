"""Batch67: source provenance, no false coverage, exact bounded math and anti-promotion."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch67_clause_review as m

@pytest.fixture(scope="module")
def snapshot():
    return m.build()

def test_replay_full_outputs():
    m.write(check=True)

def test_local_source_hash_mac_only():
    # Skipped in CI: Mac-only source bytes are not distributed through GitHub.
    if not Path("/private/tmp/kb56_page_19.txt").is_file():
        pytest.skip("Only authorized Mac has original PDFKit source")
    c,a,d,locations=m.build()
    assert m.verify_source_local(m.load(m.REGISTRY),locations)>=5

@pytest.mark.parametrize("i",range(6))
def test_bounded_exact_finite_case(i):
    assert m.witness(i) is True

@pytest.mark.parametrize("i",range(6))
def test_cross_page_review_is_safe(snapshot,i):
    c,_,_,_=snapshot
    row=c["rows"][i]
    assert row["left_page"]!=row["right_page"]
    assert row["teacher_review"]=="REVIEW_PENDING"
    assert row["math_evidence"]=="FINITE_EXACT_INSTANCE_ONLY"
    assert row["official_clause_complete"] is False
    assert row["merge_permitted"] is False
    assert row["student_publishable"] is False
    assert all(isinstance(row[k],str) and len(row[k])>20 for k in (
        "editorial_distinction","exact_finite_example","misleading_reasoning"))

@pytest.mark.parametrize("i",range(14))
def test_unnumbered_sections_not_automatically_covered(snapshot,i):
    _,a,_,_=snapshot
    row=a["rows"][i]
    assert row["coverage_status"]=="UNMAPPED"
    assert row["official_full_clause_verified"] is False
    assert row["assessment_proves_coverage"] is False
    assert row["student_publishable"] is False
    assert row["teacher_review"]=="REVIEW_PENDING"
    assert row["section_source_line_sha256"]

@pytest.mark.parametrize("t",m.TRACKS)
def test_seven_track_unknown_denominator(snapshot,t):
    _,_,d,_=snapshot
    row=d["tracks"][t]
    assert row["official_atom_denominator"] is None
    assert row["coverage_fraction"] is None
    assert row["teacher_approved"] == row["student_publishable"] == 0

@pytest.mark.parametrize("i",range(428))
def test_every_heuristic_anchor_present_without_promotion(i):
    rows=m.load(m.REGISTRY)["rows"]
    row=rows[i]
    assert row["full_page_review_completed"] is False
    assert row["teacher_review"]=="REVIEW_PENDING"
    assert row["source_line_sha256"] and len(row["source_line_sha256"])==64

@pytest.mark.parametrize("i",range(62))
def test_every_provisional_candidate_remains_unreviewed(i):
    item=m.load(m.PROPOSALS)["proposals"][i]
    assert item["official_atomic_membership"]=="UNDETERMINED"
    assert item["math_equivalence"]=="NOT_REVIEWED"
    assert item["student_publishable"] is False

def test_exact_witness_domain_failures_are_real():
    assert (-1 > 0) is False and (0 > 0) is False
    assert (0**2 == 0) is True
    assert (0**2 - 0 == 0) is True
    assert (-1)**2 - (-1) == 2

def test_illegal_merged_pair_rejected():
    sources={"queue":deepcopy(m.load(m.QUEUED))}
    sources["queue"]["rows"][0]["merge_permitted"]=True
    with pytest.raises(ValueError,match="unsafe merge"):
        m.build(sources)

def test_forged_approval_rejected():
    sources={"proposals":deepcopy(m.load(m.PROPOSALS))}
    sources["proposals"]["proposals"][0]["teacher_review"]="APPROVED"
    with pytest.raises(ValueError,match="candidate teacher status forged|provisional candidates falsely promoted"):
        m.build(sources)

def test_changed_source_window_sha_rejected():
    sources={"proposals":deepcopy(m.load(m.PROPOSALS))}
    sources["proposals"]["proposals"][0]["source_window_sha256"]="0"*64
    # this particular candidate may not occur among six contrast pairs, so mutate a pair member:
    p_id=m.load(m.QUEUED)["rows"][0]["left"]
    for r in sources["proposals"]["proposals"]:
        if r["candidate_id"]==p_id:r["source_window_sha256"]="0"*64
    with pytest.raises(ValueError,match="broken source window or anchor"):
        m.build(sources)

def test_changed_objective_anchor_sha_rejected():
    sources={"cross":deepcopy(m.load(m.CROSS))}
    sources["cross"]["links"][0]["section_source_line_sha256"]="1"*64
    with pytest.raises(ValueError,match="bad competency source hash"):
        m.build(sources)

def test_changed_student_visibility_rejected():
    sources={"assessments":deepcopy(m.load(m.ASSESSMENTS))}
    sources["assessments"][0]["student_publishable"]=True
    with pytest.raises(ValueError,match="assessment status changed"):
        m.build(sources)

def test_structural_coverage_rollup_invariants(snapshot):
    c,a,d,loc=snapshot
    assert c["teacher_confirmed_equivalences"] == c["automatic_merges"] == 0
    assert d["official_denominator_known"]==0
    assert d["missing_official_atoms_count"] is None
    assert sum(v["heuristic_source_leads"] for v in d["tracks"].values())==428
    assert sum(v["internal_provisional_atom_splits"] for v in d["tracks"].values())==62
    assert len({(x["printed_page"],x["pdfkit_line"]) for x in loc})==len(loc)
    assert c["source_visual_diagram_page35"]=="PENDING_MANUAL_REVIEW"

def test_outputs_never_contain_source_copyright_excerpts(snapshot):
    c,a,_,_=snapshot
    assert a["source_text_not_embedded"] is True
    assert all("left_source_window_sha256" in x and "right_source_window_sha256" in x for x in c["rows"])
    assert not any("official_full_clause_text" in x for x in c["rows"])
