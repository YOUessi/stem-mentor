"""Independent positive and rejected input tests for real logarithms."""
from fractions import Fraction
from math import inf, nan
import pytest
from app.kb_math_real_log_domain import valid_real_log_domain
from app.kb_batch92_exact_witness import verify
from app.kb_batch93_finite_oracles import finite_check


@pytest.mark.parametrize("base,argument,change_base", [
    (2, 8, None), (Fraction(1,2), Fraction(1,4), None),
    (2, 8, 10), (2, 8, Fraction(1,2)), (4, 1, 2),
])
def test_valid_real_log_inputs(base,argument,change_base):
    assert valid_real_log_domain(base,argument,change_base=change_base)


@pytest.mark.parametrize("base,argument,change_base", [
    (1, 8, None), (0, 8, None), (-2, 8, None),
    (2, 0, None), (2, -8, None), (2, 8, 1),
    (2, 8, 0), (2, 8, -1), (2, 8, inf),
    (inf, 8, None), (nan, 8, None), (2, nan, None),
    (True, 8, None), (2, False, None), (2+1j, 8, None),
])
def test_invalid_real_log_inputs_are_rejected(base,argument,change_base):
    assert not valid_real_log_domain(base,argument,change_base=change_base)


def test_batch92_log_witness_rechecks_domain():
    assert verify(7)["status"] == "VERIFIED_FINITE_INSTANCE_WITH_BOUNDARY_REJECTION"


def test_batch93_log_witness_rechecks_domain():
    assert finite_check("KB80-A020-L032-C01")["premise_or_boundary_rejection"] is True
