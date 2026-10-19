"""v0.12 authored, fixed and offline introductory probability/statistics presets."""
from copy import deepcopy

def p(key,label,lo,hi,value,step=1):
 return dict(key=key,label=label,min=lo,max=hi,value=value,step=step)

MODELS=[
 ("prob-choose","计数原理：组合数","probability_2d",
  r"C_n^k=\frac{n!}{k!(n-k)!}",[p("n","总数 n",0,30,8),p("k","抽取 k",0,30,3)],
  "不考虑顺序，观察 k 与 n−k 的对称性。"),
 ("prob-permute","计数原理：排列数","probability_2d",
  r"A_n^k=\frac{n!}{(n-k)!}",[p("n","总数 n",0,16,7),p("k","抽取 k",0,16,3)],
  "排列顺序会影响计数；先与组合数比较。"),
 ("prob-tree","两阶段事件概率树","probability_2d",
  r"P(A\cap B)=P(A)P(B\mid A)",[p("p","P(A)",0,1,.6,.05),
   p("q1","P(B|A)",0,1,.2,.05),p("q0","P(B|非A)",0,1,.7,.05)],
  "区分条件概率与无条件概率，四个叶节点概率和应为1。"),
 ("prob-binomial","二项分布：有放回独立重复","probability_2d",
  r"P(X=k)=\binom nk p^k(1-p)^{n-k}",[p("n","实验次数 n",0,25,10),
   p("p","成功概率 p",0,1,.4,.05),p("k","观察k",0,25,3)],
  "分布柱高是每个离散事件的理论概率，不能与模拟频率混淆。"),
 ("prob-hypergeo","超几何：无放回抽样","probability_2d",
  r"P(X=k)=\frac{\binom Kk\binom{N-K}{n-k}}{\binom Nn}",
  [p("N","总体N",2,30,20),p("K","成功个数K",0,30,8),
   p("n","抽样n",0,30,7),p("k","观察k",0,30,3)],
  "不放回抽样时成功次数之间通常不独立。"),
 ("prob-normal","正态分布：密度不是概率","probability_2d",
  r"f(x)=\frac1{\sigma\sqrt{2\pi}}e^{-\frac{(x-\mu)^2}{2\sigma^2}}",
  [p("mu","均值μ",-3,3,0,.25),p("sigma","标准差σ",.3,3,1,.1),
   p("L","观察范围左端L",-5,5,-1,.2),p("R","观察范围右端R",-5,5,1,.2)],
  "连续变量单点的密度值不是事件概率；区间概率来自面积。"),
 ("stats-bernoulli","固定种子：实验频率与理论概率","statistics_2d",
  r"\widehat p=\frac{X}{n}",[p("p","成功概率p",0,1,.35,.05),
    p("n","模拟次数n",10,1000,200,10),p("seed","固定随机种子",1,10000,42)],
  "样本频率有波动，不能将模拟值直接标成理论概率。"),
 ("stats-summary","样本均值、中位数、众数与方差","statistics_2d",
  r"\\bar x=\\frac1n\\sum x_i,\\quad s^2=\\frac{\\sum(x_i-\\bar x)^2}{n-1}",
  [p("x1","数据x₁",-5,5,1,.5),p("x2","数据x₂",-5,5,2,.5),
   p("x3","数据x₃",-5,5,2,.5),p("x4","数据x₄",-5,5,3,.5),
   p("x5","数据x₅",-5,5,5,.5)],
  "比较样本方差和总体方差的分母，注意无重复值时可能没有众数。"),
 ("stats-regression","散点图与一元线性回归","statistics_2d",
  r"\hat y=\hat\beta_0+\hat\beta_1x",
  [p("slope","模拟真实斜率",-3,3,1.5,.1),p("intercept","模拟截距",-3,3,.5,.1),
   p("noise","噪声幅度",0,3,.7,.1),p("n","样本量n",3,30,14),
   p("seed","固定随机种子",1,10000,42)],
  "相关系数与回归只描述当前合成样本，不表明因果关系。"),
]

def extra_presets():
 prompts=[
  "先预测哪一组数值会改变，为什么？",
  "看清每个概率与随机事件的定义，是否需要额外假设？",
  "用特殊参数核对归一化、定义域与样本波动，再判断你的猜想是否可靠。"
 ]
 out=[]
 for id,title,tool,latex,parameters,description in MODELS:
  out.append(dict(id=id,title=title,tool=tool,latex=latex,equation=id,
   description=description,params=deepcopy(parameters),
   source="PROJECT_AUTHORED",expert_review="PENDING",simulation=True,
   assist_default=False,
   prediction_prompt="先观察参数与图像，预测计算或抽样的结果。",
   thinking_prompts=list(prompts)))
 return out

EVIDENCE={
 "分类加法计数原理":["prob-choose"],
 "分步乘法计数原理":["prob-permute"],
 "排列与组合":["prob-choose","prob-permute"],
 "样本空间与随机事件":["prob-tree"],
 "古典概型":["prob-choose"],
 "概率加法与乘法基本关系":["prob-tree"],
 "条件概率与独立性":["prob-tree"],
 "离散型随机变量":["prob-binomial","prob-hypergeo"],
 "二项分布":["prob-binomial"],
 "超几何分布":["prob-hypergeo"],
 "正态分布":["prob-normal"],
 "均值中位数众数":["stats-summary"],
 "方差标准差":["stats-summary"],
 "回归分析与相关性":["stats-regression"]
}

def apply_coverage(rows,presets):
 ids={p["id"]:p for p in presets}
 for row in rows:
  names=EVIDENCE.get(row["concept"])
  if names is None:continue
  if not all(n in ids for n in names):raise ValueError("概率统计数据目录缺少真实场景")
  existing=row.get("available_presets",[])
  row["available_presets"]=list(dict.fromkeys(existing+names))
  row["recommended_tool"]=ids[names[0]]["tool"]
  row["status"]="INTERACTIVE_FOUNDATION"
  row["capability"]="有限固定概率分布、统计与计数模型；非所有考试情境"
  row["capability_limits"]="仅固定整数范围与合成数据；未实现一般统计推断、数学证明或真实样本采集。"
 return rows
