"""Reproducible deterministic decision-policy and local-retrieval acceptance suite.

Not a student study and NOT a metric of natural-language pedagogical quality.
"""
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.retrieval import retrieve

ROOT=Path(__file__).resolve().parent.parent


def simulate():
    cases=json.loads((ROOT/'evaluations'/'synthetic_policy_cases.json').read_text(encoding='utf8'))
    outcomes=[]
    for case in cases:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ['STEM_MENTOR_DB']=str(Path(tmp)/'demo.sqlite3')
            with TestClient(app) as api:
                sid=api.post('/api/students',json={'alias':'合成测试用户'}).json()['id']
                if case.get('setup_history'):
                    old=api.post('/api/sessions',json={'student_id':sid,'problem_id':case['setup_history']}).json()['id']
                    api.post(f'/api/sessions/{old}/turns',json={'student_text':'我尝试从已知条件推导'})
                    api.post(f'/api/sessions/{old}/complete',json={'reflection':'已写下当时的想法'})
                session=api.post('/api/sessions',json={'student_id':sid,'problem_id':case['problem_id'],'mode':case['mode']}).json()['id']
                responses=[]
                for step in case['inputs']:
                    body={'student_text':step['text']}
                    body.update({k:v for k,v in step.items() if k!='text'})
                    response=api.post(f'/api/sessions/{session}/turns',json=body)
                    responses.append(response.json())
                last=responses[-1]
                action_ok=last.get('next_action')==case['expect_action']
                rule_ok=last.get('decision_trace',{}).get('rule_id')==case['expect_rule']
                safe_knowledge=not last.get('knowledge_refs') if case['mode']=='INDEPENDENT' and not case['inputs'][-1].get('help_requested') else True
                outcomes.append({'id':case['id'],'pass':action_ok and rule_ok and safe_knowledge,
                     'expected_action':case['expect_action'],'actual_action':last.get('next_action'),
                     'policy_rule':last.get('decision_trace',{}).get('rule_id'),
                     'knowledge_hidden_for_independent':safe_knowledge})
    search_cases=[
        ('阿波罗尼斯圆','distance-ratio','method-apollonius','hit'),
        ('椭圆切线','ellipse-tangent','method-conic-tangent','hit'),
        ('椭圆切线','ellipse-focus','method-conic-tangent','excluded'),
        ('曲线外点 切线','ellipse-tangent','method-conic-tangent','excluded'),
        ('等比公比1','geometric-sum','method-geometric-sum','hit'),
    ]
    for query,pid,doc,target in search_cases:
        r=retrieve(query,pid,show_excluded=True)
        ids=[x['id'] for x in r['hits' if target=='hit' else 'excluded']]
        outcomes.append({'id':f'retrieval-{pid}-{doc}-{target}','pass':doc in ids,
                         'expected':target,'found':doc in ids})
    success=sum(int(x['pass']) for x in outcomes)
    result={'generated_at':datetime.now(timezone.utc).isoformat(),
            'engine':'DETERMINISTIC_SIMULATION','llm_api_calls':0,
            'cases':len(outcomes),'passed':success,'failed':len(outcomes)-success,
            'action_match_rate':round(success/len(outcomes),4),
            'limitation':'Matches scripted expectations, not a claim of teaching effectiveness or arbitrary math competence.',
            'outcomes':outcomes}
    os.environ.pop('STEM_MENTOR_DB',None)
    return result


if __name__=='__main__':
    result=simulate()
    text=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    target=ROOT/'evaluations'/'results'/'2026-10-15-policy-and-retrieval.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(text,encoding='utf8')
    print(f"Synthetic decisions+retrieval: {result['passed']}/{result['cases']} pass; report: {target}")
    sys.exit(0 if result['failed']==0 else 1)
