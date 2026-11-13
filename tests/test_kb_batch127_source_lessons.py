"""Batch127: source, mathematics, provenance, reviewer and student data gate regression."""
import copy, hashlib, json, sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch127_source_review as src
import build_kb_batch127_deep_lessons as deep
from app.deep_knowledge import public_summary
SOURCE=json.loads(src.OUT.read_text(encoding="utf-8"))
LOCKS=json.loads(src.LOCKS.read_text(encoding="utf-8"))
LESSONS=json.loads(deep.OUT.read_text(encoding="utf-8"))
WITNESSES=json.loads(deep.CHECKS.read_text(encoding="utf-8"))

@pytest.mark.parametrize("row",SOURCE["records"],ids=lambda x:x["id"])
def test_source_case_scope_attestation_not_certification(row):
 assert row["id"] in LOCKS
 assert row["source"]==LOCKS[row["id"]]
 assert row["teacher_status"]=="REVIEW_PENDING"
 assert row["teacher_signature"] is None
 assert row["official_atom_id"] is None
 assert row["student_authoritative"] is False
 assert row["proof_machine_certified"] is False
 assert len(row["editorial_interpretation"])>=28
 assert len(row["unresolved_risk"])>=28

@pytest.mark.parametrize("row",SOURCE["records"],ids=lambda x:x["id"])
def test_mac_original_syllabus_exact_line_hashes(row):
 lock=row["source"];page=lock["page"]
 lines=src.previous.source_pages()[page][lock["start_line"]-1:lock["end_line"]]
 assert len(lines)==len(lock["line_sha256"])
 assert [hashlib.sha256(s.encode()).hexdigest() for s in lines]==lock["line_sha256"]
 assert hashlib.sha256("\n".join(lines).encode()).hexdigest()==lock["span_sha256"]

@pytest.mark.parametrize("lesson",LESSONS,ids=lambda x:x["candidate_id"])
def test_eight_real_complete_drafts_contain_teaching_rationale_and_boundaries(lesson):
 assert lesson["review_status"]=="REVIEW_PENDING"
 assert lesson["teacher_evidence"] is None
 assert lesson["student_authoritative"] is False
 assert lesson["proof_machine_certified"] is False
 assert lesson["teacher_solution_visibility"]=="TEACHER_ONLY"
 assert len(lesson["reasoned_steps"])==3
 assert len(lesson["teacher_examples"])==2
 assert all(len(e["steps"])==2 for e in lesson["teacher_examples"])
 assert len(lesson["student_hint_ladder"])==3
 assert lesson["source"]["original_pdf_sha256"]==SOURCE["records"][0]["curriculum_pdf_sha256"]

@pytest.mark.parametrize("mutator",[
 lambda d:d.update(cases=27),
 lambda d:d.update(distinct_context_reviewed_total=239),
 lambda d:d.update(unreviewed_editorial_candidates=0),
 lambda d:d.update(source_marker_total=404),
 lambda d:d.update(teacher_approved=1),
 lambda d:d.update(student_authoritative=1),
 lambda d:d.update(official_atom_total_denominator=239),
 lambda d:d["official_atom_per_track"].update(COMPULSORY=200),
 lambda d:d["records"][0].update(official_atom_id="FAKE"),
 lambda d:d["records"][0].update(teacher_status="APPROVED"),
 lambda d:d["records"][0].update(student_authoritative=True),
 lambda d:d["records"][0].update(teacher_signature="fake"),
 lambda d:d["records"][0].update(proof_machine_certified=True),
 lambda d:d["records"][0]["source"].update(span_sha256="0"*64),
 lambda d:d["records"][0].update(interpretation_class="MATH_PROVED"),
 lambda d:d["records"][0].update(unresolved_risk="No risk"),
 lambda d:d["records"].pop(),
 lambda d:d["records"].append(copy.deepcopy(d["records"][0])),
 lambda d:d["counts_by_track"].update(COMPULSORY=999),
])
def test_source_audit_forgeries_are_rejected(mutator):
 bad=copy.deepcopy(SOURCE)
 mutator(bad)
 with pytest.raises((ValueError,KeyError)):src.validate(bad,LOCKS)

@pytest.mark.parametrize("mutator",[
 lambda docs:docs[0].update(review_status="APPROVED"),
 lambda docs:docs[0].update(student_authoritative=True),
 lambda docs:docs[0].update(proof_machine_certified=True),
 lambda docs:docs[0].update(teacher_evidence={"reviewer":"made-up"}),
 lambda docs:docs[0].update(teacher_solution_visibility="PUBLIC"),
 lambda docs:docs[0]["teacher_examples"].clear(),
 lambda docs:docs[0]["student_hint_ladder"].pop(),
 lambda docs:docs[0].update(formal_definition_or_statement="FALSE"),
 lambda docs:docs.pop(),
 lambda docs:docs.append(copy.deepcopy(docs[0])),
])
def test_deep_knowledge_forgery_and_truncation_are_rejected(mutator):
 bad=copy.deepcopy(LESSONS)
 mutator(bad)
 with pytest.raises((ValueError,KeyError)):deep.validate(bad)

def test_full_source_and_lesson_derivation_reproduces_committed_files():
 assert SOURCE==src.audited()[0]
 assert LOCKS==src.audited()[1]
 assert src.OUT.read_text(encoding="utf-8")==src.dump(SOURCE)
 assert src.REPORT.read_text(encoding="utf-8")==src.report(SOURCE)
 assert LESSONS==deep.build()
 assert WITNESSES==deep.exact_checks()
 assert deep.REPORT.read_text(encoding="utf-8")==deep.render(LESSONS,WITNESSES)
 assert deep.validate(LESSONS) and src.validate(SOURCE,LOCKS)
 assert SOURCE["counts_by_track"]=={"COMPULSORY":4,"SELECTIVE_COMPULSORY":4,"ELECTIVE_A":4,
 "ELECTIVE_B":4,"ELECTIVE_C":4,"ELECTIVE_D":4,"ELECTIVE_E":4}
 assert SOURCE["official_atom_total_denominator"] is None
 assert SOURCE["unreviewed_editorial_candidates"]==191

def test_independent_finite_exact_oracles_are_strictly_bounded():
 assert WITNESSES["exact_worked_examples"]==16
 assert WITNESSES["independent_negative_cases"]==8
 assert WITNESSES["cross_topic_checks"]==8
 assert WITNESSES["general_theorems_formally_certified"]==0
 assert WITNESSES["student_free_steps_certified"]==0
 assert WITNESSES["teacher_approved"]==0
 assert WITNESSES["student_authoritative"]==0

def test_student_index_does_not_publish_teacher_answers_or_editorial_evidence():
 s=json.dumps(public_summary(),ensure_ascii=False)
 assert "kb127-deep-" not in s
 assert "KB_BATCH127_SOURCE_REVIEW" not in s
 assert "teacher_examples" not in s
 assert "source_attestation" not in s
