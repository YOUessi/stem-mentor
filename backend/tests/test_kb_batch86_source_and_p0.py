"""Batch86: source SHA + editorial scope + 10 source-linked P0 risks, all fail-closed."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import json,sys
import pytest
import sympy as sp

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch86_semantic_review as S
import build_kb_batch86_p0_reviews as P
from app.kb_batch28_condition_oracles import evaluate
from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.fixture(scope="module")
def coverage():return S.build()
@pytest.fixture(scope="module")
def history():return P.build()
def src_auth():return S.load(S.AUTHOR)
def proof_auth():return P.load(P.AUTHOR)

def test_conservation_and_no_official_atom_promotion(coverage):
    assert coverage["schema_version"]==S.SCHEMA
    assert coverage["source_review_denominator"]==428
    assert coverage["previous_editorial_count"]==249
    assert coverage["new_editorial_count"]==89
    assert coverage["cumulative_editorial_count"]==338
    assert coverage["pending_editorial_count"]==90
    assert coverage["official_curriculum_atom_denominator"] is None
    assert coverage["teacher_approved"]==coverage["full_page_teacher_reviews"]==0
    assert coverage["student_deep_content_published"]==0
    assert coverage["student_index_includes_unreviewed_material"] is False
    assert sum(x["editorially_paraphrased_source_anchors"] for x in coverage["by_track"].values())==338
    assert sum(x["without_original_semantic_paraphrase"] for x in coverage["by_track"].values())==90
    assert Counter(r["track"] for r in coverage["new_rows"])=={
        k:v for k,v in S.COUNTS.items() if v}
    assert coverage["by_track"]["ELECTIVE_E"]["source_review_anchor_denominator"]==0
    assert S.OUT.read_text(encoding="utf8")==S.dump(coverage)
    assert S.MD.read_text(encoding="utf8")==S.markdown(coverage)
    assert coverage["new_provisional_candidates"]==len(coverage["provisional_candidates_not_deduplicated"])
    pending=coverage["pending_anchor_ids_by_track"]
    assert {tr:len(ids) for tr,ids in pending.items()}=={
        tr:row["without_original_semantic_paraphrase"]
        for tr,row in coverage["by_track"].items()}
    assert len(set().union(*[set(ids) for ids in pending.values()]))==90
    assert all(not c["teacher_approved"] and not c["student_publishable"]
               and c["official_atom_id"] is None
               and c["cross_page_equivalence"]=="NOT_ADJUDICATED"
               for c in coverage["provisional_candidates_not_deduplicated"])

@pytest.mark.parametrize("i",range(89))
def test_each_of_89_source_rows_has_original_sha_and_draft_status(i,coverage):
    row=coverage["new_rows"][i]
    original=next(x for x in S.load(S.B85.B84.B83.B81.SOURCE)["anchor_review_queue"]
                  if x["review_id"]==row["review_id"])
    for k in ("printed_page","pdfkit_line","source_line_sha256","source_page_pdfkit_sha256","track"):
        assert row[k]==original[k]
    assert row["source_kind"]==original["kind"]
    assert row["teacher_approved"] is False and row["teacher_confirmed"] is False
    assert row["student_authoritative_index_eligible"] is False
    assert row["student_publishable"] is False
    assert row["official_atom_count"] is None
    assert row["review_status"]=="REVIEW_PENDING"
    assert row["math_certification"]=="NOT_FORMALLY_VERIFIED"
    assert row["cross_track_equivalence"]=="NOT_ADJUDICATED"

@pytest.mark.parametrize("i",range(89))
@pytest.mark.parametrize("field,bad",[
 ("teacher_confirmed",True),("student_publishable",True),
 ("official_atom_count",1),("official_atom_count",0),
 ("cross_track_equivalence","CERTIFIED_EQUIVALENT"),
 ("original_editorial_paraphrase","普通数学内容"),
 ("condition_or_scope_caution",""),])
def test_all_source_edits_fail_closed_on_fake_approval_or_generic_content(i,field,bad):
    a=src_auth();a["records"][i][field]=bad
    with pytest.raises(ValueError):S.build(auth=a)

@pytest.mark.parametrize("i",range(89))
def test_each_source_track_misclassification_rejected(i):
    a=src_auth();orig=a["records"][i]["track"]
    a["records"][i]["track"]="COMPULSORY" if orig!="COMPULSORY" else "ELECTIVE_E"
    with pytest.raises(ValueError):S.build(auth=a)

@pytest.mark.parametrize("i",range(89))
def test_each_source_hidden_reviewer_receipt_rejected(i):
    a=src_auth();a["records"][i]["reviewer_signature"]="fake"
    with pytest.raises(ValueError):S.build(auth=a)

@pytest.mark.parametrize("i",range(89))
def test_heading_and_mathematical_unit_scope_enforced(i):
    a=src_auth();r=a["records"][i]
    role=r["semantic_role_provisional"]
    if role=="CURRICULUM_HEADING":
        r["possible_math_units_for_teacher_split"]=["虚构的单元知识原子"]
    elif role in ("MATHEMATICAL_REQUIREMENT","MIXED_CLAUSE"):
        r["possible_math_units_for_teacher_split"]=[]
    else:
        r["possible_math_units_for_teacher_split"]=["重复的单元知识原子","重复的单元知识原子"]
    with pytest.raises(ValueError):S.build(auth=a)

def test_source_queue_prior_approval_or_fingerprint_drift_rejected():
    a=src_auth();a["records"][0]["review_id"]=a["records"][1]["review_id"]
    with pytest.raises(ValueError):S.build(auth=a)
    a=src_auth();a["records"][0]["review_id"]=S.load(S.B85.AUTHOR)["records"][0]["review_id"]
    with pytest.raises(ValueError):S.build(auth=a)
    source=S.load(S.B85.B84.B83.B81.SOURCE)
    source["anchor_review_queue"][0]["source_line_sha256"]="0"*64
    with pytest.raises(ValueError,match="source queue"):S.build(source=source)
    prev=S.B85.build();prev["teacher_approved"]=1
    with pytest.raises(ValueError):S.build(previous=prev)
    prev=S.B85.build();prev["cumulative_editorial_count"]=428
    with pytest.raises(ValueError):S.build(previous=prev)
    a=src_auth();a["teacher_review"]="APPROVED"
    with pytest.raises(ValueError):S.build(auth=a)

def test_local_mac_original_pdfkit_evidence_or_ci_skip():
    if not S.B85.B84.B83.B81.LOCAL_PDF.is_file():
        pytest.skip("Original copyrighted PDF only on Mac; CI checks frozen SHA")
    assert len(S.build(verify_local_source=True)["new_rows"])==89

def test_missing_local_source_fails_closed(monkeypatch,tmp_path):
    monkeypatch.setattr(S.B85.B84.B83.B81,"LOCAL_PDF",tmp_path/"absent.pdf")
    with pytest.raises(ValueError,match="Mac source PDF"):S.build(verify_local_source=True)

def test_history_p0_census_with_unapproved_citations(history):
    assert history["historical_steps"]==538
    assert history["P0_total"]==182
    assert history["previous_reported_card_links"]==60
    assert history["previous_unique_P0_steps_with_drafts"]==58
    assert history["previous_duplicate_card_links"]==2
    assert history["new_teacher_draft_cards"]==10
    assert history["new_unique_P0_steps_with_drafts"]==6
    assert history["new_supplementary_reviews_of_previously_linked_steps"]==4
    assert history["combined_reported_card_links"]==70
    assert history["combined_unique_P0_steps_with_drafts"]==64
    assert history["total_duplicate_card_links"]==6
    assert history["remaining_P0_without_source_step_cards"]==118
    assert len(history["remaining_P0_source_step_ids"])==len(set(history["remaining_P0_source_step_ids"]))==118
    assert history["unresolved_conflicts"]==10
    assert history["formal_math_certifications"]==0
    assert history["teacher_approvals"]==0
    assert history["student_published"]==0
    assert history["free_text_student_steps_verified"]==0
    assert P.OUT.read_text(encoding="utf8")==P.dump(history)
    assert P.MD.read_text(encoding="utf8")==P.markdown(history)

@pytest.mark.parametrize("i",range(10))
def test_original_p0_source_SHA_and_finite_instances(i,history):
    c=history["cards"][i]
    q=P.load(P.B85.B81.PROOFS)["step_review_queue"]
    source=next(v for v in q if v["id"]==c["source_step"])
    assert source["source_sha256"]==c["original_step_sha256"]
    assert source["review_card_id"] is None
    assert source["risk_priority"].startswith("P0_")
    assert c["source_step_risk_groups"]==source["risk_groups"]
    assert len(c["assumptions"])==1
    assert len(c["proof_steps"])==3
    assert len(c["worked_examples"])==2
    assert len(c["hints"])==3
    assert c["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert c["review_status"]=="REVIEW_PENDING"
    assert c["student_authoritative_index_eligible"] is False
    assert c["general_theorem_formally_certified"] is False
    assert c["student_free_text_verified"] is False
    assert c["human_teacher_reviewer"] is None
    assert c["official_curriculum_atom_id"] is None
    assert c["finite_evidence_scope"]=="BOUNDED_EXACT_FIXTURE_NOT_UNIVERSAL_PROOF"
    assert all(x["visibility"]=="TEACHER_ONLY" for x in c["worked_examples"])
    assert evaluate(c["finite_op"],c["finite_valid_fixture"])["status"]=="VERIFIED_FINITE_INSTANCE"
    assert evaluate(c["finite_op"],c["finite_invalid_fixture"])["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("i",range(10))
@pytest.mark.parametrize("field,bad",[
 ("source_step","math.hs.nonexistent.step#0"),
 ("finite_op","fake_oracle"),
 ("proof_steps",["therefore"]),
 ("worked_examples",[]),
 ("hints",[]),
 ("assumptions",["assume a teacher approved the conclusion"]),
 ("boundary",""),
 ("wrong_method",""),
 ("title",""),
 ("kind","APPROVED"),])
def test_every_history_draft_rejects_erasure_or_source_spoof(i,field,bad):
    a=proof_auth();a["cards"][i][field]=bad
    with pytest.raises(ValueError):P.build(auth=a)

@pytest.mark.parametrize("i",range(10))
def test_history_hidden_authority_rejected(i):
    a=proof_auth();a["cards"][i]["formal_certificate"]="fake"
    with pytest.raises(ValueError):P.build(auth=a)

def test_history_extra_approval_or_tampering_rejected():
    a=proof_auth();a["teacher_approvals"]=1
    with pytest.raises(ValueError):P.build(auth=a)
    a=proof_auth();a["general_formal_certificates"]=1
    with pytest.raises(ValueError):P.build(auth=a)
    a=proof_auth();a["cards"][0]["source_step"]=a["cards"][1]["source_step"]
    with pytest.raises(ValueError):P.build(auth=a)
    a=proof_auth();a["cards"][0]["source_step"]=P.load(P.B85.AUTHOR)["cards"][0]["source_step"]
    with pytest.raises(ValueError):P.build(auth=a)
    queue=P.load(P.B85.B81.PROOFS)
    queue["step_review_queue"][0]["source_sha256"]="0"*64
    with pytest.raises(ValueError,match="historical source SHA"):P.build(proofs=queue)
    prior=P.B85.build();prior["teacher_approvals"]=1
    with pytest.raises(ValueError):P.build(previous=prior)

@pytest.mark.parametrize("i",range(10))
def test_ten_teacher_drafts_excluded_from_nonempty_student_retrieval(i,history,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,_,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    c=history["cards"][i]
    response=student_evidence_lookup(c["title"])
    raw=json.dumps(response,ensure_ascii=False)
    assert {x["knowledge_id"] for x in response["candidates"]}<={doc.id}
    assert c["id"] not in raw and c["source_step"] not in raw
    assert c["worked_examples"][0]["teacher_solution"] not in raw
    assert c["proof_steps"][0] not in raw
    assert response["teacher_solution_exposed"] is False
    assert response["unverified_content_exposed"] is False

def test_independent_exact_math_instances_not_universal_proofs(history):
    assert len(history["cards"])==10
    q=sp.Rational
    # Strictly finite points: no statement below claims universal proof certification.
    assert sp.log(243,3)==sp.log(9,3)+sp.log(27,3)
    x=sp.Symbol("x")
    assert sp.solve(2*x*x-5*x+2,x)==[q(1,2),2]
    assert q(1+9,2)>=sp.sqrt(1*9)
    d,r1,r2=5,3,4
    assert abs(r1-r2)<d<r1+r2
    p=2;cx,cy=2,4
    assert (cx-p)**2+cy**2==(cx+p)**2
    u,v=sp.Matrix([1,2]),sp.Matrix([3,4])
    assert u.dot(v)**2<=u.dot(u)*v.dot(v)
    assert q(1,2)+q(1,3)-q(1,6)==q(2,3)
    assert sp.Matrix([1,0]).dot(sp.Matrix([0,2]))==0
    assert sum(range(1,10,2))==5**2
    assert sp.diff((x-1)**2,x).subs(x,1)==0

def test_editorial_math_precision_and_zero_measure_intersection(history):
    """Check corrected finite examples; not a universal proof/teacher approval."""
    by_id={c["id"]:c for c in history["cards"]}
    # A real quadratic has both signs of sqrt(Delta), not two 'nonnegative' roots.
    d=sp.Integer(9)
    assert {sp.sqrt(d),-sp.sqrt(d)}=={sp.Integer(3),sp.Integer(-3)}
    assert "只能取+√Δ或−√Δ" in by_id["KB86-P02"]["proof_steps"][1]
    # p=0 collapses the focus POINT onto the directrix LINE, not point=line.
    assert sp.Integer(0)==0
    assert "焦点(0,0)位于准线x=0上" in by_id["KB86-P05"]["worked_examples"][1]["teacher_solution"]
    # Nonempty intersection need not have positive probability: uniform [0,1].
    overlap=sp.Interval(0,sp.Rational(1,2)).intersect(sp.Interval(sp.Rational(1,2),1))
    assert overlap==sp.FiniteSet(sp.Rational(1,2))
    assert overlap.measure==0
    assert "零概率样本点" in by_id["KB86-P07"]["counterexample_or_failed_premise"]
    assert "六项为首次独立覆盖" in P.MD.read_text(encoding="utf8")
