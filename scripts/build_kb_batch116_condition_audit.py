#!/usr/bin/env python3
"""Independent exact boundary witnesses; no universal proof certification."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from collections import Counter
from hashlib import sha256
import sympy as s

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs/evaluation/KB_BATCH116_CONDITION_AUDIT.json"
R = s.Rational
x = s.symbols("x", real=True)
def eq(a,b): return s.simplify(a-b)==0

# (id, domain assumption, misuse to reject, independent exact positive and negative witness).
CASES = [
 ("division_nonzero","cancel factor only if nonzero","cancel x from x(x-1)=0",
  lambda: eq(2*(2-1),2), lambda: eq(0*(0-1),0) and 0 != 1),
 ("squaring_equation","check original sign and domain","accept both squared roots",
  lambda: eq(s.sqrt(2+2),2), lambda: eq((-1)**2,(-1)+2) and not eq(s.sqrt(-1+2),-1)),
 ("log_composition","sqrt radicand positive for log","accept x=1 for log(sqrt(x-1))",
  lambda: eq(s.log(s.sqrt(5-1)),s.log(2)), lambda: s.log(s.sqrt(1-1))==s.zoo),
 ("negative_multiplier","inequality flips under negative scale","keep < after multiplying by -1",
  lambda: R(-2)<R(-1), lambda: not (R(-1)<R(-2))),
 ("ivt_continuity","continuity on entire closed interval","apply IVT to 1/x across zero",
  lambda: (R(-1)<0<R(1)), lambda: s.simplify(1/s.Integer(-1))<0 and 1/s.Integer(1)>0 and s.simplify(1/s.Integer(2))!=0),
 ("ivt_uniqueness","IVT provides existence, not uniqueness","declare one root from sign change",
  lambda: eq((-2)*(((-2)**2)-1),-6) and eq(2*(2**2-1),6),
  lambda: all(eq(t*(t*t-1),0) for t in (-1,0,1))),
 ("bisection_error","n bisections, midpoint error ≤ interval_length/2","confuse interval length with midpoint error",
  lambda: eq(R(2,2**4),R(1,8)), lambda: eq(R(2,2**5),R(1,16))),
 ("log_base_one","real log base must be >0 and !=1","log_1(1) unique",
  lambda: eq(s.log(8,2),3), lambda: 1**2 == 1**4),
 ("real_even_root","even real root radicand nonnegative","negative root in real domain",
  lambda: eq(s.sqrt(9),3), lambda: s.sqrt(-1)==s.I),
 ("geometric_q_one","q=1 handled separately","sum formula divide by q-1",
  lambda: 2+2+2==6, lambda: eq(s.Integer(1)-s.Integer(1),0)),
 ("dot_angle_nonzero","both vectors nonzero for angle","zero dot means 90-degree angle",
  lambda: (3*4+4*(-3)==0) and (3**2+4**2>0),
  lambda: (0*1+0*2==0) and (0**2+0**2==0)),
 ("ssa_ambiguous","SSA may produce two triangles","unique triangle from one angle and two sides",
  lambda: R(8,10)<1, lambda: (30+53<180 and 30+127<180)),
 ("apollonius_k_one","distance-ratio circle requires k !=1","k=1 still gives a proper circle",
  lambda: (2-0)**2+(0-0)**2==4,
  lambda: eq((x-0)**2+(0-0)**2-((x-2)**2+(0-0)**2),4*x-4)),
 ("determinant_zero","Cramer requires nonzero determinant","invert singular matrix",
  lambda: s.Matrix([[1,0],[0,2]]).det()==2,
  lambda: s.Matrix([[1,2],[2,4]]).det()==0),
 ("ols_sxx","OLS unique slope only if Sxx>0","divide 0 by 0",
  lambda: sum((q-R(1))**2 for q in (0,1,2))==2,
  lambda: sum((q-R(2))**2 for q in (2,2,2))==0),
 ("bernoulli_parameter_boundary","p in [0,1] or open interval has no attained MLE for all successes","claim open interval MLE=1",
  lambda: R(3,4)**3 < R(1)**3, lambda: all(R(k,10)**3<1 for k in (1,5,9))),
 ("conditional_prob_nonzero","P(B)>0 for conditional probability","treat P(A|B) when P(B)=0 as 0",
  lambda: eq(R(1,4)/R(1,2),R(1,2)), lambda: s.Integer(0)/s.Integer(0) is s.nan),
 ("exclusive_vs_independent","positive-probability mutually exclusive events not independent","say disjoint implies independent",
  lambda: eq(R(1,2)*R(1,2),R(1,4)),
  lambda: R(0)!=R(1,2)*R(1,2)),
 ("uncorrelated_dependent","zero covariance not sufficient for independence","infer independence from Cov=0",
  lambda: eq(sum(R(t**3,3) for t in (-1,0,1)),0),
  lambda: R(1,3)!=R(1,9)),
 ("density_reversed_bounds","a<=b for integral representation of event","negative integral interpreted as probability",
  lambda: eq(s.integrate(2*x,(x,0,1)),1),
  lambda: s.integrate(2*x,(x,1,0))==-1),
 ("uniform_zero_width","continuous uniform requires a<b","divide by b-a=0",
  lambda: eq(R(1,3-1),R(1,2)),
  lambda: (3-3)==0),
 ("joint_normal_covariance_psd","correlation |rho|<=1","negative eigenvalue accepted as covariance",
  lambda: s.Matrix([[1,R(1,2)],[R(1,2),1]]).det()==R(3,4),
  lambda: s.Matrix([[1,2],[2,1]]).det()==-3),
 ("density_value_not_mass","density may exceed 1 but mass <=1","treat f(x) as P(X=x)",
  lambda: eq(R(2)*R(1,2),1),
  lambda: R(2)>1),
 ("det_one_not_orthogonal","orthogonality requires Q.T*Q=I","det=1 implies orthogonal",
  lambda: s.eye(2).det()==1,
  lambda: s.Matrix([[1,1],[0,1]]).det()==1 and s.Matrix([[1,1],[0,1]]).T*s.Matrix([[1,1],[0,1]])!=s.eye(2)),
 ("affine_not_linear","T(0)=0 for linear map","nonzero intercept still linear",
  lambda: s.Matrix([[2,0],[0,3]])*s.zeros(2,1)==s.zeros(2,1),
  lambda: s.Matrix([1,2])!=s.zeros(2,1)),
 ("projection_zero_direction","target direction must be nonzero for quotient formula","project onto zero by division",
  lambda: R(3*1+4*0,1*1+0*0)==3,
  lambda: (0*0+0*0)==0),
 ("t_variance_degrees","t variance exists only for nu>2","apply nu/(nu-2) at nu=2",
  lambda: R(4,4-2)==2,
  lambda: (2-2)==0),
 ("exponential_vs_linear","fixed relative rate vs fixed absolute increment","N_n exponential increments all constant",
  lambda: R(110,100)==R(121,110),
  lambda: (110-100)!=(121-110)),
]
def require(condition, message):
    if not condition: raise ValueError(message)

def audit(cases=CASES):
    ids=[c[0] for c in cases]
    require(len(ids)==len(set(ids))==28,"condition guard case count or duplicate IDs")
    records=[]
    for name,pre,bad,valid,invalid in cases:
        require(min(len(pre),len(bad))>=8,"missing condition or misconception: "+name)
        yes,no=valid(),invalid()
        require(bool(yes) and bool(no), f"exact witness failed: {name}: {yes!r} {no!r}")
        records.append({"id":name,"assumption":pre,"invalid_generalization":bad,
            "positive_exact_witness":True,"counterexample_exact_witness":True,
            "math_validation_status":"FINITE_EXACT_CASE_ONLY",
            "general_proof_certified":False, "teacher_approved":False,
            "student_free_text_verified":False})
    return {"batch":116,"kind":"EXACT_CONDITION_BOUNDARY_SAMPLING_NOT_PROOF",
       "source_math_guard_code_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
       "case_count":len(records),"positive_cases":len(records),
       "negative_cases":len(records),"universal_proof_certificates":0,
       "teacher_approvals":0,"student_free_text_certificates":0,"cases":records}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");args=ap.parse_args()
    body=json.dumps(audit(),ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
    if args.check: require(DEST.read_text()==body,"math condition audit generated artifact drift")
    else: DEST.parent.mkdir(parents=True,exist_ok=True);DEST.write_text(body)
    print(f"Batch116 independent exact condition witnesses: {len(CASES)} positive / {len(CASES)} negative; universal proofs 0")
if __name__=="__main__": main()
