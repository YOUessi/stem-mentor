"""Batch130: source semantics, teacher-only lessons, hard math and negative gate tests."""
import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'backend')]
import build_kb_batch130_core_source as src
import build_kb_batch130_deep_lessons as deep
import check_kb_batch130_offline as offline
from app.deep_knowledge import public_summary
SCOPE=json.loads(src.OUT.read_text(encoding='utf-8'))
LOCKS=json.loads(src.LOCKS.read_text(encoding='utf-8'))
LESSONS=json.loads(deep.OUT.read_text(encoding='utf-8'))
ORACLE=json.loads(deep.ORACLE.read_text(encoding='utf-8'))
@pytest.mark.parametrize('record',SCOPE['records'],ids=lambda r:r['candidate_id'])
def test_fifty_three_original_line_windows_and_candidate_semantics(record):
    k=record['candidate_id']
    assert LOCKS[k]==record['source_lock']
    assert record['teacher_review_status']=='REVIEW_PENDING'
    assert record['student_authoritative'] is False
    assert record['official_atom_id'] is None
    assert record['mathematics_formally_certified'] is False
    assert record['contextual_interpretation']==src.R[k.removeprefix('hs-semantic-pilot-')][0]
    assert record['boundary_or_counterexample']==src.R[k.removeprefix('hs-semantic-pilot-')][1]
@pytest.mark.parametrize('record',SCOPE['records'],ids=lambda r:r['candidate_id'])
def test_original_pdf_line_sha256_actual_mac_only(record):
    """Private PDF is available only on the authorized Mac, explicitly skipped on CI."""
    import os,hashlib
    if os.environ.get('GITHUB_ACTIONS')=='true':
        pytest.skip('GitHub cannot rehash the licensed source PDF')
    d=record['source_lock'];src_pages=src.prev.prior.prior.previous.source_pages()
    raw=src_pages[d['page']][d['start_line']-1:d['end_line']]
    assert [hashlib.sha256(x.encode()).hexdigest() for x in raw]==d['line_sha256']
    assert hashlib.sha256('\n'.join(raw).encode()).hexdigest()==d['span_sha256']
@pytest.mark.parametrize('lesson',LESSONS,ids=lambda x:x['id'])
def test_eight_full_teacher_only_lessons_and_examples(lesson):
    assert lesson['teacher_review_status']=='REVIEW_PENDING'
    assert lesson['teacher_review_evidence'] is None
    assert lesson['formal_proof_certified'] is False
    assert lesson['free_student_step_verified'] is False
    assert lesson['student_authoritative'] is False
    assert lesson['teacher_solution_visibility']=='TEACHER_ONLY'
    assert lesson['source_line_lock']==LOCKS[lesson['candidate_id']]
    assert len(lesson['reasoned_steps'])>=3
    assert len(lesson['teacher_examples'])==2
    assert all(len(x['reasoned_solution'])>=3 for x in lesson['teacher_examples'])
    assert len(lesson['student_hint_ladder'])==3
    assert len(lesson['prerequisite_candidate_ids'])==len(set(lesson['prerequisite_candidate_ids']))
    assert set(lesson['prerequisite_candidate_ids']).issubset({'hs-semantic-pilot-'+k for k in src.R})
@pytest.mark.parametrize('lesson',LESSONS,ids=lambda x:x['id'])
def test_eight_independent_finite_oracle_pairs(lesson):
    suff=lesson['candidate_id'].removeprefix('hs-semantic-pilot-')
    assert ORACLE['example_results'][suff]==[True,True]
    assert ORACLE['counterexample_results'][suff] is True
@pytest.mark.parametrize('mutation',[
    lambda x:x.update(official_atom_denominator=157),
    lambda x:x.update(teacher_approved=1),
    lambda x:x.update(student_authoritative=1),
    lambda x:x.update(remaining_context_reviews=0),
    lambda x:x.update(historical_editorial_candidates=157),
    lambda x:x.update(source_pdf_text_embedded=True),
    lambda x:x['track_official_atom_denominators'].update(COMPULSORY=40),
    lambda x:x['counts_by_track']['COMPULSORY'].update(teacher_approved=1),
    lambda x:x['records'][0].update(official_atom_id='invented'),
    lambda x:x['records'][0].update(teacher_review_status='APPROVED'),
    lambda x:x['records'][0].update(student_authoritative=True),
    lambda x:x['records'][0].update(mathematics_formally_certified=True),
    lambda x:x['records'][0].update(source_evidence_status='OFFICIAL_ATOM_APPROVED'),
    lambda x:x['records'][0]['source_lock'].update(span_sha256='0'*64),
    lambda x:x['records'].pop(),
    lambda x:x['records'].append(copy.deepcopy(x['records'][0])),
])
def test_sixteen_forged_scope_statuses_fail_closed(mutation):
    d=copy.deepcopy(SCOPE);mutation(d)
    with pytest.raises((ValueError,KeyError)):src.validate(d,LOCKS,regen=False)
@pytest.mark.parametrize('mutation',[
    lambda x:x[0].update(teacher_review_status='APPROVED'),
    lambda x:x[0].update(teacher_review_evidence={'name':'imaginary'}),
    lambda x:x[0].update(student_authoritative=True),
    lambda x:x[0].update(formal_proof_certified=True),
    lambda x:x[0].update(free_student_step_verified=True),
    lambda x:x[0].update(teacher_solution_visibility='STUDENT'),
    lambda x:x[0]['teacher_examples'].pop(),
    lambda x:x[0]['reasoned_steps'].pop(),
    lambda x:x[0]['student_hint_ladder'].pop(),
    lambda x:x[1].update(prerequisite_candidate_ids=['hs-semantic-pilot-DOES-NOT-EXIST']),
    lambda x:x.pop(),
    lambda x:x.append(copy.deepcopy(x[0])),
])
def test_twelve_forged_or_truncated_teacher_lesson_mutations_fail_closed(mutation):
    d=copy.deepcopy(LESSONS);mutation(d)
    with pytest.raises((ValueError,KeyError)):deep.validate(d,regen=False)
def test_offline_published_evidence_replay_and_exact_math():
    report=offline.check()
    assert report['original_mac_pdf_rehashed_by_CI'] is False
    assert report['context_reviews']==53 and report['cumulative_context_checked']==157
    assert report['complete_teacher_pending_manuscripts']==8
    assert report['independent_exact_example_checks']==16
    assert report['invalid_counterexample_checks']==8
def test_student_public_api_does_not_leak_teacher_challenge_answers():
    summary=json.dumps(public_summary(),ensure_ascii=False)
    assert 'kb130-deep-' not in summary
    assert 'KB_BATCH130' not in summary
    assert 'teacher_examples' not in summary
    assert 'reasoned_solution' not in summary

def test_classical_probability_drafts_require_independent_trials():
    lesson=next(x for x in LESSONS if x['candidate_id'].endswith('123-c411'))
    assert '独立' in lesson['applicability_and_hypotheses']
    assert all('独立' in e['question'] for e in lesson['teacher_examples'])

def test_fair_coin_and_dice_marginals_do_not_imply_independence():
    from fractions import Fraction
    # Perfectly correlated coins: each marginal is fair, yet a single head never occurs.
    joint={('H','H'):Fraction(1,2),('T','T'):Fraction(1,2)}
    assert sum(p for (a,b),p in joint.items() if a=='H') == Fraction(1,2)
    assert sum(p for (a,b),p in joint.items() if b=='H') == Fraction(1,2)
    assert sum(p for (a,b),p in joint.items() if (a=='H') != (b=='H')) == 0
    # Both dice have uniform marginals, but second die is forced to 7-first die.
    pairs={(i,7-i):Fraction(1,6) for i in range(1,7)}
    for face in range(1,7):
        assert sum(p for (a,b),p in pairs.items() if a==face)==Fraction(1,6)
        assert sum(p for (a,b),p in pairs.items() if b==face)==Fraction(1,6)
    assert sum(p for (a,b),p in pairs.items() if a+b==7)==1
    assert 1 != Fraction(1,6)

def test_seven_track_official_denominators_remain_unknown():
    assert set(SCOPE['track_official_atom_denominators'])==set(src.prev.TRACKS)
    assert all(v is None for v in SCOPE['track_official_atom_denominators'].values())
    assert ORACLE['formal_general_theorems_certified']==0


def test_ellipse_focal_equation_exact_non_axis_witness():
    import sympy as sp
    x,y,a,c=sp.Rational(3),sp.Rational(16,5),sp.Integer(5),sp.Integer(3)
    b2=a*a-c*c
    assert x*x/a**2 + y*y/b2 == 1
    d1=sp.sqrt((x+c)**2+y*y)
    d2=sp.sqrt((x-c)**2+y*y)
    assert d1==sp.Rational(34,5) and d2==sp.Rational(16,5)
    assert d1+d2==2*a
    assert (sp.sqrt((0+c)**2)+sp.sqrt((0-c)**2)) < 2*a
