#!/usr/bin/env python3
"""Reproducible, non-authoritative, PDFKit-anchored cross-page K00 review.

17 precise ORIGINAL candidate requirements for source pages 15 and 52.
They are not certified/complete national syllabus atoms or approved lessons.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
import re
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch105_crosspage_authoring import ATOM_CANDIDATES,PAGE_PARTITIONS,CROSS_PAGE_BRIDGES
from app.kb_batch105_math import witness

FINGERPRINTS=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
PRIOR=ROOT/"curriculum/highschool_math/k00_batch73_page_partition_witness.json"
PDF=Path.home()/"Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
EVIDENCE_SHA="ec26621b7f358f892355d6e6b93622e529df30cfd6067fa1f48d77df48ffc19a"
PARTITION_SHA="0737bbb2fe9e66170c900ab1b05ac36ca84fdf11bdb37798d4e43ea643cace12"
SEVEN=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
       "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
REPORT=ROOT/"docs/evaluation/KB_BATCH105_CROSSPAGE_ATOMS.json"
MD=ROOT/"docs/evaluation/KB_BATCH105_CROSSPAGE_ATOMS.md"

def require(test,reason):
    if not test:
        raise ValueError(reason)

def canonical(v):
    return json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"

def build(atoms=ATOM_CANDIDATES,parts=PAGE_PARTITIONS,bridges=CROSS_PAGE_BRIDGES,
          verify_local=False):
    require(sha256(FINGERPRINTS.read_bytes()).hexdigest()==EVIDENCE_SHA,
            "source registry drift")
    require(sha256(PRIOR.read_bytes()).hexdigest()==PARTITION_SHA,
            "prior page partition drift")
    meta=json.loads(FINGERPRINTS.read_text())
    prior=json.loads(PRIOR.read_text())
    require(prior["source_pdf_sha256"]==PDF_SHA,"source PDF SHA mismatch")
    require(prior["full_page_teacher_reviews"]==0,"unexpected human review claim")
    page_meta={p["printed_page"]:p for p in meta["pages"]}
    for page in (14,15,51,52):
        require(page in page_meta,"unknown cross-page source")
    if verify_local:
        require(PDF.is_file() and sha256(PDF.read_bytes()).hexdigest()==PDF_SHA,
                "Mac original PDF missing or mutated")
        for page in (14,15,51,52):
            source=Path(f"/private/tmp/kb56_page_{page}.txt")
            require(source.is_file() and sha256(source.read_bytes()).hexdigest()
                    ==page_meta[page]["pdfkit_text_sha256"],
                    f"local PDFKit source drift on printed page {page}")

    max_lines={}
    for page,segments in parts.items():
        require(page in (15,52),"unexpected atomic source page")
        matching=[s for s in prior["segments"] if s["printed_page"]==page]
        max_line=max(s["last_line"] for s in matching)
        max_lines[page]=max_line
        expanded=[]
        for lo,hi,kind in segments:
            require(0<lo<=hi<=max_line and len(kind)>8,"invalid structural segment")
            expanded+=list(range(lo,hi+1))
        require(expanded==list(range(1,max_line+1)),
                "missing, overlapping or reordered page structural lines")
    require(max_lines=={15:27,52:49}, "PDFKit line registry changed")
    require(len(atoms)==17,"not all seventeen editorial candidates present")
    allowed={"CONCEPT","THEOREM","METHOD"}
    ids=set()
    seen_titles=set()
    required_fields=set(ATOM_CANDIDATES[0])
    by_track=Counter()
    draft_ids={}
    for path in sorted((ROOT/"knowledge/deep/v1").glob("*.json")):
        match=re.match(r"batch(\d+)_",path.name)
        if match is not None and int(match.group(1))>105:
            continue  # historical PDF review count frozen at batch105
        for doc in json.loads(path.read_text(encoding="utf8")):
            doc_id=doc["id"]
            require(doc_id not in draft_ids,"duplicate existing draft lesson ID")
            draft_ids[doc_id]=doc
    result=[]
    for index,atom in enumerate(atoms,1):
        require(set(atom)==required_fields,"unsupported/forged author fields")
        require(atom["title"] not in seen_titles,"duplicate mathematical requirement")
        seen_titles.add(atom["title"])
        page=atom["page"]
        require(page in (15,52),"unexpected page for candidate")
        require(atom["track"]==("COMPULSORY" if page==15 else "ELECTIVE_A"),
                "cross-track proposed atom")
        require(atom["kind"] in allowed,"invalid knowledge kind")
        require(type(atom["start"]) is int and type(atom["end"]) is int and
                1<=atom["start"]<=atom["end"]<=max_lines[page],
                "invalid source line range")
        for key,minimum in (("title",4),("editorial_interpretation",30),
                            ("mathematical_preconditions",14),
                            ("misleading_generalization",14)):
            require(isinstance(atom[key],str) and len(atom[key])>=minimum,
                    "incomplete math editorial evidence: "+key)
        oid=f"KB105-P{page:03d}-C{index:02d}"
        require(oid not in ids,"duplicate candidate id")
        ids.add(oid)
        for ref in atom["related_draft_ids"]:
            require(ref in draft_ids,"orphan draft crosslink "+ref)
            require(draft_ids[ref]["review"]["status"]!="APPROVED",
                    "approved target requires a separate citation and release audit")
        w=witness(atom["finite_oracle_key"])
        require(w["finite_or_symbolic_witness_passed"] and
                w["invalid_generalization_rejected"] and
                not w["general_proof_certified"] and
                not w["teacher_approved"] and
                not w["student_step_verified"],"oracle cannot grant teacher authority")
        result.append(dict(candidate_id=oid,printed_page=page,
                           source_line_start=atom["start"],source_line_end=atom["end"],
                           pdf_page_index=page_meta[page]["pdf_page_index"],
                           source_page_text_sha256=page_meta[page]["pdfkit_text_sha256"],
                           source_pdf_sha256=PDF_SHA,
                           track=atom["track"],kind=atom["kind"],title=atom["title"],
                           editorial_interpretation=atom["editorial_interpretation"],
                           mathematical_preconditions=atom["mathematical_preconditions"],
                           misleading_generalization=atom["misleading_generalization"],
                           related_draft_ids=atom["related_draft_ids"],
                           independently_computed_witness=w,
                           provenance_class="OFFICIAL_SOURCE_RANGE_EDITORIAL_PROPOSAL",
                           official_atom_id=None,teacher_review_status="REVIEW_PENDING",
                           formally_certified=False,
                           publishable_for_student=False,
                           is_complete_source_page_atomization=False))
        by_track[atom["track"]]+=1
    require(set(x["finite_oracle_key"] for x in atoms)==
            {r["independently_computed_witness"]["oracle_key"] for r in result},
            "oracle/candidate mismatch")
    require(by_track=={"COMPULSORY":8,"ELECTIVE_A":9},
            "source split unexpected")
    require(len(bridges)==2,"missing independent cross-page connective review")
    bridge_rows=[]
    for bridge in bridges:
        frm,to=bridge["from_page"],bridge["to_page"]
        require((frm,to,bridge["track"]) in
                {(14,15,"COMPULSORY"),(51,52,"ELECTIVE_A")},
                "cross-page bridge or track invalid")
        require((bridge["from_lines"],bridge["to_lines"]) ==
                (([27,31],[1,9]) if frm==14 else ([24,27],[2,8])),
                "cross-page connective extent drift")
        for k,p in (("from_lines",frm),("to_lines",to)):
            lo,hi=bridge[k]
            require(type(lo) is int and type(hi) is int and
                    0<lo<=hi<=max(s["last_line"] for s in prior["segments"]
                                if s["printed_page"]==p),"bad bridge range")
        require(len(bridge["interpretation"])>=35,"bridge explanation too thin")
        bridge_rows.append({**bridge,
           "from_page_sha256":page_meta[frm]["pdfkit_text_sha256"],
           "to_page_sha256":page_meta[to]["pdfkit_text_sha256"],
           "claim_type":"COURSE_CONTEXT_NOT_SEPARATE_MATH_ATOM",
           "teacher_review_status":"REVIEW_PENDING"})
    report={
       "schema_version":"kb105-page15-page52-crosspage-editorial-candidates-v1",
       "base_standard":"普通高中数学课程标准（2017年版2020年修订）",
       "base_standard_url":"https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf",
       "source_pdf_sha256":PDF_SHA,
       "author_script_sha256":sha256((ROOT/"scripts/kb_batch105_crosspage_authoring.py").read_bytes()).hexdigest(),
       "source_page_registry_sha256":EVIDENCE_SHA,
       "source_page_partition_registry_sha256":PARTITION_SHA,
       "all_source_pages_full_teacher_reviewed":False,
       "source_pages_editorially_covered":[15,52],
       "source_pages_bridge_context":[14,51],
       "line_count_by_page":{str(p):n for p,n in max_lines.items()},
       "structural_partition_count":sum(map(len,parts.values())),
       "structural_partitions":[{"page":p,"start":lo,"end":hi,"type":kind}
            for p,segments in sorted(parts.items()) for lo,hi,kind in segments],
       "cross_page_bridges":bridge_rows,
       "provisional_requirement_candidate_count":len(result),
       "provisional_requirement_count_by_track":{t:by_track[t] for t in SEVEN},
       "official_seven_track_denominators":{t:None for t in SEVEN},
       "teacher_full_page_atomizations":0,
       "teacher_approvals":0,"student_authoritative_releases":0,
       "general_formal_proof_certificates":0,
       "math_finite_or_symbolic_witnesses":len(result),
       "math_invalid_generalization_rejections":len(result),
       "historical_prerequisite_text_unreviewed":172,
       "historical_proof_steps_uncertified":538,
       "historical_math_conflicts_open":10,
       "not_new_complete_deep_lessons":True,
       "existing_candidate_deep_lessons":len(draft_ids),
       "candidates":result,
       "limitations":[
          "Only selected source requirements on printed pages 15 and 52 are separately proposed; not a complete national syllabus atomization.",
          "PDFKit text may reorder mathematics fractions and glyphs; mathematical statements are original editorial interpretations, not verbatim transcription.",
          "Page source SHA does not independently prove a candidate's semantic correctness.",
          "Symbolic limits and finite examples do not certify arbitrary universal proofs or arbitrary student work.",
          "Potentially related existing teacher-only drafts are not approved replacements for official curriculum atoms.",
          "Student tutor must not retrieve teacher-only drafts or expose answers during independent practice."
       ]}
    require(not report["all_source_pages_full_teacher_reviewed"] and
            all(v is None for v in report["official_seven_track_denominators"].values()),
            "official completeness cannot be inferred from candidate count")
    return report

def markdown(report):
    out=["# Batch105｜课标第14–15、51–52页跨页原子候选（教师候审）","",
      "**范围说明：** 依据已固定 SHA 的 2020 修订版数学课程标准，"
      "对第15页必修集合要求与第52页选修A极限要求，作原创、来源行定位的语义候选拆分。"
      "这些**不是**全国正式七轨分母，也不是教师认证的正式知识原子。","",
      f"来源 SHA256：`{report['source_pdf_sha256']}`。"
      f"两个重点页面 PDFKit 总计 {sum(report['line_count_by_page'].values())} 行，"
      f"{report['structural_partition_count']} 个不重叠结构分区，"
      f"{report['provisional_requirement_candidate_count']} 条有重叠来源行的数学要求候选；"
      "另有2个跨页导语衔接。","",
      "## 跨页与非数学原子区段",""]
    for b in report["cross_page_bridges"]:
        out+=[f"- 第{b['from_page']}页{b['from_lines'][0]}–{b['from_lines'][1]}行"
               f" → 第{b['to_page']}页{b['to_lines'][0]}–{b['to_lines'][1]}行："
               f"{b['interpretation']}"]
    out+=["","## 有限数学核验与课标要求候选",""]
    for r in report["candidates"]:
        w=r["independently_computed_witness"]
        out += [f"### {r['candidate_id']}｜{r['title']}","",
          f"课标来源：印刷页{r['printed_page']}，PDFKit行{r['source_line_start']}–{r['source_line_end']}；"
          f"轨道 {r['track']}；候选类型 {r['kind']}。","",
          f"**原创数学解释：** {r['editorial_interpretation']}","",
          f"**成立条件：** {r['mathematical_preconditions']}","",
          f"**失效/错误概括：** {r['misleading_generalization']}","",
          f"**有限数学证据：** {w['witness_note']}；"
          "仅有限精确计算或支持范围内的SymPy符号极限，不代表一般形式证明。","",
          "关联已有候审讲义（仅教师编辑参考）："+(", ".join(r["related_draft_ids"]) or "无")+"。",""]
    out+=["## 审核剩余与不可越界结论","",
      "两页虽完成**来源行结构分段和部分需求拆分**，但尚未完成老师逐页全量数学原子化。"
      "此前的其它59页也不能自动按该17条推算。正式必修、选择性必修、选修A/B/C/D/E七轨分母全部仍为 UNKNOWN。","",
      "17项负面泛化排除均为有限或符号工具范围内检查；涉及定理的一般证明仍需逐步审校。"
      "全部 REVIEW_PENDING，学生不可权威发布，未新增完整讲义。",""]
    return "\n".join(out)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true")
    args=p.parse_args()
    report=build(verify_local=args.verify_local_source)
    for dest,txt in ((REPORT,canonical(report)),(MD,markdown(report))):
        if args.check:
            require(dest.is_file() and dest.read_text(encoding="utf8")==txt,
                    "committed report drift: "+str(dest))
        else:
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_text(txt,encoding="utf8")
    print(f"Batch105: {len(report['candidates'])} requirement candidates, "
          f"{report['structural_partition_count']} source partitions, "
          f"{len(report['cross_page_bridges'])} bridges, "
          f"{report['math_finite_or_symbolic_witnesses']} witnesses; check={args.check}")

if __name__=="__main__":main()
