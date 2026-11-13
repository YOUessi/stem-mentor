#!/usr/bin/env python3
"""Eight ORIGINAL bounded course proposals. Teacher review is compulsory.

Do not call authoring, source hash, sample algebra or tests teacher approval.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch133_atomization as atoms
import build_kb_batch134_lessons as prior

OUT = ROOT / "knowledge/editorial_review/kb_batch135_eight_deep_lessons.json"
MD = ROOT / "docs/evaluation/KB_BATCH135_EIGHT_DEEP_LESSONS.md"
SAFE = ROOT / "knowledge/editorial_review/kb_batch135_student_safe_index.json"

# Original content, manually written. Proof obligations and worked examples are
# separated. A theorem proof is editorially reviewable, not formally certified.
L = {
"c_union_intersection": dict(
 formal="A∪B={x|x∈A或x∈B}，A∩B={x|x∈A且x∈B}。对同一全集内的A、B、C，有A∩(B∪C)=(A∩B)∪(A∩C)。",
 domain="A、B、C是同一讨论范围U中的集合；∪表示至少在一个集合中，∩表示同时属于；元素的重复不改变集合。",
 assumptions="集合成员资格明确；分配律在任意集合上成立，不要求互斥，不能把逻辑“或”当作异或。",
 steps=[("任取元素","令x属于A∩(B∪C)，则x∈A且x∈B∪C。"),
 ("展开并集条件","x∈B∪C等价于x∈B或x∈C，连同x∈A得(x∈A且x∈B)或(x∈A且x∈C)。"),
 ("证明左包含于右","上一步恰是x∈(A∩B)∪(A∩C)，因此左集合包含于右集合。"),
 ("逆向蕴含","从右集合成员出发反向用相同逻辑得到x∈A∩(B∪C)，两向包含故集合相等。")],
 legal="成员谓词的命题分配律及集合外延相等准则使证明合法，与集合基数无关。",
 failure="若A={1},B={1},C={1}，交集两个分支都含1；并集仍只有元素1，不能按1+1=2计算集合元素数。",
 wrong="把集合并集误作无重复检查的数目相加，或把“或”误当互斥导致交叠元素被删除。",
 repair="用任一元素x的属于关系而非集合大小证明恒等式，元素在集合中只出现一次。",
 examples=[("A={1,2,3},B={2,4},C={1,4}，求A∩(B∪C)。","{1,2}",["B∪C={1,2,4}。","与A交得到{1,2}。","检查右侧(A∩B)∪(A∩C)={2}∪{1}相同。"]),
 ("A={0,1},B={1,2},C={1,3}，求(A∩B)∪(A∩C)。","{1}",["A∩B={1}。","A∩C={1}。","并集去重后仍为{1}。"])],
 hints=["首先写出∩和∪各自的成员逻辑。","任取一个元素，展开两个括号，辨别且与或。","证明两个集合相等要证明正反两个方向的包含。"],
 near="对A={1,2}, B={2}, C=∅核对分配律。",
 far="设计学生同时报名两门社团的名单筛选，解释为何不能重复计数。"),
"c_quadratic_sign": dict(
 formal="当a≠0，p(x)=ax²+bx+c且判别式Δ>0、两实根r1<r2时，p(x)在根外与a同号、根间与a异号；Δ=0时除重根外与a同号；Δ<0时所有实数点与a同号。",
 domain="a,b,c,x∈R，a≠0；r1<r2是严格有序的实根；严格/非严格不等号需分别包含或排除零点。",
 assumptions="必须确认a非零、判别式符号，讨论Δ>0时方可引入两个严格有序实根。",
 steps=[("处理两个实根","Δ>0时按因式定理写p(x)=a(x-r1)(x-r2)。"),
 ("根外符号","当x<r1时两个括号均负，当x>r2时均正，乘积为正，故p与a同号。"),
 ("根间符号","r1<x<r2时两括号一正一负，乘积为负，故p与a异号。"),
 ("判别式退化","Δ=0时p=a(x-r)²；Δ<0时配方p=a[(x+b/(2a))²+(-Δ)/(4a²)]，括号严格为正。")],
 legal="多项式实数因式分解和平方非负性保留符号信息；零点处p=0不能称严格正或负。",
 failure="a=0时实际是线性或常值函数；对x²+1因Δ<0而硬画两个实根区间是非法操作。",
 wrong="看到两个解就总写“两根之间小于0”，忘记a<0时符号反转；或者对≥0漏掉根。",
 repair="先确定a的符号及Δ，列三个区间，并单独核对零点是否包含。",
 examples=[("求解2x²−3x−2>0。","x<−1/2或x>2。",["a=2>0且Δ=25>0。","因式分解为(2x+1)(x−2)，实根−1/2与2。","根外同a号且为严格正，故不含根。"]),
 ("求解x²+1≤0。","无实数解。",["a=1>0，Δ=−4<0。","对任意实数x均有x²+1>0。","≤0无解，不能虚构复根区间。"])],
 hints=["先检查二次项系数和判别式。","若有两根，按从小到大排列并画符号区间。","最后检查题目是严格不等式还是带等号。"],
 near="分类求(m−1)x²−1<0，需要先考虑m=1。",
 far="用抛物线与横轴位置解释利润模型何时为正并识别参数退化。"),
"c_period": dict(
 formal="函数f:R→R的正数T若满足对所有x∈R都有f(x+T)=f(x)，则T为正周期；若所有正周期中存在最小者，称为最小正周期。常数函数有任意正周期而无最小正周期。",
 domain="函数的定义域取全体实数以避免平移定义域歧义；周期T>0；若一般定义域D需另行要求对平移闭合。",
 assumptions="必须检查对每一个x成立，不能仅检查若干采样点；不能把一个已发现周期自动认定最小。",
 steps=[("固定周期定义","任意x都应有f(x+T)=f(x)，此处T不能为0。"),
 ("验证正弦周期","设f(x)=sin(2x)，由sin(2x+2π)=sin(2x)，T=π确为周期。"),
 ("证明正弦最小正周期","若任意x都满足sin(2x+2T)=sin(2x)，则将x=0和x=π/4分别代入，得sin2T=0且cos2T=1，因此2T是2π的整数倍。"),
 ("讨论常数函数","若f恒为c，每个T>0都满足定义，但任何正T都有更小的T/2，故不存在最小正周期。")],
 legal="正弦加法与周期定义支持全称恒等；对特定函数证明最小值需排除更小的正周期。",
 failure="f(x)=5对任意T>0都周期，却没有最小正周期；只观察两个图像波峰相隔T也不足以证明全称周期。",
 wrong="将0当作最小正周期，或在找到任一正周期后不论大小直接称基本周期。",
 repair="先用全称恒等式验证一个正周期，再单独证明不存在更小正周期。",
 examples=[("求f(x)=sin(2x)的最小正周期。","π。",["sin(2(x+π))=sin(2x+2π)=sin(2x)。","如证明步骤所示，所有正周期均为π的正整数倍。","故最小正周期为π。"]),
 ("g(x)=7有没有最小正周期？","没有。",["每个T>0均有g(x+T)=7=g(x)。","若T为周期，则T/2也为更小的正周期。","不存在最小的正T。"])],
 hints=["把周期写成对所有x成立的等式。","寻找正周期后还要排除更小周期。","考虑常数函数会不会存在最小正周期。"],
 near="求cos(3x)的最小正周期，必须证明任何更小的正数均不满足全称周期定义。",
 far="讨论按固定时间采样可能让不同真实周期信号产生相同观测的混叠风险。"),
"c_tangent_domain": dict(
 formal="对实角x，当cosx≠0时tanx=sinx/cosx。其实数定义域是R去掉全部π/2+kπ(k∈Z)，且对所有定义点tan(x+π)=tanx。",
 domain="x为弧度，k∈Z；cosx=0时tanx不定义；每个合法点平移π后仍合法。",
 assumptions="在求比值和约分之前严格检查cosx非零，绝不将无定义点当作无穷大实值。",
 steps=[("定义正切","tanx是正弦除以余弦，商有定义必须要求cosx≠0。"),
 ("识别零点","单位圆给出cosx=0当且仅当x=π/2+kπ，k为整数。"),
 ("检查平移","sin(x+π)=−sinx且cos(x+π)=−cosx；二者同时变号，商相等。"),
 ("检查合法性","若cosx≠0则cos(x+π)=−cosx≠0，故等式两边都有定义。")],
 legal="正切为非零分母的实数商，且三角函数平移恒等式均成立。",
 failure="x=π/2时分母cosx=0，tanx不是实数，不能把它写成tanx=∞并在实数域计算。",
 wrong="写tanx=sinx/cosx后无条件把cosx约去，在x=π/2仍声称计算成立。",
 repair="先排除x=π/2+kπ，再进行商与周期变换；使用弧度单位。",
 examples=[("求tan(π/4)与tan(5π/4)。","两者都为1。",["cos(π/4)=√2/2不为零。","tan(π/4)=1。","5π/4=π/4+π，因此正切仍为1。"]),
 ("tan(π/2)在实数域有什么值？","无定义。",["sin(π/2)=1而cos(π/2)=0。","正切所需的分母为零。","因此不能赋予实数值。"])],
 hints=["写出正切的商定义。","分母等于零时能否计算？","用正余弦的π平移变号关系验证周期。"],
 near="写出tan(3x)在[0,2π]内的全部无定义点。",
 far="在运动控制角度传感中使用tan表示斜率时，为什么垂直方向要单独处理？"),
"sc_arith_progression":dict(
 formal="等差数列满足a_{n+1}−a_n=d常数(n≥1)，通项a_n=a_1+(n−1)d；前n项和S_n=n(a_1+a_n)/2=n[2a_1+(n−1)d]/2。",
 domain="n为正整数，a_1、d为实数；有限项和无穷项求和不同，不得把S_n延展为无穷和。",
 assumptions="所有相邻项差均相同，且从n=1开始计数；若从0起需另改索引。",
 steps=[("通项推导","把n−1个相邻差a_{k+1}−a_k=d相加，中间项消去得到a_n−a_1=(n−1)d。"),
 ("顺序写和","S_n=a_1+a_2+…+a_n。"),
 ("逆序配对","S_n=a_n+a_{n−1}+…+a_1；逐列相加每列均为a_1+a_n。"),
 ("除以正数","于是2S_n=n(a_1+a_n)，得到S_n=n(a_1+a_n)/2，并代入通项。")],
 legal="差分望远镜求和和有限配对对所有正整数n合法，包含n=1，无需假设d正。",
 failure="1,2,4的相邻差为1和2，不是等差数列；不能套用上面的通项/求和结论。",
 wrong="把项数n混同末项编号n−1，或者对不恒定的相邻差直接乘平均数。",
 repair="先至少证明相邻差恒定，再写首项、末项和n个项的计数。",
 examples=[("等差数列首项3、公差2，求前5项和。","35。",["末项a5=3+4×2=11。","前5项为3,5,7,9,11。","S5=5(3+11)/2=35。"]),
 ("首项10、公差−3，求前5项和。","20。",["a5=10−12=−2。","逆序配对的每对和为10+(−2)=8。","S5=5×8/2=20。"])],
 hints=["先核对相邻两项之差是否为同一个常数。","写出a1、d、项数n，并找末项。","把同一和正写一次反写一次进行配对。"],
 near="若a3=7,a8=22，求等差数列公差与前8项和。",
 far="固定每秒增加相同距离的理想线性运动模型如何累计8个离散时段的位置值？"),
"sc_extreme_point": dict(
 formal="若f在闭区间[a,b]连续，则一定取得全局最大最小值；要找最值须比较端点、区间内导数为零点以及内点不可导点。内点可导极值点有f'=0只是必要条件而非充分条件。",
 domain="实函数f:[a,b]→R连续，a<b；可导性允许在有限候选点失败；候选集合列出后必须比较函数值。",
 assumptions="极值点的费马必要条件需该点在区间内部且可导；最值比较需要完整处理所有临界点及端点。",
 steps=[("确认存在性","连续函数在紧闭区间上由极值定理取得最大最小值。"),
 ("内点分类","若内点c有局部极值且f在c可导，则费马定理给出f'(c)=0；不可导点需另检。"),
 ("覆盖端点","全局极值也可在a或b取得，端点不要求双侧导数等于0。"),
 ("比较函数值","在所有候选处实际代入并比较函数值；f'=0本身并不能证明取得极值。")],
 legal="闭区间连续保证最值存在；费马定理只提供内点可导极值的必要候选条件。",
 failure="f(x)=x³在[-1,1]中f'(0)=0，0不是极值；f(x)=|x|在0处取得最小值却不可导。",
 wrong="只解f'(x)=0并选取其中一点当全局最值，遗漏端点和不可导尖点。",
 repair="先确认连续区间，列出导数为零、导数不存在的内点以及两个端点，逐项比较。",
 examples=[("求|x|在[-2,3]上的全局最大和最小值。","最小0、最大3。",["函数在闭区间连续。","内点x=0不可导，端点为−2、3。","值为0,2,3，因此最小0最大3。"]),
 ("求f=x³−3x在[-2,2]的最大最小值。","最大2、最小−2。",["f'=3x²−3，在内部x=±1为0。","计算f(−2)=−2,f(−1)=2,f(1)=−2,f(2)=2。","比较得最大2、最小−2。"])],
 hints=["先确认是否为闭区间连续函数。","端点与不可导点不能被求导零点筛掉。","在全部候选处比较函数值而不是只看导数。"],
 near="求f=x²在[-3,1]上的最大最小值，说明为何端点值也必须参与最终比较。",
 far="有限行程的能耗曲线存在控制饱和点时，为什么不能只搜索光滑驻点？"),
"sc_space_projection":dict(
 formal="在欧氏内积空间中，若u≠0，v在u方向的正交投影为proj_u(v)=(v·u)/(u·u)u；残差v−proj_u(v)与u正交。",
 domain="u,v为空间实向量（二维或三维均可）；点积为欧氏点积；u·u>0当且仅当u≠0。",
 assumptions="必须指定正交内积且投影轴向量非零；投影是向量，标量投影不是同一个对象。",
 steps=[("设候选投影","设沿u的投影为pu，其中p为待求实数。"),
 ("施加正交条件","要求残差v−pu与u点积为零，得到(v−pu)·u=0。"),
 ("解出系数","由v·u−p(u·u)=0且u·u>0，故p=(v·u)/(u·u)。"),
 ("说明唯一性","非零u使p唯一，代回验证残差与u正交。")],
 legal="投影轴非零时u·u严格正，可合法除法；由欧氏点积的线性性质得到唯一系数。",
 failure="u=0时公式分母为0，不能定义朝零向量的方向性正交投影。",
 wrong="把(v·u)u当投影忘记除以u·u，只有u为单位向量时才碰巧正确。",
 repair="首先检查u≠0；使用投影系数前写出正交条件，明确归一化分母。",
 examples=[("v=(3,4,0),u=(1,0,0)，求投影。","(3,0,0)。",["v·u=3，u·u=1。","系数p=3。","投影pu=(3,0,0)，残差(0,4,0)与u垂直。"]),
 ("v=(2,2,1),u=(1,1,0)，求投影。","(2,2,0)。",["v·u=4，u·u=2。","系数p=2。","投影为(2,2,0)，残差(0,0,1)点积u=0。"])],
 hints=["投影向量一定是u的标量倍数。","令残差与u点积为零。","解标量系数时检查u·u是否非零。"],
 near="将v=(1,2,3)投影到u=(0,0,2)方向并与投影到单位向量比较。",
 far="机器人观测向量在一个非单位传感器朝向上提取分量时为什么需要归一化？"),
"a_limits_quotient": dict(
 formal="若实数数列a_n→a，b_n→b且b≠0，则b_n最终非零，且a_n/b_n→a/b。不能删除极限分母b≠0的条件。",
 domain="a_n,b_n为充分大n时定义的实数数列，a,b为有限实数；b≠0且n为正整数。",
 assumptions="两个数列都收敛到有限值，分母数列的极限b非零；早期有限项可能为0但极限只需尾部商有定义。",
 steps=[("由极限保护分母","取ε=|b|/2，存在N1使n≥N1时|b_n−b|<|b|/2，故|b_n|>|b|/2>0。"),
 ("计算代数差","a_n/b_n−a/b = [b(a_n−a)−a(b_n−b)]/(b b_n)，这只在尾部合法。"),
 ("建立估计","对n≥N1，由三角不等式得到绝对误差≤(2/|b|)|a_n−a|+(2|a|/|b|²)|b_n−b|。"),
 ("完成全称ε证明","任给ε>0，分别选取两个收敛数列的尾阈值，使两个非负项各小于ε/2；取三个阈值最大值即得目标。")],
 legal="尾部非零界使商的代数变形与误差估计合法，两个收敛误差分别趋零。",
 failure="a_n=1、b_n=1/n均收敛，但b=0时a_n/b_n=n发散，商法则不能使用。",
 wrong="把1/lim b_n在lim b_n=0时当作无限大的数并继续当成有限极限运算。",
 repair="先验证分母极限非零，再证明最终分母非零，并给出误差估计。",
 examples=[("求a_n=(2+1/n)/(1−1/(2n))的极限。","2。",["分子趋于2，分母趋于1≠0。","对所有正整数n，分母≥1/2>0。","由商法则极限为2/1=2。"]),
 ("求a_n=(1+1/n)/(3+2/n)的极限。","1/3。",["分子趋于1。","分母趋于3≠0，所有正整数n分母为正。","商法则得1/3。"])],
 hints=["分别计算分子与分母的极限。","分母的极限可以为零吗？","若不为零，先解释为什么分母最终也不为零。"],
 near="讨论(3+1/n)/(n/(n+1))的极限并写明分母条件。",
 far="若分式模型的校准分母趋于0，解释为何可能放大噪声且商极限法则失效。")
}

def require(cond, message):
    if not cond:
        raise ValueError(message)

def build():
    inventory=json.loads(atoms.OUT.read_text(encoding="utf-8"))
    atoms.validate(inventory)
    records={r["id"]:r for r in inventory["records"]}
    old={r["source_candidate_id"] for r in prior.build()}
    rows=[]
    for slug, draft in L.items():
        s=records["kb133-proposal-"+slug]
        require(s["id"] not in old, "duplicate original manuscript "+slug)
        rows.append(dict(
            id="kb135-deep-"+slug,source_candidate_id=s["id"],course_track=s["track"],
            knowledge_type=s["knowledge_type"],source_span_sha256=s["source_lock"]["span_sha256"],
            source_pdf_sha256=s["source_pdf_sha256"],
            standard_version="2017-2020-editorial-bounded",
            formal_definition_or_theorem=draft["formal"],
            notation_and_domain=draft["domain"],
            applicability_and_hypotheses=draft["assumptions"],
            reasoned_steps=[{"step":a,"justification":b} for a,b in draft["steps"]],
            why_method_is_legal=draft["legal"],
            nonexample_or_failure=draft["failure"],
            typical_wrong_solution=draft["wrong"],why_wrong_and_repair=draft["repair"],
            teacher_examples=[{"question":q,"answer":a,"reasoned_solution":steps}
                              for q,a,steps in draft["examples"]],
            student_hint_ladder=draft["hints"],near_transfer=draft["near"],
            far_transfer=draft["far"],teacher_review_status="REVIEW_PENDING",
            teacher_review_evidence=None,teacher_solution_visibility="TEACHER_ONLY",
            source_status="PROVISIONAL_PDFKIT_SOURCE_PROPOSAL_NOT_OFFICIAL_ATOM",
            formal_proof_certified=False,free_student_step_verified=False,
            student_authoritative=False))
    return rows

def validate(rows):
    require(rows==build(),"authoring drift, wrong source, or unapproved publication")
    require(len(rows)==8 and len({r["id"] for r in rows})==8,"lesson completeness")
    for row in rows:
        require(len(row["reasoned_steps"])>=4 and len(row["teacher_examples"])==2
                and len(row["student_hint_ladder"])==3,"missing proof/examples/hints")
        require(all(len(x["reasoned_solution"])>=3 for x in row["teacher_examples"]),"shallow example")
        require(all(len(str(row[k]))>=24 for k in ("formal_definition_or_theorem",
            "notation_and_domain","applicability_and_hypotheses","why_method_is_legal",
            "nonexample_or_failure","typical_wrong_solution","why_wrong_and_repair",
            "near_transfer","far_transfer")),"shallow field")
        require(row["teacher_review_status"]=="REVIEW_PENDING" and
            row["teacher_review_evidence"] is None and
            row["teacher_solution_visibility"]=="TEACHER_ONLY" and
            not row["formal_proof_certified"] and not row["free_student_step_verified"]
            and not row["student_authoritative"],"forged approval")
    return True

def safe_export(rows):
    validate(rows)
    return {"status":"NO_APPROVED_MATERIAL","publishable_count":0,
            "items":[],"teacher_solution_excluded":True}

def render(rows):
    text=["# Batch135｜8份跨学科原创数学讲义（教师候审）","",
          "**仅TEACHER_ONLY / REVIEW_PENDING；来源课标候选非已审核官方原子。示例符号核查不等于一般定理形式证明。**",""]
    for row in rows:
        text.extend(["## "+row["id"]+" · "+row["course_track"],
            "**陈述**："+row["formal_definition_or_theorem"],
            "**记号与论域**："+row["notation_and_domain"],
            "**适用前提**："+row["applicability_and_hypotheses"],""])
        text.extend(f"{i}. **{x['step']}**：{x['justification']}"
                    for i,x in enumerate(row["reasoned_steps"],1))
        text.extend(["","**合法性**："+row["why_method_is_legal"],
          "**边界反例**："+row["nonexample_or_failure"],
          "**典型错解**："+row["typical_wrong_solution"],
          "**错误原因与修复**："+row["why_wrong_and_repair"],""])
        for i,e in enumerate(row["teacher_examples"],1):
            text.extend([f"**教师例题{i}**："+e["question"],"**答案**："+e["answer"]])
            text.extend("- "+x for x in e["reasoned_solution"])
        text.append("**三级学生提示（与解答严格隔离）**")
        text.extend("- "+x for x in row["student_hint_ladder"])
        text.extend(["**近迁移**："+row["near_transfer"],
                     "**远迁移**："+row["far_transfer"],
                     "**来源摘要**："+row["source_span_sha256"],""])
    return "\n".join(text).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser()
    a=p.add_mutually_exclusive_group(required=True)
    a.add_argument("--write",action="store_true")
    a.add_argument("--check",action="store_true")
    z=p.parse_args()
    if z.write:
        rows=build();validate(rows)
        OUT.write_text(atoms.stable_json(rows),encoding="utf-8")
        MD.write_text(render(rows),encoding="utf-8")
        SAFE.write_text(atoms.stable_json(safe_export(rows)),encoding="utf-8")
    else:
        rows=json.loads(OUT.read_text(encoding="utf-8"))
        validate(rows)
        require(MD.read_text(encoding="utf-8")==render(rows),"markdown content drift")
        require(json.loads(SAFE.read_text(encoding="utf-8"))==safe_export(rows),"student leak")
    print("PASS Batch135 eight original teacher-only mathematical manuscripts")
if __name__=="__main__":
    main()
