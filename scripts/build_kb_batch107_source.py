#!/usr/bin/env python3
"""Auditable, teacher-pending source-to-math editorial review for pp.17/54."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from hashlib import sha256
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch107_source_authoring import CANDIDATES,PARTITIONS
from app.kb_batch107_math import check

META=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
PRIOR=ROOT/"curriculum/highschool_math/k00_batch73_page_partition_witness.json"
OUT=ROOT/"docs/evaluation/KB_BATCH107_SOURCE_REVIEW.json"
MARKDOWN=ROOT/"docs/evaluation/KB_BATCH107_SOURCE_REVIEW.md"
PDF=Path.home()/"Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
EXPECTED_PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
ALLOWED=("CONCEPT","THEOREM","METHOD")
# Independent immutable source-range contract, reviewed against PDFKit line registry.
# This prevents a source author field from being silently moved to an unrelated
# but in-range clause. Candidate splitting remains editorial, not teacher approved.
CLAUSE_LOCK={
 "amgm_opt":(17,1,1),"quad_two":(17,9,11),"quad_tangent":(17,9,11),
 "quad_none":(17,9,11),"zero_graph":(17,10,11),
 "quad_positive":(17,13,15),"quad_nonnegative":(17,13,15),
 "quad_linear":(17,9,11),"ineq_sets":(17,13,15),
 "graph_sign":(17,16,17),"singleton":(17,24,26),
 "signed_area":(54,2,4),"solid_volume":(54,2,4),
 "work_integral":(54,2,4),"centroid_integral":(54,2,4),
 "dot_product":(54,18,18),"cross_product":(54,18,18),
 "projection":(54,19,19),"linear_dependence":(54,20,20),
 "subspace":(54,21,21),"matrix_multiply":(54,23,24),
 "orthogonal":(54,25,25),"determinant":(54,26,26)
}


def require(ok, reason):
    if not ok:raise ValueError(reason)


def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"


def build(candidates=CANDIDATES, partitions=PARTITIONS,verify_local_source=False):
    require(sha256(META.read_bytes()).hexdigest()=="ec26621b7f358f892355d6e6b93622e529df30cfd6067fa1f48d77df48ffc19a", "source fingerprint registry drift")
    require(sha256(PRIOR.read_bytes()).hexdigest()=="0737bbb2fe9e66170c900ab1b05ac36ca84fdf11bdb37798d4e43ea643cace12", "source structural partition registry drift")
    meta=json.loads(META.read_text(encoding="utf8"))
    prior=json.loads(PRIOR.read_text(encoding="utf8"))
    require(prior["source_pdf_sha256"]==EXPECTED_PDF_SHA, "official-source PDF drift")
    require(prior["full_page_teacher_reviews"]==0, "cannot invent teacher review")
    m={r["printed_page"]:r for r in meta["pages"]}
    spans={p:[r for r in prior["segments"] if r["printed_page"]==p] for p in (17,54)}
    require(set(partitions)=={17,54}, "not both expected source pages")
    limits={}
    for p,groups in partitions.items():
        require(p in m and len(spans[p])>0, "missing page registry")
        top=max(r["last_line"] for r in spans[p])
        limits[p]=top
        expanded=[]
        for lo,hi,group in groups:
            require(type(lo) is int and type(hi) is int and 0<lo<=hi<=top
                    and len(group)>10,"invalid source structural segment")
            expanded.extend(range(lo,hi+1))
        require(expanded==list(range(1,top+1)),
                "source page has missing/duplicate/reordered structural lines")
    require(limits=={17:27,54:27},"source line partition drift")
    if verify_local_source:
        require(PDF.is_file() and sha256(PDF.read_bytes()).hexdigest()==EXPECTED_PDF_SHA,
                "missing or mutated Mac standard PDF")
        for p in limits:
            f=Path(f"/private/tmp/kb56_page_{p}.txt")
            require(f.is_file() and sha256(f.read_bytes()).hexdigest()==m[p]["pdfkit_text_sha256"],
                    f"Mac PDFKit text fingerprint mismatch page={p}")
    require(len(candidates)==23, "expected 23 substantive source proposals")
    required_fields=set(CANDIDATES[0])
    seen=set()
    titles=set()
    rows=[]
    counts=Counter()
    for n,r in enumerate(candidates,1):
        require(set(r)==required_fields, "candidate schema drift")
        require(r["page"] in limits,"unknown candidate page")
        page=r["page"]
        track="COMPULSORY" if page==17 else "ELECTIVE_A"
        require(r["kind"] in ALLOWED,"invalid math class")
        require(type(r["start"]) is int and type(r["end"]) is int
                and 1<=r["start"]<=r["end"]<=limits[page], "out-of-range source")
        source_partition=[(lo,hi,t) for lo,hi,t in partitions[page]
                          if lo<=r["start"]<=r["end"]<=hi]
        require(len(source_partition)==1,
                "candidate cannot silently straddle source structural sections")
        require((r["page"],r["start"],r["end"])==CLAUSE_LOCK.get(r["oracle_key"]),
                "candidate/source clause lock mismatch")
        require(r["title"] not in titles,"duplicate title across candidate records")
        titles.add(r["title"])
        require(len(r["title"])>6 and len(r["mathematical_preconditions"])>=18
                and len(r["misleading_generalization"])>=18
                and len(r["editorial_note"])>=22, "thin mathematics editorial record")
        require(r["oracle_key"] not in seen,"duplicate oracle/review key")
        seen.add(r["oracle_key"])
        outcome=check(r["oracle_key"])
        require(outcome["finite_exact_positive_passed"]
                and outcome["invalid_generalization_rejected"]
                and not outcome["teacher_approved"]
                and not outcome["universal_proof_certified"],
                "invalid mathematical evidence authority")
        row={**r,
             "candidate_id":f"KB107-P{page:03d}-C{n:02d}",
             "track":track,
             "source_partition_type":source_partition[0][2],
             "pdf_page_index":m[page]["pdf_page_index"],
             "source_page_pdfkit_sha256":m[page]["pdfkit_text_sha256"],
             "source_pdf_sha256":EXPECTED_PDF_SHA,
             "bounded_math_check":outcome,
             "official_atom_id":None,"teacher_review_status":"REVIEW_PENDING",
             "teacher_full_page_review":False,
             "student_authoritative_release":False,
             "is_general_math_proof":False}
        rows.append(row);counts[track]+=1
    require(seen==set(CLAUSE_LOCK),"missing or extra source-clause oracle keys")
    # Count source evidence independently of editorial math tags.
    require(counts=={"COMPULSORY":11,"ELECTIVE_A":12}, "source track conservation")
    # Source 17 starts with a continuation of 16; 54 starts with a
    # continuation of elective-A integral clause from 53.
    require(rows[0]["source_partition_type"]=="CROSS_PAGE_MATH_CONTINUATION",
            "crosspage clause lost")
    report={
       "version":"batch107-k00-page17-page54-draft-v1",
       "standard":"普通高中数学课程标准（2017年版2020年修订）",
       "standard_url":"https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf",
       "source_pdf_sha256":EXPECTED_PDF_SHA,
       "source_fingerprint_registry_sha256":sha256(META.read_bytes()).hexdigest(),
       "source_partition_registry_sha256":sha256(PRIOR.read_bytes()).hexdigest(),
       "authoring_sha256":sha256((ROOT/"scripts/kb_batch107_source_authoring.py").read_bytes()).hexdigest(),
       "pages":[17,54],
       "page_line_counts":{str(k):v for k,v in limits.items()},
       "full_source_line_partition_count":sum(map(len,partitions.values())),
       "source_line_partitions":[{"page":p,"start":lo,"end":hi,"kind":name}
            for p,spans in sorted(partitions.items()) for lo,hi,name in spans],
       "crosspage_context":[
           {"from":16,"to":17,"meaning":"nonnegative AM-GM upper-bound applications continue onto page 17; no separate certified official atom"},
           {"from":53,"to":54,"meaning":"elective A definite integral applications continue onto page 54; distinguish area/volume/work/centroid as provisional interpretations"}],
       "source_requirement_editorial_candidates":len(rows),
       "counts_by_seven_tracks":{t:counts[t] for t in TRACKS},
       "official_atom_denominators_by_seven_tracks":{t:None for t in TRACKS},
       "whole_source_page_teacher_atomizations":0,
       "teacher_approved":0,"student_authoritative_releases":0,
       "formal_universal_proof_certificates":0,
       "computed_bounded_exact_positive_cases":len(rows),
       "computed_bad_generalization_rejections":len(rows),
       "unreviewed_historical_prerequisites":172,
       "uncertified_historical_proof_steps":538,
       "unresolved_math_conflicts":10,
       "candidates":rows,
       "limitations":[
           "Source lines and structural partitions are machine-auditable; semantic math candidate splitting is original editorial interpretation awaiting independent teacher review.",
           "Page 17 line 25-26 is teaching guidance, not a standalone mandatory syllabus requirement.",
           "A linked source page SHA cannot prove a mathematical generalization or a lesson.",
           "Elective A page 54 may not be replaced by generic project '选修拓展' tags without a human seven-track crosswalk.",
           "No general theorem, student free-text step or approval is certified by bounded tests.",
           "Official atom denominator is unknown; no student authority is published."] }
    return report


def markdown(r):
    lines=["# Batch107｜印刷第17、54页课程来源逐段审查（教师候审）","",
      "本记录不是官方知识原子冻结分母，也不代表任何教师审核或学生发布。","",
      f"来源页：{r['pages']}；完整页面结构划分{r['full_source_line_partition_count']}段；"
      f"23项原创编辑候选（必修11、选修A12），每项均有一组有限正例和失效反例。","",
      "## 课程跨页接续","",
      "- 第16→17页：基本不等式的实际最值应用是连续表述，不因换页生成独立官方原子。",
      "- 第53→54页：定积分应用跨页，面积、体积、功与重心是候选拆分而非教师冻结原子。","",
      "## 单项候选及数学边界",""]
    for v in r["candidates"]:
        lines.extend([f"### {v['candidate_id']}｜{v['title']}","",
          f"来源：印刷页{v['page']} 第{v['start']}–{v['end']}行；{v['track']}；{v['source_partition_type']}。","",
          f"适用条件：{v['mathematical_preconditions']}","",
          f"无效泛化：{v['misleading_generalization']}","",
          f"独立有限检验：{v['bounded_math_check']['computed_explanation']}","",
          f"编辑说明：{v['editorial_note']}",""])
    lines.extend(["## 未解决门槛","",
         "- 七轨正式知识原子分母依然未知；所有新候选 REVIEW_PENDING。",
         "- 无教师完整逐页原子审核，无普遍定理形式认证，无学生端权威索引发布。",
         "- 下一批：建立第18/55页后续来源证据、补齐先修关系和高风险证明条件复核。",""])
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true")
    args=p.parse_args()
    report=build(verify_local_source=args.verify_local_source)
    for path,content in ((OUT,canonical(report)),(MARKDOWN,markdown(report))):
        if args.check: require(path.exists() and path.read_text(encoding="utf8")==content,
                               "artifact drift "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf8")
    print("Batch107 source review",len(report["candidates"]),
          "draft source candidates; 23 finite positives and 23 invalid generalizations; check",args.check)

if __name__=="__main__":main()
