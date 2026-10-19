"""V0.12 probability/statistics visual catalog contracts with explicit teaching limits."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

IDS={"prob-choose","prob-permute","prob-tree","prob-binomial","prob-hypergeo",
     "prob-normal","stats-bernoulli","stats-regression","stats-summary"}

@pytest.fixture
def client(tmp_path,monkeypatch):
 monkeypatch.setenv("STEM_MENTOR_DB",str(tmp_path/"probability-synthetic.sqlite3"))
 with TestClient(app) as c:yield c

def test_scene_catalog_exact_count_and_real_curriculum_evidence(client):
 cat=client.get("/api/math-lab/catalog").json()
 assert len(cat["presets"])==71
 assert len(cat["counts"]["scene_families"])==11
 assert len(cat["topics"])==113
 assert cat["counts"]["interactive_foundations"]==77
 assert cat["counts"]["planned_concepts"]==36
 assert cat["counts"]["scene_families"]["probability_2d"]==6
 assert cat["counts"]["scene_families"]["statistics_2d"]==3
 assert cat["no_llm_api"] is True
 assert cat["expert_review"]=="PENDING"
 allids={s["id"]:s for s in cat["presets"]}
 assert IDS<=set(allids)
 for id in IDS:
    s=allids[id]
    assert s["tool"] in ("probability_2d","statistics_2d")
    assert s["assist_default"] is False
    assert s["source"]=="PROJECT_AUTHORED"
    assert s["expert_review"]=="PENDING"
    assert len(s["thinking_prompts"])==3
    assert all(v["min"]<=v["value"]<=v["max"] for v in s["params"])

def test_statistics_topics_require_actual_statistics_scene(client):
 topics={t["concept"]:t for t in client.get("/api/math-lab/catalog").json()["topics"]}
 for topic in ("均值中位数众数","方差标准差"):
    item=topics[topic]
    assert item["status"]=="INTERACTIVE_FOUNDATION"
    assert "stats-summary" in item["available_presets"]
    assert "已验证" not in item["capability"]
 assert topics["正态分布"]["available_presets"]==["prob-normal"]
 assert "prob-hypergeo" in topics["超几何分布"]["available_presets"]
 assert topics["二面角"]["status"]=="PLANNED"

def test_green_ui_and_offline_browser_assets(client):
 html=client.get("/").text
 assert 'content="#174938"' in html
 assert 'id="studentInput"' in html
 assert 'SIMULATION · v0.12' in html
 assert '/assets/lab/probability_math.js' in html
 assert '/assets/lab/probability2d.js' in html
 for path in ["/assets/lab/probability_math.js","/assets/lab/probability2d.js"]:
    assert client.get(path).status_code==200
 assert client.get("/openapi.json").json()["info"]["version"]=="0.12.0"
 assert client.get("/health").json()["llm_api_used"] is False
