"""KB154: 10 original math manuscripts, 40 independent finite guards, fail-closed Agent retrieval."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'backend')]
import author_kb_batch154_data as author
import build_kb_batch154_lessons as lesson
import build_kb_batch154_crosswalk as crosswalk
import build_kb_batch154_scope_graph as graph
import check_kb_batch154_math as oracle
from app import kb_batch154_index as index
from app.main import app

@pytest.fixture(scope='module')
def rows():
    return json.loads(lesson.OUT.read_text(encoding='utf-8'))

@pytest.fixture(scope='module')
def ledger():
    return json.loads(lesson.AUDIT.read_text(encoding='utf-8'))

@pytest.fixture(scope='module')
def witnesses():
    return json.loads(oracle.OUT.read_text(encoding='utf-8'))

def test_authoring_source_integrity_and_unique_review_counts(rows,ledger):
    assert author.OUT.read_text(encoding='utf-8')==author.encode(author.R)
    assert len(author.R)==len(rows)==10
    assert rows==lesson.build()
    assert lesson.validate(rows)
    assert ledger==lesson.audit(rows)
    assert ledger['prior_teacher_pending_manuscripts']==135
    assert ledger['added_original_manuscripts']==10
    assert ledger['total_teacher_only_drafts']==145
    assert len({r['candidate'] for r in ledger['rows']})==145
    assert ledger['teacher_approved']==ledger['student_authoritative']==0
    assert all(x is None for x in ledger['official_atom_denominators'].values())
    assert lesson.REPORT.read_text(encoding='utf-8')==lesson.render(rows,ledger)
    assert json.loads(lesson.SAFE.read_text(encoding='utf-8'))==lesson.student_safe()

@pytest.mark.parametrize('i',range(10))
def test_review_pending_rigorous_proof_hypotheses_and_near_far(i,rows):
    r=rows[i];a=author.R[i]
    assert r['source_candidate_id']==lesson.IDS[i]==a['id']
    assert r['course_track']==lesson.EXPECTED[a['id']]
    assert r['source_pdf_sha256']==lesson.PDF
    assert r['source_evidence_status']==lesson.EVIDENCE
    assert r['official_atom_id'] is None
    assert r['teacher_review_status']==r['prerequisite_math_review']=='REVIEW_PENDING'
    assert r['teacher_review_evidence'] is None
    assert r['teacher_solution_visibility']=='TEACHER_ONLY'
    assert not r['student_authoritative'] and not r['formal_proof_certified']
    assert not r['source_semantics_human_approved'] and not r['free_student_step_verified']
    assert len(r['reasoned_steps'])==4
    assert len(r['teacher_examples'])==2
    assert len(r['student_hint_ladder'])==3
    assert len(r['source_line_sha256'])==r['source_end_line']-r['source_start_line']+1
    assert r['elective_e_optional_example'] is False
    for key in ('formal_definition_or_theorem','notation_and_domain','applicability_and_hypotheses',
                'why_method_is_legal','nonexample_or_failure','typical_wrong_solution',
                'why_wrong_and_repair','near_transfer','far_transfer'):
        assert len(r[key])>=20

FORGERIES=[
 ('teacher_review_status','APPROVED'),
 ('teacher_review_evidence',{'fake':'teacher'}),
 ('student_authoritative',True),
 ('teacher_solution_visibility','STUDENT'),
 ('official_atom_id','FAKE'),
 ('source_semantics_human_approved',True),
 ('formal_proof_certified',True),
 ('free_student_step_verified',True),
 ('prerequisite_math_review','APPROVED'),
 ('source_evidence_status','VERIFIED'),
 ('source_pdf_sha256','0'*64),
 ('source_span_sha256','0'*64),
 ('source_line_sha256',[]),
 ('source_start_line',0),
 ('source_end_line',0),
 ('reasoned_steps',[]),
 ('teacher_examples',[]),
 ('student_hint_ladder',[]),
 ('formal_definition_or_theorem',''),
 ('nonexample_or_failure',''),
]
@pytest.mark.parametrize('i',range(10))
@pytest.mark.parametrize('field,bad',FORGERIES)
def test_200_forgery_proof_and_shallow_content_mutations_are_rejected(i,field,bad,rows):
    modified=copy.deepcopy(rows);modified[i][field]=bad
    with pytest.raises(ValueError):
        lesson.validate(modified)

@pytest.mark.parametrize('i',range(40))
def test_sympy_finite_oracle_exact_witnesses_not_general_proof(i,witnesses):
    assert witnesses==oracle.run()
    w=witnesses['witnesses'][i]
    assert w['source_candidate_id']==lesson.IDS[i//4]
    assert w['outcome']==('EXACT_FINITE_WITNESS' if i%4<2 else 'INVALID_PRECONDITION_REJECTED')
    assert w['finite_exact_check']
    assert not w['formal_general_proof_certified']
    assert not w['teacher_approved'] and not w['free_student_step_verified']

@pytest.mark.parametrize('q',['分段函数','连续函数','对数换底','古典概率','导数','最小二乘',
                              '数列极限','定积分','频数统计','透视投影'])
def test_editor_only_retrieval_never_exposes_teacher_answer(q):
    results=index.editor_preview_search(q,scope='EDITOR_LOCAL',limit=20)
    assert results
    for x in results:
        assert set(x)=={'id','course_track','source_candidate_id','review_status',
                        'condition_status','student_publishable','rank'}
        assert x['review_status']=='REVIEW_PENDING'
        assert x['condition_status']=='CONDITIONS_NOT_ESTABLISHED'
        assert x['student_publishable'] is False
    assert index.student_evidence_lookup(q)=={
        'status':'NO_APPROVED_EVIDENCE','candidates':[],
        'teacher_solution_exposed':False,'unverified_content_exposed':False}

@pytest.mark.parametrize('scope',['',None,'STUDENT','TEACHER','ADMIN','APPROVED'])
def test_fts_scope_rejects_nonlocal_editor(scope):
    with pytest.raises(index.LocalEditorOnlyError):
        index.editor_preview_search('函数',scope=scope)

def test_new_145_draft_index_and_crosswalk_counts():
    rows=index.load()
    assert len(rows)==145
    assert len({r['id'] for r in rows})==145
    c=crosswalk.build()
    assert crosswalk.validate(c)
    assert c==json.loads(crosswalk.OUT.read_text(encoding='utf-8'))
    assert c['matched_editorial_candidates']==104 and c['missing_editorial_candidates']==135
    assert c['total_pending_teacher_manuscripts']==145
    assert all(x is None for x in c['official_atom_denominators'].values())
    assert c['teacher_approved']==c['student_authoritative']==0

def test_new_145_draft_aggregate_endpoint():
    # Endpoints only expose aggregate status; no copyrighted syllabus text or proof solutions.
    for route in ['/api/knowledge/kb154-review-coverage','/api/knowledge/kb154-source-scope-status']:
        res=TestClient(app).get(route)
        assert res.status_code==200
        body=res.json()
        assert body['teacher_approved']==body['student_authoritative']==0
        assert all(z is None for z in body['official_atom_denominators'].values())
        serialized=json.dumps(body,ensure_ascii=False)
        for banned in ('reasoned_solution','teacher_examples','source_line_sha256','formal_definition_or_theorem',
                       '参考答案','student_hint_ladder','source_span_sha256'):
            assert banned not in serialized
