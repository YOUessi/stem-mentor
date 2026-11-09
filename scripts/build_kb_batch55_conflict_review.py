#!/usr/bin/env python3
"""Reproducible NON-CERTIFYING proof/conflict risk triage."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.kb_batch55_conflict_witnesses import OPS, checked_conflict_witness, ConditionsNotEstablished

RISK = ROOT / "docs/evaluation/KB_CONFLICT_RISK_BATCH07.json"
PROOF = ROOT / "docs/evaluation/KB_BATCH25_P0_PROOF_AND_CONFLICT_TRIAGE.json"
SCOPE = ROOT / "docs/evaluation/KB_BATCH54_SCOPE_AND_DENOMINATOR_AUDIT.json"
OUTPUT_JSON = ROOT / "docs/evaluation/KB_BATCH55_CONFLICT_PROOF_REVIEW.json"
OUTPUT_MD = ROOT / "docs/evaluation/KB_BATCH55_CONFLICT_PROOF_REVIEW.md"

FIXTURES = {
    "math.hs.function.composition-domain": [
        {"x": 3, "shift": -2}, {"x": 2, "shift": -2}],
    "math.hs.function.parity": [
        {"coefficients": [0, 0, 0, 0], "domain": "ALL_REAL"},
        {"coefficients": [1, 1], "domain": "POSITIVE_REAL"}],
    "math.hs.function.piecewise": [
        {"left_inclusive": True, "right_inclusive": True, "left_value": 1, "right_value": 2},
        {"left_inclusive": False, "right_inclusive": False, "left_value": 1, "right_value": 2}],
    "math.hs.function.zero-ivt": [
        {"coefficients": [-1, 0, 1], "left": -2, "right": 0},
        {"coefficients": [-1, 0, 1], "left": -2, "right": 2}],
    "math.hs.geometry.point-line-distance": [
        {"A": 3, "B": 4, "C": 0, "x": 1, "y": 2},
        {"A": 0, "B": 0, "C": 1, "x": 1, "y": 2}],
    "math.hs.probability.binomial-distribution": [
        {"n": 2, "k": 2, "p": Fraction(1, 2), "independent_identical": True},
        {"n": 2, "k": 2, "p": Fraction(1, 2), "independent_identical": False}],
    "math.hs.probability.hypergeometric": [
        {"N": 5, "K": 2, "n": 2, "k": 1, "equal_likelihood_without_replacement": True},
        {"N": 5, "K": 2, "n": 2, "k": 1, "equal_likelihood_without_replacement": False}],
    "math.hs.statistics.correlation-regression": [
        {"xs": [-1, 0, 1], "ys": [1, 0, 1]},
        {"xs": [1, 1, 1], "ys": [1, 2, 3]}],
    "math.hs.triangle.area-sine": [
        {"a": 3, "b": 4, "cos_included_angle": 0, "is_included_angle": True},
        {"a": 3, "b": 4, "cos_included_angle": 1, "is_included_angle": True}],
    "math.hs.vector.linear-operations": [
        {"u": [1, 0], "v": [0, 1]},
        {"u": [1, 0], "v": [0, 1, 1]}],
}
QUESTIONS = {
    "math.hs.function.composition-domain": "先证明 g(x) 属于 f 的定义域；在零分母处停止，不允许约分后补点。",
    "math.hs.function.parity": "先核实定义域关于原点对称；零多项式既奇且偶，非零奇偶分类量词是否正确？",
    "math.hs.function.piecewise": "分界点可重叠但赋值必须一致；既不属于任何分支时不在定义域。",
    "math.hs.function.zero-ivt": "连续且端点异号保证至少一根；两端同号仍可能有根，唯一性不由异号保证。",
    "math.hs.geometry.point-line-distance": "直线法向量非零是必要前提；距离是否需要无理数表达？",
    "math.hs.probability.binomial-distribution": "独立同分布试验是否真正给定？退化成功概率p=0或1如何处理？",
    "math.hs.probability.hypergeometric": "无放回均匀抽样及合法整数支撑集是否满足？有放回不得复用。",
    "math.hs.statistics.correlation-regression": "常量自变量令回归斜率未定义；零相关不能排除非线性或证明独立。",
    "math.hs.triangle.area-sine": "输入角须是两边夹角且三角形不退化。",
    "math.hs.vector.linear-operations": "向量同维同坐标；坐标相加正确不等于模长可相加。",
}


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe(value):
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {k:_safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [_safe(v) for v in value]
    return value


def build(risk=None, proof=None, scope=None, fixtures=None):
    risk = risk if risk is not None else json.loads(RISK.read_text())
    proof = proof if proof is not None else json.loads(PROOF.read_text())
    scope = scope if scope is not None else json.loads(SCOPE.read_text())
    fixtures = fixtures if fixtures is not None else FIXTURES
    cs = risk["conflicts"]
    if len(cs) != 10 or len({x["id"] for x in cs}) != 10:
        raise ValueError("Expected 10 distinct source conflicts")
    if {x["id"] for x in cs} != set(OPS) or set(fixtures) != set(OPS):
        raise ValueError("Source conflict/oracle inventory mismatch")
    if risk["summary"]["unresolved_conflicts"] != 10 or risk["summary"]["automatically_resolved"] != 0:
        raise ValueError("Conflict closed without human proof review")
    s=proof["summary"]
    if not (s["all_current_unverified_proof_steps"] == 538 and
            s["historical_proof_obligations"] == 451 and
            s["p0_historical_steps_attested"] == 127 and
            len(proof["p0_review_queue"]) == 127 and
            len({v["id"] for v in proof["p0_review_queue"]}) == 127 and
            s["mathematical_proofs_formally_certified"] == 0 and
            s["teacher_approved"] == 0 and s["conflicts_resolved"] == 0 and
            s["student_steps_verified"] == 0):
        raise ValueError("Unexpected proof review/certification state")
    if any(
        row["proof_status"] != "NOT_FORMALLY_VERIFIED" or
        row["teacher_review"] != "PENDING" or
        row["student_publishable"] is not False or
        row["student_step_verified"] is not False or
        row["finite_instance_certificate"] is not False or
        len(row["verified_original_step_sha256"]) != 64 or
        not row["required_human_review"] or not row["evidence_needed"]
        for row in proof["p0_review_queue"]
    ):
        raise ValueError("Per-step proof/review/publish state was falsified")
    if (len(scope["source_pages"]) != 61 or
        set(scope["official_atomic_denominator"].values()) != {None} or
        scope["student_published"] != 0 or scope["legacy_actual_teacher_approvals"] != 0 or
        any(p["full_page_manual_atomization"] != "NOT_COMPLETED" for p in scope["source_pages"])):
        raise ValueError("Official syllabus or teacher status unexpectedly promoted")
    packets=[]
    for c in sorted(cs,key=lambda v:v["id"]):
        key=c["id"]
        if (c["evidence_status"] != "MATH_NOT_INDEPENDENTLY_ADJUDICATED" or
c["decision"]!="HOLD_BOTH_SOURCE_VERSIONS" or
            any(len(c[k]) != 64 for k in ("candidate_sha256","active_sha256")) or
            not c["mathematical_risk_fields"] or len(fixtures[key]) != 2):
            raise ValueError("Unsafe version or finite test metadata")
        cases=[]
        for f in fixtures[key]:
            try:
                result=checked_conflict_witness(key,**f)
                status="FINITE_EXACT_CASE_ONLY"
            except ConditionsNotEstablished as exc:
                result={"status":"CONDITIONS_NOT_ESTABLISHED","reason":str(exc)}
                status="CONDITIONS_NOT_ESTABLISHED"
            cases.append({"inputs":_safe(f),"result":_safe(result),"status":status})
        packets.append({
            "id":key,"candidate_sha256":c["candidate_sha256"],
            "active_sha256":c["active_sha256"],
            "changed_risk_fields":c["mathematical_risk_fields"],
            "human_review_question":QUESTIONS[key],
            "bounded_exact_cases":cases,
            "version_resolution":"UNRESOLVED",
            "general_proof_status":"NOT_FORMALLY_CERTIFIED",
            "teacher_review":"REVIEW_PENDING","student_publishable":False,
        })
    return {
        "schema_version":"kb55-ten-conflict-p0-review-v1",
        "status":"RISK_TRIAGE_ONLY_NOT_MATHEMATICAL_CERTIFICATION",
        "input_sha256":{"risk":_sha(RISK),"proof":_sha(PROOF),"scope":_sha(SCOPE)},
        "conflict_count":10,"conflicts_resolved":0,
        "frozen_unverified_proof_steps":538,"historical_proof_steps":451,
        "p0_historical_steps_source_attested_not_math_certified":127,
        "p0_priority_ids":[r["id"] for r in proof["p0_review_queue"]],
        "official_atomic_denominator":scope["official_atomic_denominator"],
        "teacher_approved":0,"student_published":0,
        "packets":packets,
    }


def render_md(audit):
    lines=[
        "# Batch55｜十组数学版本冲突：有限见证与人工复核清单","",
        "仅供教师/教研审查。十组冲突全部OPEN；538条历史证明步骤未形式认证。",
        "其中127条只有文本SHA完整性证据，不能推导出数学内容正确。",
        "七轨官方课标分母仍未认证，教师批准、学生发布均为零。","",
        "| 项目 | 数量 | 数学认证 |","| --- | ---: | --- |",
        "| 来源版本冲突 | 10 | 0项裁决 |",
        "| 条件敏感的受控实例 | 20 | 不证明一般定理 |",
        "| 历史待核证明步骤 | 538 | 0项形式认证 |",
        "| 高优先级文本指纹核对 | 127 | 只确认文本未漂移 |","",
    ]
    for p in audit["packets"]:
        lines += ["## "+p["id"],"",
                  "**人工审查问题**："+p["human_review_question"],"",
                  "候选SHA："+p["candidate_sha256"]+"；当前稿SHA："+p["active_sha256"]+"。",
                  "两版均未裁决，不选择其中之一作为学生端权威事实源。",""]
        for i,x in enumerate(p["bounded_exact_cases"],1):
            lines+=["**受控案例 "+str(i)+"**："+json.dumps(x["inputs"],ensure_ascii=False,sort_keys=True),
                    "状态："+x["status"]+"；有限输出："+json.dumps(x["result"],ensure_ascii=False,sort_keys=True),""]
    lines += ["## 后续审核门槛","",
              "逐项复核两版完整原文、全部数学假设、量词、证明链及反例；保存真实教师身份、时间与版本记录。",
              "发现失败案例只要求修改，不自动裁决。有限实例不得升级为形式证明、课标通过或学生可发布。",""]
    return "\n".join(lines)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    audit=build()
    txt=json.dumps(audit,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    md=render_md(audit)
    if args.check:
        if not OUTPUT_JSON.exists() or OUTPUT_JSON.read_text()!=txt:raise SystemExit("Batch55 JSON drift")
        if not OUTPUT_MD.exists() or OUTPUT_MD.read_text()!=md:raise SystemExit("Batch55 Markdown drift")
    else:
        OUTPUT_JSON.write_text(txt)
        OUTPUT_MD.write_text(md)
    print("Batch55: 10 unresolved version conflicts, 20 finite probes, 538 uncertified proof steps")


if __name__=="__main__":
    main()
