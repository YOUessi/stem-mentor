#!/usr/bin/env python3
"""Batch54: independent original teacher drafts for 12 non-equivalent elective links.

Never infer official atom counts from a project editorial goal or page marker.
Authored educational text, not verbatim standard/copyright textbook content.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Literal
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.kb_batch34_review import Manuscript
from pydantic import Field

class Legacy54(Manuscript):
    id: str = Field(pattern=r"^math\.hs\.editorial\.batch54\.[a-z0-9.]+$")
    syllabus_track: Literal["ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E"]
    source_printed_page: int = Field(ge=52,le=73)
    source_pdf_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_page_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_standard_version: Literal["CN-HS-MATH-2017-REV2020"]
    official_scope_equivalence: Literal["NOT_CERTIFIED"]
    prerequisite_topics: list[str] = Field(min_length=1)
    source_editorial_goal: str = Field(min_length=10)

# Dynamic file-based import in existing regression tests does not register module
# namespace; supply enum type explicitly when resolving postponed annotations.
Legacy54.model_rebuild(_types_namespace={"Literal":Literal})

EVAL=ROOT/"docs/evaluation"
SOURCE=EVAL/"KB_BATCH53_CROSS_PAGE_REVIEW_QUEUE.json"
GATE=EVAL/"KB_BATCH51_OFFICIAL_SOURCE_PAGE_GATE.json"
OVERLAY=EVAL/"KB_BATCH50_PROJECT_SCOPE_OVERLAY.json"
SEED=ROOT/"knowledge/editorial_review/kb_batch54_legacy_scope.jsonl"
TEXT=EVAL/"KB_BATCH54_LEGACY_SCOPE_MANUSCRIPTS.md"
REPORT=EVAL/"KB_BATCH54_SCOPE_AND_DENOMINATOR_AUDIT.json"
PAGE=EVAL/"KB_BATCH54_PAGE_COMPLETENESS.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")

# Exactly three reasoned proof/discussion steps and two checked solved examples each.
# Each row is hand-authored. No row constitutes official scope equivalence.
CARDS=[
dict(cid="KB33-A-P052-A001",title="数列极限的ε–N量词与必要条件",kind="concept",
 claim="数列(a_n)收敛到实数L，定义为：对每个ε>0，都存在正整数N，使所有n≥N满足|a_n−L|<ε；N可以依赖ε，但不能依赖已选定的n。",
 assumptions="数列的每项与候选极限L均为实数；n取正整数；ε必须对所有正值成立。",
 steps=[("先固定任意正的误差容限ε。","极限定义的外层量词是对所有ε>0。"),("从ε构造一个整数N(ε)。","允许阈值随容差变化，却不允许每项重新挑阈值。"),("证明每个n≥N均满足误差界。","只有尾部全称量词成立，才能判定该给定L是极限。")],
 bad="检查少数很大的n就足以证明极限。", counter="a_n=(-1)^n在任意大n仍交替±1，取L=0和ε=1/2时始终不满足尾部界。", why="有限次样本验证无法替代尾部所有n的条件。",
 ex=[("证明a_n=1/n趋于0。","给定ε>0，取整数N>1/ε。","n≥N时0<1/n≤1/N<ε。","0","对所有ε都有此N，满足全称尾部界。"),
     ("判断a_n=2+1/n的极限。","对误差|a_n−2|=1/n。","给定ε取N>1/ε。","2","首项是否等于2不影响尾部极限。")],
 hints=["先把极限陈述写成∀ε>0∃N∀n≥N。","把误差|a_n−L|化简为关于n的上界。","从误差不等式反求严格足够大的整数N，最后统一检验全部n≥N。"],
 near="证明a_n=3/n趋于0并明确N对ε的依赖。",far="解释为什么一次有限计算轨迹不能证明迭代算法收敛。"),
dict(cid="KB33-A-P052-A002",title="收敛实数列有界的逐步证明",kind="theorem",
 claim="若实数数列a_n收敛到有限实数L，则存在M>0，使所有正整数n都满足|a_n|≤M；反过来有界本身不能保证收敛。",
 assumptions="收敛极限L有限；数列每项为实数；结论是整条数列有界而非仅尾部有界。",
 steps=[("在极限定义中选ε=1并取得N。","收敛性保证n≥N时|a_n−L|<1。"),("对n≥N用三角不等式得|a_n|≤|L|+|a_n−L|<|L|+1。","三角不等式给出无限尾部的统一上界。"),("与有限个前缀项|a_1|,…,|a_(N−1)|取最大值。","有限非空实数集合有最大值；空前缀无需额外项。")],
 bad="每条有界实数数列都会收敛。",counter="a_n=(-1)^n始终在[-1,1]但两子列分别恒为1和−1，无法有同一极限。",why="有界只控制幅度，不约束奇偶项振荡。",
 ex=[("a_n=1/n有界吗？","n≥1故0<1/n≤1。","M=1就统一界住全部项。","有界","还可独立证明它趋向0。"),("a_n=2+(-1)^n是否收敛？","所有项属于{1,3}故有界。","奇偶子列分别固定为1、3。","不收敛","两个不同常数子列极限排斥同一极限。")],
 hints=["先用ε=1获得一个全尾部的估计。","有限前缀和无限尾部要分别控制。","把前缀的最大绝对值与|L|+1取共同上界。"],
 near="论证收敛数列3+1/n有界。",far="为什么数值优化的参数范数有界不能保证参数迭代点收敛？"),
dict(cid="KB33-A-P052-A003",title="单调有界收敛定理的严格前提",kind="theorem",
 claim="实数数列若单调递增且有上界则收敛到其值域上确界；单调递减且有下界时收敛到下确界；单独有界不足以推出收敛。",
 assumptions="实数完备性（非空有上界集合存在上确界）；单调方向与对应一侧界必须明确。",
 steps=[("把递增数列的全体值组成非空有上界集合S，并令L=sup S。","依赖实数的上确界性质。"),("任意ε>0，L−ε不可能是S的上界，故有某N使a_N>L−ε。","上确界的最小上界定义。"),("递增保证n≥N时L−ε<a_N≤L；若a_n递减且有下界，令b_n=−a_n，则b_n递增有上界，前述结论给出a_n趋向其下确界。","单调递增情形的误差界证明收敛；递减情形通过取负数列和上下确界的对应关系归约证明。")],
 bad="只知道有界就能直接调用单调收敛定理。",counter="(-1)^n有界却不单调也不收敛。",why="没有单调性就不能用一个靠近上确界的项控制后续所有项。",
 ex=[("a_n=1−1/n是否收敛？","n增大时1/n递减，故a_n递增且≤1。","上确界为1，故极限为1。","1","差值为1/n，亦可用ε–N检验。"),("a_n=(-1)^n是否可用此定理？","数列值域只含±1所以有界。","后续增减交替，不满足任一单调条件。","不可用","不能用前提不成立的定理推导极限。")],
 hints=["标清楚是递增还是递减。","检查对应的上界或下界，并说明实数完备性。","用上确界的ε定义加单调性建立全部尾项的误差界。"],
 near="论证1−1/(n+1)的收敛性。",far="解释递推数值过程有界但可能振荡的反例。"),
dict(cid="KB33-A-P053-A002",title="介值定理与连续性的不可遗漏前提",kind="theorem",
 claim="若实函数f在闭区间[a,b]连续且a<b，任意介于f(a)与f(b)之间的实数y，都存在c∈[a,b]使f(c)=y；严格夹在两端之间时可选c∈(a,b)。",
 assumptions="区间为非退化闭实区间，f在整段连续；y确实介于端点函数值之间。",
 steps=[("设g(x)=f(x)−y，则g连续。","连续函数减常数仍连续。"),("当y在端点函数值之间，g(a)与g(b)不异号则至少一端为零，否则两端异号。","根据端点值与目标值的相对位置逐一进行代数符号分类。"),("异号情形用实数连续性与二分嵌套区间得到g(c)=0。","连续性保证每次保留的夹零闭区间长度趋零，极限点函数值为零。")],
 bad="只要函数端点值夹住目标值，中间必取到。",counter="f(x)=−1(x<0)、1(x≥0)定义于[-1,1]；端点夹住0，但函数从不取0。",why="跳跃不连续破坏了介值性质。",
 ex=[("f(x)=x²−2在[1,2]有零点吗？","函数为多项式，在[1,2]连续。","f(1)=−1且f(2)=2，异号。","至少一个零点","由介值定理；无需声称唯一。"),("f(x)=1/x在[-1,1]能直接使用介值定理吗？","函数在x=0未定义。","不满足闭区间连续的前提。","不能使用","端点符号异号但中间不必有定义的零点。")],
 hints=["先明确f在整个闭区间有定义并连续。","检查端点值是否确实夹住所求目标值。","结论是存在至少一个解；唯一性还要另外证明。"],
 near="判断x³−1在[0,2]存在零点。",far="说明数值二分搜索为何需要连续及端点异号作为安全前提。"),
dict(cid="KB33-A-P053-A004",title="拉格朗日中值定理的两重正则条件",kind="theorem",
 claim="若f在闭区间[a,b]连续且在开区间(a,b)可导，a<b，则存在c∈(a,b)，满足f'(c)=(f(b)−f(a))/(b−a)。",
 assumptions="闭区间连续、开区间处处可导、端点不同且有限；定理只保证存在，不保证c唯一。",
 steps=[("定义弦斜率m=(f(b)−f(a))/(b−a)和g(x)=f(x)−m(x−a)。","b−a非零，g连续且内部可导。"),("计算g(a)=g(b)=f(a)。","减去线性函数后端点相等。"),("罗尔定理给出c∈(a,b)且g'(c)=0，故f'(c)=m。","罗尔定理适用于g的闭区间连续与内部可导。")],
 bad="只要端点函数值存在就一定有内部切线斜率等于弦斜率。",counter="f(x)=|x|在[-1,1]的弦斜率为0，但在(-1,0)导数−1，(0,1)导数1，0处不可导。",why="内部不可导点会阻断中值定理。",
 ex=[("f=x²在[1,3]取何c？","弦斜率(9−1)/2=4。","f'(x)=2x，令2c=4得c=2。","c=2","2严格属于(1,3)。"),("f=3x+1在[0,5]如何？","弦斜率(16−1)/5=3。","每个c∈(0,5)均有f'(c)=3。","任意内部c","存在性不必意味着唯一。")],
 hints=["首先分开检查闭区间连续和内部可导两个条件。","构造通过端点的割线并从原函数中减去它。","用罗尔定理找导数为零的位置，再恢复原函数导数。"],
 near="求f=x³在[0,2]满足中值定理的c。",far="为什么带尖点的实际响应曲线不能无条件套用瞬时斜率公式？"),
dict(cid="KB33-A-P057-A002",title="显著性水平与p值的条件概率方向",kind="concept",
 claim="给定零假设H0、检验统计量T和事先指定的极端性方向，p值是H0成立时获得至少同样极端数据的概率；显著性水平α是事先约定的Ⅰ类错误概率控制阈值，不等于H0为真的后验概率。",
 assumptions="事先给定检验统计量、尾部方向及H0下的抽样分布；不把观察到的p值当作随机选择的α。",
 steps=[("根据研究问题给定H0与极端性事件E。","不同单双尾和检验统计量会改变E。"),("计算p=P_H0(T∈E)，条件始终是H0为真。","抽样分布下的尾概率定义。"),("用p和预设α作拒绝决策，不把P(数据|H0)翻转为P(H0|数据)。","贝叶斯方向逆转需要先验与备择模型。")],
 bad="p=0.03表示零假设只有3%的概率为真。",counter="在抛硬币H0为公平且两次都为正面的观测下，单侧尾概率是1/4；这不是P(H0|观测)。",why="尾概率以零假设为条件，后验假设概率需要其他先验信息。",
 ex=[("公平硬币2次都正面，单侧p值？","H0下4条长度2序列等可能。","至少2次正面仅HH一种。","1/4","这不是公平假设有25%概率为真。"),("预设α=0.05、观察p=0.04如何决策？","先确认检验方案与α在观察数据前预设。","0.04<0.05故在该规则下拒绝H0。","拒绝H0","决策不是证明备择为真，更不是计算后验概率。")],
 hints=["明确写出概率符号中的条件H0。","明确极端性是单尾还是双尾，且不可看数据后随意更改。","最后把p与预设α比较，严禁反向解读为P(H0|数据)。"],
 near="公平骰子两次均为6时计算单侧指定极端事件概率。",far="解释临床试验中为什么统计显著性不等于实际效果大小。"),
dict(cid="KB33-B-P058-A004",title="线性微分与真实函数增量的误差",kind="theorem",
 claim="函数在x可导时有Δy=f(x+h)−f(x)=f'(x)h+o(h)(h→0)；微分dy=f'(x)dx是线性主部，一般不等于实际有限增量Δy。",
 assumptions="f在给定点x可导；h或dx趋于0；小o结论是局部极限而非任意大步长恒等式。",
 steps=[("可导定义给出lim_{h→0}(f(x+h)−f(x))/h=f'(x)。","导数存在是线性化的必要条件。"),("将差商误差写成r(h)h，其中r(h)→0。","由极限定义，差商与导数之差趋0。"),("得到Δy=f'(x)h+r(h)h，故余项是o(h)。","小o定义为余项除以h趋于0。")],
 bad="函数可导就有任何非零步长下Δy=dy的严格相等。",counter="f(x)=x²，x=1、h=1时Δy=3，而dy=2。",why="有限步长保留非线性余项h²，不能无条件删去。",
 ex=[("f=x²，在x=1、h=1/10的微分与真增量？","dy=2×1×(1/10)=1/5。","Δy=(11/10)²−1=21/100。","dy=1/5，Δy=21/100","差值1/100=h²。"),("f=3x+1在任意h的微分与增量？","导数恒为3所以dy=3h。","直接相减f(x+h)−f(x)=3h。","完全相等","仿射函数无高阶剩余项。")],
 hints=["先问的是局部极限还是任意固定步长。","从导数差商定义减去f'(x)构造误差项。","取f=x²计算h²剩余项，检查为何小o不能删去。"],
 near="推导f=x³在x=1时的局部增量式。",far="解释数值近似在较大步长时可能发生系统误差。"),
dict(cid="KB33-B-P059-A002",title="微积分基本定理的连续性与端点条件",kind="theorem",
 claim="若f在[a,b]连续，定义F(x)=∫_a^x f(t)dt，则F在(a,b)可导且F'(x)=f(x)；若G是[a,b]上的任意原函数，则∫_a^b f(t)dt=G(b)−G(a)。",
 assumptions="a<b且f在整个闭区间连续；积分为定积分，原函数G在区间内满足G'=f并有合法端点。",
 steps=[("用F(x+h)−F(x)=∫_x^{x+h} f(t)dt表示积分增量。","定积分的可加性。"),("连续性使短区间上的平均函数值趋于f(x)，从而F'(x)=f(x)。","积分均值估计和连续性。"),("G−F导数恒为0，在区间内为常数，故G(b)−G(a)=F(b)−F(a)。","中值定理与F(a)=0、F(b)=∫f。")],
 bad="被积函数在区间里有奇点也能直接套两端原函数差。",counter="f(x)=1/x在[-1,1]含x=0的奇点，不能把ln|x|在两端的值相减当作跨奇点定积分。",why="既未在整个区间连续，也没有跨越奇点的一份全区间原函数。",
 ex=[("求∫_0^2 2x dx。","f=2x连续，原函数G=x²。","G(2)−G(0)=4。","4","积分下限与上限的顺序正确。"),("F(x)=∫_1^x t²dt，求F'(2)。","t²在全实数连续。","微积分基本定理给F'(x)=x²，故F'(2)=4。","4","先核查积分函数的连续性和积分变量。")],
 hints=["检查函数在整个积分区间定义且连续。","用变上限积分的短区间差商理解第一部分。","选全区间原函数，再严格计算上限值减下限值。"],
 near="计算∫_1^3 3x²dx。",far="在跨越间断点的物理速率积分中说明为什么必须分段或重新定义模型。"),
dict(cid="KB33-C-P065-A001",title="经典二值逻辑的矛盾律与排中律",kind="concept",
 claim="在经典二值命题语义中，矛盾律表达¬(p∧¬p)恒真，排中律表达p∨¬p恒真；二者是不同公式，不应推广为所有非经典逻辑的无条件定律。",
 assumptions="p为同一语义语境中的确定命题；取经典真/假二值及标准否定、合取、析取。",
 steps=[("当p为真时，¬p为假。","经典二值命题语义下否定联结词的真值规则。"),("当p为假时，¬p为真。","二值否定规则覆盖所有允许赋值。"),("两行真值表中p∧¬p恒假而p∨¬p恒真。","分别推出矛盾律与排中律，二者结构不同。")],
 bad="矛盾律与排中律是同一个命题公式。",counter="两公式分别是¬(p∧¬p)与p∨¬p，虽然经典语义下都恒真，但逻辑连接词及表达的否定关系不同。",why="同真值不代表同一语法表达式，且非经典逻辑中逻辑律可有不同地位。",
 ex=[("p为真时分别计算两公式。","¬p为假，p∧¬p为假。","于是¬(p∧¬p)真，p∨¬p真。","都为真","两条规律都符合该真值行。"),("p为假时分别计算两公式。","¬p为真，p∧¬p为假。","于是¬(p∧¬p)真，p∨¬p真。","都为真","已遍历经典二值语义所有行。")],
 hints=["先把每个命题公式明确写出，不要仅用口头标签。","分别计算p为真和p为假的两行真值表。","分清两者同为经典重言式与语法上为不同公式。"],
 near="对p、q分别列出¬(p∧¬p)和q∨¬q的真值表。",far="比较经典二值逻辑与三值逻辑对排中律的定义差异。"),
dict(cid="KB33-C-P066-A004",title="正投入Cobb–Douglas模型的对数线性化",kind="method",
 claim="若Q=A L^α K^β且A,L,K都严格为正、α和β为实数，则ln Q=ln A+αln L+βln K；该恒等式不是估计出模型参数或证明经济因果关系。",
 assumptions="A>0、L>0、K>0，实数幂按正底数定义；Q>0；现实生产函数本身为先验模型假设。",
 steps=[("所有正底数的实数幂均正，Q=A L^α K^β>0。","正实数的乘积与幂合法。"),("对等式两边取自然对数。","对数要求参数严格为正，不能在零或负输入上执行。"),("使用ln(ab)=ln a+ln b、ln(x^r)=r ln x得到线性化式。","正实数指数对数恒等式。")],
 bad="生产投入可以取零值仍直接代入ln L或ln K。",counter="L=0、α=1时Q=0而ln L、ln Q都不在实数范围定义。",why="对数变量需要严格正值，不能用模型的代数形式自动消除定义域。",
 ex=[("A=2,L=4,K=9,α=1/2,β=1/2求Q。","Q=2×sqrt(4)×sqrt(9)。","因此Q=2×2×3。","12","对数形式只适用于全部正值。"),("A=1,L=e²,K=e³,α=2,β=1求lnQ。","lnA=0，lnL=2，lnK=3。","lnQ=0+2×2+3=7。","7","直接计算Q=e^7一致。")],
 hints=["先检查A、L、K及Q严格大于0。","将乘积逐项取对数，再用幂的对数法则。","解释线性化仅是数学变换，不能据此自动断定现实模型或因果关系成立。"],
 near="将Q=3L^(1/3)K^(2/3)写成对数线性形式。",far="分析含零投入观测数据时直接使用对数回归的偏差与数据处理约束。"),
dict(cid="KB33-D-P071-A002",title="整数节拍的最小同步周期与时间单位",kind="method",
 claim="若若干循环节拍的周期为正整数p1,…,pk，且共用同一离散拍单位与起点，则首次正整数拍同步时刻是它们的最小公倍数；转换为秒必须额外知道每拍时长。",
 assumptions="各周期为正整数；节拍单位相同；初始相位为零；物理时间换算需有有效每拍秒数。",
 steps=[("第i个循环在第n拍重合要求p_i整除n。","周期性循环的定义。"),("所有循环同时重合当且仅当n是所有p_i的公倍数。","整除关系的合取。"),("最小正公倍数就是lcm(p1,…,pk)。","最小公倍数定义；没有速度时不能把拍数直接称为秒数。")],
 bad="计算出最小公倍数就知道同步所需秒数。",counter="周期为3拍和4拍，首次同步都是12拍；每拍0.5秒时是6秒，每拍2秒时是24秒。",why="相同离散拍数对应的物理时间取决于节奏速度。",
 ex=[("3拍和4拍的首次同步点？","3的倍数为3,6,9,12，4的倍数为4,8,12。","首次共同正倍数是12。","12拍","12同时被3和4整除。"),("周期6拍和8拍，120拍/分钟首次同步多少秒？","lcm(6,8)=24拍。","120拍/分钟即0.5秒/拍。","12秒","24×0.5=12秒；单位已换算。")],
 hints=["先统一周期是否用同一拍单位。","用整除关系而非直接相加来找最早共同周期。","如需物理时间，必须明确每分钟拍数或每拍秒数。"],
 near="求4拍、6拍、9拍循环的首次正整数同步拍数。",far="解释两个机器周期含相位偏移时最小公倍数为何不能直接给首次同步点。"),
dict(cid="KB33-E-P073-A004",title="一阶常系数仿射差分方程的分类求解",kind="theorem",
 claim="给定x_0、实数a,b和n≥0，递推x_(n+1)=a x_n+b的解为x_n=a^n x_0+bΣ_{k=0}^{n−1}a^k；a≠1时等于a^n x_0+b(1−a^n)/(1−a)，a=1时等于x_0+nb。",
 assumptions="n为非负整数、系数a,b为常数；有限和在n=0按空和为零；选修E示例不能升格为必修。",
 steps=[("对n=0，空和公式给出初值x_0。","归纳法初始步成立。"),("若第n步公式成立，代入a x_n+b并合并有限和得到第n+1步。","数学归纳法及分配律。"),("只有a≠1时使用有限等比和；a=1须改用常数项逐步累加。","除以1−a时必须证明其非零。")],
 bad="无论参数a为何值，直接写b(1−a^n)/(1−a)都有效。",counter="a=1,b=2,x0=3，x_n=3+2n；所谓闭式分母为零且无定义。",why="等比求和闭式需要a≠1，边界参数单独求解。",
 ex=[("x_(n+1)=2x_n+1,x0=0，求x3。","x1=1，x2=3。","x3=2×3+1=7。","7","闭式2^3−1=7一致。"),("x_(n+1)=x_n+2,x0=3，求x4。","a=1时x_n=3+2n。","令n=4代入通项表达式，得到数值11。","11","直接连加四次2得同值。")],
 hints=["先写出前两次迭代，观察齐次和常数输入两部分。","用数学归纳证明有限和公式，注意n=0空和。","把a=1与a≠1分开，防止除以零。"],
 near="求x_(n+1)=3x_n−2且x0=1的通项。",far="讨论a的绝对值与1的关系如何影响迭代稳定性；区分数学模型与真实反馈系统。"),
]

# Original notation and conceptual prerequisite tags, not yet verified graph IDs.
META={
    "KB33-A-P052-A001":("∀ε>0 ∃N∈ℕ ∀n≥N: |a_n−L|<ε",["实数与绝对值","全称量词与存在量词","数列下标"]),
    "KB33-A-P052-A002":("a_n→L ⇒ ∃M>0 ∀n≥1: |a_n|≤M",["数列ε–N极限","三角不等式","有限集合最值"]),
    "KB33-A-P052-A003":("a_1≤a_2≤…≤sup{a_n}",["单调数列","上确界及实数完备性","数列极限"]),
    "KB33-A-P053-A002":("f∈C([a,b]), y∈[min(f(a),f(b)),max(f(a),f(b))]",["连续函数","闭区间","实数完备性"]),
    "KB33-A-P053-A004":("∃c∈(a,b): f′(c)=(f(b)−f(a))/(b−a)",["闭区间连续与开区间可导","导数","罗尔定理"]),
    "KB33-A-P057-A002":("p=P_H0(T∈E), α=事先规定的拒绝阈值",["古典概率与条件概率","样本分布","检验假设"]),
    "KB33-B-P058-A004":("Δy=f′(x)h+o(h), dy=f′(x)dx",["差商与导数","线性函数","小o渐近符号"]),
    "KB33-B-P059-A002":("F(x)=∫_a^x f(t)dt; F′(x)=f(x)",["定积分","连续函数","中值定理与原函数"]),
    "KB33-C-P065-A001":("¬(p∧¬p), p∨¬p",["经典二值命题","合取析取否定","有限真值表"]),
    "KB33-C-P066-A004":("Q=A L^α K^β; lnQ=lnA+αlnL+βlnK",["正实数的幂","对数运算法则","变量与模型假设"]),
    "KB33-D-P071-A002":("n_min=lcm(p₁,…,pₖ)",["整数整除","最小公倍数","时间单位换算"]),
    "KB33-E-P073-A004":("xₙ=aⁿx₀+bΣ(k=0..n−1)aᵏ",["有限等比数列求和","数学归纳法","递推序列"]),
}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def row(card, legacy, gate):
    wrong=card["bad"]; why=card["why"]
    symbol,prerequisites=META[card["cid"]]
    evidence=next(p for p in gate["pages"] if p["printed_page"]==legacy["source_page"])
    result={
        "editorial_candidate_id":card["cid"],
        "id":"math.hs.editorial.batch54."+card["cid"].lower().replace("-","."),
        "kind":card["kind"], "title":card["title"], "claim":card["claim"],
        "notation":[symbol],
        "syllabus_track":legacy["track"],
        "source_printed_page":legacy["source_page"],
        "source_pdf_sha256":gate["source_pdf_sha256"],
        "source_page_sha256":evidence["pdfkit_page_text_sha256"],
        "source_standard_version":"CN-HS-MATH-2017-REV2020",
        "official_scope_equivalence":"NOT_CERTIFIED",
        "prerequisite_topics":prerequisites,
        "source_editorial_goal":legacy["original_goal"],
        "assumptions":[card["assumptions"]],
        "reasoning_steps":[{"claim":a,"reason":b} for a,b in card["steps"]],
        "counterexample":{"false_claim":wrong,"example":card["counter"],"explanation":why},
        "worked_examples":[{"question":q,"steps":[s1,s2],"answer":a,"check":check}
                           for q,s1,s2,a,check in card["ex"]],
        "boundaries":[card["assumptions"],"该审稿独立于旧关联，未完成官方条款拆分、课标数学等价认证和真实教师签署。"],
        "misconception":{"error":wrong,"why_wrong":why,"repair_question":"请指出缺失的数学假设，并用反例解释为什么不能直接套用结论。"},
        "hint_ladder":card["hints"], "transfer":{"near":card["near"],"far":card["far"]},
        "review":{"status":"REVIEW_PENDING","reviewer_id":None,"reviewed_at":None,"review_record":None},
        "teacher_solution_visibility":"TEACHER_ONLY","source_license":"PROJECT_AUTHORED",
        "proof_verification":"NOT_FORMALLY_CERTIFIED","student_publishable":False,
    }
    return Legacy54.model_validate(result).model_dump()

def build(*,source=None,gate=None,overlay=None,cards=None):
    source=deepcopy(source if source is not None else load(SOURCE))
    gate=deepcopy(gate if gate is not None else load(GATE))
    overlay=deepcopy(overlay if overlay is not None else load(OVERLAY))
    cards=deepcopy(cards if cards is not None else CARDS)
    require(source["source_pdf_sha256"]==gate["source_pdf_sha256"],"source checksum mismatch")
    require(len(gate["pages"])==61 and len({x["printed_page"] for x in gate["pages"]})==61,"61-page denominator incomplete")
    require(all(p["full_page_human_review"]=="PENDING" for p in gate["pages"]),"page falsely human reviewed")
    require(overlay["summary"]["project_candidates"]==313,"editorial count drift")
    require(overlay["summary"]["teacher_approved"]==0 and overlay["summary"]["student_published"]==0,"false approval")
    require(all(not x["teacher_approved"] and not x["student_published"]
                and not x["math_certified"] and not x["official_clause_verified"]
                for x in overlay["rows"]), "an individual editorial record falsely certified")
    require(all(v is None for v in source["official_atomic_denominator"].values()),"false official denominator")
    require(set(source["official_atomic_denominator"])==set(TRACKS),"missing syllabus track")
    require(len(source["source_rows"])==35,"source candidate count drift")
    legacy={r["editorial_id"]:r for r in source["legacy_non_equivalent_rows"]}
    require(len(legacy)==12,"legacy backlog changed")
    ids={c["cid"] for c in cards}
    require(len(cards)==len(ids)==12 and ids==set(legacy),"not all legacy-only targets independently addressed")
    require(set(META)==ids,"missing notation or prerequisite metadata")
    original={r["editorial_id"]:r for r in overlay["rows"]}
    require(len(original)==313,"duplicate editorial identifiers")
    rows=[]
    for card in cards:
        cid=card["cid"];l=legacy[cid];o=original[cid]
        require(l["track"]==o["track"] and l["source_page"]==o["printed_page"],"legacy attribution mismatch")
        require(not o["teacher_approved"] and not o["student_published"] and not o["direct_review_drafts"],"source not legacy-only/unapproved")
        require(l["mathematical_equivalence"]=="NOT_CERTIFIED" and l["teacher_review"]=="REVIEW_PENDING","false legacy equivalence")
        require(len(card["steps"])==3 and len(card["ex"])==2 and len(card["hints"])==3,"incomplete manuscript structure")
        r=row(card,l,gate);rows.append(r)
    require(len({r["id"] for r in rows})==12,"duplicate manuscripts")
    return rows,gate,source,overlay

def payload(rows,gate,source,overlay):
    by_track=Counter(x["track"] for x in source["legacy_non_equivalent_rows"])
    pages=[]
    for p in gate["pages"]:
        pages.append({
            "page":p["printed_page"],"pdf_page_index":p["pdf_page_index"],
            "source_page_sha256":p["pdfkit_page_text_sha256"],
            "source_page_fingerprint_present":True,
            "numbered_marker_occurrences_not_atoms":p["numbered_marker_occurrences_not_atoms"],
            "unnumbered_outlines_not_atoms":p["D_E_unnumbered_topic_outlines_not_atoms"],
            "project_editorial_candidates_not_official_atoms":p["project_editorial_candidates_not_official_atoms"],
            "full_page_manual_atomization":"NOT_COMPLETED",
            "official_atom_count":None,
        })
    return {
        "schema_version":"kb54-legacy-independent-review-and-page-blockers-v1",
        "source_pdf_sha256":source["source_pdf_sha256"], "official_source_pages":len(pages),
        "source_pages":pages,
        "historical_numbered_marker_occurrences_not_atoms":sum(p["numbered_marker_occurrences_not_atoms"] for p in pages),
        "historical_outline_occurrences_not_atoms":sum(p["unnumbered_outlines_not_atoms"] for p in pages),
        "prior_source_candidate_count_not_atoms":35,
        "project_editorial_count_not_atoms":313,
        "legacy_only_replacement_manuscripts":len(rows),
        "legacy_target_ids":[r["editorial_candidate_id"] for r in rows],
        "legacy_target_tracks":dict(sorted(by_track.items())),
        "legacy_mathematical_scope_equivalence_certified":0,
        "legacy_actual_teacher_approvals":0,
        "new_math_general_proofs_formally_certified":0,
        "student_published":0,
        "official_atomic_denominator":{t:None for t in TRACKS},
        "official_coverage_ratio":{t:None for t in TRACKS},
        "student_retrieval":{"student_documents":[],"teacher_solutions":[],"publication":"DENIED"},
        "status":"INDEPENDENT_TEACHER_DRAFTS_ONLY_OFFICIAL_SCOPE_UNVERIFIED",
    }

def render(rows,audit):
    out=["# Batch54｜12项历史非等价课标编辑目标的独立数学待审讲义","",
         "**全部原创、未正式教师审核、不得学生端发布。** 每个目标都有独立审核稿，不代表官方课程原子等价成立。",""]
    for r in rows:
        out.extend(["## "+r["title"],f"**编辑目标**：{r['editorial_candidate_id']} · {r['kind']} · REVIEW_PENDING","",
                    "**课标版本/轨道与来源页指纹**："+r["source_standard_version"]+" / "+r["syllabus_track"]+" / 印刷页"+str(r["source_printed_page"])+" / "+r["source_page_sha256"],
                    "**符号约定**："+"；".join(r["notation"]),"**先修主题（尚未认证图谱边）**："+"、".join(r["prerequisite_topics"]),"",
                    "**精确定义/命题**："+r["claim"],"","**完整前提**："+r["assumptions"][0],"",
                    "**分步论证（待教师复核）**："])
        for j,s in enumerate(r["reasoning_steps"],1):out.append(f"{j}. {s['claim']}（依据：{s['reason']}）")
        out.extend(["","**不适用例**："+r["counterexample"]["example"],
                    "**常见误解**："+r["counterexample"]["false_claim"]+"。纠正："+r["counterexample"]["explanation"],"","**教师侧例题**："])
        for x in r["worked_examples"]:
            out.append(f"- {x['question']} 思路：{'；'.join(x['steps'])}。答案：{x['answer']}。核验：{x['check']}")
        out.append("**启发提示阶梯（不展示教师答案）**："+ " → ".join(r["hint_ladder"]))
        out.extend(["**近迁移**："+r["transfer"]["near"],"**远迁移**："+r["transfer"]["far"],
                    "**限制**："+r["boundaries"][-1],""])
    return "\n".join(out).rstrip("\n")+"\n"

def page_report(a):
    o=["# Batch54｜61页官方课标原子分母阻断清单（逐页机器可审计）","",
       "**61页为待核课程内容来源页数，不是61条知识原子。所有页的完整人工逐条拆分仍未完成。**",
       "历史编号出现次数、D/E提纲、编辑候选及12篇补充稿都不能替代官方原子分母。","",
       "| 印刷页 | PDF页索引 | 编号出现次数 | D/E提纲 | 项目编辑候选 | 完整审查 | 官方原子数 |",
       "|---:|---:|---:|---:|---:|---|---|"]
    for p in a["source_pages"]:
        o.append(f"| {p['page']} | {p['pdf_page_index']} | {p['numbered_marker_occurrences_not_atoms']} | {p['unnumbered_outlines_not_atoms']} | {p['project_editorial_candidates_not_official_atoms']} | NOT_COMPLETED | null |")
    o+=["","正式完成标准：逐页依据本地合法课标原件拆分定义/定理/方法/活动的全部要求，去重与跨页语义核查，独立数学范围审校，最后教师签署七个轨道的冻结分母。",""]
    return "\n".join(o)

def create(check=False):
    rows,gate,source,overlay=build()
    a=payload(rows,gate,source,overlay)
    seed="".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows)
    a["new_review_seed_sha256"]=hashlib.sha256(seed.encode()).hexdigest()
    outputs={SEED:seed,TEXT:render(rows,a),PAGE:page_report(a),
             REPORT:json.dumps(a,ensure_ascii=False,sort_keys=True,indent=2)+"\n"}
    for filename,body in outputs.items():
        if check:
            if not filename.is_file() or filename.read_text(encoding="utf8")!=body:raise ValueError(f"generated asset drift: {filename}")
        else:
            filename.parent.mkdir(parents=True,exist_ok=True);filename.write_text(body,encoding="utf8")
    print(f"Batch54 {'CHECK' if check else 'WRITE'} 12 independent REVIEW_PENDING drafts / 24 teacher examples / 61 source pages tracked / official atoms unresolved")
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");create(ap.parse_args().check)
