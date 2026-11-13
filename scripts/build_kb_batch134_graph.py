#!/usr/bin/env python3
"""Batch134 source-locked prerequisite DAG & cross-curricular reuse *review*.

This is an editorial, bounded pilot. Neither code nor graph traversal can establish
a national syllabus atom denominator or certify mathematical soundness.
"""
from __future__ import annotations
import argparse, copy, json, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as parent
OUT=ROOT/"docs/evaluation/KB_BATCH134_GRAPH_REVIEW.json"
MD=ROOT/"docs/evaluation/KB_BATCH134_GRAPH_REVIEW.md"
EXPECTED_REUSE={
    "FUNCTION_ZERO_AND_EQUATION_LINK": ("c_quadratic_roots","c_zero_theorem"),
    "MONOTONICITY_DIFFERENT_METHODS": ("c_monotonicity","sc_derivative_monotone"),
}
def require(ok,why):
    if not ok: raise ValueError(why)
def analyze(records):
    nodes={r["id"]:r for r in records}
    require(len(nodes)==len(records),"duplicate prerequisite node IDs")
    edges={k:tuple(r["prerequisite_proposals"]) for k,r in nodes.items()}
    for k,ps in edges.items():
        require(len(set(ps))==len(ps),"duplicate prerequisites")
        require(all(p in nodes and p!=k for p in ps),"orphan/self prereq "+k)
    visiting=set();done={};order=[]
    def visit(k):
        if k in visiting: raise ValueError("prerequisite cycle involving "+k)
        if k in done:return done[k]
        visiting.add(k)
        lev=0
        for p in edges[k]:lev=max(lev,visit(p)+1)
        visiting.remove(k);done[k]=lev;order.append(k)
        return lev
    for k in sorted(nodes):visit(k)
    groups=defaultdict(list)
    for r in records:
        if r["cross_page_reuse_group"]:groups[r["cross_page_reuse_group"]].append(r["id"])
    expected={"kb133-proposal-"+slug for ls in EXPECTED_REUSE.values() for slug in ls}
    actual={id for arr in groups.values() for id in arr}
    require(actual==expected,"reuse membership drift")
    for g,slugs in EXPECTED_REUSE.items():
        require(set(groups[g])=={"kb133-proposal-"+s for s in slugs},"cross-curricular group mismatch "+g)
    require(set(groups)==set(EXPECTED_REUSE),"unknown reuse group")
    rows=[]
    for k in sorted(nodes):
        r=nodes[k]
        rows.append(dict(candidate_id=k,track=r["track"],source_span_sha256=r["source_lock"]["span_sha256"],
            prerequisite_candidates=list(edges[k]),dag_depth=done[k],category=r["knowledge_type"],
            cross_page_reuse_group=r["cross_page_reuse_group"],editorial_relation_decision=(
                "SAME_SUBJECT_DIFFERENT_METHOD_NOT_MERGED" if r["cross_page_reuse_group"] else
                "DISTINCT_PROVISIONAL_OBJECTIVE_NOT_TEACHER_VERIFIED"),
            teacher_review="REVIEW_PENDING",formal_prerequisite_correctness="UNVERIFIED",
            student_authoritative=False,official_atom_id=None))
    return dict(schema="kb134/1",source_batch=133,scope="BOUNDED_PROPOSAL_PREREQUISITE_AND_REUSE_REVIEW",
        proposed_nodes=len(records),proposed_direct_edges=sum(len(x) for x in edges.values()),
        max_dag_depth=max(done.values()),cyclic=False,orphan_links=0,
        cross_page_reuse_groups={k:sorted(v) for k,v in sorted(groups.items())},
        by_track_nodes={t:sum(r["track"]==t for r in records) for t in parent.TRACKS},
        official_atom_denominators={t:None for t in parent.TRACKS},full_source_census_complete=False,
        teacher_approvals=0,student_authoritative_releases=0,
        editorial_nodes=rows,topological_order=order)
def base():
    inventory=json.loads(parent.OUT.read_text(encoding="utf-8"))
    parent.validate(inventory)
    return inventory
def build():
    return analyze(base()["records"])
def validate(data):
    require(data==build(),"graph audit drift, poisoned edge or invented coverage")
    require(all(r["teacher_review"]=="REVIEW_PENDING" and r["official_atom_id"] is None and
                r["student_authoritative"] is False and r["formal_prerequisite_correctness"]=="UNVERIFIED"
                for r in data["editorial_nodes"]),"invalid authority")
    return True
def render(data):
    lines=["# Batch134｜拟议原子先修DAG与跨页课程复用审计","",
    "**范围限定：仅检查Batch133的41条拟议原子；这不是七轨官方完整知识原子分母，也不代表先修数学合理性已经被教师确认。**",
    "原课标不公开复制。Mac原文哈希由上游私有脚本复查；CI仅复核已提交锁定摘要。",
    f"拟议节点 {data['proposed_nodes']}；拟议直接先修边 {data['proposed_direct_edges']}；无环且无孤儿；最大有向深度 {data['max_dag_depth']}。",
    "正式七轨分母全部 UNKNOWN；教师签字0；学生权威发布0。","",
    "## 可能的课程复用而非重复正式原子", ""]
    for grp,items in data["cross_page_reuse_groups"].items():
        lines.append(f"- {grp}: "+", ".join(items)+ "。仅为项目作者建议的关联，不自动合并。")
    lines+=["","## 全量拟议ID、边界证据、先修建议", ""]
    for r in data["editorial_nodes"]:
        lines.append(f"- {r['candidate_id']} [{r['track']}; {r['category']}] 深度{r['dag_depth']}；先修={','.join(r['prerequisite_candidates']) or '暂无'}；摘要={r['source_span_sha256']}；{r['editorial_relation_decision']}；REVIEW_PENDING。")
    lines+=["","## 后续复核任务", "逐条审查每条建议先修的**数学必要性**与是否已有同义节点；有向无环仅说明结构合法，不意味着课程逻辑正确。完整官方分母需全页课程要求语义拆分与跨页人工裁决后才能冻结。"]
    return "\n".join(lines)+"\n"
def main():
    a=argparse.ArgumentParser();g=a.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    x=a.parse_args()
    if x.write:
        d=build();validate(d);OUT.write_text(parent.stable_json(d),encoding="utf-8")
        MD.write_text(render(d),encoding="utf-8")
    else:
        d=json.loads(OUT.read_text(encoding="utf-8"));validate(d)
        require(MD.read_text(encoding="utf-8")==render(d),"graph report drift")
    print("PASS graph",d["proposed_nodes"],"nodes",d["proposed_direct_edges"],"edges",len(d["cross_page_reuse_groups"]),"reuse groups; official denominators UNKNOWN")
if __name__=="__main__":main()
