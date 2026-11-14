"""Batch153 end-to-end tests: honest source scope, rigorous depth, finite math, editor RAG and no student leaks."""
import copy
import json
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'backend')]
import author_kb_batch153_data as author
import build_kb_batch153_lessons as lesson
import build_kb_batch153_crosswalk as crosswalk
import check_kb_batch153_math as oracle
from app import kb_batch153_index as index
from app.main import app

@pytest.fixture(scope='module')
def rows():
    return json.loads(lesson.OUT.read_text(encoding='utf-8'))

@pytest.fixture(scope='module')
def ledger():
    return json.loads(lesson.AUDIT.read_text(encoding='utf-8'))

@pytest.fixture(scope='module')
def exact():
    return oracle.cases()

def test_complete_reconstruction_and_all_safety_guards(rows,ledger):
    assert rows==lesson.build()
    assert lesson.validate(rows)
    assert ledger==lesson.audit(rows)
    assert ledger['prior_teacher_pending_manuscripts']==125
    assert ledger['added_original_manuscripts']==10
    assert ledger['total_teacher_only_drafts']==135
    assert len(ledger['rows'])==len({r['candidate'] for r in ledger['rows']})==135
    assert all(v is None for v in ledger['official_atom_denominators'].values())
    assert ledger['official_coverage_rate'] is None
    assert ledger['teacher_approved']==ledger['student_authoritative']==0
    assert lesson.REPORT.read_text(encoding='utf-8')==lesson.render(rows,ledger)
    assert json.loads(lesson.SAFE.read_text(encoding='utf-8'))==lesson.student_safe()
    assert author.OUT.read_text(encoding='utf-8')==author.json.dumps(author.R,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n'

def test_k00_239_editorial_leads_are_not_official_census():
    v=crosswalk.build()
    assert crosswalk.validate(v)
    assert v==json.loads(crosswalk.OUT.read_text(encoding='utf-8'))
    assert v['matched_editorial_candidates']==94
    assert v['missing_editorial_candidates']==145
    assert v['total_pending_teacher_manuscripts']==135
    assert v['official_atomic_census_complete'] is False
    assert v['official_course_coverage_rate'] is None
    assert sum(z['linked_teacher_only_drafts'] for z in v['by_track'].values())==94
    assert set(v['official_atom_denominators'])==set(lesson.TRACKS)
    assert all(n is None for n in v['official_atom_denominators'].values())

@pytest.mark.parametrize('i',range(10))
def test_ten_original_units_are_source_anchored_and_individually_deep(i,rows):
    r=rows[i];a=author.R[i]
    assert r['source_candidate_id']==lesson.IDS[i]==a['id']
    assert r['course_track']==lesson.EXPECTED[a['id']]
    assert r['source_pdf_sha256']==lesson.PDF
    assert r['source_evidence_status']==lesson.EVIDENCE
    assert r['source_semantics_human_approved'] is False
    assert r['official_atom_id'] is None
    assert r['teacher_review_status']==r['prerequisite_math_review']=='REVIEW_PENDING'
    assert r['teacher_review_evidence'] is None
    assert r['teacher_solution_visibility']=='TEACHER_ONLY'
    assert not r['formal_proof_certified'] and not r['free_student_step_verified']
    assert not r['student_authoritative']
    assert len(r['reasoned_steps'])==4
    assert len(r['teacher_examples'])==2
    assert len(r['student_hint_ladder'])==3
    assert len(r['source_line_sha256'])==r['source_end_line']-r['source_start_line']+1
    assert r['elective_e_optional_example']==(i==9)
    assert r['formal_definition_or_theorem'] and r['notation_and_domain']
    assert r['nonexample_or_failure'] and r['typical_wrong_solution']
    assert r['near_transfer'] and r['far_transfer']

FORGED=[
 ('teacher_review_status','APPROVED'),
 ('teacher_review_evidence',{'forged':'x'}),
 ('student_authoritative',True),
 ('teacher_solution_visibility','STUDENT'),
 ('official_atom_id','FAKE_OFFICIAL'),
 ('source_semantics_human_approved',True),
 ('formal_proof_certified',True),
 ('free_student_step_verified',True),
 ('prerequisite_math_review','APPROVED'),
 ('source_evidence_status','APPROVED'),
 ('source_pdf_sha256','0'*64),
 ('source_span_sha256','0'*64),
 ('source_line_sha256',[]),
 ('source_start_line',12345),
 ('reasoned_steps',[]),
 ('teacher_examples',[]),
 ('student_hint_ladder',[]),
 ('formal_definition_or_theorem',''),
 ('nonexample_or_failure','')
]
@pytest.mark.parametrize('i',range(10))
@pytest.mark.parametrize('field,bad',FORGED)
def test_190_mutations_reject_false_authority_or_incomplete_math(i,field,bad,rows):
    changed=copy.deepcopy(rows)
    changed[i][field]=bad
    with pytest.raises(ValueError):
        lesson.validate(changed)

@pytest.mark.parametrize('i',range(40))
def test_40_independent_witness_records_are_exact_not_formal(i,exact):
    assert exact==json.loads(oracle.OUT.read_text(encoding='utf-8'))
    entry=exact['witnesses'][i]
    assert entry['source_candidate_id']==lesson.IDS[i//4]
    assert entry['outcome']==('EXACT_FINITE_WITNESS' if i%4<2 else 'INVALID_PRECONDITION_REJECTED')
    assert entry['finite_exact_check']
    assert not entry['formal_general_proof_certified']
    assert not entry['teacher_approved']
    assert not entry['free_student_step_verified']

@pytest.mark.parametrize('query',['正交投影','二项分布','高斯消元','分段函数','学校选修','体育赛程'])
def test_fts5_editor_only_metadata_and_student_denial(query):
    hits=index.editor_preview_search(query,scope='EDITOR_LOCAL',limit=20)
    assert hits, query
    for h in hits:
        assert set(h)=={'id','course_track','source_candidate_id','review_status','condition_status','student_publishable','rank'}
        assert h['review_status']=='REVIEW_PENDING'
        assert h['condition_status']=='CONDITIONS_NOT_ESTABLISHED'
        assert not h['student_publishable']
    assert index.student_evidence_lookup(query)==dict(status='NO_APPROVED_EVIDENCE',
       candidates=[],teacher_solution_exposed=False,unverified_content_exposed=False)

@pytest.mark.parametrize('scope',['',None,'STUDENT','TEACHER','ADMIN','APPROVED'])
def test_fts5_rejects_any_non_local_editor_scope(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search('数列',scope=scope)

def test_public_endpoint_is_aggregate_only_and_seven_denominators_unknown():
    resp=TestClient(app).get('/api/knowledge/kb153-review-coverage')
    assert resp.status_code==200
    data=resp.json()
    assert data['editorial_review_manuscripts']==135
    assert data['editorial_candidates_linked']==94
    assert data['editorial_candidates_unlinked']==145
    assert data['teacher_approved']==data['student_authoritative']==0
    assert data['official_course_coverage_rate'] is None
    assert all(z is None for z in data['official_atom_denominators'].values())
    assert not data['teacher_solution_or_manuscript_included']
    body=json.dumps(data,ensure_ascii=False)
    for banned in ('teacher_examples','reasoned_solution','student_hint_ladder','参考答案','source_line_sha256','source_span_sha256'):
        assert banned not in body

@pytest.mark.parametrize('i',range(7))
def test_all_tracks_remain_unapproved_not_assumed_complete(i):
    t=lesson.TRACKS[i]
    data=index.public_coverage()
    assert data['official_atom_denominators'][t] is None
    assert data['by_track'][t]>=1
    assert data['teacher_approved']==data['student_authoritative']==0
