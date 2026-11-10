# Batch85 | 12 份新建历史 P0 教师侧分步论证审稿卡

**本批十二项均直接绑定未关联历史 P0 原步骤的 SHA。人工教师批准0；数学全称证明形式认证0。**
12道独立条件失败见证 + 12道前提合法有限例，仅证实这些实例，不认证一般命题。
每卡提供三段论证、两道教师侧完整例题、失效边界、典型错误、三级提示与迁移题。
源SHA与原始材料校验通过不代表其原始自然语言推理自动正确。

| 历史P0步骤 | 审稿主题 | 失败前提 |
|---|---|---|
| math.hs.logarithm.product-law#2 | 对数乘积公式的逐项真数域 | x=-2,y=-3 虽使 xy>0，却使两个实数对数均无定义。 |
| math.hs.logarithm.quotient-law#3 | 对数商式与分母真数约束 | x=-2,y=-1 时 x/y=2>0，但 log_a x 与 log_a y 都无定义。 |
| math.hs.logarithm.change-base#2 | 换底公式的非零底数对数分母 | b=1 时 log_b a 不存在；a=1 时 log_a x 也不存在。 |
| math.hs.quadratic.discriminant-roots#3 | 一元二次判别式首项系数和实根分支 | a=0,b=1,c=1 时仍可能有一个一次方程根，不能套 Δ 判别式的二次根数公式。 |
| math.hs.inequality.amgm#2 | 算术几何平均不等式的非负前提 | a=-1 时实数平方根不存在，不能照搬 AM–GM 的推导。 |
| math.hs.geometry.circle-intersections#2 | 直线与圆公共点分类的非退化法向量 | A=B=0 时 Ax+By+C=0 不是一条直线，点线距离分母为零。 |
| math.hs.geometry.circle-intersections#4 | 两圆公共点分类须先判同心重合 | 同心同半径时 d=0=|r1-r2|，却不是普通内切的一点。 |
| math.hs.geometry.parabola-focus#3 | 抛物线焦准线平方变形需要非退化参数 | p=0 时焦点落在准线，得到的 y²=0 是退化对象，不能仍称非退化抛物线。 |
| math.hs.geometry.ellipse-tangent#2 | 椭圆切线方程的切点在曲线条件 | 把椭圆中心 (0,0) 当作切点，梯度为零，切线方程退化。 |
| math.hs.vector.cauchy-schwarz#2 | 柯西不等式平方范数证明的零向量分支 | 若 v=0 直接取 t=(u·v)/‖v‖²，就除以零；正确做法是先讨论零向量。 |
| math.hs.calculus.quotient-rule#2 | 商法则需要分母邻域非零与可导 | v(x)=x−1 在 x0=1 为零，即使 u,v 都可导，(u/v) 在该点无定义。 |
| math.hs.space.angle-distance#2 | 空间夹角与零向量的定义域 | 0·v=0 不能推出零向量与 v 垂直的夹角为 90°，零向量没有方向。 |

累计历史来源步骤直接挂接教师草案：60/182 P0，仍缺122；538步仍无形式认证。
学生检索与实时自由步骤验证必须继续默认拒绝，不能自动发布。
