# Batch122: source-locked semantic curriculum proposals + full 405-cue audit

All proposals are original, teacher-only REVIEW_PENDING. **The seven-track official atom denominator is still UNKNOWN.**
Automated TOPIC/SUBTOPIC/NUMBERED cue kinds are extraction labels, not official knowledge-atom classifications. Some elective numbered clauses are tagged SUBTOPIC_CUE.

Linked 206/405 layout cues; 199 unlinked; +32 editorial proposals; 175 cumulative proposals.

|Track|Layout cues|Linked|Unlinked|New proposals|All proposals|Official atom denominator|
|---|---:|---:|---:|---:|---:|---|
|COMPULSORY|127|39|88|12|38|UNKNOWN|
|ELECTIVE_A|69|33|36|3|22|UNKNOWN|
|ELECTIVE_B|70|36|34|6|23|UNKNOWN|
|ELECTIVE_C|29|18|11|3|22|UNKNOWN|
|ELECTIVE_D|17|12|5|0|15|UNKNOWN|
|ELECTIVE_E|4|4|0|0|12|UNKNOWN|
|ELECTIVE_UNASSIGNED|0|0|0|0|0|UNKNOWN|
|SELECTIVE_COMPULSORY|89|64|25|8|43|UNKNOWN|

## Cue dispositions (not mathematical atom certification)

- NUMBERED_REQUIREMENT_AWAITING_EDITORIAL_ATOMIZATION: 45
- SOURCE_LINKED_EDITORIAL_CANDIDATE: 206
- SUBTOPIC_CUE_PENDING_CLAUSE_REVIEW: 99
- TOPIC_HEADING_NEEDS_CHILD_SCOPE_REVIEW: 55

## Authored original candidate objectives and failure conditions

### C301 集合的列举法与描述法之间的等价转换
Track: COMPULSORY; kind: method; printed page 15 line 12.
Applicability: 先固定元素的论域与确定性成员判据；列举有限集合时每一元素只能计一次且排列无关
Invalid use: 描述条件不明确时无法确定集合；把无限集合的部分样本枚举当作完整集合不合法

### C302 全集和空集须相对明确的研究论域
Track: COMPULSORY; kind: concept; printed page 15 line 14.
Applicability: 固定当前问题的全集U，空集不含任何元素且空集是所有集合的子集
Invalid use: 空集∅与仅含空集的集合{∅}不同；改变全集后补集可能改变

### C303 集合补集相对全集的元素判断
Track: COMPULSORY; kind: method; printed page 15 line 20.
Applicability: 已知A是全集U的子集，补集U\A由属于U但不属于A的全部元素组成
Invalid use: 未指明全集时不应声称补集唯一；不能把不属于A但也不属于U的对象纳入

### C304 充分必要条件的必要性方向
Track: COMPULSORY; kind: concept; printed page 16 line 8.
Applicability: 在共同论域内若命题P蕴含Q，则Q是P成立的必要条件，必要不代表足够
Invalid use: 只验证一个实例的P与Q都为真不能证明逻辑蕴含；Q成立不推出P成立

### C305 充分条件的正确蕴含方向
Track: COMPULSORY; kind: concept; printed page 16 line 10.
Applicability: 在相同论域和全部允许情形中若P推出Q，则P是Q的充分条件
Invalid use: 不能将P是Q充分条件反写成Q是P充分条件；反向还需另作证明

### C306 充要条件的双向蕴含核验
Track: COMPULSORY; kind: theorem; printed page 16 line 12.
Applicability: 在固定论域内，P与Q等价需证明P⇒Q且Q⇒P两方向全部成立
Invalid use: 仅有P⇒Q不能声称等价，例如x=2充分推出x²=4但不是必要

### C307 分段函数按输入归属分支求值
Track: COMPULSORY; kind: method; printed page 19 line 20.
Applicability: 各分支条件覆盖定义域且重叠处必须得到同一个函数值；给定x先确定有效分支
Invalid use: 将x<0的规则用于x=0会误判端点；分支重叠且不同输出时不定义函数

### C308 函数单调性与极值的区间量词
Track: COMPULSORY; kind: concept; printed page 19 line 22.
Applicability: 给定定义域内的区间I，递增要求任意x1<x2皆满足f(x1)≤f(x2)；严格递增使用严格不等号
Invalid use: 只看两个点值不能证明全区间单调；局部最大值不一定是全局最大值

### C309 指数增长模型底数和时间尺度检查
Track: COMPULSORY; kind: method; printed page 20 line 26.
Applicability: 模型A(t)=A0 a^t取a>0及明确时间单位，增长情形为a>1且A0>0
Invalid use: 底数在0和1之间是衰减；不同时间单位的指数参数不能原样混用

### C310 单位圆三角函数的坐标定义与正切边界
Track: COMPULSORY; kind: concept; printed page 21 line 22.
Applicability: 角θ终边与单位圆交点为(cosθ,sinθ)；仅cosθ≠0时tanθ=sinθ/cosθ
Invalid use: 在θ=π/2处正切未定义，不能把它当作无限大的实数函数值

### C311 连续函数异号端点的零点存在性
Track: COMPULSORY; kind: theorem; printed page 22 line 29.
Applicability: 函数在闭区间[a,b]连续且f(a)f(b)<0，介值定理保证(a,b)至少一个零点
Invalid use: 函数不连续时异号不保证零点；异号只保证存在不保证唯一

### C312 用样本频率近似概率须陈述随机机制
Track: COMPULSORY; kind: method; printed page 31 line 17.
Applicability: 重复试验应有可比较的随机机制；相对频率可作经验概率估计并报告样本量
Invalid use: 对带选择偏差的样本不能直接将频率等同总体真实概率；有限次数不能证明精确值

### S301 空间向量与平面向量分量推广
Track: SELECTIVE_COMPULSORY; kind: concept; printed page 42 line 19.
Applicability: 空间向量以三维有序实数组描述，运算要求固定同一坐标系，零向量有分量但方向未定义
Invalid use: 不同基底的坐标不可未经变换直接相加；零向量无方向不能定义夹角

### S302 方向向量与法向量对直线和平面的约束
Track: SELECTIVE_COMPULSORY; kind: method; printed page 42 line 28.
Applicability: 直线的方向向量必须非零；平面法向量必须非零，向量垂直于平面内两条独立方向
Invalid use: 仅垂直于平面内一条线不能证明是法向量；零向量不能确定唯一方向

### S303 抛物线与双曲线标准方程的参数边界
Track: SELECTIVE_COMPULSORY; kind: concept; printed page 44 line 14.
Applicability: 在标准直角坐标系中，y²=2px取p>0为右开抛物线；x²/a²−y²/b²=1取a,b>0为横轴双曲线
Invalid use: p=0时不再是标准抛物线；双曲线a=0或b=0使方程无定义；不能混淆横纵开口

### S304 伯努利试验的二项分布建模条件
Track: SELECTIVE_COMPULSORY; kind: method; printed page 47 line 23.
Applicability: n次试验相互独立且每次成功概率同为p∈[0,1]时X服从Bin(n,p)
Invalid use: 不放回抽样一般不独立，不能无条件套二项分布；不同p_i也不构成同参数二项

### S305 超几何分布的不放回抽样概率
Track: SELECTIVE_COMPULSORY; kind: method; printed page 47 line 25.
Applicability: 有限总体N个含K个目标，不放回等可能抽n个，X=k的概率为C(K,k)C(N-K,n-k)/C(N,n)
Invalid use: 抽取有放回时概率模型改变；k超出可行范围时概率为0

### S306 正态变量标准化与标准差非零条件
Track: SELECTIVE_COMPULSORY; kind: method; printed page 47 line 28.
Applicability: 若X服从正态N(μ,σ²)且σ>0，则Z=(X-μ)/σ服从N(0,1)
Invalid use: σ=0退化为常数随机变量，不能除以零；未知分布不能仅凭均值方差推断正态

### S307 Pearson样本相关系数的定义域和范围
Track: SELECTIVE_COMPULSORY; kind: concept; printed page 48 line 11.
Applicability: 样本成对数据至少两对且两个变量样本离差平方和均正，r为中心化协方差除以离差积
Invalid use: 任一变量恒定时r分母为零而未定义；r=0不等于统计独立

### S308 比较相关系数须区分关系方向与强度
Track: SELECTIVE_COMPULSORY; kind: method; printed page 48 line 13.
Applicability: 在相同变量定义及可靠成对样本下，|r|衡量线性相关强度而r符号反映方向
Invalid use: 相关系数大小不能直接解释因果性；跨样本比较还应考虑样本量与离群值

### A301 二阶导数存在性与曲率趋势的局部信息
Track: ELECTIVE_A; kind: concept; printed page 53 line 8.
Applicability: 函数一阶导在所研究点的邻域可导时定义f''，f''正负描述切线斜率局部变化趋势
Invalid use: f''(x)=0不必是拐点；f''不存在的点不能被直接归入凹凸判据

### A302 定积分与导数的基本联系及前提
Track: ELECTIVE_A; kind: theorem; printed page 53 line 21.
Applicability: f在[a,b]连续，F为f的一个原函数时积分∫_a^b f(x)dx=F(b)-F(a)
Invalid use: 原函数存在性与端点要明确；不可将不连续奇点上的积分无条件当常规定积分

### A303 空间直线的参数方程与方向退化
Track: ELECTIVE_A; kind: method; printed page 55 line 13.
Applicability: 空间直线L={P0+t v:t∈R}要求固定点P0和非零方向v，坐标分量来自同一基底
Invalid use: v=0时只有一个点；向量式中不可把两个非平行方向误认为同一条直线

### B301 连续函数定积分的有向面积与黎曼和
Track: ELECTIVE_B; kind: concept; printed page 59 line 2.
Applicability: 连续f在有界闭区间[a,b]可积，定积分是带符号累计量；若a≤b规则黎曼和极限为定积分
Invalid use: 曲线位于轴下方时积分为负，不能当作非负几何面积；颠倒积分端点必须改符号

### B302 二元驻点候选与边界极值分开核查
Track: ELECTIVE_B; kind: method; printed page 59 line 16.
Applicability: 可微二元函数的内部局部极值必有∇f=0，紧约束域求全局极值还要考虑全部边界
Invalid use: 驻点不一定是极值（如xy在原点）；仅有内点一阶条件不能取代边界分析

### B303 三元齐次线性方程组的自由变量
Track: ELECTIVE_B; kind: method; printed page 60 line 21.
Applicability: 实矩阵A的齐次系统Ax=0总有零解，非零解存在当且仅当rank(A)<变量数
Invalid use: 把存在零解当作唯一解或非平凡解均错误；行消元需保持等价变换

### EC301 指数情景模型的正值性与参数校准
Track: ELECTIVE_B; kind: method; printed page 63 line 20.
Applicability: 连续时间模型y(t)=A exp(kt)取A>0，k单位为时间倒数；参数估计需至少两组兼容观测
Invalid use: A≤0或负预测与正值情景不匹配；指数增长不能外推到资源限制下的无限时间

### EC302 弹道参数方程的理想化假设
Track: ELECTIVE_B; kind: method; printed page 64 line 6.
Applicability: 无空气阻力且重力加速度g>0恒定，位置x(t)=x0+v0x t、y(t)=y0+v0y t-gt²/2
Invalid use: 有阻力或变量g时不能照搬抛物线轨迹；求落地时间需限制t≥0

### EC303 螺旋线参数方程与单位一致性
Track: ELECTIVE_B; kind: method; printed page 64 line 7.
Applicability: 标准螺旋线可写(r cos t,r sin t,c t)，r>0并规定角参数以弧度计
Invalid use: r=0退化为轴线；z方向线性增量与水平角运动不能混为同一长度单位

### ED301 调查方案明确总体和抽样框的设计
Track: ELECTIVE_C; kind: method; printed page 68 line 8.
Applicability: 研究问题、目标总体、抽样框、抽样方法和测量指标均应先约定并记录
Invalid use: 抽样框遗漏目标群体会造成覆盖偏差，即使样本量很大也不会自动消失

### ED302 社会调查可行性评估的约束与风险
Track: ELECTIVE_C; kind: method; printed page 68 line 10.
Applicability: 在组织调查前检查成本、期限、可访问对象、拒答风险、隐私告知与数据质量
Invalid use: 不允许把无响应数据任意补齐当作真实观察，缺失机制未知时总体估计有风险

### ED303 观察访谈问卷的测量偏差区别
Track: ELECTIVE_C; kind: method; printed page 68 line 13.
Applicability: 按研究问题选用观察、访谈或问卷，并记录采集方式、题项、允许的回答范围
Invalid use: 诱导性问题、观察者效应和非随机响应均可能造成偏差，不能只靠样本数抵消


Parser source-tag audit: 20 NUMBERED_REQUIREMENT_CUE; 12 SUBTOPIC_CUE/TOPIC_CUE. This is a regex extraction tag, NOT a human judgment that these are mere headings.

## Verification boundaries

- Local legal-source text stays only on the Mac, digest/source span is frozen, each candidate links an exact source cue, explicitly distinguishing headings from numbered requirements.
- The line-level source witness is not a semantic correctness certification; visual/formula flags remain review requirements.
- No machine generated teaching approvals, no authoritative student indexing, no unsupported general proof claims.
