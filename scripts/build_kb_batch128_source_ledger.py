#!/usr/bin/env python3
"""Batch128: 28 new source-locked interpretations / 56 provisional subtargets.

An editorial subtarget is never an officially certified curriculum atom.
The exact original PDF stays on the authorised Mac and is not redistributed.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch127_source_review as prior

OUT = ROOT / "docs/evaluation/KB_BATCH128_SEMANTIC_SPLIT_LEDGER.json"
MD = ROOT / "docs/evaluation/KB_BATCH128_SEMANTIC_SPLIT_LEDGER.md"
LOCKS = ROOT / "curriculum/highschool_math/k00_batch128_source_line_locks.json"

# ID suffix, evidence class, source-specific editorial interpretation,
# falsification/definition risk, 2 proposed teaching subtargets.
# The subtargets are ORIGINAL editorial work, not quoted standard clauses.
SPECS = [
("120-c103","DIRECT_NUMBERED","课程以物理功引入数量积的概念和计算要求，应分别教学几何定义与代数计算。","夹角的定义需要非零向量；零向量的数量积仍可计算，不得据此定义零向量夹角。","数量积的几何定义","数量积的坐标计算"),
("120-c104","DIRECT_NUMBERED","投影向量的意义与使用数量积判断平面向量垂直是相邻但不同的课程要求。","投影目标方向不可取零向量；内积为零推垂直时应澄清零向量的角度无定义。","非零方向的正交投影","数量积为零与垂直"),
("120-c105","DIRECT_NUMBERED","平面向量基本定理的独立性条件与正交坐标表示需要拆开审查。","两个基向量必须不共线才有唯一分解；正交坐标系是特殊基而不是所有基。","不共线基向量的唯一分解","直角坐标系的正交分量"),
("120-c106","DIRECT_NUMBERED","坐标数量积与基于坐标的共线或垂直判定宜作为不同教学目标。","判定两非零向量夹角需分母非零；二维行列式为零与零向量共线术语要分清。","坐标数量积与夹角","坐标平行垂直判据"),
("119-s07","DIRECT_NUMBERED","本段从平均变化率到瞬时变化率，再到切线几何意义，是有明确先修链的复合课程要求。","差商极限未必存在；点处导数与左右差商极限的条件不能混同。","导数的差商极限定义","切线斜率的几何解释"),
("119-s08","DIRECT_NUMBERED","基本初等导数与仿射复合形式的求导要求应分开；不能自动推广至任意复合链式法则。","根号与倒数函数必须限制定义域；所列复合仅限 f(ax+b) 不可无证扩张到所有复合。","常见函数导数与定义域","仿射复合函数求导"),
("119-s09","DIRECT_NUMBERED","利用导数研究单调性是编号要求，对不超过三次多项式的计算范围有明确限定。","单点导数符号不证明整个区间严格单调；导数零点必须分区间分析。","导数符号与单调区间","三次以内多项式单调分析"),
("119-s10","DIRECT_NUMBERED","极值必要充分条件和闭区间端点比较是两项不同的导数应用能力。","局部驻点不一定是极值，闭区间全局最大最小值必须同时考虑端点。","驻点与局部极值判定","闭区间端点与全局最值"),
("119-a05","DIRECT_ELECTIVE_REQUIREMENT","选修A列出连续定义和闭区间有界、介值性质，可构造概念及定理两类候审对象。","连续性必须在定义域和区间上陈述；介值结论需要闭区间连续，不能仅由端点异号推出。","点与区间上的连续性","介值性质及二分应用"),
("119-a06","EXPLICIT_PROOF_REQUIRED","选修A明确提出理解并证明拉格朗日中值定理，复合求导与证明应用可拆开。","中值定理要求闭区间连续和开区间可导；不能用不满足前提的函数证明不等式。","拉格朗日中值定理的证明","中值定理用于单调与不等式"),
("120-a101","DIRECT_ELECTIVE_REQUIREMENT","选修A分别提出空间内积与外积的几何意义，正交性与有向面积不应混成一种运算。","叉积的取向依赖空间方向与顺序，内积是标量；不得把向量值外积当标量。","空间内积与夹角","空间外积与方向"),
("120-a102","DIRECT_ELECTIVE_REQUIREMENT","该条包含空间向量投影和分解，可以分为唯一投影与一般线性分解问题。","投影的分母依赖非零目标向量；一般分解的唯一性需要独立基或正交条件。","三维正交投影","空间基向量分解"),
("120-b101","DIRECT_ELECTIVE_REQUIREMENT","选修B确实要求了解连续随机变量及其分布，但密度积分是可能的教材细化而非整段原文强制公式。","离散概率质量与连续密度不能互换；点概率零不意味着事件不可能。","连续型随机变量的分布","密度与区间概率的候审扩展"),
("120-b102","DIRECT_ELECTIVE_REQUIREMENT","本段列出均匀、正态、卡方与t分布及数字特征，可拆参数约束和矩存在性两类。","t分布自由度不足时均值或方差不存在，不能无条件套用全部均值方差公式。","常见连续分布参数","不同自由度的矩存在条件"),
("120-b103","CROSS_PAGE_PENDING","选修B关于二维离散随机变量和数字特征的叙述跨页，必须核对下一页才能冻结整段归属。","本页末尾在独立性处截断；联立分布不能仅凭边缘分布唯一恢复，缺失内容不得推测。","二维离散联合分布","协方差相关系数与依赖"),
("120-b104","DIRECT_ELECTIVE_REQUIREMENT","选修B明确要求了解二维正态的联合分布及参数意义，公式细节属于候审扩写。","相关系数绝对值为1时联合分布奇异，常规二维密度公式不适用。","二维正态联合分布参数","相关参数与退化边界"),
("120-ec101","THEMATIC_ELECTIVE_REQUIREMENT","选修C的推理专题明确并列演绎、归纳、类比及必然与或然推理，宜分形式与证据级别。","有限举例不能证明全称命题；演绎规则有效也不保证未证前提为真。","演绎推理的有效性","归纳类比的或然性"),
("120-ec102","THEMATIC_ELECTIVE_REQUIREMENT","本段要求认识常见证明方法，但并未给出唯一固定方法名清单。","不能据此把反证法或逆否命题法作为全国固定清单，也不能循环论证。","直接证明的前提链","反证法作为可选教学展开"),
("120-ec103","THEMATIC_ELECTIVE_REQUIREMENT","选修C公理化专题提到独立性相容性完备性，教学应分别解释不同元性质。","一致性和完备性并非同义；跨系统讨论必须声明形式系统和语言。","公理体系相容性","独立性与完备性区别"),
("120-ec104","THEMATIC_ELECTIVE_REQUIREMENT","存贷款情境对应指数复利与等额本金两个独立模型，均涉及现实参数假设。","真实贷款常有费用利率变动与提前还款；等额本金不是等额本息。","复利指数增长模型","等额本金还款模型"),
("120-ed101","THEMATIC_ILLUSTRATION","选修D以建筑与艺术呈现不同几何对称，可做变换性质的活动题但不证明现实对象严格对称。","镜像轴对称、中心对称、平移对称不可互换；视觉近似不能当精确变换恒等。","轴对称变换实例","中心对称与平移对称比较"),
("120-ed102","THEMATIC_ILLUSTRATION","选修D以自然周期和艺术图案作示例，不提供每个现实过程的严格周期函数证明。","有限重复片段不能证明所有实数时刻具有同一周期；观测趋势可能只是准周期。","周期函数严格定义","现实周期近似建模"),
("120-ed103","THEMATIC_ILLUSTRATION","黄金分割和斐波那契数列在此属于和谐美的联系示例，并非对自然形态的普适定理。","不得宣称全部建筑物或向日葵均满足精确黄金比例；需要量化测量误差。","黄金分割比例","斐波那契比值的极限联系"),
("120-ed104","THEMATIC_ILLUSTRATION","选修D用纯音和正弦函数介绍振幅频率及信号叠加，可形成理想化模型。","现实音色由谱组成且含噪声；响度不是振幅的简单线性测量值。","纯正弦信号频率","振幅与声音测量假设"),
("120-ee101","LOCAL_SCHOOL_OPTION","课标明确选修E由学校按需求开发或选用，因此示例主题不能成为全国统一必学原子。","必须保留学校自行选用和学生适用范围，不得借此减少或增加全国必修课程分母。","学校自选课程分类","地方选修与全国必修边界"),
("120-ee102","LOCAL_SCHOOL_OPTION","机器人与数学只是选修E拓展视野示例，可开发坐标系教学但需独立作者设定目标。","机器人具体运动学公式未由这条示例逐项规定，不能标记为全国必学知识。","机器人坐标系建模示例","刚体坐标变换候审扩展"),
("120-ee103","LOCAL_SCHOOL_OPTION","球面几何仅作为选修E示例主题，球面大圆距离属于可能的自编扩展。","球面两点最短路径可能非唯一，不能把平面欧氏直线直接替代球面测地线。","球面几何自选主题","大圆最短路径示例"),
("120-ee104","LOCAL_SCHOOL_OPTION","初等数论属于选修E示例方向，欧几里得算法须作为原创可选教学内容单独归类。","除法算法依赖正模或除数非零；模零、负模约定与停止条件必须明确。","整除和最大公约数示例","欧几里得算法示例"),
]

TRACKS = ("COMPULSORY", "SELECTIVE_COMPULSORY", "ELECTIVE_A",
          "ELECTIVE_B", "ELECTIVE_C", "ELECTIVE_D", "ELECTIVE_E")
CLASS = {"DIRECT_NUMBERED", "DIRECT_ELECTIVE_REQUIREMENT",
         "EXPLICIT_PROOF_REQUIRED", "CROSS_PAGE_PENDING",
         "THEMATIC_ELECTIVE_REQUIREMENT", "THEMATIC_ILLUSTRATION",
         "LOCAL_SCHOOL_OPTION"}
def require(ok, message):
    if not ok:
        raise ValueError(message)
def encode(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
def build():
    old, candidates = prior.originals()
    prior_ids = {"hs-semantic-pilot-"+x[0] for x in prior.DETAILS}
    prior_ids |= {x[0] for x in prior.previous.SPECS}
    pages = prior.previous.source_pages()
    table = []
    locks = {}
    for suffix, cls, interpretation, risk, sub1, sub2 in SPECS:
        key = "hs-semantic-pilot-"+suffix
        require(key in candidates and key not in prior_ids,
                "unavailable or already-reviewed source " + key)
        src = candidates[key]["source"]
        page, lo, hi = src["printed_page"], src["start_line"], src["end_line"]
        require(page in pages and 0 < lo <= hi <= len(pages[page]),
                "out-of-range original PDF source")
        raw = pages[page][lo-1:hi]
        track = candidates[key]["course_track"]
        require(track in TRACKS and cls in CLASS, "bad track or source class")
        require(all(prior.provenance.old.previous.base_scope.evidence.track_at(page,i) == track
                    for i in range(lo,hi+1)), "cross-track source span")
        require(len(interpretation)>=28 and len(risk)>=28, "short source review")
        lock = {"page":page,"start_line":lo,"end_line":hi,
                "line_sha256":[hashlib.sha256(t.encode()).hexdigest() for t in raw],
                "span_sha256":hashlib.sha256("\n".join(raw).encode()).hexdigest()}
        locks[key] = lock
        units = []
        for j,title in enumerate((sub1,sub2),1):
            require(len(title)>=6,"truncated editorial teaching target")
            units.append({"provisional_id":f"kb128-proposed-{suffix}-{j:02d}",
                          "title":title,"kind":"EDITORIAL_TEACHING_SUBTARGET",
                          "teacher_status":"REVIEW_PENDING",
                          "official_atom_id":None,
                          "student_authoritative":False})
        table.append({"candidate_id":key,
            "course_track":track,
            "source_pdf_sha256":prior.provenance.old.previous.base_scope.evidence.PDF_SHA,
            "source":lock,
            "source_class":cls,
            "editorial_interpretation":interpretation,
            "outstanding_mathematical_or_scope_risk":risk,
            "subtargets":units,
            "classification_is_human_pending":True,
            "teacher_status":"REVIEW_PENDING","teacher_evidence":None,
            "official_atom_id":None,"student_authoritative":False})
    require(len(table)==28 and len({x["candidate_id"] for x in table})==28,"duplicate review")
    tcounts=dict(sorted(collections.Counter(x["course_track"] for x in table).items()))
    require(tcounts=={t:4 for t in TRACKS}, "seven-track source diversity")
    reviewed_ids=(prior_ids | {r["candidate_id"] for r in table}) & set(candidates)
    require(len(reviewed_ids)==76 and len(set(candidates)-reviewed_ids)==163,
            "historical candidate review-id overlap / missing ids")
    pertrack={}
    for t in TRACKS:
        t_all={key for key,v in candidates.items() if v["course_track"]==t}
        t_reviewed=t_all & reviewed_ids
        t_new=sum(r["course_track"]==t for r in table)
        pertrack[t]={"historical_editorial_candidates":len(t_all),
                     "context_reviewed":len(t_reviewed),
                     "context_not_reviewed":len(t_all-t_reviewed),
                     "new_provisional_subtargets":2*t_new,
                     "official_atom_denominator":None,
                     "teacher_approved":0}
    require(sum(r["historical_editorial_candidates"] for r in pertrack.values())==239
            and sum(r["context_reviewed"] for r in pertrack.values())==76
            and sum(r["context_not_reviewed"] for r in pertrack.values())==163,
            "per-track interim census did not reconcile")
    result={"batch":128,"licensed_version":"2017 edition, 2020 revision",
       "reviewed_historical_candidates_prior":48,
       "reviewed_historical_candidates_new":28,
       "reviewed_historical_candidates_total":76,
       "historic_candidates":239,"still_not_context_reviewed":163,
       "source_layout_cues":405,"provisional_editorial_subtargets":56,
       "subtargets_are_not_official_atoms":True,
       "official_atom_denominator":None,
       "per_track_official_atom_denominator":{t:None for t in TRACKS},
       "teacher_approved":0,"student_authoritative":0,
       "source_text_embedded":False,"counts_by_track":tcounts,
       "per_track_editorial_census":pertrack,
       "records":table}
    validate(result,locks,compare=False)
    return result,locks

def validate(data,locks,compare=True):
    require(data["batch"]==128 and len(data["records"])==28 and
            data["reviewed_historical_candidates_prior"]==48 and
            data["reviewed_historical_candidates_new"]==28 and
            data["reviewed_historical_candidates_total"]==76 and
            data["historic_candidates"]==239 and
            data["still_not_context_reviewed"]==163 and
            data["source_layout_cues"]==405 and
            data["provisional_editorial_subtargets"]==56,
            "false source denominators")
    require(data["subtargets_are_not_official_atoms"] is True and
            data["official_atom_denominator"] is None and
            all(x is None for x in data["per_track_official_atom_denominator"].values()) and
            data["teacher_approved"]==data["student_authoritative"]==0 and
            data["source_text_embedded"] is False, "fabricated authority")
    require(data["counts_by_track"]=={t:4 for t in TRACKS}, "track drift")
    require(set(data["per_track_editorial_census"])==set(TRACKS) and
            sum(row["historical_editorial_candidates"] for row in data["per_track_editorial_census"].values())==239 and
            sum(row["context_reviewed"] for row in data["per_track_editorial_census"].values())==76 and
            sum(row["context_not_reviewed"] for row in data["per_track_editorial_census"].values())==163 and
            sum(row["new_provisional_subtargets"] for row in data["per_track_editorial_census"].values())==56 and
            all(row["historical_editorial_candidates"]==row["context_reviewed"]+row["context_not_reviewed"]
                and row["official_atom_denominator"] is None and row["teacher_approved"]==0
                for row in data["per_track_editorial_census"].values()),
            "faked per-track count or teacher certificate")
    ids=set(); subids=set()
    for r in data["records"]:
        require(r["candidate_id"] not in ids and r["candidate_id"] in locks,"duplicate ID")
        ids.add(r["candidate_id"])
        require(r["source"]==locks[r["candidate_id"]] and
                r["source_class"] in CLASS and
                r["teacher_status"]=="REVIEW_PENDING" and
                r["teacher_evidence"] is None and
                r["official_atom_id"] is None and
                r["student_authoritative"] is False and
                r["classification_is_human_pending"] is True and
                len(r["outstanding_mathematical_or_scope_risk"])>=28,
                "source lineage / reviewer forged")
        require(len(r["subtargets"])==2, "source split missing")
        for s in r["subtargets"]:
            require(s["provisional_id"] not in subids and
                s["teacher_status"]=="REVIEW_PENDING" and
                s["official_atom_id"] is None and
                s["student_authoritative"] is False, "subtarget promotion or collision")
            subids.add(s["provisional_id"])
    require(len(subids)==56, "subtarget count incorrect")
    if compare:
        a,b=build()
        require(data==a and locks==b,"hand-authored semantic source drift")
    return True

def render(data):
    lines=["# Batch128 — 28 verified source windows, 56 provisional editorial teaching subtargets","",
       "**Scope:** The source is the authorised 2020 revised Chinese senior-high mathematics curriculum on Mac; no paragraph is uploaded.",
       "**Not official atoms:** All 56 subtargets are editorial splits requiring teacher review. Official full denominators are UNKNOWN.",
       "**Cumulative distinct context reviews:** 76/239 historical proposals; 163 remain. Teacher approved=0; student authoritative=0.",
       "","## Seven-track editorial candidate census (NOT official atom denominator)",""]
    for t in TRACKS:
        q=data["per_track_editorial_census"][t]
        lines.append(f"- {t}: {q['context_reviewed']}/{q['historical_editorial_candidates']} historically authored candidates context-reviewed, {q['context_not_reviewed']} pending; new provisional teaching subtargets {q['new_provisional_subtargets']}; official atom denominator UNKNOWN")
    lines.append("")
    for r in data["records"]:
        lines += [f"## {r['candidate_id']} ({r['course_track']})",
          f"Source: printed p.{r['source']['page']}, lines {r['source']['start_line']}-{r['source']['end_line']} | {r['source_class']}",
          f"Interpretation: {r['editorial_interpretation']}",
          f"Outstanding: {r['outstanding_mathematical_or_scope_risk']}",
          "Provisional teaching subtargets: " + " / ".join(s["title"] for s in r["subtargets"]),""]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser()
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    args=ap.parse_args()
    data,locks=build()
    for path, body in ((OUT,encode(data)),(LOCKS,encode(locks)),(MD,render(data))):
        if args.write:
            path.write_text(body,encoding="utf8")
        else:
            require(path.exists() and path.read_text(encoding="utf8")==body,"drift: "+str(path))
    print("Batch128: 28 source-locked cases, 56 provisional subtargets, 76/239 context-reviewed, 163 left; NO official atoms.")
if __name__=="__main__":
    main()
