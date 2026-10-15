"""Synthetic regression evidence for the v0.4 structured tutor architecture."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.reasoning import graphs
from app.retrieval import corpus, retrieve
from app.diagnosis import diagnose
from app.math_tools import verify_equivalence


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('STEM_MENTOR_DB',str(tmp_path/'demo.sqlite3'))
    with TestClient(app) as instance:
        yield instance


def start(client, problem='inequality-bridge', mode='GUIDE'):
    sid=client.post('/api/students',json={'alias':'合成学生'}).json()['id']
    response=client.post('/api/sessions',json={'student_id':sid,'problem_id':problem,'mode':mode})
    assert response.status_code==201,response.text
    return response.json()['id']


def send(client, session, text, **kwargs):
    r=client.post(f'/api/sessions/{session}/turns',json={'student_text':text,**kwargs})
    assert r.status_code==200,r.text
    return r.json()


def test_corpus_is_documents_not_stub():
    assert len(corpus())>=8
    assert all(len(card['content'])>45 for card in corpus())
    assert all(card['source']['permission']=='PROJECT_AUTHORED' for card in corpus())
    assert all(card['source']['expert_review']=='PENDING' for card in corpus())


def test_fts5_chinese_math_retrieval():
    hits=retrieve('阿波罗尼斯圆','distance-ratio')['hits']
    assert hits[0]['id']=='method-apollonius'
    assert hits[0]['applicability']=='CURATED_CONTEXT_MATCH'
    assert hits[0]['matched_tokens']


def test_surface_similarity_cannot_override_structure_gate():
    r=retrieve('椭圆切线','ellipse-focus',show_excluded=True)
    assert 'method-conic-tangent' not in [h['id'] for h in r['hits']]
    assert 'method-conic-tangent' in [h['id'] for h in r['excluded']]
    assert next(x for x in r['excluded'] if x['id']=='method-conic-tangent')['applicability']=='CONDITIONS_NOT_ESTABLISHED'


def test_outside_curve_cannot_recommend_tangent_rule():
    r=retrieve('曲线外点的切线','ellipse-tangent',show_excluded=True)
    assert 'method-conic-tangent' not in [h['id'] for h in r['hits']]
    assert any(h['id']=='method-conic-tangent' and h['applicability']=='CONTRAINDICATED' for h in r['excluded'])


def test_non_singular_point_is_not_false_negation():
    r=retrieve('非奇异点处的切线','ellipse-tangent')
    assert any(h['id']=='method-conic-tangent' for h in r['hits'])


def test_search_query_fts_injection_safe(client):
    r=client.post('/api/knowledge/search',json={'query':'" OR * ) (','include_excluded':True})
    assert r.status_code==200,r.text
    assert r.json()['engine']=='LOCAL_FTS5_BM25_AND_STRUCTURE_V1'


def test_unknown_context_does_not_claim_applicable():
    hits=retrieve('正弦定理 SSA')['hits']
    assert all(h['applicability']=='CONDITION_UNCHECKED' for h in hits)


def test_reasoning_graphs_have_no_proved_backward_implication():
    assert len(graphs())==6
    for graph in graphs().values():
        assert {n['role'] for n in graph['nodes']}>={'GIVEN','GOAL','FORWARD','BACKWARD','BRIDGE'}
        assert all(not e['verified'] for e in graph['edges'] if e['relation']=='BACKWARD_SEARCH_NOT_PROOF')


def test_student_visible_map_never_leaks_curated_solution(client):
    sid=start(client)
    initial=client.get(f'/api/sessions/{sid}/reasoning-map').json()
    assert set(n['role'] for n in initial['nodes'])=={'GIVEN','GOAL'}
    assert not initial['contains_teacher_solution']
    send(client,sid,'我考虑先化简表达式')
    now=client.get(f'/api/sessions/{sid}/reasoning-map').json()
    assert now['student_steps']==1
    assert now['nodes'][-1]['verification']=='STUDENT_CLAIM_UNVERIFIED'
    assert not any(n['role']=='BRIDGE' for n in now['nodes'])


def test_self_report_stage_overrides_keywords_and_is_audited(client):
    sid=start(client)
    r=send(client,sid,'我不是卡住，我准备从目标反推',self_report_stage='BACKWARD')
    assert r['thinking_stage']=='BACKWARD'
    assert r['next_action']=='ASK_BRIDGE'
    assert r['decision_trace']['stage_diagnosis']['source']=='STUDENT_SELF_REPORT'
    stored=client.get(f'/api/sessions/{sid}').json()['turns'][0]
    assert stored['decision_trace']['rule_id']=='P52_BACKWARD_TO_BRIDGE'


def test_negated_stuck_not_misclassified():
    assert diagnose('我没卡住，还想先做',[])['stage']=='START'
    assert diagnose('我现在卡住了',[])['stage']=='STUCK'


def test_repeated_stuck_changes_teaching_action(client):
    sid=start(client)
    first=send(client,sid,'我卡住了')
    second=send(client,sid,'我还是卡住了')
    assert first['next_action']=='ASK_BACKWARD_GOAL'
    assert second['next_action']=='ASK_BRIDGE'
    assert second['decision_trace']['rule_id']=='P50_REPEATED_STUCK_SWITCH'
    assert '完整答案' not in second['message']


def test_independent_ignores_unsolicited_stage_hint(client):
    sid=start(client,mode='INDEPENDENT')
    r=send(client,sid,'我卡住了，但想自己继续',self_report_stage='STUCK')
    assert r['next_action']=='WAIT'
    assert r['hint_level']==0


def test_math_equivalence_with_and_without_assumptions(client):
    example={'expr_left':'1/x+1/y','expr_right':'1/(x*y)'}
    good=client.post('/api/math/equivalence',json={**example,'problem_id':'inequality-bridge'}).json()
    bad=client.post('/api/math/equivalence',json={**example,'problem_id':'distance-ratio'}).json()
    assert good['status']=='EQUIVALENT_ON_DOMAIN'
    assert good['domain_not_fully_checked']
    assert bad['status']=='NOT_EQUIVALENT_AS_IDENTITY'


@pytest.mark.parametrize('expression',[
    '__import__("os").system("echo NOT_ALLOWED")','x.__class__','x**100000','[x for x in y]',
    'x+y if True else 0', '1/(x-x)', 'x'*400
])
def test_restricted_math_parser_never_executes_untrusted_code(expression):
    result=verify_equivalence(expression,'x','inequality-bridge')
    assert result['status']=='UNSUPPORTED'
    assert not result['verified']


def test_compatible_equivalence_mismatch_is_not_proof_of_error():
    result=verify_equivalence('x+1','x+2','inequality-bridge')
    assert result['status']=='NOT_EQUIVALENT_AS_IDENTITY'
    assert not result['verified']
    assert '不自动断言' in result['reason']


def test_web_search_evidence_has_provenance(client):
    r=client.post('/api/knowledge/search',json={'query':'阿波罗尼斯圆','problem_id':'distance-ratio'}).json()
    hit=r['hits'][0]
    assert hit['source']['expert_review']=='PENDING'
    assert 'boundary' in hit and 'source' in hit
    assert 'score_components' in hit and 'matched_tokens' in hit


def test_graph_404_and_search_validation(client):
    assert client.get('/api/sessions/missing/reasoning-map').status_code==404
    assert client.post('/api/math/equivalence',json={'expr_left':'x','expr_right':'x','problem_id':'unknown'}).status_code==422
    assert client.post('/api/knowledge/search',json={'query':'a','top_k':999}).status_code==422


def test_search_intent_does_not_get_overridden_by_open_problem():
    # The current exercise is about a distance ratio; a search for tangents
    # must not silently return an Apollonius circle due to context boost.
    result = retrieve("切线", problem_id="distance-ratio")
    assert all(hit["id"] != "method-apollonius" for hit in result["hits"])
    assert all("切线" in (hit["title"] + hit["snippet"] + hit["boundary"])
               for hit in result["hits"])
