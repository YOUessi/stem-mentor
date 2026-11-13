"""Bounded exact arithmetic and domain-precondition regression (not theorem certification)."""
import pytest
from app.kb_batch90_exact_witness import CASES, SUPPORTED, check_all, evaluate

def test_finite_case_coverage_never_promotes_teacher_or_general_proof():
    result=check_all()
    assert len(result)==16
    assert all(key.startswith("KB90-REL-") for key in result)
    for row in result.values():
        assert row["student_authoritative_index_eligible"] is False
        assert row["teacher_approved"] is False
        assert row["good"]["general_theorem_formally_certified"] is False
        assert row["invalid"]["student_free_text_verified"] is False

@pytest.mark.parametrize("relation,operation,good,bad,expected", CASES)
def test_each_finite_math_witness_matches_frozen_exact_answer(
        relation,operation,good,bad,expected):
    response=evaluate(operation,good)
    assert response["status"]=="VERIFIED_FINITE_INSTANCE", (relation,response)
    assert response["exact_value"]==expected
    assert response["teacher_approved"] is False

@pytest.mark.parametrize("relation,operation,good,bad,expected", CASES)
def test_each_invalid_domain_is_rejected(
        relation,operation,good,bad,expected):
    response=evaluate(operation,bad)
    assert response["status"]=="CONDITIONS_NOT_ESTABLISHED", (relation,response)
    assert response["general_theorem_formally_certified"] is False

def test_unsupported_operator_cannot_claim_verification():
    with pytest.raises(ValueError,match="unsupported"):
        evaluate("arbitrary_user_expression",{"expression":"2+2"})

def test_noninteger_and_negative_principal_deny_unsafe_shortcuts():
    assert evaluate("quadratic_sign",{"a":True,"b":0,"c":0,"xs":[0,1]})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert evaluate("compound_growth",{"principal":-10,"ratio":[2,1],"periods":3})["status"]=="CONDITIONS_NOT_ESTABLISHED"

def test_no_string_eval_or_free_text_verification_escape():
    v=evaluate("least_squares",{"xs":[1,"__import__('os').system('echo unsafe')"],"ys":[2,4]})
    assert v["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert v["student_free_text_verified"] is False
