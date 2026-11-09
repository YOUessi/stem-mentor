"""Bounded exact witnesses for source spans; never certify universal claims/teacher review.

No free-form mathematical expressions, untrusted eval, or floating-point input.
"""
from __future__ import annotations

from fractions import Fraction

class ConditionsNotEstablished(ValueError):
    pass

def require(ok,msg):
    if not ok:
        raise ConditionsNotEstablished(msg)

def q(x):
    require(type(x) in (int,Fraction),"exact int/Fraction only; bool and float rejected")
    y=Fraction(x)
    require(abs(y.numerator)<=10**8 and y.denominator<=10**8,"bounded exact input only")
    return y

def integer(x,lo,hi):
    require(type(x) is int and lo<=x<=hi,"bounded integer required")
    return x

def seq(x,limit=12):
    require(type(x) in (tuple,list) and 1<=len(x)<=limit,"bounded nonempty sequence required")
    return x

FIELDS = {
    "finite_set_complement":("universe","subset"),
    "finite_quantifier_negation":("truth_values",),
    "agm_square":("a","b"),
    "quadratic_discriminant":("a","b","c"),
    "exponent_integer_order":("base","m","n"),
    "rational_unit_circle_tan":("sin","cos"),
    "polynomial_bisection":("coefficients","left","right"),
    "log_exponential_inverse":("base","integer_exponent"),
}

def exact_witness(op,**kwargs):
    require(op in FIELDS,"unsupported operator")
    require(set(kwargs)==set(FIELDS[op]),"required arguments / unknown metadata")
    if op=="finite_set_complement":
        u=seq(kwargs["universe"]); sub=kwargs["subset"]
        require(type(sub) in (list,tuple) and len(sub)<=12,"bad subset")
        require(all(type(z) is int for z in tuple(u)+tuple(sub)),"finite integer universe only")
        require(len(set(u))==len(u) and len(set(sub))==len(sub),"duplicate elements")
        require(set(sub)<=set(u),"subset outside universe")
        payload={"complement":tuple(z for z in u if z not in set(sub)),
                 "relative_to_universe":True}
    elif op=="finite_quantifier_negation":
        items=seq(kwargs["truth_values"])
        require(all(type(z) is bool for z in items),"finite Boolean domain required")
        payload={"forall":all(items),"exists":any(items),
                 "not_forall_equals_exists_counterexample":(not all(items))==any(not z for z in items),
                 "not_exists_equals_forall_not":(not any(items))==all(not z for z in items)}
    elif op=="agm_square":
        a,b=q(kwargs["a"]),q(kwargs["b"])
        require(a>=0 and b>=0,"AGM requires nonnegative terms")
        # Exact nonnegative squared gap witnesses (a+b)^2 >= 4ab.
        payload={"square_gap":(a-b)**2,"inequality_holds":(a+b)**2>=4*a*b,
                 "equality":a==b,"sqrt_ab_explicitly_computed":False}
    elif op=="quadratic_discriminant":
        a,b,c=(q(kwargs[k]) for k in FIELDS[op])
        require(a!=0,"a=0 is not quadratic")
        D=b*b-4*a*c
        payload={"discriminant":D,"real_root_count":0 if D<0 else (1 if D==0 else 2),
                 "general_roots_computed":False}
    elif op=="exponent_integer_order":
        a=q(kwargs["base"]);m=integer(kwargs["m"],-20,20);n=integer(kwargs["n"],-20,20)
        require(a>0 and a!=1,"restricted course exponential function base")
        left,right=a**m,a**n
        payload={"base":a,"m":m,"n":n,"value_m":left,"value_n":right,
                 "monotonicity_witness":("increasing" if a>1 else "decreasing"),
                 "ordered_correctly":((left<right)==(m<n)) if a>1 else ((left>right)==(m<n)) if m!=n else left==right}
    elif op=="rational_unit_circle_tan":
        s,c=q(kwargs["sin"]),q(kwargs["cos"])
        require(s*s+c*c==1,"unit-circle premise missing")
        require(c!=0,"tangent not defined at zero cosine")
        payload={"tan":s/c,"identity":s*s+c*c==1,"angle_certified":False}
    elif op=="polynomial_bisection":
        co=seq(kwargs["coefficients"],limit=6); a=q(kwargs["left"]); b=q(kwargs["right"])
        cs=[q(x) for x in co]
        require(a<b,"strict ordered endpoints needed")
        require(any(cs),"zero polynomial not a usable bracketing witness")
        def f(x):
            out=Fraction(0)
            for coeff in reversed(cs):out=out*x+coeff
            return out
        fa,fb=f(a),f(b)
        require(fa*fb<0,"strict sign-change bracket required; same sign is inconclusive")
        m=(a+b)/2;fm=f(m)
        if fm==0: left=right=m
        elif fa*fm<0:left,right=a,m
        else:left,right=m,b
        payload={"midpoint":m,"f_midpoint":fm,"new_left":left,"new_right":right,
                 "interval_width":right-left,
                 "continuity_reason":"POLYNOMIAL_DEFINED_ON_ALL_REALS",
                 "root_existence_witness":True,
                 "uniqueness":"UNDETERMINED"}
    elif op=="log_exponential_inverse":
        a=q(kwargs["base"]);k=integer(kwargs["integer_exponent"],-20,20)
        require(a>0 and a!=1,"logarithm/exponential base must be positive and not 1")
        payload={"positive_argument":a**k,"exponent":k,
                 "inverse_law_for_this_integer_power":True,
                 "arbitrary_real_logarithm_computed":False}
    else:
        raise AssertionError("unreachable")
    return {
        "status":"FINITE_EXACT_CASE_ONLY",
        "scope":"NOT_FORMAL_GENERAL_PROOF",
        "teacher_approved":False,"student_solution_verified":False,
        "source_clause_certified":False,
        "result":payload,
    }
