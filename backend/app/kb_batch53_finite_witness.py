"""K07 Batch53: exact finite witnesses for cross-page syllabus condition risks.

These functions verify narrowly specified arithmetic examples. Their success
does not certify syllabus wording, a theorem, or a student's free-form proof.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Sequence


class PreconditionsNotEstablished(ValueError):
    """The requested computation requires a missing mathematical assumption."""


def _fraction(value: object) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise PreconditionsNotEstablished("only exact integral/rational inputs supported")
    return Fraction(value)


def _weights(values: Sequence[int | Fraction]) -> tuple[Fraction, ...]:
    if not isinstance(values, (tuple, list)) or not 1 <= len(values) <= 256:
        raise PreconditionsNotEstablished("finite nonempty bounded outcome space required")
    weights = tuple(_fraction(v) for v in values)
    if any(w < 0 for w in weights) or sum(weights) <= 0:
        raise PreconditionsNotEstablished("negative masses or zero total probability")
    return weights


def event_probability(
    weights: Sequence[int | Fraction],
    event: Iterable[int],
    *, classical_model: bool = False
) -> Fraction:
    """Exact P(A) in a finite weighted outcome model.

    classical_model=True adds an explicit equal-positive-mass requirement.
    Distinct outcomes are identified by integer indices; event duplicates are
    invalid rather than silently double-counted.
    """
    weights = _weights(weights)
    try:
        indices = tuple(event)
    except TypeError as e:
        raise PreconditionsNotEstablished("event must enumerate indices") from e
    if any(isinstance(i, bool) or not isinstance(i, int) for i in indices):
        raise PreconditionsNotEstablished("non-integer event index")
    if len(set(indices)) != len(indices) or any(i < 0 or i >= len(weights) for i in indices):
        raise PreconditionsNotEstablished("duplicate/out-of-range event index")
    if classical_model and (any(w == 0 for w in weights) or len(set(weights)) != 1):
        raise PreconditionsNotEstablished("finite does not imply equiprobable")
    return sum((weights[i] for i in indices), Fraction(0)) / sum(weights)


def conditional_probability(
    weights: Sequence[int | Fraction],
    event: Iterable[int],
    condition: Iterable[int]
) -> Fraction:
    """Exact finite P(A|B) only when P(B) > 0."""
    weights = _weights(weights)
    ea, eb = tuple(event), tuple(condition)
    event_probability(weights, ea)
    event_probability(weights, eb)
    denom = sum(weights[i] for i in eb)
    if denom == 0:
        raise PreconditionsNotEstablished("conditioning on zero-probability event")
    return sum((weights[i] for i in set(ea).intersection(eb)), Fraction(0)) / denom


def sequence_term_from_partial_sums(
    partial_sums: Sequence[int | Fraction], n: int
) -> Fraction:
    """With convention S_n=sum(a_1..a_n), a_1=S_1, a_n=S_n-S_{n-1} for n>=2."""
    if not isinstance(partial_sums, (tuple, list)) or not partial_sums:
        raise PreconditionsNotEstablished("nonempty finite partial-sum values required")
    if isinstance(n, bool) or not isinstance(n, int) or n < 1 or n > len(partial_sums):
        raise PreconditionsNotEstablished("n must be a positive available sequence index")
    sums = tuple(_fraction(v) for v in partial_sums)
    return sums[n-1] if n == 1 else sums[n-1]-sums[n-2]


def polynomial_derivative_at(
    coefficients: Sequence[int | Fraction], x: int | Fraction
) -> Fraction:
    """At a rational x, exact derivative of sum(c_k*x**k) (not arbitrary f)."""
    if not isinstance(coefficients, (tuple, list)) or not 1 <= len(coefficients) <= 32:
        raise PreconditionsNotEstablished("bounded polynomial coefficients required")
    x = _fraction(x)
    c = tuple(_fraction(a) for a in coefficients)
    return sum((k*c[k]*x**(k-1) for k in range(1,len(c))),Fraction(0))


def derivative_affine_power_at(
    a: int | Fraction, b: int | Fraction, n: int, x: int | Fraction
) -> Fraction:
    """Exact derivative for f(x)=(a*x+b)^n, n>=1, including inner derivative a."""
    a,b,x = _fraction(a),_fraction(b),_fraction(x)
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 24:
        raise PreconditionsNotEstablished("positive integer exponent 1..24 required")
    return n*(a*x+b)**(n-1)*a


def audit_frame_completeness(
    population: Sequence[str], observed: Sequence[str]
) -> str:
    """Matching sample count is insufficient: require unique, identical unit IDs."""
    if any(not isinstance(i,str) or not i for i in (*population,*observed)):
        raise PreconditionsNotEstablished("valid named units required")
    if len(population) == 0 or len(population) > 10000:
        raise PreconditionsNotEstablished("nonempty bounded population required")
    if len(set(population)) != len(population):
        raise PreconditionsNotEstablished("population itself contains duplicate identities")
    if len(observed) != len(population):
        return "COUNT_DIFFERENT_NOT_COMPLETE"
    if len(set(observed)) != len(observed):
        return "COUNT_EQUAL_WITH_DUPLICATES_NOT_COMPLETE"
    if set(population) != set(observed):
        return "COUNT_EQUAL_WRONG_MEMBERS_NOT_COMPLETE"
    return "FRAME_IDENTITIES_EXACTLY_MATCH"


def effective_compound_rate(
    nominal_annual_rate: int | Fraction, periods_per_year: int
) -> Fraction:
    """Finite annual effective interest rate with stated compounding frequency.

    This is a conditional financial model, not a claim about a real contract.
    """
    rate = _fraction(nominal_annual_rate)
    if rate < 0:
        raise PreconditionsNotEstablished("this teaching model requires nonnegative nominal rate")
    if (isinstance(periods_per_year,bool) or not isinstance(periods_per_year,int)
            or not 1 <= periods_per_year <= 365):
        raise PreconditionsNotEstablished("bounded positive integral compounding periods")
    return (1+rate/periods_per_year)**periods_per_year-1
