#!/usr/bin/env python3
"""Batch90: source-locked, unapproved 24 provisional candidate comparisons.

Editor judgement is not an official curricular atom count or math equivalence certification.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "backend")]
from app.kb_batch90_exact_witness import check_all
import build_kb_batch89_proofs_and_scope as B89
import build_kb_batch88_relations as B88

AUTHOR = ROOT / "curriculum/highschool_math/kb_batch90_relations_authoring.json"
OUT = ROOT / "docs/evaluation/KB_BATCH90_SOURCE_RELATIONS.json"
DOC = ROOT / "docs/evaluation/KB_BATCH90_SOURCE_RELATIONS.md"
SCHEMA = "kb90-24-math-relation-proposals-v1"
ROW_FIELDS = {
    "review_id", "left_candidate_id", "right_candidate_id", "relation_proposal",
    "shared_maths", "distinguishing_conditions", "worked_witness",
    "failure_or_boundary", "review_status", "teacher_approved",
    "math_equivalence_certified", "student_publishable", "final_atom_id"
}
ROOT_FIELDS = {
    "schema_version", "standard_version", "authorship", "authority",
    "teacher_approved", "semantic_equivalence_certified",
    "student_publishable", "relations"
}
def require(cond: bool, why: str):
    if not cond:
        raise ValueError(why)

def pairs_unique(items):
    result = {}
    for k, v in items:
        require(k not in result, "duplicate source JSON key " + k)
        result[k] = v
    return result

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=pairs_unique)

def dump(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

def build(raw=None, prior=None, previous=None):
    raw = load(AUTHOR) if raw is None else raw
    prior = B89.build()[1] if prior is None else prior
    previous = B88.build() if previous is None else previous
    require(type(raw) is dict and set(raw) == ROOT_FIELDS, "root schema drift")
    require(raw["schema_version"] == SCHEMA
            and raw["standard_version"] == "普通高中数学课程标准（2017年版2020年修订）"
            and raw["authorship"] == "ORIGINAL_PROJECT_MATH_EDITORIAL_ON_MAC"
            and raw["authority"] == "EDITOR_ONLY_NOT_TEACHER"
            and raw["teacher_approved"] is False
            and raw["semantic_equivalence_certified"] is False
            and raw["student_publishable"] is False,
            "forged authority or unsupported curriculum version")
    require(prior["provisional_labels"] == 300
            and prior["provisional_candidates_unpaired"] == 230
            and prior["provisional_candidates_with_any_pair"] == 70
            and prior["official_atom_denominator"] is None
            and prior["teacher_approved"] == 0 and prior["student_published"] == 0
            and previous["reviewed_relation_count"] == 36
            and previous["semantic_equivalence_adjudicated_count"] == 0,
            "upstream provisional census or review authority drift")
    prior_candidates = {c["candidate_id"]: c
                        for c in prior["provisional_candidate_backlog"]}
    require(len(prior_candidates) == 300, "missing source candidate")
    old_edges = {tuple(sorted((r["left_candidate_id"], r["right_candidate_id"])))
                 for r in previous["reviewed_relations"]}
    seen_edges, touched, reviews, types = set(), set(), [], Counter()
    finite = check_all()
    require(type(raw["relations"]) is list and len(raw["relations"]) == 24,
            "24 complete original relationship reviews required")
    for i, row in enumerate(raw["relations"], 1):
        require(type(row) is dict and set(row) == ROW_FIELDS, "relation schema drift")
        require(row["review_id"] == f"KB90-REL-{i:03d}", "relation id changed")
        require(row["relation_proposal"] in ("POSSIBLE_OVERLAP", "RELATED_DISTINCT"),
                "not a supported editorial relation type")
        require(row["review_status"] == "REVIEW_PENDING"
                and row["teacher_approved"] is False
                and row["math_equivalence_certified"] is False
                and row["student_publishable"] is False
                and row["final_atom_id"] is None,
                "unearned teacher/math/official atom approval")
        for key, minimum in {"shared_maths": 20, "distinguishing_conditions": 32,
                             "worked_witness": 24, "failure_or_boundary": 25}.items():
            require(type(row[key]) is str and len(row[key].strip()) >= minimum,
                    "missing substantial math explanation: " + key)
        left_id, right_id = row["left_candidate_id"], row["right_candidate_id"]
        require(type(left_id) is str and type(right_id) is str
                and left_id in prior_candidates and right_id in prior_candidates
                and left_id != right_id, "invalid relation endpoint")
        edge = tuple(sorted((left_id, right_id)))
        require(edge not in old_edges and edge not in seen_edges,
                "previously compared or duplicate/swapped relation")
        seen_edges.add(edge)
        for candidate_id in (left_id, right_id):
            require(candidate_id not in touched, "repeat candidate, expected 48 newly audited")
            touched.add(candidate_id)
            source = prior_candidates[candidate_id]
            require(source["relation_count"] == 0
                    and source["cross_track_status"] == "NOT_YET_COMPARED"
                    and source["official_math_atom_id"] is None
                    and source["teacher_approval"] is None
                    and source["student_authoritative_index_eligible"] is False,
                    "cannot count previously paired or certified candidate as new")
        left, right = prior_candidates[left_id], prior_candidates[right_id]
        types[row["relation_proposal"]] += 1
        reviews.append({
            **row,
            "left_source": {k: left[k] for k in ("candidate_id", "track", "provisional_topic",
                    "source_review_id", "source_line_sha256", "source_page")},
            "right_source": {k: right[k] for k in ("candidate_id", "track", "provisional_topic",
                    "source_review_id", "source_line_sha256", "source_page")},
            "source_fingerprint_scope": "PROJECT_PDFKIT_SOURCE_LINE_SHA256",
            "math_evidence_scope": "EDITORIAL_FINITE_EXAMPLES_ONLY_NOT_UNIVERSAL_CERTIFICATION",
            "human_equivalence_adjudication": "NOT_PERFORMED",
            "student_authoritative_index_eligible": False,
            "finite_verification": finite.get(row["review_id"],
                  {"status": "NOT_AUTOMATICALLY_VERIFIED",
                   "evidence_scope": "EDITORIAL_TEXT_WITNESS_ONLY"})
        })
    require(set(finite) <= {r["review_id"] for r in reviews} and len(finite)==16,
            "exact witness binding drift")
    require(len(touched) == 48 and len(seen_edges) == 24,
            "new source distinctness count mismatch")
    cross = sum(r["left_source"]["track"] != r["right_source"]["track"]
                for r in reviews)
    require(cross >= 7 and types["POSSIBLE_OVERLAP"] >= 2
            and types["RELATED_DISTINCT"] >= 16,
            "not broad enough to compare genuine cross-track and distinct topics")
    by_track = Counter(c["track"] for c in prior_candidates.values())
    prior_paired = Counter(c["track"] for c in prior_candidates.values()
                           if c["relation_count"] > 0)
    newly = Counter(prior_candidates[k]["track"] for k in touched)
    per_track = {}
    for track in B88.BASE.TRACKS:
        per_track[track] = {
            "provisional_candidates": by_track[track],
            "prior_paired": prior_paired[track],
            "newly_paired": newly[track],
            "now_paired": prior_paired[track] + newly[track],
            "still_unpaired": by_track[track] - prior_paired[track] - newly[track],
            "official_atom_denominator": None,
            "teacher_approved": 0
        }
    require(sum(v["still_unpaired"] for v in per_track.values()) == 182,
            "inexact unpaired backlog count")
    return {
        "schema_version": "kb90-source-locked-editorial-relations-v1",
        "standard_version": raw["standard_version"],
        "source_backlog_sha256": hashlib.sha256(B89.AUDIT.read_bytes()).hexdigest(),
        "authoring_sha256": hashlib.sha256(AUTHOR.read_bytes()).hexdigest(),
        "source_anchor_editorials": 428,
        "provisional_candidate_total": 300,
        "prior_editorial_pairs": 36, "new_editorial_pairs": 24,
        "cumulative_editorial_pairs": 60, "new_candidate_id_coverage": 48,
        "cumulative_candidate_id_coverage": 118,
        "remaining_candidate_ids_without_any_relation": 182,
        "new_cross_track_relations": cross,
        "exact_finite_case_pairs_checked": len(finite)*2,
        "editorial_relations_with_exact_finite_witness": len(finite),
        "editorial_relations_without_automated_witness": 24-len(finite),
        "new_relation_types": dict(types),
        "per_track": per_track,
        "official_curriculum_atom_denominator": None,
        "complete_teacher_atomization_pages": 0,
        "math_equivalence_teacher_adjudications": 0,
        "teacher_approved": 0, "student_published": 0,
        "historical_P0_unreviewed": 106,
        "historical_proof_steps_not_formally_certified": 538,
        "historical_unresolved_conflicts": 10,
        "review_status": "REVIEW_PENDING",
        "source_locked_relations": reviews,
        "remaining_unpaired_candidate_ids": sorted(set(prior_candidates)-{
            c["candidate_id"] for c in prior["provisional_candidate_backlog"]
            if c["relation_count"] > 0
        }-touched)
    }

def markdown(data):
    lines = [
        "# Batch90｜24组课程数学候选关系的原创审查与范围门禁", "",
        "**24组编辑草案，48个新覆盖候选，其中跨课程轨道"
        + str(data["new_cross_track_relations"]) + "组。既非教师批准也非数学等价裁决。**",
        "目前累计60组（Batch88 36 + Batch90 24），118/300临时主题有至少一组关系比较；剩余182个无配对。",
        "300是项目临时标签，428是来源锚点；二者都不是官方高中数学知识原子分母。",
        "仍未完成真实教师61页逐页原子审查、538历史证明一般形式认证与10组冲突裁决。", "",
        "| 轨道 | 项目候选 | 旧已配对 | 本次新配对 | 累计已配对 | 仍未配对 | 官方数学原子分母 |",
        "|---|---:|---:|---:|---:|---:|---|"
    ]
    for k, d in data["per_track"].items():
        lines.append(f'| {k} | {d["provisional_candidates"]} | {d["prior_paired"]} | '
                     f'{d["newly_paired"]} | {d["now_paired"]} | {d["still_unpaired"]} | 未知 |')
    lines += ["", "## 原创数学语义比较（待真实教师独立审查）", ""]
    for row in data["source_locked_relations"]:
        lines += [
            f'### {row["review_id"]}｜{row["left_source"]["provisional_topic"]} ／ '
            f'{row["right_source"]["provisional_topic"]}', "",
            f'关系：{row["relation_proposal"]}；'
            f'来源 {row["left_source"]["candidate_id"]}（{row["left_source"]["track"]}）与 '
            f'{row["right_source"]["candidate_id"]}（{row["right_source"]["track"]}）', "",
            "**共有结构：**" + row["shared_maths"], "",
            "**前提及区别：**" + row["distinguishing_conditions"], "",
            "**受控算例（未作一般证明）：**" + row["worked_witness"], "",
            "**反例/不适用：**" + row["failure_or_boundary"], "",
            "**自动化有限核验：**" + (row["finite_verification"].get("operation",
            "未自动验证；仅供编辑和教师逐项检查")),
            "此处不产生任何一般定理或课程原子等价认证。", ""
        ]
    lines += ["## 必须继续完成的课程验收", "",
              "1. 不以编辑相似性自动合并候选；正式分母均保持null，教师批注和许可仍需补齐。",
              "2. 核实剩余182条无配对临时主题，跨页跨轨语义合并与先修关系需要数学证明或教研判断。",
              "3. 针对经过独立确认的缺口增加完整原创深度课程，并在学生端严格隔离教师解题。",
              "4. 538条历史未认证证明、106个历史P0尚无直接审稿卡、10组冲突继续开放。", ""]
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    data = build()
    for path, value in ((OUT, dump(data)), (DOC, markdown(data))):
        if a.check:
            require(path.is_file() and path.read_text(encoding="utf-8") == value,
                    "generated file drift: " + str(path))
        else:
            path.write_text(value, encoding="utf-8")
    print("Batch90 source locked: 24 editorial pairs; 48 newly compared distinct candidates; "
          "118/300 covered; 182 still unpaired; 0 approvals")

if __name__ == "__main__":
    main()
