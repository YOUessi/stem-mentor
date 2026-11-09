"""Batch66: finite exact *witnesses* for independently authored teacher assessment drafts.

A witness checks one deliberately frozen exercise; it never certifies a universal
theorem, a syllabus clause, a free-form student proof, or teacher approval.
"""
from fractions import Fraction as F

from app.kb_batch65_finite_witnesses import (
    complex_quotient, vector_basis_coefficients, line_intersection_3d,
    equiprobable_event_probability,
)


class UnsafePremise(ValueError):
    pass


def exact(x):
    if type(x) is int or type(x) is F:
        return F(x)
    raise UnsafePremise("exact integer/Fraction required; floats and booleans are forbidden")


def composed_reciprocal(x):
    x = exact(x)
    if x == 1:
        raise UnsafePremise("f(g(x)) undefined: g(x)=2 at x=1")
    return F(1, 1) / (x - 1)


def finite_implication(values, antecedent, consequent):
    if not isinstance(values, (tuple, list)) or not 0 < len(values) <= 64:
        raise UnsafePremise("finite nonempty domain required")
    vals = [exact(x) for x in values]
    p = [antecedent(x) for x in vals]
    q = [consequent(x) for x in vals]
    if any(type(x) is not bool for x in p + q):
        raise UnsafePremise("predicates must return booleans")
    return all((not a) or b for a, b in zip(p, q))


def weighted_probability(outcomes, weights, event):
    if not outcomes or len(outcomes) != len(weights) or len(set(outcomes)) != len(outcomes):
        raise UnsafePremise("finite distinct sample space required")
    ww = [exact(w) for w in weights]
    if any(w < 0 for w in ww) or sum(ww) != 1:
        raise UnsafePremise("weights must be nonnegative and sum to 1")
    if not set(event) <= set(outcomes):
        raise UnsafePremise("event outside sample space")
    return sum((w for outcome, w in zip(outcomes, ww) if outcome in event), F(0))


def residuals(xs, ys, slope, intercept):
    if not xs or len(xs) != len(ys):
        raise UnsafePremise("matched nonempty samples required")
    m, b = exact(slope), exact(intercept)
    return [exact(y) - (m * exact(x) + b) for x, y in zip(xs, ys)]


def finite_mean(values):
    if not values:
        raise UnsafePremise("cannot compute empty-sample mean")
    return sum((exact(x) for x in values), F(0)) / len(values)


def witnesses():
    A = {1, 2}
    D = (-1, 0, 1)
    implication = finite_implication((0, 1, 3), lambda x: x > 2, lambda x: x > 0)
    converse = finite_implication((0, 1, 3), lambda x: x > 0, lambda x: x > 2)
    # Keys deliberately correspond to the 14 independent assessment types.
    return {
        "SET_TYPES": {"member": 2 in A, "subset": {2} <= A, "type_mismatch": type(2) is int},
        "IMPLICATION": {"forward": implication, "converse": converse, "counterexample": 1},
        "QUANTIFIER": {"all_nonnegative_squares": all(x*x >= 0 for x in D),
                       "all_idempotent": all(x*x == x for x in D), "counterexample": -1},
        "INEQUALITY": {"left": str(exact(1)*exact(-2)), "right": str(exact(3)*exact(-2)),
                       "reversed": exact(-2) > exact(-6)},
        "COMPOSITION": {"x2": str(composed_reciprocal(2)), "excluded_x": 1},
        "LOG_ORDER": {"small_argument": str(F(1,2)**2), "large_argument": str(F(1,2)),
                      "log_small": 2, "log_large": 1},
        "TRIG_IDENTITY": {"sum_squares": str(F(3,5)**2+F(4,5)**2),
                          "tangent": str(F(4,5)/F(3,5))},
        "COMPLEX_QUOTIENT": {"real_imag": list(complex_quotient(1,1,1,-1))},
        "VECTOR_BASIS": {"coefficients": list(vector_basis_coefficients((1,0),(0,1),(2,-3))[:2])},
        "SKEW_LINES": {"intersection": line_intersection_3d((0,0,0),(1,0,0),(0,0,1),(0,1,0))},
        "CLASSICAL_PROB": {"event_probability": str(equiprobable_event_probability(
                              (1,2,3,4,5,6),True,(2,4,6))),
                           "nonuniform_counterexample": str(weighted_probability((1,2,3),
                              (F(1,2),F(1,3),F(1,6)),(2,3)))},
        "MODEL_UNITS": {"fare_3_km": str(exact(10)+exact(2)*exact(3)), "unit": "CNY"},
        "MODEL_RESIDUAL": {"residuals": [str(x) for x in residuals((0,1,2),(1,3,6),2,1)]},
        "SAMPLE_MEAN": {"original": str(finite_mean((1,2,3,4))),
                        "outlier": str(finite_mean((1,2,3,100)))},
    }


# Human-checked expected outcomes are an independent, immutable golden-test source.
GOLDEN = {
    "SET_TYPES": {"member":True,"subset":True,"type_mismatch":True},
    "IMPLICATION": {"forward":True,"converse":False,"counterexample":1},
    "QUANTIFIER": {"all_nonnegative_squares":True,"all_idempotent":False,"counterexample":-1},
    "INEQUALITY": {"left":"-2","right":"-6","reversed":True},
    "COMPOSITION": {"x2":"1","excluded_x":1},
    "LOG_ORDER": {"small_argument":"1/4","large_argument":"1/2","log_small":2,"log_large":1},
    "TRIG_IDENTITY": {"sum_squares":"1","tangent":"4/3"},
    "COMPLEX_QUOTIENT": {"real_imag":[0,1]},
    "VECTOR_BASIS": {"coefficients":[2,-3]},
    "SKEW_LINES": {"intersection":None},
    "CLASSICAL_PROB": {"event_probability":"1/2","nonuniform_counterexample":"1/2"},
    "MODEL_UNITS": {"fare_3_km":"16","unit":"CNY"},
    "MODEL_RESIDUAL": {"residuals":["0","0","1"]},
    "SAMPLE_MEAN": {"original":"5/2","outlier":"53/2"},
}


def verify_finite_cases():
    observed = witnesses()
    if observed != GOLDEN:
        raise AssertionError("finite golden witness mismatch")
    return observed
