"""Green v0.7 math media and student hypothesis tests.

No model call, no proof of arbitrary text, no real learner data.
"""
from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.study_visuals import visuals

ROOT=Path(__file__).resolve().parents[2]

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv("STEM_MENTOR_DB",str(tmp_path/"simulation.sqlite3"))
    with TestClient(app) as api:
        yield api

def make_session(client,problem_id="distance-ratio",mode="GUIDE"):
    student=client.post("/api/students",json={"alias":"合成学生"}).json()["id"]
    session=client.post("/api/sessions",json={"student_id":student,"problem_id":problem_id,"mode":mode})
    assert session.status_code==201
    return session.json()["id"]

def test_all_curated_math_data_only_contains_givens(client):
    cards=visuals()
    assert len(cards)>=15
    for pid,entry in cards.items():
        r=client.get("/api/study/visual/"+pid)
        assert r.status_code==200
        value=r.json()
        assert value["problem_id"]==pid
        assert value["teacher_solution_included"] is False
        assert "latex" in value and len(value["latex"])<350
        assert all(x not in value for x in ("solution","proof","teacher_only","hidden_steps"))
    assert client.get("/api/study/visual/unlisted-problem").status_code==404

def test_geometry_is_scoped_and_requires_active_student_exploration(client):
    ratio=client.get("/api/study/visual/distance-ratio").json()
    assert ratio["geometry"]["measure"]=="ratio"
    assert ratio["geometry"]["target"]==2
    assert ratio["geometry"]["foci"]==[[0,0],[6,0]]
    assert not any(k in ratio["geometry"] for k in ("circle","radius","curve_formula","solution"))
    summed=client.get("/api/study/visual/ellipse-focus").json()
    assert summed["geometry"]["measure"]=="sum"
    assert summed["geometry"]["target"]==10
    ellipse=client.get("/api/study/visual/ellipse-tangent").json()
    assert ellipse["geometry"]["kind"]=="conic"
    assert ellipse["geometry"]["curve"]=="ellipse"
    unrelated=client.get("/api/study/visual/arithmetic-sum").json()
    assert "geometry" not in unrelated

def test_student_links_are_unproved_and_persist(client):
    sid=make_session(client)
    before=client.get("/api/sessions/"+sid+"/reasoning-map").json()
    assert before["student_steps"]==0
    r=client.post("/api/sessions/"+sid+"/turns",
                  json={"student_text":"我先观察两个固定点","self_report_stage":"FORWARD"})
    assert r.status_code==200
    r=client.post("/api/sessions/"+sid+"/turns",
                  json={"student_text":"卡在了距离比的形式","self_report_stage":"STUCK"})
    assert r.status_code==200
    req={"source":"student-step-1","target":"student-step-2","label":"怀疑这两条关系可以连接"}
    result=client.post("/api/sessions/"+sid+"/thinking-links",json=req)
    assert result.status_code==201,result.text
    body=result.json()
    assert body["verified"] is False and body["is_proof"] is False
    assert body["relation"]=="STUDENT_HYPOTHESIS_UNVERIFIED"
    duplicate=client.post("/api/sessions/"+sid+"/thinking-links",json=req)
    assert duplicate.status_code==201
    assert duplicate.json()["id"]==body["id"]
    in_graph=client.get("/api/sessions/"+sid+"/reasoning-map").json()
    assert not in_graph["contains_teacher_solution"]
    edges=[e for e in in_graph["edges"] if e["relation"]=="STUDENT_HYPOTHESIS_UNVERIFIED"]
    assert len(edges)==1
    assert edges[0]["label"]==req["label"] and edges[0]["verified"] is False
    with TestClient(app) as restarted:
        again=restarted.get("/api/sessions/"+sid+"/reasoning-map").json()
    assert any(e["relation"]=="STUDENT_HYPOTHESIS_UNVERIFIED" for e in again["edges"])

def test_links_reject_nonexistent_hidden_and_same_nodes(client):
    sid=make_session(client)
    for payload in [
      {"source":"given","target":"given"},
      {"source":"teacher-only-bridge","target":"goal"},
      {"source":"student-step-1","target":"goal"},
      {"source":"given","target":"student-step-777"},
      {"source":"given","target":"goal","label":"z"*101}
    ]:
        result=client.post("/api/sessions/"+sid+"/thinking-links",json=payload)
        assert result.status_code==422,payload
    ok=client.post("/api/sessions/"+sid+"/thinking-links",
                   json={"source":"given","target":"goal","label":"只是一个假设"})
    assert ok.status_code==201
    client.post("/api/sessions/"+sid+"/complete",json={"reflection":"停止"})
    closed=client.post("/api/sessions/"+sid+"/thinking-links",
                       json={"source":"goal","target":"given","label":"继续"})
    assert closed.status_code==409

def test_restricted_link_count(client):
    sid=make_session(client)
    for i in range(7):
        client.post("/api/sessions/"+sid+"/turns",json={"student_text":"合成尝试"+str(i)})
    all_ids=["given","goal"]+["student-step-"+str(i+1) for i in range(7)]
    possibilities=[(a,b) for a in all_ids for b in all_ids if a!=b]
    for a,b in possibilities[:30]:
        r=client.post("/api/sessions/"+sid+"/thinking-links",json={"source":a,"target":b})
        assert r.status_code==201,(a,b,r.text)
    rejected=client.post("/api/sessions/"+sid+"/thinking-links",
       json={"source":possibilities[30][0],"target":possibilities[30][1]})
    assert rejected.status_code==409

def test_green_theme_and_local_renderer_assets(client):
    root=client.get("/").text
    assert 'content="#174938"' in root
    assert '/assets/styles.css' in root
    assert '/assets/study_tools.css' in root
    assert '/assets/vendor/mathjax/tex-svg.js' in root
    assert '/assets/study_tools.js' in root
    assert client.get("/assets/study_tools.js").status_code==200
    assert client.get("/assets/vendor/mathjax/tex-svg.js").status_code==200
    assert "mathjax.org" not in root
    assert not (ROOT/"apps/web/vendor/mathjax/fonts").exists()
    assert (ROOT/"apps/web/vendor/mathjax/LICENSE").exists()
