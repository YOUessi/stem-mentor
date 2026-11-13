"""Independent, finite EXACT mathematical witnesses for ten historical conflict packets.

This module deliberately never certifies a universal theorem, resolves historical
version disagreements, checks free-form student steps, or endorses a teacher.
All accepted inputs are small exact integers/lists (no float, bool, eval, sympify).
"""
from __future__ import annotations

from fractions import Fraction as F
from itertools import combinations
from math import comb

OPS = (
    "composition_domain", "parity_domain", "piecewise_well_defined",
    "ivt_zero", "point_line_distance", "binomial_independence",
    "hypergeometric_support", "ols_variances", "triangle_included_angle",
    "vector_linear_dimensions",
)
KEYS = {
    "composition_domain": {"x", "shift"},
    "parity_domain": {"domain", "degree", "parity"},
    "piecewise_well_defined": {"domain", "branches"},
    "ivt_zero": {"a", "b", "coefficients", "family"},
    "point_line_distance": {"A", "B", "C", "point"},
    "binomial_independence": {"weights"},
    "hypergeometric_support": {"N", "K", "n", "k", "replacement"},
    "ols_variances": {"pairs", "require_correlation"},
    "triangle_included_angle": {"P", "Q", "R", "sine"},
    "vector_linear_dimensions": {"u", "v", "scalar"},
}


def _exact(value, level=0):
    if level > 5:
        raise ValueError("nested input exceeds depth")
    if type(value) is int:
        if abs(value) > 512:
            raise ValueError("exact integer outside finite witness bounds")
    elif type(value) is list:
        if len(value) > 64:
            raise ValueError("oversize exact list")
        for member in value:
            _exact(member, level+1)
    else:
        raise ValueError("only exact integers and bounded integer lists allowed")


def check(operation, payload):
    """Return (FINITE_EXACT_WITNESS_ONLY, evidence) or (CONDITIONS_NOT_ESTABLISHED, reason).

    Malformed JSON schemas fail closed by raising ValueError; mathematically
    well-formed but inapplicable instances return CONDITIONS_NOT_ESTABLISHED.
    """
    if operation not in OPS or type(payload) is not dict or set(payload) != KEYS[operation]:
        raise ValueError("unknown operation or incorrect exact witness schema")
    for val in payload.values():
        _exact(val)
    def fail(reason):
        return "CONDITIONS_NOT_ESTABLISHED", {"failed_condition": reason}
    ev = {}
    if operation == "composition_domain":
        x, shift = payload["x"], payload["shift"]
        if x == shift:
            return fail("inner_value_not_in_outer_domain")
        ev = {"g_of_x": x-shift, "f_of_g": str(F(1, x-shift))}
    elif operation == "parity_domain":
        domain = payload["domain"]
        degree, parity = payload["degree"], payload["parity"]
        if len(domain) < 1 or len(set(domain)) != len(domain) or degree < 0 or degree > 9 or parity not in (0, 1):
            return fail("finite_sample_domain_or_exponent_invalid")
        if set(domain) != {-x for x in domain}:
            return fail("domain_not_symmetric_under_negation")
        if any(((-x)**degree != (x**degree if parity == 0 else -(x**degree))) for x in domain):
            return fail("even_or_odd_equality_fails_at_sample")
        ev = {"sample_points": len(domain), "parity": "EVEN" if parity == 0 else "ODD"}
    elif operation == "piecewise_well_defined":
        domain, branches = payload["domain"], payload["branches"]
        if not domain or len(set(domain)) != len(domain) or not branches:
            return fail("invalid_finite_domain")
        values = {x: [] for x in domain}
        for br in branches:
            if len(br) != 2 or len(br[0]) != len(br[1]) or len(set(br[0])) != len(br[0]):
                return fail("malformed_branch")
            for x,y in zip(*br):
                if x not in values:
                    return fail("branch_outside_declared_domain")
                values[x].append(y)
        if any(not vv for vv in values.values()):
            return fail("uncovered_input")
        if any(len(set(vv)) != 1 for vv in values.values()):
            return fail("overlapping_branches_disagree")
        ev = {"finite_domain_size": len(domain),
              "overlap_points_agree": sum(len(vv)>1 for vv in values.values())}
    elif operation == "ivt_zero":
        a,b,coef,family = (payload[k] for k in ("a","b","coefficients","family"))
        if family != 0:
            return fail("continuity_not_established_for_nonpolynomial")
        if a >= b or not 1 <= len(coef) <= 6:
            return fail("invalid_closed_interval_or_polynomial")
        def value(x):
            return sum(c * x**i for i,c in enumerate(coef))
        va, vb = value(a), value(b)
        if va * vb >= 0:
            return fail("endpoint_strict_sign_change_not_established")
        ev = {"left": va, "right": vb, "continuity": "POLYNOMIAL_FAMILY_ONLY",
              "conclusion": "EXISTENCE_BY_IVT_NOT_UNIQUENESS"}
    elif operation == "point_line_distance":
        A,B,C = (payload[k] for k in ("A","B","C"))
        p = payload["point"]
        if len(p) != 2 or A*A+B*B == 0:
            return fail("nonzero_normal_and_two_coordinates_required")
        numerator = A*p[0]+B*p[1]+C
        ev = {"distance_squared": str(F(numerator*numerator, A*A+B*B))}
    elif operation == "binomial_independence":
        w = payload["weights"]
        if len(w) != 4 or any(x < 0 for x in w) or sum(w)==0:
            return fail("valid_joint_bernoulli_distribution_required")
        total=sum(w)
        # Joint order: (0,0), (0,1), (1,0), (1,1).
        p1,p2=F(w[2]+w[3],total),F(w[1]+w[3],total)
        if p1 != p2:
            return fail("identically_distributed_trials_required")
        if F(w[3],total) != p1*p2:
            return fail("independence_not_established_by_marginals")
        ev = {"individual_success_probability": str(p1),
              "exactly_one_success": str(F(w[1]+w[2],total)),
              "binomial_n2_k1": str(2*p1*(1-p1))}
        assert ev["exactly_one_success"] == ev["binomial_n2_k1"]
    elif operation == "hypergeometric_support":
        N,K,n,k,replacement=(payload[z] for z in ("N","K","n","k","replacement"))
        if replacement != 0:
            return fail("without_replacement_required")
        if not 1<=N<=12 or not 0<=K<=N or not 0<=n<=N:
            return fail("valid_finite_population_required")
        if not max(0,n-(N-K))<=k<=min(n,K):
            return fail("out_of_hypergeometric_support")
        possible=list(combinations(range(N),n))
        count=sum(sum(x<K for x in draw)==k for draw in possible)
        formula=F(comb(K,k)*comb(N-K,n-k),comb(N,n))
        assert F(count,len(possible))==formula
        ev={"support":[max(0,n-(N-K)),min(n,K)],"probability":str(formula),
            "enumerated_samples":len(possible)}
    elif operation == "ols_variances":
        pairs=payload["pairs"]
        if len(pairs)<2 or any(len(row)!=2 for row in pairs):
            return fail("at_least_two_complete_pairs_required")
        if payload["require_correlation"] not in (0,1):
            return fail("invalid_correlation_flag")
        nn=len(pairs)
        meanx=F(sum(row[0] for row in pairs),nn)
        meany=F(sum(row[1] for row in pairs),nn)
        Sxx=sum((F(row[0])-meanx)**2 for row in pairs)
        Syy=sum((F(row[1])-meany)**2 for row in pairs)
        Sxy=sum((F(row[0])-meanx)*(F(row[1])-meany) for row in pairs)
        if Sxx==0:
            return fail("ols_slope_denominator_Sxx_zero")
        if payload["require_correlation"]==1 and Syy==0:
            return fail("correlation_denominator_Syy_zero")
        slope=Sxy/Sxx
        intercept=meany-slope*meanx
        ev={"Sxx":str(Sxx),"Syy":str(Syy),"slope":str(slope),
            "intercept":str(intercept),"correlation_defined":Syy>0}
    elif operation == "triangle_included_angle":
        P,Q,R,sine=(payload[z] for z in ("P","Q","R","sine"))
        if any(len(x)!=2 for x in (P,Q,R,sine)) or sine[1]==0:
            return fail("valid_two_dimensional_triangle_and_sine_required")
        ux,uy=Q[0]-P[0],Q[1]-P[1]
        vx,vy=R[0]-P[0],R[1]-P[1]
        det=ux*vy-uy*vx
        nu=ux*ux+uy*uy
        nv=vx*vx+vy*vy
        s=F(*sine)
        if det==0 or nu==0 or nv==0:
            return fail("nondegenerate_triangle_required")
        if not 0<s<=1 or s*s*nu*nv!=det*det:
            return fail("sine_does_not_match_included_angle")
        ev={"area":str(F(abs(det),2)),"sine_of_included_angle_squared":str(s*s)}
    elif operation == "vector_linear_dimensions":
        u,v,a=payload["u"],payload["v"],payload["scalar"]
        if not u or len(u)!=len(v):
            return fail("same_positive_dimension_required")
        lhs=[a*(x+y) for x,y in zip(u,v)]
        rhs=[a*x+a*y for x,y in zip(u,v)]
        assert lhs==rhs
        ev={"dimension":len(u),"distributive_result":lhs}
    return "FINITE_EXACT_WITNESS_ONLY",ev
