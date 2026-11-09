#!/usr/bin/env python3
"""Batch63: source-attested windows and *provisional* atom-splitting hypotheses.

Source text never leaves the authorized Mac. Candidate labels are original
editorial suggestions, not certified official course knowledge units.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
import build_kb_batch61_requirement_anchors as B61
import build_kb_batch62_anchor_triage as B62

ROOT=Path(__file__).resolve().parents[1]
CUR=ROOT/"curriculum/highschool_math"
DOC=ROOT/"docs/evaluation"
WINDOWS=CUR/"k00_batch63_context_windows.json"
OUT=CUR/"k00_batch63_provisional_atom_proposals.json"
REPORT=DOC/"KB_BATCH63_ATOM_SPLIT_AND_SOURCE_WINDOWS.md"
SOURCE_DIR=Path("/private/tmp")
# Two independent editorial hypotheses per substantive source location;
# these are NOT official atomic curriculum requirements or finished lessons.
SPLITS={
 (15,10):(("集合的确定性与元素属于关系","CONCEPT"),("元素属于与集合包含的类型区别","CONCEPT")),
 (15,15):(("集合包含、相等及真包含关系","CONCEPT"),("双向包含判定集合相等","THEOREM_CANDIDATE")),
 (15,17):(("并交补的集合运算定义","CONCEPT"),("补集关于指定全集的相对性","METHOD")),
 (16,7):(("充分条件与必要条件的命题方向","CONCEPT"),("双向蕴含与等价命题判定","METHOD")),
 (16,14):(("带明确论域的全称命题","CONCEPT"),("带明确论域的存在命题","CONCEPT")),
 (16,16):(("全称否定变存在的量词律","THEOREM_CANDIDATE"),("存在否定变全称的量词律","THEOREM_CANDIDATE")),
 (16,24):(("同乘负数的不等号方向","METHOD"),("方程除式与不等式的非零条件","METHOD")),
 (16,26):(("非负实数算术几何平均不等式","THEOREM_CANDIDATE"),("均值不等式的等号与定义域边界","METHOD")),
 (17,9):(("非退化一元二次方程的判别式","CONCEPT"),("抛物线零点与重根的联系","THEOREM_CANDIDATE")),
 (17,12):(("二次不等式的区间符号法","METHOD"),("二次不等式判别式与边界点选择","METHOD")),
 (19,13):(("函数的定义域与唯一对应","CONCEPT"),("分段函数不同表示的同一性","METHOD")),
 (19,21):(("按区间定义函数单调性","CONCEPT"),("极值与端点、孤立定义域的区分","CONCEPT")),
 (20,13):(("整数幂与有理数幂的实数适用域","CONCEPT"),("分数指数在零及负底数处的限制","METHOD")),
 (20,19):(("实数指数函数的合法底数","CONCEPT"),("指数函数按底数区分单调方向","THEOREM_CANDIDATE")),
 (20,31):(("对数函数定义域与底数限制","CONCEPT"),("对数换底公式的合法分母","METHOD")),
 (20,34):(("对数函数图像的定义域与值域","CONCEPT"),("对数单调性按底数分类","THEOREM_CANDIDATE")),
 (21,21):(("弧度制与单位圆坐标","CONCEPT"),("正切的余弦零点排除","METHOD")),
 (22,12):(("同角三角函数平方关系","THEOREM_CANDIDATE"),("三角恒等变形的符号与定义域保持","METHOD")),
 (22,18):(("周期参数和时间量纲识别","METHOD"),("三角回归模型的适用区间与外推","METHOD")),
 (22,27):(("连续函数变号的零点存在条件","THEOREM_CANDIDATE"),("二分法区间压缩与精度停止条件","METHOD")),
 (23,2):(("函数模型变量与数据区间假设","METHOD"),("模型外推、残差与可证结论区别","METHOD")),
 (26,13):(("非共线向量构成二维基底","THEOREM_CANDIDATE"),("向量线性组合系数唯一性","THEOREM_CANDIDATE")),
 (26,20):(("余弦定理的三角形假设","THEOREM_CANDIDATE"),("正弦定理SSA的歧义与多解","METHOD")),
 (27,4):(("复数标准形式及相等条件","CONCEPT"),("纯虚数与零复数的区别","CONCEPT")),
 (27,8):(("复数加减乘法的实虚部运算","METHOD"),("共轭化分母及复数除法非零约束","METHOD")),
 (28,4):(("空间线面关系的对象分类","CONCEPT"),("平行与异面两直线的区分","CONCEPT")),
 (28,5):(("相交、平行、重合与异面判定","METHOD"),("投影重叠不推得空间直线相交","METHOD")),
 (28,16):(("直线与平面平行的充分判定","THEOREM_CANDIDATE"),("线面垂直判定中的两相交线假设","THEOREM_CANDIDATE")),
 (31,10):(("随机试验与事件集合定义","CONCEPT"),("古典概率的等可能条件","METHOD")),
 (32,9):(("简单随机抽样中的等概率机制","CONCEPT"),("抽样偏差与总体推断限制","METHOD")),
 (58,35):(("微分定义为导数与自变量增量的乘积","CONCEPT"),("有限增量与线性近似误差的区分","METHOD"))
}
ALLOWED={"CONCEPT","METHOD","THEOREM_CANDIDATE"}
# Reproducibility pin for the exact 45 local PDFKit source windows. This is a
# versioned checksum, not a teacher attestation or cryptographic signature.
WINDOW_ROWS_PIN="a07b10d24bc7455e3f196adfaa58b46ee87ce43d55e7f31b716c2c76714f727e"
def need(cond,why):
    if not cond:raise ValueError(why)
def canonical(v):
    return json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
def digest(v):
    return hashlib.sha256(v).hexdigest()
def source_segments(source_dir=SOURCE_DIR):
    reg=B61.load(B61.REGISTRY)
    B61.validate(reg)
    anchors=B62.build()["rows"]
    selected=[r for r in anchors if r["classification"] in
              ("SUBSECTION_SCOPE","DIRECT_OBJECTIVE","CONTENT_BLOCK",
               "COMPETENCY_BLOCK","PEDAGOGY_BLOCK")]
    need(len(selected)==45,"31+14 selected source anchors required")
    result=[]
    pages={}
    for page in sorted({r["printed_page"] for r in selected}):
        path=source_dir/f"kb56_page_{page}.txt"
        raw=path.read_bytes()
        fp=B61.load(B61.PAGES)
        pin=next(x for x in fp["pages"] if x["printed_page"]==page)
        need(digest(raw)==pin["pdfkit_text_sha256"],"Mac PDFKit page SHA differs")
        pages[page]=raw.decode("utf-8").splitlines()
    for row in selected:
        p,n=row["printed_page"],row["pdfkit_line"]
        seq=pages[p]
        need(digest(seq[n-1].encode())==row["source_line_sha256"],"anchor line differs")
        # End at next marker, even if the marker is a heading. A short window
        # must remain explicitly INCOMPLETE; it cannot prove the whole clause.
        marker_lines=sorted(r["pdfkit_line"] for r in reg["rows"]
                            if r["printed_page"]==p and r["pdfkit_line"]>n)
        stop=marker_lines[0]-1 if marker_lines else len(seq)
        need(stop>=n,"empty source window")
        snippet="\n".join(seq[n-1:stop])
        result.append(dict(anchor_id=row["anchor_id"],printed_page=p,
             start_line=n,end_line=stop,window_line_count=stop-n+1,
             source_window_sha256=digest(snippet.encode()),
             source_line_sha256=row["source_line_sha256"],
             source_page_pdfkit_sha256=row["source_page_pdfkit_sha256"],
             next_marker_line=marker_lines[0] if marker_lines else None,
             reaches_page_end=not marker_lines,
             original_source_text_committed=False,
             full_clause_or_cross_page_verified=False,
             source_image_manually_reviewed=False,
             status="MAC_PDFKIT_WINDOW_ONLY_REVIEW_PENDING"))
    return result

def make_windows(source_dir=SOURCE_DIR):
    rows=source_segments(source_dir)
    return dict(schema_version="kb63-source-windows-v1",
        original_pdf_sha256=B61.PDF_SHA,
        record_count=45,substantive_windows=31,nonatom_windows=14,
        includes_copyright_text=False,
        neither_full_requirement_nor_teacher_review=True,
        rows=rows)

def build(windows=None):
    windows=B61.load(WINDOWS) if windows is None else windows
    rows=B62.build()["rows"]
    substantive={ (r["printed_page"],r["pdfkit_line"]):r for r in rows
                  if r["classification"] in ("SUBSECTION_SCOPE","DIRECT_OBJECTIVE") }
    need(len(substantive)==31 and set(substantive)==set(SPLITS),
         "curated location map not complete or changed")
    need(len(windows["rows"])==45 and windows["record_count"]==45,
         "missing context windows")
    win={r["anchor_id"]:r for r in windows["rows"]}
    need(len(win)==45,"duplicate context window")
    proposals=[]
    for (p,n), source in sorted(substantive.items()):
        specs=SPLITS[p,n]
        need(len(specs)==2,"each scope must have two explicit candidate parts")
        src_window=win[source["anchor_id"]]
        for j,(title,kind) in enumerate(specs,1):
            need(kind in ALLOWED and len(title)>=9,"provisional atom lacks specificity")
            proposals.append(dict(
                candidate_id=f"KB63-P{p:03d}-L{n:03d}-C{j:02d}",
                parent_anchor_id=source["anchor_id"],hypothesized_kind=kind,
                editorial_subtopic=title,proposed_scope_condition=source["math_or_coverage_boundary"],
                known_math_failure_to_test=source["math_or_coverage_boundary"],
                source_page=p,source_window_sha256=src_window["source_window_sha256"],
                teacher_review="REVIEW_PENDING",teacher_signature=None,
                math_equivalence="NOT_REVIEWED",
                official_atomic_membership="UNDETERMINED",
                full_source_context_verified=False,proof_certification="NOT_CERTIFIED",
                content_lesson_complete=False,teacher_solution_visibility="TEACHER_ONLY",
                student_publishable=False,source_license="ORIGINAL_EDITORIAL_PARAPHRASE"))
    cnt=Counter(r["track_hint"] for r in rows if
                r["classification"] in ("SUBSECTION_SCOPE","DIRECT_OBJECTIVE"))
    return dict(schema_version="kb63-provisional-atom-candidates-v1",
        source_pdf_sha256=B61.PDF_SHA,
        context_ledger_sha256=digest(canonical(windows).encode()),
        parent_triage_sha256=digest(B62.OUT.read_bytes()),
        parent_substantive_scopes=31,nonatom_blocks_still_unmapped=14,
        provisional_candidate_count=len(proposals),
        provisional_parent_track_counts=dict(sorted(cnt.items())),
        official_atomic_denominator={k:None for k in B61.TRACKS},
        machine_review_does_not_equal_teacher_approval=True,
        formally_approved_lessons=0,student_published_lessons=0,
        proposals=proposals)

def validate(windows,output):
    need(windows==make_windows_from_committed(windows),
         "unexpected source-window schema / privilege field")
    need(windows["original_pdf_sha256"]==B61.PDF_SHA and
         windows["includes_copyright_text"] is False and
         windows["neither_full_requirement_nor_teacher_review"] is True,
         "source ledger metadata forged")
    need(output==build(windows),"atom candidate list or approvals modified")
    need(output["official_atomic_denominator"]=={k:None for k in B61.TRACKS},
         "unearned official denominator")
    need(len(output["proposals"])==62 and
         len({p["candidate_id"] for p in output["proposals"]})==62,
         "not exactly 62 distinct editorial hypotheses")
    for r in windows["rows"]:
        need(r["status"]=="MAC_PDFKIT_WINDOW_ONLY_REVIEW_PENDING" and
             r["original_source_text_committed"] is False and
             r["full_clause_or_cross_page_verified"] is False and
             r["source_image_manually_reviewed"] is False,
             "source window cannot claim review or completeness")
        need(r["window_line_count"]==r["end_line"]-r["start_line"]+1 and
             1<=r["start_line"]<=r["end_line"]<=B61.load(B61.REGISTRY)["page_line_counts"][str(r["printed_page"])],
             "source window range wrong")
    for row in output["proposals"]:
        need(row["teacher_review"]=="REVIEW_PENDING" and row["teacher_signature"] is None and
             row["math_equivalence"]=="NOT_REVIEWED" and row["official_atomic_membership"]=="UNDETERMINED" and
             row["full_source_context_verified"] is False and
             row["proof_certification"]=="NOT_CERTIFIED" and
             row["content_lesson_complete"] is False and
             row["teacher_solution_visibility"]=="TEACHER_ONLY" and
             row["student_publishable"] is False,"fraudulent review, source or publication status")
def make_windows_from_committed(w):
    need(set(w)=={"schema_version","original_pdf_sha256","record_count",
                 "substantive_windows","nonatom_windows","includes_copyright_text",
                 "neither_full_requirement_nor_teacher_review","rows"},
         "unexpected window fields")
    need(w["schema_version"]=="kb63-source-windows-v1" and
         w["record_count"]==45 and w["substantive_windows"]==31 and
         w["nonatom_windows"]==14,"source counts changed")
    need(len(w["rows"])==45,"source windows missing")
    need(digest(json.dumps(w["rows"],ensure_ascii=False,sort_keys=True,
             separators=(",",":")).encode())==WINDOW_ROWS_PIN,
         "source windows differ from versioned Mac evidence snapshot")
    triage={r["anchor_id"]:r for r in B62.build()["rows"]}
    seen=set()
    for r in w["rows"]:
        need(set(r)=={"anchor_id","printed_page","start_line","end_line","window_line_count",
              "source_window_sha256","source_line_sha256","source_page_pdfkit_sha256",
              "next_marker_line","reaches_page_end","original_source_text_committed",
              "full_clause_or_cross_page_verified","source_image_manually_reviewed","status"},
              "window fields changed")
        a=triage.get(r["anchor_id"])
        need(a is not None and a["classification"] in
             ("SUBSECTION_SCOPE","DIRECT_OBJECTIVE","CONTENT_BLOCK",
              "COMPETENCY_BLOCK","PEDAGOGY_BLOCK"),"orphaned window")
        need(r["anchor_id"] not in seen,"duplicate window");seen.add(r["anchor_id"])
        need(r["printed_page"]==a["printed_page"] and
             r["start_line"]==a["pdfkit_line"] and
             r["source_line_sha256"]==a["source_line_sha256"] and
             r["source_page_pdfkit_sha256"]==a["source_page_pdfkit_sha256"],
             "window source identity changed")
        need(len(r["source_window_sha256"])==64 and
             all(c in "0123456789abcdef" for c in r["source_window_sha256"]),
             "invalid window SHA")
    return w

def render(w,a):
    by_track=Counter(p["source_page"]<=36 and "COMPULSORY" or
                     ("ELECTIVE_B" if p["source_page"]==58 else "OTHER")
                     for p in a["proposals"])
    lines=["# Batch63｜课标上下文窗口与62个预备知识原子拆分假设","",
       "**所有候选仍待教师确认；62不是官方原子数，更不是62篇完整讲义。**","",
       f"- Mac本地PDFKit窗口：{len(w['rows'])}处（31处实质性子条、14处非原子栏目）。",
       f"- 原创初步拆分假设：{len(a['proposals'])}处；来源段落窗口仅证明源文件行连续性，不能保证完整语义或跨页完整性。",
       "- 七轨官方完整知识原子分母：全部 null；教师签核0，正式学生发布0。","",
       "## 审查队列","",
       "| 原始起点 | 初步拆分一 | 初步拆分二 | 条件/误用风险 |","|---|---|---|---|"]
    groups={}
    for p in a["proposals"]:
        groups.setdefault(p["parent_anchor_id"],[]).append(p)
    for k,rows in groups.items():
        lines.append(f"| {k} | {rows[0]['editorial_subtopic']} | {rows[1]['editorial_subtopic']} | {rows[0]['known_math_failure_to_test']} |")
    lines += ["","## 不可跨越的审查门槛","",
       "1. 45个窗口只经Mac本地文字提取核对SHA：未人工通读完整条款及前后页；第35页嵌图需视觉复核。",
       "2. 初步拆分只识别潜在原子边界，未核实跨页重复或官方知识单元完整性，不能计正式覆盖率。",
       "3. 不包含版权课标原文或真实学生数据；新增任何定理证明、错法或题族都需另外通过Schema、数学与教师审校。",
       "4. 14个学业/教学/内容栏目仍UNMAPPED，不能因为原子拆分而从能力覆盖清单中消失。",""]
    return "\n".join(lines)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    ap.add_argument("--refresh-local",action="store_true")
    ap.add_argument("--source-dir",type=Path,default=SOURCE_DIR)
    ap.add_argument("--verify-local",action="store_true")
    args=ap.parse_args()
    if args.refresh_local:
        w=make_windows(args.source_dir)
        WINDOWS.write_text(canonical(w),encoding="utf-8")
    else:
        w=B61.load(WINDOWS)
    if args.verify_local or args.refresh_local:
        need(w==make_windows(args.source_dir),"Mac PDFKit context windows drifted")
    a=build(w)
    validate(w,a)
    if args.check:
        need(OUT.read_text(encoding="utf-8")==canonical(a),"atom proposals stale")
        need(REPORT.read_text(encoding="utf-8")==render(w,a),"report stale")
    else:
        OUT.write_text(canonical(a),encoding="utf-8")
        REPORT.write_text(render(w,a),encoding="utf-8")
    print("Batch63: 45 attested source windows; 31 substantive scopes; 62 provisional atom hypotheses; 14 uncovered nonatom sections; teacher approvals=0")
if __name__=="__main__":
    main()
