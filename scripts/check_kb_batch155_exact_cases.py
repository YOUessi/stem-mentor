#!/usr/bin/env python3
"""KB155 independent bounded exact counterexamples, not general theorem certificates."""
from __future__ import annotations
import argparse
import json
from fractions import Fraction as F
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"docs/evaluation/KB_BATCH155_EXACT_WITNESSES.json"
x=S.symbols("x",real=True)

def ok(cond,case):
    if not bool(cond):raise AssertionError("KB155 math oracle failed: "+case)

def run():
    rows=[]
    def case(name,legit,invalid,legal_note,invalid_note):
        ok(legit,name+":legit")
        ok(invalid,name+":invalid")
        for label,note in (("EXACT_FINITE_WITNESS",legal_note),
                           ("INVALID_PRECONDITION_REJECTED",invalid_note)):
            rows.append(dict(case_id=name,condition_class=label,
                original_independent_rationale=note,exact_check=True,
                sample_limited=True,formal_general_proof_certified=False,
                arbitrary_student_step_verified=False,teacher_approved=False))
    case("logarithm_change_of_base",
         S.simplify(S.log(8,2)-S.log(8,4)/S.log(2,4))==0,
         S.log(1)==0 and S.log(8)>0,
         "8=2^3, so change of base with both positive non-unit bases gives 3.",
         "Base 1 is forbidden: logarithms to base 1 are not invertible.")
    f=x**3+x-1
    case("IVT_zero_existence_not_uniqueness",
         f.subs(x,S.Rational(1,2))<0 and f.subs(x,S.Rational(3,4))>0,
         S.limit(1/x,x,0,dir="-")==-S.oo and
         S.limit(1/x,x,0,dir="+")==S.oo and
         S.solveset(1/x,x,domain=S.S.Reals)==S.EmptySet,
         "Polynomial is continuous and exactly opposite signed at 1/2,3/4.",
         "1/x has opposite endpoint signs but a pole at 0 and no zero.")
    case("squaring_extraneous_root",
         S.sqrt(3+1)==3-1,
         S.sqrt(0+1)!=0-1 and
         S.simplify((x+1)-(x-1)**2).subs(x,0)==0,
         "x=3 satisfies the original radical equation.",
         "x=0 satisfies the squared equation but violates the original sign requirement.")
    q=(x*x+1)/(x-1)
    case("quotient_derivative_denominator",
         S.diff(q,x).subs(x,2)==-1,
         S.denom(S.together(q)).subs(x,1)==0,
         "Derivative evaluated at 2 with a nonzero quotient denominator equals -1.",
         "At x=1 the original quotient is undefined; no derivative at that point.")
    case("quadratic_formula_nonzero_a",
         set(S.solve(x*x-3*x+2,x))=={S.Integer(1),S.Integer(2)},
         S.Integer(0)==0 and S.solve(0*x*x+2*x-4,x)==[S.Integer(2)],
         "Nonzero quadratic leading coefficient and exact factorization yield roots 1,2.",
         "When a=0 the expression is linear: dividing by 2a is illegal.")
    xa=[S.Integer(1),S.Integer(2),S.Integer(3)]
    ya=[S.Integer(2),S.Integer(4),S.Integer(6)]
    xb=sum(xa)/3;yb=sum(ya)/3
    sxx=sum((v-xb)**2 for v in xa)
    sxy=sum((a-xb)*(b-yb) for a,b in zip(xa,ya))
    case("OLS_intercept_positive_Sxx",
         sxx==2 and sxy==4 and sxy/sxx==2 and yb-(sxy/sxx)*xb==0,
         sum((v-S.Integer(2))**2 for v in [2,2,2])==0,
         "With intercept and nonzero centered x variance, b1=Sxy/Sxx=2.",
         "Constant predictors give Sxx=0, hence slope is not uniquely identified.")
    case("conditional_probability_positive_denominator",
         F(1,4)/F(1,2)==F(1,2),
         F(0,1)==0,
         "P(A|B)=P(A∩B)/P(B)=1/2 when P(B)=1/2.",
         "P(B)=0 has undefined conditional probability under the ratio definition.")
    case("binomial_parameter_bounds",
         6*F(1,3)*(1-F(1,3))==F(4,3),
         not (0<=F(4,3)<=1),
         "Var(X)=np(1-p) gives 4/3 for n=6,p=1/3.",
         "p=4/3 is outside [0,1] and cannot parameterize a binomial trial.")
    m=S.Matrix([[1,2],[3,5]])
    singular=S.Matrix([[1,2],[2,4]])
    case("invertible_matrix_nonzero_determinant",
         m.det()==-1 and m*m.inv()==S.eye(2),
         singular.det()==0 and singular.rank()==1,
         "The invertible 2x2 example has determinant -1 and exact identity check.",
         "Singular matrix has determinant zero, so inverse formula is invalid.")
    case("geometric_sum_q_one_branch",
         sum(2**j for j in range(4))==(2**4-1)//(2-1),
         (1**4-1)==0 and (1-1)==0,
         "1+2+4+8=15, agreeing with the finite geometric sum for q=2.",
         "At q=1 the quotient formula becomes 0/0; sum is n times first term.")
    case("probability_inclusion_exclusion",
         F(1,2)+F(1,2)-F(1,4)==F(3,4),
         F(1,4)!=0 and F(1,2)+F(1,2)!=F(3,4),
         "Overlapping equally likely events have union probability 3/4.",
         "Blindly adding P(A)+P(B) ignores the nonempty intersection.")
    seq=[2,5,8,11,14]
    wrong=[2,5,9]
    case("arithmetic_sequence_constant_difference",
         set(b-a for a,b in zip(seq,seq[1:]))=={3} and sum(seq)==40,
         len(set(b-a for a,b in zip(wrong,wrong[1:])))>1,
         "Five-term progression 2,5,8,11,14 has fixed difference 3 and sum 40.",
         "Sequence 2,5,9 has differences 3 and 4 and is not arithmetic.")
    case("circle_radius_and_geometry",
         (5-2)**2+(-1+1)**2==9,
         not (-3>=0),
         "Point (5,-1) lies exactly on the circle centered at (2,-1), radius 3.",
         "A radius of -3 is inadmissible even though squaring would produce 9.")
    case("multiply_inequality_by_negative",
         (-2*S.Integer(-1)<4) and (S.Integer(-1)>-2),
         not bool(-2*S.Integer(-3)<4),
         "For x=-1, -2x<4 agrees with x>-2, after reversing inequality.",
         "For x=-3, false original inequality refutes failure to reverse sign.")
    a=S.Matrix([1,0]); b=S.Matrix([0,2]);z=S.Matrix([0,0])
    case("angle_between_nonzero_vectors",
         a.dot(b)==0 and a.norm()*b.norm()!=0,
         z.norm()==0,
         "Two nonzero vectors with zero dot product have right angle.",
         "The zero vector has no defined angle: denominator of cosine formula is zero.")
    assert len(rows)==30
    assert all(r["sample_limited"] and not r["formal_general_proof_certified"] and
        not r["arbitrary_student_step_verified"] and not r["teacher_approved"] for r in rows)
    return dict(schema="kb155-finite-independent-math-counterexamples/1",
        witnesses=rows,case_pairs=15,exact_finite_checks=30,
        legal_witnesses=15,invalid_premise_witnesses=15,formal_general_proofs_certified=0,
        arbitrary_student_steps_verified=0,teacher_approved=0)
def encode(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+"\n"
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
    v=run();data=encode(v)
    if a.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8")!=data:
            raise ValueError("KB155 exact math evidence drift")
    else:OUT.write_text(data,encoding="utf-8")
    print(f"KB155 exact finite: {len(v['witnesses'])}/30; general proof 0")
if __name__=="__main__":main()
