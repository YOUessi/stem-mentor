"""Two independently recomputed finite numerical examples per Batch35 manuscript.

This checks ARITHMETIC of designated examples, NOT causal/historical conclusions,
not universal proof validity and not free-form student reasoning.
"""
from __future__ import annotations
from fractions import Fraction as F
from sympy import Matrix, symbols, integrate, Abs, Rational, limit, oo, simplify, sin, pi, cos, log, exp

def key(track,page,serial):
    return f"KB33-{track}-P{page}-A{serial:03d}"

def finite_evidence():
    x=symbols("x",real=True)
    records={}
    def add(track,page,serial,a,b,rationale):
        ident=key(track,page,serial)
        if type(a)!=bool or type(b)!=bool or not (a and b):
            raise AssertionError(f"Finite example failed {ident}: {a} {b}")
        if ident in records:raise AssertionError("duplicate finite case")
        records[ident]=dict(finite_examples=2,
            status="EXACT_BOUNDED_NUMERIC_CASES_ONLY",
            tested_scope=rationale,
            universal_theorem_certified=False,
            teacher_approved=False,student_step_verified=False,
            causal_historical_or_empirical_interpretation_verified=False)
    add("A","054",1,integrate(x,(x,0,2))==2,integrate(Abs(x),(x,-1,1))==1,
        "指定多项式有向积分和绝对面积，不验证任意黎曼可积函数。")
    n=Matrix([1,1,0]);v=Matrix([1,-1,0])
    add("A","055",4,n.dot(v)==0 and n!=Matrix.zeros(3,1),
        Matrix([0,0,1]).dot(Matrix([1,0,0]))==0,
        "两个特定非零法向量的内积；平面包含需另作位置判断。")
    add("A","056",2,F(2)*F(1,4)==F(1,2),
        integrate(Rational(1,2),(x,2,2))==0,
        "两个均匀密度的区间和单点算术，不能认定混合分布无原子。")
    vals=[-1,0,1];eX=sum(vals,F(0))/3;eY=sum((q*q for q in vals),F(0))/3
    eXY=sum((q*q*q for q in vals),F(0))/3
    add("A","056",3,F(1,4)-F(1,2)*F(1,2)==0,
        eXY-eX*eY==0 and eY==F(2,3),
        "独立公平币和零协方差非独立构造的有限矩。")
    add("A","056",4,F(1,6-2)==F(1,4),
        F(4)>0 and 2*2==4,"正值尺度和指定均匀密度归一化。")
    add("A","057",1,F(1,2)*F(1,2)>F(1,3)*F(2,3),
        F(1,2**2)>F(1,3**2),
        "指定两组Bernoulli/Uniform似然大小，不验证全局一般MLE推导。")
    X=Matrix([[1,0],[0,1]]);Y=Matrix([[1,1],[2,2]])
    add("A","057",4,X.rank()==2 and X.inv()*Matrix([2,3])==Matrix([2,3]),
        Y.rank()==1 and (Y.T*Y).det()==0,
        "2×2满秩和共线设计矩阵的精确秩。")
    add("B","058",1,limit(x*x,x,0)==0,
        limit(1/x,x,0,dir="+")==oo and limit(1/x,x,0,dir="-")==-oo,
        "指定函数的点极限与左右发散，函数点赋值独立。")
    a=Matrix([1,0,0]);b=Matrix([0,1,0])
    add("B","060",1,a.cross(b)==Matrix([0,0,1]),
        Matrix([1,2,0]).cross(Matrix([2,4,0]))==Matrix.zeros(3,1),
        "三维基向量叉积及平行退化。")
    add("B","061",2,F(1,4)==F(1,2)*F(1,2),
        F(1,2)-F(1,2)*F(1,2)==F(1,4),
        "公平独立与完全相关0/1变量两个实例。")
    add("B","061",3,F(11-10,1)/(F(2)/2)==1,
        (5-1)==4,"特定已知标准差的z值与样本量自由度的算术。")
    add("B","061",4,abs(1-0)<abs(1-10),abs(8-10)<abs(8-0),
        "一维两个最近中心分组算术，不能认证真实标签。")
    add("B","062",1,F((3-1)*4,4)==2,
        F((2-1)*2,2)==1,"指定样本方差和零假设方差的统计量值；非检验有效性。")
    add("B","062",4,(80-70)==10,(78-72)==6,
        "两组平均差仅为算术，完全不认证实验设计或因果识别。")
    add("B","063",1,3*4==12,F(5,1)==F(5,1),
        "线性预测差和量纲系数的指定算术。")
    add("B","063",2,Matrix([[2,0],[0,3]])*Matrix([1,1])==Matrix([2,3]),
        Matrix([[0,-1],[1,0]])*Matrix([1,0])==Matrix([0,1]),
        "两个指定二维线性变换。")
    add("B","063",4,F(100)*F(11,10)**2==121,
        F(80)*F(3,4)**2==45,
        "固定离散增长率两步实例，不证现实适用性。")
    t=symbols("t",real=True)
    add("B","064",1,simplify(sin(pi*(t+2))-sin(pi*t))==0,
        simplify(cos(2*pi*(t+5)/5)-cos(2*pi*t/5))==0,
        "指定三角模型的两个周期恒等式；非最小周期一般判据。")
    add("C","066",2,F(1200,12)+F(1200,100)==112,
        F(210)-F(121-F(210,10))==110,
        "两张指定等额本金/本息现金流的首期余额算术。")
    add("C","066",3,F(6)/(1-F(1,3))==9,
        Matrix([[Rational(3,4),0],[0,Rational(1,2)]]).inv()*Matrix([3,2])==Matrix([4,4]),
        "给定正需求的一个单部门、一个双部门投入产出例子。")
    add("C","067",3,F(1,2)==F(1)/(1+F(1)),
        simplify(1/(1+exp(-log(3)))-Rational(3,4))==0,
        "固定logit值0与ln3的模型概率；不认证个人分类。")
    skewed=[1,1,1,100]
    add("C","068",3,F(2+3,2)==F(5,2),
        F(sum(skewed),len(skewed))==F(103,4) and F(skewed[1]+skewed[2],2)==1 and F(103,4)!=1,
        "精确比较有序数据中位数与异常值拉动的均值，不代表类别量表具数值意义。")
    add("C","069",1,F(60,100)==F(3,5),
        F(45,60)==F(3,4),
        "两种分母的响应比例；不验证调查覆盖代表性。")
    add("D","069",2,(((-2)**2)==2**2),
        ((-2)**3)!=2**3,
        "x²偶性与x³非偶性两个取值；全称对称还需解析证明。")
    add("D","071",3,100*3==300,F(1,2*2)==F(1,2)*F(1,2),
        "理想谐波指定频率与倍增弦长倒数关系，非实测声学。")
    add("D","072",2,all(simplify(sin(2*pi*5*k/4)-sin(2*pi*k/4))==0 for k in range(-10,11)),
        all(simplify(sin(pi*k))==0 for k in range(-10,11)),
        "对有限整数采样格核验混叠构造；无连续信号重建认证。")
    reflect=Matrix([[1,0],[0,-1]])
    half_turn=Matrix([[-1,0],[0,-1]])
    add("D","072",3,
        reflect*Matrix([2,0])==Matrix([2,0]) and reflect*Matrix([2,3])!=Matrix([2,3]),
        half_turn*Matrix([0,0])==Matrix([0,0]) and half_turn*Matrix([2,0])!=Matrix([2,0]),
        "精确反射矩阵与半周旋转的固定/非固定点；不能由个别固定点认证整个图样对称。")
    add("D","072",4,F(10,5)==2,
        F(3,2)!=F(1+5**0,1),
        "矩形指定比例算术；无法检验创作者历史动机。")
    add("D","073",3,80-70==10,78-72==6,
        "两组描述性均差，绝对不认证干预因果效应。")
    if len(records)!=29:raise AssertionError(f"Expected 29 finite topic arithmetic checks, got {len(records)}")
    return records

def guard(op:str, value:object)->str:
    """Closed, typed input checks. Never attempts to parse arbitrary expressions."""
    try:
        supported={"fraction","normal_variance","time_growth","loan","sampling","regression","geometry","study","density","harmonics","io","angle"}
        if op not in supported:
            return "CONDITIONS_NOT_ESTABLISHED"
        if not isinstance(value,dict) or set(value)!=set({
            "fraction":["numerator","denominator"],"normal_variance":["variance"],
            "time_growth":["initial","factor","steps"],"loan":["principal","periods","rate_percent"],
            "sampling":["rate","max_frequency"],"regression":["n","p","rank"],
            "geometry":["nx","ny","nz"],"study":["design"],
            "density":["a","b"],"harmonics":["fixed_ends","linear_model"],
            "io":["coefficient","demand"],"angle":["angle_degrees"]
        }.get(op,[])):
            return "CONDITIONS_NOT_ESTABLISHED"
        if op=="study": valid=type(value["design"]) is str and value["design"]=="RANDOM_ASSIGNED"
        elif op=="harmonics": valid=type(value["fixed_ends"]) is bool and value["fixed_ends"] and type(value["linear_model"]) is bool and value["linear_model"]
        else:
            valid=all(type(x) is int and abs(x)<=10000 for x in value.values())
            if not valid:return "CONDITIONS_NOT_ESTABLISHED"
            if op=="fraction":valid=value["denominator"]!=0
            elif op=="normal_variance":valid=value["variance"]>0
            elif op=="time_growth":valid=value["initial"]>=0 and value["factor"]>=0 and 0<=value["steps"]<=100
            elif op=="loan":valid=value["principal"]>0 and 1<=value["periods"]<=100 and value["rate_percent"]>=0
            elif op=="sampling":valid=0<=2*value["max_frequency"]<value["rate"]
            elif op=="regression":valid=1<=value["p"]<=value["n"]<=100 and value["rank"]==value["p"]
            elif op=="geometry":valid=any(value[k]!=0 for k in ("nx","ny","nz"))
            elif op=="density":valid=value["a"]<value["b"]
            elif op=="io":valid=0<=value["coefficient"]<100 and value["demand"]>=0
            elif op=="angle":valid=0<value["angle_degrees"]<360
        return "FINITE_PREMISE_GUARDED" if valid else "CONDITIONS_NOT_ESTABLISHED"
    except (TypeError,ValueError,KeyError,OverflowError):
        return "CONDITIONS_NOT_ESTABLISHED"

def guard_pairs():
    return {
        "fraction":({"numerator":1,"denominator":2},{"numerator":1,"denominator":0}),
        "normal_variance":({"variance":4},{"variance":-1}),
        "time_growth":({"initial":100,"factor":2,"steps":4},{"initial":100,"factor":-1,"steps":4}),
        "loan":({"principal":1200,"periods":12,"rate_percent":1},{"principal":1200,"periods":0,"rate_percent":1}),
        "sampling":({"rate":8,"max_frequency":3},{"rate":8,"max_frequency":5}),
        "regression":({"n":5,"p":2,"rank":2},{"n":5,"p":2,"rank":1}),
        "geometry":({"nx":1,"ny":0,"nz":0},{"nx":0,"ny":0,"nz":0}),
        "study":({"design":"RANDOM_ASSIGNED"},{"design":"OBSERVATIONAL"}),
        "density":({"a":1,"b":3},{"a":3,"b":1}),
        "harmonics":({"fixed_ends":True,"linear_model":True},{"fixed_ends":False,"linear_model":True}),
        "io":({"coefficient":30,"demand":6},{"coefficient":100,"demand":6}),
        "angle":({"angle_degrees":180},{"angle_degrees":0}),
    }
