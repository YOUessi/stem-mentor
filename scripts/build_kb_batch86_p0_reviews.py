#!/usr/bin/env python3
"""Batch86: ten independent, original, SHA-linked history-P0 proof reviews.

Exact oracle witnesses check *specific finite examples* and do not constitute
universal theorem proofs, independent teacher approval, or student verification.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"backend"),str(ROOT/"scripts")]
from app.kb_batch28_condition_oracles import evaluate,SUPPORTED
import build_kb_batch85_p0_history as B85

AUTHOR=ROOT/"knowledge/editorial_review/kb_batch86_p0_authoring.json"
OUT=ROOT/"knowledge/editorial_review/kb_batch86_p0_teacher_cards.json"
MD=ROOT/"docs/evaluation/KB_BATCH86_P0_HISTORY_GUARDS.md"
FIELDS=B85.FIELDS
SCHEMA="kb86-ten-source-linked-p0-review-drafts-v1"
OPS={"log_product_domain","quadratic_discriminant","amgm_rational_roots",
     "circle_circle","parabola_focus","cauchy_schwarz",
     "union_probability","vector_angle","odd_square_induction","fermat_difference"}
def require(ok,msg):
    if not ok:raise ValueError(msg)
def load(p):return json.loads(Path(p).read_text(encoding="utf8"))
def dump(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
def build(auth=None,proofs=None,profiles=None,previous=None):
    auth=load(AUTHOR) if auth is None else auth
    proofs=load(B85.B81.PROOFS) if proofs is None else proofs
    profiles=load(B85.PROFILES) if profiles is None else profiles
    previous=B85.build() if previous is None else previous
    require(type(auth) is dict and set(auth)=={
        "schema_version","curriculum_standard_version","copyright_origin",
        "review_status","teacher_approvals","general_formal_certificates",
        "student_releases","cards"},"author schema or hidden approval field")
    require(auth["schema_version"]==SCHEMA
            and auth["curriculum_standard_version"]=="普通高中数学课程标准（2017年版2020年修订）"
            and auth["copyright_origin"]=="ORIGINAL_PROJECT_AUTHORED"
            and auth["review_status"]=="REVIEW_PENDING"
            and auth["teacher_approvals"]==auth["general_formal_certificates"]==auth["student_releases"]==0,
            "unauthorized approval or source")
    require(hashlib.sha256(B85.B81.dump(proofs).encode()).hexdigest()==B85.B81.EXPECTED_SHA["proofs"]
            and proofs.get("unresolved_conflicts")==10
            and proofs.get("formally_certified_steps")==0,
            "historical source SHA, unreviewed conflict or cert status changed")
    queue=proofs["step_review_queue"]
    index={r["id"]:r for r in queue}
    require(len(queue)==len(index)==538,"historical source denominator lost")
    require(type(profiles) is dict and profiles["schema_version"]=="kb-batch28-p0-conditions-v1"
            and profiles["teacher_review"]=="PENDING"
            and profiles["complete_proof_certificates"]==0
            and profiles["student_visibility"]=="NEVER_STUDENT_EXPOSE",
            "math oracle profile release changed")
    profile={p["operation"]:p for p in profiles["profiles"]}
    require(set(OPS).issubset(set(SUPPORTED)&set(profile)),"unsupported finite evidence oracle")
    require(previous["schema_version"]=="kb85-twelve-direct-history-p0-teacher-drafts-v1"
            and previous["P0_total"]==182
            and previous["combined_source_step_cards"]==60
            and previous["remaining_P0_without_source_step_cards"]==122
            and previous["unresolved_conflicts"]==10
            and previous["teacher_approvals"]==0
            and previous["formal_math_certifications"]==0
            and previous["student_published"]==0,
            "historical prior P0 baseline or teacher status tamper")
    existing={r["source_step"] for r in load(B85.AUTHOR)["cards"]}
    require(len(existing)==12,"Batch85 source-step cards collision")
    items=auth["cards"]
    require(type(items) is list and len(items)==10
            and len({c.get("source_step") for c in items if type(c) is dict})==10
            and {c.get("finite_op") for c in items if type(c) is dict}==OPS,
            "ten different P0 obligations required")
    compiled=[]
    for i,c in enumerate(items,1):
        require(type(c) is dict and set(c)==FIELDS and c["id"]==f"KB86-P{i:02d}",
                "author card identity or unexpected fields")
        sid,op=c["source_step"],c["finite_op"]
        require(sid not in existing and sid in index
                and index[sid]["risk_priority"].startswith("P0_")
                and index[sid]["review_card_id"] is None
                and sid in profile[op]["risk_step_ids"],
                "historical source step not eligible for this mathematical guard")
        require(c["kind"]=="THEOREM" and c["assumptions"]==[]
                and len(c["title"])>=8 and len(c["statement"])>=28,
                "title, statement, or unauthorized author assumptions")
        require(type(c["proof_steps"]) is list and len(c["proof_steps"])==3
                and all(type(v) is str and len(v)>=25 for v in c["proof_steps"]),
                "three distinct substantial mathematical reasoning steps required")
        require(type(c["worked_examples"]) is list and len(c["worked_examples"])==2
                and all(type(ex) is dict and set(ex)=={"question","teacher_solution"}
                        and type(ex["question"]) is str and len(ex["question"])>=12
                        and type(ex["teacher_solution"]) is str and len(ex["teacher_solution"])>=30
                        for ex in c["worked_examples"]),
                "both complete teacher-only worked examples required")
        require(type(c["hints"]) is list and len(c["hints"])==3
                and len(set(c["hints"]))==3
                and all(type(h) is str and len(h)>=15 for h in c["hints"]),
                "three-tier student-safe hints required")
        require(all(type(c[k]) is str and len(c[k])>=22
                    for k in ("wrong_method","boundary","near","far")),
                "missing misconception, counterexample boundary, or transfers")
        p=profile[op]
        require(p["status"]=="EDITORIAL_CONDITION_PROPOSAL_NOT_PROOF"
                and p["teacher_review"]=="PENDING", "oracle profile certified unexpectedly")
        good=evaluate(op,p["valid_exact_fixture"]);bad=evaluate(op,p["invalid_fixture"])
        require(good["status"]=="VERIFIED_FINITE_INSTANCE"
                and bad["status"]=="CONDITIONS_NOT_ESTABLISHED",
                "exact math witness status unexpected")
        require(all(v[k] is False for v in (good,bad)
                    for k in ("teacher_approved","student_step_verified",
                              "complete_theorem_certified","official_curriculum_atom_verified")),
                "finite witness promoted to teacher/math authority")
        row=deepcopy(c)
        row.update({
            "assumptions":[p["necessary_hypotheses"]],
            "counterexample_or_failed_premise":p["explanatory_counterexample"].replace("零概率原子", "零概率样本点"),
            "finite_valid_fixture":p["valid_exact_fixture"],
            "finite_invalid_fixture":p["invalid_fixture"],
            "finite_valid_result":good,"finite_invalid_result":bad,
            "original_step_sha256":index[sid]["source_sha256"],
            "source_step_risk_groups":index[sid]["risk_groups"],
            "source_kind":"PROJECT_HISTORICAL_DRAFT_STEP",
            "standard_version":auth["curriculum_standard_version"],
            "original_authorship":"PROJECT_AUTHORED",
            "review_status":"REVIEW_PENDING",
            "teacher_solution_visibility":"TEACHER_ONLY",
            "student_publishable":False,"student_free_text_verified":False,
            "general_theorem_formally_certified":False,
            "finite_evidence_scope":"BOUNDED_EXACT_FIXTURE_NOT_UNIVERSAL_PROOF",
            "human_teacher_reviewer":None,"official_curriculum_atom_id":None,
            "student_authoritative_index_eligible":False})
        for e in row["worked_examples"]:e["visibility"]="TEACHER_ONLY"
        compiled.append(row)
    p0=[r for r in queue if r["risk_priority"].startswith("P0_")]
    require(len(p0)==182 and sum(r["review_card_id"] is not None for r in queue)==36,
            "historical census drift")
    ledger={r["id"] for r in p0 if r["review_card_id"] is not None}
    batch81={r["linked_historical_step_id"] for r in load(B85.B81.CARDS81)["review_cards"]}
    batch85={r["source_step"] for r in load(B85.AUTHOR)["cards"]}
    batch86={r["source_step"] for r in compiled}
    require(len(ledger)==36 and len(batch81)==12 and len(batch85)==12 and len(batch86)==10,
            "historical editorial counts changed")
    previous_ids=ledger|batch81|batch85
    existing_p0=previous_ids|batch86
    # Batch81 and Batch85 reuse two steps. Four Batch86 source-step
    # checks revisit already reviewed Batch81 obligations. All ten new
    # reviews are substantial drafts, but only six grow the DISTINCT census.
    require(len(previous_ids)==58 and len(batch81&batch85)==2
            and len(batch86&previous_ids)==4
            and len(existing_p0)==64,
            "distinct P0 source-step census changed; inspect overcount")
    remaining=[r["id"] for r in p0 if r["id"] not in existing_p0]
    require(len(remaining)==118,"remaining DISTINCT P0 obligations not conserved")
    return {
        "schema_version":"kb86-ten-history-p0-teacher-drafts-v1",
        "historical_steps":538,"P0_total":182,
        "previous_reported_card_links":60,
        "previous_unique_P0_steps_with_drafts":58,
        "previous_duplicate_card_links":2,
        "new_teacher_draft_cards":10,
        "new_unique_P0_steps_with_drafts":6,
        "new_supplementary_reviews_of_previously_linked_steps":4,
        "combined_reported_card_links":70,
        "combined_unique_P0_steps_with_drafts":64,
        "total_duplicate_card_links":6,
        "remaining_P0_without_source_step_cards":118,
        "remaining_P0_source_step_ids":remaining,
        "unresolved_conflicts":10,
        "source_queue_sha256":B85.B81.EXPECTED_SHA["proofs"],
        "author_sha256":hashlib.sha256(dump(auth).encode()).hexdigest(),
        "profile_sha256":hashlib.sha256(B85.PROFILES.read_bytes()).hexdigest(),
        "review_status":"REVIEW_PENDING","teacher_approvals":0,
        "formal_math_certifications":0,"student_published":0,
        "free_text_student_steps_verified":0,"cards":compiled}
def markdown(d):
    l=["# Batch86｜10项历史P0严格条件审查（待教师审核）","",
       "十份材料均绑定真实历史高风险原步骤及其源 SHA；其中六项为首次独立覆盖，四项为补充复核。",
       "逐卡提供准确前提、可审三步论证、两道原创教师侧已解例题、无效边界、错因、三级提示和迁移。",
       "**现有数学工具只证实有限输入的具体证据，不能认证全称命题；真实教师批准仍为零。**","",
       "| 来源步骤 | 数学主题 | 不可忽略的前提 |","|---|---|---|"]
    for c in d["cards"]:
        l.append(f'| {c["source_step"]} | {c["title"]} | {c["counterexample_or_failed_premise"]} |')
    l+=["",
        "**去重审计修正：**既往宣称60个已关联步骤，但其中Batch81/85重复2条，因此先前独立步骤实际为58；",
        "本批10篇原创卡中6条是真正新覆盖、4条属于对已有关联步骤的补充审查，",
        "累计70张卡对接到**64/182个不同历史P0步骤**，还有**118个未关联步骤**。",
        "全部538个历史步骤均未取得一般定理形式认证，10组历史数学冲突未裁决。"]
    return "\n".join(l)+"\n"
def main():
    a=argparse.ArgumentParser();a.add_argument("--check",action="store_true")
    opt=a.parse_args();d=build()
    for p,v in ((OUT,dump(d)),(MD,markdown(d))):
        if opt.check:require(p.is_file() and p.read_text(encoding="utf8")==v,
                             "generated P0 evidence drift "+str(p))
        else:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,encoding="utf8")
    print("Batch86 P0: 10 new drafts (6 new distinct steps + 4 supplemental); 64/182 distinct P0 links, 118 missing; 0 certified")
if __name__=="__main__":main()
