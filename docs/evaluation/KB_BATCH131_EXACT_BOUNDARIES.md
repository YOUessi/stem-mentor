# Batch131 — 16 exact positive + 16 exact invalid boundary witnesses

These independently recomputed finite witnesses are NOT universal proofs or approval of student work.

## cone_cylinder
Valid-condition witness: 圆锥半径2高3且高度为正
Invalid or degenerate boundary: 混同圆锥与同底同高圆柱体积
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## two_event_union
Valid-condition witness: 共同概率空间内交集概率为3/10
Invalid or degenerate boundary: 忘记交集导致并集概率超过1
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## variance_denominator
Valid-condition witness: 样本为(1,3)且n=2
Invalid or degenerate boundary: 将描述方差与n−1无偏样本方差混用
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## vertical_line
Valid-condition witness: 过(2,0)与(2,3)的直线为x=2
Invalid or degenerate boundary: 竖直直线不能表示为有限斜率函数
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## circle_tangent
Valid-condition witness: 圆x²+y²=25和直线y=5
Invalid or degenerate boundary: 无效直线系数全零会令距离分母为零
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## ellipse_focal_sum
Valid-condition witness: a=5,c=3,b=4,椭圆右顶点(5,0)
Invalid or degenerate boundary: 距离和等于焦距时不是非退化椭圆
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## binomial_three_trials
Valid-condition witness: 三个独立成功率1/2伯努利试验
Invalid or degenerate boundary: 不放回抽球不能自动假定联合独立
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## hypergeometric_impossible
Valid-condition witness: N=5,K=1,n=2无放回
Invalid or degenerate boundary: 不可能抽出两个成功对象
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## normal_std_zero
Valid-condition witness: μ=3,σ=2,x=7
Invalid or degenerate boundary: σ=0不能进行正态标准化
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## pearson_constant
Valid-condition witness: x=(1,2,3),y=(2,4,6)
Invalid or degenerate boundary: 常量x的离差平方和为零，相关系数未定义
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## log_composition
Valid-condition witness: f(x)=ln(x²),x>0
Invalid or degenerate boundary: 链式求导缺失因子或在x=0求值
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## vector_projection
Valid-condition witness: 投影目标u非零
Invalid or degenerate boundary: 目标方向零向量导致范数平方为零
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## linear_rank_consistency
Valid-condition witness: 线性系统Ax=b需比较秩
Invalid or degenerate boundary: 同样系数矩阵可能有解或无解
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## differentiability_at_point
Valid-condition witness: x²在2点可导
Invalid or degenerate boundary: |x|在0的左右导数不相同
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## riemann_mesh_weight
Valid-condition witness: 右端点网格宽度为1/n
Invalid or degenerate boundary: 漏乘网格宽时和式不收敛到有限面积
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.

## bisection_preconditions
Valid-condition witness: 连续多项式x²−2在[1,2]端点异号
Invalid or degenerate boundary: 异号但不连续的1/x不能调用零点定理
SymPy exact checks: positive PASS / negative PASS; formal proof NOT CERTIFIED.
