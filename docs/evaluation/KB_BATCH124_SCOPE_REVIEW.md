# Batch124 — mathematics curriculum clauses: editorial atomization and exclusions

Source: 2017 curriculum, 2020 revision; Mac-held original PDF only. No copyrighted source lines checked in.
All items are **editorial proposals** pending expert review. Official seven-track atom denominators remain UNKNOWN.
New proposed concepts/methods/theorems: 32; cumulative 239.
Source cues linked 270/405; unlinked 135.
Separately: 3 research/activity/competency clauses have proposed NON-ATOM dispositions awaiting human adjudication.
Do not subtract those 3 to invent any official atom denominator.

|Track|Cues|Linked|Unlinked|Draft atoms|Nonatom proposals|Official denominator|
|---|---:|---:|---:|---:|---:|---|
|COMPULSORY|127|76|51|75|2|UNKNOWN|
|ELECTIVE_A|69|41|28|30|0|UNKNOWN|
|ELECTIVE_B|70|43|27|30|0|UNKNOWN|
|ELECTIVE_C|29|20|9|24|0|UNKNOWN|
|ELECTIVE_D|17|14|3|17|0|UNKNOWN|
|ELECTIVE_E|4|4|0|12|0|UNKNOWN|
|ELECTIVE_UNASSIGNED|0|0|0|0|0|UNKNOWN|
|SELECTIVE_COMPULSORY|89|72|17|51|1|UNKNOWN|

## Numbered requirement review proposals
- COMPULSORY printed p21, line 6: 历史资料收集与论文写作属于可选学习活动，不自动视为一个有定理/定义的原子; REVIEW_PENDING (not certified).
- COMPULSORY printed p23, line 9: 现实应用资料收集是探究活动，可关联建模任务但非独立数学事实; REVIEW_PENDING (not certified).
- SELECTIVE_COMPULSORY printed p44, line 16: 数形结合思想是跨主题教学目标，非一个独立数学命题; REVIEW_PENDING (not certified).

## Source-locked original mathematical objectives
### C501 — 按任务选择函数的解析式、表格和图像表征
COMPULSORY · printed p19 line 18 · method
Premises: 对同一定义域中的函数，解析式便于计算，表格可呈现离散观测，图像便于研究总体形态；转换时要核对采样范围
Failure/false use: 只凭有限采样点不能确定连续函数全貌；把数据图表插值当作唯一函数会漏掉其他可能

### C502 — 指数函数图像的描点和单调方向
COMPULSORY · printed p20 line 29 · method
Premises: 实底数a>0且a≠1，f(x)=a^x的定义域是实数；a>1时严格递增，0<a<1时严格递减，图像始终正值
Failure/false use: a=1时变成常数函数不再符合通常的指数函数定义；描点只提供证据，不可充作全域证明

### C503 — 实对数函数的定义域、反函数关系与单调性
COMPULSORY · printed p20 line 34 · concept
Premises: 实数底数a>0且a≠1，y=log_a(x)定义于x>0，是y=a^x关于直线y=x的反函数图像
Failure/false use: 底数在0到1之间时对数函数递减；x≤0时无实值，不允许把负自变量代入实对数

### C504 — 指数函数与对数函数互为反函数的条件
COMPULSORY · printed p21 line 3 · theorem
Premises: 给定a>0且a≠1，指数映射a^x由实数双射到正实数，其逆映射是log_a(x)
Failure/false use: 在a=1时指数函数不单射；将log_a(a^x)=x与a^(log_a(x))=x的定义域混写会出错

### C505 — 三角函数在主周期上的图像性质判读
COMPULSORY · printed p21 line 27 · method
Premises: 弧度变量x取实数，正弦余弦在[0,2π]上可由单位圆确认零点、极值和对称性；正切在极点处无定义
Failure/false use: 正切x在π/2和3π/2无定义，不能跨越极点声明连续；主周期区间外结论须借周期延拓

### C506 — 正弦模型振幅、周期、相位与现实单位
COMPULSORY · printed p22 line 2 · method
Premises: 对A sin(ωx+φ)且A≠0、ω≠0的非退化模型，振幅|A|、周期2π/|ω|；水平平移须除以ω
Failure/false use: ω=0时为常量无最小正周期；将角度制直接代入弧度模型会使周期和相位错误

### C507 — 余弦差公式的单位圆向量证明
COMPULSORY · printed p22 line 13 · theorem
Premises: 任意实数α、β的单位向量内积给出cos(α−β)=cosαcosβ+sinαsinβ，无需除以正弦余弦
Failure/false use: 把cos(α−β)误写成cosα−cosβ是错误的；用正切证明时分母可能为零而原公式不受限

### C508 — 和差角公式到积化和差的等价变换
COMPULSORY · printed p22 line 16 · method
Premises: α、β为任意实角；可将sin(u+v)与sin(u−v)相加，变换全程不需要除以可能为零的量
Failure/false use: 将sinαsinβ直接写成sin(αβ)没有依据；遗漏二倍系数会使验证角度错误

### C509 — 函数零点与方程实根的同一性
COMPULSORY · printed p22 line 28 · concept
Premises: 对实函数f:D→R，若x0∈D且f(x0)=0，则x0是零点，也是方程f(x)=0的实根；图像与x轴交点可辅助判读
Failure/false use: 穿过x轴并非必要，切触也可为零点；只依据两端异号断言根存在须另验连续性

### C510 — 真实问题建模中的变量、单位与适用域
COMPULSORY · printed p23 line 3 · method
Premises: 从可观察对象提出变量，标注单位与数据适用区间，写出可检验的关系及误差来源，再回到现实约束比较
Failure/false use: 维度不一致的方程不能解释现实；拟合已知数据很准不代表外推和因果解释一定成立

### C511 — 比较不同函数增长速度时先统一量纲与区间
COMPULSORY · printed p23 line 6 · method
Premises: 对同一正向无量纲输入且固定合法参数，可在相同区间比较常系数指数、幂和对数函数的增长形态
Failure/false use: 极限意义上的最终增长快慢不能替代有限区间数值比较；未统一单位不能直接比较系数

### C512 — 位移和受力作为平面自由向量的建模前提
COMPULSORY · printed p25 line 22 · concept
Premises: 仅用大小和方向即可描述的量适用自由向量表示；位置向量需要先指定原点，力的作用点问题还涉及附加物理信息
Failure/false use: 把温度或质量当平面向量不合适；只知道位移终点而没有起点不能确定该段位移

### C513 — 平面向量的长度方向和零向量区别
COMPULSORY · printed p25 line 24 · concept
Premises: 向量由大小、方向共同描述；零向量长度为0，不给它定义唯一方向；相等向量须分量相同
Failure/false use: 不能为零向量强行定义与任意向量的夹角；起点不同也可能是相等的自由向量

### C514 — 向量分解法解平面几何与简单力学问题
COMPULSORY · printed p26 line 21 · method
Premises: 在选定坐标系下使用相等向量与内积的代数结论，必须保留几何长度非负以及物理单位
Failure/false use: 内积为零推垂直须向量非零；位移、力和速度分量不能因符号相似而直接相加

### C515 — 柱锥台球基本立体图形的条件化识别
COMPULSORY · printed p27 line 25 · concept
Premises: 必须先核实几何体的底面、截面、轴线等定义特征，再区分棱柱、圆柱、棱锥、圆锥与球
Failure/false use: 仅凭透视图像近似圆形不能断言是球体；斜棱柱的侧棱不能直接当高

### C516 — 基本几何体体积公式的高度与半径前提
COMPULSORY · printed p27 line 28 · method
Premises: 圆柱体积πr²h、圆锥体积πr²h/3，r≥0且h≥0；棱柱体积是底面积乘垂直高
Failure/false use: 斜高不是圆锥的垂直高；直径误当半径会造成面积四倍偏差

### C517 — 斜二测法绘制空间图形的比例失真
COMPULSORY · printed p28 line 2 · method
Premises: 在约定斜二测轴角及缩放系数后，按投影规则画长方体等简图；绘图保持约定而非真实测量长度
Failure/false use: 投影后角度和长度常失真，不可从纸面斜角直接推断空间真实直角与垂直

### C518 — 空间点线面关系须从几何定义或公理出发
COMPULSORY · printed p28 line 5 · concept
Premises: 用真实的三维位置判断点在直线或平面、两直线平行相交异面等，必要时构造空间坐标
Failure/false use: 立体图的两条投影线交叉不必在三维相交；看起来平行也不能替代空间几何证明

### C519 — 直线与平面平行判定的充分条件
COMPULSORY · printed p28 line 16 · theorem
Premises: 若直线l不在平面α内，且l平行于平面α中的一条直线m，则l平行于α（无公共点）
Failure/false use: 遗漏l不在α内时，l可能本来就在平面上；投影平行不能代替真实平行

### C520 — 两平面垂直判定中的包含垂线条件
COMPULSORY · printed p28 line 26 · theorem
Premises: 若平面β包含一条垂直于平面α的直线，则两个平面垂直；条件须是空间线面垂直
Failure/false use: 仅图示某条线与平面上一条线垂直不足以认定线面垂直；平面间视觉直角未必可证

### C521 — 同一样本空间事件并集概率的容斥关系
COMPULSORY · printed p31 line 16 · theorem
Premises: 对同一概率空间的事件A、B，总有P(A∪B)=P(A)+P(B)−P(A∩B)；互斥时交集概率为零
Failure/false use: 独立并不意味着互斥；直接相加两个重叠事件概率会对交集重复计数

### C522 — 抽样前明确总体和合法的数据来源
COMPULSORY · printed p32 line 6 · method
Premises: 需声明总体、变量和收集途径，检查样本的选择机制以及数据单位和缺失情况
Failure/false use: 方便样本不必代表目标总体；已发布的统计年鉴若口径不同不可不加转换直接拼接

### C523 — 总体样本样本量及样本随机性的区别
COMPULSORY · printed p32 line 8 · concept
Premises: 总体为关心的全体对象，样本是实际观测的对象集合，样本量n为其数量；随机抽样机制影响推断
Failure/false use: 样本量大不自动消除系统选择偏差；一次样本均值不等于无误差总体均值

### C524 — 样本标准差衡量离散程度的两种分母
COMPULSORY · printed p32 line 27 · method
Premises: 样本离差平方和除以n得到描述性方差，若以独立同分布样本无偏估计总体方差常用n−1且n≥2
Failure/false use: 混用n与n−1会改变结果；当n=1时不能使用n−1作为除数

### C525 — 经验百分位数在排序和插值规则下的定义
COMPULSORY · printed p33 line 1 · concept
Premises: 对有限排序样本先规定百分位计算算法，才能解释给定分位所处位置；不同软件约定可能返回不同数
Failure/false use: 未经说明直接给一个唯一百分位数并不严谨；第90百分位不是样本值有90%等于该数

### S501 — 圆锥曲线定义与二次方程退化风险
SELECTIVE_COMPULSORY · printed p44 line 10 · concept
Premises: 在平面直角坐标系下将椭圆、双曲线和抛物线的几何定义与其标准方程建立对应
Failure/false use: 一般二次方程可能是退化曲线或空集；仅看二次项便断言是哪类圆锥曲线不可靠

### S502 — 用抛物线焦点准线定义解决距离应用
SELECTIVE_COMPULSORY · printed p44 line 17 · method
Premises: 在固定平面中抛物线点到固定焦点F与不经过F的直线l距离相等，计算时保持坐标单位一致
Failure/false use: 焦点落在准线上会退化而非标准抛物线；仅有相等距离的有限离散点不能证明整个轨迹

### A501 — 导数作为变化率极限与切线斜率
ELECTIVE_A · printed p53 line 6 · concept
Premises: 实函数在x0附近有定义，f'(x0)是差商在h趋于0时存在的有限极限；物理量需遵守单位
Failure/false use: 割线斜率不能直接当某一点导数；绝对值函数在尖点的左右导数不同，通常不可导

### A502 — 平面等距变换保持两点距离
ELECTIVE_A · printed p55 line 17 · concept
Premises: 平面变换T若对所有P,Q有|T(P)−T(Q)|=|P−Q|则为等距变换，平移旋转反射均属于此类
Failure/false use: 一般缩放系数k≠1不保持距离；等距变换保长度但反射不保持有向方向

### A503 — 显著性检验必须预先明确原假设和拒绝域
ELECTIVE_A · printed p57 line 7 · method
Premises: 检验前给出H0、H1、显著性水平α和统计量在H0下的分布；p值是在H0下观测同等或更极端数据的概率
Failure/false use: p值不是H0为真的概率；不拒绝H0不意味着已经证明H0为真

### B501 — 空间内积和叉积几何意义的非零条件
ELECTIVE_B · printed p60 line 6 · theorem
Premises: 三维实向量u、v的内积是|u||v|cosθ，叉积模为|u||v|sinθ；非零向量才能定义夹角
Failure/false use: 零向量没有唯一方向，且叉积方向依赖右手定则；不能把叉积直接写成一个实数

### B502 — 正交试验设计区分平衡列和交互作用
ELECTIVE_B · printed p62 line 23 · method
Premises: 选择与因素水平相容的正交表且满足试验独立可比等前提，正交列帮助估计主效应
Failure/false use: 未经检查交互作用混杂不能声称每个因素独立可识别；正交表不能自动消除测量偏差


## Limits
- Finite mathematical witnesses are not universal proofs.
- No teacher approval, official completion, or student-authoritative release.
- All remaining source cues require targeted human line/context/visual review, not just string matching.
