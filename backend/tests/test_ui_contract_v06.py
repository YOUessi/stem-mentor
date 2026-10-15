"""Study Studio static asset + backend contract regression, no browser deps."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv("STEM_MENTOR_DB",str(tmp_path/"synthetic.sqlite3"))
    with TestClient(app) as api:
        yield api

def test_studio_markup_preserves_learning_features(client):
    response=client.get("/")
    assert response.status_code==200
    html=response.text
    for item in (
        "id=\"problemSelect\"","id=\"studentInput\"","id=\"chat\"",
        "id=\"thinkingStage\"","id=\"mathLeft\"","id=\"mathRight\"",
        "id=\"methodSearchBtn\"","id=\"reviewList\"","id=\"historyList\"",
        "id=\"splitHandle\"","id=\"commandPalette\"","id=\"commandTrigger\"",
        "id=\"heroEpisodeCount\"","id=\"heroReviewCount\""):
        assert html.count(item)==1,item
    assert '/assets/studio.js' in html
    assert 'STEM MENTOR' in html
    assert 'v0.6' in html

def test_studio_assets_are_local_and_motion_safe(client):
    page=client.get("/").text
    assert 'src="https://' not in page
    assert '<script src="/assets/app.js" defer></script>' in page
    assert '<script src="/assets/studio.js" defer></script>' in page
    js=client.get("/assets/studio.js")
    assert js.status_code==200
    assert 'initPalette' in js.text
    assert 'initSplit' in js.text
    assert 'window.stemSaveDraft' in js.text
    css=client.get("/assets/styles.css")
    assert css.status_code==200
    assert 'prefers-reduced-motion' in css.text
    assert '.command-overlay' in css.text
    assert '.split-handle' in css.text

def test_curated_tutor_api_unchanged_by_visual_upgrade(client):
    catalog=client.get("/api/catalog").json()
    assert len(catalog["problems"])>=15
    assert len(catalog["methods"])>=26
    health=client.get("/health").json()
    assert health["engine"]=="DETERMINISTIC_SIMULATION"
    assert health["llm_api_used"] is False
    student=client.post("/api/students",json={"alias":"界面测试合成学生"}).json()["id"]
    new=client.post("/api/sessions",json={"student_id":student,"mode":"INDEPENDENT","problem_id":"distance-ratio"})
    assert new.status_code==201
    session_id=new.json()["id"]
    turn=client.post("/api/sessions/"+session_id+"/turns",json={"student_text":"我先看看题目条件"})
    assert turn.status_code==200
    assert turn.json()["next_action"]=="WAIT"
    assert turn.json()["hint_level"]==0
