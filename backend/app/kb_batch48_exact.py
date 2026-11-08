"""Batch48 finite exact witnesses. Output NEVER certifies a general theorem or teacher review."""
from __future__ import annotations
from fractions import Fraction
from math import comb, factorial
from typing import Any

OPS=(
 "space_point_line_distance_sq","line_acute_cos_sq","two_point_slope",
 "general_line_relation","point_slope_evaluate","vertical_general_line",
 "linear_line_intersection","point_line_distance_sq","circle_membership",
 "circle_general_radius_sq","two_circle_position","ellipse_focal_sum",
 "ellipse_focus_sq","parabola_focus_directrix","hyperbola_focal_difference",
 "conic_type_and_axis","overlap_union_count","branch_count",
 "arrangements_combinations","finite_conditional_probability",
)
SAMPLES={
 "space_point_line_distance_sq":({"q":[1,2,0],"p":[0,0,0],"u":[1,0,0]},"4",{"q":[1,2,0],"p":[0,0,0],"u":[0,0,0]}),
 "line_acute_cos_sq":({"u":[1,0,0],"v":[-1,1,0]},"1/2",{"u":[0,0,0],"v":[-1,1,0]}),
 "two_point_slope":({"x1":1,"y1":2,"x2":3,"y2":8},"3",{"x1":2,"y1":1,"x2":2,"y2":7}),
 "general_line_relation":({"A":1,"B":2,"D":2,"E":-1},"PERPENDICULAR",{"A":0,"B":0,"D":2,"E":-1}),
 "point_slope_evaluate":({"x0":2,"y0":5,"kn":-3,"kd":1,"x":4},"-1",{"x0":2,"y0":5,"kn":-3,"kd":0,"x":4}),
 "vertical_general_line":({"A":1,"B":0,"C":-3},"VERTICAL:x=3",{"A":0,"B":0,"C":5}),
 "linear_line_intersection":({"A":1,"B":1,"C":3,"D":1,"E":-1,"F":1},"(2,1)",{"A":0,"B":0,"C":3,"D":1,"E":-1,"F":1}),
 "point_line_distance_sq":({"A":3,"B":4,"C":-12,"x":1,"y":1},"1",{"A":0,"B":0,"C":1,"x":1,"y":1}),
 "circle_membership":({"a":1,"b":-2,"r":3,"x":4,"y":-2},"ON_CIRCLE",{"a":1,"b":-2,"r":0,"x":1,"y":-2}),
 "circle_general_radius_sq":({"D":-4,"E":6,"F":-12},"25",{"D":0,"E":0,"F":1}),
 "two_circle_position":({"x1":0,"y1":0,"r1":2,"x2":5,"y2":0,"r2":3},"EXTERNAL_TANGENT",{"x1":0,"y1":0,"r1":0,"x2":5,"y2":0,"r2":3}),
 "ellipse_focal_sum":({"a":5,"c":3},"16",{"a":3,"c":3}),
 "ellipse_focus_sq":({"a":5,"b":4,"axis":0},"9",{"a":3,"b":4,"axis":0}),
 "parabola_focus_directrix":({"p":4,"x":2,"y":4},"ON_PARABOLA",{"p":0,"x":2,"y":4}),
 "hyperbola_focal_difference":({"a":3,"c":5},"16",{"a":5,"c":5}),
 "conic_type_and_axis":({"sx":1,"sy":1,"aa":25,"bb":16},"ELLIPSE_X_MAJOR",{"sx":0,"sy":1,"aa":25,"bb":16}),
 "overlap_union_count":({"a":3,"b":2,"overlap":1},"4",{"a":3,"b":2,"overlap":3}),
 "branch_count":({"options":[2,1,1]},"4",{"options":[2,-1,1]}),
 "arrangements_combinations":({"n":5,"k":3,"ordered":1},"60",{"n":5,"k":6,"ordered":1}),
 "finite_conditional_probability":({"N":6,"B":3,"intersection":2},"2/3",{"N":6,"B":0,"intersection":0}),
}
assert tuple(SAMPLES)==OPS

def require(v:bool)->None:
    if not v:
        raise ValueError("mathematical conditions not established")
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def fmt(x:Any)->str:return str(x)
def calc(op:str,d:dict)->str:
    if op=="space_point_line_distance_sq":
        v=[a-b for a,b in zip(d["q"],d["p"])];u=d["u"];n=dot(u,u)
        require(n>0)
        return fmt(Fraction(dot(v,v))-Fraction(dot(v,u)**2,n))
    if op=="line_acute_cos_sq":
        u=d["u"];v=d["v"];n=dot(u,u)*dot(v,v)
        require(n>0)
        return fmt(Fraction(dot(u,v)**2,n))
    if op=="two_point_slope":
        dx=d["x2"]-d["x1"];require(dx!=0)
        return fmt(Fraction(d["y2"]-d["y1"],dx))
    if op=="general_line_relation":
        a,b,c,e=(d[k] for k in ("A","B","D","E"))
        require((a,b)!=(0,0) and (c,e)!=(0,0))
        if a*e-b*c==0:return "PARALLEL_DIRECTIONS_ONLY"
        if a*c+b*e==0:return "PERPENDICULAR"
        return "NEITHER"
    if op=="point_slope_evaluate":
        require(d["kd"]!=0)
        return fmt(Fraction(d["y0"])+Fraction(d["kn"],d["kd"])*(d["x"]-d["x0"]))
    if op=="vertical_general_line":
        a,b,c=d["A"],d["B"],d["C"]
        require((a,b)!=(0,0))
        return "VERTICAL:x="+fmt(Fraction(-c,a)) if b==0 else "NONVERTICAL"
    if op=="linear_line_intersection":
        a,b,c,e,f,g=(d[k] for k in ("A","B","C","D","E","F"))
        require((a,b)!=(0,0) and (e,f)!=(0,0))
        delta=a*f-b*e
        if delta!=0:
            x=Fraction(c*f-b*g,delta);y=Fraction(a*g-c*e,delta)
            return f"({x},{y})"
        # Rank / consistency conditions: first normal is nonzero.
        return "COINCIDENT" if a*g==e*c and b*g==f*c else "PARALLEL_DISTINCT"
    if op=="point_line_distance_sq":
        a,b,c,x,y=(d[k] for k in ("A","B","C","x","y"))
        require(a*a+b*b>0)
        return fmt(Fraction((a*x+b*y+c)**2,a*a+b*b))
    if op=="circle_membership":
        a,b,r,x,y=(d[k] for k in ("a","b","r","x","y"));require(r>0)
        return "ON_CIRCLE" if (x-a)**2+(y-b)**2==r*r else "NOT_ON_CIRCLE"
    if op=="circle_general_radius_sq":
        a,b,c=d["D"],d["E"],d["F"]
        r2=Fraction(a*a+b*b,4)-c;require(r2>0);return fmt(r2)
    if op=="two_circle_position":
        x1,y1,r1,x2,y2,r2=(d[k] for k in ("x1","y1","r1","x2","y2","r2"))
        require(r1>0 and r2>0)
        d2=(x1-x2)**2+(y1-y2)**2
        if d2==0 and r1==r2:return "COINCIDENT"
        if d2>(r1+r2)**2:return "EXTERNAL_DISJOINT"
        if d2==(r1+r2)**2:return "EXTERNAL_TANGENT"
        if d2<(r1-r2)**2:return "INTERNAL_DISJOINT"
        if d2==(r1-r2)**2:return "INTERNAL_TANGENT"
        return "TWO_INTERSECTIONS"
    if op=="ellipse_focal_sum":
        a,c=d["a"],d["c"];require(a>c>0);return fmt(a*a-c*c)
    if op=="ellipse_focus_sq":
        a,b=d["a"],d["b"];require(a>b>0 and d["axis"] in (0,1));return fmt(a*a-b*b)
    if op=="parabola_focus_directrix":
        p,x,y=d["p"],d["x"],d["y"];require(p!=0)
        return "ON_PARABOLA" if y*y==2*p*x else "NOT_ON_PARABOLA"
    if op=="hyperbola_focal_difference":
        a,c=d["a"],d["c"];require(c>a>0);return fmt(c*c-a*a)
    if op=="conic_type_and_axis":
        sx,sy,aa,bb=(d[k] for k in ("sx","sy","aa","bb"))
        require(sx==1 and sy in (-1,1) and aa>0 and bb>0)
        if sy==-1:return "HYPERBOLA_X_REAL"
        return "CIRCLE" if aa==bb else ("ELLIPSE_X_MAJOR" if aa>bb else "ELLIPSE_Y_MAJOR")
    if op=="overlap_union_count":
        a,b,v=d["a"],d["b"],d["overlap"]
        require(a>=0 and b>=0 and 0<=v<=min(a,b))
        return fmt(a+b-v)
    if op=="branch_count":
        seq=d["options"];require(len(seq)>0 and all(x>=0 for x in seq))
        return fmt(sum(seq))
    if op=="arrangements_combinations":
        n,k,ordered=d["n"],d["k"],d["ordered"]
        require(0<=k<=n<=20 and ordered in (0,1))
        return fmt(factorial(n)//factorial(n-k) if ordered else comb(n,k))
    if op=="finite_conditional_probability":
        n,b,i=d["N"],d["B"],d["intersection"]
        require(n>0 and 0<b<=n and 0<=i<=b)
        return fmt(Fraction(i,b))
    raise ValueError("unsupported operation")

def witness(op,params):
    out=dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,
      general_theorem_certified=False,student_freeform_step_verified=False,
      teacher_approved=False,student_publishable=False)
    if type(op) is not str or op not in SAMPLES:
        out["status"]="UNSUPPORTED";return out
    shape=SAMPLES[op][0]
    if type(params) is not dict or set(params)!=set(shape):return out
    for k,v in params.items():
        if type(v) is int:
            if abs(v)>100:return out
        elif type(v) is list:
            if len(v)>20 or any(type(i) is not int or abs(i)>100 for i in v):return out
            if k in ("p","q","u","v") and len(v)!=3:return out
        else:return out
    try:
        out["exact_value"]=calc(op,params);out["status"]="FINITE_EXACT_CASE_ONLY"
    except (ValueError,TypeError,ZeroDivisionError,OverflowError,IndexError):
        pass
    return out
