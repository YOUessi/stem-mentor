#!/usr/bin/env python3
"""Read-only inventory of the STEM Mentor demo knowledge corpus.

Counts engineering artifacts, NOT educational accuracy, teaching completeness,
or student mastery. Run from any working directory using stdlib Python.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf8"))


def audit():
    cards=read("knowledge/corpus/methods.json")
    graphs=read("knowledge/reasoning_graphs.json")
    visuals=read("knowledge/study_visuals.json")
    topics=read("curriculum/highschool_math/curriculum_map.json")["coverage"]
    presets=read("curriculum/highschool_math/visual_presets.json")["presets"]
    # The demo app stores curated problems and micro reviews in this module.
    import sys
    sys.path.insert(0,str(ROOT/"backend"))
    from app.catalog import PROBLEMS,MICRO_POINTS

    required_deep_sections=("theorems","proofs","worked_examples","counterexamples","misconceptions")
    result={
      "scope":"ENGINEERING_INVENTORY_NOT_PEDAGOGICAL_CERTIFICATION",
      "version":"2026-10-20",
      "curriculum":{
        "engineering_topic_count":len(topics),
        "interactively_mapped":sum(t["status"]=="INTERACTIVE_FOUNDATION" for t in topics),
        "planned":sum(t["status"]=="PLANNED" for t in topics),
        "review_pending":sum(t.get("source",{}).get("teacher_review")=="PENDING" for t in topics),
        "formal_lesson_sections_present":sum(any(bool(t.get(k)) for k in required_deep_sections)
            for t in topics)
      },
      "method_corpus":{
        "cards":len(cards),
        "types":dict(Counter(x["kind"] for x in cards)),
        "review_pending":sum(x.get("source",{}).get("expert_review")=="PENDING" for x in cards),
        "author_original":sum(x.get("source",{}).get("permission")=="PROJECT_AUTHORED" for x in cards),
        "cards_with_prerequisites":sum(bool(x.get("prerequisites")) for x in cards),
        "cards_with_boundaries":sum(bool(x.get("boundary")) for x in cards),
        "cards_with_hints":sum(bool(x.get("hint")) for x in cards),
        "cards_with_dedicated_deep_section":sum(any(bool(x.get(k)) for k in required_deep_sections)
            for x in cards)
      },
      "problem_bank":{
        "curated_problems":len(PROBLEMS),
        "reasoning_graphs":len(graphs),
        "micro_review_cards":len(MICRO_POINTS),
        "formula_cards":len(visuals),
        "hand_authored_geometry_scenes":sum(bool(x.get("geometry")) for x in visuals.values())
      },
      "interactive_math":{
        "total_presets":len(presets),
        "tool_types":dict(Counter(x["tool"] for x in presets)),
        "presets_pending_teacher_review":sum(x.get("expert_review")=="PENDING" for x in presets)
      },
      "reliability":{
        "retrieval_technique":"LOCAL_FTS5_BM25_AND_STRUCTURE_V1",
        "teacher_approved_corpus_available":False,
        "general_math_proof_verification":False,
        "student_identity_authentication":False,
        "verified_learning_outcomes":False
      }
    }
    assert result["curriculum"]["interactively_mapped"]+result["curriculum"]["planned"]==len(topics)
    assert result["problem_bank"]["reasoning_graphs"]==len(PROBLEMS)
    assert all("source" in x and x.get("boundary") for x in cards)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",action="store_true",help="Write a JSON inventory to stdout")
    args=parser.parse_args()
    summary=audit()
    if args.json:
        print(json.dumps(summary,ensure_ascii=False,indent=2))
    else:
        print("High-school STEM Mentor knowledge inventory, not teacher-certified content")
        for k in ("curriculum","method_corpus","problem_bank","interactive_math","reliability"):
            print(f"\n[{k}]")
            for key,value in summary[k].items():print(f"  {key}: {value}")


if __name__=="__main__":
    main()
