#!/usr/bin/env python3
"""Machine-auditable 300 PROVISIONAL source-label work queue, never official atom denominators.

The frozen editorial statuses remain pending; attaching a deep draft does not
turn it into a human-reviewed or student-approved mathematical fact.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'backend')]
import build_kb_batch93_candidate_triage as B93
import build_kb_batch94_deep_scope as B94
import build_kb_batch95_depth as B95
import build_kb_batch96_depth as B96
import build_kb_batch97_depth as B97
OUT=ROOT/'docs/evaluation/KB_BATCH97_300_CANDIDATE_STATUS.json'
MD=ROOT/'docs/evaluation/KB_BATCH97_300_CANDIDATE_STATUS.md'
STAGES={
 'PAIR_RELATION_EDITORIAL_PENDING':'PAIR_COMPARISON_NOT_ATOMIZED',
 'SINGLE_CANDIDATE_EDITORIAL_PENDING':'INDIVIDUAL_SCOPE_NOT_ATOMIZED',
 'NOT_YET_INDIVIDUALLY_AUDITED':'NO_INDIVIDUAL_EDITORIAL',
}

def guard(c,reason):
    if not c:raise ValueError(reason)

def build(base=None,draft_links=None):
    base=B93.build()['provisional_candidate_ledger'] if base is None else base
    src=B93.read(B93.SOURCES)['provisional_candidate_backlog']
    sources={x['candidate_id']:x for x in src}
    guard(type(base) is list and len(base)==len(src)==300,'frozen 300 source labels required')
    if draft_links is None:
        draft_links=[(94,B94.build()[1]['canonical_lesson_source_links']),
                     (95,B95.build()[1]['canonical_lesson_source_links']),
                     (96,B96.build()[1]['canonical_lesson_source_links']),
                     (97,B97.build()[1]['canonical_lesson_source_links'])]
    guard([len(rows) for _,rows in draft_links]==[14,16,12,12], 'frozen sequential lesson batch sizes')
    links={}
    for batch,items in draft_links:
        for x in items:
            aid=x['source_candidate_id']
            guard(aid not in links and aid in sources,'duplicate or unknown full draft source')
            guard(x['source_line_sha256']==sources[aid]['source_line_sha256'],
                  'source SHA mismatch in deep draft')
            guard(x['official_atom_id'] is None and not x['teacher_approved'] and not x['student_publishable'],
                  'a deep draft cannot grant human approval or official atom id')
            links[aid]=(batch,x['lesson_id'])
    guard(len(links)==54,'42 distinct editor draft sources required')
    rows=[]
    for candidate in base:
        cid=candidate['candidate_id']
        guard(cid in sources and candidate['source_line_sha256']==sources[cid]['source_line_sha256'],
              'unknown or corrupted source candidate SHA')
        src_row=sources[cid]
        state=candidate['scope_audit_state']
        guard(state in STAGES,'unknown source audit status')
        if cid in links:
            guard(state=='NOT_YET_INDIVIDUALLY_AUDITED',
                'deep draft must be a formerly individual-unaudited provisional candidate')
            batch,lesson_id=links[cid]
            stage='FULL_DEEP_DRAFT_PENDING_TEACHER'
        else:
            batch=lesson_id=None
            stage=STAGES[state]
        rows.append({'candidate_id':cid,'provisional_topic':src_row['provisional_topic'],
            'track':src_row['track'],'source_page':src_row['source_page'],
            'source_review_id':src_row['source_review_id'],
            'source_line_sha256':src_row['source_line_sha256'],
            'editorial_stage':stage,'deep_draft_batch':batch,'deep_lesson_id':lesson_id,
            'official_atom_id':None,'teacher_review_status':'REVIEW_PENDING',
            'teacher_approval':None,'student_authoritative_index_eligible':False})
    guard(len({x['candidate_id'] for x in rows})==300,'duplicate source candidate')
    counts=Counter(x['editorial_stage'] for x in rows)
    guard(counts==Counter({'PAIR_COMPARISON_NOT_ATOMIZED':166,
                 'INDIVIDUAL_SCOPE_NOT_ATOMIZED':24,
                 'NO_INDIVIDUAL_EDITORIAL':56,
                 'FULL_DEEP_DRAFT_PENDING_TEACHER':54}),
          'regressed/falsely completed provisional denominator')
    tracks={t: {'provisional_source_labels':sum(r['track']==t for r in rows),
                 'official_math_atom_denominator':None,
                 'teacher_reviewed_atom_count':0,
                 'status_counts':dict(sorted(Counter(r['editorial_stage'] for r in rows if r['track']==t).items()))}
            for t in B93.TRACKS}
    guard(sum(x['provisional_source_labels'] for x in tracks.values())==300,
          'seven track matrix must account for all candidates')
    return {'schema_version':'kb97-provisional-source-stage-matrix-v1',
        'scope':'PROJECT_PROVISIONAL_LABELS_NOT_OFFICIAL_CURRICULUM_ATOMS',
        'standard':'普通高中数学课程标准（2017年版2020年修订）',
        'frozen_candidate_source_sha256':sha256(B93.SOURCES.read_bytes()).hexdigest(),
        'official_atom_denominator':None,
        'official_atom_denominators_by_track':{t:None for t in B93.TRACKS},
        'human_full_page_atomization':'0/61',
        'student_authoritative_release':0,'teacher_approved':0,
        'provisional_source_labels':len(rows),'editorial_stages':dict(sorted(counts.items())),
        'track_matrix':tracks,'candidates':rows}

def markdown(result):
    out=['# Batch97｜300个项目临时主题的逐项审计状态（**非官方课标原子分母**）','',
         '所有课程轨道的正式原子分母仍为 UNKNOWN；教师逐页原子化 0/61、批准0、学生权威发布0。',
         '“FULL_DEEP_DRAFT_PENDING_TEACHER”只表示存在结构化原创草案，绝不代表教师审查完成。','',
         '| 项目编辑状态 | 临时主题数 |','|---|---:|']
    out += [f'| {name} | {n} |' for name,n in result['editorial_stages'].items()]
    out += ['','| 轨道 | 临时来源标签 | 官方数学知识原子数 |','|---|---:|---|']
    for t,v in result['track_matrix'].items():
        out += [f"| {t} | {v['provisional_source_labels']} | UNKNOWN（未核实） |"]
    out += ['','每个临时标签的来源ID、轨道、来源页、SHA及编辑状态请查阅配套JSON。','',
            '不得将关系比较、主题标签或已写的讲义直接计作独立官方课标知识原子；跨页语义去重、教师逐页复核、内容真实性审查仍需完成。']
    return '\n'.join(out)+'\n'

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    out=build();files={OUT:json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+'\n',MD:markdown(out)}
    for path,txt in files.items():
        if a.check:guard(path.is_file() and path.read_text()==txt,'generated source matrix drift')
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(txt)
    print('BATCH97 candidate audit:',out['provisional_source_labels'],'stages=',out['editorial_stages'], 'CHECK' if a.check else 'WRITTEN')

if __name__=='__main__':main()
