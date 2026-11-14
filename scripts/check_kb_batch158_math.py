#!/usr/bin/env python3
"""Independent exact bounded witnesses for KB158, not general proof certification."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch158_lessons as lessons
OUT=ROOT/"docs/evaluation/KB_BATCH158_EXACT_WITNESSES.json"
def enc(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def group(i,items):
    if len(items)!=4:raise ValueError("expected two legal and two rejected cases")
    rows=[]
    for j,(key,observed,reason) in enumerate(items):
        if bool(observed) is not (j<2):raise AssertionError(f"KB158 failed {lessons.IDS[i]}/{key}: {observed}")
        rows.append(dict(source_candidate_id=lessons.IDS[i],case=key,
            assertion_is_true=bool(observed),passed=True,basis=reason,
            expectation="LEGAL_OR_BOUNDARY_TRUE" if j<2 else "INVALID_PREMISE_OR_FALSE_GENERALIZATION_REJECTED",
            mathematical_scope="BOUNDED_EXACT_WITNESS_NOT_GENERAL_PROOF"))
    return rows
def build():
    a,b=S.symbols("a b",real=True)
    R=S.Rational; rows=[]
    rows+=group(0,[
      ("rational-power-16",16**R(3,4)==8,"正底数16的四次正根是2，再立方为8"),
      ("same-positive-base-add",S.simplify(4**R(1,2)*4**R(3,2)-4**2)==0,"在正底数4上同底数指数相加"),
      ("negative-base-sqrt-real",S.sqrt(-4).is_real is True,"负底数偶次实根不存在"),
      ("zero-negative-power-finite",S.Pow(0,-1).is_finite is True,"零的负幂不是有限实数")])
    alpha,beta=S.symbols("alpha beta",real=True)
    rows+=group(1,[
      ("cos-difference-general-identity",S.trigsimp(S.cos(alpha-beta)-S.cos(alpha)*S.cos(beta)-S.sin(alpha)*S.sin(beta))==0,"使用全实角三角恒等式精确化简"),
      ("sin-addition-general-identity",S.trigsimp(S.sin(alpha+beta)-S.sin(alpha)*S.cos(beta)-S.cos(alpha)*S.sin(beta))==0,"单位圆旋转分量完全相等"),
      ("cos-distributes-over-subtraction",S.cos(S.pi/3-S.pi/3)==S.cos(S.pi/3)-S.cos(S.pi/3),"cos差角不能拆作余弦的差"),
      ("sin-distributes-over-addition",S.sin(S.pi/6+S.pi/3)==S.sin(S.pi/6)+S.sin(S.pi/3),"sin和角不能拆作两个正弦之和")])
    samples=[1,2,3,100]
    rows+=group(2,[
      ("outlier-mean",R(sum(samples),len(samples))==R(53,2),"样本算术均值为106/4"),
      ("even-sample-median",R(samples[1]+samples[2],2)==R(5,2),"排序后中间两个数取平均"),
      ("outlier-does-not-change-mean",R(1+2+3+100,4)==R(1+2+3+1000,4),"均值受极大值影响"),
      ("unique-mode-in-tie",len({2,3})==1,"重复最多的值可以不唯一")])
    u=S.Matrix([3,4,0]);v=S.Matrix([1,1])
    rows+=group(3,[
      ("orthonormal-distance",S.sqrt(u.dot(u))==5,"直角坐标差向量长度为5"),
      ("opposite-displacements-same-length",S.sqrt(u.dot(u))==S.sqrt((-u).dot(-u)),"距离与方向无关"),
      ("oblique-basis-incorrect-norm",S.sqrt(5)==S.sqrt(2),"斜基坐标向量(1,1)真实长度不是√2"),
      ("negative-euclidean-distance",-S.sqrt(u.dot(u))==5,"距离必须非负")])
    def corr(xs,ys):
        xm=R(sum(xs),len(xs));ym=R(sum(ys),len(ys))
        xx=sum((x-xm)**2 for x in xs);yy=sum((y-ym)**2 for y in ys)
        return None if xx==0 or yy==0 else S.simplify(sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/S.sqrt(xx*yy))
    rows+=group(4,[
      ("positive-perfect-correlation",corr([1,2,3],[2,4,6])==1,"非零中心化向量相同方向"),
      ("negative-perfect-correlation",corr([1,2,3],[6,4,2])==-1,"非零中心化向量相反方向"),
      ("constant-x-correlation-is-zero",corr([5,5,5],[1,2,3])==0,"X无方差则Pearson系数未定义而不是0"),
      ("perfect-correlation-exceeds-one",corr([1,2,3],[2,4,6])>1,"Cauchy–Schwarz界保证|r|≤1")])
    epsilon=R(1,100);delta=epsilon/3;x0=R(2)+delta/2
    rows+=group(5,[
      ("linear-epsilon-delta-instance",abs(3*x0+1-7)<epsilon,"任取ε=1/100、δ=ε/3，再取满足0<|x−2|<δ的具体点"),
      ("removable-singularity-limit",S.limit((a*a-1)/(a-1),a,1)==2,"去心极限可存在而函数原点无定义"),
      ("jump-left-right-equal",S.limit(S.Integer(0),a,0,dir='-')==S.limit(S.Integer(1),a,0,dir='+'),"跳跃函数左右极限不一致"),
      ("epsilon-is-zero-allowed",R(0)>0,"极限定义要求任给正ε而非ε=0")])
    joint=[[R(1,4),R(1,4)],[R(0),R(1,2)]]
    rows+=group(6,[
      ("joint-probability-normalized",sum(map(sum,joint))==1,"联合质量全非负且总和为1"),
      ("y-one-marginal",joint[0][1]+joint[1][1]==R(3,4),"固定Y=1对X边缘化"),
      ("diagonal-joint-is-independent",R(0)==R(1,2)*R(1,2),"均匀边缘且非对角概率零不代表独立"),
      ("joint-probability-total-not-one",sum(map(sum,joint))==R(3,4),"合法联合质量不应只有3/4")])
    xs=[1,2,3]; ys=[2,4,6]
    rows+=group(7,[
      ("observed-perfect-linear",corr(xs,ys)==1,"样本上观察到r=1说明三点正共线"),
      ("linear-fit-exact-three-points",all(y==2*x for x,y in zip(xs,ys)),"三个观测点完全满足y=2x"),
      ("association-derives-intervention",(2*5)==(2*1),"两种结构模型X=Z,Y=2X与X=Z,Y=2Z有相同观察数据，但干预do(X=5),Z=1时Y分别为10和2"),
      ("common-cause-ruled-out-by-correlation",corr(xs,ys)!=1,"观察相关不能排除共同原因")])
    Reflect=S.diag(1,-1);HalfTurn=-S.eye(2); q=S.Matrix([1,-2]); O=S.Matrix([3,4])
    rows+=group(8,[
      ("reflection-preserves-length",S.simplify((Reflect*q).dot(Reflect*q)-q.dot(q))==0,"反射矩阵正交"),
      ("central-midpoint",O==S.Rational(1,2)*(q+(2*O-q)),"中心点是原点和像点中点"),
      ("reflection-has-positive-determinant",Reflect.det()==1,"二维镜像反射会翻转取向"),
      ("half-turn-fixes-all-points",HalfTurn*q==q,"中心对称只固定中心点")])
    t=S.symbols("t",real=True)
    density=S.Piecewise((2,(t>=0)&(t<=R(1,2))),(0,True))
    rows+=group(9,[
      ("uniform-interval-integral",S.integrate(2,(t,0,R(1,4)))==R(1,2),"密度2在长度1/4区间上的概率为1/2"),
      ("discrete-mass-normalization",sum([R(1,2),R(1,4),R(1,4)])==1,"离散概率质量总和为1"),
      ("density-must-be-at-most-one",2<=1,"连续概率密度可大于1"),
      ("single-point-probability-is-density",S.integrate(2,(t,0,0))==2,"连续分布单点积分为0，不等于密度值")])
    if len(rows)!=40 or sum(x["assertion_is_true"] for x in rows)!=20:raise ValueError("KB158 witness partition invalid")
    return dict(schema="kb158-independent-finite-exact-witness/1",cases=rows,
                verified_bounded_cases=40,legal_or_boundary_true=20,
                invalid_premise_rejected=20,formal_general_proofs_certified=0,
                student_free_steps_verified=0,teacher_approved=0)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args();out=enc(build())
    if a.write:OUT.write_text(out,encoding="utf-8")
    elif OUT.read_text(encoding="utf-8")!=out:raise ValueError("KB158 exact witness artifact drift")
    print("PASS KB158 40 independent bounded exact witnesses; no general theorem certified")
if __name__=="__main__":main()
