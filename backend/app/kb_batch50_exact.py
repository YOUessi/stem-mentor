"""Batch50 exact finite witnesses: deliberately NOT general proofs or student-step certification."""
from __future__ import annotations
from fractions import Fraction as F
from math import comb

SAMPLES = {
 "unsquared_root_filter": ({"candidate":3},"VALID",{"candidate":-2}),
 "independence_2x2": ({"a":1,"b":1,"c":1,"d":1},"EMPIRICAL_FACTORIZATION_ONLY",{"a":0,"b":0,"c":1,"d":1}),
 "product_probability": ({"a":1,"b":1,"c":1,"d":3},"1/6",{"a":0,"b":1,"c":0,"d":1}),
 "two_coin_success_count": ({"successes":1},"1/2",{"successes":3}),
 "binomial_probability": ({"n":3,"k":2,"p_num":1,"p_den":2},"3/8",{"n":3,"k":2,"p_num":2,"p_den":0}),
 "hypergeometric_probability": ({"N":5,"K":2,"n":2,"k":1},"3/5",{"N":2,"K":3,"n":2,"k":1}),
 "normal_center_half": ({"variance":4},"1/2",{"variance":0}),
 "normal_z_score": ({"mu":10,"variance":4,"x":14},"2",{"mu":10,"variance":0,"x":14}),
 "nonlinear_zero_covariance": ({"width":1},"ZERO_LINEAR_COV_NONLINEAR",{"width":0}),
 "pearson_perfect": ({"x1":1,"x2":2,"x3":3,"slope":2},"1",{"x1":1,"x2":1,"x3":1,"slope":2}),
 "cosine_perfect": ({"slope":-2},"-1",{"slope":0}),
 "ols_slope": ({"x1":1,"x2":3,"y1":2,"y2":6},"2",{"x1":1,"x2":1,"y1":2,"y2":6}),
 "regression_point": ({"intercept":2,"slope":3,"x":4},"14",{"intercept":2,"slope":3,"x":101}),
 "in_range_or_extrapolation": ({"low":0,"high":5,"x":20},"EXTRAPOLATION",{"low":5,"high":0,"x":20}),
 "empirical_2x2": ({"a":3,"b":2,"c":1,"d":4},"3/10",{"a":0,"b":0,"c":0,"d":0}),
 "expected_2x2": ({"a":8,"b":2,"c":12,"d":18},"5",{"a":0,"b":0,"c":5,"d":5}),
 "chi_square_2x2": ({"a":20,"b":10,"c":10,"d":20},"20/3",{"a":0,"b":0,"c":5,"d":5}),
}
INDEX_OP = {i:op for i,op in enumerate(SAMPLES)}
assert len(SAMPLES)==17
def require(ok:bool):
    if not ok: raise ValueError("mathematical premises missing")
def tab(d):
    a,b,c,e=(d[k] for k in ("a","b","c","d"))
    require(min(a,b,c,e)>=0 and a+b+c+e>0)
    return a,b,c,e,a+b+c+e
def calc(op,d):
    if op=="unsquared_root_filter":
        c=d["candidate"];require(c>=-1)
        return "VALID" if c==3 else "INVALID_EXTRANEOUS"
    if op=="independence_2x2":
        a,b,c,e,N=tab(d)
        require((a+b)>0 and (c+e)>0 and (a+c)>0 and (b+e)>0)
        return "EMPIRICAL_FACTORIZATION_ONLY" if a*e==b*c else "EMPIRICAL_NONFACTORING_ONLY"
    if op=="product_probability":
        a,b,c,e,N=tab(d)
        require(a+c>0)
        return str(F(a+c,N)*F(a,a+c))
    if op=="two_coin_success_count":
        k=d["successes"];require(0<=k<=2)
        return str(F(comb(2,k),4))
    if op=="binomial_probability":
        n,k,p,den=d["n"],d["k"],d["p_num"],d["p_den"]
        require(0<=k<=n<=30 and 0<=p<=den and den>0)
        f=F(p,den)
        return str(F(comb(n,k),1)*f**k*(1-f)**(n-k))
    if op=="hypergeometric_probability":
        N,K,n,k=d["N"],d["K"],d["n"],d["k"]
        require(0<N<=60 and 0<=K<=N and 0<=n<=N and max(0,n-N+K)<=k<=min(n,K))
        return str(F(comb(K,k)*comb(N-K,n-k),comb(N,n)))
    if op=="normal_center_half":
        require(d["variance"]>0)
        return "1/2"
    if op=="normal_z_score":
        from math import isqrt
        v=d["variance"];s=isqrt(v) if v>=0 else 0
        require(v>0 and s*s==v)
        return str(F(d["x"]-d["mu"],s))
    if op=="nonlinear_zero_covariance":
        require(d["width"]>0)
        return "ZERO_LINEAR_COV_NONLINEAR"  # x=(-w,0,w); y=x^2
    if op=="pearson_perfect":
        x=[d["x1"],d["x2"],d["x3"]];s=d["slope"]
        require(len(set(x))>1 and s!=0)
        return "1" if s>0 else "-1"
    if op=="cosine_perfect":
        require(d["slope"]!=0)
        return "1" if d["slope"]>0 else "-1"
    if op=="ols_slope":
        dx=d["x2"]-d["x1"];require(dx!=0)
        return str(F(d["y2"]-d["y1"],dx))
    if op=="regression_point":
        return str(d["intercept"]+d["slope"]*d["x"])
    if op=="in_range_or_extrapolation":
        lo,hi,x=d["low"],d["high"],d["x"]
        require(lo<=hi)
        return "INTERPOLATION" if lo<=x<=hi else "EXTRAPOLATION"
    if op=="empirical_2x2":
        a,b,c,e,N=tab(d)
        return str(F(a,N))
    if op in ("expected_2x2","chi_square_2x2"):
        a,b,c,e,N=tab(d)
        obs=((a,b),(c,e))
        r=[a+b,c+e];col=[a+c,b+e]
        require(min(r+col)>0)
        E=[[F(r[i]*col[j],N) for j in range(2)] for i in range(2)]
        if op=="expected_2x2":return str(E[0][0])
        return str(sum(((F(obs[i][j])-E[i][j])**2/E[i][j] for i in range(2) for j in range(2)),F(0)))
    raise ValueError("unsupported")
def witness(op,params):
    out={"status":"CONDITIONS_NOT_ESTABLISHED","exact_value":None,"general_theorem_certified":False,
         "student_freeform_step_verified":False,"teacher_approved":False,"student_publishable":False}
    if type(op) is not str or op not in SAMPLES:
        out["status"]="UNSUPPORTED";return out
    template=SAMPLES[op][0]
    if type(params) is not dict or set(params)!=set(template):return out
    if any(type(v) is not int or abs(v)>100 for v in params.values()):return out
    if op=="normal_z_score" and params["variance"]>0:
        from math import isqrt
        variance=params["variance"]
        if isqrt(variance)**2!=variance:
            out["status"]="UNSUPPORTED"  # valid Gaussian variance, irrational sigma beyond this rational-only witness
            return out
    try:
        out["exact_value"]=calc(op,params)
        out["status"]="FINITE_EXACT_CASE_ONLY"
    except (ValueError,ZeroDivisionError,TypeError,OverflowError):
        pass
    return out
