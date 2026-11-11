#!/usr/bin/env python3
"""Conservative K00/K01/K08/K09 integrator: cumulative editorial counts, no authority."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch101_review_queue as QUEUE
import build_kb_batch101_math_pairs as MATH
OUT=ROOT/"docs/evaluation/KB_BATCH101_COVERAGE_GATES.json"
MD=ROOT/"docs/evaluation/KB_BATCH101_COVERAGE_GATES.md"

def check(ok,msg):
    if not ok:raise ValueError(msg)

def build(queue=None,math=None):
    queue=QUEUE.build() if queue is None else queue
    math=MATH.build() if math is None else math
    QUEUE.validate_report(queue)
    MATH.validate(math)
    formerly_unpaired={r["source_candidate_id"]:r for r in queue["semantic_pair_reviewer_queue"]}
    new_pairs=math["editorial_pairs"]
    paired_ids=[p["left_source_candidate_id"] for p in new_pairs]
    check(len(paired_ids)==len(set(paired_ids))==20
          and all(x in formerly_unpaired for x in paired_ids),"new math comparisons not from unpaired source")
    still_unpaired=set(formerly_unpaired)-set(paired_ids)
    check(len(still_unpaired)==114,"unpaired queue conservation changed")
    source=QUEUE.source_read(QUEUE.SOURCE)["provisional_candidate_backlog"]
    by_track=Counter(r["track"] for r in source)
    old=QUEUE.source_read(QUEUE.PREV)
    oldpaired=set(r["candidate_id"] for r in source)-set(old["remaining_unpaired_candidate_ids"])
    check(len(oldpaired)==166,"historical paired labels drift")
    check(not oldpaired & set(paired_ids) and len(oldpaired | set(paired_ids))==186,
          "double counted editorial comparisons")
    tracks={}
    for t in QUEUE.TRACKS:
        new=sum(p["left_track"]==t for p in new_pairs)
        historic=sum(r["track"]==t and r["candidate_id"] in oldpaired for r in source)
        outstanding=sum(formerly_unpaired[k]["source_track"]==t for k in still_unpaired)
        check(historic+new+outstanding==by_track[t],"seven-track conservation "+t)
        tracks[t]={
          "provisional_project_labels":by_track[t],
          "editorially_compared_prior":historic,
          "newly_authored_math_comparisons":new,
          "remaining_without_pairwise_editorial":outstanding,
          "official_curriculum_atom_denominator":None,
          "formal_teacher_atom_memberships":0,
          "teacher_approved_lessons":0,
          "student_authoritative_release":0
        }
    check(sum(t["provisional_project_labels"] for t in tracks.values())==300,
          "300 provisional labels incomplete")
    pages=queue["page_evidence"]
    return {
      "schema_version":"kb101-cumulative-conservative-coverage-v1",
      "source_status":"PROJECT_PROVISIONAL_LABELS_NOT_OFFICIAL_ATOMS",
      "source_sha256":QUEUE.digest(QUEUE.SOURCE),
      "math_pair_artifact_sha256":QUEUE.digest(MATH.OUT),
      "review_queue_artifact_sha256":QUEUE.digest(QUEUE.OUT),
      "official_curriculum_standard":"普通高中数学课程标准（2017年版2020年修订）",
      "official_atom_denominator":None,
      "official_atom_denominators_by_track":{t:None for t in QUEUE.TRACKS},
      "provisional_project_labels":300,
      "originally_editorially_compared":166,
      "newly_math_compared_this_batch":20,
      "cumulative_editorially_compared_labels":186,
      "remaining_without_pairwise_editorial":114,
      "final_teacher_semantic_equivalence_adjudications":0,
      "full_official_source_pages":61,
      "source_anchor_lines":428,
      "pages_with_no_project_source_anchors":[p["printed_page"] for p in pages if not p["project_anchor_count"]],
      "fully_human_atomized_pages":0,
      "drafts_pending_teacher":86,
      "textual_prerequisite_notes":172,
      "unresolved_textual_prerequisites":172,
      "candidate_only_prerequisite_edges_promoted":0,
      "semantic_manual_search_required":queue["semantic_manual_search_required"],
      "prerequisite_manual_search_required":queue["prerequisite_manual_search_required"],
      "finite_math_instance_comparisons":20,
      "general_mathematical_proofs_certified_this_batch":0,
      "teacher_approved":0,
      "student_authoritative_release":0,
      "track_matrix":tracks,
      "proof_steps_unverified_legacy":538,
      "math_conflicts_unresolved_legacy":10,
      "next_work":"Complete 114 unpaired semantic source comparisons and the 61-page official atomization; review all 172 textual prerequisite relations with domain experts; expand full lessons, teacher proof certificates and safe retrieval."
    }

def validate(result):
    check(result["provisional_project_labels"]==
          result["originally_editorially_compared"]+
          result["newly_math_compared_this_batch"]+
          result["remaining_without_pairwise_editorial"]==300,
          "provisional coverage arithmetic invalid")
    check(result["newly_math_compared_this_batch"]==20
          and result["cumulative_editorially_compared_labels"]==186
          and result["remaining_without_pairwise_editorial"]==114,
          "editorial comparison count invalid")
    check(result["official_atom_denominator"] is None
          and all(v is None for v in result["official_atom_denominators_by_track"].values())
          and result["fully_human_atomized_pages"]==0,
          "official count fabricated")
    check(result["teacher_approved"]==result["student_authoritative_release"]==0
          and result["candidate_only_prerequisite_edges_promoted"]==0
          and result["final_teacher_semantic_equivalence_adjudications"]==0
          and result["general_mathematical_proofs_certified_this_batch"]==0,
          "authority promotion not allowed")
    check(result["textual_prerequisite_notes"]==result["unresolved_textual_prerequisites"]==172,
          "unreviewed prereq count mismatch")
    check(len(result["track_matrix"])==7
          and all(v["official_curriculum_atom_denominator"] is None and
                  v["editorially_compared_prior"]+v["newly_authored_math_comparisons"]+
                  v["remaining_without_pairwise_editorial"]==v["provisional_project_labels"]
                  for v in result["track_matrix"].values()),"per-track conservation failure")

def markdown(x):
    out=["# Batch101｜七轨暂定主题与审核门禁真实累计覆盖","",
         "**重要：** 正式课标原子分母仍不可审计，下面300仅是内部来源临时主题；186项仅指成对编辑比较草案，绝非186份教师认可的原子或正式讲义。","",
         "|关键指标|累计|","|---|---:|",
         "|项目临时主题|300|",
         "|以前已作成对编辑比较|166|",
         "|本批新增具有数学区别/前提/反例的编辑比较|20|",
         "|累计成对编辑比较|186|",
         "|仍未做成对编辑比较|114|",
         "|正式课程逐页教师原子化|0/61|",
         "|源行锚点|428|",
         f"|来源页没有工程锚点|{x['pages_with_no_project_source_anchors']}|",
         "|待审深度讲义|86|",
         "|仍未认可的文本先修|172|",
         f"|语义候选需要人工跨领域发现|{x['semantic_manual_search_required']}|",
         f"|先修候选需要人工跨领域发现|{x['prerequisite_manual_search_required']}|",
         "|本批受控数学算例对比|20|",
         "|教师认可/学生权威发布|0/0|","",
         "|工程七轨|工程临时主题|既有编辑比较|新增数学比较|剩余未比较|官方原子分母|",
         "|---|---:|---:|---:|---:|---|"]
    for k,v in x["track_matrix"].items():
        out.append(f"|{k}|{v['provisional_project_labels']}|{v['editorially_compared_prior']}|{v['newly_authored_math_comparisons']}|{v['remaining_without_pairwise_editorial']}|UNKNOWN|")
    out+=["","**严禁误用：** 词面推荐仅用于辅助分配教研审查工作，不生成正式先修边、不输出教师解答、不宣称一般数学证明或官方原子合并。","",
          "**后续：** 114项未比较临时主题、61页完整教师原子化、172条先修、538条历史证明及10项冲突；以真实教学审核为准。",""]
    return "\n".join(out)

def run(check_only=False):
    result=build();validate(result)
    files={OUT:json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",
           MD:markdown(result)}
    for p,v in files.items():
        if check_only:check(p.read_text(encoding="utf8")==v,"cumulative coverage artifact drift")
        else:p.write_text(v,encoding="utf8")
    print("BATCH101 COVERAGE 166+20+114=300; unapproved prereq=172; teacher 0; check",check_only)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    run(p.parse_args().check)
