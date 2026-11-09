#!/usr/bin/env python3
"""Reproducible K00 source-span editorial triage, NOT an official atom denominator.

The copyright syllabus PDF is inspected ONLY on authorized Mac. Neither source
passages nor PDF pages are embedded in version control. The attested span hashes
come from local PDFKit-extracted plaintext lines. CI verifies the signed-off
*editorial snapshot*, but cannot claim it independently read the source PDF.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "curriculum/highschool_math"
OUT = ROOT / "docs/evaluation"
TSV = SRC / "k00_batch56_compulsory_source_spans.tsv"
SNAP = SRC / "k00_batch56_pdfkit_span_attestations.json"
PAGE = SRC / "k00_batch51_pdfkit_page_fingerprints.json"
OVERLAY = OUT / "KB_BATCH50_PROJECT_SCOPE_OVERLAY.json"
B54 = OUT / "KB_BATCH54_SCOPE_AND_DENOMINATOR_AUDIT.json"
B55 = OUT / "KB_BATCH55_CONFLICT_PROOF_REVIEW.json"
OUTPUT = OUT / "KB_BATCH56_COMPULSORY_SOURCE_SPAN_REVIEW.json"
REPORT = OUT / "KB_BATCH56_COMPULSORY_SOURCE_SPAN_REVIEW.md"
PDF_SHA = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A", "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")
KINDS = ("CONTENT", "OPTIONAL_STARRED", "TEACHING_GUIDANCE", "ACHIEVEMENT_REQUIREMENT")
EXPECT = {15:7,16:8,17:3,18:3,19:6,20:6,21:6,22:7,23:3,24:3}
SPANS = sum(EXPECT.values())

def require(ok,reason):
    if not ok:
        raise ValueError(reason)

def load(p):
    return json.loads(Path(p).read_text(encoding="utf8"))

def read_seeds():
    result=[]
    for raw in TSV.read_text(encoding="utf8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        pieces=raw.split("|")
        require(len(pieces)==7,"invalid original editorial TSV row")
        page,begin,end,kind,starred,goal,guard=pieces
        require(page.isdigit() and begin.isdigit() and end.isdigit(),"non-integer page/line")
        result.append({
            "printed_page":int(page),"line_start":int(begin),"line_end":int(end),
            "source_kind":kind,"starred_optional":starred=="Y",
            "original_editorial_paraphrase":goal,"safety_guard":guard,
            "_raw_starred":starred,
        })
    return result

def normalized_span(page_text,begin,end):
    lines=page_text.splitlines()
    require(1 <= begin <= end <= len(lines),"PDFKit source span out of range")
    return "\n".join(lines[begin-1:end])

def attest_source(*,source_dir,pdf_path,rows,pages):
    source_dir=Path(source_dir)
    pdf_path=Path(pdf_path)
    require(pdf_path.is_file() and sha256(pdf_path.read_bytes()).hexdigest()==PDF_SHA,
            "original official PDF absent or SHA mismatch")
    page_index={p["printed_page"]:p for p in pages["pages"]}
    # Validate every locked page, even if only 10 pages contain annotated spans.
    for page_num in range(13,74):
        target=source_dir / f"kb56_page_{page_num}.txt"
        require(target.is_file(),"missing local PDFKit page text")
        raw_page=target.read_bytes()  # PDFKit text may contain CR; do not normalize newlines before hash
        require(sha256(raw_page).hexdigest()==page_index[page_num]["pdfkit_text_sha256"],
                f"PDFKit page hash mismatch P{page_num}")
    records={}
    for r in rows:
        p=r["printed_page"]
        data=(source_dir/f"kb56_page_{p}.txt").read_text(encoding="utf8")
        key=f"P{p:03d}-L{r['line_start']:03d}-{r['line_end']:03d}"
        records[key]=sha256(normalized_span(data,r["line_start"],r["line_end"]).encode("utf8")).hexdigest()
    require(len(records)==len(rows),"duplicate source span location")
    return {
        "schema_version":"kb56-local-mac-pdfkit-span-hashes-v1",
        "pinned_pdf_sha256":PDF_SHA,
        "source_scan": "PDFKit verified full 61 pages on authorized Mac; only hashes committed",
        "source_passages_or_pdf_committed":False,
        "attestations":dict(sorted(records.items())),
    }

def build(*,seeds=None,pages=None,overlay=None,base54=None,base55=None,attestation=None):
    seeds=deepcopy(seeds if seeds is not None else read_seeds())
    pages=deepcopy(pages if pages is not None else load(PAGE))
    overlay=deepcopy(overlay if overlay is not None else load(OVERLAY))
    b54=deepcopy(base54 if base54 is not None else load(B54))
    b55=deepcopy(base55 if base55 is not None else load(B55))
    snap=deepcopy(attestation if attestation is not None else load(SNAP))
    require(pages["official_pdf_sha256"]==b54["source_pdf_sha256"]==PDF_SHA,
            "official source SHA drift")
    require(b54["official_source_pages"]==61 and len(pages["pages"])==61,
            "official 61-page source incomplete")
    require(set(p["printed_page"] for p in pages["pages"])==set(range(13,74)),
            "missing original syllabus page")
    require(overlay["summary"]["project_candidates"]==313,"project candidate count drift")
    require(overlay["summary"]["teacher_approved"]==0
            and overlay["summary"]["student_published"]==0,"approval forged")
    require(b55["frozen_unverified_proof_steps"]==538
            and b55["conflict_count"]==10 and b55["conflicts_resolved"]==0,
            "legacy mathematical risk inventory drift")
    require(b54["official_atomic_denominator"]=={k:None for k in TRACKS},
            "official atomic denominator falsely certified")
    require(b55["official_atomic_denominator"]=={k:None for k in TRACKS},
            "formal proof inventory promoted as curriculum denominator")
    require(snap["pinned_pdf_sha256"]==PDF_SHA
            and snap["source_passages_or_pdf_committed"] is False,
            "source snapshot provenance drift")
    require(len(seeds)==SPANS and len(snap["attestations"])==SPANS,
            "partial or fabricated source span inventory")
    page_lookup={p["printed_page"]:p for p in pages["pages"]}
    editable={}
    for row in overlay["rows"]:
        eid=row["editorial_id"]
        require(eid not in editable,"duplicate editorial ID")
        require(row["track"] in TRACKS and isinstance(row["printed_page"],int),"invalid existing editorial scope")
        require(not row["teacher_approved"] and not row["student_published"],
                "legacy editorial target falsely approved")
        editable[eid]=row
    require(len(editable)==313,"incomplete old editorial inventory")
    per_page={p:sorted(eid for eid,row in editable.items() if row["printed_page"]==p
                and row["track"]=="COMPULSORY") for p in EXPECT}
    observed=Counter()
    used=set()
    output=[]
    for row in seeds:
        p=row["printed_page"]; begin=row["line_start"]; end=row["line_end"]
        require(p in EXPECT and 1<=begin<=end<=100,"invalid source page or span")
        require(row["_raw_starred"] in ("Y","N"),"invalid optional input")
        kind=row["source_kind"]
        require(kind in KINDS,"invalid source kind")
        require(row["starred_optional"]==(kind=="OPTIONAL_STARRED"),"optional-star misclassified")
        require(kind!="OPTIONAL_STARRED" or p in (20,21),"starred source page mismatch")
        require(20<=len(row["original_editorial_paraphrase"])<=140,
                "insufficient or excessive original editorial statement")
        require(len(row["safety_guard"])>=8
                and re.fullmatch(r"[A-Z0-9_]+",row["safety_guard"]),
                "missing condition or assessment boundary")
        key=f"P{p:03d}-L{begin:03d}-{end:03d}"
        require(key not in used, "duplicate source span")
        used.add(key)
        digest=snap["attestations"].get(key)
        require(isinstance(digest,str) and re.fullmatch(r"[a-f0-9]{64}",digest),
                "missing trusted local PDFKit span attestation")
        page_data=page_lookup[p]
        require(page_data["pdf_page_index"]==p+7
                and page_data["full_page_human_review"]=="PENDING",
                "PDF index or source-page review status forged")
        require(re.fullmatch(r"[a-f0-9]{64}",page_data["pdfkit_text_sha256"]),
                "source page fingerprint missing")
        observed[p]+=1
        output.append({
            "candidate_id":"KB56-C-P%03d-S%03d"%(p,observed[p]),
            "source_span_id":key,"printed_page":p,"pdf_page_index":p+7,
            "source_pdf_sha256":PDF_SHA,
            "source_page_pdfkit_sha256":page_data["pdfkit_text_sha256"],
            "source_span_pdfkit_sha256":digest,
            "source_kind":kind,"starred_optional":row["starred_optional"],
            "exam_requirement_status":"EXPLICITLY_NOT_EXAM_REQUIREMENT" if kind=="OPTIONAL_STARRED"
                                      else "NOT_DETERMINED_BY_THIS_AUDIT",
            "original_editorial_paraphrase":row["original_editorial_paraphrase"],
            "mathematical_or_policy_guard":row["safety_guard"],
            "related_same_page_editorial_ids_not_equivalence":per_page[p],
            "related_lesson_math_equivalence_certified":False,
            "source_scope_review":"EDITORIAL_PDFKIT_SPAN_TRIAGE_NOT_TEACHER_CERTIFIED",
            "cross_page_deduplication":"PENDING",
            "official_atom_certified":False,
            "full_page_atomization_certified":False,
            "teacher_review":"REVIEW_PENDING","student_publishable":False,
            "formal_math_proof_certified":False,
        })
    require(dict(observed)==EXPECT,"full annotated page-span batch incomplete")
    require(set(snap["attestations"])==used,"unbound or missing source attestation")
    require(sum(r["source_kind"]=="OPTIONAL_STARRED" for r in output)==2,
            "starred no-exam distinction lost")
    by_kind=dict(sorted(Counter(r["source_kind"] for r in output).items()))
    return {
        "schema_version":"kb56-original-source-span-triage-v1",
        "status":"PARTIAL_EDITORIAL_SOURCE_SPAN_TRIAGE_NOT_OFFICIAL_ATOM_DENOMINATOR",
        "pinned_original_pdf_sha256":PDF_SHA,
        "source_pages_partially_annotated":sorted(EXPECT),
        "source_pages_total":61,
        "candidate_source_spans":len(output),
        "span_counts_by_printed_page":{str(p):observed[p] for p in sorted(observed)},
        "spans_by_kind":by_kind,
        "starred_not_exam_requirements":2,
        "school_achievement_or_pedagogic_spans_not_new_atoms":
            by_kind["ACHIEVEMENT_REQUIREMENT"]+by_kind["TEACHING_GUIDANCE"],
        "project_editorial_candidates_not_atoms":313,
        "historical_proof_steps_still_unverified":538,
        "mathematical_conflicts_still_open":10,
        "official_atomic_denominator":{k:None for k in TRACKS},
        "full_human_teacher_page_atomizations_completed":0,
        "source_passages_or_pdf_committed":False,
        "teacher_approved":0,"student_published":0,
        "note":"Mac PDFKit verified provenance. A bounded source span is neither a unique knowledge atom nor an approved lesson; optional starred readings are not exams. Full-page and cross-page human source review remains pending.",
        "rows":output,
    }

def report(data):
    s=[
      "# Batch56｜Mac PDFKit 十页课程来源精细定位与范围门禁",
      "",
      "源：教育部《普通高中数学课程标准（2017年版2020年修订）》；Mac原始PDF SHA256 "+
         f"`{PDF_SHA}`。不提交PDF或原文。",
      "",
      "**52条定位**属于可复核的原件片段与原创编辑解释，不能相加形成官方原子知识分母。",
      "此批逐行定位印刷第15–24页，包含内容要求、学业要求、教学提示与明确标星的选学内容。",
      "此外所有61页的指纹均在本地原件上校验；其他51页未获完整人工拆分或教师签署。",
      "",
      "| 类型 | 本批定位数量 | 能否进入官方必授原子分母 |",
      "|---|---:|---|",
    ]
    for kind,count in data["spans_by_kind"].items():
        s.append(f"| {kind} | {count} | 否：需要去重、拆分与教研签署 |")
    s.extend(["", "| 原课标印刷页 | 本批可重放片段 |", "|---:|---:|"])
    for page,count in data["span_counts_by_printed_page"].items():
        s.append(f"| {page} | {count} |")
    s.extend([
       "",
       "## 关键纠错与分类边界",
       "",
       "- 印刷19页脚注说明标星内容为选学、不作考试要求；20页函数史、21页对数史两条标星候选必须独立标记，不能作为全国考试必授项。",
       "- 印刷18及24页的学业要求，是跨知识的能力目标；它们可形成评测标准，但不可不经拆分去重直接计为新增数学概念或定理。",
       "- 印刷22页同角正切关系必须注明分母非零；二分法要区分存在零点与唯一性。",
       "- 同页既有编辑ID均仅供发现关联，不是范围等价或完整讲义审查证据。",
       "- 官方七轨知识原子分母全部仍为 null；教师批准与学生端正式发布均为0。",
       "",
       "## 可审核片段（不重印课标文字）",
       "",
    ])
    for r in data["rows"]:
        s.append(f"- `{r['candidate_id']}` 印刷P{r['printed_page']} / `{r['source_span_id']}`｜"
                 f"{r['source_kind']}｜{r['original_editorial_paraphrase']}｜条件/范围："
                 f"`{r['mathematical_or_policy_guard']}`｜状态 REVIEW_PENDING。")
    s.extend([
        "",
        "## 后续阻断",
        "",
        "逐页继续正式识别所有编号与非编号内容、学业要求和选学标识；对跨页同义项进行去重和强弱条件审校，"
        "建立完整课程原子索引并通过真实教师批准，才可以确定七轨正式分母与真实内容缺口。",
        "原文核验命令在Mac运行 `python scripts/build_kb_batch56_source_span_review.py --check "
        "--verify-source-pdf /private/tmp/stem-mentor-official-math-2020-batch51.pdf "
        "--source-dir /private/tmp`；GitHub CI只核验已承诺来源指纹与文档生成一致性，"
        "不得把CI说成独立阅读原PDF。",
    ])
    return "\n".join(s)+"\n"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    ap.add_argument("--verify-source-pdf",type=Path)
    ap.add_argument("--source-dir",type=Path)
    args=ap.parse_args()
    require((args.verify_source_pdf is None)==(args.source_dir is None),
            "source PDF and PDFKit text dir must be supplied together")
    seeds=read_seeds()
    if args.verify_source_pdf is not None:
        recomputed=attest_source(source_dir=args.source_dir,pdf_path=args.verify_source_pdf,
                                 rows=seeds,pages=load(PAGE))
        if args.check:
            require(load(SNAP)==recomputed,"source span digests drift from pinned original PDF")
        else:
            SNAP.write_text(json.dumps(recomputed,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
                            encoding="utf8")
    data=build()
    payload=json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    md=report(data)
    if args.check:
        require(OUTPUT.read_text(encoding="utf8")==payload,"source span JSON drift")
        require(REPORT.read_text(encoding="utf8")==md,"source span review report drift")
    else:
        OUTPUT.write_text(payload,encoding="utf8")
        REPORT.write_text(md,encoding="utf8")
    print(f"Batch56 original PDFKit span review: {len(data['rows'])} spans, "
          f"{len(data['source_pages_partially_annotated'])} pages, "
          f"{data['starred_not_exam_requirements']} optional-not-exam, "
          "official denominators unverified; check=",args.check)

if __name__=="__main__":
    main()
