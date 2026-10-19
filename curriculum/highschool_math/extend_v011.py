"""v0.11 authored finite-sequence scene presets and limited curriculum evidence."""
from copy import deepcopy

def p(key,label,lo,hi,val,step=1):
    return {"key":key,"label":label,"min":lo,"max":hi,"value":val,"step":step}

def choice(key,label,labels,default=0):
    return {"key":key,"label":label,"min":0,"max":len(labels)-1,
            "value":default,"step":1,"options":[
                {"value":i,"label":label_text} for i,label_text in enumerate(labels)]}

def extra_presets():
    a1=p("a1","首项 a₁",-6,6,2,.5)
    d=p("d","公差 d",-4,4,2,.5)
    q=p("q","公比 q",-2,2,1.5,.05)
    n=p("n","观察项数 n",1,24,12,1)
    models=[
      ("seq-arithmetic","等差数列：差与通项猜想",
        r"a_{n+1}=a_n+d", [a1,d,n],
        "先观察相邻两项的差，再猜想第 n 项。",
        ["观察相邻两项的差是否相同。","你能用第一项与重复的差表示第 n 项吗？","当公差为负或零时，你的猜想仍成立吗？"]),
      ("seq-geometric","等比数列：公比与交替",
        r"a_{n+1}=q a_n", [a1,q,n],
        "正负、公比 0、1 和接近 1 都需要单独核对。",
        ["观察相邻项的乘法关系。","如果公比是负的，能预测符号吗？","q=1 和 q=0 时，哪些通常推导需要单独讨论？"]),
      ("seq-geometric-edge","等比数列：q=1、0、−1 边界",
        r"a_{n+1}=q a_n", [p("a1","首项 a₁",-6,6,2,.5),
        choice("q","典型公比",["q=1：恒定","q=0：之后为零","q=−1：交替","q=0.5：衰减","q=−1.5：交替放大"],0),n],
        "选择边界公比。注意 q=1 的有限和不能使用含 1-q 分母的表达式。",
        ["不必先背公式，观察每项究竟发生了什么。","把 n 项实际加起来，是否存在特殊情况？","为什么含 1−q 分母的通式不能在 q=1 直接代入？"]),
      ("seq-linear-recurrence","一阶递推：从当前项到下一项",
        r"a_{n+1}=r a_n+c",[a1,p("r","乘数 r",-2,2,.8,.1),p("c","增量 c",-4,4,1,.25),n],
        "对比 r=1、r=0、0<r<1 等边界，观察初值与稳定点。",
        ["观察 a_{n+1} 与 a_n 的对应关系。","有没有某个值代入后保持不变？","r=1 时，这个递推与哪种熟悉的数列相同？"]),
      ("seq-two-term","二阶递推：两项决定下一项",
        r"a_{n+2}=a_{n+1}+a_n",[p("a1","第一项 a₁",-5,5,1,1),
        p("a2","第二项 a₂",-5,5,1,1),n],
        "必须提供两个初值，不能凭一个初值唯一确定整列。",
        ["下一项由前面的几项共同决定？","只给 a₁ 而不给 a₂，结果能唯一确定吗？","改变第二项，前几项怎样受到影响？"]),
      ("seq-partial-sum","数列的部分和：从项到 Sₙ",
        r"S_n=\sum_{k=1}^{n}a_k",[choice("kind","数列类型",["等差","等比"],0),
        a1,d,q,n],"前五项可见；先预测总和，主动打开部分和轨迹。",
        ["每个 Sₙ 比上一个部分和多了哪项？","你能用相邻两个部分和还原 aₙ 吗？","当 q=1 或负公比时，观察到的和是否符合你的猜想？"]),
      ("seq-growth","有限项增长比较：等差与等比",
        r"a_n=a_1+(n-1)d,\quad b_n=a_1q^{n-1}",[a1,d,q,n],
        "只比较这 n 项及其绝对值，不从有限图像宣称无穷远的大小关系。",
        ["先猜测哪一列在当前有限范围增长更快。","负公比时，比较有符号数值还是绝对值更合适？","有限项的观察能否直接证明任意 n 的结论？"]),
      ("seq-fixed-point","递推的平衡点：观察趋近",
        r"a_{n+1}=r a_n+c",[a1,p("r","乘数 r",-1.5,1.5,.5,.05),
          p("c","常量 c",-3,3,2,.25),n],
        "观察与候选平衡点之间的距离；收敛性不靠有限画点证明。",
        ["如果下一项和当前项相等，该数需要满足什么条件？","什么时候递推根本不存在唯一固定点？","图上看起来靠近，是否就完成严格证明？"]),
    ]
    output=[]
    for id,title,latex,params,description,hints in models:
        output.append(dict(id=id,tool="sequence_2d",title=title,equation=id,latex=latex,
         params=deepcopy(params),description=description,source="PROJECT_AUTHORED",
         expert_review="PENDING",simulation=True,assist_default=False,
         prediction_prompt="先观察前几项。你预测下一项、后续规律或部分和会怎样变化？",
         thinking_prompts=hints))
    return output

EVIDENCE={
 "数列概念与递推":["seq-linear-recurrence","seq-two-term"],
 "等差数列":["seq-arithmetic","seq-growth"],
 "等比数列":["seq-geometric","seq-geometric-edge"],
 "数列求和与数列模型":["seq-partial-sum","seq-growth"]
}
LIMITS={
 "数列概念与递推":"仅有限项的一阶仿射和二阶和式递推；不能证明一般递推的无穷性质。",
 "等差数列":"固定实数首项、公差的前 24 项；未实现一般形式的代数证明。",
 "等比数列":"实数公比及有限项、q=1、0、−1 的特例；不自动证明无穷收敛。",
 "数列求和与数列模型":"有限部分和与两类固定数列的增长比较；不支持任意求和式与通用应用建模。"
}
def apply_coverage(rows,presets):
    known={p["id"]:p for p in presets}
    for row in rows:
        ids=EVIDENCE.get(row["concept"])
        if ids is None:continue
        if not all(x in known for x in ids):
            raise ValueError("v0.11课程证据缺少实际场景")
        row.update(available_presets=list(ids),status="INTERACTIVE_FOUNDATION",
             capability="已有具体受控数列实验场景（非完整教学）",
             capability_limits=LIMITS[row["concept"]],
             recommended_tool=known[ids[0]]["tool"])
    return rows
