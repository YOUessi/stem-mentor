#!/usr/bin/env python3
"""Batch84: 67 source-specific editorial judgements, no official atom certification.

Frozen Mac PDF and extracted PDFKit lines are verified only with explicit
--verify-local-source. CI never needs copyrighted primary source bytes.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import build_kb_batch83_semantic_coverage as B83

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = ROOT / "curriculum/highschool_math/kb_batch84_semantic_authoring.json"
OUT = ROOT / "docs/evaluation/KB_BATCH84_SEMANTIC_COVERAGE.json"
MD = ROOT / "docs/evaluation/KB_BATCH84_SEMANTIC_COVERAGE.md"
TRACK_COUNTS = {"COMPULSORY": 20, "SELECTIVE_COMPULSORY": 15,
                "ELECTIVE_A": 10, "ELECTIVE_B": 10, "ELECTIVE_C": 12,
                "ELECTIVE_D": 0, "ELECTIVE_E": 0}
FIELDS = B83.FIELDS

def require(ok, why):
    if not ok:
        raise ValueError(why)

def load(path):
    return json.loads(path.read_text(encoding="utf8"))

def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

def build(auth=None, source=None, previous=None, verify_local_source=False):
    auth = load(AUTHOR) if auth is None else auth
    source = load(B83.B81.SOURCE) if source is None else source
    previous = B83.build() if previous is None else previous
    require(type(auth) is dict and set(auth) == {
        "schema_version", "standard_version", "source_lineage", "copyright_policy",
        "teacher_review", "records"}, "unrecognized authoring schema")
    require(auth["schema_version"] == "kb84-67-source-specific-editorial-v1"
            and auth["source_lineage"] == "MAC_PDFKIT_SHA_VERIFIED_ORIGINAL_SOURCE"
            and auth["copyright_policy"] == "ORIGINAL_PARAPHRASES_NO_SOURCE_PASSAGE"
            and auth["teacher_review"] == "REVIEW_PENDING"
            and auth["standard_version"] ==
                 "普通高中数学课程标准（2017年版2020年修订）",
            "source copyright or approval gate")
    require(source.get("source_pdf_sha256") == B83.SOURCE_PDF_SHA
            and source.get("official_atom_denominator") is None
            and source.get("full_page_teacher_atomizations") == 0
            and source.get("officially_certified_atom_count") == 0
            and source.get("student_publishable_count") == 0
            and sha256(B83.B81.dump(source).encode()).hexdigest() ==
                B83.B81.SOURCE_QUEUE_SHA256,
            "frozen source lineage or teacher-state spoofing")
    require(previous.get("schema_version") ==
                "kb83-102-of-428-source-editorial-proposals-v1"
            and previous.get("cumulative_editorial_reviews") == 102
            and previous.get("teacher_approved") == 0
            and previous.get("official_curriculum_atom_denominator") is None
            and previous.get("student_deep_content_published") == 0,
            "prior review baseline changed")
    rows = auth["records"]
    require(type(rows) is list and len(rows) == sum(TRACK_COUNTS.values()),
            "new editorial row count drift")
    require(all(type(r) is dict and set(r) == FIELDS for r in rows),
            "missing or forbidden review-status fields")
    require(len({r["review_id"] for r in rows}) == len(rows),
            "duplicate source anchor")
    prior_ids = {r["review_id"] for r in B83.B81.build()["rows"]}
    prior_ids.update(r["review_id"] for r in B83.load(B83.AUTHOR)["records"])
    require(len(prior_ids) == 102, "previous source anchor count drift")
    queue = source["anchor_review_queue"]
    src = {row["review_id"]: row for row in queue}
    require(len(src) == len(queue) == 428, "frozen source anchor collision")
    expected = {tr: [r["review_id"] for r in queue
                     if r["track"] == tr and r["review_id"] not in prior_ids][:n]
                for tr, n in TRACK_COUNTS.items()}
    bynew = {tr: [] for tr in TRACK_COUNTS}
    if verify_local_source:
        require(B83.B81.LOCAL_PDF.is_file() and sha256(B83.B81.LOCAL_PDF.read_bytes()).hexdigest()
                == B83.SOURCE_PDF_SHA, "Mac original PDF unavailable or SHA changed")
        page_sha = {int(p["printed_page"]): p["pdfkit_text_sha256"]
                    for p in load(B83.B81.PARTS)["pages"]}
    compiled = []
    for r in rows:
        rid, tr = r["review_id"], r["track"]
        require(rid in src and rid not in prior_ids
                and tr in TRACK_COUNTS and src[rid]["track"] == tr,
                "orphan source id, prior review duplicate or track spoofing")
        bynew[tr].append(rid)
        origin = src[rid]
        role = r["semantic_role_provisional"]
        require(role in B83.ROLES, "unknown semantic role")
        require(not(origin["kind"] == "MAJOR_NUMBER"
                    and role != "CURRICULUM_HEADING")
                and not (origin["kind"] == "CIRCLED_ITEM"
                         and role == "CURRICULUM_HEADING"),
                "source structure role mismatch")
        candidate = r["possible_math_units_for_teacher_split"]
        require(type(candidate) is list and len(candidate) <= 5
                and all(type(s) is str and len(s) >= 6 for s in candidate)
                and len(candidate) == len(set(candidate)),
                "invalid math candidates")
        require((role == "CURRICULUM_HEADING" and not candidate)
                or (role in ("MIXED_CLAUSE", "MATHEMATICAL_REQUIREMENT")
                    and bool(candidate))
                or (role in ("COMPETENCY_REQUIREMENT", "APPLICATION_CONTEXT")),
                "heading falsely counted or math goal without candidate")
        require(type(r["original_editorial_paraphrase"]) is str
                and len(r["original_editorial_paraphrase"]) >= 20
                and type(r["condition_or_scope_caution"]) is str
                and len(r["condition_or_scope_caution"]) >= 7,
                "thin or absent math/source-specific boundary explanation")
        require(r["cross_track_equivalence"] == "NOT_ADJUDICATED"
                and r["teacher_confirmed"] is False
                and r["student_publishable"] is False
                and r["official_atom_count"] is None,
                "false editorial approval or atom count")
        if verify_local_source:
            page, line = origin["printed_page"], origin["pdfkit_line"]
            target = B83.B81.LOCAL_LINES / f"kb56_page_{page}.txt"
            require(target.exists() and page in page_sha, "original PDFKit page missing")
            raw = target.read_bytes()
            require(sha256(raw).hexdigest() ==
                    origin["source_page_pdfkit_sha256"] == page_sha[page],
                    "source page SHA verification failed")
            split = raw.decode("utf8").splitlines()
            require(1 <= line <= len(split) and
                    sha256(split[line-1].encode("utf8")).hexdigest() ==
                    origin["source_line_sha256"],
                    "source line SHA verification failed")
        compiled.append({
            **r, "source_pdf_sha256": B83.SOURCE_PDF_SHA,
            "source_page_pdfkit_sha256": origin["source_page_pdfkit_sha256"],
            "source_line_sha256": origin["source_line_sha256"],
            "printed_page": origin["printed_page"], "pdfkit_line": origin["pdfkit_line"],
            "source_kind": origin["kind"], "source_parent_segment": origin["parent_segment"],
            "review_status": "REVIEW_PENDING", "teacher_approved": False,
            "math_certification": "NOT_FORMALLY_VERIFIED",
            "student_authoritative_index_eligible": False,
        })
    for tr, expected_ids in expected.items():
        require(bynew[tr] == expected_ids, "non-source-specific selection drift: " + tr)
    by_source = Counter(x["track"] for x in queue)
    by_prior = {tr: previous["by_track"][tr]["editorially_paraphrased_source_anchors"]
                for tr in TRACK_COUNTS}
    bytrack = {
        tr: {"source_review_anchor_denominator": by_source[tr],
             "editorially_paraphrased_source_anchors": by_prior[tr] + len(bynew[tr]),
             "without_original_semantic_paraphrase": by_source[tr] - by_prior[tr] - len(bynew[tr]),
             "official_mathematical_atom_denominator": None,
             "teacher_full_page_atomization": 0,
             "student_approved_math_atoms": 0}
        for tr in TRACK_COUNTS
    }
    require(sum(x["source_review_anchor_denominator"] for x in bytrack.values()) == 428
            and sum(x["editorially_paraphrased_source_anchors"] for x in bytrack.values()) == 169
            and sum(x["without_original_semantic_paraphrase"] for x in bytrack.values()) == 259,
            "K00 coverage conservation failure")
    return {
        "schema_version": "kb84-169-of-428-source-editorial-proposals-v1",
        "standard_version": auth["standard_version"],
        "source_pdf_sha256": B83.SOURCE_PDF_SHA,
        "source_queue_sha256": B83.B81.SOURCE_QUEUE_SHA256,
        "author_sha256": sha256(dump(auth).encode()).hexdigest(),
        "source_review_denominator": 428,
        "previous_editorial_count": 102, "new_editorial_count": 67,
        "cumulative_editorial_count": 169, "pending_editorial_count": 259,
        "candidate_splits_not_deduplicated": sum(len(r["possible_math_units_for_teacher_split"]) for r in rows),
        "official_curriculum_atom_denominator": None,
        "full_page_teacher_reviews": 0, "teacher_approved": 0,
        "student_deep_content_published": 0, "by_track": bytrack,
        "new_by_role": dict(Counter(r["semantic_role_provisional"] for r in rows)),
        "new_rows": compiled,
        "student_index_includes_unreviewed_material": False,
    }

def markdown(d):
    lines = [
        "# Batch84｜67条课标原始来源语义审查（仅项目内部）", "",
        "**169/428是已编辑解释的来源锚点，不是官方知识原子覆盖率，更不是169篇讲义。**",
        "来源于Mac本地原始课标及逐行PDFKit SHA核对；不复制有版权的原文。",
        "官方原子分母仍未知；教师全页审核0/61、教师批准0、学生正式深度发布0。", "",
        "| 轨道 | 来源锚点 | 已作项目编辑解释 | 未作逐行编辑解释 | 课程知识原子分母 |",
        "|---|---:|---:|---:|---|"]
    for tr, v in d["by_track"].items():
        lines.append(f'| {tr} | {v["source_review_anchor_denominator"]} | '
                     f'{v["editorially_paraphrased_source_anchors"]} | '
                     f'{v["without_original_semantic_paraphrase"]} | 未知 |')
    lines.extend(["", f'本批新增 {d["new_editorial_count"]} 份具名来源编辑稿；'
                  f'未去重候选 {d["candidate_splits_not_deduplicated"]} 项。',
                  "", "标题/能力/应用情境不会自动变成定理；所有跨轨数学等价和教师认证均为待定。",
                  "", "## 本批来源行与语义分工",
                  "| 原始来源锚点 | 轨道 | 类型 | 原创简述 | 前提风险 |",
                  "|---|---|---|---|---|"])
    for r in d["new_rows"]:
        lines.append(f'| {r["review_id"]} | {r["track"]} | {r["semantic_role_provisional"]} | '
                     f'{r["original_editorial_paraphrase"]} | {r["condition_or_scope_caution"]} |')
    return "\n".join(lines) + "\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-source",action="store_true")
    a=p.parse_args()
    d=build(verify_local_source=a.verify_local_source)
    for path, val in ((OUT,dump(d)),(MD,markdown(d))):
        if a.check:
            require(path.is_file() and path.read_text(encoding="utf8")==val,
                    "generated coverage artifact drift: "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(val,encoding="utf8")
    print("Batch84: 67 new / 169 cumulative / 428 source anchors; 259 pending; official atom total unknown")

if __name__=="__main__":
    main()
