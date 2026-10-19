"""v0.11b closed-interval extrema. Five fixed functions, candidate comparison."""
from copy import deepcopy

def p(key,label,lo,hi,value,step=.1):
 return dict(key=key,label=label,min=lo,max=hi,value=value,step=step)

def interval(L=-2,R=3):
 return [p("L","闭区间左端点 L",-4,4,L,.1),
         p("R","闭区间右端点 R",-3,6,R,.1)]

def extra_presets():
 definitions=[
  ("extrema-quadratic","闭区间最值：二次函数",
   r"f(x)=ax^2+bx+c,\quad x\in[L,R]",
   [p("a","二次系数 a",-2,2,1,.1),p("b","一次系数 b",-4,4,-2,.1),
    p("c","常数 c",-3,3,0,.1)]+interval(-1,3),
   "区间内部驻点可能是最小值，但全局最大值常在某个端点。"),
  ("extrema-cubic","闭区间最值：三次函数",
   r"f(x)=a(x^3-3x)+k,\quad x\in[L,R]",
   [p("a","尺度 a",-1,1,.5,.05),p("k","偏移 k",-3,3,0,.1)]+interval(-2,3),
   "存在驻点仍须与端点比较；不能将局部极大误认为全局最大。"),
  ("extrema-absolute","闭区间最值：绝对值折点",
   r"f(x)=a|x-h|+k,\quad x\in[L,R]",
   [p("a","系数 a",-2,2,1,.1),p("h","折点 h",-3,3,1,.1),
    p("k","平移 k",-3,3,0,.1)]+interval(-2,3),
   "不可导的折点也可能取得最值，不能只找 f'(x)=0。"),
  ("extrema-sine","闭区间最值：三角函数",
   r"f(x)=A\sin(\omega x+\varphi)+k",
   [p("A","振幅 A",-3,3,1,.1),p("w","角频率 ω",-3,3,1,.1),
    p("phi","相位 φ",-3,3,0,.1),p("k","平移 k",-3,3,0,.1)]+interval(0,5),
   "只考虑闭区间内部实际落入的临界点，比较相同最大值出现的多个位置。"),
  ("extrema-log","闭区间最值：对数函数与定义域",
   r"f(x)=\ln x,\quad 0<L\le x\le R",
   [p("L","左端点 L（应大于0）",.1,5,.5,.1),
    p("R","右端点 R",.2,6,4,.1)],
   "整个闭区间必须落在 x>0，端点不符合定义域时不得输出假最值。"),
 ]
 guidance=[
   "先圈出题目规定的闭区间，预测最值可能发生在哪里。",
   "除了满足 f′(x)=0 的点，还有哪些点必须比较？",
   "检查端点、区间内部驻点及不可导点；用反例验证只找驻点是否可靠。"
 ]
 return [dict(id=id,tool="function_2d",title=title,equation=id,
    latex=latex,params=deepcopy(params),description=desc,
    source="PROJECT_AUTHORED",expert_review="PENDING",
    simulation=True,assist_default=False,prediction_prompt=guidance[0],
    thinking_prompts=list(guidance)) for id,title,latex,params,desc in definitions]

def apply_coverage(rows,presets):
 known={p["id"] for p in presets}
 fresh={p["id"] for p in extra_presets()}
 if not fresh<=known:raise ValueError("Extrema scene evidence missing")
 for item in rows:
    if item["concept"]=="极值与最值":
       item["available_presets"]=list(dict.fromkeys(
         item["available_presets"]+["extrema-quadratic","extrema-cubic","extrema-absolute","extrema-sine","extrema-log"]))
       item["capability_limits"]="仅5类固定函数的闭区间候选点/端点比较，无法验证任意函数的全局最值定理。"
    if item["concept"]=="导数判断单调性":
       item["available_presets"]=list(dict.fromkeys(item["available_presets"]+["extrema-cubic"]))
       item["capability_limits"]="固定函数的驻点、端点候选与数值观察；不等于已经自动证明任意函数单调性。"
 return rows
