#!/usr/bin/env python3
"""Author 8 scoped mathematical repair manuscripts: teacher review only."""
from __future__ import annotations
import json, hashlib, argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"knowledge/editorial_review/kb_batch37_scope_repairs.jsonl"
AUDIT=ROOT/"docs/evaluation/KB_BATCH37_SCOPE_REPAIR_AUDIT.json"
MARKDOWN=ROOT/"docs/evaluation/KB_BATCH37_EIGHT_SCOPE_REPAIR_MANUSCRIPTS.md"
PREVIOUS=ROOT/"docs/evaluation/KB_BATCH36_47_LEGACY_SCOPE_AUDIT.json"
# All mathematical content is original. A source page does not attest clause equivalence.
E=[
dict(e="KB33-A-P052-A004",title="收敛数列极限的四则法则和分母非零假设",kind="theorem",
 claim="若实数列a_n→a、b_n→b且两极限有限，则其和、差、积的极限依次是a+b、a−b、ab；仅当b≠0时，尾部b_n非零，商列a_n/b_n趋于a/b。",
 notation=["lim(a_n+b_n)=a+b","lim(a_nb_n)=ab","b≠0 => lim(a_n/b_n)=a/b"],
 assumptions=["a_n、b_n是实数列，分别收敛到有限实数a、b；商的结论另要求b≠0。"],
 steps=[("加减法由误差的三角不等式逐项控制。","|(a_n±b_n)−(a±b)|≤|a_n−a|+|b_n−b|，两个右项均趋于0。"),
 ("积的误差拆分为两个收敛误差与有界系数。","a_nb_n−ab=(a_n−a)b_n+a(b_n−b)且收敛数列b_n有界。"),
 ("若b≠0，取尾部使|b_n−b|<|b|/2，则|b_n|>|b|/2。","反三角不等式给出所有足够大n的非零分母下界。"),
 ("证明倒数差趋0并套用积法则获得商极限。","|1/b_n−1/b|≤2|b_n−b|/|b|²→0。")],
 wrong="分母数列只要收敛就可以把分子和分母极限直接相除",
 counter="a_n=1、b_n=1/n→0，但a_n/b_n=n没有有限极限。",
 why="商法则要求分母极限非零，不能用仅有各项不等于零替代。",
 ex=[("a_n=2+1/n，b_n=1+1/n，商的极限？",["两列趋2、1且b=1≠0。","用商极限定律得到2/1。"],"2","(2n+1)/(n+1)−2=−1/(n+1)→0。"),
 ("a_n=3−1/n，b_n=2+1/n，积的极限？",["两列趋3和2。","乘积极限是3×2。"],"6","积展开为6+1/n−1/n²。")],
 bounds=["尾部商列合法不表示每一个初项商都有定义。"],
 hints=["先核查两列是否各自收敛。","单独检查分母极限是否为0。","商先证明尾部远离零再证明倒数收敛。"],
 near="若a_n=1+2/n、b_n=3−1/n，求其商极限并列出适用条件。",
 far="找一个分母极限为0但商仍趋于常数的数列例子，并解释不矛盾。"),
dict(e="KB33-A-P054-A003",title="空间向量投影与夹角：零向量约束",kind="method",
 claim="在三维欧氏空间中，非零u上的投影为proj_u(v)=(v·u)u/(u·u)，余量与u正交；只有u和v都非零时才能以cosθ=(u·v)/(|u||v|)定义夹角。",
 notation=["proj_u(v)=(v·u)u/(u·u)","cosθ=(u·v)/(|u||v|)"],
 assumptions=["欧氏内积；u≠0；求夹角时v也必须非零。"],
 steps=[("先检验u·u>0，确认投影公式可除。","非零欧氏向量的范数平方严格为正。"),
 ("写v=αu+(v−αu)，要求余量与u垂直。","由(v−αu)·u=0求得α=(v·u)/(u·u)。"),
 ("求夹角时先排除两个零向量并验证cos值的合法范围。","柯西—施瓦茨保证|u·v|≤|u||v|。")],
 wrong="零向量与任意向量也能用投影和夹角公式直接计算",
 counter="u=(0,0,0)时u·u=0发生零除；v=(0,0,0)时夹角分母为0。",
 why="零向量没有方向，点积为零不能据此认定夹角是直角。",
 ex=[("v=(3,4,0)投影到u=(1,0,0)上？",["计算v·u=3、u·u=1。","投影等于3u。"],"(3,0,0)","余量(0,4,0)与u垂直。"),
 ("u=(1,0,0)、v=(0,0,2)的夹角？",["长度分别为1和2且均非零。","内积0，所以cosθ=0。"],"90度","两向量为正交向量。")],
 bounds=["投影到多维子空间需要另行指定合法的子空间或正交基。"],
 hints=["先排除零向量。","投影可以是某个倍数的u。","用余量点积为0求倍数。"],
 near="把(1,2,2)投影到(0,0,3)并检查余量。",
 far="将三维速度分解成沿斜坡方向和垂直斜坡方向的分量。"),
dict(e="KB33-A-P055-A005",title="三维正交变换与平移的欧氏距离保持定理",kind="theorem",
 claim="设Q为实3×3正交矩阵（Q转置乘Q等于单位阵），t为任意三维平移向量，则T(x)=Qx+t保持任意两点间欧氏距离；一般仿射变换并不都保持距离。",
 notation=["QᵀQ=I₃","T(x)=Qx+t","|T(x)−T(y)|=|x−y|"],
 assumptions=["Q是3×3实矩阵并满足QᵀQ=I；x,y,t∈R³。"],
 steps=[("两点像差T(x)−T(y)=Q(x−y)。","相同平移t在相减时抵消。"),
 ("对d=x−y计算|Qd|²=dᵀQᵀQd=dᵀd。","正交矩阵恒等式及欧氏范数的二次型表达。"),
 ("左右范数非负且平方相等，故两点距离相等。","非负实数取平方根保留唯一值。")],
 wrong="任意三维仿射变换都会保持距离",
 counter="变换(x,y,z)↦(2x,y,z)把原本距离为1的(0,0,0)、(1,0,0)变成距离2。",
 why="该缩放矩阵不满足正交条件QᵀQ=I。",
 ex=[("Q(x,y,z)=(-y,x,z)，两点(1,0,0)、(0,0,0)像距？",["Q的列正交且长度都为1。","像为(0,1,0)、(0,0,0)。"],"1","原始两点距离同样为1。"),
 ("T(x,y,z)=(x+3,y−2,−z)，两点(0,0,0)、(0,1,0)像距？",["减去共同平移后只剩反射(0,1,0)。","计算该差的范数为1。"],"1","像点(3,−2,0)与(3,−1,0)距离1。")],
 bounds=["det(Q)=−1的正交变换含反射，不能都称作纯旋转。"],
 hints=["写出变换后两个点的差。","公共平移会相消。","用QᵀQ=I计算差向量的范数平方。"],
 near="验证diag(−1,1,1)在三维中是否保持距离。",
 far="构造一个三维剪切变换的两个点反例并指出矩阵不正交。"),
dict(e="KB33-B-P060-A002",title="空间两直线距离：非平行与平行退化的分支算法",kind="method",
 claim="设空间直线L1:p+su、L2:q+tv且u、v均非零。若u×v非零，距离为|(q−p)·(u×v)|/|u×v|；若u×v=0，距离改用|(q−p)×u|/|u|。",
 notation=["u×v≠0 => d=|(q−p)·(u×v)|/|u×v|","u×v=0 => d=|(q−p)×u|/|u|"],
 assumptions=["空间为R³；u、v均非零；对象为无限延长直线而非有限线段。"],
 steps=[("计算叉积u×v并首先决定两方向是否平行。","叉积为零与非零决定公式中分母合法性。"),
 ("非平行时在公共法向量方向投影q−p并取绝对值。","共同法向量垂直两条直线方向，相交时投影为0。"),
 ("平行时用连接向量对方向u的垂直分量计算距离。","由平行四边形面积公式求高|(q−p)×u|/|u|。")],
 wrong="只要是两条不同空间直线就一定能除以|u×v|",
 counter="L1=(s,0,0)、L2=(t,0,1)为平行直线，u×v=0却具有确定距离1。",
 why="平行时叉积为零，非平行分支公式分母为0。",
 ex=[("L1=(s,0,0)、L2=(0,t,1)求距离。",["u×v=(0,0,1)非零。","q−p=(0,0,1)，法向投影长度1。"],"1","两点(0,0,0)和(0,0,1)给出公垂线。"),
 ("L1=(s,0,0)、L2=(t,3,4)求距离。",["两方向相同，走平行分支。","|(0,3,4)×(1,0,0)|=5。"],"5","垂距来自直角三角形3²+4²。")],
 bounds=["线段需要同时限制两个参数区间，不能把无限直线公式直接套到线段。"],
 hints=["先检查方向向量是否非零。","叉积为零还是非零？","按分支选不同的合法分母。"],
 near="给出两条相交直线和两条平行直线，分别计算距离。",
 far="解释机器人两条有限运动轨迹为何不能只用无限直线距离判断安全性。"),
dict(e="KB33-C-P067-A001",title="加权算术均值与正数调和均值的适用边界",kind="method",
 claim="实数观测x_i的非负权重w_i总和为正时，加权算术平均A=Σw_ix_i/Σw_i；所有具有正权重的x_i>0时调和均值H=Σw_i/Σ(w_i/x_i)。两者解决不同的聚合任务。",
 notation=["A=Σw_ix_i/Σw_i","H=Σw_i/Σ(w_i/x_i)"],
 assumptions=["w_i≥0且Σw_i>0；H要求每个正权重观测严格正；观测有可比的数量单位。"],
 steps=[("核实权重和非零以及测量尺度是否容许数值相加。","纯次序等级标签不能自动认定间距相等。"),
 ("加权算术平均按归一后的权重求样本值加权和。","归一系数w_i/Σw_i之和为1。"),
 ("对等距离行程先合计耗时Σd_i/v_i再用总距离除以总时间。","等距离的总速率是调和平均而不是算术平均。")],
 wrong="任何等级标签和往返速率都可以直接用普通算术平均",
 counter="各走1千米，速率20和60 km/h时平均速率为2/(1/20+1/60)=30，不是40。",
 why="速度的平均基数是时间，等级标签又可能只满足排序尺度。",
 ex=[("60和90分的权重分别为1、3，求加权均值。",["加权总分为60+270=330。","除权重和4。"],"82.5","结果在两分数之间且靠近90。"),
 ("各走1千米，速率20、60 km/h，求全程平均速率。",["总时间1/20+1/60=1/15小时。","总距离2千米除以1/15小时。"],"30 km/h","总时间4分钟，2公里相当于30 km/h。")],
 bounds=["非正速率或权重导致上述调和表达式没有原定的平均速度含义。"],
 hints=["先问要合并的量是什么。","核对权重总和与分母。","等距离速率用总距离除以总时间。"],
 near="计算4与9的等权加权算术均值、调和均值并比较。",
 far="讨论满意度等级编码为1至5时均值的解释为何需要额外的尺度假设。"),
dict(e="KB33-C-P067-A002",title="恒定相对增长率的离散指数模型与人口外推限制",kind="method",
 claim="若P0>0、固定相对增长率r满足1+r>0，且每期满足P_(n+1)−P_n=rP_n，则P_n=P0(1+r)^n；此只是恒定增长假设的推论，不是人口无界增长的经验事实。",
 notation=["P_(n+1)=(1+r)P_n","P_n=P0(1+r)^n"],
 assumptions=["n为非负整数，P0>0，r为不随时间变化的常数，r>−1；实际外推需对迁移、资源及增长率变化另行论证。"],
 steps=[("由相对增量等式移项得乘数递推P_(n+1)=(1+r)P_n。","两边同加P_n，没有改变数学假设。"),
 ("递推展开P1=P0(1+r)、P2=P0(1+r)²；对n归纳。","每一步均用同一个恒定乘数得到P_n=P0(1+r)^n。"),
 ("区分该代数恒等式与长期人口预测可信度。","密度效应或迁入迁出使实际增长率不固定。")],
 wrong="用两个时间点拟合出固定增长率便证明实际人口永远指数增长",
 counter="资源容量为K的离散Logistic模型采用随P_n变化的增长率r(1−P_n/K)，与固定r递推不同。",
 why="模型拟合只在明确假设与观测范围内有意义，不能保证长期外推。",
 ex=[("P0=1000、r=0.05，两期的模型预测值？",["每期乘以1.05。","P2=1000×1.05²。"],"1102.5（模型连续值）","人数取整需要额外规则，计算值不是实际观测人口。"),
 ("P0=1000、r=−0.1，第三期预测值？",["每期因子为0.9。","P3=1000×0.9³。"],"729","0.9³=0.729。")],
 bounds=["实际人口的整数性和计量误差需要另外处理；更改时间步长要换算增长因子。"],
 hints=["说明相对增量与当期人口的比例。","写出第一、二期再归纳。","指出恒定增长率何时可能不成立。"],
 near="P0=200、r=0.1时求第四期模型预测值。",
 far="对比容量限制模型与指数模型在远期预测中各自需要哪些证据。"),
dict(e="KB33-D-P070-A003",title="黄金分割严格比例的代数刻画与审美主张界限",kind="theorem",
 claim="将长度L=a+b分为较长段a和较短段b，要求a>b>0且L/a=a/b，则比值t=a/b唯一等于(1+√5)/2；比值性质不能逻辑推出某艺术作品必然满足此关系。",
 notation=["a>b>0","L=a+b","(a+b)/a=a/b","t=(1+√5)/2"],
 assumptions=["长度a、b为正且a>b，L=a+b；仅证明严格几何比例，不假定作品审美价值。"],
 steps=[("令t=a/b>1，将(a+b)/a=a/b变形为1+1/t=t。","a、b均非零，除法成立。"),
 ("乘以正t得到t²−t−1=0，解得两实根(1±√5)/2。","二次方程求根公式与等价乘法。"),
 ("因为t>1，唯一合法根为(1+√5)/2。","另一个根为负，与较长段除以较短段为正冲突。")],
 wrong="存在黄金比例就证明任何艺术品都满足这种比例且一定更美",
 counter="5与3的分段并非严格黄金分割：5²=25，但5×3+3²=24。",
 why="严格比例是可检验的代数等式，审美判断不属于该定理的结论。",
 ex=[("短段b=2，求严格黄金比例的长段a。",["比值t=a/2=(1+√5)/2。","故a=1+√5。"],"1+√5","a²−2a−4=0。"),
 ("长段5、短段3是否严格满足黄金分割？",["比较a²=25。","比较ab+b²=24，不相等。"],"否","5/3只是近似，不是无理数黄金比例。")],
 bounds=["有限非零整数段的比值是有理数，不可能恰等于黄金比。"],
 hints=["先指定较长与较短段。","把两个比值相等写成t的方程。","解出根后只保留符合t>1的根。"],
 near="给定总长度3，求严格黄金分割较长段的表达式。",
 far="如何评估图像黄金比例的声明？先确定测量点、误差和数据来源。"),
dict(e="KB33-E-P073-A005",title="球面大圆短弧：中心角、弦长及对跖退化",kind="method",
 claim="在半径R>0球面上，对|P|=|Q|=R，中心角θ=arccos(P·Q/R²)∈[0,π]，大圆较短弧长Rθ而弦长2Rsin(θ/2)；对跖点的最短半大圆不唯一。",
 notation=["θ=arccos((P·Q)/R²)","s=Rθ","c=2Rsin(θ/2)"],
 assumptions=["球心取原点，P和Q都位于同一半径R>0的理想圆球表面；非一般椭球或平面曲线。"],
 steps=[("核验两点模均为R，按内积公式取得中心角θ。","柯西—施瓦茨确保内积余弦位于[−1,1]。"),
 ("对经过球心和两点的大圆按弧度制计算Rθ。","半径R的圆弧长公式；弦长另由等腰三角形求得。"),
 ("判别P和Q是否对跖；对跖时通过球轴有无穷多大圆。","球心、两点共线时不能据此唯一确定一个平面。")],
 wrong="球面两点的最短表面路径就是三维直线弦且总是唯一",
 counter="单位球两个正交轴端点弦长√2，但球面大圆短弧长π/2；对跖点有无穷条半大圆路径。",
 why="三维弦通常位于球体内部不是允许的表面路径；对跖点无法确定唯一大圆平面。",
 ex=[("单位球P=(1,0,0)、Q=(0,1,0)短弧长？",["点积0，θ=π/2。","R=1，故短弧为π/2。"],"π/2","对应弦长√2，两者不相等。"),
 ("半径2球上两对跖点的大圆短弧长度？",["点积−4，θ=π。","Rθ=2π。"],"2π；最短路径不唯一","每条过球心轴的大圆半圈长度皆为2π。")],
 bounds=["P=Q时弧长0而最短常路径没有方向；一般地形与椭球须用不同模型。"],
 hints=["先确定两点的球面半径是否相同。","用归一化内积求中心角。","弧长乘半径，并检查对跖的路径唯一性。"],
 near="半径3球上两正交半径端点的大圆短弧长度是多少？",
 far="分析实际地球航线与平面地图直线距离不一致的原因。")
]
def build():
    raw=json.loads(PREVIOUS.read_text(encoding="utf8"))
    mismatches={r["editorial_candidate_id"]:r for r in raw["links"] if r["review_finding"]=="CLAIM_MISMATCH"}
    assert len(E)==len(mismatches)==8
    docs=[]; records=[]
    for r in E:
        code=r["e"].lower().replace("-",".")
        doc=dict(editorial_candidate_id=r["e"],id="math.hs.editorial.batch37."+code,
          kind=r["kind"],title=r["title"],claim=r["claim"],notation=r["notation"],
          assumptions=r["assumptions"],
          reasoning_steps=[dict(claim=c,reason=reason) for c,reason in r["steps"]],
          counterexample=dict(false_claim=r["wrong"],example=r["counter"],explanation=r["why"]),
          worked_examples=[dict(question=q,steps=st,answer=answer,check=check) for q,st,answer,check in r["ex"]],
          boundaries=r["bounds"],misconception=dict(error=r["wrong"],why_wrong=r["why"],
          repair_question="请指出失效的条件并用给定反例核验正确的使用范围。"),
          hint_ladder=r["hints"],transfer=dict(near=r["near"],far=r["far"]),
          review=dict(status="REVIEW_PENDING",reviewer_id=None,reviewed_at=None,review_record=None),
          teacher_solution_visibility="TEACHER_ONLY",source_license="PROJECT_AUTHORED",
          proof_verification="NOT_FORMALLY_CERTIFIED",student_publishable=False)
        docs.append(doc)
        original=mismatches[r["e"]]
        records.append(dict(editorial_candidate_id=r["e"],candidate_track=original["candidate_track"],
          source_page=original["source_printed_page"],editorial_goal=original["original_editorial_goal"],
          historic_mismatched_lesson=original["legacy_lesson_id"],new_staged_manuscript=doc["id"],
          manuscript_sha256=hashlib.sha256(json.dumps(doc,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest(),
          source_anchor="PAGE_ONLY_NOT_CLAUSE_ATTESTED",math_scope_repair_staged=True,
          original_scope_mismatch_still_recorded=True,official_clause_alignment_verified=False,
          mathematical_equivalence_certified=False,teacher_review="REVIEW_PENDING",
          student_publishable=False,student_full_solution_exposed=False,
          teacher_only_worked_examples=2,graduated_hints=3,near_far_transfer_staged=True))
    assert set(mismatches)=={d["editorial_candidate_id"] for d in docs}
    seed="".join(json.dumps(d,ensure_ascii=False,separators=(",",":"))+"\n" for d in docs)
    audit=dict(schema_version="kb-batch37-mismatch-repair-v1",
      prior_scope_audit_sha256=hashlib.sha256(PREVIOUS.read_bytes()).hexdigest(),
      manuscript_seed_sha256=hashlib.sha256(seed.encode()).hexdigest(),
      summary=dict(historical_associations=47,historical_mismatches=8,
        mismatch_goals_with_new_staged_manuscript=8,other_noncertified_associations=39,
        officially_certified_associations=0,unchanged_deep_drafts=287,
        previously_staged_review_manuscripts=49,new_review_manuscripts=8,
        all_separate_review_manuscripts=57,new_teacher_side_examples=16,
        project_editorial_candidates_not_official_denominator=313,
        official_denominators={k:None for k in ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")},
        uncertified_historical_proof_steps=538,unresolved_conflicts=10,
        approved_by_teacher=0,published_to_student=0,formally_certified_proofs=0),
      records=records,student_retrieval_projection=dict(index_additions=0,student_documents=[],
        student_teacher_solutions=[],status="NOT_PUBLISHED"),
      limitation="Page-level project-authored objectives, not official syllabus clause attestation; staged content not approved.")
    lines=["# Batch37｜八项数学范围错配的原创完整审核稿","",
      "仅教师审核：REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED。页码来源并非课标逐条认证，禁止学生端索引。",""]
    for i,(doc,rec) in enumerate(zip(docs,records),1):
        lines += [f"## {i:02d}. {doc['title']}","",
           f"来源编辑目标：{rec['editorial_candidate_id']}；方向：{rec['candidate_track']}；页码：{rec['source_page']}；历史错配讲义：{rec['historic_mismatched_lesson']}。","",
           f"项目原创教学目标：{rec['editorial_goal']}","",
           f"类型：{doc['kind']}；数学记号：{'；'.join(doc['notation'])}。","",
           "### 数学陈述、完整使用条件","",doc["claim"],"",
           *["- "+s for s in doc["assumptions"]],"","### 数学推导与逐步依据",""]
        lines += [f"{n}. {s['claim']} **依据**：{s['reason']}" for n,s in enumerate(doc["reasoning_steps"],1)]
        lines += ["","### 错误主张、反例与边界","",
          "错误主张："+doc["counterexample"]["false_claim"],"",
          "具体反例："+doc["counterexample"]["example"],"",
          "失效原因："+doc["counterexample"]["explanation"],"",
          "适用边界："+ "；".join(doc["boundaries"]),"",
          "### 教师专用例题与完整解答",""]
        for n,ex in enumerate(doc["worked_examples"],1):
            lines += [f"**例题{n}**：{ex['question']}","",f"1. {ex['steps'][0]}",f"2. {ex['steps'][1]}",
              "答案："+ex["answer"],"独立复核点："+ex["check"],""]
        lines += ["### 分级启发提示（仅草稿，不发布）",""]
        lines += [f"{n}. {h}" for n,h in enumerate(doc["hint_ladder"],1)]
        lines += ["","近迁移："+doc["transfer"]["near"],"", "远迁移："+doc["transfer"]["far"],"",
          "本审核稿的完整证明未形式认证，也未有教师签字；不能因字段完整而宣布官方课程覆盖。",""]
    return {SOURCE:seed,AUDIT:json.dumps(audit,ensure_ascii=False,indent=2)+"\n",MARKDOWN:"\n".join(lines).rstrip("\n")+"\n"}
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
    outputs=build()
    if args.check:
        stale=[str(p) for p,v in outputs.items() if not p.exists() or p.read_text(encoding="utf8")!=v]
        if stale:raise SystemExit("STALE_BATCH37:"+",".join(stale))
        print("Batch37 all three generated artifacts reproduced; 8 teacher-only manuscripts, 16 examples")
    else:
        for path,value in outputs.items():
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value,encoding="utf8")
        print("Batch37: written 8 original teacher-only repairs, 16 worked examples, audit + markdown")
if __name__=="__main__":main()
