"""Batch51 K00/K01 source coverage, original-PDF provenance and fail-closed tests.

PDFKit artifacts were generated on Mac from the pinned original PDF.
CI checks committed fingerprints only; CI never downloads copyrighted text.
"""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "scripts/build_kb_batch51_official_source_gate.py"
SPEC = importlib.util.spec_from_file_location("kb_batch51_source_gate", P)
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)
SOURCE = G.load(G.SOURCE)
DE = G.load(G.DE)
PDFKIT = G.load(G.PDFKIT)
EDITOR = G.load(G.EDITOR)
CLAUSES = G.load(G.CLAUSES)
RESULT = G.assemble()

def payload():
    return [copy.deepcopy(x) for x in (SOURCE,DE,PDFKIT,EDITOR,CLAUSES)]

def rebuild(p):
    return G.assemble(source=p[0],de=p[1],pdfkit=p[2],editor=p[3],clauses=p[4])

def test_complete_original_page_evidence_and_no_false_denominator():
    assert RESULT["source_pdf_sha256"] == G.PDF_SHA
    assert RESULT["source_page_denominator"] == 61
    assert len(RESULT["pages"]) == 61
    assert RESULT["review_gate"]["official_atomic_knowledge_denominator"] is None
    assert RESULT["review_gate"]["official_coverage_fraction"] is None
    assert RESULT["review_gate"]["human_full_page_reviews_completed"] == 0
    assert RESULT["review_gate"]["safety"] == "HARD_FAIL_CLOSED"

def test_extractor_and_editorial_denominators_never_conflated():
    x=RESULT["source_evidence_units_not_official_atoms"]
    assert x["numbered_marker_occurrences"] == 317
    assert x["D_E_unnumbered_topic_outlines"] == 23
    assert x["combined_heterogeneous_evidence_count"] == 340
    assert RESULT["editorial_scope_not_official"]["project_candidates"] == 313
    assert RESULT["editorial_scope_not_official"]["direct_pending_review"] == 301
    assert RESULT["editorial_scope_not_official"]["legacy_only_unverified"] == 12
    assert all(t["official_atomic_denominator"] is None for t in RESULT["track_evidence"])
    assert all(t["official_coverage_fraction"] is None for t in RESULT["track_evidence"])

@pytest.mark.parametrize("printed",range(13,74))
def test_all_61_pages_have_pinned_independent_mac_fingerprint(printed):
    row=RESULT["pages"][printed-13]
    assert row["printed_page"] == printed
    assert row["pdf_page_index"] == printed+7
    assert len(row["pdfkit_page_text_sha256"])==64
    assert row["pdfkit_unicode_scalars"]>0
    assert row["full_page_human_review"]=="PENDING"
    assert row["teacher_verified_official_atoms"]==0
    assert row["official_atomic_denominator"] is None
    assert row["mathematical_semantic_equivalence"]=="NOT_ASSESSED"

@pytest.mark.parametrize("track,numbered,de_topics,edit",[
    ("COMPULSORY",114,0,125),
    ("SELECTIVE_COMPULSORY",82,0,92),
    ("ELECTIVE_A",54,0,28),
    ("ELECTIVE_B",51,0,29),
    ("ELECTIVE_C",16,0,19),
    ("ELECTIVE_D",0,17,16),
    ("ELECTIVE_E",0,6,4),
])
def test_seven_tracks_are_distinct_evidence_types(track,numbered,de_topics,edit):
    row=next(x for x in RESULT["track_evidence"] if x["track"]==track)
    assert row["numbered_marker_occurrences_not_atoms"]==numbered
    assert row["D_E_topics_not_atoms"]==de_topics
    assert row["project_candidates_not_atoms"]==edit
    assert row["teacher_approved"] == 0

@pytest.mark.parametrize("p,label",sorted(G.NO_MARKER_TRIAGE.items()))
def test_unenumerated_source_blind_spots_are_never_silently_approved(p,label):
    row=RESULT["pages"][p-13]
    assert row["source_anchor_gap"] is True
    assert row["triage_label"]==label
    assert row["mathematical_semantic_equivalence"]=="NOT_ASSESSED"

def test_bad_pdfkit_text_must_not_pass_as_empty_curriculum():
    r=RESULT["pages"][35-13]
    assert r["pdfkit_control_scalars"] >= 20
    assert r["critical_manual_review"] is True
    assert "CORRUPTION" in r["triage_label"]

@pytest.mark.parametrize("p",sorted(G.CRITICAL))
def test_critical_unnumbered_or_ocr_pages_remain_pending(p):
    assert RESULT["pages"][p-13]["critical_manual_review"]
    assert p in RESULT["high_priority_gap_pages"]

@pytest.mark.parametrize("r",SOURCE["enumerated_source_anchors"], ids=lambda r:r["id"])
def test_all_317_marker_occurrences_are_unapproved_evidence_not_atoms(r):
    assert r["teacher_review"]=="PENDING"
    assert not r["approved_lesson_ids"]
    assert r["track"] in G.TRACKS

@pytest.mark.parametrize("r",DE["items"], ids=lambda r:r["id"])
def test_all_23_DE_topics_are_unapproved_source_outline(r):
    assert r["teacher_review"]=="PENDING"
    assert r["student_available"] is False
    assert r["track"] in {"ELECTIVE_D","ELECTIVE_E"}

@pytest.mark.parametrize("r",EDITOR["rows"], ids=lambda r:r["editorial_id"])
def test_all_313_editorial_items_are_not_approved_by_source_page_match(r):
    assert not r["teacher_approved"]
    assert not r["student_published"]
    assert not r["official_clause_verified"]
    assert not r["math_certified"]

@pytest.mark.parametrize("entry",CLAUSES["entries"],ids=lambda r:r["editorial_candidate_id"])
def test_12_legacy_source_checks_do_not_certify_math_equivalence(entry):
    assert entry["teacher_review"]=="REVIEW_PENDING"
    assert not entry["official_atomic_equivalence_certified"]
    assert not entry["legacy_lesson_certified"]
    assert not entry["student_publishable"]

def test_rebuilt_files_are_deterministic():
    assert G.OUT.read_text(encoding="utf-8")==json.dumps(RESULT,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    assert G.MD.read_text(encoding="utf-8")==G.markdown(RESULT)
    assert "340 不是官方原子数" in G.MD.read_text(encoding="utf-8")

def fake_source_sha(p): p[0]["source"]["sha256"]="0"*64
def fake_DE_sha(p): p[1]["source_pdf_sha256"]="1"*64
def fake_pdfkit_sha(p): p[2]["official_pdf_sha256"]="2"*64
def fake_clause_sha(p): p[4]["source"]["sha256"]="3"*64
def fake_atom_total(p): p[0]["denominator_contract"]["official_atomic_knowledge_denominator"]=317
def fake_editor_total(p): p[3]["summary"]["official_atom_denominator"]=313
def remove_page(p): p[2]["pages"].pop()
def repeat_page(p): p[2]["pages"][2]["printed_page"]=13
def move_pdf_index(p): p[2]["pages"][4]["pdf_page_index"]=400
def fake_missing_hash(p): p[2]["pages"][0]["pdfkit_text_sha256"]="bad"
def fake_all_reviewed(p): p[2]["pages"][0]["full_page_human_review"]="APPROVED"
def fake_DE_complete(p): p[1]["summary"]["fully_complete"]=True
def fake_DE_teacher(p): p[1]["summary"]["teacher_verified_knowledge_atoms"]=23
def fake_marker_approved(p): p[0]["enumerated_source_anchors"][0]["teacher_review"]="APPROVED"
def fake_marker_lesson(p): p[0]["enumerated_source_anchors"][0]["approved_lesson_ids"]=["fake"]
def fake_DE_approved(p): p[1]["items"][0]["student_available"]=True
def fake_editor_student(p): p[3]["rows"][0]["student_published"]=True
def fake_editor_math(p): p[3]["rows"][0]["math_certified"]=True
def fake_editor_clause(p): p[3]["rows"][0]["official_clause_verified"]=True
def fake_editor_approved(p): p[3]["rows"][0]["teacher_approved"]=True
def fake_source_marker_duplicate(p): p[0]["enumerated_source_anchors"][1]["id"]=p[0]["enumerated_source_anchors"][0]["id"]
def fake_source_page_count(p): p[0]["pages"][15]["source_numbered_marker_count"]+=1
def fake_track(p): p[3]["rows"][0]["track"]="UNOFFICIAL"
def fake_legacy_remove(p): p[4]["entries"].pop()
def fake_legacy_publish(p): p[4]["entries"][0]["student_publishable"]=True
def fake_legacy_math(p): p[4]["entries"][0]["legacy_lesson_certified"]=True
def fake_legacy_track(p): p[4]["entries"][0]["track"]="ELECTIVE_E"
def fake_editorial_double(p): p[3]["rows"][1]["editorial_id"]=p[3]["rows"][0]["editorial_id"]
def fake_DE_item_duplicate(p): p[1]["items"][1]["id"]=p[1]["items"][0]["id"]
def fake_ghost_page(p): p[2]["pages"][0]["printed_page"]=999
def fake_DE_orphan(p): p[1]["items"][0]["printed_page"]=200
def fake_count_mismatch(p): p[0]["denominator_contract"]["by_track_source_numbered_candidates"]["ELECTIVE_A"]+=1

@pytest.mark.parametrize("mutate",[
    fake_source_sha,fake_DE_sha,fake_pdfkit_sha,fake_clause_sha,
    fake_atom_total,fake_editor_total,remove_page,repeat_page,
    move_pdf_index,fake_missing_hash,fake_all_reviewed,fake_DE_complete,
    fake_DE_teacher,fake_marker_approved,fake_marker_lesson,fake_DE_approved,
    fake_editor_student,fake_editor_math,fake_editor_clause,fake_editor_approved,
    fake_source_marker_duplicate,fake_source_page_count,fake_track,
    fake_legacy_remove,fake_legacy_publish,fake_legacy_math,
    fake_legacy_track,fake_editorial_double,fake_DE_item_duplicate,
    fake_ghost_page,fake_DE_orphan,fake_count_mismatch,
],ids=lambda f:f.__name__)
def test_fail_closed_rejects_forgery_drift_or_missing_evidence(mutate):
    p=payload()
    mutate(p)
    with pytest.raises(ValueError):
        rebuild(p)


def test_page35_image_reveals_curriculum_content_but_no_approval():
    split = G.load(G.SPLIT35)
    assert split["mac_rendered_page_png_sha256"] == G.PAGE35_PNG_SHA
    assert split["source_printed_page"] == 35
    assert split["official_atom_denominator"] is None
    assert RESULT["page35_visual_evidence"]["new_project_authored_split_candidates"] == 7
    assert "MODELLING" in RESULT["page35_visual_evidence"]["image_read_outcome"]
    assert not RESULT["page35_visual_evidence"]["original_image_committed"]
    assert not split["source_passages_committed"]
    assert all(x["teacher_review"] == "REVIEW_PENDING"
               and x["cross_page_deduplication"] == "PENDING"
               and x["full_lesson_available"] is False
               and x["student_published"] is False
               for x in split["candidates"])

@pytest.mark.parametrize("candidate",G.load(G.SPLIT35)["candidates"],ids=lambda r:r["id"])
def test_seven_page35_visual_original_splits_are_unapproved_editorial_candidates(candidate):
    assert candidate["id"].startswith("KB51-C-P035-V")
    assert candidate["kind"] in {"CONCEPT","METHOD","TEACHING_ACTIVITY"}
    assert len(candidate["goal"])>15
    assert len(candidate["misconception"])>10
    assert candidate["source_region"] in {
        "MODELLING_FLOWCHART","MATH_INQUIRY_EXPLANATION","COMPULSORY_RESEARCH_REQUIREMENT"}
    assert candidate["mathematical_formal_certification"] is False
    assert candidate["student_published"] is False

@pytest.mark.parametrize("bad_field,bad_value",[
    ("mac_rendered_page_png_sha256","a"*64),
    ("source_printed_page",34),
    ("teacher_review","APPROVED"),
    ("official_atom_denominator",7),
    ("rendered_source_image_committed",True),
    ("source_passages_committed",True),
])
def test_page35_visual_candidate_source_and_authority_forgery_rejected(bad_field,bad_value):
    bad=copy.deepcopy(G.load(G.SPLIT35))
    bad[bad_field]=bad_value
    with pytest.raises(ValueError):
        G.assemble(split35=bad)

@pytest.mark.parametrize("bad_field,bad_value",[
    ("teacher_review","APPROVED"),
    ("cross_page_deduplication","COMPLETED"),
    ("full_lesson_available",True),
    ("student_published",True),
    ("mathematical_formal_certification",True),
])
def test_page35_editorial_candidate_forged_completion_rejected(bad_field,bad_value):
    bad=copy.deepcopy(G.load(G.SPLIT35))
    bad["candidates"][0][bad_field]=bad_value
    with pytest.raises(ValueError):
        G.assemble(split35=bad)

def test_page35_duplicate_source_candidate_id_rejected():
    bad=copy.deepcopy(G.load(G.SPLIT35))
    bad["candidates"][1]["id"]=bad["candidates"][0]["id"]
    with pytest.raises(ValueError):
        G.assemble(split35=bad)
