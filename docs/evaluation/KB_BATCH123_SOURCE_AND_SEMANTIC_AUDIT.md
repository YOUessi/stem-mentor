# Batch123: source-locked semantic curriculum proposals + full 405-cue audit

All proposals are original, teacher-only REVIEW_PENDING. **The seven-track official atom denominator is still UNKNOWN.**
Automated TOPIC/SUBTOPIC/NUMBERED cue kinds are extraction labels, not official knowledge-atom classifications. Some elective numbered clauses are tagged SUBTOPIC_CUE.

Linked 238/405 layout cues; 167 unlinked; +32 editorial proposals; 207 cumulative proposals.

|Track|Layout cues|Linked|Unlinked|New proposals|All proposals|Official atom denominator|
|---|---:|---:|---:|---:|---:|---|
|COMPULSORY|127|51|76|12|50|UNKNOWN|
|ELECTIVE_A|69|38|31|5|27|UNKNOWN|
|ELECTIVE_B|70|41|29|5|28|UNKNOWN|
|ELECTIVE_C|29|20|9|2|24|UNKNOWN|
|ELECTIVE_D|17|14|3|2|17|UNKNOWN|
|ELECTIVE_E|4|4|0|0|12|UNKNOWN|
|ELECTIVE_UNASSIGNED|0|0|0|0|0|UNKNOWN|
|SELECTIVE_COMPULSORY|89|70|19|6|49|UNKNOWN|

## Cue dispositions (not mathematical atom certification)

- NUMBERED_REQUIREMENT_AWAITING_EDITORIAL_ATOMIZATION: 33
- SOURCE_LINKED_EDITORIAL_CANDIDATE: 238
- SUBTOPIC_CUE_PENDING_CLAUSE_REVIEW: 81
- TOPIC_HEADING_NEEDS_CHILD_SCOPE_REVIEW: 53

## Authored original candidate objectives and failure conditions

### C401 使用韦恩图核对集合交并补的成员关系
Track: COMPULSORY; kind: method; printed page 15 line 22.
Applicability: 同一个全集内讨论两个集合，图内每一位置表示确定的成员判据，阴影同时满足相应逻辑运算规则
Invalid use: 交集只取同时属于两者的元素；误把A或B中的所有位置涂成交集会造成多算

### C402 全称命题的否定由存在反例表达
Track: COMPULSORY; kind: method; printed page 16 line 18.
Applicability: 量词在已固定的非空论域内解释，否定任意x均满足P(x)等价于存在x不满足P(x)
Invalid use: 把全称否定写成所有x均不满足P会强化命题；仅举例验证不能证明全称陈述

### C403 二次函数符号图解一元二次不等式
Track: COMPULSORY; kind: method; printed page 17 line 13.
Applicability: 实系数二次式ax²+bx+c中a≠0，解不等式要按判别式及开口方向区别并保留端点取等条件
Invalid use: 判别式负时不能凭空画出两个实根；二次项系数为负时不能套用向上开口的符号表

### C404 函数奇偶性须在关于原点对称的定义域上判断
Track: COMPULSORY; kind: concept; printed page 19 line 24.
Applicability: 实函数定义域D满足x∈D当且仅当−x∈D，偶函数要求f(−x)=f(x)，奇函数要求f(−x)=−f(x)
Invalid use: 仅在x≥0定义的函数不应未经扩展就称为奇函数；f(0)存在的奇函数必满足f(0)=0

### C405 周期函数的非零周期与最小正周期区别
Track: COMPULSORY; kind: concept; printed page 19 line 25.
Applicability: 实函数f在定义域D上的周期T必须非零且每个允许x满足x+T仍在D和f(x+T)=f(x)
Invalid use: 常数函数任意正数均可作周期，但不存在最小正周期；局部重复不足以证明全域周期性

### C406 实数范围有理数指数幂的底数和根式条件
Track: COMPULSORY; kind: method; printed page 20 line 21.
Applicability: 通常a>0时定义a^(m/n)为正n次根的m次幂，其中m为整数且n为正整数；零与负底数另行审查
Invalid use: 不允许将负数的偶次实根视为实数；a=0时负指数无定义，不能直接使用正底数通式

### C407 对数换底公式的底数合法性核验
Track: COMPULSORY; kind: method; printed page 20 line 32.
Applicability: 对数log_a(x)的实数定义要求a>0且a≠1、x>0；换底底数b也要求b>0且b≠1
Invalid use: 对x≤0取实对数无意义；把log_a(x)误写为log_b(x)log_b(a)属于倒置换底

### C408 弧度制下弧长与角度的量纲约定
Track: COMPULSORY; kind: concept; printed page 21 line 18.
Applicability: 半径r>0的圆中圆心角θ以弧度计时有有向弧长s=rθ，计算非有向弧长应取|rθ|
Invalid use: 把角度值90直接代入弧度公式会得到错误弧长；零半径无法定义该圆上的中心角

### C409 两角和差三角函数公式的推导与全实数角适用范围
Track: COMPULSORY; kind: theorem; printed page 22 line 14.
Applicability: 角α、β均为实数，正弦与余弦加减公式对所有实数角成立；推导时不需要对cosα或cosβ做除法
Invalid use: 从含正切的公式推导时必须另行排除分母为零情形；不得把sin(α+β)写为sinα+sinβ

### C410 二分法保留异号端点的近似零点算法
Track: COMPULSORY; kind: method; printed page 22 line 27.
Applicability: 实函数在[a,b]连续且f(a)f(b)<0，每轮取中点并保留仍异号的闭半区间，误差界随区间长度减半
Invalid use: 若函数存在跳跃不连续，则异号不能保证区间内有零点；不应把数值近似当作唯一根的证明

### C411 有限等可能样本空间上的古典概率计数
Track: COMPULSORY; kind: method; printed page 31 line 14.
Applicability: 样本空间有限且各基本结果概率相同，事件A概率为有利结果数除以总体基本结果数
Invalid use: 不等可能结果不能只用数量之比；事件样本点必须不重不漏，不能遗漏有序性或重复计数

### C412 样本均值中位数众数估计总体位置的限制
Track: COMPULSORY; kind: method; printed page 32 line 25.
Applicability: 随机样本与目标总体对应且数据测量方式一致，均值、中位数与众数分别描述不同位置特征
Invalid use: 重尾或离群值可使均值与中位数偏离；样本统计量不等于未知总体参数的精确值

### S401 空间三线性无关向量的坐标唯一分解
Track: SELECTIVE_COMPULSORY; kind: theorem; printed page 42 line 21.
Applicability: 空间中三个不共面的向量组成一组基，任一空间向量可唯一写成这三个向量的实系数线性组合
Invalid use: 若三个向量共面或有一个为零则不构成基，系数可能不唯一也可能不能表示目标向量

### S402 直线圆位置判断的圆心到直线距离法
Track: SELECTIVE_COMPULSORY; kind: method; printed page 44 line 8.
Applicability: 圆心(x0,y0)、半径r>0，直线Ax+By+C=0须有(A,B)≠(0,0)；比较d=|Ax0+By0+C|/√(A²+B²)与r
Invalid use: 当A=B=0时不是直线，距离公式分母为零；d=r只表明切线，交点计算仍需满足两方程

### S403 离散型随机变量分布列的归一与非负性
Track: SELECTIVE_COMPULSORY; kind: concept; printed page 47 line 20.
Applicability: 离散随机变量的所有可取值概率pk≥0，所有可取值覆盖完整样本空间且Σpk=1
Invalid use: 遗漏取值导致概率和小于1时不是完整分布列；把密度直接当作某点概率会混淆离散与连续

### S404 正态分布均值与方差的参数意义
Track: SELECTIVE_COMPULSORY; kind: concept; printed page 48 line 3.
Applicability: X∼N(μ,σ²)要求σ>0，均值μ为对称中心，方差σ²表示波动尺度而非每次偏离的固定距离
Invalid use: 任意同均值方差变量不必服从正态；σ=0时退化成常量，不可继续使用标准正态密度公式

### S405 成对数据线性相关性与异常值影响
Track: SELECTIVE_COMPULSORY; kind: method; printed page 48 line 10.
Applicability: 数据以(x_i,y_i)成对采集并保持同一对象配对，可通过散点图和相关系数探索线性关联
Invalid use: 孤立异常点可显著改变Pearson系数；相关系数接近零并不能排除显著的非线性关系

### S406 正态概率区间换元使用标准差非零前提
Track: SELECTIVE_COMPULSORY; kind: method; printed page 47 line 27.
Applicability: 已知X服从N(μ,σ²)且σ>0时，事件a≤X≤b可换算到标准正态区间，其中先确保a≤b
Invalid use: 若区间端点反序则概率为零；没有正态假设时不能仅依均值方差查标准正态表

### A401 函数极限四则运算须有各项有限极限
Track: ELECTIVE_A; kind: theorem; printed page 52 line 39.
Applicability: x趋近同一极限点时f、g分别具有有限极限L、M，加减乘成立；商法则另需M≠0
Invalid use: 若分母极限为零则不能直接使用商法则；无穷极限与不存在极限不能套作有限四则

### A402 导数驻点和区间边界共同确定全局最值
Track: ELECTIVE_A; kind: method; printed page 53 line 15.
Applicability: 函数在紧区间连续且在内部可导时，全局极值候选包括导数为零或不可导的内点及两个端点
Invalid use: 导数等于零不保证极大极小；忽略端点会漏掉严格单调函数的全局极值

### A403 三维直线和平面相交平行重合的代数判别
Track: ELECTIVE_A; kind: method; printed page 55 line 14.
Applicability: 直线P+t v中v≠0，平面n·(X−Q)=0中n≠0；若n·v≠0则唯一交点，等于零需再检验P是否在面上
Invalid use: n·v=0仅说明直线与平面平行方向，不能断言无交点；可能整条直线就在平面内

### A404 连续均匀分布和正态分布的密度与概率区别
Track: ELECTIVE_A; kind: concept; printed page 56 line 17.
Applicability: 连续随机变量概率来自密度对区间的积分；均匀分布要求b>a且区间内密度1/(b−a)
Invalid use: 连续随机变量单点概率为零，不能把密度值当单点概率；若a=b均匀密度分母无定义

### A405 带截距简单线性回归的非退化最小二乘解
Track: ELECTIVE_A; kind: method; printed page 57 line 13.
Applicability: 成对数据n≥2且Σ(x_i−x̄)²>0时最小二乘斜率为Sxy/Sxx，截距为ȳ−b x̄
Invalid use: 所有自变量相同时斜率不可辨识；回归相关关系不是因果解释且外推需额外检验

### B401 定积分计算面积须区分有向积分和几何面积
Track: ELECTIVE_B; kind: method; printed page 59 line 9.
Applicability: 两连续函数在[a,b]上有序且a≤b，区域面积为∫(上函数−下函数)dx，若上下关系改变需分段
Invalid use: 不分段直接积分两曲线差可能正负抵消，得到错误非负几何面积

### B402 线性目标在紧凸多边形顶点取得最值
Track: ELECTIVE_B; kind: theorem; printed page 59 line 18.
Applicability: P为非空有界闭凸多边形、f(x,y)=ax+by+c为线性函数，则最大最小值至少在一个顶点取得
Invalid use: 对圆盘、椭圆或非线性目标不可仅检查多边形顶点；无界区域可能没有有限极值

### B403 异面直线距离的混合积公式与方向条件
Track: ELECTIVE_B; kind: method; printed page 60 line 11.
Applicability: 空间两直线方向u、v均非零且不平行，分别过P、Q，距离为|(Q−P)·(u×v)|/|u×v|
Invalid use: 当两方向平行时叉积为零，公式不可用；两线不相交并不自动保证方向不平行

### B404 三阶行列式零值等价列向量线性相关
Track: ELECTIVE_B; kind: theorem; printed page 60 line 16.
Applicability: 三阶实矩阵的行列式非零当且仅当列向量构成R³的一组基；为零时存在非零齐次解
Invalid use: 行列式为零不能据此断言方程无解，非齐次系统可能有无穷多解或无解

### B405 三元克拉默法则只能用于系数矩阵非奇异时
Track: ELECTIVE_B; kind: method; printed page 60 line 25.
Applicability: 三元线性系统Ax=b的系数矩阵A为3×3且det(A)≠0时，唯一解xi=det(A_i)/det(A)
Invalid use: det(A)=0时不能做除法；这不等于一定无解，可能无解或无穷多解

### EC401 对数线性生产函数模型的正值与弹性条件
Track: ELECTIVE_C; kind: method; printed page 66 line 25.
Applicability: 仅对产出和投入均严格为正的数据可取对数，若Q=A K^α L^β，需A>0、K>0、L>0再做对数线性化
Invalid use: 投入为零或负时实对数无定义；参数拟合出负预测不等于现实数据可取负产出

### EC402 调查相关回归分析须区分样本相关与因果识别
Track: ELECTIVE_C; kind: method; printed page 68 line 23.
Applicability: 研究设计需要定义总体、变量与数据采集条件，相关回归描述观测关联而不自动识别干预因果效应
Invalid use: 样本选择偏差、共同原因和逆向因果会造成虚假因果解释，不能因回归系数显著就推断政策有效

### ED401 运动轨迹中分解速度与加速度的物理模型条件
Track: ELECTIVE_D; kind: method; printed page 72 line 22.
Applicability: 在近地面短程抛体且忽略空气阻力、加速度g近似常量时可按水平匀速、竖直匀变速分解
Invalid use: 有明显空气阻力、碰撞或推进力时不能照搬理想抛物线；模型只适用于明确时间区间

### ED402 体育设施中的长度角度面积与尺度换算
Track: ELECTIVE_D; kind: concept; printed page 73 line 9.
Applicability: 测量明确单位、参考长度及几何形状假设后，用比例尺和三角几何推导场地布局参数
Invalid use: 图像像素比例未标定不可直接当真实长度；将平面面积缩放倍数误写为长度倍数属于量纲错误


Parser source-tag audit: 12 NUMBERED_REQUIREMENT_CUE; 20 SUBTOPIC_CUE/TOPIC_CUE. This is a regex extraction tag, NOT a human judgment that these are mere headings.

## Verification boundaries

- Local legal-source text stays only on the Mac, digest/source span is frozen, each candidate links an exact source cue, explicitly distinguishing headings from numbered requirements.
- The line-level source witness is not a semantic correctness certification; visual/formula flags remain review requirements.
- No machine generated teaching approvals, no authoritative student indexing, no unsupported general proof claims.
