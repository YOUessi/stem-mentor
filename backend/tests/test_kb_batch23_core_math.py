from scripts.kb_frozen_batch24 import frozen_batch24_lessons
"""Batch23 independent exact checks, draft-only K00 audit and anti-spoiler controls."""
import copy
import importlib.util
import json
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from hashlib import sha256

import pytest
import sympy as sp
from pydantic import ValidationError
from app.deep_knowledge import DeepLesson, curriculum, lessons, coverage_report
from app.deep_retrieval import student_evidence_lookup, editor_draft_search, EditorOnlyError
from app.kb_batch23_guarded_math import SUPPORTED, evaluate

ROOT=Path(__file__).resolve().parents[2]
SOURCE=json.loads((ROOT/'curriculum/highschool_math/author_draft_batch23.json').read_text(encoding='utf8'))
AUDIT=json.loads((ROOT/'docs/evaluation/KB_BATCH23_INTEGRITY_AND_SCOPE.json').read_text(encoding='utf8'))
CORPUS=json.loads((ROOT/'knowledge/deep/v1/core_elective_batch23.json').read_text(encoding='utf8'))
def loader(name):
    spec=importlib.util.spec_from_file_location('batch23_'+name,ROOT/'scripts'/name)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod
author=loader('author_kb_batch23.py')
build=loader('build_kb_batch23_integrity.py')

def test_materialization_exact_and_coverage_is_not_official():
    assert len(SOURCE)==20 and len(CORPUS)==20
    assert author.render()[0][1]==(ROOT/'curriculum/highschool_math/author_draft_batch23.json').read_text()
    rendered,report=build.build()
    assert json.loads(rendered)==CORPUS==[x['lesson'] for x in SOURCE]
    assert json.loads(report)==AUDIT
    assert len(frozen_batch24_lessons())==287 and len(curriculum())==178
    assert coverage_report()['deep_lesson_documents']==len(lessons())
    assert AUDIT['summary']['official_atomic_denominator'] is None
    assert AUDIT['summary']['official_coverage_rate'] is None
    assert AUDIT['summary']['editorial_gap_tickets_still_open']==28
    assert AUDIT['summary']['draft_nearby_gap_candidates']==28
    assert AUDIT['source_review_tasks_preserved']==427
    assert AUDIT['teacher_approved']==0
    assert all(r['verified_official_atomic_denominator'] is None for r in AUDIT['official_tracks'])

def test_20_distinct_authored_knowledge_types_and_trusted_previews():
    assert {x['tag'] for x in SOURCE if x['gap'] is not None}=={'C18','C19','D23','D24','E26'}
    assert {x['gap'] for x in SOURCE if x['gap'] is not None}=={18,19,23,24,26}
    assert len({x['lesson']['curriculum_ids'][0] for x in SOURCE if x['gap'] is None})==15
    assert sum(len(x['lesson']['worked_examples']) for x in SOURCE)==40
    for row in SOURCE:
        doc=DeepLesson.model_validate(row['lesson'])
        assert doc.review.status=='REVIEW_PENDING'
        assert doc.teacher_solution_visibility=='TEACHER_ONLY'
        assert not doc.review.reviewer_id
        assert len(doc.hint_ladder)==3 and len(doc.worked_examples)==2
        assert all(len(e.steps)==2 and e.steps[0]!=e.steps[1] for e in doc.worked_examples)
        assert all('。。' not in ''.join(e.steps) for e in doc.worked_examples)
    assert all(x['ticket_status']=='OPEN_EDITORIAL_CANDIDATE_NOT_PROVEN_MISSING'
               and not x['verified_official_clause_equivalence']
               and not x['student_publishable'] for x in AUDIT['editorial_ticket_review'])

def test_current_proof_queue_has_no_accidental_certificate():
    previous=json.loads((ROOT/'docs/evaluation/KB_BATCH22_UNVERIFIED_PROOF_QUEUE.json').read_text())
    assert previous['summary']['total_unverified_proof_steps']==497
    actual=sum(len(x['lesson']['proof_steps']) for x in SOURCE)
    assert actual==AUDIT['new_proof_unverified']
    assert AUDIT['current_unverified_proof_steps']==497+actual
    assert len(AUDIT['new_proof_review_queue'])==actual
    claims={}
    for x in SOURCE:
        for i,step in enumerate(x['lesson']['proof_steps'],1):
            claims[x['lesson']['id']+'#'+str(i)]=sha256(
                (step['claim']+'\x00'+step['reason']).encode()).hexdigest()
    assert set(claims)=={x['id'] for x in AUDIT['new_proof_review_queue']}
    for row in AUDIT['new_proof_review_queue']:
        assert row['content_sha256']==claims[row['id']]
        assert row['status']=='NOT_FORMALLY_VERIFIED'
        assert not row['whole_theorem_certified'] and not row['student_publishable']
    assert AUDIT['certified_whole_proofs']==0

@pytest.mark.parametrize('field,value',[
    ('teacher_solution_visibility','STUDENT_VISIBLE'),
    ('review',{'status':'APPROVED','reviewer_id':'spoof','reviewed_at':'2026-11-08','review_record':'spoof'}),
    ('worked_examples',[]),('hint_ladder',[]),
])
def test_forged_approval_leak_and_missing_problems_rejected(field,value):
    bad=copy.deepcopy(SOURCE[0]['lesson']);bad[field]=value
    with pytest.raises(ValidationError):
        DeepLesson.model_validate(bad)

@pytest.mark.parametrize('tag', [x['tag'] for x in SOURCE])
def test_all_20_drafts_not_student_released(tag):
    row=next(x for x in SOURCE if x['tag']==tag)
    assert row['lesson']['review']['status']=='REVIEW_PENDING'
    assert row['lesson']['teacher_solution_visibility']=='TEACHER_ONLY'
    assert student_evidence_lookup(row['lesson']['title'])['status']=='NO_APPROVED_EVIDENCE'

def test_editor_preview_not_public_api():
    with pytest.raises(EditorOnlyError):
        editor_draft_search('SSA 概率 导数')
    assert student_evidence_lookup('概率 欧拉 净空')['status']=='NO_APPROVED_EVIDENCE'

@pytest.mark.parametrize('op',SUPPORTED)
def test_no_oracle_claims_teacher_approval_or_freetext_proof(op):
    for value in ({},None,{'value':'__import__("os").system("id")'}):
        r=evaluate(op,value)
        assert r['status']=='CONDITIONS_NOT_ESTABLISHED'
        assert r['teacher_approved'] is False
        assert r['student_step_verified'] is False
        assert r['complete_theorem_certified'] is False
assert evaluate('student_freetext_proof',{'claim':'I insist it is true'})['status']=='UNSUPPORTED'

@pytest.mark.parametrize('x',range(-15,16))
def test_square_and_sqrt_original_agreement(x):
    r=evaluate('squared_equation_candidate',{'x':x})
    if x<-2: assert r['status']=='CONDITIONS_NOT_ESTABLISHED'
    else:
        assert r['witness']['squared_equation_holds']==(x in (-1,2))
        assert r['witness']['original_equation_holds']==(x==2)

@pytest.mark.parametrize('n',range(1,110))
def test_telescoping_exact_sum(n):
    r=evaluate('telescoping_finite_sum',{'n':n})
    assert r['status']=='VERIFIED_FINITE_INSTANCE'
    assert Q(r['witness']['sum'])==Q(n,n+1)
assert evaluate('telescoping_finite_sum',{'n':0})['status']=='CONDITIONS_NOT_ESTABLISHED'

@pytest.mark.parametrize('w,l,m',product((1,2,7),(1,3,11),(0,'1/2',1,3)))
def test_rectangular_clearance_area_exact(w,l,m):
    r=evaluate('court_clearance_area',{'width':w,'length':l,'margin':m})
    assert r['status']=='VERIFIED_FINITE_INSTANCE'
    assert Q(r['witness']['area'])==(w+2*Q(m))*(l+2*Q(m))
    assert Q(r['witness']['added_clearance_area'])==2*Q(m)*(w+l)+4*Q(m)**2
assert evaluate('court_clearance_area',{'width':10,'length':8,'margin':-1})['status']=='CONDITIONS_NOT_ESTABLISHED'

@pytest.mark.parametrize('n,p',product(range(1,11),(0,'1/4','1/2','3/4',1)))
def test_binomial_distribution_normalization_and_moments(n,p):
    probs=[]
    for k in range(n+1):
        r=evaluate('binomial_point_mass',{'n':n,'k':k,'p':p})
        assert r['status']=='VERIFIED_FINITE_INSTANCE'
        probs.append(Q(r['witness']['probability']))
        assert Q(r['witness']['expectation'])==n*Q(p)
    assert sum(probs)==1
    assert sum(k*v for k,v in enumerate(probs))==n*Q(p)
    assert sum((Q(k)-n*Q(p))**2*v for k,v in enumerate(probs))==n*Q(p)*(1-Q(p))
assert evaluate('binomial_point_mass',{'n':3,'k':2,'p':'7/5'})['status']=='CONDITIONS_NOT_ESTABLISHED'

@pytest.mark.parametrize('m,b',product(range(-8,9),range(-12,13)))
def test_parabola_intersection_discriminant_as_computed(m,b):
    r=evaluate('parabola_line_discriminant',{'m':m,'b':b})
    d=m*m+4*b
    assert Q(r['witness']['discriminant'])==d
    assert r['witness']['distinct_real_intersections']==(2 if d>0 else 1 if d==0 else 0)
    x=sp.symbols('x',real=True)
    assert sp.discriminant(x*x-m*x-b,x)==d

@pytest.mark.parametrize('a,b,c,d',product((-2,0,3),(-2,0,1),(-3,0,2),(-2,0,3)))
def test_complex_quotient_exact_rationals(a,b,c,d):
    r=evaluate('complex_divide',{'a':a,'b':b,'c':c,'d':d})
    if c==d==0:
        assert r['status']=='CONDITIONS_NOT_ESTABLISHED'
    else:
        assert r['status']=='VERIFIED_FINITE_INSTANCE'
        real=Q(r['witness']['real']);imag=Q(r['witness']['imag'])
        assert sp.expand((c+sp.I*d)*(real+sp.I*imag)-(a+sp.I*b))==0

@pytest.mark.parametrize('pa,pb,pab',product((Q(0),Q(1,2),Q(1)),repeat=3))
def test_probability_frechet_bounds_with_conditional_denominators(pa,pb,pab):
    r=evaluate('two_event_union',{'pa':str(pa),'pb':str(pb),'pab':str(pab)})
    okay=max(Q(0),pa+pb-1)<=pab<=min(pa,pb)
    assert (r['status']=='VERIFIED_FINITE_INSTANCE')==okay
    if okay:
        assert Q(r['witness']['union_probability'])==pa+pb-pab

@pytest.mark.parametrize('x,y',product(range(-7,8),repeat=2))
def test_quadratic_monotonic_never_claims_across_vertex(x,y):
    r=evaluate('quadratic_monotonic_pair',{'x':x,'y':y})
    domain=(x<y and (x>=0 or y<=0))
    assert (r['status']=='VERIFIED_FINITE_INSTANCE')==domain
    if domain:
        assert r['witness']['direction']==('strict_increase' if x>=0 else 'strict_decrease')

def test_symbolic_derivative_monotonic_and_piecewise_counterexample():
    x=sp.symbols('x',real=True)
    assert sp.diff(x**3,x).subs(x,0)==0
    assert sp.diff(x*x,x)==2*x
    assert sp.limit(sp.Abs(x)/x,x,0,dir='-')==-1
    assert sp.limit(sp.Abs(x)/x,x,0,dir='+')==1

def test_sine_ambiguity_and_euler_counts_are_bounded_examples_not_general_proofs():
    assert sp.simplify(sp.sin(sp.asin(sp.Rational(4,5)))-sp.Rational(4,5))==0
    assert sp.simplify(sp.sin(sp.pi-sp.asin(sp.Rational(4,5)))-sp.Rational(4,5))==0
    assert 4-6+4==2 and 8-12+6==2 and 1-2+1==0
    assert AUDIT['summary']['full_official_atom_inventory'] is False

@pytest.mark.parametrize('tag,expected',[
    ('C18',('75%','75%')),('C19',('1/4','每人2件')),('D23',('1','-1')),
    ('D24',('264','63')),('E26',('2','0')),('CORE003',('是','否')),
    ('CORE010',('x=2','不能')),('CORE013',('f(1)<f(3)','f(−3)>f(−1)')),
    ('CORE017',('3','1')),('CORE027',('1','−1')),('CORE038',('4/5','无')),
    ('CORE042',('(1+3i)/2','−i')),('CORE044',('是','不能')),
    ('CORE053',('3/4','2/3')),('CORE065',('3/4','1/2')),
    ('CORE068',('是','0')),('CORE090',('一个切点(1,1)','0')),
    ('CORE096',('1/2','1/8')),('CORE099',('3/8','1')),('CORE102',('r=1','r=−1')),
])
def test_all_40_expected_teacher_side_results_and_two_steps(tag,expected):
    lesson=next(x['lesson'] for x in SOURCE if x['tag']==tag)
    assert tuple(ex['answer'] for ex in lesson['worked_examples'])==expected
    assert all(ex['steps'][0]!=ex['steps'][1] for ex in lesson['worked_examples'])
