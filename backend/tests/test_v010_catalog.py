"""v0.10 contracts: new scene data and discrete mathematical choices, not grading."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import pytest
from fastapi.testclient import TestClient
from app.main import app
import app.math_lab_catalog as catalog

ROOT=Path(__file__).resolve().parents[2]
NEW_IDS={'complex-point','complex-operations','complex-rotation','sets-operations',
         'sets-complement','interval-single','interval-operations','ineq-linear',
         'ineq-quadratic','ineq-absolute'}

@pytest.fixture
def client(monkeypatch,tmp_path):
    monkeypatch.setenv('STEM_MENTOR_DB',str(tmp_path/'synthetic-v010.sqlite3'))
    with TestClient(app) as c: yield c


def test_v010_adds_ten_scenes_without_losing_the_original_39(client):
    body=client.get('/api/math-lab/catalog').json()
    ids={p['id'] for p in body['presets']}
    assert NEW_IDS<=ids,NEW_IDS-ids
    assert len(ids)==49
    assert len(body['topics'])==113 and body['no_llm_api'] is True
    assert {'vec2d-add','unit-circle','derivative-log','3d-section-prism','tri-ssa',
            'fn-linear','conic-ellipse','3d-sphere'}<=ids
    assert len(body['counts']['scene_families'])==8


def test_discrete_parameter_metadata_carries_mathematical_labels(client):
    presets={p['id']:p for p in client.get('/api/math-lab/catalog').json()['presets']}
    assert NEW_IDS<=presets.keys()
    for scene,key in [('complex-operations','op'),('sets-operations','op'),
                      ('interval-single','lc'),('interval-operations','op'),
                      ('ineq-quadratic','relation')]:
        param=next(p for p in presets[scene]['params'] if p['key']==key)
        assert len(param['options'])>=2
        values=[p['value'] for p in param['options']]
        assert len(set(values))==len(values) and param['value'] in values
        assert all(isinstance(v,(int,float)) for v in values)
        assert all(p['label'] for p in param['options'])
    for name in NEW_IDS:
        assert presets[name]['assist_default'] is False
        assert presets[name]['expert_review']=='PENDING'


@pytest.mark.parametrize('invalid',['duplicate','default_missing','outside_bounds','nonfinite','missing_label'])
def test_catalog_rejects_invalid_choice_metadata(tmp_path,monkeypatch,invalid):
    # A production implementation that ignores options must fail this test.
    original=catalog.ROOT
    data=json.loads((original/'visual_presets.json').read_text('utf8'))
    p=data['presets'][0]['params'][0]
    good=p['value'];bad=p['max']+1
    if invalid=='duplicate': options=[{'value':good,'label':'a'},{'value':good,'label':'b'}]
    elif invalid=='default_missing': options=[{'value':p['min'],'label':'a'}];p['value']=p['max']
    elif invalid=='outside_bounds': options=[{'value':good,'label':'a'},{'value':bad,'label':'b'}]
    elif invalid=='nonfinite': options=[{'value':good,'label':'a'},{'value':float('nan'),'label':'b'}]
    else: options=[{'value':good,'label':''}]
    p['options']=options
    (tmp_path/'visual_presets.json').write_text(json.dumps(data),'utf8')
    shutil.copy2(original/'curriculum_map.json',tmp_path/'curriculum_map.json')
    monkeypatch.setattr(catalog,'ROOT',tmp_path)
    catalog.lab_catalog.cache_clear()
    try:
        with pytest.raises(ValueError,match='(?i)(option|choice)'):
            catalog.lab_catalog()
    finally:
        catalog.lab_catalog.cache_clear()


def test_v010_course_claims_bind_to_real_presets_only(client):
    data=client.get('/api/math-lab/catalog').json()
    topics={t['concept']:t for t in data['topics']}
    for concept,scene in [('复数与复平面','complex-point'),('复数加减乘除及几何意义','complex-operations'),
                          ('集合及其表示','sets-operations'),('交集并集补集','sets-complement'),
                          ('一元二次不等式','ineq-quadratic')]:
        assert scene in topics[concept]['available_presets'],concept
    assert topics['全称量词与存在量词']['status']=='PLANNED'
    assert topics['二面角']['status']=='PLANNED'
    assert '有限' in topics['集合及其表示']['capability_limits']
    assert '未实现' in topics['含参数不等式']['capability_limits']


def test_v010_builders_are_deterministic_and_keep_prior_models(tmp_path):
    source=ROOT/'curriculum/highschool_math'
    assert (source/'extend_v010.py').exists()
    for file in source.glob('*.py'):shutil.copy2(file,tmp_path/file.name)
    for file in ('build_presets.py','build_curriculum.py'):
        subprocess.run([sys.executable,str(tmp_path/file)],cwd=tmp_path,check=True,capture_output=True)
    for file in ('visual_presets.json','curriculum_map.json'):
        assert (source/file).read_bytes()==(tmp_path/file).read_bytes()
