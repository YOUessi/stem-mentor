#!/usr/bin/env python3
"""Mac-audited semantic source boundaries; proposal inventory, NEVER official atom census."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch149_unnumbered_elective_queue as upstream

OUT = ROOT / "docs/evaluation/KB_BATCH150_DE_SEMANTIC_BOUNDARY.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH150_DE_SEMANTIC_BOUNDARY.md"
SOURCE = upstream.OUT
TRACKS = ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
          "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
HASH = re.compile(r"^[0-9a-f]{64}$")

# Each tuple is an ORIGINAL, high-level editorial paraphrase, never a textbook quotation.
# A source span is page, first and last physical PDFKit line (inclusive).
# Topics represent ideas/activities, not proven minimum official atoms.
SPEC = [
 ("C","社会调查","数据调查的结果报告","Method",69,1,69,3),
 ("C","社会调查","典型社会调查案例的意义","Exploration",69,4,69,5),
 ("D","美与数学","曲线与曲面所体现的形状特征","Exploration",69,17,69,23),
 ("D","美与数学","反射、旋转和位移的对称结构","Concept",70,2,70,7),
 ("D","美与数学","自然及艺术中重复变化的周期性","Exploration",70,8,70,11),
 ("D","美与数学","黄金比例和递推数列的模型适用边界","Exploration",70,12,70,15),
 ("D","音乐与数学","正弦波频率、振幅及叠加","Concept",70,23,70,25),
 ("D","音乐与数学","音律的频率比与等比数列","Exploration",71,1,71,4),
 ("D","音乐与数学","节拍分数、同步及最小公倍数","Method",71,5,71,7),
 ("D","音乐与数学","乐器振动与共鸣的模型","Exploration",71,8,71,10),
 ("D","音乐与数学","作品节奏、平移及组合变换","Exploration",71,11,71,13),
 ("D","美术与数学","平面绘画的透视与几何变换","Exploration",72,2,72,4),
 ("D","美术与数学","工艺、建筑和字体中的几何关系","Exploration",72,5,72,7),
 ("D","美术与数学","计算机绘图的数学与工具","Exploration",72,8,72,10),
 ("D","美术与数学","艺术创作中的数学观念","Exploration",72,11,72,12),
 ("D","体育与数学","投掷跳跃中的向量分解与运动模型","Method",72,22,73,1),
 ("D","体育与数学","运动指标数据的统计解释","Method",73,2,73,5),
 ("D","体育与数学","赛事排程与图论、优化建模","Exploration",73,6,73,8),
 ("D","体育与数学","运动设备和场馆的曲面几何","Exploration",73,9,73,12),
 ("E","拓展视野","机器人坐标与运动几何","Exploration",73,16,73,17),
 ("E","拓展视野","群作用与对称性入门","Exploration",73,16,73,17),
 ("E","拓展视野","球面几何的角与距离","Exploration",73,16,73,17),
 ("E","拓展视野","多面体拓扑不变量的直观","Exploration",73,16,73,17),
 ("E","拓展视野","数列差分及离散变化","Exploration",73,16,73,17),
 ("E","拓展视野","初等数论的整除与同余","Exploration",73,16,73,17),
 ("E","日常生活","数量与决策的生活数学实例","Exploration",73,18,73,18),
 ("E","日常生活","复利、预算及家庭财务模型","Exploration",73,18,73,18),
 ("E","地方特色","地方建筑的几何数据研究","Exploration",73,19,73,20),
 ("E","地方特色","地区经济调查与统计分析","Exploration",73,19,73,20),
 ("E","大学先修","微积分基础的先修主题","Exploration",73,21,73,22),
 ("E","大学先修","线性代数和解析几何先修主题","Exploration",73,21,73,22),
 ("E","大学先修","概率与数理统计先修主题","Exploration",73,21,73,22),
]

def ensure(condition, reason):
    if not condition:
        raise ValueError("KB150 source semantic boundary: " + reason)

def owner(page, line):
    if page == 69:
        return "ELECTIVE_C" if line <= 5 else ("ELECTIVE_D" if line <= 23 else "PARATEXT")
    if page == 70:
        return "PARATEXT" if line in (1, 26) else "ELECTIVE_D"
    if page == 71:
        return "PARATEXT" if line == 24 else "ELECTIVE_D"
    if page == 72:
        return "PARATEXT" if line in (1,25) else "ELECTIVE_D"
    if page == 73:
        return "ELECTIVE_D" if line <= 12 else ("ELECTIVE_E" if line <= 22 else "PARATEXT")
    raise ValueError("Page outside original D/E review scope")

def source_id(p, l):
    return f"STD2020-SOURCELINE-P{p:02d}-L{l:03d}"

def span_locs(p1,l1,p2,l2):
    ensure((p1,l1) <= (p2,l2) and 69 <= p1 <= p2 <= 73,
           "invalid source span")
    lengths={69:24,70:26,71:24,72:25,73:23}
    return [(p,l) for p in range(p1,p2+1)
            for l in range(l1 if p==p1 else 1, (l2 if p==p2 else lengths[p])+1)]

def sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def load():
    raw=json.loads(SOURCE.read_text(encoding="utf-8"))
    ensure(upstream.validate(raw), "upstream source SHA queue drift")
    return raw

def build(raw=None):
    raw=load() if raw is None else raw
    ensure(upstream.validate(raw), "source line queue has drifted")
    originals={(r["printed_page"],r["line_number"]):r for r in raw["line_rows"]}
    ensure(len(originals)==122, "original 122 physical lines lost")
    rows=[]
    for (p,l),r in sorted(originals.items()):
        track=owner(p,l)
        rows.append(dict(line_id=source_id(p,l), printed_page=p, pdfkit_line=l,
            original_line_sha256=r["line_sha256"], classification=track,
            source_classification="EDITORIAL_BOUNDARY_PROPOSAL",
            officially_certified=False, teacher_review="REVIEW_PENDING",
            original_text_committed=False))
    expected={"ELECTIVE_C":5,"ELECTIVE_D":100,"ELECTIVE_E":10,"PARATEXT":7}
    ensure(dict(Counter(x["classification"] for x in rows))==expected,
           "unexpected C-D-E or page header/footer partition")
    proposals=[]
    for i,(short,section,title,kind,p1,l1,p2,l2) in enumerate(SPEC,1):
        track="ELECTIVE_"+short
        positions=span_locs(p1,l1,p2,l2)
        # Exclude source headings and page furniture; no proposal allowed to cite other track.
        ids=[];hashes=[]
        for p,l in positions:
            if p1 != p2 and owner(p,l)=="PARATEXT":
                continue  # crosspage footer/header is not a curricular statement
            line=originals.get((p,l))
            ensure(line is not None and owner(p,l)==track,
                   f"{title}: source lines lost, cross-track contamination, or paratext")
            ids.append(source_id(p,l));hashes.append(line["line_sha256"])
        proposals.append(dict(id=f"STD2020-EDITORIAL-PROP150-{i:03d}",
            original_paraphrase=title, source_topic=section, source_track=track,
            content_type=kind, source_line_ids=ids, source_line_sha256=hashes,
            source_pdf_sha256=raw["source_pdf_sha256"],
            curriculum_scope_status="EDITORIAL_PROPOSAL_NOT_APPROVED_ATOM",
            is_school_elective_example=(track=="ELECTIVE_E"),
            official_knowledge_atom_id=None, mathematical_conditions_review="NOT_YET_CHECKED",
            theorem_proof_required=False, duplicate_with_other_proposals="UNDETERMINED",
            teacher_review="REVIEW_PENDING", teacher_approved=False,
            lesson_complete=False, student_authoritative=False))
    return dict(schema="kb150-licensed-source-line-semantic-proposals/1",
        official_pdf_sha256=raw["source_pdf_sha256"],
        originals_rehashed_on_mac=False,
        source_line_partition=rows,
        source_line_counts=expected,
        source_boundary_evidence=[
            {"kind":"C_TO_D","page":69,"line":6,"source_id":source_id(69,6),
             "classification":"EDITORIAL_SOURCE_HEADING_SEEN"},
            {"kind":"D_TO_E","page":73,"line":13,"source_id":source_id(73,13),
             "classification":"EDITORIAL_SOURCE_HEADING_SEEN"},
            {"kind":"D_CROSSPAGE_CONTINUATION","from":source_id(72,24),
             "to":source_id(73,1),"classification":"EDITORIAL_SOURCE_CONTINUATION_SEEN"}],
        proposals=proposals, proposed_count=len(proposals),
        approved_atom_denominators={k:None for k in TRACKS},
        complete_official_course_census=False, teacher_approved=0,
        valid_teacher_manuscripts_new=0, student_authoritative=0,
        warning="32 candidate ideas are sourced paraphrases (including E school elective examples), NOT teacher-approved official atom denominators, NOT full manuscripts.")

def validate(v):
    raw=load()
    ensure(v["official_pdf_sha256"]==raw["source_pdf_sha256"],"untrusted PDF")
    ensure(v["schema"]=="kb150-licensed-source-line-semantic-proposals/1",
           "unsupported schema")
    r=v["source_line_partition"]
    ensure(len(r)==122 and len({q["line_id"] for q in r})==122,
           "line loss or duplicate")
    upstream_rows={(z["printed_page"],z["line_number"]):z for z in raw["line_rows"]}
    for row in r:
        p,l=row["printed_page"],row["pdfkit_line"]
        old=upstream_rows.get((p,l))
        ensure(old is not None and row["line_id"]==source_id(p,l)
            and row["classification"]==owner(p,l)
            and row["original_line_sha256"]==old["line_sha256"]
            and row["source_classification"]=="EDITORIAL_BOUNDARY_PROPOSAL"
            and not row["officially_certified"] and not row["original_text_committed"]
            and row["teacher_review"]=="REVIEW_PENDING","line wrong track/authority/hash")
    ensure(dict(Counter(z["classification"] for z in r))==
           v["source_line_counts"]=={"ELECTIVE_C":5,"ELECTIVE_D":100,"ELECTIVE_E":10,"PARATEXT":7},
           "wrong partition totals")
    ensure(v["source_boundary_evidence"]==build(raw)["source_boundary_evidence"],
           "source heading or crosspage seam mutated")
    ps=v["proposals"]
    ensure(len(ps)==v["proposed_count"]==32 and
           len({x["id"] for x in ps})==32, "proposal count/ID drift")
    expected=build(raw)["proposals"]
    ensure(ps==expected,"forged proposal, provenance, approval, or source ownership")
    ensure(v["approved_atom_denominators"]=={k:None for k in TRACKS}
           and not v["complete_official_course_census"] and not v["teacher_approved"]
           and not v["student_authoritative"] and not v["valid_teacher_manuscripts_new"],
           "false official knowledge coverage/review status")
    return True

def mac_replay(v):
    """Read on-device original PDFKit scratch only. Never emit or commit source prose."""
    pages=upstream.source_lines()
    for r in v["source_line_partition"]:
        p,l=r["printed_page"],r["pdfkit_line"]
        ensure(sha(pages[p][l-1])==r["original_line_sha256"],
               f"source text mismatched p{p} line{l}")
    # Full-width OCR header classification is explicitly anchored at these positions.
    ensure("类课程" in pages[69][5] and "类课程" in pages[73][12],
           "original syllabus section-boundary headers moved")
    ensure("向量" in pages[72][23] and "跳高" in pages[73][0],
           "crosspage sport-model continuation changed")
    return True

def render(v):
    counts=Counter(p["source_track"] for p in v["proposals"])
    s=[
      "# KB150｜选修C/D/E跨页分轨实质审查与32个候审原子提案","",
      "基于授权Mac课标原始PDFKit逐行SHA重放，修复上游把印刷页69整页视作D、页73整页未定的过粗分类。",
      "**这是编辑级来源语义初审，不是教师对正式课标原子分母的批准。**","",
      "| 来源轨道/版面 | 原始非空行 | 编辑级待审核提案 | 正式已核定知识原子 |",
      "|---|---:|---:|---|",
    ]
    for t in ("ELECTIVE_C","ELECTIVE_D","ELECTIVE_E","PARATEXT"):
        s.append(f"| {t} | {v['source_line_counts'][t]} | {counts.get(t,0)} | UNKNOWN |")
    s.extend(["",
      "关键来源分界：印刷第69页第1–5行仍属C社会调查模块，第6行进入D；第73页第1–12行属于D体育模块，第13行进入E；其余页眉、页脚计入PARATEXT而非知识要求。",
      "第72页末体育向量应用在第73页首续句，须将跨页内容保持同一主题证据链；避免把页脚误记为知识内容。","",
      "## 原创语义提案（非正式课程分母）","",
      "| 提案ID | 课程 | 编辑主题 | 类型 | 来源行 |",
      "|---|---|---|---|---|"])
    for p in v["proposals"]:
        locs=p["source_line_ids"]
        s.append(f"| {p['id']} | {p['source_track']} | {p['original_paraphrase']} | {p['content_type']} | {locs[0]} ~ {locs[-1]} |")
    s.extend(["","所有提案仍是REVIEW_PENDING，不是完成讲义，特别是E轨仅提供学校可选主题示例，不可声称各学校必须开设。",
      "下一阶段：由真实审校人员核实课标概念/要求的增拆与跨页语义重复；再建立完整分母、完善逐主题讲义/题族与教师签字。",
      "源文件只含行号、SHA和原创短标签；不包含版权课标正文。",""])
    return "\n".join(s)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    ap.add_argument("--mac-replay",action="store_true")
    args=ap.parse_args()
    value=build()
    ensure(validate(value),"validation failed")
    if args.mac_replay:
        ensure(mac_replay(value),"Mac original line replay failed")
    content=json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
    md=render(value)
    if args.check:
        ensure(OUT.read_text(encoding="utf-8")==content and
               REPORT.read_text(encoding="utf-8")==md,
               "committed artifact drift")
    else:
        OUT.write_text(content,encoding="utf-8")
        REPORT.write_text(md,encoding="utf-8")
    print("KB150 C/D/E semantic boundary PASS: 5 C +100 D +10 E +7 furniture; 32 pending proposals; all official denominators UNKNOWN")
    if args.mac_replay:
        print("KB150 original Mac PDFKit SHA replay PASS: 122/122 licensed lines; 2 headings and 1 crosspage continuation")
if __name__=="__main__":
    main()
