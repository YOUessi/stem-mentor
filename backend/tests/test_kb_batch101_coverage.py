"""Cumulative seven-track arithmetic with official denominator left unknown."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys,json
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch101_coverage as C

@pytest.fixture(scope="module")
def report():
    return C.build()

def test_authored_math_comparisons_reflected_without_teacher_approval(report):
    C.validate(report)
    assert report["originally_editorially_compared"]==166
    assert report["newly_math_compared_this_batch"]==20
    assert report["cumulative_editorially_compared_labels"]==186
    assert report["remaining_without_pairwise_editorial"]==114
    assert report["source_anchor_lines"]==428
    assert report["full_official_source_pages"]==61
    assert report["fully_human_atomized_pages"]==0
    assert report["official_atom_denominator"] is None
    assert report["pages_with_no_project_source_anchors"]==[13,14,51]
    assert report["teacher_approved"]==report["student_authoritative_release"]==0

@pytest.mark.parametrize("track",(
"COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
"ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"))
def test_each_track_distinguishes_provisional_labels_from_official_atoms(report,track):
    row=report["track_matrix"][track]
    assert row["official_curriculum_atom_denominator"] is None
    assert (row["editorially_compared_prior"]+
            row["newly_authored_math_comparisons"]+
            row["remaining_without_pairwise_editorial"]==
            row["provisional_project_labels"])
    assert row["teacher_approved_lessons"]==row["student_authoritative_release"]==0
    if track=="ELECTIVE_E":assert row["provisional_project_labels"]==0

@pytest.mark.parametrize("attack",(
  "wrong_total","fake_denominator","fake_track_denominator","fake_approved",
  "fake_teacher_merges","fake_prereq","fake_student","mark_pages_done",
  "wrong_new_comparisons","understate_remaining","fake_math_certification",
  "break_track_conservation","hide_text_prerequisites",
))
def test_coverage_negative_mutation_gates(report,attack):
    row=deepcopy(report)
    t=row["track_matrix"]["COMPULSORY"]
    if attack=="wrong_total":row["provisional_project_labels"]=299
    elif attack=="fake_denominator":row["official_atom_denominator"]=300
    elif attack=="fake_track_denominator":row["official_atom_denominators_by_track"]["COMPULSORY"]=75
    elif attack=="fake_approved":row["teacher_approved"]=1
    elif attack=="fake_teacher_merges":row["final_teacher_semantic_equivalence_adjudications"]=1
    elif attack=="fake_prereq":row["candidate_only_prerequisite_edges_promoted"]=1
    elif attack=="fake_student":row["student_authoritative_release"]=1
    elif attack=="mark_pages_done":row["fully_human_atomized_pages"]=61
    elif attack=="wrong_new_comparisons":row["newly_math_compared_this_batch"]=21
    elif attack=="understate_remaining":row["remaining_without_pairwise_editorial"]=0
    elif attack=="fake_math_certification":row["general_mathematical_proofs_certified_this_batch"]=1
    elif attack=="break_track_conservation":t["newly_authored_math_comparisons"]+=1
    elif attack=="hide_text_prerequisites":row["unresolved_textual_prerequisites"]=0
    with pytest.raises(ValueError):
        C.validate(row)

def test_source_sha_artifact_stability(report):
    assert C.OUT.exists() and C.MD.exists()
    assert json.loads(C.OUT.read_text(encoding="utf8"))==report
    assert C.MD.read_text(encoding="utf8")==C.markdown(report)
    assert C.QUEUE.digest(C.QUEUE.SOURCE)==report["source_sha256"]
    assert C.QUEUE.digest(C.MATH.OUT)==report["math_pair_artifact_sha256"]
    assert C.QUEUE.digest(C.QUEUE.OUT)==report["review_queue_artifact_sha256"]
