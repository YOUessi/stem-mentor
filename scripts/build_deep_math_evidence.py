#!/usr/bin/env python3
"""Freeze author-created K07 subclaims and explicit invalid-condition examples.

DO NOT label any output a complete theorem proof or teacher reviewed.
This script generates the versioned data file; mathematical assertions are
validated separately by backend/app/deep_math_evidence.py and pytest.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROWS = []


def add(key, lesson, kind, lhs, rhs, explanation, nonzero=(), values=None,
        relation="eq", variable=None, scope=None):
    if scope is None:
        scope = ("FINITE_WITNESS" if kind == "counterexample"
                 else "SUPPORTING_TRIG" if ("sin(" in lhs + rhs or "cos(" in lhs + rhs)
                 else "SUPPORTING_ALGEBRA")
    status = {"identity": "IDENTITY_ON_DECLARED_DOMAIN",
              "derivative": "DERIVATIVE_IDENTITY",
              "counterexample": "VALID_COUNTEREXAMPLE",
              "domain_gap": "DOMAIN_NOT_ESTABLISHED"}[kind]
    ROWS.append(dict(
        id="ev." + key, lesson_id="math.hs." + lesson, kind=kind,
        lhs=lhs, rhs=rhs, nonzero=list(nonzero), assignments=values or {},
        relation=relation, differentiate_by=variable,
        expected_status=status, explanation=explanation, proof_scope=scope,
        provenance="PROJECT_AUTHORED", review_status="REVIEW_PENDING"
    ))


# Standard algebraic transformations; equality here is an *algebraic subclaim*.
add("square-sum", "quadratic.sign", "identity",
    "(x+y)**2", "x**2+2*x*y+y**2",
    "直接展开平方的交叉项；不能误认为平方和没有二倍乘积项。")
add("square-diff", "quadratic.sign", "identity",
    "(x-y)**2", "x**2-2*x*y+y**2",
    "负号作用于交叉项，不能把最后的 y 平方项直接写成负数。")
add("difference-squares", "quadratic.sign", "identity",
    "(x-y)*(x+y)", "x**2-y**2",
    "平方差分解是整式恒等关系，不要求除以 x-y。")
add("quadratic-factor", "quadratic.sign", "identity",
    "(x-2)*(x-3)", "x**2-5*x+6",
    "二次因式展开验证候选根与多项式系数的一致性。")
add("quadratic-square", "function.quadratic-vertex", "identity",
    "x**2-4*x+3", "(x-2)**2-1",
    "配方保持原二次函数值不变；顶点结论仍需另查系数符号。")
add("vertex-parametric", "function.quadratic-vertex", "identity",
    "a*x**2+b*x+c", "a*(x+b/(2*a))**2+(4*a*c-b**2)/(4*a)",
    "一般二次函数配方中须先保证首项系数 a 不为零。", nonzero=["a"])
add("rational-cancel", "function.domain", "identity",
    "(x**2-1)/(x-1)", "x+1",
    "因式抵消只在分母 x-1 非零的定义域内成立；x=1 为缺口。", nonzero=["x-1"])
add("rational-cubic", "function.domain", "identity",
    "(x**3-1)/(x-1)", "x**2+x+1",
    "三次幂差展开和约分都不改变原分式在 x=1 处无定义的事实。", nonzero=["x-1"])
add("unit-cancellation", "function.domain", "identity",
    "x/x", "1",
    "即使化简结果常数为一，原分式在 x=0 处仍然无定义。", nonzero=["x"])
add("cancellation-parameter", "inequality.sign-multiplication", "identity",
    "(a*b)/b", "a",
    "约去参数 b 必须明确 b 不等于零，不能从一般参数自动推断。", nonzero=["b"])
add("fraction-add", "probability.conditioning", "identity",
    "1/x+1/y", "(x+y)/(x*y)",
    "分母的非零义务来自原式与结果；这里只证明算术变形，不证明条件概率公式。", nonzero=["x", "y"])
add("reciprocal-product", "function.domain", "identity",
    "1/(x*y)*(x*y)", "1",
    "合并后的常数一掩盖了 x 或 y 为零时原表达式未定义。", nonzero=["x*y"])
add("difference-quotient", "function.domain", "identity",
    "(a**2-b**2)/(a-b)", "a+b",
    "平方差商在 a=b 的点没有定义；因式消去不允许补全原定义域。", nonzero=["a-b"])
add("geometric-finite-four", "sequence.geometric-sum", "identity",
    "(1-q)*(1+q+q**2+q**3)", "1-q**4",
    "等比前四项错位相减的核心抵消恒等式，对所有实数公比均有效。")
add("geometric-finite-six", "sequence.geometric-sum", "identity",
    "(1-q)*(1+q+q**2+q**3+q**4+q**5)", "1-q**6",
    "等比前六项错位相减证明的是乘法恒等式，而除法还需要排除 q=1。")
add("geometric-ratio-four", "sequence.geometric-sum", "identity",
    "1+q+q**2+q**3", "(1-q**4)/(1-q)",
    "等比前四项的除法表达式仅在 q 不等于一时合法。", nonzero=["1-q"])
add("geometric-ratio-six", "sequence.geometric-sum", "identity",
    "1+q+q**2+q**3+q**4+q**5", "(1-q**6)/(1-q)",
    "等比前六项的有限和不能将 q=1 直接代入分式公式。", nonzero=["1-q"])
add("arithmetic-four", "sequence.arithmetic-sum", "identity",
    "a+(a+d)+(a+2*d)+(a+3*d)", "4*a+6*d",
    "四项等差数列直接加和，应与首尾配对后的公式相同。")
add("arithmetic-six", "sequence.arithmetic-sum", "identity",
    "a+(a+d)+(a+2*d)+(a+3*d)+(a+4*d)+(a+5*d)", "3*(2*a+5*d)",
    "六项求和等于三组首尾等值和；验证定长实例而非全部 n 的形式证明。")
add("nonnegative-square", "inequality.amgm", "identity",
    "a**2+b**2-2*a*b", "(a-b)**2",
    "平方非负是二元不等式的代数核心，但并未独立证明开方所需非负条件。")
add("binomial-cube", "counting.binomial", "identity",
    "(a+b)**3", "a**3+3*a**2*b+3*a*b**2+b**3",
    "三次二项式系数可按展开核对；只检查固定指数三。")
add("binomial-four", "counting.binomial", "identity",
    "(a+b)**4", "a**4+4*a**3*b+6*a**2*b**2+4*a*b**3+b**4",
    "四次二项式展开验证组合系数；固定四次不等于一般 n 的定理证明。")
add("binomial-five", "counting.binomial", "identity",
    "(a+b)**5", "a**5+5*a**4*b+10*a**3*b**2+10*a**2*b**3+5*a*b**4+b**5",
    "五次二项展开系数符合对称规律，仍需要归纳或组合证明全部整数 n。")
add("trig-pythagorean", "trig.pythagorean", "identity",
    "sin(x)**2+cos(x)**2", "1",
    "三角基本恒等式经符号化简核对，符号计算并非对单位圆几何推导的审校。")
add("sine-add", "trig.sum-angle", "identity",
    "sin(x+y)", "sin(x)*cos(y)+cos(x)*sin(y)",
    "核对正弦和角公式在实数自变量上的恒等性，保留原几何证明待教师核查。")
add("cosine-add", "trig.sum-angle", "identity",
    "cos(x+y)", "cos(x)*cos(y)-sin(x)*sin(y)",
    "余弦和角公式中交叉项为负，注意不能照搬正弦公式符号。")
add("sine-sub", "trig.sum-angle", "identity",
    "sin(x-y)", "sin(x)*cos(y)-cos(x)*sin(y)",
    "减角公式由和角公式替换负角得到，符号需保持一致。")
add("cosine-sub", "trig.sum-angle", "identity",
    "cos(x-y)", "cos(x)*cos(y)+sin(x)*sin(y)",
    "余弦减角公式的交叉项为加号，核对时需要区分正负角。")

# Differentiation of finite forms only. Not a proof of the general derivative rule.
add("differentiate-cubic", "calculus.power-rule", "derivative",
    "x**3", "3*x**2",
    "固定三次幂的导数由 SymPy 核对；不代表一般整数指数定理已经审核。",
    variable="x")
add("differentiate-fifth", "calculus.power-rule", "derivative",
    "x**5", "5*x**4",
    "固定五次幂的导数用于检测漏掉幂系数的典型错误。",
    variable="x")
add("differentiate-polynomial", "calculus.power-rule", "derivative",
    "x**2+3*x+2", "2*x+3",
    "逐项微分核对二次多项式导数，不能自动延伸到任意复合函数。",
    variable="x")
add("differentiate-sine", "calculus.power-rule", "derivative",
    "sin(x)", "cos(x)",
    "验证基础正弦导数的一个具体恒等式，不意味着相关极限证明已完成。",
    variable="x")
add("differentiate-cosine", "calculus.power-rule", "derivative",
    "cos(x)", "-sin(x)",
    "验证余弦导数负号，防止模型把余弦导数误记为正弦。",
    variable="x")

# Finite, exact witnesses to common false claims; each is deliberately invalid.
add("wrong-square-sum", "quadratic.sign", "counterexample",
    "(x+y)**2", "x**2+y**2",
    "x=y=1 给出左侧四、右侧二，说明不能遗漏二倍乘积项。",
    values={"x":"1","y":"1"})
add("wrong-square-diff", "quadratic.sign", "counterexample",
    "(x-y)**2", "x**2-y**2",
    "x=3,y=2 时左右分别为一和五，暴露错误的平方差混淆。",
    values={"x":"3","y":"2"})
add("wrong-square-monotonicity", "function.monotonicity", "counterexample",
    "x**2", "y**2",
    "x=-3 小于 y=-2，但平方后九大于四，不能据自变量递增判断平方函数全域递增。",
    values={"x":"-3","y":"-2"}, relation="le")
add("wrong-ratio-symmetry", "function.domain", "counterexample",
    "x/y", "y/x",
    "x=2,y=3 两侧分别为三分之二和二分之三，不可随意交换分子分母。",
    nonzero=["x","y"], values={"x":"2","y":"3"})
add("wrong-reciprocal-sum", "probability.conditioning", "counterexample",
    "1/(x+y)", "1/x+1/y",
    "x=2,y=3 时五分之一不等于六分之五；分母相加不是分数相加。",
    nonzero=["x","y","x+y"], values={"x":"2","y":"3"})
add("wrong-idempotence", "logic.implication", "counterexample",
    "x**2", "x",
    "x=-1 时平方等于一而原数为负一，不能把平方运算与恒等运算混同。",
    values={"x":"-1"})
add("wrong-product-positive", "inequality.sign-multiplication", "counterexample",
    "a*b", "0",
    "a=-2,b=3 时乘积为负，乘法保号要严格检查参数与因子的符号。",
    values={"a":"-2","b":"3"}, relation="ge")
add("wrong-square-subadd", "inequality.amgm", "counterexample",
    "(a+b)**2", "a**2+b**2",
    "a=1,b=-3 时左边为四、右边为十，没有非负假设就不能断言平方和大小方向。",
    values={"a":"1","b":"-3"}, relation="ge")
add("wrong-sign-multiply", "inequality.sign-multiplication", "counterexample",
    "a*x", "a*y",
    "虽然 x=1<y=3，但 a=-2 时乘以负数使不等号反向，得到负二大于负六。",
    values={"a":"-2","x":"1","y":"3"}, relation="le")
add("wrong-binomial-square", "counting.binomial", "counterexample",
    "(a+b)**2", "a**2+b**2",
    "a=b=2 时左侧十六而右侧八，二项式定理必须保留中间项。",
    values={"a":"2","b":"2"})

# Guard omission must be rejected even if SymPy simplifies to a tautology.
add("missing-cancel-domain", "function.domain", "domain_gap",
    "(x**2-1)/(x-1)", "x+1",
    "即使分式可约分，x=1 仍不在原始表达式定义域之中。")
add("missing-x-divisor", "function.domain", "domain_gap",
    "x/x", "1",
    "没有显式声明 x 非零，就不能对 x/x=1 给出无条件恒等判断。")
add("missing-y-divisor", "probability.conditioning", "domain_gap",
    "1/x+1/y", "(x+y)/(x*y)",
    "仅声明 x 非零，不足以保证包含 y 的倒数表达式有定义。",nonzero=["x"])
add("missing-vertex-a", "function.quadratic-vertex", "domain_gap",
    "a*x**2+b*x+c", "a*(x+b/(2*a))**2+(4*a*c-b**2)/(4*a)",
    "二次配方分式含 a 作为分母，必须排除 a=0 的退化一次函数。")
add("missing-sum-q-one", "sequence.geometric-sum", "domain_gap",
    "1+q+q**2+q**3", "(1-q**4)/(1-q)",
    "未排除 q=1 就使用有分母的求和公式，会将合法退化情形误作未定义。")


def main():
    path = ROOT / "knowledge/deep/math_evidence_v1.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ROWS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}: {len(ROWS)} claims; {len(set(r['lesson_id'] for r in ROWS))} lessons")


if __name__ == "__main__":
    main()
