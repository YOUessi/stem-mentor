"""Teacher-side finite exact witnesses for elective A-E editorial examples only.

These operators cannot certify universal theorems, teacher approvals,
free-form student reasoning, or official curriculum equivalence.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import gcd
import re

OPS=("affine_recurrence","compound_growth","rhythm_sync","orthogonal_matrix_2d","unique_linear_system_2d")

def _ratio(x):
    if isinstance(x,bool):raise ValueError("Boolean value is not a number")
    if isinstance(x,int):
        if abs(x)>1000:raise ValueError("Outside bounded rational range")
        return F(x)
    if not isinstance(x,str) or not re.fullmatch(r"-?(?:0|[1-9][0-9]{0,3})(?:/[1-9][0-9]{0,3})?",x):
        raise ValueError("Only bounded decimal integer or a/b rational literal")
    f=F(x)
    if abs(f.numerator)>1000 or f.denominator>1000:
        raise ValueError("Outside bounded rational range")
    return f

def _int(x,low=0,high=40):
    if isinstance(x,bool) or not isinstance(x,int) or not low<=x<=high:
        raise ValueError("Bounded integer expected")
    return x

def _square_2(mat):
    if not isinstance(mat,list) or len(mat)!=2 or any(not isinstance(row,list) or len(row)!=2 for row in mat):
        raise ValueError("Expected 2x2 matrix")
    return [[_ratio(x) for x in row] for row in mat]

def finite(op,p):
    if op not in OPS or not isinstance(p,dict):raise ValueError("Unsupported finite witness")
    if op=="affine_recurrence":
        a,b,x0=(_ratio(p[k]) for k in ("a","b","x0"))
        n=_int(p["n"],0,24)
        cur=x0
        for _ in range(n):cur=a*cur+b
        formula=a**n*x0 + (b*n if a==1 else b*(a**n-1)/(a-1))
        if cur!=formula:raise ArithmeticError("Recurrence witness inconsistency")
        return dict(direct=cur,closed_form=formula,
                    fixed_point=None if a==1 else b/(1-a))
    if op=="compound_growth":
        principal,rate=(_ratio(p[k]) for k in ("principal","rate"))
        n=_int(p["n"],0,18)
        if principal<0 or 1+rate<=0:raise ValueError("Economic amount and growth factor domain")
        value=principal
        for _ in range(n):value=value*(1+rate)
        if value!=principal*(1+rate)**n:raise ArithmeticError("Compounding mismatch")
        return dict(amount=value,formula=value)
    if op=="rhythm_sync":
        p1=_int(p["p"],1,60);p2=_int(p["q"],1,60)
        multiple=p1*p2//gcd(p1,p2)
        if multiple%p1 or multiple%p2 or any(t%p1==0 and t%p2==0 for t in range(1,multiple)):
            raise ArithmeticError("Not least common positive synchronization")
        return dict(first_sync=multiple,gcd=gcd(p1,p2))
    if op=="orthogonal_matrix_2d":
        a,b=_square_2(p["matrix"])
        # Columns orthonormal; all arithmetic exact with bounded rational input.
        dot11=a[0]**2+b[0]**2;dot22=a[1]**2+b[1]**2
        dot12=a[0]*a[1]+b[0]*b[1]
        if (dot11,dot22,dot12)!=(1,1,0):
            raise ValueError("Matrix columns not orthonormal")
        det=a[0]*b[1]-a[1]*b[0]
        if det*det!=1:raise ArithmeticError("Orthogonal determinant invariant")
        return dict(gram_identity=True,determinant=det)
    if op=="unique_linear_system_2d":
        m=_square_2(p["matrix"])
        if not isinstance(p["rhs"],list) or len(p["rhs"])!=2:
            raise ValueError("Right hand side has wrong dimension")
        c,d=map(_ratio,p["rhs"])
        (a,b),(e,f)=m;det=a*f-b*e
        if det==0:raise ValueError("No unique solution when determinant is zero")
        x=(f*c-b*d)/det;y=(-e*c+a*d)/det
        if a*x+b*y!=c or e*x+f*y!=d:raise ArithmeticError("Substitution failed")
        return dict(x=x,y=y,determinant=det)
    raise ValueError("Unsupported")

def guarded_evaluate(op,p):
    base=dict(status="CONDITIONS_NOT_ESTABLISHED",witness=None,
              whole_theorem_certified=False,teacher_approved=False,
              student_freeform_step_verified=False,official_atomic_goal_certified=False,
              student_solution_release_authorized=False)
    try:
        out=finite(op,p)
    except (TypeError,KeyError,ValueError,ZeroDivisionError,OverflowError):
        return base
    return {**base,"status":"VERIFIED_FINITE_INSTANCE","witness":{
        k:str(v) if isinstance(v,F) else v for k,v in out.items()}}
