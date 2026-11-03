#!/usr/bin/env python3
"""Conservative proof-obligation prioritization and conflict triage report.

No automated step changes REVIEW_PENDING or NOT_FORMALLY_VERIFIED.
The 32 limited arithmetic checks guard against common false implications;
none select a winning historical version or certify 451 natural-language steps.
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"backend"))
from app.batch18_math_checks import conflict_subclaim_checks
from app.official_clause_audit import page_progress
from app.deep_knowledge import lessons

def risk(lesson, step):
    s = (lesson["id"]+" "+step.get("claim","")+" "+step.get("reason","")).lower()
    domains = {
        "ASSUMPTIONS_DOMAIN": r"定义域|分母|非零|充要|前提|对数|平方|等号",
        "LIMIT_CALCULUS": r"极限|收敛|连续|可导|积分|中值|微分",
        "PROBABILITY_STATISTICS": r"概率|独立|二项|超几何|抽样|方差|统计|条件事件",
        "GEOMETRY_DEGENERACY": r"平面|垂直|切线|弦长|法向量|椭圆|双曲线|退化|三角形",
        "LINEAR_ALGEBRA": r"矩阵|行列式|线性相关|向量组|克拉默|投影",
    }
    matched = [k for k,pattern in domains.items() if re.search(pattern,s)]
    priority = "P0_GUARD_AND_COUNTEREXAMPLE" if ("ASSUMPTIONS_DOMAIN" in matched or len(matched)>=2) else ("P1_THEOREM_PROOF" if matched else "P2_REVIEW")
    return matched or ["OTHER_MATHEMATICAL_REASONING"], priority

def build():
    proof = json.loads((ROOT/"docs/evaluation/KB_PROOF_OBLIGATIONS_BATCH07.json").read_text())
    conflicts = json.loads((ROOT/"docs/evaluation/KB_CONFLICT_RISK_BATCH07.json").read_text())
    gaps = json.loads((ROOT/"knowledge/deep/semantic_gaps_batch04.json").read_text())["gaps"]
    new_gaps = json.loads((ROOT/"curriculum/highschool_math/k00_gap_tickets_batch18.json").read_text())
    checks=conflict_subclaim_checks()
    lesson_index={lesson.id:lesson for lesson in lessons()}
    if set(checks) != {r["id"] for r in conflicts["conflicts"]}:
        raise ValueError("Source conflicts and curated checks disagree")
    rows=[]
    for lesson in proof["lessons"]:
        for item in lesson["proof_step_obligations"]:
            if item["status"]!="NOT_FORMALLY_VERIFIED":
                raise ValueError("An unsupported step appears marked verified")
            domains,priority=risk(lesson,item)
            rows.append({
                "id":lesson["id"]+"#"+str(item["index"]),
                "lesson_id":lesson["id"], "step_index":item["index"],
                "claim_reason_sha256":hashlib.sha256(
                    (item["claim"]+"\x00"+item["reason"]).encode()).hexdigest(),
                "risk_groups":domains, "priority":priority,
                "proof_status":"NOT_FORMALLY_VERIFIED", "review_status":"HUMAN_REVIEW_PENDING",
                "teacher_solution_visibility":"TEACHER_ONLY",
            })
    if len(rows)!=proof["summary"]["proof_step_obligations_not_formally_verified"]:
        raise ValueError("Source proof counts have drifted")
    if len({r["id"] for r in rows})!=len(rows):
        raise ValueError("Duplicate proof obligation ID")
    if len(gaps)!=23 or any(r["status"]!="OPEN" for r in gaps):
        raise ValueError("Existing 23 semantic gaps must remain open")
    result={
        "schema_version":"1.0",
        "scope":"PRIORITY_TRIAGE_ONLY_NO_TEACHER_CERTIFICATION",
        "official_page_ledger":page_progress(),
        "summary":{
            "proof_obligations":len(rows),
            "by_priority":dict(Counter(r["priority"] for r in rows)),
            "by_risk_group":dict(Counter(k for r in rows for k in r["risk_groups"])),
            "whole_proofs_certified":0, "student_steps_verified":0,
            "conflicting_version_pairs":len(checks),
            "versions_resolved":0, "limited_subclaim_checks":sum(len(x["exact_observations"]) for x in checks.values()),
            "existing_semantic_gaps_open":len(gaps),
            "new_source_located_gap_tickets_open":len(new_gaps["tickets"]),
            "teacher_approved_lessons":0,
        },
        "conflict_checks":[
            {"lesson_id":row["id"],"candidate_sha256":row["candidate_sha256"],
             "active_sha256":row["active_sha256"],"risk_fields":row["mathematical_risk_fields"],
             "comparison_status":"BOTH_VERSIONS_ON_HOLD",
             **checks[row["id"]]}
            for row in conflicts["conflicts"]
        ],
        "legacy_gap_ids_open":[r["curriculum_id"] for r in gaps],
        "legacy_semantic_gap_triage":[{
            "curriculum_id":r["curriculum_id"],
            "recommended_lesson_id":r["recommended_lesson_id"],
            "candidate_draft_exists":r["recommended_lesson_id"] in lesson_index,
            "candidate_review_state":(lesson_index[r["recommended_lesson_id"]].review.status
                                      if r["recommended_lesson_id"] in lesson_index else "NOT_FOUND"),
            "gap_review_status":"OPEN_HUMAN_MATHEMATICS_REVIEW_REQUIRED",
            "gap_closed":False,
        } for r in gaps],
        "proof_review_queue":rows,
    }
    return result
def main():
    o=build()
    p=ROOT/"docs/evaluation/KB_BATCH18_SOURCE_AND_PROOF_RISK_AUDIT.json"
    p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(o["summary"],ensure_ascii=False,indent=2))
if __name__=="__main__":main()
