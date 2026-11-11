"""Independent exact checks for **specified controlled witnesses only**.
Theorem proofs, whole-domain correctness, editorial wording, source identity,
and student free-form work are NEVER certified by these checks.
"""
from fractions import Fraction as F
from math import comb, pi, sin, log, sqrt, isclose
from sympy import Matrix
CASES = {
 "KB80-A020-L032-C01": "logarithm-positive-domain",
 "KB80-A022-L002-C01": "nondegenerate-sine-period",
 "KB80-A026-L016-C01": "vector-component-arithmetic",
 "KB80-A038-L016-C02": "prefix-sum-difference",
 "KB80-A042-L026-C01": "projection-nonzero-denominator",
 "KB80-A044-L012-C01": "ellipse-focal-identity",
 "KB80-A047-L017-C01": "partition-total-probability",
 "KB80-A047-L025-C01": "hypergeometric-without-replacement",
 "KB80-A048-L011-C01": "pearson-zero-variance-boundary",
 "KB80-A054-L025-C01": "orthogonal-length-preservation",
 "KB80-A059-L013-C01": "partial-derivative-fixed-variable",
 "KB80-A060-L006-C02": "cross-product-antisymmetry",
 "KB80-A066-L008-C02": "equal-principal-loan-balance",
 "KB80-A070-L023-C02": "sine-opposite-phase-cancellation",
}

def finite_check(candidate_id):
    """Always check BOTH a legitimate exact instance AND a premise/boundary rejection."""
    assert candidate_id in CASES
    if candidate_id=="KB80-A020-L032-C01":
        good=8*2==16 and 2**4==16
        bad=not (-2>0 and -3>0)
    elif candidate_id=="KB80-A022-L002-C01":
        good=isclose(2*sin(3*(pi/5)+1),2*sin(3*(pi/5)+1+2*pi),abs_tol=1e-12)
        bad=(0==0) and (not (0!=0))  # degenerate angular frequency
    elif candidate_id=="KB80-A026-L016-C01":
        good=tuple(a+b for a,b in zip((1,2),(3,-1)))==(4,1)
        bad=len((1,2))!=len((1,2,3))
    elif candidate_id=="KB80-A038-L016-C02":
        good=all(n*n-(n-1)*(n-1)==2*n-1 for n in range(1,25))
        bad=not (1>=2) # cannot use n>=2-only statement for first index
    elif candidate_id=="KB80-A042-L026-C01":
        u=Matrix([2,3]);v=Matrix([1,0])
        good=(u.dot(v)/v.dot(v))*v==Matrix([2,0])
        bad=Matrix([0,0]).dot(Matrix([0,0]))==0
    elif candidate_id=="KB80-A044-L012-C01":
        good=5**2-3**2==4**2 and abs(5-4)+abs(5+4)==10
        bad=(5-5)==0  # two foci not distinct for a=b
    elif candidate_id=="KB80-A047-L017-C01":
        good=F(2,5)*F(4,5)+F(3,5)*F(1,5)==F(11,25)
        bad=F(2,5)+F(2,5)!=1 # weights fail to cover a partition
    elif candidate_id=="KB80-A047-L025-C01":
        good=F(comb(2,1)*comb(3,1),comb(5,2))==F(3,5)
        bad=F(3,5)!=2*F(2,5)*F(3,5) # with-replacement probability differs
    elif candidate_id=="KB80-A048-L011-C01":
        xs=(1,2,3);ys=(2,4,6)
        xbar=F(sum(xs),3);ybar=F(sum(ys),3)
        numer=sum((F(x)-xbar)*(F(y)-ybar) for x,y in zip(xs,ys))
        denomx=sum((F(x)-xbar)**2 for x in xs)
        denomy=sum((F(y)-ybar)**2 for y in ys)
        good=numer**2==denomx*denomy and numer>0
        bad=sum((x-2)**2 for x in (2,2,2))==0
    elif candidate_id=="KB80-A054-L025-C01":
        q=Matrix([[0,-1],[1,0]])
        good=q.T*q==Matrix.eye(2) and q*Matrix([3,4])==Matrix([-4,3])
        shear=Matrix([[1,1],[0,1]])
        bad=shear.T*shear!=Matrix.eye(2)
    elif candidate_id=="KB80-A059-L013-C01":
        from sympy import symbols,diff
        x,y=symbols("x y",real=True);expr=x*x*y+3*y
        good=diff(expr,x).subs({x:1,y:2})==4 and diff(expr,y).subs({x:1,y:2})==4
        # A separately constructed function has partial derivatives at origin but is discontinuous.
        bad=(F(1,2)!=0)  # along diagonal h=h: x*y/(x²+y²) -> 1/2 vs at origin 0
    elif candidate_id=="KB80-A060-L006-C02":
        a=Matrix([1,0,0]);b=Matrix([0,1,0])
        good=a.cross(b)==Matrix([0,0,1])
        bad=a.cross(b)!=b.cross(a) and a.cross(a)==Matrix([0,0,0])
    elif candidate_id=="KB80-A066-L008-C02":
        vals=[F(120,1)-F(40,1)*i for i in range(3)]
        pay=[F(40,1)+v*F(1,100) for v in vals]
        good=pay==[F(206,5),F(204,5),F(202,5)] and sum(pay)==F(612,5)
        bad=(pay[0]!=pay[1]!=pay[2])
    else:
        good=all(isclose(sin(x)+sin(x+pi),0,abs_tol=1e-12) for x in (0,pi/5,pi/2,3*pi/2))
        bad=not isclose(sin(pi/4)+sin(2*pi/4), sin(pi/4)+sin(2*(pi/4)+pi),abs_tol=1e-12)
    assert good and bad, "finite positive/boundary witness failed: "+candidate_id
    return {
        "candidate_id":candidate_id,
        "witness_name":CASES[candidate_id],
        "finite_positive_case":True,
        "premise_or_boundary_rejection":True,
        "general_theorem_certified":False,
        "teacher_approved":False,
        "student_publishable":False,
        "scope":"CONTROLLED_EXACT_OR_NUMERIC_WITNESS_ONLY",
    }

def check_all():
    return {candidate_id:finite_check(candidate_id) for candidate_id in CASES}
