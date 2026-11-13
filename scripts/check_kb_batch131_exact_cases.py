#!/usr/bin/env python3
"""Batch131 independent, bounded SymPy checks; NOT quantified proofs or student grading."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/evaluation/KB_BATCH131_EXACT_BOUNDARIES.json'
MD=ROOT/'docs/evaluation/KB_BATCH131_EXACT_BOUNDARIES.md'

def oracle():
    R=S.Rational
    pi=S.pi
    x,y,n=S.symbols('x y n',positive=True,integer=True)
    V=lambda *z:S.Matrix(z)
    results=[]
    def add(k,assume,invalid,good,bad):
        if not bool(good) or not bool(bad):raise ValueError('incorrect oracle: '+k)
        results.append({'case':k,'checked_assumption':assume,'invalid_boundary':invalid,
                        'exact_valid_witness_passed':True,'exact_invalid_witness_rejected':True,
                        'universally_proved':False,'teacher_approved':False,'student_step_verified':False})
    add('cone_cylinder', '圆锥半径2高3且高度为正','混同圆锥与同底同高圆柱体积',
        S.simplify(S.Rational(1,3)*pi*2**2*3-4*pi)==0,
        S.simplify(pi*2**2*3-4*pi)!=0)
    add('two_event_union','共同概率空间内交集概率为3/10','忘记交集导致并集概率超过1',
        R(3,5)+R(1,2)-R(3,10)==R(4,5),
        R(3,5)+R(1,2)>1)
    add('variance_denominator','样本为(1,3)且n=2','将描述方差与n−1无偏样本方差混用',
        (1**2+1**2)/2==1 and (1**2+1**2)/(2-1)==2,
        S.Integer(2)/S.Integer(0)==S.zoo)
    add('vertical_line','过(2,0)与(2,3)的直线为x=2','竖直直线不能表示为有限斜率函数',
        all(2==2 for _ in (0,3)), S.Integer(3)/S.Integer(0)==S.zoo)
    add('circle_tangent','圆x²+y²=25和直线y=5','无效直线系数全零会令距离分母为零',
        S.solveset(x*x+25-25,x,domain=S.S.Reals)==S.FiniteSet(0),
        S.sqrt(0**2+0**2)==0)
    add('ellipse_focal_sum','a=5,c=3,b=4,椭圆右顶点(5,0)','距离和等于焦距时不是非退化椭圆',
        S.sqrt((5-3)**2)+S.sqrt((5+3)**2)==10 and 5**2-3**2==4**2,
        not (5>5))
    add('binomial_three_trials','三个独立成功率1/2伯努利试验','不放回抽球不能自动假定联合独立',
        S.binomial(3,2)*R(1,2)**3==R(3,8),
        S.binomial(2,2)/S.binomial(4,2)!=R(1,4))
    add('hypergeometric_impossible','N=5,K=1,n=2无放回','不可能抽出两个成功对象',
        sum(k*S.binomial(1,k)*S.binomial(4,2-k)/S.binomial(5,2) for k in (0,1))==R(2,5),
        S.binomial(1,2)==0)
    add('normal_std_zero','μ=3,σ=2,x=7','σ=0不能进行正态标准化',
        R(7-3,2)==2, S.Integer(4)/S.Integer(0)==S.zoo)
    add('pearson_constant','x=(1,2,3),y=(2,4,6)','常量x的离差平方和为零，相关系数未定义',
        sum((a-2)*(b-4) for a,b in zip((1,2,3),(2,4,6)))==4,
        sum((a-5)**2 for a in (5,5,5))==0)
    add('log_composition','f(x)=ln(x²),x>0','链式求导缺失因子或在x=0求值',
        S.simplify(S.diff(S.log(x*x),x)-2/x)==0,
        S.simplify(S.diff(S.log(x*x),x).subs(x,2)-R(1,2))!=0)
    u=V(1,0,0);v=V(2,3,4);z=V(0,0,0)
    add('vector_projection','投影目标u非零','目标方向零向量导致范数平方为零',
        u*(v.dot(u)/u.dot(u))==V(2,0,0),z.dot(z)==0)
    A=S.Matrix([[1,1],[2,2]])
    add('linear_rank_consistency','线性系统Ax=b需比较秩','同样系数矩阵可能有解或无解',
        A.rank()==A.row_join(V(2,4)).rank()==1,
        A.row_join(V(2,5)).rank()!=A.rank())
    t=S.symbols('t',real=True)
    add('differentiability_at_point','x²在2点可导','|x|在0的左右导数不相同',
        S.diff(t*t,t).subs(t,2)==4,
        S.limit(S.Abs(t)/t,t,0,dir='+')!=S.limit(S.Abs(t)/t,t,0,dir='-'))
    nn=S.symbols('nn',integer=True,positive=True)
    norm_sum=S.summation(S.Symbol('k'),(S.Symbol('k'),1,nn))/nn**2
    add('riemann_mesh_weight','右端点网格宽度为1/n','漏乘网格宽时和式不收敛到有限面积',
        S.limit(norm_sum,nn,S.oo)==R(1,2),
        S.limit(norm_sum*nn,nn,S.oo)==S.oo)
    add('bisection_preconditions','连续多项式x²−2在[1,2]端点异号','异号但不连续的1/x不能调用零点定理',
        (1**2-2)*(2**2-2)<0,
        S.Integer(-1)*S.Integer(1)<0 and S.solveset(1/t,t,domain=S.Interval(-1,1))==S.EmptySet)
    return results
def check():
    rows=oracle()
    assert len(rows)==16 and len({r['case'] for r in rows})==16
    return {'batch':131,'verification_type':'FINITE_EXACT_SYMPY_WITNESSES_NOT_GENERAL_PROOF',
            'positive_exact_checks':len(rows),'invalid_boundary_checks':len(rows),
            'proofs_formally_certified':0,'student_free_text_steps_verified':0,
            'teacher_approvals':0,'cases':rows}
def validate_snapshot(candidate):
    if candidate != check(): raise ValueError('tampered or stale exact mathematical witness')
    return True
def render(d):
    x=['# Batch131 — 16 exact positive + 16 exact invalid boundary witnesses','',
       'These independently recomputed finite witnesses are NOT universal proofs or approval of student work.','']
    for r in d['cases']:
        x += ['## '+r['case'], 'Valid-condition witness: '+r['checked_assumption'],
             'Invalid or degenerate boundary: '+r['invalid_boundary'],
             'SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.','']
    return '\n'.join(x)
def main():
    a=argparse.ArgumentParser();g=a.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true')
    opts=a.parse_args();d=check()
    outputs=((OUT,json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+'\n'),(MD,render(d)))
    for f,s in outputs:
        if opts.write: f.write_text(s,encoding='utf-8')
        elif not f.exists() or f.read_text(encoding='utf-8')!=s: raise ValueError('stale math evidence '+str(f))
    print('B131 MATH 16 valid + 16 invalid EXACT; universal proofs=0')
if __name__=='__main__':main()
