"""Batch30: exact bounded mathematical witnesses for K07 (never a proof certificate).

Typed finite fixtures only.  No eval, parsing of arbitrary algebra, real student
answers, copyrighted content, or calls to model APIs.
"""
from __future__ import annotations
import re
from math import prod
from fractions import Fraction as F

MAX = 1000000

class ConditionsNotEstablished(ValueError):
    pass

def rat(x):
    if type(x) not in (str, int) or not re.fullmatch(r"-?(?:0|[1-9][0-9]{0,5})(?:/[1-9][0-9]{0,5})?", str(x)):
        raise ConditionsNotEstablished("Canonical bounded exact rational required")
    try: q = F(str(x))
    except (ValueError, ZeroDivisionError) as exc: raise ConditionsNotEstablished(str(exc))
    if abs(q.numerator)>MAX or q.denominator>MAX: raise ConditionsNotEstablished("Numerator/denominator bound")
    return q

def integer(x, lo, hi):
    if type(x) is not int or x<lo or x>hi:
        raise ConditionsNotEstablished("Bounded integer requirement")
    return x

def arr(x, lo=1, hi=8):
    if type(x) is not list or not lo<=len(x)<=hi:
        raise ConditionsNotEstablished("Bounded exact finite array requirement")
    return [rat(t) for t in x]

def vec3(x):
    return arr(x,3,3)

def inner(a,b):
    if len(a)!=len(b):raise ConditionsNotEstablished("Dimension mismatch")
    return sum((x*y for x,y in zip(a,b)),F(0))

def finite_weights(d):
    w=arr(d["weights"],1,8)
    if any(v<0 for v in w) or sum(w)!=1:raise ConditionsNotEstablished("Probability mass must be nonnegative and sum to one")
    return w

def compute(op,d):
    if type(d) is not dict or len(d)>12: raise ConditionsNotEstablished("Limited typed fixture required")
    if op=="product_count":
        sizes=d["sizes"]
        if type(sizes) is not list or not 1<=len(sizes)<=8:raise ConditionsNotEstablished("Finite stages")
        counts=[integer(n,1,20) for n in sizes]
        return dict(sequence_count=prod(counts),stages=len(counts),bijectivity_not_checked=True)
    if op=="square_difference_quotient":
        a,h=rat(d["a"]),rat(d["h"])
        if h==0:raise ConditionsNotEstablished("Difference quotient needs h nonzero")
        return dict(quotient=((a+h)**2-a*a)/h,simplified=2*a+h,limiting_derivative=2*a)
    if op=="mvt_quadratic":
        a,b=rat(d["a"]),rat(d["b"])
        if not a<b:raise ConditionsNotEstablished("a<b is required")
        c=(a+b)/2
        return dict(c=c,secant=(b*b-a*a)/(b-a),derivative_at_c=2*c,universal_mvt_not_certified=True)
    if op=="convex_chord_quadratic":
        k,b,c,x,z,y=[rat(d[q]) for q in ("k","b","c","x","z","y")]
        if k<0 or not x<z<y:raise ConditionsNotEstablished("Convex coefficient and ordered distinct points")
        f=lambda t:k*t*t+b*t+c
        gap=(y-z)/(y-x)*f(x)+(z-x)/(y-x)*f(y)-f(z)
        return dict(chord_minus_fz=gap,nonnegative=gap>=0,product_witness=k*(z-x)*(y-z))
    if op=="annuity_nonzero_rate":
        n=integer(d["n"],1,24)
        rate=rat(d["rate"])
        if rate<=-1 or rate==0:raise ConditionsNotEstablished("Regular annuity ratio requires rate > -1 and != 0")
        q=1/(1+rate)
        return dict(q=q,sum_of_discounts=sum((q**t for t in range(1,n+1)),F(0)),
                    closed=(1-(1+rate)**(-n))/rate)
    if op=="epsilon_delta_square":
        a,eps,h=rat(d["a"]),rat(d["epsilon"]),rat(d["h"])
        if eps<=0:raise ConditionsNotEstablished("epsilon > 0")
        delta=min(F(1),eps/(1+2*abs(a)))
        if h==0 or abs(h)>=delta:raise ConditionsNotEstablished("Require 0<|h|<delta")
        error=abs((a+h)**2-a*a)
        return dict(delta=delta,actual_error=error,target_epsilon=eps,strictly_less=error<eps,
                    derived_upper_bound=abs(h)*(1+2*abs(a)))
    if op=="bernoulli_mle":
        n=integer(d["n"],1,40); k=integer(d["k"],0,n)
        p=F(k,n)
        samples=[rat(x) for x in d["grid"]]
        if len(samples)>20 or any(not 0<=x<=1 for x in samples):
            raise ConditionsNotEstablished("Finite candidate probabilities in [0,1]")
        L=lambda t:t**k*(1-t)**(n-k)
        return dict(mle=p,likelihood=L(p),competitor_likelihoods=[L(t) for t in samples],
                    finite_comparison_only=True,unique_global_optimum_not_certified=True)
    if op=="ols_two_parameter":
        x=arr(d["x"],2,8); y=arr(d["y"],2,8)
        if len(x)!=len(y):raise ConditionsNotEstablished("Equal sample sizes")
        n=len(x); mx=sum(x)/n; my=sum(y)/n
        sxx=sum((v-mx)**2 for v in x)
        if sxx==0:raise ConditionsNotEstablished("OLS slope not identifiable: Sxx=0")
        sxy=sum((a-mx)*(b-my) for a,b in zip(x,y))
        slope=sxy/sxx; intercept=my-slope*mx
        residual=[yi-intercept-slope*xi for xi,yi in zip(x,y)]
        return dict(sxx=sxx,sxy=sxy,slope=slope,intercept=intercept,residual_sum=sum(residual),
                    residual_x_sum=sum(xi*ri for xi,ri in zip(x,residual)),
                    sse=sum(ri*ri for ri in residual))
    if op=="time_rescale_bijection":
        a,b,c,s,u=[rat(d[k]) for k in ("a","b","c","s","u")]
        if s==0:raise ConditionsNotEstablished("Invertible time parameter change requires s!=0")
        return dict(direct=a*(s*u)**2+b*s*u+c,expanded=a*s*s*u*u+b*s*u+c,
                    transformed_quadratic_coefficient=a*s*s)
    if op=="partial_y_polynomial":
        x,y,h=rat(d["x"]),rat(d["y"]),rat(d["h"])
        if h==0:raise ConditionsNotEstablished("Difference quotient h!=0")
        f=lambda yy:x*x*yy+3*yy*yy
        return dict(difference_quotient=(f(y+h)-f(y))/h,simplified=x*x+6*y+3*h,
                    partial_at_y=x*x+6*y)
    if op=="epsilon_n_reciprocal":
        eps=rat(d["epsilon"]);N=integer(d["N"],1,1000); n=integer(d["n"],N,100000)
        if eps<=0 or F(1,N)>=eps:raise ConditionsNotEstablished("N must satisfy 1/N<epsilon")
        return dict(one_over_n=F(1,n),one_over_N=F(1,N),strict_bound=F(1,n)<eps)
    if op=="circle_polar":
        R=rat(d["R"]); P=arr(d["P"],2,2)
        if R<=0 or P==[0,0]:raise ConditionsNotEstablished("Positive circle radius and nonzero pole")
        norm2=inner(P,P); dsq=R**4/norm2
        return dict(distance_squared=dsq,radius_squared=R*R,
                    intersections=2 if dsq<R*R else 1 if dsq==R*R else 0)
    if op=="bisection_square2":
        a,b=rat(d["a"]),rat(d["b"])
        f=lambda t:t*t-2
        if not a<b or f(a)*f(b)>=0:raise ConditionsNotEstablished("Ordered endpoints must have strictly opposite signs")
        m=(a+b)/2
        lo,hi=(a,m) if f(a)*f(m)<0 else (m,b) if f(m)*f(b)<0 else (m,m)
        return dict(midpoint=m,half_interval=[lo,hi],found_exact_root=(f(m)==0))
    if op=="solid_cone_prism_volume":
        B,h=rat(d["B"]),rat(d["h"])
        if B<0 or h<=0:raise ConditionsNotEstablished("Nonnegative base area and strictly positive height")
        return dict(prism=B*h,cone=B*h/3,cone_integral_coefficient=B/(h*h),
                    caveat="Requires parallel similar cone cross-sections")
    if op=="triangle_cosine":
        a,b,c=rat(d["a"]),rat(d["b"]),rat(d["c"])
        if min(a,b,c)<=0 or not a+b>c or not a+c>b or not b+c>a:
            raise ConditionsNotEstablished("Strict nondegenerate triangle inequalities")
        cosA=(b*b+c*c-a*a)/(2*b*c)
        area16=(a+b+c)*(-a+b+c)*(a-b+c)*(a+b-c)
        return dict(cosA=cosA,cos_in_range=(-1<cosA<1),sixteen_area_squared=area16)
    if op=="cross_lagrange_3":
        u,v=vec3(d["u"]),vec3(d["v"])
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        lhs=inner(cross,cross)
        return dict(cross=list(cross),cross_norm2=lhs,lagrange_gap=inner(u,u)*inner(v,v)-inner(u,v)**2)
    if op=="expectation_linearity":
        w=finite_weights(d);x=arr(d["x"]);y=arr(d["y"])
        if len(x)!=len(w) or len(y)!=len(w):raise ConditionsNotEstablished("Finite random variables defined on same sample space")
        a,b=rat(d["a"]),rat(d["b"])
        E=lambda z:sum((p*t for p,t in zip(w,z)),F(0))
        return dict(lhs=E([a*s+b*t for s,t in zip(x,y)]),rhs=a*E(x)+b*E(y),no_independence_assumed=True)
    if op=="row_scale_reversible":
        lam=rat(d["lambda"]);x,y=rat(d["x"]),rat(d["y"])
        a,b,c=[rat(d[k]) for k in ("a","b","c")]
        if lam==0:raise ConditionsNotEstablished("Row scaling by zero is irreversible")
        return dict(before=a*x+b*y-c,after=lam*(a*x+b*y-c),same_solution_truth=((a*x+b*y==c)==(lam*(a*x+b*y)==lam*c)))
    if op=="rotation_rational":
        c,s=rat(d["cos"]),rat(d["sin"]);u=arr(d["u"],2,2)
        if c*c+s*s!=1:raise ConditionsNotEstablished("Unit circle sine/cosine required")
        x,y=u
        return dict(det=c*c+s*s,original_norm2=x*x+y*y,
                    transformed_norm2=(c*x-s*y)**2+(s*x+c*y)**2)
    if op=="square_sum_induction":
        n=integer(d["n"],1,1000)
        return dict(previous_sum=n*n,next_odd=2*n+1,next_sum=n*n+2*n+1,
                    target=(n+1)**2)
    raise ConditionsNotEstablished("Unsupported operator")

SUPPORTED=frozenset(("product_count","square_difference_quotient","mvt_quadratic",
"convex_chord_quadratic","annuity_nonzero_rate","epsilon_delta_square","bernoulli_mle",
"ols_two_parameter","time_rescale_bijection","partial_y_polynomial",
"epsilon_n_reciprocal","circle_polar","bisection_square2","solid_cone_prism_volume",
"triangle_cosine","cross_lagrange_3","expectation_linearity","row_scale_reversible",
"rotation_rational","square_sum_induction"))

def evaluate(op,data):
    safety=dict(student_step_verified=False,complete_theorem_certified=False,
                teacher_approved=False,official_curriculum_atom_verified=False)
    if op not in SUPPORTED:return dict(status="UNSUPPORTED",reason="Unregistered operation",**safety)
    try:
        witness=compute(op,data)
        def ser(x):
            if isinstance(x,F): return str(x)
            if isinstance(x,(tuple,list)):return [ser(v) for v in x]
            if isinstance(x,dict):return {k:ser(v) for k,v in x.items()}
            return x
        return dict(status="VERIFIED_FINITE_INSTANCE",operation=op,witness=ser(witness),**safety)
    except (ConditionsNotEstablished,ValueError,ZeroDivisionError,TypeError,KeyError,OverflowError) as exc:
        return dict(status="CONDITIONS_NOT_ESTABLISHED",operation=op,reason=str(exc),**safety)
