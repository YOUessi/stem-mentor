#!/usr/bin/env python3
"""Batch23 fail-closed author-to-corpus reconciliation, proof queue and K00 dashboard.

No curriculum atom denominator, whole-proof certification, teacher approval or student publication.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.deep_knowledge import DeepLesson, curriculum, lessons
from app.k00_gap_audit import gap_tickets
from app.official_clause_audit import TRACKS

AUTHOR=ROOT/'curriculum/highschool_math/author_draft_batch23.json'
MAP=ROOT/'curriculum/highschool_math/engineering_gap_candidates_batch23.json'
PRIOR=ROOT/'docs/evaluation/KB_BATCH22_UNVERIFIED_PROOF_QUEUE.json'
SCOPE=ROOT/'docs/evaluation/KB_BATCH22_CURRICULUM_REVIEW_MATRIX.json'
GAP_PRIOR=ROOT/'docs/evaluation/KB_BATCH22_EDITORIAL_TRACK_MATRIX.json'
QUEUE=ROOT/'docs/evaluation/KB_BATCH20_K00_REVIEW_QUEUE.json'
OUT=ROOT/'knowledge/deep/v1/core_elective_batch23.json'
AUDIT=ROOT/'docs/evaluation/KB_BATCH23_INTEGRITY_AND_SCOPE.json'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def build():
    draft=json.loads(AUTHOR.read_text(encoding='utf8'))
    mapping=json.loads(MAP.read_text(encoding='utf8'))
    past=json.loads(PRIOR.read_text(encoding='utf8'))
    past_scope=json.loads(SCOPE.read_text(encoding='utf8'))
    past_gaps=json.loads(GAP_PRIOR.read_text(encoding='utf8'))
    queue=json.loads(QUEUE.read_text(encoding='utf8'))
    tickets={int(x['id'][-3:]):x for x in gap_tickets()['tickets']}
    current={x['id']:x for x in curriculum()}
    if len(draft)!=20 or len(mapping)!=5 or len(current)!=178:
        raise ValueError('Expected 20 authored drafts, 5 elective links, 178 engineering candidates')
    if len({x['lesson']['id'] for x in draft})!=20 or len({x['tag'] for x in draft})!=20:
        raise ValueError('Duplicated lesson or original author tag')
    if past['summary']['total_unverified_proof_steps']!=497 or past_scope['summary']['deep_lesson_draft_total']!=247:
        raise ValueError('Historical proof/curriculum snapshots changed without review')
    if len(queue['review_queue'])!=427 or queue['summary']['official_atomic_denominator'] is not None:
        raise ValueError('Unresolved official scope review tasks changed')
    if any(x['review_status']!='HUMAN_CURRICULUM_AND_MATH_REVIEW_PENDING'
           or x['teacher_approved'] or x['counts_as_verified_atomic_skill'] for x in queue['review_queue']):
        raise ValueError('Unreviewed course source asserted authority')
    if len(tickets)!=28 or len(past_gaps['tickets'])!=28:
        raise ValueError('Unresolved editorial source inventory changed')
    map_by_id={m['id']:m for m in mapping}
    if set(map_by_id)!={f'HS-MATH-{i}' for i in range(174,179)}:
        raise ValueError('Elective candidate IDs changed')
    for m in mapping:
        if current[m['id']]!=m or m['source']['teacher_review']!='PENDING' or m['source']['mapping_type']!='ENGINEERING_INTERPRETATION' or m['status']!='PLANNED':
            raise ValueError('Elective map drift or fictitious authority')
    rendered=[];added_proof=[];new_elective={};kind_counts=Counter();core_ids=[]
    for row in draft:
        lesson=DeepLesson.model_validate(row['lesson'])
        doc=lesson.model_dump(mode='json')
        if doc!=row['lesson'] or lesson.review.status!='REVIEW_PENDING' or lesson.teacher_solution_visibility!='TEACHER_ONLY':
            raise ValueError('Authored data drift or teaching permission violation')
        if any((lesson.review.reviewer_id,lesson.review.reviewed_at,lesson.review.review_record)):
            raise ValueError('Fake independent teacher approval evidence')
        if len(lesson.curriculum_ids)!=1 or not(lesson.worked_examples and len(lesson.worked_examples)==2 and len(lesson.hint_ladder)==3):
            raise ValueError('No ambiguous multi-topic or missing problem-family evidence')
        cid=lesson.curriculum_ids[0]
        if cid not in current or current[cid]['source']['teacher_review']!='PENDING':
            raise ValueError('Unknown/unapproved curriculum mapping')
        if row['gap'] is not None:
            n=row['gap']
            if n not in {18,19,23,24,26} or n in new_elective:
                raise ValueError('Gap needs exact per-ticket association')
            if cid not in map_by_id or current[cid]['elective_track']!=tickets[n]['track']:
                raise ValueError('Wrong elective track or ID')
            if current[cid]['editorial_objective_id']!=f'EDITORIAL-GAP-{n:03d}':
                raise ValueError('Bad elective objective provenance')
            new_elective[n]=lesson.id
        else:
            if cid in map_by_id or current[cid]['level'] not in ('必修','选择性必修'):
                raise ValueError('Core subskill must reuse existing required-track mapping')
            core_ids.append(cid)
        kind_counts[lesson.kind]+=1
        if any(x.steps[0]==x.steps[1] or '。。' in ''.join(x.steps) for x in lesson.worked_examples):
            raise ValueError('Duplicated or corrupted solution steps')
        rendered.append(doc)
        for i,step in enumerate(lesson.proof_steps,1):
            joined=step.claim+'\x00'+step.reason
            added_proof.append(dict(id=lesson.id+'#'+str(i),
                content_sha256=hashlib.sha256(joined.encode('utf8')).hexdigest(),
                review_priority='P0_REVIEW_IF_DOMAIN_OR_EQUIVALENCE_MISSING',
                status='NOT_FORMALLY_VERIFIED',whole_theorem_certified=False,
                human_teacher_review='PENDING',student_publishable=False))
    if set(new_elective)!={18,19,23,24,26} or len(core_ids)!=15:
        raise ValueError('Core/elective allocation changed')
    prev_by_ticket={int(x['ticket_id'][-3:]):x for x in past_gaps['tickets']}
    editorial=[]
    for n in range(1,29):
        prior=prev_by_ticket[n]
        if prior['ticket_status']!='OPEN_EDITORIAL_CANDIDATE_NOT_PROVEN_MISSING':
            raise ValueError('Unexpected prior editorial ticket closure')
        editorial.append(dict(ticket_id=prior['ticket_id'],track=prior['track'],
            prior_draft_topic_adjacency=prior['has_any_editorial_draft'],
            new_lesson_id=new_elective.get(n),
            has_any_project_draft=prior['has_any_editorial_draft'] or n in new_elective,
            ticket_status='OPEN_EDITORIAL_CANDIDATE_NOT_PROVEN_MISSING',
            verified_official_clause_equivalence=False,
            teacher_review='PENDING',official_atom=False,student_publishable=False))
    if sum(x['has_any_project_draft'] for x in editorial)!=28:
        raise ValueError('Unexpected draft adjacency count')
    current_lessons={d.id:d for d in lessons() if not d.id.startswith("math.hs.batch24.")}
    # This build can be invoked before materialization; validate the source without pretending it is live.
    if OUT.exists():
        if len(current_lessons)!=267 or any(current_lessons.get(x['id']) is None or current_lessons[x['id']].model_dump(mode='json')!=x for x in rendered):
            raise ValueError('Expected 267 live deep draft lessons')
    scope=dict(schema_version='batch23-scope-v1',
        source_audit_tasks=427,source_review_kinds=queue['summary']['task_counts_by_kind'],
        engineering_candidate_total=len(current),required_core_subskills_added=15,
        elective_editorial_candidates_added=5,deep_lesson_drafts_expected=267,
        existing_deep_lesson_drafts=247,editorial_gap_candidates=28,
        draft_nearby_gap_candidates=28,editorial_gap_tickets_still_open=28,
        full_official_atom_inventory=False,official_atomic_denominator=None,
        approved_teacher_knowledge=0,official_coverage_rate=None,
        student_deep_lessons_released=0)
    by_track=Counter()
    for row in current.values():
        level=row['level']
        key=(row['elective_track'] if level=='选修拓展' and 'elective_track' in row else
             'ELECTIVE_UNASSIGNED' if level=='选修拓展' else
             'COMPULSORY' if level=='必修' else 'SELECTIVE_COMPULSORY')
        by_track[key]+=1
    audit=dict(schema_version='batch23-unverified-source-and-math-v1',
        scope='ENGINEERING_DRAFT_NOT_VERIFIED_OFFICIAL_COVERAGE_OR_MATHEMATICS',
        frozen_source=dict(batch22_proof_sha256=sha(PRIOR),batch22_k00_sha256=sha(SCOPE),
            author_sha256=sha(AUTHOR),curriculum_map_sha256=sha(ROOT/'curriculum/highschool_math/curriculum_map.json'),
            k00_review_queue_sha256=sha(QUEUE)),
        summary=scope,new_by_type=dict(sorted(kind_counts.items())),
        new_by_course_level=dict(sorted(Counter(current[x['curriculum_ids'][0]]['level'] for x in rendered).items())),
        engineering_candidates_by_track=dict(sorted(by_track.items())),
        new_core_existing_course_ids=core_ids,new_elective_ticket_ids=sorted(new_elective),
        new_teacher_only_example_count=sum(len(x['worked_examples']) for x in rendered),
        new_proof_unverified=len(added_proof),historical_unverified_proof_steps=497,
        current_unverified_proof_steps=497+len(added_proof),
        certified_whole_proofs=0,teacher_approved=0,
        source_review_tasks_preserved=427,
        new_proof_review_queue=added_proof,editorial_ticket_review=editorial,
        official_tracks=[dict(track=track,project_engineering_candidate_count=by_track[track],
            verified_official_atomic_denominator=None,
            verified_official_coverage_rate=None,review_status='PENDING')
            for track in (*TRACKS,'ELECTIVE_UNASSIGNED')],
        warnings=[
            'All 28 ticket-adjacent drafts remain OPEN; topic adjacency never constitutes evidence of curriculum coverage.',
            'The 427 page/marker/heading/editorial tasks overlap; this is NOT an official atom denominator.',
            'A proof step claim/reason hash preserves provenance; it does NOT certify mathematical validity.',
            'Teacher approval and free-text student validation remain disabled; only teacher-only drafts are indexed.'])
    return json.dumps(rendered,ensure_ascii=False,indent=2)+'\n',json.dumps(audit,ensure_ascii=False,indent=2)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    for path,body in zip((OUT,AUDIT),build()):
        if args.check:
            if path.read_text(encoding='utf8')!=body:raise ValueError(f'Batch23 output drift: {path}')
        else:path.write_text(body,encoding='utf8')
    print('PASS: 20 new lessons, 5 editorial-near gaps still open; official denominator NULL')
