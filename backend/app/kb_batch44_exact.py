"""Batch44 bounded exact CASE checks for 20 teacher-only core mathematics drafts.

No finite witness is a proof of a general theorem. Unsupported/free-form text is never certified.
All JSON-like arguments are exact bounded integers and lists, with no Python eval/sympify.
"""
from __future__ import annotations

from fractions import Fraction
from math import gcd

KEYS = {
    "set_predicate": ("domain","divisor","threshold"),
    "set_symdiff": ("universe","left","right"),
    "function_table": ("xs","ys"),
    "maximum_on_interval": ("lo","hi","right_closed"),
    "real_power_domain": ("x","numerator","denominator"),
    "rational_power": ("base","numerator","denominator"),
    "positive_exp_law": ("base","p","q"),
    "positive_exp_monotonic": ("base_num","base_den","x","y"),
    "log_inverse_integer": ("base","exponent"),
    "angle_degree_to_radian": ("degrees",),
    "vector_equal": ("u","v"),
    "zero_vector_direction": ("u",),
    "displacement": ("a","b"),
    "triangle_vector": ("a","b","c"),
    "vector_scale": ("u","numerator","denominator"),
    "vector_dot": ("u","v"),
    "vector_projection": ("u","v"),
    "complex_parts": ("real","imag"),
    "complex_equal": ("ar","ai","br","bi"),
    "complex_modulus_sq": ("real","imag"),
}

def _integer(x):
    return type(x) is int and -20 <= x <= 20

def _array(a, lo=0, hi=24):
    return type(a) is list and lo <= len(a) <= hi and all(_integer(x) for x in a)

def _vector(a):
    if not _array(a,2,2):
        raise ValueError("requires an exact two-dimensional integer vector")
    return a

def _points(a,b):
    x,y=_vector(a),_vector(b)
    return x,y

def _format(x):
    if type(x) is bool:
        return "true" if x else "false"
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x,tuple):
        return ",".join(_format(item) for item in x)
    return str(x)

def _perfect_root(base: int, n: int) -> int:
    if base < 0 and n % 2 == 0:
        raise ValueError("even root of negative real is undefined")
    sign = -1 if base < 0 else 1
    val = abs(base)
    for k in range(0,21):
        if k**n == val:
            return sign*k
    raise ValueError("irrational root outside exact rational witness scope")

def _calculate(op, a):
    if op == "set_predicate":
        D=a["domain"]; d=a["divisor"]; t=a["threshold"]
        if not _array(D) or len(set(D))!=len(D) or d==0:
            raise ValueError("finite unique domain and nonzero divisor")
        return tuple(sorted(x for x in D if x>t and x%d==0))
    if op=="set_symdiff":
        U,L,R=(a["universe"],a["left"],a["right"])
        if not all(_array(x) and len(set(x))==len(x) for x in (U,L,R)):
            raise ValueError("sets must not have duplicate elements")
        if not set(L)<=set(U) or not set(R)<=set(U):
            raise ValueError("subsets of fixed universe required")
        return tuple(sorted(set(L)^set(R)))
    if op=="function_table":
        xs,ys=a["xs"],a["ys"]
        if not _array(xs,1) or not _array(ys,1) or len(xs)!=len(ys):
            raise ValueError("paired nonempty table")
        pairs={}
        for x,y in zip(xs,ys):
            if x in pairs and pairs[x]!=y:
                raise ValueError("different outputs for same input")
            pairs[x]=y
        return tuple(f"{x}:{y}" for x,y in sorted(pairs.items()))
    if op=="maximum_on_interval":
        lo,hi,closed=a["lo"],a["hi"],a["right_closed"]
        if hi<=lo or closed not in (0,1):
            raise ValueError("nonempty bounded interval, explicit endpoint inclusion")
        return f"{'MAX' if closed else 'NO_MAX'}|{hi}"
    if op=="real_power_domain":
        x,p,n=a["x"],a["numerator"],a["denominator"]
        if n<=0 or gcd(abs(p),n)!=1:
            raise ValueError("require positive reduced denominator")
        if (x<0 and n%2==0) or (x==0 and p<=0):
            raise ValueError("not in real-power domain")
        return "DEFINED"
    if op=="rational_power":
        b,p,n=a["base"],a["numerator"],a["denominator"]
        if n<=0 or n>8 or gcd(abs(p),n)!=1 or b==0 and p<0:
            raise ValueError("require reduced rational exponent, nonzero for negative powers")
        root=_perfect_root(b,n)
        return Fraction(root,1)**p
    if op=="positive_exp_law":
        b,p,q=a["base"],a["p"],a["q"]
        if b<=0:
            raise ValueError("positive base for all integer exponents")
        left=Fraction(b)**p*Fraction(b)**q
        right=Fraction(b)**(p+q)
        if left!=right:raise ArithmeticError("exponential law violated")
        return right
    if op=="positive_exp_monotonic":
        bn,bd,x,y=(a[k] for k in ("base_num","base_den","x","y"))
        if bn<=0 or bd<=0 or bn==bd or x>=y:
            raise ValueError("positive non-unit base, strict input order")
        base=Fraction(bn,bd)
        fx,fy=base**x,base**y
        if not ((fx<fy) == (base>1)):
            raise ArithmeticError("monotonicity witness mismatch")
        return "INCREASING" if base>1 else "DECREASING"
    if op=="log_inverse_integer":
        b,e=a["base"],a["exponent"]
        if b<=1:
            raise ValueError("valid logarithm base > 1")
        x=Fraction(b)**e
        if x<=0:raise ArithmeticError("logarithm domain")
        return f"{e}|{x}"
    if op=="angle_degree_to_radian":
        return f"{Fraction(a['degrees'],180)}*pi"
    if op=="vector_equal":
        u,v=_points(a["u"],a["v"])
        return u==v
    if op=="zero_vector_direction":
        u=_vector(a["u"])
        return "ZERO|NO_DIRECTION" if u==[0,0] else "NONZERO|DIRECTION_DEFINED"
    if op=="displacement":
        p,q=_points(a["a"],a["b"])
        return tuple(y-x for x,y in zip(p,q))
    if op=="triangle_vector":
        p,q,r=(_vector(a[k]) for k in ("a","b","c"))
        first=[y-x for x,y in zip(p,q)]
        second=[z-y for y,z in zip(q,r)]
        total=tuple(x+y for x,y in zip(first,second))
        assert total==tuple(z-x for x,z in zip(p,r))
        return total
    if op=="vector_scale":
        u=_vector(a["u"])
        den=a["denominator"]
        if den==0:
            raise ValueError("scalar denominator cannot be zero")
        scale=Fraction(a["numerator"],den)
        return tuple(scale*x for x in u)
    if op=="vector_dot":
        u,v=_points(a["u"],a["v"])
        return sum(x*y for x,y in zip(u,v))
    if op=="vector_projection":
        u,v=_points(a["u"],a["v"])
        norm2=sum(x*x for x in v)
        if norm2==0:
            raise ValueError("projection direction requires nonzero v")
        dot=sum(x*y for x,y in zip(u,v))
        result=tuple(Fraction(dot*y,norm2) for y in v)
        residual=tuple(Fraction(x)-y for x,y in zip(u,result))
        if sum(x*y for x,y in zip(residual,v)) != 0:
            raise ArithmeticError("projection residual not perpendicular")
        return result
    if op=="complex_parts":
        return f"{a['real']}|{a['imag']}"
    if op=="complex_equal":
        return a["ar"]==a["br"] and a["ai"]==a["bi"]
    if op=="complex_modulus_sq":
        r,i=a["real"],a["imag"]
        return f"{r},{i}|{r*r+i*i}"
    raise KeyError("operator unsupported")

def witness(operator:object,payload:object)->dict:
    flags=dict(general_theorem_certified=False,
               student_freeform_step_verified=False,
               teacher_approved=False,student_publishable=False)
    if type(operator) is not str or operator not in KEYS:
        return dict(status="UNSUPPORTED",exact_value=None,**flags)
    if type(payload) is not dict or set(payload)!=set(KEYS[operator]):
        return dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,**flags)
    if not all((_array(v) if type(v) is list else
                (type(v) is int and -720<=v<=720) if operator=="angle_degree_to_radian" else _integer(v))
               for v in payload.values()):
        return dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,**flags)
    try:
        val=_calculate(operator,payload)
    except (ValueError,TypeError,ArithmeticError,ZeroDivisionError,KeyError,OverflowError,AssertionError):
        return dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,**flags)
    return dict(status="FINITE_EXACT_CASE_ONLY",exact_value=_format(val),**flags)

VALID = {
 "set_predicate":dict(domain=[-4,-2,0,1,2,4],divisor=2,threshold=0),
 "set_symdiff":dict(universe=[1,2,3,4],left=[1,2],right=[2,3]),
 "function_table":dict(xs=[0,1,1,2],ys=[1,3,3,5]),
 "maximum_on_interval":dict(lo=0,hi=1,right_closed=0),
 "real_power_domain":dict(x=-8,numerator=1,denominator=3),
 "rational_power":dict(base=-8,numerator=1,denominator=3),
 "positive_exp_law":dict(base=2,p=-1,q=3),
 "positive_exp_monotonic":dict(base_num=1,base_den=2,x=0,y=2),
 "log_inverse_integer":dict(base=2,exponent=-2),
 "angle_degree_to_radian":dict(degrees=150),
 "vector_equal":dict(u=[2,3],v=[2,3]),
 "zero_vector_direction":dict(u=[0,0]),
 "displacement":dict(a=[-2,1],b=[3,4]),
 "triangle_vector":dict(a=[0,0],b=[2,1],c=[5,-1]),
 "vector_scale":dict(u=[2,-4],numerator=-1,denominator=2),
 "vector_dot":dict(u=[2,-1],v=[3,4]),
 "vector_projection":dict(u=[-2,5],v=[0,2]),
 "complex_parts":dict(real=5,imag=-7),
 "complex_equal":dict(ar=3,ai=2,br=3,bi=2),
 "complex_modulus_sq":dict(real=-2,imag=3),
}
INVALID={
 "set_predicate":dict(domain=[1,2],divisor=0,threshold=0),
 "set_symdiff":dict(universe=[1,2],left=[1,3],right=[2]),
 "function_table":dict(xs=[1,1],ys=[2,3]),
 "maximum_on_interval":dict(lo=1,hi=0,right_closed=1),
 "real_power_domain":dict(x=-16,numerator=1,denominator=2),
 "rational_power":dict(base=-16,numerator=1,denominator=2),
 "positive_exp_law":dict(base=0,p=1,q=2),
 "positive_exp_monotonic":dict(base_num=2,base_den=2,x=0,y=1),
 "log_inverse_integer":dict(base=1,exponent=3),
 "angle_degree_to_radian":dict(degrees=True),
 "vector_equal":dict(u=[2,3,4],v=[2,3]),
 "zero_vector_direction":dict(u=[0,0,0]),
 "displacement":dict(a=[1,2,3],b=[4,5]),
 "triangle_vector":dict(a=[0,0],b=[2,1],c=[5]),
 "vector_scale":dict(u=[2,-4],numerator=1,denominator=0),
 "vector_dot":dict(u=[2,3],v=[1,2,3]),
 "vector_projection":dict(u=[1,2],v=[0,0]),
 "complex_parts":dict(real="5",imag=-7),
 "complex_equal":dict(ar=3,ai=2,br=3,bi=False),
 "complex_modulus_sq":dict(real=2,imag=2.5),
}
EXPECTED={
 "set_predicate":"2,4","set_symdiff":"1,3",
 "function_table":"0:1,1:3,2:5","maximum_on_interval":"NO_MAX|1",
 "real_power_domain":"DEFINED","rational_power":"-2",
 "positive_exp_law":"4","positive_exp_monotonic":"DECREASING",
 "log_inverse_integer":"-2|1/4","angle_degree_to_radian":"5/6*pi",
 "vector_equal":"true","zero_vector_direction":"ZERO|NO_DIRECTION",
 "displacement":"5,3","triangle_vector":"5,-1",
 "vector_scale":"-1,2","vector_dot":"2","vector_projection":"0,5",
 "complex_parts":"5|-7","complex_equal":"true",
 "complex_modulus_sq":"-2,3|13",
}
