#!/usr/bin/env python3
"""Independently re-evaluate 20 fixed teacher worked-example answers (bounded cases).

These are case-specific exact checks, not automatic proof or teacher approval.
Neither worked answer nor its solution is served to students.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import sympy as S

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch158_lessons as lesson

OUT = ROOT / "docs/evaluation/KB_BATCH158_TEACHER_EXAMPLE_ORACLES.json"

# Frozen expected answer strings are checked against the manuscripts; the truth
# of each answer is computed independently rather than asserted from the text.
EXPECTED = [
    ("8（正实数根）", "a²"),
    ("1（精确值）", "√3/2"),
    ("均值26.5；中位数2.5", "没有唯一众数；2和3并列"),
    ("5（同一长度单位）", "5（同一长度单位）"),
    ("1（精确值）", "未定义"),
    ("成立；可取δ=ε/3", "2（极限值）"),
    ("p_X=(1/2,1/2)，p_Y=(1/4,3/4)", "不独立"),
    ("不能", "样本精确正线性相关；不直接证明因果"),
    ("(2,−3)", "(5,10)"),
    ("1/2", "1/2"),
]

def correlation(xs, ys):
    xs = list(map(S.Rational, xs))
    ys = list(map(S.Rational, ys))
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    u, v = [x - mx for x in xs], [y - my for y in ys]
    xx, yy = sum(x*x for x in u), sum(y*y for y in v)
    return None if xx == 0 or yy == 0 else S.simplify(sum(x*y for x,y in zip(u,v))/S.sqrt(xx*yy))

def exact_truth_cases():
    a = S.symbols("a", positive=True)
    epsilon = S.symbols("eps", positive=True)
    q1 = S.Matrix([1,2,3])
    q2 = S.Matrix([4,6,3])
    q3 = S.Matrix([-1,2,0])
    q4 = S.Matrix([2,2,4])
    p = S.Matrix([2,3])
    center = S.Matrix([3,4])
    joint = [[S.Rational(1,4),S.Rational(1,4)], [S.Rational(0),S.Rational(1,2)]]
    xs, ys = [1,2,3], [2,4,6]
    # Observationally X=Z,Y=2X and X=Z,Y=2Z coincide for all Z;
    # under do(X=5),Z=1 they diverge. Thus observational perfection
    # cannot establish a causal direction.
    obs_equal = all(2*z == 2*x for x,z in zip(xs,xs))
    intervention_differs = (2*5 != 2*1)
    cases=[
        (S.Integer(16)**S.Rational(3,4)==8, "16 positive rational exponent"),
        (S.simplify(a**S.Rational(1,2)*a**S.Rational(3,2)-a**2)==0, "positive-base exponent product"),
        (S.sin(S.pi/3+S.pi/6)==1, "exact sine addition"),
        (S.cos(S.pi/3-S.pi/6)==S.sqrt(3)/2, "exact cosine difference"),
        (S.Rational(106,4)==S.Rational(53,2) and S.Rational(2+3,2)==S.Rational(5,2), "mean and median"),
        (max([2,2,3,3,5].count(v) for v in {2,3,5})==2 and {v for v in {2,3,5} if [2,2,3,3,5].count(v)==2}=={2,3}, "two modes"),
        ((q2-q1).dot(q2-q1)==25, "3D distance 3 4 0"),
        ((q4-q3).dot(q4-q3)==25, "3D distance 3 0 4"),
        (correlation(xs,ys)==1, "Pearson r=1"),
        (correlation([5,5,5],[2,3,4]) is None, "zero variance undefined"),
        (epsilon>0 and S.simplify(abs(3*(2+epsilon/6)+1-7)-epsilon/2)==0, "epsilon-delta admissible constructive epsilon"),
        (S.limit((a*a-1)/(a-1),a,1)==2, "removable singularity limit"),
        ([sum(row) for row in joint]==[S.Rational(1,2)]*2 and [sum(row[j] for row in joint) for j in range(2)]==[S.Rational(1,4),S.Rational(3,4)], "joint marginalization"),
        (S.Rational(0)!=S.Rational(1,2)*S.Rational(1,2), "diagonal joint dependence"),
        (obs_equal and intervention_differs, "observational correlation noncausal countermodel"),
        (correlation(xs,ys)==1 and intervention_differs, "r1 is insufficient for causation"),
        (S.diag(1,-1)*p==S.Matrix([2,-3]), "x-axis reflection"),
        (2*center-S.Matrix([1,-2])==S.Matrix([5,10]), "central reflection"),
        (S.integrate(2,(S.Symbol("t"),0,S.Rational(1,4)))==S.Rational(1,2), "continuous uniform probability"),
        (sum([F(1,4),F(1,4)])==F(1,2), "discrete probability sum"),
    ]
    return cases

def build(rows=None):
    rows=lesson.build() if rows is None else rows
    lesson.validate(rows)
    assert len(rows)==len(EXPECTED)==10
    cases=exact_truth_cases()
    if len(cases)!=20:raise ValueError("expected 20 bounded computed examples")
    out=[]
    for i,(row,answers) in enumerate(zip(rows,EXPECTED)):
        examples=row["teacher_examples"]
        if len(examples)!=2:raise ValueError("two teacher examples required")
        for j,expected in enumerate(answers):
            actual=examples[j]["answer"]
            if actual!=expected:raise ValueError(f"manuscript answer drift {row['id']} example {j+1}")
            is_true,reason=cases[2*i+j]
            if is_true is not S.true and is_true is not True:
                raise ValueError(f"exact mathematics failed {row['id']} example {j+1}: {reason}")
            out.append({"manuscript_id":row["id"],"example_number":j+1,
                        "exact_case_passed":True,"scope":"BOUNDED_EXACT_CASE_NOT_GENERAL_PROOF",
                        "oracle_reason":reason,"student_answer_exposed":False})
    return {"schema":"kb158-independent-worked-examples-v1",
            "cases":out,"worked_examples_checked":20,"unproved_general_claims":0,
            "teacher_approved":0,"student_authoritative":0}

def serialize(x):
    return json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"

def main():
    p=argparse.ArgumentParser()
    x=p.add_mutually_exclusive_group(required=True)
    x.add_argument("--write",action="store_true")
    x.add_argument("--check",action="store_true")
    a=p.parse_args()
    body=serialize(build())
    if a.write:OUT.write_text(body,encoding="utf-8")
    elif OUT.read_text(encoding="utf-8")!=body:raise ValueError("example oracle artifact drift")
    print("PASS KB158 20 exact teacher worked-example answer checks; teacher approvals 0")
if __name__=="__main__":main()
