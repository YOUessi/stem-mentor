#!/usr/bin/env python3
"""Batch87 seven full teacher-only cross-domain math drafts with bounded exact witnesses."""
from __future__ import annotations
import argparse,hashlib,json,sys
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch87_semantic_review as S
from app.kb_batch87_exact_oracles import evaluate,SUPPORTED
AUTHOR=ROOT/"knowledge/editorial_review/kb_batch87_guarded_math_authoring.json"
OUT=ROOT/"knowledge/editorial_review/kb_batch87_guarded_math_teacher_drafts.json"
MD=ROOT/"docs/evaluation/KB_BATCH87_GUARDED_MATH_LESSONS.md"
SCHEMA="kb87-seven-source-anchored-guarded-math-teacher-drafts-v1"
FIELDS={"id","source_review_id","kind","title","definition","symbols","assumptions",
        "statement","proof_steps","validity","boundary","wrong_method",
        "worked_examples","hints","near","far","prerequisites",
        "finite_op","finite_valid_fixture","finite_invalid_fixture","expected_exact"}
def require(ok,msg):
    if not ok:raise ValueError(msg)
def load(p):return json.loads(Path(p).read_text(encoding="utf8"))
def dump(v):return json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
def build(auth=None,coverage=None):
    auth=load(AUTHOR) if auth is None else auth
    coverage=S.build() if coverage is None else coverage
    require(type(auth) is dict and set(auth)=={
        "schema_version","curriculum_standard_version","authorship","review_status",
        "teacher_approvals","formal_general_theorem_certificates","student_published",
        "cards"},"teacher authoring schema or hidden field")
    require(auth["schema_version"]=="kb87-seven-guarded-math-lessons-authoring-v1"
        and auth["curriculum_standard_version"]=="普通高中数学课程标准（2017年版2020年修订）"
        and auth["authorship"]=="ORIGINAL_PROJECT_MATERIAL"
        and auth["review_status"]=="REVIEW_PENDING"
        and auth["teacher_approvals"]==auth["formal_general_theorem_certificates"]==auth["student_published"]==0,
        "teacher/general certificate/student release spoof")
    require(coverage["schema_version"]==S.SCHEMA
        and coverage["cumulative_editorial_count"]==428
        and coverage["pending_editorial_count"]==0
        and coverage["official_curriculum_atom_denominator"] is None
        and coverage["full_page_teacher_reviews"]==0
        and coverage["teacher_approved"]==0
        and coverage["student_deep_content_published"]==0,
        "source coverage authority is incomplete or modified")
    newsource={r["review_id"]:r for r in coverage["new_rows"]}
    cards=auth["cards"]
    require(type(cards) is list and len(cards)==7
            and all(type(c) is dict and set(c)==FIELDS for c in cards)
            and len({c["id"] for c in cards})==7
            and len({c["source_review_id"] for c in cards})==7,
            "seven complete unique source-linked teacher modules required")
    compiled=[]
    for i,c in enumerate(cards,1):
        require(c["id"]==f"KB87-M{i:02d}"
            and c["source_review_id"] in newsource
            and newsource[c["source_review_id"]]["semantic_role_provisional"]=="MATHEMATICAL_REQUIREMENT",
            "lesson ID or source math requirement not valid")
        require(c["kind"] in {"CONCEPT","THEOREM","METHOD"} and len(c["title"])>=8,
                "lesson type or title invalid")
        require(all(type(c[k]) is str and len(c[k])>=({"definition":35,"statement":30,"validity":25,"boundary":25,"wrong_method":25,"near":20,"far":20}[k]) for k in
                    ("definition","statement","validity","boundary","wrong_method","near","far")),
                "missing substantive definition, theorem boundary, misconception, or transfers")
        require(type(c["symbols"]) is list and len(c["symbols"])>=3
                and all(type(x) is str and len(x)>=5 for x in c["symbols"]),
                "formal symbols required")
        require(type(c["assumptions"]) is list and len(c["assumptions"])>=2
                and all(type(x) is str and len(x)>=4 for x in c["assumptions"]),
                "all mathematical hypotheses must be explicit")
        require(type(c["proof_steps"]) is list and len(c["proof_steps"])==4
                and all(type(s) is list and len(s)==2
                        and all(type(y) is str and len(y)>=3 for y in s)
                        and len(s[1])>=20 for s in c["proof_steps"]),
                "four substantial independently reviewable derivation steps required")
        require(type(c["worked_examples"]) is list and len(c["worked_examples"])==2
                and all(type(ex) is dict and set(ex)=={"question","teacher_solution"}
                        and all(type(v) is str and len(v)>=(12 if k=="question" else 20) for k,v in ex.items())
                        for ex in c["worked_examples"]),
                "two substantial teacher-only worked examples required")
        require(type(c["hints"]) is list and len(c["hints"])==3
                and len(set(c["hints"]))==3
                and all(type(h) is str and len(h)>=10 for h in c["hints"]),
                "three progressively helpful student-safe hints required")
        require(type(c["prerequisites"]) is list and len(c["prerequisites"])>=2
                and all(type(x) is str and len(x)>=4 for x in c["prerequisites"]),
                "unreviewed prerequisite topic names required")
        require(c["finite_op"] in SUPPORTED
                and type(c["finite_valid_fixture"]) is dict
                and type(c["finite_invalid_fixture"]) is dict
                and type(c["expected_exact"]) is str,
                "unsupported finite evidence operation")
        good=evaluate(c["finite_op"],c["finite_valid_fixture"])
        bad=evaluate(c["finite_op"],c["finite_invalid_fixture"])
        require(good["status"]=="VERIFIED_FINITE_INSTANCE"
            and good["exact_value"]==c["expected_exact"]
            and bad["status"]=="CONDITIONS_NOT_ESTABLISHED"
            and all(v["teacher_approved"] is False
                    and v["general_theorem_certified"] is False
                    and v["student_free_text_verified"] is False
                    and v["student_publishable"] is False
                    for v in (good,bad)),"bounded independent evidence mismatch")
        source=newsource[c["source_review_id"]]
        compiled.append({**deepcopy(c),
            "source_pdf_sha256":source["source_pdf_sha256"],
            "source_line_sha256":source["source_line_sha256"],
            "source_page_pdfkit_sha256":source["source_page_pdfkit_sha256"],
            "printed_page":source["printed_page"],"pdfkit_line":source["pdfkit_line"],
            "track":source["track"],"official_atom_id":None,
            "prerequisite_ids_confirmed":False,
            "teacher_approval":None,"review_status":"REVIEW_PENDING",
            "teacher_solution_visibility":"TEACHER_ONLY","student_publishable":False,
            "student_authoritative_index_eligible":False,
            "general_theorem_formally_certified":False,
            "student_free_text_step_verified":False,
            "finite_evidence_scope":"EXACT_FINITE_FIXTURES_NOT_UNIVERSAL_THEOREM",
            "finite_good_witness":good,"finite_invalid_witness":bad,
            "worked_examples":[{**ex,"visibility":"TEACHER_ONLY"} for ex in c["worked_examples"]]})
    return {"schema_version":SCHEMA,"standard_version":auth["curriculum_standard_version"],
        "author_sha256":hashlib.sha256(dump(auth).encode()).hexdigest(),
        "source_coverage_schema":S.SCHEMA,"lesson_count":len(compiled),
        "teacher_approvals":0,"general_formal_math_certificates":0,
        "official_curriculum_atom_denominator":None,
        "student_releases":0,"student_free_text_step_verifications":0,
        "review_status":"REVIEW_PENDING","cards":compiled}
def markdown(d):
    lines=["# Batch87｜七份跨域原创教师审稿课程（严格有限证据）","",
        "新增7个课程数学来源锚点链接的原创完整教学单元草案，每份有定义、条件、逐步论证、两道教师侧解题、反例错因、三级提示及近远迁移。",
        "**所有素材仍为REVIEW_PENDING，教师已批准0，一般命题形式认证0，学生正式发布0。**",
        "有限有理数/SymPy核验只能证实所列测试输入，并不替代一般定理证明或教师确认。",""]
    for c in d["cards"]:
        lines+=[f'## {c["id"]}｜{c["title"]}',"",
           f'来源：{c["source_review_id"]} / {c["track"]}；审核：REVIEW_PENDING。',"",
           f'**正式定义：**{c["definition"]}',"",
           "**记号：**"+"；".join(c["symbols"]),"",
           "**前提：**"+"；".join(c["assumptions"]),"",
           f'**数学陈述：**{c["statement"]}',"",
           "**逐步推理（待独立教师核对）：**"]
        for i,(name,detail) in enumerate(c["proof_steps"],1):
            lines.append(f'{i}. **{name}：**{detail}')
        lines+=["",f'**合法性说明：**{c["validity"]}',"",
            f'**反例/不适用边界：**{c["boundary"]}',"",
            f'**典型错因：**{c["wrong_method"]}',"",
            "**教师侧题族（不得直接泄漏给自主挑战学生）：**"]
        for i,ex in enumerate(c["worked_examples"],1):
            lines.append(f'{i}. 题目：{ex["question"]}。**教师解答：**{ex["teacher_solution"]}')
        lines+=["","**学生提示阶梯（不直接输出教师答案）：**"]
        for i,h in enumerate(c["hints"],1):
            lines.append(f'{i}. {h}')
        lines+=["",f'**近迁移：**{c["near"]}',"",
                 f'**远迁移：**{c["far"]}',"",
                 "**先修主题（未完成官方ID核对）：**"+"；".join(c["prerequisites"]),"",
                 f'**独立有限核验：**{c["finite_op"]} → {c["finite_good_witness"]["exact_value"]}；',
                 "非法边界→CONDITIONS_NOT_ESTABLISHED。",""]
    return "\n".join(lines).rstrip("\n")+"\n"
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
    x=build()
    for path,value in ((OUT,dump(x)),(MD,markdown(x))):
        if args.check:
            require(path.is_file() and path.read_text(encoding="utf8")==value,"generated lesson artifact drift")
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value,encoding="utf8")
    print("Batch87 teacher-only originals: 7 full modules x2 solved examples x4 reasoning steps; finite exact witnesses valid and invalid.")
if __name__=="__main__":main()
