"""Batch42 exact bounded math witnesses for 20 original review topics.
FINITELY MANY CONTROLLED INPUTS ONLY. Not a general proof or learner solution grader.
"""
from __future__ import annotations
from fractions import Fraction

KEYS={
"set_membership":("universe","members","target"),
"set_union":("universe","left","right"),
"set_intersection":("universe","left","right"),
"finite_forall":("values","threshold"),
"finite_exists_square":("values","square"),
"linear_zero":("slope","intercept","candidate"),
"quadratic_sign":("a","b","c","x"),
"exponential_order":("numerator","denominator","x","y"),
"unit_circle_quadrant":("quarter_turn",),
"tan_quadrant":("quarter_turn",),
"sequence_term":("a1","d","n"),
"arithmetic_differences":("terms",),
"geometric_ratios":("terms",),
"constant_derivative":("constant","point"),
"identity_derivative":("point",),
"quadratic_finite_max":("points","center"),
"spatial_vector_sum":("left","right"),
"plane_normal_valid":("normal","direction1","direction2"),
"conditional_finite_uniform":("total","event_a","event_b"),
"finite_probability_mass":("weights","denominator"),
}
def _integer(v):
    return type(v) is int and -1000 <= v <= 1000

def _list(v, *, lo=1, hi=15):
    return type(v) is list and lo <= len(v) <= hi and all(_integer(i) for i in v)

def _distinct(v):
    return len(set(v))==len(v)

def _format(v):
    if type(v) is bool:return str(v).lower()
    if type(v) is Fraction:return str(v)
    if type(v) is tuple:return ",".join(str(x) for x in v)
    return str(v)

def _calc(op, a):
    if op in ("set_membership","set_union","set_intersection"):
        u=a["universe"]; left=a["members"] if op=="set_membership" else a["left"]
        if not _list(u) or not _distinct(u) or not _list(left,lo=0) or not set(left)<=set(u) or not _distinct(left):
            raise ValueError("Finite distinct universe and valid subset needed")
        if op=="set_membership":
            if not _integer(a["target"]) or a["target"] not in u:raise ValueError("Target outside universe")
            return a["target"] in left
        right=a["right"]
        if not _list(right,lo=0) or not _distinct(right) or not set(right)<=set(u):
            raise ValueError("Invalid right subset")
        result=set(left)|set(right) if op=="set_union" else set(left)&set(right)
        return tuple(sorted(result))
    if op in ("finite_forall","finite_exists_square"):
        vals=a["values"]
        if not _list(vals) or not _distinct(vals):raise ValueError("Finite distinct test universe required")
        if op=="finite_forall":return all(i>=a["threshold"] for i in vals)
        if a["square"]<0:raise ValueError("Square target must be nonnegative")
        return any(i*i==a["square"] for i in vals)
    if op=="linear_zero":
        if a["slope"]==0:raise ValueError("Linear root formula requires nonzero slope")
        return Fraction(-a["intercept"],a["slope"])==a["candidate"]
    if op=="quadratic_sign":
        if a["a"]==0:raise ValueError("Quadratic leading coefficient cannot vanish")
        z=a["a"]*a["x"]*a["x"]+a["b"]*a["x"]+a["c"]
        return "POSITIVE" if z>0 else "NEGATIVE" if z<0 else "ZERO"
    if op=="exponential_order":
        p,q=a["numerator"],a["denominator"]
        if p<=0 or q<=0 or p==q or abs(a["x"])>8 or abs(a["y"])>8:
            raise ValueError("Positive nonunit rational base and bounded powers")
        base=Fraction(p,q)
        x,y=base**a["x"],base**a["y"]
        return "LESS" if x<y else "GREATER" if x>y else "EQUAL"
    if op in ("unit_circle_quadrant","tan_quadrant"):
        k=a["quarter_turn"]
        if k not in (0,1,2,3):raise ValueError("Exact table only for quarter turns")
        cos,sin=((1,0),(0,1),(-1,0),(0,-1))[k]
        if op=="tan_quadrant":
            if cos==0:raise ValueError("Tangent undefined at odd quarter turn")
            return Fraction(sin,cos)
        return f"{cos}|{sin}"
    if op=="sequence_term":
        if not 1<=a["n"]<=100:raise ValueError("Positive 1-indexed sequence term required")
        return a["a1"]+(a["n"]-1)*a["d"]
    if op=="arithmetic_differences":
        t=a["terms"]
        if not _list(t,lo=2,hi=12):raise ValueError("At least two valid consecutive terms")
        gaps=[b-c for c,b in zip(t,t[1:])]
        return str(gaps[0]) if len(set(gaps))==1 else "NOT_ARITHMETIC"
    if op=="geometric_ratios":
        t=a["terms"]
        if not _list(t,lo=2,hi=12) or any(v==0 for v in t):
            raise ValueError("All terms nonzero in stated geometric convention")
        ratios=[Fraction(b,c) for c,b in zip(t,t[1:])]
        return str(ratios[0]) if len(set(ratios))==1 and ratios[0]!=0 else "NOT_GEOMETRIC"
    if op=="constant_derivative":return 0
    if op=="identity_derivative":return 1
    if op=="quadratic_finite_max":
        xs=a["points"]
        if not _list(xs) or not _distinct(xs):raise ValueError("Explicit finite distinct domain required")
        best=max(xs,key=lambda x: (-(x-a["center"])**2,-x))
        return f"{best}|{-((best-a['center'])**2)}"
    if op=="spatial_vector_sum":
        left,right=a["left"],a["right"]
        if not _list(left,lo=3,hi=3) or not _list(right,lo=3,hi=3):
            raise ValueError("Three integer vector components per direction")
        return tuple(x+y for x,y in zip(left,right))
    if op=="plane_normal_valid":
        n,u,v=[a[k] for k in ("normal","direction1","direction2")]
        if not all(_list(w,lo=3,hi=3) for w in (n,u,v)) or not any(n):
            raise ValueError("Nonzero normal and 3D input vectors required")
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        if not any(cross):raise ValueError("Two directions must be independent")
        return sum(x*y for x,y in zip(n,u))==sum(x*y for x,y in zip(n,v))==0
    if op=="conditional_finite_uniform":
        n=a["total"];A=a["event_a"];B=a["event_b"]
        if not 1<=n<=100 or not _list(A,lo=0) or not _list(B) or not _distinct(A) or not _distinct(B):
            raise ValueError("Nonempty conditioning event and finite space required")
        if not set(A)<=set(range(1,n+1)) or not set(B)<=set(range(1,n+1)):
            raise ValueError("Invalid finite uniform sample event")
        return Fraction(len(set(A)&set(B)),len(B))
    if op=="finite_probability_mass":
        ws=a["weights"];d=a["denominator"]
        if not _list(ws) or d<=0 or any(w<0 for w in ws):
            raise ValueError("Nonnegative weights and positive denominator needed")
        return "VALID" if sum(ws)==d else "NOT_NORMALIZED"
    raise KeyError("Unknown operator")

def witness(operator:str, input_values:object):
    """A bounded exact calculation; unsupported / unchecked assumptions fail closed."""
    empty={"general_theorem_certified":False,"student_freeform_step_verified":False,
           "teacher_approved":False,"student_publishable":False}
    if operator not in KEYS:
        return dict(status="UNSUPPORTED",exact_value=None,**empty)
    if type(input_values) is not dict or set(input_values)!=set(KEYS[operator]):
        return dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,**empty)
    if not all((_integer(v) if type(v) is not list else _list(v,lo=0)) for v in input_values.values()):
        return dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,**empty)
    try:
        value=_calc(operator,input_values)
    except (ValueError,ZeroDivisionError,KeyError,TypeError):
        return dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,**empty)
    return dict(status="FINITE_EXACT_CASE_ONLY",exact_value=_format(value),**empty)

VALID={
"set_membership":dict(universe=[0,1,2],members=[1],target=1),
"set_union":dict(universe=[1,2,3],left=[1,2],right=[2,3]),
"set_intersection":dict(universe=[1,2,3],left=[1,2],right=[2,3]),
"finite_forall":dict(values=[0,1,2],threshold=0),
"finite_exists_square":dict(values=[0,1,2,3],square=9),
"linear_zero":dict(slope=2,intercept=-4,candidate=2),
"quadratic_sign":dict(a=1,b=0,c=-4,x=3),
"exponential_order":dict(numerator=2,denominator=1,x=1,y=3),
"unit_circle_quadrant":dict(quarter_turn=1),
"tan_quadrant":dict(quarter_turn=2),
"sequence_term":dict(a1=3,d=2,n=4),
"arithmetic_differences":dict(terms=[2,5,8]),
"geometric_ratios":dict(terms=[2,6,18]),
"constant_derivative":dict(constant=7,point=2),
"identity_derivative":dict(point=5),
"quadratic_finite_max":dict(points=[0,1,2],center=1),
"spatial_vector_sum":dict(left=[1,2,3],right=[3,-1,0]),
"plane_normal_valid":dict(normal=[0,0,1],direction1=[1,0,0],direction2=[0,1,0]),
"conditional_finite_uniform":dict(total=6,event_a=[4,5,6],event_b=[2,4,6]),
"finite_probability_mass":dict(weights=[1,3],denominator=4),
}
INVALID={
"set_membership":dict(universe=[0,1,2],members=[1],target=3),
"set_union":dict(universe=[1,2,3],left=[1,2],right=[2,4]),
"set_intersection":dict(universe=[1,2,3],left=[1,2],right=[2,4]),
"finite_forall":dict(values=[0,0],threshold=0),
"finite_exists_square":dict(values=[0,1,2],square=-1),
"linear_zero":dict(slope=0,intercept=-4,candidate=2),
"quadratic_sign":dict(a=0,b=0,c=-4,x=3),
"exponential_order":dict(numerator=1,denominator=0,x=1,y=3),
"unit_circle_quadrant":dict(quarter_turn=4),
"tan_quadrant":dict(quarter_turn=1),
"sequence_term":dict(a1=3,d=2,n=0),
"arithmetic_differences":dict(terms=[2]),
"geometric_ratios":dict(terms=[0,2]),
"constant_derivative":dict(constant=7,point=2000),
"identity_derivative":dict(point=True),
"quadratic_finite_max":dict(points=[],center=1),
"spatial_vector_sum":dict(left=[1,2],right=[3,-1,0]),
"plane_normal_valid":dict(normal=[0,0,0],direction1=[1,0,0],direction2=[0,1,0]),
"conditional_finite_uniform":dict(total=6,event_a=[4,5,6],event_b=[]),
"finite_probability_mass":dict(weights=[1,3],denominator=0),
}
