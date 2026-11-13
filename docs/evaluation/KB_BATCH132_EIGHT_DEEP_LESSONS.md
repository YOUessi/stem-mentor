# Batch132 — eight deep original elective mathematics lesson manuscripts

REVIEW_PENDING / TEACHER_ONLY. Exact checked examples are finite cases, not a universal theorem proof or teacher endorsement.
Independently recomputed: 16 examples and 8 invalid-condition cases.

## 平面等距变换的正交矩阵判据 (ELECTIVE_A)
Editorial source anchor p.55 lines 20-20 (not official atom denominator)
Formal statement: 二维欧氏空间中的线性映射T(x)=Qx保持任意两点欧氏距离，当且仅当实矩阵Q满足QᵀQ=I；任意固定平移T(x)=Qx+b也保持距离。此时Q行列式只能是±1。
Symbols and domain: Q为2×2实矩阵，x,b为列向量；‖x‖₂=√(xᵀx)；I是单位矩阵。
All hypotheses: 欧氏内积及实数矩阵；若讨论Qx+b是仿射等距变换，不得错误称为线性除非b=0。
### Justified steps
1. 充分性：计算变换后距离 — ‖Qx−Qy‖₂²=(x−y)ᵀQᵀQ(x−y)=‖x−y‖₂²，平方根非负得距离相同。
2. 必要性：从所有点对距离保留得到所有向量范数保留 — 取y=0，‖Qv‖₂²=‖v‖₂²对所有v成立，因此vᵀ(QᵀQ−I)v=0。
3. 用基向量及其和求出矩阵元 — 代入e₁、e₂得对角元为零，再代入e₁+e₂且矩阵对称，得非对角元为零，故QᵀQ=I。
4. 加入平移并求行列式约束 — (Qx+b)−(Qy+b)=Q(x−y)；对QᵀQ取行列式得det(Q)²=1。
Failure / non-example: 非均匀缩放diag(2,1)使水平距离加倍；一般平移不满足T(0)=0，因此不是线性变换。
Typical incorrect reasoning: 把任何旋转加平移写成一个2×2线性矩阵，并省略仿射常量b。
Repair: 先分别验证是否保持原点和两点距离；平移应写作Qx+b，齐次坐标另有表示方式。
### Teacher-only worked examples
**Question:** Q=[[0,-1],[1,0]]将(1,0)和(0,2)变为哪些点？距离是否守恒？
1. 计算Q(1,0)=(0,1)，Q(0,2)=(-2,0)。
2. 初始差向量为(1,-2)，长度√5。
3. 新差向量为(2,1)，长度√5。
**Teacher-only answer:** 新点(0,1)、(-2,0)，距离均为√5。
**Question:** 关于y轴反射Q=diag(-1,1)，求(2,1)和(0,1)的像及距离。
1. 把两点分别乘以Q得(-2,1)、(0,1)。
2. 原距离为2，像点距离为2。
3. 直接算QᵀQ=I，确认一般距离守恒。
**Teacher-only answer:** 像点(-2,1)和(0,1)，距离仍为2。
### Student hints without solution
1. 先写变换矩阵，并分别变换两点。
2. 计算像点差向量，观察平移向量为什么消失。
3. 比较QᵀQ与单位矩阵，而不是凭图像看似旋转。
Near transfer: 判断Q=diag(1,-1)是否也为等距变换，并给出决定它是否旋转的行列式条件。
Far transfer: 在图像配准中区分相机平移与镜头缩放对物体间像素距离的影响。

## 非齐次线性方程组秩相等判定有解 (ELECTIVE_B)
Editorial source anchor p.60 lines 22-22 (not official atom denominator)
Formal statement: 对m×n实系数矩阵A与m维常数列b，Ax=b有解当且仅当rank(A)=rank([A|b])；若有解，唯一解当且仅当rank(A)=n，否则存在自由变量而有无穷多实解。
Symbols and domain: A为系数矩阵；[A|b]为增广矩阵；rank为列空间或行最简阶梯形非零主元数；n为未知数数量。
All hypotheses: 有限维实线性方程组；不得把齐次方程组必有零解的结论直接套在非齐次系统。
### Justified steps
1. 将有解改写为列空间包含关系 — Ax=b意味着b是A的各列向量的线性组合，即b∈Col(A)。
2. 比较添加b前后列空间维数 — b∈Col(A)等价于添加b列没有增大列空间维数，故rank([A|b])=rank(A)。
3. 可解时讨论唯一性 — 任两解x₁,x₂差满足A(x₁−x₂)=0；解唯一等价于Null(A)={0}。
4. 由秩-零度定理判断自由变量 — dim Null(A)=n−rank(A)；为0时唯一，否则对任意零空间向量沿任意倍数得无限多解。
Failure / non-example: A=[1;0]、b=[0;1]时rank(A)=1、rank([A|b])=2无解；即使两秩都为1也可能有不唯一解。
Typical incorrect reasoning: 见rank(A)=rank([A|b])就断言系统有唯一解。
Repair: 一致性与唯一性是两个不同门槛：再计算rank(A)与未知数n的关系。
### Teacher-only worked examples
**Question:** x+y=3与2x+2y=6有几个解？
1. 两行系数成比例、常数列也同比例，两秩均1。
2. 未知数n=2，秩1<n。
3. 令x=t，y=3−t得无穷多个解。
**Teacher-only answer:** 无穷多解(x,y)=(t,3−t)。
**Question:** x+y=3与2x+2y=5有几个解？
1. 系数行成比例故rank(A)=1。
2. 常数不同倍，增广矩阵秩变为2。
3. 两秩不等，因此不存在解。
**Teacher-only answer:** 无解。
### Student hints without solution
1. 把每个方程的系数和常数分开构成矩阵。
2. 先行消元比较两个秩，不要先算未知数。
3. 若秩相等再和未知数个数比较以区分唯一与无限。
Near transfer: 判断x+y=3与x−y=1的解类型，并求出唯一解。
Far transfer: 在推荐系统中把重复线性约束当新增独立信息会造成什么参数辨识问题。

## 定积分与导数的基本联系及前提 (ELECTIVE_A)
Editorial source anchor p.53 lines 21-21 (not official atom denominator)
Formal statement: 微积分基本定理的一个版本：若f在闭区间[a,b]连续，定义F(x)=∫ₐˣ f(t)dt，则在(a,b)处F′(x)=f(x)；在端点讨论适当单侧导数。因而对f的任一原函数G有∫ₐᵇ f(t)dt=G(b)−G(a)。
Symbols and domain: f为实值连续函数；F为变上限积分；a<b；G′=f；积分为有向定积分。
All hypotheses: 闭区间上的连续性、Riemann可积性；对求导公式讨论内点；若仅分段连续，不得无条件在跳点取导。
### Justified steps
1. 连续性给出定积分与局部平均值可控 — F(x+h)−F(x)=∫ₓˣ⁺ʰf(t)dt，除以h为该小区间平均值。
2. 减去f(x)并估计误差 — 由连续性，t靠近x时|f(t)−f(x)|任意小，因此积分平均与f(x)之差也趋于0。
3. 于是证明导数等于f — 差商极限存在并为f(x)，即F′(x)=f(x)。
4. 比较G与F并使用零导数常值 — 若G′=f，则(G−F)′=0，由中值定理知G−F恒定；F(a)=0，因此F(b)=G(b)−G(a)。
Failure / non-example: 若f在0有跳跃，F(x)=∫₀ˣf(t)dt未必在0处可导；仅知道各侧可积不够。
Typical incorrect reasoning: 把∫₀ˣ f(t)dt的导数无条件写作f(x)，省略连续性和内点条件。
Repair: 先核查目标点附近f的连续性；不能满足时需直接计算差商并说明单侧情况。
### Teacher-only worked examples
**Question:** f(t)=2t，F(x)=∫₀ˣ2t dt；求F(3)、F′(3)。
1. 原函数为t²，积分得F(x)=x²。
2. F(3)=9。
3. 求导F′(x)=2x，故F′(3)=6=f(3)。
**Teacher-only answer:** F(3)=9且F′(3)=6。
**Question:** 求∫₀²t²dt并核对原函数端点差。
1. 原函数G(t)=t³/3。
2. G(2)−G(0)=8/3−0。
3. f连续，满足基本定理前提。
**Teacher-only answer:** 8/3。
### Student hints without solution
1. 先判断被积函数在整个目标区间是否连续。
2. 写出变上限积分的差商及局部区间。
3. 选一个原函数，再做两个端点的差值而不是直接代上限。
Near transfer: 将f(t)=cos t的变上限积分和导数关系重新计算一遍。
Far transfer: 对离散采样的传感器输出，讨论为何插值后求积分仍有模型误差而不能完全继承连续数学假设。

## 连续函数定积分的有向面积与黎曼和 (ELECTIVE_B)
Editorial source anchor p.59 lines 2-2 (not official atom denominator)
Formal statement: 连续实函数f在[a,b]上的有向定积分是上下带符号面积之差，而其与x轴之间的几何面积为∫ₐᵇ|f(x)|dx；函数跨零点时须分段取绝对值。
Symbols and domain: ∫为Riemann定积分；a<b；|f|为函数逐点绝对值；几何面积非负。
All hypotheses: f连续以保证积分存在；计算几何面积需判断零点或区间上函数符号，复杂边界还需确认曲线间上下关系。
### Justified steps
1. 求出区间内的全部符号变点 — 在每段内用测试点或连续性论证f符号一致，不能只靠一张示意图。
2. 每段积分按符号处理 — 当f≥0，有向积分与面积相同；当f≤0，几何面积取其相反数。
3. 把各段非负面积相加 — 总几何面积等于∫|f|，而不是有向积分的绝对值；后者可能因抵消而较小。
Failure / non-example: f(x)=x在[-1,1]的积分为0但几何面积为1；绝对值不能移到整个积分外再取。
Typical incorrect reasoning: 面积=|∫₋₁¹x dx|=0，因此断言没有围成面积。
Repair: 先按0拆成[-1,0]和[0,1]两段分别取绝对值后相加，得到1。
### Teacher-only worked examples
**Question:** 计算f(x)=x在[-1,1]的有向积分及几何面积。
1. 原函数为x²/2，上下限之差是0。
2. 零点0分成负正两段。
3. 绝对面积为−∫₋₁⁰x dx+∫₀¹x dx=1。
**Teacher-only answer:** 有向积分0，几何面积1。
**Question:** 对f(x)=x−1在[0,2]计算有向积分和几何面积。
1. 原函数x²/2−x，在2与0的差为0。
2. 零点x=1。
3. 左右负正面积均为1/2，总面积1。
**Teacher-only answer:** 有向积分0，几何面积1。
### Student hints without solution
1. 画出或确定函数在哪些区间为正、负。
2. 先分别算有向积分与符号翻转点。
3. 面积计算要对每段取绝对值，不能只取积分总值绝对值。
Near transfer: 对f(x)=x²−1在[-2,2]计算几何面积，先求出零点。
Far transfer: 在财务现金流中区分正负净流量积分与总交易量，解释抵消与累计绝对量的不同。

## 三维直线和平面相交平行重合的代数判别 (ELECTIVE_A)
Editorial source anchor p.55 lines 14-14 (not official atom denominator)
Formal statement: 非零法向量n给出平面Π：n·(r−r₀)=0；非零方向向量v给出直线r=p+tv。代入后解t[n·v]=n·(r₀−p)，可分类唯一相交、平行不交或整线包含。
Symbols and domain: n为平面非零法向量，r₀为平面上一点，p为直线上一点，v≠0；t为实参数。
All hypotheses: 空间欧氏坐标；n和v均非零；所有法向量、点和方向的维度一致。
### Justified steps
1. 写下合法平面与直线表达 — 法向量非零，否则平面方程可能恒真或无解；方向非零，否则不是直线。
2. 代入直线参数式 — 得到标量线性方程t(n·v)=n·(r₀−p)。
3. 非零系数时求唯一交点 — 若n·v≠0，可解唯一t并回代直线参数。
4. 零系数时判断常数项 — 若n·v=0且右侧≠0则无解、平行；若右侧也为0则所有t成立，整条直线包含在平面中。
Failure / non-example: 只由n·v=0就说直线与平面平行且不相交，忽略整条直线位于平面内的情况。
Typical incorrect reasoning: 看到直线方向与平面法向量正交，就直接认定“严格平行不相交”，未代入已知直线上的点。
Repair: 把一个直线上点代入平面方程进一步区分包含与不相交。
### Teacher-only worked examples
**Question:** 平面z=0，直线(1,0,1)+t(0,0,-1)，求交点。
1. 平面法向量n=(0,0,1)，方向v=(0,0,-1)非零。
2. 代入z=1−t=0得t=1。
3. 回代得到交点(1,0,0)。
**Teacher-only answer:** 唯一交点(1,0,0)。
**Question:** 平面z=0，直线(1,0,1)+t(1,0,0)，判断位置关系。
1. n·v=0，所以无法得到有限唯一交参。
2. 直线任意点z=1，而平面要求z=0。
3. 右侧非零，判定平行不相交。
**Teacher-only answer:** 严格平行且不相交。
### Student hints without solution
1. 先检查给出的方向向量和法向量是否为零。
2. 把直线参数式代入平面并化简成t的一元方程。
3. 系数为0时必须继续看常数项，才能区分平行与包含。
Near transfer: 平面z=0与直线(1,0,0)+t(1,0,0)属于哪种关系？
Far transfer: 机器人轨迹检查中为什么“速度方向平行地面”并不意味着机器人必然离地。

## 带截距简单线性回归的非退化最小二乘解 (ELECTIVE_A)
Editorial source anchor p.57 lines 13-13 (not official atom denominator)
Formal statement: 含截距的一元普通最小二乘：给定n≥2个配对样本(xᵢ,yᵢ)，若Sxx=Σ(xᵢ−x̄)²>0，则唯一最小二乘斜率b₁=Sxy/Sxx，截距b₀=ȳ−b₁x̄，其中Sxy=Σ(xᵢ−x̄)(yᵢ−ȳ)。
Symbols and domain: n为观测对数；x̄、ȳ是样本均值；Sxx、Sxy为中心化平方和、乘积和；ŷ=b₀+b₁x。
All hypotheses: 所有x,y有限实数；需要n≥2且至少两个不同的x使Sxx>0；该算法是描述拟合，不自动得到因果效应。
### Justified steps
1. 定义平方损失L(b₀,b₁)=Σ(yᵢ−b₀−b₁xᵢ)² — 这是有限实数二次函数；最小化的是纵向残差平方，而不是垂直距离。
2. 对截距求一阶条件 — ∂L/∂b₀=−2Σ(yᵢ−b₀−b₁xᵢ)=0，推出b₀=ȳ−b₁x̄。
3. 代入并对斜率求条件 — L变为Σ[(yᵢ−ȳ)−b₁(xᵢ−x̄)]²；导数为−2Sxy+2b₁Sxx。
4. 检查唯一极小值条件 — Sxx>0使斜率方向严格凸，故b₁=Sxy/Sxx唯一；若Sxx=0，斜率与截距无法分别唯一确定。
Failure / non-example: 全部x相同则Sxx=0，斜率公式无定义；即便拟合相关很强也不能据此证明因果。
Typical incorrect reasoning: 使用所有x相同的数据求出一个有限斜率并报告“完美线性关系”。
Repair: 先检查Sxx，若为零则拒绝唯一斜率并声明参数不可辨识。
### Teacher-only worked examples
**Question:** 数据点(0,1),(1,3),(2,5)，求最小二乘直线。
1. x̄=1，ȳ=3，Sxx=2。
2. Sxy=(-1)(-2)+0+1·2=4。
3. 斜率2，截距3−2·1=1。
**Teacher-only answer:** ŷ=1+2x。
**Question:** 数据点(0,5),(2,1)，求含截距最小二乘直线。
1. x̄=1，ȳ=3，Sxx=2。
2. Sxy=(-1)(2)+(1)(-2)=-4。
3. 斜率−2，截距3−(-2)·1=5。
**Teacher-only answer:** ŷ=5−2x。
### Student hints without solution
1. 先核查每个x都不是同一个值。
2. 列表求出x̄、ȳ、Sxx、Sxy。
3. 只有Sxx>0才除，之后用b₀=ȳ−b₁x̄求截距。
Near transfer: 数据点(1,1),(2,4),(3,9)求拟合直线并比较真实二次函数。
Far transfer: 训练集上斜率存在并不证明未来市场价格有相同趋势，说明外推验证需要什么数据。

## 三元克拉默法则只能用于系数矩阵非奇异时 (ELECTIVE_B)
Editorial source anchor p.60 lines 25-25 (not official atom denominator)
Formal statement: 三元线性系统Ax=b若det(A)≠0，则有唯一解，且对i=1,2,3有xᵢ=det(Aᵢ)/det(A)，Aᵢ是用b替换A第i列的矩阵；这就是克拉默法则。
Symbols and domain: A为3×3系数矩阵，b为3×1列向量，Aᵢ为替换第i列矩阵，det为行列式。
All hypotheses: 实数或适当域上的方阵，det(A)严格非零；若det(A)=0不能使用除法公式，不应直接推断无解。
### Justified steps
1. det(A)非零给出逆矩阵 — 三阶方阵det(A)≠0等价于可逆，故Ax=b有且仅有x=A⁻¹b。
2. 用多线性证明列替换关系 — 把b=Σxⱼ A的第j列代入第i列替换后的行列式。
3. 利用两列相同则行列式为零 — 当j≠i时替换列与原第j列相同，对应行列式为零；仅j=i留下xᵢdet(A)。
4. 合法除以非零det(A) — 因此det(Aᵢ)=xᵢdet(A)，得到每个分量的公式；未假定det(A)=0情况。
Failure / non-example: 若A两行相同det(A)=0，系统仍可能有无限多解，也可能无解；克拉默分式不可用于这些情况。
Typical incorrect reasoning: 计算det(A)=0后把0/0直接等于0，或者断言“无解”。
Repair: 分母为零时停止克拉默法则，改查rank(A)和rank([A|b])。
### Teacher-only worked examples
**Question:** A=diag(2,3,4)，b=(4,9,8)，求x。
1. det(A)=24非零。
2. 直接解2x=4、3y=9、4z=8得x=(2,3,2)。
3. 以替换列行列式分别为48、72、48，除24一致。
**Teacher-only answer:** (2,3,2)。
**Question:** x+y=3，y=2，2z=6，求三元解。
1. A=[[1,1,0],[0,1,0],[0,0,2]]，det(A)=2。
2. 第二式y=2，第三式z=3。
3. 第一式x=1，且解唯一。
**Teacher-only answer:** (1,2,3)。
### Student hints without solution
1. 先按行写出系数矩阵，计算det(A)。
2. det(A)=0时立即停止分式并分析秩。
3. 非零时逐列替换常数列，最后把答案代回所有方程。
Near transfer: 对A=[[1,0,0],[0,1,0],[0,0,0]]，b=(1,2,0)解释为何有解但不能用克拉默。
Far transfer: 在三维标定中传感器线性方程重复可能让解不唯一，说明增加独立观测的作用。

## 空间内积和叉积几何意义的非零条件 (ELECTIVE_B)
Editorial source anchor p.60 lines 6-6 (not official atom denominator)
Formal statement: 实三维向量u,v的内积u·v=Σuᵢvᵢ；叉积u×v为垂直于二者的有向向量，满足‖u×v‖=‖u‖‖v‖sinθ，其中θ在u,v均非零时为夹角。
Symbols and domain: 向量坐标u=(u₁,u₂,u₃)，v=(v₁,v₂,v₃)；u·v为标量，u×v为向量。
All hypotheses: 方向和夹角讨论要求两个向量都非零；叉积运算本身可对零向量定义为零。
### Justified steps
1. 内积按坐标求和 — u·v=u₁v₁+u₂v₂+u₃v₃；非零向量时由内积除长度获得cosθ。
2. 按行列式形式展开叉积 — u×v=(u₂v₃−u₃v₂,u₃v₁−u₁v₃,u₁v₂−u₂v₁)。
3. 检查正交和面积解释 — 直接代数可验(u×v)·u=0及(u×v)·v=0，长度等于张成平行四边形的面积。
4. 限制零向量夹角 — 若u=0或v=0，夹角公式分母为零，不能给出θ；叉积则仍为零。
Failure / non-example: 零向量与非零向量内积为0，但夹角没有定义；不能声称一定相互垂直且夹角90度。
Typical incorrect reasoning: 见u·v=0就直接在零向量场景宣称夹角θ=π/2。
Repair: 先验‖u‖‖v‖>0再讨论cosθ；叉积的代数定义与夹角定义分开。
### Teacher-only worked examples
**Question:** u=(1,0,0),v=(0,1,0)，求内积、叉积和夹角。
1. 逐项相乘加总得内积0。
2. 叉积按坐标公式得(0,0,1)。
3. 两向量非零，cosθ=0，因此θ=90度。
**Teacher-only answer:** 内积0，叉积(0,0,1)，夹角90度。
**Question:** u=(1,2,0),v=(2,0,0)，求内积、叉积及平行四边形面积。
1. 内积1·2+2·0=2。
2. 叉积第三分量1·0−2·2=-4，其余为0。
3. 叉积长度4就是面积。
**Teacher-only answer:** 内积2，叉积(0,0,-4)，面积4。
### Student hints without solution
1. 先确定你算的是标量内积还是向量叉积。
2. 按三个分量展开，核查叉积方向和符号。
3. 如果求夹角必须先检查两个向量均非零。
Near transfer: 对u=(1,1,0)、v=(1,-1,0)求叉积并解释其方向。
Far transfer: 航迹控制中用叉积表示法向方向时，为什么零速度向量不能定义唯一朝向。
