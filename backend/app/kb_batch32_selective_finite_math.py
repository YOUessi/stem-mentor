"""Independent bounded exact-rational *instances* for K00 selective-course drafts.

Not a proof assistant; never claim general theorem certification, student step
validation, official syllabus atom verification or teacher approval.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import comb

class PreconditionsNotEstablished(ValueError):
    pass

def whole(v, low=-200, high=200):
    if type(v) is not int or not low <= v <= high:
        raise PreconditionsNotEstablished("Bounded non-boolean integer required")
    return v

def q(v):
    if type(v) is int and abs(v) <= 200:
        return F(v)
    if type(v) is str and len(v) <= 12:
        import re
        if re.fullmatch(r"-?(?:0|[1-9]\d{0,2})(?:/[1-9]\d{0,2})?", v):
            try:
                ans = F(v)
            except ZeroDivisionError as exc:
                raise PreconditionsNotEstablished("Nonzero denominator required") from exc
            if abs(ans.numerator) <= 200 and ans.denominator <= 200:
                return ans
    raise PreconditionsNotEstablished("Only canonical bounded exact rational values")

def qlist(v, minlen=2, maxlen=8):
    if type(v) is not list or not minlen <= len(v) <= maxlen:
        raise PreconditionsNotEstablished("Bounded finite list required")
    return [q(z) for z in v]

def finite(op, data):
    if type(op) is not str or type(data) is not dict or len(data) > 8:
        raise PreconditionsNotEstablished("Unsupported or untyped fixture")
    if op == "arithmetic_series":
        a=q(data["first"]);d=q(data["difference"]);n=whole(data["n"],1,32)
        direct=sum((a+d*i for i in range(n)),F())
        formula=n*(2*a+(n-1)*d)/2
        return {"direct":direct,"formula":formula,"exact_match":direct==formula,"n":n}
    if op == "conditional_probability_finite":
        universe=data["universe"];a=data["event_a"];b=data["event_b"]
        if any(type(x) is not list or len(x)>16 for x in (universe,a,b)):
            raise PreconditionsNotEstablished("Finite list sets only")
        if any(type(v) is not int or abs(v)>200 for arr in (universe,a,b) for v in arr):
            raise PreconditionsNotEstablished("Bounded integer sample points only")
        U,A,B=set(universe),set(a),set(b)
        if len(U)!=len(universe) or len(A)!=len(a) or len(B)!=len(b) or not U or not (A|B)<=U or not B:
            raise PreconditionsNotEstablished("Distinct universe and events subsets; positive B probability")
        return {"intersection_size":len(A&B),"given_size":len(B),
                "conditional":F(len(A&B),len(B)), "finite_equiprobable_sample_space":True}
    if op == "hypergeometric_mass":
        N=whole(data["population"],1,40);K=whole(data["successes"],0,N)
        n=whole(data["draws"],0,N);k=whole(data["observed"],0,n)
        if k>K or n-k>N-K:
            raise PreconditionsNotEstablished("Impossible observed count under no replacement")
        mass=F(comb(K,k)*comb(N-K,n-k),comb(N,n))
        return {"mass":mass,"numerator":comb(K,k)*comb(N-K,n-k),
                "denominator":comb(N,n),"draw_without_replacement":True}
    if op == "point_line_distance_squared":
        A=q(data["A"]);B=q(data["B"]);C=q(data["C"]);x=q(data["x"]);y=q(data["y"])
        if A==B==0:
            raise PreconditionsNotEstablished("General-form line must have nonzero normal")
        squared=(A*x+B*y+C)**2/(A*A+B*B)
        return {"exact_distance_squared":squared,"normal_nonzero":True}
    if op == "binomial_choice":
        n=whole(data["n"],0,35);k=whole(data["k"],0,n)
        ways=comb(n,k)
        return {"count":ways,"symmetry":ways==comb(n,n-k),
                "pascal":True if k==0 or k==n else ways==comb(n-1,k-1)+comb(n-1,k)}
    if op == "least_squares_line":
        xs=qlist(data["x"]);ys=qlist(data["y"])
        if len(xs)!=len(ys):
            raise PreconditionsNotEstablished("Equal number of paired observations required")
        N=len(xs);sx=sum(xs,F());sy=sum(ys,F())
        var=N*sum((u*u for u in xs),F())-sx*sx
        if var==0:
            raise PreconditionsNotEstablished("Nonconstant predictor required for unique slope")
        slope=(N*sum((u*v for u,v in zip(xs,ys)),F())-sx*sy)/var
        intercept=(sy-slope*sx)/N
        residuals=[y-(slope*x+intercept) for x,y in zip(xs,ys)]
        return {"slope":slope,"intercept":intercept,
                "sum_residuals":sum(residuals,F()),
                "sum_x_residuals":sum((x*e for x,e in zip(xs,residuals)),F()),
                "stationary_normal_equations":sum(residuals,F())==0 and
                    sum((x*e for x,e in zip(xs,residuals)),F())==0,
                "causality_not_established":True}
    raise PreconditionsNotEstablished("Operator outside bounded selective fixture scope")

OPS=("arithmetic_series","conditional_probability_finite","hypergeometric_mass",
     "point_line_distance_squared","binomial_choice","least_squares_line")

def evaluate(op, data):
    try:
        witness=finite(op,data)
        return dict(status="VERIFIED_FINITE_INSTANCE",witness=witness,reason="Typed bounded exact rational case")
    except (PreconditionsNotEstablished,KeyError,TypeError,ValueError,OverflowError,ZeroDivisionError) as e:
        return dict(status="CONDITIONS_NOT_ESTABLISHED",witness=None,reason=str(e)[:160],
                    )
    finally:
        pass

def guarded_evaluate(op,data):
    result=evaluate(op,data)
    return {**result,"whole_theorem_certified":False,"student_freeform_step_verified":False,
            "teacher_approved":False,"official_curriculum_atom_verified":False,
            "student_solution_release_authorized":False}
