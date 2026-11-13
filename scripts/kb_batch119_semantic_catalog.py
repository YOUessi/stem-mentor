"""Batch119: project-authored, line-bounded *semantic candidates*, not official atoms.

Each row is manually read against a private, legally held curriculum PDF.
Columns: local key, track, printed page, source line range, knowledge kind,
proposed distinct teaching objective, mathematical precondition, counterexample
or invalid application, source visual review flag, prerequisite local key.
This is intentionally NOT an exhaustive extraction from 405 layout cues.
"""
from __future__ import annotations

# Unquoted project-authored text only; original curriculum PDF is never committed.
ROWS = [
# COMPULSORY: algebra, geometry, probability and modelling
("C01","COMPULSORY",27,4,7,"concept","复数的代数形式与相等判据","z=a+bi，a,b均为实数；相等需实虚部分别相等","不能由模相等推出复数相等",False,None),
("C02","COMPULSORY",27,8,10,"method","复数代数形式的四则运算","复数相除时除数不为零；共轭与模平方不能当成任意分母","用零复数作分母将导致未定义",False,"C01"),
("C03","COMPULSORY",28,8,8,"theorem","不共线三点唯一确定一个平面","三点必须不在同一直线上","三点共线时存在无穷多个经过它们的平面",False,None),
("C04","COMPULSORY",28,9,10,"theorem","直线上两点同属一平面的包含条件","两个不同点都在同一直线和给定平面中","仅一交点属于平面不意味着整条直线属于平面",False,"C03"),
("C05","COMPULSORY",28,11,12,"theorem","相交平面的公共交线","两个平面不同且有公共点","同一个平面不是两个不重合的平面",False,"C03"),
("C06","COMPULSORY",31,10,13,"concept","有限样本空间及事件集合运算","随机试验所有可能基本结果必须列清","遗漏样本点会破坏互斥与全集的判断",False,None),
("C07","COMPULSORY",31,6,8,"method","有限等可能试验的古典概率","样本空间有限并且各基本结果等可能","不等概率情境不能用有利数除以总数的均匀计数法",False,"C06"),
("C08","COMPULSORY",33,6,10,"method","古典概型适用性核验与树状图枚举","有限性、等可能性、无重漏的枚举","掷不均匀硬币不能按两等可能结果计算",False,"C07"),
("C09","COMPULSORY",35,9,13,"method","数学建模验证失败后的重建循环","模型与观测或现实约束必须对照","公式可解不代表现实假设成立；偏差过大需重新建模",True,None),
# SELECTIVE COMPULSORY: sequences/derivatives/vector geometry/statistics
("S01","SELECTIVE_COMPULSORY",38,11,13,"concept","数列是定义在正整数上的函数","自然数指标必须按规定从1或0开始固定","不应把连续变量上任意函数值都称为同一数列",False,None),
("S02","SELECTIVE_COMPULSORY",38,14,15,"concept","等差数列与公差","相邻差相同；n是正整数","只看首尾两项不能判定整个序列等差",False,"S01"),
("S03","SELECTIVE_COMPULSORY",38,16,17,"theorem","等差数列前n项和公式","首项、恒定公差和正整数项数均须明确","非等差数列不能直接使用n(a1+an)/2",False,"S02"),
("S04","SELECTIVE_COMPULSORY",38,21,22,"concept","等比数列与公比条件","比值定义需要前项非零；递推式a(n+1)=q a(n)可独立表述","有零项时盲目作相邻项之商是不合法的",False,"S01"),
("S05","SELECTIVE_COMPULSORY",38,23,24,"theorem","等比数列有限求和的分段公式","q=1与q不等于1必须分开讨论","把q=1代入(1-q^n)/(1-q)会除以零",False,"S04"),
("S06","SELECTIVE_COMPULSORY",38,28,30,"method","数学归纳法的起点及递推步","包含起点验证和对所有n的归纳递推","只验证前几项不能当作证明所有正整数命题",False,"S01"),
("S07","SELECTIVE_COMPULSORY",39,8,13,"concept","导数作为差商极限及切线斜率","在研究点附近定义并存在有限双侧极限","绝对值函数在零点左右斜率不同，导数不存在",False,None),
("S08","SELECTIVE_COMPULSORY",39,14,24,"method","基本求导与仿射复合求导","复合函数f(ax+b)在对应内点可导","不能把f(ax+b)的导数误写成f'(ax+b)而漏掉a",True,"S07"),
("S09","SELECTIVE_COMPULSORY",39,26,29,"method","导数符号判定单调区间","函数在区间连续且内部可导，导数符号须有一致控制","f'(c)=0不意味着c必定是极值点",False,"S07"),
("S10","SELECTIVE_COMPULSORY",39,30,33,"method","闭区间多项式极值与端点比较","需比较端点、内部驻点且定义域为给定闭区间","只检查f'=0会遗漏端点上的最大值",False,"S09"),
("S11","SELECTIVE_COMPULSORY",43,2,5,"method","空间位置关系向量判定","向量和法向量的方向及非零性须明确","零向量与所有向量点积为零但不能当成有效法向量",False,None),
("S12","SELECTIVE_COMPULSORY",43,6,8,"method","点到平面的向量距离","平面法向量非零；点到平面距离取绝对值","用零法向量会使距离公式分母为零",False,"S11"),
("S13","SELECTIVE_COMPULSORY",47,12,16,"concept","条件概率及事件独立的区别","条件事件必须有正概率；独立性是概率乘法关系","P(B)=0时不能定义P(A|B)",False,"C06"),
("S14","SELECTIVE_COMPULSORY",47,16,19,"method","全概率与贝叶斯更新的分母条件","构成划分的一组事件及正概率证据事件","分母为零或划分重叠时不能应用",True,"S13"),
("S15","SELECTIVE_COMPULSORY",48,14,18,"method","一元回归最小二乘斜率与截距","带截距回归要求Sxx>0以确定唯一斜率","所有解释变量相同时斜率不可唯一确定",False,None),
("S16","SELECTIVE_COMPULSORY",48,19,21,"concept","二乘二列联表与独立性检验","频数非负、总数为正；统计检验还需抽样假设","检验p值不等于零假设真实的后验概率",False,"S13"),
# ELECTIVE A — rigorous limits and calculus
("A01","ELECTIVE_A",52,9,20,"concept","数列极限的ε-N量词定义","必须对任意ε>0存在N使其后全部项满足误差限制","只在某一子列接近目标不能说明全列收敛",True,"S01"),
("A02","ELECTIVE_A",52,21,21,"theorem","收敛数列有界性","数列在实数域收敛到有限值","有界数列如(-1)^n不必收敛",False,"A01"),
("A03","ELECTIVE_A",52,22,29,"theorem","实数单调有界数列必收敛","需同一序列既单调又有上界或下界","单调无上界的n不会收敛至有限实数",True,"A01"),
("A04","ELECTIVE_A",52,32,38,"concept","函数极限的ε-δ定义","要求任意靠近但不等于a的定义域点满足条件","f(a)本身的取值不能单独决定极限",True,None),
("A05","ELECTIVE_A",53,1,4,"theorem","闭区间连续函数的介值性质","a<b，函数在整个闭区间连续","分段跳跃函数可跨越目标值而无对应函数值",False,"A04"),
("A06","ELECTIVE_A",53,10,14,"theorem","拉格朗日中值定理的端点与内部条件","闭区间连续且开区间可导，a<b","在尖点不可导的绝对值函数不能直接套中值定理",False,"A05"),
# ELECTIVE B — applied calculus, multivariate
("B01","ELECTIVE_B",58,25,27,"concept","一阶与二阶导数的物理和几何解释","f需二阶可导，导数的物理单位随阶次改变","加速度的单位不能与速度的单位混同",False,"S07"),
("B02","ELECTIVE_B",58,28,30,"method","用中值定理判断单调并证明不等式","应用区间须连续且可导，并核查导数符号","在ln(1+x)无定义的x≤-1处不能展开证明",False,"B01"),
("B03","ELECTIVE_B",59,11,13,"concept","二元函数及其定义域","f(x,y)的定义集合应显式表示在R²中的子集","f(x,y)=1/(x-y)在对角线上无定义",False,None),
("B04","ELECTIVE_B",59,12,13,"method","简单二元函数的偏导数计算","保持另一自变量固定并在定义域内取极限","偏导数存在并不能自动推出全微分存在",False,"B03"),
# ELECTIVE C — logic and model
("EC01","ELECTIVE_C",64,21,25,"concept","数学命题的条件结论及其形式","分清定义与可真可假的陈述，固定论域","把任意开放句直接判断真伪而不指定变量范围会出错",False,None),
("EC02","ELECTIVE_C",65,1,1,"method","充分条件与必要条件的有向关系","命题P⇒Q表示P充分Q必要，反向另需证明","从P⇒Q不能推出Q⇒P",False,"EC01"),
("EC03","ELECTIVE_C",65,2,5,"concept","矛盾律与排中律的区别","经典二值命题逻辑下，P与非P不同时真，至少一真","将两种原则混同为同一个断言会掩盖语义差异",False,"EC01"),
("EC04","ELECTIVE_C",65,6,10,"concept","演绎、归纳与类比推理的证据力度","演绎需要真实前提与有效形式，有限枚举不等于全称证明","只观察若干例子不能逻辑保证一般结论",False,"EC01"),
("EC05","ELECTIVE_C",65,11,13,"method","直接证明与反证法的合法性","反证法应在同一逻辑体系中得到真正矛盾","发现一个计算不方便之处不构成逻辑矛盾",False,"EC03"),
("EC06","ELECTIVE_C",65,18,24,"method","经济社会模型的参数与失效域","参数单位和适用范围要与情境匹配","短期观察的增长率不能无条件外推到无限时间",False,None),
# ELECTIVE D — mathematical patterns in art and life
("ED01","ELECTIVE_D",69,9,20,"concept","数学形态与审美的客观描述区别","曲线方程只能描述可检验的形态性质","不能仅凭相似外观断言两物形状完全相同",False,None),
("ED02","ELECTIVE_D",70,2,7,"concept","轴对称、中心对称与平移对称","必须明确变换及图形整体保持不变","单个局部看似对称不代表整个图案对称",False,None),
("ED03","ELECTIVE_D",70,8,11,"concept","周期模型的重复条件","存在正周期T使定义域允许的f(x+T)=f(x)","某图案偶尔重复一次并非周期性的证明",False,None),
("ED04","ELECTIVE_D",70,8,11,"method","音乐图案周期性与采样周期的区分","抽样记录与连续现象都需检验重复结构","采样混叠产生的假周期不能当成真实频率",False,"ED03"),
# ELECTIVE E — elective examples, NOT mandatory official atom claims
("EE01","ELECTIVE_E",73,16,17,"concept","机器人运动中的坐标与变换作为选修示例","机器人模型涉及明确坐标框架与维度，属于地方自主示例","二维轨迹的结果不能无条件套给三维刚体",False,None),
("EE02","ELECTIVE_E",73,16,17,"concept","初等数论同余作为选修示例","模数必须为正整数，比较整数余数","模0运算不符合通常整数同余定义",False,None),
("EE03","ELECTIVE_E",73,18,20,"method","家庭复利与现实成本建模作为选修示例","计息频率、利率单位和费用定义须一致","年利率不能直接作为每月复利利率",False,None),
("EE04","ELECTIVE_E",73,21,22,"concept","大学先修概率统计的拓展边界","标为可选先修方向，不纳入高中必修认证分母","先修课程出现于选修例子不代表每名高中生都必须修习",False,None),
]
