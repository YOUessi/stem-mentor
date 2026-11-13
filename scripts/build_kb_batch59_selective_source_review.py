#!/usr/bin/env python3
"""Batch59 K00 independent original selective-compulsory source-span review.

Neither the copyright syllabus nor extracted text is committed. In CI the
versioned SHA attestations and editorial inventory are checked for consistency;
on the authorized Mac --verify-source-pdf independently checks original PDF,
all 61 cached PDFKit pages, and the exact source span SHA hashes.
These *partial source leads* are not certified curriculum atoms or equivalences.
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
CURR = ROOT / "curriculum/highschool_math"
EVAL = ROOT / "docs/evaluation"
SEED = CURR / "k00_batch59_selective_source_spans.tsv"
SNAP = CURR / "k00_batch59_pdfkit_span_attestations.json"
PAGE = CURR / "k00_batch51_pdfkit_page_fingerprints.json"
OLD = EVAL / "KB_BATCH57_SOURCE_SPAN_REVIEW.json"
COMP = EVAL / "KB_BATCH58_COMPETENCY_COVERAGE.json"
OVERLAY = EVAL / "KB_BATCH50_PROJECT_SCOPE_OVERLAY.json"
RISK = EVAL / "KB_BATCH55_CONFLICT_PROOF_REVIEW.json"
OUTPUT = EVAL / "KB_BATCH59_SELECTIVE_SOURCE_SPAN_REVIEW.json"
REPORT = EVAL / "KB_BATCH59_SELECTIVE_SOURCE_SPAN_REVIEW.md"
PDF_SHA = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
KINDS = ("CONTENT", "OPTIONAL_STARRED", "TEACHING_GUIDANCE",
         "ACHIEVEMENT_REQUIREMENT", "ACTIVITY_REQUIREMENT", "TRACK_BOUNDARY")
TRACKS = ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
          "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
EXPECTED_PAGES = set(range(37,51))
MAX_CLAUSE = 180


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_seeds():
    out = []
    for line in SEED.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cells = line.split("|")
        require(len(cells) == 7, "invalid source TSV column count")
        p, a, b, kind, starred, paraphrase, guard = cells
        require(p.isdecimal() and a.isdecimal() and b.isdecimal(),
                "source page/line must be integer")
        out.append({"printed_page":int(p),"line_start":int(a),"line_end":int(b),
                    "source_kind":kind,"optional_starred_flag":starred,
                    "original_editorial_paraphrase":paraphrase,
                    "mathematical_or_policy_guard":guard})
    return out


def span_key(row):
    return f"P{row['printed_page']:03d}-L{row['line_start']:03d}-{row['line_end']:03d}"


def source_attest(source_dir, pdf_path, seeds, pages):
    pdf_path, source_dir = Path(pdf_path), Path(source_dir)
    require(pdf_path.is_file() and sha256(pdf_path.read_bytes()).hexdigest() == PDF_SHA,
            "official PDF missing or changed SHA")
    by_page = {e["printed_page"]:e for e in pages["pages"]}
    require(set(by_page) == set(range(13,74)), "official 61-page inventory incomplete")
    lines_by_page = {}
    for page in range(13,74):
        file = source_dir / f"kb56_page_{page}.txt"
        require(file.is_file(), f"PDFKit page {page} missing")
        raw = file.read_bytes()
        require(sha256(raw).hexdigest() == by_page[page]["pdfkit_text_sha256"],
                f"PDFKit page {page} SHA mismatch")
        lines_by_page[page] = raw.decode("utf8").splitlines()
    attest = {}
    for row in seeds:
        key = span_key(row)
        p,a,b = row["printed_page"],row["line_start"],row["line_end"]
        require(p in EXPECTED_PAGES and 1<=a<=b<=len(lines_by_page[p]),
                "PDFKit source span outside page range")
        require(key not in attest, "duplicate span attestation")
        attest[key] = sha256("\n".join(lines_by_page[p][a-1:b]).encode("utf8")).hexdigest()
    return {
        "schema_version":"kb59-mac-pdfkit-sha-pointers-v1",
        "pinned_pdf_sha256":PDF_SHA,
        "source_passages_or_pdf_committed":False,
        "any_full_page_human_review_certified":False,
        "attestations":dict(sorted(attest.items()))
    }


def build(*, seeds=None, pages=None, old=None, comp=None,
          overlay=None, risk=None, snapshot=None):
    seeds = deepcopy(read_seeds() if seeds is None else seeds)
    pages = deepcopy(load(PAGE) if pages is None else pages)
    old = deepcopy(load(OLD) if old is None else old)
    comp = deepcopy(load(COMP) if comp is None else comp)
    overlay = deepcopy(load(OVERLAY) if overlay is None else overlay)
    risk = deepcopy(load(RISK) if risk is None else risk)
    snapshot = deepcopy(load(SNAP) if snapshot is None else snapshot)
    require(pages["official_pdf_sha256"]==PDF_SHA
            and set(x["printed_page"] for x in pages["pages"])==set(range(13,74))
            and len(pages["pages"])==61, "official PDF 61-page fingerprint drift")
    require(old["new_source_spans"]==78 and old["combined_nonunique_source_spans"]==130
            and old["pages_partially_annotated_combined"]==list(range(15,37)),
            "Batch57 130 pointer baseline drift")
    require(old["teacher_approved"]==old["student_published"]==0
            and all(x is None for x in old["official_atomic_denominator"].values()),
            "prior scope or approval incorrectly promoted")
    require(overlay["summary"]["project_candidates"]==313
            and overlay["summary"]["teacher_approved"]==overlay["summary"]["student_published"]==0
            and all(not x["teacher_approved"] and not x["student_published"] for x in overlay["rows"]),
            "project editorials: false teacher approval or count drift")
    require(risk["frozen_unverified_proof_steps"]==538 and risk["conflict_count"]==10
            and risk["conflicts_resolved"]==0, "unverified proof/conflict risk baseline changed")
    require(all(x is None for x in risk["official_atomic_denominator"].values()),
            "formal curriculum denominator invented")
    require(comp["teacher_approved"]==comp["student_published"]==0,
            "competency approval drift")
    require(snapshot["pinned_pdf_sha256"]==PDF_SHA
            and snapshot["source_passages_or_pdf_committed"] is False
            and snapshot["any_full_page_human_review_certified"] is False,
            "source attestation provenance forged")
    require(len(seeds)>=80 and len(seeds)==len(snapshot["attestations"]),
            "partial selective source inventory missing entries")
    page_index={x["printed_page"]:x for x in pages["pages"]}
    editorial=overlay["rows"]
    seen=set()
    rows=[]
    counts=Counter()
    for seed in seeds:
        p,a,b=seed["printed_page"],seed["line_start"],seed["line_end"]
        kind=seed["source_kind"]
        require(p in EXPECTED_PAGES and 1<=a<=b<=100, "selective page or lines invalid")
        require(kind in KINDS, "unsupported requirement category")
        require(seed["optional_starred_flag"] in ("Y","N"), "invalid starred flag")
        require((kind=="OPTIONAL_STARRED")==(seed["optional_starred_flag"]=="Y"),
                "starred optional mismatch")
        require(kind!="OPTIONAL_STARRED" or p in (38,40,44,47),
                "starred optional source location outside confirmed pages")
        require(kind!="TRACK_BOUNDARY" or (p,a,b)==(50,20,23),
                "elective track boundary cannot be moved")
        require(20<=len(seed["original_editorial_paraphrase"])<=MAX_CLAUSE
                and "\n" not in seed["original_editorial_paraphrase"],
                "incomplete original editorial paraphrase")
        require(bool(re.fullmatch(r"[A-Z0-9_]{8,84}",seed["mathematical_or_policy_guard"])),
                "missing mathematical or policy guard")
        key=span_key(seed)
        require(key not in seen, "duplicate source span")
        seen.add(key)
        digest=snapshot["attestations"].get(key)
        require(isinstance(digest,str) and re.fullmatch(r"[a-f0-9]{64}",digest),
                "missing source span attestation hash")
        page=page_index[p]
        require(page["pdf_page_index"]==p+7 and page["full_page_human_review"]=="PENDING",
                "false PDF page or teacher certification")
        require(bool(re.fullmatch(r"[a-f0-9]{64}",page["pdfkit_text_sha256"])),
                "PDFKit full page fingerprint missing")
        counts[p]+=1
        related=sorted(x["editorial_id"] for x in editorial
                       if x["printed_page"]==p and x["track"]=="SELECTIVE_COMPULSORY")
        rows.append({
            "candidate_id":f"KB59-C-P{p:03d}-S{counts[p]:03d}",
            "source_span_id":key,
            "printed_page":p,"pdf_page_index":p+7,
            "source_kind":kind,"track":"SELECTIVE_COMPULSORY",
            "starred_optional":kind=="OPTIONAL_STARRED",
            "source_pdf_sha256":PDF_SHA,
            "source_page_pdfkit_sha256":page["pdfkit_text_sha256"],
            "source_span_pdfkit_sha256":digest,
            "original_editorial_paraphrase":seed["original_editorial_paraphrase"],
            "mathematical_or_policy_guard":seed["mathematical_or_policy_guard"],
            "same_page_related_editorial_ids_not_equivalence":related,
            "exam_requirement_status":(
                "EXPLICITLY_OPTIONAL_NOT_EXAM" if kind=="OPTIONAL_STARRED" else
                "NON_CONTENT_REQUIREMENT_REQUIRES_SEPARATE_ASSESSMENT" if kind in
                ("TEACHING_GUIDANCE","ACHIEVEMENT_REQUIREMENT","ACTIVITY_REQUIREMENT") else
                "TRACK_BOUNDARY_NOT_AN_ATOM" if kind=="TRACK_BOUNDARY" else
                "REQUIRES_ATOMIC_SCOPE_DEDUP_REVIEW"),
            "requirement_coverage_status":"UNMAPPED" if kind in
                ("TEACHING_GUIDANCE","ACHIEVEMENT_REQUIREMENT","ACTIVITY_REQUIREMENT")
                else "NOT_APPLICABLE_TO_COMPETENCY_LEDGER",
            "full_page_human_review":"PENDING",
            "cross_page_mathematical_deduplication":"PENDING",
            "official_atom_certified":False,
            "mathematical_scope_equivalence_certified":False,
            "formal_general_proof_certified":False,
            "teacher_review":"REVIEW_PENDING",
            "student_publishable":False,
        })
    require(set(counts)==EXPECTED_PAGES, "missing selective-compulsory source page")
    require(seen==set(snapshot["attestations"]), "source hashes have orphan or missing rows")
    require(len([r for r in rows if r["source_kind"]=="TRACK_BOUNDARY"])==1,
            "elective track boundary must remain explicit")
    require(len([r for r in rows if r["starred_optional"]])==5,
            "five starred optional source positions must remain marked")
    competencies=[{"candidate_id":r["candidate_id"],
                    "source_span_id":r["source_span_id"],
                    "kind":r["source_kind"],
                    "coverage":"UNMAPPED",
                    "teacher_review":"REVIEW_PENDING",
                    "linked_approved_assessment_ids":[],
                    "not_a_certified_content_atom":True}
                  for r in rows if r["requirement_coverage_status"]=="UNMAPPED"]
    kinds=dict(sorted(Counter(x["source_kind"] for x in rows).items()))
    return {
        "schema_version":"kb59-partial-selective-source-evidence-v1",
        "status":"PARTIAL_PDFKIT_SOURCE_POINTERS_NO_OFFICIAL_ATOMIZATION",
        "official_pdf_sha256":PDF_SHA,
        "source_pages_total":61,
        "newly_partially_annotated_pages":sorted(EXPECTED_PAGES),
        "partially_annotated_pages_combined":list(range(15,51)),
        "previous_nonunique_source_spans":130,
        "new_nonunique_source_spans":len(rows),
        "combined_nonunique_source_spans":130+len(rows),
        "counts_per_page":{str(p):counts[p] for p in sorted(counts)},
        "counts_by_kind":kinds,
        "starred_optional_not_exam":5,
        "non_content_requirements_separately_unmapped":len(competencies),
        "project_editorial_candidates_not_official_atoms":313,
        "unverified_historical_proof_steps":538,
        "unresolved_math_conflicts":10,
        "official_atomic_denominator":{k:None for k in TRACKS},
        "full_teacher_reviewed_page_atomizations":0,
        "teacher_approved":0,
        "student_published":0,
        "source_passages_or_pdf_committed":False,
        "competency_requirement_queue":competencies,
        "rows":rows,
        "note":"Partial non-unique manual PDFKit source leads: not a unique official atom count; no cross-page mathematical equivalence or teacher approval."
    }


def render(data):
    lines=["# Batch59｜选择性必修来源审计：印刷37–50页", "",
           "仅在授权Mac通过锁定2020修订课标原PDF/PDFKit行区间做来源核对，仓库仅保存原创释义与SHA位置，不收录原文。",
           f"原始课标 SHA256：`{PDF_SHA}`。","",
           f"新增 **{data['new_nonunique_source_spans']} 条非去重来源位置**；合计 {data['combined_nonunique_source_spans']} 条；",
           "**不是正式课标原子分母、教师认证覆盖率或完整讲义数**。", "",
           "| 类别 | 数量 |","|---|---:|"]
    for kind,n in data["counts_by_kind"].items():
        lines.append(f"| {kind} | {n} |")
    lines.extend(["",f"非内容要求另列为 **{data['non_content_requirements_separately_unmapped']} 条UNMAPPED能力/教学/活动项**，没有认证量规映射。",
                  "带星内容只能列为可选：数学归纳法、微积分史、解析几何史、贝叶斯公式等五个来源位置，不能冒充考试必授。",
                  "P50选修A–E轨道边界已经标识，但本批没有审查这些选修轨的内部内容。",
                  "22页前置局部定位+14页本批局部定位=36/61页；尚有25页未做该系列定位；**0页完成教师全页原子化**。",
                  "538条历史证明步骤未形式认证、10组冲突未裁决；七轨分母仍null，正式教师批准0，学生发布0。","",
                  "## 逐页来源位置", "",
                  "| 印刷页 | 本批位置 |","|---:|---:|"])
    lines.extend(f"| {p} | {n} |" for p,n in data["counts_per_page"].items())
    lines.extend(["","## 逐条来源释义及前提",""])
    for r in data["rows"]:
        lines.append(f"- `{r['candidate_id']}` P{r['printed_page']} `{r['source_span_id']}` "
                     f"{r['source_kind']}：{r['original_editorial_paraphrase']} "
                     f"（前提 `{r['mathematical_or_policy_guard']}`；`REVIEW_PENDING`）。")
    lines.extend(["","## 机器重放与审核边界","",
      "CI: `python scripts/build_kb_batch59_selective_source_review.py --check`，核验版本化快照、前提及负面门禁。",
      "Mac PDFKit: `python scripts/build_kb_batch59_selective_source_review.py --check --verify-source-pdf /private/tmp/stem-mentor-official-math-2020-batch51.pdf --source-dir /private/tmp`。",
      "原PDF不入仓库、源图语义没有被自动读入；全量数学范围去重、未覆盖章节与教师审批继续阻断正式学生发布。",""])
    return "\n".join(lines)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    ap.add_argument("--verify-source-pdf",type=Path)
    ap.add_argument("--source-dir",type=Path)
    args=ap.parse_args()
    require((args.verify_source_pdf is None)==(args.source_dir is None),
            "original PDF and source directory must be paired")
    seeds=read_seeds()
    if args.verify_source_pdf:
        snap=source_attest(args.source_dir,args.verify_source_pdf,seeds,load(PAGE))
        if args.check:
            require(load(SNAP)==snap,"local PDFKit source attestation drift")
        else:
            SNAP.write_text(json.dumps(snap,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    data=build()
    expected_json=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    expected_md=render(data)
    if args.check:
        require(OUTPUT.read_text(encoding="utf8")==expected_json,"KB59 audit generation drift")
        require(REPORT.read_text(encoding="utf8")==expected_md,"KB59 readable review drift")
    else:
        OUTPUT.write_text(expected_json,encoding="utf8")
        REPORT.write_text(expected_md,encoding="utf8")
    print(f"KB59: {len(data['rows'])} nonunique pointers, {data['non_content_requirements_separately_unmapped']} requirements, 14 pages; seven denominators null")


if __name__=="__main__":
    main()
