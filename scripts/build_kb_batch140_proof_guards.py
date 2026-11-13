#!/usr/bin/env python3
"""Batch140: source-fingerprinted, teacher-pending P0 step reviews.

Reviews are human-authored mathematical *obligations*, never formally certified
proof steps. The independent exact oracle lives in check_kb_batch140_math.py.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "scripts")]
from app.deep_knowledge import lessons
import build_kb_batch128_p0_proof_guards as baseline

QUEUE = ROOT / "docs/evaluation/KB_BATCH80_PROOF_QUEUE.json"
OUT = ROOT / "docs/evaluation/KB_BATCH140_P0_STEP_REVIEW.json"
MD = ROOT / "docs/evaluation/KB_BATCH140_P0_STEP_REVIEW.md"
LOCK = ROOT / "docs/evaluation/KB_BATCH128_P0_PROOF_GUARDS.json"

# Each row: immutable historical step identifier; *necessary condition*;
# the mathematical justification to inspect; a concrete boundary/failed
# precondition; and an independently checked oracle case key.
CASES = [
("math.hs.geometry.circle-intersections#3",
 "两圆半径 r₁,r₂ 都严格正，中心距 d>0；三角形边长不等式只约束不同圆心的公共点。",
 "对任一公共点P，距离 C₁P=r₁、C₂P=r₂ 与 C₁C₂=d 同时成立，因此由距离三角不等式得 |r₁-r₂|≤d≤r₁+r₂；但不等式单独并不足以推出公共点唯一或个数。",
 "同心且半径均为2时 d=0，三条长度是2、2、0的退化三角形，却有整圆无限多公共点；不能套用普通相切分类。",
 "circle_triangles"),
("math.hs.geometry.circle-intersections#4",
 "两圆均非退化、圆心不重合；等号条件还须区分外切 d=r₁+r₂ 与内切 d=|r₁-r₂|。",
 "将连心线取作横轴，解两圆方程相减得到公共弦的固定横坐标；竖坐标平方正则双交点，零则单切点，负则无实交点。完全重合是另外一类。",
 "圆心重合且半径相等时不管等号形式如何，公共点都是无穷多个；若半径不等则无公共点。",
 "circle_count"),
("math.hs.geometry.parabola-focus#3",
 "p>0、焦点为(p,0)、准线 x=-p，并且采用欧氏距离且距离平方皆非负。",
 "由 y²=4px 推得 (x-p)²+y²=(x+p)²；两侧是点到焦点和准线距离的平方，非负距离平方相等可恢复原距离相等，证明逆向包含。",
 "若 p=0，焦点落在准线上，方程 y²=0 给出整条x轴，但这不是通常的非退化抛物线；模型前提已失效。",
 "parabola_converse"),
("math.hs.quadratic.discriminant-roots#3",
 "a≠0并在实数域讨论一元二次方程，判别式 Δ=b²-4ac 严格大于零。",
 "配方得到 (2ax+b)²=Δ；取两实平方根分支，再除以非零2a，获得两个不同实根。负判别式不能在实数域照此取根。",
 "a=0 时所谓二次式退化为线性方程，2a为零，根公式无法使用；Δ>0也不能替代a≠0。",
 "quadratic_discriminant"),
("math.hs.vector.pythagorean-dot#3",
 "u、v位于同一个有限维实内积空间，向量加法、数量积与范数由同一正定内积诱导。",
 "展开 ‖u+v‖²=‖u‖²+2(u·v)+‖v‖²；如果平方范数恰好可加，则对两侧作等式移项和除2，得到 u·v=0。这是充要条件的逆向。",
 "若拿两条不同维度的坐标向量拼接后直接做加法，‖u+v‖²没有本命题意义；也不能用零向量夹角作为垂直证明。",
 "pythagoras_converse"),
("math.hs.logarithm.product-law#3",
 "对数底数 a>0 且 a≠1，两个实数真数 x,y 都严格正，并在实数范围内使用幂函数的逆运算。",
 "令u=log_a x、v=log_a y，x=a^u、y=a^v，故xy=a^(u+v)>0；在正值域取a为底的对数，得log_a(xy)=u+v。",
 "x=-2,y=-4 时乘积8为正，但 log_a(-2) 和 log_a(-4) 在实数域不存在；仅xy>0远远不够。",
 "log_product"),
("math.hs.geometry.ellipse-parameter#2",
 "椭圆半轴 a,b 必须严格正；标准方程是 x²/a²+y²/b²=1。",
 "由标准方程将 x/a 与 y/b 视为两个实数，平方和为1，故对应单位圆点；因此存在角t使它们分别等于cos t、sin t。反方向要另行代入核验。",
 "a=0或b=0时分母未定义，不能声称退化线段也被标准椭圆参数式无条件覆盖。",
 "ellipse_param"),
("math.hs.inequality.amgm#3",
 "a,b为非负实数，平方根是非负的算术平方根，等号条件需要该平方根的单射性。",
 "AM-GM差量等于(√a-√b)²/2；其为0等价于√a=√b，由非负平方根的单射性得到a=b，且相等时差量确为零。",
 "a=-1,b=-1 时平均值有实数意义，但实数平方根不存在；不能沿用本等号证明。",
 "amgm_equality"),
("math.hs.function.quadratic-vertex#2",
 "原式确为二次函数，即二次项系数a≠0，所有自变量和系数都位于实数域，且代数除法合法。",
 "x²+(b/a)x 配成(x+b/(2a))²-b²/(4a²)属于严格代数恒等式，扩大平方并消去新增常数即可复原原表达式。",
 "a=0时 b/a 和 b/(2a) 无定义；即使原式仍代表直线，也不存在二次函数顶点公式。",
 "vertex_completion"),
("math.hs.function.quadratic-vertex#4",
 "a≠0 且自变量可取全体实数；平方项系数的符号决定最大值或最小值。",
 "二次函数写成a(x+b/(2a))²+c-b²/(4a)后，平方非负；当a>0在顶点取全局最小值，当a<0取全局最大值。",
 "若定义域改成x≥1，而原顶点在x=0，不能仍说最大或最小在顶点处于该定义域内取得。",
 "vertex_extremum"),
("math.hs.logarithm.inverse#2",
 "实数对数底数a>0且a≠1；x,y作为真数需严格正，指数函数映射的值域才覆盖所取真数。",
 "按照实对数定义，u=log_a x 等价于 a^u=x；指数在实数域严格单调并满射正实数，逆向关系成立；y同理。",
 "x=0或a=1时逆函数关系没有合法实对数；不能把 log_1 x 当普通实数函数。",
 "log_inverse"),
("math.hs.trig.sum-angle#1",
 "欧氏平面使用正交、同尺度、固定正向直角坐标，角度使用与三角函数一致的约定。",
 "旋转变换把e₁变为(cosα,sinα)，e₂变为(-sinα,cosα)，两基向量的像构成矩阵的两列，由线性性确定任意向量的像。",
 "若把坐标轴换成斜基后仍直接套同一矩阵，通常不会保持该斜基坐标所表达的实际欧氏距离。",
 "rotation_matrix"),
("math.hs.vector.dot-product#4",
 "a与b均为非零实欧氏向量，夹角θ∈[0,π]由它们的非零方向唯一确定，模长乘积才能作为分母。",
 "将a·b=|a||b|cosθ两端除以严格正的模长乘积，得到点积为零当且仅当cosθ=0；指定的角域中唯一零点为π/2。",
 "a=0时点积为零仍成立，但夹角根本不存在；不得将其宣称为直角关系。",
 "dot_angle"),
("math.hs.space.basis-three-unique#2",
 "M是实数域的3×3方阵，三列为候选空间基向量，矩阵秩可按通常线性代数定义计算。",
 "如果齐次方程 Mv=0 只有零解，则零空间维数0，由秩-零度定理可知秩3；故行列式非零且存在逆矩阵。必须处理方阵维数。",
 "仅3×2矩阵的零空间平凡不能推出3×3行列式非零，更不能求不存在的方阵逆。",
 "basis_three"),
("math.hs.calculus.quotient-rule#2",
 "v在x₀可导且v(x₀)≠0；在x₀附近应选取v持续非零的邻域。",
 "可导蕴含连续，所以v(x)→v(x₀)非零，求导的差商分母趋向v(x₀)²>0；按极限定理得到(1/v)'=-v'/v²。",
 "v(x₀)=0时倒数函数甚至在该点未定义，比如v(x)=x、x₀=0。",
 "reciprocal_derivative"),
("math.hs.calculus.fermat-stationary#2",
 "x₀是定义域的内点且f在x₀有局部最大值，并有双侧极限需要的邻域。",
 "局部极大意味着足够小h时f(x₀+h)-f(x₀)≤0；h正时差商非正，h负时除负数要反号所以差商非负。",
 "只在右侧有定义的端点最大值不能依此建立负h差商，不能推导导数等于零。",
 "fermat_sign"),
("math.hs.vector.cauchy-schwarz#2",
 "u,v属于同一正定实内积空间，t为任意实数，范数平方必须总为非负实数。",
 "双线性和对称性展开 (u-tv)·(u-tv)=‖u‖²-2t(u·v)+t²‖v‖²，对任意实t非负；本步尚未除以‖v‖²。",
 "若把所谓范数平方写成不正定的伪内积，则展开虽成立却不能断言对任意t非负。",
 "cauchy_expand"),
("math.hs.vector.cauchy-schwarz#3",
 "v≠0保证‖v‖²严格正，允许取t=(u·v)/‖v‖²并进行正数乘法。",
 "把此t代入上一非负二次式，化简后得到‖u‖²-(u·v)²/‖v‖²≥0；两边乘严格正的‖v‖²可保留不等号方向。",
 "v=0时不等式结论依然平凡成立，但此取t与分式推导无定义，必须独立处理零向量。",
 "cauchy_minimize"),
("math.hs.vector.cauchy-schwarz#4",
 "以真实欧氏正定内积定义范数，v非零时t按前一步取值；v零时单独处理。",
 "等号与‖u-tv‖²=0等价；正定性使u=tv。v=0时任意u与v仍线性相关，且点积不等式为0=0。",
 "用非正定二次型时存在非零零长度向量，零范数便不能推出两向量相等。",
 "cauchy_equality"),
("math.hs.probability.expectation-linearity#3",
 "X,Y在同一概率空间且可积，即E|X|、E|Y|都有限；a,b为有限实常数。",
 "利用期望积分的线性性分别抽出常数得到E[aX+bY]=aE[X]+bE[Y]；整个推导不需要独立性。",
 "若X是Cauchy随机变量，E[X]不存在，不能把未定义的期望拆开和重组；独立也无法弥补不可积。",
 "expectation_linearity"),
("math.hs.elective.linear.rank-vectors#3",
 "A是3×3实方阵，det A=0；列向量按相同基底表示，且列数正好等于方阵维数。",
 "由方阵奇异得到rank(A)<3；秩-零度定理保证至少一维非零零空间，存在v≠0使Av=0，即列向量线性相关。",
 "非方阵没有3×3行列式，即便列数不等于行数也不能按此公式断言唯一解。",
 "rank_vectors"),
("math.hs.elective.statistics.ols-two-parameter#1",
 "n≥1，所有x_i,y_i为有限实数且考虑带截距的平方残差目标；固定斜率b。",
 "目标S(a,b)=Σ(y_i-a-bx_i)² 对a的一阶导数为-2Σ(y_i-a-bx_i)，二阶导数2n>0，故唯一最佳截距a=ȳ-bx̄。",
 "当n=0时均值未定义、曲率为0，任何截距的空和都相同，不存在唯一最佳截距。",
 "ols_intercept"),
("math.hs.elective.model.parametric-circle#3",
 "半径r>0，角参数t用弧度制且路径为x=r cos t、y=r sin t。",
 "按弧度求导得到(-r sin t,r cos t)，速度大小r√(sin²t+cos²t)=r；严格正半径保证速度非零。",
 "r=0时路径退化常点，速度大小0不能再宣称为非零匀速；若角参数以度数变化导数也需比例因子。",
 "parametric_circle"),
("math.hs.elective.sequence.epsilon-n#2",
 "n,N均为正整数并且已经选定满足1/N<ε的整数N，ε>0，所有比较都仅发生于正实数域。",
 "n≥N>0时倒数函数在正实数域严格递减，故0<1/n≤1/N<ε，证明所有足够大的n满足界限。",
 "若取N=0则1/N无意义；若ε=0则不存在任何正整数N使严格正的1/N<ε。",
 "epsilon_n"),
]

def fail(message: str):
    raise ValueError("Batch140 P0 audit: " + message)

def encode(obj: object) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"

def get_source():
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    existing = json.loads(LOCK.read_text(encoding="utf-8"))
    return queue, existing

def build():
    queue, old = get_source()
    source = {r["id"]: r for r in queue["step_review_queue"]}
    originals = {r.id: r for r in lessons()}
    old_ids = {r["historical_proof_step_id"] for r in old["records"]}
    if len(old_ids) != 20 or len(CASES) != 24:
        fail("24 new / 20 old source-locked cards required")
    if len({x[0] for x in CASES}) != len(CASES):
        fail("duplicate historical step")
    records = []
    for sid, condition, proof, counter, oracle in CASES:
        if sid in old_ids or sid not in source:
            fail("historical step missing or already guarded: " + sid)
        ledger = source[sid]
        if ledger["review_card_id"] is not None or ledger["risk_priority"] != "P0_GUARD_AND_COUNTEREXAMPLE" or ledger["formal_certification"] != "NOT_FORMALLY_VERIFIED":
            fail("not an unguarded historical P0 item: " + sid)
        name, _, index = sid.rpartition("#")
        if name not in originals:
            fail("missing original lesson: " + name)
        step = originals[name].proof_steps[int(index)-1]
        sha = hashlib.sha256((step.claim + "\x00" + step.reason).encode("utf-8")).hexdigest()
        if sha != ledger["source_sha256"]:
            fail("historical proof step changed without review: " + sid)
        if not all(len(s) >= 32 for s in (condition, proof, counter)):
            fail("unfinished mathematical review: " + sid)
        records.append({
            "historical_proof_step_id":sid,
            "historical_step_sha256":sha,
            "original_claim":step.claim,
            "original_reason":step.reason,
            "historical_risk_groups":ledger["risk_groups"],
            "necessary_preconditions":condition,
            "step_justification_review":proof,
            "non_applicable_boundary":counter,
            "independent_oracle_key":oracle,
            "finite_example_verdict":"EXACT_FINITE_WITNESS_ONLY",
            "invalid_condition_verdict":"PRECONDITION_NOT_ESTABLISHED",
            "quantified_general_proof_certified":False,
            "original_step_formally_verified":False,
            "teacher_review_status":"REVIEW_PENDING",
            "teacher_signature":None,
            "student_publishable":False,
        })
    all_p0 = {r["id"] for r in source.values() if r["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE"}
    old_guarded = {r["id"] for r in source.values() if r["risk_priority"]=="P0_GUARD_AND_COUNTEREXAMPLE" and r["review_card_id"]}
    guarded = old_guarded | old_ids | {r["historical_proof_step_id"] for r in records}
    # Critically, KB28/29/30 already authored *editorial* records for all 127
    # KB80 P0 IDs.  The 47 below are missing the newer source-locked guard-card
    # shape; they are NOT 47 historically unreviewed mathematical steps.
    legacy_files=(
      ("KB_BATCH28_P0_CONDITION_REVIEW.json","reviewed_step_proposals"),
      ("KB_BATCH29_P0_CONDITION_REVIEW.json","new_editorial_step_proposals"),
      ("KB_BATCH30_P0_COMPLETION_AUDIT.json","batch30_new_editorial_rows"),
    )
    legacy_groups=[]
    for filename,field in legacy_files:
        item=json.loads((ROOT/"docs/evaluation"/filename).read_text(encoding="utf-8"))
        group={row["risk_step_id"] for row in item[field]}
        if len(group)!=len(item[field]):fail("duplicate historic editorial step: "+filename)
        legacy_groups.append(group)
    if len(set.union(*legacy_groups))!=127 or set.union(*legacy_groups)!=all_p0 or sum(map(len,legacy_groups))!=127:
        fail("historic KB28/29/30 P0 editorial coverage/lineage drift")
    previous_editorial_batches={"KB_BATCH28":35,"KB_BATCH29":48,"KB_BATCH30":44}
    if [len(q) for q in legacy_groups]!=list(previous_editorial_batches.values()):
        fail("historic editorial count drift")
    unguarded = sorted(all_p0 - guarded)
    if len(all_p0)!=127 or len(old_guarded)!=36 or len(guarded)!=80 or len(unguarded)!=47:
        fail("P0 denominator/card union drift")
    report = {
       "schema":"kb140-source-locked-p0-review/1",
       "old_unverified_proof_step_count":len(source),
       "p0_step_denominator":len(all_p0),
       "initial_source_review_cards":len(old_guarded),
       "batch128_additional_cards":len(old_ids),
       "batch140_additional_cards":len(records),
       "p0_with_distinct_review_cards":len(guarded),
       "p0_without_review_cards":len(unguarded),
       "earlier_kb28_29_30_editorial_records":previous_editorial_batches,
       "p0_with_any_earlier_editorial_review":len(set.union(*legacy_groups)),
       "p0_without_any_earlier_editorial_review":0,
       "source_card_lineage_not_global_first_review_count":True,
       "remaining_p0_step_ids":unguarded,
       "unresolved_conflicts":queue["unresolved_conflicts"],
       "all_steps_formally_certified":0,
       "teacher_approved":0,
       "student_authoritative":0,
       "independent_finite_cases_expected":2*len(records),
       "records":records,
    }
    validate(report)
    return report

def validate(report):
    if report["p0_step_denominator"]!=127 or report["old_unverified_proof_step_count"]!=538:
        fail("invented historical count")
    if report["batch140_additional_cards"]!=24 or report["p0_with_distinct_review_cards"]!=80 or report["p0_without_review_cards"]!=47:
        fail("invented guard coverage")
    if report["earlier_kb28_29_30_editorial_records"]!={"KB_BATCH28":35,"KB_BATCH29":48,"KB_BATCH30":44} or report["p0_with_any_earlier_editorial_review"]!=127 or report["p0_without_any_earlier_editorial_review"]!=0 or report["source_card_lineage_not_global_first_review_count"] is not True:
        fail("misrepresented prior editorial coverage")
    if report["independent_finite_cases_expected"]!=48:
        fail("invented witness count")
    if report["all_steps_formally_certified"]!=0 or report["teacher_approved"]!=0 or report["student_authoritative"]!=0:
        fail("forged approval/proof")
    if len(report["records"])!=24 or len({r["historical_proof_step_id"] for r in report["records"]})!=24:
        fail("duplicate review cards")
    original_steps={obj.id:obj for obj in lessons()}
    original_queue={r["id"]:r for r in json.loads(QUEUE.read_text(encoding="utf-8"))["step_review_queue"]}
    for r,case in zip(report["records"],CASES):
        sid,condition,proof,counter,oracle=case
        name,_,num=sid.rpartition("#")
        step=original_steps[name].proof_steps[int(num)-1]
        digest=hashlib.sha256((step.claim+"\x00"+step.reason).encode("utf-8")).hexdigest()
        if r["historical_proof_step_id"]!=sid or r["historical_step_sha256"]!=digest or digest!=original_queue[sid]["source_sha256"]:
            fail("proof step source SHA/canonical identity drift")
        if any((r["original_claim"]!=step.claim,r["original_reason"]!=step.reason,
                r["necessary_preconditions"]!=condition,r["step_justification_review"]!=proof,
                r["non_applicable_boundary"]!=counter,r["independent_oracle_key"]!=oracle,
                r["historical_risk_groups"]!=original_queue[sid]["risk_groups"])):
            fail("altered mathematical premise or independent witness reference")
        if r["teacher_review_status"]!="REVIEW_PENDING" or r["teacher_signature"] is not None or r["student_publishable"] is not False or r["quantified_general_proof_certified"] is not False or r["original_step_formally_verified"] is not False:
            fail("premature mathematical or teacher approval")
        if not r["historical_step_sha256"] or not r["necessary_preconditions"] or not r["step_justification_review"] or not r["non_applicable_boundary"]:
            fail("incomplete review")
    return True

def render(report):
    parts = [
        "# Batch140｜历史P0证明步骤前提与有限验证审查（教师候审）",
        "",
        "**这是24条原始证明步骤的逐项数学审查卡，不是24条已认证的形式化证明。**",
        "538条历史步骤中的KB80定义P0共127项；KB28/29/30已给全部127项建立候审编辑记录（35+48+44），但这些不构成证明认证。",
        "在另外的KB80源卡体系中：原36张、Batch128增20张、本批新增24张严密引用及独立SymPy验证卡；该体系合计80张，剩余47项缺此类型的新卡，**并非47条从未审查过**。",
        "学生权威发布0，正式教师审核0，形式化证明认证0；未关闭10项数学冲突。",
        "原始claim与reason直接以SHA256锁定到项目既有证明步骤，不复制课标原文。",
        "",
    ]
    for r in report["records"]:
        parts += [
          "## "+r["historical_proof_step_id"], "",
          "历史步骤SHA-256: "+r["historical_step_sha256"],
          "原声明："+r["original_claim"],
          "原依据："+r["original_reason"],
          "### 必须先建立的前提",r["necessary_preconditions"],
          "### 逐步合法性审查",r["step_justification_review"],
          "### 不适用边界与反例",r["non_applicable_boundary"],
          "### 有限精确验证",r["independent_oracle_key"]+
          "：1项合法输入与1项前提失效输入；本身不形成量词层面的证明。","",
        ]
    parts += ["## 历史剩余审查队列","", "剩余47条缺少KB80/128/140独立来源卡，但已存在KB28/29/30较早的编辑记录；仍不得自动标记已验证：",""]
    parts += ["- "+x for x in report["remaining_p0_step_ids"]]
    return "\n".join(parts)+"\n"

def main():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write",action="store_true")
    mode.add_argument("--check",action="store_true")
    args=parser.parse_args()
    data=build()
    if args.write:
        OUT.write_text(encode(data),encoding="utf-8")
        MD.write_text(render(data),encoding="utf-8")
    else:
        if json.loads(OUT.read_text(encoding="utf-8"))!=data:
            fail("frozen P0 review artifacts have drifted")
        if MD.read_text(encoding="utf-8")!=render(data):
            fail("frozen complete reasoning has drifted")
    print("Batch140: 24 P0 source-locked review cards, 80/127 guarded; 47 unguarded; zero formal certification")

if __name__ == "__main__":
    main()
