#!/usr/bin/env python3
"""Exact finite positive/negative witnesses for Batch120; no general-proof certificate."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import sympy as S
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch120_semantic_expansion as source
OUT = ROOT / "docs/evaluation/KB_BATCH120_MATH_FINITE_WITNESSES.json"

def cases():
    r = S.Rational
    x = S.symbols("x", real=True)
    z = S.Matrix([0, 0, 0])
    m = S.Matrix
    rot = m([[0, -1], [1, 0]])
    v = m([1, 0])
    t = m([2, 0])
    return [
        # COMPULSORY
        ("C103", "数量积零与非零向量", m([1,2]).dot(m([2,-1])) == 0, m([1,2]).dot(m([1,2])) != 0),
        ("C104", "正交投影非零分母", m([3,4]).dot(m([3,4])) == 25, m([0,0]).dot(m([0,0])) == 0),
        ("C107", "余弦定理与非退化三边", 3**2+4**2 == 5**2, 1+2 == 3),
        ("C108", "SSA可能两角", S.sin(S.pi/6) == S.sin(5*S.pi/6), S.pi/6 != 5*S.pi/6),
        ("C111", "抽样均值与均方距离", sum([1,2,3]) == 6, sum((k-2)**2 for k in [1,2,3]) == 2),
        ("C112", "分层比例的整数配置", 20*r(1,4) == 5, 20*r(3,4) == 15),
        # SELECTIVE COMPULSORY
        ("S101", "等差递推", [2+3*k for k in range(3)] == [2,5,8], 2+3*3 != 2+3*2),
        ("S102", "等比有限幂和与q0区别", sum(2*3**k for k in range(4)) == 80, 3 != 1),
        ("S104", "平方根正点求导", S.diff(S.sqrt(x),x).subs(x,4)==r(1,4), S.diff(S.sqrt(x),x).subs(x,0)==S.zoo),
        ("S105", "三维两点距离", S.sqrt(3**2+4**2+12**2)==13, S.sqrt(3**2+4**2)==5),
        ("S108", "水平与竖直的法向判定", m([1,0]).dot(m([0,1]))==0, m([1,0]).dot(m([1,0]))!=0),
        ("S111", "椭圆a^2=b^2+c^2", 5**2==4**2+3**2, 5>3),
        # ELECTIVE A
        ("A101", "外积与平行退化", m([1,0,0]).cross(m([0,1,0]))==m([0,0,1]), m([1,0,0]).cross(m([2,0,0]))==z),
        ("A102", "投影的非零分母", m([1,2,3]).dot(m([0,0,2])) == 6, m([0,0,0]).dot(m([0,0,0])) == 0),
        ("A103", "线性相关秩亏", m([[1,2],[2,4]]).det()==0, m([[1,0],[0,1]]).det()!=0),
        ("A108", "可逆三元线性系统", m.diag(2,3,4).det()==24, m.diag(2,3,0).det()==0),
        # ELECTIVE B
        ("B101", "密度归一化", S.integrate(r(1,2),(x,0,2))==1, S.integrate(r(1,2),(x,0,1))==r(1,2)),
        ("B102", "t分布方差自由度阈值", r(4,4-2)==2, 2-2==0),
        ("B104", "rho=1奇异", m([[1,1],[1,1]]).det()==0, m([[1,0],[0,1]]).det()!=0),
        ("B105", "伯努利开区间边界似然", r(9,10)**3 < 1, r(999,1000)**3>r(9,10)**3),
        # ELECTIVE C
        ("EC104", "复利与简单利息差异", (1+r(1,10))**2>1+2*r(1,10), (1+r(1,10))**2==r(121,100)),
        ("EC105", "线性模型负产量不可行", m([[1,0],[0,1]]).inv()*m([-1,2])==m([-1,2]), -1<0),
        ("EC106", "权重归一化", r(1,4)*8+r(3,4)*12==11, r(1,4)+r(3,4)==1),
        ("EC107", "指数倍率一致与截距", 2**4==16, (2**4)/(2**3)==2),
        # ELECTIVE D
        ("ED104", "正弦振幅与频率独立", S.diff(3*S.sin(2*x),x).subs(x,0)==6, S.diff(5*S.sin(2*x),x).subs(x,0)==10),
        ("ED105", "十二平均律频率翻倍", S.simplify((2**S.Rational(1,12))**12)==2, 2**S.Rational(1,12) != 2),
        ("ED106", "节拍最小公倍数", S.ilcm(3,4)==12, S.ilcm(2,4)==4),
        ("ED107", "线性变换不保长度的例子", m.diag(2,1)*m([1,0])==m([2,0]), m([2,0]).norm()!=m([1,0]).norm()),
        # ELECTIVE E
        ("EE102", "旋转和平移不交换", rot*(v+t)!=rot*v+t, rot*v+t==m([2,1])),
        ("EE103", "球面直角三角形内角和", 3*S.pi/2 > S.pi, S.pi/2+S.pi/2+S.pi/2 == 3*S.pi/2),
        ("EE104", "Euclid非零整数输入", S.igcd(84,30)==6, S.igcd(6,0)==6),
        ("EE105", "名义收益扣除通胀", (1+r(1,10))/(1+r(1,5))-1 < 0, (1+r(1,10))/(1+r(1,5))-1==r(-1,12)),
    ]

def build():
    source_data = json.loads(source.OUT.read_text())
    source.validate(source_data)
    found = {r["local_key"] for r in source_data["candidates"]}
    rows = []
    for key, name, positive, negative in cases():
        source.demand(key in found, "unanchored math case " + key)
        source.demand(bool(positive) and bool(negative), "failed exact finite math check " + key)
        rows.append({"candidate": "hs-semantic-pilot-120-" + key.lower(),
                     "case_name": name, "exact_positive_passed": True,
                     "exact_negative_passed": True, "general_proof_certified": False})
    source.demand(len({r["candidate"] for r in rows}) == len(rows), "duplicate case mapping")
    return {
        "batch": 120, "precision": "SYMPY_EXACT_FINITE_NOT_GENERAL_PROOF",
        "exact_witness_pairs": len(rows),
        "exact_cases_passed": 2*len(rows),
        "formal_general_proofs_certified": 0,
        "student_free_text_verified": False, "teacher_approved": False,
        "cases": rows
    }

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    opts = parser.parse_args()
    val = source.serial(build())
    if opts.write:
        OUT.write_text(val, encoding="utf-8")
    else:
        source.demand(OUT.exists() and OUT.read_text(encoding="utf-8")==val,"math oracles artifact drift")
    print("Batch120:", len(cases()), "positive/negative exact witness pairs; zero general proofs")
if __name__ == "__main__":
    main()
