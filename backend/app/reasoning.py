"""Structured math reasoning as annotated, condition-aware graphs.

This is a teacher-authored heuristic scaffold, NOT a generated complete proof.
Student-visible maps only contain givens, goals and student's own attempts.
"""
from functools import lru_cache
import json
from pathlib import Path
from .storage import thinking_links_list

GRAPH_PATH = Path(__file__).resolve().parents[2] / 'knowledge' / 'reasoning_graphs.json'
STAGES = {'START', 'FORWARD', 'STUCK', 'BACKWARD', 'BRIDGE', 'CALCULATION', 'REFLECTION'}


@lru_cache(maxsize=1)
def graphs():
    source = json.loads(GRAPH_PATH.read_text(encoding='utf8'))
    for problem_id, graph in source.items():
        ids = {n['id'] for n in graph['nodes']}
        if len(ids) != len(graph['nodes']):
            raise ValueError(f'Duplicate nodes for {problem_id}')
        for edge in graph['edges']:
            if edge['source'] not in ids or edge['target'] not in ids:
                raise ValueError(f'Broken graph link for {problem_id}')
            if edge['relation'] == 'BACKWARD_SEARCH_NOT_PROOF' and edge.get('verified'):
                raise ValueError('Backward search cannot be marked as proven')
        for stage, prompt in graph['guidance'].items():
            if stage not in STAGES or not prompt:
                raise ValueError(f'Invalid stage prompt for {problem_id}')
    return source


def graph_for(problem_id):
    return graphs().get(problem_id)


def guide_for(problem_id, stage):
    graph = graph_for(problem_id)
    return graph['guidance'].get(stage) if graph else None


def student_map(session):
    """No unrevealed teacher-only solutions; student statements are not treated as proofs."""
    problem = session['problem']
    graph = graph_for(problem.get('id'))
    nodes = []
    edges = []
    if graph:
        nodes = [{**{k: n[k] for k in ('id','role','statement','verification')},'origin':'CURATED_TASK'}
                 for n in graph['nodes'] if not n['teacher_only']]
    else:
        nodes = [
            {'id':'given','role':'GIVEN','statement':'题目条件请由学生提取','verification':'UNASSESSED','origin':'CUSTOM_TASK'},
            {'id':'goal','role':'GOAL','statement':'问题目标请由学生提取','verification':'UNASSESSED','origin':'CUSTOM_TASK'}]
    prev = None
    for i, turn in enumerate(session['turns']):
        node_id = f'student-step-{i+1}'
        stage = turn['stage'] if turn['stage'] in STAGES else 'FORWARD'
        nodes.append({'id':node_id,'role':stage,'statement':turn['student_text'][:300],
                      'verification':'STUDENT_CLAIM_UNVERIFIED','origin':'STUDENT',
                      'teacher_action':turn['action'],'timestamp':turn['created_at']})
        if prev:
            edges.append({'source':prev,'target':node_id,'relation':'NEXT_ATTEMPT_NOT_IMPLICATION','verified':False})
        prev = node_id
    public_ids={n['id'] for n in nodes}
    for link in thinking_links_list(session['id']):
        if link['source'] in public_ids and link['target'] in public_ids:
            edges.append({'source':link['source'],'target':link['target'],
                'relation':'STUDENT_HYPOTHESIS_UNVERIFIED','verified':False,
                'origin':'STUDENT','label':link['label'][:100]})
    return {'problem_id':problem.get('id'),'nodes':nodes,'edges':edges,'student_steps':len(session['turns']),
            'contains_teacher_solution':False,'note':'思维历程图：虚线是学习过程先后，绿色连线只是学生的待验证猜想，并非数学证明。'}
