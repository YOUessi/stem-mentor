"""The iPad pilot is additive; no teacher-only answer or cloud ink route."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app

ROOT=Path(__file__).resolve().parents[2]
@pytest.fixture()
def client(tmp_path,monkeypatch):
    monkeypatch.setenv("STEM_MENTOR_DB",str(tmp_path/"synthetic.sqlite3"))
    with TestClient(app) as c:yield c

def test_ipad_routes_and_old_home_coexist(client):
    old=client.get("/")
    home=client.get("/ipad")
    study=client.get("/ipad/study")
    assert all(r.status_code==200 for r in (old,home,study))
    assert old.text!=home.text
    assert home.text==study.text
    assert 'content="#174938"' in home.text
    assert '<canvas id="inkCanvas"' in home.text
    assert 'id="agentPanel"' in home.text
    assert 'id="continueWriting"' in home.text
    assert 'id="recentSessions"' in home.text
    assert 'id="studentInput"' in old.text

def test_ipad_assets_stay_local_and_no_secret_tool_exposed(client):
    html=client.get("/ipad").text
    for name in ["ink_core.js","storage.js","app.js","ipad.css"]:
        assert ("/assets/ipad/"+name) in html
        assert client.get("/assets/ipad/"+name).status_code==200
    assert "https://cdn" not in html
    assert client.get("/openapi.json").json()["info"]["version"]=="0.14.0"
    assert client.get("/assets/ipad/index.html").status_code==200

def test_demo_session_is_compatible_but_reading_ipad_does_not_write_records(client):
    st=client.post("/api/students",json={"alias":"合成手写用户"}).json()["id"]
    problem=client.get("/api/catalog").json()["problems"][0]["id"]
    sess=client.post("/api/sessions",json={"student_id":st,
        "problem_id":problem,"mode":"INDEPENDENT"}).json()
    before=client.get(f"/api/sessions/{sess['id']}").json()
    for _ in range(3):
        assert client.get("/ipad/study").status_code==200
    after=client.get(f"/api/sessions/{sess['id']}").json()
    assert before["turns"]==after["turns"]==[]
    assert after["student_id"]==st
    assert after["hint_count"]==0
    assert client.get("/health").json()["llm_api_used"] is False
    assert client.get("/api/students/"+st+"/dashboard").json()["independent_mastery_verified"] is False

def test_pilot_ink_is_persisted_locally_not_as_grading_api(client):
    text=(ROOT/"apps/web/ipad/app.js").read_text(encoding="utf8")
    store=(ROOT/"apps/web/ipad/storage.js").read_text(encoding="utf8")
    assert "indexedDB" in store
    assert "indexedDB" not in text or "Store.save" in text
    assert "Store.save" in text
    assert "attempt_text" not in text or "Ink" in text
    assert '"/turns"' not in text or "sendToAgent" in text
    assert "fetch('/api/ink" not in text
    assert "getCoalescedEvents" in text
    assert "pointerType" in text
