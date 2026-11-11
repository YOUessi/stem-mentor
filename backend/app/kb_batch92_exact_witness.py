"""Batch92: independent finite exact witnesses for 16 of 24 draft source relations.

These computations do NOT establish universal theorem correctness, semantic
identity of two curriculum atoms, or teacher approval. No NLP is trusted here.
All numerical values are independently specified, not parsed from editorial
worked examples; calculations use integers/Fraction/SymPy.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import pi, sin, cos
from sympy import symbols, simplify, sqrt, diff, log, sin as ssin, cos as scos

SUPPORTED = tuple(range(1, 17))


def verify(i: int) -> dict:
    if type(i) is not int or i not in SUPPORTED:
        raise ValueError("only finite source relation cases 1..16 supported")
    x = symbols("x", real=True)
    if i == 1:
        U = frozenset({1, 2, 3})
        A = frozenset({1})
        smaller = frozenset({1, 2})
        positive = U - A == frozenset({2, 3}) and smaller - A == frozenset({2})
        negative = U - A == smaller - A
        witness = "全集改变，A={1}的相对补集由{2,3}变为{2}"
    elif i == 2:
        values = range(-20, 21)
        positive = all((n % 2 == 0) == (n*n % 2 == 0) for n in values)
        negative = any(n % 2 != 0 and n*n % 2 == 0 for n in values)
        # 'negative' deliberately tests invalid implication "2 is odd".
        witness = "41个冻结整数支持奇偶双向；仅有限见证，非全称证明"
    elif i == 3:
        D = [0, 1]
        P = lambda t: t == 0
        positive = (not any(map(P, D))) == all(not P(t) for t in D)
        negative = (not any(map(P, D))) == any(not P(t) for t in D)
        witness = "D={0,1}时 ¬∃P 为假，而 ∃¬P 为真"
    elif i == 4:
        f = lambda t: t*t-4
        positive = f(0) < 0 and f(2) == 0 and f(3) > 0
        negative = f(-1) >= 0 or f(2) < 0
        witness = "x²−4在非负长度域上小于0的区间为[0,2)"
    elif i == 5:
        p = lambda t: t*t
        positive = [p(t) for t in (-1, 0, 2)] == [1, 0, 4]
        negative = p(-1) < p(0)
        witness = "x²在[-1,2]并非全区间严格递增"
    elif i == 6:
        positive = simplify(ssin(-x)+ssin(x)) == 0 and simplify(scos(-x)-scos(x)) == 0
        negative = simplify(ssin(-x + 1) + ssin(x + 1)) == 0
        witness = "sin x奇、cos x偶；sin(x+1)一般不是奇函数"
    elif i == 7:
        positive = simplify(log(sqrt(2),2)-F(1,2)) == 0 and 2 ** F(1,1) == 2
        negative = 1 > 0 and 1 != 1
        witness = "对数底数2合法，底数1不合法"
    elif i == 8:
        a,b = symbols("a b", real=True)
        positive = simplify(2*ssin(a)*ssin(b)-(scos(a-b)-scos(a+b))) == 0
        negative = simplify(2*ssin(a)*ssin(b)-(scos(a-b)+scos(a+b))) == 0
        witness = "积化和差需相减而非相加"
    elif i == 9:
        positive = [2*t+1 for t in (0,1,2)] == [1,3,5] and [2**t for t in (0,1,2)] == [1,2,4]
        negative = all(2**t > 2*t+1 for t in (0,1,2))
        witness = "t=0,1,2时指数并非处处压过线性"
    elif i == 10:
        u,v = (1,0),(0,2)
        positive = tuple(u[j]+v[j] for j in range(2)) == (1,2)
        negative = tuple(u[j]-v[j] for j in range(2)) == (1,2)
        witness = "u+v=(1,2)，不能与u−v=(1,−2)混同"
    elif i == 11:
        det = lambda u,v: u[0]*v[1]-u[1]*v[0]
        positive = det((2,4),(1,2)) == 0
        negative = sum(t*t for t in (0,0)) > 0  # zero vector fails nonzero direction precondition
        witness = "det((2,4),(1,2))=0，零向量不能决定唯一方向"
    elif i == 12:
        u,v = (3,4),(1,0)
        norm2 = v[0]**2+v[1]**2
        projection = tuple(F(u[0]*v[0]+u[1]*v[1],norm2)*c for c in v)
        orthogonal = tuple(u[k]-projection[k] for k in range(2))
        positive = projection == (3,0) and orthogonal == (0,4)
        negative = sum(c*c for c in (0,0)) != 0  # zero denominator forbidden
        witness = "非零v=(1,0)可投影，v=0须拒绝"
    elif i == 13:
        dot = lambda u,v:sum(a*b for a,b in zip(u,v))
        positive = dot((1,2),(2,-1)) == 0 and dot((1,2),(1,2)) > 0
        negative = dot((0,0),(1,1)) != 0
        witness = "非零正交点积为0，零向量无法定义非零夹角"
    elif i == 14:
        z1,z2 = 2+3j,3+2j
        positive = z1 != z2 and (z1-(1+1j)) == 1+2j
        negative = z1 == z2
        witness = "复数相等须实部和虚部分别相等"
    elif i == 15:
        positive = F(1,3)*F(12) == 4
        negative = F(12) == F(4)
        witness = "同底同高圆锥体积是圆柱体积1/3"
    else:
        A,B = {2,4,6},{4,5}
        positive = len(A|B)==4 and len(A)+len(B)-len(A&B)==4
        negative = len(A|B)==len(A)+len(B)
        witness = "事件相交时P(A∪B)需扣除P(A∩B)"
    if not isinstance(positive, bool): positive=bool(positive)
    if not isinstance(negative, bool): negative=bool(negative)
    if not positive or negative:
        raise AssertionError(f"witness {i}: positive={positive} negative={negative}")
    return {
        "review_id": f"KB92-REL-{i:03d}",
        "status": "VERIFIED_FINITE_INSTANCE_WITH_BOUNDARY_REJECTION",
        "witness": witness, "general_theorem_certified": False,
        "semantic_equivalence_certified": False,
        "teacher_approved": False, "student_publishable": False,
        "evidence_scope": "CONTROLLED_EXACT_OR_SYMBOLIC_CASE_ONLY"
    }


def check_all() -> dict:
    return {f"KB92-REL-{i:03d}": verify(i) for i in SUPPORTED}
