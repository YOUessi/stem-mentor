#!/usr/bin/env python3
"""Reconciling every historical proof step; teacher-only, unapproved review cards."""
from __future__ import annotations
import argparse, hashlib, json, sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.deep_knowledge import lessons
from app.kb_batch78_math import CASE_OPS, GOOD, BAD, check
OUT=ROOT/"docs/evaluation/KB_BATCH78_PROOF_DEBT_MATRIX.json"
CARDS=ROOT/"knowledge/editorial_review/kb_batch78_guarded_proof_cards.json"
MD=ROOT/"docs/evaluation/KB_BATCH78_GUARDED_PROOF_REVIEW.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
PARTS=[
 ("BATCH18","docs/evaluation/KB_BATCH18_SOURCE_AND_PROOF_RISK_AUDIT.json","proof_review_queue",451),
 ("BATCH21","docs/evaluation/KB_BATCH21_PROOF_REVIEW_UNION.json","new_proof_review_queue",23),
 ("BATCH22","docs/evaluation/KB_BATCH22_UNVERIFIED_PROOF_QUEUE.json","new_review_obligations",23),
 ("BATCH23","docs/evaluation/KB_BATCH23_INTEGRITY_AND_SCOPE.json","new_proof_review_queue",22),
 ("BATCH24","docs/evaluation/KB_BATCH24_INTEGRITY_AND_PROOFS.json","new_unverified_proof_review_queue",19)]
def digest(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(p.read_text(encoding="utf8"))
def serialize(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

# The exact text SHA is calculated from live authored lessons, not copied from the audits.
def ledger(parts_override=None, lesson_override=None):
    index={l.id:l for l in (lessons() if lesson_override is None else lesson_override)}
    rows=[]; digests={}
    for name,rel,key,count in PARTS:
        path=ROOT/rel
        data=read(path) if parts_override is None or name not in parts_override else parts_override[name]
        digests[name]=digest(path.read_bytes())
        group=data[key]
        if len(group)!=count:raise ValueError(name+" historical count drift")
        for old in group:
            rid=old["id"];lid,sep,num=rid.rpartition("#")
            if not sep or not num.isdecimal() or int(num)<1 or lid not in index:
                raise ValueError("Broken source proof ID "+rid)
            l=index[lid];i=int(num)
            if i>len(l.proof_steps):raise ValueError("Missing original proof step "+rid)
            step=l.proof_steps[i-1]
            actual=digest((step.claim+"\x00"+step.reason).encode("utf8"))
            if actual!=old.get("claim_reason_sha256",old.get("content_sha256")):
                raise ValueError("Original claim/reason tampered: "+rid)
            if old.get("lesson_id",lid)!=lid or old.get("step_index",i)!=i:
                raise ValueError("Step ID mislinked")
            status=old.get("proof_status",old.get("status"))
            if status!="NOT_FORMALLY_VERIFIED" or old.get("student_publishable", False) is not False:
                raise ValueError("Illegally certified/released historical step "+rid)
            if old.get("whole_theorem_certified") or old.get("complete_proof_certified"):
                raise ValueError("Falsified whole theorem certification")
            review=old.get("review_status",old.get("human_teacher_review",old.get("teacher_review")))
            if review not in ("HUMAN_REVIEW_PENDING","PENDING"):
                raise ValueError("Falsified human review")
            if l.review.status!="REVIEW_PENDING" or l.teacher_solution_visibility!="TEACHER_ONLY":
                raise ValueError("Historical teacher solution leaked")
            priority=old.get("priority",old.get("editorial_priority",old.get("review_priority","P1_UNVERIFIED")))
            groups=old.get("risk_groups",old.get("risk_tags",["HUMAN_MATH_REVIEW"]))
            rows.append(dict(id=rid,origin=name,original_step_sha256=actual,
                source_file_sha256=digests[name],risk_groups=groups,risk_priority=priority,
                status="NOT_FORMALLY_VERIFIED",teacher_review="PENDING",student_publishable=False,
                student_step_verified=False,whole_proof_certified=False))
    if len(rows)!=538 or len({r["id"] for r in rows})!=538:
        raise ValueError("538 distinct proof steps not preserved")
    if sum(x["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE" for x in rows)!=127:
        raise ValueError("127 historical P0 steps lost")
    return rows,digests

# Each record: subject, claim, assumptions, three independent mathematical
# reasoning steps, concrete assumption-failure counterexample, common error,
# an original solved-example prompt. All text is new and teacher-side.
T=[
 ("math.hs.logarithm.quotient-law","实对数商法则",
  "a>0且a≠1、x>0、y>0时，log_a(x/y)=log_a x−log_a y。",
  "a>0;a≠1;x>0;y>0",
  "置u=log_a x、v=log_a y，所有实对数均有定义。|用指数律得a^(u−v)=x/y>0，y非零。|由指数和对数互逆得log_a(x/y)=u−v。",
  "x=-4,y=-2时商为正，但右侧两项实对数无定义。",
  "误以为只要x/y>0就可分别取log。","以a=2,x=12,y=3验证合法变形。"),
 ("math.hs.logarithm.change-base","换底公式",
  "a,b>0且都不等于1、x>0时，log_a x=log_b x/log_b a。",
  "a>0;a≠1;b>0;b≠1;x>0",
  "设t=log_a x可得x=a^t。|对两边取以b为底的对数得log_b x=t log_b a。|因为a≠1所以log_b a≠0，合法除以它。",
  "a=1时log_a x无定义且换底式分母log_b 1=0。",
  "只检验a>0而忽略底数不等于1。","以a=2,b=4,x=8核对换底值。"),
 ("math.hs.quadratic.discriminant-roots","二次判别式",
  "a≠0的实系数二次方程的Δ=b²−4ac决定0、1、2个实根。",
  "a,b,c为实数;a≠0",
  "乘4a后配平方得(2ax+b)²=Δ。|实数平方非负，Δ<0不可能；Δ=0只允许平方为0。|Δ>0时取±√Δ，再合法除以2a得到两根。",
  "a=0时退化为线性方程，二次求根式分母为0。",
  "开平方只取正根，或忘记检查a≠0。","解2x²−5x+2=0并分别代回。"),
 ("math.hs.probability.hypergeometric","超几何分布",
  "N≥1,0≤K≤N,0≤n≤N整数，等可能不放回采样时P(X=k)=C(K,k)C(N-K,n-k)/C(N,n)，k须在可行范围。",
  "N,K,n,k均整数;N≥1;0≤K≤N;0≤n≤N;max(0,n−N+K)≤k≤min(n,K)",
  "样本空间为C(N,n)个等可能大小为n的子集。|恰有k成功需从K个成功者和N-K个失败者分别选k、n-k个。|两种选法相乘再除以总样本数，且分母正。",
  "N=5,K=1,n=4,k=3超出成功库存，事件不可能。",
  "不放回抽样却直接套独立伯努利的二项公式。","N=8,K=3,n=2求恰好一次成功概率。"),
 ("math.hs.calculus.quotient-rule","商的导数",
  "u,v在x₀可导、v(x₀)≠0时，(u/v)'=(u'v−uv')/v²在x₀成立。",
  "u在x₀可导;v在x₀可导;v(x₀)≠0",
  "可导保证v连续，故x₀附近v也非零。|求1/v差商，得到−(v(x)−v(x₀))/((x−x₀)v(x)v(x₀))。|极限得倒数导数−v'/v²；乘积法则得到目标式。",
  "u=1,v=x在x₀=0时函数无定义，不能求商导数。",
  "只求分子导数再除原分母。","在x=1求(x²+1)/(x+2)的导数。"),
 ("math.hs.elective.calculus.monotonicity-mvt","中值定理推单调",
  "区间I上的函数连续、内部可导且内部处处f'(x)>0，则f严格递增。",
  "I为区间;f在I连续;f内部可导;内部所有x有f'(x)>0",
  "任取I内a<b，中值定理前提成立。|存在c∈(a,b)使f(b)-f(a)=f'(c)(b-a)。|右侧两因子均正，故任意a<b都有f(b)>f(a)。",
  "f=x²在[-2,2]并非单调，只有右半区间导数为正。",
  "只查看一个点的导数，便推断全区间单调。","比较x²在[1,3]与[-2,2]的单调性。"),
 ("math.hs.geometry.ellipse-tangent","椭圆切线",
  "a,b>0且P₀在x²/a²+y²/b²=1时，切线x₀x/a²+y₀y/b²=1。",
  "a>0;b>0;x₀²/a²+y₀²/b²=1",
  "置F=x²/a²+y²/b²−1，其梯度为(2x/a²,2y/b²)。|P₀在椭圆上且不为零点，梯度非零，因此切线与梯度垂直。|线性化切线方程并利用F(P₀)=0得结论。",
  "P₀=(0,0)不在椭圆上，盲代后给出0=1。",
  "不检验切点在曲线上就使用模板。","求x²/9+y²/4=1在(3,0)处的切线。"),
 ("math.hs.space.line-plane-normal","线面方程与包含",
  "u,n∈R³非零时，直线P+tu包含于平面n·(X-Q)=0的充要条件为n·u=0且n·(P-Q)=0。",
  "u≠零向量;n≠零向量;P,Q在R³",
  "P+tu是合法非零方向的所有直线点。|代入平面得n·(P-Q)+t(n·u)。|此式对任意实数t恒零当且仅当常数项及系数均零。",
  "u=(1,0,0),n=(0,0,1),P=(0,0,1),Q=0时方向平行平面但直线不在平面内。",
  "只检查n·u=0就断言直线在平面内。","比较z=0与z=1两条平行直线。"),
 ("math.hs.geometry.point-line-distance","点线距离",
  "a²+b²>0时，P到直线ax+by+c=0的距离为|ax₀+by₀+c|/√(a²+b²)。",
  "a,b,c为实数;a²+b²>0",
  "n=(a,b)是非零法向量，任取线上Q有n·(P-Q)=ax₀+by₀+c。|单位法向为n/||n||，投影长度取绝对值。|正交分解说明该长度为点到直线的最短距离。",
  "a=b=0,c=1时所谓直线为空且分母0。",
  "省略绝对值，把带符号的投影当距离。","求原点到3x+4y−12=0的距离。"),
 ("math.hs.elective.matrix.inverse-two-by-two","二阶逆矩阵",
  "二阶A=[[a,b],[c,d]]可逆当且仅当ad−bc≠0，此时逆为伴随矩阵除以行列式。",
  "a,b,c,d为实数;应用显式求逆式需ad−bc≠0",
  "令B=[[d,-b],[-c,a]]，逐项算出AB=BA=(ad−bc)I。|非零行列式允许除以ad−bc，得到双侧逆。|行列式为零时存在非零核向量，故不可逆。",
  "A=[[1,2],[2,4]]的行列式为0，不能对伴随矩阵除以0。",
  "以为任意方阵都可直接使用逆矩阵公式。","计算[[1,2],[3,4]]的逆并回乘验算。"),
 ("math.hs.elective.linear.cramer-three","克拉默法则",
  "A为3×3实矩阵且det A≠0，Ax=b唯一解满足x_i=det(A_i)/det A。",
  "A∈R^(3×3);det A≠0;A_i按第i列替换为b",
  "非零行列式使Ax=b存在唯一解。|利用b=Σx_j A_j和行列式对某列的线性性展开det(A_i)。|j≠i项有重复列因而为0，剩下x_i det(A)，可合法除去。",
  "A=diag(1,1,0)时det A=0，即使b=0也不能求0/0。",
  "以方程个数等于未知数个数代替非奇异前提。","A=diag(2,3,5),b=(4,6,10)求解。"),
 ("math.hs.vector.projection","向量正交投影",
  "b非零时proj_b(a)=[(a·b)/(b·b)]b。",
  "a,b同维实向量;b非零",
  "设投影p=tb，要求残差a−tb与b正交。|展开得a·b=t(b·b)，b非零保证b·b>0。|代回唯一t得到投影向量；长度需另取绝对值。",
  "b=0时分母b·b为0，投影方向未定义。",
  "将有符号标量投影错当投影向量。","计算a=(3,4)、b=(1,0)的投影。"),
 ("math.hs.probability.multiplication","条件概率乘法",
  "P(A)>0时P(A∩B)=P(A)P(B|A)；若A、B独立还可写为P(A)P(B)。",
  "A,B是同一概率空间事件;P(A)>0;独立形式需额外已知独立",
  "按定义P(B|A)=P(A∩B)/P(A)。|P(A)>0可两边乘以分母。|仅当独立定义成立时进一步写成P(A)P(B)。",
  "A为空事件时P(B|A)无定义。",
  "把互斥事件当独立事件。","等可能1至6，A={1,2,3},B={3,4}求交概率。"),
 ("math.hs.probability.complement-independence","补事件与独立",
  "A,B独立时，A的补集与B独立，A与B的补集也独立，双补仍独立。",
  "A,B同一概率空间;P(A∩B)=P(A)P(B)",
  "由B=(A∩B)不交并(A补∩B)得到后项概率为P(B)−P(A∩B)。|代入独立式得到(1−P(A))P(B)=P(A补)P(B)。|交换A,B并再次取补可得其他补事件独立，无须用条件概率除法。",
  "四等可能结果中A=B={1,2}，它们并不独立。",
  "以互斥性取代独立性，或者错误添加非零分母前提。","四等可能结果中A={1,2},B={1,3}核查双补。"),
 ("math.hs.geometry.circle-intersections","圆与直线交点",
  "r>0的圆至有效直线距离d时，d<r、d=r、d>r分别对应2、1、0个交点。",
  "r>0;直线法向非零;d≥0",
  "以垂足为原点建立圆心到直线的正交坐标。|把直线代入圆得t²=r²−d²。|实数平方根数量取决于右端严格正、零、负。",
  "r=0时退化为点，不属于本命题的非退化圆。",
  "把重合两圆误算为普通单点相切。","圆x²+y²=25与y=3、5、6分别有几交点？"),
 ("math.hs.space.angle-distance","线面无向夹角",
  "非零方向u和非零平面法向n对应无向线面夹角θ时，sinθ=|u·n|/(||u||||n||)。",
  "u,n∈R³;u非零;n非零;θ∈[0,π/2]",
  "非零内积角公式给出|u·n|/(||u||||n||)=cosφ。|φ为直线与法向的最小无向夹角，线面角与它互余。|因此sinθ=cosφ；有向二面角仍需独立侧向选择。",
  "u=0或n=0时分母为0，几何角无定义。",
  "把线与法向夹角当成线面夹角。","对u=(1,0,0)、n=(0,0,1)和u=n分别求θ。"),
]
SOLUTIONS=[
 "log_2(12/3)=log_2 4=2；log_2 12−log_2 3=log_2(12/3)=2，逐项真数均正。",
 "log_2 8=3；log_4 8=3/2、log_4 2=1/2；(3/2)/(1/2)=3。",
 "Δ=(−5)²−4·2·2=9；x=(5±3)/4，得x=2或1/2，两根代回均为0。",
 "分母C(8,2)=28；成功1次的样本数C(3,1)C(5,1)=15；概率15/28。",
 "u=x²+1、v=x+2，在x=1有u=2,u'=2,v=3,v'=1；商导数=(2·3−2·1)/3²=4/9。",
 "x²在[1,3]内部导数2x>0，f(3)−f(1)=8；中值点c=2满足2c(3−1)=8。",
 "F=x²/9+y²/4−1，∇F(3,0)=(2/3,0)非零；线性化为(2/3)(x−3)=0，即x=3。",
 "n=(0,0,1),u=(1,0,0),Q=0；P=(0,0,0)时n·u=0且n·(P-Q)=0，直线含于z=0；P=(0,0,1)第二项=1，不包含。",
 "a=3,b=4,c=−12；原点代入得|−12|=12；法向量长度√(3²+4²)=5，距离12/5。",
 "A=[[1,2],[3,4]],det A=−2；逆矩阵=[[−2,1],[3/2,−1/2]]，左右相乘均为I。",
 "det A=2·3·5=30；把第1/2/3列换b分别得det(A_i)=60；x_i=60/30=2。",
 "a=(3,4),b=(1,0)，a·b=3,b·b=1；proj_b a=3(1,0)=(3,0)，残差(0,4)与b正交。",
 "六等可能结果，P(A)=3/6=1/2，P(B|A)=1/3；乘积1/6，且A∩B={3}也为1/6。",
 "四等可能结果，A={1,2},B={1,3},P(A∩B)=1/4=P(A)P(B)；A补={3,4},B补={2,4},交={4}，仍为1/4。",
 "x²+y²=25代入y=3得x²=16，有x=±4两点；y=5得x=0一点；y=6得x²=−11无实点。",
 "u=(1,0,0),n=(0,0,1)，|u·n|=0，所以sinθ=0、θ=0；u=n=(0,0,1)时sinθ=1、θ=π/2。",
]
NEAR=[
 "换成底3、真数27与9，逐项核验真数后简化。","用b=9给log_3 81换底，重检log_b 3≠0。",
 "把常数项改为3，讨论Δ的变化和实根数量。","保持N=8,K=3，将样本量改为3并计算k的可行集。",
 "同一商函数在x=0求导并核对导数定义。","对x³在[0,2]使用同样的中值论证。",
 "在椭圆(0,2)处证明切线为y=2。","保持u,n，改取P=(1,2,0)核对整条直线位置。",
 "将直线常数项改为−6重算原点距离。","取A=[[2,1],[1,1]]，求逆并回乘。",
 "把b改为(2,3,5)，重新求三个分子行列式。","令a=(2,2),b=(1,1)，验证残差正交。",
 "改变B为{2,3,4}，用条件事件A计算交概率。","取A={1,4},B={1,2}，重新检验是否独立。",
 "固定r=5比较y=−5与y=0的交点。","取u=(1,0,1),n=(0,0,1)计算sinθ。",
]
FAR=[
 "讨论log_a(xy)−log_a x−log_a y在负因子下何处无意义。","比较指数增长率log函数的比值换底与求导中的底数限制。",
 "将二次根判别转成圆与直线交点数，找出退化系数。","将不放回计数替换为放回抽样并解释分布改变。",
 "讨论有理函数连续性与极限处可去间断，区分可导域。","解释导数处处非负与严格单调之间的不同条件。",
 "推广到非奇异隐式曲线F(x,y)=0的一般切线法向条件。","把直线包含于平面的两条件迁移到射线和线段的包含判断。",
 "用空间点面距离检验法向量非零的同类风险。","从逆矩阵存在性研究列向量线性无关与唯一解。",
 "比较满列秩矩形系统与方阵Cramer法则是否可移植。","把投影用于最小二乘残差正交性并分析零列向量。",
 "构造正概率互斥事件，证明其并非独立。","把补集独立性质迁移到三事件联合独立问题并区分两两独立。",
 "讨论同心重合两圆时相交数量为何不是1。","区分线面无向夹角与有向二面角的法向量选择。",
]
assert len(SOLUTIONS)==len(NEAR)==len(FAR)==len(T)==16
def make_cards(rows):
    index={r["id"]:r for r in rows}
    cards=[]
    for j,(lid,title,statement,assumptions,steps,bad,wrong,task) in enumerate(T,1):
        hits=[r for r in rows if r["origin"]=="BATCH18" and r["id"].startswith(lid+"#") and r["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE"]
        if not hits:raise ValueError("Missing original high-risk proof step "+lid)
        hit=hits[0]
        # Only the Chinese sentence terminator followed by a pipe is a step
        # boundary. Literal mathematical pipes (P(B|A), |a|, ||v||) must survive.
        sentences=steps.split("。|")
        if len(sentences)!=3 or not all(sentences):
            raise ValueError("Expected exactly three intact authored proof steps: "+lid)
        authored_steps=[text+("。" if i<2 else "") for i,text in enumerate(sentences)]
        cards.append(dict(id=f"KB78-P{j:02}",kind="THEOREM_OR_METHOD_REVIEW",
            bounded_case_operation=CASE_OPS[j-1], bounded_valid_input=GOOD[CASE_OPS[j-1]],
            bounded_invalid_input=BAD[CASE_OPS[j-1]],
            mathematical_topic=title,statement=statement,assumptions=assumptions.split(";"),
            proof_steps=[{"index":i+1,"claim_and_reason":text} for i,text in enumerate(authored_steps)],
            invalid_boundary=bad,common_wrong_method=wrong,
            worked_examples=[{"question":task,"teacher_solution":SOLUTIONS[j-1],"visibility":"TEACHER_ONLY"},
               {"question":"删除命题的一项必要假设并判断公式是否仍适用。",
                "teacher_solution":bad,"visibility":"TEACHER_ONLY"}],
            hint_ladder=["先找出数学对象、定义域和需要排除的退化情况。",
                         "分别核实非零、有效区间、事件关系或可导前提。",
                         "再推演关键一步是否为合法等价变形；不直接提供最终数值。"],
            near_transfer=NEAR[j-1],
            far_transfer=FAR[j-1],
            linked_historical_step_id=hit["id"],original_step_sha256=hit["original_step_sha256"],
            linked_source_kind="PROJECT_HISTORICAL_DRAFT_NOT_OFFICIAL_ATOM",
            student_publishable=False,formal_math_certification="NOT_FORMALLY_VERIFIED",
            review_status="REVIEW_PENDING",reviewer_id=None,teacher_solution_visibility="TEACHER_ONLY",
            official_curriculum_atom_id=None,student_free_text_verified=False))
    return cards
def validate_cards(cards,rows):
    if len(cards)!=16 or len({r["id"] for r in cards})!=16:raise ValueError("16 distinct cards required")
    original={r["id"]:r for r in rows}
    for c in cards:
        src=original.get(c["linked_historical_step_id"])
        if not src or src["risk_priority"]!="P0_GUARD_AND_COUNTEREXAMPLE" or src["original_step_sha256"]!=c["original_step_sha256"]:
            raise ValueError("Historic step provenance changed")
        if (c["student_publishable"] or c["reviewer_id"] is not None or c["student_free_text_verified"]
            or c["official_curriculum_atom_id"] is not None or c["review_status"]!="REVIEW_PENDING"
            or c["teacher_solution_visibility"]!="TEACHER_ONLY"
            or c["formal_math_certification"]!="NOT_FORMALLY_VERIFIED"):
            raise ValueError("Fake teacher approval or math certification")
        if c["bounded_case_operation"]!=CASE_OPS[int(c["id"].split("P")[-1])-1]:
            raise ValueError("Bounded case operation rewired")
        if check(c["bounded_case_operation"],c["bounded_valid_input"])[0]!="VERIFIED_FINITE_INSTANCE":
            raise ValueError("Positive math instance not verified")
        if check(c["bounded_case_operation"],c["bounded_invalid_input"])[0]!="CONDITIONS_NOT_ESTABLISHED":
            raise ValueError("Invalid math assumptions were accepted")
        if len(c["assumptions"])<2 or len(c["proof_steps"])!=3 or len(c["worked_examples"])!=2 or len(c["hint_ladder"])!=3:
            raise ValueError("Incomplete review card")
        if any(step.get("index")!=i or len(step.get("claim_and_reason","").strip())<10
               for i,step in enumerate(c["proof_steps"],1)):
            raise ValueError("Truncated mathematical proof reasoning")
        if not all(x["teacher_solution"] and x["visibility"]=="TEACHER_ONLY" for x in c["worked_examples"]):
            raise ValueError("Worked solution leaked")
        for field in ("statement","invalid_boundary","common_wrong_method","near_transfer","far_transfer"):
            if not c[field]:raise ValueError("Missing "+field)
def build(parts_override=None,lesson_override=None):
    rows,hashes=ledger(parts_override,lesson_override)
    cards=make_cards(rows);validate_cards(cards,rows)
    previous=read(ROOT/"docs/evaluation/KB_BATCH24_INTEGRITY_AND_PROOFS.json")
    if previous["summary"]["all_unverified_proof_steps"]!=538:raise ValueError("Frozen history changed")
    k00=read(ROOT/"docs/evaluation/KB_BATCH75_EDITORIAL_SUBCLAUSE_MATRIX.json")
    if len(k00["records"])!=60 or any(x is not None for x in k00["official_denominators"].values()):
        raise ValueError("Cannot invent official seven-track denominator")
    summary=dict(historical_proof_steps=len(rows),source_counts=dict(sorted(Counter(x["origin"] for x in rows).items())),
       claim_and_reason_sha_verified=len(rows),
       p0_unverified_steps=sum(x["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE" for x in rows),
       new_teacher_review_cards=len(cards),new_teacher_only_example_tasks=2*len(cards),
       bounded_exact_positive_witnesses=len(cards),bounded_invalid_assumptions_rejected=len(cards),
       formally_certified_steps=0,whole_theorem_certifications=0,teacher_approvals=0,
       free_text_student_steps_verified=0,student_published=0,
       official_atomic_denominators={t:None for t in TRACKS},full_page_human_atomizations=0,
       historical_conflicts_unresolved=10)
    return dict(schema_version="batch78-proof-step-lineage-v1",
       scope="SOURCE_HASH_AND_GUARDED_EDITORIAL_PROOFS_ONLY_NO_FORMAL_CERTIFICATION",
       standard_version="普通高中数学课程标准（2017年版2020年修订）",
       source_sha256=hashes,summary=summary,proof_obligations=rows,review_cards=cards)
def markdown(pack):
    lines=["# Batch78｜538条历史证明步骤和16份前提审查卡","",
      "该文档中的论证属于项目原创教师审查稿，不是机器证明的通用定理，也未经教师独立认证。",
      "538/538仅指旧稿逐步文字和来源哈希均可追溯；它们始终未形式认证。",
      "## 可审计计数","",serialize(pack["summary"])]
    for r in pack["review_cards"]:
        lines.extend(["", "## "+r["id"]+" "+r["mathematical_topic"],
          "来源历史步骤："+r["linked_historical_step_id"],
          "原始步骤SHA256："+r["original_step_sha256"],
          "陈述："+r["statement"],"完整前提："+"；".join(r["assumptions"]),"论证草案："])
        lines.extend([str(x["index"])+". "+x["claim_and_reason"] for x in r["proof_steps"]])
        lines.extend(["失效反例："+r["invalid_boundary"],"典型错法："+r["common_wrong_method"],
           "受控例题："+r["worked_examples"][0]["question"],
           "教师侧例题解析："+r["worked_examples"][0]["teacher_solution"],
           "反事实练习："+r["worked_examples"][1]["question"],
           "教师侧反事实解析："+r["worked_examples"][1]["teacher_solution"],
           "分级提示："])
        lines.extend([str(i+1)+". "+s for i,s in enumerate(r["hint_ladder"])])
        lines.extend(["近迁移："+r["near_transfer"],"远迁移："+r["far_transfer"],
           "状态：REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_VERIFIED"])
    return "\n".join(lines)+"\n"
def main():
    a=argparse.ArgumentParser();a.add_argument("--check",action="store_true");o=a.parse_args()
    data=build()
    outputs=[(OUT,serialize(data)),(CARDS,serialize(data["review_cards"])),(MD,markdown(data))]
    for p,s in outputs:
        if o.check:
            if not p.exists() or p.read_text(encoding="utf8")!=s:
                raise SystemExit("Out-of-date generated proof audit "+str(p))
        else:p.write_text(s,encoding="utf8")
    print(json.dumps(data["summary"],ensure_ascii=False))
if __name__=="__main__":main()
