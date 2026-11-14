#!/usr/bin/env python3
"""K00 semantic *review queue*: source overlap is not equivalent to course atom equality.

Pins 32 C/D/E provisional proposals against private-source line SHA ledgers.
Tracks without complete syllabus census intentionally retain unknown denominators.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_kb_batch150_de_boundary as upstream
import build_kb_batch152_lessons as lessons
OUT=ROOT/'docs/evaluation/KB_BATCH152_CDE_SEMANTIC_REVIEW.json'
REPORT=ROOT/'docs/evaluation/KB_BATCH152_CDE_SEMANTIC_REVIEW.md'

class GateError(ValueError):pass

def require(ok,why):
 if not ok:raise GateError('KB152 semantic gate: '+why)

def check_upstream(data):
 # No local PDF contents are published; upstream validates the 122 SHA-locked physical line rows.
 require(upstream.validate(data),'upstream unpinned or invalid')
 require(data['approved_atom_denominators']=={t:None for t in lessons.TRACKS},'fraudulent official denominator')
 for p in data['proposals']:
  require(p['curriculum_scope_status']=='EDITORIAL_PROPOSAL_NOT_APPROVED_ATOM','fake atom approval')
  require(p['official_knowledge_atom_id'] is None and not p['teacher_approved'],'fake teacher signoff')
  require(p['mathematical_conditions_review']=='NOT_YET_CHECKED','unearned proof certification')
  require(p['source_track'] in {'ELECTIVE_C','ELECTIVE_D','ELECTIVE_E'},'wrong source owner')
  require(p['source_pdf_sha256']==data['official_pdf_sha256'],'source PDF drift')
 return True

def build(source=None,drafts=None):
 upstream_source=upstream.build()
 source=upstream_source if source is None else source
 check_upstream(source)
 require(source==upstream_source,'source ledger tampered')
 ps=source['proposals']; require(len(ps)==32 and len({p['id'] for p in ps})==32,'32 unique proposals')
 # A line number is not a curricular requirement; multiple elective E examples share one line.
 partition={r['line_id']:r for r in source['source_line_partition']}
 for p in ps:
  require(len(p['source_line_ids'])==len(p['source_line_sha256'])>0,'source provenance missing')
  for lid,digest in zip(p['source_line_ids'],p['source_line_sha256']):
   require(lid in partition and partition[lid]['original_line_sha256']==digest,'source line SHA mismatch')
   require(partition[lid]['classification']==p['source_track'],'cross-track source overlap')
 pairs=[]
 for a,b in combinations(ps,2):
  xa,xb=set(a['source_line_ids']),set(b['source_line_ids']);overlap=xa&xb
  if not overlap:continue
  require(a['source_track']==b['source_track'],'cross-track collision')
  typ='EXACT_SAME_LINE_SET_REVIEW' if xa==xb else 'PARTIAL_LINE_OVERLAP_REVIEW'
  pairs.append(dict(left=a['id'],right=b['id'],source_track=a['source_track'],kind=typ,
    overlap_source_lines=len(overlap),min_source_lines=min(len(xa),len(xb)),
    semantic_duplicate_confirmed=False,teacher_adjudicated=False,
    disposition='HUMAN_REVIEW_REQUIRED_NOT_AUTO_MERGED'))
 drafts=lessons.build() if drafts is None else drafts
 require(lessons.validate(drafts),'invalid draft inventory')
 proposals_by_track=defaultdict(list)
 for p in ps:proposals_by_track[p['source_track']].append(p)
 overlaps=[]
 for d in drafts:
  if d['course_track'] not in proposals_by_track:continue
  own={f'STD2020-SOURCELINE-P{d["source_printed_page"]:02d}-L{i:03d}' for i in range(d['source_start_line'],d['source_end_line']+1)}
  for p in proposals_by_track[d['course_track']]:
   if own.intersection(p['source_line_ids']):
    overlaps.append(dict(draft_id=d['id'],proposal_id=p['id'],source_overlap_lines=len(own.intersection(p['source_line_ids'])),
      teacher_review='REVIEW_PENDING',same_official_requirement_confirmed=False,auto_approved=False))
 count=Counter(p['source_track'] for p in ps)
 risk_count=Counter(x['kind'] for x in pairs)
 return dict(schema='kb152-cde-semantic-overlap-review/1',original_pdf_sha256=source['official_pdf_sha256'],
  source_line_partition_count=len(partition),provisional_semantic_proposals=32,
  proposal_counts_by_track={t:count[t] for t in lessons.TRACKS},
  same_source_review_pairs=pairs,distinct_pair_count=len(pairs),pair_risk_counts=dict(risk_count),
  draft_to_proposal_source_overlaps=overlaps,
  official_atom_denominators={t:None for t in lessons.TRACKS},
  official_census_complete=False,official_course_coverage_rate=None,
  semantic_duplicates_teacher_confirmed=0,auto_merged_atoms=0,teacher_approved=0,student_authoritative=0,
  warning='Line overlap, proposal counts, and manuscripts cannot substitute for full seven-track official syllabus atom census.')

def validate(data):
 require(data==build(),'stored risk queue drift or forged approval')
 return True

def render(d):
 lines=['# Batch152｜选修C/D/E 32项源行关联提案的语义审查队列','',
 '此队列是编辑候选的来源交叠风险，**不是国家课标原子分母**；未经教师核验不作语义去重。','',
 '| 轨道 | 暂定提案 | 是否完成官方原子分母 |','|---|---:|---|']
 for tr in lessons.TRACKS:lines.append(f'| {tr} | {d["proposal_counts_by_track"][tr]} | UNKNOWN |')
 lines+=['',f'有源行交叠的候选对共 {d["distinct_pair_count"]} 对；其中完全相同源行集合 {d["pair_risk_counts"].get("EXACT_SAME_LINE_SET_REVIEW",0)} 对，部分重叠 {d["pair_risk_counts"].get("PARTIAL_LINE_OVERLAP_REVIEW",0)} 对。',
 f'与本批10份深度稿仅凭来源位置相交的关联记录：{len(d["draft_to_proposal_source_overlaps"])} 条。','',
 '以上全部为待人工判断关系，不代表知识同义、知识重复或审校通过。尤其是选修E的示例性方向不能冒充全国必修要求。','',
 '| 提案左 | 提案右 | 课程 | 源行重叠 | 机器分类 | 人工裁决 |','|---|---|---|---:|---|---|']
 for r in d['same_source_review_pairs']:
  lines.append(f'| {r["left"]} | {r["right"]} | {r["source_track"]} | {r["overlap_source_lines"]} | {r["kind"]} | REVIEW_PENDING |')
 lines+=['','**后续人工核对标准**：读取Mac授权原始完整条款和前后跨页语境；判别目标能力、对象、量词、条件与课程选用方式；确认同义才能合并，不同能力必须拆分；保存审查者及校验痕迹。','']
 return '\n'.join(lines)

def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args()
 v=build()
 if a.write: OUT.write_text(lessons.encode(v),encoding='utf-8');REPORT.write_text(render(v),encoding='utf-8')
 else:validate(json.loads(OUT.read_text(encoding='utf-8')));require(REPORT.read_text(encoding='utf-8')==render(v),'review markdown drift')
 print('PASS KB152 32 CDE proposals; source-overlap pairs',v['distinct_pair_count'],'draft-overlaps',len(v['draft_to_proposal_source_overlaps']),'official denominators UNKNOWN')
if __name__=='__main__':main()
