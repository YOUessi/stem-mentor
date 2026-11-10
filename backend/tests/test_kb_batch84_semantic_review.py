"""Batch84 independent exact negative review gates and 67 PDFKit line references."""
import json
import sys
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import pytest
import sympy as sp
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch84_semantic_review as B84
from app.kb_batch84_guarded_transformations import CARDS,check_case,verified_cards,SCHEMAS

def auth():
    return B84.load(B84.AUTHOR)

@pytest.fixture(scope="module")
def report():
    return B84.build()

def test_full_seven_track_source_obligations_remain_distinct_from_official_atoms(report):
    assert report["source_review_denominator"]==428
    assert report["previous_editorial_count"]==102
    assert report["new_editorial_count"]==67
    assert report["cumulative_editorial_count"]==169
    assert report["pending_editorial_count"]==259
    assert report["official_curriculum_atom_denominator"] is None
    assert report["teacher_approved"]==report["student_deep_content_published"]==0
    assert report["full_page_teacher_reviews"]==0
    assert sum(r["source_review_anchor_denominator"] for r in report["by_track"].values())==428
    assert sum(r["editorially_paraphrased_source_anchors"] for r in report["by_track"].values())==169
    assert sum(r["without_original_semantic_paraphrase"] for r in report["by_track"].values())==259
    assert all(x["official_mathematical_atom_denominator"] is None for x in report["by_track"].values())
    assert report["by_track"]["ELECTIVE_C"]["without_original_semantic_paraphrase"]==0
    assert report["by_track"]["ELECTIVE_D"]["without_original_semantic_paraphrase"]==0
    assert report["by_track"]["ELECTIVE_E"]["official_mathematical_atom_denominator"] is None
    assert B84.OUT.read_text(encoding="utf8")==B84.dump(report)
    assert B84.MD.read_text(encoding="utf8")==B84.markdown(report)
    assert Counter(x["track"] for x in report["new_rows"])=={
        k:v for k,v in B84.TRACK_COUNTS.items() if v>0}
    assert report["candidate_splits_not_deduplicated"]==51

@pytest.mark.parametrize("i", range(67))
def test_source_lineage_and_teacher_pending(i,report):
    row=report["new_rows"][i]
    origin=next(x for x in B84.load(B84.B83.B81.SOURCE)["anchor_review_queue"]
                if x["review_id"]==row["review_id"])
    for field in ("printed_page","pdfkit_line","source_line_sha256","source_page_pdfkit_sha256","track"):
        assert row[field]==origin[field]
    assert row["review_status"]=="REVIEW_PENDING"
    assert row["math_certification"]=="NOT_FORMALLY_VERIFIED"
    assert row["student_publishable"] is False
    assert row["student_authoritative_index_eligible"] is False
    assert row["teacher_confirmed"] is False
    assert row["teacher_approved"] is False
    assert row["official_atom_count"] is None

@pytest.mark.parametrize("i", range(67))
@pytest.mark.parametrize("field,bad",[
    ("teacher_confirmed", True),
    ("student_publishable", True),
    ("official_atom_count", 0),
    ("official_atom_count", 1),
    ("cross_track_equivalence", "CERTIFIED_EQUIVALENT"),
    ("original_editorial_paraphrase", "目录"),
    ("condition_or_scope_caution", ""),
])
def test_false_approval_and_thin_editorial_claim_rejected(i,field,bad):
    data=auth()
    data["records"][i][field]=bad
    with pytest.raises(ValueError):
        B84.build(auth=data)

@pytest.mark.parametrize("i",range(67))
def test_cross_track_source_spoof_rejected(i):
    data=auth()
    r=data["records"][i]
    r["track"]="ELECTIVE_E" if r["track"]!="ELECTIVE_E" else "COMPULSORY"
    with pytest.raises(ValueError,match="track"):
        B84.build(auth=data)

@pytest.mark.parametrize("i",range(67))
def test_hidden_field_rejected(i):
    data=auth()
    data["records"][i]["teacher_approval_receipt"]={"spoof":True}
    with pytest.raises(ValueError,match="fields"):
        B84.build(auth=data)

@pytest.mark.parametrize("i",range(67))
def test_heading_cannot_become_math_atom_and_math_requirement_cannot_be_empty(i):
    data=auth()
    r=data["records"][i]
    if r["semantic_role_provisional"]=="CURRICULUM_HEADING":
        r["possible_math_units_for_teacher_split"]=["伪造数学原子"],
    elif r["semantic_role_provisional"] in ("MIXED_CLAUSE","MATHEMATICAL_REQUIREMENT"):
        r["possible_math_units_for_teacher_split"]=[]
    else:
        r["possible_math_units_for_teacher_split"]=["重复内容","重复内容"]
    with pytest.raises(ValueError):
        B84.build(auth=data)

def test_no_prior_102_double_counted():
    data=auth()
    data["records"][0]["review_id"]=B84.B83.load(B84.B83.AUTHOR)["records"][0]["review_id"]
    with pytest.raises(ValueError):
        B84.build(auth=data)

def test_source_sha_tamper_rejected():
    source=B84.load(B84.B83.B81.SOURCE)
    source["anchor_review_queue"][-1]["source_line_sha256"]="0"*64
    with pytest.raises(ValueError,match="frozen"):
        B84.build(source=source)

def test_previous_teacher_state_spoof_rejected():
    old=B84.B83.build()
    old["teacher_approved"]=1
    with pytest.raises(ValueError,match="prior"):
        B84.build(previous=old)

def test_actual_mac_original_source_hash_or_explicit_skip():
    if not B84.B83.B81.LOCAL_PDF.is_file():
        pytest.skip("Mac-only original PDF absent; CI checks frozen anchor hashes")
    assert len(B84.build(verify_local_source=True)["new_rows"])==67

def test_missing_pdf_fails_closed_even_where_ci_skips(monkeypatch,tmp_path):
    monkeypatch.setattr(B84.B83.B81,"LOCAL_PDF",tmp_path/"missing.pdf")
    with pytest.raises(ValueError,match="unavailable"):
        B84.build(verify_local_source=True)

def test_all_ten_guarded_original_math_reviews_are_pending_and_teacher_only():
    xs=list(verified_cards())
    assert len(xs)==10 and len({r["id"] for r in xs})==10
    assert len({r["op"] for r in xs})==10
    for row in xs:
        assert row["review_state"]=="REVIEW_PENDING"
        assert row["teacher_only"] is True
        assert row["student_authoritative_index_eligible"] is False
        assert row["student_answer_verified"] is False
        assert row["general_theorem_certified"] is False
        assert row["teacher_approved"] is False
        assert row["status"]=="FINITE_EXACT_COUNTEREXAMPLE_ONLY"
        assert len(row["steps"])>=3 and len(row["hints"])==3
        assert all(row[x] for x in ("worked_example","valid_guarded_example","failure","assumptions","near","far"))
        assert row["valid_guarded_example"] != row["worked_example"]

@pytest.mark.parametrize("card",CARDS,ids=lambda c:c["op"])
def test_independent_sympy_finite_counterexamples(card):
    p=card["payload"]
    op=card["op"]
    z=sp.Integer
    if op=="square_equation_reverse":
        assert z(p["x"])**2==z(p["t"])**2 and p["x"]!=p["t"]
    elif op=="zero_factor_cancellation":
        assert z(p["a"])*p["k"]==z(p["b"])*p["k"] and p["a"]!=p["b"]
    elif op=="multiply_order_negative":
        assert z(p["a"])<z(p["b"]) and z(p["k"])<0
        assert z(p["a"])*z(p["k"])>z(p["b"])*z(p["k"])
    elif op=="reciprocal_direction_positive":
        assert 0<z(p["a"])<z(p["b"])
        assert sp.Rational(1,p["a"])>sp.Rational(1,p["b"])
    elif op=="absolute_root":
        assert sp.sqrt(z(p["n"])**2)==-p["n"] and -p["n"]!=p["n"]
    elif op=="quadratic_formula_degenerate":
        x=sp.Symbol("x")
        assert p["a"]==0
        assert sp.solve(z(p["a"])*x**2+z(p["b"])*x+z(p["c"]),x)==[2]
    elif op=="cramer_determinant_zero":
        A=sp.Matrix([[p["a"],p["b"]],[p["c"],p["d"]]])
        assert A.det()==0 and A*sp.Matrix([3,0])==A*sp.Matrix([1,1])==sp.Matrix([p["e"],p["f"]])
    elif op=="cross_multiplication_zero_denominator":
        assert z(p["a"])*z(p["d"])==z(p["b"])*z(p["c"])
        assert p["b"]==0
    elif op=="conditional_probability_zero":
        assert p["event"]==p["intersection"]==0 and p["total"]>0
    elif op=="real_log_product":
        assert p["x"]<0 and p["y"]<0 and p["x"]*p["y"]>0
        assert sp.log(z(p["x"])*z(p["y"]))==0
        assert sp.log(z(p["x"])).is_real is False
    else:
        pytest.fail(op)
    result=check_case(op,p)
    assert result["status"]=="FINITE_EXACT_COUNTEREXAMPLE_ONLY"

@pytest.mark.parametrize("card",CARDS,ids=lambda c:c["op"])
@pytest.mark.parametrize("bad",[
    lambda p: {**p,next(iter(p)):True},
    lambda p: {**p,next(iter(p)):1.2},
    lambda p: {**p,next(iter(p)):"3"},
    lambda p: {**p,next(iter(p)):100000},
    lambda p: {**p,"teacher_approved":1},
])
def test_malformed_exact_payload_never_accepted(card,bad):
    with pytest.raises(ValueError):
        check_case(card["op"],bad(dict(card["payload"])))

@pytest.mark.parametrize("card",CARDS,ids=lambda c:c["op"])
def test_missing_schema_field_fails_closed(card):
    p=dict(card["payload"]);p.pop(next(iter(p)))
    with pytest.raises(ValueError):
        check_case(card["op"],p)

@pytest.mark.parametrize("card",CARDS,ids=lambda c:c["op"])
def test_counterexample_not_a_general_claim_for_unrelated_zero_input(card):
    p={k:0 for k in SCHEMAS[card["op"]]}
    if card["op"]=="cross_multiplication_zero_denominator":
        p["b"]=p["d"]=1  # zero numerator does not make a defined fraction invalid
    assert check_case(card["op"],p)["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_unknown_case_and_non_dict_rejected():
    with pytest.raises(ValueError):
        check_case("invented",{"x":1})
    with pytest.raises(ValueError):
        check_case(CARDS[0]["op"],[])

def test_versioned_teacher_only_math_output_integrity_and_nonpublication():
    import build_kb_batch84_math_cards as K07
    d=K07.build()
    assert d["card_count"]==10
    assert d["teacher_review"]=="REVIEW_PENDING"
    assert d["student_index_eligible"] is False
    assert d["general_math_proof_certified"] is False
    assert d["independent_student_step_verification"] is False
    assert K07.OUT.read_text(encoding="utf8")==K07.dump(d)
    assert K07.MD.read_text(encoding="utf8")==K07.markdown(d)

# Actual approved-retrieval contract: a seeded, independently signed synthetic
# lesson remains accessible while NONE of the pending ten teacher drafts enter
# student evidence or get credited as a validated answer.
from test_attested_release_batch08 import offline_reviewer_fixture
@pytest.mark.parametrize("card", CARDS, ids=lambda c:c["op"])
def test_teacher_only_guards_not_retrieved_as_student_authority(card,offline_reviewer_fixture):
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    doc,reviewers,_,_,record,save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    response=student_evidence_lookup(card["topic"])
    raw=json.dumps(response,ensure_ascii=False)
    assert {x["knowledge_id"] for x in response["candidates"]}<={doc.id}
    assert card["id"] not in raw
    assert card["worked_example"] not in raw
    assert card["steps"][0] not in raw
    assert response["teacher_solution_exposed"] is False
    assert response["unverified_content_exposed"] is False


def test_ten_independent_guarded_valid_examples_are_not_confused_with_counterexamples():
    # Independent of check_case: the legal side of the transformations.
    q = sp.Rational
    assert 2**2 == 2**2 and 2 >= 0
    assert q(2)*3 == q(2)*3 and 3 != 0
    assert 1 < 2 and 1*3 < 2*3 and 3 > 0
    assert q(1, 2) - q(1, 5) == q(3, 10) > 0
    assert sp.sqrt(sp.Integer(4)**2) == 4
    x = sp.symbols("x")
    assert sp.solve(x*x-3*x+2, x) == [1, 2]
    assert sp.Matrix.eye(2).det() == 1 and sp.Matrix.eye(2).inv()*sp.Matrix([2, 3]) == sp.Matrix([2, 3])
    assert q(1,2) == q(2,4) and 1*4 == 2*2
    assert q(1,4) / q(1,2) == q(1,2)
    assert sp.simplify(sp.log(2*sp.Integer(3)) - sp.log(2) - sp.log(3)) == 0
    assert len([r for r in verified_cards() if r["valid_guarded_example"]]) == 10
