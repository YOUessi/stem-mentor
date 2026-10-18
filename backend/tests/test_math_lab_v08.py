"""Engineering coverage checks for the offline high-school mathematics laboratory."""
import collections
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.math_lab_catalog import lab_catalog

ROOT=Path(__file__).resolve().parents[2]

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv("STEM_MENTOR_DB",str(tmp_path/"curriculum-demo.sqlite3"))
    with TestClient(app) as c:yield c

def test_curriculum_mapping_is_complete_inventory_not_full_implementation(client):
    doc=client.get("/api/math-lab/catalog")
    assert doc.status_code==200
    body=doc.json()
    assert body["no_llm_api"] is True
    assert body["expert_review"]=="PENDING"
    assert "教育部" not in body["claim"]  # Claim is bounded to engineering tool status.
    assert len(body["topics"])==113
    assert len(body["presets"])==29
    assert body["counts"]["total_concepts"]==113
    assert body["counts"]["scene_presets"]==29
    assert body["counts"]["interactive_foundations"]<body["counts"]["total_concepts"]
    assert "完整教学" not in body["claim"] or "并非" in body["claim"]
    assert all(t["source"]["teacher_review"]=="PENDING" for t in body["topics"])

def test_curriculum_includes_required_high_school_math_themes():
    body=lab_catalog()
    levels={t["level"] for t in body["topics"]}
    assert levels=={"必修","选择性必修","选修拓展"}
    concepts={t["concept"] for t in body["topics"]}
    for name in ["正弦定理","余弦定理","二次函数","椭圆定义及几何性质",
                 "双曲线定义及几何性质","抛物线定义及几何性质",
                 "空间直角坐标系","空间向量与坐标运算",
                 "概率加法与乘法基本关系","条件概率与独立性",
                 "数列概念与递推","统计"]:
        if name=="统计":
            assert any(t["theme"]=="概率与统计" for t in body["topics"])
        else:
            assert name in concepts
    assert "2020" in body["reference"]
    assert body["reference_url"].startswith("https://www.pep.com.cn/")

def test_visual_scene_parameters_and_unique_id_schema():
    doc=lab_catalog()
    ids=[p["id"] for p in doc["presets"]]
    assert len(ids)==len(set(ids))
    genres=collections.Counter(x["tool"] for x in doc["presets"])
    assert genres=={"function_2d":12,"space_3d":8,"conic_2d":6,"triangle_2d":3}
    for scene in doc["presets"]:
        assert scene["source"]=="PROJECT_AUTHORED"
        assert scene["expert_review"]=="PENDING"
        assert scene["simulation"] is True
        assert scene["latex"]
        assert all(p["min"]<=p["value"]<=p["max"] for p in scene["params"])

def test_static_tools_keep_green_ui_and_original_tutoring_contract(client):
    html=client.get("/").text
    assert 'content="#174938"' in html
    assert 'id="studentInput"' in html
    assert 'data-view="lab"' in html
    assert 'id="labPlot"' in html
    assert 'id="labCurriculumList"' in html
    for path in ["/assets/math_lab.css","/assets/lab/plot2d.js",
        "/assets/lab/triangle.js","/assets/lab/scene3d.js",
        "/assets/lab/controller.js"]:
        assert client.get(path).status_code==200,path
    assert client.get("/health").json()["llm_api_used"] is False
    assert client.get("/api/catalog").json()["simulation"] is True

@pytest.mark.parametrize("filename",["plot2d.js","triangle.js","scene3d.js","controller.js"])
def test_no_external_script_execution(filename):
    content=(ROOT/"apps/web/lab"/filename).read_text(encoding="utf8")
    assert "eval(" not in content
    assert "new Function(" not in content
    assert "https://cdn" not in content
    assert "Math.random()" not in content
    assert "javascript:" not in content

def test_curriculum_search_scopes_future_work_explicitly():
    doc=lab_catalog()
    planned=[t for t in doc["topics"] if t["status"]=="PLANNED"]
    assert planned
    assert any(t["recommended_tool"]=="statistics_plot" for t in planned)
    assert any(t["recommended_tool"]=="probability_plot" for t in planned)
    assert any(t["recommended_tool"]=="venn_logic" for t in planned)
