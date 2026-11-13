#!/usr/bin/env python3
"""Batch88 cross-track mathematics relation proposals; never certified equivalence."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch87_candidate_census as BASE

SRC = ROOT / "curriculum/highschool_math/kb_batch88_cross_track_editorials.json"
OUT = ROOT / "docs/evaluation/KB_BATCH88_PROVISIONAL_RELATIONS.json"
MARKDOWN = ROOT / "docs/evaluation/KB_BATCH88_PROVISIONAL_RELATIONS.md"
FIELDS = {
    "review_id", "left_candidate_id", "right_candidate_id", "relation_proposal",
    "shared_maths", "distinguishing_conditions", "worked_witness",
    "failure_or_boundary", "review_state", "teacher_approved",
    "math_equivalence_certified", "student_publishable", "final_atom_id"
}
TEXT_FIELDS = ("shared_maths", "distinguishing_conditions", "worked_witness", "failure_or_boundary")
RELATION_TYPES = {"POSSIBLE_OVERLAP", "RELATED_DISTINCT"}

def require(ok: bool, msg: str):
    if not ok:
        raise ValueError(msg)

def unique_pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, f"duplicate JSON object key: {key}")
        result[key] = value
    return result

def load(path=SRC):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)

def dump(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n"

def build(raw=None, census=None):
    if raw is None:
        raw = load()
    if census is None:
        census = BASE.build()
    require(type(raw) is dict and set(raw) == {"schema_version", "provenance", "decision_authority", "relations"}, "authoring unexpected fields")
    require(raw["schema_version"] == "kb88-provisional-cross-track-review-v1", "schema drift")
    require(raw["provenance"] == "mac-original-editorial-proposals", "provenance drift")
    require(raw["decision_authority"] == "EDITOR_ONLY_NOT_TEACHER", "forged authority")
    require(type(raw["relations"]) is list and len(raw["relations"]) == 36, "incomplete relationship review")
    require(census["source_editorials_completed"] == 428 and
        census["exact_string_distinct_label_count"] == 300 and
        census["official_curriculum_atom_denominator"] is None and
        census["semantic_equivalence_adjudicated_count"] == 0 and
        census["teacher_approved_complete_lessons"] == 0, "census authority or denominator drift")
    atoms = {t["candidate_id"]: t for t in census["provisional_candidates"]}
    require(len(atoms) == 300, "missing provisional candidates")
    reviews, pairset, ids, counts = [], set(), set(), Counter()
    for i, row in enumerate(raw["relations"], 1):
        require(type(row) is dict and set(row) == FIELDS, f"relationship {i} schema violation")
        rid = f"KB88-REL-{i:03}"
        require(row["review_id"] == rid, "review id changed/reordered")
        a, b = row["left_candidate_id"], row["right_candidate_id"]
        require(type(a) is str and type(b) is str and a in atoms and b in atoms and a != b, "unknown or self-relation")
        pair = tuple(sorted((a, b)))
        require(pair not in pairset, "duplicate or swapped relationship")
        pairset.add(pair)
        require(row["relation_proposal"] in RELATION_TYPES, "unsupported semantic relation")
        for key in TEXT_FIELDS:
            require(type(row[key]) is str and len(row[key].strip()) >= 12, f"missing maths reasoning: {key}")
        require(row["review_state"] == "REVIEW_PENDING"
                and row["teacher_approved"] is False
                and row["math_equivalence_certified"] is False
                and row["student_publishable"] is False
                and row["final_atom_id"] is None, "unearned approval/equivalence/publication")
        left, right = atoms[a], atoms[b]
        for atom in (left, right):
            require(atom["cross_page_equivalence"] == "NOT_ADJUDICATED"
                and atom["cross_track_equivalence"] == "NOT_ADJUDICATED"
                and atom["official_math_atom_id"] is None
                and atom["student_publishable"] is False, "nonprovisional source used")
        item = {
            **row,
            "left": {"candidate_id": a, "topic": left["provisional_topic"],
                     "track": left["track"], "printed_page": left["printed_page"],
                     "source_review_id": left["source_review_id"],
                     "source_line_sha256": left["source_line_sha256"]},
            "right": {"candidate_id": b, "topic": right["provisional_topic"],
                     "track": right["track"], "printed_page": right["printed_page"],
                     "source_review_id": right["source_review_id"],
                     "source_line_sha256": right["source_line_sha256"]},
            "evidence_status": "EDITOR_EXAMPLE_NOT_GENERAL_MATH_CERTIFICATION",
            "needs_human_adjudication": True
        }
        reviews.append(item)
        ids.update((a, b))
        counts[row["relation_proposal"]] += 1
    require(counts["POSSIBLE_OVERLAP"] >= 20 and
        counts["RELATED_DISTINCT"] >= 6, "insufficient mixed relation coverage")
    require(len(ids) >= 55, "relation coverage too concentrated")
    return {
        "schema_version": "kb88-editorial-provisional-relations-result-v1",
        "reviewed_relation_count": len(reviews),
        "unique_provisional_candidate_ids_seen": len(ids),
        "relation_counts": dict(sorted(counts.items())),
        "source_anchor_editorials": 428,
        "provisional_candidate_count": 300,
        "unreviewed_relation_space_not_claimed_complete": True,
        "semantic_equivalence_adjudicated_count": 0,
        "official_curriculum_atom_denominator": None,
        "teacher_approved_atoms": 0,
        "student_published_atoms": 0,
        "teacher_pending_relation_count": len(reviews),
        "reviewed_relations": reviews,
    }

def markdown(data):
    s = [
        "# Batch88｜36组跨课程候选数学关系：审稿意见，不是已认证合并",
        "",
        "428个来源锚点均已产生项目级释义，当前仍只有300个**暂定标签**而非官方知识原子。",
        f"本批对{data['reviewed_relation_count']}对候选作了原创数学语义比较，涉及{data['unique_provisional_candidate_ids_seen']}个不同标签；",
        f"潜在重叠{data['relation_counts']['POSSIBLE_OVERLAP']}对、需要保持区分{data['relation_counts']['RELATED_DISTINCT']}对。",
        "全部是EDITOR提案；没有教师批准、数学语义认证或正式课标分母裁决。每对的正例不证明两个课程学习目标严格等价。",
        "",
        "| 审查ID | 左侧候选 | 右侧候选 | 初步关系 | 共用数学结构 | 必须区分的假设或范围 |",
        "|---|---|---|---|---|---|",
    ]
    for r in data["reviewed_relations"]:
        s.append(f"| {r['review_id']} | {r['left']['candidate_id']}（{r['left']['track']}） | "
                 f"{r['right']['candidate_id']}（{r['right']['track']}） | {r['relation_proposal']} | "
                 f"{r['shared_maths']} | {r['distinguishing_conditions']} |")
    s += [
        "", "## 严格审校边界", "",
        "1. 每组均保存原始源锚点ID和行SHA及具体正例、失效/不适用例。",
        "2. 标为POSSIBLE_OVERLAP的两项仍不得在知识图谱中合并；数学对象、条件、年级、深度和跨轨权限必须真人复核。",
        "3. RELATED_DISTINCT不能因题面相似就合并；任何例子只构成有限见证，不等于一般定理机器证明。",
        "4. 七轨正式数学原子分母仍为null，教师完整全页验收仍0/61，历史P0 64/182、538历史证明未形式认证、10冲突未裁决。",
        "5. 全部关系为REVIEW_PENDING，学生权威检索不应索引教师侧未审稿。",
        ""
    ]
    return "\n".join(s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    data = build()
    for path, val in ((OUT, dump(data)), (MARKDOWN, markdown(data))):
        if args.check:
            require(path.is_file() and path.read_text(encoding="utf-8") == val, "generated provenance drift: " + path.name)
        else:
            path.write_text(val, encoding="utf-8")
    print(f"Batch88: {data['reviewed_relation_count']} editor-proposed relations; {data['unique_provisional_candidate_ids_seen']} subjects; 0 approved; official atom denominator UNKNOWN")

if __name__ == "__main__":
    main()
