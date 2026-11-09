#!/usr/bin/env python3
"""K00: critical unnumbered-source requirement crosswalk, never official atom denominator.

Editorial paraphrases from Mac PDFKit source inspection of printed pages 34, 41,
50, 65 of the 2017/2020 national high-school mathematics standard.
The source text/page image is NOT reproduced or committed. Linkage is only
a discovery aid, never a mathematical equivalence or teacher approval.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURR = ROOT / "curriculum/highschool_math"
EVAL = ROOT / "docs/evaluation"
PAGES = CURR / "k00_batch51_pdfkit_page_fingerprints.json"
OVERLAY = EVAL / "KB_BATCH50_PROJECT_SCOPE_OVERLAY.json"
B51 = EVAL / "KB_BATCH51_OFFICIAL_SOURCE_PAGE_GATE.json"
OUTPUT = EVAL / "KB_BATCH52_CRITICAL_SOURCE_CROSSWALK.json"
REPORT = EVAL / "KB_BATCH52_CRITICAL_SOURCE_CROSSWALK.md"
PDF_SHA = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
TRACK_BY_PAGE = {34:"COMPULSORY",41:"SELECTIVE_COMPULSORY",50:"SELECTIVE_COMPULSORY",65:"ELECTIVE_C"}
SECTION_BY_PAGE = {34:"ACHIEVEMENT_AND_MODELLING",41:"ACHIEVEMENT_AND_GEOMETRY_INTRODUCTION",50:"SELECTIVE_MODELLING_ACTIVITY",65:"ELECTIVE_C_LOGIC_MODELS"}
PAGE_COUNTS = {34:8,41:8,50:5,65:7}

# Each goal is an ORIGINAL short educational paraphrase, not a quotation.
# Last field supplies ONLY related existing editorial IDs; never a scope match.
CANDIDATES = [
(34,"01","METHOD","识别等可能有限样本空间作为古典概型的关键前提，并将实际问题转换为概率事件。",[]),
(34,"02","CONCEPT","明确有限样本空间、事件和概率的联系，分辨并非等可能的样本结果。",[]),
(34,"03","METHOD","根据研究总体、抽样框及实际限制选择恰当的抽样方法。",["KB32-C-P034-A002"]),
(34,"04","METHOD","区分样本统计量与总体参数，说明统计推断依赖代表性。",["KB32-C-P034-A002"]),
(34,"05","CONCEPT","区分有随机误差的统计思维与条件固定的确定性演算。",["KB32-C-P034-A001"]),
(34,"06","CONCEPT","区分有限观察归纳的可撤销结论与前提成立时的演绎证明。",["KB32-C-P034-A001"]),
(34,"07","METHOD","解释统计推断具有不确定性，必须连同抽样条件解释现实结论。",["KB32-C-P034-A001","KB32-C-P034-A002"]),
(34,"08","METHOD","把建模问题组织为提出问题、建立模型、求解、检验与修订的可追溯循环。",["KB32-C-P034-A003","KB32-C-P034-A004","KB32-C-P034-A005"]),
(41,"01","CONCEPT","把数列通项公式理解为以正整数为定义域的函数描述。",[]),
(41,"02","METHOD","在具备合适递推机制时，用等差或等比数列对现实变化进行建模。",["KB32-S-P041-A001"]),
(41,"03","THEOREM_SCOPE","明确部分和与通项互求需要区别首项和后续项，不能对首项直接套差分公式。",[]),
(41,"04","CONCEPT","用差商趋近描述瞬时变化率，并明确极限存在是导数定义的关键前提。",[]),
(41,"05","METHOD","在可导条件和复合层次清楚时运用求导法则，不将链式法则的内层导数遗漏。",[]),
(41,"06","METHOD","使用导数解释函数变化与现实变量的局部变化，附有模型单位与定义域。",["KB32-S-P041-A002"]),
(41,"07","HISTORY_CONTEXT","区分微积分发展的历史证据与微积分公式的数学证明。",[]),
(41,"08","COURSE_STRUCTURE","在空间向量与平面解析几何之间标注已修先修及几何—代数过渡，不视为额外独立定理。",[]),
(50,"01","ACTIVITY_REQUIREMENT","选择性必修阶段保留独立课题研究任务，不用必修项目替代新增成果。",["KB32-S-P050-A001"]),
(50,"02","ACTIVITY_REQUIREMENT","允许新课题或旧课题深化，但必须标明任务变化及范围。",["KB32-S-P050-A002"]),
(50,"03","METHOD","区分选题、开题、研究及结题各阶段的可审核交付。",["KB32-S-P050-A001"]),
(50,"04","METHOD","沿用既有课题时明确新增假设、方法、证据或结论，避免重复成果冒充深化。",["KB32-S-P050-A002"]),
(50,"05","TEACHING_ARTIFACT","根据研究对象选择测量报告、算法程序、实物或文字报告等表达形式。",["KB32-S-P050-A003"]),
(65,"01","CONCEPT","在经典二值命题语境下说明同一律、矛盾律和排中律各自的含义。",["KB33-C-P065-A001"]),
(65,"02","CONCEPT","给出矛盾律与排中律的不同命题形式，不将二者视为同一个公式。",["KB33-C-P065-A001"]),
(65,"03","METHOD","区分演绎推理的必然保真与归纳、类比推理的可撤销特点。",["KB33-C-P065-A002","KB33-C-P065-A003"]),
(65,"04","CONCEPT","比较或然性与必然性结论，说明观察样本不能替代所有情形的证明。",["KB33-C-P065-A003"]),
(65,"05","METHOD","区分直接证明、逆否证明等方法的适用前提，防止把逆命题误作逆否命题。",["KB33-C-P065-A004"]),
(65,"06","CONCEPT","在有限形式系统示例中区别相容性、独立性与完备性，不能用单例认证任意公理体系。",["KB33-C-P065-A005"]),
(65,"07","ELECTIVE_TOPIC","把存贷款、投入产出或人口增长模型标为学校选择的应用示例，不升级为全国必修结论。",[]),
]

def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

def require(ok,reason):
    if not ok:
        raise ValueError(reason)

def assemble(pages=None,overlay=None,baseline=None,proposals=None):
    pages = deepcopy(pages if pages is not None else load(PAGES))
    overlay = deepcopy(overlay if overlay is not None else load(OVERLAY))
    baseline = deepcopy(baseline if baseline is not None else load(B51))
    proposals = deepcopy(proposals if proposals is not None else CANDIDATES)
    require(pages["official_pdf_sha256"] == baseline["source_pdf_sha256"] == PDF_SHA, "source PDF SHA drift")
    require(len(pages["pages"])==61 and baseline["source_page_denominator"]==61,"incomplete source page scan")
    require(overlay["summary"]["official_atom_denominator"] is None,"editorial goals falsely official")
    require(overlay["summary"]["project_candidates"]==313,"editorial goal count drift")
    require(overlay["summary"]["teacher_approved"]==0 and overlay["summary"]["student_published"]==0,"falsely approved base")
    require(set(TRACK_BY_PAGE)==set(PAGE_COUNTS),"untracked critical page")
    ix={p["printed_page"]:p for p in pages["pages"]}
    require(set(ix)==set(range(13,74)),"missing page coverage")
    ids={}
    for row in overlay["rows"]:
        require(row["editorial_id"] not in ids, "duplicate legacy editorial ID")
        ids[row["editorial_id"]]=row
    require(len(ids)==313,"editorial ID count drift")
    require(len(proposals)==28,"partial critical-page coverage candidates")
    seen=set()
    rows=[]
    for page,num,kind,goal,links in proposals:
        require(page in TRACK_BY_PAGE and num.isdigit() and len(num)==2,"bad page/number")
        candidate_id=f"KB52-{TRACK_BY_PAGE[page]}-P{page:03d}-U{num}"
        require(candidate_id not in seen,"duplicate source requirement candidate")
        seen.add(candidate_id)
        require(kind in {"METHOD","CONCEPT","THEOREM_SCOPE","ACTIVITY_REQUIREMENT","HISTORY_CONTEXT","COURSE_STRUCTURE","TEACHING_ARTIFACT","ELECTIVE_TOPIC"},"invalid requirement kind")
        require(len(goal)>=20 and len(goal)<=140 and "课标原文" not in goal,"invalid or unreviewable paraphrase")
        require(len(links)==len(set(links)),"duplicate related editorial links")
        for link in links:
            require(link in ids,"orphan related editorial link")
            require(ids[link]["track"]==TRACK_BY_PAGE[page],"cross-track editorial contamination")
            require(ids[link]["printed_page"]==page,"related editorial wrong source page")
            require(not ids[link]["teacher_approved"] and not ids[link]["student_published"],"related draft falsely published")
        pp=ix[page]
        require(pp["full_page_human_review"]=="PENDING","false source human review")
        require(len(pp["pdfkit_text_sha256"])==64 and pp["pdf_page_index"]==page+7,"invalid PDFKit page provenance")
        rows.append({
            "candidate_id":candidate_id, "track":TRACK_BY_PAGE[page],
            "printed_page":page,"pdf_page_index":page+7,
            "source_pdf_sha256":PDF_SHA,
            "source_page_pdfkit_text_sha256":pp["pdfkit_text_sha256"],
            "source_section_triage":SECTION_BY_PAGE[page],
            "requirement_type":kind, "original_editorial_paraphrase":goal,
            "related_editorial_ids_not_equivalence":links,
            "linkage_status":"RELATED_SCOPE_UNVERIFIED" if links else "NO_SAME_PAGE_EDITORIAL_LINK_UNVERIFIED",
            "cross_page_deduplication":"PENDING",
            "full_teacher_lesson_new":False,"source_passages_committed":False,
            "teacher_review":"REVIEW_PENDING","mathematical_scope_certified":False,
            "student_publishable":False, "official_atom_certified":False,
        })
    counts=Counter(r["printed_page"] for r in rows)
    require(dict(counts)==PAGE_COUNTS,"page split incomplete")
    require(len(rows)==len({r["candidate_id"] for r in rows}),"non-unique IDs")
    require(baseline["review_gate"]["official_atomic_knowledge_denominator"] is None
            and all(row["official_atomic_denominator"] is None for row in baseline["track_evidence"]),
            "baseline official denominator cannot be promoted")
    by_track=Counter(r["track"] for r in rows)
    return {
      "schema_version":"1.0","status":"SOURCE_REQUIREMENT_TRIAGE_NOT_OFFICIAL_ATOMS",
      "source_standard":"2017 national math curriculum / 2020 revision",
      "source_pdf_sha256":PDF_SHA,"source_pages_verified_by_pdfkit":[34,41,50,65],
      "new_triage_candidates":len(rows),
      "by_page":{str(k):v for k,v in sorted(counts.items())},
      "by_track":dict(sorted(by_track.items())),
      "without_same_page_editorial_link":sum(not r["related_editorial_ids_not_equivalence"] for r in rows),
      "source_page35_other_7_split_candidates_not_duplicated":7,
      "project_editorial_candidates_unchanged":313,
      "official_atomic_denominator":{k:None for k in ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")},
      "teacher_approved":0,"student_published":0,
      "source_raw_pdf_committed":False,
      "note":"Separate source requirement triage, project editorial IDs, and full lessons. No teacher, formal proof, or product release approval is implied.",
      "rows":rows,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    data=assemble()
    payload=json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    md="# Batch52｜高风险未编号课标要求交叉审计（仅候选，不是官方分母）\n\n"
    md+="来自Mac PDFKit读取的印刷第34、41、50、65页。只保留原创概括、页码、页面SHA和待核ID，不复制课标全文。\n\n"
    md+="| 页码 | 轨道 | 原创来源要求候选 |\n|---:|---|---:|\n"
    for page,count in sorted(PAGE_COUNTS.items()):
        md+=f"| {page} | {TRACK_BY_PAGE[page]} | {count} |\n"
    md+=f"\n合计 **{len(data['rows'])} 条**，仅依现有同页候选未找到直连的 **{data['without_same_page_editorial_link']} 条**。这些并不一定是正式内容缺口，须跨页去重及与既有讲义核对。\n\n"
    md+="旧313项项目编辑候选及第35页7项候选保持独立；七轨道官方分母仍为null，教师批准=0，正式学生发布=0。\n\n"
    md+="## 待处理的全部候选（关联不是等价）\n\n"
    for r in data["rows"]:
        md+=f"- **{r['candidate_id']}**｜{r['original_editorial_paraphrase']}｜同页旧候选：{', '.join(r['related_editorial_ids_not_equivalence']) or '未匹配'}；状态 REVIEW_PENDING。\n"
    md+="\n## 后续核验\n\n逐页与官方原件图表、上下文和教学要求复核；确认跨页去重、课程级别、学业要求与专题选择性质后，才能建立全国/选修各轨道的官方知识原子分母。\n"
    if args.check:
        require(OUTPUT.read_text(encoding="utf-8")==payload,"source crosswalk artifact drift")
        require(REPORT.read_text(encoding="utf-8")==md,"source crosswalk report drift")
    else:
        OUTPUT.write_text(payload,encoding="utf-8")
        REPORT.write_text(md,encoding="utf-8")
    print(f"Batch52 crosswalk {len(data['rows'])} candidates; {data['without_same_page_editorial_link']} with no same-page link; check={args.check}")

if __name__=="__main__":
    main()
