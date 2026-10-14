"""Curated synthetic lesson content. Never imply support for arbitrary math solving."""
PROBLEMS = {
    "distance-ratio": {
        "id": "distance-ratio", "title": "两个定点与距离之比", "subject": "高中数学 · 平面解析几何",
        "prompt": "已知 A(0,0)、B(6,0)，动点 P 满足 PA=2PB。求 P 的轨迹。",
        "goal": "分析动点的轨迹类型并解释理由", "known": ["A、B 是两个不同的定点", "PA/PB=2", "P 是动点"],
        "method_tags": ["distance_ratio", "locus"],
        "structure_tags": ["two_fixed_points", "constant_distance_ratio", "locus"],
        "analysis": ["这道题在求一个数值，还是满足条件的一组点？", "哪些点固定、哪些量变化？在变化过程中什么量保持不变？", "如果比例变成 1，轨迹可能有什么不同？"],
        "guide": ["你目前得到什么距离关系？可以尝试设动点坐标。", "如果正向展开卡住，反过来想：你希望最终得到哪种轨迹方程？", "你能尝试整理并配方，同时检查比例为 1 时的退化情况吗？"],
        "micro_point_id": "distance-ratio-one"
    },
    "ellipse-tangent": {
        "id": "ellipse-tangent", "title": "椭圆上一点的切线", "subject": "高中数学 · 圆锥曲线",
        "prompt": "已知椭圆 x²/9+y²/4=1，点 P 在椭圆上。讨论如何求 P 处的切线方程。",
        "goal": "选择并解释切线求法，而非只记快捷公式", "known": ["曲线是二次方程", "切点 P 位于椭圆上"],
        "method_tags": ["conic_tangent", "implicit_derivative", "polarization"],
        "structure_tags": ["quadratic_curve", "point_on_curve", "tangent_at_point"],
        "analysis": ["本题给了切点，和没有给切点的切线题有什么区别？", "最终的切线应是什么次数的方程？现有曲线是什么次数？", "有没有方法利用切点而不把大量参数全部联立展开？"],
        "guide": ["你已有哪一种切线方法？它需要哪些条件？", "若判别式法计算冗长，可以从目标反推：切线需要满足什么局部性质？", "试着用隐式求导检查你的候选关系，再思考这个技巧的适用边界。"],
        "micro_point_id": "conic-point-valid"
    },
    "hyperbola-tangent": {
        "id": "hyperbola-tangent", "title": "双曲线上一点的切线", "subject": "高中数学 · 圆锥曲线",
        "prompt": "已知双曲线 x²/9−y²/4=1，点 P 在曲线上。讨论求 P 处切线的策略。",
        "goal": "由二次曲线的结构推导切线方法并与旧题比较", "known": ["切点在曲线上", "已知二次曲线方程"],
        "method_tags": ["conic_tangent", "implicit_derivative", "polarization"],
        "structure_tags": ["quadratic_curve", "point_on_curve", "tangent_at_point"],
        "analysis": ["题目给出的目标是否与此前某类曲线的切线问题具有共同结构？", "双曲线和椭圆的表达式有什么关键异同？", "如果借用旧方法，需要额外验证哪些条件？"],
        "guide": ["你首先会尝试哪一种求切线的方法？", "如果正向计算停滞，不妨从切线的定义或曲线的局部变化反推。", "先比较新旧二次式中的符号，再自己用求导验证是否可迁移。"],
        "micro_point_id": "conic-point-valid"
    },
    "ellipse-focus": {
        "id": "ellipse-focus", "title": "椭圆定义中的焦点距离", "subject": "高中数学 · 圆锥曲线",
        "prompt": "平面点 P 到 A(−3,0)、B(3,0) 的距离之和为 10，讨论 P 的轨迹及其存在条件。",
        "goal": "根据距离和理解椭圆轨迹和退化条件", "known": ["两个不同定点", "PA+PB=10"],
        "method_tags": ["ellipse_foci", "distance_sum"],
        "structure_tags": ["two_fixed_points", "fixed_distance_sum", "locus"],
        "analysis": ["这一次保持不变的是距离比还是距离和？", "两点间最短距离与题目给的距离和有什么关系？", "为何仅仅看到椭圆二字还不足以选择切线方法？"],
        "guide": ["先用三角不等式检查轨迹是否存在。", "从轨迹定义反推，需要满足什么距离和关系？", "你能解释距离和等于两个定点间距离时发生什么吗？"],
        "micro_point_id": "ellipse-distance-sum"
    },
    "inequality-bridge": {
        "id": "inequality-bridge", "title": "不等式中的正推与反推", "subject": "高中数学 · 不等式",
        "prompt": "已知 x,y>0 且 x+y=1，证明 1/x+1/y≥4。",
        "goal": "从正向化简到逆向设定中间目标", "known": ["x,y 为正数", "x+y=1", "目标是不等式"],
        "method_tags": ["am_gm", "backward_goal", "product_bound"],
        "structure_tags": ["positive_two_variables", "fixed_sum", "bound_reciprocal_sum"],
        "analysis": ["你觉得本题需要计算精确值，还是证明所有取值下的下界？", "你能分别找出已知条件和目标包含哪些量？", "如果先把左边合成一个分式，会发现什么？"],
        "guide": ["你从 x+y=1 能得到怎样的表达式？", "如果左边化成 1/(xy) 后卡住，从结论反推需要 xy 满足什么上界？", "你能用已知的和来控制乘积，并自行完成最后运算吗？"],
        "micro_point_id": "positive-conditions"
    },
    "geometric-sum": {
        "id": "geometric-sum", "title": "等比数列求和的特殊情况", "subject": "高中数学 · 数列",
        "prompt": "首项为 a₁、公比为 q 的等比数列，求前 n 项和，并说明需要分情况的原因。",
        "goal": "理解求和公式分母及 q=1 的情况", "known": ["n 是正整数", "数列是等比数列"],
        "method_tags": ["geometric_series", "case_split"],
        "structure_tags": ["geometric_sequence", "sum_n_terms", "special_case"],
        "analysis": ["什么情况下求和公式中的分母可能为零？", "你能先明确公式的适用范围，而不是直接代入吗？", "特殊情况是否能用定义直接求和？"],
        "guide": ["试着使用错位相减法，但先看要除的量是什么。", "如果公比等于 1，是否还能合法除以 1−q？", "用最原始的数列求和定义检查特殊情况。"],
        "micro_point_id": "geometric-q-one"
    }
}
METHODS = [
    {"id": "distance_ratio", "name": "阿波罗尼斯圆", "description": "两固定点到动点的距离之比为固定正数", "trigger": "两个定点 + 定距离比", "boundary": "比值为 1 时是垂直平分线而非圆"},
    {"id": "conic_tangent", "name": "二次曲线切线的局部分析", "description": "切点、隐式求导、二次式极化", "trigger": "已知二次曲线上的非奇异点", "boundary": "不能对曲线外点或奇异点直接套切线公式"},
    {"id": "backward_goal", "name": "从目标逆向寻找桥梁", "description": "由欲证结论拆出可以连接已知的中间目标", "trigger": "正推表达式与结论距离较远", "boundary": "逆推得到必要条件不自动等价于证明"},
    {"id": "case_split", "name": "特殊情况分类讨论", "description": "公式除法、边界或退化情形需单独验证", "trigger": "运算含可能为零的除数", "boundary": "不遗漏端点和定义域限制"}
]
MICRO_POINTS = {
    "geometric-q-one": {"id": "geometric-q-one", "title": "等比数列 q=1", "topic": "geometric_series", "question": "等比数列求前 n 项和时，为什么必须单独讨论 q=1？这时前 n 项和是什么？", "answer_hint": "公比为 1 时各项都相等，Sₙ=n·a₁。", "acceptable": ["na1", "n*a1", "n·a1", "n a1", "n倍首项", "n倍的首项", "n个a1"]},
    "distance-ratio-one": {"id": "distance-ratio-one", "title": "距离比等于 1 的退化", "topic": "distance_ratio", "question": "两个不同定点 A、B，满足 PA/PB=1 的点 P 的轨迹是什么？", "answer_hint": "垂直平分线，而不是阿波罗尼斯圆。", "acceptable": ["垂直平分线"]},
    "conic-point-valid": {"id": "conic-point-valid", "title": "曲线切点的合法条件", "topic": "conic_tangent", "question": "求某点处二次曲线的普通切线前，需要先核对这个点满足哪些基本条件？", "answer_hint": "该点在曲线上，并且是非奇异点。", "acceptable": ["非奇异", "曲线上且不是奇异", "在曲线上且梯度不为零"]},
    "ellipse-distance-sum": {"id": "ellipse-distance-sum", "title": "距离和轨迹的存在条件", "topic": "ellipse_foci", "question": "与两定点的距离之和小于两定点间距离时，是否存在这样的动点？为什么？", "answer_hint": "由三角不等式，不可能存在这样的动点。", "acceptable": ["不存在", "不可能"]},
    "positive-conditions": {"id": "positive-conditions", "title": "正数条件不能丢", "topic": "am_gm", "question": "用 xy>0 将 1/(xy)≥4 改写为 xy≤1/4 时，为什么要核对 xy 的符号？", "answer_hint": "乘除不等式时，负数会使方向反转，零不可作分母。", "acceptable": ["方向", "负数", "不等号"]}
}

def public_problem(problem):
    return {k:problem[k] for k in ("id","title","subject","prompt","goal","known")}
