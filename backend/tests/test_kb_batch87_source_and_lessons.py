"""Batch87: 90 honest K00 source-line reviews and seven K02-K08 guarded teacher drafts."""
from __future__ import annotations
import json,sys
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import pytest
import sympy as sp
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch87_semantic_review as S
import build_kb_batch87_math_lessons as M
from app.kb_batch87_exact_oracles import evaluate,SUPPORTED
from test_attested_release_batch08 import offline_reviewer_fixture

@pytest.fixture(scope="module")
def source():return S.build()
@pytest.fixture(scope="module")
def lessons():return M.build()
def auth_source():return S.load(S.AUTHOR)
def auth_lessons():return M.load(M.AUTHOR)

def test_all_source_anchors_covered_but_no_official_or_teacher_promotion(source):
    assert source["schema_version"]==S.SCHEMA
    assert (source["previous_editorial_count"],source["new_editorial_count"],
            source["cumulative_editorial_count"],source["pending_editorial_count"])==(338,90,428,0)
    assert source["source_review_denominator"]==428
    assert source["official_curriculum_atom_denominator"] is None
    assert source["teacher_approved"]==source["full_page_teacher_reviews"]==0
    assert source["student_deep_content_published"]==0
    assert source["student_index_includes_unreviewed_material"] is False
    assert sum(v["source_anchor_denominator"] for v in source["by_track"].values())==428
    assert sum(v["original_editorial_coverage"] for v in source["by_track"].values())==428
    assert sum(v["source_anchors_without_editorial"] for v in source["by_track"].values())==0
    assert source["by_track"]["ELECTIVE_E"]["source_anchor_denominator"]==0
    assert {t:v["source_anchor_denominator"] for t,v in source["by_track"].items()}=={
        "COMPULSORY":142,"SELECTIVE_COMPULSORY":101,
        "ELECTIVE_A":69,"ELECTIVE_B":70,"ELECTIVE_C":29,"ELECTIVE_D":17,"ELECTIVE_E":0}
    assert source["new_provisional_math_topic_count"]==46
    assert len(source["new_provisional_math_topics_not_deduplicated"])==46
    assert S.OUT.read_text(encoding="utf8")==S.dump(source)
    assert S.MD.read_text(encoding="utf8")==S.markdown(source)

@pytest.mark.parametrize("i",range(90))
def test_each_source_row_provenance_and_teacher_status(i,source):
    r=source["new_rows"][i]
    original=next(q for q in S.load(S.B86.B85.B84.B83.B81.SOURCE)["anchor_review_queue"] if q["review_id"]==r["review_id"])
    for k in ("printed_page","pdfkit_line","source_line_sha256","source_page_pdfkit_sha256","track"):
        assert r[k]==original[k]
    assert r["review_status"]=="REVIEW_PENDING"
    assert r["math_certification"]=="NOT_FORMALLY_VERIFIED"
    assert r["teacher_approved"] is False
    assert r["student_authoritative_index_eligible"] is False
    assert r["student_publishable"] is False
    assert r["official_atom_count"] is None
    assert r["cross_track_equivalence"]=="NOT_ADJUDICATED"

@pytest.mark.parametrize("i",range(90))
@pytest.mark.parametrize("field,bad",[
    ("teacher_confirmed",True),("student_publishable",True),
    ("official_atom_count",1),("official_atom_count",0),
    ("cross_track_equivalence","CERTIFIED_EQUIVALENT"),
    ("original_editorial_paraphrase","内容"),("condition_or_scope_caution",""),
])
def test_every_source_mutation_fails_closed(i,field,bad):
    a=auth_source();a["records"][i][field]=bad
    with pytest.raises(ValueError):S.build(auth=a)

@pytest.mark.parametrize("i",range(90))
def test_every_source_misattributed_track_rejected(i):
    a=auth_source()
    x=a["records"][i]
    x["track"]="ELECTIVE_E" if x["track"]!="ELECTIVE_E" else "COMPULSORY"
    with pytest.raises(ValueError):S.build(auth=a)

@pytest.mark.parametrize("i",range(90))
def test_each_source_hidden_reviewer_field_rejected(i):
    a=auth_source();a["records"][i]["teacher_receipt"]="fake"
    with pytest.raises(ValueError):S.build(auth=a)

@pytest.mark.parametrize("i",range(90))
def test_missing_or_illegal_math_candidates_rejected(i):
    a=auth_source();r=a["records"][i]
    if r["semantic_role_provisional"]=="CURRICULUM_HEADING":
        r["possible_math_units_for_teacher_split"]=["虚构的已审核数学知识原子"]
    elif r["semantic_role_provisional"]=="MATHEMATICAL_REQUIREMENT":
        r["possible_math_units_for_teacher_split"]=[]
    else:
        r["possible_math_units_for_teacher_split"]=["重叠的数学候选","重叠的数学候选"]
    with pytest.raises(ValueError):S.build(auth=a)

def test_prior_history_source_pdf_and_queue_fingerprint_fail_closed():
    a=auth_source();a["records"][0]["review_id"]=a["records"][1]["review_id"]
    with pytest.raises(ValueError):S.build(auth=a)
    a=auth_source();a["records"][0]["review_id"]=S.B86.load(S.B86.AUTHOR)["records"][0]["review_id"]
    with pytest.raises(ValueError):S.build(auth=a)
    original=S.load(S.B86.B85.B84.B83.B81.SOURCE)
    original["anchor_review_queue"][0]["source_line_sha256"]="f"*64
    with pytest.raises(ValueError,match="frozen source"):S.build(source=original)
    previous=S.B86.build();previous["teacher_approved"]=1
    with pytest.raises(ValueError):S.build(previous=previous)
    previous=S.B86.build();previous["cumulative_editorial_count"]=428
    with pytest.raises(ValueError):S.build(previous=previous)

def test_local_pdf_verification_rejects_absent_source(monkeypatch,tmp_path):
    monkeypatch.setattr(S.B86.B85.B84.B83.B81,"LOCAL_PDF",tmp_path/"absent.pdf")
    with pytest.raises(ValueError,match="Mac local copyrighted source"):
        S.build(verify_local_source=True)

def test_seven_source_anchored_teacher_drafts_are_not_released(source,lessons):
    assert lessons["schema_version"]==M.SCHEMA
    assert lessons["lesson_count"]==7 and len(lessons["cards"])==7
    assert lessons["teacher_approvals"]==lessons["general_formal_math_certificates"]==0
    assert lessons["student_releases"]==lessons["student_free_text_step_verifications"]==0
    assert lessons["official_curriculum_atom_denominator"] is None
    assert M.OUT.read_text(encoding="utf8")==M.dump(lessons)
    assert M.MD.read_text(encoding="utf8")==M.markdown(lessons)
    assert {c["source_review_id"] for c in lessons["cards"]}<={q["review_id"] for q in source["new_rows"]}

@pytest.mark.parametrize("i",range(7))
def test_math_lemma_provenance_exact_positive_negative_and_hints(i,lessons):
    c=lessons["cards"][i]
    origin=next(q for q in S.build()["new_rows"] if q["review_id"]==c["source_review_id"])
    assert (c["source_line_sha256"],c["printed_page"],c["track"]) == (
        origin["source_line_sha256"],origin["printed_page"],origin["track"])
    assert len(c["proof_steps"])==4
    assert len(c["worked_examples"])==2
    assert len(c["hints"])==3
    assert c["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert all(ex["visibility"]=="TEACHER_ONLY" for ex in c["worked_examples"])
    assert c["teacher_approval"] is None
    assert c["review_status"]=="REVIEW_PENDING"
    assert c["official_atom_id"] is None
    assert c["prerequisite_ids_confirmed"] is False
    assert c["student_authoritative_index_eligible"] is False
    assert c["student_publishable"] is False
    assert c["general_theorem_formally_certified"] is False
    assert c["student_free_text_step_verified"] is False
    assert c["finite_evidence_scope"]=="EXACT_FINITE_FIXTURES_NOT_UNIVERSAL_THEOREM"
    valid=evaluate(c["finite_op"],c["finite_valid_fixture"])
    invalid=evaluate(c["finite_op"],c["finite_invalid_fixture"])
    assert valid["status"]=="VERIFIED_FINITE_INSTANCE"
    assert valid["exact_value"]==c["expected_exact"]
    assert invalid["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("i",range(7))
@pytest.mark.parametrize("field,bad",[
    ("source_review_id","KB80-invalid"),("definition",""),
    ("assumptions",[]),("proof_steps",[]),("worked_examples",[]),
    ("hints",["请直接给出答案"]),("boundary",""),("wrong_method",""),
    ("finite_op","UNSUPPORTED_FAKE"),("expected_exact","999"),
    ("prerequisites",[]),
])
def test_every_lesson_rejects_source_scope_evidence_or_content_erasure(i,field,bad):
    a=auth_lessons();a["cards"][i][field]=bad
    with pytest.raises(ValueError):M.build(auth=a)

@pytest.mark.parametrize("i",range(7))
def test_every_lesson_hidden_approval_field_rejected(i):
    a=auth_lessons();a["cards"][i]["teacher_signed"]=True
    with pytest.raises(ValueError):M.build(auth=a)

@pytest.mark.parametrize("k",["teacher_approvals","formal_general_theorem_certificates","student_published"])
def test_header_review_authority_false_promotion_rejected(k):
    a=auth_lessons();a[k]=1
    with pytest.raises(ValueError):M.build(auth=a)

@pytest.mark.parametrize("i",range(7))
def test_student_retrieval_on_nonempty_approved_index_keeps_teacher_answers_private(
        i,lessons,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,_,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    c=lessons["cards"][i]
    response=student_evidence_lookup(c["title"])
    raw=json.dumps(response,ensure_ascii=False)
    assert {x["knowledge_id"] for x in response["candidates"]}<={doc.id}
    assert c["id"] not in raw and c["source_review_id"] not in raw
    assert c["worked_examples"][0]["teacher_solution"] not in raw
    assert c["proof_steps"][0][1] not in raw
    assert response["teacher_solution_exposed"] is False
    assert response["unverified_content_exposed"] is False

def test_mathematical_values_independently_recomputed_with_sympy_not_a_general_certificate():
    # Seven different methods, with exact independent recomputation.
    assert F(3,6)==F(1,2)  # finite uniform count, EQUIPROBABILITY ASSUMED
    assert F(80*10+20*30,80+20)==14
    assert F(sp.binomial(3,1)*sp.binomial(5,1),sp.binomial(8,2))==F(15,28)
    x=sp.Matrix([1,2,3]);y=sp.Matrix([2,4,6])
    ux=x-sp.Matrix([2,2,2]);uy=y-sp.Matrix([4,4,4])
    assert ux.dot(uy)/sp.sqrt(ux.dot(ux)*uy.dot(uy))==1
    X=sp.Matrix([[1,0,0],[1,1,0],[1,0,1],[1,1,1]])
    z=sp.Matrix([1,3,4,6])
    assert list((X.T*X).inv()*X.T*z)==[1,2,3]
    assert sp.diff(10*sp.Symbol("t")-sp.Symbol("t")**2,sp.Symbol("t")).subs("t",3)/2==2
    chi=sum((sp.Rational(o)-e)**2/e for o,e in
            zip([12,8,6,14],[sp.Rational(9),sp.Rational(11),sp.Rational(9),sp.Rational(11)]))
    assert chi==sp.Rational(40,11)
    # General theorem validity, independent teacher sign-off and student free-text verifications remain ZERO.
def test_all_seven_invalid_scope_examples_return_unverified(lessons):
    for c in lessons["cards"]:
        result=evaluate(c["finite_op"],c["finite_invalid_fixture"])
        assert result["status"]=="CONDITIONS_NOT_ESTABLISHED"
        assert result["teacher_approved"] is False
        assert result["general_theorem_certified"] is False
        assert result["student_free_text_verified"] is False


def test_full_project_level_provisional_census_does_not_invent_official_denominator():
    import build_kb_batch87_candidate_census as C
    x=C.build()
    assert (x["source_review_anchors"],x["source_editorials_completed"],
            x["source_editorials_missing"])==(428,428,0)
    assert x["provisional_topic_label_occurrences"]==300
    assert x["exact_string_distinct_label_count"]==300
    assert x["semantic_equivalence_adjudicated_count"]==0
    assert x["official_curriculum_atom_denominator"] is None
    assert x["total_full_page_teacher_atomizations"]==0
    assert x["teacher_approved_complete_lessons"]==0
    assert x["student_published_deep_lessons"]==0
    assert x["not_an_official_atom_count"] is True
    assert len(x["provisional_candidates"])==300
    assert len({r["candidate_id"] for r in x["provisional_candidates"]})==300
    assert [x["by_track"][k]["provisional_label_occurrences"] for k in (
        "COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
        "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")]==[75,66,60,60,31,8,0]
    assert x["new_source_linked_teacher_drafts"]==7
    assert C.OUT.read_text(encoding="utf8")==C.dump(x)
    assert C.MD.read_text(encoding="utf8")==C.markdown(x)

def test_candidate_census_rejects_hidden_teacher_approval_missing_lines_and_duplicate_math_label():
    import build_kb_batch87_candidate_census as C
    x=S.build()
    a=deepcopy(x);a["official_curriculum_atom_denominator"]=300
    with pytest.raises(ValueError):C.build(editorial=a)
    lessons=M.build();lessons["teacher_approvals"]=1
    with pytest.raises(ValueError):C.build(teacher=lessons)
    b=S.B86
    rows=b.B85.B84.B83.B81.build()["rows"]+[
        r for module in (b.B85.B84.B83,b.B85.B84,b.B85,b,S)
        for r in module.build()["new_rows"]]
    with pytest.raises(ValueError):C.build(allrows=rows[:-1])
    a=deepcopy(rows)
    a[-1]["source_line_sha256"]="0"*64
    with pytest.raises(ValueError):C.build(allrows=a)
    a=deepcopy(rows)
    # Two identically labelled draft topics do not constitute two independent atoms.
    first=next(r for r in a if r["possible_math_units_for_teacher_split"])
    second=next(r for r in a if r is not first and r["track"]==first["track"] and r["possible_math_units_for_teacher_split"])
    second["possible_math_units_for_teacher_split"][0]=first["possible_math_units_for_teacher_split"][0]
    with pytest.raises(ValueError,match="provisional math labels drift"):C.build(allrows=a)

def test_finite_oracles_fail_closed_when_outside_supported_scopes():
    assert evaluate("unknown",{})["status"]=="UNSUPPORTED"
    assert evaluate("classical_uniform",{"n":6,"event":[1,3],"uniform_certified":False})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert evaluate("classical_uniform",{"n":6,"event":[1,1],"uniform_certified":True})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert evaluate("classical_uniform",{"n":6,"event":[1,3],"uniform_certified":"yes"})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert evaluate("weighted_strata",{"population_counts":[0,10],"stratum_means":[4,6]})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert evaluate("hypergeometric",{"N":5,"K":6,"n":2,"k":1})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert evaluate("pearson",{"x":[1,1,1],"y":[2,3,4]})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert evaluate("bivariate_ols",{"rows":[[1,1,1],[1,2,2],[1,3,3]],"y":[2,3,4]})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert evaluate("projectile_slope",{"vx":"0","vertical_initial_velocity":10,"gravity":2,"t":3})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert evaluate("contingency_2x2",{"table":[[0,0],[4,6]]})["status"]=="CONDITIONS_NOT_ESTABLISHED"
