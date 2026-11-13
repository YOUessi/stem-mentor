# Batch129 — nine full original mathematics review manuscripts

All worked solutions are TEACHER_ONLY and REVIEW_PENDING. No teacher signature, universal theorem certificate or student authority.
Independent exact examples: 18; invalid condition checks: 9; cross topic checks: 9.

## 余弦定理的边角关系 (COMPULSORY)
Source: printed p.26, lines 23-25
Formal statement: 在非退化三角形中，若两边长a,b夹角为γ，第三边长c，则c²=a²+b²−2ab cosγ；该式可用于给定SAS求第三边，也可在三边满足三角不等式后反求夹角。
Symbols: a,b,c为严格正的实数边长，γ为两边a,b间的内角，0<γ<π，cosγ是角γ的余弦值。
Preconditions: 三条边构成非退化欧氏平面三角形；计算夹角时只在对应的边长已知且正、满足严格三角不等式后才能逆用余弦。
Why/how: 以夹角顶点为公共原点，取两个邻边向量u,v，模为a,b且夹角γ；第三边向量为u−v，模为c。展开(u−v)·(u−v)=a²+b²−2u·v，再由u·v=ab cosγ得到结论；逆用时cosγ=(a²+b²−c²)/(2ab)。
### Reasoned mathematical steps
1. 建立向量模型 — 两邻边必须由同一顶点发出，第三边才能用其差向量表示。
2. 展开平方范数 — 利用内积的双线性和对称性，不能误将模的平方直接作差。
3. 核对角度和退化 — 若用三边反求夹角，先检查a,b>0、三角形严格不等式及反余弦值范围。
Boundary/nonexample: 若a=2,b=3,c=5，三边只构成退化线段，γ=π不是非退化三角形内角；不能当作合法三角形例题。
Common wrong solution: 典型错误：夹角60°、两邻边5和7，直接计算第三边为5²+7²−2×5×7×cos60°=39。
Why wrong and repair: 公式右侧是c²而非c，第三边必须为正平方根√39，不能遗漏开平方。
### Verified controlled teacher examples
- 某三角形两邻边长5、7，夹角60°，求第三边。
  - c²=25+49−70×(1/2)=39。
  - 边长为正，故c=√39。
  - Answer: √39; independent check: SAS内积展开给出长度平方39，再取正根。
- 三角形边长3、4、5，求3和4所夹角。
  - cosγ=(3²+4²−5²)/(2×3×4)=0。
  - γ为0到π之间的内角，故γ=90°。
  - Answer: 90°; independent check: 勾股关系与余弦0完全一致。
### Student hint ladder (no full answer)
1. 识别给定的是两边及夹角，还是三边。
2. 把角放在两条已知邻边之间，写对第三边的余弦式。
3. 先算边长平方，最后检查正平方根或角度范围。
Near transfer: 给定邻边6、8且夹角120°，求第三边并比较与夹角60°的结果。
Far transfer: 无人机按两条航线组成的三角形测量距离时，解释方向角误差如何影响根据余弦定理得到的距离。

## 分层随机抽样按层比例分配样本 (COMPULSORY)
Source: printed p.32, lines 14-17
Formal statement: 将有限总体按互不重叠且合并为全集的H层分组，第h层总体量N_h，总体N=ΣN_h；按比例配置样本n_h≈nN_h/N，并以总体权重W_h=N_h/N加权各层均值。
Symbols: H为层数，N_h为层总体数，n_h为层样本数，N为总量，n为目标样本数；层均值为x̄_h，W_h为总体层权重。
Preconditions: 各层互不重叠且完整覆盖目标总体，层内按给定抽样设计随机选取；比例配置的n_h必须为非负整数，且Σn_h=n；计算均值权重用总体比例而不是随意使用样本比例。
Why/how: 总体所有数值之和可以按层拆成Σ_h N_h μ_h；两边除以N得总体均值μ=Σ_h W_h μ_h。以各层样本均值代入得到估计量Σ_h W_h x̄_h；分层样本量比例分配可减少层覆盖不均，但不是无需随机性的许可证。
### Reasoned mathematical steps
1. 定义总体与层 — 先核实层的并集为总体且两两不交，不能漏掉不愿作答的群体。
2. 确定抽样配额 — 由nN_h/N计算理想份额，整数舍入后必须核对总样本量。
3. 按总体权重合并 — 明确估计对象是总体均值；权重来自N_h/N，避免把层均值直接平均。
Boundary/nonexample: 若两层总体量10与90、计划样本量1，则按比例计算0.1与0.9都不是合法整数；不能声称每层严格按比例抽0.1个人。
Common wrong solution: 典型错误：两层人数40和60，各层样本均值12和18，简单算(12+18)/2=15作为总体均值。
Why wrong and repair: 两层总体权重不相等，必须使用0.4×12+0.6×18=15.6；若设计为不等比例样本也不能直接平均两层均值。
### Verified controlled teacher examples
- 40人与60人两个层，分别抽8与12人，两层样本均值12与18，求分层均值估计。
  - 总体层权重是40/100和60/100，样本分配8+12=20符合比例。
  - 加权均值为(2/5)×12+(3/5)×18=78/5。
  - Answer: 15.6; independent check: 总体权重计算为4.8+10.8。
- 两个互斥层规模30、70，抽样10人按比例分配并得到均值2和5，求总体均值估计。
  - 抽样配额为3和7，权重3/10和7/10。
  - 估计均值(3/10)×2+(7/10)×5=41/10。
  - Answer: 4.1; independent check: 分层规模分别对应30%与70%。
### Student hint ladder (no full answer)
1. 先列出所有层及各层总体数量。
2. 检查层权重之和是否为1，样本量整数之和是否正确。
3. 使用总体人数作为加权系数分母。
Near transfer: 三层人数20、30、50，样本量20，分别得到均值3、5、7，计算分层均值。
Far transfer: 学校不同年级参与率差异很大时，解释分层抽样为何可以改善代表性，以及未回应偏差仍可能存在。

## 条件概率及事件独立的区别 (SELECTIVE_COMPULSORY)
Source: printed p.47, lines 12-16
Formal statement: 在同一概率空间中，若P(B)>0，事件A在条件B下的概率定义为P(A|B)=P(A∩B)/P(B)；当P(A∩B)=P(A)P(B)时称A、B独立。互斥是集合条件A∩B=∅，不可与独立混淆。
Symbols: A,B是同一概率空间中的事件，P表示概率，∩表示同时发生，条件符号|表示在B发生的前提下。
Preconditions: 计算P(A|B)需P(B)>0；有限古典概型按计数计算还要要求所有基本结果等可能；独立判据不要求条件分母在其乘积等式中出现。
Why/how: 因为B已发生，样本范围限制在B内，满足A的部分恰为交集A∩B；再以P(B)作归一化得到条件概率。若A与B独立且P(B)>0，代入乘积判据得P(A|B)=P(A)，反之也成立。
### Reasoned mathematical steps
1. 明确条件事件 — 条件事件B必须严格正概率，不可把B等同于需要求概率的A。
2. 找交集 — 同时满足A与B才计入条件分子的概率，有限等可能时可数样本点。
3. 归一化及判独立 — 以P(B)而不是P(A)除，独立需要再比较乘积判据。
Boundary/nonexample: 若P(B)=0，P(A∩B)/P(B)分母为零，不能把条件概率写为0；两互斥正概率事件不能独立。
Common wrong solution: 典型错误：A为骰子结果大于3，B为偶数，看到A与B有共同点就断言两事件独立。
Why wrong and repair: 有交集不代表独立，须核对P(A∩B)是否等于P(A)P(B)；这里交集2/6，乘积(3/6)(3/6)=1/4，不相等。
### Verified controlled teacher examples
- 公平骰子，A为点数大于3，B为偶数，计算P(A|B)。
  - B={2,4,6}，交集A∩B={4,6}。
  - P(A|B)=(2/6)/(3/6)=2/3。
  - Answer: 2/3; independent check: 条件B下3个等可能结果，其中2个满足A。
- 两次独立公平硬币，B表示第一次正面，A表示至少一次正面，求P(A|B)。
  - Ω={HH,HT,TH,TT}且B={HH,HT}。
  - A∩B=B，因此P(A|B)=P(B)/P(B)=1。
  - Answer: 1; independent check: 知道首枚为正面就已确保至少一次正面。
### Student hint ladder (no full answer)
1. 先确定条件事件是哪一个，确认其概率非零。
2. 写出交集与条件事件的概率。
3. 把交集概率除以条件事件概率，再判断是否有独立性。
Near transfer: 公平骰子A为奇数、B为小于4，求P(A|B)并核对是否独立。
Far transfer: 医学检测中一个阳性结果改变了样本空间；解释为何条件概率不同于无条件患病率。

## 全概率与贝叶斯更新的分母条件 (SELECTIVE_COMPULSORY)
Source: printed p.47, lines 16-19
Formal statement: 设B_1,...,B_k是概率空间的两两互斥且合并为全集的划分，P(B_i)>0；对于P(A)>0，贝叶斯公式P(B_j|A)=P(A|B_j)P(B_j)/Σ_i P(A|B_i)P(B_i)，分母就是由全概率公式得到的P(A)。
Symbols: A为观测证据事件，B_i为互斥穷尽的原因分组；P(B_i)为先验，P(A|B_i)为似然，P(B_j|A)为后验。
Preconditions: 所有B_i构成完整划分并有正概率以定义各似然；观测A须P(A)>0；模型中的先验和似然必须在同一概率空间且定义一致。
Why/how: A∩Ω可按互斥划分写为互不相交的A∩B_i，因此P(A)=Σ_iP(A∩B_i)=Σ_iP(A|B_i)P(B_i)。再把条件概率P(B_j|A)=P(A∩B_j)/P(A)化简得贝叶斯式。
### Reasoned mathematical steps
1. 列出原因划分 — 先验互斥、覆盖全集，不能漏掉对照群体。
2. 算每个原因对证据的贡献 — 用似然乘先验而不是把检测结果直接解释为疾病概率。
3. 除以证据总概率 — 将全部贡献相加成非零分母，检查后验落在0与1之间。
Boundary/nonexample: 若P(A)=0，观察A后的条件概率无定义；若检测试验的灵敏度与误报率没有条件定义，也不能机械套公式。
Common wrong solution: 典型错误：某病阳性灵敏度90%，观察阳性就认为患病概率90%，完全忽略先验和假阳性率。
Why wrong and repair: 灵敏度是P(阳性|患病)，目标是P(患病|阳性)，两者条件方向相反且大小可能差很大。
### Verified controlled teacher examples
- 患病率1/10，灵敏度9/10，非患病误报率1/5，求阳性后患病概率。
  - 阳性且患病为(1/10)(9/10)=9/100；阳性且不患病为(9/10)(1/5)=18/100。
  - 后验=(9/100)/(27/100)=1/3。
  - Answer: 1/3; independent check: 贝叶斯分子9/100，归一化分母27/100。
- 先选A箱概率2/5，其抽红概率3/4；选B箱概率3/5，其抽红概率1/3，已抽红求来自A箱概率。
  - A且红为(2/5)(3/4)=3/10，B且红为(3/5)(1/3)=1/5。
  - P(A箱|红)=(3/10)/(3/10+1/5)=3/5。
  - Answer: 3/5; independent check: 红球总概率1/2，A贡献3/10。
### Student hint ladder (no full answer)
1. 先把可能原因列成互斥完备类别。
2. 把每类的先验乘对应证据似然。
3. 分母是所有类别贡献之和，不是先验概率之和。
Near transfer: 患病率1/100，灵敏度99/100，假阳性率1/10，计算一次阳性后的患病率。
Far transfer: 面对机器故障日志的报警，解释基率不平衡如何影响报警的正预测值与排障优先级。

## 三元线性方程组的高斯消元 (ELECTIVE_A)
Source: printed p.55, lines 2-4
Formal statement: 有限的三元线性方程组Ax=b可用增广矩阵[A|b]作高斯消元：行交换、行乘非零标量、某行加另一行的倍数都保持解集；最终依据系数秩和增广秩判别有解与唯一性。
Symbols: A为实数3×3系数矩阵，x为三个未知数列向量，b为实数常数列，rank表示矩阵秩。
Preconditions: 每个变换必须是可逆的初等行变换，行缩放系数不可为零；若出现[0,0,0|c]且c≠0则无解，不能只看最后一行有零就认定无穷多解。
Why/how: 行操作对应方程互换、非零倍数缩放和方程线性组合，逆操作存在故解集不变。若消元后每个未知量都有主元，则存在唯一解；系数秩小于增广秩则出现0=c矛盾。
### Reasoned mathematical steps
1. 构造增广矩阵 — 将系数列与常数列对齐；右侧不能跟着未知数一起做列操作。
2. 进行可逆行消元 — 优先使用行加倍数，必要时换行；行乘因子必须非零。
3. 回代并核对原方程 — 读出主元与自由变量；将求得的解代回全部原方程，而非只核对末行。
Boundary/nonexample: 方程x+y=1与2x+2y=3不相容；若把第二行随意乘0会伪造零行并失去无解的证据。
Common wrong solution: 典型错误：遇到主元为零就把该行乘以0来得到一行零，声称矩阵已经简化。
Why wrong and repair: 乘0不属于可逆行变换，会丢失原来的约束。必须换行或利用其它行的非零元作为主元。
### Verified controlled teacher examples
- 解x+y+z=6、x−y+z=2、x+y−z=0。
  - 第一式减第二式得2y=4，故y=2；第一式减第三式得2z=6，故z=3。
  - 代入第一式x=6−2−3=1。
  - Answer: x=1,y=2,z=3; independent check: 代回三式分别为6、2、0。
- 解x+y+z=3、x−y+z=1、x+y−z=1。
  - 相减得到2y=2和2z=2，故y=z=1。
  - 代入第一式得到x=1。
  - Answer: x=1,y=1,z=1; independent check: 代回三式分别为3、1、1。
### Student hint ladder (no full answer)
1. 先写清每个未知量对应矩阵哪一列。
2. 找出能消掉同一未知数的两行并做减法。
3. 求出两个变量后回代，并逐个核对全部等式。
Near transfer: 解x+2y+z=7、2x+y+z=8、x+y+2z=9并用矩阵秩检查唯一性。
Far transfer: 机器人三方向力的线性平衡模型若测量方程线性相关，解释为何可能不能识别唯一的三维力。

## 矩估计与似然估计的参数约束 (ELECTIVE_B)
Source: printed p.62, lines 5-7
Formal statement: 在独立同分布伯努利观测X_i∈{0,1}、未知参数p∈[0,1]下，似然函数L(p)=p^k(1−p)^(n−k)，k=ΣX_i；最大似然估计为p̂=k/n。对于k=0或k=n，最大值位于边界，不能只用内部导数求解。
Symbols: n为正整数样本数，k为成功次数，p为成功概率，p̂为估计值；L为观察到该具体样本的概率函数。
Preconditions: 样本须在给定p条件下独立且采用同一伯努利分布；p的参数域为闭区间[0,1]，真实样本不含隐私信息；样本相关性会破坏所用似然形式。
Why/how: 似然为∏p^{X_i}(1−p)^{1−X_i}。当0<k<n，内部对数导数k/p−(n−k)/(1−p)=0，解为k/n，二阶导负；当k=0或n，直接比较单调性得到边界p̂=0或1。
### Reasoned mathematical steps
1. 声明模型及参数域 — 首先核实每个观察只能取0或1且独立同分布，参数p在闭区间。
2. 写完整似然 — 指数k和n−k分别来自成功与失败个数；不可把顺序样本误写成不同参数。
3. 求最大值并审查边界 — 内部解为k/n；k为0或n时必须直接检查p=0或p=1。
Boundary/nonexample: 所有观测为0时，内部方程k/p−(n−k)/(1−p)=0没有有效内部解，但最大似然仍为边界p=0。
Common wrong solution: 典型错误：三次观测全部失败，导数法得不到内部驻点，就宣布不存在最大似然估计。
Why wrong and repair: 可行参数是闭区间[0,1]，边界取得的最大值合法；求导为零仅用于内部候选点。
### Verified controlled teacher examples
- 伯努利独立样本为1,1,0,1，求成功率最大似然估计。
  - 统计n=4，k=3，写似然L(p)=p³(1−p)。
  - 内部对数似然最优在p=k/n=3/4。
  - Answer: 3/4; independent check: L(3/4)=27/256，二阶导为负且端点似然为0。
- 三次伯努利独立样本全为0，求最大似然估计。
  - n=3，k=0，似然L(p)=(1−p)³。
  - 该函数在[0,1]上单调递减，最大在p=0。
  - Answer: 0; independent check: L(0)=1，任何p>0的似然小于1。
### Student hint ladder (no full answer)
1. 先统计样本总数和成功次数。
2. 不要忘记p只能在0到1之间。
3. 内部用k/n，全部成功或失败时单独检查边界。
Near transfer: 对样本0,1,0,1,0,1求伯努利最大似然估计并解释其不代表真实参数已被证明。
Far transfer: 对在线系统的失败率估计，分析一小时的调用成功失败是否真正独立同分布，哪些时段效应会使模型失效。

## 人口指数增长拟合与模型外推失效 (ELECTIVE_C)
Source: printed p.67, lines 8-11
Formal statement: 理想连续指数增长模型N(t)=N_0 exp(rt)中，N_0>0为初始规模，r为固定的单位时间增长率，t为相同时间单位的非负自变量；若r>0则严格增长，若r=0则常量。
Symbols: N(t)为时刻t的规模，N_0为初始规模，r量纲为每单位时间，exp为自然指数函数。
Preconditions: 模型假定增长速度与现有规模成正比且r在所讨论期间不变；有限资源、迁移、政策和时变出生死亡率会使长时间指数外推失效。
Why/how: 从微分方程dN/dt=rN分离变量得dN/N=r dt，在N>0的区间积分得ln N=rt+C，由初始条件得C=ln N_0，于是N=N_0 e^{rt}。如每T单位时间翻倍，则e^{rT}=2，即r=ln2/T。
### Reasoned mathematical steps
1. 明确规模及时间单位 — 把初值、时间与增长率的量纲放在同一单位体系，非物理的负规模不允许。
2. 由倍增时间推率 — 若给的是翻倍周期T，先算r=ln2/T再代入。
3. 做模型现实边界检查 — 计算值只代表既定恒定率模型的预测，不把样本拟合当作无限期因果规律。
Boundary/nonexample: 当资源容量有限且靠近饱和水平时，恒定比例增长可能明显失效，不能把指数拟合短期很好解释为无限期持续翻倍。
Common wrong solution: 典型错误：一座城市三年人口翻倍，所以不论未来几十年的政策和迁移如何都每三年精确翻倍。
Why wrong and repair: 指数函数的结论是条件推论，现实人口受到容量和时变参数制约；拟合不能独立验证全部长期假设。
### Verified controlled teacher examples
- 指数模型初值100，每3年翻倍，求第3年与第6年模型值。
  - 增长率r=ln2/3，因此N(3)=100 exp(ln2)=200。
  - N(6)=100 exp(2ln2)=400。
  - Answer: N(3)=200,N(6)=400; independent check: 指数恒等式e^(ln2)=2。
- 理想初值50，每2单位时间翻倍，求t=4时模型值。
  - 增长率r=ln2/2。
  - N(4)=50exp(2ln2)=50×4=200。
  - Answer: 200; independent check: 连续增长公式在两轮倍增时给出4倍。
### Student hint ladder (no full answer)
1. 先写清初始值和时间的单位。
2. 把翻倍间隔转成指数增长率ln2/T。
3. 指数值算完后再讨论预测与实测的偏差。
Near transfer: 某理想人口模型N(0)=80，4年翻倍，求N(10)的精确表达式。
Far transfer: 结合环境承载上限，讨论何时需要改用带容量参数的Logistic模型，并说明新模型应重新验证。

## 节拍周期与最小公倍数的同步分析 (ELECTIVE_D)
Source: printed p.71, lines 5-7
Formal statement: 两种严格周期节拍T_1,T_2>0若T_1/T_2是有理数，则存在共同正周期；对于正有理数秒的节拍，可先化成共同分母T_i=m_i/D，最短同步时间为lcm(m_1,m_2)/D。
Symbols: T_1,T_2为正的节拍时长，D为共同的正整数时间单位分母，m_1,m_2为正整数计数，lcm为最小公倍数。
Preconditions: 要求两个节拍在同一时间原点开始并使用同一单位，且节拍严格周期重复；若比例为无理数，正整数倍节拍永远不能精确重合。
Why/how: 同步时间同时为T_1和T_2的正整数倍：t=kT_1=ℓT_2。换成共同分母后k m_1=ℓ m_2，最小正整数共同值为最小公倍数，故t=lcm(m_1,m_2)/D。
### Reasoned mathematical steps
1. 统一时间单位 — 先把分数节拍转换成同一分母，不能直接取分数分子最大值。
2. 求最小共同整数倍 — 分别列出节拍整数倍或使用最小公倍数，确保是最小正同步时刻。
3. 检查严格周期条件 — 采样误差、节拍漂移和无理数比值会改变是否真正重复。
Boundary/nonexample: 若T_1=1秒，T_2=√2秒，整数k=ℓ√2在正整数k,ℓ下不成立，所以没有有限正的精确同步时间。
Common wrong solution: 典型错误：节拍3/4秒和1/2秒直接取分母最小公倍数4秒作为最短重合时刻。
Why wrong and repair: 分母并不是节拍长度；统一分母4后，节拍为3/4与2/4，最小共同分子为lcm(3,2)=6，故同步为6/4秒。
### Verified controlled teacher examples
- 两个节拍周期分别为3/4秒与1/2秒，从同一时刻开始，求最早再同步时间。
  - 用共同分母4写成3/4与2/4秒。
  - lcm(3,2)=6，最小同步时间6/4=3/2秒。
  - Answer: 3/2秒; independent check: 两个节拍在1.5秒分别完成2次和3次。
- 两个节拍周期分别为2/3秒与4/5秒，求最早再同步时间。
  - 共同分母15，节拍为10/15与12/15秒。
  - lcm(10,12)=60，所以最早同步60/15=4秒。
  - Answer: 4秒; independent check: 4秒分别包含6个2/3秒与5个4/5秒。
### Student hint ladder (no full answer)
1. 先确保两种节拍都用秒作单位。
2. 将两个有理数节拍变成相同分母。
3. 对两个分子求最小公倍数，再除以共同分母。
Near transfer: 周期5/6秒和2/3秒的两声部何时首次重新同步？
Far transfer: 合奏中两个乐手节拍略有随机漂移时，说明理论最小公倍数与观测同步误差的区别。

## 家庭理财复利和通胀单位示例 (ELECTIVE_E)
Source: printed p.73, lines 18-18
Formal statement: 理想固定利率复利模型A_n=P(1+i)^n：P>0为初始本金，i>−1为每计息周期的有效利率，n为非负整数计息周期数；选修E家庭理财只是学校可选教学情境，并非全国必修原子。
Symbols: P为本金，A_n为第n个完整计息周期后的名义金额，i为每周期有效利率，n为计息次数。
Preconditions: 必须注明计息周期和利率的相同单位，假设每期利率固定且利息留存本金；手续费、税收、提前取款、通胀都未包含在理想公式中。
Why/how: 每期末本金与既有利息共同乘(1+i)，有A_{k+1}=A_k(1+i)。从A_0=P递推n次得A_n=P(1+i)^n；若讨论实际购买力，还须独立给定每期物价因子。
### Reasoned mathematical steps
1. 确定利率和计息周期 — 年利率不能直接乘以月份数代入指数，先明确每期的有效利率。
2. 按递推复利 — 每一期新增利息都计入下一期本金，因而是乘方而非线性累加。
3. 检查现实解释 — 报告名义金额时不能默认扣掉费用或已调整通胀。
Boundary/nonexample: 名义年利率10%与每月复利10%不是同一利率；即使名义金额增加，通胀很高时购买力可能下降。
Common wrong solution: 典型错误：1000元每期利率10%，连续两期直接用1000×(1+2×0.1)=1200元。
Why wrong and repair: 简单利息的线性相加忽略第一期利息也参与第二期计息；复利应得到1000×1.1²=1210元。
### Verified controlled teacher examples
- 本金1000元，每期有效利率10%，全部复利两期，求名义本息。
  - 每期因子为11/10，连续两期金额=1000×(11/10)²。
  - 1000×121/100=1210元。
  - Answer: 1210元; independent check: 第二期以1100元而不是1000元计息。
- 本金800元，每期有效利率25%，连续3期复利，求名义金额。
  - 每期因子为5/4，金额800×(5/4)³。
  - 800×125/64=3125/2元。
  - Answer: 1562.5元; independent check: 精确乘方为125/64，乘800得1562.5。
### Student hint ladder (no full answer)
1. 先写明本金P和利率对应的一个计息周期。
2. 每期金额都乘同一个1+i。
3. 最终用乘方而不是把每期利率简单相加。
Near transfer: 某学校自选理财活动以本金2000元、有效季利率2%、持续6季为题，求名义金额并解释费用未计入。
Far transfer: 给定名义增长率与不同的通胀率，设计真实购买力模型并指出市场条件变化时固定复利模型不能保证收益。
