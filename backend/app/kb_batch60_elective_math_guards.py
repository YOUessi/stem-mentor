"""Batch60: exact bounded witnesses for A-E electives; never general proofs or teacher approvals."""
from fractions import Fraction
from math import comb
from typing import Any

class ConditionsNotEstablished(ValueError):pass

FIELDS={
    "epsilon_n_tail":("epsilon","N"),
    "cramer3":("matrix","rhs"),
    "vector_cross":("left","right"),
    "uniform_interval_probability":("a","b","x","y"),
    "bernoulli_mle":("observations",),
    "t_statistic_squared":("observations","mu0"),
    "two_predictor_ols":("x1","x2","y"),
    "compound_interest":("principal","rate","periods"),
    "cobb_douglas_integer":("capital","labor","scale","alpha","beta"),
    "harmonic_mean":("values",),
    "logistic_odds":("odds","threshold"),
    "reflection_squared_distance":("p","q"),
    "round_robin_match_count":("teams",),
    "survey_ht":("values","inclusion_probabilities"),
}

def require(condition, message):
    if not condition:raise ConditionsNotEstablished(message)

def f(x:Any)->Fraction:
    require(type(x) in (int,Fraction),"exact int or Fraction required; no float or bool")
    return Fraction(x)

def integer(x,minimum=0,maximum=100):
    require(type(x) is int and minimum<=x<=maximum,"integer parameter outside bounded domain")
    return x

def seq(x,lower=1,upper=100):
    require(isinstance(x,(tuple,list)) and lower<=len(x)<=upper,"sample length out of bounds")
    return tuple(f(v) for v in x)

def vec(x,n):
    require(isinstance(x,(tuple,list)) and len(x)==n,"vector shape invalid")
    return tuple(f(v) for v in x)

def det3(m):
    a,b,c=m
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])

def solve3(matrix,rhs):
    d=det3(matrix)
    require(d!=0,"singular 3x3 design matrix")
    solution=[]
    for j in range(3):
        altered=tuple(tuple(rhs[i] if k==j else matrix[i][k] for k in range(3)) for i in range(3))
        solution.append(det3(altered)/d)
    require(all(sum(matrix[i][j]*solution[j] for j in range(3))==rhs[i] for i in range(3)),"exact 3x3 reconstruction failed")
    return tuple(solution),d

def check(op:str,**kw)->dict:
    require(op in FIELDS,"unsupported finite elective witness")
    require(set(kw)==set(FIELDS[op]),"missing/extra parameter or forged approval")
    if op=="epsilon_n_tail":
        eps=f(kw["epsilon"]);N=integer(kw["N"],1,100000)
        require(eps>0,"epsilon must be strictly positive")
        require(Fraction(1,N)<eps,"N not a valid witness for the tail of 1/n")
        out={"epsilon":eps,"N":N,"tail_bound":Fraction(1,N),"model":"1/n for positive n"}
    elif op=="cramer3":
        m=tuple(vec(row,3) for row in kw["matrix"]) if isinstance(kw["matrix"],(tuple,list)) and len(kw["matrix"])==3 else None
        require(m is not None,"3x3 matrix required")
        rhs=vec(kw["rhs"],3)
        x,d=solve3(m,rhs)
        out={"solution":x,"determinant":d}
    elif op=="vector_cross":
        u=vec(kw["left"],3);v=vec(kw["right"],3)
        z=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        require(sum(z[i]*u[i] for i in range(3))==sum(z[i]*v[i] for i in range(3))==0,"cross orthogonality failed")
        out={"cross":z,"squared_area":sum(t*t for t in z),"degenerate":z==(0,0,0)}
    elif op=="uniform_interval_probability":
        a,b,x,y=(f(kw[k]) for k in ("a","b","x","y"))
        require(a<b and a<=x<=y<=b,"uniform interval support invalid")
        out={"probability":(y-x)/(b-a),"endpoint_point_mass":Fraction(0)}
    elif op=="bernoulli_mle":
        raw=kw["observations"]
        require(isinstance(raw,(tuple,list)) and 1<=len(raw)<=1000 and all(type(t) is int and t in (0,1) for t in raw),"nonbinary observations or sample size")
        out={"successes":sum(raw),"n":len(raw),"estimate":Fraction(sum(raw),len(raw)),"warning":"not an interval estimate"}
    elif op=="t_statistic_squared":
        sample=seq(kw["observations"],2);mu=f(kw["mu0"])
        n=len(sample);mean=sum(sample)/n;var=sum((x-mean)**2 for x in sample)/(n-1)
        require(var>0,"zero sample variance: t statistic not defined")
        out={"sample_mean":mean,"sample_variance":var,"t_squared":n*(mean-mu)**2/var,"warning":"not a p-value"}
    elif op=="two_predictor_ols":
        x1,x2,y=(seq(kw[k],3,100) for k in ("x1","x2","y"))
        require(len(x1)==len(x2)==len(y),"unpaired regression data")
        vectors=list(zip((Fraction(1) for _ in x1),x1,x2))
        m=tuple(tuple(sum(row[i]*row[j] for row in vectors) for j in range(3)) for i in range(3))
        rhs=tuple(sum(row[i]*target for row,target in zip(vectors,y)) for i in range(3))
        coeff,det=solve3(m,rhs)
        residual=tuple(t-sum(row[j]*coeff[j] for j in range(3)) for row,t in zip(vectors,y))
        require(all(sum(row[j]*r for row,r in zip(vectors,residual))==0 for j in range(3)),"normal equations failed")
        out={"coefficients":coeff,"normal_determinant":det,"squared_error":sum(t*t for t in residual),"warning":"association not causation"}
    elif op=="compound_interest":
        p,r=f(kw["principal"]),f(kw["rate"]);n=integer(kw["periods"],0,100)
        require(p>=0 and r>-1,"nonnegative principal and positive gross rate required")
        out={"future_value":p*(1+r)**n,"periods":n,"model":"fixed rate, discrete compounding"}
    elif op=="cobb_douglas_integer":
        K,L,A=(f(kw[k]) for k in ("capital","labor","scale"))
        alpha,beta=(integer(kw[k],0,8) for k in ("alpha","beta"))
        require(K>0 and L>0 and A>0,"positive inputs needed for economic model")
        out={"production":A*K**alpha*L**beta,"double_capital_factor":Fraction(2)**alpha,
             "double_labor_factor":Fraction(2)**beta,"warning":"integer-exponent finite model, not fitted elasticity"}
    elif op=="harmonic_mean":
        values=seq(kw["values"])
        require(all(x>0 for x in values),"harmonic mean requires positive observations")
        hm=len(values)/sum(Fraction(1,x) for x in values)
        mean=sum(values)/len(values)
        require(min(values)<=hm<=mean,"harmonic arithmetic inequality failed")
        out={"harmonic_mean":hm,"arithmetic_mean":mean}
    elif op=="logistic_odds":
        odds,threshold=f(kw["odds"]),f(kw["threshold"])
        require(odds>0 and 0<=threshold<=1,"positive odds and probability threshold required")
        prob=odds/(1+odds)
        out={"probability":prob,"threshold_decision":int(prob>=threshold),"warning":"score not true label or calibration evidence"}
    elif op=="reflection_squared_distance":
        p,q=vec(kw["p"],2),vec(kw["q"],2)
        reflect=lambda a:(a[0],-a[1])
        rp,rq=reflect(p),reflect(q)
        d=sum((p[i]-q[i])**2 for i in range(2))
        rd=sum((rp[i]-rq[i])**2 for i in range(2))
        require(d==rd,"reflection squared distance invariant broken")
        out={"squared_distance":d,"reflected_squared_distance":rd}
    elif op=="round_robin_match_count":
        n=integer(kw["teams"],2,100)
        pairs={(i,j) for i in range(n) for j in range(i+1,n)}
        require(len(pairs)==n*(n-1)//2,"unordered game count mismatch")
        out={"teams":n,"matches":len(pairs),"model":"one match per unordered pair"}
    else:
        vals=seq(kw["values"]);prob=seq(kw["inclusion_probabilities"])
        require(len(vals)==len(prob) and all(0<p<=1 for p in prob),"paired nonzero inclusion probabilities required")
        out={"weighted_sample_total":sum(v/p for v,p in zip(vals,prob)),"warning":"one sample does not establish unbiased survey design"}
    return {"operation":op,"status":"FINITE_EXACT_CASE_ONLY","scope":"NOT_FORMAL_GENERAL_PROOF",
            "official_atom_certified":False,"teacher_approved":False,
            "student_solution_verified":False,"values":out}
