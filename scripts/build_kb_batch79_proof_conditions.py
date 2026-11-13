#!/usr/bin/env python3
"""12 original, historically linked high-risk mathematical review packs (teacher only)."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"backend"))
from app.kb_batch79_math import OPS, GOOD, BAD, check
PARENT = ROOT/"docs/evaluation/KB_BATCH78_PROOF_DEBT_MATRIX.json"
FROZEN_PARENT_SHA256 = "da5fec7f7da73c3c9d602e9cf8b29c2ec3c943f3929196eea768d0bb3c4215d5"
OUT = ROOT/"knowledge/editorial_review/kb_batch79_condition_proof_cards.json"
MD = ROOT/"docs/evaluation/KB_BATCH79_TWELVE_CONDITION_PROOFS.md"
# id / operator / topic / statement / assumptions / three authored reasoning steps /
# condition-failure counterexample / recurring error / solved question / solved answer / near / far
T = [
("math.hs.inequality.amgm#1","amgm","正数算术几何平均不等式",
 "对任意正实数a,b，有(a+b)/2≥√(ab)，且等号仅当a=b。",
 "a>0;b>0;实数范围",
 "a,b正保证√a、√b及√ab在实数中存在。|平方(√a−√b)²≥0得到a+b≥2√ab，除以正数2保持不等号。|等号成立当且仅当√a=√b，等价于a=b；不把这个结论逆向套给负数。",
 "a=-2,b=8时√(ab)在实数无定义，不能引用正数版定理。","忽略非负开方定义域，或声称所有实数均满足。",
 "a=2,b=8时比较均值。","(2+8)/2=5，√16=4，所以5≥4；两值不同，严格不等。",
 "检验a=5,b=5为何等号成立。","用于两项非负代价优化时，先核实变量符号再调用。"),
("math.hs.vector.cauchy-schwarz#1","cauchy2","二维柯西—施瓦茨不等式",
 "对任意u=(u₁,u₂),v=(v₁,v₂)∈R²，有(u·v)²≤(u·u)(v·v)。",
 "u,v同属R²;分量均为实数",
 "直接展开(u·u)(v·v)−(u·v)²。|配方得到(u₁v₂−u₂v₁)²≥0，此步对任意实数成立且没有除法。|把非负平方移项得到不等式；等号当且仅当两个向量线性相关（零向量亦满足）。",
 "u属于R²而v属于R³时内积未在同一空间中定义。","把u·v当作任意异维向量的运算，或错误要求向量都非零。",
 "u=(1,2),v=(3,4)检验不等式。","u·v=11，平方121；||u||²||v||²=5×25=125；差4=(1×4−2×3)²。",
 "取u=(1,2),v=(2,4)说明等号。","推广到R³时应换用相应恒等式，不能照搬二维交叉项。"),
("math.hs.sequence.geometric-sum#4","geometric_sum","有限等比数列求和的q≠1分支",
 "对n≥1整数、首项a和公比q≠1，有Σₖ₌₀ⁿ⁻¹a qᵏ=a(1−qⁿ)/(1−q)。",
 "n为正整数;q≠1;a,q为实数",
 "把有限和写为S=a+aq+⋯+aq^(n−1)，再写qS=aq+⋯+aqⁿ。|逐项相减严格得到(1−q)S=a(1−qⁿ)，没有使用无穷级数极限。|q≠1确保除法合法；若q=1单独计算S=na，不能套零分母形式。",
 "取q=1,n=4,a=3时原和12存在，但分式出现0/0。","把有限公式误写成无穷级数，或忘记q=1分支。",
 "a=3,q=2,n=4求和。","直接3+6+12+24=45；分式3(1−16)/(1−2)=45，逐步一致。",
 "考察q=0和n=1的边界。","迁移到贷款现金流求和前先说明每期折现率和有限期数。"),
("math.hs.function.composition-domain#1","composition","复合函数定义域的双层约束",
 "f(t)=1/t、g(x)=x−2时，f∘g的实数定义域为R∖{2}。",
 "f的定义域t≠0;g对所有实数x有定义;g(x)须属于f的定义域",
 "先检查内函数g(x)=x−2的定义域为R。|外函数仅接受非零输入，故必须解x−2≠0。|得到x≠2且(f∘g)(x)=1/(x−2)；不能只检查内层的定义域。",
 "x=2在g的定义域内但g(2)=0，f(0)无定义。","只取g的定义域，而遗漏g(x)∈D_f。",
 "x=3时计算f(g(x))。","g(3)=1，f(1)=1，符合x≠2。",
 "把g改为x²−4，写出应排除的点。","若外函数改为√t，还需要新的非负实数输入约束。"),
("math.hs.probability.bayes-partition#3","bayes","有限等可能样本空间中的贝叶斯公式",
 "同一有限等可能样本空间中P(A)>0且P(B)>0时，P(A|B)=P(B|A)P(A)/P(B)。",
 "样本空间有限非空且等可能;A,B合法事件;P(A)>0;P(B)>0",
 "按条件概率定义P(A|B)=P(A∩B)/P(B)。|同理P(B|A)=P(A∩B)/P(A)，因此P(B|A)P(A)=P(A∩B)。|由于P(B)>0，合法除以P(B)得到结论；条件事件为零概率时两种写法不能照用。",
 "B=空集时P(A|B)无定义，即使交集概率为0也不可除以0。","把P(A|B)与P(B|A)混淆，或遗漏条件事件非零。",
 "六等可能结果A={1,2,3},B={1,2,3,4}求P(A|B)。","交集大小3、B大小4，所以P(A|B)=3/4；Bayes右侧(3/3)(3/6)/(4/6)=3/4。",
 "令A与B不相交但都非空，验证结果为零。","将事件先验变更带入诊断概率，检查是否错误认为条件概率可交换。"),
("math.hs.function.bisection-root#2","bisection","介值定理与二分法的严格异号门槛",
 "连续f(x)=x²−c(c>0)若a<b且f(a)f(b)<0，则(a,b)存在零点。",
 "c>0;a<b;f为连续多项式;f(a)f(b)<0",
 "多项式在实数闭区间[a,b]连续，因此可调用介值定理。|端点函数值严格异号，0严格处于两值之间，于是存在ξ∈(a,b)使f(ξ)=0。|二分时在包含异号端点的半区间继续，不能把异号条件误说成任意区间均有根，也不能据此声称根唯一。",
 "f=x²−2在[2,3]两端均正，不能以异号介值定理保证根。","不检查连续性或端点符号，或把存在性冒充唯一性。",
 "f=x²−2在[1,2]执行首次二分。","f(1)=-1、f(2)=2；中点3/2，f(3/2)=1/4>0，新的异号括区为[1,3/2]。",
 "讨论f(a)=0时为何无需再断言开区间有根。","比较f=x²−1在[-2,2]的多根情况，解释介值定理不证明唯一性。"),
("math.hs.geometry.parabola-focus#1","parabola","抛物线焦点—准线距离定义",
 "对p>0，曲线y²=4px上任一点P到F=(p,0)与准线x=−p距离相等。",
 "p>0;P=(x,y)实坐标;y²=4px",
 "点P到焦点距离平方为(x−p)²+y²。|利用曲线条件y²=4px变换为(x+p)²，且p>0保证曲线点x≥0从而x+p>0。|至准线x=−p的距离为|x+p|，两种非负距离平方相等，故距离相等。",
 "p=0时方程退化为直线y=0，焦点—准线重合，不能当作非退化抛物线。","把任何满足y=0的直线点当作p=0的抛物线点。",
 "p=2、P=(2,4)验算。","4²=4×2×2=16；到焦点(2,0)距离4；到直线x=-2距离4。",
 "改变p与合法整数点验证平方距离恒等。","把焦点定义推广到旋转抛物线时先给出旋转坐标与准线。"),
("math.hs.sequence.arithmetic-sum#4","arithmetic_sum","有限等差数列前n项和",
 "n为正整数，首项a、公差d时S_n=n(2a+(n−1)d)/2。",
 "n≥1且为整数;a,d为实数",
 "把首n项顺序相加写成S_n。|逆序再写一遍，配对每一列均得2a+(n−1)d，一共有n列。|将两行相加后除以常数2得到公式，n只需为正整数，无需额外要求d≠0。",
 "n=0不属于此处“前n项”的正整数叙述；不能以空项作为本命题示例。","以为d必须非零或把n−1误写为n。",
 "a=2,d=3,n=5求和。","2+5+8+11+14=40；公式5(4+12)/2=40。",
 "取d=0核对常数数列。","迁移到梯形面积公式时区分连续几何长度和离散整数项数。"),
("math.hs.geometry.circle-complete-square#3","circle_square","圆的一般方程配平方与非退化半径",
 "x²+y²+Dx+Ey+F=0表示非退化实圆当且仅当(D²+E²)/4−F>0。",
 "D,E,F为实数;二次项均为x²+y²且系数为1",
 "分别配平方得到(x+D/2)²+(y+E/2)²=(D²+E²)/4−F。|记右端r²；若r²>0则为中心(-D/2,-E/2)、半径√r²的非退化圆。|r²=0只有单点、r²<0无实点，因此不能将它们发布为正常半径的圆。",
 "D=2,E=0,F=4时r²=1−4=−3，无实点。","只找出圆心就默认半径存在，或忽略r²=0的单点退化。",
 "x²+y²−2x−4y−4=0配平方。","化为(x−1)²+(y−2)²=9，圆心(1,2)、半径3。",
 "构造r²=0的单点退化方程。","从一般二次曲线判别中解释为何必须有等系数且无xy项。"),
("math.hs.elective.statistics.ols-two-parameter#3","ols","一元带截距最小二乘的唯一性条件",
 "给定n≥2个实观测，若S_xx=Σ(x_i−x̄)²>0，最小二乘直线唯一且斜率S_xy/S_xx，截距ȳ−斜率×x̄。",
 "n≥2;所有x_i,y_i实数;S_xx>0;目标为残差平方和",
 "对Q(α,β)=Σ(y_i−α−βx_i)²分别求偏导，得到Σ残差=0、Σx_i残差=0。|第一式得α=ȳ−βx̄，代入第二式得到βS_xx=S_xy。|S_xx>0意味着目标函数在斜率方向严格凸，故这一解是唯一极小值；不能以相关系数替代因果结论。",
 "所有x_i都相同则S_xx=0，有斜率无法唯一确定，不得除以S_xx。","把二点拟合或相关性当作因果证明，忽略自变量无变异。",
 "点(0,1),(1,3),(2,5)拟合。","x̄=1、ȳ=3，S_xx=2、S_xy=4；β=2,α=1；三个残差都为0。",
 "把所有y_i改成常数并比较斜率。","迁移到带多特征回归时要改为矩阵列秩条件，不能沿用标量分母。"),
("math.hs.statistics.variance-affine#3","variance_affine","总体型经验方差的仿射变换",
 "非空有限样本的经验总体方差Var_n(X)=n⁻¹Σ(x_i−x̄)²满足Var_n(aX+b)=a² Var_n(X)。",
 "n≥2整数;数据为有限实数;a,b为实数;分母使用n而非n−1",
 "变换后的样本均值为a x̄+b，故每个中心化离差变成a(x_i−x̄)。|平方并求和得Σ(a(x_i−x̄))²=a²Σ(x_i−x̄)²。|除以同一个正整数n得到恒等式；a=0也合法，方差成为0，但不应因此强加a≠0。",
 "空样本n=0时均值和除以n的经验方差均无定义。","把a²误写为a，或者误将n分母的方差与n−1版本直接混用。",
 "数据[1,3,5]经y=2x+7变换。","原均值3，方差((−2)²+0+2²)/3=8/3；新数据[9,13,17]方差32/3=4×8/3。",
 "取a=0观察方差归零。","比较总体型方差与不偏样本方差在同样尺度变换下的规则。"),
("math.hs.triangle.cosine-law#4","cosine_law","三角形余弦定理及退化边界",
 "在非退化三角形中，夹角C对应对边c、邻边a,b时cos C=(a²+b²−c²)/(2ab)。",
 "a,b,c>0;严格三角形不等式;a,b为夹角的邻边",
 "在角C的两条邻边上取向量u,v，长度分别为a,b，夹角C。|对边向量为u−v，故c²=||u−v||²=a²+b²−2u·v。|u·v=ab cos C且ab>0，合法移项并除2ab，得到公式；退化边长不得套用内角定义。",
 "边长1,1,3违反三角形不等式，代公式得到越界余弦值，不能称三角形内角。",
 "只检查余弦公式的代数值，却没有判断三条边能否构成非退化三角形。",
 "a=3,b=4,c=5时求C。","cos C=(9+16−25)/(2×3×4)=0，所以C=90°。",
 "构造等边三角形验证cos60°。","迁移到三维向量求夹角时检查非零向量和角的取值范围。"),
]
HINTS = [
 ("先检查a、b是否允许在实数中开平方。", "把√a与√b的差平方，寻找一个始终非负的表达式。", "考察差的平方何时为零，用它判断等号条件而非直接代值。"),
 ("检查两个内积是否发生在同一个二维实向量空间。", "尝试展开两个平方范数的积与内积平方之差。", "识别行列式型平方项，并检查零向量情形的等号。"),
 ("分别写下n项原和S与同样n项的qS。", "逐项抵消两个有限和，保留首项与末项。", "在除以1−q之前检查是否等于零；若等于零改用常数和。"),
 ("先区分内函数的定义域与外函数允许的输入。", "找出g(x)什么时候让分母成为零，而不是只看g本身。", "用排除后的自变量测试复合表达式，并重核外层是否有定义。"),
 ("把A与B作为同一样本空间的事件，找出两个条件概率的分母。", "先将两种条件概率各自写成交集概率除以条件事件概率。", "检查分母为正后再进行代数整理，别把两个条件的方向交换。"),
 ("检查f的连续性以及区间端点是否严格异号。", "使用介值定理先证明至少存在一个零点，不要直接断言唯一。", "在中点求f值后决定应保留哪对异号端点；中点为根则停止。"),
 ("写出点到焦点与点到竖直准线的两个距离。", "先比较距离的平方，并将曲线方程代入消去y²。", "把平方相等转回距离相等时确认两边都是非负的。"),
 ("把首项到第n项顺序写成一个有限和。", "逆序写第二遍，将两式逐列配对。", "清楚数出配对数并检查n的整数范围，不强加d非零。"),
 ("分别对x与y完成平方，别漏掉移动到右侧的常数。", "把所得右端记为半径的平方并判断符号。", "单独分析正数、零和负数三种情形是否真的给出一个圆。"),
 ("先写出残差平方和，明确有截距和斜率两个未知数。", "对两个参数写正常方程，再将自变量中心化。", "检查Sxx为何必须大于零，才能保证斜率唯一而不是除以零。"),
 ("计算线性变换后的样本均值，别急着求方差。", "把每一项的新离差与旧离差比较，注意平移项怎样消去。", "平方后看系数是a还是a²，并解释a=0时是否仍成立。"),
 ("先验证三边能组成严格非退化的三角形。", "把夹角两边看作向量，利用对边等于它们的差。", "展开差向量的平方范数后检查能否合法除以2ab。"),
]
assert len(HINTS)==len(T)==len(OPS)==12

def digest(text):return hashlib.sha256(text.encode("utf8")).hexdigest()
def dump(data):return json.dumps(data,sort_keys=True,ensure_ascii=False,indent=2)+"\n"
def read(p):return json.loads(p.read_text(encoding="utf8"))

def build(ledger_override=None):
    frozen=read(PARENT) if ledger_override is None else ledger_override
    if digest(dump(frozen)) != FROZEN_PARENT_SHA256:
        raise ValueError("Historical Batch78 ledger content SHA changed")
    rows=frozen["proof_obligations"]
    by_id={r["id"]:r for r in rows}
    previous={c["linked_historical_step_id"] for c in frozen["review_cards"]}
    if len(rows)!=538 or len(by_id)!=538 or len(frozen["review_cards"])!=16:
        raise ValueError("Missing preserved Batch78 mathematical proof provenance")
    cards=[]
    for i,rec in enumerate(T):
        lid,op,title,statement,assumptions,steps,bad,wrong,question,solution,near,far=rec
        prior=by_id.get(lid)
        if not prior or lid in previous or prior["risk_priority"]!="P0_GUARD_AND_COUNTEREXAMPLE":
            raise ValueError("Card not linked to distinct unreviewed P0 proof step: "+lid)
        fragments=steps.split("。|")
        if len(fragments)!=3 or not all(z.strip() for z in fragments):
            raise ValueError("Proof must have 3 complete Chinese sentences")
        if check(op,GOOD[op])[0]!="VERIFIED_FINITE_INSTANCE" or check(op,BAD[op])[0]!="CONDITIONS_NOT_ESTABLISHED":
            raise ValueError("Finite exact positive/invalid case witness missing")
        card=dict(id=f"KB79-P{i+1:02}",kind="THEOREM_OR_METHOD_REVIEW",
            linked_historical_step_id=lid,original_step_sha256=prior["original_step_sha256"],
            original_ledger_sha256=digest(PARENT.read_text(encoding="utf8")),source_kind="PROJECT_HISTORICAL_DRAFT_NOT_OFFICIAL_ATOM",
            title=title,statement=statement,assumptions=assumptions.split(";"),
            proof_steps=[{"index":j+1,"claim_and_reason":s+("。" if j<2 else "")} for j,s in enumerate(fragments)],
            invalid_boundary=bad,common_wrong_method=wrong,
            finite_op=op,finite_valid=GOOD[op],finite_invalid=BAD[op],
            worked_examples=[{"question":question,"teacher_solution":solution,"visibility":"TEACHER_ONLY"},
               {"question":"检验本命题的一个失败前提，说明为什么结论不能照用。","teacher_solution":bad,"visibility":"TEACHER_ONLY"}],
            hint_ladder=list(HINTS[i]),
            near_transfer=near,far_transfer=far,review_status="REVIEW_PENDING",
            curriculum_standard_version="普通高中数学课程标准（2017年版2020年修订）",
            curriculum_track_hint="UNDETERMINED_PENDING_OFFICIAL_ATOMIZATION",copyright_origin="ORIGINAL_PROJECT_AUTHORED",
            reviewer_id=None,formal_math_certification="NOT_FORMALLY_VERIFIED",student_publishable=False,
            teacher_solution_visibility="TEACHER_ONLY",student_free_text_verified=False,official_curriculum_atom_id=None,
            finite_instance_status="VERIFIED_FINITE_INSTANCE_ONLY")
        cards.append(card)
    validate(cards, frozen)
    return dict(schema_version="kb79-guarded-proof-review-v1",
        curriculum_standard_version="普通高中数学课程标准（2017年版2020年修订）",
        parent_batch78_ledger_sha256=digest(PARENT.read_text(encoding="utf8")),
        historical_step_count=538,existing_batch78_guard_cards=16,new_batch79_guard_cards=12,
        total_distinct_high_risk_review_card_links=28,official_atom_denominator=None,
        teacher_approvals=0,formally_certified_proofs=0,student_published=0,
        review_cards=cards)

def validate(cards, frozen):
    if digest(dump(frozen)) != FROZEN_PARENT_SHA256:
        raise ValueError("Tampered frozen historical proof ledger")
    if any(tuple(c["hint_ladder"])!=HINTS[i] for i,c in enumerate(cards)):
        raise ValueError("Missing topic-specific scaffold for proof card")
    if len(cards)!=12 or len({c["id"] for c in cards})!=12:
        raise ValueError("Missing or duplicate review cards")
    prior={r["id"]:r for r in frozen["proof_obligations"]}
    old={c["linked_historical_step_id"] for c in frozen["review_cards"]}
    if len({c["linked_historical_step_id"] for c in cards})!=12:
        raise ValueError("Duplicated historical source step")
    for i,c in enumerate(cards):
        source=prior.get(c["linked_historical_step_id"])
        if not source or source["risk_priority"]!="P0_GUARD_AND_COUNTEREXAMPLE" or c["linked_historical_step_id"] in old or source["original_step_sha256"]!=c["original_step_sha256"]:
            raise ValueError("Historical P0 provenance corrupted")
        if c["id"]!=f"KB79-P{i+1:02}" or c["finite_op"]!=OPS[i]:
            raise ValueError("Card and exact operation mismatched")
        if (c["source_kind"]!="PROJECT_HISTORICAL_DRAFT_NOT_OFFICIAL_ATOM" or
            c["original_ledger_sha256"]!=FROZEN_PARENT_SHA256 or
            c["curriculum_standard_version"]!="普通高中数学课程标准（2017年版2020年修订）" or
            c["curriculum_track_hint"]!="UNDETERMINED_PENDING_OFFICIAL_ATOMIZATION" or
            c["copyright_origin"]!="ORIGINAL_PROJECT_AUTHORED"):
            raise ValueError("Falsified historical source type or ledger SHA")
        if (c["review_status"]!="REVIEW_PENDING" or c["reviewer_id"] is not None or
            c["formal_math_certification"]!="NOT_FORMALLY_VERIFIED" or c["student_publishable"] or
            c["student_free_text_verified"] or c["official_curriculum_atom_id"] is not None or
            c["teacher_solution_visibility"]!="TEACHER_ONLY" or c["finite_instance_status"]!="VERIFIED_FINITE_INSTANCE_ONLY"):
            raise ValueError("Falsified teacher certification or student publication")
        if len(c["proof_steps"])!=3 or len(c["assumptions"])<2 or len(c["worked_examples"])!=2 or len(c["hint_ladder"])!=3:
            raise ValueError("Incomplete math review fields")
        if any(not a.strip() for a in c["assumptions"]) or any(not h.strip() for h in c["hint_ladder"]):
            raise ValueError("Empty mathematical assumptions or hint")
        if any(step["index"]!=j+1 or not step["claim_and_reason"].strip() for j,step in enumerate(c["proof_steps"])):
            raise ValueError("Broken mathematical reasoning steps")
        if not all(c[f] for f in ("statement","invalid_boundary","common_wrong_method","near_transfer","far_transfer")):
            raise ValueError("Empty mathematical boundary or transfer")
        if any(not s["claim_and_reason"].strip().endswith("。") for s in c["proof_steps"]):
            raise ValueError("Truncated or malformed proof sentence")
        if not all(e["visibility"]=="TEACHER_ONLY" and e["teacher_solution"] for e in c["worked_examples"]):
            raise ValueError("Teacher solution missing or leaked")
        if check(c["finite_op"],c["finite_valid"])[0]!="VERIFIED_FINITE_INSTANCE" or check(c["finite_op"],c["finite_invalid"])[0]!="CONDITIONS_NOT_ESTABLISHED":
            raise ValueError("Math condition witness was bypassed")

def markdown(package):
    lines=["# STEM Mentor Batch79｜十二项数学前提与证明审查（教师侧）","",
        "> 有限整数算例与符号恒等式见证不能代替一般证明的正式认证；原始538步仍全部未形式认证。","",
        "> 本批12篇用于教研审核，不是官方独立课标原子，也不发布给学生。",""]
    for c in package["review_cards"]:
        lines += [f"## {c['id']}｜{c['title']}","",
            f"**原有风险步骤**：{c['linked_historical_step_id']}（SHA256: {c['original_step_sha256']}）",
            f"**准确命题**：{c['statement']}",
            f"**前提**：{'；'.join(c['assumptions'])}", "",
            "**分步论证（待教师确认）**"]
        lines += [f"{s['index']}. {s['claim_and_reason']}" for s in c["proof_steps"]]
        lines += ["",f"**违反前提的反例**：{c['invalid_boundary']}",
            f"**典型错因**：{c['common_wrong_method']}",
            f"**例题**：{c['worked_examples'][0]['question']}",
            f"**教师侧解答**：{c['worked_examples'][0]['teacher_solution']}",
            f"**三级提示**：{' → '.join(c['hint_ladder'])}",
            f"**近迁移**：{c['near_transfer']}",f"**远迁移**：{c['far_transfer']}","",
            "**发布状态**：REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_VERIFIED",""]
    return "\n".join(lines).rstrip("\n")+"\n"
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    p=build()
    for dest,content in [(OUT,dump(p)),(MD,markdown(p))]:
        if args.check:
            if not dest.exists() or dest.read_text(encoding="utf8")!=content:
                raise SystemExit("Generated file differs: "+str(dest))
        else:
            dest.write_text(content,encoding="utf8")
    print(json.dumps({"historic_debt":p["historical_step_count"],"new_cards":p["new_batch79_guard_cards"],
        "high_risk_cards_cumulative":p["total_distinct_high_risk_review_card_links"],
        "certified_proofs":p["formally_certified_proofs"]}))
if __name__=="__main__":main()
