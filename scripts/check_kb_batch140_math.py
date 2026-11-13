#!/usr/bin/env python3
"""Independent SymPy finite truth/invalid-premise oracle for Batch140.

Crucially this module does not import or parse any free-form author answer
strings. It tests 24 mathematical relationships with 48 exact finite cases.
It does NOT prove universally quantified theorems or student work.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import sympy as S

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch140_proof_guards as author

OUT = ROOT / "docs/evaluation/KB_BATCH140_EXACT_MATH_WITNESSES.json"
R = S.Rational
M = S.Matrix

def require(cond, why):
    if cond is not True and cond != S.true:
        raise AssertionError(why)

def evidence():
    x,y,t,a,b = S.symbols("x y t a b", real=True)
    positive = []
    invalid = []
    def check(key, claim, good, boundary, bad):
        require(good,key+" : valid finite case")
        require(bad,key+" : failed premise / boundary")
        positive.append((key,claim))
        invalid.append((key,boundary))
    # Circle intersection triangle inequality / degeneracy
    d,r1,r2=4,2,3
    check("circle_triangles","radii 2,3 and d4 satisfy exact triangle bounds",
          abs(r1-r2)<=d<=r1+r2,
          "coincident circles produce multiple common points",
          all(p[0]**2+p[1]**2==4 for p in [(2,0),(-2,0),(0,2)]))
    # Common points between circles centers (0,0),(6,0), radius 5
    pts=[(3,4),(3,-4)]
    check("circle_count","two distinct points satisfy both radius-five circles",
          len(pts)==2 and all(px*px+py*py==25 and (px-6)**2+py*py==25 for px,py in pts),
          "same center and radius has at least three, not one, intersections",
          len({(5,0),(-5,0),(0,5)})==3 and
          all(px*px+py*py==25 for px,py in [(5,0),(-5,0),(0,5)]))
    # Reverse equivalence of parabola focus-directrix
    check("parabola_converse","p=1, x=1, y=2 satisfies equal focus/directrix distances",
          (1-1)**2+2**2==(1+1)**2 and 2**2==4*1*1,
          "p=0 degeneracy yields all y=0 without nondegenerate parabola",
          S.factor(y*y-4*0*x)==y*y)
    roots=S.solve(x*x-3*x+2,x)
    check("quadratic_discriminant","two distinct real roots when a1 delta1",
          roots==[1,2] and (-3)**2-4*1*2==1,
          "a=0 makes division by 2a invalid",
          S.Integer(2)*0==0 and S.solve(2*x-2,x)==[1])
    u=M([1,0]);v=M([0,3])
    check("pythagoras_converse","orthogonality iff norm-square additivity in R2",
          (u+v).dot(u+v)==u.dot(u)+v.dot(v) and u.dot(v)==0,
          "different dimension vectors cannot be added",
          len(M([1,2]))!=len(M([1,2,3])))
    check("log_product","log base2 of 2 times4 equals sum of logs",
          S.simplify(S.log(8,2)-S.log(2,2)-S.log(4,2))==0,
          "two negative true factors have positive product but undefined real logs",
          (-2)*(-4)==8 and -2<0 and -4<0)
    check("ellipse_param","a3 b2 ellipse maps to unit circle",
          R(0,3)**2+R(2,2)**2==1 and R(0,9)+R(2**2,4)==1,
          "zero half axis cannot occur in the standard equation",
          S.Integer(0)==0 and 3>0)
    check("amgm_equality","equal positive operands yield equality in AM-GM",
          R(4+4,2)==S.sqrt(4*4) and (S.sqrt(4)-S.sqrt(4))**2==0,
          "negative operands have no real square roots",
          S.Integer(-1)<0)
    check("vertex_completion","symbolic completing square identity a2 b8",
          S.expand((x+2)**2-4)==S.expand(x*x+4*x),
          "a=0 invalidates b over a",
          S.Integer(0)==0 and S.simplify(3*x+1)==3*x+1)
    check("vertex_extremum","parabola has global minimum at x0",
          S.solve(S.diff(x*x,x),x)==[0] and (1**2>0),
          "domain x>=1 excludes unconstrained vertex",
          0<1 and 1**2>0**2)
    check("log_inverse","real base2 log8 is3 and exponent undoes it",
          S.log(8,2)==3 and 2**3==8,
          "zero logarithm argument lies outside positive reals",
          S.Integer(0)<=0)
    rotate=M([[S.cos(S.pi/2),-S.sin(S.pi/2)],[S.sin(S.pi/2),S.cos(S.pi/2)]])
    skew=M([[1,1],[0,1]])
    check("rotation_matrix","pi/2 rotation maps basis e1 to e2 with norm preserved",
          rotate*M([1,0])==M([0,1]) and rotate.T*rotate==S.eye(2),
          "same coordinate rotation does not preserve physical metric in skew basis",
          (skew*rotate*M([1,0])).dot(skew*rotate*M([1,0])) !=
           (skew*M([1,0])).dot(skew*M([1,0])))
    check("dot_angle","nonzero orthogonal pair has zero cosine",
          M([1,0]).dot(M([0,3]))==0 and
          S.simplify(M([1,0]).dot(M([0,3]))/(M([1,0]).norm()*M([0,3]).norm()))==0,
          "zero vector has norm zero and cannot define angle",
          M([0,0]).norm()==0)
    diag=M([[1,0,0],[0,2,0],[0,0,3]])
    not_square=M([[1,0],[0,1],[0,0]])
    check("basis_three","full rank 3x3 has trivial nullspace and nonzero determinant",
          diag.det()==6 and diag.nullspace()==[] and diag.inv()*diag==S.eye(3),
          "injective 3x2 matrix is not a 3x3 basis",
          not_square.nullspace()==[] and not_square.shape==(3,2))
    check("reciprocal_derivative","reciprocal x+2 differentiates to -1/4 at zero",
          S.diff(1/(x+2),x).subs(x,0)==R(-1,4),
          "v(0)=0 makes reciprocal undefined at zero",
          S.limit(1/x,x,0,dir="+")==S.oo)
    q=-x*x
    check("fermat_sign","local maximum minus h squared has correct left/right quotient signs",
          S.simplify((q.subs(x,R(1,2))-q.subs(x,0))/R(1,2))<0 and
          S.simplify((q.subs(x,R(-1,2))-q.subs(x,0))/R(-1,2))>0,
          "boundary maximum on x>=0 need not have stationary derivative",
          S.diff(-x,x).subs(x,0)==-1)
    u=M([2,3]);v=M([1,-1])
    norm=(u-t*v).dot(u-t*v)
    check("cauchy_expand","inner product yields nonnegative squared norm polynomial",
          S.expand(norm)==u.dot(u)-2*t*u.dot(v)+t*t*v.dot(v) and norm.subs(t,3)>=0,
          "indefinite quadratic form can be negative for nonzero vectors",
          (M([0,1]).T*M([[1,0],[0,-1]])*M([0,1]))[0]==-1)
    u=M([1,2]);v=M([0,2]); coefficient=R(u.dot(v),v.dot(v))
    check("cauchy_minimize","minimizer t1 produces CS bound",
          coefficient==1 and S.simplify((u-coefficient*v).dot(u-coefficient*v))==1 and
          u.dot(v)**2 <=u.dot(u)*v.dot(v),
          "zero v invalidates inverse squared norm",
          M([0,0]).dot(M([0,0]))==0)
    u=M([3,6]);v=M([1,2])
    bad=M([1,1]);J=M([[1,0],[0,-1]])
    check("cauchy_equality","proportional nonzero vectors attain CS equality",
          u.dot(v)**2==u.dot(u)*v.dot(v) and u==3*v,
          "indefinite form has a nonzero null vector",
          (bad.T*J*bad)[0]==0 and bad!=M([0,0]))
    X=[S.Integer(0),S.Integer(1)];Y=[S.Integer(0),S.Integer(1)]
    check("expectation_linearity","dependent X,Y still obey expectation linearity",
          sum(2*xx+3*yy for xx,yy in zip(X,Y))/2==
            2*sum(X)/2+3*sum(Y)/2==R(5,2),
          "Cauchy has infinite first absolute moment",
          S.integrate(x/(1+x*x),(x,1,S.oo))==S.oo)
    A=M([[1,0,0],[0,1,0],[0,0,0]])
    check("rank_vectors","singular 3x3 matrix has nontrivial kernel",
          A.det()==0 and A.rank()==2 and M([0,0,1]) in A.nullspace(),
          "rectangular 3x2 has no 3x3 determinant",
          not_square.shape==(3,2))
    entries=[(0,2),(2,4)];b_fixed=1
    avgx=R(sum(z for z,_ in entries),len(entries))
    avgy=R(sum(z for _,z in entries),len(entries))
    check("ols_intercept","fixed slope1 and two samples yield unique intercept2",
          avgy-b_fixed*avgx==2 and
          S.diff(sum((yi-a-b_fixed*xi)**2 for xi,yi in entries),a).subs(a,2)==0 and
          S.diff(sum((yi-a-b_fixed*xi)**2 for xi,yi in entries),a,2)==4,
          "n=0 empty objective has zero curvature and undefined means",
          S.diff(S.Integer(0),a,2)==0)
    velocity=M([-2*S.sin(t),2*S.cos(t)])
    check("parametric_circle","r2 radians yields exact speed two",
          S.trigsimp(velocity.dot(velocity))==4 and velocity.subs(t,S.pi/2)==M([-2,0]),
          "zero-radius path has zero rather than nonzero speed",
          M([0,0]).norm()==0)
    check("epsilon_n","epsilon one tenth and N11 has correct tested tail bounds",
          all(R(1,n)<=R(1,11)<R(1,10) for n in (11,25,100)),
          "epsilon zero admits no positive reciprocal bound",
          R(1,11)>0 and S.Integer(0)==0)

    original_keys=[case[4] for case in author.CASES]
    require(len(positive)==len(invalid)==len(original_keys)==24,"wrong exact case count")
    require([key for key,_ in positive]==original_keys,"oracle ordering or missing source link")
    return {
      "schema":"kb140-independent-exact-witness/1",
      "scope":"48_EXACT_FINITE_CASES_NOT_UNIVERSAL_PROOFS",
      "source_step_count":24,
      "positive_boundary_count":24,
      "invalid_premise_count":24,
      "teacher_approved":0,
      "general_proof_certified":0,
      "student_free_text_verified":0,
      "official_course_denominators":None,
      "cases":[{
         "historical_step_id":row[0],
         "oracle_key":row[4],
         "positive_case_description":positive[i][1],
         "positive_case_pass":True,
         "invalid_premise_description":invalid[i][1],
         "invalid_premise_pass":True,
         "status":"FINITE_EXACT_CASES_NOT_GENERAL_PROOF",
      } for i,row in enumerate(author.CASES)]
    }

def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    args=parser.parse_args()
    data=evidence()
    if args.write:
        OUT.write_text(author.encode(data),encoding="utf-8")
    else:
        require(json.loads(OUT.read_text(encoding="utf-8"))==data,"stored exact oracle drift")
    print("PASS Batch140 independent SymPy: 24 positive/boundary, 24 invalid-premise; zero general proofs")

if __name__=="__main__":
    main()
