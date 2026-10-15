"""Check local authored material schema and provenance; never claim teacher review."""
from collections import Counter
from .catalog import PROBLEMS, MICRO_POINTS
from .reasoning import graphs
from .retrieval import corpus, _terms

NEEDED={'id','kind','title','subject','aliases','methods','structures','requires','prerequisites','content','boundary','hint','source','version'}

def validate_knowledge():
    cards=list(corpus())
    issues=[]
    topics=Counter()
    statuses=Counter()
    ids=[c['id'] for c in cards]
    if len(ids)!=len(set(ids)): issues.append('duplicate id')
    for c in cards:
        missing=NEEDED-set(c)
        if missing:
            issues.append(str(c.get('id'))+': missing '+str(sorted(missing)))
            continue
        topics[c['subject']]+=1
        source=c['source']
        statuses[source.get('expert_review','MISSING')]+=1
        if source.get('permission')!='PROJECT_AUTHORED': issues.append(c['id']+': unauthorized')
        if not set(c['requires']).issubset(set(c['structures'])): issues.append(c['id']+': invalid requires')
        if len(c['content'])<=45 or not c['boundary'] or not c['hint']: issues.append(c['id']+': incomplete body')
        if not _terms(c['title']): issues.append(c['id']+': no tokens')
    gs=graphs()
    for pid,p in PROBLEMS.items():
        if pid not in gs: issues.append(pid+': missing graph')
        if p.get('micro_point_id') not in MICRO_POINTS: issues.append(pid+': missing micro-point')
        if not p.get('analysis') or not p.get('guide'): issues.append(pid+': missing prompts')
    return {'valid_contract':not issues,'issues':issues,'corpus_documents':len(cards),
            'curated_problems':len(PROBLEMS),'reasoning_graphs':len(gs),
            'exam_micro_points':len(MICRO_POINTS),'subject_counts':dict(topics),
            'expert_review_status':dict(statuses),'teacher_approved_documents':statuses.get('APPROVED',0),
            'scope':'AUTOMATIC_SCHEMA_AND_SOURCE_CHECK_ONLY',
            'note':'不等于教师审核通过或对任意数学题有自动理解能力'}
