#!/usr/bin/env python3
"""Validate and materialize twelve editorial DRAFT lessons, with K00 provenance."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.deep_knowledge import DeepLesson, curriculum
from app.k00_gap_audit import gap_tickets

AUTHOR=ROOT/'curriculum/highschool_math/author_draft_batch22.json'
MAP=ROOT/'curriculum/highschool_math/engineering_gap_candidates_batch22.json'
B21=ROOT/'docs/evaluation/KB_BATCH21_EDITORIAL_GAP_OVERLAPS.json'
OUTPUT=ROOT/'knowledge/deep/v1/elective_gap_batch22.json'
REPORT=ROOT/'docs/evaluation/KB_BATCH22_EDITORIAL_TRACK_MATRIX.json'
EXPECTED_GAPS={4,5,7,8,9,13,15,16,21,22,25,28}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    authors=json.loads(AUTHOR.read_text(encoding='utf-8'))
    added=json.loads(MAP.read_text(encoding='utf-8'))
    previous=json.loads(B21.read_text(encoding='utf-8'))
    gaps={int(x['id'][-3:]):x for x in gap_tickets()['tickets']}
    course={x['id']:x for x in curriculum() if int(x['id'].split('-')[-1])<=173}
    assert len(course)==173
    assert len(authors)==len(added)==12
    if {x['gap'] for x in authors}!=EXPECTED_GAPS or len({x['lesson']['id'] for x in authors})!=12:
        raise ValueError('Batch22 must have twelve distinct editorial gaps and lessons')
    prior={int(x['gap_ticket'][-3:]) for x in previous['ticket_status'] if x['editorial_draft_lesson_id']}
    if prior & EXPECTED_GAPS or len(prior)!=11:
        raise ValueError('Batch21 overlap source changed')
    valid=[]
    counts=Counter()
    map_by_id={x['id']:x for x in added}
    if len(map_by_id)!=12:
        raise ValueError('Duplicate new curriculum map ids')
    associations={}
    for a in authors:
        g=gaps[a['gap']]
        lesson=DeepLesson.model_validate(a['lesson'])
        if lesson.review.status!='REVIEW_PENDING' or lesson.teacher_solution_visibility!='TEACHER_ONLY':
            raise ValueError('No teacher-approved/student-publication without evidence')
        if any([lesson.review.reviewer_id,lesson.review.reviewed_at,lesson.review.review_record]):
            raise ValueError('Fabricated reviewer signature')
        if len(lesson.curriculum_ids)!=1:
            raise ValueError('No unverified multi-course mapping')
        c=map_by_id[lesson.curriculum_ids[0]]
        if c!=course[c['id']] or c['elective_track']!=g['track']:
            raise ValueError('Course-map drift or wrong elective track')
        if c['editorial_objective_id']!=f"EDITORIAL-GAP-{a['gap']:03d}":
            raise ValueError('Untraceable source-scope association')
        if len(lesson.worked_examples)!=2 or len(lesson.hint_ladder)!=3:
            raise ValueError('Problem-family quality gate missing')
        counts[g['track']]+=1
        associations[a['gap']]=(lesson.id,c['id'])
        valid.append(lesson.model_dump(mode='json'))
    rows=[]
    for g in gap_tickets()['tickets']:
        n=int(g['id'][-3:])
        from21=next((x['editorial_draft_lesson_id'] for x in previous['ticket_status'] if x['gap_ticket']==g['id']),None)
        associated=associations.get(n)
        rows.append(dict(ticket_id=g['id'],track=g['track'],printed_page=g['printed_page'],
            source_page_text_sha256=g['source_page_text_sha256'],
            historical_batch21_lesson=from21,
            batch22_lesson_id=associated[0] if associated else None,
            batch22_engineering_course_id=associated[1] if associated else None,
            has_any_editorial_draft=bool(from21 or associated),
            ticket_status=g['gap_status'],teacher_review='PENDING',
            verified_source_clause_equivalence=False,official_atomic_knowledge_unit=False,
            formal_proof_certified=False,student_publishable=False))
    c=Counter(x['track'] for x in rows if x['has_any_editorial_draft'])
    missing=[x['ticket_id'] for x in rows if not x['has_any_editorial_draft']]
    report=dict(schema_version='batch22-editorial-matrix-v1',
        scope='EDITORIAL_DRAFT_NEARNESS_NOT_VERIFIED_OFFICIAL_CURRICULUM',
        source_pdf_sha256=gap_tickets()['source_pdf_sha256'],
        batch21_snapshot_sha256=sha(B21),author_sha256=sha(AUTHOR),map_sha256=sha(MAP),
        summary=dict(open_editorial_tickets=28,batch21_adjacencies=11,
          batch22_new_adjacencies=12,combined_adjacencies=23,
          not_yet_adjacent=5,not_yet_adjacent_ids=missing,
          new_by_track=dict(sorted(counts.items())),
          cumulative_by_track=dict(sorted(c.items())),
          engineering_map_total=len(course),
          official_atomic_denominator=None,
          official_coverage_rate=None,teacher_approved=0,formal_proofs_certified=0,
          student_deep_lessons_released=0),
        tickets=rows,warnings=[
            'All 28 editorial gap tickets remain open; even 23 nearby drafts do NOT close them.',
            'Physical source-page hashes are source tracking only, not a line-level official clause audit.',
            'Human syllabus atomization, mathematical review and teacher signing remain pending.',
        ])
    return (json.dumps(valid,ensure_ascii=False,indent=2)+'\n',
            json.dumps(report,ensure_ascii=False,indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    outputs=list(zip((OUTPUT,REPORT),build()))
    for path,txt in outputs:
        if a.check:
            if path.read_text(encoding='utf8')!=txt:raise ValueError(f'Batch22 drift: {path}')
        else:
            path.write_text(txt,encoding='utf8')
    print('PASS: 12 REVIEW_PENDING lessons, 23/28 editorial overlaps; official denominator remains null')

if __name__=='__main__':main()
