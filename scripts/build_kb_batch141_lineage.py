#!/usr/bin/env python3
"""Batch141: close the *new-format* P0 lineage gap from prior editorial material.

This is a lossless, source-fingerprinted migration and applicability audit of
KB29/30 editorial work; it is NOT 47 newly proven lemmas, a teacher approval,
or a reclassification of the 538 historically unverified proof steps.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "scripts")]
from app.deep_knowledge import lessons
import build_kb_batch140_proof_guards as previous

OUT = ROOT / "docs/evaluation/KB_BATCH141_P0_LINEAGE.json"
MD = ROOT / "docs/evaluation/KB_BATCH141_P0_LINEAGE.md"
BASE = ROOT / "docs/evaluation/"
LEGACIES = (
    ("KB_BATCH29_P0_CONDITION_REVIEW.json", "new_editorial_step_proposals", "claim_reason_sha256"),
    ("KB_BATCH30_P0_COMPLETION_AUDIT.json", "batch30_new_editorial_rows", "exact_original_claim_reason_sha256"),
)
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A",
          "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")
EXACT_IDS = (
 "math.hs.calculus.tangent-line#3",
 "math.hs.complex.operations#2",
 "math.hs.elective.geometry.euclidean-isometries#2",
 "math.hs.elective.matrix.inverse-two-by-two#3",
 "math.hs.function.composition-domain#3",
 "math.hs.geometry.line-general#2",
 "math.hs.geometry.line-relations#2",
 "math.hs.geometry.point-line-distance#3",
 "math.hs.probability.multiplication#2",
 "math.hs.space.perpendicular-plane#2",
 "math.hs.elective.statistics.bernoulli-mle#3",
 "math.hs.space.solid-volumes#3",
)

def demand(test, reason):
    if not test:
        raise ValueError("KB141 provenance/review: " + reason)

def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"

def load_legacy():
    by_id = {}
    for filename, key, sha_field in LEGACIES:
        raw = json.loads((BASE / filename).read_text(encoding="utf-8"))
        for legacy in raw[key]:
            sid = legacy["risk_step_id"]
            demand(sid not in by_id, "duplicated old editorial ID: " + sid)
            by_id[sid] = (legacy, filename, sha_field)
    return by_id

def course_family(step_id):
    # This is a local editorial family grouping, NOT a certified track assignment.
    if ".elective." in step_id or ".extension." in step_id:
        return "ELECTIVE_OR_EXTENSION_EDITORIAL_UNRESOLVED"
    return "CORE_OR_SELECTIVE_EDITORIAL_UNRESOLVED"

def build():
    old = previous.build()
    queue_raw = json.loads(previous.QUEUE.read_text(encoding="utf-8"))
    queue = {r["id"]: r for r in queue_raw["step_review_queue"]}
    originals = {x.id: x for x in lessons()}
    legacy = load_legacy()
    missing = old["remaining_p0_step_ids"]
    demand(len(missing) == len(set(missing)) == 47, "expected 47 missing new-format P0 cards")
    demand(set(missing) <= set(legacy), "old editorial records missing")
    new = []
    for sid in missing:
        src, filename, sha_field = legacy[sid]
        lesson_id, _, number = sid.rpartition("#")
        demand(lesson_id in originals and number.isdigit(), "missing historical original: " + sid)
        steps = originals[lesson_id].proof_steps
        demand(1 <= int(number) <= len(steps), "missing original step index: " + sid)
        step = steps[int(number)-1]
        digest = hashlib.sha256((step.claim + "\x00" + step.reason).encode("utf-8")).hexdigest()
        q = queue[sid]
        demand(q["source_sha256"] == digest == src[sha_field], "source/previous editorial mismatch: " + sid)
        demand(q["risk_priority"] == "P0_GUARD_AND_COUNTEREXAMPLE" and
               q["formal_certification"] == "NOT_FORMALLY_VERIFIED",
               "incorrect risk or historical certification: " + sid)
        condition = src["necessary_hypotheses"]
        counter = src.get("counterexample_or_failure_mode", src.get("explanatory_counterexample"))
        demand(isinstance(condition, str) and len(condition) >= 45, "missing condition: " + sid)
        demand(isinstance(counter, str) and len(counter) >= 30, "missing invalid boundary: " + sid)
        demand(src.get("teacher_review") == "PENDING" and
               src.get("complete_proof_certified") is False and
               src.get("student_publishable") is False,
               "legacy claimed approval: " + sid)
        demand(src.get("student_step_verified") is False, "legacy wrongly verified free student text")
        legacy_digest = hashlib.sha256(canonical(src).encode("utf-8")).hexdigest()
        new.append({
            "historical_proof_step_id": sid,
            "historical_step_sha256": digest,
            "original_claim": step.claim,
            "original_reason": step.reason,
            "historical_risk_groups": q["risk_groups"],
            "necessary_preconditions": condition,
            "legacy_counterexample_or_boundary": counter,
            "legacy_editorial_source": "docs/evaluation/" + filename,
            "legacy_editorial_record_sha256": legacy_digest,
            "legacy_editorial_operation": src.get("operation", "NO_OPERATION_IN_LEGACY"),
            "legacy_next_review_action": src.get("next_review_action"),
            "justification_status": "HISTORIC_EXPLANATION_ONLY_REQUIRES_INDEPENDENT_PROOF_REVIEW",
            "independent_exact_case_status": ("24_FINITE_CASES_IN_SEPARATE_ORACLE"
                                              if sid in EXACT_IDS else "NOT_IN_THIS_BATCH_ORACLE"),
            "student_free_text_verified": False,
            "general_proof_certified": False,
            "original_step_formally_verified": False,
            "teacher_review_status": "REVIEW_PENDING",
            "teacher_signature": None,
            "student_publishable": False,
            "course_family_provisional": course_family(sid),
        })
    by_fam = dict(Counter(r["course_family_provisional"] for r in new))
    result = {
        "schema": "kb141-source-locked-editorial-lineage/1",
        "evidence_boundary": "MIGRATED_KB29_KB30_EDITORIAL_GUARDS_NOT_NEW_FORMAL_PROOFS",
        "historical_proof_steps": 538,
        "historical_p0_denominator": 127,
        "previous_source_card_union": 80,
        "new_source_locked_legacy_cards": len(new),
        "new_format_p0_union": 80 + len(new),
        "p0_without_new_format_card": 0,
        "all_p0_with_prior_editorial_notes": 127,
        "original_math_conflicts_unresolved": 10,
        "source_status": "PREVIOUS_APPROVED_SOURCE_PAGES_NOT_IMPLIED",
        "independent_exact_witnessed_steps": len(EXACT_IDS),
        "independent_exact_case_count": 2*len(EXACT_IDS),
        "review_without_new_exact_case": len(new)-len(EXACT_IDS),
        "provisional_families_not_official_tracks": by_fam,
        "official_course_atom_denominators": {x:None for x in TRACKS},
        "official_coverage_fraction": None,
        "human_teacher_approvals": 0,
        "general_formal_proof_certificates": 0,
        "student_authoritative_publications": 0,
        "student_free_form_step_certifications": 0,
        "records": new,
    }
    validate(result)
    return result

def validate(result):
    previous_rows = previous.build()
    legacy = load_legacy()
    queue = {r["id"]: r for r in json.loads(previous.QUEUE.read_text(encoding="utf-8"))["step_review_queue"]}
    originals = {x.id:x for x in lessons()}
    ids = previous_rows["remaining_p0_step_ids"]
    demand(result["historical_proof_steps"]==538 and result["historical_p0_denominator"]==127, "invented denominator")
    demand(result["previous_source_card_union"]==80 and result["new_source_locked_legacy_cards"]==47
           and result["new_format_p0_union"]==127 and result["p0_without_new_format_card"]==0,
           "new-format lineage count mismatch")
    demand(result["all_p0_with_prior_editorial_notes"]==127 and
           result["original_math_conflicts_unresolved"]==10, "incorrect historical debt")
    demand(result["independent_exact_witnessed_steps"]==12 and
           result["independent_exact_case_count"]==24 and
           result["review_without_new_exact_case"]==35, "overclaiming bounded math checks")
    demand(result["official_course_atom_denominators"]=={x:None for x in TRACKS} and
           result["official_coverage_fraction"] is None, "fake official math curriculum coverage")
    for f in ("human_teacher_approvals", "general_formal_proof_certificates",
              "student_authoritative_publications", "student_free_form_step_certifications"):
        demand(result[f]==0, "forged approval: "+f)
    records = result["records"]
    demand([r["historical_proof_step_id"] for r in records] == ids, "missing/reordered/extra original step")
    demand(result["provisional_families_not_official_tracks"]==
           dict(Counter(course_family(x) for x in ids)), "invented course family")
    for r in records:
        sid = r["historical_proof_step_id"]
        src, filename, sha_field = legacy[sid]
        parent,_,i=sid.rpartition("#")
        step=originals[parent].proof_steps[int(i)-1]
        digest=hashlib.sha256((step.claim+"\x00"+step.reason).encode("utf-8")).hexdigest()
        demand(r["historical_step_sha256"]==digest==src[sha_field]==queue[sid]["source_sha256"],
               "historical step fingerprint drift: "+sid)
        demand(r["original_claim"]==step.claim and r["original_reason"]==step.reason,
               "historical original rewritten: "+sid)
        demand(r["legacy_editorial_record_sha256"]==
               hashlib.sha256(canonical(src).encode("utf-8")).hexdigest() and
               r["legacy_editorial_source"]=="docs/evaluation/"+filename,
               "historic editorial citation drift: "+sid)
        demand(r["necessary_preconditions"]==src["necessary_hypotheses"] and
               r["legacy_counterexample_or_boundary"]==
               src.get("counterexample_or_failure_mode",src.get("explanatory_counterexample")),
               "legitimate mathematical condition tampered: "+sid)
        demand(r["historical_risk_groups"]==queue[sid]["risk_groups"] and
               r["legacy_editorial_operation"]==src.get("operation","NO_OPERATION_IN_LEGACY") and
               r["legacy_next_review_action"]==src.get("next_review_action"),
               "risk/operation drift: "+sid)
        demand(r["justification_status"]=="HISTORIC_EXPLANATION_ONLY_REQUIRES_INDEPENDENT_PROOF_REVIEW"
               and r["independent_exact_case_status"]==
               ("24_FINITE_CASES_IN_SEPARATE_ORACLE" if sid in EXACT_IDS else "NOT_IN_THIS_BATCH_ORACLE"),
               "fake independent proof or case count")
        demand(r["general_proof_certified"] is False and
               r["original_step_formally_verified"] is False and
               r["student_free_text_verified"] is False and
               r["teacher_review_status"]=="REVIEW_PENDING" and
               r["teacher_signature"] is None and r["student_publishable"] is False,
               "unauthorized mathematical or teacher approval")
        demand(r["course_family_provisional"]==course_family(sid), "forged official track")
    return True

def render(report):
    lines = [
        "# Batch141｜47条历史P0高风险证明步骤：新式来源锁定卡的完整补齐",
        "",
        "**范围说明：迁移并重新锁定的是KB29/KB30已有数学前提审查内容，绝非新增47份数学证明。**",
        "127/127 P0原本已有KB28/29/30编辑记录；从另一种来源卡格式的80/127补到127/127。",
        "全部47条的原始数学陈述、理由、原始步骤SHA与早期编辑记录SHA均被逐项检查。",
        "独立的精确有限案例另行覆盖12条步骤、共24个案例；余35条仅建立来源一致性卡。",
        "这不是全量538条历史证明步骤的形式认证，也不能关闭既有10项数学冲突。",
        "七轨正式知识原子分母仍UNKNOWN；教师批准0；学生权威发布0。",
        "",
    ]
    for r in report["records"]:
        lines.extend([
            "## "+r["historical_proof_step_id"], "",
            "原始SHA-256: `"+r["historical_step_sha256"]+"`",
            "历史编辑档案: "+r["legacy_editorial_source"]+
            "（record SHA-256 `"+r["legacy_editorial_record_sha256"]+"`）",
            "原始命题步骤: "+r["original_claim"],
            "历史说明（未独立认证）: "+r["original_reason"],
            "### 必须前提", r["necessary_preconditions"],
            "### 不适用反例/边界", r["legacy_counterexample_or_boundary"],
            "独立精确有限案例: "+("有（但不是量词证明）" if r["historical_proof_step_id"] in EXACT_IDS else "本批无"),
            "数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。", "",
        ])
    return "\n".join(lines)+"\n"

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    opts=p.parse_args()
    data=build()
    if opts.write:
        OUT.write_text(canonical(data),encoding="utf-8")
        MD.write_text(render(data),encoding="utf-8")
    else:
        demand(json.loads(OUT.read_text(encoding="utf-8"))==data,"stored lineage record drift")
        demand(MD.read_text(encoding="utf-8")==render(data),"stored review text drift")
    print("PASS KB141: 47 existing editorial cases source-locked; P0 127/127 newer cards, 0 formal proofs")

if __name__=="__main__":
    main()
