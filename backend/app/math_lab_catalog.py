"""Offline national high-school mathematics visualization planning catalog.
This is an engineering interpretation, not an official copy of a test blueprint.
"""
from pathlib import Path
from functools import lru_cache
import json

ROOT=Path(__file__).resolve().parents[2]/"curriculum"/"highschool_math"
TOOL_IDS={"function_2d","conic_2d","triangle_2d","space_3d","vector_2d"}
PLANNED_TOOLS={"venn_logic","number_line","complex_plane","probability_tree",
 "statistics_plot","modeling_workspace","combinatorics","probability_plot","enrichment"}

@lru_cache(maxsize=1)
def lab_catalog():
    curriculum=json.loads((ROOT/"curriculum_map.json").read_text(encoding="utf8"))
    scenes=json.loads((ROOT/"visual_presets.json").read_text(encoding="utf8"))
    topics=curriculum["coverage"]
    presets=scenes["presets"]
    if len({topic["id"] for topic in topics})!=len(topics):
        raise ValueError("Duplicated curriculum concept IDs")
    if len({p["id"] for p in presets})!=len(presets):
        raise ValueError("Duplicated lab preset IDs")
    if any(p["tool"] not in TOOL_IDS for p in presets):
        raise ValueError("Lab preset has an unsupported tool")
    if any(t["recommended_tool"] not in TOOL_IDS|PLANNED_TOOLS for t in topics):
        raise ValueError("Unknown mapped curriculum tool")
    scene_ids={p["id"] for p in presets}
    for topic in topics:
        evidence=topic.get("available_presets",[])
        if not all(id in scene_ids for id in evidence):
            raise ValueError("Coverage references an unknown scene")
        if (topic["status"]=="INTERACTIVE_FOUNDATION") != bool(evidence):
            raise ValueError("Unsupported coverage claim")
        if not topic.get("capability_limits"):
            raise ValueError("Missing capability limitation")
    for p in presets:
        keys=[v["key"] for v in p["params"]]
        if len(set(keys))!=len(keys):
            raise ValueError("Repeated slider parameter key")
        for v in p["params"]:
            if not (v["min"]<=v["value"]<=v["max"]) or v["step"]<=0:
                raise ValueError("Illegal preset slider bounds")
    counts={
        "total_concepts":len(topics),
        "interactive_foundations":sum(t["status"]=="INTERACTIVE_FOUNDATION" for t in topics),
        "planned_concepts":sum(t["status"]=="PLANNED" for t in topics),
        "scene_presets":len(presets),
        "scene_families":{tool:sum(p["tool"]==tool for p in presets) for tool in TOOL_IDS}
    }
    return {
      "version":curriculum["version"],
      "title":"高中数学知识点与动态工具规划",
      "reference":curriculum["curriculum_reference"],
      "reference_url":curriculum["reference_url"],
      "scope_note":curriculum["scope_note"],
      "counts":counts,
      "topics":topics,
      "presets":presets,
      "no_llm_api":True,
      "expert_review":"PENDING",
      "tool_design_level":"CURATED_INTERACTIVE_EXPLORATION",
      "claim":"基础画板并非某知识点的完整课程教学实现"
    }
