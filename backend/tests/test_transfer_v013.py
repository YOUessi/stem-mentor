"""Authentic prior-history transfer cycle. Tests are synthetic, NOT achievement evidence."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv("STEM_MENTOR_DB",str(tmp_path/"synthetic-transfer.sqlite3"))
    with TestClient(app) as c: yield c

def student(c):
    response=c.post("/api/students",json={"alias":"模拟学习者"})
    assert response.status_code==201
    return response.json()["id"]

def session(c,uid,pid="ellipse-tangent",mode="INDEPENDENT"):
    r=c.post("/api/sessions",json={"student_id":uid,"problem_id":pid,"mode":mode})
    assert r.status_code==201,r.text
    return r.json()["id"]

def history(c,uid,pid="ellipse-tangent"):
    old=session(c,uid,pid)
    c.post(f"/api/sessions/{old}/turns",json={
        "student_text":"我先利用已知条件思考是否需要切线的局部关系"})
    completed=c.post(f"/api/sessions/{old}/complete",json={
        "reflection":"复盘：需要先检验切点属于曲线，具体学生步骤未数学验证。"})
    assert completed.status_code==200
    return completed.json()["episode"]["id"]

def baseline(c,sid,text="我先列出这道新题的已知条件与切线目标。"):
    return c.post(f"/api/sessions/{sid}/transfer/attempts",
                  json={"phase":"BEFORE_RECALL","attempt_text":text,"self_report_stage":"FORWARD"})

def recall(c,sid):
    return c.post(f"/api/sessions/{sid}/turns",json={
        "student_text":"请提醒我自己过去做过的结构相近题，先不要告诉我完整答案。",
        "request_type":"recall","help_requested":True})

def followup(c,sid,episode):
    return c.post(f"/api/sessions/{sid}/transfer/attempts",json={
        "phase":"AFTER_RECALL","source_episode_id":episode,
        "attempt_text":"对比旧椭圆与新双曲线，先重新核对切点约束与符号区别。",
        "self_report_stage":"BACKWARD"})

def test_new_session_hides_old_titles_until_baseline(client):
    uid=student(client); history(client,uid)
    sid=session(client,uid,"hyperbola-tangent")
    result=client.get(f"/api/sessions/{sid}/transfer")
    assert result.status_code==200
    body=result.json()
    assert body["phase"]=="BEFORE_RECALL"
    assert body["history_candidate"] is None
    assert body["math_verified"] is False
    assert "椭圆" not in str(body)
    assert body["records"]==[]

def test_real_owner_history_and_unverified_before_after(client):
    uid=student(client);eid=history(client,uid)
    sid=session(client,uid,"hyperbola-tangent")
    before=baseline(client,sid)
    assert before.status_code==201,before.text
    attempt=before.json()
    assert attempt["phase"]=="BEFORE_RECALL"
    assert attempt["math_verified"] is False
    assert attempt["evidence_status"]=="NO_IN_APP_HINTS_OBSERVED_NOT_PROOF"
    assert attempt["hint_count_at_submission"]==0
    unlocked=client.get(f"/api/sessions/{sid}/transfer").json()
    assert unlocked["history_candidate"]["source_episode_id"]==eid
    assert "椭圆" in unlocked["history_candidate"]["prior_problem_title"]
    assert "正确" not in unlocked["history_candidate"]["prior_problem_title"]
    assert followup(client,sid,eid).status_code==409  # No actual recall turn yet
    reply=recall(client,sid).json()
    assert reply["next_action"]=="RECALL_EPISODE"
    assert reply["reference_episode_id"]==eid
    later=followup(client,sid,eid)
    assert later.status_code==201,later.text
    assert later.json()["math_verified"] is False
    assert later.json()["evidence_status"]=="STUDENT_POST_RECALL_NOT_VERIFIED"
    res=client.get(f"/api/sessions/{sid}/transfer").json()
    assert [x["phase"] for x in res["records"]]==["BEFORE_RECALL","AFTER_RECALL"]
    assert res["independent_mastery_verified"] is False
    assert "学生" in res["disclaimer"]
    with TestClient(app) as restart:
        assert len(restart.get(f"/api/sessions/{sid}/transfer").json()["records"])==2

def test_duplicate_phase_not_double_counted(client):
    uid=student(client);sid=session(client,uid)
    assert baseline(client,sid).status_code==201
    assert baseline(client,sid).status_code==409
    assert len(client.get(f"/api/sessions/{sid}/transfer").json()["records"])==1

def test_fake_or_other_student_history_cannot_be_used(client):
    alice=student(client);bob=student(client)
    own=history(client,alice);sid=session(client,bob,"hyperbola-tangent")
    assert baseline(client,sid).status_code==201
    assert client.get(f"/api/sessions/{sid}/transfer").json()["history_candidate"] is None
    assert followup(client,sid,own).status_code in (404,422)
    assert recall(client,sid).json()["next_action"]=="NO_MEMORY"

def test_unrelated_episodes_are_not_recommendations(client):
    uid=student(client);history(client,uid,"triangle-sss")
    target=session(client,uid,"ellipse-focus")
    assert baseline(client,target).status_code==201
    assert client.get(f"/api/sessions/{target}/transfer").json()["history_candidate"] is None
    assert recall(client,target).json()["next_action"]=="NO_MEMORY"

def test_baseline_requires_independent_mode_and_before_tutor_help(client):
    uid=student(client)
    guide=session(client,uid,"hyperbola-tangent","GUIDE")
    assert baseline(client,guide).status_code==409
    early=session(client,uid,"hyperbola-tangent")
    r=client.post(f"/api/sessions/{early}/turns",json={
        "student_text":"卡住了", "help_requested":True})
    assert r.status_code==200
    assert baseline(client,early).status_code==409

def test_before_recall_mode_but_unhinted_turns_are_recorded_not_scored(client):
    uid=student(client);sid=session(client,uid)
    response=client.post(f"/api/sessions/{sid}/turns",json={"student_text":"先写下一步观察"})
    assert response.json()["next_action"]=="WAIT"
    out=baseline(client,sid)
    assert out.status_code==201
    assert out.json()["math_verified"] is False

def test_cannot_write_after_completion_and_validation(client):
    uid=student(client);sid=session(client,uid)
    assert baseline(client,sid,text="x").status_code==422
    assert baseline(client,sid).status_code==201
    assert client.post(f"/api/sessions/{sid}/complete",json={"reflection":"我尝试了"}).status_code==200
    assert followup(client,sid,"any").status_code==409

def test_student_summary_never_claims_correctness(client):
    uid=student(client);other=student(client)
    history(client,uid);sid=session(client,uid,"hyperbola-tangent")
    assert baseline(client,sid).status_code==201
    status=client.get(f"/api/students/{uid}/transfer-summary").json()
    assert status["baseline_attempts"]==1
    assert status["post_recall_attempts"]==0
    assert status["mathematically_verified_attempts"]==0
    assert status["independent_mastery_verified"] is False
    assert client.get(f"/api/students/{other}/transfer-summary").json()["baseline_attempts"]==0


def test_late_history_is_not_a_prior_learning_episode(client):
    """A completed episode created after the target session starts cannot count
    as prior knowledge for this frozen independent-baseline experiment."""
    uid=student(client)
    target=session(client,uid,"hyperbola-tangent")
    assert baseline(client,target).status_code==201
    # Episode recorded later should not become past knowledge
    # available when this target exercise began.
    late=history(client,uid,"ellipse-tangent")
    current=client.get(f"/api/sessions/{target}/transfer")
    assert current.status_code==200
    assert current.json()["history_candidate"] is None
    assert current.json()["phase"]=="NO_MATCHING_HISTORY"
    assert followup(client,target,late).status_code==404


def test_prior_real_episode_still_available_when_later_unrelated_history_exists(client):
    uid=student(client)
    past=history(client,uid,"ellipse-tangent")
    target=session(client,uid,"hyperbola-tangent")
    assert baseline(client,target).status_code==201
    # Later source from the same structural family cannot replace the old.
    history(client,uid,"parabola-tangent")
    current=client.get(f"/api/sessions/{target}/transfer").json()
    assert current["history_candidate"]["source_episode_id"]==past


def test_concurrent_duplicate_baseline_is_one_immutable_record(client):
    """Concurrent demo UI requests must not overwrite baseline or cause a 500."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    uid=student(client)
    sid=session(client,uid)
    barrier=Barrier(6)
    def attempt(i):
        barrier.wait(timeout=10)
        return client.post(f"/api/sessions/{sid}/transfer/attempts",json={
            "phase":"BEFORE_RECALL",
            "attempt_text":f"我的原始思路第{i}次提交，先检查条件和目标。"})
    with ThreadPoolExecutor(max_workers=6) as workers:
        responses=list(workers.map(attempt,range(6)))
    assert sorted(r.status_code for r in responses)==[201,409,409,409,409,409], [
        (r.status_code,r.text[:180]) for r in responses]
    actual=client.get(f"/api/sessions/{sid}/transfer").json()["records"]
    assert len(actual)==1
    assert actual[0]["phase"]=="BEFORE_RECALL"
    assert actual[0]["evidence_status"]=="NO_IN_APP_HINTS_OBSERVED_NOT_PROOF"
