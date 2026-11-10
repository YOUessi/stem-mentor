# Batch80｜8项高风险历史证明前提复核（教师侧草案）

本批8条对应先前99条未有审查卡的历史P0，全部有两例、三段推理、前提失效见证与三级启发提示。
**仅证明受限数值实例与不适用条件被机器检查；未做一般定理形式化认证。**

| 历史证明步骤 | 数学主题 | 正例 | 拒绝例 |
|---|---|---|---|
| math.hs.logarithm.product-law#1 | 实对数积法则及真数边界 | {'a': 2, 'x': 2, 'y': 8} | {'a': 2, 'x': -2, 'y': -3} |
| math.hs.quadratic.sign#2 | 二次函数配方判断符号的先决条件 | {'a': 1, 'b': -2, 'c': 2, 'x': 0} | {'a': 0, 'b': 2, 'c': -3, 'x': 1} |
| math.hs.function.abs-triangle#2 | 绝对值三角不等式与等号条件 | {'u': 2, 'v': 5} | {'u': 2, 'v': -3} |
| math.hs.counting.product-rule#2 | 分步计数乘法原理中的固定选择数 | {'counts': [3, 3, 3]} | {'counts': [2, 3]} |
| math.hs.calculus.tangent-line#1 | 切线线性近似要求可导 | {'kind': 0, 'x0': 2, 'h': 1} | {'kind': 1, 'x0': 0, 'h': 1} |
| math.hs.vector.dot-product#2 | 向量夹角公式中的非零条件 | {'u': [1, 0], 'v': [0, 2]} | {'u': [0, 0], 'v': [1, 2]} |
| math.hs.probability.total#3 | 全概率分解依赖互斥且穷尽的分割 | {'N': 4, 'A': [2, 3], 'blocks': [[1, 2], [3, 4]]} | {'N': 4, 'A': [2, 3], 'blocks': [[1, 2], [2, 3, 4]]} |
| math.hs.trig.double-angle-reduction#2 | 二倍角公式及易漏常数项 | {'p': 3, 'q': 4, 'r': 5} | {'p': 1, 'q': 1, 'r': 1} |

所有内容来源为原创编辑草案，保持REVIEW_PENDING/TEACHER_ONLY。
教师正式签核前，不能进入学生权威检索或完整答案索引。
