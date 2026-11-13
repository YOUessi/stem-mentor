# Batch140｜历史P0证明步骤前提与有限验证审查（教师候审）

**这是24条原始证明步骤的逐项数学审查卡，不是24条已认证的形式化证明。**
538条历史步骤中的KB80定义P0共127项；KB28/29/30已给全部127项建立候审编辑记录（35+48+44），但这些不构成证明认证。
在另外的KB80源卡体系中：原36张、Batch128增20张、本批新增24张严密引用及独立SymPy验证卡；该体系合计80张，剩余47项缺此类型的新卡，**并非47条从未审查过**。
学生权威发布0，正式教师审核0，形式化证明认证0；未关闭10项数学冲突。
原始claim与reason直接以SHA256锁定到项目既有证明步骤，不复制课标原文。

## math.hs.geometry.circle-intersections#3

历史步骤SHA-256: ed7c89d7b27327bf1748752ee00db456b8a11aea8b8000c7dfb2434e3186d0ed
原声明：两圆公共点 P 必须使三边 C₁P=r₁、C₂P=r₂、C₁C₂=d 构成三角形或退化三角形。
原依据：三角形不等式及其等号给出外切/内切的界限。
### 必须先建立的前提
两圆半径 r₁,r₂ 都严格正，中心距 d>0；三角形边长不等式只约束不同圆心的公共点。
### 逐步合法性审查
对任一公共点P，距离 C₁P=r₁、C₂P=r₂ 与 C₁C₂=d 同时成立，因此由距离三角不等式得 |r₁-r₂|≤d≤r₁+r₂；但不等式单独并不足以推出公共点唯一或个数。
### 不适用边界与反例
同心且半径均为2时 d=0，三条长度是2、2、0的退化三角形，却有整圆无限多公共点；不能套用普通相切分类。
### 有限精确验证
circle_triangles：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.geometry.circle-intersections#4

历史步骤SHA-256: 19988bb9e5e4cb63d6eb5fea029bf6f4f13d277505b31f2b78f950c376788d9b
原声明：严格三角形不等式时通常由对称性产生两个交点，等号时三个点共线只剩一个交点。
原依据：当中心和半径完全相同则公共点无穷多，因此与等号内切的普通情况不同。
### 必须先建立的前提
两圆均非退化、圆心不重合；等号条件还须区分外切 d=r₁+r₂ 与内切 d=|r₁-r₂|。
### 逐步合法性审查
将连心线取作横轴，解两圆方程相减得到公共弦的固定横坐标；竖坐标平方正则双交点，零则单切点，负则无实交点。完全重合是另外一类。
### 不适用边界与反例
圆心重合且半径相等时不管等号形式如何，公共点都是无穷多个；若半径不等则无公共点。
### 有限精确验证
circle_count：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.geometry.parabola-focus#3

历史步骤SHA-256: 18734b19734c82ec85030cd3fa74c26bd7c3b18991858e29b13fe1d633f7c0a6
原声明：反过来若 y²=4px，代回平方等式得到两距离平方相等，非负距离故原距离相等。
原依据：平方根取非负值，所以平方相等可恢复原始距离等式。
### 必须先建立的前提
p>0、焦点为(p,0)、准线 x=-p，并且采用欧氏距离且距离平方皆非负。
### 逐步合法性审查
由 y²=4px 推得 (x-p)²+y²=(x+p)²；两侧是点到焦点和准线距离的平方，非负距离平方相等可恢复原距离相等，证明逆向包含。
### 不适用边界与反例
若 p=0，焦点落在准线上，方程 y²=0 给出整条x轴，但这不是通常的非退化抛物线；模型前提已失效。
### 有限精确验证
parabola_converse：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.quadratic.discriminant-roots#3

历史步骤SHA-256: b8e51299bb0bd8b9677f3f00768f9efd2ef8f3f8c15c7599ce9075cc933cda4d
原声明：若 Δ>0，则 2ax+b=±√Δ，两值不同；因 2a≠0，得 x=(-b±√Δ)/(2a)。
原依据：求平方根的两支，并保证除法合法。
### 必须先建立的前提
a≠0并在实数域讨论一元二次方程，判别式 Δ=b²-4ac 严格大于零。
### 逐步合法性审查
配方得到 (2ax+b)²=Δ；取两实平方根分支，再除以非零2a，获得两个不同实根。负判别式不能在实数域照此取根。
### 不适用边界与反例
a=0 时所谓二次式退化为线性方程，2a为零，根公式无法使用；Δ>0也不能替代a≠0。
### 有限精确验证
quadratic_discriminant：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.vector.pythagorean-dot#3

历史步骤SHA-256: 78c281116957ee3448cdcdc5b4a93a8784df9bbccc5f14e434eeee6140bb2d9a
原声明：反之若平方范数可加，从展开式两侧同时减去 ‖u‖²+‖v‖²，可得 2u·v=0，故 u·v=0。
原依据：实数等式移项与 2 非零，证明必要性而非只证明单向。
### 必须先建立的前提
u、v位于同一个有限维实内积空间，向量加法、数量积与范数由同一正定内积诱导。
### 逐步合法性审查
展开 ‖u+v‖²=‖u‖²+2(u·v)+‖v‖²；如果平方范数恰好可加，则对两侧作等式移项和除2，得到 u·v=0。这是充要条件的逆向。
### 不适用边界与反例
若拿两条不同维度的坐标向量拼接后直接做加法，‖u+v‖²没有本命题意义；也不能用零向量夹角作为垂直证明。
### 有限精确验证
pythagoras_converse：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.logarithm.product-law#3

历史步骤SHA-256: 4493e259c85eb86971446c4805035321895ee3cbf1afb994575902049dd0aa4b
原声明：对两边取底为 a 的对数，得 log_a(xy)=u+v=log_a x+log_a y。
原依据：指数函数单射保证逆操作有效，等式中的对数均在定义域内。
### 必须先建立的前提
对数底数 a>0 且 a≠1，两个实数真数 x,y 都严格正，并在实数范围内使用幂函数的逆运算。
### 逐步合法性审查
令u=log_a x、v=log_a y，x=a^u、y=a^v，故xy=a^(u+v)>0；在正值域取a为底的对数，得log_a(xy)=u+v。
### 不适用边界与反例
x=-2,y=-4 时乘积8为正，但 log_a(-2) 和 log_a(-4) 在实数域不存在；仅xy>0远远不够。
### 有限精确验证
log_product：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.geometry.ellipse-parameter#2

历史步骤SHA-256: ffa825951ead8dc0d8e5817e3b53b90036dc11d5e70324b5447b647b8d377bb8
原声明：若 x²/a²+y²/b²=1，则向量 (x/a,y/b) 在单位圆上。
原依据：两坐标平方和为 1；正的 a,b 保证除法有意义。
### 必须先建立的前提
椭圆半轴 a,b 必须严格正；标准方程是 x²/a²+y²/b²=1。
### 逐步合法性审查
由标准方程将 x/a 与 y/b 视为两个实数，平方和为1，故对应单位圆点；因此存在角t使它们分别等于cos t、sin t。反方向要另行代入核验。
### 不适用边界与反例
a=0或b=0时分母未定义，不能声称退化线段也被标准椭圆参数式无条件覆盖。
### 有限精确验证
ellipse_param：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.inequality.amgm#3

历史步骤SHA-256: e0bc5b3829912231c78160ae6d08e2cafc3100bda71452a50b2d1c1dbee9fba3
原声明：等号成立当且仅当 (√a-√b)²=0，即 √a=√b。
原依据：非负平方根函数单射，所以等价于 a=b。
### 必须先建立的前提
a,b为非负实数，平方根是非负的算术平方根，等号条件需要该平方根的单射性。
### 逐步合法性审查
AM-GM差量等于(√a-√b)²/2；其为0等价于√a=√b，由非负平方根的单射性得到a=b，且相等时差量确为零。
### 不适用边界与反例
a=-1,b=-1 时平均值有实数意义，但实数平方根不存在；不能沿用本等号证明。
### 有限精确验证
amgm_equality：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.function.quadratic-vertex#2

历史步骤SHA-256: 4be6d7a1cbc175f64b55e1a0e2b8adb5c7abdd74c2abf7cb90947d9fbcc072d4
原声明：用 x²+(b/a)x=(x+b/(2a))²-b²/(4a²) 配方。
原依据：展开右侧平方后消去交叉项，得到完全平方恒等式。
### 必须先建立的前提
原式确为二次函数，即二次项系数a≠0，所有自变量和系数都位于实数域，且代数除法合法。
### 逐步合法性审查
x²+(b/a)x 配成(x+b/(2a))²-b²/(4a²)属于严格代数恒等式，扩大平方并消去新增常数即可复原原表达式。
### 不适用边界与反例
a=0时 b/a 和 b/(2a) 无定义；即使原式仍代表直线，也不存在二次函数顶点公式。
### 有限精确验证
vertex_completion：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.function.quadratic-vertex#4

历史步骤SHA-256: e6c416e26a19436114b257b35dd80e8bb755e133c23acadc8675f41c8bab4abf
原声明：平方项非负；a>0 时贡献非负，a<0 时贡献非正。
原依据：令平方项为 0 可取得全局最小或最大值。
### 必须先建立的前提
a≠0 且自变量可取全体实数；平方项系数的符号决定最大值或最小值。
### 逐步合法性审查
二次函数写成a(x+b/(2a))²+c-b²/(4a)后，平方非负；当a>0在顶点取全局最小值，当a<0取全局最大值。
### 不适用边界与反例
若定义域改成x≥1，而原顶点在x=0，不能仍说最大或最小在顶点处于该定义域内取得。
### 有限精确验证
vertex_extremum：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.logarithm.inverse#2

历史步骤SHA-256: 41b2828120226d56edf2f97aa09a0dfdf758751aaa107bb7d85499c84fcac4cf
原声明：令 u=log_a x、v=log_a y，则 a^u=x、a^v=y。
原依据：由对数定义得到指数形式。
### 必须先建立的前提
实数对数底数a>0且a≠1；x,y作为真数需严格正，指数函数映射的值域才覆盖所取真数。
### 逐步合法性审查
按照实对数定义，u=log_a x 等价于 a^u=x；指数在实数域严格单调并满射正实数，逆向关系成立；y同理。
### 不适用边界与反例
x=0或a=1时逆函数关系没有合法实对数；不能把 log_1 x 当普通实数函数。
### 有限精确验证
log_inverse：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.trig.sum-angle#1

历史步骤SHA-256: ea393eb80f2828c0c2ee1158a20e17b195f6a701902c56c64204581c259f4caf
原声明：绕原点旋转角 α 的平面线性映射对应矩阵 [[cosα,-sinα],[sinα,cosα]]。
原依据：矩阵两列分别是单位基向量旋转后的坐标，可由保距和保向验证。
### 必须先建立的前提
欧氏平面使用正交、同尺度、固定正向直角坐标，角度使用与三角函数一致的约定。
### 逐步合法性审查
旋转变换把e₁变为(cosα,sinα)，e₂变为(-sinα,cosα)，两基向量的像构成矩阵的两列，由线性性确定任意向量的像。
### 不适用边界与反例
若把坐标轴换成斜基后仍直接套同一矩阵，通常不会保持该斜基坐标所表达的实际欧氏距离。
### 有限精确验证
rotation_matrix：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.vector.dot-product#4

历史步骤SHA-256: 6ac2a4d5681faf932f4f8ea4569bc55db876beca0e6e048104700ef9d5d18ec6
原声明：当 a,b 都非零时，a·b=0 等价于 cosθ=0，即 θ=90°。
原依据：|a||b| 严格为正可相除，θ 在 0 到 π 的唯一余弦零点是 π/2。
### 必须先建立的前提
a与b均为非零实欧氏向量，夹角θ∈[0,π]由它们的非零方向唯一确定，模长乘积才能作为分母。
### 逐步合法性审查
将a·b=|a||b|cosθ两端除以严格正的模长乘积，得到点积为零当且仅当cosθ=0；指定的角域中唯一零点为π/2。
### 不适用边界与反例
a=0时点积为零仍成立，但夹角根本不存在；不得将其宣称为直角关系。
### 有限精确验证
dot_angle：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.space.basis-three-unique#2

历史步骤SHA-256: dc20e769169e0dbd2b5acd1837f4fb2d598076c72c061f35c1e6917a80ccb58d
原声明：三维方阵零空间平凡，故det M≠0并存在逆矩阵M^(-1)。
原依据：方阵可逆、行列式非零与零空间平凡的等价定理。
### 必须先建立的前提
M是实数域的3×3方阵，三列为候选空间基向量，矩阵秩可按通常线性代数定义计算。
### 逐步合法性审查
如果齐次方程 Mv=0 只有零解，则零空间维数0，由秩-零度定理可知秩3；故行列式非零且存在逆矩阵。必须处理方阵维数。
### 不适用边界与反例
仅3×2矩阵的零空间平凡不能推出3×3行列式非零，更不能求不存在的方阵逆。
### 有限精确验证
basis_three：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.calculus.quotient-rule#2

历史步骤SHA-256: 68893ea2edf43c35a78788acd400a574b2cfa301a37def704ad17bdbe9c9e164
原声明：令 x→x₀，由 v 的连续和可导性得到 w'(x₀)=-v'(x₀)/[v(x₀)]²。
原依据：分母极限为 v(x₀)²>0，因此极限乘除成立。
### 必须先建立的前提
v在x₀可导且v(x₀)≠0；在x₀附近应选取v持续非零的邻域。
### 逐步合法性审查
可导蕴含连续，所以v(x)→v(x₀)非零，求导的差商分母趋向v(x₀)²>0；按极限定理得到(1/v)'=-v'/v²。
### 不适用边界与反例
v(x₀)=0时倒数函数甚至在该点未定义，比如v(x)=x、x₀=0。
### 有限精确验证
reciprocal_derivative：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.calculus.fermat-stationary#2

历史步骤SHA-256: 3ca552a8f402f02791b1540c3fe9c8418f221bf5b9fb7d8d7e3c9c02a23799be
原声明：对 h>0，差商 [f(x₀+h)-f(x₀)]/h≤0；对 h<0，差商 ≥0。
原依据：除以负数必须改变不等号方向，左右极限受相反符号约束。
### 必须先建立的前提
x₀是定义域的内点且f在x₀有局部最大值，并有双侧极限需要的邻域。
### 逐步合法性审查
局部极大意味着足够小h时f(x₀+h)-f(x₀)≤0；h正时差商非正，h负时除负数要反号所以差商非负。
### 不适用边界与反例
只在右侧有定义的端点最大值不能依此建立负h差商，不能推导导数等于零。
### 有限精确验证
fermat_sign：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.vector.cauchy-schwarz#2

历史步骤SHA-256: 9272449b59eabc68eb8b55b647ba78b9990dbc8acfb391267c51cec01a33c5bf
原声明：对任意实数 t，0≤‖u-tv‖²=‖u‖²-2t(u·v)+t²‖v‖²。
原依据：实向量的范数平方非负，将数量积双线性展开得到二次多项式。
### 必须先建立的前提
u,v属于同一正定实内积空间，t为任意实数，范数平方必须总为非负实数。
### 逐步合法性审查
双线性和对称性展开 (u-tv)·(u-tv)=‖u‖²-2t(u·v)+t²‖v‖²，对任意实t非负；本步尚未除以‖v‖²。
### 不适用边界与反例
若把所谓范数平方写成不正定的伪内积，则展开虽成立却不能断言对任意t非负。
### 有限精确验证
cauchy_expand：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.vector.cauchy-schwarz#3

历史步骤SHA-256: 550a05fd0c8eeff2940a8638a8e64138dfbc2a7a3b02f17dc46c72f13116d02a
原声明：取 t=(u·v)/‖v‖²，得到 0≤‖u‖²-(u·v)²/‖v‖²，于是 (u·v)²≤‖u‖²‖v‖²。
原依据：v≠0 保证分母非零；两边乘正数并移项。
### 必须先建立的前提
v≠0保证‖v‖²严格正，允许取t=(u·v)/‖v‖²并进行正数乘法。
### 逐步合法性审查
把此t代入上一非负二次式，化简后得到‖u‖²-(u·v)²/‖v‖²≥0；两边乘严格正的‖v‖²可保留不等号方向。
### 不适用边界与反例
v=0时不等式结论依然平凡成立，但此取t与分式推导无定义，必须独立处理零向量。
### 有限精确验证
cauchy_minimize：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.vector.cauchy-schwarz#4

历史步骤SHA-256: 38b2cc37573f32b5248ab10f8039f2a8a6808ddd5e152d82c24fd27439bbb124
原声明：等号当且仅当 ‖u-tv‖²=0，即 u=tv；加上 v=0 情形可表述为两个向量线性相关。
原依据：欧氏范数为零当且仅当向量是零，完成等号条件的充分性与必要性。
### 必须先建立的前提
以真实欧氏正定内积定义范数，v非零时t按前一步取值；v零时单独处理。
### 逐步合法性审查
等号与‖u-tv‖²=0等价；正定性使u=tv。v=0时任意u与v仍线性相关，且点积不等式为0=0。
### 不适用边界与反例
用非正定二次型时存在非零零长度向量，零范数便不能推出两向量相等。
### 有限精确验证
cauchy_equality：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.probability.expectation-linearity#3

历史步骤SHA-256: e100b327c6aad6752dafa0063597d3de45aab00e5f0aca556f3422d52a6f3b45
原声明：两部分分别是 aE[X] 和 bE[Y]，从而得到原式。
原依据：按期望定义识别两项，独立性不是前提。
### 必须先建立的前提
X,Y在同一概率空间且可积，即E|X|、E|Y|都有限；a,b为有限实常数。
### 逐步合法性审查
利用期望积分的线性性分别抽出常数得到E[aX+bY]=aE[X]+bE[Y]；整个推导不需要独立性。
### 不适用边界与反例
若X是Cauchy随机变量，E[X]不存在，不能把未定义的期望拆开和重组；独立也无法弥补不可积。
### 有限精确验证
expectation_linearity：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.elective.linear.rank-vectors#3

历史步骤SHA-256: 4fc0495c345ae6ddef3499e3b2e341e13dc4096d2c11e62e6401db31c1afb932
原声明：当 det A=0 时 A 不可逆，齐次系统至少有非零解，于是三个列向量存在非平凡的零组合。
原依据：秩–零度关系/方阵消元保证奇异时非零零空间。
### 必须先建立的前提
A是3×3实方阵，det A=0；列向量按相同基底表示，且列数正好等于方阵维数。
### 逐步合法性审查
由方阵奇异得到rank(A)<3；秩-零度定理保证至少一维非零零空间，存在v≠0使Av=0，即列向量线性相关。
### 不适用边界与反例
非方阵没有3×3行列式，即便列数不等于行数也不能按此公式断言唯一解。
### 有限精确验证
rank_vectors：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.elective.statistics.ols-two-parameter#1

历史步骤SHA-256: 91d956e441597d3b16e51f04a724a6b08ab22931f8ef31fb1ab1c646799fe96e
原声明：对 a 求偏导得到 -2Σ(y_i-a-bx_i)=0，所以对固定 b 的最优截距 a=ȳ-bx̄。
原依据：平方和严格凸于 a，正规方程成立。
### 必须先建立的前提
n≥1，所有x_i,y_i为有限实数且考虑带截距的平方残差目标；固定斜率b。
### 逐步合法性审查
目标S(a,b)=Σ(y_i-a-bx_i)² 对a的一阶导数为-2Σ(y_i-a-bx_i)，二阶导数2n>0，故唯一最佳截距a=ȳ-bx̄。
### 不适用边界与反例
当n=0时均值未定义、曲率为0，任何截距的空和都相同，不存在唯一最佳截距。
### 有限精确验证
ols_intercept：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.elective.model.parametric-circle#3

历史步骤SHA-256: 8c4cd3930764b87844685c233f57a3aa0e9745270f8e65e2dffd4b438f1d07d9
原声明：求导得 x'=-r sin t、y'=r cos t；速度模长 sqrt(r²sin²t+r²cos²t)=r。
原依据：按弧度制求导且 r>0，速度非零；r=0 导致退化。
### 必须先建立的前提
半径r>0，角参数t用弧度制且路径为x=r cos t、y=r sin t。
### 逐步合法性审查
按弧度求导得到(-r sin t,r cos t)，速度大小r√(sin²t+cos²t)=r；严格正半径保证速度非零。
### 不适用边界与反例
r=0时路径退化常点，速度大小0不能再宣称为非零匀速；若角参数以度数变化导数也需比例因子。
### 有限精确验证
parametric_circle：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## math.hs.elective.sequence.epsilon-n#2

历史步骤SHA-256: 6bfd9f0c0211d1ed97e95fe7a2e242b5bb3c3b9384854b61065931ea4f1d3973
原声明：对所有 n≥N，有 0<1/n≤1/N<ε。
原依据：n、N 均为正数，取倒数改变不等号方向。
### 必须先建立的前提
n,N均为正整数并且已经选定满足1/N<ε的整数N，ε>0，所有比较都仅发生于正实数域。
### 逐步合法性审查
n≥N>0时倒数函数在正实数域严格递减，故0<1/n≤1/N<ε，证明所有足够大的n满足界限。
### 不适用边界与反例
若取N=0则1/N无意义；若ε=0则不存在任何正整数N使严格正的1/N<ε。
### 有限精确验证
epsilon_n：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。

## 历史剩余审查队列

剩余47条缺少KB80/128/140独立来源卡，但已存在KB28/29/30较早的编辑记录；仍不得自动标记已验证：

- math.hs.calculus.tangent-line#3
- math.hs.complex.operations#2
- math.hs.complex.operations#3
- math.hs.elective.calculus.differentiable-continuous#1
- math.hs.elective.calculus.second-derivative-convexity#3
- math.hs.elective.finance.annuity-present-value#3
- math.hs.elective.function.epsilon-delta-square#2
- math.hs.elective.geometry.euclidean-isometries#2
- math.hs.elective.geometry.euclidean-isometries#3
- math.hs.elective.matrix.gaussian-row-equivalence#2
- math.hs.elective.matrix.inverse-two-by-two#3
- math.hs.elective.model.input-output-triangular#2
- math.hs.elective.model.time-rescaling#4
- math.hs.elective.multivariable.partial-polynomial#3
- math.hs.elective.sequence.fibonacci-golden-ratio#3
- math.hs.elective.statistics.bernoulli-mle#2
- math.hs.elective.statistics.bernoulli-mle#3
- math.hs.extension.circle-polar#1
- math.hs.extension.circle-polar#3
- math.hs.extension.cross-product#3
- math.hs.function.composition-domain#3
- math.hs.geometry.line-circle#3
- math.hs.geometry.line-equation#2
- math.hs.geometry.line-equation#3
- math.hs.geometry.line-general#1
- math.hs.geometry.line-general#2
- math.hs.geometry.line-general#3
- math.hs.geometry.line-relations#1
- math.hs.geometry.line-relations#2
- math.hs.geometry.line-relations#3
- math.hs.geometry.point-line-distance#3
- math.hs.geometry.space-dot#1
- math.hs.geometry.space-dot#2
- math.hs.geometry.space-dot#3
- math.hs.probability.multiplication#2
- math.hs.space.parallel-perpendicular-criteria#3
- math.hs.space.perpendicular-plane#1
- math.hs.space.perpendicular-plane#2
- math.hs.space.perpendicular-plane#3
- math.hs.space.point-line-distance#3
- math.hs.space.solid-volumes#1
- math.hs.space.solid-volumes#2
- math.hs.space.solid-volumes#3
- math.hs.triangle.sine-law#3
- math.hs.trig.double-angle-reduction#3
- math.hs.vector.linear-operations#1
- math.hs.vector.projection#2
