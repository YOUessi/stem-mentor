"""Teacher-side condition-aware certificates for a few *curated* tasks.

No arbitrary student text gets eval'ed, parsed or granted 'proof' status.
These independent symbolic checks do not constitute automatic proof of
arbitrary conjectures or evaluation of the student's actual argument.
"""
from functools import lru_cache
from sympy import symbols, simplify, Rational, diff
from .catalog import PROBLEMS

x, y = symbols('x y', real=True)

def _certificate(problem_id, assertion, checks, conditions, explanation):
    return {'problem_id':problem_id,'assertion_id':assertion,
            'checks':checks,'all_symbolic_checks_pass':all(c['passed'] for c in checks),
            'required_conditions':conditions,'explanation':explanation,
            'student_work_verified':False,'teacher_only':True,
            'engine':'CURATED_GUARDED_SYMBOLIC_CERTIFICATE'}

def _check(name, proposition):
    return {'rule':name,'passed':bool(proposition)}

@lru_cache(maxsize=1)
def certificates():
    outcome={}
    # A forward algebraic equivalence under x+y=1, x>0,y>0.
    reduced = simplify((1/x+1/y-1/(x*y)).subs(y,1-x))
    product_identity = simplify((x+y)**2-4*x*y-(x-y)**2)
    outcome['inequality-bridge']=_certificate('inequality-bridge','BOUND_PRODUCT_TO_GOAL',
        [_check('substitution_with_nonzero_denominators',reduced==0),
         _check('square_nonnegative_identity',product_identity==0)],
        ['x+y=1','x>0','y>0','(x-y)^2>=0','positive_reciprocal_is_order_reversing'],
        '代数部分可由符号恒等式复核；从平方非负到乘积上界仍依赖明确写出的实数条件。')
    # Equality after squaring is sufficient only because both distances are nonnegative.
    distance = x*x+y*y-4*((x-6)**2+y*y)
    circle = (x-8)**2+y*y-16
    outcome['distance-ratio']=_certificate('distance-ratio','SQUARED_LOCUS_TO_CIRCLE',
        [_check('circle_equation_equivalence',simplify(distance+3*circle)==0),
         _check('B_point_not_on_circle',simplify(circle.subs({x:6,y:0}))!=0)],
        ['A=(0,0)','B=(6,0)','PA=2*PB','PA>=0','PB>=0','PB!=0'],
        '比例关系平方及配方在受控数值题上核实；非负距离保证平方后的方向处理。')
    F=x*x/9 + y*y/4 - 1
    fx,fy=diff(F,x),diff(F,y)
    outcome['ellipse-tangent']=_certificate('ellipse-tangent','TANGENT_AT_3_0',
        [_check('point_on_curve',simplify(F.subs({x:3,y:0}))==0),
         _check('nonsingular_gradient',simplify(fx.subs({x:3,y:0}))!=0),
         _check('tangent_linearization',simplify((fx*(x-3)+fy*y).subs({x:3,y:0}))==0)],
        ['P=(3,0)在该椭圆上','grad(F)(P)!=0'],
        '只验证示范点 (3,0) 的切线构造条件，不证明任意点的学生推导。')
    H=x*x/9-y*y/4-1
    hx,hy=diff(H,x),diff(H,y)
    outcome['hyperbola-tangent']=_certificate('hyperbola-tangent','TANGENT_AT_3_0',
        [_check('point_on_curve',simplify(H.subs({x:3,y:0}))==0),
         _check('nonsingular_gradient',simplify(hx.subs({x:3,y:0}))!=0),
         _check('directional_gradient_y_zero',simplify(hy.subs({x:3,y:0}))==0)],
        ['P=(3,0)在该双曲线上','grad(H)(P)!=0'],
        '仅验证受控示例点处的隐式切线条件。')
    for pid in outcome:
        assert pid in PROBLEMS, f'Unknown curated problem: {pid}'
    return outcome

def coverage():
    checked=certificates()
    return {'curated_problems':len(PROBLEMS),'problems_with_limited_certificates':len(checked),
        'checked_ids':sorted(checked),'verified_student_steps':0,
        'note':'证书仅对应预设的代数事实和局部条件，不代表整题自动证明。'}

def teacher_certificate(problem_id):
    """Do not expose this via student API; hidden algebra could disclose the answer."""
    return certificates().get(problem_id)
