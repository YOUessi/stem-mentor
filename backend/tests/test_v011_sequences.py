"""v0.11 finite-sequence scene contracts and explicit curriculum support limits."""
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.math_lab_catalog import lab_catalog

ROOT=Path(__file__).resolve().parents[2]
NEW={"seq-arithmetic","seq-geometric","seq-geometric-edge",
 "seq-linear-recurrence","seq-two-term","seq-partial-sum","seq-growth","seq-fixed-point"}

def test_v011_presets_exact_and_previous_49_retained(tmp_path,monkeypatch):
    monkeypatch.setenv("STEM_MENTOR_DB",str(tmp_path/"synthetic.sqlite3"))
    with TestClient(app) as client:
        response=client.get("/api/math-lab/catalog")
        assert response.status_code==200
        body=response.json()
        assert body["no_llm_api"] is True
        assert body["expert_review"]=="PENDING"
        presets={p["id"]:p for p in body["presets"]}
        assert len(presets)>=57
        assert NEW <= set(presets)
        assert {"fn-linear","3d-plane","sets-operations","interval-single","unit-circle"}<=set(presets)
        assert body["counts"]["scene_families"]["sequence_2d"]==8
        assert len(body["counts"]["scene_families"])>=9
        assert body["counts"]["interactive_foundations"]>=63
        assert body["counts"]["planned_concepts"]<=50
        assert len(body["topics"])==113
        assert client.get("/health").json()["llm_api_used"] is False

def test_new_scene_contracts_and_prompt_scaffolds():
    lab=lab_catalog()
    presets={p["id"]:p for p in lab["presets"]}
    for sid in NEW:
        item=presets[sid]
        assert item["tool"]=="sequence_2d"
        assert item["assist_default"] is False
        assert item["source"]=="PROJECT_AUTHORED"
        assert item["expert_review"]=="PENDING"
        assert len(item["thinking_prompts"])==3
        assert all(isinstance(s,str) and len(s)>8 for s in item["thinking_prompts"])
        assert len({p["key"] for p in item["params"]})==len(item["params"])
        assert any(p["key"]=="n" for p in item["params"])
        assert all(p["min"]<=p["value"]<=p["max"] for p in item["params"])
    special=next(p for p in presets["seq-geometric-edge"]["params"] if p["key"]=="q")
    assert len(special["options"])==5
    assert all(t["value"]<5 for t in special["options"])

def test_curriculum_evidence_not_faked():
    by_name={t["concept"]:t for t in lab_catalog()["topics"]}
    for topic in ("数列概念与递推","等差数列","等比数列","数列求和与数列模型"):
        item=by_name[topic]
        assert item["status"]=="INTERACTIVE_FOUNDATION"
        assert item["available_presets"]
        assert all(p in NEW for p in item["available_presets"])
        assert "未" in item["capability_limits"] or "有限" in item["capability_limits"]
    assert by_name["二面角"]["status"]=="PLANNED"
    assert by_name["正态分布"]["status"]=="INTERACTIVE_FOUNDATION"

def test_ui_retains_original_green_theme_and_local_modules(tmp_path,monkeypatch):
    monkeypatch.setenv("STEM_MENTOR_DB",str(tmp_path/"synthetic.sqlite3"))
    with TestClient(app) as client:
        html=client.get("/").text
        assert 'content="#174938"' in html
        assert 'SIMULATION · v0.12' in html
        assert 'id="studentInput"' in html
        for asset in ("sequences_math.js","sequences2d.js"):
            assert ("/assets/lab/"+asset) in html
            assert client.get("/assets/lab/"+asset).status_code==200
        assert client.get("/assets/math_lab.css").status_code==200
        assert client.get("/openapi.json").json()["info"]["version"]!='0.0.0'  # Exact current version is independently checked by v0.12 tests
