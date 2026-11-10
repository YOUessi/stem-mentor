#!/usr/bin/env python3
"""Twelve original teacher-only history-P0 reviews, with exact *finite* witnesses.

The witness oracle is pre-existing audited code. New value is a source-step-specific
full mathematical review draft, not a newly certified mathematical theorem.
"""
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
from copy import deepcopy
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.kb_batch28_condition_oracles import evaluate,SUPPORTED
import build_kb_batch81_risk_census as B81
AUTHOR=ROOT/"knowledge/editorial_review/kb_batch85_p0_authoring.json"
PROFILES=ROOT/"knowledge/proof/batch28_p0_condition_profiles.json"
OUT=ROOT/"knowledge/editorial_review/kb_batch85_p0_teacher_cards.json"
MD=ROOT/"docs/evaluation/KB_BATCH85_P0_HISTORY_GUARDS.md"
EXTRA_HYPOTHESES={
"log_product_domain":"三个实数对数表达式同时有定义；不能单凭xy>0推断x与y分别为正。",
"log_quotient_domain":"商表达式本身与拆分后的每一项须分别在实数对数定义域内。",
"log_change_base_domain":"新底数b下log_b(a)不为零，换底除法才可逆。",
"quadratic_discriminant":"实根的判定限定在实数域，复数域根数结论不能混淆。",
"amgm_rational_roots":"主值平方根为非负，取等须逐步推出a=b。",
"line_circle":"平面使用相同的欧氏坐标系，距离的分母A²+B²严格为正。",
"circle_circle":"同心时必须先单独分支，不使用不同心三角形交点数结论。",
"parabola_focus":"两种距离均非负，平方相等恢复距离相等不产生额外符号分支。",
"ellipse_tangent":"切点不仅要满足曲线方程，椭圆的梯度在此点还必须非零。",
"cauchy_schwarz":"定理容许零向量，带||v||²分母的证明步骤须单独处理v=0。",
"quotient_polynomial_derivative":"v在求导点连续且非零，故在足够小邻域内依然非零。",
"vector_angle":"与内积等于零的代数关系不同，角度定义要求两条有方向的非零向量。",
}
FIELDS={"id","source_step","finite_op","title","kind","statement",
"assumptions","proof_steps","worked_examples","wrong_method","boundary","near","far","hints"}

def require(ok,msg):
    if not ok:raise ValueError(msg)
def load(p):return json.loads(Path(p).read_text(encoding="utf8"))
def dump(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def build(auth=None,proofs=None,profiles=None):
    auth=load(AUTHOR) if auth is None else auth
    proofs=load(B81.PROOFS) if proofs is None else proofs
    profiles=load(PROFILES) if profiles is None else profiles
    require(type(auth) is dict and set(auth)=={
        "schema_version","curriculum_standard_version","copyright_origin",
        "review_status","teacher_approvals","general_formal_certificates",
        "student_releases","cards"},"author schema or extra approval fields")
    require(auth["schema_version"]=="kb85-12-history-p0-source-linked-original-drafts-v1"
            and auth["copyright_origin"]=="ORIGINAL_PROJECT_AUTHORED"
            and auth["review_status"]=="REVIEW_PENDING"
            and auth["teacher_approvals"]==auth["general_formal_certificates"]==auth["student_releases"]==0
            and auth["curriculum_standard_version"]=="普通高中数学课程标准（2017年版2020年修订）",
            "unauthorized publisher or source")
    require(hashlib.sha256(B81.dump(proofs).encode()).hexdigest()==B81.EXPECTED_SHA["proofs"],
            "frozen proof queue tamper")
    require(proofs.get("unresolved_conflicts")==10
            and proofs.get("formally_certified_steps")==0,
            "history conflict/certification spoofing")
    q=proofs["step_review_queue"]
    require(len(q)==538 and len({r["id"] for r in q})==538,"historical denominator drift")
    index={r["id"]:r for r in q}
    require(type(profiles) is dict and profiles["schema_version"]=="kb-batch28-p0-conditions-v1"
            and profiles["teacher_review"]=="PENDING"
            and profiles["complete_proof_certificates"]==0
            and profiles["student_visibility"]=="NEVER_STUDENT_EXPOSE",
            "profile evidence or teacher state invalid")
    profile={p["operation"]:p for p in profiles["profiles"]}
    rows=auth["cards"]
    require(type(rows) is list and len(rows)==12
            and len({r.get("source_step") for r in rows if type(r) is dict})==12
            and len({r.get("finite_op") for r in rows if type(r) is dict})==12,
            "12 distinct historical review obligations required")
    compiled=[]
    for i,c in enumerate(rows,1):
        require(type(c) is dict and set(c)==FIELDS
                and c["id"]==f"KB85-P{i:02d}","card identity, extra fields or order")
        sid,op=c["source_step"],c["finite_op"]
        require(op in EXTRA_HYPOTHESES and op in SUPPORTED
                and op in profile and sid in profile[op]["risk_step_ids"],
                "historical step to actual oracle source mismatch")
        source=index.get(sid)
        require(source is not None and source["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE"
                and source["review_card_id"] is None
                and source["review_status"]=="REVIEW_PENDING"
                and source["formal_certification"]=="NOT_FORMALLY_VERIFIED"
                and source["student_publishable"] is False,
                "historical step missing, already covered or improperly promoted")
        require(c["kind"] in ("THEOREM","METHOD")
                and len(c["title"])>=7 and len(c["statement"])>=28
                and c["assumptions"]==[],
                "poorly formed statement or hidden author assumptions")
        require(type(c["proof_steps"]) is list and len(c["proof_steps"])==3
                and all(type(x) is str and len(x)>=20 for x in c["proof_steps"]),
                "missing independent three-stage derivation")
        require(type(c["worked_examples"]) is list and len(c["worked_examples"])==2
                and all(type(x) is dict and set(x)=={"question","teacher_solution"}
                        and len(x["question"])>=12 and len(x["teacher_solution"])>=25
                        for x in c["worked_examples"]),
                "missing two distinct complete worked examples")
        require(type(c["hints"]) is list and len(c["hints"])==3
                and all(type(z) is str and len(z)>=13 for z in c["hints"]),
                "missing 3 tiered hints")
        require(all(type(c[k]) is str and len(c[k])>=20
                    for k in ("wrong_method","boundary","near","far")),
                "missing misconception, boundary, or transfer")
        pr=profile[op]
        require(pr["status"]=="EDITORIAL_CONDITION_PROPOSAL_NOT_PROOF"
                and pr["teacher_review"]=="PENDING","profile status changed")
        positive=evaluate(op,pr["valid_exact_fixture"])
        negative=evaluate(op,pr["invalid_fixture"])
        require(positive["status"]=="VERIFIED_FINITE_INSTANCE"
                and negative["status"]=="CONDITIONS_NOT_ESTABLISHED",
                "finite typed positive/invalid guard mismatch")
        require(all(not e[k] for e in (positive,negative)
                    for k in ("teacher_approved","student_step_verified",
                              "complete_theorem_certified","official_curriculum_atom_verified")),
                "finite evidence improperly promoted")
        row=deepcopy(c)
        row.update({
            "assumptions":[pr["necessary_hypotheses"],EXTRA_HYPOTHESES[op]],
            "counterexample_or_failed_premise":pr["explanatory_counterexample"],
            "finite_valid_fixture":pr["valid_exact_fixture"],
            "finite_invalid_fixture":pr["invalid_fixture"],
            "finite_valid_result":positive,"finite_invalid_result":negative,
            "original_step_sha256":source["source_sha256"],
            "source_step_risk_groups":source["risk_groups"],
            "source_kind":"PROJECT_HISTORICAL_DRAFT_STEP",
            "standard_version":auth["curriculum_standard_version"],
            "original_authorship":"PROJECT_AUTHORED",
            "review_status":"REVIEW_PENDING",
            "teacher_solution_visibility":"TEACHER_ONLY",
            "student_publishable":False,"student_free_text_verified":False,
            "general_theorem_formally_certified":False,
            "finite_evidence_scope":"BOUNDED_EXACT_FIXTURE_NOT_UNIVERSAL_PROOF",
            "human_teacher_reviewer":None,"official_curriculum_atom_id":None,
            "student_authoritative_index_eligible":False,
        })
        for ex in row["worked_examples"]:ex["visibility"]="TEACHER_ONLY"
        compiled.append(row)
    allp0=[r for r in q if r["risk_priority"].startswith("P0_")]
    require(len(allp0)==182 and len([r for r in q if r["review_card_id"]])==36,
            "frozen historical risk and prior card baseline")
    return {
        "schema_version":"kb85-twelve-direct-history-p0-teacher-drafts-v1",
        "historical_steps":538,"P0_total":182,
        "previous_source_step_cards":48,
        "new_source_step_cards":12,"combined_source_step_cards":60,
        "remaining_P0_without_source_step_cards":122,
        "unresolved_conflicts":10,
        "source_queue_sha256":B81.EXPECTED_SHA["proofs"],
        "author_sha256":hashlib.sha256(dump(auth).encode()).hexdigest(),
        "source_profile_sha256":hashlib.sha256(PROFILES.read_bytes()).hexdigest(),
        "review_status":"REVIEW_PENDING","teacher_approvals":0,
        "formal_math_certifications":0,"student_published":0,
        "free_text_student_steps_verified":0,
        "cards":compiled}
def markdown(d):
    l=["# Batch85 | 12 份新建历史 P0 教师侧分步论证审稿卡","",
       "**本批十二项均直接绑定未关联历史 P0 原步骤的 SHA。人工教师批准0；数学全称证明形式认证0。**",
       "12道独立条件失败见证 + 12道前提合法有限例，仅证实这些实例，不认证一般命题。",
       "每卡提供三段论证、两道教师侧完整例题、失效边界、典型错误、三级提示与迁移题。",
       "源SHA与原始材料校验通过不代表其原始自然语言推理自动正确。","",
       "| 历史P0步骤 | 审稿主题 | 失败前提 |",
       "|---|---|---|"]
    for c in d["cards"]:
        l.append(f'| {c["source_step"]} | {c["title"]} | {c["counterexample_or_failed_premise"]} |')
    l.extend(["", "累计历史来源步骤直接挂接教师草案：60/182 P0，仍缺122；538步仍无形式认证。",
              "学生检索与实时自由步骤验证必须继续默认拒绝，不能自动发布。"])
    return "\n".join(l)+"\n"
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");a=ap.parse_args()
    doc=build()
    for path,value in ((OUT,dump(doc)),(MD,markdown(doc))):
        if a.check:require(path.exists() and path.read_text(encoding="utf8")==value,
                          "generated P0 artifact drift "+str(path))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value,encoding="utf8")
    print("Batch85 P0: +12 linked historical cards; 60/182 P0 card-linked; 122 no card; 0 certified")
if __name__=="__main__":main()
