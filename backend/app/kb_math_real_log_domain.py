"""Strict real-logarithm domain predicate; no numerical proof claims.

For log_base(argument) over reals, base>0, base!=1, argument>0.
For a change-of-base expression, the replacement base must also be valid.
This predicate is for concrete real numbers, NOT a solver for symbolic assumptions.
"""
from __future__ import annotations
from math import isfinite
from numbers import Real


def valid_real_log_domain(base: Real, argument: Real, *, change_base: Real | None = None) -> bool:
    def is_legal_real(value: object) -> bool:
        return isinstance(value, Real) and not isinstance(value, bool) and isfinite(value)

    if not (is_legal_real(base) and is_legal_real(argument)):
        return False
    if not (base > 0 and base != 1 and argument > 0):
        return False
    if change_base is not None:
        if not is_legal_real(change_base) or change_base <= 0 or change_base == 1:
            return False
    return True
