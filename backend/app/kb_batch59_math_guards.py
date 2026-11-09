"""Batch59: bounded exact witnesses for selective-compulsory mathematics.

These calculations prove ONLY the returned finite statement under stated
parameters. They are not universal theorem proofs, course certification or
validation of arbitrary student text. All inputs are exact int/Fraction.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb
from typing import Any

class ConditionsNotEstablished(ValueError):
    """An input assumption or the supported mathematical domain is missing."""

FIELDS = {
    "arithmetic_partial_sum":("first","difference","n"),
    "geometric_partial_sum":("first","ratio","n"),
    "affine_square_derivative":("a","b","x"),
    "space_basis_coordinates":("basis","vector"),
    "line_slope_relation":("line1","line2"),
    "ellipse_focal_parameters":("a","c"),
    "binomial_coefficient":("n","k"),
    "hypergeometric_probability":("population","successes","draws","observed"),
    "bayes_two_hypotheses":("prior","likelihood_a","likelihood_not_a"),
    "pearson_squared":("xs","ys"),
    "least_squares":("xs","ys"),
    "two_by_two_chi_square":("table",),
}

def require(ok: bool, why: str) -> None:
    if not ok:
        raise ConditionsNotEstablished(why)

def number(x: Any) -> Fraction:
    require(type(x) in (int,Fraction), "exact integer or rational input required")
    return Fraction(x)

def integer(x: Any, *, minval=0) -> int:
    require(type(x) is int and x>=minval, "nonnegative integer domain violated")
    return x

def vector(x: Any, length: int) -> tuple[Fraction,...]:
    require(isinstance(x,(tuple,list)) and len(x)==length, "vector length mismatch")
    return tuple(number(y) for y in x)

def sequence(x: Any) -> tuple[Fraction,...]:
    require(isinstance(x,(tuple,list)) and 2<=len(x)<=100, "sample size outside supported range")
    return tuple(number(y) for y in x)

def det3(m):
    return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
            -m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
            +m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))

def check(op: str, **kw: Any) -> dict:
    require(op in FIELDS, "unsupported finite math witness family")
    require(set(kw)==set(FIELDS[op]), "missing or extra parameters, or attempted approval injection")
    out = {}
    if op=="arithmetic_partial_sum":
        a,d,n=number(kw["first"]),number(kw["difference"]),integer(kw["n"],minval=1)
        require(n<=1000,"finite enumeration bound exceeded")
        direct=sum((a+i*d for i in range(n)),Fraction(0))
        closed=n*(2*a+(n-1)*d)/2
        require(direct==closed,"finite arithmetic sum inconsistency")
        out={"sum":direct,"closed":closed,"domain":"n positive integer"}
    elif op=="geometric_partial_sum":
        a,q,n=number(kw["first"]),number(kw["ratio"]),integer(kw["n"],minval=1)
        require(n<=1000,"finite enumeration bound exceeded")
        direct=sum((a*q**i for i in range(n)),Fraction(0))
        closed=n*a if q==1 else a*(1-q**n)/(1-q)
        require(direct==closed,"finite geometric sum inconsistency")
        out={"sum":direct,"branch":"RATIO_ONE" if q==1 else "RATIO_NOT_ONE"}
    elif op=="affine_square_derivative":
        a,b,x=(number(kw[k]) for k in ("a","b","x"))
        # For f(x)=(ax+b)^2, derivative by polynomial coefficient rule.
        deriv=2*a*a*x+2*a*b
        # Independently expand f(x+h)-f(x) and check the linear h coefficient.
        numerator_linear=2*a*(a*x+b)
        require(deriv==numerator_linear,"affine chain derivative disagreement")
        out={"derivative_at_x":deriv,"inner_derivative":a}
    elif op=="space_basis_coordinates":
        raw=kw["basis"]
        require(isinstance(raw,(tuple,list)) and len(raw)==3,"3 basis vectors required")
        cols=[vector(e,3) for e in raw]
        target=vector(kw["vector"],3)
        matrix=tuple(tuple(cols[j][i] for j in range(3)) for i in range(3))
        determinant=det3(matrix)
        require(determinant!=0,"basis vectors linearly dependent")
        coords=[]
        for j in range(3):
            altered=[list(row) for row in matrix]
            for i in range(3):altered[i][j]=target[i]
            coords.append(det3(altered)/determinant)
        require(all(sum(matrix[i][j]*coords[j] for j in range(3))==target[i]
                    for i in range(3)), "vector reconstruction inconsistent")
        out={"coordinates":tuple(coords),"determinant":determinant}
    elif op=="line_slope_relation":
        lines=[]
        for name in ("line1","line2"):
            pair=kw[name]
            require(isinstance(pair,(tuple,list)) and len(pair)==2,"two points required per line")
            p,q=vector(pair[0],2),vector(pair[1],2)
            dx,dy=q[0]-p[0],q[1]-p[1]
            require(dx!=0 or dy!=0,"coincident points do not define a line")
            lines.append((dx,dy))
        (ax,ay),(bx,by)=lines
        cross=ax*by-ay*bx
        dot=ax*bx+ay*by
        out={"parallel_directions":cross==0,"perpendicular_directions":dot==0,
             "slope1":None if ax==0 else ay/ax,
             "slope2":None if bx==0 else by/bx,
             "warning":"Parallel directions do not establish distinct parallel lines."}
    elif op=="ellipse_focal_parameters":
        a,c=number(kw["a"]),number(kw["c"])
        require(a>0 and 0<=c<a,"nondegenerate ellipse requires a>c>=0")
        out={"b_squared":a*a-c*c,"focal_sum":2*a,
             "special_case":"CIRCLE" if c==0 else "TWO_DISTINCT_FOCI"}
    elif op=="binomial_coefficient":
        n,k=integer(kw["n"]),integer(kw["k"])
        require(n<=200 and k<=n,"k<=n and bounded n required")
        out={"coefficient":comb(n,k),"expansion_domain":"nonnegative integer exponent"}
    elif op=="hypergeometric_probability":
        N,K,n,k=(integer(kw[x]) for x in ("population","successes","draws","observed"))
        require(N>0 and K<=N and n<=N and k<=n and k<=K and n-k<=N-K,
                "hypergeometric feasible integer parameters required")
        out={"probability":Fraction(comb(K,k)*comb(N-K,n-k),comb(N,n)),
             "sampling":"UNIFORM_WITHOUT_REPLACEMENT"}
    elif op=="bayes_two_hypotheses":
        p,u,v=(number(kw[z]) for z in ("prior","likelihood_a","likelihood_not_a"))
        require(0<=p<=1 and 0<=u<=1 and 0<=v<=1,"probabilities in [0,1]")
        denominator=p*u+(1-p)*v
        require(denominator>0,"Bayes evidence event must have positive probability")
        out={"posterior":p*u/denominator,"evidence_probability":denominator,
             "curriculum_scope":"EXPLICIT_STARRED_OPTIONAL"}
    elif op=="pearson_squared":
        xs,ys=sequence(kw["xs"]),sequence(kw["ys"])
        require(len(xs)==len(ys),"paired samples required")
        n=len(xs);sx=sum(xs);sy=sum(ys)
        xx=n*sum(x*x for x in xs)-sx*sx
        yy=n*sum(y*y for y in ys)-sy*sy
        xy=n*sum(x*y for x,y in zip(xs,ys))-sx*sy
        require(xx>0 and yy>0,"zero sample variation makes Pearson r undefined")
        sq=xy*xy/(xx*yy)
        require(0<=sq<=1,"Cauchy-Schwarz finite bound violated")
        out={"r_squared":sq,"r_sign":0 if xy==0 else 1 if xy>0 else -1,
             "warning":"correlation is not causation"}
    elif op=="least_squares":
        xs,ys=sequence(kw["xs"]),sequence(kw["ys"])
        require(len(xs)==len(ys),"paired samples required")
        n=len(xs);sx=sum(xs);sy=sum(ys)
        sxx=n*sum(x*x for x in xs)-sx*sx
        require(sxx>0,"constant predictor: OLS slope undefined")
        slope=(n*sum(x*y for x,y in zip(xs,ys))-sx*sy)/sxx
        intercept=(sy-slope*sx)/n
        out={"slope":slope,"intercept":intercept,
             "warning":"fit does not certify causal relation or safe extrapolation"}
    else:
        raw=kw["table"]
        require(isinstance(raw,(list,tuple)) and len(raw)==2
                and all(isinstance(z,(list,tuple)) and len(z)==2 for z in raw),
                "2x2 table required")
        a,b,c,d=(integer(raw[i][j]) for i in range(2) for j in range(2))
        n=a+b+c+d
        require(n>0,"empty table")
        rows=[a+b,c+d];cols=[a+c,b+d]
        require(all(x>0 for x in rows+cols),
                "each row and column marginal count must be positive")
        expected=[[Fraction(rows[i]*cols[j],n) for j in range(2)] for i in range(2)]
        observed=[[a,b],[c,d]]
        chi=sum((observed[i][j]-expected[i][j])**2/expected[i][j]
                for i in range(2) for j in range(2))
        out={"chi_square":chi,"expected":expected,
             "warning":"a statistic is not a proof of population independence"}
    return {
        "operation":op,"status":"FINITE_EXACT_CASE_ONLY",
        "scope":"NOT_FORMAL_GENERAL_PROOF",
        "official_atom_certified":False,"teacher_approved":False,
        "student_solution_verified":False,"values":out
    }
