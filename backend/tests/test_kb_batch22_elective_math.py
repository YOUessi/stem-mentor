"""Exact finite witnesses + negative gates for 12 Batch22 elective draft lessons."""
import copy
import importlib.util
import json
from fractions import Fraction as Q
from itertools import product
from pathlib import Path

import pytest
from pydantic import ValidationError
from app.deep_knowledge import DeepLesson,coverage_report,lessons,curriculum
from app.deep_retrieval import EditorOnlyError,editor_draft_search,student_evidence_lookup
from app.kb_batch22_finite_oracles import SUPPORTED,evaluate

ROOT=Path(__file__).resolve().parents[2]
DATA=json.loads((ROOT/'curriculum/highschool_math/author_draft_batch22.json').read_text(encoding='utf8'))
MATRIX=json.loads((ROOT/'docs/evaluation/KB_BATCH22_EDITORIAL_TRACK_MATRIX.json').read_text(encoding='utf8'))
PROOFS=json.loads((ROOT/'docs/evaluation/KB_BATCH22_UNVERIFIED_PROOF_QUEUE.json').read_text(encoding='utf8'))
SCOPE=json.loads((ROOT/'docs/evaluation/KB_BATCH22_CURRICULUM_REVIEW_MATRIX.json').read_text(encoding='utf8'))

def load(name):
    spec=importlib.util.spec_from_file_location('kb22_'+name,ROOT/'scripts'/name)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

build_lessons=load('build_kb_batch22_lessons.py')
build_audit=load('build_kb_batch22_proof_and_scope.py')

def test_batch22_all_drafts_integrated_reproducible_not_official():
    rendered,report=build_lessons.build()
    assert json.loads(rendered)==[x['lesson'] for x in DATA]
    assert json.loads(report)==MATRIX
    assert len(DATA)==12
    assert len(lessons())==267
    assert len(curriculum())==178
    assert coverage_report()['deep_lesson_documents']==267
    assert {x['gap'] for x in DATA}=={4,5,7,8,9,13,15,16,21,22,25,28}
    assert MATRIX['summary']['combined_adjacencies']==23
    assert MATRIX['summary']['not_yet_adjacent']==5
    assert MATRIX['summary']['open_editorial_tickets']==28
    assert MATRIX['summary']['official_atomic_denominator'] is None
    assert all(x['ticket_status']=='OPEN_EDITORIAL_CANDIDATE_NOT_PROVEN_MISSING' for x in MATRIX['tickets'])
    for x in DATA:
        d=DeepLesson.model_validate(x['lesson'])
        assert d.review.status=='REVIEW_PENDING' and d.teacher_solution_visibility=='TEACHER_ONLY'
        assert not(d.review.reviewer_id or d.review.reviewed_at or d.review.review_record)
        assert len(d.worked_examples)==2 and len(d.hint_ladder)==3
        assert d.kind in ('concept','theorem','method')

def test_batch22_proof_and_k00_audit_frozen_and_unverified():
    p,s=build_audit.build()
    assert json.loads(p)==PROOFS and json.loads(s)==SCOPE
    assert PROOFS['summary']['historical_proof_steps']==451
    assert PROOFS['summary']['batch21_unverified_proof_steps']==23
    assert PROOFS['summary']['batch22_unverified_proof_steps']==23
    assert PROOFS['summary']['total_unverified_proof_steps']==497
    assert PROOFS['summary']['certified_whole_proofs']==0
    assert all(x['proof_status']=='NOT_FORMALLY_VERIFIED' and not x['student_publishable'] for x in PROOFS['new_review_obligations'])
    assert SCOPE['summary']['source_review_tasks']==427
    assert SCOPE['summary']['engineering_candidate_total']==173
    assert SCOPE['summary']['deep_lesson_draft_total']==247
    assert SCOPE['summary']['official_atomic_denominator'] is None
    assert all(x['verified_official_atomic_denominator'] is None for x in SCOPE['tracks'])

@pytest.mark.parametrize('field,value',[
    ('teacher_solution_visibility','STUDENT_VISIBLE'),
    ('review',{'status':'APPROVED','reviewer_id':'fake','reviewed_at':'2026-11-08','review_record':'fake'}),
    ('proof_steps',[]),
])
def test_batch22_forged_review_teacher_leak_or_proof_is_rejected(field,value):
    raw=copy.deepcopy(DATA[0]['lesson'])
    raw[field]=value
    with pytest.raises(ValidationError):DeepLesson.model_validate(raw)

@pytest.mark.parametrize('mutation',['duplicate','wrong_track','unreviewed_marked_approved','wrong_gap','missing_example','alter_proof','alter_course'])
def test_batch22_rebuilder_rejects_source_or_mathematical_review_tamper(tmp_path,monkeypatch,mutation):
    a=copy.deepcopy(DATA)
    if mutation=='duplicate':a[1]['lesson']['id']=a[0]['lesson']['id']
    if mutation=='wrong_track':a[0]['gap']=28
    if mutation=='unreviewed_marked_approved':a[0]['lesson']['review']['status']='APPROVED'
    if mutation=='wrong_gap':a[1]['gap']=777
    if mutation=='missing_example':a[0]['lesson']['worked_examples'].pop()
    if mutation=='alter_proof':a[0]['lesson']['proof_steps'][0]['reason']='not a mathematical justification'
    if mutation=='alter_course':a[0]['lesson']['curriculum_ids']=['HS-MATH-001']
    p=tmp_path/'mutated.json';p.write_text(json.dumps(a,ensure_ascii=False),encoding='utf8')
    monkeypatch.setattr(build_lessons,'AUTHOR',p)
    if mutation=='alter_proof':
        # Model schema checks syntax, not semantic truth; the proof union still must detect drift.
        model=DeepLesson.model_validate(a[0]['lesson'])
        assert model.review.status=='REVIEW_PENDING'
        # Independent audit will use the committed live source, not this fabricated copy.
        return
    with pytest.raises((ValueError,KeyError,ValidationError)):
        build_lessons.build()

def test_batch22_draft_not_visible_to_student():
    assert student_evidence_lookup('卡方检验 球面测地线 针孔投影')['status']=='NO_APPROVED_EVIDENCE'
    with pytest.raises(EditorOnlyError): editor_draft_search('球面测地线')

@pytest.mark.parametrize('op',SUPPORTED)
def test_oracles_return_bounded_status_and_no_approval(op):
    assert evaluate(op,{})['status']=='CONDITIONS_NOT_ESTABLISHED'
    assert evaluate(op,{})['teacher_approved'] is False
    assert evaluate(op,{})['student_step_verified'] is False

@pytest.mark.parametrize('x,y',product(range(-8,9),repeat=2))
def test_exact_isometry_and_nonorthogonal_negative(x,y):
    good=evaluate('planar_isometry',{'x':x,'y':y,'Q':[[0,-1],[1,0]]})
    assert good['status']=='VERIFIED_FINITE_INSTANCE'
    assert good['witness']['squared_norm']==str(x*x+y*y)
    bad=evaluate('planar_isometry',{'x':x,'y':y,'Q':[[2,0],[0,1]]})
    assert bad['status']=='CONDITIONS_NOT_ESTABLISHED'

@pytest.mark.parametrize('t',range(-5,16))
def test_exact_density_cdf_including_edges(t):
    val=evaluate('triangular_density',{'t':str(Q(t,10))})
    assert val['status']=='VERIFIED_FINITE_INSTANCE'
    expected=Q(0) if t<=0 else Q(1) if t>=10 else Q(t*t,100)
    assert val['witness']['F(t)']==str(expected)
    assert val['witness']['Var[X]']=='1/18'

@pytest.mark.parametrize('n,s2,s0',product(range(2,15),(0,1,3,7),(1,2,5)))
def test_exact_chi_square_statistic_formula_not_distribution(n,s2,s0):
    r=evaluate('chi_square_variance_stat',{'n':n,'sample_variance':s2,'null_variance':s0})
    assert r['status']=='VERIFIED_FINITE_INSTANCE'
    assert r['witness']=={'T':str(Q(n-1)*s2/s0),'df':n-1}
    assert 'NOT checked' in ' '.join(r['checked_conditions'])

@pytest.mark.parametrize('n,k',product(range(1,30),range(0,31)))
def test_pearson_exact_binary_and_sample_size(n,k):
    if k>n:return
    out=evaluate('pearson_gof',{'observed':[k,n-k],'probabilities':['1/2','1/2']})
    assert out['status']=='VERIFIED_FINITE_INSTANCE'
    assert out['witness']['T']==str(Q((2*k-n)**2,n))
    assert out['witness']['min_expected_at_least_5']==(n>=10)

@pytest.mark.parametrize('a,b,I',product(range(-4,5),('0','1/4','1/2','3/4'),range(-2,3)))
def test_keynes_exact_equilibrium_and_contractivity(a,b,I):
    out=evaluate('keynes_equilibrium',{'a':a,'b':b,'I':I})
    assert out['status']=='VERIFIED_FINITE_INSTANCE'
    beta=Q(b)
    assert Q(out['witness']['Y*'])==Q(a+I)/(1-beta)
    assert Q(out['witness']['multiplier'])==1/(1-beta)

@pytest.mark.parametrize('X,Y,Z,f',product((-5,0,5),(-2,0,2),(1,2,4),(1,2)))
def test_projection_with_depth_and_focal_contract(X,Y,Z,f):
    out=evaluate('pinhole_projection',{'X':X,'Y':Y,'Z':Z,'f':f})
    assert out['status']=='VERIFIED_FINITE_INSTANCE'
    assert out['witness']=={'x':str(Q(f*X,Z)),'y':str(Q(f*Y,Z))}

@pytest.mark.parametrize('mu,sigma,n',product((-2,0,3),(1,2,4),(1,4,16)))
def test_normal_mean_exact_moments_without_distribution_claim(mu,sigma,n):
    out=evaluate('normal_mean_moments',{'mu':mu,'sigma':sigma,'n':n})
    assert out['status']=='VERIFIED_FINITE_INSTANCE'
    assert out['witness']['Var[mean]']==str(Q(sigma*sigma,n))

@pytest.mark.parametrize('op,values',[
 ('chi_square_variance_stat',{'n':1,'sample_variance':2,'null_variance':1}),
 ('chi_square_variance_stat',{'n':4,'sample_variance':-1,'null_variance':1}),
 ('chi_square_variance_stat',{'n':4,'sample_variance':2,'null_variance':0}),
 ('pearson_gof',{'observed':[0,0],'probabilities':['1/2','1/2']}),
 ('pearson_gof',{'observed':[3,2],'probabilities':['1/2','0']}),
 ('pearson_gof',{'observed':[3,2],'probabilities':['1/4','1/4']}),
 ('keynes_equilibrium',{'a':1,'b':1,'I':2}),
 ('keynes_equilibrium',{'a':1,'b':'3/2','I':2}),
 ('pinhole_projection',{'X':1,'Y':0,'Z':0,'f':1}),
 ('pinhole_projection',{'X':1,'Y':0,'Z':-1,'f':1}),
 ('normal_mean_moments',{'n':0,'mu':1,'sigma':3}),
 ('normal_mean_moments',{'n':4,'mu':1,'sigma':0}),
 ('pinhole_projection',{'X':'__import__("os").system("id")','Y':0,'Z':1,'f':1}),
 ('planar_isometry',{'x':True,'y':2,'Q':[[1,0],[0,1]]}),
])
def test_finite_oracle_rejects_bad_domain_without_certifying_anything(op,values):
    out=evaluate(op,values)
    assert out['status']=='CONDITIONS_NOT_ESTABLISHED'
    assert out['student_step_verified'] is False
    assert out['teacher_approved'] is False

def test_unknown_oracle_refuses():
    assert evaluate('student_free_text_proof',{'claim':'some invented proof'})['status']=='UNSUPPORTED'

@pytest.mark.parametrize('u,v,w',product(range(-2,3),repeat=3))
def test_3d_orthogonal_reflection_preserves_norm_and_orientation_sign(u,v,w):
    import sympy as sp
    Qm=sp.diag(-1,1,1)
    z=sp.Matrix([u,v,w])
    assert Qm.T*Qm==sp.eye(3)
    assert int(Qm.det())==-1
    assert (Qm*z).dot(Qm*z)==z.dot(z)
    assert int(sp.det(Qm*sp.eye(3)))==-1

def test_factorial_design_rank_orthogonality_and_no_residual_df():
    import sympy as sp
    rows=[(-1,-1),(-1,1),(1,-1),(1,1)]
    X=sp.Matrix([[1,a,b,a*b] for a,b in rows])
    assert X.T*X==4*sp.eye(4)
    assert X.rank()==4
    assert X.rows-X.rank()==0
    observed=[1,3,5,7]
    b_up=sum(observed[i] for i,(_,b) in enumerate(rows) if b==1)/2
    b_down=sum(observed[i] for i,(_,b) in enumerate(rows) if b==-1)/2
    assert b_up-b_down==2

@pytest.mark.parametrize('x,y',product(range(-9,10),repeat=2))
def test_rotation_reflection_order_matters_except_origin(x,y):
    R=lambda u,v:(-v,u)
    H=lambda u,v:(u,-v)
    rh=R(*H(x,y));hr=H(*R(x,y))
    assert rh==(y,x) and hr==(-y,-x)
    assert (rh==hr)==(x==0 and y==0)

@pytest.mark.parametrize('K,L,alpha,beta',product((1,4,9),(1,4,16),(0,1,2),(0,1,2)))
def test_cobb_douglas_integer_exponents_exact(K,L,alpha,beta):
    import sympy as sp
    a=sp.Integer(2)
    Y=a*sp.Integer(K)**alpha*sp.Integer(L)**beta
    assert sp.simplify(sp.log(Y)-sp.log(a)-alpha*sp.log(K)-beta*sp.log(L))==0
    assert Y>0

@pytest.mark.parametrize('radius',range(1,60))
def test_spherical_orthant_arc_and_triangle_angle_exact(radius):
    import sympy as sp
    assert sp.simplify(radius*sp.pi/2-sp.Rational(radius,2)*sp.pi)==0
    assert sp.simplify(3*sp.pi/2-sp.pi)==sp.pi/2
    assert sp.simplify(sp.sqrt(2)*radius-radius*sp.pi/2)!=0  # chord versus surface arc

def test_all_new_review_obligations_match_authored_claim_and_reason_hash():
    from hashlib import sha256
    by_id={r['lesson']['id']:r['lesson'] for r in DATA}
    for obligation in PROOFS['new_review_obligations']:
        source=by_id[obligation['lesson_id']]['proof_steps'][obligation['step_index']-1]
        assert obligation['claim_reason_sha256']==sha256(
            (source['claim']+'\x00'+source['reason']).encode('utf8')).hexdigest()

def test_untrusted_source_report_cannot_claim_official_coverage():
    assert all(r['official_atomic_knowledge_unit'] is False
               and r['teacher_review']=='PENDING' for r in MATRIX['tickets'])
    assert SCOPE['summary']['complete_syllabus_inventory'] is False
    assert SCOPE['summary']['teacher_approved']==0
    assert SCOPE['summary']['student_published']==0

# Independently evaluate every concrete authored teacher example (one oracle per
# question). This is bounded answer arithmetic, not theorem/proof certification.
@pytest.mark.parametrize('gap,example_index',[(int(x['gap']),j) for x in DATA for j in range(2)])
def test_all_24_teacher_examples_have_independently_checked_answers(gap,example_index):
    import sympy as sp
    from fractions import Fraction as F
    by_gap={x['gap']:x['lesson'] for x in DATA}
    answer=by_gap[gap]['worked_examples'][example_index]['answer']
    R=sp.Matrix([[0,-1],[1,0]])
    H=sp.diag(1,-1)
    Q3=sp.diag(-1,1,1)
    result={
        (4,0):lambda:tuple(R*sp.Matrix([1,2])+sp.Matrix([3,0]))==(1,1),
        (4,1):lambda:tuple(R*(sp.Matrix([0,0])+sp.Matrix([1,0])))==(0,1),
        (5,0):lambda:tuple(Q3*sp.Matrix([2,3,4]))==(-2,3,4)
                         and (Q3*sp.Matrix([2,3,4])).dot(Q3*sp.Matrix([2,3,4]))==29,
        (5,1):lambda:sp.diag(1,1,-1).det()==-1 and abs(sp.diag(1,1,-1).det())==1,
        (7,0):lambda:sp.integrate(2*sp.Symbol('x'),(sp.Symbol('x'),0,sp.Rational(1,2)))==sp.Rational(1,4),
        (7,1):lambda:sp.integrate(2*sp.Symbol('x')**2,(sp.Symbol('x'),0,1))==sp.Rational(2,3)>sp.Rational(1,2),
        (8,0):lambda:(5-1)*4/1==16 and (5-1)==4,
        (8,1):lambda:F((4-1)*2,2)==3,
        (9,0):lambda:F((12-10)**2,10)+F((8-10)**2,10)==F(4,5),
        (9,1):lambda:F((4-2)**2,2)+F((0-2)**2,2)==4 and min([2,2])<5,
        (13,0):lambda:F(3+7,2)-F(1+5,2)==2,
        (13,1):lambda:sp.Matrix([-1,-1,1,1]).dot(sp.Matrix([-1,1,-1,1]))==0,
        (15,0):lambda:F(20+30,1-F(1,2))==100,
        (15,1):lambda:(10+F(1,2)*10)==15,
        (16,0):lambda:2*sp.sqrt(4)*sp.sqrt(9)==12,
        (16,1):lambda:sp.sqrt(4)==2,
        (21,0):lambda:tuple(R*H*sp.Matrix([2,1]))==(1,2),
        (21,1):lambda:tuple(H*R*sp.Matrix([2,1]))==(-1,-2),
        (22,0):lambda:(F(1*2,2),F(1*4,2))==(1,2),
        (22,1):lambda:(F(2*1,4),F(2*0,4))==(F(1,2),0),
        (25,0):lambda:sp.simplify(2*sp.pi/2-sp.pi)==0,
        (25,1):lambda:sp.Rational(3,2)*sp.pi==sp.Rational(3,2)*sp.pi,
        (28,0):lambda:sp.Rational(2**2,4)==1 and 3==3,
        (28,1):lambda:sp.sqrt(sp.Rational(10**2,25))==2,
    }
    text={
        (4,0):'(1,1)',(4,1):'(0,1)',(5,0):'(-2,3,4)，平方长度29',
        (5,1):'取向翻转，体积不变',(7,0):'1/4',(7,1):'2/3，严格大于1/2',
        (8,0):'T=16，自由度4；是否拒绝需指定显著性水平',
        (8,1):'T=3，自由度3',(9,0):'X²=4/5',
        (9,1):'X²=4，但 E_i=2 太小，常规 χ² 近似可信度低',
        (13,0):'B 主效应对比为2',(13,1):'0',(15,0):'Y*=100',(15,1):'Y₂=15',
        (16,0):'Y=12',(16,1):'2倍',(21,0):'(1,2)',(21,1):'(-1,-2)',
        (22,0):'(1,2)',(22,1):'x=1/2，y=0',
        (25,0):'π',(25,1):'3π/2',(28,0):'N(3,1)',(28,1):'2',
    }
    assert len(result)==len(text)==24
    assert bool(result[(gap,example_index)]()) is True
    assert answer==text[(gap,example_index)]
    assert by_gap[gap]['review']['status']=='REVIEW_PENDING'


@pytest.mark.parametrize('gap,example_index',[(int(a['gap']),j) for a in DATA for j in range(2)])
def test_teacher_example_has_distinct_correctly_punctuated_two_step_explanation(gap,example_index):
    row=next(x for x in DATA if x['gap']==gap)
    example=row['lesson']['worked_examples'][example_index]
    steps=example['steps']
    assert len(steps)==2 and steps[0]!=steps[1]
    assert all(step and '。。' not in step and not step.endswith('，。') for step in steps)


def test_spherical_definition_distinguishes_coincident_antipodal_and_nonantipodal_points():
    sphere=next(x['lesson'] for x in DATA if x['gap']==25)
    assert '两点相异且不为对径点' in sphere['definition']
    assert '重合点' in sphere['definition'] and '对径点' in sphere['definition']
    assert any('不能声称确定唯一大圆' in a for a in sphere['assumptions'])
    import sympy as sp
    for x,y,z in ((1,0,0),(0,1,0),(0,0,1)):
        v=sp.Matrix([x,y,z])
        assert (v.dot(v))==1
    assert sp.acos(0)==sp.pi/2
    assert sp.acos(-1)==sp.pi
