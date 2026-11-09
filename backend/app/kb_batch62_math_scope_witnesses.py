"""Finite exact witnesses for ten high-risk Batch62 scope boundaries.

NO function proves a general theorem or verifies unrestricted student work.
Failure to establish premises is a ValueError rather than inferred permission.
Only integers and Fraction inputs are accepted; floats are deliberately refused.
"""
from __future__ import annotations
from fractions import Fraction
from collections.abc import Sequence

SCOPE="FINITE_EXACT_CASE_ONLY"

def q(x):
    if type(x) is int or type(x) is Fraction:
        return Fraction(x)
    raise ValueError("input must be exact integer/Fraction, not float/bool")

def witness(code: str, **facts):
    return {"scope":SCOPE,"certifies_general_theorem":False,
            "certifies_student_free_text":False,"code":code,"facts":facts}

def finite_complement(universe, target):
    U=set(universe); A=set(target)
    if len(U)>10000 or not A<=U:raise ValueError("missing finite universe/subset premise")
    return witness("FINITE_COMPLEMENT",universe_size=len(U),target_size=len(A),
                   complement=sorted(U-A))

def finite_quantifier_negation(domain, predicate_truth):
    D=list(domain); T=list(predicate_truth)
    if not D or len(D)!=len(T) or any(type(x) is not bool for x in T):
        raise ValueError("finite nonempty domain and boolean predicate required")
    all_true=all(T);exists_counterexample=any(not x for x in T)
    return witness("QUANTIFIER_NEGATION",forall=all_true,
                   exists_negated=exists_counterexample,
                   logical_equivalence=(not all_true)==exists_counterexample)

def amgm_squared_nonnegative(a,b):
    a,b=q(a),q(b)
    if a<0 or b<0:raise ValueError("AM-GM requires nonnegative reals")
    gap=(a-b)**2
    return witness("AMGM_SQUARED_CASE",gap=gap,nonnegative=gap>=0,
                   equality_case=(gap==0),
                   limitation="checks algebraic square only; not a full AM-GM proof")

def quadratic_real_root_count(a,b,c):
    a,b,c=q(a),q(b),q(c)
    if a==0:raise ValueError("quadratic leading coefficient must be nonzero")
    delta=b*b-4*a*c
    n=2 if delta>0 else (1 if delta==0 else 0)
    return witness("QUADRATIC_DISCRIMINANT",discriminant=delta,real_root_count=n)

def exponential_integer_power_pair(base,n):
    base=q(base)
    if not (base>0 and base!=1):raise ValueError("invalid real exponential base")
    if type(n) is not int or not (-30<=n<=30):
        raise ValueError("bounded integer exponents only")
    first=base**n; second=base**(n+1)
    return witness("EXPONENTIAL_LOCAL_PAIR",first=first,second=second,
                   increasing_pair=second>first,base_gt_one=base>1)

def logarithm_real_domain(base,argument):
    base,argument=q(base),q(argument)
    if not(base>0 and base!=1 and argument>0):
        raise ValueError("real logarithm premises not satisfied")
    return witness("LOG_DOMAIN_ONLY",valid_domain=True,
                   limitation="no general logarithm identity is proved")

def vector_basis_two_dimensions(u,v):
    if len(u)!=2 or len(v)!=2:raise ValueError("2-dimensional coordinate pairs required")
    ux,uy=map(q,u);vx,vy=map(q,v)
    det=ux*vy-uy*vx
    return witness("VECTOR_BASIS_DET",determinant=det,is_basis=(det!=0))

def equally_likely_event(outcome_weights,event_indices):
    W=[q(w) for w in outcome_weights]
    E=set(event_indices)
    if not W or len(W)>10000 or any(w<=0 for w in W):
        raise ValueError("positive finite weights required")
    if any(type(i) is not int or i<0 or i>=len(W) for i in E):
        raise ValueError("event index outside finite universe")
    if len(set(W))!=1:
        raise ValueError("classical count requires equal elementary event weights")
    return witness("CLASSICAL_EQUAL_WEIGHT",probability=Fraction(len(E),len(W)),
                   count=len(E),universe_count=len(W))

def quadratic_differential_vs_delta(x,h):
    x,h=q(x),q(h)
    differential=2*x*h
    actual=(x+h)**2-x*x
    return witness("QUADRATIC_LOCAL_LINEAR",differential=differential,
                   actual_increment=actual,remainder=actual-differential,
                   equality_only_if_zero_h=(actual==differential)==(h==0))

def triangle_cosine_ratio(a,b,c):
    a,b,c=q(a),q(b),q(c)
    if min(a,b,c)<=0 or not(a+b>c and a+c>b and b+c>a):
        raise ValueError("nondegenerate positive triangle sides required")
    cos=(a*a+b*b-c*c)/(2*a*b)
    return witness("FINITE_COSINE_RATIO",cosine_of_opposite_c=cos,
                   in_real_angle_range=(-1<cos<1))
