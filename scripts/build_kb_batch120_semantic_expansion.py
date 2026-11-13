#!/usr/bin/env python3
"""64 source-line-locked semantic proposals and seven-track *editorial* coverage, NOT official census.

Private Mac source check is mandatory during authoring and local testing.
On CI the committed opaque source hashes are checked against frozen evidence,
not against a redistributed copyrighted source.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from kb_batch120_semantic_catalog import ROWS, FROZEN_SOURCE_SHA256
import build_kb_batch118_source_atom_ledger as evidence
import build_kb_batch119_semantic_pilot as previous

OUT = ROOT / "curriculum/highschool_math/k00_batch120_semantic_expansion.json"
COVER = ROOT / "docs/evaluation/KB_BATCH120_SEVEN_TRACK_COVERAGE.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH120_SEMANTIC_EXPANSION.md"
ADJUDICATION = ROOT / "knowledge/editorial_review/kb_batch120_q0_geometric_adjudication.json"
TRACKS = evidence.TRACKS


def demand(condition: bool, why: str):
    if not condition:
        raise ValueError(why)


def hash_text(txt: str) -> str:
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


def serial(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"


def prior_data():
    prev = json.loads(previous.OUT.read_text(encoding="utf-8"))
    demand(previous.validate(prev), "prior pilot invalid")
    return prev


def base_data():
    z = json.loads(evidence.OUT.read_text(encoding="utf-8"))
    demand(evidence.validate(z), "source cue ledger invalid")
    return z


def build(use_local: bool = False):
    base, prior = base_data(), prior_data()
    pages = {p["printed_page"]: p for p in base["pages"]}
    cues = base["markers"]
    old_ids = {r["id"] for r in prior["candidates"]}
    old_titles = {(r["course_track"], r["proposed_objective"]) for r in prior["candidates"]}
    stored = {}
    if OUT.exists():
        stored = {r["local_key"]: r["source"]["source_span_sha256"]
                  for r in json.loads(OUT.read_text(encoding="utf-8")).get("candidates", [])}
    private = {p["printed_page"]: p["lines"] for p in evidence.source_pages()} if use_local else None
    found, ids, seen_keys, titles = [], set(), set(), set()
    for key, track, p, lo, hi, kind, title, condition, nonexample, visual, prereq in ROWS:
        rid = "hs-semantic-pilot-120-" + key.lower()
        demand(key not in seen_keys and rid not in ids and rid not in old_ids, "duplicate id")
        demand(track in TRACKS and kind in ("concept", "theorem", "method"), "illegal type/track")
        demand(p in pages and 1 <= lo <= hi <= pages[p]["source_line_count"], "invalid line bounds " + key)
        demand(all(evidence.track_at(p, n) == track for n in range(lo, hi + 1)), "track/source mismatch " + key)
        demand(len(title) >= 9 and len(condition) >= 12 and len(nonexample) >= 13, "empty math meaning " + key)
        demand((track, title) not in old_titles and (track, title) not in titles, "duplicate objective " + key)
        dependency = []
        if prereq is not None:
            if prereq.startswith("119:"):
                dependency = ["hs-semantic-pilot-119-" + prereq[4:].lower()]
                demand(dependency[0] in old_ids, "unknown historical prerequisite " + key)
            else:
                dependency = ["hs-semantic-pilot-120-" + prereq.lower()]
                demand(dependency[0] in ids, "forward/orphan prerequisite " + key)
        digest = hash_text("\n".join(private[p][lo - 1:hi])) if private else FROZEN_SOURCE_SHA256[key]
        demand(digest == FROZEN_SOURCE_SHA256[key], "source-span does not match separately frozen catalog " + key)
        demand(isinstance(digest, str) and re.fullmatch(r"[a-f0-9]{64}", digest), "missing source hash " + key)
        matching = [m["editorial_marker_id"] for m in cues
                    if m["printed_page"] == p and lo <= m["source_line"] <= hi and m["track_hint"] == track]
        found.append({
            "id": rid, "local_key": key, "course_track": track, "kind": kind,
            "proposed_objective": title, "applicability": condition, "invalid_use": nonexample,
            "prerequisite_candidate_ids": dependency,
            "source": {
                "printed_page": p, "physical_page_index": p + 7,
                "start_line": lo, "end_line": hi,
                "original_pdf_sha256": evidence.PDF_SHA,
                "frozen_page_sha256": pages[p]["source_page_sha256"],
                "source_span_sha256": digest, "matching_layout_cues": matching,
                "visual_formula_recheck": "REQUIRED" if visual else "NOT_FLAGGED"
            },
            "review_status": "REVIEW_PENDING", "teacher_evidence": None,
            "proof_verification": "UNVERIFIED",
            "teacher_solution_visibility": "TEACHER_ONLY",
            "student_authoritative": False, "official_atom_id": None,
            "official_atom_certified": False,
            "elective_e_optional_example": track == "ELECTIVE_E",
        })
        seen_keys.add(key)
        ids.add(rid)
        titles.add((track, title))
    used_prior = {id_ for r in prior["candidates"] for id_ in r["source"]["matching_layout_cues"]}
    used_new = {id_ for r in found for id_ in r["source"]["matching_layout_cues"]}
    counts_old = Counter(r["course_track"] for r in prior["candidates"])
    counts_new = Counter(r["course_track"] for r in found)
    data = {
        "schema_version": "kb120-semantic-editorial-v1",
        "curriculum_standard": base["curriculum_standard"],
        "original_pdf_sha256": evidence.PDF_SHA,
        "source_text_committed": False,
        "official_atom_census_complete": False, "official_atom_total_denominator": None,
        "semantic_candidates_not_official_atoms": True,
        "prior_pilot_count": len(prior["candidates"]), "new_candidate_count": len(found),
        "cumulative_editorial_candidate_count": len(prior["candidates"]) + len(found),
        "source_cue_total": len(cues),
        "source_cues_linked_prior": len(used_prior),
        "source_cues_linked_new": len(used_new),
        "source_cues_linked_cumulative": len(used_prior | used_new),
        "source_cues_not_linked_cumulative": len(cues) - len(used_prior | used_new),
        "teacher_approved_count": 0, "student_authoritative_count": 0,
        "by_track": {
            track: {"previous": counts_old[track], "new": counts_new[track],
                    "cumulative_editorial_candidates": counts_old[track] + counts_new[track],
                    "official_atom_denominator": None, "teacher_approved": 0,
                    "whole_track_complete": False}
            for track in TRACKS
        },
        "candidates": found
    }
    validate(data)
    return data


def validate(data):
    base, prior = base_data(), prior_data()
    pages = {p["printed_page"]: p for p in base["pages"]}
    cues = {m["editorial_marker_id"]: m for m in base["markers"]}
    prior_ids = {r["id"] for r in prior["candidates"]}
    prior_linked = {id_ for r in prior["candidates"] for id_ in r["source"]["matching_layout_cues"]}
    demand(data["schema_version"] == "kb120-semantic-editorial-v1" and
           data["original_pdf_sha256"] == evidence.PDF_SHA and
           data["curriculum_standard"] == base["curriculum_standard"] and
           data["semantic_candidates_not_official_atoms"] is True and
           data["source_text_committed"] is False, "invalid provenance")
    demand(data["official_atom_census_complete"] is False and
           data["official_atom_total_denominator"] is None and
           data["teacher_approved_count"] == data["student_authoritative_count"] == 0,
           "fraudulent curriculum/teacher approval")
    demand(set(data["by_track"]) == set(TRACKS), "missing track")
    demand(data["new_candidate_count"] == len(data["candidates"]) == len(ROWS) and
           data["prior_pilot_count"] == len(prior["candidates"]) and
           data["cumulative_editorial_candidate_count"] == len(prior["candidates"]) + len(ROWS),
           "inflated curriculum counts")
    seen = set(prior_ids)
    linked = set()
    count = Counter()
    objectives = {(r["course_track"], r["proposed_objective"]) for r in prior["candidates"]}
    demand(set(FROZEN_SOURCE_SHA256) == {r[0] for r in ROWS}, "source hash catalog coverage gap")
    for row, raw in zip(data["candidates"], ROWS):
        key, want_track, want_page, want_lo, want_hi, want_kind, want_title, want_condition, want_nonexample, want_visual, want_prereq = raw
        rid, track, src = row["id"], row["course_track"], row["source"]
        demand(row["local_key"] == key and rid == "hs-semantic-pilot-120-" + key.lower() and
               track == want_track and row["kind"] == want_kind and
               row["proposed_objective"] == want_title and
               row["applicability"] == want_condition and row["invalid_use"] == want_nonexample,
               "catalog mismatch " + key)
        want_dependencies = ([] if want_prereq is None else
            ["hs-semantic-pilot-119-" + want_prereq[4:].lower()] if want_prereq.startswith("119:") else
            ["hs-semantic-pilot-120-" + want_prereq.lower()])
        demand(row["prerequisite_candidate_ids"] == want_dependencies, "catalog prerequisite mismatch " + key)
        demand((src["printed_page"],src["start_line"],src["end_line"]) == (want_page,want_lo,want_hi) and
               src["source_span_sha256"] == FROZEN_SOURCE_SHA256[key] and
               src["visual_formula_recheck"] == ("REQUIRED" if want_visual else "NOT_FLAGGED"),
               "independent source commitment mismatch " + key)
        want_cues = [m["editorial_marker_id"] for m in base["markers"]
                    if m["printed_page"] == want_page and want_lo <= m["source_line"] <= want_hi
                    and m["track_hint"] == want_track]
        demand(src["matching_layout_cues"] == want_cues, "layout cue mismatch " + key)
        p, lo, hi = src["printed_page"], src["start_line"], src["end_line"]
        demand(re.fullmatch(r"hs-semantic-pilot-120-[a-z0-9]+", rid) and rid not in seen,
               "duplicate/illegal id")
        demand(track in TRACKS and row["kind"] in ("concept", "method", "theorem"), "invalid taxonomy")
        demand((track, row["proposed_objective"]) not in objectives, "duplicate teaching objective")
        objectives.add((track, row["proposed_objective"]))
        demand(len(row["applicability"]) >= 12 and len(row["invalid_use"]) >= 13, "missing math boundary")
        demand(row["review_status"] == "REVIEW_PENDING" and row["teacher_evidence"] is None
               and row["proof_verification"] == "UNVERIFIED" and
               row["teacher_solution_visibility"] == "TEACHER_ONLY" and
               row["student_authoritative"] is False and row["official_atom_id"] is None and
               row["official_atom_certified"] is False, "fake approval / student leak")
        demand(p in pages and 1 <= lo <= hi <= pages[p]["source_line_count"], "bad lines")
        demand(src["physical_page_index"] == p + 7 and
               src["original_pdf_sha256"] == evidence.PDF_SHA and
               src["frozen_page_sha256"] == pages[p]["source_page_sha256"] and
               re.fullmatch(r"[a-f0-9]{64}", src["source_span_sha256"]), "invalid source fingerprint")
        demand(src["visual_formula_recheck"] in ("REQUIRED", "NOT_FLAGGED"), "missing visual flag")
        demand(all(evidence.track_at(p, n) == track for n in range(lo, hi + 1)),
               "cross-track line contamination")
        for cid in src["matching_layout_cues"]:
            demand(cid in cues and cues[cid]["printed_page"] == p and
                   lo <= cues[cid]["source_line"] <= hi and
                   cues[cid]["track_hint"] == track, "untrusted cue")
            linked.add(cid)
        for dep in row["prerequisite_candidate_ids"]:
            demand(dep in seen and dep != rid, "orphan/forward/cyclic prerequisite")
        demand(row["elective_e_optional_example"] == (track == "ELECTIVE_E"),
               "E optional curriculum misclassified")
        seen.add(rid)
        count[track] += 1
    demand(data["source_cue_total"] == len(cues) and
           data["source_cues_linked_prior"] == len(prior_linked) and
           data["source_cues_linked_new"] == len(linked) and
           data["source_cues_linked_cumulative"] == len(linked | prior_linked) and
           data["source_cues_not_linked_cumulative"] == len(cues) - len(linked | prior_linked),
           "misleading source-cue denominator")
    prior_counts = Counter(r["course_track"] for r in prior["candidates"])
    for track in TRACKS:
        t = data["by_track"][track]
        demand(t["previous"] == prior_counts[track] and t["new"] == count[track] and
               t["cumulative_editorial_candidates"] == count[track] + prior_counts[track] and
               t["official_atom_denominator"] is None and t["teacher_approved"] == 0 and
               t["whole_track_complete"] is False, "fake official track coverage")
    return True


def verify_source(data):
    private = {p["printed_page"]: p["lines"] for p in evidence.source_pages()}
    for r in data["candidates"]:
        s = r["source"]
        actual = hash_text("\n".join(private[s["printed_page"]][s["start_line"]-1:s["end_line"]]))
        demand(actual == s["source_span_sha256"], "private source hash drift " + r["id"])


def q0_adjudication():
    # Critical distinction: finite algebraic power sum vs conventional
    # high-school geometric sequence defined by nonzero consecutive ratio.
    return {
        "status": "REVIEW_PENDING", "teacher_evidence": None,
        "student_authoritative": False,
        "historical_reference": "hs-semantic-pilot-119-s04 / hs-semantic-pilot-119-s05",
        "algebraic_finite_sum": {
            "domain": "n>=1 integer, a and q real",
            "definition": "a*sum(q**k for k=0..n-1), q**0=1 including q=0",
            "q_zero": "n>=1 -> a", "q_one": "n*a",
            "q_other": "a*(1-q**n)/(1-q) for q != 1"
        },
        "standard_geometric_sequence": {
            "domain": "nonzero a1, nonzero q, positive-integer n under adjacent nonzero ratios",
            "q_zero_or_a1_zero": "does not meet nonzero-ratio definition, despite algebraic series existence"
        },
        "negative_examples": [
            "q=1 gives 0/0 if formula with 1-q is used",
            "q=0 causes later adjacent ratio 0/0 and cannot be treated as a conventional geometric progression",
            "a1=0 makes all later adjacent ratios undefined"
        ],
        "general_proof_machine_certified": False,
        "source_usage": "editorial mathematical clarification, teacher review required"
    }


def render(data):
    lines = ["# Batch120｜七轨64条新增来源锁定的语义候选（非官方知识原子）", "",
             "本批为编辑候审内容，未经教师核对；不提交课标PDF原文。行级散列在Mac原件上复核。",
             f"新增 {data['new_candidate_count']}，与上批累计 {data['cumulative_editorial_candidate_count']}，"
             f"405条排版线索累计关联 {data['source_cues_linked_cumulative']}；"
             f"仍未关联 {data['source_cues_not_linked_cumulative']}。不等于官方课程覆盖率。", "",
             "| 轨道 | 上批 | 本批 | 累计编辑候选 | 官方原子分母 | 教师批准 |",
             "| --- | ---: | ---: | ---: | --- | ---: |"]
    for t in TRACKS:
        row = data["by_track"][t]
        lines.append(f"| {t} | {row['previous']} | {row['new']} | {row['cumulative_editorial_candidates']} | UNKNOWN | 0 |")
    lines += ["", "| ID | 源印刷页:行 | 目标 | 数学适用条件 | 非例 | 待重检图像 |",
              "| --- | --- | --- | --- | --- | --- |"]
    for r in data["candidates"]:
        s = r["source"]
        lines.append(f"| {r['local_key']} | {s['printed_page']}:{s['start_line']}-{s['end_line']} | "
                     f"{r['proposed_objective']} | {r['applicability']} | {r['invalid_use']} | "
                     f"{s['visual_formula_recheck']} |")
    lines += ["", "## 范围与数学审校", "",
              "- 每条具有独立目标、前提、不合法用法、先修候选引用和冻结来源证据；但不是逐章完整教师讲义。",
              "- 与上批pilot关联的排版线索的并集去重，不把同一行的不同语义或跨轨等价重复当作官方分母。",
              "- E轨只是学校选择性示例；不会被统计为全体高中学生必修内容。",
              "- 等比数列q=0问题单列候审裁决：有限幂级数代数上合法，不等于邻项商定义下的标准等比数列。",
              "- 承认尚未完成余下的全部课标正文审查、历史172项先修、538条证明步骤、10项冲突和教师签署。",
              "- 所有候选 REVIEW_PENDING / TEACHER_ONLY，学生权威检索保持隔离。", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    switch = parser.add_mutually_exclusive_group(required=True)
    switch.add_argument("--write", action="store_true")
    switch.add_argument("--check", action="store_true")
    parser.add_argument("--verify-local-source", action="store_true")
    args = parser.parse_args()
    obj = build(use_local=args.write or args.verify_local_source)
    q0 = q0_adjudication()
    coverage = {
        "batch": 120, "source_layout_cues": obj["source_cue_total"],
        "source_cues_linked_cumulative": obj["source_cues_linked_cumulative"],
        "source_cues_unlinked": obj["source_cues_not_linked_cumulative"],
        "previous_editorial_candidates": obj["prior_pilot_count"],
        "new_editorial_candidates": obj["new_candidate_count"],
        "cumulative_editorial_candidates": obj["cumulative_editorial_candidate_count"],
        "per_track": obj["by_track"],
        "official_atom_denominator": {t: None for t in TRACKS},
        "all_official_atom_denominators_known": False,
        "teacher_approved": 0, "student_authoritative_releases": 0,
        "whole_curriculum_completed": False
    }
    files = {OUT: serial(obj), COVER: serial(coverage),
             REPORT: render(obj), ADJUDICATION: serial(q0)}
    for path, value in files.items():
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")
        else:
            demand(path.exists() and path.read_text(encoding="utf-8") == value,
                   "generated artifact drift: " + str(path))
    if args.verify_local_source:
        verify_source(obj)
    print(f"Batch120: {len(ROWS)} new, {obj['cumulative_editorial_candidate_count']} cumulative editorial candidates, "
          f"{obj['source_cues_linked_cumulative']}/{obj['source_cue_total']} layout cues linked; "
          "official seven-track denominator UNKNOWN; no teacher approval")


if __name__ == "__main__":
    main()
