#!/usr/bin/env python3
"""Batch137 seven original bounded review manuscripts; no certified syllabus or teacher approval."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as atoms
import build_kb_batch136_lessons as base

OUT=ROOT/"knowledge/editorial_review/kb_batch137_seven_deep_lessons.json"
MD=ROOT/"docs/evaluation/KB_BATCH137_SEVEN_DEEP_LESSONS.md"
SAFE=ROOT/"knowledge/editorial_review/kb_batch137_student_safe_index.json"
A={}
def add(slug,formal,domain,assumptions,steps,legal,failure,wrong,repair,examples,hints,near,far):
    if slug in A:raise ValueError("duplicate authoring slug")
    A[slug]=dict(formal=formal,domain=domain,assumptions=assumptions,steps=steps,legal=legal,
                 failure=failure,wrong=wrong,repair=repair,examples=examples,hints=hints,near=near,far=far)

add("sc_sequence_model",
"数列可以视为定义在有限指标集{1,…,N}或正整数集（必要时从指定n₀起）的函数n↦a_n；通项描述取值，递推关系还必须给出足够初值才能唯一确定数列。",
"指标n属于明确给出的有限或无限整数指标集，a_n取实数；从n=0开始须单独标明。递推初值、定义域与通项公式不应混同。",
"作为函数，每个合法指标恰有一项；递推形式需要检验初值和后续每一步是否有定义且唯一。",
["确定指标集合N+与每个n所对应的项a_n，这满足函数的单值性。",
 "通项a_n=2n+1可直接求任意n的项，前3项依次为3、5、7。",
 "若给出a_1=3及a_{n+1}=a_n+2，对每个n已有唯一后继，数学归纳可逐项确定数列。",
 "单有a_{n+1}=a_n+2而无初值时，a_n=2n+c有任意常数c，故未唯一确定一条数列。"],
"数列的合法性来自函数定义；递推存在唯一性需由指定初值及确定性的递推规则支撑。",
"把a_{n+1}=a_n+2当作唯一数列却不提供初值，实际产生无限多条不同数列。",
"从几个观察项3,5,7就断定所有后续项必须等差递增2，有限样本不能确定唯一通项。",
"区分观察到的有限项与经过定义的生成规则；明确起始下标、初值和递推合法性。",
[("a_1=4,a_{n+1}=a_n+3，求前四项。","4、7、10、13。",["初值确定a_1=4。","连续三次使用递推每次加3。","得到4、7、10、13。"]),
 ("a_n=n(n+1)，求a_1,a_2,a_3。","2、6、12。",["对每个正整数直接代入通项。","n=1,2,3分别得2,6,12。","这里不需要附加递推初值。"])],
["先写明n从哪个整数开始。","给通项就代入；给递推先确认初值。","从有限前几项不能逻辑确定唯一的无穷数列。"],
"给出a_1=1,a_{n+1}=2a_n并求第五项，讨论若缺失a_1会如何。",
"把每日观测数据当成无穷数列建模，说明测量样本和数学递推规律为何不同。")

add("sc_induction_optional",
"数学归纳法：对每个正整数n的命题P(n)，若P(1)为真且对任意k≥1都有P(k)⇒P(k+1)，则∀n≥1，P(n)成立。",
"n,k∈N+；归纳起点可改为n_0，但需要覆盖实际命题指标域的全部整数。",
"必须同时证明起点、任意k的归纳蕴含；归纳假设只允许使用P(k)及题设，不可先假定P(k+1)。",
["先代入n=1核验基例，此处任何缺失都会破坏整条归纳链。",
 "任取k≥1并暂时假设P(k)成立，声明接下来要证明P(k+1)。",
 "例如求和S_k=k(k+1)/2，S_{k+1}=S_k+(k+1)=(k+1)(k+2)/2。",
 "基例和任意后继蕴含共同覆盖全部正整数，因此所声明的求和公式成立。"],
"归纳原理是正整数上的证明规则；归纳假设只保证当前k，不代表对未来项的无依据假定。",
"只证明n=2起且覆盖k≥2，便无法声称n=1也成立；起点错误不能靠后继步骤修复。",
"写出“假设对所有n都对，因此k+1对”作为递推步骤，这是循环论证。",
"核对基例，再写任意k的独立代数桥梁；避免把待证结论代入假设。",
[("证明1+2+⋯+n=n(n+1)/2。","对全部n≥1成立。",["基例n=1时两边为1。","假设到k的和为k(k+1)/2。","加上k+1后化简得(k+1)(k+2)/2。"]),
 ("证明2+4+⋯+2n=n(n+1)。","对全部n≥1成立。",["基例2=1×2。","假设前k项和为k(k+1)。","加2(k+1)得(k+1)(k+2)。"])],
["先检查起始整数是否被题目覆盖。","归纳假设只写P(k)而非待证P(k+1)。","把第k+1项加入并将式子变成n=k+1版本。"],
"证明前n个奇数之和为n²，比较基例与递推桥梁。",
"在递归程序正确性证明中，区分终止条件与递归保持的不变式。")

add("sc_derivative_rules",
"若f,g在x处均可导，则(f±g)'=f'±g'，(fg)'=f'g+fg'；若g(x)≠0，则(f/g)'=(f'g−fg')/g²；复合函数在内外相应点可导时满足链式法则。",
"函数定义在包含x邻域的实区间；f,g于x可导；商法则需g(x)≠0；链式法则需内函数g在x、外函数f在g(x)可导。",
"不能在分母为0处套商法则；绝对值尖点不一定可导；复合函数求导必须在外函数正确的输入点取值。",
["乘积增量展开f(x+h)g(x+h)−f(x)g(x)，添减f(x+h)g(x)，再除以h。",
 "因可导蕴含连续，h→0时f(x+h)→f(x)，从而得到乘积公式f'g+fg'。",
 "商法则先写f/g=f·(1/g)，利用g(x)≠0与倒数增量得到(1/g)'=−g'/g²。",
 "令u=g(x+h)−g(x)=g'(x)h+o(h)；外函数的可导性给出f(g(x)+u)−f(g(x))=f'(g(x))u+u·r(u)，且r(u)→0（定义r(0)=0）。除以h取极限即得链式法则，即使偶有u=0也成立。"],
"每条运算律分别来源于差商极限和可导连续性，且商与复合的前提必须分别核对。",
"g(x)=x，f(x)=1，x=0处1/x无定义，不能将公式−1/x²当作原点导数。",
"把(x²·x³)'误写为2x·3x²，或把sin(x²)的导数漏掉2x因子。",
"先明确运算结构，再核对每个因子可导、分母是否为零和链式法则的内层导数。",
[("求y=x²(x+1)的导函数。","3x²+2x。",["两因子在实数上可导。","乘积法则给2x(x+1)+x²。","化简得3x²+2x。"]),
 ("求y=(x²+1)/(x+1)在x≠−1时的导数。","(x²+2x−1)/(x+1)²。",["在x≠−1时分母不为零。","商法则得[2x(x+1)−(x²+1)]/(x+1)²。","整理分子得到x²+2x−1。"])],
["辨认求导对象是和、积、商还是复合。","列出各组成函数可导和非零分母条件。","先按规则展开，再进行代数化简和反代核查。"],
"计算(x²+1)sin x的导数并指出各项由哪条运算律产生。",
"讨论瞬时增长率模型中观测量为两个函数的比值时，分母接近零对误差有何影响。")

add("sc_space_basis",
"若u,v,w是三维实向量空间中线性无关的三个向量，则任意p∈R³存在唯一实数a,b,c使p=au+bv+cw；反之唯一展开性质意味着三向量构成基。",
"u,v,w,p∈R³；三向量线性无关等价于列矩阵M=[u v w]行列式非零。",
"必须有三个线性无关的向量；共面、重复或零向量均不能保证对任意三维向量唯一展开。",
["组成3×3矩阵M=[u v w]，线性无关等价于核M仅含零向量。",
 "在三维方阵情形核为零意味着det M≠0，故M可逆。",
 "对任意p，取(a,b,c)^T=M⁻¹p，得到展开的存在性。",
 "若两组系数均表示p，两式相减产生Mδ=0；核为零推出δ=0，故系数唯一。"],
"可逆矩阵等价刻画存在唯一展开；定理适用于三维向量且严格要求三向量线性无关。",
"u=(1,0,0),v=(0,1,0),w=(1,1,0)共面，不能表示p=(0,0,1)。",
"看到三个向量就称它们是基，忽略行列式为零以及不能张成全部R³的可能。",
"构造列矩阵并检查秩或行列式；对给定向量解线性方程组并检查解的唯一性。",
[("标准基e1,e2,e3表示p=(2,−1,3)。","p=2e1−e2+3e3。",["三列组成单位阵，行列式为1。","求解线性系统得到系数2、−1、3。","各坐标相加还原p。"]),
 ("u=(1,0,0),v=(0,2,0),w=(0,0,3)，展开p=(1,4,6)。","p=u+2v+2w。",["矩阵行列式6≠0。","逐坐标得a=1,2b=4,3c=6。","故系数唯一为1、2、2。"])],
["先判断所讨论空间是否为三维。","把向量放入矩阵列并检验det是否为0。","求系数后反代检查是否确实得到目标向量。"],
"取u=(1,1,0),v=(0,1,1),w=(1,0,1)求p=(2,2,2)的唯一展开。",
"机器人三维运动控制中三个执行方向线性相关时，为什么无法独立控制所有坐标方向？")

add("a_monotone_convergence",
"实数数列单调有界收敛定理：若a_{n+1}≥a_n且存在实数M使a_n≤M对所有n成立，则a_n收敛到sup{a_n}；单调递减且有下界时收敛到inf{a_n}。",
"n∈N+，a_n∈R；“有界”针对整个序列；上确界存在依赖实数完备性，不等于有限验证。",
"上升数列需要上界，下降数列需要下界；不应把单调本身误当作收敛的充分条件。",
["设集合S={a_n:n≥1}非空且有上界，实数完备性保证L=sup S存在且为有限实数。",
 "任给ε>0，由上确界性质存在N使a_N>L−ε，否则L−ε也是上界，矛盾。",
 "由非递减性，n≥N时a_N≤a_n≤L，于是0≤L−a_n<ε。",
 "根据极限定义a_n→L；非递增有下界情形对−a_n应用上述结论得到下确界。"],
"证明依赖序列单调、有界和实数的上确界性质；有限项采样无法证明全局有界。",
"a_n=n严格递增却无上界，因而不收敛到有限实数。",
"用“越往后变化越小”代替收敛证明，或只看到前100项被限制就断言有界。",
"分别证明每一步单调性与全体项上界，最后用上确界的ε论证收敛。",
[("a_n=1−1/n是否收敛？求极限。","收敛到1。",["n≥1时1/(n+1)<1/n，故a_n递增。","a_n<1给出全局上界1。","由定理收敛，且|a_n−1|=1/n→0。"]),
 ("a_n=1/(n+1)是否收敛？求极限。","收敛到0。",["a_n正且逐项递减。","0是下界。","又1/(n+1)→0，与单调收敛定理一致。"])],
["先确认数列是递增还是递减。","递增须找上界，递减须找下界。","将上界与极限值区分，并写出ε证明关键步骤。"],
"考察a_n=∑_{k=1}^n 1/2^k并给出单调上界和极限。",
"把逐轮更新的损失值建模为单调有界数列，解释数学收敛与到达全局最优的区别。")

add("a_function_limit",
"极限lim_{x→a}f(x)=L表示对任意ε>0存在δ>0，使得0<|x−a|<δ且x属于定义域时均有|f(x)−L|<ε；a应是定义域的聚点。",
"f:D→R，a为D的聚点，L∈R；x→a不要求f(a)本身有定义，且必须排除x=a。",
"若左右都有定义域点趋近a，双侧极限存在当且仅当左右极限存在且相等；单侧定义域需采用相对D的极限。",
["先固定任意ε>0，要求构造只与ε有关的δ>0。",
 "若f(x)=2x+1，取δ=ε/2，则0<|x−a|<δ保证|f(x)−(2a+1)|=2|x−a|<ε。",
 "对在左右两侧均可趋近的点a，双侧δ条件同时约束左右邻域。",
 "例如f(x)=x/|x|在a=0左右极限为−1与1，不相等，故双侧极限不存在。"],
"ε-δ定义明确了所有足够近且属于定义域的点都必须接近L，单一序列样本不是充分证明。",
"函数f(x)=x/|x|在0处没有双侧极限；仅从右侧取样会错误得到1。",
"把f(a)直接当作极限，或仅取x靠近a的一侧即宣布双侧极限。",
"先核对a为聚点、0<|x−a|和定义域，再分别处理可能的左右邻域。",
[("求lim_{x→2}(3x−1)。","5。",["差值|3x−1−5|=3|x−2|。","任给ε取δ=ε/3。","由ε-δ条件得极限为5。"]),
 ("求lim_{x→0}x²。","0。",["|x²−0|=|x|²。","任给ε取δ=√ε。","0<|x|<δ时差值<ε。"])],
["明确自变量趋近的点是否为定义域聚点。","用|f(x)−L|与|x−a|建立上界。","先有ε再构造δ，若双侧邻域存在须同时检查。"],
"证明lim_{x→1}(x²+2)=3，给出可行的δ与ε关系。",
"对传感器标定函数解释为何单侧观测不足以证明双侧连续行为。")

add("a_continuity",
"函数f在定义域内聚点a连续，当且仅当lim_{x→a,x∈D}f(x)=f(a)；对双侧定义域点，左右极限都要等于f(a)。",
"f:D→R且a∈D为聚点；若a仅有单侧定义域邻域，连续性按相对定义域理解；孤立点按拓扑定义自动连续。",
"f(a)必须有定义，且相应极限存在并与函数值相等；双侧连续不能只验证某一侧。",
["在a处连续的ε-δ条件为：对每个ε>0存在δ>0，x∈D且|x−a|<δ时|f(x)−f(a)|<ε。",
 "若a为D的聚点，此条件与函数极限等于f(a)的定义等价，x=a处不等式自动成立。",
 "分段函数在两侧都有定义域点时须分别求左极限、右极限并与f(a)比较。",
 "对f(x)=|x|，a=0时|f(x)−f(0)|=|x|，取δ=ε即可证明连续；但不可据此断定0可导。"],
"连续定义是函数极限与该点函数值的相容性；连续性与可导性是不同概念。",
"设f(x)=0(x<0)，f(x)=1(x≥0)，在0右侧极限与f(0)相等但左侧极限为0，故不连续。",
"因为函数在a点有值，就断定该点连续；或因为存在右极限，就直接写双侧连续。",
"先验证函数值，再核对定义域左右的极限，最后比较三者而不泄漏教师例题答案。",
[("f(x)=x²，在x=1处连续吗？","连续。",["f(1)=1。","lim_{x→1}x²=1。","极限和函数值相同，所以连续。"]),
 ("g(x)=x(x≠0),g(0)=2，在x=0处连续吗？","不连续。",["g(0)=2。","当x趋近0但不等于0时g(x)=x，极限为0。","0≠2，因而不连续。"])],
["先核对目标点确实属于函数定义域。","双侧邻域存在时分别检查左右极限。","极限值和实际函数值一致才称该点连续。"],
"分析h(x)=sin x/x (x≠0),h(0)=1在0处连续与否并说明极限依据。",
"分段费率模型在阈值处怎样设计以避免不合理的瞬时跳变？")

FILES=("kb_batch133_six_core_lessons.json","kb_batch134_eight_proof_lessons.json",
       "kb_batch135_eight_deep_lessons.json","kb_batch136_twelve_deep_lessons.json")
def build():
    inv=json.loads(atoms.OUT.read_text(encoding="utf-8"));atoms.validate(inv)
    source={r["id"]:r for r in inv["records"]}
    existing={r.get("source_candidate_id",r.get("candidate_id"))
              for name in FILES
              for r in json.loads((ROOT/"knowledge/editorial_review"/name).read_text(encoding="utf-8"))}
    if len(A)!=7:raise ValueError("must author all seven missing candidates")
    result=[]
    for slug,d in A.items():
        src=source["kb133-proposal-"+slug]
        if src["id"] in existing:raise ValueError("duplicate manuscript source "+slug)
        result.append(dict(
            id="kb137-deep-"+slug,source_candidate_id=src["id"],course_track=src["track"],
            knowledge_type=src["knowledge_type"],source_span_sha256=src["source_lock"]["span_sha256"],
            source_pdf_sha256=src["source_pdf_sha256"],standard_version="2017-2020-editorial-bounded",
            formal_definition_or_theorem=d["formal"],notation_and_domain=d["domain"],
            applicability_and_hypotheses=d["assumptions"],
            reasoned_steps=[dict(step=f"步骤{i}",justification=s) for i,s in enumerate(d["steps"],1)],
            why_method_is_legal=d["legal"],nonexample_or_failure=d["failure"],
            typical_wrong_solution=d["wrong"],why_wrong_and_repair=d["repair"],
            teacher_examples=[dict(question=q,answer=a,reasoned_solution=sol) for q,a,sol in d["examples"]],
            student_hint_ladder=d["hints"],near_transfer=d["near"],far_transfer=d["far"],
            teacher_review_status="REVIEW_PENDING",teacher_review_evidence=None,
            teacher_solution_visibility="TEACHER_ONLY",
            source_status="PROVISIONAL_PDFKIT_SOURCE_PROPOSAL_NOT_OFFICIAL_ATOM",
            formal_proof_certified=False,free_student_step_verified=False,student_authoritative=False))
    return result
def validate(rows):
    if rows!=build() or len(rows)!=7 or len({r["id"] for r in rows})!=7:
        raise ValueError("manuscript drift / count / source / approval")
    for r in rows:
        if len(r["reasoned_steps"])!=4 or len(r["teacher_examples"])!=2 or len(r["student_hint_ladder"])!=3:
            raise ValueError("incomplete mathematics")
        if not all(len(ex["reasoned_solution"])>=3 for ex in r["teacher_examples"]):
            raise ValueError("teacher worked solution too short")
        if any(len(r[f])<20 for f in ("formal_definition_or_theorem","notation_and_domain",
                   "applicability_and_hypotheses","why_method_is_legal","nonexample_or_failure",
                   "typical_wrong_solution","why_wrong_and_repair")):
            raise ValueError("shallow content")
    return True
def safe_export(rows):
    validate(rows)
    return {"status":"NO_APPROVED_MATERIAL","publishable_count":0,"items":[],
            "teacher_solution_excluded":True}
def render(rows):
    text=base.render(rows).replace("Batch136｜十二份原创高中数学深度教师候审讲义",
                                   "Batch137｜七份原创数学深度教师候审讲义")
    return text
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    z=p.parse_args()
    if z.write:
        rows=build();validate(rows)
        OUT.write_text(atoms.stable_json(rows),encoding="utf-8")
        MD.write_text(render(rows),encoding="utf-8")
        SAFE.write_text(atoms.stable_json(safe_export(rows)),encoding="utf-8")
    else:
        rows=json.loads(OUT.read_text(encoding="utf-8"))
        validate(rows)
        if MD.read_text(encoding="utf-8")!=render(rows):raise ValueError("Markdown drift")
        if json.loads(SAFE.read_text(encoding="utf-8"))!=safe_export(rows):raise ValueError("safe export drift")
    print("PASS: seven original deep teacher-only manuscripts; all approvals and student releases zero")
if __name__=="__main__":main()
