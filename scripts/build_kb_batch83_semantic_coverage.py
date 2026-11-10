#!/usr/bin/env python3
"""Source-specific editorial review of 60 *additional* syllabus anchors.

Nothing here counts as a certified curriculum atom, an approved teacher lesson,
a general mathematical proof, or student-publishable instructional evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
import build_kb_batch81_semantic_triage as B81
from app.kb_batch83_math_relations import RELATIONS, finite_witnesses

AUTHOR = ROOT / "curriculum/highschool_math/kb_batch83_semantic_authoring.json"
OUT = ROOT / "docs/evaluation/KB_BATCH83_SEMANTIC_COVERAGE.json"
MD = ROOT / "docs/evaluation/KB_BATCH83_SEMANTIC_COVERAGE.md"
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A",
          "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")
ROLES = ("CURRICULUM_HEADING", "MIXED_CLAUSE", "MATHEMATICAL_REQUIREMENT",
         "COMPETENCY_REQUIREMENT", "APPLICATION_CONTEXT")
FIELDS = frozenset((
    "review_id", "track", "semantic_role_provisional", "original_editorial_paraphrase",
    "possible_math_units_for_teacher_split", "condition_or_scope_caution",
    "cross_track_equivalence", "teacher_confirmed", "official_atom_count",
    "student_publishable"
))
SOURCE_PDF_SHA = B81.PDF_SHA


def check(cond, reason):
    if not cond:
        raise ValueError(reason)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def build(auth=None, source=None, previous=None, verify_local_source=False):
    auth = load(AUTHOR) if auth is None else auth
    source = load(B81.SOURCE) if source is None else source
    previous = B81.build() if previous is None else previous
    check(auth.get("schema_version") == "kb83-60-source-semantic-editorial-proposals-v1"
          and auth.get("teacher_review") == "REVIEW_PENDING"
          and auth.get("source_lineage") == "SHA_VERIFIED_MAC_PDFKIT_SOURCE_FOR_SELECTED_ROWS"
          and auth.get("copyright_policy") == "ORIGINAL_PARAPHRASES_NO_SOURCE_PASSAGE",
          "authoring header or copyright/review policy invalid")
    check(source.get("source_pdf_sha256") == SOURCE_PDF_SHA
          and source.get("official_atom_denominator") is None
          and source.get("full_page_teacher_atomizations") == 0
          and source.get("officially_certified_atom_count") == 0
          and source.get("student_publishable_count") == 0,
          "frozen source state illegally promoted")
    check(sha256(B81.dump(source).encode("utf8")).hexdigest() == B81.SOURCE_QUEUE_SHA256,
          "frozen 428 anchor source queue modified")
    check(previous.get("schema_version") == "kb81-42-source-semantic-triage-v1"
          and previous.get("selected_independently_paraphrased_anchors") == 42
          and previous.get("remaining_without_manual_semantic_paraphrase") == 386
          and previous.get("teacher_approved") == 0
          and previous.get("official_curriculum_atom_denominator") is None,
          "previous editorial baseline invalid")
    previous_ids = {x["review_id"] for x in previous["rows"]}
    check(len(previous_ids) == 42, "previous 42 ids collided")
    queue = source["anchor_review_queue"]
    src = {row["review_id"]: row for row in queue}
    check(len(queue) == len(src) == 428, "source anchor inventory drift")
    expected = {}
    by_source = Counter(r["track"] for r in queue)
    for track in TRACKS[:-1]:
        remaining = [r["review_id"] for r in queue
                     if r["track"] == track and r["review_id"] not in previous_ids]
        check(len(remaining) >= 10, "too few source anchors in " + track)
        expected[track] = remaining[:10]
    check(by_source["ELECTIVE_E"] == 0, "elective E has unexpected sourced anchors")
    selected = {track: [] for track in TRACKS}
    rows = auth.get("records")
    check(type(rows) is list and len(rows) == 60, "expected 60 original editorial records")
    check(len({r.get("review_id") for r in rows if type(r) is dict}) == 60,
          "duplicate or malformed review identifiers")
    if verify_local_source:
        check(B81.LOCAL_PDF.is_file()
              and sha256(B81.LOCAL_PDF.read_bytes()).hexdigest() == SOURCE_PDF_SHA,
              "official source PDF unavailable or source hash drift")
        known_pages = {int(x["printed_page"]): x["pdfkit_text_sha256"]
                       for x in load(B81.PARTS)["pages"]}
    for row in rows:
        check(type(row) is dict and set(row) == FIELDS,
              "unauthorized, missing or concealed authoring fields")
        review_id = row["review_id"]
        check(review_id in src and review_id not in previous_ids,
              "unknown or duplicate prior reviewed source anchor")
        origin = src[review_id]
        track = row["track"]
        check(track in TRACKS[:-1] and origin["track"] == track,
              "source anchor cross-track classification invalid")
        selected[track].append(review_id)
        role = row["semantic_role_provisional"]
        check(role in ROLES, "unrecognized semantic role")
        kind = origin["kind"]
        check(not (kind == "MAJOR_NUMBER" and role != "CURRICULUM_HEADING")
              and not (kind == "CIRCLED_ITEM" and role == "CURRICULUM_HEADING"),
              "source structure contradicts editorial role")
        cs = row["possible_math_units_for_teacher_split"]
        check(type(cs) is list and len(cs) == len(set(cs))
              and len(cs) <= 5 and all(type(s) is str and len(s) >= 6 for s in cs),
              "invalid or duplicate provisional math units")
        check((role == "CURRICULUM_HEADING" and len(cs) == 0)
              or (role in ("MIXED_CLAUSE", "MATHEMATICAL_REQUIREMENT") and len(cs) >= 1)
              or (role in ("COMPETENCY_REQUIREMENT", "APPLICATION_CONTEXT")),
              "source role mathematical split missing or heading inflated")
        check(type(row["original_editorial_paraphrase"]) is str
              and len(row["original_editorial_paraphrase"]) >= 20
              and type(row["condition_or_scope_caution"]) is str
              and len(row["condition_or_scope_caution"]) >= 7,
              "missing original specific paraphrase or boundary concern")
        check(row["cross_track_equivalence"] == "NOT_ADJUDICATED"
              and row["teacher_confirmed"] is False
              and row["official_atom_count"] is None
              and row["student_publishable"] is False,
              "false teacher certification, syllabus denominator or publication")
        if verify_local_source:
            page = origin["printed_page"]
            line = origin["pdfkit_line"]
            local = B81.LOCAL_LINES / f"kb56_page_{page}.txt"
            check(local.exists() and page in known_pages, "source PDFKit page missing")
            raw = local.read_bytes()
            check(sha256(raw).hexdigest() == known_pages[page]
                  and known_pages[page] == origin["source_page_pdfkit_sha256"],
                  "PDFKit page text hash mismatch")
            lines = raw.decode("utf-8").splitlines()
            check(1 <= line <= len(lines)
                  and sha256(lines[line-1].encode("utf-8")).hexdigest()
                      == origin["source_line_sha256"],
                  "PDFKit anchored source line mismatch")
    for track in TRACKS[:-1]:
        check(selected[track] == expected[track],
              "source-specific 10-record selection changed: " + track)
    witnesses = finite_witnesses()
    all_ids = previous_ids | {r["review_id"] for r in rows}
    check(len(witnesses) == len(RELATIONS) == 5
          and {w["op"] for w in witnesses} == {r[0] for r in RELATIONS},
          "missing finite mathematical differentiation witnesses")
    for w, (op, left, right) in zip(witnesses, RELATIONS):
        check(w["op"] == op and w["left_anchor"] == left
              and w["right_anchor"] == right
              and left in all_ids and right in all_ids
              and w["general_equivalence_certified"] is False
              and w["teacher_approved"] is False
              and w["evidence_scope"] == "FINITE_EXACT_COUNTEREXAMPLE_ONLY",
              "cross-topic relation forged or orphaned")
    compiled = []
    for r in rows:
        origin = src[r["review_id"]]
        compiled.append({
            **r,
            "source_pdf_sha256": SOURCE_PDF_SHA,
            "source_page_pdfkit_sha256": origin["source_page_pdfkit_sha256"],
            "source_line_sha256": origin["source_line_sha256"],
            "source_parent_segment": origin["parent_segment"],
            "source_kind": origin["kind"],
            "printed_page": origin["printed_page"],
            "pdfkit_line": origin["pdfkit_line"],
            "review_status": "REVIEW_PENDING",
            "teacher_approved": False,
            "editorial_paraphrase_completed": True,
            "math_certification": "NOT_FORMALLY_VERIFIED",
            "student_authoritative_index_eligible": False,
        })
    previous_tracks = Counter(x["track"] for x in previous["rows"])
    fresh_tracks = Counter(x["track"] for x in compiled)
    by_track = {}
    for track in TRACKS:
        total = by_source[track]
        authored = previous_tracks[track] + fresh_tracks[track]
        check(authored <= total, "source count overshot")
        by_track[track] = {
            "source_review_anchor_denominator": total,
            "editorially_paraphrased_source_anchors": authored,
            "without_original_semantic_paraphrase": total - authored,
            "official_mathematical_atom_denominator": None,
            "teacher_full_page_atomization": 0,
            "student_approved_math_atoms": 0,
        }
    check(sum(x["editorially_paraphrased_source_anchors"] for x in by_track.values()) == 102
          and sum(x["without_original_semantic_paraphrase"] for x in by_track.values()) == 326,
          "K00 source editorial denominators not conserved")
    return {
        "schema_version": "kb83-102-of-428-source-editorial-proposals-v1",
        "source_pdf_sha256": SOURCE_PDF_SHA,
        "source_queue_sha256": B81.SOURCE_QUEUE_SHA256,
        "authoring_file_sha256": sha256(AUTHOR.read_bytes()).hexdigest(),
        "source_anchor_denominator": 428,
        "previous_editorial_reviews": 42,
        "new_editorial_reviews": 60,
        "cumulative_editorial_reviews": 102,
        "not_editorially_reviewed": 326,
        "source_review_complete_fraction": "102/428",
        "official_curriculum_atom_denominator": None,
        "teacher_full_page_atomizations": 0,
        "teacher_approved": 0,
        "student_deep_content_published": 0,
        "by_track": by_track,
        "new_by_role": dict(sorted(Counter(r["semantic_role_provisional"] for r in rows).items())),
        "new_candidate_splits_not_deduplicated":
             sum(len(r["possible_math_units_for_teacher_split"]) for r in rows),
        "mathematics_finite_non_equivalence_witnesses": witnesses,
        "new_rows": compiled,
        "all_mathematics_and_editorial_statuses_unapproved": True,
    }


def markdown(data):
    a = [
        "# Batch83｜60份新增课标来源语义分诊与5种数学边界精确反例", "",
        "**102/428为项目级来源行语义分诊，不是官方高中数学知识原子覆盖。**",
        "本批只在Mac使用授权PDFKit原始页行核对，仓库不保存受版权保护的课标全文。",
        "正式课程原子分母仍为未知；真实教师逐页审核0/61，批准0，学生深度发布0。", "",
        "| 课程轨道 | 来源审核义务 | 累计原创语义审查 | 待审来源锚点 | 官方数学原子分母 |",
        "|---|---:|---:|---:|---|",
    ]
    for t, v in data["by_track"].items():
        a.append(f'| {t} | {v["source_review_anchor_denominator"]} | '
                 f'{v["editorially_paraphrased_source_anchors"]} | '
                 f'{v["without_original_semantic_paraphrase"]} | UNKNOWN |')
    a += ["", "原文结构标题不会直接生成数学知识原子；能力/建模目标不等同于一般命题。",
          "有限见证只检查列出的有理数计算；没有认证一般等价或定理。", "",
          "| 有界精确反例 | 独立区别 |",
          "|---|---|"]
    for w in data["mathematics_finite_non_equivalence_witnesses"]:
        a.append(f'| {w["op"]} | {w["distinction"]} |')
    a += ["", f'新增原始语义单元：{data["new_editorial_reviews"]}；未归并主题候选：'
          f'{data["new_candidate_splits_not_deduplicated"]}；有待分诊来源锚点：'
          f'{data["not_editorially_reviewed"]}。', ""]
    return "\n".join(a)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-local-source", action="store_true")
    args = parser.parse_args()
    result = build(verify_local_source=args.verify_local_source)
    for path, content in ((OUT, dump(result)), (MD, markdown(result))):
        if args.check:
            check(path.exists() and path.read_text(encoding="utf8") == content,
                  "generated source coverage artifact drift: " + str(path))
        else:
            path.write_text(content, encoding="utf8")
    print("Batch83: 60 new / 102 cumulative / 428 source anchors; 5 exact finite "
          "distinctions; 0 official atoms or human teacher approvals")


if __name__ == "__main__":
    main()
