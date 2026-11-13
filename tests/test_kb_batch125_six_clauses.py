import copy, json, sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch125_six_requirements as r
DATA=json.loads(r.OUT.read_text())

@pytest.mark.parametrize("record",DATA["records"],ids=lambda x:x["cue_id"])
def test_six_remaining_numbered_requirements_are_review_packets_not_approvals(record):
    assert record["teacher_review_status"]=="REVIEW_PENDING"
    assert record["official_atom_count_effect"] is None
    assert record["teacher_signature"] is None
    assert record["student_authoritative"] is False
    assert len(record["source_line_sha256"])==64
    assert len(record["interpretation"])>=40
    assert len(record["prerequisites_or_boundaries"])>=24
    assert len(record["typical_invalid_inference"])>=22
    assert len(record["human_next_action"])>=22

@pytest.mark.parametrize("change",[
  lambda x:x.update(teacher_approved=1),
  lambda x:x.update(official_atom_denominator=405),
  lambda x:x.update(official_atoms_certified=1),
  lambda x:x["records"][0].update(teacher_review_status="APPROVED"),
  lambda x:x["records"][0].update(student_authoritative=True),
  lambda x:x["records"][0].update(official_atom_count_effect=1),
  lambda x:x["records"][0].update(prerequisites_or_boundaries=""),
  lambda x:x["records"][0].update(course_track="ELECTIVE_E"),
  lambda x:x["records"][0].update(proposed_disposition="OFFICIAL_ATOM"),
  lambda x:x["records"][0].update(teacher_signature={"llm":"approved"}),
  lambda x:x["records"].append(copy.deepcopy(x["records"][0])),
])
def test_forged_course_clause_verdicts_are_rejected(change):
    d=copy.deepcopy(DATA);change(d)
    with pytest.raises((ValueError,IndexError)):r.validate(d)

def test_report_and_source_grounding():
    assert r.validate(DATA)
    assert DATA["proposed_activities_or_competencies"]==6
    assert DATA["official_atoms_certified"]==0
    assert DATA["teacher_approved"]==0
    assert DATA["official_atom_denominator"] is None
    assert DATA["records"][2]["proposed_disposition"]=="GEOMETRY_PROOF_COMPETENCY_CANDIDATE"
    assert DATA["records"][3]["proposed_disposition"]=="SAMPLING_METHOD_BUNDLE_CANDIDATE"
    assert r.OUT.read_text()==r.dump(DATA)
    assert r.REPORT.read_text()==r.render(DATA)
