"""v0.5 synthetic regression: retrieval gates, no leakage, policy adaptation.

These tests do not imply validation with actual students.
"""
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.retrieval import retrieve
from app.knowledge_quality import validate_knowledge
from app.proof_obligations import teacher_certificate, coverage
from app.reasoning import graphs

ROOT=Path(__file__).resolve().parents[2]
CASES=json.loads((ROOT/'evaluations/retrieval_hard_cases_v05.json').read_text(encoding='utf8'))

@pytest.mark.parametrize('case',CASES,ids=[x['id'] for x in CASES])
def test_curated_retrieval_hard_cases(case):
    r=retrieve(case['query'],case['problem_id'],limit=30,show_excluded=True)
    ids=[x['id'] for x in r['hits']]
    exclusion={x['id']:x for x in r['excluded']}
    if case['expect']=='hit':
        assert case['target'] in ids[:5]
    elif case['expect']=='excluded':
        assert case['target'] not in ids
        assert exclusion[case['target']]['applicability']=='CONDITIONS_NOT_ESTABLISHED'
    else:
        assert case['expect']=='contra'
        assert case['target'] not in ids
        assert exclusion[case['target']]['applicability']=='CONTRAINDICATED'

def test_curated_content_has_boundary_and_honest_review_status():
    q=validate_knowledge()
    assert q['valid_contract'],q['issues']
    assert q['corpus_documents']>=26
    assert q['curated_problems']>=15
    assert q['reasoning_graphs']==q['curated_problems']
    assert q['teacher_approved_documents']==0
    assert q['expert_review_status'].get('PENDING')==q['corpus_documents']

def test_reasoning_plan_is_guarded_and_not_student_proof():
    all_certs=coverage()
    assert all_certs['problems_with_limited_certificates']>=4
    assert all_certs['verified_student_steps']==0
    assert teacher_certificate('log-domain') is None
    for pid in all_certs['checked_ids']:
        cert=teacher_certificate(pid)
        assert cert['teacher_only']
        assert cert['all_symbolic_checks_pass']
        assert cert['student_work_verified'] is False
        assert cert['required_conditions']

def test_new_graphs_teacher_scaffolds_stay_hidden():
    for pid in ('triangle-ssa','triangle-sss','parabola-tangent','log-domain','median-length'):
        graph=graphs()[pid]
        assert any(n['role']=='BACKWARD' and n['teacher_only'] for n in graph['nodes'])
        assert all(not edge['verified'] for edge in graph['edges'] if edge['relation']=='BACKWARD_SEARCH_NOT_PROOF')

@pytest.fixture
def api(monkeypatch,tmp_path):
    monkeypatch.setenv('STEM_MENTOR_DB',str(tmp_path/'synthetic.sqlite3'))
    with TestClient(app) as client:
        yield client

def new_session(client,mode='GUIDE',pid='inequality-bridge'):
    student=client.post('/api/students',json={'alias':'合成学生'}).json()['id']
    sess=client.post('/api/sessions',json={'student_id':student,'mode':mode,'problem_id':pid})
    assert sess.status_code==201,sess.text
    return sess.json()['id']

def advance(client,session,text='我卡住了'):
    r=client.post(f'/api/sessions/{session}/turns',json={'student_text':text})
    assert r.status_code==200,r.text
    return r.json()

def test_repeated_stuck_switches_actions_instead_of_repeating(api):
    sid=new_session(api)
    actions=[advance(api,sid)['next_action'] for _ in range(4)]
    assert actions==['ASK_BACKWARD_GOAL','ASK_BRIDGE','ASK_SPECIFIC_OBSTACLE','OFFER_TEACHING_CHOICE']
    final=api.get(f'/api/sessions/{sid}').json()
    assert [t['action'] for t in final['turns']]==actions
    assert final['turns'][0]['student_text']=='我卡住了'

def test_analysis_mode_can_stop_questioning_and_switch(api):
    sid=new_session(api,'ANALYZE','distance-ratio')
    actions=[advance(api,sid,'我先分析条件')['next_action'] for _ in range(5)]
    assert actions==['ASK_OBSERVATION','ASK_STRATEGY','ASK_STRATEGY',
                     'ASK_METHOD_JUSTIFICATION','OFFER_MODE_SWITCH']

def test_student_api_never_exposes_teacher_only_proof(api):
    sid=new_session(api)
    r=advance(api,sid,'我想先整理已知')
    assert r['math_verified'] is False
    assert r['decision_trace']['student_work_verified'] is False
    assert 'required_conditions' not in r
    graph=api.get(f'/api/sessions/{sid}/reasoning-map').json()
    assert graph['contains_teacher_solution'] is False
    assert all(n.get('teacher_only') is not True for n in graph['nodes'])
    assert len(graph['nodes'])<len(graphs()['inequality-bridge']['nodes'])+2

def test_api_reports_honest_scope_without_leaking_certificate(api):
    r=api.get('/api/knowledge/quality')
    assert r.status_code==200 and r.json()['valid_contract']
    r=api.get('/api/math/proof-coverage')
    assert r.status_code==200
    assert r.json()['verified_student_steps']==0
    assert 'assertion_id' not in str(r.json())
    assert api.get('/health').json()['llm_api_used'] is False

def test_recall_from_ssa_not_recommended_for_sss(api):
    uid=api.post('/api/students',json={'alias':'合成学生'}).json()['id']
    old=api.post('/api/sessions',json={'student_id':uid,'problem_id':'triangle-ssa'}).json()['id']
    advance(api,old,'我用正弦定理并检查另一角')
    api.post(f'/api/sessions/{old}/complete',json={'reflection':'受提示练习，非独立掌握'})
    current=api.post('/api/sessions',json={'student_id':uid,'problem_id':'triangle-sss'}).json()['id']
    r=api.post(f'/api/sessions/{current}/turns',
               json={'student_text':'回忆以前的数学题','request_type':'recall','help_requested':True}).json()
    assert r['next_action']=='NO_MEMORY'
    assert r['reference_episode_id'] is None
