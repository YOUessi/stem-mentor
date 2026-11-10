"""Batch79: exact, bounded, independent witnesses for 12 guarded historical claims.

Each successful return establishes a *finite instance only*. Neither symbolic
identity checks nor exhaustive small domains certify a teacher's full theorem.
No eval/sympify on user-controlled strings, no unbounded combinatorics.
"""
from fractions import Fraction as Q
from itertools import combinations
from math import isqrt

OPS = (
    "amgm", "cauchy2", "geometric_sum", "composition", "bayes",
    "bisection", "parabola", "arithmetic_sum", "circle_square",
    "ols", "variance_affine", "cosine_law",
)
KEYS = {
    "amgm": {"a", "b"},
    "cauchy2": {"a", "b"},
    "geometric_sum": {"a", "q", "n"},
    "composition": {"x"},
    "bayes": {"N", "A", "B"},
    "bisection": {"a", "b", "c"},
    "parabola": {"p", "x", "y"},
    "arithmetic_sum": {"a", "d", "n"},
    "circle_square": {"D", "E", "F"},
    "ols": {"xs", "ys"},
    "variance_affine": {"xs", "a", "b"},
    "cosine_law": {"a", "b", "c"},
}
GOOD = {
    "amgm": {"a": 2, "b": 8},
    "cauchy2": {"a": [1, 2], "b": [3, 4]},
    "geometric_sum": {"a": 3, "q": 2, "n": 4},
    "composition": {"x": 3},
    "bayes": {"N": 6, "A": [1, 2, 3], "B": [1, 2, 3, 4]},
    "bisection": {"a": 1, "b": 2, "c": 2},
    "parabola": {"p": 2, "x": 2, "y": 4},
    "arithmetic_sum": {"a": 2, "d": 3, "n": 5},
    "circle_square": {"D": -2, "E": -4, "F": -4},
    "ols": {"xs": [0, 1, 2], "ys": [1, 3, 5]},
    "variance_affine": {"xs": [1, 3, 5], "a": 2, "b": 7},
    "cosine_law": {"a": 3, "b": 4, "c": 5},
}
BAD = {
    "amgm": {"a": -2, "b": 8},
    "cauchy2": {"a": [1, 2], "b": [3, 4, 5]},
    "geometric_sum": {"a": 3, "q": 1, "n": 4},
    "composition": {"x": 2},
    "bayes": {"N": 6, "A": [1, 2, 3], "B": []},
    "bisection": {"a": 2, "b": 3, "c": 2},
    "parabola": {"p": 0, "x": 0, "y": 0},
    "arithmetic_sum": {"a": 2, "d": 3, "n": 0},
    "circle_square": {"D": 2, "E": 0, "F": 4},
    "ols": {"xs": [1, 1, 1], "ys": [1, 3, 5]},
    "variance_affine": {"xs": [], "a": 2, "b": 7},
    "cosine_law": {"a": 1, "b": 1, "c": 3},
}
assert set(OPS) == set(GOOD) == set(BAD) == set(KEYS)

def _guard_value(value):
    if type(value) is int:
        if abs(value) > 256:
            raise ValueError("Integer exceeds bounded finite witness limits")
    elif type(value) is list:
        if len(value) > 32:
            raise ValueError("List exceeds bounded finite witness limits")
        for item in value:
            _guard_value(item)
    else:
        raise ValueError("Only exact integers and bounded lists; no bool, float or strings")

def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def _mean(xs):
    return Q(sum(xs), len(xs))

def check(op, arguments):
    """Return (VERIFIED_FINITE_INSTANCE|CONDITIONS_NOT_ESTABLISHED, evidence)."""
    if op not in OPS or type(arguments) is not dict or set(arguments) != KEYS[op]:
        raise ValueError("Unknown operator or wrong exact input schema")
    for value in arguments.values():
        _guard_value(value)
    a = arguments
    def fail(reason):
        return "CONDITIONS_NOT_ESTABLISHED", {"failed_condition": reason}
    proof = {}
    if op == "amgm":
        x, y = a["a"], a["b"]
        if x <= 0 or y <= 0:
            return fail("two_strictly_positive_real_inputs")
        difference = (x + y)**2 - 4*x*y
        assert difference == (x-y)**2 and difference >= 0
        proof = {"square_gap": difference, "inequality": "sum_ge_twice_geometric_mean"}
    elif op == "cauchy2":
        u, v = a["a"], a["b"]
        if len(u) != 2 or len(v) != 2:
            return fail("both_vectors_in_same_two_dimensional_space")
        lhs = _dot(u,u)*_dot(v,v)-_dot(u,v)**2
        assert lhs == (u[0]*v[1]-u[1]*v[0])**2 and lhs >= 0
        proof = {"lagrange_identity_gap": lhs}
    elif op == "geometric_sum":
        first, q, n = a["a"], a["q"], a["n"]
        if q == 1 or not 1 <= n <= 16:
            return fail("q_not_one_and_n_positive_bounded_integer")
        series = sum(first * q**k for k in range(n))
        assert series * (1-q) == first * (1-q**n)
        proof = {"sum": series, "cross_multiplication_identity": True}
    elif op == "composition":
        x = a["x"]
        if x == 2:
            return fail("inner_output_in_reciprocal_outer_domain")
        proof = {"g_x": x-2, "f_of_g": str(Q(1,x-2))}
    elif op == "bayes":
        N, A, B = a["N"], a["A"], a["B"]
        if not 1 <= N <= 32 or len(A) != len(set(A)) or len(B) != len(set(B)):
            return fail("uniform_finite_nonduplicated_events")
        if any(not 1 <= z <= N for z in A+B) or not B or not A:
            return fail("both_conditioning_events_in_domain_and_nonempty")
        a0, b0 = set(A), set(B)
        value = Q(len(a0 & b0), len(b0))
        rhs = Q(len(a0 & b0),len(a0))*Q(len(a0),N)/Q(len(b0),N)
        assert value == rhs
        proof = {"bayes_probability": str(value), "direct_enumeration": str(rhs)}
    elif op == "bisection":
        lo, hi, c = a["a"], a["b"], a["c"]
        if lo >= hi or c <= 0 or (lo*lo-c)*(hi*hi-c) >= 0:
            return fail("continuous_polynomial_and_strict_opposite_endpoint_signs")
        mid = Q(lo+hi,2)
        proof = {"f_left": lo*lo-c, "f_right": hi*hi-c,
                 "midpoint": str(mid), "f_midpoint": str(mid*mid-c)}
    elif op == "parabola":
        p, x, y = a["p"],a["x"],a["y"]
        if p <= 0 or y*y != 4*p*x:
            return fail("positive_parameter_and_point_on_parabola")
        assert (x-p)**2+y*y == (x+p)**2
        proof = {"squared_distance_to_focus_and_directrix": (x+p)**2}
    elif op == "arithmetic_sum":
        first,d,n=a["a"],a["d"],a["n"]
        if not 1 <= n <= 32:
            return fail("positive_integer_number_of_terms")
        total=sum(first+d*k for k in range(n))
        assert 2*total == n*(2*first+(n-1)*d)
        proof = {"sum": total, "paired_terms_identity": True}
    elif op == "circle_square":
        D,E,F=a["D"],a["E"],a["F"]
        r2=Q(D*D+E*E,4)-F
        if r2 <= 0:
            return fail("strictly_positive_squared_radius")
        proof = {"center": [str(Q(-D,2)),str(Q(-E,2))], "radius_squared": str(r2)}
    elif op == "ols":
        xs,ys=a["xs"],a["ys"]
        if not 2<=len(xs)==len(ys)<=32:
            return fail("same_number_at_least_two_observations")
        xbar,ybar=_mean(xs),_mean(ys)
        denom=sum((x-xbar)**2 for x in xs)
        if denom==0:
            return fail("positive_regressor_centered_sum_of_squares")
        slope=sum((x-xbar)*(y-ybar) for x,y in zip(xs,ys))/denom
        intercept=ybar-slope*xbar
        residual=[Q(y)-intercept-slope*x for x,y in zip(xs,ys)]
        assert sum(residual)==0 and sum(x*r for x,r in zip(xs,residual))==0
        proof = {"slope": str(slope), "intercept": str(intercept), "normal_equations": True}
    elif op == "variance_affine":
        xs,scale,shift=a["xs"],a["a"],a["b"]
        if len(xs)<2:
            return fail("at_least_two_observations_for_declared_empirical_variance")
        mu=_mean(xs)
        left=[scale*x+shift for x in xs]
        mu2=_mean(left)
        variance=sum((x-mu)**2 for x in xs)/len(xs)
        transformed=sum((x-mu2)**2 for x in left)/len(left)
        assert transformed==scale*scale*variance
        proof={"population_variance": str(variance), "transformed_variance": str(transformed)}
    elif op == "cosine_law":
        x,y,z=a["a"],a["b"],a["c"]
        if not (x>0 and y>0 and z>0 and x+y>z and x+z>y and y+z>x):
            return fail("positive_nondegenerate_triangle_side_lengths")
        cosine=Q(x*x+y*y-z*z,2*x*y)
        assert -1<cosine<1
        proof={"cosine_of_included_angle":str(cosine)}
    assert proof
    return "VERIFIED_FINITE_INSTANCE",proof
