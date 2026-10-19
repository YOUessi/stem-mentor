"""v0.11b catalog, opt-in extrema scenes, and protected tutoring API contracts."""
from fastapi.testclient import TestClient
from app.main import app
from app.math_lab_catalog import lab_catalog
import pytest

IDS={"extrema-quadratic","extrema-cubic","extrema-absolute",
     "extrema-sine","extrema-log"}

@pytest.fixture()
def client(tmp_path,monkeypatch):
 monkeypatch.setenv("STEM_MENTOR_DB",str(tmp_path/"extrema-demo.sqlite3"))
 with TestClient(app) as c:yield c

def test_extrema_catalog_five_fixed_models_without_spoilers(client):
 data=client.get("/api/math-lab/catalog").json()
 all_ids={p["id"] for p in data["presets"]}
 assert len(all_ids)>=62
 assert IDS<=all_ids
 assert data["counts"]["total_concepts"]==113
 assert data["counts"]["interactive_foundations"]>=63
 assert data["counts"]["planned_concepts"]<=50
 assert data["counts"]["scene_families"]["function_2d"]==22
 assert data["no_llm_api"] is True
 catalog={p["id"]:p for p in data["presets"]}
 for sid in IDS:
   p=catalog[sid]
   assert p["tool"]=="function_2d"
   assert p["assist_default"] is False
   assert p["expert_review"]=="PENDING"
   assert len(p["thinking_prompts"])==3
   assert {q["key"] for q in p["params"]}>={"L","R"}
   assert p["prediction_prompt"]
   assert p["source"]=="PROJECT_AUTHORED"

def test_extrema_has_explicit_curriculum_scope(client):
 topics={x["concept"]:x for x in client.get("/api/math-lab/catalog").json()["topics"]}
 assert IDS<=set(topics["极值与最值"]["available_presets"])
 assert "固定函数" in topics["极值与最值"]["capability_limits"]
 assert "extrema-cubic" in topics["导数判断单调性"]["available_presets"]
 assert topics["极值与最值"]["status"]=="INTERACTIVE_FOUNDATION"
 assert topics["二面角"]["status"]=="PLANNED"

def test_green_original_studio_and_assets(client):
 html=client.get("/").text
 assert 'content="#174938"' in html
 assert "SIMULATION · v0.13" in html
 assert "extrema_math.js" in html and "extrema2d.js" in html
 assert 'id="studentInput"' in html
 for name in ["extrema_math.js","extrema2d.js"]:
   assert client.get("/assets/lab/"+name).status_code==200
 assert client.get("/openapi.json").json()["info"]["version"]!='0.0.0'  # New v0.12 suite enforces exact release version
 assert client.get("/health").json()["llm_api_used"] is False
