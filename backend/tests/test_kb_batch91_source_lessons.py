"""Batch91 K00/K01 content, math, retrieval, authority and privacy regressions."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch91_source_lessons as B
from app.deep_knowledge import DeepLesson, lessons, coverage_report
from app.deep_retrieval import editor_draft_search, editor_draft_full, student_evidence_lookup, EditorOnlyError
from app.kb_batch91_independent_oracles import verify, evaluate_all

@pytest.fixture(scope="module")
def pack():
    return B.build()
@pytest.fixture(scope="module")
def baseline():
    return B.B90.build(), B.B89.build()[1]

def test_typed_source_denominators_are_not_official(pack):
    cards,scope=pack
    assert len(cards)==20
    assert scope["source_anchor_count"]==428
    assert scope["source_provisional_labels"]==300
    assert scope["source_relations_editorial"]==60
    assert scope["unpaired_provisional_labels"]==182
    assert scope["official_curriculum_atom_denominator"] is None
    assert set(scope["official_atom_counts_by_track"])==set(B.TRACK)
    assert all(v is None for v in scope["official_atom_counts_by_track"].values())
    assert scope["teacher_approved"]==scope["student_authoritative_release"]==0
    assert scope["general_theorem_proof_certifications"]==0
    assert scope["historical_proof_steps_not_certified"]==538
    assert scope["unresolved_math_conflicts"]==10

def test_all_seven_tracks_clearly_accounted_for(pack):
    _,scope=pack
    bytrack=scope["per_track"]
    assert sum(x["project_provisional_candidate_count"] for x in bytrack.values())==300
    assert sum(x["new_deep_draft_candidates"] for x in bytrack.values())==20
    assert sum(x["remaining_without_batch91_deep_draft"] for x in bytrack.values())==280
    assert bytrack["ELECTIVE_E"]["project_provisional_candidate_count"]==0
    assert bytrack["ELECTIVE_E"]["source_track_official_atom_denominator"] is None
    assert all(x["approved"]==0 for x in bytrack.values())

@pytest.mark.parametrize("index",range(20))
def test_twenty_complete_deep_lessons_typed(pack,index):
    cards,scope=pack
    doc=DeepLesson.model_validate(cards[index])
    assert doc.id==f"math.hs.batch91.{index+1:02d}"
    assert len(doc.worked_examples)==2
    assert len(doc.hint_ladder)==3
    assert doc.transfer.near and doc.transfer.far
    assert len(doc.counterexamples)==len(doc.misconceptions)==1
    assert len(doc.notation)>=3
    assert len(doc.assumptions)>=2
    assert doc.review.status=="REVIEW_PENDING"
    assert doc.teacher_solution_visibility=="TEACHER_ONLY"
    if doc.kind=="theorem":
        assert len(doc.proof_steps)>=3
        assert all(len(x.reason)>20 for x in doc.proof_steps)
    else:
        assert len(doc.rationale_steps)>=3
    assert doc.review.reviewer_id is None
    link=scope["canonical_lesson_source_links"][index]
    assert link["knowledge_id"]==doc.id
    assert link["source_candidate_id"]
    assert link["source_line_sha256"]
    assert len(link["source_line_sha256"])==64
    assert link["curriculum_atom_id"] is None
    assert link["teacher_review"] is None
    assert link["student_publishable"] is False
    assert link["editor_status"]=="REVIEW_PENDING"
    assert link["finite_mathematical_evidence"]["general_theorem_formally_certified"] is False

@pytest.mark.parametrize("index",range(1,21))
def test_twenty_independent_exact_finite_witnesses(index):
    result=verify(index)
    assert result["positive"]=="VERIFIED_FINITE_INSTANCE"
    assert result["negative"]=="INVALID_GENERALIZATION_OR_BOUNDARY_REJECTED"
    assert result["general_theorem_formally_certified"] is False
    assert result["teacher_approved"] is False

@pytest.mark.parametrize("index",range(1,21))
def test_canonical_corpus_and_editor_search(pack,index):
    doc=pack[0][index-1]
    live=next(x for x in lessons() if x.id==doc["id"])
    assert live.title==doc["title"]
    hits=editor_draft_search(doc["title"],scope="EDITOR_LOCAL",limit=20)
    assert any(h["knowledge_id"]==doc["id"] for h in hits)

@pytest.mark.parametrize("index",range(20))
def test_worked_examples_never_in_student_evidence(pack,index):
    doc=pack[0][index]
    answer=doc["worked_examples"][0]["answer"]
    assert answer not in " ".join(h["title"] for h in
                    editor_draft_search(doc["title"],scope="EDITOR_LOCAL",limit=20))
    with pytest.raises(EditorOnlyError):
        editor_draft_full(doc["id"])
    with pytest.raises(EditorOnlyError):
        editor_draft_search(doc["title"])
    result=student_evidence_lookup(doc["title"])
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["teacher_solution_exposed"] is False
    assert result["unverified_content_exposed"] is False
    assert answer not in json.dumps(result,ensure_ascii=False)

def test_corpus_counts_are_not_teacher_approval(pack):
    d=coverage_report()
    assert d["deep_lesson_documents"]>=307
    assert d["review_statuses"]["REVIEW_PENDING"]>=307
    assert d["human_teacher_review_complete"] is False
    assert d["direct_student_teaching_enabled"] is False

@pytest.mark.parametrize("poison",[
    "duplicate_anchor","wrong_anchor","wrong_curriculum","extra_field",
    "missing_lesson","repeated_lesson","empty_assumptions","missing_proof_step",
    "missing_example","short_formal_definition","short_counterexample",
    "missing_hint","missing_transfer","missing_symbol",
])
def test_source_authoring_negative_regressions(pack,baseline,poison):
    records=deepcopy(B.DATA)
    first=records[0]
    if poison=="duplicate_anchor":records[1]["anchor"]=first["anchor"]
    elif poison=="wrong_anchor":first["anchor"]="NOT-IN-OFFICIAL-SOURCE"
    elif poison=="wrong_curriculum":first["curriculum_id"]="HS-MATH-99999"
    elif poison=="extra_field":first["teacher_approved"]=True
    elif poison=="missing_lesson":records.pop()
    elif poison=="repeated_lesson":records.append(deepcopy(first))
    elif poison=="empty_assumptions":first["assumptions"]=[]
    elif poison=="missing_proof_step":records[3]["steps"].pop()
    elif poison=="missing_example":first["examples"].pop()
    elif poison=="short_formal_definition":first["definition"]="test"
    elif poison=="short_counterexample":first["negative"]=("fake","test","none")
    elif poison=="missing_hint":first["hints"].pop()
    elif poison=="missing_transfer":first["transfer"]=("x","y")
    elif poison=="missing_symbol":first["notation"]=[]
    with pytest.raises((ValueError,KeyError)):
        B.build(auth=records,previous=baseline[0],history=baseline[1])

@pytest.mark.parametrize("poison",[
    ("official_curriculum_atom_denominator",300),
    ("teacher_approved",1),("student_published",1),
    ("provisional_candidate_total",299),
    ("source_anchor_editorials",427),
])
def test_upstream_authority_scope_forgery_rejected(baseline,poison):
    prior=deepcopy(baseline[0]);prior[poison[0]]=poison[1]
    with pytest.raises(ValueError,match="upstream"):
        B.build(previous=prior,history=baseline[1])

def test_generated_report_is_reproducible(pack):
    cards,scope=pack
    assert B.OUT.read_text(encoding="utf-8")==B.dumped(cards)
    assert B.SCOPE.read_text(encoding="utf-8")==B.dumped(scope)
    assert B.DOC.read_text(encoding="utf-8")==B.markdown(cards,scope)
    assert evaluate_all()[1]["lesson_index"]==1

def test_no_duplicate_source_or_corpus_ids(pack):
    cards,scope=pack
    ids=[x.id for x in lessons()]
    anchors=[x["source_candidate_id"] for x in scope["canonical_lesson_source_links"]]
    assert len(ids)==len(set(ids))
    assert len(anchors)==len(set(anchors))==20

@pytest.mark.parametrize("index",range(20))
def test_student_hint_vs_teacher_solution_level(pack,index):
    doc=pack[0][index]
    assert not any(ex["answer"] in hint
                   for ex in doc["worked_examples"] for hint in doc["hint_ladder"])
    assert all("teacher_solution" not in hint for hint in doc["hint_ladder"])
    assert all(ex["steps"] and ex["check"] for ex in doc["worked_examples"])

def test_prerequisite_graph_is_explicit_acyclic_and_student_safe(pack):
    docs,scope=pack
    by_id={x["id"]:x for x in docs}
    assert set(B.PREREQUISITE_LINKS)=={
        "math.hs.batch91.12","math.hs.batch91.13","math.hs.batch91.15",
        "math.hs.batch91.18","math.hs.batch91.19","math.hs.batch91.20"}
    for doc in docs:
        target=B.PREREQUISITE_LINKS.get(doc["id"],[])
        assert doc["prerequisite_lesson_ids"]==target
        assert all(key in by_id for key in target)
        assert doc["id"] not in target
    assert all(not link["student_publishable"] for link in scope["canonical_lesson_source_links"])

def test_zero_ratio_geometric_series_boundary_is_not_0_power_0(pack):
    geometric=next(x for x in pack[0] if x["id"]=="math.hs.batch91.07")
    assert any("q=0" in v and "0^0" in v for v in geometric["boundaries"])
    # Avoid evaluating an undefined 0^0: a1 is defined as the first term.
    first=5
    recurrence=[first]
    for _ in range(3):
        recurrence.append(recurrence[-1]*0)
    assert recurrence==[5,0,0,0]
    assert sum(recurrence)==first
