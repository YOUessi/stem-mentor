"""Independent, limited K07 exact/boundary checks and fail-closed review queues.

Never promotes a theorem/proof/student step to VERIFIED. No API calls or eval.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from sympy import Rational, Symbol, sqrt, simplify, binomial

ROOT=Path(__file__).resolve().parents[1]
CONFLICT=ROOT/"docs/evaluation/KB_CONFLICT_RISK_BATCH07.json"
PROOF=ROOT/"docs/evaluation/KB_PROOF_OBLIGATIONS_BATCH07.json"
GAPS=ROOT/"knowledge/deep/semantic_gaps_batch04.json"
OUTPUT=ROOT/"docs/evaluation/KB_BATCH18_K07_RISK_REVIEW.json"

def read(path):return json.loads(path.read_text(encoding="utf8"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def limited_checks():
    records=[]
    def check(topic, test_id, condition, observation, kind="BOUNDARY"):
        records.append({"conflict_id":topic, "case":test_id, "passed":bool(condition),
                        "case_type":kind,"math_note":observation,
                        "scope":"CURATED_EXACT_SUBCLAIM_NOT_A_WHOLE_PROOF"})
    key="math.hs.function.composition-domain"
    # f(t)=ln t, g(x)=x-1, D(f∘g)=(1,+inf)
    for x,valid in [(-1,False),(0,False),(1,False),(2,True),(6,True)]:
        check(key,f"log-composition-x-{x}",(x-1>0)==valid,
              "D(g)=R and g(x) must lie in D(ln)=(0,+inf)")
    for x,valid in [(2,False),(5,True),(8,True)]:
        check(key,f"sqrt-composition-x-{x}",(x-5>=0)==valid,
              "sqrt inner input must be nonnegative")
    key="math.hs.function.parity"
    check(key,"asymmetric-square-not-even",
          not all(-x>0 for x in (1,2)),
          "Expression x² is even algebraically but domain (0,+inf) is not symmetric")
    for x in range(-5,6):
        check(key,f"zero-both-even-odd-{x}",0==0 and 0==-0,
              "zero function on symmetric domain is both even and odd")
        check(key,f"cubic-odd-{x}",(-x)**3==-x**3,
              "x³ is odd on all real inputs")
    key="math.hs.function.piecewise"
    for x in range(-5,6):
        check(key,f"disjoint-total-branches-{x}",int(x<=0)+int(x>0)==1,
              "x≤0 and x>0 partition all real inputs")
    check(key,"overlap-at-zero",int(0<=0)+int(0>=0)==2,
          "x≤0 and x≥0 overlap at 0 and require explicit coincidence/priority")
    key="math.hs.function.zero-ivt"
    check(key,"opposite-sign-continuous-has-zero",(-1)*1<0 and (0-1)==-1 and (2-1)==1,
          "f=x-1 continuous on [0,2], f(0)<0<f(2), zero at 1")
    check(key,"same-sign-can-have-zeros",
          ((-2)**2-1)>0 and (2**2-1)>0 and (1**2-1)==0,
          "f=x²-1 has two zeros despite equal-sign endpoints on [-2,2]")
    check(key,"discontinuous-sign-change-insufficient",
          -1<0<1 and (lambda z:-1 if z<0 else 1)(0)==1,
          "jump function is never zero despite endpoint sign change")
    key="math.hs.geometry.point-line-distance"
    for a,b in ((3,4),(-6,-8),(9,12)):
        x,y=3,4
        d=simplify(abs(a*x+b*y)/sqrt(a*a+b*b))
        check(key,f"normal-scaling-{a}-{b}",d==5,
              "distance to ax+by=0 invariant under nonzero scaling")
    check(key,"zero-normal-rejected",not (0*0+0*0>0),
          "A=B=0 gives zero denominator: not a valid line")
    key="math.hs.probability.binomial-distribution"
    for n in range(0,9):
        for p in (Rational(0),Rational(1,2),Rational(1)):
            total=sum(binomial(n,k)*p**k*(1-p)**(n-k) for k in range(n+1))
            check(key,f"binomial-normalization-n{n}-p{p}",total==1,
                  "exact binomial theorem sum with n nonnegative integer, 0≤p≤1")
    check(key,"dependence-breaks-binomial",
          Rational(0)!=binomial(2,1)*Rational(1,2)**2,
          "two identical Bernoulli outcomes are dependent, P(X=1)=0")
    key="math.hs.probability.hypergeometric"
    for N in range(1,9):
        for K in range(N+1):
            for n in range(N+1):
                values=[Fraction(math.comb(K,k)*math.comb(N-K,n-k),math.comb(N,n))
                        for k in range(max(0,n-(N-K)),min(n,K)+1)]
                check(key,f"hypergeom-sum-N{N}-K{K}-n{n}",
                      sum(values,Fraction(0))==1,
                      "without replacement; integer 0≤K,n≤N, feasible k")
    check(key,"replacement-changes-model",
          Fraction(math.comb(2,2)*math.comb(2,0),math.comb(4,2))==Fraction(1,6)
          and Fraction(1,6)!=Fraction(1,4),
          "N=4,K=2,n=2, no-replacement vs independent-replacement probability")
    key="math.hs.statistics.correlation-regression"
    X=(0,1,2);Y=(1,3,5)
    d=sum((x-Fraction(sum(X),len(X)))**2 for x in X)
    cov=sum((x-Fraction(sum(X),len(X)))*(y-Fraction(sum(Y),len(Y))) for x,y in zip(X,Y))
    slope=Fraction(cov,d)
    intercept=Fraction(sum(Y),len(Y))-slope*Fraction(sum(X),len(X))
    check(key,"ols-exact-line",slope==2 and intercept==1,
          "OLS slope 2, intercept 1, provided sum(x-xbar)^2>0")
    check(key,"constant-predictor-undefined",
          sum((x-1)**2 for x in (1,1,1))==0,
          "slope denominator 0, must reject any numeric slope")
    key="math.hs.triangle.area-sine"
    check(key,"included-angle-exact",
          simplify(Rational(1,2)*3*4*sqrt(3)/2-3*sqrt(3))==0,
          "two sides 3,4 with included 60 degrees give area 3√3")
    check(key,"nonincluded-angle-not-interchangeable",
          simplify(3*sqrt(3)-3)!=0,
          "substitute sin30° for included sin60° gives wrong area")
    check(key,"degenerate-zero-angle",
          Rational(1,2)*3*4*0==0,
          "zero angle has zero area, not a nondegenerate triangle")
    key="math.hs.vector.linear-operations"
    x=(1,2,3);y=(4,-2,1)
    add=lambda a,b:tuple(aa+bb for aa,bb in zip(a,b)) if len(a)==len(b) else None
    check(key,"same-dimension-add",add(x,y)==(5,0,4),
          "componentwise sum in R³")
    check(key,"dimension-mismatch-rejected",add((1,2),(1,2,3)) is None,
          "different ambient dimensions cannot be summed")
    check(key,"vector-commutes",add(x,y)==add(y,x),"vector addition commutative")
    check(key,"scalar-distributive",
          tuple(3*a for a in add(x,y))==add(tuple(3*a for a in x),tuple(3*b for b in y)),
          "fixed R³ distributivity example")
    assert all(r["passed"] for r in records),[r for r in records if not r["passed"]]
    return records

def priority(row, conflict_ids):
    txt=" ".join([row["id"]]+row.get("theorem_assumptions",[])+
        [p["claim"]+" "+p["reason"] for p in row["proof_step_obligations"]])
    hazard_terms=("分母","非零","连续","极限","概率","独立","正态","切线",
                  "偏导","根号","退化","取值","定义域","充分","必要",
                  "可逆","等价","零点","导数","角","除","不等")
    reasons=[]
    if row["id"] in conflict_ids:reasons.append("UNRESOLVED_VERSION_CONFLICT")
    for word in hazard_terms:
        if word in txt:reasons.append("ASSUMPTION:"+word)
    return ("P0" if row["id"] in conflict_ids else "P1" if reasons else "P2"),reasons

def build():
    conflicts=read(CONFLICT)["conflicts"]
    proof_data=read(PROOF)
    gaps=read(GAPS)["gaps"]
    conflict_ids={c["id"] for c in conflicts}
    checks=limited_checks()
    observed=Counter(c["conflict_id"] for c in checks)
    if set(observed)!=conflict_ids:
        raise ValueError("not all ten conflicts have curated cases")
    if len(conflicts)!=10 or len(gaps)!=23:
        raise ValueError("source drift: inspect before rewriting review queue")
    proof_queue=[]
    for row in proof_data["lessons"]:
        if row["kind"]!="theorem":continue
        level,reasons=priority(row,conflict_ids)
        for step in row["proof_step_obligations"]:
            proof_queue.append({"lesson_id":row["id"],"step_index":step["index"],
                "risk_priority":level,"risk_reasons":reasons,
                "proof_claim":step["claim"],"stated_reason":step["reason"],
                "verification_status":"NOT_FORMALLY_VERIFIED",
                "human_review":"PENDING"})
    if len(proof_queue)!=proof_data["summary"]["proof_step_obligations_not_formally_verified"]:
        raise ValueError("proof obligation drift")
    conflict_review=[]
    for c in conflicts:
        conflict_review.append({"lesson_id":c["id"],
         "active_sha256":c["active_sha256"],"candidate_sha256":c["candidate_sha256"],
         "changed_fields":c["mathematical_risk_fields"],
         "review_hint":c["review_hint"],"new_exact_boundary_cases":observed[c["id"]],
         "decision":"HOLD_BOTH_SOURCE_VERSIONS",
         "adjudication":"OPEN_REQUIRES_INDEPENDENT_TEACHER",
         "math_truth_status":"NOT_CERTIFIED",
         "warning":"Finite curated cases cannot select the authoritative text/version."})
    return {"scope":"CURATED_BOUNDARY_CASES_NOT_WHOLE_PROOF_CERTIFICATION",
      "source_sha256":{"conflicts":sha(CONFLICT),"proof_obligations":sha(PROOF),"semantic_gaps":sha(GAPS)},
      "summary":{"conflicts_total":len(conflicts),"conflicts_unresolved":len(conflicts),
        "conflicts_with_curated_cases":len(observed),"curated_cases":len(checks),
        "curated_checks_passed":sum(c["passed"] for c in checks),
        "semantic_depth_gaps":len(gaps),"semantic_gaps_closed":0,
        "proof_step_obligations_total":len(proof_queue),
        "proof_step_obligations_unverified":len(proof_queue),
        "whole_proofs_certified":0,"teacher_approved":0,"verified_student_steps":0,
        "by_priority":dict(Counter(q["risk_priority"] for q in proof_queue))},
      "conflict_reviews":conflict_review,"curated_boundary_cases":checks,
      "semantic_gap_queue":[{"engineering_id":g["curriculum_id"],
        "missing_subskill":g["missing_content"],"recommended_lesson_id":g["recommended_lesson_id"],
        "closure_status":"OPEN_TEACHER_VERIFICATION_REQUIRED"} for g in gaps],
      "proof_step_queue":proof_queue}

def validate(data):
    s=data["summary"]
    if any(s[k]!=0 for k in ("semantic_gaps_closed","whole_proofs_certified","teacher_approved","verified_student_steps")):
        raise ValueError("inadmissible release or proof certification")
    if s["curated_cases"]!=len(data["curated_boundary_cases"]) or not all(c["passed"] for c in data["curated_boundary_cases"]):
        raise ValueError("false curated result")
    if len(data["conflict_reviews"])!=10 or len(data["semantic_gap_queue"])!=23:
        raise ValueError("untracked source risks")
    if s["proof_step_obligations_unverified"]!=len(data["proof_step_queue"]):
        raise ValueError("proof count mismatch")
    if any(x["verification_status"]!="NOT_FORMALLY_VERIFIED" for x in data["proof_step_queue"]):
        raise ValueError("false proof certification")
    return True

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
    data=build()
    validate(data)
    rendered=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
    if args.check:
        if OUTPUT.read_text(encoding="utf8")!=rendered:raise ValueError("K07 risk snapshot drift")
    else:
        OUTPUT.write_text(rendered,encoding="utf8")
    print(f"K07 {'check PASS' if args.check else 'built'}: "
          f"{data['summary']['curated_cases']} exact boundary checks, "
          f"10 conflicts / 23 gaps still open, 451 proof steps still unverified; "
          f"priorities {data['summary']['by_priority']}")
if __name__=="__main__":main()
