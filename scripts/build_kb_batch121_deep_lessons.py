#!/usr/bin/env python3
"""Eight original comprehensive math lessons, strict teacher-only drafts.

Finite exact SymPy oracles check two worked examples per lesson, never
certify universal mathematical statements or free-form student steps.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch121_editorial_scope as sem
OUT=ROOT/"knowledge/editorial_review/kb_batch121_eight_depth_lessons.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH121_EIGHT_DEPTH_LESSONS.md"
ORACLE=ROOT/"docs/evaluation/KB_BATCH121_EXACT_MATH_ORACLES.json"

def L(key,definition,symbols,scope,explanation,steps,boundary,wrong,why_wrong,examples,hints,near,far):
    return locals()
def E(question,steps,answer,verification):
    return {"question":question,"steps":steps,"answer":answer,"verification":verification}

ROWS=[
L("C203",
 "在固定论域D中，‘所有x都满足P(x)’的否定为‘至少存在一个x不满足P(x)’；它不要求每个x都不满足。",
 "∀为全称量词；∃为存在量词；¬表示否定；P(x)表示x满足的性质；D为命题讨论域。",
 "论域固定；任意性质的真伪在同一解释下评价。可空论域也符合量词对偶，但举出实际反例须论域非空。",
 "因为全称命题为真要求每个元素都满足条件，故其失败恰好意味着找到了一个未满足条件的元素。",
 [("列出原命题","写成∀x∈D P(x)，固定同一个D与谓词P，避免在否定时偷偷更换论域。"),
  ("使用量词对偶","否定‘对所有对象都成立’正是‘有一个对象使它不成立’，因此¬∀xP(x)⇔∃x¬P(x)。"),
  ("反向核验","若确有x0不满足P(x)，原命题被否；若原命题为假，就至少有一个这样的x0。")],
 "没有找到反例不等于已证明全称命题；数值枚举只在穷尽有限论域时能证明这一结论。",
 "错误写法：‘所有整数是偶数’的否定是‘所有整数都是奇数’。",
 "反例3并不能证明所有整数都为奇数，却已足以否定所有整数都为偶数。",
 [E("D={1,2,3}，原命题‘所有x>=2’是否成立？写其否定。",
    ["检验1<2，因此全称命题不成立。","否定为存在x<2，例如x=1。"],"假；∃x∈D使x<2","存在1这个反例满足条件。"),
  E("D={2,4,6}，命题‘每个元素都是偶数’的否定真假？",
    ["依次检验三个元素均为偶数。","其否定‘存在奇数元素’为假。"],"否定为假","有限全集穷尽检验无任何奇数。")],
 ["先锁定量词所覆盖的对象集合。","找一个使性质不成立的对象即可反驳全称断言。","将∀替换为∃，并且只否定谓词P，不替换论域。"],
 "对命题‘任意实数x，都有x²>=0’写出否定并判定真假。",
 "软件测试断言‘所有输入都有效’若有一个错误输入，即可反驳全称命题，为什么抽样通过不能证明全称正确？"),
L("C204",
 "当a≠0时，二次函数f(x)=ax²+bx+c的正负号由开口方向、实根及根的重数决定；解f(x)≥0就是寻找图像位于或高于x轴的点。",
 "a,b,c为实系数；a≠0；Δ=b²−4ac；f(x)为实值二次多项式；不等号端点由严格性决定。",
 "仅适用于一元二次函数；先判Δ>0、Δ=0或Δ<0，再区分a正负和不等号方向。",
 "二次式可写成a(x−r1)(x−r2)（Δ≥0）；实根两侧符号由因子的正负决定；无实根时全域符号与a相同。",
 [("判别与开口","计算Δ并记录a的符号；Δ<0时二次式在实轴上无零点且符号恒与a同。"),
  ("定位实根","Δ>0时求r1<r2并据两因子乘积得开口向上时外侧为正、内侧为负。"),
  ("处理边界","Δ=0时只在重根处取0，其余点与a同号；≥、≤包含等号零点，>、<不包含。")],
 "a=0应按一次或常数不等式重新分析；不能把Δ<0等价于‘无解’，还需看不等号和a。",
 "错误写法：由−x²+4>0得到x<−2或x>2，因为把‘外侧正’无条件套在开口向下的抛物线。",
 "x=0时−x²+4=4>0，已经反驳该错误解集；真正解集为−2<x<2。",
 [E("解x²−5x+6≥0。",["因式分解为(x−2)(x−3)。","开口向上，取两根外侧且包含根。"],"x≤2 或 x≥3","x=0给6≥0；x=5/2给−1/4<0。"),
  E("解−x²+4>0。",["化为x²<4。","故|x|<2；严格不等号不包含±2。"],"−2<x<2","x=0符合；x=±2只等于0而不符合。")],
 ["确定a正负和二次式是否有实根。","先画符号表，不要先背外侧或内侧。","最后检查严格与非严格不等号的根端点。"],
 "将第1题改为x²−5x+6<0，比较解集与原题。",
 "汽车制动安全裕度可化成一个二次不等式，为什么模型变量必须再与时间t≥0取交集？"),
L("S205",
 "直线Ax+By+C=0（A²+B²>0）与圆(x−h)²+(y−k)²=r²（r>0）的位置由圆心到直线的距离d=|Ah+Bk+C|/sqrt(A²+B²)决定。",
 "A,B,C是直线系数；(h,k)为圆心；r>0是半径；d是圆心到直线的非负最短距离。",
 "正交直角坐标系、非退化圆与非退化直线；d<r两交点，d=r一切点，d>r无交点。",
 "沿直线法向量投影圆心至直线得到最短距离d；与半径r比较可知圆是否跨越、刚好触及或远离直线。",
 [("明确几何对象","确认A²+B²>0及r>0，保证直线法向量和圆都非退化。"),
  ("计算法向距离","单位法向量为(A,B)/sqrt(A²+B²)，圆心代入直线表达式得到带符号距离，再取绝对值。"),
  ("与半径比较","由圆心至直线垂足和直线方向组成直角三角形，d²+t²=r²；实t解数量依d与r的比较确定。")],
 "退化A=B=0不是一条直线；r=0退化为单点，不适合套两交点或切线分类。",
 "错误写法：直线x=5与半径5的圆存在两个交点，因为其距离等于半径。",
 "距离等于半径给t²=0，只有一个切点(5,0)，而不是两条不同交线。",
 [E("圆x²+y²=25与直线x=5有几个交点？",["d=5且r=5。","相等意味着只有垂足(5,0)为切点。"],"1个切点(5,0)","联立y²=0，恰一个不同实点。"),
  E("圆x²+y²=25与直线x=3有几个交点？",["圆心距d=3<5。","联立得y²=25−9=16，故y=±4。"],"2个交点(3,4),(3,−4)","两个点均满足x²+y²=25。")],
 ["先确认圆和直线的标准形式及非退化性。","求圆心到直线的距离d，而不是随意取一点距离。","比较d和r之后，用联立方程核对交点数量。"],
 "把直线改为x=6，求位置关系和可能的交点数。",
 "雷达检测圆形覆盖区与航线的交点时，为什么单位变化或经纬度坐标不能直接代入该欧氏距离公式？"),
L("S206",
 "离散随机变量X的分布列列出每个可能取值xi及其概率pi，要求所有pi≥0且Σpi=1。",
 "X是随机变量；xi是不同取值；pi=P(X=xi)；E[X]=Σxi pi（绝对可积时）；Σ表示对全部可能值求和。",
 "有限离散分布至少需要取值不重复、概率非负、总概率恰为1；无限分布需要收敛性条件才能交换某些运算。",
 "互斥且穷尽的事件{X=xi}划分样本空间，概率可加性给出Σpi=1，非负性来自概率公理。",
 [("列出取值及其事件","以X=xi划分样本空间，明确每项对应的互斥结果。"),
  ("审查合法性","逐项检查pi≥0及Σpi=1；否则是错误的候选分布，不能继续无条件求期望。"),
  ("计算期望","若绝对可积，按各可能值与其概率加权求和得到E[X]。")],
 "样本频率不是未说明统计假设时的精确理论概率；未知概率不能直接用比例值替代而不标为估计。",
 "错误写法：P(X=0)=1/2，P(X=1)=1/3，P(X=2)=1/3是有效分布，因为三项都为正。",
 "总概率为7/6>1，故即使所有项均为正，也不构成概率分布。",
 [E("X取0,1,2，概率为1/2,1/3,1/6，求E[X]。",["概率非负且和为1。","加权求和为0/2+1/3+2/6。"],"2/3","概率和1，期望2/3。"),
  E("Y取−1和1，概率分别为1/4和3/4，求E[Y]。",["两概率之和为1。","期望=−1/4+3/4。"],"1/2","两个取值的概率全部在[0,1]且合计1。")],
 ["先问：所有可能取值是否列齐？","将各概率精确相加，负值与总和不为1都必须拒绝。","合法后才加权求期望；必要时检查无限和的绝对收敛。"],
 "把第1题的最后一个概率换为1/3，是否仍能计算严格意义的期望？",
 "在线上实验中只有非随机访客的点击频率，为什么不能直接宣称该频率是所有人群的理论点击概率？"),
L("A201",
 "若实数数列an→a、bn→b，有限极限满足(an+bn)→a+b、anbn→ab；当b≠0时an/bn→a/b。",
 "n趋向正无穷；an、bn是实数项；a、b为有限实极限；bn最终非零是商成立所需条件。",
 "分子分母极限均存在且有限；商法则需b≠0，由收敛性可推出足够大n时|bn|≥|b|/2>0。",
 "加法由极限定义和三角不等式得到；乘积先利用收敛数列有界性；商用倒数差恒等式与分母远离0进行控制。",
 [("证明和的收敛","|an+bn−(a+b)|≤|an−a|+|bn−b|→0，由ε定义得an+bn→a+b。"),
  ("证明积的收敛","恒等式anbn−ab=(an−a)bn+a(bn−b)；bn收敛所以有界，右边两项均趋于0。"),
  ("确保分母与零隔离","b≠0且bn→b，存在N使|bn−b|<|b|/2，从而n>N时|bn|>|b|/2。"),
  ("证明倒数收敛","有|1/bn−1/b|=|bn−b|/(|bn||b|)≤2|bn−b|/|b|²→0。"),
  ("合成商的极限","an→a且1/bn→1/b，使用刚证明的乘积极限规律，得到an/bn→a/b。")],
 "若b=0，分式极限可能为0、有限数、无穷或不存在，不能单凭分子分母极限决定。",
 "错误写法：(1/n)/(1/n²)极限是0/0=1；实际上原式n无有限极限。",
 "取n=100得到100，取n=1000得到1000，足以反驳固定极限1的断言。",
 [E("求(1+1/n)/(2+1/n)在n→∞时的极限。",["分子极限1、分母极限2≠0。","运用商法则，极限为1/2。"],"1/2","n趋向无穷时分母始终大于2。"),
  E("求(3−1/n)/(1+1/n)在n→∞时的极限。",["分子极限3、分母极限1≠0。","运用商法则，极限为3。"],"3","分母严格为正，无失效条件。")],
 ["先分别求分子分母的候选极限。","核对分母极限是否非零且有限。","若分母趋0，退回原式做约分或比较，不套商法则。"],
 "求[(2+1/n)/(4−1/n)]的极限，并指出商法则的前提。",
 "数值计算中两个非常接近零的数做商可能误差剧烈，为什么有限计算的不稳定不直接否定数学极限定理？"),
L("B203",
 "连续二元二次函数在非空闭圆或闭椭圆上能取得最大最小值；找值须比较全部内部候选和约束边界候选。",
 "f(x,y)为实二元二次多项式；闭圆x²+y²≤R²(R>0)或椭圆x²/a²+y²/b²≤1(a,b>0)。",
 "闭圆/椭圆紧且非空，f连续；内部极值的必要条件∇f=0；边界需单独参数化或拉格朗日判别，注意退化临界集。",
 "极值存在来自紧集上连续函数的极值定理；内部可微最值为驻点；边界可参数化并比较临界值。",
 [("保证存在性","圆/椭圆包含边界且有界，二次f连续，依极值定理可取到最大值和最小值。"),
  ("查内部驻点","在约束不等式严格成立的区域解∇f=0；若有驻点曲线须一并检查其目标值。"),
  ("查完整边界并比较","圆设x=Rcosθ,y=Rsinθ；椭圆设x=a cosθ,y=b sinθ，求θ∈[0,2π]上的临界值，比较内外所有候选。")],
 "不能仅检查轴交点或认为极值只在边界：正定二次型的最小值常在内部；若退化为线段也需另行分析。",
 "错误写法：f=x+2y在单位闭圆上的最大值是2，因为只比较(±1,0),(0,±1)四个轴端点。",
 "由柯西不等式，最大值√5，在(x,y)=(1/√5,2/√5)处达到，大于2。",
 [E("f=x+2y，x²+y²≤1，求最大最小值。",["柯西不等式给|x+2y|≤√5·√(x²+y²)≤√5。","取(x,y)=±(1,2)/√5分别取到两端。"],"最小−√5；最大√5","界和达到点均精确满足约束。"),
  E("f=x²+4y²，x²/4+y²≤1，求最大最小值。",["f≥0，原点可取得0。","因x²≤4(1−y²)，故f≤4；(±2,0)和(0,±1)达到4。"],"最小0；最大4","约束紧且示例达到两端。")],
 ["先检查闭域是否非空有界以及目标是否连续。","内部解梯度=0，边界不可只取四个轴点。","参数化完整边界并比较所有临界目标值与内部值。"],
 "把第1题目标改成3x−4y，利用柯西不等式找闭单位圆极值。",
 "自动驾驶安全域是椭圆但成本函数含交叉项xy，为什么只枚举四个方向容易漏最危险点？"),
L("EC202",
 "Logistic二分类概率映射为p=1/(1+e^(−z))，它将有限实数z映到严格(0,1)内；logit(p)=ln(p/(1−p))=z。",
 "z为实数线性预测值；p为正类概率；e为自然指数底；ln为自然对数。",
 "该等式是给定模型的映射关系，并不保证数据真实服从Logistic模型或该预测概率已校准；仅当0<p<1定义logit。",
 "由p=1/(1+e^(−z))得到1−p=e^(−z)/(1+e^(−z))，相除给p/(1−p)=e^z，再取自然对数得z。",
 [("检查指数正值","对所有有限z，e^(−z)>0，因此0<p<1，端点0和1仅为极限而非实际有限输入值。"),
  ("计算优势比","1−p=e^(−z)/(1+e^(−z))，于是p/(1−p)=e^z。"),
  ("反求对数几率","取自然对数可得ln[p/(1−p)]=z，条件p∈(0,1)确保表达式定义。")],
 "Logistic模型的logit是条件模型，不自动成为因果效应；不能直接对p=0或1求有限logit。",
 "错误写法：z=ln3时p=ln3；正确概率应为3/4。",
 "因为e^(−ln3)=1/3，p=1/(1+1/3)=3/4，数值与ln3显然不同。",
 [E("当z=0时，预测概率p和logit(p)是多少？",["e^0=1，故p=1/2。","优势比等于1，ln1=0。"],"p=1/2，logit=0","对称点满足两概率各为1/2。"),
  E("当z=ln3时，求p及优势比。",["e^(−ln3)=1/3。","p=1/(1+1/3)=3/4，优势比为3。"],"p=3/4，优势比=3","代入ln(3)=z成立。")],
 ["先检查z是对数几率还是概率。","把z代入sigmoid定义再化简，而非把z直接当成p。","逆变换时检查p必须严格在0和1之间。"],
 "当z=−ln3时，p与优势比分别是多少？",
 "社会调查存在漏答和抽样偏差时，模型输出p=0.8为什么不等于被调查总体真实比例80%？"),
L("ED201",
 "周期信号最小正周期为T（秒）时，基频f=1/T（Hz）；纯正弦信号A sin(2πft+φ)中振幅A与频率f是不同参数。",
 "T>0为周期（秒）；f>0为每秒周期数（赫兹Hz）；A为振幅；φ为相位；t为秒。",
 "只对有明确周期的信号定义该倒数关系；多谐波可有基周期，但纯噪声不一定有单一周期。",
 "在长为T秒的一次完整重复中发生1个周期，单位时间重复次数是1/T；将振幅放大不会改变重复时间。",
 [("确定周期","观察波形重复所需最小正时间T，先核实是否真的周期以及时间单位。"),
  ("求基频","每秒包含1/T个完整周期，所以f=1/T，单位是s⁻¹=Hz。"),
  ("区分幅度与相位","正弦式中的A只缩放纵向幅值，φ只平移时间相位，均不直接修改f。")],
 "一个乐器音色含高次谐波；观测窗口太短或采样不足时可能发生频率混叠，不能将错误估计当作基频。",
 "错误写法：把正弦波振幅由1改为2会使音高频率440Hz翻倍为880Hz。",
 "sin(2π440t)与2sin(2π440t)仍在T=1/440秒后重复，故频率相同。",
 [E("周期T=1/440秒的纯音频率是多少？",["每秒重复次数是周期的倒数。","计算(1/440)的倒数=440。"],"440Hz","单位秒的倒数为Hz。"),
  E("周期T=1/220秒的信号频率是多少？",["用f=1/T。","结果是220Hz。"],"220Hz","周期较长，频率是440Hz例子的一半。")],
 ["先辨别横轴单位是秒还是毫秒。","找真正的重复周期，避免将半周期误认为周期。","用f=1/T换算，检查频率单位和是否有谐波干扰。"],
 "给定T=2毫秒，换算基频为多少Hz？",
 "录音采样率仅500Hz时能否可靠表示440Hz纯音？结合奈奎斯特频率说明可能出现什么混叠。"),
]
def demand(v,m):
    if not v:raise ValueError(m)
def build():
    candidates={r["local_key"]:r for r in json.loads(sem.OUT.read_text(encoding="utf-8"))["candidates"]}
    out=[]
    for raw in ROWS:
        r=candidates[raw["key"]]
        demand(len(raw["definition"])>=40 and len(raw["symbols"])>=30 and len(raw["scope"])>=38 and
               len(raw["explanation"])>=40 and len(raw["steps"])>=3 and len(raw["examples"])==2 and
               len(raw["hints"])==3 and len(raw["wrong"])>=25 and len(raw["why_wrong"])>=25 and
               len(raw["near"])>=18 and len(raw["far"])>=25,"incomplete teaching manuscript "+raw["key"])
        out.append({"id":"kb121-deep-"+raw["key"].lower(),"candidate_id":r["id"],
            "curriculum_standard":sem.base()["curriculum_standard"],
            "course_track":r["course_track"],"source":r["source"],"kind":r["kind"],
            "title":r["proposed_objective"],"formal_definition_or_statement":raw["definition"],
            "symbols":raw["symbols"],"applicability":raw["scope"],
            "why_it_works":raw["explanation"],
            "reasoned_steps":[{"step":s,"justification":why} for s,why in raw["steps"]],
            "boundary_and_counterexample":raw["boundary"],
            "typical_wrong_solution":raw["wrong"],"why_wrong":raw["why_wrong"],
            "teacher_examples":raw["examples"],"student_hint_ladder":raw["hints"],
            "near_transfer":raw["near"],"far_transfer":raw["far"],
            "proof_required":r["kind"]=="theorem",
            "proof_step_machine_certified":False,"math_example_exact_checks_passed":2,
            "teacher_review_status":"REVIEW_PENDING","teacher_evidence":None,
            "student_authoritative":False,"teacher_solution_visibility":"TEACHER_ONLY"})
    validate(out)
    return out
def validate(items):
    demand(len(items)==len(ROWS)==8 and len({r["candidate_id"] for r in items})==8,"duplicate/omitted manuscript")
    candidates={r["id"]:r for r in json.loads(sem.OUT.read_text(encoding="utf-8"))["candidates"]}
    for item,raw in zip(items,ROWS):
        demand(item["candidate_id"] in candidates,"unknown referenced editorial candidate")
        target=candidates[item["candidate_id"]]
        demand(item["id"]=="kb121-deep-"+raw["key"].lower() and
               item["candidate_id"]=="hs-semantic-pilot-121-"+raw["key"].lower() and
               item["course_track"]==target["course_track"] and item["source"]==target["source"]
               and item["kind"]==target["kind"] and item["title"]==target["proposed_objective"],"source/candidate spoofing")
        demand(item["formal_definition_or_statement"]==raw["definition"] and
               item["symbols"]==raw["symbols"] and item["applicability"]==raw["scope"] and
               item["why_it_works"]==raw["explanation"] and
               item["reasoned_steps"]==[{"step":s,"justification":why} for s,why in raw["steps"]] and
               item["boundary_and_counterexample"]==raw["boundary"] and
               item["typical_wrong_solution"]==raw["wrong"] and item["why_wrong"]==raw["why_wrong"] and
               item["teacher_examples"]==raw["examples"] and item["student_hint_ladder"]==raw["hints"] and
               item["near_transfer"]==raw["near"] and item["far_transfer"]==raw["far"],"original math manuscript tampered")
        demand(item["proof_required"]==(target["kind"]=="theorem") and
               item["proof_step_machine_certified"] is False and item["math_example_exact_checks_passed"]==2
               and item["teacher_review_status"]=="REVIEW_PENDING" and item["teacher_evidence"] is None
               and item["student_authoritative"] is False and item["teacher_solution_visibility"]=="TEACHER_ONLY","false proof/review/publication claim")
        demand(len(item["teacher_examples"])==2 and len(item["student_hint_ladder"])==3
               and all(len(x["steps"])>=2 for x in item["teacher_examples"]),"incomplete examples")
    return True
def oracle():
    # Independent exact computations, not an LLM self-assessment.
    R=S.Rational;x=S.symbols("x",real=True)
    expressions={
      "C203":[not all(v>=2 for v in (1,2,3)) and any(v<2 for v in (1,2,3)),
              not any(v%2!=0 for v in (2,4,6))],
      "C204":[S.solveset(x*x-5*x+6>=0,x,domain=S.S.Reals)==S.Union(S.Interval(-S.oo,2),S.Interval(3,S.oo)),
              S.solveset(-x*x+4>0,x,domain=S.S.Reals)==S.Interval.open(-2,2)],
      "S205":[S.solveset(25-25-x*x,x,domain=S.S.Reals)==S.FiniteSet(0),
              S.solveset(25-9-x*x,x,domain=S.S.Reals)==S.FiniteSet(-4,4)],
      "S206":[S.simplify(R(0,1)*R(1,2)+R(1,3)+2*R(1,6))==R(2,3) and sum([R(1,2),R(1,3),R(1,6)])==1,
              -R(1,4)+R(3,4)==R(1,2) and R(1,4)+R(3,4)==1],
      "A201":[S.limit((1+1/x)/(2+1/x),x,S.oo)==R(1,2),
              S.limit((3-1/x)/(1+1/x),x,S.oo)==3],
      "B203":[S.simplify(S.sqrt(1**2+2**2))==S.sqrt(5) and S.simplify((1/S.sqrt(5))**2+(2/S.sqrt(5))**2)==1,
              S.simplify(S.Integer(4)*(1-x*x/4)+x*x)==4 and S.simplify(S.Integer(4)-(x*x+4*(1-x*x/4)))==0],
      "EC202":[S.simplify(1/(1+S.exp(-S.Integer(0))))==R(1,2) and S.log(1)==0,
               S.simplify(1/(1+S.exp(-S.log(3))))==R(3,4) and S.exp(S.log(3))==3],
      "ED201":[1/R(1,440)==440,1/R(1,220)==220],
    }
    demand(set(expressions)=={r["key"] for r in ROWS},"oracle missing family")
    demand(all(len(vals)==2 and all(bool(v) for v in vals) for vals in expressions.values()),"exact math example failed")
    # Boundary negatives checked as exact facts, not universal formal proof.
    negative={
      "C203":any(v%2 for v in (2,3,4)),
      "C204":(-S.Integer(0)**2+4)>0,
      "S205":S.simplify(5**2-5**2)==0,
      "S206":sum([R(1,2),R(1,3),R(1,3)])!=1,
      "A201":S.limit((1/x)/(1/x**2),x,S.oo)==S.oo,
      "B203":S.sqrt(5)>2,
      "EC202":S.log(3)!=R(3,4),
      "ED201":S.simplify(S.diff(2*S.sin(2*S.pi*440*x),x)/(2*S.pi*440*2*S.cos(2*S.pi*440*x)))==1,
    }
    demand(all(bool(z) for z in negative.values()),"negative math case failed")
    return {"batch":121,"worked_example_cases":16,"exact_worked_example_checks_passed":16,
        "boundary_negative_checks_passed":8,"general_formal_proofs_certified":0,
        "student_free_text_verified":False,"teacher_approved":0,
        "details_by_candidate":{key:{"exact_worked_cases":2,"exact_negative_cases":1}
          for key in expressions}}
def render(rows):
    out=["# Batch121｜8份原创数学深度讲义（教师候审）","",
         "所有定理推导和例题均为原创草案；SymPy只独立核对具体数值和边界案例。未对一般命题完成形式证明或教师审校；教师解答默认不得向学生独立挑战泄漏。",""]
    for r in rows:
        out += [f"## {r['title']} · {r['course_track']}","",
                "**严格定义/表述**："+r["formal_definition_or_statement"],"",
                "**符号**："+r["symbols"],"",
                "**适用前提**："+r["applicability"],"",
                "**为什么成立**："+r["why_it_works"],""]
        for i,step in enumerate(r["reasoned_steps"],1):
            out += [f"{i}. **{step['step']}**：{step['justification']}"]
        out+=["","**边界与反例**："+r["boundary_and_counterexample"],"",
              "**典型错误解法**："+r["typical_wrong_solution"],"",
              "**错因**："+r["why_wrong"],"","### 教师示范题（不向学生自主解题泄露）",""]
        for i,ex in enumerate(r["teacher_examples"],1):
            out += [f"{i}. {ex['question']}","  - "+"；".join(ex["steps"]),
                    "  - 答案："+ex["answer"],"  - 验证："+ex["verification"]]
        out += ["","**三级渐进提示**："+ " → ".join(r["student_hint_ladder"]),"",
                "**近迁移**："+r["near_transfer"],"",
                "**远迁移**："+r["far_transfer"],""]
    return "\n".join(out).rstrip("\n")+"\n"
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    args=p.parse_args()
    rows=build();files={OUT:sem.serial(rows),REPORT:render(rows),ORACLE:sem.serial(oracle())}
    for path,blob in files.items():
        if args.write:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(blob,encoding="utf-8")
        else:demand(path.exists() and path.read_text(encoding="utf-8")==blob,"lesson drift "+str(path))
    print("Batch121: 8 original deep teacher draft lessons, 16 exact examples, 8 boundary negative cases, 0 approved")
if __name__=="__main__":main()
