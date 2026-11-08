"""Bounded, exact INSTANCE witnesses for eight scoped elective manuscripts.
No symbolic generalization, teacher approval or student freeform proof verification.
"""
from __future__ import annotations
from fractions import Fraction
from typing import Any

FIELDS={
 "limit_ratio":("a0","a1","b0","b1","n"),
 "project3":("ux","uy","uz","vx","vy","vz"),
 "orthogonal_diag3":("sx","sy","sz","x1","x2","x3","y1","y2","y3"),
 "lines3":("px","py","pz","qx","qy","qz","ux","uy","uz","vx","vy","vz"),
 "weighted_means":("x1","x2","w1","w2"),
 "fixed_growth":("p0","r_num","r_den","n"),
 "golden_integer_residual":("a","b"),
 "sphere_axes":("r","px","py","pz","qx","qy","qz"),
}
VALID={
 "limit_ratio":{"a0":2,"a1":1,"b0":1,"b1":1,"n":2},
 "project3":{"ux":1,"uy":0,"uz":0,"vx":3,"vy":4,"vz":0},
 "orthogonal_diag3":{"sx":-1,"sy":1,"sz":-1,"x1":1,"x2":2,"x3":3,"y1":0,"y2":0,"y3":0},
 "lines3":{"px":0,"py":0,"pz":0,"qx":0,"qy":0,"qz":1,"ux":1,"uy":0,"uz":0,"vx":0,"vy":1,"vz":0},
 "weighted_means":{"x1":20,"x2":60,"w1":1,"w2":1},
 "fixed_growth":{"p0":1000,"r_num":-1,"r_den":10,"n":3},
 "golden_integer_residual":{"a":5,"b":3},
 "sphere_axes":{"r":1,"px":1,"py":0,"pz":0,"qx":0,"qy":1,"qz":0},
}
INVALID={
 "limit_ratio":dict(VALID["limit_ratio"],b0=0,b1=0),
 "project3":dict(VALID["project3"],ux=0,uy=0,uz=0),
 "orthogonal_diag3":dict(VALID["orthogonal_diag3"],sx=2),
 "lines3":dict(VALID["lines3"],ux=0,uy=0,uz=0),
 "weighted_means":dict(VALID["weighted_means"],x1=0),
 "fixed_growth":dict(VALID["fixed_growth"],r_num=-10,r_den=10),
 "golden_integer_residual":dict(VALID["golden_integer_residual"],b=0),
 "sphere_axes":dict(VALID["sphere_axes"],px=0,py=0,pz=0),
}

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def diff(a,b):return tuple(x-y for x,y in zip(a,b))
def compute(op:str, p:dict[str,int])->str:
 if op=="limit_ratio":
    if p["n"]<1 or p["b0"]==0 or p["b0"]*p["n"]+p["b1"]==0:raise ValueError("unsafe denominator")
    return str(Fraction(p["a0"]*p["n"]+p["a1"],p["b0"]*p["n"]+p["b1"]))
 if op=="project3":
    u=(p["ux"],p["uy"],p["uz"]);v=(p["vx"],p["vy"],p["vz"])
    if dot(u,u)==0:raise ValueError("projection direction zero")
    k=Fraction(dot(u,v),dot(u,u))
    return ",".join(map(str,(k*x for x in u)))
 if op=="orthogonal_diag3":
    signs=(p["sx"],p["sy"],p["sz"])
    if any(abs(x)!=1 for x in signs):raise ValueError("not orthogonal")
    dist=tuple(p[f"x{i}"]-p[f"y{i}"] for i in (1,2,3))
    before=dot(dist,dist);after=sum((sg*x)**2 for sg,x in zip(signs,dist))
    if before!=after:raise ValueError("not an isometry")
    return str(before)
 if op=="lines3":
    p0=tuple(p[f"p{x}"] for x in "xyz");q0=tuple(p[f"q{x}"] for x in "xyz")
    u=tuple(p[f"u{x}"] for x in "xyz");v=tuple(p[f"v{x}"] for x in "xyz")
    if dot(u,u)==0 or dot(v,v)==0:raise ValueError("zero line direction")
    n=cross(u,v);w=diff(q0,p0)
    if dot(n,n):return "NONPARALLEL:"+str(Fraction(dot(w,n)**2,dot(n,n)))
    return "PARALLEL:"+str(Fraction(dot(cross(w,u),cross(w,u)),dot(u,u)))
 if op=="weighted_means":
    x,y,w,z=p["x1"],p["x2"],p["w1"],p["w2"]
    if min(x,y)<=0 or min(w,z)<0 or w+z==0:raise ValueError("positive weighted harmonic domain")
    A=Fraction(w*x+z*y,w+z)
    H=Fraction(w+z,1)/(Fraction(w,x)+Fraction(z,y))
    return str(A)+"|"+str(H)
 if op=="fixed_growth":
    rden=p["r_den"];n=p["n"]
    if p["p0"]<=0 or rden<=0 or n<0 or n>12:raise ValueError("growth scope")
    factor=Fraction(rden+p["r_num"],rden)
    if factor<=0:raise ValueError("growth factor <=0")
    return str(p["p0"]*factor**n)
 if op=="golden_integer_residual":
    a,b=p["a"],p["b"]
    if a<=b or b<=0:raise ValueError("positive ordered segments required")
    return str(a*a-a*b-b*b)
 if op=="sphere_axes":
    r=p["r"];a=tuple(p["p"+x] for x in "xyz");b=tuple(p["q"+x] for x in "xyz")
    if r<=0 or dot(a,a)!=r*r or dot(b,b)!=r*r:raise ValueError("not on a sphere")
    cos=Fraction(dot(a,b),r*r)
    if cos==1:return "COINCIDENT:0"
    if cos==0:return "RIGHT_ANGLE:"+str(r)+"*pi/2"
    if cos==-1:return "ANTIPODAL:"+str(r)+"*pi"
    return "UNSUPPORTED_GENERAL_ANGLE:cos="+str(cos)
 raise ValueError("unknown operator")

def witness(op:str,params:Any)->dict[str,str]:
 if op not in FIELDS:return {"status":"UNSUPPORTED","reason":"unknown bounded operator"}
 if not isinstance(params,dict) or set(params)!=set(FIELDS[op]):
    return {"status":"CONDITIONS_NOT_ESTABLISHED","reason":"missing or extra parameter"}
 if any(type(params[k]) is not int or abs(params[k])>100000 for k in FIELDS[op]):
    return {"status":"CONDITIONS_NOT_ESTABLISHED","reason":"bounded integer inputs only"}
 try:answer=compute(op,params)
 except (ZeroDivisionError,ValueError,OverflowError) as exc:
    return {"status":"CONDITIONS_NOT_ESTABLISHED","reason":str(exc)}
 if answer.startswith("UNSUPPORTED_GENERAL_ANGLE"):
    return {"status":"UNSUPPORTED","reason":"exact arbitrary arccos not implemented"}
 return dict(status="FINITE_EXACT_CASE_ONLY",exact_value=answer,
             teacher_approved="false",general_theorem_certified="false",
             student_freeform_step_verified="false")
