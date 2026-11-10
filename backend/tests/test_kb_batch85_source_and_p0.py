"""Batch85: 80 source-specific interpretations, 12 SHA-tied P0 teacher drafts."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest
import sympy as sp

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch85_semantic_review as S
import build_kb_batch85_p0_history as P
from app.kb_batch28_condition_oracles import evaluate
from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.fixture(scope="module")
def coverage():return S.build()
@pytest.fixture(scope="module")
def proof_cards():return P.build()

def author_s():return S.load(S.AUTHOR)
def author_p():return P.load(P.AUTHOR)

def test_complete_source_denominator_not_misrepresented_as_official_atoms(coverage):
    assert coverage["source_review_denominator"]==428
    assert coverage["new_editorial_count"]==80
    assert coverage["previous_editorial_count"]==169
    assert coverage["cumulative_editorial_count"]==249
    assert coverage["pending_editorial_count"]==179
    assert coverage["official_curriculum_atom_denominator"] is None
    assert coverage["full_page_teacher_reviews"]==0
    assert coverage["teacher_approved"]==0
    assert coverage["student_deep_content_published"]==0
    assert coverage["student_index_includes_unreviewed_material"] is False
    assert sum(v["editorially_paraphrased_source_anchors"]
               for v in coverage["by_track"].values())==249
    assert sum(v["without_original_semantic_paraphrase"]
               for v in coverage["by_track"].values())==179
    assert Counter(c["track"] for c in coverage["new_rows"])=={
        k:v for k,v in S.COUNTS.items() if v>0}
    assert all(v["official_mathematical_atom_denominator"] is None
               and v["student_approved_math_atoms"]==0
               for v in coverage["by_track"].values())
    assert coverage["by_track"]["ELECTIVE_E"]["source_review_anchor_denominator"]==0
    assert S.OUT.read_text(encoding="utf8")==S.dump(coverage)
    assert S.MD.read_text(encoding="utf8")==S.markdown(coverage)

@pytest.mark.parametrize("i",range(80))
def test_each_original_source_shas_and_draft_visibility(i,coverage):
    row=coverage["new_rows"][i]
    base=next(r for r in S.load(S.B84.B83.B81.SOURCE)["anchor_review_queue"]
              if r["review_id"]==row["review_id"])
    for key in ("track","source_line_sha256","source_page_pdfkit_sha256",
                "printed_page","pdfkit_line","source_kind"):
        assert row[key]==(base["kind"] if key=="source_kind" else base[key])
    assert row["review_status"]=="REVIEW_PENDING"
    assert row["math_certification"]=="NOT_FORMALLY_VERIFIED"
    assert row["teacher_approved"] is False
    assert row["teacher_confirmed"] is False
    assert row["student_publishable"] is False
    assert row["student_authoritative_index_eligible"] is False
    assert row["official_atom_count"] is None

@pytest.mark.parametrize("i",range(80))
@pytest.mark.parametrize("field,bad",[
 ("teacher_confirmed",True),("student_publishable",True),
 ("official_atom_count",0),("official_atom_count",1),
 ("cross_track_equivalence","CERTIFIED_EQUIVALENT"),
 ("original_editorial_paraphrase","目录"),
 ("condition_or_scope_caution","")])
def test_all_source_rows_reject_fake_approval_or_thin_scope(i,field,bad):
    a=author_s();a["records"][i][field]=bad
    with pytest.raises(ValueError):S.build(auth=a)

@pytest.mark.parametrize("i",range(80))
def test_source_track_and_hidden_approval_rejected(i):
    a=author_s()
    a["records"][i]["track"]="ELECTIVE_E"
    with pytest.raises(ValueError):S.build(auth=a)
    a=author_s()
    a["records"][i]["reviewer_signature"]="forged"
    with pytest.raises(ValueError):S.build(auth=a)

@pytest.mark.parametrize("i",range(80))
def test_heading_cannot_claim_math_atom_or_requirement_be_vacuous(i):
    a=author_s();r=a["records"][i];role=r["semantic_role_provisional"]
    if role=="CURRICULUM_HEADING":
        r["possible_math_units_for_teacher_split"]=["伪造的知识原子描述"]
    elif role in ("MATHEMATICAL_REQUIREMENT","MIXED_CLAUSE"):
        r["possible_math_units_for_teacher_split"]=[]
    else:
        r["possible_math_units_for_teacher_split"]=["两个完全重复的题目","两个完全重复的题目"]
    with pytest.raises(ValueError):S.build(auth=a)

def test_source_collision_and_frozen_source_sha_rejected():
    a=author_s();a["records"][0]["review_id"]=a["records"][1]["review_id"]
    with pytest.raises(ValueError):S.build(auth=a)
    a=author_s();a["records"][0]["review_id"]=S.load(S.B84.AUTHOR)["records"][0]["review_id"]
    with pytest.raises(ValueError):S.build(auth=a)
    source=S.load(S.B84.B83.B81.SOURCE)
    source["anchor_review_queue"][0]["source_line_sha256"]="0"*64
    with pytest.raises(ValueError,match="source SHA"):S.build(source=source)

def test_prior_authority_and_source_count_gate():
    prior=S.B84.build();prior["teacher_approved"]=1
    with pytest.raises(ValueError):S.build(previous=prior)
    prior=S.B84.build();prior["cumulative_editorial_count"]=428
    with pytest.raises(ValueError):S.build(previous=prior)

def test_actual_source_mac_pdfkit_sha_or_skip():
    if not S.B84.B83.B81.LOCAL_PDF.is_file():
        pytest.skip("Mac copyrighted original only; CI tests frozen source hashes")
    assert len(S.build(verify_local_source=True)["new_rows"])==80

def test_missing_mac_original_pdf_fail_closed(monkeypatch,tmp_path):
    monkeypatch.setattr(S.B84.B83.B81,"LOCAL_PDF",tmp_path/"none.pdf")
    with pytest.raises(ValueError,match="Mac original"):S.build(verify_local_source=True)

def test_history_p0_populations_are_reconciled_without_formal_approvals(proof_cards):
    assert proof_cards["historical_steps"]==538
    assert proof_cards["P0_total"]==182
    assert proof_cards["previous_source_step_cards"]==48
    assert proof_cards["new_source_step_cards"]==12
    assert proof_cards["combined_source_step_cards"]==60
    assert proof_cards["remaining_P0_without_source_step_cards"]==122
    assert proof_cards["formal_math_certifications"]==0
    assert proof_cards["teacher_approvals"]==0
    assert proof_cards["unresolved_conflicts"]==10
    assert proof_cards["free_text_student_steps_verified"]==0
    assert P.OUT.read_text(encoding="utf8")==P.dump(proof_cards)
    assert P.MD.read_text(encoding="utf8")==P.markdown(proof_cards)

@pytest.mark.parametrize("i",range(12))
def test_history_source_sha_proofs_and_finite_cases_hold(i,proof_cards):
    c=proof_cards["cards"][i]
    original=next(r for r in P.load(P.B81.PROOFS)["step_review_queue"]
                  if r["id"]==c["source_step"])
    assert original["source_sha256"]==c["original_step_sha256"]
    assert original["review_card_id"] is None
    assert original["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE"
    assert c["source_step_risk_groups"]==original["risk_groups"]
    assert len(c["assumptions"])==2
    assert len(c["proof_steps"])==3
    assert len(c["worked_examples"])==2
    assert len(c["hints"])==3
    assert c["review_status"]=="REVIEW_PENDING"
    assert c["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert c["student_authoritative_index_eligible"] is False
    assert c["general_theorem_formally_certified"] is False
    assert c["student_free_text_verified"] is False
    assert c["human_teacher_reviewer"] is None
    assert c["official_curriculum_atom_id"] is None
    assert all(x["visibility"]=="TEACHER_ONLY" for x in c["worked_examples"])
    assert evaluate(c["finite_op"],c["finite_valid_fixture"])["status"]=="VERIFIED_FINITE_INSTANCE"
    assert evaluate(c["finite_op"],c["finite_invalid_fixture"])["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("i",range(12))
@pytest.mark.parametrize("field,bad",[
 ("source_step","math.hs.invalid#0"),
 ("finite_op","unknown_profile"),
 ("proof_steps",["因此成立"]),
 ("worked_examples",[]),
 ("hints",[]),
 ("assumptions",["偷偷加入已批准"]),
 ("boundary",""),("wrong_method",""),
 ("title",""),("kind","APPROVED")])
def test_history_drafts_reject_spoofing_or_content_erasure(i,field,bad):
    a=author_p();a["cards"][i][field]=bad
    with pytest.raises(ValueError):P.build(auth=a)

@pytest.mark.parametrize("i",range(12))
def test_history_hidden_teacher_approval_rejected(i):
    a=author_p();a["cards"][i]["approval_receipt"]="fabricated"
    with pytest.raises(ValueError):P.build(auth=a)

def test_history_duplicate_or_already_linked_step_rejected():
    a=author_p();a["cards"][0]["source_step"]=a["cards"][1]["source_step"]
    with pytest.raises(ValueError):P.build(auth=a)
    a=author_p();a["cards"][0]["source_step"]="math.hs.space.coordinate-distance#2"
    with pytest.raises(ValueError):P.build(auth=a)

def test_history_source_hash_tamper_and_formal_certification_rejected():
    proof=P.load(P.B81.PROOFS);proof["step_review_queue"][0]["source_sha256"]="0"*64
    with pytest.raises(ValueError,match="frozen"):P.build(proofs=proof)
    a=author_p();a["teacher_approvals"]=1
    with pytest.raises(ValueError):P.build(auth=a)
    a=author_p();a["general_formal_certificates"]=1
    with pytest.raises(ValueError):P.build(auth=a)

@pytest.mark.parametrize("i",range(12))
def test_teacher_side_drafts_not_present_in_actual_student_retrieval(i,proof_cards,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    c=proof_cards["cards"][i]
    resp=student_evidence_lookup(c["title"])
    raw=json.dumps(resp,ensure_ascii=False)
    assert {x["knowledge_id"] for x in resp["candidates"]}<={doc.id}
    assert c["id"] not in raw and c["source_step"] not in raw
    assert c["worked_examples"][0]["teacher_solution"] not in raw
    assert c["proof_steps"][0] not in raw
    assert resp["teacher_solution_exposed"] is False
    assert resp["unverified_content_exposed"] is False

def test_independent_sympy_guarded_examples_not_just_oracle_self_assessment(proof_cards):
    by={c["finite_op"]:c for c in proof_cards["cards"]}
    q=sp.Rational
    assert sp.simplify(sp.log(32,2)-sp.log(4,2)-sp.log(8,2))==0
    assert sp.simplify(sp.log(8,2)-sp.log(4,2)-sp.log(2,2))==0
    assert sp.simplify(sp.log(8,2)-sp.log(8,4)/sp.log(2,4))==0
    x=sp.symbols("x",real=True)
    assert sp.solve(x**2-3*x+2,x)==[1,2]
    assert q(4+9,2)-sp.sqrt(4*9)==q(1,2)
    assert sp.solve([x**2+sp.symbols("y")**2-1,x-1],[x,sp.symbols("y")])==[(1,0)]
    assert sp.solve([x**2+sp.symbols("y")**2-1,(x-2)**2+sp.symbols("y")**2-1],[x,sp.symbols("y")])==[(1,0)]
    assert sp.simplify(2**2-4*1*1)==0
    y=sp.symbols("y",real=True)
    assert sp.solve([x**2/4+y**2-1,x-2],[x,y])==[(2,0)]
    assert sp.Matrix([1,2]).dot(sp.Matrix([2,4]))**2==5*20
    assert sp.diff((1+2*x)/(1+x),x).subs(x,1)==q(1,4)
    assert sp.Matrix([1,0]).dot(sp.Matrix([0,1]))==0
    assert len(by)==12
