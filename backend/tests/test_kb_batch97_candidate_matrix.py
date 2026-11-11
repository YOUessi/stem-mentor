"""Seven-track provenance ledger, no invented official atom denominators."""
from copy import deepcopy
from collections import Counter
from pathlib import Path
import json
import sys
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'backend')]
import build_kb_batch97_candidate_matrix as B

@pytest.fixture(scope='module')
def matrix():return B.build()

def test_300_pending_records_and_seven_track_unknown(matrix):
    assert matrix['provisional_source_labels']==300
    assert len(matrix['candidates'])==300
    assert len(matrix['track_matrix'])==7
    assert matrix['official_atom_denominator'] is None
    assert all(v is None for v in matrix['official_atom_denominators_by_track'].values())
    assert matrix['human_full_page_atomization']=='0/61'
    assert matrix['teacher_approved']==matrix['student_authoritative_release']==0
    assert sum(v['provisional_source_labels'] for v in matrix['track_matrix'].values())==300
    assert matrix['editorial_stages']=={
        'FULL_DEEP_DRAFT_PENDING_TEACHER':54,
        'INDIVIDUAL_SCOPE_NOT_ATOMIZED':24,
        'NO_INDIVIDUAL_EDITORIAL':56,
        'PAIR_COMPARISON_NOT_ATOMIZED':166}

def test_unique_source_and_draft_provenance(matrix):
    c=matrix['candidates']
    assert len({r['candidate_id'] for r in c})==300
    assert all(len(r['source_line_sha256'])==64 and r['official_atom_id'] is None for r in c)
    assert all(r['teacher_review_status']=='REVIEW_PENDING' and
               r['student_authoritative_index_eligible'] is False and
               r['teacher_approval'] is None for r in c)
    deep=[r for r in c if r['deep_lesson_id']]
    assert len(deep)==54
    assert Counter(r['deep_draft_batch'] for r in deep)=={94:14,95:16,96:12,97:12}
    assert all(r['editorial_stage']=='FULL_DEEP_DRAFT_PENDING_TEACHER' for r in deep)

@pytest.mark.parametrize('track',B.B93.TRACKS)
def test_per_track_consistent(track,matrix):
    v=matrix['track_matrix'][track]
    assert v['official_math_atom_denominator'] is None
    assert v['teacher_reviewed_atom_count']==0
    expected=Counter(r['editorial_stage'] for r in matrix['candidates'] if r['track']==track)
    assert v['status_counts']==dict(expected)
    assert v['provisional_source_labels']==sum(expected.values())

def test_fake_64hex_source_signature_rejected():
    base=deepcopy(B.B93.build()['provisional_candidate_ledger'])
    base[0]['source_line_sha256']='0'*64
    with pytest.raises(ValueError,match='SHA'):B.build(base=base)

def test_swapped_duplicate_candidate_rejected():
    base=deepcopy(B.B93.build()['provisional_candidate_ledger'])
    base[0]=deepcopy(base[1])
    with pytest.raises(ValueError,match='duplicate|regressed|300'):
        B.build(base=base)

def test_fake_teacher_approval_in_draft_rejected():
    a=[(94,B.B94.build()[1]['canonical_lesson_source_links']),
       (95,B.B95.build()[1]['canonical_lesson_source_links']),
       (96,B.B96.build()[1]['canonical_lesson_source_links']),
       (97,B.B97.build()[1]['canonical_lesson_source_links'])]
    a=deepcopy(a);a[3][1][0]['teacher_approved']=True
    with pytest.raises(ValueError,match='approval'):B.build(draft_links=a)

def test_generated_file_bytes_match(matrix):
    assert json.loads(B.OUT.read_text())==matrix
    assert B.MD.read_text()==B.markdown(matrix)
