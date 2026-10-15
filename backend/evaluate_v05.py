"""Run independent curated retrieval hard cases; deterministic tests, not student outcomes."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from app.retrieval import retrieve
from app.knowledge_quality import validate_knowledge

ROOT=Path(__file__).resolve().parent.parent

def run():
    cases=json.loads((ROOT/'evaluations/retrieval_hard_cases_v05.json').read_text(encoding='utf8'))
    results=[]
    for case in cases:
        response=retrieve(case['query'],case['problem_id'],limit=30,show_excluded=True)
        hits=response['hits']
        excluded=response['excluded']
        rank=next((i+1 for i,h in enumerate(hits) if h['id']==case['target']),None)
        exclusion=next((h for h in excluded if h['id']==case['target']),None)
        expected=case['expect']
        if expected=='hit':
            passed=rank is not None and rank<=5
        elif expected=='excluded':
            passed=rank is None and exclusion is not None and exclusion['applicability']=='CONDITIONS_NOT_ESTABLISHED'
        elif expected=='contra':
            passed=rank is None and exclusion is not None and exclusion['applicability']=='CONTRAINDICATED'
        else: raise ValueError('bad fixture expectation')
        results.append({'id':case['id'],'pass':passed,'expect':expected,
                        'target':case['target'],'rank':rank,
                        'excluded_status':exclusion['applicability'] if exclusion else None,
                        'top3':[h['id'] for h in hits[:3]]})
    pass_count=sum(int(x['pass']) for x in results)
    hit=[x for x in results if x['expect']=='hit']
    negative=[x for x in results if x['expect']!='hit']
    quality=validate_knowledge()
    return {'generated_at':datetime.now(timezone.utc).isoformat(),'engine':'LOCAL_FTS5_AND_CURATED_STRUCTURE_V05',
            'model_api_calls':0,'cases':len(cases),'passed':pass_count,
            'failed':len(cases)-pass_count,'top3_hits':sum(x['rank'] is not None and x['rank']<=3 for x in hit),
            'positive_cases':len(hit),'negative_cases':len(negative),
            'negative_cases_passed':sum(x['pass'] for x in negative),'corpus_quality':quality,
            'limitations':'本评测仅验证人工定义的精确题卡结构、索引匹配与明显反例，不衡量真实学生能力或开放题语义理解。',
            'results':results}

if __name__=='__main__':
    report=run()
    target=ROOT/'evaluations/results/2026-10-15-v05-retrieval.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(f"Hard-negative retrieval: {report['passed']}/{report['cases']}; top3={report['top3_hits']}/{report['positive_cases']}; contract_valid={report['corpus_quality']['valid_contract']}")
    for row in report['results']:
        if not row['pass']: print('FAIL',row)
    sys.exit(0 if report['failed']==0 and report['corpus_quality']['valid_contract'] else 1)
