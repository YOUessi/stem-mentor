"""Batch132: original Mac source, offline scope, independent SymPy, teacher-only negative gates."""
import copy,hashlib,json,os,sys
from functools import lru_cache
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'backend')]
import build_kb_batch132_electives as scope
import build_kb_batch132_lessons as deep
from app.deep_knowledge import public_summary
D=json.loads(scope.OUT.read_text(encoding='utf-8'))
L=json.loads(scope.LOCK.read_text(encoding='utf-8'))
LESSONS=json.loads(deep.OUT.read_text(encoding='utf-8'))
ORACLE=json.loads(deep.ORACLE.read_text(encoding='utf-8'))
@lru_cache(maxsize=1)
def pages():return scope.prior.previous.prev.prior.prior.previous.source_pages()
@pytest.mark.parametrize('record',D['records'],ids=lambda x:x['candidate_id'])
def test_39_elective_historical_candidates_guard_context(record):
    k=record['candidate_id'];s=k.removeprefix('hs-semantic-pilot-')
    assert record['source_lock']==L[k]
    assert record['contextual_interpretation']==scope.R[s][0]
    assert record['boundary_or_counterexample']==scope.R[s][1]
    assert record['teacher_review_status']=='REVIEW_PENDING'
    assert record['teacher_signature'] is None
    assert record['official_atom_id'] is None
    assert record['student_authoritative'] is False
    assert record['mathematics_formally_certified'] is False
    assert record['source_evidence_status']=='ORIGINAL_LINE_HASH_CHECKED_EDITORIAL_INTERPRETATION_PENDING'
@pytest.mark.parametrize('record',D['records'],ids=lambda x:x['candidate_id'])
def test_39_source_line_hashes_recomputed_only_on_mac(record):
    if os.getenv('GITHUB_ACTIONS')=='true':
        pytest.skip('licensed original source cached only on Mac; CI validates committed digests, not source original')
    k=record['candidate_id'];lk=record['source_lock']
    lines=pages()[lk['page']][lk['start_line']-1:lk['end_line']]
    assert len(lines)==len(lk['line_sha256'])
    assert [hashlib.sha256(x.encode()).hexdigest() for x in lines]==lk['line_sha256']
    assert hashlib.sha256('\n'.join(lines).encode()).hexdigest()==lk['span_sha256']
@pytest.mark.parametrize('lesson',LESSONS,ids=lambda d:d['id'])
def test_8_deep_original_teacher_manuscripts(lesson):
    assert lesson['teacher_review_status']=='REVIEW_PENDING'
    assert lesson['teacher_solution_visibility']=='TEACHER_ONLY'
    assert lesson['teacher_review_evidence'] is None
    assert lesson['student_authoritative'] is False
    assert lesson['formal_proof_certified'] is False
    assert lesson['free_student_step_verified'] is False
    assert lesson['source_line_lock']==L[lesson['candidate_id']]
    assert len(lesson['reasoned_steps'])>=3
    assert all('justification' in step and 'step' in step for step in lesson['reasoned_steps'])
    assert len(lesson['teacher_examples'])==2
    assert all(len(e['reasoned_solution'])>=3 for e in lesson['teacher_examples'])
    assert len(lesson['student_hint_ladder'])==3
    assert lesson['near_transfer']!=lesson['far_transfer']
@pytest.mark.parametrize('lesson',LESSONS,ids=lambda d:d['id'])
def test_8_recomputed_independent_oracle_pairs_and_invalid_condition(lesson):
    k=lesson['candidate_id'].removeprefix('hs-semantic-pilot-')
    computed=deep.math_oracles()
    assert computed['example_results'][k]==[True,True]
    assert computed['counterexample_results'][k] is True
    assert ORACLE==computed
@pytest.mark.parametrize('record',LESSONS,ids=lambda d:d['id'])
def test_8_student_hints_have_no_full_teacher_answers(record):
    hints=' '.join(record['student_hint_ladder'])
    assert record['teacher_solution_visibility']=='TEACHER_ONLY'
    assert record['teacher_examples'][0]['answer'] not in hints
    assert record['teacher_examples'][1]['answer'] not in hints
@pytest.mark.parametrize('mutation',[
    lambda d:d.update(historical_editorial_candidates=200),
    lambda d:d.update(new_context_reviews=40),
    lambda d:d.update(context_reviewed_total=238),
    lambda d:d.update(remaining_context_reviews=1),
    lambda d:d.update(curriculum_layout_cues=239),
    lambda d:d.update(official_atom_denominator=239),
    lambda d:d.update(student_authoritative=1),
    lambda d:d.update(teacher_approved=1),
    lambda d:d.update(source_pdf_text_embedded=True),
    lambda d:d.update(scope='OFFICIAL_ATOM_CENSUS'),
    lambda d:d['track_official_atom_denominators'].update(ELECTIVE_A=30),
    lambda d:d['count_by_track']['ELECTIVE_A'].update(official_atom_denominator=30),
    lambda d:d['count_by_track']['ELECTIVE_A'].update(not_checked=1),
    lambda d:d['records'][0].update(teacher_review_status='APPROVED'),
    lambda d:d['records'][0].update(teacher_signature='imagined reviewer'),
    lambda d:d['records'][0].update(official_atom_id='fake'),
    lambda d:d['records'][0].update(student_authoritative=True),
    lambda d:d['records'][0].update(mathematics_formally_certified=True),
    lambda d:d['records'][0].update(source_evidence_status='OFFICIAL_CERTIFIED'),
    lambda d:d['records'][0].update(contextual_interpretation='bad'),
    lambda d:d['records'][0]['source_lock'].update(span_sha256='0'*64),
    lambda d:d['records'][0]['source_lock']['line_sha256'].pop(),
    lambda d:d['records'].pop(),
    lambda d:d['records'].append(copy.deepcopy(d['records'][0])),
])
def test_24_forged_scope_rejections(mutation):
    d=copy.deepcopy(D);mutation(d)
    with pytest.raises((ValueError,KeyError,TypeError)):
        scope.validate(d,L)
@pytest.mark.parametrize('mutation',[
    lambda d:d[0].update(teacher_review_status='APPROVED'),
    lambda d:d[0].update(teacher_review_evidence={'reviewer':'invented'}),
    lambda d:d[0].update(student_authoritative=True),
    lambda d:d[0].update(formal_proof_certified=True),
    lambda d:d[0].update(free_student_step_verified=True),
    lambda d:d[0].update(teacher_solution_visibility='STUDENT'),
    lambda d:d[0].update(source_line_lock={'page':1}),
    lambda d:d[0].update(teacher_examples=[]),
    lambda d:d[0]['teacher_examples'][0]['reasoned_solution'].pop(),
    lambda d:d[0].update(student_hint_ladder=['just one']),
    lambda d:d[0].update(formal_definition_or_theorem='forged theorem'),
    lambda d:d.pop(),
    lambda d:d.append(copy.deepcopy(d[0])),
])
def test_13_forged_teacher_lessons_rejected(mutation):
    d=copy.deepcopy(LESSONS);mutation(d)
    with pytest.raises((ValueError,KeyError,TypeError)):
        deep.validate_lessons(d)
def test_offline_evidence_replay_and_private_mac_source_separation():
    assert scope.validate(D,L)
    assert deep.validate_lessons(LESSONS)
    assert ORACLE==deep.math_oracles()
    assert scope.MD.read_text(encoding='utf-8')==scope.render(D)
    assert deep.MD.read_text(encoding='utf-8')==deep.render(LESSONS,ORACLE)
    assert D['context_reviewed_total']==D['historical_editorial_candidates']==239
    assert D['remaining_context_reviews']==0
    assert all(v is None for v in D['track_official_atom_denominators'].values())
    assert all(v['not_checked']==0 and v['official_atom_denominator'] is None
               for v in D['count_by_track'].values())
    assert ORACLE['independently_checked_teacher_examples']==16
    assert ORACLE['boundary_counterexamples']==8
    assert ORACLE['formal_general_theorems_certified']==0
    assert ORACLE['free_student_steps_verified']==ORACLE['teacher_approved']==0
def test_student_authoritative_summary_does_not_expose_unapproved_answers():
    public=json.dumps(public_summary(),ensure_ascii=False)
    assert 'kb132-deep-' not in public
    assert 'KB_BATCH132' not in public
    assert 'teacher_examples' not in public
    assert 'reasoned_solution' not in public
