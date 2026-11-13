"""Batch46 bounded exact mathematics. An exact finite computation is NOT a general proof or a student-step certificate."""
from __future__ import annotations
from fractions import Fraction
from math import prod

OPS = (
 "sequence_points", "arithmetic_n", "geometric_n", "positive_exponential_sample",
 "polynomial_derivative_limit", "polynomial_product_derivative", "affine_power_chain",
 "monotonic_grid_only", "quadratic_closed_extrema", "distance_squared_3d",
 "displacement_equality", "vector_chain", "basis_determinant", "unit_basis_norm_sq",
 "vector_linear_combination", "dot_product_3d", "vector_projection",
 "line_direction_span", "line_plane_class", "orthogonality_3d"
)

# All parameters are bounded exact integers; inputs are fixed-shape objects, not expressions.
SAMPLES={
 "sequence_points":({"values":[2,4,6]},"1:2;2:4;3:6",{"values":[]}),
 "arithmetic_n":({"a1":3,"d":-2,"n":5},"-5",{"a1":3,"d":-2,"n":0}),
 "geometric_n":({"a1":2,"q":-2,"n":4},"-16",{"a1":2,"q":-2,"n":0}),
 "positive_exponential_sample":({"a1":3,"q":2,"n":4},"24",{"a1":3,"q":-2,"n":4}),
 "polynomial_derivative_limit":({"coeffs":[0,0,1],"x0":3},"6",{"coeffs":[],"x0":3}),
 "polynomial_product_derivative":({"f":[0,0,1],"g":[1,1],"x0":2},"16",{"f":[0,0,1],"g":[],"x0":2}),
 "affine_power_chain":({"a":3,"b":1,"power":4,"x0":0},"12",{"a":3,"b":1,"power":-1,"x0":0}),
 "monotonic_grid_only":({"coeffs":[0,1,0,1],"lo":-2,"hi":2},"NONNEGATIVE_ON_GRID_ONLY",{"coeffs":[0,-1],"lo":-2,"hi":2}),
 "quadratic_closed_extrema":({"a":1,"b":-2,"c":0,"lo":0,"hi":3},"max=3;min=-1",{"a":0,"b":-2,"c":0,"lo":0,"hi":3}),
 "distance_squared_3d":({"a":[0,0,0],"b":[1,2,2]},"9",{"a":[0,0],"b":[1,2,2]}),
 "displacement_equality":({"a":[0,0,0],"b":[1,2,3],"c":[3,0,0],"d":[4,2,3]},"TRUE",{"a":[0,0,0],"b":[1,2,3],"c":[3,0,0],"d":[4,2]}),
 "vector_chain":({"a":[0,0,0],"b":[1,2,0],"c":[2,2,3]},"2,2,3",{"a":[0,0,0],"b":[1,2,0],"c":[2,3]}),
 "basis_determinant":({"u":[1,0,0],"v":[0,1,0],"w":[0,0,1]},"1",{"u":[1,0,0],"v":[0,1,0],"w":[1,1,0]}),
 "unit_basis_norm_sq":({"u":[2,-1,2]},"9",{"u":[]}),
 "vector_linear_combination":({"u":[1,-2,3],"v":[-1,4,0],"k":3},"2,-2,9",{"u":[1,-2,3],"v":[-1,4],"k":3}),
 "dot_product_3d":({"u":[1,2,-1],"v":[2,0,2]},"0",{"u":[1,2,-1],"v":[2,0]}),
 "vector_projection":({"u":[3,4,0],"v":[2,0,0]},"3,0,0",{"u":[3,4,0],"v":[0,0,0]}),
 "line_direction_span":({"d":[0,1,-1],"scale":-2},"SAME_LINE_DIRECTION_SPAN",{"d":[0,1,-1],"scale":0}),
 "line_plane_class":({"p":[0,0,1],"d":[1,0,0],"n":[0,0,1],"offset":0},"PARALLEL_DISTINCT",{"p":[0,0,1],"d":[0,0,0],"n":[0,0,1],"offset":0}),
 "orthogonality_3d":({"u":[1,2,-1],"v":[2,-1,0]},"TRUE",{"u":[0,0,0],"v":[2,-1,0]}),
}
assert tuple(SAMPLES)==OPS

def safe(v):
    if type(v) is int:
        return -20<=v<=20
    if type(v) is list:
        return 1<=len(v)<=8 and all(type(x) is int and -20<=x<=20 for x in v)
    return False

def dot(u,v):
    return sum(a*b for a,b in zip(u,v))
def vec3(v):
    if len(v)!=3: raise ValueError("not 3d")
def nonzero(v):
    if not any(v): raise ValueError("zero vector")
def poly(cs,x):
    return sum(c*x**i for i,c in enumerate(cs))
def derivative(cs,x):
    return sum(i*c*x**(i-1) for i,c in enumerate(cs) if i)
def fmt_vec(seq):
    return ",".join(str(v) for v in seq)
def det(u,v,w):
    return u[0]*(v[1]*w[2]-v[2]*w[1])-u[1]*(v[0]*w[2]-v[2]*w[0])+u[2]*(v[0]*w[1]-v[1]*w[0])

def calculate(op,p):
    if op=="sequence_points":
        return ";".join(f"{i}:{v}" for i,v in enumerate(p["values"],1))
    if op=="arithmetic_n":
        if not 1<=p["n"]<=20: raise ValueError("invalid n")
        return str(p["a1"]+(p["n"]-1)*p["d"])
    if op=="geometric_n":
        if not 1<=p["n"]<=20: raise ValueError("invalid n")
        return str(p["a1"]*p["q"]**(p["n"]-1))
    if op=="positive_exponential_sample":
        if p["q"]<=0 or p["a1"]<=0 or not 1<=p["n"]<=20: raise ValueError("positive base and amplitude required")
        return str(p["a1"]*p["q"]**(p["n"]-1))
    if op=="polynomial_derivative_limit":
        return str(derivative(p["coeffs"],p["x0"]))
    if op=="polynomial_product_derivative":
        f,g,x=p["f"],p["g"],p["x0"]
        return str(derivative(f,x)*poly(g,x)+poly(f,x)*derivative(g,x))
    if op=="affine_power_chain":
        if not 0<=p["power"]<=8: raise ValueError("polynomial degree")
        return str(p["power"]*p["a"]*(p["a"]*p["x0"]+p["b"])**max(0,p["power"]-1))
    if op=="monotonic_grid_only":
        if not p["lo"]<p["hi"]: raise ValueError("interval")
        if not all(derivative(p["coeffs"],Fraction(p["lo"]*(10-i)+p["hi"]*i,10))>=0 for i in range(11)):
            raise ValueError("derivative negative on checked grid")
        return "NONNEGATIVE_ON_GRID_ONLY"
    if op=="quadratic_closed_extrema":
        if p["a"]==0 or p["lo"]>=p["hi"]: raise ValueError("quadratic or interval degenerate")
        pts=[Fraction(p["lo"]),Fraction(p["hi"])]
        center=Fraction(-p["b"],2*p["a"])
        if pts[0]<=center<=pts[1]: pts.append(center)
        vals=[p["a"]*x*x+p["b"]*x+p["c"] for x in pts]
        return f"max={max(vals)};min={min(vals)}"
    if op=="distance_squared_3d":
        a,b=p["a"],p["b"];vec3(a);vec3(b)
        return str(sum((x-y)**2 for x,y in zip(a,b)))
    if op=="displacement_equality":
        a,b,c,d=(p[k] for k in ("a","b","c","d"))
        for v in (a,b,c,d):vec3(v)
        return "TRUE" if [y-x for x,y in zip(a,b)]==[y-x for x,y in zip(c,d)] else "FALSE"
    if op=="vector_chain":
        a,b,c=(p[k] for k in ("a","b","c"))
        for v in (a,b,c):vec3(v)
        return fmt_vec([z-x for x,y,z in zip(a,b,c)])
    if op=="basis_determinant":
        u,v,w=p["u"],p["v"],p["w"]
        for q in (u,v,w):vec3(q)
        d=det(u,v,w)
        if d==0:raise ValueError("dependent basis")
        return str(d)
    if op=="unit_basis_norm_sq":
        u=p["u"];vec3(u)
        return str(dot(u,u))
    if op=="vector_linear_combination":
        u,v=p["u"],p["v"];vec3(u);vec3(v)
        return fmt_vec([p["k"]*x+y for x,y in zip(u,v)])
    if op=="dot_product_3d":
        u,v=p["u"],p["v"];vec3(u);vec3(v)
        return str(dot(u,v))
    if op=="vector_projection":
        u,v=p["u"],p["v"];vec3(u);vec3(v);nonzero(v)
        return fmt_vec([Fraction(dot(u,v)*x,dot(v,v)) for x in v])
    if op=="line_direction_span":
        d=p["d"];vec3(d);nonzero(d)
        if p["scale"]==0:raise ValueError("scale cannot vanish")
        return "SAME_LINE_DIRECTION_SPAN"
    if op=="line_plane_class":
        d,n=p["d"],p["n"];vec3(d);vec3(n);nonzero(d);nonzero(n);vec3(p["p"])
        slope=dot(d,n)
        return "INTERSECT_ONE_POINT" if slope else ("CONTAINED" if dot(p["p"],n)==p["offset"] else "PARALLEL_DISTINCT")
    if op=="orthogonality_3d":
        u,v=p["u"],p["v"];vec3(u);vec3(v);nonzero(u);nonzero(v)
        return "TRUE" if dot(u,v)==0 else "FALSE"
    raise ValueError("unknown math operation")

def witness(op,params):
    result=dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,
                general_theorem_certified=False,student_freeform_step_verified=False,
                student_publishable=False,teacher_approved=False)
    if not isinstance(op,str) or op not in SAMPLES:
        result["status"]="UNSUPPORTED"
        return result
    if type(params) is not dict or set(params)!=set(SAMPLES[op][0]) or not all(safe(v) for v in params.values()):
        return result
    try:
        result["exact_value"]=calculate(op,params)
        result["status"]="FINITE_EXACT_CASE_ONLY"
    except (ValueError,ZeroDivisionError,OverflowError,TypeError):
        pass
    return result
