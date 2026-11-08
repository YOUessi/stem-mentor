"""Finite, exact, bounded witness checks. These DO NOT prove general theorems.

Only explicit dictionary payloads accepted; never eval user expressions or mark student
free-text steps verified. Negative fixtures exercise missing mathematical premises.
"""
from fractions import Fraction
from math import comb

KEYS={
 "unit_circle_period":("angle","turns"),
 "sine_parameters":("amplitude","omega","phase","center"),
 "cos_difference":("alpha","beta"),
 "sin_sum":("alpha","beta"),
 "tan_identity":("angle",),
 "continuous_sign_bracket":("coefficients","lo","hi"),
 "bisection_error":("coefficients","lo","hi","steps"),
 "vector_basis":("u","v"),
 "vector_inner":("u","v"),
 "complex_division":("ar","ai","br","bi"),
 "solid_classification":("base","apex","geometry"),
 "solid_volume":("base","height","shape"),
 "three_point_plane":("a","b","c"),
 "line_in_plane":("a","b","z"),
 "plane_intersection":("axis1","axis2"),
 "sample_space_coins":("flips","two_outcomes_each","all_sequences_possible"),
 "event_subset":("universe","event"),
 "event_union_intersection":("universe","a","b"),
 "mutually_exclusive":("universe","a","b"),
 "classical_probability":("outcomes","favorable","equally_likely"),
 "population_sample":("population","sample"),
 "simple_random_sample":("population","sample","uniform"),
 "stratified_proportion":("first","second","sample"),
 "descriptive_variance":("values",),
}

ANGLE={0:(1,0),90:(0,1),180:(-1,0),270:(0,-1)}
def _integer(x):return type(x) is int and -100<=x<=100
def _vector(x,n):
    if type(x) is not list or len(x)!=n or not all(_integer(i) for i in x):
        raise ValueError("bounded integer coordinates required")
    return x
def _subset(u,s):
    U,S=_vector(u,len(u)),_vector(s,len(s))
    if len(U)>32 or len(U)!=len(set(U)) or len(S)!=len(set(S)) or not set(S)<=set(U):
        raise ValueError("unique finite event and matching universe")
    return set(S)
def _signed_angle(x):
    if x%90: raise ValueError("exact right-angle witness only")
    return ANGLE[x%360]
def _poly(cs,x):
    return sum(v*(x**j) for j,v in enumerate(cs))
def _compute(op,p):
    if op=="unit_circle_period":
        if not -5<=p["turns"]<=5:raise ValueError("bounded rotations")
        return _signed_angle(p["angle"]+360*p["turns"])
    if op=="sine_parameters":
        a,w,phi,c=[p[k] for k in KEYS[op]]
        if a<=0 or w<=0:raise ValueError("positive amplitude and angular frequency")
        return f"AMP:{a}|PERIOD:{Fraction(2,w)}pi|RANGE:{c-a},{c+a}|SHIFT:{Fraction(-phi,w)}"
    if op=="cos_difference":
        a,b=[p[k] for k in KEYS[op]]
        ax,ay=_signed_angle(a);bx,by=_signed_angle(b)
        return ax*bx+ay*by
    if op=="sin_sum":
        ax,ay=_signed_angle(p["alpha"]);bx,by=_signed_angle(p["beta"])
        return ay*bx+ax*by
    if op=="tan_identity":
        x,y=_signed_angle(p["angle"])
        if x==0:raise ValueError("cos angle must not vanish")
        return Fraction(x*x+y*y,x*x)
    if op=="continuous_sign_bracket":
        cs=_vector(p["coefficients"],len(p["coefficients"]))
        a,b=p["lo"],p["hi"]
        if not 2<=len(cs)<=5 or a>=b or _poly(cs,a)*_poly(cs,b)>=0:
            raise ValueError("explicit continuous polynomial and strict opposite endpoints")
        return "ROOT_EXISTS_UNIQUENESS_UNDETERMINED"
    if op=="bisection_error":
        a,b,n=p["lo"],p["hi"],p["steps"]
        cs=_vector(p["coefficients"],len(p["coefficients"]))
        if a>=b or not 0<=n<=20 or not 2<=len(cs)<=5 or _poly(cs,a)*_poly(cs,b)>=0:
            raise ValueError("continuity and strict opposite sign bracket required")
        return Fraction(b-a,2**(n+1))
    if op=="vector_basis":
        (a,b),(c,d)=_vector(p["u"],2),_vector(p["v"],2)
        det=a*d-b*c
        if det==0:raise ValueError("basis must be linearly independent")
        return det
    if op=="vector_inner":
        u,v=_vector(p["u"],2),_vector(p["v"],2)
        return sum(a*b for a,b in zip(u,v))
    if op=="complex_division":
        a,b,c,d=[p[k] for k in KEYS[op]]
        z=c*c+d*d
        if not z:raise ValueError("complex denominator zero")
        return (Fraction(a*c+b*d,z),Fraction(b*c-a*d,z))
    if op=="solid_classification":
        base,apex,geometry=p["base"],p["apex"],p["geometry"]
        if (type(base) is not str or base not in ("circle","polygon") or
            type(apex) is not bool or type(geometry) is not str or
            geometry!=("convergent" if apex else "parallel")):
            raise ValueError("base, apex and parallel/convergent side geometry required")
        return {("circle",False):"CYLINDER",("circle",True):"CONE",
                ("polygon",False):"PRISM",("polygon",True):"PYRAMID"}[(base,apex)]
    if op=="solid_volume":
        base,high,kind=p["base"],p["height"],p["shape"]
        if base<=0 or high<=0 or kind not in ("prism","pyramid"):
            raise ValueError("positive base area and perpendicular height")
        return Fraction(base*high,3 if kind=="pyramid" else 1)
    if op=="three_point_plane":
        a,b,c=[_vector(p[k],3) for k in ("a","b","c")]
        u=[j-i for i,j in zip(a,b)];v=[j-i for i,j in zip(a,c)]
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        if cross==(0,0,0):raise ValueError("three points must be noncollinear")
        return cross
    if op=="line_in_plane":
        a,b=_vector(p["a"],3),_vector(p["b"],3)
        if a==b or a[2]!=p["z"] or b[2]!=p["z"]:
            raise ValueError("distinct points in z=constant plane")
        return "CONTAINED"
    if op=="plane_intersection":
        a,b=p["axis1"],p["axis2"]
        if type(a) is not str or type(b) is not str or a not in "xyz" or b not in "xyz" or len(a)!=1 or len(b)!=1 or a==b:
            raise ValueError("two independent coordinate-plane normals")
        return "LINE"
    if op=="sample_space_coins":
        n=p["flips"]
        if (type(p["two_outcomes_each"]) is not bool or p["two_outcomes_each"] is not True or
            type(p["all_sequences_possible"]) is not bool or p["all_sequences_possible"] is not True or
            not 1<=n<=8):
            raise ValueError("n binary recordings require all 2**n sequences possible")
        return 2**n
    if op=="event_subset":
        u,s=p["universe"],p["event"]
        return len(_subset(u,s))
    if op=="event_union_intersection":
        u=p["universe"];a=_subset(u,p["a"]);b=_subset(u,p["b"])
        return (tuple(sorted(a&b)),tuple(sorted(a|b)))
    if op=="mutually_exclusive":
        u=p["universe"];a=_subset(u,p["a"]);b=_subset(u,p["b"])
        return not bool(a&b)
    if op=="classical_probability":
        n,k,e=p["outcomes"],p["favorable"],p["equally_likely"]
        if n<=0 or k<0 or k>n or e!=1:raise ValueError("finite nonempty equiprobable sample space required")
        return Fraction(k,n)
    if op=="population_sample":
        N,n=p["population"],p["sample"]
        if N<=0 or n<1 or n>N:raise ValueError("sample must fit population")
        return f"N:{N}|n:{n}"
    if op=="simple_random_sample":
        N,n=p["population"],p["sample"]
        if type(p["uniform"]) is not bool or p["uniform"] is not True or N<=0 or n<1 or n>N:
            raise ValueError("requires uniform combinations in without-replacement SRS")
        return Fraction(1,comb(N,n))
    if op=="stratified_proportion":
        N1,N2,n=p["first"],p["second"],p["sample"]
        N=N1+N2
        if N1<=0 or N2<=0 or n<1 or n>N:raise ValueError("valid two strata and sample size")
        a,b=Fraction(n*N1,N),Fraction(n*N2,N)
        if a.denominator!=1 or b.denominator!=1:
            raise ValueError("fractional allocations need separately specified rounding")
        return (int(a),int(b))
    if op=="descriptive_variance":
        v=_vector(p["values"],len(p["values"]))
        if not 1<=len(v)<=24:raise ValueError("nonempty bounded numerical sample")
        n=len(v);mean=Fraction(sum(v),n)
        var=sum((Fraction(x)-mean)**2 for x in v)/n
        return (max(v)-min(v),var)
    raise KeyError("unsupported")
def _fmt(v):
    if type(v) is bool:return "true" if v else "false"
    if type(v) is tuple:return ",".join(_fmt(x) for x in v)
    if isinstance(v,Fraction):return str(v)
    return str(v)
def witness(op,payload):
    flags=dict(general_theorem_certified=False,teacher_approved=False,
        student_freeform_step_verified=False,student_publishable=False)
    if type(op) is not str or op not in KEYS:
        return dict(status="UNSUPPORTED",exact_value=None,**flags)
    if type(payload) is not dict or set(payload)!=set(KEYS[op]):
        return dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,**flags)
    for k,v in payload.items():
        angle=(op in ("unit_circle_period","cos_difference","sin_sum","tan_identity") and
               k in ("angle","alpha","beta"))
        if type(v) is int and not (-720<=v<=720 if angle else _integer(v)):break
        if type(v) is bool and (op,k) not in (
            ("solid_classification","apex"),
            ("sample_space_coins","two_outcomes_each"),
            ("sample_space_coins","all_sequences_possible"),
            ("simple_random_sample","uniform")):break
        if type(v) is list and (len(v)>32 or any(type(x) is not int or not _integer(x) for x in v)):break
        if type(v) not in (int,list,str,bool):break
    else:
        try:
            ans=_compute(op,payload)
            return dict(status="FINITE_EXACT_CASE_ONLY",exact_value=_fmt(ans),**flags)
        except (ValueError,ArithmeticError,ZeroDivisionError,TypeError,KeyError,OverflowError):
            pass
    return dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,**flags)

VALID={
 "unit_circle_period":dict(angle=90,turns=1),
 "sine_parameters":dict(amplitude=3,omega=2,phase=0,center=1),
 "cos_difference":dict(alpha=90,beta=0),
 "sin_sum":dict(alpha=0,beta=90),
 "tan_identity":dict(angle=0),
 "continuous_sign_bracket":dict(coefficients=[-1,1,0,1],lo=0,hi=1),
 "bisection_error":dict(coefficients=[-2,0,1],lo=1,hi=2,steps=3),
 "vector_basis":dict(u=[1,0],v=[0,1]),
 "vector_inner":dict(u=[2,-1],v=[3,4]),
 "complex_division":dict(ar=3,ai=1,br=1,bi=-1),
 "solid_classification":dict(base="circle",apex=False,geometry="parallel"),
 "solid_volume":dict(base=12,height=5,shape="pyramid"),
 "three_point_plane":dict(a=[0,0,0],b=[1,0,0],c=[0,1,0]),
 "line_in_plane":dict(a=[0,0,2],b=[1,0,2],z=2),
 "plane_intersection":dict(axis1="x",axis2="y"),
 "sample_space_coins":dict(flips=2,two_outcomes_each=True,all_sequences_possible=True),
 "event_subset":dict(universe=[1,2,3,4,5,6],event=[5,6]),
 "event_union_intersection":dict(universe=[1,2,3,4,5,6],a=[2,4,6],b=[4,5,6]),
 "mutually_exclusive":dict(universe=[1,2,3,4],a=[1],b=[2]),
 "classical_probability":dict(outcomes=6,favorable=2,equally_likely=1),
 "population_sample":dict(population=100,sample=15),
 "simple_random_sample":dict(population=4,sample=2,uniform=True),
 "stratified_proportion":dict(first=30,second=70,sample=20),
 "descriptive_variance":dict(values=[1,3]),
}
INVALID={
 "unit_circle_period":dict(angle=45,turns=1),
 "sine_parameters":dict(amplitude=3,omega=0,phase=0,center=1),
 "cos_difference":dict(alpha=45,beta=0),
 "sin_sum":dict(alpha=0,beta=45),
 "tan_identity":dict(angle=90),
 "continuous_sign_bracket":dict(coefficients=[1,0,1],lo=-1,hi=1),
 "bisection_error":dict(coefficients=[2,0,1],lo=1,hi=2,steps=3),
 "vector_basis":dict(u=[1,0],v=[2,0]),
 "vector_inner":dict(u=[1],v=[3,4]),
 "complex_division":dict(ar=3,ai=1,br=0,bi=0),
 "solid_classification":dict(base="circle",apex=False,geometry="convergent"),
 "solid_volume":dict(base=12,height=0,shape="pyramid"),
 "three_point_plane":dict(a=[0,0,0],b=[1,0,0],c=[2,0,0]),
 "line_in_plane":dict(a=[0,0,2],b=[0,0,2],z=2),
 "plane_intersection":dict(axis1="x",axis2="x"),
 "sample_space_coins":dict(flips=2,two_outcomes_each=False,all_sequences_possible=True),
 "event_subset":dict(universe=[1,2,3],event=[1,4]),
 "event_union_intersection":dict(universe=[1,2,3],a=[1,4],b=[2]),
 "mutually_exclusive":dict(universe=[1,2,3],a=[1,1],b=[2]),
 "classical_probability":dict(outcomes=6,favorable=2,equally_likely=0),
 "population_sample":dict(population=5,sample=6),
 "simple_random_sample":dict(population=4,sample=2,uniform=False),
 "stratified_proportion":dict(first=3,second=3,sample=1),
 "descriptive_variance":dict(values=[]),
}
EXPECTED={
 "unit_circle_period":"0,1","sine_parameters":"AMP:3|PERIOD:1pi|RANGE:-2,4|SHIFT:0",
 "cos_difference":"0","sin_sum":"1","tan_identity":"1",
 "continuous_sign_bracket":"ROOT_EXISTS_UNIQUENESS_UNDETERMINED","bisection_error":"1/16",
 "vector_basis":"1","vector_inner":"2","complex_division":"1,2",
 "solid_classification":"CYLINDER","solid_volume":"20",
 "three_point_plane":"0,0,1","line_in_plane":"CONTAINED",
 "plane_intersection":"LINE","sample_space_coins":"4",
 "event_subset":"2","event_union_intersection":"4,6,2,4,5,6",
 "mutually_exclusive":"true","classical_probability":"1/3",
 "population_sample":"N:100|n:15","simple_random_sample":"1/6",
 "stratified_proportion":"6,14","descriptive_variance":"2,1",
}
