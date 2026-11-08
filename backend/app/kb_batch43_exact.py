"""Batch43: 24 bounded EXACT CASE witnesses with explicit domain gates.
Not formal proof certification, not a free-text student solver, not a teacher review.
"""
from __future__ import annotations
from fractions import Fraction
from math import comb, perm

KEYS = {
"subset":("universe","left","right"),
"complement":("universe","members"),
"sufficient":("p","q"),
"equivalent":("p","q"),
"neg_exists":("truth",),
"quadratic_inequality":("a","b","c","points"),
"change_base":("base","p","q"),
"unit_identity":("cos_num","sin_num","den"),
"bisection":("lo","hi","square"),
"parallel_nonzero":("left","right"),
"perpendicular_nonzero":("left","right"),
"ssa_acute":("a","b","sin_num","sin_den"),
"induction_sum":("n",),
"quadratic_derivative":("a","b","c","x","h"),
"fermat_quadratic":("a","center","shift"),
"plane_distance_squared":("point","plane_point","normal"),
"line_slope":("p","q"),
"circle_line":("cx","cy","radius","a","b","c"),
"permutation":("n","r"),
"combination":("n","r"),
"binomial_coefficients":("n",),
"total_probability":("weights","successes","total","trials"),
"bayes_posterior":("weights","likelihoods","total","trials","target"),
"discrete_moments":("values","weights","total"),
}
def _int(x):
    return type(x) is int and -100 <= x <= 100
def _vec(v,lo=1,hi=20):
    return type(v) is list and lo <= len(v) <= hi and all(_int(i) for i in v)
def _distinct(v):
    return len(set(v))==len(v)
def _positive(v):
    return _int(v) and v>0
def _text(v):
    if type(v) is bool: return "true" if v else "false"
    if isinstance(v,Fraction):return str(v)
    if type(v) is tuple:return ",".join(str(z) for z in v)
    return str(v)
def _calc(op,a):
    if op in ("subset","complement"):
        universe=a["universe"]
        if not _vec(universe) or not _distinct(universe):raise ValueError("invalid universe")
        first=a["left"] if op=="subset" else a["members"]
        if not _vec(first,lo=0) or not _distinct(first) or not set(first)<=set(universe):
            raise ValueError("left must be subset of universe")
        if op=="complement":return tuple(sorted(set(universe)-set(first)))
        right=a["right"]
        if not _vec(right,lo=0) or not _distinct(right) or not set(right)<=set(universe):
            raise ValueError("right must be subset of universe")
        return set(first)<=set(right)
    if op in ("sufficient","equivalent"):
        p,q=a["p"],a["q"]
        if not _vec(p) or not _vec(q) or len(p)!=len(q) or set(p+q)-{0,1}:
            raise ValueError("finite binary proposition truth arrays required")
        if op=="sufficient":return all(not x or y for x,y in zip(p,q))
        return all(x==y for x,y in zip(p,q))
    if op=="neg_exists":
        v=a["truth"]
        if not _vec(v,lo=0) or set(v)-{0,1}:raise ValueError("truth array")
        return not any(v)
    if op=="quadratic_inequality":
        points=a["points"]
        if a["a"]==0 or not _vec(points) or not _distinct(points):
            raise ValueError("nonzero quadratic and distinct finite domain")
        return tuple(x for x in sorted(points) if a["a"]*x*x+a["b"]*x+a["c"]<=0)
    if op=="change_base":
        if not 2<=a["base"]<=10 or not 1<=a["p"]<=8 or not 1<=a["q"]<=8:
            raise ValueError("positive non-unit common base/exponents")
        return Fraction(a["p"],a["q"])
    if op=="unit_identity":
        den=a["den"]
        if den<=0:raise ValueError("positive denominator")
        return a["cos_num"]**2+a["sin_num"]**2==den**2
    if op=="bisection":
        lo,hi,c=a["lo"],a["hi"],a["square"]
        if lo<0 or hi<=lo or c<=0 or (lo*lo-c)*(hi*hi-c)>=0:
            raise ValueError("continuous x squared minus c requires bracket with strict signs")
        mid=Fraction(lo+hi,2)
        fmid=mid*mid-c
        if fmid==0:return f"ROOT|{mid}"
        newlo,newhi=(lo,mid) if fmid>0 else (mid,hi)
        return f"{newlo}|{newhi}|{newhi-newlo}"
    if op in ("parallel_nonzero","perpendicular_nonzero"):
        u,v=a["left"],a["right"]
        if not _vec(u,2,2) or not _vec(v,2,2) or not any(u) or not any(v):
            raise ValueError("two nonzero 2d vectors")
        if op=="parallel_nonzero":return u[0]*v[1]-u[1]*v[0]==0
        return u[0]*v[0]+u[1]*v[1]==0
    if op=="ssa_acute":
        side,adj=a["a"],a["b"]
        num,den=a["sin_num"],a["sin_den"]
        if side<=0 or adj<=0 or not 0<num<den:
            raise ValueError("nondegenerate sides and acute sine in (0,1)")
        altitude=Fraction(adj*num,den)
        if side<altitude:return "NONE"
        if side==altitude:return "ONE"
        return "TWO" if side<adj else "ONE"
    if op=="induction_sum":
        n=a["n"]
        if not 1<=n<=100:raise ValueError("positive finite integer index")
        total=sum(range(1,n+1))
        if total!=n*(n+1)//2:raise ArithmeticError("invariant failure")
        return total
    if op=="quadratic_derivative":
        if a["h"]==0:raise ValueError("difference quotient needs h nonzero")
        x,h=a["x"],a["h"]
        aa,b,c=a["a"],a["b"],a["c"]
        f=lambda z:aa*z*z+b*z+c
        diff=Fraction(f(x+h)-f(x),h)
        formal=2*aa*x+b
        if diff!=formal+aa*h:raise ArithmeticError("difference identity failed")
        return f"{formal}|{diff}"
    if op=="fermat_quadratic":
        if a["a"]==0:raise ValueError("nonzero curvature for strict extremum")
        return "MINIMUM|0" if a["a"]>0 else "MAXIMUM|0"
    if op=="plane_distance_squared":
        p,p0,n=[a[k] for k in ("point","plane_point","normal")]
        if not all(_vec(v,3,3) for v in (p,p0,n)) or not any(n):
            raise ValueError("proper plane requires nonzero normal")
        dot=sum((x-y)*t for x,y,t in zip(p,p0,n))
        return Fraction(dot*dot,sum(t*t for t in n))
    if op=="line_slope":
        p,q=a["p"],a["q"]
        if not _vec(p,2,2) or not _vec(q,2,2) or p==q:
            raise ValueError("two distinct points")
        dx=q[0]-p[0]
        return "UNDEFINED" if dx==0 else Fraction(q[1]-p[1],dx)
    if op=="circle_line":
        cx,cy,r,A,B,C=[a[k] for k in ("cx","cy","radius","a","b","c")]
        norm=A*A+B*B
        if r<=0 or norm==0:raise ValueError("positive circle radius and genuine line")
        distance2=Fraction((A*cx+B*cy+C)**2,norm)
        return "TWO" if distance2<r*r else "TANGENT" if distance2==r*r else "NONE"
    if op in ("permutation","combination"):
        n,r=a["n"],a["r"]
        if not 0<=r<=n<=12:raise ValueError("bounded nonnegative n,r")
        return perm(n,r) if op=="permutation" else comb(n,r)
    if op=="binomial_coefficients":
        if not 0<=a["n"]<=12:raise ValueError("nonnegative integer n")
        return tuple(comb(a["n"],k) for k in range(a["n"]+1))
    if op in ("total_probability","bayes_posterior"):
        weights=a["weights"]
        outcomes=a["successes"] if op=="total_probability" else a["likelihoods"]
        total,trials=a["total"],a["trials"]
        if not _vec(weights) or not _vec(outcomes) or len(weights)!=len(outcomes) or \
            total<=0 or trials<=0 or sum(weights)!=total or \
            any(w<=0 for w in weights) or any(not 0<=x<=trials for x in outcomes):
            raise ValueError("strict positive partition, normalized prior and bounded likelihood")
        numerator=sum(w*x for w,x in zip(weights,outcomes))
        if op=="total_probability":return Fraction(numerator,total*trials)
        idx=a["target"]
        if not 0<=idx<len(weights) or numerator<=0:raise ValueError("positive evidence and valid hypothesis")
        return Fraction(weights[idx]*outcomes[idx],numerator)
    if op=="discrete_moments":
        values,weights,total=a["values"],a["weights"],a["total"]
        if not _vec(values) or not _vec(weights) or len(values)!=len(weights) or \
            total<=0 or sum(weights)!=total or any(w<0 for w in weights):
            raise ValueError("nonnegative normalized finite distribution required")
        mean=Fraction(sum(v*w for v,w in zip(values,weights)),total)
        variance=sum((Fraction(v)-mean)**2*w for v,w in zip(values,weights))/total
        return f"{mean}|{variance}"
    raise KeyError("unsupported")
def witness(operator:object,values:object)->dict:
    flags=dict(general_theorem_certified=False,student_freeform_step_verified=False,
        teacher_approved=False,student_publishable=False)
    if type(operator) is not str or operator not in KEYS:
        return dict(status="UNSUPPORTED",exact_value=None,**flags)
    if type(values) is not dict or set(values)!=set(KEYS[operator]):
        return dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,**flags)
    if not all(_int(x) if type(x) is not list else _vec(x,lo=0)
        for x in values.values()):
        return dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,**flags)
    try:
        result=_calc(operator,values)
    except (ValueError,TypeError,ZeroDivisionError,ArithmeticError,KeyError,OverflowError):
        return dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,**flags)
    return dict(status="FINITE_EXACT_CASE_ONLY",exact_value=_text(result),**flags)
VALID={
"subset":dict(universe=[1,2,3],left=[1,3],right=[1,2,3]),
"complement":dict(universe=[0,1,2,3],members=[1,3]),
"sufficient":dict(p=[0,0,1,1],q=[0,1,1,1]),
"equivalent":dict(p=[0,1,0,1],q=[0,1,0,1]),
"neg_exists":dict(truth=[0,0,0]),
"quadratic_inequality":dict(a=1,b=-5,c=6,points=[0,1,2,3,4]),
"change_base":dict(base=2,p=3,q=2),
"unit_identity":dict(cos_num=3,sin_num=4,den=5),
"bisection":dict(lo=1,hi=2,square=2),
"parallel_nonzero":dict(left=[2,4],right=[1,2]),
"perpendicular_nonzero":dict(left=[1,2],right=[2,-1]),
"ssa_acute":dict(a=5,b=8,sin_num=1,sin_den=2),
"induction_sum":dict(n=10),
"quadratic_derivative":dict(a=1,b=0,c=0,x=3,h=1),
"fermat_quadratic":dict(a=1,center=0,shift=0),
"plane_distance_squared":dict(point=[1,2,4],plane_point=[0,0,1],normal=[0,0,1]),
"line_slope":dict(p=[0,0],q=[2,4]),
"circle_line":dict(cx=0,cy=0,radius=2,a=0,b=1,c=-1),
"permutation":dict(n=4,r=3),
"combination":dict(n=5,r=3),
"binomial_coefficients":dict(n=3),
"total_probability":dict(weights=[3,2],successes=[2,1],total=5,trials=4),
"bayes_posterior":dict(weights=[1,3],likelihoods=[3,1],total=4,trials=4,target=0),
"discrete_moments":dict(values=[0,2],weights=[1,1],total=2),
}
INVALID={
"subset":dict(universe=[1,2,3],left=[4],right=[1,2,3]),
"complement":dict(universe=[0,1],members=[2]),
"sufficient":dict(p=[1,0],q=[1]),
"equivalent":dict(p=[1,0],q=[2,0]),
"neg_exists":dict(truth=[0,2,0]),
"quadratic_inequality":dict(a=0,b=-5,c=6,points=[0,1]),
"change_base":dict(base=1,p=3,q=2),
"unit_identity":dict(cos_num=3,sin_num=4,den=0),
"bisection":dict(lo=0,hi=1,square=2),
"parallel_nonzero":dict(left=[0,0],right=[1,2]),
"perpendicular_nonzero":dict(left=[0,0],right=[1,2]),
"ssa_acute":dict(a=5,b=8,sin_num=1,sin_den=0),
"induction_sum":dict(n=0),
"quadratic_derivative":dict(a=1,b=0,c=0,x=3,h=0),
"fermat_quadratic":dict(a=0,center=0,shift=0),
"plane_distance_squared":dict(point=[1,2,4],plane_point=[0,0,1],normal=[0,0,0]),
"line_slope":dict(p=[1,1],q=[1,1]),
"circle_line":dict(cx=0,cy=0,radius=2,a=0,b=0,c=-1),
"permutation":dict(n=3,r=4),
"combination":dict(n=3,r=-1),
"binomial_coefficients":dict(n=-1),
"total_probability":dict(weights=[3,3],successes=[2,1],total=5,trials=4),
"bayes_posterior":dict(weights=[1,3],likelihoods=[0,0],total=4,trials=4,target=0),
"discrete_moments":dict(values=[0,2],weights=[1,1],total=3),
}
EXPECTED={
"subset":"true","complement":"0,2","sufficient":"true","equivalent":"true",
"neg_exists":"true","quadratic_inequality":"2,3","change_base":"3/2",
"unit_identity":"true","bisection":"1|3/2|1/2","parallel_nonzero":"true",
"perpendicular_nonzero":"true","ssa_acute":"TWO","induction_sum":"55",
"quadratic_derivative":"6|7","fermat_quadratic":"MINIMUM|0",
"plane_distance_squared":"9","line_slope":"2","circle_line":"TWO",
"permutation":"24","combination":"10","binomial_coefficients":"1,3,3,1",
"total_probability":"2/5","bayes_posterior":"1/2","discrete_moments":"1|1",
}
