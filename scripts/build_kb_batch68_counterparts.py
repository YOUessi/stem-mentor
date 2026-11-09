#!/usr/bin/env python3
"""Batch68 original counterpart lessons: never an official syllabus denominator.

Build solely on the authorized Mac. All outputs are teacher-side DRAFT/REVIEW_PENDING.
Exact finite witnesses are not universal theorem certificates or freeform student grading.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch67_clause_review as prior

DATA = ROOT / "knowledge/editorial_review/kb_batch68_counterpart_authoring.tsv"
HINTS = ROOT / "knowledge/editorial_review/kb_batch68_topic_hints.tsv"
PROPOSALS = ROOT / "curriculum/highschool_math/k00_batch63_provisional_atom_proposals.json"
WINDOWS = ROOT / "curriculum/highschool_math/k00_batch63_context_windows.json"
REGISTRY = ROOT / "curriculum/highschool_math/k00_batch61_source_anchor_registry.json"
OLD = (ROOT / "knowledge/editorial_review/kb_batch64_deep_lessons.json",
       ROOT / "knowledge/editorial_review/kb_batch65_remaining_substantive_lessons.json")
OUT = ROOT / "knowledge/editorial_review/kb_batch68_counterpart_lessons.json"
MATRIX = ROOT / "docs/evaluation/KB_BATCH68_CANDIDATE_LINK_MATRIX.json"
REVIEW = ROOT / "docs/evaluation/KB_BATCH68_COUNTERPART_TEACHER_REVIEW.md"
SELECTED = (1,2,4,5,6,7,8,9,10,11,12,13,14,16,17,20,22,23,29,31)
TRACKS = prior.TRACKS

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def dump(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

def require(ok, msg):
    if not ok:
        raise ValueError(msg)

def parse_authoring(raw=None):
    if raw is None:
        raw = DATA.read_text(encoding="utf-8")
    rows = []
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        cols = [c.strip() for c in line.split("§")]
        require(len(cols) == 15, "Each authored lesson requires exactly fifteen populated fields")
        require(all(cols), "Blank mathematical teaching component")
        require(cols[0].isdigit(), "Invalid counterpart index")
        idx = int(cols[0])
        require(idx in SELECTED, "Unauthorized scope/index")
        require(all(len(c) >= 13 for c in cols[1:] if c not in (cols[6], cols[7], cols[8], cols[9])),
                "Math explanation/reasoning/transfer too shallow")
        rows.append((idx, cols[1:]))
    require([i for i,_ in rows] == list(SELECTED), "Missing, repeated or reordered authored counterparts")
    return rows

def parse_hints(raw=None):
    if raw is None:
        raw=HINTS.read_text(encoding="utf-8")
    rows={}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        cols=[v.strip() for v in line.split("§")]
        require(len(cols)==5 and cols[0].isdigit(), "Invalid notation/hint fields")
        i=int(cols[0])
        require(i in SELECTED and i not in rows, "Duplicated or unknown hint index")
        require(len(cols[1])>=4 and all(len(h)>=14 for h in cols[2:]),
                "Missing topic-specific notation or progressively useful hint")
        require(len(set(cols[2:]))==3, "Repeating hints does not scaffold understanding")
        rows[i]=cols[1:]
    require(tuple(rows)==SELECTED, "Expected 20 matching source-specific hint triplets")
    return rows

def exact_case(i):
    """Small independent integer/Fraction witnesses. No universal proof assertions."""
    if i == 1:
        a={1,2}
        return (1 in a, frozenset({1}).issubset(a), frozenset({1}) in a) == (True,True,False)
    if i == 2:
        a={1,2}; b={2,1,1}; c={1,3}
        return (a<=b,b<=a,a==b,a==c) == (True,True,True,False)
    if i == 4:
        return all((x==2) == (2*x==4) for x in range(-8,9)) and (-1)**2==1 and -1!=1
    if i == 5:
        return any(x<0 for x in (-2,0,3)) and not any(x*x==1 for x in (0,2,4))
    if i == 6:
        d=(0,1)
        return not(any(x!=0 for x in d) == False) and (not any(x<0 for x in d)) == all(x>=0 for x in d)
    if i == 7:
        roots={x for x in range(-3,4) if x*x==x}
        return roots=={0,1} and (F(0)*2==F(0)*3) and (2!=3)
    if i == 8:
        return F(1+9,2)>=F(3) and F(4+4,2)==4 and F(-1-4,2)<F(2)
    if i == 9:
        a,b,c=F(2),F(8),F(8)
        return b*b-4*a*c==0 and -b/(2*a)==-2 and F(0)*2!=2
    if i == 10:
        q=lambda x: x*x-1
        return q(F(-2))>0 and q(F(0))<0 and q(F(1))==0 and q(F(2))>0
    if i == 11:
        def v(x):return x if x<=0 else x*x
        return v(F(0))==0 and (1!=2) and ((-1)<0)
    if i == 12:
        d=[F(j,10) for j in range(0,11)]
        return max(d)==1 and all(x<F(1) for x in [F(j,10) for j in range(1,10)])
    if i == 13:
        return F(0)**2==0 and F(0)**3==0 and F(-8)**3==-512
    if i == 14:
        return F(2)**3>F(2)**2 and F(1,2)**3<F(1,2)**2 and F(1)**3==F(1)**2
    if i == 16:
        # exact integer powers, corresponding to log_2(2)=1, log_2(4)=2;
        # (1/2)^(-1)=2, (1/2)^(-2)=4.
        return 2**1==2 and 2**2==4 and F(1,2)**(-1)==2 and F(1,2)**(-2)==4
    if i == 17:
        try:
            import sympy as s
        except ImportError:
            # No pretending a numerical approximation proves the singularity.
            return False
        return s.cos(s.pi/2)==0 and s.sin(s.pi/2)==1 and s.cos(0)==1
    if i == 20:
        f=lambda x:x*x-2
        return f(F(1))<0 and f(F(2))>0 and f(F(3,2))>0 and f(F(5,4))<0 and F(3,2)-F(5,4)==F(1,4)
    if i == 22:
        def det(u,v):return u[0]*v[1]-u[1]*v[0]
        return det((1,1),(1,-1))==-2 and (3+1,3-1)==(4,2) and det((1,0),(2,0))==0
    if i == 23:
        # sin(30deg)=1/2, a=2, b=3 => sinB=3/4.
        # For acute B, sinB>sin30 implies B>30, so 180-B+30<180;
        # hence both acute and supplementary candidates have positive C.
        v=F(3)*F(1,2)/F(2)
        return v==F(3,4) and F(1,2)<v<1 and F(4)*F(1,2)/F(2)==1
    if i == 29:
        ps=(F(1,2),F(1,4),F(1,4))
        return sum(ps)==1 and ps[0]+ps[1]==F(3,4) and F(2,3)!=F(3,4)
    if i == 31:
        f=lambda x:x*x
        x=F(2)
        return (f(x+1)-f(x),2*x,F(1))==(5,4,1) and (f(x+F(1,2))-f(x),2*x*F(1,2))==(F(9,4),2)
    raise ValueError("Math witness index not part of the selected batch")

def build(inputs=None):
    inputs = inputs or {}
    authoring = inputs.get("authoring", parse_authoring())
    hints = inputs.get("hints", parse_hints())
    props = inputs.get("proposals", load(PROPOSALS))
    windows = inputs.get("windows", load(WINDOWS))
    reg = inputs.get("registry", load(REGISTRY))
    old = inputs.get("old", [*load(OLD[0]),*load(OLD[1])])
    require(len(props["proposals"])==62, "Provisional syllabus inventory mismatch")
    require(len(windows["rows"])==45 and len(reg["rows"])==428, "Source lineage changed")
    window_by_id = {w["anchor_id"]:w for w in windows["rows"]}
    anchor_by_id={f"KB61-P{r['printed_page']:03d}-L{r['pdfkit_line']:03d}":r for r in reg["rows"]}
    require(len(window_by_id)==45 and len(anchor_by_id)==428, "Duplicated provenance key")
    require(len(old)==31 and len({v["lesson_id"] for v in old})==31, "Prior manuscript inventory changed")
    source_locations={}
    output=[]
    for idx,parts in authoring:
        target=props["proposals"][2*(idx-1)+1]
        parent=props["proposals"][2*(idx-1)]
        require(target["parent_anchor_id"]==parent["parent_anchor_id"], "Not a shared source scope")
        require(target["teacher_review"]==parent["teacher_review"]=="REVIEW_PENDING", "Forged teacher status")
        require(target["student_publishable"] is False and target["math_equivalence"]=="NOT_REVIEWED"
                and target["official_atomic_membership"]=="UNDETERMINED",
                "Provisional atom was improperly promoted")
        require(target["content_lesson_complete"] is False, "Target was already certified complete")
        anchor=anchor_by_id[target["parent_anchor_id"]]
        window=window_by_id[target["parent_anchor_id"]]
        require(anchor["source_line_sha256"]==window["source_line_sha256"] and
                target["source_window_sha256"]==window["source_window_sha256"] and
                anchor["printed_page"]==target["source_page"], "Source page/window SHA broken")
        old_match=[x for x in old if x["loc"]==[target["source_page"],anchor["pdfkit_line"]]]
        require(len(old_match)==1, "Each new second-atom draft must reference one preceding parent draft")
        require(old_match[0]["student_publishable"] is False and
                old_match[0]["teacher_review"]=="REVIEW_PENDING", "Parent status unexpectedly approved")
        require(exact_case(idx) is True, "Bounded independently computed math witness failed")
        statement,hyp,r1,r2,r3,e1,a1,e2,a2,neg,wrong,why,near,far=parts
        require(len({r1,r2,r3})==3 and len({e1,e2})==2, "Generic duplicated math explanation")
        require(e1!=e2 and a1!=a2 and len(neg)>=19, "Weak examples or counterexample")
        source_locations[target["parent_anchor_id"]]=anchor
        output.append(dict(
            lesson_id=f"KB68-ATOM-{idx:02}", title=target["editorial_subtopic"],
            editorial_id=target["candidate_id"], related_parent_draft_id=old_match[0]["lesson_id"],
            proposed_kind=target["hypothesized_kind"],
            statement=statement, assumptions=[hyp], notation=hints[idx][0],
            prerequisites=[parent["editorial_subtopic"]],
            reasoning=[{"step":k+1,"claim":r,"justification":"教师侧文字论证；尚未形式认证"}
                       for k,r in enumerate((r1,r2,r3))],
            worked_examples=[{"question":e1,"teacher_solution":a1},
                             {"question":e2,"teacher_solution":a2}],
            invalid_case=neg, common_wrong_method=wrong, explanation_of_error=why,
            hint_ladder=hints[idx][1:],
            near_transfer=near, far_transfer=far,
            source_standard="2017版2020年修订普通高中数学课标（本地受许可使用，未上传原文）",
            source_track_hint=anchor["track_hint"], source_page=anchor["printed_page"],
            parent_anchor_id=target["parent_anchor_id"], source_line_sha256=anchor["source_line_sha256"],
            source_window_sha256=target["source_window_sha256"],
            source_license="ORIGINAL_PROJECT_AUTHORED",
            official_atomic_membership="UNDETERMINED",
            official_clause_full_text_verified=False, proof_certification="NOT_FORMALLY_CERTIFIED",
            finite_math_witness="FINITE_EXACT_INSTANCE_ONLY",
            teacher_review="REVIEW_PENDING", teacher_signature=None,
            teacher_solution_visibility="TEACHER_ONLY", student_publishable=False,
            student_freeform_steps_verified=False))
    require(len(output)==20 and len(source_locations)==20, "Expected 20 distinct source-backed counterpart manuscripts")
    require(len({v["editorial_id"] for v in output})==20, "Duplicate authored atom")
    by_id={v["editorial_id"]:v for v in output}
    matrix=[]
    for p in props["proposals"]:
        draft=by_id.get(p["candidate_id"])
        matrix.append(dict(
            provisional_candidate_id=p["candidate_id"],
            source_anchor_id=p["parent_anchor_id"],
            track_hint=anchor_by_id[p["parent_anchor_id"]]["track_hint"],
            author_draft_id=draft["lesson_id"] if draft else None,
            full_official_clause_review="NOT_COMPLETED",
            content_review="REVIEW_PENDING" if draft else "NOT_AUTHORED_IN_BATCH68",
            teacher_approved=False, independent_math_proof_certified=False,
            official_atom_approved=False, student_publishable=False))
    counts=Counter(a["track_hint"] for a in matrix)
    result=dict(schema_version="kb68-companion-authoring-v1",
                source_pdf_sha256=props["source_pdf_sha256"],
                authoring_sha256=hashlib.sha256(DATA.read_bytes()).hexdigest(),
                hints_sha256=hashlib.sha256(HINTS.read_bytes()).hexdigest(),
                items=output)
    status=dict(schema_version="kb68-candidate-link-ledger-v1",
                scope="62 internal split hypotheses; not an official curriculum denominator",
                total_provisional_candidates=62,
                explicitly_drafted_second_candidates=20,
                not_explicitly_drafted_in_batch68=42,
                official_atomic_denominator={k:None for k in TRACKS},
                provisional_track_counts={k:counts[k] for k in TRACKS},
                formal_proofs_certified=0, teacher_approved=0,
                officially_fully_reviewed_pages=0, student_published=0,
                records=matrix)
    return result,status,source_locations

def render_md(result,status):
    lines=["# Batch68｜20份项目原创的暂定原子对应讲义（仅供教师审查）",
           "",
           "此处20个条目均属于62个**内部暂定拆分假设**中的第二条内容候选；不是官方知识原子。",
           "与前31篇家族范围草案不能直接相加为国家课程覆盖率。全套课标条款仍未全文教师审核。",
           "所有完整例题答案仅限教师侧；数学文字推导未形式证明，精确计算只作有限案例验证。",
           "","| 项目 | 数量 |","| --- | ---: |",
           "| 本批原创暂定原子讲义 | 20 |",
           "| 本批配套例题 | 40 |",
           "| 本批逐步解释（非形式证明） | 60 |",
           "| 本批失效反例与错因组 | 20 |",
           "| 本批有限精确见证 | 20 |",
           "| 未被本批逐候选关联的暂定假设 | 42 |",
           "| 真实教师批准、官方原子认证、学生发布 | 0 |",""]
    for v in result["items"]:
        lines.extend([
            f"## {v['lesson_id']} · {v['title']}","",
            f"**来源坐标**：{v['parent_anchor_id']}（课标印刷页{v['source_page']}；局部 SHA={v['source_line_sha256'][:16]}…）。",
            f"**关联父级草案**：{v['related_parent_draft_id']}。官方条款审核仍未完成。","",
            "**数学陈述**："+v["statement"],"","**适用前提**："+v["assumptions"][0],"",
            "**教师侧论证（未形式认证）**","",
        ])
        lines.extend(f"{step['step']}. {step['claim']}" for step in v["reasoning"])
        lines.extend(["","**教师侧例题（不得用于独立挑战提示直接泄漏）**",""])
        for e in v["worked_examples"]:
            lines.extend([f"- 题：{e['question']} 解析：{e['teacher_solution']}"])
        lines.extend(["",f"**不适用例/边界**：{v['invalid_case']}",
                      "",f"**典型错法**：{v['common_wrong_method']}",
                      f"**错误原因**：{v['explanation_of_error']}",
                      "",f"**分层提示**：{' → '.join(v['hint_ladder'])}",
                      "",f"**近迁移**：{v['near_transfer']}",
                      f"**远迁移**：{v['far_transfer']}",
                      "","**审核**：REVIEW_PENDING；证明 NOT_FORMALLY_CERTIFIED；学生发布 false。",""])
    return "\n".join(lines).rstrip()+"\n"

def write(check=False,verify_local=False):
    result,status,locations=build()
    if verify_local:
        require(prior.verify_source_local(load(REGISTRY),list(locations.values()))==len({r["printed_page"] for r in locations.values()}),
                "Mac original PDFKit byte lineage incomplete")
    expected={OUT:dump(result),MATRIX:dump(status),REVIEW:render_md(result,status)}
    for path,body in expected.items():
        if check:
            require(path.is_file() and path.read_text(encoding="utf-8")==body,
                    "Generated snapshot missing/stale: "+str(path))
        else:
            path.write_text(body,encoding="utf-8")
    print(f"BATCH68 {'CHECK' if check else 'WRITE'} OK: {len(result['items'])} original, 40 examples, "
          f"60 steps, 20 exact finite cases, {len(locations)} local source anchors, "
          "0 official approvals")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--verify-local",action="store_true")
    args=parser.parse_args()
    write(check=args.check,verify_local=args.verify_local)
