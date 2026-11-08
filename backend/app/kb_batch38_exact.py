"""Batch38 independent finite rational witnesses, with explicit premise rejection.

Never certifies a general proof, a manuscript, a teacher approval or a student's steps.
"""
from __future__ import annotations
from fractions import Fraction
from math import factorial

FIELDS={
    "factorial_sum":("n",),
    "matrix2_product":("a","b","c","d","e","f","g","h"),
    "row_scale_equation":("factor","a","b"),
    "cramer_2x2":("a","b","c","d","u","v"),
    "density_linear":("coef","num","den"),
    "chi_square_2":("o1","o2","e1","e2"),
    "quadratic_convex":("a",),
    "linear_mvt":("slope","left","right"),
    "square_affine_max":("a","b","side"),
    "kmeans_two":("x","y"),
    "leontief_scalar":("anum","aden","demand"),
    "fixed_compound_rate":("jnum","jden","m"),
    "isometry2":("a","b","c","d"),
    "annuity":("amount","inum","iden","periods"),
}
VALID={
    "factorial_sum":{"n":3},
    "matrix2_product":{"a":1,"b":2,"c":0,"d":1,"e":1,"f":0,"g":1,"h":1},
    "row_scale_equation":{"factor":2,"a":1,"b":3},
    "cramer_2x2":{"a":2,"b":1,"c":1,"d":1,"u":5,"v":3},
    "density_linear":{"coef":2,"num":1,"den":2},
    "chi_square_2":{"o1":12,"o2":8,"e1":10,"e2":10},
    "quadratic_convex":{"a":1},
    "linear_mvt":{"slope":3,"left":0,"right":2},
    "square_affine_max":{"a":1,"b":2,"side":1},
    "kmeans_two":{"x":0,"y":2},
    "leontief_scalar":{"anum":1,"aden":2,"demand":10},
    "fixed_compound_rate":{"jnum":1,"jden":10,"m":2},
    "isometry2":{"a":0,"b":-1,"c":1,"d":0},
    "annuity":{"amount":110,"inum":1,"iden":10,"periods":2},
}
INVALID={
    "factorial_sum":{"n":-1},
    "matrix2_product":dict(VALID["matrix2_product"],a=10**7),
    "row_scale_equation":dict(VALID["row_scale_equation"],factor=0),
    "cramer_2x2":dict(VALID["cramer_2x2"],a=1,b=1,c=2,d=2),
    "density_linear":dict(VALID["density_linear"],coef=3),
    "chi_square_2":dict(VALID["chi_square_2"],e1=0),
    "quadratic_convex":{"a":-1},
    "linear_mvt":dict(VALID["linear_mvt"],left=2,right=0),
    "square_affine_max":dict(VALID["square_affine_max"],side=0),
    "kmeans_two":dict(VALID["kmeans_two"],x=10000001),
    "leontief_scalar":dict(VALID["leontief_scalar"],anum=1,aden=1),
    "fixed_compound_rate":dict(VALID["fixed_compound_rate"],jnum=-11,jden=10,m=1),
    "isometry2":dict(VALID["isometry2"],a=2),
    "annuity":dict(VALID["annuity"],inum=-11,iden=10),
}
def exact(op,p):
    if op=="factorial_sum":
        n=p["n"]
        if n<0 or n>15:raise ValueError("finite factorial bound")
        return str(sum((Fraction(1,factorial(k)) for k in range(n+1)),Fraction()))
    if op=="matrix2_product":
        a,b,c,d,e,f,g,h=(p[k] for k in FIELDS[op])
        return f"{a*e+b*g},{a*f+b*h};{c*e+d*g},{c*f+d*h}"
    if op=="row_scale_equation":
        if p["factor"]==0:raise ValueError("non-invertible transformation")
        return f"{p['factor']*p['a']}x={p['factor']*p['b']}"
    if op=="cramer_2x2":
        a,b,c,d,u,v=(p[k] for k in FIELDS[op])
        det=a*d-b*c
        if det==0:raise ValueError("Cramer denominator zero")
        return str(Fraction(u*d-b*v,det))+","+str(Fraction(a*v-u*c,det))
    if op=="density_linear":
        k,n,d=(p[x] for x in FIELDS[op])
        if d<=0 or n<0 or n>d or k!=2:raise ValueError("invalid density or integration interval")
        t=Fraction(n,d)
        return str(t*t)
    if op=="chi_square_2":
        o1,o2,e1,e2=(p[k] for k in FIELDS[op])
        if e1<=0 or e2<=0 or min(o1,o2)<0 or o1+o2!=e1+e2:
            raise ValueError("expected count or total invalid")
        return str(Fraction((o1-e1)**2,e1)+Fraction((o2-e2)**2,e2))
    if op=="quadratic_convex":
        if p["a"]<0:raise ValueError("not convex within this family")
        return str(2*p["a"])
    if op=="linear_mvt":
        if p["left"]>=p["right"]:raise ValueError("interval empty")
        return str(p["slope"])
    if op=="square_affine_max":
        if p["side"]<=0:raise ValueError("requires nondegenerate compact square")
        return str(p["side"]*(max(0,p["a"])+max(0,p["b"])))
    if op=="kmeans_two":
        x,y=(p[k] for k in FIELDS[op])
        midpoint=Fraction(x+y,2);cost=Fraction((x-y)**2,2)
        return f"{midpoint}|{cost}"
    if op=="leontief_scalar":
        a,d=p["anum"],p["aden"]
        if d<=0 or not 0<=a<d or p["demand"]<0:raise ValueError("spectral radius fails")
        return str(Fraction(p["demand"]*d,d-a))
    if op=="fixed_compound_rate":
        n,d,m=p["jnum"],p["jden"],p["m"]
        if d<=0 or not 1<=m<=24 or d*m+n<=0:raise ValueError("invalid compounding premise")
        return str((1+Fraction(n,d*m))**m-1)
    if op=="isometry2":
        a,b,c,d=(p[k] for k in FIELDS[op])
        if a*a+c*c!=1 or b*b+d*d!=1 or a*b+c*d!=0:
            raise ValueError("not an orthogonal matrix")
        return str(a*d-b*c)
    if op=="annuity":
        a,n,d,k=(p[x] for x in FIELDS[op])
        if a<0 or d<=0 or d+n<=0 or not 1<=k<=12:raise ValueError("discount assumptions fail")
        r=1+Fraction(n,d)
        return str(sum((Fraction(a,1)/(r**j) for j in range(1,k+1)),Fraction()))
    raise KeyError(op)

def witness(operator:str, params:object)->dict[str,str]:
    base={"teacher_approved":"false","general_theorem_certified":"false",
          "student_freeform_step_verified":"false","mathematics_scope":"FINITE_EXACT_CASE_ONLY"}
    if operator not in FIELDS:return dict(base,status="UNSUPPORTED",exact_value="")
    try:
        keys=FIELDS[operator]
        if not isinstance(params,dict) or set(params)!=set(keys):
            raise ValueError("missing/extra fields")
        if any(type(params[k]) is not int or abs(params[k])>1000000 for k in keys):
            raise ValueError("unsupported type or bound")
        result=exact(operator,params)
        return dict(base,status="FINITE_EXACT_CASE_ONLY",exact_value=result)
    except (TypeError,ValueError,ZeroDivisionError,OverflowError):
        return dict(base,status="CONDITIONS_NOT_ESTABLISHED",exact_value="")
