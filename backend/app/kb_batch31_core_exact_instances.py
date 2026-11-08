"""K07 finite rational witnesses for selected Batch31 K00 draft concepts.

These checks never certify a general theorem, a free-form proof, an untrusted
student answer, an official curriculum atom or an approved lesson.
No eval/sympify of arbitrary text. Strict typed operands only.
"""
from __future__ import annotations
from fractions import Fraction as Q
from collections.abc import Callable

class ConditionsNotEstablished(ValueError):pass

MAX=10000

def rational(v):
    if type(v) is int and -MAX<=v<=MAX:return Q(v)
    if (type(v) is str and 1<=len(v)<=12):
        import re
        if re.fullmatch(r"-?(?:0|[1-9]\d{0,3})(?:/[1-9]\d{0,3})?",v):
            try:r=Q(v)
            except ZeroDivisionError as e:raise ConditionsNotEstablished("Zero denominator") from e
            if abs(r.numerator)<=MAX and r.denominator<=MAX:return r
    raise ConditionsNotEstablished("Only bounded canonical exact rationals are supported")

def ints(v, minlen, maxlen):
    if type(v) is not list or not minlen<=len(v)<=maxlen:
        raise ConditionsNotEstablished("Bounded nonempty list needed")
    return [rational(x) for x in v]

def do(op:str,payload:dict)->dict:
    if type(payload) is not dict or len(payload)>8 or type(op) is not str:
        raise ConditionsNotEstablished("Unknown or untyped finite fixture")
    x=payload
    if op=="finite_relative_complement":
        U=x.get("universe");A=x.get("subset")
        if type(U) is not list or type(A) is not list or len(U)>12 or len(A)>12:
            raise ConditionsNotEstablished("Finite lists only")
        if any(type(v) is not int or abs(v)>MAX for v in U+A):
            raise ConditionsNotEstablished("Bounded integer elements only")
        if len(U)!=len(set(U)) or len(A)!=len(set(A)) or not set(A)<=set(U):
            raise ConditionsNotEstablished("Complement requires an actual subset of universe")
        return dict(relative_complement=sorted(set(U)-set(A)),general_theorem_verified=False)
    if op=="strict_inequality_scale":
        a,b,c=(rational(x[k]) for k in ("a","b","multiplier"))
        if not a<b or c==0:raise ConditionsNotEstablished("Need a<b and multiplier !=0")
        left,right=a*c,b*c
        return dict(left=left,right=right,relation="<" if c>0 else ">",
                    correct=(left<right if c>0 else left>right))
    if op=="quadratic_discriminant":
        a,b,c=(rational(x[k]) for k in ("a","b","c"))
        if not a:raise ConditionsNotEstablished("Quadratic requires nonzero leading coefficient")
        d=b*b-4*a*c
        return dict(discriminant=d,distinct_real_roots=2 if d>0 else 1 if d==0 else 0)
    if op=="agm_squared_witness":
        a,b=(rational(x[k]) for k in ("a","b"))
        if min(a,b)<0:raise ConditionsNotEstablished("AM-GM domain requires both nonnegative")
        gap=(a+b)**2-4*a*b
        return dict(squared_gap=gap,difference_square=(a-b)**2,valid=gap>=0,
                    equality=a==b,whole_inequality_theorem_not_certified=True)
    if op=="exact_log_integer_power":
        base=rational(x["base"]);arg=rational(x["argument"])
        if base<=0 or base==1 or arg<=0:raise ConditionsNotEstablished("Log domain: b>0 !=1, x>0")
        for n in range(-10,11):
            if base**n==arg:
                return dict(integer_log=n,scope="only exact integer-power cases")
        raise ConditionsNotEstablished("Exact integer logarithm outside supported small exponent set")
    if op=="unit_circle_tangent":
        s,c=rational(x["sin"]),rational(x["cos"])
        if s*s+c*c!=1 or c==0:
            raise ConditionsNotEstablished("Require exact unit-circle pair and cos !=0")
        return dict(tangent=s/c,unit_identity_confirmed=True)
    if op=="geometric_sum":
        first,q=rational(x["first"]),rational(x["q"])
        n=x.get("n")
        if type(n) is not int or not 1<=n<=32:raise ConditionsNotEstablished("1<=n<=32 integer")
        direct=sum((first*q**k for k in range(n)),Q(0))
        closed=first*n if q==1 else first*(1-q**n)/(1-q)
        return dict(direct=direct,closed=closed,equal=direct==closed,
                    used_nonzero_denominator=q!=1)
    if op=="affine_bisection":
        a,b,lo,hi=(rational(x[k]) for k in ("a","b","lo","hi"))
        if a==0 or not lo<hi:raise ConditionsNotEstablished("Nonconstant affine and ordered endpoints")
        f=lambda t:a*t+b
        if f(lo)*f(hi)>=0:raise ConditionsNotEstablished("Strict opposite endpoint signs required")
        m=(lo+hi)/2
        l,r=(lo,m) if f(lo)*f(m)<=0 else (m,hi)
        return dict(midpoint=m,new_lo=l,new_hi=r,new_width=r-l,
                    exact_root=-b/a,valid_bracket=l<=-b/a<=r,
                    supported_function_only="affine continuous")
    if op=="vector_perpendicular_nonzero":
        u,v=ints(x["u"],2,3),ints(x["v"],2,3)
        if len(u)!=len(v) or not any(u) or not any(v):
            raise ConditionsNotEstablished("Equal dimension and both nonzero for angle")
        return dict(dot=sum((a*b for a,b in zip(u,v)),Q(0)),
                    perpendicular=sum(a*b for a,b in zip(u,v))==0,
                    angle_defined=True)
    if op=="three_points_unique_plane":
        p,q,r=(ints(x[z],3,3) for z in ("p","q","r"))
        u=[b-a for a,b in zip(p,q)];v=[b-a for a,b in zip(p,r)]
        n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        if n==(Q(0),Q(0),Q(0)):
            raise ConditionsNotEstablished("Three points must be noncollinear")
        return dict(normal=list(n),noncollinear=True,unique_plane_exists=True)
    if op=="complex_division":
        a,b,c,d=(rational(x[k]) for k in ("a","b","c","d"))
        if c==d==0:raise ConditionsNotEstablished("Complex denominator cannot be zero")
        den=c*c+d*d
        return dict(real=(a*c+b*d)/den,imag=(b*c-a*d)/den,
                    denominator_norm_squared=den,nonzero_denominator=True)
    if op=="finite_quantifier":
        vals=x.get("predicate_values")
        if type(vals) is not list or not 1<=len(vals)<=16 or any(type(v) is not bool for v in vals):
            raise ConditionsNotEstablished("Nonempty finite Boolean predicate truth table needed")
        return dict(forall=all(vals),exists=any(vals),not_forall=not all(vals),
                    exists_not=any(not v for v in vals),de_morgan_holds=(not all(vals))==any(not v for v in vals),
                    finite_domain_only=True)
    raise ConditionsNotEstablished("Unsupported op")

OPS=("finite_relative_complement","strict_inequality_scale","quadratic_discriminant",
     "agm_squared_witness","exact_log_integer_power","unit_circle_tangent",
     "geometric_sum","affine_bisection","vector_perpendicular_nonzero",
     "three_points_unique_plane","complex_division","finite_quantifier")

def evaluate(op,payload):
    """Result contract segregates finite math checks from all authority claims."""
    try:
        witness=do(op,payload)
    except (ConditionsNotEstablished,KeyError,TypeError,ValueError,ZeroDivisionError) as exc:
        return dict(status="CONDITIONS_NOT_ESTABLISHED",
                    reason=str(exc)[:160],witness=None,
                    complete_theorem_certified=False,student_step_verified=False,
                    teacher_approved=False,official_curriculum_atom_verified=False)
    return dict(status="VERIFIED_FINITE_INSTANCE",reason="Bounded exact rational fixture only",
                witness=witness,complete_theorem_certified=False,student_step_verified=False,
                teacher_approved=False,official_curriculum_atom_verified=False)
