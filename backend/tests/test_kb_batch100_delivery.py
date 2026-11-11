"""Mac-only Batch100 regression: source-lineage, math premises, exact instances, safe RAG."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
import build_kb_batch100_depth as DEPTH
import build_kb_batch100_coverage as COVER
from kb_batch100_authoring import ROWS,SELECTED
from app.kb_batch100_oracles import IDS,check_all,evaluate,nonzero,pair_balanced,quadratic_interval,matrix_prediction
from app.deep_knowledge import DeepLesson,lessons
from app.deep_retrieval import student_evidence_lookup
from pydantic import ValidationError
from sympy import Matrix

@pytest.mark.parametrize("index",SELECTED)
def test_each_of_20_authoring_records_mathematical_fields_and_examples(index):
    r=ROWS[index]
    assert r["kind"] in {"concept","method","theorem"}
    assert len(r["why"])==len(r["hints"])==3
    assert len(r["examples"])==2
    assert r["examples"][0]["question"]!=r["examples"][1]["question"]
    assert len(set(r["hints"]))==3
    assert len(r["transfer"])==2
    for e in r["examples"]:
        assert all(len(z)>0 for z in (e["question"],e["answer"],e["check"]))
        assert len(e["steps"])==2
        assert all(len(z)>10 for z in e["steps"])

@pytest.mark.parametrize("index",SELECTED)
def test_20_exact_witnesses_reject_bad_boundary(index):
    witness=evaluate(index)
    assert witness["exact_positive"] and witness["invalid_case_rejected"]
    assert not witness["general_theorem_certified"]
    assert not witness["student_publishable"]
    assert not witness["teacher_approved"]

@pytest.mark.parametrize("invalid",(None,True,False,-1,1,20,"0",0.0,2.0,{},[]))
def test_unrecognized_oracle_never_returns_success(invalid):
    with pytest.raises(ValueError):
        evaluate(invalid)

def test_all_oracles_are_distinct_and_finite_only():
    assert len(IDS)==len(set(IDS))==len(check_all())==20
    assert not any(x["general_theorem_certified"] for x in check_all().values())

@pytest.mark.parametrize("lesson_id",[f"math.hs.batch100.{n:02d}" for n in range(1,21)])
def test_new_lessons_have_review_pending_and_no_student_authority(lesson_id):
    x=next(v for v in lessons() if v.id==lesson_id)
    assert x.review.status=="REVIEW_PENDING"
    assert x.teacher_solution_visibility=="TEACHER_ONLY"
    assert x.prerequisite_lesson_ids==[]
    assert len(x.worked_examples)==2
    assert len(x.hint_ladder)==3
    assert x.provenance.permission=="PROJECT_AUTHORED"
    result=student_evidence_lookup(x.title)
    assert result["status"]=="NO_APPROVED_EVIDENCE"
    assert result["teacher_solution_exposed"] is False
    body=json.dumps(result,ensure_ascii=False)
    for ex in x.worked_examples:
        if len(ex.answer)>2:assert ex.answer not in body

@pytest.mark.parametrize("number",range(1,21))
def test_source_link_has_distinct_sha_and_unreviewed_track_alignment(number):
    _,audit=DEPTH.build()
    row=audit["canonical_lesson_source_links"][number-1]
    assert row["lesson_id"]==f"math.hs.batch100.{number:02d}"
    assert len(row["source_line_sha256"])==64
    assert row["source_candidate_id"].startswith("KB")
    assert row["engineering_topic_alignment"]=="UNREVIEWED_EDITORIAL_CANDIDATE"
    assert row["engineering_track_status"] in {"MATCH_EDITORIAL_ONLY","TRACK_UNRESOLVED"}
    assert row["review_status"]=="REVIEW_PENDING"
    assert row["official_atom_id"] is None and not row["student_authoritative_index_eligible"]
    assert not row["bounded_exact_instance_witness"]["general_theorem_certified"]

@pytest.mark.parametrize("tamper",("missing","duplicate","alien","wrong_track","bad_kind","missing_example","fake_approval"))
def test_builder_negative_schema_and_authority_gates(tamper):
    rows=deepcopy(ROWS)
    selected=list(SELECTED)
    align=dict(DEPTH.ALIGNMENTS)
    if tamper=="missing":selected.pop()
    if tamper=="duplicate":selected[-1]=selected[0]
    if tamper=="alien":selected[-1]=1000
    if tamper=="wrong_track":align[6]="HS-MATH-143" # C mapping while source A
    if tamper=="bad_kind":rows[0]["kind"]="proof_from_llm"
    if tamper=="missing_example":rows[0]["examples"].pop()
    if tamper=="fake_approval":rows[0]["why"]=[]
    with pytest.raises((ValueError,KeyError)):
        DEPTH.build(selected=tuple(selected),records=rows,alignments=align)

def test_teacher_review_forgery_cannot_validate():
    payloads,_=DEPTH.build()
    fake=deepcopy(payloads[0])
    fake["review"]={"status":"APPROVED","reviewer_id":"fake",
                    "reviewed_at":"2026-11-12T02:00:00Z","review_record":"fake"}
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(fake)

def test_invalid_math_input_edges_rejected():
    with pytest.raises(ValueError):nonzero([0,0])
    with pytest.raises(ValueError):pair_balanced([0,1],[0,0,1])
    with pytest.raises(ValueError):quadratic_interval(1,-4,0,5,0)
    with pytest.raises(ValueError):matrix_prediction([[1,1],[1,1],[1,1]],[2,3,4])

def test_20_packs_and_markdown_are_deterministic():
    docs,report=DEPTH.build()
    assert len(docs)==20
    assert DEPTH.PACK.read_text(encoding="utf8")==DEPTH.dump(docs)
    assert DEPTH.AUDIT.read_text(encoding="utf8")==DEPTH.dump(report)
    assert DEPTH.DOC.read_text(encoding="utf8")==DEPTH.markdown(docs,report)
    md=DEPTH.DOC.read_text(encoding="utf8")
    for x in docs:
        assert x["title"] in md and x["statement"] in md
        for e in x["worked_examples"]:
            assert e["answer"] in md and e["check"] in md

def test_300_source_labels_strict_conservation_unknown_official_denominators():
    _,r=DEPTH.build()
    assert sum(r["stage_counts"].values())==300
    assert r["stage_counts"]=={
        "FULL_DEEP_DRAFT_PENDING_TEACHER":86,
        "INDIVIDUAL_SCOPE_EDITORIAL_PENDING":24,
        "INDIVIDUAL_SCOPE_NOT_ATOMIZED":24,
        "PAIR_COMPARISON_NOT_ATOMIZED":166}
    assert r["official_atom_denominator"] is None
    assert all(v is None for v in r["official_atom_denominators_by_track"].values())
    assert r["remaining_without_pairwise_semantic_comparison"]==134
    assert r["new_original_deep_drafts"]==20
    assert r["draft_examples"]==40
    assert r["graduated_hints"]==60
    assert r["finite_math_oracle_count"]==20
    assert r["universally_formal_certificates"]==0
    assert r["teacher_approved"]==r["student_authoritative_releases"]==0

def test_coverage_is_source_locked_and_never_a_student_graph():
    result=COVER.verify()
    assert result["total_provisional_labels"]==300
    assert result["total_teacher_pending_source_locked_deep_drafts"]==86
    assert result["new_unresolved_textual_prerequisites"]==40
    assert result["total_unresolved_textual_prerequisites"]==172
    assert result["promoted_teacher_approved_prerequisite_edges"]==0
    assert result["teacher_approved"]==0
    assert result["official_atom_denominator"] is None
    assert COVER.OUT.read_text(encoding="utf8")==json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert COVER.MD.read_text(encoding="utf8")==COVER.md(result)

@pytest.mark.parametrize("scenario",("duplicate","missing","unapproved"))
def test_coverage_rejects_forged_student_evidence_or_lost_lessons(scenario):
    docs,report=DEPTH.build()
    altered=deepcopy(docs)
    if scenario=="duplicate":altered[-1]["id"]=altered[0]["id"]
    elif scenario=="missing":altered.pop()
    else:
        altered[0]["review"]["status"]="APPROVED"
    with pytest.raises((ValueError,ValidationError)):
        COVER.verify(payloads=altered)

def test_proof_steps_are_separate_and_not_confused_with_finite_oracles():
    docs,_=DEPTH.build()
    th=[x for x in docs if x["kind"]=="theorem"]
    assert len(th)>=3
    assert all(len(x["proof_steps"])==3 and not x["rationale_steps"] for x in th)
    assert all(len(z["claim"])>=12 and len(z["reason"])>=12
               for x in th for z in x["proof_steps"])
    assert all(x["review"]["status"]=="REVIEW_PENDING" for x in th)
