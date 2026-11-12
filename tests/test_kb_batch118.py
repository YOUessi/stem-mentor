"""Batch118 syllabus-cue ledger, complete review gating, source identity and teaching privacy."""
import copy
import json
import sys
from pathlib import Path
import pytest
from pydantic import ValidationError

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch118_source_atom_ledger as ledger
import build_kb_batch118_lessons as lessons_builder
from app.deep_knowledge import DeepLesson, public_summary

DATA=json.loads(ledger.OUT.read_text())
DOCS=json.loads(lessons_builder.PACK.read_text())
LINKS=json.loads(lessons_builder.META.read_text())
COVER=json.loads(lessons_builder.COVER.read_text())

@pytest.mark.parametrize("page",DATA["pages"],ids=lambda r:f"page-{r['printed_page']}")
def test_page_has_locked_source_and_unknown_official_denominator(page):
    earlier=json.loads(ledger.SOURCE.read_text())["pages"][page["printed_page"]-13]
    assert page["source_page_sha256"]==earlier["page_text_sha256"]
    assert page["source_line_count"]==earlier["nonempty_pdfkit_line_count"]
    assert page["pdf_page_index"]==page["printed_page"]+7
    assert page["official_atom_denominator"] is None
    assert page["editorial_source_line_review"] in (
        "INSPECTED_PENDING_TEACHER","INDEXED_PENDING_EDITORIAL"
    )

@pytest.mark.parametrize("cue",DATA["markers"],ids=lambda r:r["editorial_marker_id"])
def test_cue_is_a_unique_hash_locked_unapproved_source_link(cue):
    assert cue["track_hint"]==ledger.track_at(cue["printed_page"],cue["source_line"])
    assert cue["official_atom_id"] is None
    assert cue["teacher_review_evidence"] is None
    assert cue["review_status"]=="REVIEW_PENDING"
    assert cue["source_status"]=="SOURCE_HASH_LOCKED_NOT_TEACHER_ATOMIZED"
    assert cue["math_proof_status"]=="UNVERIFIED"
    assert not cue["student_authoritative"]
    assert cue["page_text_sha256"]==DATA["pages"][cue["printed_page"]-13]["source_page_sha256"]

@pytest.mark.parametrize("printed_page,line,expected",[
    (36,15,"COMPULSORY"),(36,16,"SELECTIVE_COMPULSORY"),
    (50,19,"SELECTIVE_COMPULSORY"),(50,20,"ELECTIVE_UNASSIGNED"),
    (51,19,"ELECTIVE_UNASSIGNED"),(51,20,"ELECTIVE_A"),
    (57,15,"ELECTIVE_A"),(57,16,"ELECTIVE_B"),
    (64,9,"ELECTIVE_B"),(64,10,"ELECTIVE_C"),
    (69,5,"ELECTIVE_C"),(69,6,"ELECTIVE_D"),
    (73,12,"ELECTIVE_D"),(73,13,"ELECTIVE_E"),
])
def test_cross_track_transition_is_line_level(printed_page,line,expected):
    assert ledger.track_at(printed_page,line)==expected

@pytest.mark.parametrize("track",ledger.TRACKS)
def test_seven_official_denominators_must_remain_unknown(track):
    assert DATA["track_counts"][track]["official_atom_denominator"] is None
    assert COVER["official_atom_denominators"][track] is None
    assert DATA["track_counts"][track]["teacher_approved_count"]==0

@pytest.mark.parametrize("attack",[
    lambda d: d.update(official_atom_total_denominator=405),
    lambda d: d.update(official_atom_complete_census=True),
    lambda d: d.update(teacher_approved_total=1),
    lambda d: d["track_counts"]["COMPULSORY"].update(official_atom_denominator=127),
    lambda d: d["pages"][73-13]["line_track_partitions"][-1].update(track="ELECTIVE_D"),
    lambda d: d["markers"][0].update(review_status="APPROVED"),
    lambda d: d["markers"][0].update(student_authoritative=True),
    lambda d: d["markers"][0].update(official_atom_id="forged.1"),
    lambda d: d["markers"][0].update(math_proof_status="CERTIFIED"),
    lambda d: d["markers"][0].update(source_line_sha256="0"*64),
    lambda d: d["pages"][0].update(source_line_count=0),
    lambda d: d["markers"].append(copy.deepcopy(d["markers"][0])),
    lambda d: d.update(source_text_committed=True),
])
def test_source_ledger_rejects_tampering_and_fake_approval(attack):
    forged=copy.deepcopy(DATA)
    attack(forged)
    with pytest.raises(ValueError):
        ledger.validate(forged)

@pytest.mark.parametrize("doc",DOCS,ids=lambda row:row["id"])
def test_deep_lesson_completeness_is_not_teacher_certification(doc):
    model=DeepLesson.model_validate(doc)
    assert model.review.status=="REVIEW_PENDING"
    assert model.teacher_solution_visibility=="TEACHER_ONLY"
    assert model.review.reviewer_id is None
    assert len(model.worked_examples)==2
    assert len(model.hint_ladder)==3
    assert len(model.counterexamples)>=1
    assert len(model.assumptions)>=2
    assert len(model.notation)>=2
    assert len(model.proof_steps)==3 if model.kind=="theorem" else not model.proof_steps
    assert model.provenance.permission=="PROJECT_AUTHORED"

@pytest.mark.parametrize("doc",DOCS,ids=lambda row:row["id"])
def test_forged_teacher_approval_rejected(doc):
    tampered=copy.deepcopy(doc)
    tampered["review"].update(status="APPROVED",reviewer_id="fictional",review_record="fictional",reviewed_at="2026-11-13")
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(tampered)

@pytest.mark.parametrize("doc",DOCS,ids=lambda row:row["id"])
def test_tiered_hints_do_not_contain_complete_teacher_answers(doc):
    hints=" ".join(doc["hint_ladder"])
    answers={row["answer"] for row in doc["worked_examples"]}
    assert all(answer not in hints for answer in answers)
    assert "教师答案" not in hints
    assert "最终答案为" not in hints

@pytest.mark.parametrize("row",LINKS["items"],ids=lambda row:row["lesson_id"])
def test_review_pending_source_lesson_joins(row):
    assert row["official_atom_id"] is None
    assert row["teacher_approved"] is False
    assert row["student_authoritative"] is False
    assert row["review_status"]=="REVIEW_PENDING"
    assert row["source_page_sha256"]==DATA["pages"][row["printed_page"]-13]["source_page_sha256"]
    assert row["source_cue_ids"]
    ids={m["editorial_marker_id"] for m in DATA["markers"]}
    assert set(row["source_cue_ids"])<=ids

def test_coverage_frozen_baseline_and_no_student_authority():
    assert COVER["prior_drafts"]==498
    assert COVER["new_drafts"]==8
    assert COVER["total_review_pending_drafts"]==506
    assert COVER["new_teacher_only_examples"]==16
    assert COVER["new_hint_levels"]==24
    assert COVER["new_transfer_prompts"]==16
    assert COVER["new_counterexamples"]==8
    assert COVER["teacher_approved"]==COVER["authoritative_student_releases"]==0
    assert DATA["total_indexed_source_lines"]==1684
    assert DATA["total_provisional_markers"]==405
    assert len(DATA["batch118_editorial_line_inspection_pages"])==24
    assert len(DATA["pages"])==61
    assert len({x["editorial_marker_id"] for x in DATA["markers"]})==405

def test_student_public_summary_does_not_include_new_drafts_or_solutions():
    text=json.dumps(public_summary(),ensure_ascii=False)
    assert "batch118_probability_distribution" not in text
    assert "teacher_solution" not in text
    assert all(x["teacher_solution_visibility"]=="TEACHER_ONLY" for x in DOCS)

def test_committed_artifacts_reproducible_without_local_pdf():
    assert ledger.validate(DATA)
    assert ledger.REPORT.read_text()==ledger.markdown(DATA)
    for path,object_value in lessons_builder.generate().items():
        assert path.read_text()==(object_value if isinstance(object_value,str) else lessons_builder.dump(object_value))

def test_future_draft_cannot_change_batch117_historical_denominator():
    import build_kb_batch117 as prev
    assert not prev.is_frozen_prior_pack(lessons_builder.PACK)
    assert prev.coverage()["total_deep_drafts"]==498


def test_editorial_pdf_and_worked_solution_consistency():
    assert lessons_builder.MD.read_text().startswith("# Batch118｜概率统计")
    assert "累加1/4+1/2+1/4=1" in lessons_builder.MD.read_text()
    assert "公平骰子X只取1,3" not in lessons_builder.MD.read_text()
