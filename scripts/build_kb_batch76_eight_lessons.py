#!/usr/bin/env python3
"""Eight new teacher-only lessons on cross-track mathematical prerequisites.

Hand-written mathematical arguments; independent bounded exact witnesses.
Neither the witnesses nor authored reasoning constitute formal proof certification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import build_kb_batch76_equivalence as E
import build_kb_batch75_lessons as P

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"knowledge/editorial_review/kb_batch76_cross_track_teacher_drafts.json"
MD=ROOT/"docs/evaluation/KB_BATCH76_EIGHT_MATH_LESSONS.md"

def lesson(id,anchor,track,kind,title,definition,symbols,assumptions,claim,steps,
           validity,boundary,counter,error,examples,hints,near,far,witness):
 row=P.lesson(id,anchor,track,kind,title,definition,symbols,assumptions,claim,
   steps,validity,boundary,counter,error,examples,hints,near,far,witness)
 row["source_editorial_subspan_id"]=anchor
 row["source_license"]="ORIGINAL_PROJECT_AUTHORED"
 return row

L=[
lesson("KB76-M01","KB75-P052-S02","ELECTIVE_A","THEOREM","数列收敛的ε-N定义与非例",
 "实数列(a_n)收敛到L是指对任意ε>0,存在正整数N,使所有n≥N均满足|a_n-L|<ε。",
 ["n∈N+","ε>0","N:与ε有关的正整数"],["论域是从n=1起的实数数列","ε为任意严格正的实数,而不是某个指定阈值"],
 "a_n=1/n收敛到0;有界性本身不蕴含收敛。",
 [["明确量词顺序","先任取ε>0,再选N,最后必须对所有n≥N成立。"],
 ["构造N","由阿基米德性质存在正整数N>1/ε。"],
 ["逐项核验","当n≥N时0<1/n≤1/N<ε,故|a_n-0|<ε。"],
 ["给出不适用边界","b_n=(-1)^n有界却有两个不同常值子列,不能收敛到单个实数。"]],
 "ε-N证明是尾项全称性质,不能仅展示若干项逼近。",
 "有界数列不必收敛,前有限多项也不能代替对所有尾项的证明。",
 "(-1)^n交替取-1和1,两条子列极限不一致。",
 "将观察前10项靠近零误当成对任意ε的尾项证明。",
 [["求1/n在ε=1/4下可行的N。","任取N=5,对所有n≥5有1/n≤1/5<1/4。"],
 ["对a_n=2/n,ε=1/5选N。","只需N>10,可取N=11;所有n≥11满足2/n<1/5。"]],
 ["先写出∀ε>0,∃N,∀n≥N的顺序。","将误差化成便于控制的不等式。","构造严格大于阈值的正整数N并核对等号边界。"],
 "证明(a/n)→0时说明a是固定实数而不是随n变化。",
 "用数列收敛与算法迭代误差的停止阈值作对比。",
 dict(type="sequence_threshold",numerator=1,epsilon=[1,4],N=5)),
lesson("KB76-M02","KB75-P052-S03","ELECTIVE_A","CONCEPT","函数极限存在并不推出连续",
 "f在x0处连续要求f(x0)有定义,极限lim(x→x0)f(x)存在,且此极限等于f(x0)。",
 ["x0=0","lim_{x→0}","f(0):点值"],["考察点0在函数定义域内","左右趋近时遵守邻域内的函数定义"],
 "f(x)=x²(x≠0)而f(0)=1在0的极限为0,但并不连续。",
 [["处理去心邻域","当0<|x|<δ时使用x²,不能把f(0)=1混入极限。"],
 ["验证极限","任取ε>0,选δ=√ε,则0<|x|<δ使|x²-0|<ε。"],
 ["核对点值","按题设f(0)=1,因此极限0≠1。"],
 ["判定结论","连续的三项条件未同时满足,0为可去间断点。"]],
 "判断连续必须将极限与点值比较,不能只算出一个极限。",
 "若考察点根本不在定义域中,不能声称函数在该点连续。",
 "g(x)=x²(x≠0),g(0)=1在0处不连续,尽管两侧极限同为0。",
 "把函数图像的邻近趋势当作端点赋值。",
 [["f(x)=x²(x≠0),f(0)=1,判断0处连续吗？","极限为0,点值1,因此不连续;连续所需的相等条件失败。"],
 ["若改定义f(0)=0呢？","其余保持x²,极限与点值均为0,故在0连续。"]],
 ["先确认f(x0)是否定义。","从去心邻域求两侧极限。","将极限与原点值逐项比较。"],
 "区分跳跃间断点和可去间断点。",
 "在传感器校准表中解释插值极限与单个异常赋值的区别。",
 dict(type="point_limit_mismatch",center_value=1,limit_value=0,sample_x=[1,2],sample_y=[1,4])),
lesson("KB76-M03","KB75-P052-S04","ELECTIVE_A","THEOREM","微积分基本定理与求导积分前提",
 "若g在闭区间[a,b]连续,F为满足F'=g的原函数,则∫_a^b g(x)dx=F(b)-F(a)。",
 ["g(x)=2x","F(x)=x²","a,b:积分上下限"],["g在[a,b]连续","F在区间内可导且F'(x)=g(x)","a≤b且均为有限实数"],
 "在上述条件下,∫_0^2 2x dx=4,不能忽略连续性及原函数检验。",
 [["说明原函数存在性","连续性允许定义G(x)=∫_a^xg(t)dt并在区间内部有G'=g。"],
 ["证明导数相同","若F'=g,则(G-F)'=0,连通区间上的G-F为常数。"],
 ["计算端点差","由G(a)=0得G(b)=F(b)-F(a),即定积分值。"],
 ["核对具体例子","F(x)=x²满足F'=2x,所以∫_0^2 2x dx=2²-0²=4。"]],
 "不能将不具备连续性和原函数条件的任意表达式直接套用此版本定理。",
 "若把F(x)=x³错当成2x的原函数,所得端点差8不等于实际面积4。",
 "g(x)=2x,错误选F=x³时F'=3x²≠2x,端点差会得到错误值。",
 "不检查F'=g,只凭形式相似写出上下限代入。",
 [["求∫_0^2 2x dx。","F=x²的导数为2x,端点差4-0=4。"],
 ["求∫_0^1 3x² dx。","F=x³的导数为3x²,端点差1-0=1。"]],
 ["先检查被积函数在区间的连续性。","给出一个F并求导核对F'=g。","最后计算F(b)-F(a),检查上下限顺序。"],
 "比较积分上下限颠倒后的符号。",
 "用速度连续模型解释位移与端点原函数差的含义。",
 dict(type="fundamental_calculus",scale=2,power=1,a=0,b=2,expected=4)),
lesson("KB76-M04","KB75-P056-S03","ELECTIVE_A","CONCEPT","二维联合分布边缘化与独立性",
 "有限二维离散随机向量(X,Y)的联合概率表p_ij≥0且总和为1;边缘概率P(X=i)=Σ_j p_ij。若独立则每格p_ij=P(X=i)P(Y=j)。",
 ["p_ij:联合质量","p_i+:行边缘","p_+j:列边缘"],["两维取值集合均有限","联合表所有概率非负且总和恰为1"],
 "合法联合概率表的行列边缘可精确计算;共同边缘相同也不能保证独立。",
 [["核验归一化","示例表四格1/8,3/8,1/4,1/4总和为1。"],
 ["计算行边缘","按各行两个联合格子求和,得到行边缘分别为1/2和1/2。"],
 ["计算列边缘","两列分别3/8和5/8,行列各自都归一。"],
 ["检验独立","左上格若独立应为(1/2)(3/8)=3/16,但实际1/8,故不独立。"]],
 "联合分布给定后才能边缘化;只知道边缘通常不能唯一恢复联合分布。",
 "相关为0或边缘均匀都不能一般推出随机变量独立。",
 "有相同边缘(1/2,1/2)的独立四格1/4与完全依赖对角线1/2属于不同联合表。",
 "把两个边缘相乘当作所有联合事件概率,漏掉独立性假设。",
 [["求联合表第一行1/8,3/8的行边缘。","求和1/8+3/8=1/2,因为两格属于同一个X取值的全部Y情形。"],
 ["第一列1/8和1/4,求列边缘。","1/8+1/4=3/8,不能直接认为行边缘等于列边缘。"]],
 ["先逐项核对非负且总和为1。","沿被消去的坐标求和。","检验独立时逐格比较联合与边缘乘积。"],
 "构造边缘完全相同但联合结构不同的两个2×2表。",
 "用合成调查中的年龄与购买行为说明不能从单变量分布还原联合分布。",
 dict(type="joint_table",cells=[[1,8],[3,8],[1,4],[1,4]],rows=[[1,2],[1,2]],columns=[[3,8],[5,8]],independent=False)),
lesson("KB76-M05","KB75-P061-S03","ELECTIVE_B","METHOD","一元最小二乘直线与因果推断的边界",
 "对n≥2组实数数据(x_i,y_i),若Σ(x_i-x̄)²>0,最小二乘直线y≈a+bx中b=Σ(x_i-x̄)(y_i-ȳ)/Σ(x_i-x̄)²,a=ȳ-bx̄。",
 ["x̄:样本x均值","ȳ:样本y均值","b:拟合斜率"],["n≥2且样本x不全相等","仅声明有限样本平方误差最小,没有假定因果性"],
 "对(0,1),(1,3),(2,5),唯一最小二乘斜率为2,截距1。",
 [["展开损失","最小化Σ(y_i-a-bx_i)²,分别对a,b求导并令其为0。"],
 ["解正规条件","第一个条件得a=ȳ-bx̄,代入另一个得b的协方差/方差比。"],
 ["检查分母","Σ(x_i-x̄)²>0时斜率解唯一,否则斜率不可识别。"],
 ["代入实例","x̄=1,ȳ=3,分子4,分母2,得到b=2,a=1。"]],
 "回归系数是描述/预测关系;未经实验或识别假设不能自动解释为因果效应。",
 "所有x相同时分母为0;不同变量共享时间趋势也不代表存在直接因果。",
 "x全部为1时无论y如何变化,不能通过上述公式得到唯一斜率。",
 "把b>0解释为x必然导致y上升或直接除以零方差。",
 [["对x=0,1,2,y=1,3,5求拟合斜率。","x均值1,y均值3,中心乘积和4,x平方偏差和2,得斜率2。"],
 ["x=1,2,3,y=5,5,5的斜率是多少？","中心化y均为0,斜率0,截距5,并不代表x会导致y恒定。"]],
 ["先检查样本至少两点且x值不全相同。","计算x,y各自样本均值。","用中心化公式求斜率,再讨论不可推断的因果结论。"],
 "在包含异常值的样本中比较OLS与鲁棒方法的假设。",
 "讨论网站流量与广告投放同时上涨的共同因素问题。",
 dict(type="ols_line",x=[0,1,2],y=[1,3,5],slope=2,intercept=1)),
lesson("KB76-M06","KB75-P060-S01","ELECTIVE_B","THEOREM","三维叉积的垂直性与交换顺序",
 "在定向右手标准正交坐标系的R³中,a×b=(a₂b₃-a₃b₂,a₃b₁-a₁b₃,a₁b₂-a₂b₁),与a及b均正交。",
 ["a,b∈R³","a×b:向量叉积","·:欧氏内积"],["三维右手标准正交坐标系","分量为有限实数并采用通常欧氏内积"],
 "a×b与a,b正交且b×a=-(a×b);若a,b线性相关则叉积为零。",
 [["定义分量","按右手定向的坐标公式逐分量构造。"],
 ["核对正交","a·(a×b)展开后正负项两两相消为0,b·(a×b)同理。"],
 ["交换次序","互换a,b后每个分量都改变符号。"],
 ["讨论退化","a,b平行时各2×2行列式为0,叉积为零但没有唯一非零法向量。"]],
 "长度等于平行四边形面积,但当输入退化时不能用零向量定单位法向。",
 "不能当作普通数量乘法使用交换律a×b=b×a。",
 "e1×e2=e3而e2×e1=-e3,只在叉积为零时二者相同。",
 "把叉积和内积混淆,或者忘记右手坐标系方向。",
 [["a=(1,0,0),b=(0,1,0)求叉积。","叉积(0,0,1),同时与a、b内积都为0。"],
 ["a=(1,1,0),b=(0,1,1)求叉积。","叉积(1,-1,1),点乘a得0,点乘b也得0。"]],
 ["确认三维向量和定向坐标系。","展开叉积的三个分量。","与原两个向量点乘核零,检查交换符号。"],
 "讨论a,b共线时为何无法归一化叉积。",
 "利用空间平面法向量解释真实三维姿态估计的退化工况。",
 dict(type="cross_product",a=[1,1,0],b=[0,1,1],expected=[1,-1,1])),
lesson("KB76-M07","KB75-P063-S04","ELECTIVE_B","METHOD","参数曲线斜率及参数导数零分母",
 "若x(t),y(t)在t0邻域内连续可导,且x'(t0)≠0,则曲线在t0附近可视为y关于x的局部函数,切线斜率为y'(t0)/x'(t0)。",
 ["x(t)=t²","y(t)=t³","t0:参数点"],["参数函数在t0附近连续可导","x'(t0)≠0是按商式求切线斜率的必需前提"],
 "t0=1时x'=2,y'=3,斜率3/2;在t0=0不能直接作0/0,但这不代表没有切线。",
 [["求参数导数","由幂函数求导,x'=2t,y'=3t²。"],
 ["检查非退化","t0=1时x'=2≠0,故局部可用x作坐标。"],
 ["使用链式法则","dy/dt=(dy/dx)(dx/dt),于是dy/dx=3t/2。"],
 ["核对零分母","t0=0时x'=0,y'=0,公式0/0无定义;须改用点集或极限独立研究切线。"]],
 "参数点不一定单射,同一点可能对应多个切向;不能只看图形猜测斜率。",
 "零参数导数仅阻止商式推导,不直接证明没有几何切线。",
 "x=t²,y=t³在t=0得到0/0,却具有水平半切线方向,需分别研究。",
 "把y'(t)直接当作dy/dx或消去dx/dt=0。",
 [["t=1时x=t²,y=t³切线斜率。","dx/dt=2,dy/dt=3,所以斜率3/2。"],
 ["t=-1时切线斜率是多少？","dx/dt=-2,dy/dt=3,因此斜率-3/2,不同参数可能指向不同切向。"]],
 ["先分别对x(t),y(t)求导。","检查dx/dt是否为零。","仅在非零时作比,并考虑参数点与曲线点区别。"],
 "比较圆的参数化x=cos t,y=sin t在顶部的切线。",
 "用二维机器人轨迹识别速度向量退化时斜率公式失效。",
 dict(type="parametric_slope",t=1,expected=[3,2])),
lesson("KB76-M08","KB75-P056-S02","ELECTIVE_A","CONCEPT","非均匀连续密度与零点质量",
 "非负函数f(x)若在R上积分等于1,可作为连续型随机变量密度;区间概率等于该区间上的积分,单点概率为0。",
 ["f(x)=2x (0≤x≤1),其余为0","P(a≤X≤b)"],["密度非负且在全实轴可积并归一","本例概率区间均位于[0,1]"],
 "对密度f(x)=2x, P(0≤X≤1/2)=1/4;f(3/4)=3/2>1不矛盾。",
 [["检查归一","∫_0^1 2x dx=[x²]_0^1=1,且密度非负。"],
 ["计算区间质量","从0积到1/2得(1/2)²=1/4。"],
 ["解释单点","积分在长度为0的单点为0,不能把f(x0)当作P(X=x0)。"],
 ["区分均匀","f随x变化并非常数,所以不能套用均匀分布长度比。"]],
 "密度可以大于1,但积分概率总在[0,1];密度可能在某点不可用函数值表示概率。",
 "若直接写P(X=3/4)=f(3/4)=3/2,会得到超过1的非法概率。",
 "f(3/4)=3/2而P(X=3/4)=0,证明密度高度与点质量不同。",
 "拿密度函数的高度替代区间积分或错误套用均匀长度公式。",
 [["求P(0≤X≤1/2)。","积分∫_0^{1/2}2x dx=1/4。"],
 ["求P(1/2≤X≤1)。","积分∫_{1/2}^1 2x dx=1-1/4=3/4。"]],
 ["先检查密度非负及总积分为1。","把区间概率写成定积分。","计算端点差,不要把密度值当成单点概率。"],
 "换成三角形递减密度f=2(1-x)并重新积分。",
 "说明服务等待时间连续模型为何单点时间的概率为零。",
 dict(type="triangular_density",lower=[0,1],upper=[1,2],expected=[1,4]))
]

# Prerequisite topics are editorial hints, not falsely resolved curriculum IDs.
PREREQS={
 "KB76-M01":["绝对值不等式","正整数与阿基米德性质"],
 "KB76-M02":["函数定义域与点值","函数极限的ε-δ定义"],
 "KB76-M03":["连续函数","导数与原函数","定积分定义"],
 "KB76-M04":["概率样本空间与事件","二维随机变量的取值"],
 "KB76-M05":["样本均值","二次函数最小化与可辨识性"],
 "KB76-M06":["三维向量与欧氏内积","行列式与右手系"],
 "KB76-M07":["一元导数","参数化曲线与链式法则"],
 "KB76-M08":["非负函数定积分","连续型概率密度与区间概率"],
}
for draft in L:
 draft["prerequisite_topics"]=PREREQS[draft["id"]]
 draft["prerequisite_ids_confirmed"]=False

def fraction(v):
 if type(v) is int:return Q(v)
 if isinstance(v,list) and len(v)==2 and all(type(z) is int for z in v) and v[1]!=0:return Q(v[0],v[1])
 raise ValueError("only exact integer/rational arrays accepted")

def verify_case(w):
 t=w.get("type")
 if t=="sequence_threshold":
  a=fraction(w["numerator"]);eps=fraction(w["epsilon"]);N=w["N"]
  assert a>0 and eps>0 and type(N) is int and N>0 and a/N<eps
 elif t=="point_limit_mismatch":
  assert fraction(w["center_value"])!=fraction(w["limit_value"])==0
  xs=[fraction(z) for z in w["sample_x"]]
  ys=[fraction(z) for z in w["sample_y"]]
  assert len(xs)==len(ys)>=2 and all(x!=0 and y==x*x for x,y in zip(xs,ys))
 elif t=="fundamental_calculus":
  c=fraction(w["scale"]);p=w["power"]
  a=fraction(w["a"]);b=fraction(w["b"])
  assert type(p) is int and 0<=p<=8 and a<=b
  assert c*(b**(p+1)-a**(p+1))/(p+1)==fraction(w["expected"])
 elif t=="joint_table":
  cells=[fraction(z) for z in w["cells"]]
  assert len(cells)==4 and all(0<=z<=1 for z in cells) and sum(cells)==1
  rows=[cells[0]+cells[1],cells[2]+cells[3]]
  cols=[cells[0]+cells[2],cells[1]+cells[3]]
  assert rows==[fraction(z) for z in w["rows"]]
  assert cols==[fraction(z) for z in w["columns"]]
  is_independent=all(cells[i*2+j]==rows[i]*cols[j] for i in range(2) for j in range(2))
  assert type(w["independent"]) is bool and is_independent==w["independent"]
 elif t=="ols_line":
  xx=[fraction(v) for v in w["x"]]; yy=[fraction(v) for v in w["y"]]
  assert 2<=len(xx)==len(yy)<=50
  xbar=sum(xx)/len(xx);ybar=sum(yy)/len(yy)
  den=sum((x-xbar)**2 for x in xx)
  assert den>0
  slope=sum((x-xbar)*(y-ybar) for x,y in zip(xx,yy))/den
  assert slope==fraction(w["slope"]) and ybar-slope*xbar==fraction(w["intercept"])
 elif t=="cross_product":
  a=[fraction(v) for v in w["a"]];b=[fraction(v) for v in w["b"]]
  assert len(a)==len(b)==3
  cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
  assert cross==[fraction(v) for v in w["expected"]]
  assert sum(cross[i]*a[i] for i in range(3))==0
  assert sum(cross[i]*b[i] for i in range(3))==0
 elif t=="parametric_slope":
  u=fraction(w["t"])
  assert 2*u!=0 and 3*u*u/(2*u)==fraction(w["expected"])
 elif t=="triangular_density":
  lo=fraction(w["lower"]);hi=fraction(w["upper"])
  assert 0<=lo<=hi<=1 and hi*hi-lo*lo==fraction(w["expected"])
 else:raise ValueError("unknown witness type")
 return True

def canon(d):return json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
def validate(d):
 queue=E.audit()
 assert d["source_comparison_queue_sha256"]==hashlib.sha256(E.OUT.read_bytes()).hexdigest()
 assert d["teacher_approved"]==d["student_published"]==0
 assert d["official_denominators"]==queue["official_denominators"]
 assert d["teacher_review"]=="REVIEW_PENDING" and d["distribution"]=="TEACHER_ONLY"
 assert len(d["teacher_drafts"])==8 and len({r["id"] for r in d["teacher_drafts"]})==8
 idx={r["source_editorial_subspan_id"]:r for r in queue["cases"]}
 for row in d["teacher_drafts"]:
  assert row["source_editorial_subspan_id"] in idx
  assert idx[row["source_editorial_subspan_id"]]["track_hint"]==row["curriculum_track_hint"]
  assert row["teacher_review"]=="REVIEW_PENDING" and row["teacher_signature"] is None
  assert row["teacher_solution_visibility"]=="TEACHER_ONLY" and not row["student_publishable"]
  assert row["independent_challenge_solution_reveal"] is False
  assert row["mathematical_certification"]=="NOT_FORMALLY_CERTIFIED"
  assert row["teacher_proof_review"]=="NOT_COMPLETED" and row["official_atom_count"] is None
  assert row["source_license"]=="ORIGINAL_PROJECT_AUTHORED"
  assert row["prerequisite_topics"]==PREREQS[row["id"]] and len(row["prerequisite_topics"])>=2
  assert row["prerequisite_ids_confirmed"] is False
  assert row["knowledge_kind"] in ("THEOREM","METHOD","CONCEPT")
  for key in ["title","definition","statement","mathematical_validity","invalid_boundary",
              "counterexample","common_wrong_method","near_transfer","far_transfer"]:
   assert isinstance(row[key],str) and len(row[key])>=(8 if key in ("title","near_transfer","far_transfer") else 15),(row["id"],key)
  assert len(row["assumptions"])>=2 and len(row["symbols"])>=2 and len(row["reasoning_steps"])>=4
  assert all(len(s)==2 and len(s[0])>=2 and len(s[1])>=15 for s in row["reasoning_steps"])
  assert len(row["worked_examples"])==2 and all(len(q)>10 and len(ans)>15 for q,ans in row["worked_examples"])
  assert len(row["graduated_hints"])==3 and all(len(h)>8 for h in row["graduated_hints"])
  verify_case(row["finite_case"])
 return True

def build():
 q=E.audit()
 d=dict(schema_version="kb76-eight-original-teacher-lessons-v1",
   source_comparison_queue_sha256=hashlib.sha256(E.OUT.read_bytes()).hexdigest(),
   source_pdf_sha256=q["source_pdf_sha256"],
   teacher_review="REVIEW_PENDING",distribution="TEACHER_ONLY",
   teacher_approved=0,student_published=0,teacher_signature=None,
   official_denominators=q["official_denominators"],
   finite_math_status="BOUNDED_EXACT_WITNESSES_ONLY",
   proof_certification="NOT_FORMALLY_CERTIFIED",teacher_drafts=L)
 validate(d);return d

def markdown(d):
 lines=["# Batch76｜8篇新原创数学教师侧讲义","",
 "- 含ε-N极限、连续性、微积分基本定理、二维联合分布、最小二乘、叉积、参数曲线、非均匀连续密度。",
 "- 每篇2个完整原创例题、≥4个逐步依据、适用/失效条件、反例/错因、三级提示及近远迁移。",
 "- 这些数学论证为待教师审核的项目作者草案;8类有限精确实例测试不能代替全称定理形式证明。",
 "- 全部REVIEW_PENDING、TEACHER_ONLY；学生检索不允许泄露教师解答。",""]
 for x in d["teacher_drafts"]:
  lines += [f"## {x['id']}｜{x['title']}",f"- 来源待审候选：{x['source_editorial_subspan_id']}（{x['curriculum_track_hint']}）",
   f"- 数学断言：{x['statement']}",f"- 前提：{'；'.join(x['assumptions'])}",
   *[f"  {j}. {step[0]}：{step[1]}" for j,step in enumerate(x["reasoning_steps"],1)],
   f"- 失效反例：{x['counterexample']}",
   f"- 教师侧原创例题：{'；'.join(ans for _,ans in x['worked_examples'])}",
   f"- 错法：{x['common_wrong_method']}",""]
 return "\n".join(lines)

def main():
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
 d=build();m=markdown(d)
 if a.check:
  assert OUT.read_text(encoding="utf8")==canon(d)
  assert MD.read_text(encoding="utf8")==m
 else:
  OUT.write_text(canon(d),encoding="utf8");MD.write_text(m,encoding="utf8")
 print("KB76 independent original teacher drafts",len(d["teacher_drafts"]))
if __name__=="__main__":main()
