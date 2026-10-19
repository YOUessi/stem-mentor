"""Contract checks authored before v0.9 catalog/renderer implementation."""
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app

ROOT=Path(__file__).resolve().parents[2]
NEW_IDS={'vec2d-add','vec2d-projection','unit-circle','derivative-quadratic',
         'derivative-cubic','derivative-log','derivative-abs',
         '3d-section-prism','3d-section-pyramid','3d-section-sphere'}

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('STEM_MENTOR_DB',str(tmp_path/'v09.sqlite3'))
    with TestClient(app) as c: yield c

def test_v09_ten_new_scenes_preserve_previous_twenty_nine(client):
    data=client.get('/api/math-lab/catalog').json()
    ids={p['id'] for p in data['presets']}
    assert NEW_IDS<=ids, f'Missing planned v0.9 scenes: {NEW_IDS-ids}'
    assert len(ids)==49
    assert {'fn-linear','fn-piecewise','tri-ssa','conic-ellipse','3d-plane'}<=ids
    assert data['no_llm_api'] is True
    assert len(data['topics'])==113

def test_ready_coverage_links_real_scene_not_only_generic_family(client):
    data=client.get('/api/math-lab/catalog').json()
    known={p['id'] for p in data['presets']}
    for topic in data['topics']:
        assert 'available_presets' in topic,topic['concept']
        assert 'capability_limits' in topic,topic['concept']
        ids=topic['available_presets']
        assert all(i in known for i in ids)
        if topic['status']=='INTERACTIVE_FOUNDATION': assert ids,topic['concept']
        else: assert ids==[],topic['concept']
    by_name={t['concept']:t for t in data['topics']}
    assert by_name['弧度制和单位圆']['available_presets']==['unit-circle']
    assert 'vec2d-projection' in by_name['向量投影与夹角']['available_presets']
    assert by_name['二面角']['status']=='PLANNED'
    assert by_name['直线平面夹角']['status']=='PLANNED'
    assert '展开图' in by_name['空间截面与展开图']['capability_limits']

def test_new_assets_and_adaptive_green_family_controls(client):
    html=client.get('/').text
    assert 'content="#174938"' in html
    assert 'id="studentInput"' in html and 'id="labPlot"' in html
    for path in ['exploration_math.js','explorers2d.js','sections3d.js']:
        assert '/assets/lab/'+path in html,path
        assert client.get('/assets/lab/'+path).status_code==200
    assert 'id="labAssistToggle"' in html
    assert client.get('/health').json()['llm_api_used'] is False

@pytest.mark.parametrize('scene',sorted(NEW_IDS))
def test_new_scene_has_clear_boundary_and_explicit_core_module(scene,client):
    scene_map={p['id']:p for p in client.get('/api/math-lab/catalog').json()['presets']}
    assert scene in scene_map,scene
    item=scene_map[scene]
    assert item['expert_review']=='PENDING'
    assert item['source']=='PROJECT_AUTHORED'
    assert item.get('description') and item.get('latex')
    assert item.get('assist_default') is False
    keys=[p['key'] for p in item['params']]
    assert len(set(keys))==len(keys)
    assert all(p['min']<=p['value']<=p['max'] for p in item['params'])


def test_catalog_builders_reproduce_versioned_evidence_without_mutating_repo(tmp_path):
    import shutil,subprocess,sys
    source=ROOT/'curriculum'/'highschool_math'
    for name in ['build_presets.py','build_curriculum.py','extend_v09.py','extend_v010.py']:
        shutil.copy2(source/name,tmp_path/name)
    subprocess.run([sys.executable,str(tmp_path/'build_presets.py')],cwd=tmp_path,check=True,capture_output=True)
    subprocess.run([sys.executable,str(tmp_path/'build_curriculum.py')],cwd=tmp_path,check=True,capture_output=True)
    for name in ['visual_presets.json','curriculum_map.json']:
        assert (source/name).read_bytes()==(tmp_path/name).read_bytes(),name


def test_projection_only_exposes_parameters_that_change_its_geometry(client):
    scenes={p['id']:p for p in client.get('/api/math-lab/catalog').json()['presets']}
    # k changes scaled-a in the addition scene, not projection onto b.
    assert {p['key'] for p in scenes['vec2d-projection']['params']}=={'ax','ay','bx','by'}
    assert 'k' in {p['key'] for p in scenes['vec2d-add']['params']}
