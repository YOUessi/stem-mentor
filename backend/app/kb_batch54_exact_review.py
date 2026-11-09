"""Twelve bounded exact educational witnesses for Batch54 review-only math cards.

These are not general proof certificates, official clause certifications, model
evaluation, or a parser of arbitrary student text. Fail closed on unknown fields.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import pairwise
from math import comb, gcd, lcm

class PreconditionsNotEstablished(ValueError):
    pass

def rational(value):
    if isinstance(value,bool) or not isinstance(value,(int,Fraction)):
        raise PreconditionsNotEstablished("integer/Fraction exact input required")
    f=Fraction(value)
    if abs(f.numerator)>1000000 or f.denominator>1000000:
        raise PreconditionsNotEstablished("operand range exceeded")
    return f

def integer(value,minimum=0,maximum=100):
    if isinstance(value,bool) or not isinstance(value,int) or not minimum<=value<=maximum:
        raise PreconditionsNotEstablished("invalid bounded integer")
    return value

def poly(coefficients,x):
    return sum(c*x**i for i,c in enumerate(coefficients))

def reviewed_finite_witness(op: str, **kwargs):
    """Return a per-instance, non-publishable result; never a universal proof."""
    specs={
        "epsilon_inverse_n":{"epsilon"},
        "bounded_prefix":{"values"},
        "monotone_prefix":{"values"},
        "ivt_polynomial":{"coefficients","left","right"},
        "mvt_quadratic":{"p","q","r","left","right"},
        "binomial_tail":{"trials","at_least"},
        "quadratic_differential":{"p","q","r","x","h"},
        "ftc_polynomial":{"coefficients","left","right"},
        "classical_logic":{"p"},
        "production_power":{"A","L","K","alpha","beta"},
        "beat_lcm":{"periods","beats_per_minute"},
        "affine_recurrence":{"a","b","x0","n"},
    }
    if op not in specs or set(kwargs)!=specs.get(op):
        raise PreconditionsNotEstablished("unknown operation or missing/extra argument")
    status="FINITE_EXACT_CASE_ONLY"
    if op=="epsilon_inverse_n":
        eps=rational(kwargs["epsilon"])
        if eps<=0: raise PreconditionsNotEstablished("epsilon must be strictly positive")
        n=eps.denominator//eps.numerator+1
        return {"status":status,"N":n,"strict_witness":Fraction(1,n)<eps}
    if op in ("bounded_prefix","monotone_prefix"):
        vals=kwargs["values"]
        if not isinstance(vals,(tuple,list)) or not 2<=len(vals)<=40:
            raise PreconditionsNotEstablished("finite, nontrivial prefix required")
        xs=[rational(v) for v in vals]
        if op=="bounded_prefix":
            return {"status":"FINITE_PREFIX_ONLY_NOT_CONVERGENCE","bound":max(abs(x) for x in xs)}
        return {"status":"FINITE_PREFIX_ONLY_NOT_CONVERGENCE",
                "nondecreasing":all(a<=b for a,b in pairwise(xs)),
                "nonincreasing":all(a>=b for a,b in pairwise(xs))}
    if op=="ivt_polynomial":
        coeff=kwargs["coefficients"]
        if not isinstance(coeff,(tuple,list)) or not 1<=len(coeff)<=6:
            raise PreconditionsNotEstablished("finite polynomial coefficients required")
        cf=[rational(v) for v in coeff]
        a,b=rational(kwargs["left"]),rational(kwargs["right"])
        if a>=b:raise PreconditionsNotEstablished("nondegenerate ordered interval required")
        va,vb=poly(cf,a),poly(cf,b)
        return {"status":status,"left_value":va,"right_value":vb,
                "zero_bracketed_by_continuous_polynomial":va*vb<=0,
                "root_unique":"UNDETERMINED"}
    if op=="mvt_quadratic":
        p,q,r=map(rational,(kwargs["p"],kwargs["q"],kwargs["r"]))
        a,b=rational(kwargs["left"]),rational(kwargs["right"])
        if a>=b: raise PreconditionsNotEstablished("closed interval with a<b required")
        c=(a+b)/2
        slope=(poly([r,q,p],b)-poly([r,q,p],a))/(b-a)
        if p==0:
            return {"status":status,"witness_c":c,"slope":slope,"non_unique":True,
                    "derivative_at_witness":q}
        return {"status":status,"witness_c":c,"slope":slope,
                "derivative_at_witness":2*p*c+q,"non_unique":False}
    if op=="binomial_tail":
        n=integer(kwargs["trials"],1,24);k=integer(kwargs["at_least"],0,n)
        return {"status":status,"p_value_under_fair_coin_null":
                Fraction(sum(comb(n,i) for i in range(k,n+1)),2**n),
                "posterior_h0":"NOT_DETERMINED"}
    if op=="quadratic_differential":
        p,q,r,x,h=map(rational,(kwargs["p"],kwargs["q"],kwargs["r"],
                               kwargs["x"],kwargs["h"]))
        delta=poly([r,q,p],x+h)-poly([r,q,p],x)
        differential=(2*p*x+q)*h
        return {"status":status,"finite_delta":delta,"linear_differential":differential,
                "remainder":delta-differential,"expected_remainder":p*h*h}
    if op=="ftc_polynomial":
        cs=kwargs["coefficients"]
        if not isinstance(cs,(tuple,list)) or not 1<=len(cs)<=6:
            raise PreconditionsNotEstablished("polynomial of degree at most five required")
        cf=[rational(v) for v in cs]
        a,b=rational(kwargs["left"]),rational(kwargs["right"])
        if a>b: raise PreconditionsNotEstablished("ordered integration bounds required")
        value=sum(c*(b**(i+1)-a**(i+1))/(i+1) for i,c in enumerate(cf))
        return {"status":status,"integral":value,"integrand_at_left":poly(cf,a)}
    if op=="classical_logic":
        p=kwargs["p"]
        if not isinstance(p,bool):raise PreconditionsNotEstablished("classical truth value required")
        return {"status":status,"noncontradiction":not (p and not p),
                "excluded_middle":p or not p,"same_syntax":False}
    if op=="production_power":
        A,L,K=(rational(kwargs[k]) for k in ("A","L","K"))
        alpha=integer(kwargs["alpha"],0,8);beta=integer(kwargs["beta"],0,8)
        if min(A,L,K)<=0:raise PreconditionsNotEstablished("all log inputs strictly positive")
        return {"status":status,"Q":A*(L**alpha)*(K**beta),
                "log_rule_applicable":True,"causal_model_validity":"NOT_ASSESSED"}
    if op=="beat_lcm":
        ps=kwargs["periods"]
        if not isinstance(ps,(tuple,list)) or not 2<=len(ps)<=5:
            raise PreconditionsNotEstablished("2-5 positive integer periods required")
        vals=[integer(v,1,96) for v in ps]
        pulses=lcm(*vals)
        bpm=kwargs["beats_per_minute"]
        if bpm is None:
            return {"status":status,"first_sync_beats":pulses,"seconds":None}
        tempo=rational(bpm)
        if tempo<=0:raise PreconditionsNotEstablished("strict positive tempo required")
        return {"status":status,"first_sync_beats":pulses,"seconds":pulses*60/tempo}
    if op=="affine_recurrence":
        a,b,x=map(rational,(kwargs["a"],kwargs["b"],kwargs["x0"]))
        n=integer(kwargs["n"],0,30)
        current=x
        for _ in range(n):current=a*current+b
        finite_formula=a**n*x+b*sum((a**k for k in range(n)),Fraction(0))
        return {"status":status,"iterated_value":current,"finite_sum_formula":finite_formula,
                "a_equals_one_branch_used":a==1}
    raise AssertionError("exhaustiveness invariant")
