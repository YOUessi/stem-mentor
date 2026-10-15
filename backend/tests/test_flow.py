"""Deterministic simulation contract tests. These are NOT learning-effect studies."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("STEM_MENTOR_DB",str(tmp_path/"demo.sqlite3"))
    with TestClient(app) as c:
        yield c


def student(client):
    result=client.post("/api/students",json={"alias":"模拟学生"})
    assert result.status_code==201
    return result.json()["id"]


def start(client,student_id,problem_id="ellipse-tangent",mode="GUIDE"):
    response=client.post("/api/sessions",json={"student_id":student_id,"problem_id":problem_id,"mode":mode})
    assert response.status_code==201,response.text
    return response.json()["id"]


def turn(client,sid,text,**kwargs):
    response=client.post(f"/api/sessions/{sid}/turns",json={"student_text":text,**kwargs})
    assert response.status_code==200,response.text
    return response.json()


def test_boot_and_ui(client):
    health=client.get("/health").json()
    assert health["llm_api_used"] is False
    assert health["engine"]=="DETERMINISTIC_SIMULATION"
    assert "STEM Mentor" in client.get("/").text
    assert client.get("/assets/app.js").status_code==200
    assert len(client.get("/api/catalog").json()["problems"])>=6


def test_analysis_and_strategy_are_not_full_solutions(client):
    uid=student(client)
    sid=start(client,uid,"distance-ratio","ANALYZE")
    r=turn(client,sid,"我想先看已知和待求")
    assert r["next_action"]=="ASK_OBSERVATION"
    assert r["scope"]=="CURATED_PROBLEM"
    assert "=" not in r["message"]
    assert r["math_verified"] is False
    second=turn(client,sid,"我把题目拆成两个定点和一个动点")
    assert second["next_action"]=="ASK_STRATEGY"


def test_guide_switches_to_backward_goal(client):
    uid=student(client)
    sid=start(client,uid,"inequality-bridge")
    turn(client,sid,"我利用和为1合并成一个分式")
    response=turn(client,sid,"但我卡住了，不知道下一步")
    assert response["thinking_stage"]=="STUCK"
    assert response["next_action"]=="ASK_BACKWARD_GOAL"
    assert "目标" in response["message"] or "结论" in response["message"]


def test_independent_no_hint_unless_requested(client):
    uid=student(client)
    sid=start(client,uid,"geometric-sum","INDEPENDENT")
    response=turn(client,sid,"我先尝试从定义出发")
    assert response["next_action"]=="WAIT"
    assert response["hint_level"]==0
    assert client.get(f"/api/sessions/{sid}").json()["hint_count"]==0
    helped=turn(client,sid,"我卡住了",help_requested=True)
    assert helped["next_action"]!="WAIT"
    assert client.get(f"/api/sessions/{sid}").json()["hint_count"]>0


def test_switch_modes_preserves_attempts(client):
    uid=student(client)
    sid=start(client,uid,"ellipse-tangent")
    turn(client,sid,"我想先求导")
    changed=client.patch(f"/api/sessions/{sid}/mode",json={"mode":"INDEPENDENT"})
    assert changed.status_code==200
    assert changed.json()["mode"]=="INDEPENDENT"
    assert changed.json()["turns"][0]["student_text"]=="我想先求导"
    # A second test client simulates reopening a page after a process restart.
    with TestClient(app) as second_client:
        assert second_client.get(f"/api/sessions/{sid}").json()["turns"][0]["student_text"]=="我想先求导"


def test_only_real_same_student_structural_history(client):
    owner=student(client)
    newcomer=student(client)
    old=start(client,owner,"ellipse-tangent")
    turn(client,old,"我考虑过判别式法")
    completion=client.post(f"/api/sessions/{old}/complete",json={"reflection":"想到了利用切点"})
    ep=completion.json()["episode"]
    assert ep["evidence_status"]=="SELF_REPORTED_NOT_VERIFIED"
    new=start(client,owner,"hyperbola-tangent")
    found=turn(client,new,"请帮我回忆以前的相似题",request_type="recall",help_requested=True)
    assert found["next_action"]=="RECALL_EPISODE"
    assert found["reference_episode_id"]==ep["id"]
    assert "椭圆" in found["message"]
    different_structure=start(client,owner,"ellipse-focus")
    not_found=turn(client,different_structure,"回忆旧题",request_type="recall",help_requested=True)
    assert not_found["next_action"]=="NO_MEMORY"
    other=start(client,newcomer,"hyperbola-tangent")
    isolated=turn(client,other,"回忆旧题",request_type="recall",help_requested=True)
    assert isolated["next_action"]=="NO_MEMORY"
    # Completion must not be confused with proved mastery.
    assert client.get(f"/api/students/{owner}/dashboard").json()["independent_mastery_verified"] is False


def test_review_scheduling_and_rule_only_marking(client):
    uid=student(client)
    cards=client.get(f"/api/students/{uid}/reviews").json()["reviews"]
    assert len(cards)>=4
    correct=client.post(f"/api/students/{uid}/reviews/geometric-q-one/answer",json={"answer":"S_n=n*a1, 因为q=1"}).json()
    assert correct["rule_match"] is True
    assert correct["not_a_proof_of_mastery"] is True
    assert correct["box_level"]==1
    due=client.get(f"/api/students/{uid}/reviews").json()["reviews"]
    assert "geometric-q-one" not in [x["point_id"] for x in due]
    wrong=client.post(f"/api/students/{uid}/reviews/geometric-q-one/answer",json={"answer":"不知道"}).json()
    assert wrong["rule_match"] is False
    assert wrong["box_level"]==0


def test_math_checker_scope(client):
    ok=client.get("/api/math/known-check/inequality-sum-to-product").json()
    assert ok["valid_under_conditions"] is True
    assert ok["tool"]=="SYMPY_CURATED_CHECK"
    assert client.get("/api/math/known-check/arbitrary-proof").status_code==404


def test_generic_problem_safe_fallback(client):
    uid=student(client)
    r=client.post("/api/sessions",json={"student_id":uid,"custom_problem":"给定一个复杂的未知多项式问题"})
    assert r.status_code==201
    reply=turn(client,r.json()["id"],"这里应该怎么做")
    assert reply["scope"]=="GENERIC_FALLBACK"
    assert reply["math_verified"] is False
    assert "模拟" in reply["message"]


def test_validation_and_completed_session_lock(client):
    uid=student(client)
    assert client.post("/api/sessions",json={"student_id":uid,"problem_id":"not-exist"}).status_code==422
    sid=start(client,uid)
    assert client.post(f"/api/sessions/{sid}/turns",json={"student_text":""}).status_code==422
    assert client.get("/api/sessions/not-exist").status_code==404
    assert client.post(f"/api/sessions/{sid}/complete",json={"reflection":"完成"}).status_code==200
    assert client.post(f"/api/sessions/{sid}/turns",json={"student_text":"继续"}).status_code==409
    assert client.patch(f"/api/sessions/{sid}/mode",json={"mode":"ANALYZE"}).status_code==409


def test_review_suggestion_is_contextual_and_not_interruptive(client):
    uid=student(client)
    sid=start(client,uid,"geometric-sum")
    assert client.get(f"/api/sessions/{sid}/review-suggestion").json()["suggestion"] is None
    client.post(f"/api/sessions/{sid}/complete",json={"reflection":"检查 q=1 的特殊情况"})
    suggestion=client.get(f"/api/sessions/{sid}/review-suggestion").json()
    assert suggestion["suggestion"]["id"]=="geometric-q-one"
    client.post(f"/api/students/{uid}/reviews/geometric-q-one/answer",json={"answer":"n*a1"})
    assert client.get(f"/api/sessions/{sid}/review-suggestion").json()["suggestion"] is None


def test_curated_knowledge_search_is_real_local_index(client):
    result=client.post('/api/knowledge/search',json={'query':'切线','problem_id':'ellipse-tangent'}).json()
    assert result['engine']=='LOCAL_FTS5_BM25_AND_STRUCTURE_V1'
    assert result['corpus_size']>=8
    assert any(h['id']=='method-conic-tangent' for h in result['hits'])
    assert any(m['id']=='conic_tangent' for m in result['methods'])
    assert client.post('/api/knowledge/search',json={'query':'切线','problem_id':'no-id'}).status_code==422
