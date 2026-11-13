"""Independent, bounded exact example checks for Batch34 editorial manuscripts.

This is NOT a universal theorem prover, author endorsement or student checker.
Uncovered topics remain pending. No untrusted expression eval/parse is used.
"""
from __future__ import annotations
from fractions import Fraction as F
import re
from sympy import Matrix, Symbol, Rational, sin, cos, pi, diff, limit, simplify, integrate

BASE="KB33-"
def i(track,page,serial):
    return f"{BASE}{track}-P{page}-A{serial:03}"

def evidence():
    x=Symbol("x",real=True)
    h=Symbol("h",real=True)
    records={}
    def add(id, result_a, result_b, justification):
        if type(result_a) is not bool or type(result_b) is not bool or not (result_a and result_b):
            raise AssertionError(f"Finite witness failed for {id}: {result_a}/{result_b}")
        records[id]=dict(valid_numeric_instances=2,invalid_premises_exercised=0,
                         check_class="EXACT_BOUNDED_EXAMPLE_NOT_WHOLE_PROOF",
                         validity_reason=justification,whole_theorem_formally_certified=False,
                         student_answer_automatically_verified=False,teacher_approved=False)
    add(i("A","053",1), limit(x*x,x,2)==4, limit(x*x,x,0)==0 and 1!=0,
        "多项式极限与反例函数点赋值独立比较。")
    add(i("A","053",3), limit(((3+h)**2-9)/h,h,0)==6,
        limit(((2+h)**3-8)/h,h,0)==12,
        "对指定多项式差商直接取双侧极限，不能代表任意函数可导。")
    add(i("A","053",5), diff(x*x,x).subs(x,0)==0 and (x*x).subs(x,0)==0,
        limit(abs(h)/h,h,0,dir="+")==1 and limit(abs(h)/h,h,0,dir="-")==-1,
        "对平方函数驻点和绝对值函数尖点作有界实例核验；驻点不蕴含极值的一般命题仍待证明。")
    add(i("A","054",2), Matrix([1,0,0]).dot(Matrix([0,1,0]))==0 and Matrix([1,0,0]).cross(Matrix([0,1,0]))==Matrix([0,0,1]),
        Matrix([1,0,0]).dot(Matrix([2,0,0]))==2 and Matrix([1,0,0]).cross(Matrix([2,0,0]))==Matrix([0,0,0]),
        "三维定值向量内外积独立坐标计算。")
    add(i("A","054",4), Matrix([[1,0],[0,1],[0,0]]).rank()==2,
        Matrix([[1,2],[2,4],[0,0]]).rank()==1,
        "两个指定向量组秩与线性独立的实例检查。")
    add(i("B","058",5), min(abs(k) for k in (-2,-1,0,1))==0 and max(abs(k) for k in (-2,-1,0,1))==2,
        min((k-1)**2 for k in (-1,0,1,2))==0 and max((k-1)**2 for k in (-1,0,1,2))==4,
        "用包含端点及驻点的有限整数样本网格核验两道例题值；不是一般连续函数极值证明。")
    add(i("B","059",1), integrate(x,(x,0,2))==2, integrate(3,(x,0,2))==6,
        "对指定连续函数的定积分用独立符号积分核对。")
    add(i("B","059",4), 0**2+0**2==0 and 1**2+0**2==1,
        0+0==0 and 1+1==2,
        "核验单位圆盘和单位正方形上的端点/中心候选值，不凭几个点认证全局最值。")
    A=Matrix([[2,0],[0,3]]); B=Matrix([[1,2],[2,4]])
    add(i("B","060",3), A.det()==6 and A*A.inv()==Matrix.eye(2),
        B.det()==0 and B*Matrix([-2,1])==Matrix([0,0]),
        "2×2行列式与可逆/退化证据的有限矩阵计算。")
    add(i("B","061",1), integrate(1,(x,Rational(1,2),Rational(1,2)))==0,
        integrate(1,(x,Rational(1,4),Rational(3,4)))==Rational(1,2),
        "均匀[0,1]实例的区间积分，不泛化到离散分布。")
    add(i("B","064",3), Matrix([cos(0),sin(0),0])==Matrix([1,0,0]),
        Matrix([cos(pi),sin(pi),pi])==Matrix([-1,0,pi]),
        "两个指定参数点的三角函数精确值。")
    add(i("C","064",4), all((not (t>2)) or (t>0) for t in range(-10,11)) and not (1>2) and 1>0,
        all((t*t==4)==(abs(t)==2) for t in range(-20,21)),
        "有限整数网格只提供反例和实例；充要方向仍需一般推导。")
    add(i("C","065",2), all((not (((not p) or q) and p)) or q for p in (False,True) for q in (False,True)),
        12%4==0 and 12%2==0 and 4>3 and 4>0,
        "完整四行有限命题真值表加具体数值实例；不校验任意自然语言。")
    def poly(n):return (n-1)*(n-2)*(n-3)
    add(i("C","065",3), [poly(k) for k in (1,2,3)]==[0,0,0], poly(4)==6,
        "对有限归纳误区的明确可复现反例。")
    add(i("C","068",1), F(900,1000)==F(9,10), F(60,90)==F(2,3),
        "抽样框覆盖率与响应率不同分母的有理数算术。")
    add(i("C","068",2), F(6,60)==F(4,40)==F(1,10),
        F(60,100)*F(1)+F(40,100)*F(3)==F(9,5),
        "分层入样概率与总体层权重精确计算。")
    p=pi/7
    add(i("D","070",2), simplify(sin(2*(p+pi))-sin(2*p))==0 and
        simplify(sin(2*(p+pi/2))-sin(2*p)) != 0,
        simplify(sin(p+2*pi)+sin(2*(p+2*pi))-sin(p)-sin(2*p))==0 and
        simplify(sin(pi/2+pi)+sin(2*(pi/2+pi))-sin(pi/2)-sin(2*(pi/2))) != 0,
        "对特定点验证候选周期与反例平移；不能仅凭此断言一般组合函数最小正周期。")
    add(i("D","070",4), simplify((6*pi)/(2*pi))==3,
        sin(pi/2)*3==3 and simplify((4*pi)/(2*pi))==2,
        "频率系数和初相位定值计算。")
    def projectile(t):
        return (F(3)*t,F(4)*t-F(5)*t*t)
    add(i("D","073",1), projectile(F(2,5))==(F(6,5),F(4,5)),
        projectile(F(1))==(F(3),F(-1)),
        "水平与竖直抛体坐标用有理数代入，并另标落地后的模型失效。")
    add(i("E","073",6), Matrix([2*cos(0)+cos(pi/2),2*sin(0)+sin(pi/2)])==Matrix([2,1]),
        Matrix([2*cos(pi/2)+cos(pi/2),2*sin(pi/2)+sin(pi/2)])==Matrix([0,3]),
        "相对关节角复合与两次指定构型坐标的精确三角验证。")
    if len(records)!=20 or sum(v["valid_numeric_instances"] for v in records.values())!=40:
        raise AssertionError("Expected 20 independently checked topics and 40 bounded witnesses")
    return records

def guarded_premise(kind: str, params: dict) -> str:
    """Reject unsafe preconditions for *selected finite examples*; no free-text parsing.

    No SUCCESS code here authorizes proof certification or student-side release.
    """
    if not isinstance(params, dict) or any(type(v) not in (int,str,bool) for v in params.values()):
        return "CONDITIONS_NOT_ESTABLISHED"
    # Exact premise checks must not reinterpret True as 1, swallow huge numeric
    # strings, or accept boolean-flavored integers as a consent/geometry flag.
    boolean_keys = {"defined", "theta2_is_relative"}
    for key, value in params.items():
        if key in boolean_keys and type(value) is not bool:
            return "CONDITIONS_NOT_ESTABLISHED"
        if type(value) is bool and key not in boolean_keys:
            return "CONDITIONS_NOT_ESTABLISHED"
        if type(value) is int and abs(value) > 10**12:
            return "CONDITIONS_NOT_ESTABLISHED"
        if type(value) is str:
            if len(value)>64 or (key != "distribution" and
                re.fullmatch(r"[+-]?\d{1,18}(?:/[+-]?\d{1,18})?", value) is None):
                return "CONDITIONS_NOT_ESTABLISHED"
    try:
        if kind == "point_continuity":
            valid = set(params) == {"limit", "value", "defined"} and params["defined"] is True and F(params["limit"]) == F(params["value"])
        elif kind == "matrix_inverse":
            valid = set(params) == {"a", "b", "c", "d"} and F(params["a"])*F(params["d"]) != F(params["b"])*F(params["c"])
        elif kind == "density_singleton":
            valid = params == {"distribution": "ABSOLUTELY_CONTINUOUS"}
        elif kind == "fraction":
            valid = set(params) == {"num","den"} and F(params["num"]).denominator > 0 and F(params["den"]) != 0
        elif kind == "helix":
            valid = set(params) == {"radius","pitch"} and F(params["radius"]) > 0 and F(params["pitch"]) != 0
        elif kind == "projectile":
            valid = set(params) == {"g", "vy", "t"} and F(params["g"]) > 0 and F(params["vy"]) > 0 and 0 <= F(params["t"]) <= 2*F(params["vy"])/F(params["g"])
        elif kind == "robot_joint":
            valid = set(params) == {"l1", "l2", "theta2_is_relative"} and F(params["l1"]) > 0 and F(params["l2"]) > 0 and params["theta2_is_relative"] is True
        elif kind == "stratified_sample":
            valid = set(params) == {"N", "n"} and F(params["N"]).denominator == 1 and F(params["n"]).denominator == 1 and F(params["N"]) >= F(params["n"]) > 0
        else:
            return "CONDITIONS_NOT_ESTABLISHED"
    except (ValueError, ZeroDivisionError, TypeError, OverflowError, KeyError):
        return "CONDITIONS_NOT_ESTABLISHED"
    return "FINITE_GUARD_PASSED" if valid else "CONDITIONS_NOT_ESTABLISHED"

def guarded_fixture_pairs():
    return {
       "point_continuity": ({"limit":"4", "value":"4", "defined":True}, {"limit":"0", "value":"1", "defined":True}),
       "matrix_inverse": ({"a":2,"b":0,"c":0,"d":3}, {"a":1,"b":2,"c":2,"d":4}),
       "density_singleton": ({"distribution":"ABSOLUTELY_CONTINUOUS"}, {"distribution":"DISCRETE"}),
       "fraction": ({"num":1,"den":2}, {"num":1,"den":0}),
       "helix": ({"radius":1,"pitch":2}, {"radius":1,"pitch":0}),
       "projectile": ({"g":10,"vy":4,"t":"2/5"}, {"g":10,"vy":4,"t":1}),
       "robot_joint": ({"l1":2,"l2":1,"theta2_is_relative":True}, {"l1":2,"l2":1,"theta2_is_relative":False}),
       "stratified_sample": ({"N":60,"n":6}, {"N":60,"n":0}),
    }

def rejected_bad_conditions():
    pairs=guarded_fixture_pairs()
    for op,(good,bad) in pairs.items():
        if guarded_premise(op,good)!="FINITE_GUARD_PASSED":
            raise AssertionError(f"Valid finite premise unexpectedly rejected: {op}")
        if guarded_premise(op,bad)!="CONDITIONS_NOT_ESTABLISHED":
            raise AssertionError(f"Invalid premise unexpectedly accepted: {op}")
    return tuple(pairs)
