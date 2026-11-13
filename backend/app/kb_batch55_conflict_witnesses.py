"""Independent bounded exact counterexamples for ten unresolved math-content conflicts.

Never a general proof, student-answer verifier, semantic equivalence decision,
teacher approval, or authorization to publish unreviewed content.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb, isqrt


class ConditionsNotEstablished(ValueError):
    """The caller has not established this particular oracle's mathematical premises."""


OPS = {
    "math.hs.function.composition-domain": {"x", "shift"},
    "math.hs.function.parity": {"coefficients", "domain"},
    "math.hs.function.piecewise": {"left_inclusive", "right_inclusive", "left_value", "right_value"},
    "math.hs.function.zero-ivt": {"coefficients", "left", "right"},
    "math.hs.geometry.point-line-distance": {"A", "B", "C", "x", "y"},
    "math.hs.probability.binomial-distribution": {"n", "k", "p", "independent_identical"},
    "math.hs.probability.hypergeometric": {"N", "K", "n", "k", "equal_likelihood_without_replacement"},
    "math.hs.statistics.correlation-regression": {"xs", "ys"},
    "math.hs.triangle.area-sine": {"a", "b", "cos_included_angle", "is_included_angle"},
    "math.hs.vector.linear-operations": {"u", "v"},
}


def _r(value: object) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ConditionsNotEstablished("Exact int/Fraction only, no float/bool/str")
    f = Fraction(value)
    if abs(f.numerator) > 1_000_000 or f.denominator > 1_000_000:
        raise ConditionsNotEstablished("Unbounded rational operand")
    return f


def _i(value: object, lo: int, hi: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
        raise ConditionsNotEstablished("Integer parameter outside supported range")
    return value


def _seq(value: object, lo: int, hi: int) -> tuple[Fraction, ...]:
    if not isinstance(value, (list, tuple)) or not lo <= len(value) <= hi:
        raise ConditionsNotEstablished("Unsupported exact sequence length")
    return tuple(_r(z) for z in value)


def _poly(cs: tuple[Fraction, ...], x: Fraction) -> Fraction:
    return sum((c * x**i for i, c in enumerate(cs)), Fraction(0))


def checked_conflict_witness(conflict_id: str, **fields: object) -> dict:
    """Return **only** a bounded independently calculated mathematical case.

    Unknown/missing/extra fields fail closed; the output never resolves the
    conflicting authored versions or certifies their unrestricted proofs.
    """
    if conflict_id not in OPS or set(fields) != OPS[conflict_id]:
        raise ConditionsNotEstablished("Unknown conflict ID or invalid field schema")
    out: dict = {
        "status": "FINITE_EXACT_CASE_ONLY",
        "conflict_decision": "OPEN_REQUIRES_HUMAN_MATHEMATICAL_REVIEW",
        "universal_proof_certified": False,
        "student_solution_verified": False,
        "teacher_approved": False,
    }
    if conflict_id == "math.hs.function.composition-domain":
        x, shift = _r(fields["x"]), _r(fields["shift"])
        inner = x + shift
        if inner == 0:
            raise ConditionsNotEstablished("f(t)=1/t requires g(x) != 0")
        out.update(inner=inner, composition=1 / inner, reverse_composition="NOT_CLAIMED")
    elif conflict_id == "math.hs.function.parity":
        if fields["domain"] != "ALL_REAL":
            raise ConditionsNotEstablished("Polynomial parity classification here requires full real domain")
        cs = _seq(fields["coefficients"], 1, 4)
        cs = cs + (Fraction(0),) * (4 - len(cs))
        out.update(is_even=(cs[1] == 0 and cs[3] == 0),
                   is_odd=(cs[0] == 0 and cs[2] == 0),
                   zero_polynomial=all(c == 0 for c in cs),
                   classification_scope="DEGREE_AT_MOST_THREE_POLYNOMIAL_ON_REAL_LINE")
    elif conflict_id == "math.hs.function.piecewise":
        l, r = fields["left_inclusive"], fields["right_inclusive"]
        if not isinstance(l, bool) or not isinstance(r, bool):
            raise ConditionsNotEstablished("Branch inclusion flags must be booleans")
        a, b = _r(fields["left_value"]), _r(fields["right_value"])
        out.update(boundary_defined=l or r, overlap=l and r,
                   boundary_value=a if l and not r else b if r and not l else a if l and a == b else None,
                   ambiguous_if_different=(l and r and a != b),
                   gap=(not l and not r))
    elif conflict_id == "math.hs.function.zero-ivt":
        cs = _seq(fields["coefficients"], 1, 5)
        l, r = _r(fields["left"]), _r(fields["right"])
        if l >= r:
            raise ConditionsNotEstablished("Closed interval needs a < b")
        fl, fr = _poly(cs, l), _poly(cs, r)
        out.update(left_value=fl, right_value=fr,
                   existence_guaranteed_by_bracket=fl * fr <= 0,
                   uniqueness="UNDETERMINED",
                   same_sign_does_not_imply_no_roots=True,
                   continuity="POLYNOMIAL_ON_REAL_LINE")
    elif conflict_id == "math.hs.geometry.point-line-distance":
        a, b, c, x, y = [_r(fields[k]) for k in ("A", "B", "C", "x", "y")]
        if a == b == 0:
            raise ConditionsNotEstablished("A=B=0 cannot define a line")
        sq = (a*x + b*y + c)**2 / (a*a + b*b)
        n, d = isqrt(sq.numerator), isqrt(sq.denominator)
        out.update(squared_distance=sq,
                   exact_distance=Fraction(n, d) if n*n == sq.numerator and d*d == sq.denominator else None,
                   irrational_distance="NOT_REPRESENTABLE_AS_FRACTION" if n*n != sq.numerator or d*d != sq.denominator else None)
    elif conflict_id == "math.hs.probability.binomial-distribution":
        n = _i(fields["n"], 0, 24)
        k = _i(fields["k"], 0, n)
        p = _r(fields["p"])
        if not 0 <= p <= 1 or fields["independent_identical"] is not True:
            raise ConditionsNotEstablished("i.i.d. Bernoulli with p in [0,1] required")
        out.update(probability=comb(n, k)*p**k*(1-p)**(n-k),
                   model="BINOMIAL_ONLY_UNDER_EXPLICIT_IID_ASSUMPTION")
    elif conflict_id == "math.hs.probability.hypergeometric":
        N = _i(fields["N"], 1, 100)
        K = _i(fields["K"], 0, N)
        n = _i(fields["n"], 0, N)
        k = _i(fields["k"], 0, n)
        if fields["equal_likelihood_without_replacement"] is not True:
            raise ConditionsNotEstablished("Uniform subset sampling without replacement required")
        support_min, support_max = max(0, n - (N - K)), min(n, K)
        out.update(support=[support_min, support_max],
                   probability=Fraction(comb(K, k)*comb(N-K, n-k), comb(N, n))
                   if support_min <= k <= support_max else Fraction(0))
    elif conflict_id == "math.hs.statistics.correlation-regression":
        xs, ys = _seq(fields["xs"], 3, 32), _seq(fields["ys"], 3, 32)
        if len(xs) != len(ys):
            raise ConditionsNotEstablished("Paired observations must have same length")
        n = len(xs)
        dx = [n*x-sum(xs) for x in xs]
        dy = [n*y-sum(ys) for y in ys]
        sxx, syy = sum(x*x for x in dx), sum(y*y for y in dy)
        if sxx == 0:
            raise ConditionsNotEstablished("Constant x makes OLS slope undefined")
        sxy = sum(x*y for x, y in zip(dx, dy))
        out.update(slope=Fraction(sxy, sxx),
                   correlation_squared=Fraction(sxy*sxy, sxx*syy) if syy else None,
                   correlation_defined=syy != 0,
                   causality="NOT_ESTABLISHED",
                   nonlinear_relationship_excluded=False)
    elif conflict_id == "math.hs.triangle.area-sine":
        a,b,c = _r(fields["a"]),_r(fields["b"]),_r(fields["cos_included_angle"])
        if a <= 0 or b <= 0 or not -1 < c < 1 or fields["is_included_angle"] is not True:
            raise ConditionsNotEstablished("Nondegenerate triangle, positive sides, included angle required")
        out.update(area_squared=a*a*b*b*(1-c*c)/4,
                   nondegenerate=True,
                   expression="1/2*a*b*sin(included angle), square verified exactly")
    elif conflict_id == "math.hs.vector.linear-operations":
        u, v = _seq(fields["u"], 2, 5), _seq(fields["v"], 2, 5)
        if len(u) != len(v):
            raise ConditionsNotEstablished("Same vector dimension required")
        s = tuple(a+b for a,b in zip(u,v))
        out.update(sum_components=s, norm_sum_squared=sum(w*w for w in s),
                   norm_u_squared=sum(a*a for a in u),
                   norm_v_squared=sum(b*b for b in v),
                   norm_additivity="NOT_ASSUMED")
    return out
