"""Batch131: 43 new source-locked contextual judgments and 16 exact condition pairs.

On GitHub source hashes are structural-only; only authorized Mac replays PDFKit
input. None of the editorial candidates is teacher-approved or student-authoritative.
"""
from __future__ import annotations
import copy,hashlib,json,os,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'backend')]
import build_kb_batch131_contexts as scope
import check_kb_batch131_exact_cases as mathcheck
from app.deep_knowledge import public_summary
D=json.loads(scope.DATA.read_text(encoding='utf8'))
L=json.loads(scope.LOCKS.read_text(encoding='utf8'))
O=json.loads(mathcheck.OUT.read_text(encoding='utf8'))
@pytest.mark.parametrize('record',D['records'],ids=lambda r:r['candidate_id'])
def test_43_authored_context_and_track_closure(record):
    key=record['candidate_id'];suffix=key.removeprefix('hs-semantic-pilot-')
    assert record['source_lock']==L[key]
    assert record['contextual_interpretation']==scope.R[suffix][0]
    assert record['boundary_or_counterexample']==scope.R[suffix][1]
    assert record['teacher_review_status']=='REVIEW_PENDING'
    assert record['teacher_signature'] is None
    assert record['official_atom_id'] is None
    assert not record['student_authoritative'] and not record['mathematics_formally_certified']
@pytest.mark.parametrize('record',D['records'],ids=lambda r:r['candidate_id'])
def test_mac_recomputes_exact_private_line_fingerprint(record):
    if os.environ.get('GITHUB_ACTIONS')=='true':
        pytest.skip('Private Mac-only PDFKit originals not present on GitHub CI')
    d=record['source_lock']
    pages=scope.previous.prev.prior.prior.previous.source_pages()
    raw=pages[d['page']][d['start_line']-1:d['end_line']]
    assert [hashlib.sha256(s.encode()).hexdigest() for s in raw]==d['line_sha256']
    assert hashlib.sha256('\n'.join(raw).encode()).hexdigest()==d['span_sha256']
@pytest.mark.parametrize('case',O['cases'],ids=lambda c:c['case'])
def test_16_exact_math_positive_negative_boundaries(case):
    assert case['exact_valid_witness_passed'] is True
    assert case['exact_invalid_witness_rejected'] is True
    assert case['universally_proved'] is False
    assert case['student_step_verified'] is False
    assert case['teacher_approved'] is False
    recomputed={r['case']:r for r in mathcheck.oracle()}
    assert recomputed[case['case']]==case
@pytest.mark.parametrize('mutation',[
    lambda d:d.update(official_atom_denominator=239),
    lambda d:d.update(teacher_approved=1),
    lambda d:d.update(student_authoritative=1),
    lambda d:d.update(remaining_context_reviews=0),
    lambda d:d.update(context_reviewed_total=239),
    lambda d:d.update(historical_editorial_candidates=200),
    lambda d:d.update(source_pdf_text_embedded=True),
    lambda d:d['track_official_atom_denominators'].update(COMPULSORY=75),
    lambda d:d['counts_by_track']['COMPULSORY'].update(teacher_approved=1),
    lambda d:d['counts_by_track']['COMPULSORY'].update(not_checked=-1),
    lambda d:d['records'][0].update(official_atom_id='fabricated'),
    lambda d:d['records'][0].update(teacher_review_status='APPROVED'),
    lambda d:d['records'][0].update(student_authoritative=True),
    lambda d:d['records'][0].update(mathematics_formally_certified=True),
    lambda d:d['records'][0].update(source_evidence_status='CERTIFIED'),
    lambda d:d['records'][0].update(contextual_interpretation='forged'),
    lambda d:d['records'][0]['source_lock'].update(span_sha256='0'*64),
    lambda d:d['records'][0]['source_lock']['line_sha256'].pop(),
    lambda d:d['records'].pop(),
    lambda d:d['records'].append(copy.deepcopy(d['records'][0])),
])
def test_twenty_poisoned_scope_mutations_rejected(mutation):
    d=copy.deepcopy(D);mutation(d)
    with pytest.raises((ValueError,KeyError,TypeError)):
        scope.validate_offline(d,L)
@pytest.mark.parametrize('mutation',[
    lambda d:d.update(proofs_formally_certified=1),
    lambda d:d.update(student_free_text_steps_verified=1),
    lambda d:d.update(teacher_approvals=1),
    lambda d:d.update(positive_exact_checks=123),
    lambda d:d['cases'][0].update(universally_proved=True),
    lambda d:d['cases'][0].update(student_step_verified=True),
    lambda d:d['cases'][0].update(exact_valid_witness_passed=False),
    lambda d:d['cases'].pop(),
])
def test_eight_poisoned_math_snapshots_rejected(mutation):
    d=copy.deepcopy(O);mutation(d)
    with pytest.raises(ValueError):mathcheck.validate_snapshot(d)
def test_offline_snapshot_and_reproducible_render_are_identical():
    assert scope.validate_offline(D,L)
    assert scope.REPORT.read_text(encoding='utf8')==scope.render(D)
    assert O==mathcheck.check()
    assert mathcheck.MD.read_text(encoding='utf8')==mathcheck.render(O)
def test_7_track_counts_have_explicit_unknown_denominators():
    assert D['context_reviewed_total']==200 and D['remaining_context_reviews']==39
    assert len(D['records'])==43
    assert all(v is None for v in D['track_official_atom_denominators'].values())
    assert all(v['official_atom_denominator'] is None for v in D['counts_by_track'].values())
def test_student_public_summary_keeps_all_drafts_out():
    summary=json.dumps(public_summary(),ensure_ascii=False)
    assert 'KB_BATCH131' not in summary
    assert 'contextual_interpretation' not in summary
    assert 'reasoned_solution' not in summary
def test_math_engine_does_not_certify_free_text_or_teacher_review():
    assert O['positive_exact_checks']==O['invalid_boundary_checks']==16
    assert O['proofs_formally_certified']==0
    assert O['student_free_text_steps_verified']==0
    assert O['teacher_approvals']==0
