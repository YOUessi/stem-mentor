#!/usr/bin/env python3
"""K00 source trace audit for printed pages 25–36, NOT atomic curriculum certification.

Mac PDFKit retains the original official PDF and line-extracted pages OUTSIDE Git.
This generator commits only original teaching paraphrases and SHA256 source pointers.
CI checks snapshot integrity; only the Mac --verify-source-pdf mode checks original bytes.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"curriculum/highschool_math"
EVAL=ROOT/"docs/evaluation"
SEED=SRC/"k00_batch57_source_spans.tsv"
SNAP=SRC/"k00_batch57_pdfkit_span_attestations.json"
PAGE=SRC/"k00_batch51_pdfkit_page_fingerprints.json"
OLD=EVAL/"KB_BATCH56_COMPULSORY_SOURCE_SPAN_REVIEW.json"
OVERLAY=EVAL/"KB_BATCH50_PROJECT_SCOPE_OVERLAY.json"
RISK=EVAL/"KB_BATCH55_CONFLICT_PROOF_REVIEW.json"
OUTPUT=EVAL/"KB_BATCH57_SOURCE_SPAN_REVIEW.json"
REPORT=EVAL/"KB_BATCH57_SOURCE_SPAN_REVIEW.md"
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
EXPECT={25:3,26:14,27:7,28:11,29:8,30:4,31:6,32:8,33:4,34:5,35:4,36:4}
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
KINDS=("CONTENT","OPTIONAL_STARRED","TEACHING_GUIDANCE","ACHIEVEMENT_REQUIREMENT","ACTIVITY_REQUIREMENT","PDFKIT_UNREADABLE_FIGURE","TRACK_BOUNDARY")

def need(ok,why):
    if not ok: raise ValueError(why)

def load(p):
    return json.loads(Path(p).read_text(encoding="utf8"))

def parse():
    rows=[]
    for line in SEED.read_text(encoding="utf8").splitlines():
        if not line or line.startswith("#"):continue
        parts=line.split("|")
        need(len(parts)==8,"invalid source seed column count")
        p,a,b,kind,star,goal,guard,track=parts
        need(p.isdigit() and a.isdigit() and b.isdigit(),"source page/line must be numeric")
        rows.append(dict(printed_page=int(p),line_start=int(a),line_end=int(b),
            source_kind=kind,optional_flag=star,original_paraphrase=goal,condition_guard=guard,track=track))
    return rows

def span_key(r):
    return "P%03d-L%03d-%03d"%(r["printed_page"],r["line_start"],r["line_end"])

def verify_original(source_dir,pdf_path,rows,pages):
    source_dir=Path(source_dir)
    pdf_path=Path(pdf_path)
    need(pdf_path.is_file() and sha256(pdf_path.read_bytes()).hexdigest()==PDF_SHA,
        "official PDF absent or SHA mismatch")
    lookup={p["printed_page"]:p for p in pages["pages"]}
    need(set(lookup)==set(range(13,74)),"official pages incomplete")
    for p in range(13,74):
        source=source_dir/f"kb56_page_{p}.txt"
        need(source.is_file(),"PDFKit local page missing")
        # Raw bytes: page 35 has control codes, and some PDFKit pages include CR.
        need(sha256(source.read_bytes()).hexdigest()==lookup[p]["pdfkit_text_sha256"],
            "PDFKit source-page raw-byte mismatch: "+str(p))
    digests={}
    for row in rows:
        source=source_dir/f"kb56_page_{row['printed_page']}.txt"
        lines=source.read_text(encoding="utf8").splitlines()
        a,b=row["line_start"],row["line_end"]
        need(1<=a<=b<=len(lines),"source lines out of range")
        key=span_key(row)
        need(key not in digests,"duplicate source location")
        digests[key]=sha256("\n".join(lines[a-1:b]).encode("utf8")).hexdigest()
    return {"schema_version":"kb57-pdfkit-mac-local-attestation-v1",
            "pinned_pdf_sha256":PDF_SHA,
            "source_passages_or_pdf_committed":False,
            "readable_image_semantics_attested":False,
            "attestations":dict(sorted(digests.items()))}

def build(*,rows=None,pages=None,old=None,overlay=None,risk=None,snapshot=None):
    rows=deepcopy(rows if rows is not None else parse())
    pages=deepcopy(pages if pages is not None else load(PAGE))
    old=deepcopy(old if old is not None else load(OLD))
    overlay=deepcopy(overlay if overlay is not None else load(OVERLAY))
    risk=deepcopy(risk if risk is not None else load(RISK))
    snapshot=deepcopy(snapshot if snapshot is not None else load(SNAP))
    need(pages["official_pdf_sha256"]==PDF_SHA and len(pages["pages"])==61,
         "source PDF identity or 61-page inventory drift")
    page_index={p["printed_page"]:p for p in pages["pages"]}
    need(set(page_index)==set(range(13,74)),"61 printed pages incomplete")
    need(old["candidate_source_spans"]==52 and old["source_pages_partially_annotated"]==list(range(15,25)),
         "previous source-span baseline drift")
    need(old["teacher_approved"]==old["student_published"]==0
         and all(v is None for v in old["official_atomic_denominator"].values()),
         "previous source evidence wrongly promoted")
    need(overlay["summary"]["project_candidates"]==313
         and overlay["summary"]["teacher_approved"]==0
         and overlay["summary"]["student_published"]==0, "editorial baseline / approval drift")
    need(all(not e["teacher_approved"] and not e["student_published"] for e in overlay["rows"]),
         "individual editorial target forged teacher approval")
    need(risk["frozen_unverified_proof_steps"]==538
         and risk["conflict_count"]==10 and risk["conflicts_resolved"]==0,
         "unreviewed mathematical risk inventory drift")
    need(all(v is None for v in risk["official_atomic_denominator"].values()),
         "uncertified official denominators cannot be promoted")
    need(snapshot["pinned_pdf_sha256"]==PDF_SHA
         and snapshot["source_passages_or_pdf_committed"] is False
         and snapshot["readable_image_semantics_attested"] is False,
         "source attestation provenance or image semantics forged")
    need(len(rows)==sum(EXPECT.values())==len(snapshot["attestations"]),
         "partial source span inventory")
    counts=Counter();used=set();out=[]
    editorial=overlay["rows"]
    need(len({r["editorial_id"] for r in editorial})==313,"duplicate editorial reference IDs")
    for row in rows:
        p,a,b=row["printed_page"],row["line_start"],row["line_end"]
        kind,track=row["source_kind"],row["track"]
        need(p in EXPECT and 1<=a<=b<=100,"invalid source page or line")
        need(row["optional_flag"] in ("Y","N"),"starred flag invalid")
        need(kind in KINDS,"unrecognized source kind")
        need(row["optional_flag"]==("Y" if kind=="OPTIONAL_STARRED" else "N"),
             "optional-star type mismatch")
        need(kind!="OPTIONAL_STARRED" or p in (27,29),"starred source scope mismatch")
        need(kind!="PDFKIT_UNREADABLE_FIGURE" or (p,a,b) in ((34,21,21),(35,1,14)),
             "figure evidence cannot be invented")
        need(kind!="TRACK_BOUNDARY" or (p,a,b,track)==(36,16,20,"SELECTIVE_COMPULSORY"),
             "selective/compulsory boundary mismatch")
        need(track==("SELECTIVE_COMPULSORY" if kind=="TRACK_BOUNDARY" else "COMPULSORY"),
             "wrong curriculum track")
        need(19<=len(row["original_paraphrase"])<=150,"missing original mathematical/teaching explanation")
        need(re.fullmatch(r"[A-Z0-9_]{8,72}",row["condition_guard"]) is not None,
             "missing explicit mathematical or policy guard")
        key=span_key(row)
        need(key not in used,"duplicate source span")
        used.add(key)
        digest=snapshot["attestations"].get(key)
        need(isinstance(digest,str) and re.fullmatch(r"[a-f0-9]{64}",digest) is not None,
             "source-span SHA attestation missing")
        pg=page_index[p]
        need(pg["pdf_page_index"]==p+7 and pg["full_page_human_review"]=="PENDING",
             "wrong PDF index or fabricated complete review")
        need(re.fullmatch(r"[a-f0-9]{64}",pg["pdfkit_text_sha256"]) is not None,
             "missing source page hash")
        counts[p]+=1
        ids=sorted(e["editorial_id"] for e in editorial if e["track"]==track and e["printed_page"]==p)
        out.append({
            "candidate_id":f"KB57-C-P{p:03d}-S{counts[p]:03d}","source_span_id":key,
            "printed_page":p,"pdf_page_index":p+7,"track":track,"source_kind":kind,
            "starred_optional":row["optional_flag"]=="Y",
            "source_pdf_sha256":PDF_SHA,"source_page_pdfkit_sha256":pg["pdfkit_text_sha256"],
            "source_span_pdfkit_sha256":digest,"original_editorial_paraphrase":row["original_paraphrase"],
            "mathematical_or_policy_guard":row["condition_guard"],
            "exam_requirement_status":("EXPLICITLY_OPTIONAL_NOT_EXAM" if kind=="OPTIONAL_STARRED"
                else "NOT_A_CONTENT_ATOM" if kind in ("PDFKIT_UNREADABLE_FIGURE","TRACK_BOUNDARY",
                         "TEACHING_GUIDANCE","ACHIEVEMENT_REQUIREMENT")
                else "REQUIRES_SCOPE_REVIEW"),
            "semantic_source_readability":("VISUAL_REVIEW_REQUIRED" if kind=="PDFKIT_UNREADABLE_FIGURE"
                else "PDFKIT_TEXT_LINE_REVIEW_ONLY"),
            "same_page_related_editorial_ids_not_equivalence":ids,
            "full_page_human_review":"PENDING","cross_page_mathematical_deduplication":"PENDING",
            "official_atom_certified":False,"mathematical_scope_equivalence_certified":False,
            "teacher_review":"REVIEW_PENDING","student_publishable":False,
            "formal_general_proof_certified":False})
    need(dict(counts)==EXPECT,"source page counts changed")
    need(used==set(snapshot["attestations"]),"unattached or missing source attestations")
    need(sum(r["starred_optional"] for r in out)==3,"starred elective records missing")
    need(sum(r["source_kind"]=="PDFKIT_UNREADABLE_FIGURE" for r in out)==2,
         "unreadable modeling diagram must remain unresolved")
    need(len({r["candidate_id"] for r in out})==len(out),"duplicate candidate IDs")
    kind_counts=dict(sorted(Counter(r["source_kind"] for r in out).items()))
    return {
        "schema_version":"kb57-partial-source-evidence-v1",
        "status":"PARTIAL_ORIGINAL_SOURCE_TRIAGE_NOT_OFFICIAL_ATOMS",
        "official_pdf_sha256":PDF_SHA,
        "source_pages_total":61,
        "pages_newly_partially_annotated":sorted(EXPECT),
        "pages_partially_annotated_combined":list(range(15,37)),
        "batch56_source_spans_kept_separately":52,
        "new_source_spans":len(out),"combined_nonunique_source_spans":52+len(out),
        "new_counts_per_page":{str(p):counts[p] for p in sorted(counts)},
        "new_counts_by_kind":kind_counts,
        "starred_optional_not_exam":3,
        "source_image_gaps_not_interpreted":2,
        "project_editorial_candidates_not_official_atoms":313,
        "unverified_historical_proof_steps":538,"unresolved_math_conflicts":10,
        "official_atomic_denominator":{k:None for k in TRACKS},
        "full_teacher_reviewed_page_atomizations":0,
        "teacher_approved":0,"student_published":0,
        "source_passages_or_pdf_committed":False,
        "note":"Partial, overlapping line-anchored editorial scope records, NOT a complete per-page, cross-page deduplicated or teacher-certified mathematical atom count. Model diagram P35 requires original visual review.",
        "rows":out}

def render(data):
    s=[
        "# Batch57｜25–36页几何、概率统计、建模课标来源审查（未正式原子化）","",
        "来源：教育部2017版2020修订高中数学课标。原PDF及PDFKit文字仅保留于授权Mac，不提交原文；"
        "锁定PDF SHA256：`"+PDF_SHA+"`。","",
        f"本批**{data['new_source_spans']}条独立释义的原文定位**、12个来源页；与此前52条合计"
        f"{data['combined_nonunique_source_spans']}条定位记录。这些记录有重叠，**不能充当官方知识原子分母**。","",
        "| 来源分类 | 新记录数 | 处理方式 |","|---|---:|---|",
    ]
    for kind,count in data["new_counts_by_kind"].items():
        s.append(f"| {kind} | {count} | 待跨页去重/数学范围核验/教师复核 |")
    s.extend(["","## 保留的高风险来源边界","",
        "- 印刷27页及29页明确标星的复数三角表示、几何发展史等记录属于**选学、不作为考试必授要求**，不能冒充同页一般必授项目。",
        "- 印刷28–29页的空间判定/性质依赖不同的假设：线面平行的外部直线、面面平行的相交直线、角对应平行产生相等或互补等均不可省略。",
        "- 印刷30页的教学范围强调早期空间几何的直观感知与选择性必修后续论证的分层；教学建议不等于独立定理。",
        "- 印刷31–33页概率/统计的有限样本、等可能、独立性、抽样框、样本方差分母及百分位定义需要独立核查。",
        "- 印刷34–35页的数学建模流程图PDFKit出现不可解码图形与控制符，**没有自动从乱码推断图示语义**；仅定位待人工看图，不计算覆盖。",
        "- 印刷35页的课题研究实践要求不等同于普通证明题；36页开始进入选择性必修课程，不得跨轨道误算。",
        "- 本轮新增标记是人工编辑的来源解释、不是原文大段转载，不是自动认证的完整讲义、定理、证明或标准化教师批准。","",
        "## 逐页定位数量","", "| 印刷页 | 新定位 |", "|---:|---:|"])
    s.extend(f"| {p} | {n} |" for p,n in data["new_counts_per_page"].items())
    s.extend(["","## 逐项原创编辑释义与数学条件",""])
    for r in data["rows"]:
        s.append(f"- `{r['candidate_id']}` P{r['printed_page']} `{r['source_span_id']}` "
                 f"{r['source_kind']} / {r['track']}：{r['original_editorial_paraphrase']} "
                 f"（约束 `{r['mathematical_or_policy_guard']}`；`REVIEW_PENDING`）。")
    s.extend(["","## 下一批验收阻断","",
       "尚未逐条审完全部61个来源页；每页划分可能重叠，跨页数学等价、选学范围及教师签署均未完成，"
       "**七个官方知识原子分母继续是null**。既有313项仅为项目编辑候选；538条步骤仍未形式认证，10组冲突未裁决。",
       "学生端正式发布为0。真实教师核验、课标完整范围去重和数学独立审查完成前，保留Draft。",
       "Mac原件核验：`python scripts/build_kb_batch57_source_review.py --check "
       "--verify-source-pdf /private/tmp/stem-mentor-official-math-2020-batch51.pdf "
       "--source-dir /private/tmp`；CI只验证哈希台账和生成一致性，不声称独立打开官方PDF。",""])
    return "\n".join(s)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    ap.add_argument("--verify-source-pdf",type=Path)
    ap.add_argument("--source-dir",type=Path)
    args=ap.parse_args()
    need((args.verify_source_pdf is None)==(args.source_dir is None),
         "PDF and extracted page directory must be paired")
    seeds=parse()
    if args.verify_source_pdf is not None:
        snap=verify_original(args.source_dir,args.verify_source_pdf,seeds,load(PAGE))
        if args.check:
            need(load(SNAP)==snap,"local PDFKit attestation drift")
        else:
            SNAP.write_text(json.dumps(snap,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    audit=build()
    json_body=json.dumps(audit,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    md=render(audit)
    if args.check:
        need(OUTPUT.read_text(encoding="utf8")==json_body,"generated JSON drift")
        need(REPORT.read_text(encoding="utf8")==md,"generated Markdown drift")
    else:
        OUTPUT.write_text(json_body,encoding="utf8")
        REPORT.write_text(md,encoding="utf8")
    print(f"Batch57 checked: {audit['new_source_spans']} new source pointers on "
          f"{len(audit['pages_newly_partially_annotated'])} pages; "
          "unreadable visual gaps=2; official denominators UNVERIFIED; check="+str(args.check))

if __name__=="__main__":
    main()
