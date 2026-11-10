#!/usr/bin/env python3
"""Batch77: 11 authored, review-only counterparts for genuinely unlinked local candidates.

The 26 candidates form a LOCAL editorial denominator. No official curriculum
denominator, proof certification, teacher approval or student publication follows.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from fractions import Fraction as F
from pathlib import Path
import build_kb_batch76_eight_lessons as T
import build_kb_batch76_progress as P

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"knowledge/editorial_review/kb_batch77_unlinked_candidate_drafts.json"
MD=ROOT/"docs/evaluation/KB_BATCH77_ELEVEN_MATH_LESSONS.md"
ITEMS=[]
LINKS={r["candidate_id"]:r for r in P.build()["candidates"]}
QUEUES={r["source_editorial_subspan_id"]:r for r in T.E.audit()["cases"]}

def add(id, anchor, kind, title, definition, symbols, assumptions, statement,
        steps, validity, boundary, counter, wrong, example1, example2,
        hints, near, far, witness, prerequisites):
    source=LINKS[anchor]
    assert not source["linked_teacher_draft_count"],"do not duplicate existing draft"
    r=T.lesson(id,anchor,source["track_hint"],kind,title,definition,symbols,
      assumptions,statement,steps,validity,boundary,counter,wrong,
      [example1,example2],hints,near,far,witness)
    r["prerequisite_topics"]=prerequisites
    r["prerequisite_ids_confirmed"]=False
    r["local_source_mathematical_relation"]=QUEUES[anchor]["proposed_relation"]
    r["source_subspan_sha256"]=source["source_sha256"]
    ITEMS.append(r)

add("KB77-M01","KB75-P016-S03","THEOREM","量词命题的否定、论域及反例构造",
 "在非空论域D中，¬(∀x∈D,P(x))当且仅当∃x∈D,¬P(x)；¬(∃x∈D,P(x))当且仅当∀x∈D,¬P(x)。",
 ["D:非空论域","∀:对所有","∃:存在","¬:逻辑否定"],
 ["论域和谓词P在前后两句完全相同","采用经典二值逻辑"],
 "否定量词须交换∀和∃并否定其内部谓词，不可只改不等式符号。",
 [["否定全称","∀x P(x)失败意味着至少存在一个x使P(x)不成立。"],
  ["否定存在","∃x P(x)失败意味着没有任何x满足P；故每一个x都满足¬P。"],
  ["保留论域","对实数论域的命题不能在取反时悄悄改成整数论域。"],
  ["给出反例","∀x∈R,x²>0为假：x=0；其否定∃x∈R,x²≤0为真。"]],
 "量词交换是逻辑等价规律，不依靠抽样若干数值来证明全称。",
 "空论域也有相应的标准逻辑语义，但本教学例按非空实数域；不把逆否命题与量词否定混同。",
 "错误否定‘所有实数平方都严格正’为‘所有实数平方均非正’；x=1即可否定后者。",
 "只把x²>0改成x²≤0却保留∀，产生比真实否定更强的命题。",
 ("在全体实数论域内，否定∀x∈R,x²>0。","∃x∈R,x²≤0；可取x=0成立。"),
 ("在整数论域内，否定命题∃n∈Z,n²<0。","∀n∈Z,n²≥0；整数平方均非负，因而该否定为真。"),
 ["找出最外层是∀还是∃。","换成另一种量词但保持D。","只在内部P(x)上取逻辑否定，给出见证或证明。"],
 "否定∀n∈N,n≥5并给出一个违例。","用软件断言的‘所有输入通过’和存在失败样本的关系作类比。",
 dict(type="quantifier_negation",truths=[True,False,True],forall=False,exists_not=True),
 ["命题与逻辑联结词","整数量词与不等式"])
add("KB77-M02","KB75-P027-S01","METHOD","复平面关于虚轴的反射与乘i",
 "复数z=x+yi对应点(x,y)，关于虚轴反射得到(-x,y)，对应w=-共轭(z)；乘i得到(-y,x)，一般是逆时针90°旋转而非反射。",
 ["z=x+yi","共轭(z)=x-yi","i²=-1"],
 ["使用标准复平面坐标与通常复数乘法","反射轴是虚轴即x=0"],
 "虚轴反射由z↦-共轭(z)给出；z↦iz通常不是同一个映射。",
 [["确定几何点","z的实部与虚部分别给出横纵坐标。"],
  ["执行反射","虚轴反射改变横坐标符号而保持纵坐标不变。"],
  ["改写复数","(-x)+yi=-(x-yi)=-共轭(z)。"],
  ["比较乘法","i(x+yi)=-y+xi；取z=1两者分别为-1与i。"]],
 "两种映射偶尔在单独点重合不代表映射整体相同。",
 "原点在两种映射下均不变；不能以一个固定点为证据宣布两变换相等。",
 "z=1时关于虚轴反射为-1，乘i为i，结果不同。",
 "把复数乘i一律解释为关于虚轴对称，混淆旋转与反射。",
 ("z=2+3i关于虚轴反射的对应复数。","坐标(2,3)变(-2,3)，故为-2+3i。"),
 ("z=1+i乘i后与反射后分别是什么？","iz=-1+i；-共轭(z)=-1+i，此特例恰好相同，不可推广到所有z。"),
 ["先画出对应的复平面坐标点与作为反射轴的虚轴。","核对关于虚轴反射只改变实部的符号、保持虚部不变。","再单独乘i对照，检查是否为同一变换。"],
 "写出关于实轴反射的复数公式并比较。","用图像处理中水平翻转和图像旋转区别两种变换。",
 dict(type="complex_reflect",x=2,y=3,reflected=[-2,3],rotated=[-3,2]),
 ["复数代数运算","平面坐标变换"])
add("KB77-M03","KB75-P046-S04","METHOD","相关系数与样本均值的区别",
 "对非零方差的成对数值样本，皮尔逊样本相关系数r=Σ(xi-x̄)(yi-ȳ)/sqrt(Σ(xi-x̄)²Σ(yi-ȳ)²)，衡量样本线性关联而非均值。",
 ["x̄,ȳ:样本均值","r:样本相关系数","Sxy:中心化乘积和"],
 ["样本成对观测且n≥2","两变量中心化平方和均严格正"],
 "即使两组样本具有完全相同的各变量均值，相关方向也可以相反。",
 [["建立两组数据","固定x=(0,1,2),令y+=(0,1,2)，另令y-=(2,1,0)。"],
  ["检查均值","两组的x均值均为1，y均值也均为1。"],
  ["计算协同变化","逐对求差并相乘后求和，两组中心化乘积和分别是2和-2。"],
  ["归一化","两组平方偏差和均为2，因而r+=1,r-=-1。"]],
 "相关不是线性回归的因果参数；列联分析面向分类变量，不能直接套此公式。",
 "方差为零使分母为0；样本相关只能描述这组配对观测。",
 "两组样本各自变量均值相同，但一个r=+1另一个r=-1。",
 "通过x和y各自平均数相同来推断二者独立或正相关。",
 ("x=(0,1,2),y=(2,1,0)，r是多少？","中心积和-2，两个偏差平方和都是2，r=-1。"),
 ("x=(0,1,2),y=(0,2,4)，r是多少？","y与x严格正线性，中心化乘积和4，平方和2和8，r=1。"),
 ["先检查成对样本与非零方差。","分别计算x与y的样本均值，并对成对数据中心化。","比较协同方向并计算归一化值。"],
 "给相同边际频数重新配对，讨论相关系数为何变化。","讨论消费数据中同时受季节影响的两个指标为何不能直接认定因果。",
 dict(type="signed_correlation",x=[0,1,2],positive=[0,1,2],negative=[2,1,0]),
 ["样本均值","实数向量的内积与柯西不等式"])
add("KB77-M04","KB75-P056-S04","METHOD","已知总体方差的单样本Z统计量与模型前提",
 "在独立同分布的正态样本且已知总体标准差σ>0条件下，检验均值μ=μ0可用Z=(x̄-μ0)/(σ/√n)；零假设下Z服从标准正态分布。",
 ["μ0:原假设均值","σ>0:已知总体标准差","n:样本数量","Z:检验统计量"],
 ["样本独立来自同一正态总体","σ为已知正值，n≥1，检验不依赖因果解释"],
 "四个样本(1,1,3,3)的均值为2，μ0=1且σ=2时Z=1；统计量的计算不等于直接拒绝原假设。",
 [["求样本均值","样本合计8,样本容量4,均值为2。"],
  ["求标准误","σ/√n=2/2=1，而非σ本身。"],
  ["计算统计量","(2-1)/1=1，此计算不自动给出决策。"],
  ["区分推断","假设检验结论还依赖显著性水平、单双侧备择与模型条件。"]],
 "精确统计量验证仅覆盖此有理数算例；分布结论依赖概率模型，而非四个观测值自身。",
 "若σ未知不能直接套已知总体方差的Z模型；样本不独立或非正态时需重新审查方法适用性。",
 "把总体标准差σ=2误当标准误，会错误算Z=1/2。",
 "未设置显著性水平就凭Z的符号宣称原假设必被拒绝。",
 ("n=4,x=(1,1,3,3),μ0=1,σ=2计算Z。","样本均值x̄=2，已知σ=2且n=4所以标准误=1，统计量Z=1。"),
 ("改为μ0=2,其他保持不变，Z是多少？","x̄=2，故分子0，Z=0；这只是统计量而非结论。"),
 ["确定已知还是未知总体方差。","分别计算样本平均值以及已知总体方差条件下的均值标准误。","再列明原假设、备择假设及决策规则。"],
 "对比未知σ时t检验的额外假设。","在质量控制中区分统计显著与实际重要性。",
 dict(type="known_sigma_z",data=[1,1,3,3],mu0=1,sigma=2,z=1),
 ["样本平均数与方差","正态总体的均值抽样分布"])
add("KB77-M05","KB75-P058-S03","METHOD","一元导数与定积分不能混同",
 "若f在点x0可导，f'(x0)是差商的极限；若f在[a,b]可积，∫_a^b f(x)dx是有向面积型累积量。两者运算对象及前提不同。",
 ["f(x)=x³","f'(x)=3x²","∫_0^2 f(x)dx"],
 ["本例f是全实数上的多项式","被积区间闭且有界，计算采用通常黎曼积分"],
 "f=x³在x=2导数为12，而区间[0,2]的定积分为4；不能交换两种运算。",
 [["导数定义","由((x+h)³-x³)/h=3x²+3xh+h²，h趋零得3x²。"],
  ["代入点值","f'(2)=3×4=12，是指定点的局部变化率。"],
  ["找原函数","F(x)=x⁴/4满足F'=x³。"],
  ["算积分","F(2)-F(0)=16/4=4，量化区间累积量。"]],
 "导数在点的量纲为函数值/自变量，积分的量纲为函数值×自变量。",
 "不可从f在某点可导推断任意区间的原函数表达式；不连续等特殊情形要重新核对积分存在条件。",
 "同一多项式在点2的导数12，与区间[0,2]积分4不相等。",
 "把f'(2)代入积分的计算结果或以面积公式当点变化率。",
 ("给定多项式函数f(x)=x³，求其在x=1处的导数f'(1)。","对x³求导得到3x²，再代入x=1得到该点导数为3。"),
 ("f=x³，求∫_0^1 f(x)dx。","原函数x⁴/4，代端点得1/4，与导数值3不同。"),
 ["先识别题目要求点处变化率还是区间累积。","导数用差商，积分用原函数端点差。","比较结果量纲并核查积分区间。"],
 "证明常数函数导数为0却在非零长度区间有非零积分。","比较速度瞬时值与路程累积量。",
 dict(type="derivative_integral",power=3,point=2,lower=0,upper=2,derivative=12,integral=4),
 ["差商极限","原函数和微积分基本定理"])

add("KB77-M06","KB75-P060-S03","THEOREM","矩形线性系统满列秩与唯一解条件",
 "A为m×n实矩阵。若Ax=b有解且rank(A)=n，则解唯一；若rank(A)<n且有解，则解不唯一。",
 ["A∈R^(m×n)","b∈R^m","rank(A):列秩","ker(A):零空间"],
 ["明确m,n为正整数，b属于A的列空间才保证存在解","判断唯一性时不能把满列秩错当自动保证存在性"],
 "A=((1,0),(0,1),(1,1))为3×2矩阵，b=(2,3,5)时唯一解为(2,3)。",
 [["建立差方程","若x,y均满足Ax=b，则A(x-y)=0。"],
  ["利用满列秩","rank(A)=n时零空间只有零向量，故x-y=0。"],
  ["反向讨论","rank(A)<n则存在v≠0且Av=0，任一解x使x+v也是解。"],
  ["检查存在条件","对示例，第三行方程恰与前两行一致；若b3≠b1+b2，虽然满列秩却无解。"]],
 "有解与唯一是不同条件；方阵det(A)≠0是满列秩的一种特例而非所有矩形系统的判据。",
 "满列秩不能保证每个b都可解，除非进一步满足相容性（或是方阵可逆）。",
 "将b改成(2,3,6)，同一满列秩矩阵无解：前两式强制x=2,y=3而第三式要求x+y=6。",
 "对3×2矩阵强行取行列式，或仅凭rank(A)=n宣布任何b都有唯一解。",
 ("A三行分别(1,0),(0,1),(1,1)，b=(2,3,5)，求解。","前两行得x=2,y=3，第三行2+3=5，故唯一。"),
 ("把b第三分量改成6，有解吗？","前两行仍强制(2,3)，第三行不成立，所以无解，不可因满列秩称有唯一解。"),
 ["先明确系数矩阵的行数和列数，不能直接对非方阵求行列式。","检查是否存在满足所有行的解。","最后用零空间判断该解是否唯一。"],
 "比较欠定系统m<n为什么不能满列秩。","用超定传感器标定说明‘可辨识’与‘数据一致’是两件事。",
 dict(type="rectangular_rank",A=[[1,0],[0,1],[1,1]],x=[2,3],b=[2,3,5],inconsistent_b=[2,3,6]),
 ["线性方程组","列线性相关与齐次零空间"])
add("KB77-M07","KB75-P061-S02","CONCEPT","二维连续联合密度与矩形区域概率",
 "非负函数f(x,y)若在R²的二重积分为1，是二维连续随机向量的联合密度；P((X,Y)∈R)=∬_R f(x,y)dxdy。",
 ["f(x,y)=4xy于[0,1]²","P(X≤a,Y≤b)","f_X(x)=∫ f(x,y)dy"],
 ["本例支撑是单位正方形，区间端点在[0,1]","联合密度非负并且总积分为1"],
 "f(x,y)=4xy于单位正方形满足归一且对应独立的边缘密度2x、2y；左下1/2正方形概率1/16。",
 [["归一化","∫_0^1∫_0^1 4xy dydx=(2∫_0^1 xdx)²=1。"],
  ["计算边缘","固定x对y积分得2x，固定y对x积分得2y。"],
  ["判断独立","本例f(x,y)=f_X(x)f_Y(y)几乎处处成立，故X,Y独立。"],
  ["算矩形概率","∫_0^(1/2)∫_0^(1/2)4xy dydx=(1/2)²(1/2)²=1/16。"]],
 "边缘分布相同不能推出独立，且矩形概率需用二重积分而非某个点的密度值。",
 "若联合密度不归一或负值出现则不是合法密度；不允许将离散概率表直接当连续密度。",
 "只给边缘f_X=f_Y=1不能唯一确定联合依赖结构；同边缘可有不同联合分布。",
 "把f(1/2,1/2)=1说成该点概率为1，或不核对独立就乘边缘区间概率。",
 ("求本例P(X≤1/2,Y≤1/2)。","矩形二重积分为(1/4)(1/4)=1/16。"),
 ("在给定二维联合密度模型下，求边缘概率P(X≤1/2)。","对y积分先得边缘f_X=2x，再积到1/2得到1/4。"),
 ["先验证非负和总积分为1。","画出联合密度支撑和目标矩形区域，明确两个积分上下限。","必要时先求边缘并核对独立性。"],
 "把密度换成4(1-x)(1-y)后重新求矩形概率。","在位置传感器二维误差模型中区分独立与相关噪声。",
 dict(type="joint_rectangle",left=[0,1],right=[1,2],bottom=[0,1],top=[1,2],expected=[1,16]),
 ["一维连续随机变量","二重积分与独立性"])
add("KB77-M08","KB75-P061-S04","METHOD","K均值聚类的平方误差目标与因果边界",
 "给定有限二维点集和固定K个非空簇，K均值的簇内平方误差SSE=Σ_kΣ_{i∈Ck}||xi-μk||²，其中μk是该簇样本均值。",
 ["xi∈R²:观测向量","Ck:第k簇","μk:簇中心","SSE:簇内平方误差和"],
 ["K为介于1和样本数之间的正整数","每个样本恰属于一个非空簇，点有一致的量纲和特征尺度"],
 "四点(0,0),(0,1),(10,10),(10,11)划为前后两簇时中心分别(0,1/2),(10,21/2)，SSE=1。",
 [["计算各中心","两个簇的第一坐标均恒定，第二坐标分别是0,1与10,11的均值。"],
  ["计算每点残差","同一簇两个点到中心的平方距离各为1/4。"],
  ["累计目标","四个残差平方相加得到SSE=1，越小代表该划分簇内紧密。"],
  ["说明解释边界","优化几何分组目标并不建立分组原因或因果效应。"]],
 "K均值不是有监督分类器；所得簇编号可置换且受特征尺度影响。",
 "K>样本数时不可能分为K个非空簇；两类标签本身不能推出自变量导致结果。",
 "把高身高簇的成绩较高直接推断身高导致成绩较好，缺乏干预或识别条件。",
 "直接用簇编号作为处理组随机分配结果，或忽略样本量纲。",
 ("计算(0,0),(0,1)的中心和SSE。","中心(0,1/2)，两点平方偏差各1/4，故SSE=1/2。"),
 ("四点两两聚成两组时总SSE是多少？","两组各为1/2，总计1；这只评价给定划分，不证明全局最优。"),
 ["先确认二维特征的计量单位及需要构造的非空簇数K。","对每个非空簇内的全部样本逐坐标计算算术平均数。","计算每个点的平方欧氏距离并求和，再讨论局限。"],
 "对原数据同时放大一个坐标10倍，比较SSE的变化。","解释用户分群与A/B随机实验的区别。",
 dict(type="cluster_sse",points=[[0,0],[0,1],[10,10],[10,11]],assignments=[0,0,1,1],expected=1),
 ["二维坐标及平方距离","算术平均数与无监督学习"])
add("KB77-M09","KB75-P063-S02","THEOREM","有限插值数据不能唯一确定曲线模型",
 "若给定三个不同横坐标x=0,1,2且y=x²，则二次多项式p(x)=x²插值这些点；但q(x)=x²+kx(x-1)(x-2)对任意实数k也通过三点。",
 ["p(x)=x²","q_k(x)=x²+kx(x-1)(x-2)","k∈R"],
 ["只给出三个离散观测点且不限定候选模型最高次数","横坐标为三个不同实数0,1,2"],
 "即使三个点都在抛物线y=x²上，仍有无穷多条更高次多项式曲线穿过它们。",
 [["构造原插值","p(0)=0,p(1)=1,p(2)=4，满足给定数据。"],
  ["构造零化因子","h(x)=x(x-1)(x-2)在三个观测横坐标上都为0。"],
  ["添加自由参数","q_k=p+kh在已观察点与p完全一致。"],
  ["展示外推差异","在x=3时p(3)=9,q_1(3)=9+3×2×1=15。"]],
 "如果额外规定多项式次数不超过2，三个不同横坐标可唯一确定二次及以下插值多项式。",
 "不能把精确插值视为唯一真实机制，也不保证未观测区域预测准确。",
 "q_1和p对三点完全一致，但在x=3分别给出15和9。",
 "用三点完全拟合就宣布模型唯一正确，不检验模型复杂度和外推。",
 ("取k=1，求q(0),q(1),q(2)。","每个位置h(x)=0，所以得到0,1,4，与p一致。"),
 ("取k=1，求q(3)并与p(3)比较。","q(3)=15，p(3)=9，外推相差6。"),
 ["找出全部已观测横坐标。","构造在这些点为零的多项式。","添加任意倍数并检查未观测点。"],
 "用四个离散点构造不同四次插值函数。","比较模型拟合误差与未见数据预测误差。",
 dict(type="interpolation_alias",xs=[0,1,2],k=1,query=3,p=9,q=15),
 ["多项式与因式定理","函数拟合与外推"])
add("KB77-M10","KB75-P063-S03","THEOREM","指数模型严格单调与非零周期的区分",
 "函数f(t)=2^t在R上严格递增，因此不存在T>0使所有t都有f(t+T)=f(t)；g(t)=sin(t)则满足g(t+2π)=g(t)。",
 ["f(t)=2^t","g(t)=sin(t)","T:周期长度"],
 ["底数2大于1，t是实数","周期定义要求T>0且对定义域内所有t恒等成立"],
 "指数增长模型不具有正周期，而正弦函数有正周期2π；有限观测相同并不充分判定模型。",
 [["利用指数律","2^(t+T)=2^t·2^T。"],
  ["反证周期","若为周期，则2^T=1；底数2>1时只能T=0，违背T>0。"],
  ["证明正弦周期","由单位圆角度加整周性质sin(t+2π)=sin(t)。"],
  ["区分有限采样","少数采样点的重复可能是混叠，不能代替全域周期恒等式。"]],
 "严格增长与周期性对同一非平凡函数不相容；在有限数据上只能提出待检验的模型假设。",
 "指数底数1对应常数函数有任意正周期，不能将底数2的结论无条件推广。",
 "2^0=1,2^1=2，不满足T=1的周期等式，而sin(0)=sin(2π)=0。",
 "仅见两个时刻数值接近就宣布数据严格周期，或以单调指数强行套三角周期。",
 ("f(t)=2^t，比较f(0)与f(1)。","分别为1和2，说明T=1不是周期。"),
 ("g(t)=sin(t)，求g(0)与g(2π)。","两者为0；验证周期还必须检查任意t，不能仅看这一点。"),
 ["从定义写出对所有t的等式。","用指数律或三角恒等式。","排除T=0，说明有限数据检验的局限。"],
 "检查f(t)=(1/2)^t为何也没有正周期。","分析潮汐时间序列可能受到长期趋势与周期项共同影响。",
 dict(type="exponential_not_periodic",base=2,t=0,T=1,first=1,shifted=2),
 ["指数函数单调性","三角函数与周期定义"])
add("KB77-M11","KB75-P066-S02","METHOD","经济建模的量纲一致性与盈亏平衡",
 "单价p（元/件）、单位可变成本c（元/件）、固定成本K（元）和销售量n（件）构成利润Π(n)=(p-c)n-K（元）；不能直接将不同量纲量相加。",
 ["p,c:元/件","n:件","K:元","Π:元"],
 ["本例p,c,K为非负有理数且p>c，销售件数n为非负整数","本模型不含税费、折扣、容量和需求弹性"],
 "p=8,c=5,K=30时盈亏平衡n=10；若销量必须为整数，至少10件才有非负利润。",
 [["明确计量单位","(元/件)乘(件)得到元，才可以与固定成本K相减。"],
  ["写出利润","Π=8n-5n-30=3n-30。"],
  ["求平衡阈值","Π≥0当且仅当3n≥30，即n≥10。"],
  ["检查反例","n=9时利润为-3元；仅解实数方程还须核对整数可行域。"]],
 "模型数学结论基于假设，不把销售量外推、价格不变当作现实必然。",
 "若p≤c且K>0，不存在有限非负销量能令利润非负；不可再套正毛利率阈值公式。",
 "把8元/件和30元直接相减写成-22元/件属于量纲混乱。",
 "忽略单位或在p=c时除以(p-c)，制造零分母。",
 ("p=8,c=5,K=30,n=9利润是多少？","Π=(8-5)×9-30=-3元，仍亏损。"),
 ("维持同样售价、单位成本及固定成本，销量n=11时利润为多少？","将销售量n=11代入利润模型Π=(8-5)n-30，得到3元且利润为正。"),
 ["为售价、成本、销量与利润分别写出正确量纲，拒绝直接混加。","先将收入和成本统一成元。","解不等式并核对销售量整数限制。"],
 "若每件售价9元、成本5元、固定成本31元，求最小整数销量。","讨论折扣导致单价随销量改变时线性模型失效。",
 dict(type="unit_profit",price=8,cost=5,fixed=30,quantity=10,profit=0,below_quantity=9,below_profit=-3,units=["元/件","元/件","元","件"]),
 ["一次不等式","函数模型的定义域与量纲"])

def Q(value):
    if type(value) is int:return F(value)
    if isinstance(value,list) and len(value)==2 and all(type(z) is int for z in value) and value[1]!=0:
        return F(*value)
    raise ValueError("exact integer or [integer,nonzero integer] only")

def case_check(w):
    t=w.get("type")
    if t=="quantifier_negation":
        vals=w["truths"]
        assert isinstance(vals,list) and len(vals)>=2 and all(type(z) is bool for z in vals)
        assert type(w["forall"]) is bool and type(w["exists_not"]) is bool
        assert all(vals)==w["forall"] and any(not z for z in vals)==w["exists_not"]
    elif t=="complex_reflect":
        x,y=Q(w["x"]),Q(w["y"])
        assert [Q(v) for v in w["reflected"]]==[-x,y]
        assert [Q(v) for v in w["rotated"]]==[-y,x] and [x,y]!=[0,0]
    elif t=="signed_correlation":
        x=[Q(v) for v in w["x"]];a=[Q(v) for v in w["positive"]];b=[Q(v) for v in w["negative"]]
        assert len(x)==len(a)==len(b)>=3
        n=len(x); xb=sum(x)/n; ab=sum(a)/n;bb=sum(b)/n
        ss=lambda z,mean:sum((u-mean)**2 for u in z)
        cov=lambda z,mean:sum((i-xb)*(j-mean) for i,j in zip(x,z))
        den=ss(x,xb)
        assert den>0 and ss(a,ab)==ss(b,bb)==den and cov(a,ab)==den and cov(b,bb)==-den
        assert xb==ab==bb
    elif t=="known_sigma_z":
        data=[Q(v) for v in w["data"]];n=len(data)
        assert n>=2 and math.isqrt(n)**2==n
        assert Q(w["sigma"])>0 and (sum(data)/n-Q(w["mu0"]))*math.isqrt(n)/Q(w["sigma"])==Q(w["z"])
    elif t=="derivative_integral":
        p=w["power"];assert type(p) is int and 0<=p<=10
        at,lo,hi=Q(w["point"]),Q(w["lower"]),Q(w["upper"])
        assert lo<=hi
        assert p*at**(p-1)==Q(w["derivative"])
        assert (hi**(p+1)-lo**(p+1))/(p+1)==Q(w["integral"])
    elif t=="rectangular_rank":
        a=[[Q(c) for c in row] for row in w["A"]]
        assert len(a)>=2 and all(len(row)==2 for row in a)
        minors=[a[i][0]*a[j][1]-a[i][1]*a[j][0] for i in range(len(a)) for j in range(i+1,len(a))]
        assert any(v!=0 for v in minors)
        x=[Q(v) for v in w["x"]]
        assert len(x)==2
        b=[sum(v*xi for v,xi in zip(row,x)) for row in a]
        assert b==[Q(v) for v in w["b"]]
        ib=[Q(v) for v in w["inconsistent_b"]]
        assert len(ib)==len(b) and ib!=b
        assert any(a[i][0]*x[0]+a[i][1]*x[1]!=ib[i] for i in range(len(a)))
        # Inconsistency is certified via the same full-column-rank linear solution
        # determined by any nonsingular 2x2 row subset.
        i,j=next((i,j) for i in range(len(a)) for j in range(i+1,len(a))
                 if a[i][0]*a[j][1]-a[i][1]*a[j][0])
        det=a[i][0]*a[j][1]-a[i][1]*a[j][0]
        xx=(ib[i]*a[j][1]-a[i][1]*ib[j])/det
        yy=(a[i][0]*ib[j]-ib[i]*a[j][0])/det
        assert any(row[0]*xx+row[1]*yy!=target for row,target in zip(a,ib))
    elif t=="joint_rectangle":
        lo,hi,bot,top=map(Q,(w["left"],w["right"],w["bottom"],w["top"]))
        assert 0<=lo<=hi<=1 and 0<=bot<=top<=1
        assert (hi**2-lo**2)*(top**2-bot**2)==Q(w["expected"])
    elif t=="cluster_sse":
        pts=[[Q(v) for v in row] for row in w["points"]]
        ids=w["assignments"];assert len(ids)==len(pts)>=3
        assert all(len(row)==2 for row in pts) and all(type(i) is int for i in ids)
        assert set(ids)=={0,1}
        sse=F(0)
        for label in (0,1):
            group=[p for p,i in zip(pts,ids) if i==label]
            mx=sum(p[0] for p in group)/len(group);my=sum(p[1] for p in group)/len(group)
            sse+=sum((p[0]-mx)**2+(p[1]-my)**2 for p in group)
        assert sse==Q(w["expected"])
    elif t=="interpolation_alias":
        xs=[Q(v) for v in w["xs"]];k=Q(w["k"]);t0=Q(w["query"])
        assert xs==[0,1,2] and k!=0 and t0 not in xs
        p=t0*t0;q=p+k*t0*(t0-1)*(t0-2)
        assert p==Q(w["p"]) and q==Q(w["q"]) and p!=q
    elif t=="exponential_not_periodic":
        b,t0,T=map(Q,(w["base"],w["t"],w["T"]))
        assert b.denominator==1 and 1<b<=16 and t0.denominator==T.denominator==1 and 0<=t0<=10 and 0<T<=10
        assert b**t0==Q(w["first"]) and b**(t0+T)==Q(w["shifted"]) and Q(w["shifted"])>Q(w["first"])
    elif t=="unit_profit":
        assert w["units"]==["元/件","元/件","元","件"]
        p,c,f=Q(w["price"]),Q(w["cost"]),Q(w["fixed"])
        n=w["quantity"];b=w["below_quantity"]
        assert p>c>=0 and f>=0 and type(n) is int and type(b) is int and 0<=b<n
        assert (p-c)*n-f==Q(w["profit"]) and (p-c)*b-f==Q(w["below_profit"])
        assert Q(w["profit"])>=0 and Q(w["below_profit"])<0
    else:raise ValueError("unknown finite witness type")
    return True

def canonical(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def build():
    prior=P.build()
    assert len(ITEMS)==11 and len({r["id"] for r in ITEMS})==11
    queue=T.E.audit()
    old=json.loads(T.P.OUT.read_text(encoding="utf8"))["teacher_drafts"]
    already=old+T.build()["teacher_drafts"]
    existing={r["source_editorial_subspan_id"] for r in already}
    missing={r["candidate_id"] for r in prior["candidates"] if not r["linked_teacher_draft_count"]}
    assert {r["source_editorial_subspan_id"] for r in ITEMS}==missing and not existing.intersection(missing)
    for r in ITEMS:
        key=r["source_editorial_subspan_id"]
        assert r["curriculum_track_hint"]==LINKS[key]["track_hint"]
        assert r["source_subspan_sha256"]==LINKS[key]["source_sha256"]
        assert r["local_source_mathematical_relation"]==QUEUES[key]["proposed_relation"]
        assert r["teacher_review"]=="REVIEW_PENDING" and r["teacher_signature"] is None
        assert r["mathematical_certification"]=="NOT_FORMALLY_CERTIFIED"
        assert r["teacher_solution_visibility"]=="TEACHER_ONLY" and not r["student_publishable"]
        assert not r["independent_challenge_solution_reveal"]
        assert r["teacher_proof_review"]=="NOT_COMPLETED" and r["official_atom_count"] is None
        assert r["source_license"]=="ORIGINAL_PROJECT_AUTHORED"
        assert not r["prerequisite_ids_confirmed"] and len(r["prerequisite_topics"])>=2
        assert r["knowledge_kind"] in {"CONCEPT","THEOREM","METHOD"}
        assert all(isinstance(r[k],str) and len(r[k])>=12 for k in ("title","definition","statement",
          "mathematical_validity","invalid_boundary","counterexample","common_wrong_method","near_transfer","far_transfer"))
        assert len(r["reasoning_steps"])>=4
        assert all(len(s)==2 and isinstance(s[0],str) and len(s[0])>=3 and isinstance(s[1],str) and len(s[1])>=15 for s in r["reasoning_steps"])
        assert len(r["symbols"])>=2 and len(r["assumptions"])>=2
        assert len(r["worked_examples"])==2 and all(len(q)>12 and len(ans)>16 for q,ans in r["worked_examples"])
        assert len(r["graduated_hints"])==3 and all(len(h)>10 for h in r["graduated_hints"])
        case_check(r["finite_case"])
    newmap={r["source_editorial_subspan_id"]:r["id"] for r in ITEMS}
    candidates=[]
    for row in prior["candidates"]:
        linked=sorted(row["linked_review_only_teacher_draft_ids"]+([newmap[row["candidate_id"]]] if row["candidate_id"] in newmap else []))
        candidates.append(dict(candidate_id=row["candidate_id"],track_hint=row["track_hint"],
          source_sha256=row["source_sha256"],review_only_teacher_draft_ids=linked,
          review_only_teacher_draft_count=len(linked),official_atom_id=None,
          teacher_review="REVIEW_PENDING",source_certified=False,
          teacher_approved=False,student_publishable=False))
    assert len(candidates)==26 and all(r["review_only_teacher_draft_count"]>0 for r in candidates)
    by_track={track:dict(local_candidates=sum(r["track_hint"]==track for r in candidates),
        with_review_only_drafts=sum(r["track_hint"]==track and r["review_only_teacher_draft_count"]>0 for r in candidates),
        official_denominator=None) for track in queue["official_denominators"]}
    return dict(schema_version="kb77-remaining-candidate-review-only-v1",
        source_pdf_sha256=queue["source_pdf_sha256"],source_queue_sha256=hashlib.sha256(T.E.OUT.read_bytes()).hexdigest(),
        prior_local_coverage_sha256=hashlib.sha256(P.OUT.read_bytes()).hexdigest(),
        local_denominator=26,local_candidates_with_drafts=26,remaining_local_candidates_without_drafts=0,
        new_review_only_drafts=11,new_bounded_exact_witnesses=11,
        official_denominators=queue["official_denominators"],teacher_full_page_reviews=0,
        formal_math_certifications=0,teacher_approvals=0,student_publications=0,
        by_track=by_track,candidates=candidates,teacher_drafts=ITEMS,
        claim="26/26 only measures this editorial candidate pool, NOT course completeness.")

def validate(x):
    expected=build()
    assert canonical(x)==canonical(expected),"generated file may be tampered or stale"
    assert x["teacher_approvals"]==x["student_publications"]==x["formal_math_certifications"]==0
    assert all(z is None for z in x["official_denominators"].values())
    assert all(not r["teacher_approved"] and not r["student_publishable"] for r in x["candidates"])
    return True

def markdown(x):
    out=["# Batch77｜11个旧候选补充教师侧原创建议稿（非国家课标分母）","",
      "- 局部26个编辑候选已有教师草案关联26个，新增11篇；所有官方七轨分母仍未知。",
      "- 新增11份稿件含22道解答例题、≥44条分步解释、33条分层提示、22项近远迁移、11项有理数有限实例。",
      "- 独立符号或精确计算只验证指定有限实例，不签发一般证明认证。教师审核0、正式发布0。",""]
    for row in x["teacher_drafts"]:
        out += [f"## {row['id']}｜{row['title']}",
          f"来源：{row['source_editorial_subspan_id']}｜{row['curriculum_track_hint']}｜{row['source_subspan_sha256']}",
          f"定义：{row['definition']}",f"前提：{'；'.join(row['assumptions'])}",
          f"结论：{row['statement']}", "逐步推理（待教师核对）："]
        out += [f"{i}. {label}：{body}" for i,(label,body) in enumerate(row["reasoning_steps"],1)]
        out += ["失效前提："+row["invalid_boundary"],"反例："+row["counterexample"],
                "典型错因："+row["common_wrong_method"],"原创教师侧例题："]
        out += [f"- {q} → {a}" for q,a in row["worked_examples"]]
        out += ["三级提示："+ " → ".join(row["graduated_hints"]),
                "近迁移："+row["near_transfer"],"远迁移："+row["far_transfer"],""]
    out += ["## 尚未完成","七轨正式分母未知；61页正式教师逐条审核0；历史538条证明步骤未认证、10组冲突未裁决；所有11篇需教师数学审稿。",""]
    return "\n".join(out)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    obj=build();validate(obj);md=markdown(obj)
    if args.check:
        assert OUT.read_text(encoding="utf8")==canonical(obj)
        assert MD.read_text(encoding="utf8")==md
    else:
        OUT.write_text(canonical(obj),encoding="utf8")
        MD.write_text(md,encoding="utf8")
    print("Batch77 11 authored drafts; 26/26 local links; 11 bounded exact witnesses; official denominators unknown")
if __name__=="__main__":main()
