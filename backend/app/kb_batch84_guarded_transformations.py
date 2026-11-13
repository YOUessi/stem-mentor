"""Teacher-only exact integer counterexamples to ten unsafe algebraic inferences.

Each record is an original review pending teaching note. Counterexample checks
do NOT certify general theorems, student explanations, or teacher review.
No float, bool, symbolic string evaluation, or user-provided arbitrary code.
"""
from __future__ import annotations
from fractions import Fraction as F

# Every card records the mathematical claim *actually being challenged*, the
# failed premise and a repair. Worked examples, hints and near/far transfers
# must remain teacher-side while approval is pending.
CARDS = (
    {"id":"KB84-T01","op":"square_equation_reverse",
     "topic":"平方方程的增根","claim":"由 x²=t² 可以直接认定 x=t",
     "assumptions":"实数中平方只确定绝对值；反推同号解需补充符号条件。",
     "steps":["先检验候选根能否满足平方后的方程。","因 x²=t² 等价于 x=t 或 x=-t，分别检查原式。","把未满足原式的候选根标为增根，不可删去核验步骤。"],
     "worked_example":"方程 x=2 两边平方得到 x²=4；后者的 -2 并非原方程的根。",
     "failure":"从平方后方程逆推原方程时漏掉符号分支。",
     "hints":["平方可能丢失哪类信息？","比较 x 与 -x 的平方。","分别代回平方前的方程判断。"],
     "near":"解 sqrt(x+1)=x-1 时检查右侧非负。",
     "far":"由向量模相等能否认定两个向量相同？",
     "payload":{"x":-2,"t":2}},
    {"id":"KB84-T02","op":"zero_factor_cancellation",
     "topic":"等式约去可能为零的公因子","claim":"ak=bk 必然推出 a=b",
     "assumptions":"在域中 k≠0 才允许同时除以 k。",
     "steps":["把等式写成 (a-b)k=0。","由零因子性质得到 a=b 或 k=0。","消去 k 前必须确认它不是零。"],
     "worked_example":"2·0=7·0 成立，而 2≠7。",
     "failure":"把可能为零的量作为分母。",
     "hints":["等式两端有哪些因子？","若公因子取零会怎样？","先拆分零因子分支再约分。"],
     "near":"解 x(x-1)=0 时不要消去 x。",
     "far":"参数矩阵有零特征值时消去矩阵是否合法？",
     "payload":{"a":2,"b":7,"k":0}},
    {"id":"KB84-T03","op":"multiply_order_negative",
     "topic":"不等式乘以负数方向翻转","claim":"a<b 时任意乘 k 后仍有 ak<bk",
     "assumptions":"乘数 k>0 时方向保持；k<0 时方向翻转；k=0 时变成相等。",
     "steps":["确认 a<b 在实数有序域成立。","分 k>0、k<0、k=0 三种情况。","将所用乘数符号写在转换旁。"],
     "worked_example":"1<2，却有 -3>-6。",
     "failure":"负乘数下保持原方向。",
     "hints":["乘数的符号是否已知？","在数轴上比较 -3 和 -6。","按正负零分情况整理。"],
     "near":"解 -2x<6 时翻转不等号。",
     "far":"参数 c 未知时乘 c 的不等式如何分类？",
     "payload":{"a":1,"b":2,"k":-3}},
    {"id":"KB84-T04","op":"reciprocal_direction_positive",
     "topic":"正数倒数次序反向","claim":"0<a<b 便有 1/a<1/b",
     "assumptions":"0<a<b 时 ab>0，倒数关系严格反向。",
     "steps":["先确认 a,b 为正且不为零。","比较倒数差 (1/a-1/b)=(b-a)/(ab)。","分子分母均正，因此倒数差大于零。"],
     "worked_example":"1<2 但 1>1/2。",
     "failure":"将正数区间的倒数函数误认成递增。",
     "hints":["倒数的分母是否可为零？","先算两个具体值。","考察倒数差的分子与分母符号。"],
     "near":"比较 1/3 与 1/5 的大小。",
     "far":"若 a,b 跨零，能否不分情况比较倒数？",
     "payload":{"a":1,"b":2}},
    {"id":"KB84-T05","op":"absolute_root",
     "topic":"主值平方根与绝对值","claim":"对任意实数 n，sqrt(n²)=n",
     "assumptions":"主平方根取非负值，所以 sqrt(n²)=|n|。",
     "steps":["按照平方根定义选择非负的主值。","令 n<0，比较 n 和 |n|。","仅在 n≥0 条件下把 |n| 写成 n。"],
     "worked_example":"n=-3 时 sqrt(9)=3，不是 -3。",
     "failure":"对负数误删绝对值符号。",
     "hints":["根号的结果能否为负？","试算 -3 的平方再开方。","用绝对值写出总是成立的式子。"],
     "near":"化简 sqrt((x-2)²) 时分区间。",
     "far":"用距离公式化简两点横坐标差的平方根。",
     "payload":{"n":-3}},
    {"id":"KB84-T06","op":"quadratic_formula_degenerate",
     "topic":"二次公式的首项系数前提","claim":"ax²+bx+c=0 对任意 a 都可套二次公式",
     "assumptions":"二次公式只适用于 a≠0；a=0 时先按一次方程或常数方程处理。",
     "steps":["检查最高次项系数 a 是否为零。","a=0,b≠0 时求唯一解 x=-c/b。","不要在 a=0 的分支使用分母 2a。"],
     "worked_example":"0x²+2x-4=0 的解为 x=2，但二次公式含分母0。",
     "failure":"忽略公式分母中的 2a≠0。",
     "hints":["所谓二次方程的首项条件是什么？","令 a=0 后还有几次？","先分次数再选择公式。"],
     "near":"解含参数 m 的 mx²+x-1=0。",
     "far":"二阶微分方程最高阶系数退化时仍是二阶吗？",
     "payload":{"a":0,"b":2,"c":-4}},
    {"id":"KB84-T07","op":"cramer_determinant_zero",
     "topic":"克拉默法则的非零行列式条件","claim":"行列式为零时仍可直接使用克拉默法则唯一求解",
     "assumptions":"唯一解的克拉默分式需要 det(A)≠0；det(A)=0 时另判秩与相容性。",
     "steps":["求系数矩阵行列式。","行列式零时拒绝用 det(A_i)/det(A) 求解。","分别检查是否无解或有无限多解。"],
     "worked_example":"x+2y=3 与 2x+4y=6 同一约束；(3,0)及(1,1)均为解。",
     "failure":"把秩亏损系统误当唯一解。",
     "hints":["分母行列式是否非零？","第二个方程和第一个有何关系？","给出两个不同满足方程的解。"],
     "near":"求解线性方程组 x+y=2,2x+2y=4。",
     "far":"最小二乘正规方程矩阵奇异时参数是否唯一？",
     "payload":{"a":1,"b":2,"c":2,"d":4,"e":3,"f":6}},
    {"id":"KB84-T08","op":"cross_multiplication_zero_denominator",
     "topic":"交叉相乘隐藏零分母","claim":"ad=bc 即能说明 a/b=c/d",
     "assumptions":"有理式交叉相乘的等价关系要求 b≠0 且 d≠0。",
     "steps":["先明确两个分式各自的定义域。","仅在 b,d 都不为零时相乘得到 ad=bc。","对被清除的分母再检查是否带来虚假的解。"],
     "worked_example":"a=0,b=0,c=1,d=1 时 ad=bc=0，但 a/b 无定义。",
     "failure":"把等价变形的定义域条件省掉。",
     "hints":["原分式是否都存在？","计算 b 和 d 的值。","先标定义域再交叉相乘。"],
     "near":"解 (x-1)/(x-1)=1 时注意 x=1。",
     "far":"在概率公式中消去概率分母能否容许零概率事件？",
     "payload":{"a":0,"b":0,"c":1,"d":1}},
    {"id":"KB84-T09","op":"conditional_probability_zero",
     "topic":"条件概率不能以零概率事件为条件",
     "claim":"P(A|B)=P(A∩B)/P(B) 在 P(B)=0 时仍有定义",
     "assumptions":"初等条件概率的比式需要 P(B)>0。",
     "steps":["先从样本空间计算条件事件的概率。","P(B)=0 时拒绝分母为零的条件概率定义。","需要更一般条件分布理论时不能套用初等离散比式。"],
     "worked_example":"等可能两点样本空间中令 B=空集，P(B)=0，无论 A 如何均不能用0/0。",
     "failure":"把 0/0 误解释为零概率或一概率。",
     "hints":["公式的分母是哪一个概率？","空事件概率是多少？","判定该条件概率是否按现有定义成立。"],
     "near":"在两次掷硬币中以不可能事件作条件。",
     "far":"连续随机变量的点条件分布为什么不能直接使用概率比式？",
     "payload":{"total":2,"event":0,"intersection":0}},
    {"id":"KB84-T10","op":"real_log_product",
     "topic":"实数对数积公式的正值前提","claim":"只要 xy>0 就可在实数内写 ln(xy)=ln x+ln y",
     "assumptions":"实数对数积公式要求 x>0 且 y>0，不能只检查 xy>0。",
     "steps":["先检验 ln(x)、ln(y) 分别在实数域有定义。","负负相乘使 xy>0 并不能让两个对数项存在。","仅在两因子各自为正时使用实数对数积公式。"],
     "worked_example":"x=y=-1 时 ln(xy)=ln(1)=0，而 ln(-1) 在实数域无定义。",
     "failure":"把乘积在定义域内误当各因子在定义域内。",
     "hints":["对数函数允许的真数范围是什么？","两个负数的积是否正？","分别检查公式两端每个子表达式。"],
     "near":"化简 ln((x-2)(x+2)) 时列出实数定义域。",
     "far":"实数与复数对数的分支条件能否混用？",
     "payload":{"x":-1,"y":-1}},
)
# A separate, legally guarded second example for every false-inference card.
# The first worked example is an exact failing counterexample; this one shows
# a valid use with stated conditions, not a teacher certification.
VALID_EXAMPLES = {
    "KB84-T01": "若 x,t 均非负且 x²=t²，则 |x|=|t|，所以 x=t；例如 x=t=2。",
    "KB84-T02": "若 k=3≠0 且 2k=2k，除以3得到2=2；先验证被消因子非零。",
    "KB84-T03": "当 a=1<b=2 且 k=3>0 时，乘法后3<6仍成立。",
    "KB84-T04": "对 a=2,b=5，0<a<b 且 ab>0；倒数差1/2−1/5=3/10>0。",
    "KB84-T05": "当 n=4≥0 时，主平方根 sqrt(4²)=4=|4|，可以去绝对值。",
    "KB84-T06": "a=1,b=-3,c=2 且判别式1≥0；二次公式得 x=(3±1)/2，即1或2。",
    "KB84-T07": "对可逆系数阵 A=diag(1,1)，det(A)=1≠0；方程 Ax=(2,3) 唯一解 x=(2,3)。",
    "KB84-T08": "a=1,b=2,c=2,d=4 且 b,d 均非零；交叉积4=4，因此1/2=2/4。",
    "KB84-T09": "若 P(B)=1/2>0 且 P(A∩B)=1/4，条件概率按定义为(1/4)/(1/2)=1/2。",
    "KB84-T10": "对 x=2>0,y=3>0，实数对数积公式合法：ln6=ln2+ln3。",
}

OPS = tuple(x["op"] for x in CARDS)
SCHEMAS = {
    "square_equation_reverse":{"x","t"},
    "zero_factor_cancellation":{"a","b","k"},
    "multiply_order_negative":{"a","b","k"},
    "reciprocal_direction_positive":{"a","b"},
    "absolute_root":{"n"},
    "quadratic_formula_degenerate":{"a","b","c"},
    "cramer_determinant_zero":{"a","b","c","d","e","f"},
    "cross_multiplication_zero_denominator":{"a","b","c","d"},
    "conditional_probability_zero":{"total","event","intersection"},
    "real_log_product":{"x","y"},
}
def check_case(op, payload):
    """A finite exact *counterexample*, never a universal proof certificate."""
    if op not in SCHEMAS or type(payload) is not dict or set(payload) != SCHEMAS[op]:
        raise ValueError("unknown exact case or payload schema")
    if any(type(v) is not int or abs(v) > 512 for v in payload.values()):
        raise ValueError("only small exact integers, not floats/bools/strings")
    p=payload
    if op=="square_equation_reverse":
        counter = p["x"]**2 == p["t"]**2 and p["x"] != p["t"]
        evidence={"squared":p["x"]**2,"candidate":p["x"],"claimed_target":p["t"]}
    elif op=="zero_factor_cancellation":
        counter = p["a"]*p["k"] == p["b"]*p["k"] and p["a"] != p["b"]
        evidence={"factor":p["k"],"left":p["a"]*p["k"],"right":p["b"]*p["k"]}
    elif op=="multiply_order_negative":
        counter = p["a"]<p["b"] and p["k"]<0 and p["a"]*p["k"]>p["b"]*p["k"]
        evidence={"a_times_k":p["a"]*p["k"],"b_times_k":p["b"]*p["k"]}
    elif op=="reciprocal_direction_positive":
        counter = 0<p["a"]<p["b"] and F(1,p["a"])>F(1,p["b"])
        evidence={"inverse_a":str(F(1,p["a"])) if p["a"] else None,
                  "inverse_b":str(F(1,p["b"])) if p["b"] else None}
    elif op=="absolute_root":
        counter = p["n"]<0 and abs(p["n"])!=p["n"]
        evidence={"n_squared":p["n"]**2,"nonnegative_sqrt":abs(p["n"])}
    elif op=="quadratic_formula_degenerate":
        counter = p["a"]==0 and p["b"]!=0
        evidence={"linear_root":str(F(-p["c"],p["b"])) if p["b"] else None,
                  "quadratic_formula_denominator":2*p["a"]}
    elif op=="cramer_determinant_zero":
        a,b,c,d,e,f=(p[k] for k in ("a","b","c","d","e","f"))
        det=a*d-b*c
        counter=det==0 and a!=0 and (c*e==a*f)
        evidence={"determinant":det,"consistent":counter,"unique":False if counter else None}
    elif op=="cross_multiplication_zero_denominator":
        a,b,c,d=(p[k] for k in ("a","b","c","d"))
        counter=(a*d==b*c) and (b==0 or d==0)
        evidence={"cross_left":a*d,"cross_right":b*c,"fractions_defined":b!=0 and d!=0}
    elif op=="conditional_probability_zero":
        n,event,intersection=(p[k] for k in ("total","event","intersection"))
        counter=n>0 and event==0 and intersection==0
        evidence={"event_mass":str(F(event,n)) if n else None,
                  "conditional_ratio_defined":False if counter else None}
    elif op=="real_log_product":
        counter=p["x"]<0 and p["y"]<0 and p["x"]*p["y"]>0
        evidence={"product":p["x"]*p["y"],
                  "real_log_x_defined":p["x"]>0,"real_log_y_defined":p["y"]>0}
    else:
        raise ValueError("unexpected operation")
    return {
        "status":"FINITE_EXACT_COUNTEREXAMPLE_ONLY" if counter else "CONDITIONS_NOT_ESTABLISHED",
        "operation":op,"evidence":evidence,"general_theorem_certified":False,
        "teacher_approved":False,"student_answer_verified":False,
    }

def verified_cards():
    assert len(CARDS)==10 and len({x["id"] for x in CARDS})==10
    for c in CARDS:
        assert c["op"] in OPS and len(c["steps"])>=3 and len(c["hints"])==3
        assert len(c["assumptions"])>12 and len(c["failure"])>=10
        assert len(c["near"])>8 and len(c["far"])>8
        assert len(VALID_EXAMPLES)==len(CARDS) and len(VALID_EXAMPLES[c["id"]])>25
        result=check_case(c["op"],c["payload"])
        assert result["status"]=="FINITE_EXACT_COUNTEREXAMPLE_ONLY",c["op"]
        yield {**c,**result, "valid_guarded_example":VALID_EXAMPLES[c["id"]],
               "review_state":"REVIEW_PENDING",
               "teacher_only":True,"student_authoritative_index_eligible":False,
               "source_license":"ORIGINAL_MATH_EXPLANATION"}
