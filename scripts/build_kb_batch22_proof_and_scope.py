#!/usr/bin/env python3
"""Fail-closed current proof-review queue and syllabus review denominator dashboard.

Risk tags are ONLY reviewer priorities. Neither automated mathematical proof
certification nor an official/teacher-validated syllabus atomization.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
sys.path.insert(0,str(ROOT))
from app.deep_knowledge import curriculum,lessons
from scripts.kb_frozen_batch24 import frozen_batch24_lessons
from app.official_clause_audit import TRACKS
from app.k00_gap_audit import gap_tickets

BASE=ROOT/'docs/evaluation/KB_PROOF_OBLIGATIONS_BATCH07.json'
PRIOR=ROOT/'docs/evaluation/KB_BATCH21_PROOF_REVIEW_UNION.json'
NEW=ROOT/'knowledge/deep/v1/elective_gap_batch22.json'
LESSON_MATRIX=ROOT/'docs/evaluation/KB_BATCH22_EDITORIAL_TRACK_MATRIX.json'
TASKS=ROOT/'docs/evaluation/KB_BATCH20_K00_REVIEW_QUEUE.json'
PROOFS_OUT=ROOT/'docs/evaluation/KB_BATCH22_UNVERIFIED_PROOF_QUEUE.json'
SCOPE_OUT=ROOT/'docs/evaluation/KB_BATCH22_CURRICULUM_REVIEW_MATRIX.json'
FLAGS={
  'DENOMINATOR_DOMAIN': ('除','分母','非零','>0','正','概率密度','正态','Z>0'),
  'CONDITIONAL_INDEPENDENCE': ('独立','方差','正态','期望','协方差'),
  'GEOMETRY_DEGENERACY': ('旋转','正交','球面','投影','行列式','角'),
  'MODEL_ASSUMPTIONS': ('模型','稳定','实验','经济','统计'),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    base=json.loads(BASE.read_text(encoding='utf8'))
    previous=json.loads(PRIOR.read_text(encoding='utf8'))
    new=json.loads(NEW.read_text(encoding='utf8'))
    course=[x for x in curriculum() if int(x["id"].split("-")[-1])<=173]
    current={x.id:x for x in frozen_batch24_lessons() if not x.id.startswith(("math.hs.batch23.","math.hs.batch24."))}
    historical={x['id'] for x in base['lessons']}
    prior_ids={x['lesson_id'] for x in previous['new_proof_review_queue']}
    b21={r['id'] for r in json.loads((ROOT/'knowledge/deep/v1/elective_gap_batch21.json').read_text(encoding='utf8'))}
    b22={r['id'] for r in new}
    if not(len(historical)==224 and len(b21)==11 and len(b22)==12 and len(current)==247
          and historical.isdisjoint(b21|b22) and b21.isdisjoint(b22)
          and set(current)==historical|b21|b22 and prior_ids.issubset(b21) and len(prior_ids)==6):
        raise ValueError('Unverified proof source union must equal 247 live drafts')
    if previous['summary']['total_current_unverified_proof_steps']!=474:
        raise ValueError('Historical proof queue changed without audit')
    if len(previous['new_proof_review_queue'])!=23 or base['summary']['proof_step_obligations_not_formally_verified']!=451:
        raise ValueError('Historical proof obligations drift')
    if any(x['proof_status']!='NOT_FORMALLY_VERIFIED'
           for x in previous['new_proof_review_queue']):
        raise ValueError('Historical proof falsely certified')
    added=[]
    for doc in new:
        actual=current[doc['id']]
        if doc!=actual.model_dump(mode='json'):
            raise ValueError('Proof queue must match validated knowledge corpus exactly')
        if actual.review.status!='REVIEW_PENDING' or actual.teacher_solution_visibility!='TEACHER_ONLY':
            raise ValueError('Unsafe lesson publication state')
        for idx,step in enumerate(doc['proof_steps'],1):
            joined=step['claim']+'\x00'+step['reason']
            tags=[k for k,terms in FLAGS.items() if any(t in joined for t in terms)]
            added.append(dict(
                id=doc['id']+'#'+str(idx),lesson_id=doc['id'],step_index=idx,
                claim_reason_sha256=hashlib.sha256(joined.encode('utf8')).hexdigest(),
                editorial_priority='P0_HUMAN_ATTENTION' if tags else 'P1_HUMAN_ATTENTION',
                risk_tags=tags or ['GENERAL_PROOF_REVIEW'],proof_status='NOT_FORMALLY_VERIFIED',
                complete_proof_certified=False,teacher_review='PENDING',student_publishable=False))
    expected=sum(len(x['proof_steps']) for x in new)
    if expected!=len(added) or len({x['id'] for x in added})!=len(added):
        raise ValueError('Lost/duplicated proof steps')
    proof=dict(schema_version='batch22-proof-union-v1',scope='REVIEW_ONLY_NOT_FORMAL_VERIFICATION',
        baseline_batch07_sha256=sha(BASE),historical_batch21_sha256=sha(PRIOR),
        new_lesson_source_sha256=sha(NEW),
        summary=dict(current_draft_lessons=247,historical_proof_steps=451,
          batch21_unverified_proof_steps=23,batch22_unverified_proof_steps=len(added),
          total_unverified_proof_steps=474+len(added),
          batch22_priority_counts=dict(sorted(Counter(x['editorial_priority'] for x in added).items())),
          certified_whole_proofs=0,teacher_approved=0,student_steps_verified=0,
          official_atomic_denominator=None),
        new_review_obligations=added,warnings=[
          'Risk tagging is keyword triage, not a mathematical correctness decision.',
          'Historical 451 obligations and Batch21 23 remain frozen without certification.',
          'Even independently verified finite examples cannot validate full proof language.'])
    queue=json.loads(TASKS.read_text(encoding='utf8'))
    author_matrix=json.loads(LESSON_MATRIX.read_text(encoding='utf8'))
    if len(queue['review_queue'])!=427 or queue['summary']['official_atomic_denominator'] is not None:
        raise ValueError('K00 source-review denominator corrupted')
    if any(x['review_status']!='HUMAN_CURRICULUM_AND_MATH_REVIEW_PENDING' or
           x['teacher_approved'] or x['counts_as_verified_atomic_skill']
           for x in queue['review_queue']):
        raise ValueError('Unreviewed K00 task asserted approval')
    course_track=Counter()
    lesson_track=Counter()
    lookup={x['id']:x for x in course}
    for x in course:
        track=x.get('elective_track') if x['level']=='选修拓展' else (
              'COMPULSORY' if x['level']=='必修' else 'SELECTIVE_COMPULSORY'
              if x['level']=='选择性必修' else 'ELECTIVE_UNASSIGNED')
        course_track[track or 'ELECTIVE_UNASSIGNED']+=1
    for x in current.values():
        for cid in x.curriculum_ids:
            c=lookup[cid]
            track=c.get('elective_track') if c['level']=='选修拓展' else (
                'COMPULSORY' if c['level']=='必修' else 'SELECTIVE_COMPULSORY')
            lesson_track[track or 'ELECTIVE_UNASSIGNED']+=1
    marked=Counter(x['track'] for x in author_matrix['tickets'] if x['has_any_editorial_draft'])
    task_track=Counter(x['track'] or 'CROSS_TRACK_PAGE' for x in queue['review_queue'])
    rows=[]
    for track in [*TRACKS,'ELECTIVE_UNASSIGNED']:
        rows.append(dict(track=track,engineering_map_candidates=course_track[track],
          deep_lesson_course_associations=lesson_track[track],
          open_source_review_tasks=task_track[track],
          editor_gap_candidates_with_lesson_adjacency=marked[track],
          verified_official_atomic_denominator=None,teacher_approved_atoms=0,
          complete_official_coverage_rate=None,student_published_deep_units=0))
    dashboard=dict(schema_version='batch22-k00-provisional-denominators-v1',
        scope='UNVERIFIED_EVIDENCE_AND_ENGINEERING_COUNT_NOT_OFFICIAL_ATOM_COUNT',
        source_review_queue_sha256=sha(TASKS),editorial_gap_report_sha256=sha(LESSON_MATRIX),
        proof_review_queue_sha256=None,
        summary=dict(source_review_tasks=427,
          task_denominator_by_kind=queue['summary']['task_counts_by_kind'],
          engineering_candidate_total=len(course),deep_lesson_draft_total=len(current),
          editorial_gap_tickets=28,editorial_drafts_topic_adjacent=23,
          editorial_gaps_still_open=28,official_atomic_denominator=None,
          teacher_approved=0,student_published=0,
          complete_syllabus_inventory=False),
        tracks=rows,
        blockers=[
          'Each numbered source marker may contain multiple requirements, and unnumbered requirements remain.',
          '61 physical pages, 315 numbered marker candidates, 23 unnumbered D/E headings and 28 editorial gap decisions overlap; never add these as official atoms.',
          'All official atomic coverage denominators remain null until independent full syllabus decomposition and teacher review.',
          'Existing 113 catalogue entries are not 113 complete lessons; 173 current engineering candidates include 12 new project-proposed elective candidates.',
        ])
    return (json.dumps(proof,ensure_ascii=False,indent=2)+'\n',
            json.dumps(dashboard,ensure_ascii=False,indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    for path,txt in zip((PROOFS_OUT,SCOPE_OUT),build()):
        if a.check:
            if path.read_text(encoding='utf8')!=txt:
                raise AssertionError(f'Unverified audit drift: {path}')
        else:path.write_text(txt,encoding='utf8')
    print('PASS: 247 draft lessons; new 23 unverified proof steps; 497 total; 427 K00 source tasks; official denominator NULL')

if __name__=='__main__':main()
