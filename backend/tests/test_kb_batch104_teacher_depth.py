"""Batch104: twelve substantive lessons, reject unsafe mutations, finite maths.

No claim of human approval, official scope completion, proof certification or
verification of unrestricted student free-text reasoning.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import pytest
from pydantic import ValidationError
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
import build_kb_batch104_deep as B
from kb_batch104_authoring import UNITS
from app.kb_batch104_oracles import witness
from app.deep_knowledge import DeepLesson,lessons,curriculum
from app.deep_retrieval import student_evidence_lookup

@pytest.mark.parametrize("index",range(12))
def test_every_lesson_has_complete_specific_original_math_and_two_worked_examples(index):
    row=UNITS[index]
    d=B.build()[0][index]
    x=DeepLesson.model_validate(d)
    assert x.id==f"math.hs.batch104.{index+1:02d}"
    assert x.curriculum_ids==[row["curriculum_id"]]
    assert x.kind==row["kind"] and x.title==row["title"]
    assert x.statement==row["statement"] and len(x.statement)>=35
    assert len(x.assumptions)>=2 and len(x.notation)>=2
    assert len(x.worked_examples)==2 and x.worked_examples[0].question!=x.worked_examples[1].question
    assert len(x.hint_ladder)==3 and len(set(x.hint_ladder))==3
    assert x.counterexamples[0].example==row["negative"][1]
    assert len(x.misconceptions)==1 and x.transfer.near and x.transfer.far
    if x.kind=="theorem":
        assert len(x.proof_steps)>=3
        assert all(len(s.reason)>12 for s in x.proof_steps)
    else:
        assert len(x.rationale_steps)>=3
        assert x.definition is not None if x.kind=="concept" else x.statement is not None
    assert x.review.status=="REVIEW_PENDING"
    assert not x.review.reviewer_id and not x.review.review_record
    assert x.teacher_solution_visibility=="TEACHER_ONLY"
    assert x.provenance.permission=="PROJECT_AUTHORED"

@pytest.mark.parametrize("index",range(12))
def test_exact_oracle_checks_valid_and_invalid_cases_without_proving_universal_claim(index):
    r=witness(index)
    assert r["exact_positive"] is True and r["invalid_case_rejected"] is True
    assert r["universally_certified"] is False
    assert r["student_response_verified"] is False
    assert r["teacher_approved"] is False

@pytest.mark.parametrize("invalid",[None,False,True,-1,12,13,0.0,"1",{},[],(1,)])
def test_oracle_rejects_unknown_or_malicious_index(invalid):
    with pytest.raises(ValueError):
        witness(invalid)

@pytest.mark.parametrize("kind",[
  "missing","extra","invalid_curriculum","unproven_kind",
  "no_examples","incomplete_proof","no_statement","no_counterexample",
  "fake_hint","bad_link","forward_link","self_link","duplicate_link",
])
def test_builder_fail_closed_on_bad_source_or_graph(kind):
    rows=deepcopy(UNITS)
    links=deepcopy(B.LINKS)
    if kind=="missing":rows.pop()
    if kind=="extra":rows.append(deepcopy(rows[0]))
    if kind=="invalid_curriculum":rows[0]["curriculum_id"]="HS-MATH-999999"
    if kind=="unproven_kind":rows[0]["kind"]="LLM_CERTIFIED"
    if kind=="no_examples":rows[0]["examples"].pop()
    if kind=="incomplete_proof":rows[0]["reasoning"][0]["reason"]="guess"
    if kind=="no_statement":rows[0]["statement"]="x"
    if kind=="no_counterexample":rows[0]["negative"]=("yes","bad","bad")
    if kind=="fake_hint":rows[0]["hints"][1]=rows[0]["hints"][0]
    if kind=="bad_link":links[3]=(13,)
    if kind=="forward_link":links[3]=(4,)
    if kind=="self_link":links[3]=(3,)
    if kind=="duplicate_link":links[3]=(2,2)
    with pytest.raises((ValueError,IndexError,KeyError)):
        B.build(units=rows,links=links)

def test_teacher_forgery_and_teacher_solution_exposure_fail_closed():
    docs,_=B.build()
    fake=deepcopy(docs[0])
    fake["review"].update(status="APPROVED",reviewer_id="teacher-123",
                          reviewed_at="2026-11-12T08:00:00Z",review_record="invented")
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(fake)
    all_ids={x.id for x in lessons()}
    assert {x["id"] for x in docs} <= all_ids
    for d in docs:
        payload=student_evidence_lookup(d["title"])
        assert payload["status"]=="NO_APPROVED_EVIDENCE"
        assert payload["teacher_solution_exposed"] is False
        # Never leak the full teacher response, even if overlap by chance with title.
        serialized=json.dumps(payload,ensure_ascii=False)
        for ex in d["worked_examples"]:
            assert ex["question"] not in serialized
            assert ex["check"] not in serialized

def test_source_evidence_lineage_not_a_false_official_syllabus_completion():
    docs,audit=B.build()
    assert len(docs)==12 and audit["new_worked_examples"]==24
    assert audit["new_hint_levels"]==36
    assert audit["new_finite_math_witnesses"]==12
    assert audit["new_bad_case_rejections"]==12
    assert audit["prerequisite_edges_editor_only"]==5
    assert audit["official_atom_denominator"] is None
    assert len(audit["official_atom_denominators_by_seven_tracks"])==7
    assert all(v is None for v in audit["official_atom_denominators_by_seven_tracks"].values())
    assert audit["teacher_approved"]==audit["student_authoritative_index_eligible"]==0
    assert audit["general_theorem_certificates"]==0
    assert audit["unresolved_previous_textual_prerequisites"]==172
    assert audit["engineering_mapping_sha256"]==sha256(
        (ROOT/"curriculum/highschool_math/curriculum_map.json").read_bytes()).hexdigest()
    assert audit["editorial_source_file_sha256"]==sha256(B.AUTHOR.read_bytes()).hexdigest()
    assert all(s["official_atom_id"] is None and not s["source_clauses_verified"]
               for s in audit["lesson_to_project_topic"])

def test_deterministic_pack_complete_markdown_and_review_graph():
    docs,audit=B.build()
    assert B.PACK.read_text(encoding="utf8")==B.canonical(docs)
    assert B.AUDIT.read_text(encoding="utf8")==B.canonical(audit)
    markdown=B.MD.read_text(encoding="utf8")
    assert markdown==B.markdown(docs,audit)
    lookup={d.id:d for d in lessons()}
    for d in docs:
        assert d["statement"] in markdown
        assert d["counterexamples"][0]["example"] in markdown
        assert all(e["answer"] in markdown and e["check"] in markdown for e in d["worked_examples"])
        assert all(dep in lookup and dep!=d["id"] for dep in d["prerequisite_lesson_ids"])
    assert len({d["id"] for d in docs})==12
    assert len({d["curriculum_ids"][0] for d in docs})==12
    assert all(d["review"]["status"]=="REVIEW_PENDING" for d in docs)
    assert len(lookup)>=audit["deep_lesson_documents_with_new_drafts"]
    assert all(d["id"] in lookup for d in docs)

def test_existing_eng_mappings_not_official_full_atom_denominator():
    rows=curriculum()
    _,audit=B.build()
    assert len(rows)==audit["existing_project_mapping_count"]
    assert sum(audit["engineering_map_counts_by_level"].values())==len(rows)
    assert audit["deep_lesson_documents_with_new_drafts"]==audit["existing_deep_lesson_documents"]+12
