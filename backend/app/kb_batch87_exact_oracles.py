"""Batch87 finite exact teacher-side witnesses, NEVER universal theorem certification."""
from __future__ import annotations
from fractions import Fraction as F
from math import comb
from typing import Any
import sympy as sp

SUPPORTED=frozenset({
    "classical_uniform","weighted_strata","hypergeometric",
    "pearson","bivariate_ols","projectile_slope","contingency_2x2"})
def frac(v):
    if type(v) is bool or type(v) not in (int,str):
        raise ValueError("exact integer or rational string required")
    return F(v)
def result(ok, detail, exact=None):
    return {
        "status":"VERIFIED_FINITE_INSTANCE" if ok else "CONDITIONS_NOT_ESTABLISHED",
        "explanation":detail,"exact_value":str(exact) if exact is not None else None,
        "teacher_approved":False,"general_theorem_certified":False,
        "student_free_text_verified":False,"student_publishable":False}
def evaluate(op:str,data:dict[str,Any]):
    if op not in SUPPORTED:
        evidence=result(False,"No bounded exact oracle supports this operation")
        evidence["status"]="UNSUPPORTED"
        return evidence
    if type(data) is not dict:return result(False,"invalid fixture")
    try:
        if op=="classical_uniform":
            n=data["n"];event=data["event"]
            if type(n) is not int or n<1 or type(event) is not list or data.get("uniform_certified") is not True:
                return result(False,"finite nonempty and genuinely equiprobable outcomes required")
            if len(set(event))!=len(event) or any(type(i) is not int or i<1 or i>n for i in event):
                return result(False,"event must be a subset of indexed outcomes")
            return result(True,"finite uniform outcome counting",F(len(event),n))
        if op=="weighted_strata":
            weights=data["population_counts"];means=data["stratum_means"]
            if type(weights) is not list or type(means) is not list or len(weights)!=len(means) or len(weights)<2:
                return result(False,"same number of strata required")
            if any(type(w) is not int or w<=0 for w in weights):
                return result(False,"positive population size required for every stratum")
            y=[frac(v) for v in means]
            return result(True,"weighted population mean conditional on stated stratum means",
                          sum((F(w)*m for w,m in zip(weights,y)),F(0))/sum(weights))
        if op=="hypergeometric":
            N,K,n,k=(data[v] for v in ("N","K","n","k"))
            if any(type(v) is not int for v in (N,K,n,k)) or not (0<=K<=N and 0<=n<=N and max(0,n-(N-K))<=k<=min(K,n) and N>0):
                return result(False,"finite population integers and support bounds required")
            return result(True,"without-replacement probability for one fixed exact draw",F(comb(K,k)*comb(N-K,n-k),comb(N,n)))
        if op=="pearson":
            xs=data["x"];ys=data["y"]
            if type(xs) is not list or type(ys) is not list or len(xs)!=len(ys) or len(xs)<2:
                return result(False,"matched pairs and at least two observations required")
            xx=[frac(x) for x in xs];yy=[frac(y) for y in ys];n=len(xx)
            cx=[v-sum(xx)/n for v in xx];cy=[v-sum(yy)/n for v in yy]
            a=sum((v*v for v in cx),F(0));b=sum((v*v for v in cy),F(0))
            if a==0 or b==0:return result(False,"Pearson denominator zero: undefined correlation")
            r=sp.simplify(sp.Rational(sum((u*v for u,v in zip(cx,cy)),F(0)).numerator,
                                     sum((u*v for u,v in zip(cx,cy)),F(0)).denominator) /
                 sp.sqrt(sp.Rational(a.numerator,a.denominator)*sp.Rational(b.numerator,b.denominator)))
            return result(True,"Pearson coefficient for this paired exact sample",r)
        if op=="bivariate_ols":
            raw=data["rows"];rhs=data["y"]
            if type(raw) is not list or type(rhs) is not list or len(raw)!=len(rhs) or len(raw)<3:
                return result(False,"matching design and response sizes required")
            if any(type(row) is not list or len(row)!=3 for row in raw):
                return result(False,"intercept and exactly two predictors required")
            X=sp.Matrix([[sp.Rational(frac(v).numerator,frac(v).denominator) for v in row] for row in raw])
            y=sp.Matrix([sp.Rational(frac(v).numerator,frac(v).denominator) for v in rhs])
            if X.rank()<3:return result(False,"design rank deficient; unique coefficients unavailable")
            beta=(X.T*X).inv()*X.T*y
            return result(True,"unique full-column-rank least squares coefficients (finite sample)",",".join(map(str,beta)))
        if op=="projectile_slope":
            vx=frac(data["vx"]);v0=frac(data["vertical_initial_velocity"]);g=frac(data["gravity"]);t=frac(data["t"])
            if vx==0 or g<=0 or t<0:return result(False,"nonzero horizontal velocity, positive gravity and nonnegative time required")
            return result(True,"slope dy/dx at fixed time for ideal projectile", (v0-g*t)/vx)
        if op=="contingency_2x2":
            a=data["table"]
            if type(a) is not list or len(a)!=2 or any(type(r) is not list or len(r)!=2 for r in a):
                return result(False,"two by two table required")
            if any(type(v) is not int or v<0 for row in a for v in row):
                return result(False,"nonnegative integer counts required")
            rs=[sum(r) for r in a];cs=[a[0][i]+a[1][i] for i in range(2)]
            total=sum(rs)
            if total==0 or any(t==0 for t in rs+cs):
                return result(False,"positive row and column marginals required")
            chi=F(0)
            for i in range(2):
                for j in range(2):
                    e=F(rs[i]*cs[j],total)
                    chi+=(F(a[i][j])-e)**2/e
            return result(True,"Pearson chi-square statistic for this exact table, not a p-value",chi)
    except (KeyError,TypeError,ValueError,ZeroDivisionError,IndexError,OverflowError) as exc:
        return result(False,"invalid exact fixture: "+type(exc).__name__)
    return result(False,"unreachable")
