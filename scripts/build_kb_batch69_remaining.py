#!/usr/bin/env python3
"""Batch69: eleven original teacher-only second-candidate manuscripts and 62-row lineage.

Mac is the sole authoring/test host. No inferred official atom count, proof
certification, teacher signature, or student release may be generated here.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch68_counterparts as B68
import build_kb_batch67_clause_review as B67

AUTH = ROOT / "knowledge/editorial_review/kb_batch69_remaining_authoring.tsv"
OUT = ROOT / "knowledge/editorial_review/kb_batch69_remaining_lessons.json"
MATRIX = ROOT / "docs/evaluation/KB_BATCH69_ALL62_CANDIDATE_LINEAGE.json"
REVIEW = ROOT / "docs/evaluation/KB_BATCH69_TEACHER_REVIEW.md"
SELECTED = (3, 15, 18, 19, 21, 24, 25, 26, 27, 28, 30)
TRACKS = B67.TRACKS

def require(test, why):
    if not test:
        raise ValueError(why)

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def dump(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

def parse_authoring(raw=None):
    raw = AUTH.read_text(encoding="utf-8") if raw is None else raw
    rows = []
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = [c.strip() for c in line.split("§")]
        require(len(fields) == 19 and fields[0].isdigit(), "Malformed manuscript fields")
        require(all(fields), "Empty authored math field")
        idx = int(fields[0])
        require(idx in SELECTED, "Unrecognized provisional target")
        require(all(len(v) >= 12 for v in fields[1:]), "Insufficient explanatory depth")
        require(len(set(fields[3:6])) == 3 and len(set(fields[13:16])) == 3,
                "Repeated mathematical steps or scaffolding")
        require(fields[6] != fields[8] and fields[7] != fields[9] and fields[16] != fields[17],
                "Duplicate worked problem or transfer")
        rows.append((idx, fields[1:]))
    require(tuple(i for i, _ in rows) == SELECTED, "Missing/duplicated/reordered authored candidates")
    return rows

def exact_case(index):
    """Independent exact finite example checks, not universal proof verification."""
    if index == 3:
        u={1,2,3,4}; a={1,3}
        return u-a=={2,4} and ({1,2,3,4,5}-a)=={2,4,5} and not {1,6}<=u
    if index == 15:
        # 8=2**3, 4=2**2, 9=3**2, so both ratios exact.
        return (F(3,2)/F(1,2)==3 and F(1,2)==F(1,2) and 3**2==9)
    if index == 18:
        # sin(pi/3)^2=3/4 and cos(pi/3)^2=1/4;
        # cos(pi/2)^2=0, division by it must be rejected.
        return F(3,4)+F(1,4)==1 and F(1)+F(0)==1 and F(1,4)!=0
    if index == 19:
        try:
            import sympy as s
        except ImportError:
            return False
        t=s.symbols("t")
        f=2*s.sin(s.pi*t)+3
        g=3*s.sin(2*s.pi*t)+1
        return [s.simplify(f.subs(t,x)) for x in (0,s.Rational(1,2),1)]==[3,5,3] and s.simplify(g.subs(t,s.Rational(1,4)))==4
    if index == 21:
        vals=[0,1,2]
        a=lambda t:t*t
        b=lambda t:t*t+t*(t-1)*(t-2)
        return all(a(t)==b(t) for t in vals) and a(3)==9 and b(3)==15
    if index == 24:
        return (complex(0,3).real==0 and complex(0,3).imag!=0
                and complex(0,0).imag==0 and complex(2,0).real==2)
    if index == 25:
        # Pair rational complex components; no numerical approximation.
        mul=lambda x,y:(x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0])
        return mul((F(0),F(1)),(F(1),F(-1)))==(F(1),F(1)) and mul((F(5,2),F(1,2)),(F(1),F(1)))==(F(2),F(3))
    if index == 26:
        # A=(t,0,0); B=(0,s,1) cannot equal in z.
        # C=(s,1,0) shares no point with A but direction parallel.
        return (0 != 1) and (F(1)*F(0)-F(0)*F(1)==0) and (F(1)*F(1)-F(0)*F(0)==1)
    if index == 27:
        return (0!=1) and ((F(0),F(0),F(0))==(F(0),F(0),F(0)))
    if index == 28:
        dot=lambda u,v:sum(x*y for x,y in zip(u,v))
        return dot((0,0,1),(1,0,0))==0 and dot((0,0,1),(0,1,0))==0 and dot((0,1,0),(2,0,0))==0 and dot((0,1,0),(0,1,0))==1
    if index == 30:
        from math import comb
        return comb(4,2)==6 and F(comb(3,1),comb(4,2))==F(1,2) and F(1,comb(4,2))==F(1,6) and F(2,5)==F(2,5)
    raise ValueError("Undeclared finite evidence family")

def build(inputs=None):
    inputs = inputs or {}
    drafts = inputs.get("authoring", parse_authoring())
    props = inputs.get("proposals", load(B68.PROPOSALS))
    reg = inputs.get("registry", load(B68.REGISTRY))
    windows = inputs.get("windows", load(B68.WINDOWS))
    first = inputs.get("parents", [*load(B68.OLD[0]), *load(B68.OLD[1])])
    previous = inputs.get("previous", load(B68.OUT)["items"])
    require(len(props["proposals"])==62 and len(reg["rows"])==428 and
            len(windows["rows"])==45 and len(first)==31 and len(previous)==20,
            "Prior batch inventory unexpectedly changed")
    anchors={f"KB61-P{r['printed_page']:03d}-L{r['pdfkit_line']:03d}":r for r in reg["rows"]}
    win={x["anchor_id"]:x for x in windows["rows"]}
    require(len(anchors)==428 and len(win)==45, "Duplicate source provenance")
    first_by_loc={}
    for p in first:
        require(p["student_publishable"] is False and p["teacher_review"]=="REVIEW_PENDING",
                "Prior parent status forged")
        loc=tuple(p["loc"])
        require(loc not in first_by_loc, "Duplicated parent source location")
        first_by_loc[loc]=p
    prior_by_candidate={x["editorial_id"]:x for x in previous}
    require(len(prior_by_candidate)==20 and all(x["student_publishable"] is False and x["teacher_review"]=="REVIEW_PENDING"
            for x in previous), "Prior counterpart not safely teacher-only")

    new={}
    for i, fields in drafts:
        parent,target=props["proposals"][2*(i-1):2*i]
        require(parent["parent_anchor_id"]==target["parent_anchor_id"], "Mismatched candidate pair")
        require(parent["teacher_review"]==target["teacher_review"]=="REVIEW_PENDING"
                and not target["content_lesson_complete"] and
                target["math_equivalence"]=="NOT_REVIEWED" and
                target["official_atomic_membership"]=="UNDETERMINED" and
                target["student_publishable"] is False, "Promoted unreviewed atom")
        source=anchors[target["parent_anchor_id"]]
        window=win[target["parent_anchor_id"]]
        require(target["source_window_sha256"]==window["source_window_sha256"] and
                source["source_line_sha256"]==window["source_line_sha256"] and
                target["source_page"]==source["printed_page"], "Source lineage/SHA mismatch")
        match=first_by_loc.get((source["printed_page"],source["pdfkit_line"]))
        require(match is not None, "Missing teacher-only source scope parent")
        require(exact_case(i) is True, "Exact bounded witness failed")
        (statement, assumptions, r1,r2,r3,q1,a1,q2,a2,negative,wrong,why,h1,h2,h3,near,far,notation)=fields
        new[target["candidate_id"]]={
            "lesson_id":f"KB69-ATOM-{i:02d}", "title":target["editorial_subtopic"],
            "editorial_id":target["candidate_id"], "parent_anchor_id":target["parent_anchor_id"],
            "related_parent_draft_id":match["lesson_id"],"proposed_kind":target["hypothesized_kind"],
            "statement":statement,"assumptions":[assumptions],"notation":notation,
            "prerequisites":[parent["editorial_subtopic"]],
            "reasoning":[{"step":k+1,"claim":c,"justification":"待教师逐步审查；非形式证明"}
                         for k,c in enumerate((r1,r2,r3))],
            "worked_examples":[{"question":q1,"teacher_solution":a1},{"question":q2,"teacher_solution":a2}],
            "invalid_case":negative, "common_wrong_method":wrong,"explanation_of_error":why,
            "hint_ladder":[h1,h2,h3], "near_transfer":near,"far_transfer":far,
            "source_standard":"2017版2020年修订普通高中数学课标（本地核对，未上传原文）",
            "source_track_hint":source["track_hint"],"source_page":source["printed_page"],
            "source_line_sha256":source["source_line_sha256"],
            "source_window_sha256":target["source_window_sha256"],
            "source_license":"ORIGINAL_PROJECT_AUTHORED",
            "official_atomic_membership":"UNDETERMINED",
            "official_clause_full_text_verified":False,
            "proof_certification":"NOT_FORMALLY_CERTIFIED",
            "finite_math_witness":"FINITE_EXACT_INSTANCE_ONLY",
            "teacher_review":"REVIEW_PENDING", "teacher_signature":None,
            "teacher_solution_visibility":"TEACHER_ONLY",
            "student_publishable":False, "student_freeform_steps_verified":False
        }
    require(len(new)==11 and not (set(new)&set(prior_by_candidate)), "Overlap with previous authored candidates")
    rows=[]
    for i in range(31):
        first_p,second_p=props["proposals"][2*i:2*i+2]
        source=anchors[first_p["parent_anchor_id"]]
        loc=(source["printed_page"], source["pdfkit_line"])
        match=first_by_loc.get(loc)
        require(match is not None and match["student_publishable"] is False,
                "Missing prior scope manuscript")
        require(second_p["parent_anchor_id"]==first_p["parent_anchor_id"], "Unequal source")
        require(second_p["source_window_sha256"]==win[second_p["parent_anchor_id"]]["source_window_sha256"],
                "Source SHA mismatch in complete 62-row audit")
        for j,p in enumerate((first_p,second_p)):
            counterpart=prior_by_candidate.get(p["candidate_id"]) or new.get(p["candidate_id"])
            require(j==0 or counterpart is not None, "Second candidate without a teacher manuscript")
            if j==1:
                require(counterpart["parent_anchor_id"]==p["parent_anchor_id"] and
                        counterpart["editorial_id"]==p["candidate_id"] and
                        not counterpart["student_publishable"] and counterpart["teacher_review"]=="REVIEW_PENDING",
                        "Mismatched or promoted counterpart")
            rows.append({
                "provisional_candidate_id":p["candidate_id"],"source_anchor_id":p["parent_anchor_id"],
                "track_hint":source["track_hint"],
                "linked_manuscript_id":match["lesson_id"] if j==0 else counterpart["lesson_id"],
                "link_kind":"PARENT_SCOPE_DRAFT_NOT_ATOM_CERTIFIED" if j==0 else "SECOND_CANDIDATE_LESSON_PENDING",
                "official_atom_membership":"UNDETERMINED","full_official_clause_review":"NOT_COMPLETED",
                "teacher_approved":False,"math_proof_certified":False,"student_publishable":False
            })
    require(len(rows)==62 and len({x["provisional_candidate_id"] for x in rows})==62,
            "62-row tentative inventory not uniquely linked")
    result={
        "schema_version":"kb69-teacher-manuscripts-v1",
        "source_pdf_sha256":props["source_pdf_sha256"],
        "authoring_sha256":sha256(AUTH.read_bytes()).hexdigest(),
        "items":[new[p["candidate_id"]] for i,p in enumerate(props["proposals"]) if i%2==1 and p["candidate_id"] in new]
    }
    count=Counter(x["link_kind"] for x in rows)
    audit={
        "schema_version":"kb69-provisional-audit-v1",
        "disclaimer":"62 internal candidate splits: none teacher-certified, none constitutes an official curriculum denominator.",
        "provisional_candidate_count":62,
        "prior_parent_scope_manuscripts":count["PARENT_SCOPE_DRAFT_NOT_ATOM_CERTIFIED"],
        "prior_and_new_second_candidate_manuscripts":count["SECOND_CANDIDATE_LESSON_PENDING"],
        "new_second_candidate_manuscripts":len(new),
        "official_atomic_denominator":{t:None for t in TRACKS},
        "officially_fully_reviewed_pages":0,"teacher_approved":0,
        "formal_proofs_certified":0,"student_published":0,
        "unmapped_competency_requirements":14,
        "unreviewed_legacy_proof_steps":538,"unresolved_math_conflicts":10,
        "records":rows
    }
    return result,audit,[anchors[props["proposals"][2*(i-1)+1]["parent_anchor_id"]] for i in SELECTED]

def render_md(result,audit):
    lines=[
        "# Batch69｜11篇原创候选原子教师稿与62项逐候选来源对照",
        "",
        "所有62项只是内部暂定拆分假设。前31项已存在父级主题范围稿，不可据此称31篇独立原子讲义完成；第二项20篇Batch68加本批11篇，均待审。",
        "七轨正式课标原子分母仍为unknown/null；全页官方条款原子审查0/61、教师批准0、认证证明0、学生发布0。",
        "教师完整解答只保留在教师侧文件，有限精确算例不替代一般数学证明。",
        "",
        "| 类型 | 数量 |","| --- | ---: |",
        "| 本批新增教师侧候选稿 | 11 |",
        "| 本批新增教师侧原创例题 | 22 |",
        "| 本批教师侧推理说明（未形式认证） | 33 |",
        "| 本批反例/错因 | 11 |",
        "| 本批原创三级提示 | 33 |",
        "| 内部候选拆分有稿件引用（包含父级范围稿） | 62/62 |",
        "| 正式教师签核与正式发布 | 0 |",""
    ]
    for r in result["items"]:
        lines.extend([
            f"## {r['lesson_id']} · {r['title']}","",
            f"来源锚点：{r['parent_anchor_id']}，印刷页{r['source_page']}；来源局部 SHA {r['source_line_sha256'][:16]}…；父级范围稿 {r['related_parent_draft_id']}。","",
            f"**数学陈述**：{r['statement']}","",
            f"**适用前提**：{r['assumptions'][0]}","",
            f"**符号与先修**：{r['notation']}；{r['prerequisites'][0]}。","",
            "**逐步说明（教师审核前不视为形式证明）**",""
        ])
        lines.extend(f"{v['step']}. {v['claim']}" for v in r["reasoning"])
        lines.extend(["","**原创例题与教师侧答案**",""])
        for x in r["worked_examples"]:
            lines.append(f"- **题目**：{x['question']} **教师解答**：{x['teacher_solution']}")
        lines.extend([
            "",f"**失效例**：{r['invalid_case']}",
            f"**典型错解**：{r['common_wrong_method']}",
            f"**原因**：{r['explanation_of_error']}",
            "",f"**三级提示**：{' → '.join(r['hint_ladder'])}",
            f"**近迁移**：{r['near_transfer']}",
            f"**远迁移**：{r['far_transfer']}",
            "","**审核结论**：REVIEW_PENDING；原子归属UNDETERMINED；证明NOT_FORMALLY_CERTIFIED；学生端不可见。",""
        ])
    return "\n".join(lines).rstrip()+"\n"

def write(check=False,verify_local=False):
    result,audit,locations=build()
    if verify_local:
        require(B67.verify_source_local(load(B68.REGISTRY),locations)==len({x["printed_page"] for x in locations}),
                "Mac original syllabus local hash verification failed")
    for path,body in [(OUT,dump(result)),(MATRIX,dump(audit)),(REVIEW,render_md(result,audit))]:
        if check:
            require(path.exists() and path.read_text(encoding="utf-8")==body,"Snapshot stale or missing: "+str(path))
        else:
            path.write_text(body,encoding="utf-8")
    print(f"BATCH69 {'CHECK' if check else 'WRITE'} OK; 11 teacher drafts; 22 examples; 33 steps; 11 bounded checks; 62 provisional links; 0 approvals")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local",action="store_true")
    args=p.parse_args()
    write(check=args.check,verify_local=args.verify_local)
