# Batch128 — 20 historically unguarded P0 proof-step reviews

All original proof steps retain NOT_FORMALLY_VERIFIED. These 20 review cards supply explicit conditions and 40 limited exact witnesses, NOT universal proofs.
P0 tracked 127; pre-existing cards 36; new cards 20; now guarded for review 56; still without a card 71.
Historical total 538 steps, formal certifications 0; unresolved mathematical conflicts 10; teacher approvals 0.

## math.hs.space.coordinate-distance#2
Source hash: 6dad090c005d4e0b015f7af09a301c70ff36c655d74e137d2a955a3392a4b167
Required condition: 直角坐标基正交且各轴单位尺度一致，平方和才表达欧氏距离。
Justification review: 把水平与竖直分量的平方和相加是基于正交性的毕达哥拉斯定理，并非任意斜坐标都合法。
Failure boundary: 斜基e1=(1,0),e2=(1,1)时坐标(1,1)的真实长度√5不等于√2。
Exact finite check: space_distance (one positive / one invalid case); status UNVERIFIED.

## math.hs.space.line-plane-normal#3
Source hash: 390062f36e9ea7e05992f538c695162310e3130fe43030cc9d40b2f42bdbec5c
Required condition: 法向量n必须非零，过Q的正交补才有二维且唯一的平面。
Justification review: 需要先证明非零向量的正交补维数为2；不能用零向量法线推出唯一平面。
Failure boundary: n=(0,0,0)时n·(X-Q)=0对整个空间成立而不是一张平面。
Exact finite check: plane_normal (one positive / one invalid case); status UNVERIFIED.

## math.hs.space.angle-distance#2
Source hash: 8a5bd38695865065466bb95f91da53e5105ede61d66f92b6f3d3c88c74c913bf
Required condition: 方向向量u与法向量n都非零，才能定义归一化的夹角。
Justification review: 绝对值把有向内积变成最小无向夹角的余弦，不能省略非零分母条件。
Failure boundary: u=0或n=0时角不存在，公式的归一化分母为零。
Exact finite check: space_angle (one positive / one invalid case); status UNVERIFIED.

## math.hs.geometry.circle-intersections#2
Source hash: d90abd1594e2f935a35f3841316518c15ef30b9641a6d9ab5963b31804f92b84
Required condition: 半径r>0且给定直线真实存在，d≥0才可用三种交点数分类。
Justification review: 在垂足坐标中平方根个数依赖r²-d²的符号，需要先确立非退化圆和有效直线。
Failure boundary: r=0只表示退化点集，不是命题中的非退化圆。
Exact finite check: circle_intersect (one positive / one invalid case); status UNVERIFIED.

## math.hs.geometry.parabola-focus#2
Source hash: bba9bff646f1c07d50feb0d030c379d96ed8b70ef0c5402e35f56458d331ce81
Required condition: 焦点与准线不同且两距离非负才能从距离等式合法平方。
Justification review: 距离非负保证正向平方可逆，但p=0时非退化抛物线的定义失去效力。
Failure boundary: p=0时焦点落在准线上，不能用一般非退化抛物线的公式证明。
Exact finite check: parabola (one positive / one invalid case); status UNVERIFIED.

## math.hs.geometry.ellipse-tangent#2
Source hash: 443ac6f37a1400f09adbfb3531dbc6b02de29f251636aacf5a5b9b6bbf63c2b9
Required condition: 切点P必须在隐式曲线上且该点梯度非零。
Justification review: 梯度法线推导只在正则点有效，不能因能算出代数线性式就称其为切线。
Failure boundary: P=(0,0)不在x²/9+y²/4=1上，代入模板产生伪切线。
Exact finite check: ellipse_tangent (one positive / one invalid case); status UNVERIFIED.

## math.hs.proof.induction#3
Source hash: f4967d620a23cb38ce08adbebea9d89c948fec54395a7c74a467bfc26337d4f1
Required condition: 归纳起点必须成立且从任意k≥起点能推出k+1。
Justification review: 最小反例论证要求自然数良序和前一项在归纳范围内，不能跳过起点。
Failure boundary: 若命题只从n≥1声明，则n=0不属于这段归纳推理的合法检验域。
Exact finite check: induction (one positive / one invalid case); status UNVERIFIED.

## math.hs.logarithm.quotient-law#3
Source hash: c1ee45dbd39b231b8aec3afbe28c8503d5bfb28f7bbee15316682f8ae9ae40d5
Required condition: 实对数底数a>0且a≠1，同时x>0且y>0。
Justification review: 商为正不等于分子分母分别可取实对数，指数与实对数互逆必须在正值域。
Failure boundary: x=-4,y=-2时x/y>0但右侧两个实对数都无定义。
Exact finite check: log_quotient (one positive / one invalid case); status UNVERIFIED.

## math.hs.logarithm.change-base#2
Source hash: e6e193fbf4b65a2bf45fd317119989e3da21781462a985173b84024790c5e355
Required condition: a,b>0且a,b≠1，并且x>0。
Justification review: 对数幂法则以合法底数与合法真数为前提，后续除log_b(a)需要该量非零。
Failure boundary: a=1时log_b(a)=0且log_a(x)本身没有定义。
Exact finite check: change_base (one positive / one invalid case); status UNVERIFIED.

## math.hs.quadratic.discriminant-roots#2
Source hash: 5b715bf35232fe5c15537cd264dd13c7791b97791a5a0b6a84f6362a1a400eae
Required condition: 方程系数a≠0并在实数域中讨论根的个数。
Justification review: 实平方非负才允许通过判别式符号分类；退化线性情形不能用二次公式。
Failure boundary: a=0时原方程不是二次方程，公式中的2a为零。
Exact finite check: discriminant (one positive / one invalid case); status UNVERIFIED.

## math.hs.sequence.odd-square-sum#3
Source hash: 29ae1a7d3404263f30632b9ff82a3f7cb317cd49b2ac3979524ca6e7b84ee2a2
Required condition: n取从正确起点开始的整数且归纳假设已经对n成立。
Justification review: 平方恒等式核验是归纳步的一部分；单个等式成立不代替对所有n的归纳论证。
Failure boundary: 若题目声明n≥1，擅自把n=-1代入有限求和符号不属于原定义域。
Exact finite check: odd_sum (one positive / one invalid case); status UNVERIFIED.

## math.hs.vector.pythagorean-dot#2
Source hash: 0fe9ac83fab9a47e95fdfb06e1474fe8a82c6eba91b0754f081d995d76b585e2
Required condition: 已证明u·v=0才可消掉范数展开中的交叉项。
Justification review: 平行四边形平方恒等式普适，但毕达哥拉斯等式需要正交，零向量的角度仍未定义。
Failure boundary: u=v=(1,0)时交叉项不为零，平方范数不等于两平方范数的和。
Exact finite check: orthogonal_norm (one positive / one invalid case); status UNVERIFIED.

## math.hs.probability.union-bound-two#3
Source hash: 6ccc5319207953d107e30e568bdde23df76e8a156d2ee58ff7f64fad5890b484
Required condition: 同一概率空间内P(A∩B)=0才与两事件并集上界取等。
Justification review: 零概率交集未必为空集，证明应只移项概率而不额外假设集合不交。
Failure boundary: 两事件均含正概率结果时交集概率正，联合上界不取等。
Exact finite check: union_bound (one positive / one invalid case); status UNVERIFIED.

## math.hs.logarithm.product-law#2
Source hash: b9fd40f7691c411d52b93c4c4e9379ebc21ff78558ca3ed3b70e13cb20162a2d
Required condition: 实对数各真数x,y都必须严格正且底数合法。
Justification review: 乘积xy为正仍允许x,y都负，不能从乘积正直接合法化两个实对数。
Failure boundary: x=-2,y=-4时xy=8为正而log_a(x)、log_a(y)无实值。
Exact finite check: log_product (one positive / one invalid case); status UNVERIFIED.

## math.hs.sequence.square-sum#2
Source hash: 4057d163895e6ae3f0191458ded207b8ff77d92f3aa55a21ddb5d8a8574aece3
Required condition: 归纳假设只能用于已完成的n=m整数步，起点不可省略。
Justification review: 这一步是归纳假设的陈述，本身不是平方和恒等式的形式化证明。
Failure boundary: n=-1不是从1起始有限求和的合法项数，不能据此外推归纳命题。
Exact finite check: square_sum (one positive / one invalid case); status UNVERIFIED.

## math.hs.vector.parallelogram#3
Source hash: 180cb657d4bbb7f92b5ed2e9c578e8fec0f1269fb968f3bdd43b738f4177adf3
Required condition: 两向量必须属于同一实内积空间且加减法有定义。
Justification review: 通过双向展开抵消正负交叉项，不需要正交；不能跨不同维度直接相加。
Failure boundary: u∈R²、v∈R³时u+v并非此命题中的合法向量加法。
Exact finite check: parallelogram (one positive / one invalid case); status UNVERIFIED.

## math.hs.probability.variance-covariance#2
Source hash: a3b4da758ef2c3a46722b5fbba424f21ac8d6561c713238b2dd47ca50a1a546f
Required condition: 随机变量平方期望有限，协方差及方差才可按恒等式展开。
Justification review: 有限期望允许线性拆项；不能把具有不存在二阶矩的变量强套方差公式。
Failure boundary: 不构成有效概率分布的负权重不能解释为期望；Cauchy分布方差未定义。
Exact finite check: variance_cov (one positive / one invalid case); status UNVERIFIED.

## math.hs.geometry.circle-complete-square#1
Source hash: 12bf2c8bd2be2c1e45485bd93f52d4c77b4507b1eae8328de65e29dd617db4df
Required condition: 代数配方对实数D,E有效，但现实圆还要求配方后半径平方严格正。
Justification review: 完成平方恒等式正确不代表任意原方程都有非退化实圆的几何解释。
Failure boundary: x²+y²+1=0配方后半径平方为负，没有真实圆。
Exact finite check: circle_square (one positive / one invalid case); status UNVERIFIED.

## math.hs.geometry.ellipse-parameter#1
Source hash: 2796d506f645c2d43b2e03f678e194e3117b86c0aeefa58fe12db08101deab42
Required condition: a,b严格非零，代入参数式时才能约去分母平方。
Justification review: 三角恒等式给出正向包含；只验证一个方向不能自动证明参数化覆盖全部椭圆。
Failure boundary: a=0时参数形式退化，椭圆标准方程的分母不可用。
Exact finite check: ellipse_param (one positive / one invalid case); status UNVERIFIED.

## math.hs.inequality.amgm#2
Source hash: c870676b102d80db79a5e15ebd316f39f75876444ac2e736e4180487b1474982
Required condition: 实数a,b非负使根号有实数意义，且除数2为正。
Justification review: 除以2保持不等号是合法的，但前面的平方非负条件依赖a,b非负。
Failure boundary: a=-1,b=4时√ab在实数域未定义，不能照搬非负数AM-GM。
Exact finite check: amgm (one positive / one invalid case); status UNVERIFIED.
