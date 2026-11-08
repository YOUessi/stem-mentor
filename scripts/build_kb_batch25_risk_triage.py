#!/usr/bin/env python3
"""K07: re-attest 127 P0 natural-language proof obligations and ten version conflicts.

The 10 exact instance probes below test hazardous conditions, NOT the proof
as a whole and NOT which of two source variants is authoritative.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import lessons
from app.kb_batch25_math import evaluate

HISTORY=ROOT/"docs/evaluation/KB_BATCH18_SOURCE_AND_PROOF_RISK_AUDIT.json"
CONFLICTS=ROOT/"docs/evaluation/KB_CONFLICT_RISK_BATCH07.json"
CURRENT=ROOT/"docs/evaluation/KB_BATCH24_INTEGRITY_AND_PROOFS.json"
OUT=ROOT/"docs/evaluation/KB_BATCH25_P0_PROOF_AND_CONFLICT_TRIAGE.json"
CHECKS={
 "ASSUMPTIONS_DOMAIN":"核对原定义域、非零分母与代入/变形是否双向合法；必须给出排除点。",
 "GEOMETRY_DEGENERACY":"核对非退化、长度和向量非零、平行/共线边界；不能依赖示意图。",
 "PROBABILITY_STATISTICS":"核对样本空间、独立与否、参数合法区间、支撑集和极端概率。",
 "LINEAR_ALGEBRA":"核对向量维度、可逆性、秩或非零条件，禁止把有限数值样本当通用证明。",
 "LIMIT_CALCULUS":"核对极限存在、连续可导前提与区间边界，不能逆推定理结论。"
}
# One bounded independent exact fixture per one of the 10 historically conflicting themes.
FIXTURES={
 "math.hs.function.composition-domain":("composition_reciprocal",{"x":2,"shift":-2},"CONDITIONS_NOT_ESTABLISHED"),
 "math.hs.function.parity":("parity_polynomial_at_point",{"coefficients":[0,0,1],"x":2},"VERIFIED_FINITE_INSTANCE"),
 "math.hs.function.piecewise":("piecewise_endpoint",{"x":1,"threshold":1},"VERIFIED_FINITE_INSTANCE"),
 "math.hs.function.zero-ivt":("ivt_polynomial_endpoints",{"a":0,"b":2,"k":1},"VERIFIED_FINITE_INSTANCE"),
 "math.hs.geometry.point-line-distance":("point_line_distance_squared",{"A":0,"B":0,"C":1,"x":2,"y":3},"CONDITIONS_NOT_ESTABLISHED"),
 "math.hs.probability.binomial-distribution":("binomial_point_mass",{"n":4,"k":2,"p":"1/2"},"VERIFIED_FINITE_INSTANCE"),
 "math.hs.probability.hypergeometric":("hypergeometric_point_mass",{"N":7,"K":3,"n":2,"k":1},"VERIFIED_FINITE_INSTANCE"),
 "math.hs.statistics.correlation-regression":("regression_slope",{"xs":[1,2,3],"ys":[2,4,6]},"VERIFIED_FINITE_INSTANCE"),
 "math.hs.triangle.area-sine":("triangle_double_area",{"P":[0,0],"Q":[2,0],"R":[0,3]},"VERIFIED_FINITE_INSTANCE"),
 "math.hs.vector.linear-operations":("vector_linear_combination",{"u":[1,2],"v":[3,4],"a":2,"b":-1},"VERIFIED_FINITE_INSTANCE"),
}
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
    original=read(HISTORY);conflicts=read(CONFLICTS);prior=read(CURRENT)
    if original["summary"]["by_priority"]["P0_GUARD_AND_COUNTEREXAMPLE"]!=127:
        raise ValueError("P0 baseline changed")
    if (len(original["proof_review_queue"]),len(conflicts["conflicts"]),len(lessons()))!=(451,10,287):
        raise ValueError("Frozen source or corpus counts changed")
    if prior["summary"]["all_unverified_proof_steps"]!=538:
        raise ValueError("Historical proof queue drift")
    indexed={d.id:d for d in lessons()}
    risky=[];group_counts=Counter()
    for rec in original["proof_review_queue"]:
        if rec["priority"]!="P0_GUARD_AND_COUNTEREXAMPLE":continue
        doc=indexed.get(rec["lesson_id"])
        if doc is None or doc.review.status!="REVIEW_PENDING" or doc.teacher_solution_visibility!="TEACHER_ONLY":
            raise ValueError("Original P0 doc not safely loaded")
        n=rec["step_index"]
        if not isinstance(n,int) or n<1 or n>len(doc.proof_steps):
            raise ValueError("P0 step index invalid")
        step=doc.proof_steps[n-1]
        digest=hashlib.sha256((step.claim+"\0"+step.reason).encode("utf-8")).hexdigest()
        if digest!=rec["claim_reason_sha256"]:
            raise ValueError("P0 proof claim/reason has changed: "+rec["id"])
        groups=rec["risk_groups"]
        if not groups or any(g not in CHECKS for g in groups):
            raise ValueError("Missing review checklist for risk family")
        group_counts.update(groups)
        risky.append(dict(id=rec["id"],lesson_id=rec["lesson_id"],index=n,
             verified_original_step_sha256=digest,risk_groups=groups,
             required_human_review=[CHECKS[g] for g in groups],
             evidence_needed=["theorem assumptions", "checked claim and reason",
                              "counterexample or edge-case", "independent mathematical reviewer"],
             finite_instance_certificate=False,proof_status="NOT_FORMALLY_VERIFIED",
             teacher_review="PENDING",student_step_verified=False,
             student_publishable=False))
    if len(risky)!=127 or len({x["id"] for x in risky})!=127:
        raise ValueError("127 original P0 items were not all accounted for")
    judged=[];status_counts=Counter()
    if set(FIXTURES)!={c["id"] for c in conflicts["conflicts"]}:
        raise ValueError("Every historical conflict must receive a bounded test")
    for c in sorted(conflicts["conflicts"],key=lambda x:x["id"]):
        op,inp,want=FIXTURES[c["id"]]
        result=evaluate(op,inp)
        if result["status"]!=want or any(result[v] for v in
            ("student_step_verified","complete_theorem_certified","teacher_approved","official_curriculum_atom_verified")):
            raise ValueError("Unsafe math fixture for "+c["id"])
        if c["decision"]!="HOLD_BOTH_SOURCE_VERSIONS" or c["evidence_status"]!="MATH_NOT_INDEPENDENTLY_ADJUDICATED":
            raise ValueError("Historical conflict decision silently changed")
        status_counts.update([result["status"]])
        judged.append(dict(id=c["id"],candidate_sha256=c["candidate_sha256"],
                active_sha256=c["active_sha256"],mathematical_risk_fields=c["mathematical_risk_fields"],
                restricted_oracle=op,operand_fixture=inp,finite_check_result=result,
                independent_math_adjudication=False,version_winner=None,
                disposition="HOLD_BOTH_UNTIL_MATH_AND_EDITORIAL_REVIEW",teacher_review="PENDING"))
    return json.dumps(dict(schema_version="kb-batch25-p0-conflict-v1",
       scope="STEP_HASH_AND_BOUNDED_EXACT_WITNESSES_NOT_FULL_PROOFS",
       input_sha256={"batch18_451_step_risk_ledger":sha(HISTORY),
                     "batch07_10_conflicts":sha(CONFLICTS),
                     "batch24_proof_union":sha(CURRENT)},
       summary=dict(historical_proof_obligations=451,all_current_unverified_proof_steps=538,
            p0_historical_steps_attested=len(risky),p0_text_mismatches=0,
            p0_by_risk_group=dict(sorted(group_counts.items())),
            conflicting_versions_reviewed_as_finite_instances=len(judged),
            finite_checks_by_status=dict(sorted(status_counts.items())),
            mathematical_proofs_formally_certified=0,teacher_approved=0,
            conflicts_resolved=0,student_steps_verified=0,
            verified_official_atomic_denominator=None),
       p0_review_queue=risky,conflict_finite_evidence=judged,
       warnings=["The checked P0 SHA only attests that prose matches the frozen review baseline.",
                 "Ten finite oracle probes test concrete cases, not the truth of full conflict versions.",
                 "Zero formal proof certificates, zero teacher approvals, all conflicts remain OPEN."]),
       ensure_ascii=False,indent=2)+"\n"
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");a=ap.parse_args()
    data=build()
    if a.check:
        if OUT.read_text(encoding="utf-8")!=data:raise SystemExit("Batch25 P0 audit drift")
    else:OUT.write_text(data,encoding="utf-8")
    print("PASS 127 P0 step hashes + 10 conflict bounded probes; no full proof or teacher approvals")
if __name__=="__main__":main()
