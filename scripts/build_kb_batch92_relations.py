#!/usr/bin/env python3
"""Batch92 source-locked, editor-only mathematical topic relation audit.

The 300 old provisional source topics are NOT the official curricular atom
denominator; no auto-merging, teacher approval or student release is permitted.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "scripts")]
from app.kb_batch92_exact_witness import check_all
import build_kb_batch90_relations as B90
import build_kb_batch89_proofs_and_scope as B89

AUTHOR = ROOT / "curriculum/highschool_math/kb_batch92_relations_authoring.json"
OUT = ROOT / "docs/evaluation/KB_BATCH92_SOURCE_RELATIONS.json"
DOC = ROOT / "docs/evaluation/KB_BATCH92_SOURCE_RELATIONS.md"
SCHEMA = "kb92-24-math-relation-proposals-v1"
ROOT_KEYS = {"schema_version", "standard_version", "authorship", "authority",
             "teacher_approved", "semantic_equivalence_certified",
             "student_publishable", "relations"}
ROW_KEYS = {"review_id", "left_candidate_id", "right_candidate_id",
            "relation_proposal", "shared_maths", "distinguishing_conditions",
            "worked_witness", "failure_or_boundary", "review_status",
            "teacher_approved", "math_equivalence_certified",
            "student_publishable", "final_atom_id"}
TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A",
          "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_duplicate_json_keys(pairs):
    d = {}
    for key, value in pairs:
        require(key not in d, "duplicate JSON key " + key)
        d[key] = value
    return d


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=no_duplicate_json_keys)


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def build(raw=None, earlier=None, historical=None):
    raw = read(AUTHOR) if raw is None else raw
    earlier = B90.build() if earlier is None else earlier
    historical = B89.build()[1] if historical is None else historical
    require(type(raw) is dict and set(raw) == ROOT_KEYS, "authoring schema")
    require(raw["schema_version"] == SCHEMA and
            raw["standard_version"] == "普通高中数学课程标准（2017年版2020年修订）" and
            raw["authorship"] == "ORIGINAL_PROJECT_MATH_EDITORIAL_ON_MAC" and
            raw["authority"] == "EDITOR_ONLY_NOT_TEACHER" and
            raw["teacher_approved"] is False and
            raw["semantic_equivalence_certified"] is False and
            raw["student_publishable"] is False, "forged authoring authority")
    require(earlier["source_anchor_editorials"] == 428 and
            earlier["provisional_candidate_total"] == 300 and
            earlier["cumulative_editorial_pairs"] == 60 and
            earlier["cumulative_candidate_id_coverage"] == 118 and
            earlier["remaining_candidate_ids_without_any_relation"] == 182 and
            earlier["official_curriculum_atom_denominator"] is None and
            earlier["teacher_approved"] == 0 and earlier["student_published"] == 0 and
            earlier["math_equivalence_teacher_adjudications"] == 0,
            "previous K00 scope or authority drift")
    require(historical["provisional_labels"] == 300 and
            historical["official_atom_denominator"] is None and
            historical["teacher_approved"] == 0 and historical["student_published"] == 0,
            "historical scope falsely certified")
    require(type(raw["relations"]) is list and len(raw["relations"]) == 24,
            "all 24 substantial original relation records required")
    candidates = {r["candidate_id"]: r
                  for r in historical["provisional_candidate_backlog"]}
    require(len(candidates) == 300, "historical source candidate count")
    unpaired = set(earlier["remaining_unpaired_candidate_ids"])
    require(len(unpaired) == 182, "incomplete previous unmatched list")
    finite = check_all()
    require(len(finite) == 16, "exact limited-witness coverage drift")

    touched, seen_edges, reviews, types = set(), set(), [], Counter()
    for i, row in enumerate(raw["relations"], start=1):
        require(type(row) is dict and set(row) == ROW_KEYS, "relation field schema")
        require(row["review_id"] == f"KB92-REL-{i:03d}", "relation id sequence")
        require(row["relation_proposal"] in ("POSSIBLE_OVERLAP", "RELATED_DISTINCT"),
                "unsupported relation judgment")
        require(row["review_status"] == "REVIEW_PENDING" and
                row["teacher_approved"] is False and
                row["math_equivalence_certified"] is False and
                row["student_publishable"] is False and
                row["final_atom_id"] is None,
                "fake approval, release, or atom merge")
        for name, limit in (("shared_maths", 25), ("distinguishing_conditions", 34),
                            ("worked_witness", 25), ("failure_or_boundary", 25)):
            require(type(row[name]) is str and len(row[name].strip()) >= limit,
                    "math text is missing/too short: " + name)
        left, right = row["left_candidate_id"], row["right_candidate_id"]
        require(type(left) is str and type(right) is str and
                left != right and left in unpaired and right in unpaired,
                "pair must use two distinct previously-unpaired source topics")
        edge = tuple(sorted((left, right)))
        require(edge not in seen_edges and left not in touched and right not in touched,
                "duplicate/swapped pair or reused candidate")
        seen_edges.add(edge)
        touched.update((left, right))
        for k in (left, right):
            source = candidates[k]
            require(source["relation_count"] == 0 and
                    source["cross_track_status"] == "NOT_YET_COMPARED" and
                    source["official_math_atom_id"] is None and
                    source["teacher_approval"] is None and
                    source["student_authoritative_index_eligible"] is False and
                    type(source["source_line_sha256"]) is str and
                    len(source["source_line_sha256"]) == 64,
                    "untrusted/modified original source provenance")
        types[row["relation_proposal"]] += 1
        def source_min(k):
            source = candidates[k]
            return {f: source[f] for f in ("candidate_id", "track",
                "provisional_topic", "source_review_id", "source_line_sha256",
                "source_page")}
        reviews.append({**row,
            "left_source": source_min(left), "right_source": source_min(right),
            "finite_verification": finite.get(row["review_id"],
                {"status": "NOT_AUTOMATICALLY_VERIFIED",
                 "evidence_scope": "UNVERIFIED_EDITORIAL_WITNESS"}),
            "student_authoritative_index_eligible": False,
            "official_atom_adjudication": "NOT_PERFORMED",
            "teacher_review": None,
            "source_sha_scope": "PDFKIT_ORIGINAL_LINE_SHA256"})
    require(len(touched) == 48 and len(seen_edges) == 24,
            "all 48 independent topics need editorial audit")
    require(types["POSSIBLE_OVERLAP"] == 3 and types["RELATED_DISTINCT"] == 21,
            "relationship claims drift")
    cross = sum(r["left_source"]["track"] != r["right_source"]["track"]
                for r in reviews)
    require(cross >= 4, "need meaningful cross-track review examples")
    bytrack = Counter(r["track"] for r in candidates.values())
    old = set(candidates) - unpaired
    remaining = sorted(unpaired - touched)
    require(len(old) == 118 and len(remaining) == 134,
            "incorrect coverage after newly paired topics")
    per_track = {}
    for track in TRACKS:
        prev = sum(candidates[k]["track"] == track for k in old)
        added = sum(candidates[k]["track"] == track for k in touched)
        total = bytrack[track]
        per_track[track] = {
            "provisional_topics": total, "prior_reviewed": prev,
            "newly_reviewed": added, "cumulative_reviewed": prev + added,
            "still_without_relations": total - prev - added,
            "official_curriculum_atom_denominator": None,
            "teacher_approved": 0}
    require(sum(v["still_without_relations"] for v in per_track.values()) == 134,
            "per-track denominator inconsistency")
    return {
        "schema_version": "kb92-source-locked-math-topic-audit-v1",
        "standard_version": raw["standard_version"],
        "author_sha256": sha256(AUTHOR.read_bytes()).hexdigest(),
        "upstream_source_sha256": sha256(B90.OUT.read_bytes()).hexdigest(),
        "source_anchor_count": 428, "provisional_topics": 300,
        "previous_relation_pairs": 60, "new_relation_pairs": 24,
        "cumulative_relation_pairs": 84,
        "previously_reviewed_provisional_topics": 118,
        "newly_reviewed_provisional_topics": 48,
        "cumulative_reviewed_provisional_topics": 166,
        "remaining_unpaired_provisional_topics": 134,
        "remaining_unpaired_candidate_ids": remaining,
        "cross_track_pairs": cross, "relation_types": dict(types),
        "independently_checked_finite_witnesses": len(finite),
        "original_editorial_only_witnesses": 24-len(finite),
        "relation_reviews": reviews, "per_track": per_track,
        "official_curriculum_atom_denominator": None,
        "official_atom_denominators_by_track": {k: None for k in TRACKS},
        "full_page_teacher_atomization_reviews": 0,
        "teacher_adjudicated_atom_merges": 0,
        "teacher_approved": 0, "student_authoritative_release": 0,
        "general_theorem_proof_certificates": 0,
        "historical_uncertified_proof_steps": 538,
        "historical_P0_unreviewed_proof_steps": 106,
        "unresolved_math_conflicts": 10,
        "review_status": "REVIEW_PENDING",
        "student_solution_access": "NO_UNREVIEWED_EDUCATIONAL_FACTS_OR_TEACHER_SOLUTIONS"
    }


def markdown(data):
    L = [
        "# Batch92｜24组课标候选数学关系原创审查（编辑草案）", "",
        "**这不是正式课标原子化结果。** 本批24组、48个此前完全未比较的来源候选，"
        f"其中跨轨{data['cross_track_pairs']}组。全部保留REVIEW_PENDING。", "",
        "追溯：428个来源锚点 / 300个项目临时主题；总关系数84组，"
        "不同被比较主题166/300，剩余134。**官方七轨知识原子分母仍未知。**", "",
        "此前Batch91的20份深度讲义同样不是这300个主题的正式全覆盖；"
        "不能把48项关系审查计作48份新增讲义。", "",
        "真实教师全页审核0/61；538历史推理步骤未形式认证，"
        "106个历史P0源步骤缺审稿卡，10组冲突未裁决。", "",
        "|轨道|临时主题|此前已比较|新增比较|累计比较|仍未比较|正式原子分母|",
        "|---|---:|---:|---:|---:|---:|---|"
    ]
    for k,v in data["per_track"].items():
        L.append(f"|{k}|{v['provisional_topics']}|{v['prior_reviewed']}|"
                 f"{v['newly_reviewed']}|{v['cumulative_reviewed']}|"
                 f"{v['still_without_relations']}|未知|")
    for r in data["relation_reviews"]:
        L += ["", f"## {r['review_id']}｜{r['left_source']['provisional_topic']} "
              f"vs {r['right_source']['provisional_topic']}", "",
              f"**关系编辑判断：**{r['relation_proposal']}（禁止自动合并/认证）", "",
              f"**来源左：**{r['left_candidate_id']} / "
              f"{r['left_source']['track']} / 第{r['left_source']['source_page']}页 / "
              f"行SHA {r['left_source']['source_line_sha256']}", "",
              f"**来源右：**{r['right_candidate_id']} / "
              f"{r['right_source']['track']} / 第{r['right_source']['source_page']}页 / "
              f"行SHA {r['right_source']['source_line_sha256']}", "",
              "**共同数学结构：**" + r["shared_maths"], "",
              "**关键假设/区别：**" + r["distinguishing_conditions"], "",
              "**原创示例：**" + r["worked_witness"], "",
              "**前提失效/反例：**" + r["failure_or_boundary"], "",
              "**受控独立检查：**" +
              r["finite_verification"]["status"] +
              "（不能推广为一般命题证明）", ""]
    L += ["## 后续质量门槛", "",
          "继续为剩余134个临时主题校验关系，跨页与跨轨正式去重"
          "仍需要真实教师审定官方课标原子表；并扩充真正完整的原创课程单元、"
          "条件证明、题族、未见题与学生端RAG防泄漏测试。", ""]
    return "\n".join(L)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    scope = build()
    for path, content in ((OUT, dump(scope)), (DOC, markdown(scope))):
        if args.check:
            require(path.is_file() and path.read_text(encoding="utf-8") == content,
                    "generated content drift " + str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print("BATCH92", scope["new_relation_pairs"], "pairs",
          scope["newly_reviewed_provisional_topics"], "new source topics",
          scope["remaining_unpaired_provisional_topics"], "remaining",
          "official_curriculum_denominator=UNKNOWN")


if __name__ == "__main__":
    main()
