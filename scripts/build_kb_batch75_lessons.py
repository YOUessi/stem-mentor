#!/usr/bin/env python3
"""Eight original cross-track review-only mathematics lessons with exact witnesses.

Teacher solutions never enter the student index. Finite arithmetic checks are
NOT substitutes for teacher review or general symbolic proof.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import build_kb_batch75_clause_splits as S
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"knowledge/editorial_review/kb_batch75_cross_track_teacher_drafts.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH75_CROSS_TRACK_MATH.md"

def lesson(id,anchor,track,kind,title,definition,symbols,assumptions,claim,steps,
           valid,boundary,counter,error,examples,hints,near,far,witness):
 return dict(id=id,source_editorial_subspan_id=anchor,curriculum_track_hint=track,
   knowledge_kind=kind,title=title,definition=definition,symbols=symbols,
   assumptions=assumptions,statement=claim,reasoning_steps=steps,
   mathematical_validity=valid,invalid_boundary=boundary,counterexample=counter,
   common_wrong_method=error,worked_examples=examples,graduated_hints=hints,
   near_transfer=near,far_transfer=far,finite_case=witness,
   source_license="ORIGINAL_PROJECT_AUTHORED",teacher_review="REVIEW_PENDING",
   teacher_signature=None,teacher_solution_visibility="TEACHER_ONLY",
   mathematical_certification="NOT_FORMALLY_CERTIFIED",
   teacher_proof_review="NOT_COMPLETED",official_atom_count=None,
   student_publishable=False,independent_challenge_solution_reveal=False)

L=[
lesson("KB75-M01","KB75-P016-S02","COMPULSORY","CONCEPT","充分条件与必要条件及逆命题",
 "对于同一论域内的命题P,Q，若P⇒Q总成立，则P是Q的充分条件，Q是P的必要条件；仅当反向也成立才是充要条件。",
 ["P: n被4整除","Q: n是偶数"],["论域为全体整数n","整除的定义是存在整数k满足n=4k"],
 "在整数域中被4整除是偶数的充分而非必要条件。",
 [["先固定论域","若把n换成非整数，整除表述可能失去原有含义。"],
  ["证明正向","n=4k=2(2k)，因k整数，2k整数，故n偶。"],
  ["检验逆向","取n=2，n是偶数却不是4的整数倍。"],
  ["区分条件方向","成立P⇒Q并不自动意味着Q⇒P，所以不是充要条件。"]],
 "充分条件判断须检查正向全称命题；必要条件判断须检查反向。",
 "不能因观察几个偶数都是4的倍数就把偶数当成4倍数的充分条件。",
 "n=2满足偶数却不满足4倍数，因此Q⇒P失败。",
 "把P⇒Q直接倒过来写成Q⇒P，属于逆命题未证。",
 [["在整数中，12是4的倍数能推出什么？","12=4×3=2×6，因此12是偶数；这是P⇒Q的实例，不单凭一个例子证明所有整数。"],
  ["10为偶数，能推出10被4整除吗？","10=2×5而10/4不是整数，因此反向不成立；一个反例即可否定全称逆命题。"]],
 ["先把题中两个性质写成P和Q。","证明P能否推出Q而不是凭样本猜测。","尝试构造满足Q但不满足P的整数。"],
 "讨论n是6倍数与n是3倍数的充分必要方向。",
 "判断几何中正方形与矩形的条件方向，必须保持图形定义一致。",
 dict(type="implication_divisible",n=12,divisor=4,consequent=2,expected=True)),
lesson("KB75-M02","KB75-P032-S02","COMPULSORY","METHOD","样本均值与总体均值不能混为一谈",
 "有限样本均值为所有样本值之和除以样本个数；总体均值是目标总体全部取值的均值或其分布期望，通常不等于一次抽样的均值。",
 ["x_i:第i个观察值","n:样本容量","x_bar:样本均值"],
 ["本例的样本为完全自编的合成数字","样本容量n必须为正且取值均可相加"],
 "算术平均数可从给定观测求出，但代表性与总体推断需要抽样设计和附加假设。",
 [["写出平均数定义","样本均值是(x1+…+xn)/n，n=0时不可定义。"],
  ["执行本例计算","对3、5、7，平均值(3+5+7)/3=5。"],
  ["展示推断边界","若目标总体为3、5、7、9，则总体均值=6，并非5。"],
  ["识别误推原因","样本均值是统计量而非每次都与总体参数一致的恒等量。"]],
 "把样本统计量用作总体参数估计时，必须报告抽样方式和不确定性。",
 "偏向高分样本、仅挑选容易联系的人，都不能当然代表目标总体。",
 "总体[3,5,7,9]的均值6，前3人的样本均值5，并非必然相等。",
 "把观察到的样本均值当成无误差的总体均值，忽视抽样偏差。",
 [["样本4、6、8的平均值是多少？","总和为18，除以3得到6；这只对该三元素样本成立。"],
  ["样本2、2与总体2、2、10能否有相同均值？","样本均值2；总体均值14/3；两者不同，不能从样本直接断言总体。"]],
 ["先区分样本与目标总体。","列出样本总和及非零样本容量。","讨论抽样机制是否足以支持总体结论。"],
 "用随机抽样与便利抽样比较抽样设计前提。",
 "调研投票率时区分调查对象、未应答者和估计总体。",
 dict(type="sample_mean",values=[3,5,7],expected_num=5,expected_den=1)),
lesson("KB75-M03","KB75-P046-S03","SELECTIVE_COMPULSORY","THEOREM","条件概率的非零分母和事件包含关系",
 "在同一概率空间中，若P(B)>0，则P(A|B)=P(A∩B)/P(B)，即把样本空间限制到B后的A发生概率。",
 ["A,B:同一概率空间中的事件","P(B):条件事件概率","P(A∩B):交事件概率"],
 ["A和B均是同一概率空间的可测事件","P(B)>0并且0≤P(A∩B)≤P(B)≤1"],
 "条件概率公式在非零条件事件上成立，且计算值处于[0,1]。",
 [["限定条件事件","只在B发生的情况下讨论，新的归一化基准是P(B)。"],
  ["使用交事件","同时发生A与B的概率不能大于B的概率。"],
  ["归一化","P(B)>0才可用P(A∩B)/P(B)计算条件概率。"],
  ["核对边界","由0≤P(A∩B)≤P(B)得0≤P(A|B)≤1。"]],
 "分母必须严格正；A和B必须来自同一事件模型。",
 "P(B)=0时不能套除法公式；交事件概率大于P(B)不可能。",
 "若P(B)=0，写成1/5÷0属于非法运算，不存在该商。",
 "把P(A|B)误写为P(A∩B)/P(A)，颠倒条件事件。",
 [["P(B)=2/5，P(A∩B)=1/5，求P(A|B)。","(1/5)/(2/5)=1/2；同时检查1/5≤2/5以验证事件包含约束。"],
  ["P(B)=1/2，P(A∩B)=1/4，求条件概率。","(1/4)/(1/2)=1/2，分母非零且交事件不超过条件事件。"]],
 ["先写清楚究竟是给定A还是给定B。","检查分母是否为零。","核对交事件包含关系后做分式约分。"],
 "若条件从B改成A，解释为什么结果可能不同。",
 "医疗筛查的阳性预测值与灵敏度不是同一条件概率。",
 dict(type="conditional",intersection=[1,5],condition=[2,5],expected=[1,2])),
lesson("KB75-M04","KB75-P056-S02","ELECTIVE_A","CONCEPT","均匀连续分布的密度与区间概率",
 "若X在a<b的实数区间[a,b]均匀分布，则密度在该区间为1/(b-a)，区间外为0；区间概率是密度在交集上的积分。",
 ["X:连续随机变量","a,b:有限支撑端点","f_X(x):密度"],
 ["a,b为有限实数且a<b","仅在模型已指定均匀密度时使用该公式"],
 "对a≤u≤v≤b，P(u≤X≤v)=(v-u)/(b-a)；连续变量单点概率为0。",
 [["确认密度归一","密度非负且积分从a到b等于(b-a)/(b-a)=1。"],
  ["计算区间概率","求区间[u,v]与支撑[a,b]的交长度，再除以b-a。"],
  ["处理点概率","连续密度在单点上的积分为0。"],
  ["辨认定义域","若a=b，1/(b-a)无意义，不能当作均匀连续分布。"]],
 "计算区间概率先交支撑域；密度值并不是单点发生概率。",
 "区间长度为0时单点概率为0；将密度1/4解释为P(X=3)=1/4是错误的。",
 "X在[2,6]均匀分布时P(X=3)=0，尽管密度f(3)=1/4。",
 "把概率密度函数在一个点上的高度误当作该点概率。",
 [["X在[2,6]均匀分布，P(3≤X≤5)是多少？","有利区间长度2，总长度4，概率=2/4=1/2。"],
  ["X在[0,10]均匀分布，P(8≤X≤12)是多少？","只能落在[8,10]部分，交集长度2，故概率2/10=1/5，而不是4/10。"]],
 ["先找概率密度支撑区间。","对目标区间和支撑求交集。","把交集长度除以总长度。"],
 "讨论不同宽度均匀密度的最高值可能大于1却无矛盾。",
 "用持续到达时间模型说明与离散等可能模型的区别。",
 dict(type="uniform_interval",a=2,b=6,u=3,v=5,expected=[1,2])),
lesson("KB75-M05","KB75-P058-S02","ELECTIVE_B","CONCEPT","二元函数偏导数必须固定另一变量",
 "设f在(x0,y0)邻域内有定义，若lim(h→0)[f(x0+h,y0)-f(x0,y0)]/h存在，则称其为对x的偏导数，并且计算中保持y=y0不变。",
 ["f(x,y):二元函数","h:x方向增量","∂f/∂x:对x偏导数"],
 ["被考察点周围允许x方向的非零小增量","所需单变量差商极限存在"],
 "对多项式f(x,y)=x²y+3y，∂f/∂x=2xy，∂f/∂y=x²+3。",
 [["回到偏导定义","求x偏导时，y始终取固定y0，不能随着h变化。"],
  ["计算差商","( (x+h)²y+3y -(x²y+3y) )/h = 2xy+hy。"],
  ["取极限","h趋0得2xy，导数存在。"],
  ["交换方向","求y偏导时x固定，得x²+3；两种偏导不同。"]],
 "偏导数不是沿任意曲线路径的导数；混合变化需要链式法则或全微分。",
 "沿y=x变化得到的d/dx f(x,x)并非固定y时的∂f/∂x。",
 "f(x,x)=x³+3x，导数3x²+3；固定y求偏导后代y=x得到2x²，两者一般不同。",
 "把另一个变量当作x的函数，却声称在求偏导。",
 [["f=x²y+3y，在(2,1)的x偏导是多少？","∂f/∂x=2xy，代入得4；另一变量y保持1。"],
  ["f=x²y+3y，在(2,1)的y偏导是多少？","∂f/∂y=x²+3=7；与x偏导4不同。"]],
 ["先标明求哪一个方向的偏导。","其余变量在该方向差商中固定。","取差商极限并在指定点代值。"],
 "比较方向导数与偏导，检查方向是否沿坐标轴。",
 "在多变量成本模型中解释固定产量或固定价格的假设。",
 dict(type="partial_polynomial",x=2,y=1,expected_x=4,expected_y=7)),
lesson("KB75-M06","KB75-P060-S02","ELECTIVE_B","THEOREM","三阶线性方程组的行列式非零唯一解",
 "三阶系数矩阵A对应线性系统Ax=b；当det(A)≠0时A可逆，存在唯一解x=A⁻¹b。克拉默法则将第i列替为b得xi=det(Ai)/det(A)。",
 ["A:3×3系数矩阵","b:常数列向量","det(A):行列式"],
 ["矩阵必须恰为3×3且元素属于实数或有理数","det(A)≠0时才可除以det(A)"],
 "当det(A)≠0时三元一次方程组有唯一解，并可用克拉默法则。",
 [["说明可逆条件","非零行列式意味着矩阵列向量线性无关，线性映射可逆。"],
  ["取得存在性","对任意b令x=A⁻¹b，则Ax=b。"],
  ["证明唯一性","若Ax=b且Ay=b，则A(x-y)=0，左乘A⁻¹得到x=y。"],
  ["说明克拉默法则","行列式对列线性，用b=ΣxiAi列展开得到det(Ai)=xi det(A)。"]],
 "det(A)=0时不能使用逆矩阵或克拉默分母；零行列式可能无解也可能无穷多解。",
 "系数矩阵存在两行相等时行列式为0，不能因为写出形式分式就说唯一解。",
 "A为零矩阵，b=0时有无穷多解；b非零时无解，均不满足唯一解断言。",
 "未计算行列式是否为0就对它作除法。",
 [["A=diag(2,3,5)，b=(4,9,10)，求解。","det(A)=30≠0，解为(2,3,2)，代入A得到(4,9,10)，各行严格成立。"],
  ["A=diag(1,2,3)，b=(2,6,12)，求解。","det(A)=6≠0，逐行解得(2,3,4)，代入验证等式。"]],
 ["检查系数矩阵形状是否正好3×3。","先计算det(A)并判断是否为0。","使用克拉默或消元后将解代回三式。"],
 "构造一组线性相关的列并比较无解和无穷多解。",
 "对三传感器标定讨论何时测量方程不足以唯一确定参数。",
 dict(type="cramer_3x3",A=[[2,0,0],[0,3,0],[0,0,5]],b=[4,9,10],expected=[2,3,2])),
lesson("KB75-M07","KB75-P064-S03","ELECTIVE_C","THEOREM","逆否命题与原命题的逻辑等价",
 "对于任意命题P和Q，P⇒Q与¬Q⇒¬P在所有真假赋值下有相同真值，因此两命题等价。",
 ["P,Q:命题","¬:否定","⇒:蕴含"],
 ["P与Q具有确定真值且采用经典二值逻辑","需保持P和Q的论域和量词范围不变"],
 "证明P⇒Q可等价地证明¬Q⇒¬P，而不能直接替换成Q⇒P。",
 [["蕴含假值情况","P⇒Q仅在P真且Q假时为假。"],
  ["逆否命题假值","¬Q⇒¬P仅在¬Q真且¬P假时为假，亦即Q假且P真。"],
  ["逐真值组合比较","两者唯一的假值组合相同，其余三个组合都为真。"],
  ["阐明证明方法","因此为证明原命题，可证明逆否；逆命题需另证。"]],
 "仅在相同论域和一致否定下作等价替换；反命题或逆命题不一定等价。",
 "正向n是6倍数⇒n是3倍数成立；逆向n是3倍数⇒n是6倍数不成立。",
 "n=3为3的倍数而不是6的倍数，否定了非法逆向推理。",
 "把逆否命题偷换成逆命题或简单把结论否定。",
 [["若n被6整除，则n被3整除，写出逆否命题。","若n不被3整除，则n不被6整除；这与原命题等价。"],
  ["n被3整除⇒n被6整除是否成立？","不成立，n=3就是反例；不能将逆命题当逆否命题。"]],
 ["写出P,Q并将二者分别取否定。","逆否是¬Q⇒¬P，顺序和真假均要调整。","检查真值表四组情形是否一致。"],
 "尝试把不能被偶数整除的问题改用逆否证明。",
 "在自动程序断言中区分逆否推理与不合法的逆向推断。",
 dict(type="contrapositive_truth",p=True,q=False,expected=False)),
lesson("KB75-M08","KB75-P069-S03","ELECTIVE_D","METHOD","轴对称变换的坐标不变量",
 "在直角坐标平面中，关于y轴的反射T(x,y)=(-x,y)；它保留点到原点的距离和两点间距离，且T(T(P))=P。",
 ["P=(x,y):原平面点","T:关于y轴镜像变换","d:欧氏距离"],
 ["采用同一正交单位的直角坐标系","反射轴为y轴，不是任意倾斜坐标轴"],
 "对任意平面点，关于y轴反射是保距且为自身逆变换。",
 [["写出变换","T只改变横坐标符号，纵坐标不变。"],
  ["验证两次反射","T(T(x,y))=T(-x,y)=(x,y)。"],
  ["验证距离","反射后两点差变为(-(x1-x2),y1-y2)，平方距离不变。"],
  ["明确适用范围","一般仿射缩放不一定保距，不能把所有图案变化称为反射。"]],
 "对称性是一种可测几何关系，不能从美观主观感受推出严格数学对称。",
 "变换(x,y)→(2x,y)不是关于y轴的反射，且改变了横向长度。",
 "点(2,3)变为(4,3)属于x方向拉伸，而y轴反射应该是(-2,3)。",
 "只看图形大致像镜面就断言每点满足精确反射关系。",
 [["P=(2,3)关于y轴的像是什么？","T(P)=(-2,3)，两点到原点的距离都为√13。"],
  ["点(-4,1)连续反射两次的结果是什么？","第一次(4,1)，第二次(-4,1)，与原点完全重合。"]],
 ["先指定镜像轴而不凭视觉猜测。","写出坐标变换的精确公式。","检查变换两次是否还原并核对距离平方。"],
 "比较关于x轴与关于y轴的反射顺序。",
 "在图案设计中用坐标与距离数据验证严格轴对称而非主观美感。",
 dict(type="reflection_y",point=[2,3],expected=[-2,3])),
]
def canon(x):return json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
def exact(v):
 if type(v) is int:return F(v)
 if isinstance(v,list) and len(v)==2 and all(type(z) is int for z in v) and v[1]!=0:return F(v[0],v[1])
 raise ValueError("Exact rational integer/fraction required")
def det3(A):
 assert len(A)==3 and all(len(row)==3 for row in A)
 a,b,c=A
 return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def verify_finite(case):
 """Strict finite case independently recomputed, not full theorem certification."""
 t=case["type"]
 if t=="implication_divisible":
  n=exact(case["n"]);a=exact(case["divisor"]);b=exact(case["consequent"])
  assert a.denominator==b.denominator==n.denominator==1 and a>0 and b>0 and a%b==0
  result=(n%a!=0 or n%b==0)
  assert type(case["expected"]) is bool and result is case["expected"]
 elif t=="sample_mean":
  values=[exact(z) for z in case["values"]]
  assert 1<=len(values)<=100
  assert sum(values,F(0))/len(values)==exact([case["expected_num"],case["expected_den"]])
 elif t=="conditional":
  p=exact(case["intersection"]);b=exact(case["condition"])
  assert 0<=p<=b<=1 and b>0
  assert p/b==exact(case["expected"])
 elif t=="uniform_interval":
  a=exact(case["a"]);b=exact(case["b"]);u=exact(case["u"]);v=exact(case["v"])
  assert a<b and u<=v
  overlap=max(F(0),min(b,v)-max(a,u))
  assert overlap/(b-a)==exact(case["expected"])
 elif t=="partial_polynomial":
  x=exact(case["x"]);y=exact(case["y"])
  assert 2*x*y==exact(case["expected_x"]) and x*x+3==exact(case["expected_y"])
 elif t=="cramer_3x3":
  A=[[exact(z) for z in row] for row in case["A"]]
  b=[exact(z) for z in case["b"]]
  assert len(A)==len(b)==3 and all(len(row)==3 for row in A)
  d=det3(A);assert d!=0
  ans=[]
  for i in range(3):
   matrix=[[b[j] if k==i else A[j][k] for k in range(3)] for j in range(3)]
   ans.append(det3(matrix)/d)
  assert ans==[exact(z) for z in case["expected"]]
  assert all(sum(A[i][j]*ans[j] for j in range(3))==b[i] for i in range(3))
 elif t=="contrapositive_truth":
  assert type(case["p"]) is type(case["q"]) is type(case["expected"]) is bool
  p,q=case["p"],case["q"]
  assert ((not p) or q)==(q or (not p))==case["expected"]
  # Exhaustively verify ALL 4 truth-table rows for this propositional law.
  assert all(((not x) or y)==(y or (not x)) for x in [False,True] for y in [False,True])
 elif t=="reflection_y":
  p=[exact(z) for z in case["point"]];e=[exact(z) for z in case["expected"]]
  assert len(p)==len(e)==2
  tpoint=[-p[0],p[1]]
  assert e==tpoint and [-tpoint[0],tpoint[1]]==p
  assert sum(v*v for v in p)==sum(v*v for v in tpoint)
 else:raise ValueError("Unsupported exact finite witness")
 return True
def build():
 source=S.B73.load(S.OUT)
 index={r["id"]:r for r in source["records"]}
 assert len(L)==8 and len(set(x["id"] for x in L))==8
 for row in L:
  sid=row["source_editorial_subspan_id"]
  assert sid in index and index[sid]["track_hint"]==row["curriculum_track_hint"]
  assert index[sid]["role"] in ("KNOWLEDGE_CANDIDATE","EXISTING_DRAFT_LINK")
  assert row["knowledge_kind"] in ("METHOD","THEOREM","CONCEPT")
  for key in ("title","definition","statement","mathematical_validity",
              "invalid_boundary","counterexample","common_wrong_method",
              "near_transfer","far_transfer"):
   assert isinstance(row[key],str) and len(row[key])>(7 if key=="title" else 15),(row["id"],key)
  assert len(row["symbols"])>=2 and len(row["assumptions"])>=2
  assert len(row["reasoning_steps"])>=3
  assert all(len(a)==2 and len(a[0])>2 and len(a[1])>10 for a in row["reasoning_steps"])
  assert len(row["worked_examples"])>=2
  assert all(len(q)>=14 and len(ans)>18 for q,ans in row["worked_examples"])
  assert len(row["graduated_hints"])==3
  assert row["source_license"]=="ORIGINAL_PROJECT_AUTHORED"
  assert row["teacher_review"]=="REVIEW_PENDING" and row["teacher_signature"] is None
  assert row["teacher_solution_visibility"]=="TEACHER_ONLY"
  assert row["mathematical_certification"]=="NOT_FORMALLY_CERTIFIED"
  assert row["teacher_proof_review"]=="NOT_COMPLETED" and not row["student_publishable"]
  assert row["official_atom_count"] is None and row["independent_challenge_solution_reveal"] is False
  verify_finite(row["finite_case"])
 return dict(schema_version="kb75-cross-track-original-teacher-drafts-v1",
     source_pdf_sha256=S.B74.PDF_SHA,source_editorial_matrix_sha256=__import__("hashlib").sha256(S.OUT.read_bytes()).hexdigest(),
     teacher_review="REVIEW_PENDING",distribution="TEACHER_ONLY",
     teacher_approved=0,student_published=0,official_atom_denominators={t:None for t in S.B73.TRACKS},
     finite_case_certification="EXACT_BOUNDED_INSTANCES_ONLY",
     universal_math_proof_certification="NOT_FORMALLY_CERTIFIED",
     teacher_drafts=L)
def validate_teacher_pack(pack):
 """Reject unauthorized publication and forged teacher attestations."""
 assert pack["schema_version"]=="kb75-cross-track-original-teacher-drafts-v1"
 assert pack["distribution"]=="TEACHER_ONLY"
 assert pack["teacher_review"]=="REVIEW_PENDING"
 assert pack["teacher_approved"]==pack["student_published"]==0
 assert pack["official_atom_denominators"]=={t:None for t in S.B73.TRACKS}
 assert pack["finite_case_certification"]=="EXACT_BOUNDED_INSTANCES_ONLY"
 assert pack["universal_math_proof_certification"]=="NOT_FORMALLY_CERTIFIED"
 assert pack["source_editorial_matrix_sha256"]==__import__("hashlib").sha256(S.OUT.read_bytes()).hexdigest()
 assert len(pack["teacher_drafts"])==8 and len({x["id"] for x in pack["teacher_drafts"]})==8
 for row in pack["teacher_drafts"]:
  assert row["teacher_review"]=="REVIEW_PENDING" and row["teacher_signature"] is None
  assert row["teacher_solution_visibility"]=="TEACHER_ONLY"
  assert row["mathematical_certification"]=="NOT_FORMALLY_CERTIFIED"
  assert row["teacher_proof_review"]=="NOT_COMPLETED" and row["official_atom_count"] is None
  assert row["student_publishable"] is False and row["independent_challenge_solution_reveal"] is False
  assert row["source_license"]=="ORIGINAL_PROJECT_AUTHORED"
  verify_finite(row["finite_case"])
 return True

def report(x):
 return "\n".join(["# Batch75｜跨轨8篇原创数学深度草案和受控验证","",
   "- 8篇原创：必修2、选择性必修1、选修A1、B2、C1、D1；选修E依学校真实课程计划单独处理。",
   "- 每篇2道完整原创例题、≥3步逐步数学依据、反例与错误原因、三级提示与近远迁移。",
   "- 精确算术实例8类，测试覆盖非法输入及条件失效；一类命题逻辑等价采用完整四行真值表检查。",
   "- 验证实例不是一般定理形式认证；定理草案仍需数学教师独立审核。",
   "- 8份草案全部REVIEW_PENDING/TEACHER_ONLY，未接入学生批准索引。",
   "- 来源是Batch75 Mac PDFKit细分子片段，而非已认证的官方课程原子。",
   "", "## 逐篇审查范围",
   *[f"- {z['id']}（{z['curriculum_track_hint']}）：{z['title']}；证据 {z['source_editorial_subspan_id']}。"
     for z in x["teacher_drafts"]],
   "", "## 下一批","- 教师复核条件和数学推导，继续补齐课程全量原子分母与真正缺失的教学单元。",""])
def main():
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
 x=build();validate_teacher_pack(x);m=report(x)
 if a.check:
  assert OUT.read_text(encoding="utf8")==canon(x)
  assert REPORT.read_text(encoding="utf8")==m
 else:
  OUT.write_text(canon(x),encoding="utf8");REPORT.write_text(m,encoding="utf8")
 print("Batch75 lessons:",len(x["teacher_drafts"]),"teacher drafts with exact bounded witnesses")
if __name__=="__main__":main()
