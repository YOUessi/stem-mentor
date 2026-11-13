#!/usr/bin/env python3
"""Eight new original mathematical teacher-only lessons; bounded syllabus proposals."""
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as source
OUT=ROOT/"knowledge/editorial_review/kb_batch134_eight_proof_lessons.json"
MD=ROOT/"docs/evaluation/KB_BATCH134_EIGHT_DEEP_LESSONS.md"
SAFE=ROOT/"knowledge/editorial_review/kb_batch134_student_safe_index.json"
# In each tuple: definition, domain, assumptions, reasoned (step, justification) triples or more,
# correctness, failure, common mistake, repair, 2 examples (question,answer, reasoning), hints, near/far.
L={
"c_inequality_product":dict(
 formal="算术-几何平均值不等式：实数a,b≥0时 (a+b)/2≥√(ab)，且等号成立当且仅当a=b。不可遗漏非负假设。",
 domain="a,b为非负实数；√(ab)是非负实数平方根；(a+b)/2为算术平均数。",
 assumptions="a≥0、b≥0；所有平方根在实数域定义，且不能将不等式直接扩大到任意实数对。",
 steps=[("从平方非负出发","(√a−√b)²≥0，非负平方根合法，因为a、b均非负。"),("展开并移项","a+b−2√(ab)≥0，由恒等变形得a+b≥2√(ab)。"),("除以正数","两边同除以2得到(a+b)/2≥√(ab)，不会改变不等号。"),("判断等号","平方等于0当且仅当√a=√b，等价于a=b。")],
 legal="非负根式可定义，平方非负与等价移项保持真假；若要应用乘积最值还需固定a+b。",
 failure="令a=-1、b=-4时√(ab)=2，而(a+b)/2=-2.5，结论反向；不能把非负条件删去。",
 wrong="只见乘积ab≥0就套用均值不等式，忽略两个数分别非负。",
 repair="先分别核对a≥0、b≥0，而不是仅检查ab≥0；等号必须单独核查。",
 examples=[("取a=4,b=9，验证均值不等式并判断等号。","13/2≥6，严格大于。",["4、9均非负，符合条件。","(4+9)/2=13/2，√36=6。","13/2>6，故不取等号。"]),("已知a,b≥0且a+b=10，求ab的最大值。","25，在a=b=5时取到。",["均值不等式给出√(ab)≤(a+b)/2=5。","两边是非负数，可以平方得ab≤25。","a=b=5满足和为10且取等号。"])],
 hints=["先检查两个变量各自的符号与根式定义域。","考虑(√a−√b)²≥0能给出什么关系。","最后核对等号成立条件，不要直接代入负数。"],
 near="在a,b>0且ab=16的条件下求a+b下界，并说明何时取等号。",
 far="将周长固定的矩形面积最大化转换为两条非负边长的均值不等式问题。"),
"c_parity":dict(
 formal="函数f:D→R为偶函数当且仅当D关于0对称且对全部x∈D有f(-x)=f(x)；为奇函数当且仅当D关于0对称且f(-x)=-f(x)。",
 domain="D⊆R是函数定义域；检验任意x∈D时必须有-x∈D。奇偶性定义于函数整体的定义域。",
 assumptions="首先逐项检查定义域关于原点对称，再比较全部成对自变量的函数值；只算某一个样本点不能证明全域。",
 steps=[("验证定义域","先证明x∈D推出-x∈D，才有在全部定义域上比较f(-x)的可能。"),("检验偶性","对任意x∈D直接求f(-x)，再与f(x)比较，不能只验证几个样本点。"),("检验奇性","对任意x∈D求f(-x)并与-f(x)比较，两者恒等才符合奇函数定义。"),("解释几何对称","偶函数图像关于y轴对称；奇函数图像关于原点中心对称，反之同样须有相应定义域。")],
 legal="两个判别式是定义层面的全称命题，必须在同一函数域内严格验证。",
 failure="f(x)=x定义在(0,1)时，虽然形式代数满足f(-x)=-f(x)，但-x不在定义域，函数既不能按此定义称奇也不能称偶。",
 wrong="只因解析式出现奇数次幂就直接判定奇函数，完全不看定义域。",
 repair="写出精确域D并核验D=-D，再用任意x的函数值相等式。",
 examples=[("f(x)=x²在[-2,2]上是奇函数还是偶函数？","偶函数。",["定义域[-2,2]关于0对称。","对任意x，f(-x)=(-x)²=x²=f(x)。","故f是偶函数，不是非零域上的奇函数。"]),("f(x)=x³在[-1,1]上是奇函数还是偶函数？","奇函数。",["定义域关于0对称。","f(-x)=(-x)³=-x³=-f(x)。","在此域上是奇函数，图像关于原点对称。"])],
 hints=["先完整写出函数的定义域。","检查对每个x是否也能合法代入-x。","代数比较f(-x)与f(x)、-f(x)，要对所有x成立。"],
 near="函数f(x)=x²定义在[0,2]上，讨论其是否是偶函数。",
 far="一个测量信号在时间t与-t的记录区域不对称，能否只凭波形外观判为奇信号？"),
"c_log_inverse":dict(
 formal="对实数a>0且a≠1，指数函数f(x)=a^x在R上严格单调且取值(0,∞)，因此有反函数log_a:(0,∞)→R；a^(log_a y)=y (y>0)，log_a(a^x)=x。",
 domain="a>0且a≠1，x∈R，y>0；log_a y是真数正的实对数；若a∈(0,1)则两函数递减。",
 assumptions="底数正且不等于1；互逆组合时每一步的自变量必须处于对应函数的定义域。",
 steps=[("核实单射","a>1时a^x严格递增；0<a<1时严格递减，任意两个不同x不会映到同一值。"),("核实值域","连续指数函数的输出严格为正且向两端变化覆盖所有正实数。"),("定义对数","对于任意y>0，存在唯一x使a^x=y，把该x记作log_a y。"),("验证互逆","由唯一性和定义得到a^(log_a y)=y，以及log_a(a^x)=x，两者条件不同。")],
 legal="反函数的构造需要原函数在其指定定义域内一一对应到指定值域；不只是符号运算。",
 failure="a=1时1^x=1不是单射，没有全R上的反函数；log_2(-3)在实数域没有定义。",
 wrong="把log_a y视为对所有实数y存在，并认为底数a=1时仍可换底。",
 repair="先逐项核验a>0、a≠1、y>0，写出定义域和值域后再使用互逆关系。",
 examples=[("求log_2 8并验证指数对数互逆。","3。",["2>0且2≠1、8>0。","因2³=8，按对数定义log_2 8=3。","验证2^(log_2 8)=2³=8。"]),("求log_2(1/4)并验证结果。","-2。",["真数1/4>0，底数2合法。","2^(-2)=1/4，因此log_2(1/4)=-2。","代回指数等式确认值。"])],
 hints=["先写清底数与真数限制。","把对数等式改写成指数等式。","检验结果是否使原指数恰好等于真数。"],
 near="证明log_(1/2)4=-2，并解释对数函数单调性为何为递减。",
 far="推导指数衰减半衰期t在正比值R(t)/R0下的对数表达，并解释正值前提。"),
"c_cosine_difference":dict(
 formal="实角α,β满足cos(α−β)=cosα cosβ+sinα sinβ。此恒等式可由平面单位圆向量的欧氏内积和旋转不变性推出。",
 domain="α、β是实角，三角函数按弧度解释；单位圆向量u=(cosα,sinα)、v=(cosβ,sinβ)。",
 assumptions="两向量均为单位向量，使用正交旋转保持内积；此恒等式对全部实角成立，无需把α−β限制为锐角。",
 steps=[("构造单位向量","令u=(cosα,sinα)，v=(cosβ,sinβ)，其长度都为1。"),("利用正交旋转","把u、v同时旋转-β，内积保持，v变为(1,0)。"),("写出旋转后的内积","旋转后的u=(cos(α−β),sin(α−β))，与(1,0)内积等于cos(α−β)。"),("用原始内积表达","原坐标u·v=cosα cosβ+sinα sinβ，与旋转后相同，故恒等式成立。")],
 legal="二维旋转矩阵正交，保持点积；坐标点积定义提供右侧两项而非两余弦相减。",
 failure="令α=β=π/3，则cos(α−β)=1，然而cosα−cosβ=0；不能把差角余弦写成余弦的差。",
 wrong="错误地将cos(α−β)拆成cosα−cosβ，混淆了差角恒等式和线性关系。",
 repair="从单位圆向量内积推导；必要时用α=β这样的简单反例快速检验。",
 examples=[("计算cos(π/3−π/6)。","√3/2。",["两个角对应三角函数值分别为1/2、√3/2和√3/2、1/2。","差角余弦为(1/2)(√3/2)+(√3/2)(1/2)=√3/2。","直接角差为π/6，复核同值。"]),("计算cos(π/4−(-π/4))。","0。",["cos(π/4)=cos(-π/4)=√2/2。","sin(π/4)=√2/2，sin(-π/4)=-√2/2。","代入得1/2−1/2=0，也等于cos(π/2)。"])],
 hints=["尝试把两个角表示为单位圆上的两个单位向量。","考虑同时旋转后两向量的夹角与内积是否变化。","用坐标点积与单位圆表达式连接，不要直接拆成两项差。"],
 near="用差角公式计算cos(75°)，说明角度转成弧度后计算等价。",
 far="说明两个归一化二维传感器方向向量点积如何提供相对方向的余弦。"),
"sc_derivative_monotone":dict(
 formal="若f在区间I连续且在其内部可导，并且内部任意x都有f'(x)≥0，则f在I非减；若处处f'(x)>0，则严格递增。只在单点f'(x)≥0不足以判定区间单调。",
 domain="I为实区间；若含端点在端点连续；f'(x)只在内部点要求存在；非减允许部分函数值相等。",
 assumptions="对I内部所有点导数存在并具有指定符号；区间任两点之间可合法应用拉格朗日中值定理。",
 steps=[("任取两点","从I任取x1<x2并固定闭子区间[x1,x2]。"),("核验中值前提","由给定连续与可导条件，f在该子区间闭合连续、内部可导。"),("套拉格朗日中值定理","存在c∈(x1,x2)使f(x2)−f(x1)=f'(c)(x2−x1)。"),("由符号得单调","x2−x1>0；导数≥0得函数值差≥0，处处>0得函数值差>0。")],
 legal="中值定理连接有限增量与某点导数，故是区间全称的结论而非局部样本外推。",
 failure="f(x)=x³在x=0导数为0，但仍严格递增；f(x)=−x³在x=0同样导数0，却严格递减；单点零导数不决定单调性。",
 wrong="发现f'(0)=0就认为该点附近函数恒定或出现极值。",
 repair="单调性要考察整段区间导数符号；驻点只作为分类线索，还需比较两侧变化。",
 examples=[("证明f(x)=x³在R上严格递增，能否只凭f'(0)>0？","严格递增；但f'(0)=0不能用处处>0判据。",["f'(x)=3x²≥0对全部实数成立。","中值定理先得f非减。","若x2>x1则x2³−x1³=(x2−x1)(x1²+x1x2+x2²)>0，因此严格递增。"]),("判定f(x)=x²在[0,2]的单调性。","在[0,2]严格递增。",["f在[0,2]连续、(0,2)可导。","f'(x)=2x>0对所有内部x成立。","中值定理推出在整个闭区间严格递增。"])],
 hints=["确定研究区间，不是仅在某个点计算导数。","检查闭区间连续与开区间可导是否满足。","任取x1<x2，考虑用中值定理解释f(x2)−f(x1)的符号。"],
 near="讨论f(x)=x³在R上导数等于0的点与严格单调之间的关系。",
 far="为有噪声的增长测量拟合可导曲线时，区分样本导数估计为正与数学上的全区间单调保证。"),
"sc_space_distance":dict(
 formal="在三维正交归一坐标系中，P=(x1,y1,z1)，Q=(x2,y2,z2) 的欧氏距离为√((x2−x1)²+(y2−y1)²+(z2−z1)²)。",
 domain="P,Q是三维欧氏空间中点；三个坐标轴两两垂直、单位等长；距离为非负实数。",
 assumptions="坐标基正交归一，三个坐标分量使用同一长度单位；任意两点包括重合点。",
 steps=[("写出位移向量","连接P到Q的向量为v=(x2−x1,y2−y1,z2−z1)。"),("展开正交基点积","若e1,e2,e3正交归一，则v·v=Σ_i(Δi)²，交叉项因e_i·e_j=0消失。"),("定义距离","距离为位移向量长度||v||=√(v·v)，取非负平方根。"),("退化检查","P=Q时三分量差均为0，距离也为0，公式仍合法。")],
 legal="毕达哥拉斯在正交归一基下恰与欧氏内积范数等价；斜坐标基需使用Gram矩阵。",
 failure="基e1=(1,0)，e2=(1,1)非正交时坐标差(1,1)表示位移(2,1)，长度√5而非√2。",
 wrong="在任意非正交坐标系直接平方坐标差相加，忘记基向量的内积交叉项。",
 repair="检查坐标基是否正交归一；否则计算位移向量实际坐标或用Gram矩阵。",
 examples=[("P=(1,2,3)，Q=(4,6,3)，求PQ。","5。",["位移分量是(3,4,0)。","长度平方为9+16+0=25。","取非负根得5。"]),("P=(-1,0,2)，Q=(2,4,14)，求PQ。","13。",["位移为(3,4,12)。","距离平方9+16+144=169。","开方得13。"])],
 hints=["先确认是否为三维正交坐标系。","分别减去对应坐标获得位移三个分量。","把分量平方求和后再取非负平方根。"],
 near="改变空间中两点的相同z坐标，解释为何距离公式退化为平面距离。",
 far="机器人传感器在斜轴坐标下的距离计算为什么必须先校准变换或引入度量矩阵。"),
"a_sequence_limit":dict(
 formal="数列a_n收敛于L∈R，指对任意ε>0存在正整数N，使所有n≥N满足|a_n−L|<ε。每个实数收敛数列必有界，反之不成立。",
 domain="n为正整数；ε为任意正实数；N可随ε改变且只要求最终尾部；L为有限实数。",
 assumptions="数列的每一项均定义；证明极限必须处理任意ε，不能只验某个容差或有限样本。",
 steps=[("给定ε","任取ε>0，由收敛定义可选N≥2使所有n≥N时|a_n−L|<min(ε,1)，必要时增大N。"),("证明尾部有界","由三角不等式|a_n|≤|L|+|a_n−L|<|L|+1，对所有n≥N成立。"),("合并有限前缀","有限项a1…a_(N−1)有最大绝对值M0，令M=max(M0,|L|+1)，全数列有界。"),("反例否定逆命题","a_n=(-1)^n保持|a_n|=1，但奇偶子列分别取1和−1，不存在共同极限。")],
 legal="全称ε、尾部以及有限前缀是收敛定义的准确量词结构；有限前缀最大值存在。",
 failure="a_n=(-1)^n有界却不收敛；只看第1到第100项无法证明全部尾项满足定义。",
 wrong="取ε=0.1验证若干项后宣称数列收敛，或由有界直接推得收敛。",
 repair="为任意ε给出N(ε)并检查全部n≥N；有界不等于收敛。",
 examples=[("严格证明a_n=1/n收敛到0。","极限为0。",["任意ε>0，取正整数N>1/ε。","当n≥N时|1/n−0|=1/n≤1/N<ε。","满足ε-N定义。"]),("求a_n=(2n+1)/n的极限并给出N条件。","2；可取N>1/ε。",["a_n−2=1/n。","任取ε>0，取N>1/ε。","n≥N时|a_n−2|=1/n<ε。"])],
 hints=["任取任意ε>0，不要把它固定为小数。","把|a_n−L|化成可以与n比较的表达式。","选N(ε)使所有更大的n都符合严格小于关系。"],
 near="写出a_n=3+2/n趋于3的完整ε-N论证。",
 far="说明算法误差上界1/n为何可用于任意指定精度的最终收敛保证，而有限次样本不能代替证明。"),
"a_integral_area":dict(
 formal="定积分∫_a^b f(x)dx是有向累计量。连续f的曲线与x轴在[a,b]围成的几何面积为∫_a^b |f(x)|dx；当f跨零点时必须按符号分段。",
 domain="a<b实数，f在[a,b]连续（或更一般可积且绝对值可积）；面积用非负单位，符号积分可正负相消。",
 assumptions="所讨论函数连续从而积分存在；解释几何面积须比较曲线与x轴位置并处理符号切换。",
 steps=[("区分两个对象","有向定积分按函数正负累计，而几何面积只计非负高度。"),("确定符号区间","先求或识别函数零点，将[a,b]划为正负性不变的子区间。"),("分别积分","f≥0时面积段等于∫f；f≤0时面积段等于−∫f，对每段结果非负。"),("合并为绝对值积分","各段相加等价于∫_a^b |f(x)|dx；除非f不改变符号，不能直接取|∫f|代替∫|f|。")],
 legal="连续函数可积；积分可加性与|f|非负性允许逐段构造面积。",
 failure="f(x)=x在[-1,1]上∫f=0但∫|f|=1；将净积分0称为面积0是错误的。",
 wrong="在含正负区间直接计算积分并把抵消后的结果当作图形面积。",
 repair="先找函数与x轴交点，再分段计算绝对值积分；明确面积单位与符号差异。",
 examples=[("求y=x在[-1,1]与x轴围成的几何面积。","1（有向积分为0）。",["零点x=0把区间分为两段。","面积为-∫_-1^0 xdx+∫_0^1 xdx。","两段各1/2，总面积1。"]),("求y=x−1在[0,2]与x轴的几何面积。","1（有向积分为0）。",["零点x=1，函数左负右正。","面积=-∫_0^1(x−1)dx+∫_1^2(x−1)dx。","每段1/2，总和1。"])],
 hints=["先想清楚题目要求有向累计量还是无符号几何面积。","寻找函数与x轴的交点并逐段判断正负。","遇到负函数段时用绝对值而不是把面积记成负数。"],
 near="求f(x)=2x在[-1,1]与x轴围成的几何面积并比较有向积分。",
 far="比较往返路程的净位移积分与总路程积分，解释速度符号与距离的区别。")
}
def require(x,m):
 if not x:raise ValueError(m)
def build():
 a=json.loads(source.OUT.read_text(encoding="utf-8"));source.validate(a)
 m={r["id"]:r for r in a["records"]};out=[]
 for slug,v in L.items():
  s=m["kb133-proposal-"+slug]
  out.append(dict(id="kb134-deep-"+slug,source_candidate_id=s["id"],course_track=s["track"],
   knowledge_type=s["knowledge_type"],source_span_sha256=s["source_lock"]["span_sha256"],
   source_pdf_sha256=s["source_pdf_sha256"],standard_version="2017-2020-editorial-bounded",
   formal_definition_or_theorem=v["formal"],notation_and_domain=v["domain"],applicability_and_hypotheses=v["assumptions"],
   reasoned_steps=[dict(step=k,justification=t) for k,t in v["steps"]],
   why_method_is_legal=v["legal"],nonexample_or_failure=v["failure"],
   typical_wrong_solution=v["wrong"],why_wrong_and_repair=v["repair"],
   teacher_examples=[dict(question=q,answer=answer,reasoned_solution=steps) for q,answer,steps in v["examples"]],
   student_hint_ladder=v["hints"],near_transfer=v["near"],far_transfer=v["far"],
   teacher_review_status="REVIEW_PENDING",teacher_review_evidence=None,teacher_solution_visibility="TEACHER_ONLY",
   source_status="PROVISIONAL_PDFKIT_SOURCE_PROPOSAL_NOT_OFFICIAL_ATOM",formal_proof_certified=False,
   free_student_step_verified=False,student_authoritative=False))
 return out
def validate(rows):
 require(rows==build(),"lessons differ from author-reviewed frozen source and publication controls")
 require(len(rows)==8 and len({r["id"] for r in rows})==8,"missing lessons")
 for r in rows:
  require(all(len(r[k])>=20 for k in ("formal_definition_or_theorem","notation_and_domain",
   "applicability_and_hypotheses","nonexample_or_failure","typical_wrong_solution","why_wrong_and_repair",
   "why_method_is_legal","near_transfer","far_transfer")),"short lesson field")
  require(len(r["reasoned_steps"])>=4 and len(r["teacher_examples"])==2 and
   all(len(e["reasoned_solution"])>=3 for e in r["teacher_examples"]) and len(r["student_hint_ladder"])==3,"incomplete reasoning")
  require(not r["student_authoritative"] and r["teacher_review_evidence"] is None and
   r["teacher_review_status"]=="REVIEW_PENDING","forged teacher approval")
 return True
def safe_export(rows):
 validate(rows)
 return dict(status="NO_APPROVED_MATERIAL",publishable_count=0,items=[],teacher_solution_excluded=True)
def render(rows):
 s=["# Batch134｜八份跨主题原创深度数学讲义（仅供教师候审）","",
 "**REVIEW_PENDING / TEACHER_ONLY；来源为项目候选而非教师批准的官方课程知识原子；符号实例检验不等于定理的形式证明。**",""]
 for r in rows:
  s.extend(["## "+r["id"]+" · "+r["course_track"],"**正式表述** "+r["formal_definition_or_theorem"],
   "**记号与论域** "+r["notation_and_domain"],"**全部适用条件** "+r["applicability_and_hypotheses"],""])
  s.extend(f"{i}. **{a['step']}**：{a['justification']}" for i,a in enumerate(r["reasoned_steps"],1))
  s+=["","**合法性依据** "+r["why_method_is_legal"],"**边界反例** "+r["nonexample_or_failure"],
    "**典型错误** "+r["typical_wrong_solution"],"**错因及修复** "+r["why_wrong_and_repair"],""]
  for i,e in enumerate(r["teacher_examples"],1):
   s.extend([f"**教师例题{i}：** "+e["question"],"**完整答案：** "+e["answer"]])
   s.extend("  - "+v for v in e["reasoned_solution"])
  s+=["**学生独立挑战提示（不得与答案同屏）**"]
  s.extend("  - "+h for h in r["student_hint_ladder"])
  s+=["**近迁移** "+r["near_transfer"],"**远迁移** "+r["far_transfer"],
   "来源锁："+r["source_candidate_id"]+" / "+r["source_span_sha256"],""]
 return "\n".join(s).rstrip()+"\n"
def main():
 a=argparse.ArgumentParser();a.add_argument("--write",action="store_true");a.add_argument("--check",action="store_true");z=a.parse_args()
 require(z.write!=z.check,"choose one mode")
 if z.write:
  v=build();validate(v);OUT.write_text(source.stable_json(v),encoding="utf-8")
  MD.write_text(render(v),encoding="utf-8")
  SAFE.write_text(source.stable_json(safe_export(v)),encoding="utf-8")
 else:
  v=json.loads(OUT.read_text(encoding="utf-8"));validate(v)
  require(MD.read_text(encoding="utf-8")==render(v),"render drift")
  require(json.loads(SAFE.read_text())==safe_export(v),"student solution leakage")
 print("PASS",len(v),"teacher-only lessons",sum(len(x["teacher_examples"]) for x in v),"worked examples; approved 0")
if __name__=="__main__":main()
