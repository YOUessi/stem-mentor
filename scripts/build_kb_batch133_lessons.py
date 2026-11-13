#!/usr/bin/env python3
"""Six original rigorous TEACHER_ONLY lesson manuscripts linked to bounded source proposals."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as atoms
OUT=ROOT/"knowledge/editorial_review/kb_batch133_six_core_lessons.json"
MD=ROOT/"docs/evaluation/KB_BATCH133_SIX_DEEP_LESSONS.md"
# All explanations below are original authoring, not borrowed official syllabus text.
LESSONS={
"c_complement": {
 "formal_definition_or_theorem":"给定全集 U 与子集 A⊆U，A 相对于 U 的补集定义为 U\\A={x∈U | x∉A}。补集随 U 改变；若 A⊈U 则不能把 U\\A 直接当作通常的相对补集定义题。",
 "notation_and_domain":"U、A 是集合；x∈U 与 x∈A 为元素关系。'\\' 表示差集，∅为空集；选择有限全集时每个元素只计一次。",
 "applicability_and_hypotheses":"明确全集 U 且 A⊆U；进行幂集或Venn图运算时所有集合共用相同全集。",
 "reasoned_steps":[["定义谓词","对每个 x∈U 检验 x∈A 与否，此时 U\\A 收纳且仅收纳不属于 A 的 x。"],["论证互不相交","如果 x 同时属于 A 与 U\\A，则 x∈A 和 x∉A 矛盾，故交集为空。"],["论证覆盖全集","任意 x∈U 必满足 x∈A 或 x∉A，故 A∪(U\\A)=U。"],["提醒背景变化","当 U 改变，候选元素的范围就改变，补集一般随之改变。"]],
 "why_method_is_legal":"集合外延公理下，两集合元素谓词相同即相等；可逐个检测有限全集。",
 "nonexample_or_failure":"取 U={1,2,3}、A={1}，补集是{2,3}；不是实数全集的所有非1元素。",
 "typical_wrong_solution":"忘记题目给出的全集，直接写 A^c=R\\A。",
 "why_wrong_and_repair":"补集为相对概念；先写出 U，再从 U 中删去 A 的元素。",
 "teacher_examples":[["U={1,2,3,4,5,6}，A={2,4,6}，求 A 在 U 中的补集。","{1,3,5}",["确认 A⊆U。","从 U 中逐一删除2、4、6。","剩余元素是1、3、5。"]],["U={1,2,3,4}，A={2,3}，B={1,2}，求 (A∪B) 的补集。","{4}",["先求 A∪B={1,2,3}。","全集仍为 U。","U\\(A∪B)={4}。"]]],
 "student_hint_ladder":["先确定全集是什么。","只考虑全集中的元素，判断其是否落入目标集合。","对每一个未落入集合的全集元素做一次登记，仍不要直接给出答案。"],
 "near_transfer":"对 U={-2,-1,0,1,2} 与 A={-2,0,2} 比较 A^c 和 -A。",
 "far_transfer":"讨论某班学生选体育/音乐社团时，'未选体育社团'是否等于'选了音乐社团'，要求先确定全集与交叠情况。"
},
"c_quantifier_negation":{
 "formal_definition_or_theorem":"在固定论域 D 上，¬(∀x∈D,P(x)) 等价于 ∃x∈D,¬P(x)；¬(∃x∈D,P(x)) 等价于 ∀x∈D,¬P(x)。否定应同时交换量词并否定内部谓词。",
 "notation_and_domain":"D 为固定论域；P(x) 是在 D 中有确定真值的命题；∀ 为任意，∃ 为至少存在，¬ 为否定。",
 "applicability_and_hypotheses":"原命题的量词范围明确，且对每个被讨论对象 P(x) 有定义；若定义域变化则不是同一命题的否定。",
 "reasoned_steps":[["理解全称语义","∀x P(x) 为真要求没有任何反例。"],["否定全称","要使所有对象都满足P不成立，必须存在至少一个反例，即 ∃x ¬P(x)。"],["理解存在语义","∃x P(x) 为真只需有一个见证对象。"],["否定存在","若找不到任何见证，必有每个对象不满足P，即 ∀x ¬P(x)。"]],
 "why_method_is_legal":"这是量词的真假条件，不依赖于把'所有'口语化为'全部不'。",
 "nonexample_or_failure":"“不是所有实数x都满足x²>0”不能写作“所有实数x都满足x²≤0”，因为只需x=0为反例。",
 "typical_wrong_solution":"把 ¬∀x P(x) 写成 ∀x ¬P(x)；既保留全称量词又把每一对象都否定。",
 "why_wrong_and_repair":"否定全称要求一个反例，不要求全部对象都违反原命题。",
 "teacher_examples":[["写出命题“所有实数 x 都有 x²>0”的否定，并判断真假。","存在实数 x 使 x²≤0；真（取 x=0）。",["原论域是实数。","交换全称为存在，同时把>0否定为≤0。","选x=0给出有效见证。"]],["写出“存在实数 x 使 x²=-1”的否定，并判断真假。","所有实数 x 均满足 x²≠-1；真。",["交换存在为全称。","把等号否定为不等号。","实数平方非负，因此所有实数确实不等于-1。"]]],
 "student_hint_ladder":["先圈出量词与其论域。","想象反驳原命题最少需要一个对象还是全部对象。","交换∀与∃，并逐字否定量词后的数学关系。"],
 "near_transfer":"否定“对每个正整数n，n²≥n”，注意论域仍为正整数。",
 "far_transfer":"将“每位学生至少选过一种课程”写成含双重量词语句，再逐层写出否定。"
},
"c_quadratic_roots":{
 "formal_definition_or_theorem":"对实系数 a x²+b x+c=0 且 a≠0，令 Δ=b²−4ac：Δ>0时有两个不同实根，Δ=0时有一个二重实根，Δ<0时无实根；Δ≥0时实根为(-b±√Δ)/(2a)。",
 "notation_and_domain":"a,b,c∈R 且 a≠0；Δ是判别式；只在实数域讨论实根个数；二重根按不同实数根个数只计一次。",
 "applicability_and_hypotheses":"二次项系数a非零，√Δ只在Δ≥0时作为实数平方根，分母2a非零。",
 "reasoned_steps":[["配方","将等式乘4a并移项得 (2ax+b)²=b²−4ac=Δ。"],["判别正值","若Δ>0则正负两个平方根不同，得到两个实根。"],["判别零值","若Δ=0则 2ax+b=0 只有一个实根。"],["判别负值","实数平方非负，故Δ<0不可能成立；若a=0须先退化为线性或常值方程。"]],
 "why_method_is_legal":"等式变换中乘以4a在a≠0下可逆；平方根分支由Δ符号决定。",
 "nonexample_or_failure":"a=0,b=2,c=-4时为线性方程2x−4=0，不允许在求根公式中除以2a。",
 "typical_wrong_solution":"见到Δ=0就写两个不同实根；或者见到Δ<0仍写包含实数平方根的答案。",
 "why_wrong_and_repair":"实数二重根仅有一个不同根；先校验a≠0再判别Δ的符号。",
 "teacher_examples":[["求解2x²−3x−2=0并说明实根数。","x=2 或 x=-1/2；两个不同实根。",["a=2,b=-3,c=-2，Δ=9+16=25。","代入(-b±√Δ)/(2a)。","得到(3±5)/4分别为2和-1/2。"]],["求x²−4x+4=0并说明实根数。","x=2（重根），恰好一个不同实根。",["Δ=16−16=0。","代入求根公式得x=4/2=2。","原式为(x−2)²，验证重根。"]]],
 "student_hint_ladder":["先查二次项是否真的存在。","计算b²−4ac并先判断它的符号。","再选择使用平方根公式或退化方程的规则。"],
 "near_transfer":"参数方程 (m−1)x²+2x+1=0 何时有两个不同实根？必须分 m=1。",
 "far_transfer":"分析抛物线与水平线 y=k 的交点个数，并说明切点对应哪种判别式。"
},
"c_zero_theorem":{
 "formal_definition_or_theorem":"若 f:[a,b]→R 在[a,b]连续、a<b 且 f(a)f(b)<0，则至少存在 c∈(a,b) 使 f(c)=0。只保证存在，不自动保证唯一或二分法已收敛到精确零点。",
 "notation_and_domain":"a,b 为实数且a<b，c为内部零点；连续是整个闭区间上的条件；<0表示两端函数值严格异号。",
 "applicability_and_hypotheses":"闭区间连续、两端严格异号、端点函数值有定义；二分迭代每次保留异号区间。",
 "reasoned_steps":[["整理端点","不失一般性设 f(a)<0<f(b)。"],["使用介值性","闭区间连续函数会取得端点函数值之间的每个中间值。"],["选取零值","因为0介于f(a)和f(b)之间，存在c∈[a,b]使f(c)=0。"],["排除端点","端点值严格异号且非零，所以c∈(a,b)，但可能有多个零点。"]],
 "why_method_is_legal":"介值定理要求闭区间连续；二分每次使用连续子区间且由异号保留存在性。",
 "nonexample_or_failure":"f(x)在x<0时为-1、x≥0时为1，在[-1,1]端点异号但内部没有零点，因函数不连续。",
 "typical_wrong_solution":"看到f(a)f(b)>0就断言区间没有零点，或者端点异号就断言零点唯一。",
 "why_wrong_and_repair":"端点同号仍可能有偶数个零点；异号只保证至少一个，唯一性需额外单调性等条件。",
 "teacher_examples":[["f(x)=x³−x−1，在[1,2]中是否一定有零点？","有至少一个零点。",["多项式在闭区间连续。","f(1)=-1、f(2)=5，乘积为-5。","介值定理保证至少一个c∈(1,2)。"]],["用二分法对 f(x)=x²−2 在[1,2]进行前两次取中点，写出保留区间。","先保留[1,3/2]，再保留[5/4,3/2]。",["f(1)=-1，f(2)=2。","第一个中点3/2的函数值为1/4>0，保留左半区间。","第二个中点5/4的函数值为-7/16<0，保留右半区间。"]]],
 "student_hint_ladder":["确认函数是否在整个闭区间连续。","分别计算两个端点函数值的符号。","如果满足异号，只能提出存在性结论；不要直接推断唯一。"],
 "near_transfer":"f(x)=x²−1在[-2,2]端点同号，但区间内仍有两个零点。",
 "far_transfer":"讨论实际温度测量值在两个时刻一负一正时，何种连续性假设支持中间达到0°C。"
},
"sc_geom_progression":{
 "formal_definition_or_theorem":"若 a_k=a_1 q^(k-1)（k≥1），有限前n项和 S_n=Σ(k=1..n)a_1 q^(k-1)。q≠1时 S_n=a_1(1-q^n)/(1-q)，q=1时 S_n=n a_1。",
 "notation_and_domain":"n为正整数，a_1为实数，q为实数；对采用相邻项比值定义的等比数列，须额外要求每一相邻比值有定义；q=0的有限多项式恒等式不自动等同标准等比数列定义。",
 "applicability_and_hypotheses":"使用错位相减时每项有定义；只有在q≠1时才允许除以1-q；q=1单独计算。",
 "reasoned_steps":[["写有限和","S_n=a_1+a_1q+…+a_1 q^(n−1)。"],["乘以q","qS_n=a_1q+a_1q²+…+a_1 q^n。"],["相减并约去中间项","(1−q)S_n=a_1(1−q^n)。"],["分类讨论","q≠1时合法相除；q=1时n项全部等于a_1，故S_n=n a_1。"]],
 "why_method_is_legal":"有限项代数相加、相减合法，除法只在分母非零时合法。",
 "nonexample_or_failure":"用q=1代入(1-q^n)/(1-q)出现0/0；当q=0时有限幂级数代数式有意义，但若定义要求相邻项比值存在则不能直接称为该定义下的等比数列。",
 "typical_wrong_solution":"不分类直接使用S_n=a_1(1-q^n)/(1-q)并设置q=1。",
 "why_wrong_and_repair":"先检查是否可除以1−q；若q=1直接数项。",
 "teacher_examples":[["等比数列首项3，公比2，求前4项和。","45",["写3+6+12+24。","q=2非1。","用3(1−2⁴)/(1−2)=45。"]],["常数列各项均为5，求前6项和，并说明q=1情况。","30",["公比为1且首项非零。","每项都是5。","S_6=6×5=30。"]]],
 "student_hint_ladder":["明确求和项数n与首项、公比。","比较q与1，考虑是否允许除法。","尝试把整段求和乘以q，再与原求和相减。"],
 "near_transfer":"首项2、公比-1的数列求前7项和，并讨论奇偶n。",
 "far_transfer":"在固定等比增长模型中比较累计增长总量与最后一期单量，说明q接近1时数值计算方式为何需谨慎。"
},
"a_mean_value":{
 "formal_definition_or_theorem":"拉格朗日中值定理：若 a<b，f 在[a,b]连续且在(a,b)可导，则存在c∈(a,b)满足 f'(c)=(f(b)−f(a))/(b−a)。存在性不蕴涵c唯一。",
 "notation_and_domain":"a,b∈R且a<b；f:[a,b]→R；f'表示内部导数。对复合不等式应用需额外验证导数界。",
 "applicability_and_hypotheses":"完整闭区间连续、开区间可导及端点不同；不可导点跨越区间时不能直接使用。",
 "reasoned_steps":[["作割线辅助函数","令m=(f(b)−f(a))/(b−a)，g(x)=f(x)−m(x−a)。"],["验证Rolle端点相等","g(a)=f(a)，g(b)=f(b)−(f(b)−f(a))=f(a)。"],["证明Rolle基础条件","g连续且可导；极值定理保证g在闭区间取极值。若非恒定，则至少一个内部极值存在，费马必要条件给出g'(c)=0；恒定时任意内点可取。"],["回代导数","g'(c)=f'(c)−m=0，故f'(c)=m。"],["审核边界","绝对值在含0区间不可导；若只知一侧导数不够，不能使用本定理。"]],
 "why_method_is_legal":"减去线性函数不破坏连续或可导条件；Rolle定理在上述假设下使用，最终导数等式经可逆代数移项获得。",
 "nonexample_or_failure":"f(x)=|x|在[-1,1]连续但于0不可导，割线斜率0，区间内其余点导数为±1，不存在满足结论的c。",
 "typical_wrong_solution":"只检查端点存在就使用中值定理，或认为某个中点c=(a+b)/2必满足。",
 "why_wrong_and_repair":"必须验证全区间连续和内部可导；定理只给出至少一个内部点，未指定中点。",
 "teacher_examples":[["对f(x)=x²在[1,3]求满足中值定理结论的c。","c=2",["多项式连续可导。","割线斜率(9−1)/(3−1)=4。","f'(c)=2c=4，得c=2∈(1,3)。"]],["对f(x)=x³在[0,2]求满足中值定理结论的正c。","c=2/√3",["多项式满足连续可导。","割线斜率(8−0)/2=4。","3c²=4，取c=2/√3∈(0,2)。"]]],
 "student_hint_ladder":["检查闭区间连续与内部可导。","先算割线斜率，不要先猜c。","令f'(c)等于割线斜率，求候选点后核实落在开区间。"],
 "near_transfer":"将f(x)=ln x应用于[1,e]并写出c的表达式。",
 "far_transfer":"已知某段实际位移曲线在时间区间连续可导，解释为何存在某瞬时速度等于区间平均速度；测量突跳时为何不能直接断言。"
}
}
def require(ok,msg):
    if not ok:raise ValueError(msg)
def build():
    data=json.loads(atoms.OUT.read_text(encoding="utf-8"))
    atoms.validate(data)
    candidates={r["id"]:r for r in data["records"]}
    rows=[]
    for slug,fields in LESSONS.items():
        source=candidates["kb133-proposal-"+slug]
        x=dict(fields)
        x.update(id="kb133-deep-"+slug, candidate_id=source["id"],course_track=source["track"],
                 knowledge_type=source["knowledge_type"],source_line_lock=source["source_lock"],
                 source_pdf_sha256=source["source_pdf_sha256"],
                 version="2017-2020-editorial-batch133",teacher_review_status="REVIEW_PENDING",
                 teacher_review_evidence=None,teacher_solution_visibility="TEACHER_ONLY",
                 source_status="PROVISIONAL_PDFKIT_SOURCE_PROPOSAL_NOT_OFFICIAL_ATOM",
                 formal_proof_certified=False,free_student_step_verified=False,
                 student_authoritative=False)
        x["reasoned_steps"]=[{"step":s,"justification":j} for s,j in fields["reasoned_steps"]]
        x["teacher_examples"]=[{"question":q,"answer":a,"reasoned_solution":steps} for q,a,steps in fields["teacher_examples"]]
        rows.append(x)
    return rows
def validate(data):
    expected=set(LESSONS)
    require(isinstance(data,list) and len(data)==len(expected)==6,"six complete lessons required")
    require({r["id"].removeprefix("kb133-deep-") for r in data}==expected,"missing/extra IDs")
    index=json.loads(atoms.OUT.read_text())
    atoms.validate(index)
    candidate={r["id"]:r for r in index["records"]}
    for r in data:
        slug=r["id"].removeprefix("kb133-deep-")
        s=candidate["kb133-proposal-"+slug]
        require(r["candidate_id"]==s["id"] and r["source_line_lock"]==s["source_lock"] and
                r["course_track"]==s["track"] and r["knowledge_type"]==s["knowledge_type"],"source mismatch")
        require(r["source_pdf_sha256"]==atoms.SOURCE_SHA and
                r["teacher_review_status"]=="REVIEW_PENDING" and r["teacher_review_evidence"] is None and
                r["teacher_solution_visibility"]=="TEACHER_ONLY" and
                r["student_authoritative"] is False and r["formal_proof_certified"] is False and
                r["free_student_step_verified"] is False and
                r["source_status"]=="PROVISIONAL_PDFKIT_SOURCE_PROPOSAL_NOT_OFFICIAL_ATOM",
                "forged teacher/student approval")
        for k in ("formal_definition_or_theorem","notation_and_domain","applicability_and_hypotheses",
                  "why_method_is_legal","nonexample_or_failure","typical_wrong_solution","why_wrong_and_repair",
                  "near_transfer","far_transfer"):
            require(isinstance(r[k],str) and len(r[k])>=20,"missing substantial lesson field "+k)
        require(len(r["reasoned_steps"])>=3 and all(len(v["justification"])>=18 for v in r["reasoned_steps"]),"incomplete reasoning")
        require(len(r["student_hint_ladder"])==3 and all(len(v)>=9 for v in r["student_hint_ladder"]),"short hint ladder")
        require(len(r["teacher_examples"])==2 and all(len(z["reasoned_solution"])>=3 for z in r["teacher_examples"]),"incomplete examples")
        require(r["formal_definition_or_theorem"]==LESSONS[slug]["formal_definition_or_theorem"],"edited math without review")
    return True
def render(data):
    lines=["# Batch133 六份原创深度数学教师候审讲义","",
        "**全部为 REVIEW_PENDING / TEACHER_ONLY，非正式课标原子，未经教师签字及形式化证明。**",
        "来源只记录受保护 PDFKit 行哈希，不复制原课标文字。",""]
    for r in data:
        lines.extend([f"## {r['id']} · {r['course_track']} · {r['knowledge_type']}",
            "**定义/定理** "+r["formal_definition_or_theorem"],"**符号与域** "+r["notation_and_domain"],
            "**前提** "+r["applicability_and_hypotheses"],"**为何合法** "+r["why_method_is_legal"],""])
        for i,s in enumerate(r["reasoned_steps"],1):
            lines.append(f"{i}. **{s['step']}**：{s['justification']}")
        lines.extend(["","**反例** "+r["nonexample_or_failure"],
              "**典型错法** "+r["typical_wrong_solution"],"**错误修复** "+r["why_wrong_and_repair"],""])
        for i,e in enumerate(r["teacher_examples"],1):
            lines.extend([f"**教师例题{i}** {e['question']}","**教师答案** "+e["answer"]])
            lines.extend(f"  - {t}" for t in e["reasoned_solution"])
        lines.append("**学生分层提示（独立挑战时逐层释放，绝不拼接教师解答）**")
        lines.extend(f"  - {t}" for t in r["student_hint_ladder"])
        lines.extend(["**近迁移** "+r["near_transfer"],"**远迁移** "+r["far_transfer"],
            f"源锚: {r['candidate_id']} / {r['source_line_lock']['span_sha256']}",""])
    return "\n".join(lines).rstrip()+"\n"
def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    a=p.parse_args()
    if a.write:
        rows=build();validate(rows)
        OUT.write_text(atoms.stable_json(rows),encoding="utf-8")
        MD.write_text(render(rows),encoding="utf-8")
    else:
        rows=json.loads(OUT.read_text(encoding="utf-8"));validate(rows)
        require(MD.read_text(encoding="utf-8")==render(rows),"markdown drift")
    print("PASS",len(LESSONS),"deep teacher-only lessons,",sum(len(r['teacher_examples']) for r in rows),"teacher examples, 0 approval")
if __name__=="__main__":main()
