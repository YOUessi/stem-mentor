#!/usr/bin/env python3
"""Batch129: audited seven-track source windows; provisional targets are NOT official atoms."""
from __future__ import annotations
import argparse, collections, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch128_source_ledger as prior

OUT=ROOT/"docs/evaluation/KB_BATCH129_SCOPE_REVIEWS.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH129_SCOPE_REVIEWS.md"
LOCKS=ROOT/"curriculum/highschool_math/k00_batch129_source_line_locks.json"
TRACKS=prior.TRACKS
# suffix, source kind, contextual interpretation, unresolved mathematical condition, subtargets
SPECS=[
("120-c107","DIRECT_NUMBERED","原文把借助向量探索三角形边角关系与掌握余弦定理并列；计算边长及反求角度可作不同的候审能力。","三角形三边须为正且满足严格三角不等式；边长为零或不构成三角形时不能使用角度公式。","余弦定理的边长求解","反求角度的余弦条件"),
("120-c108","DIRECT_NUMBERED","同一编号课程要求同时覆盖正弦定理和余弦定理；正弦定理的比值关系应与余弦定理区分。","正弦定理的除法形式须有非零角的正弦值；SSA条件可能出现两个三角形，不能忽略多解。","正弦定理与外接圆","正弦条件的解的个数"),
("120-c111","DIRECT_NUMBERED","简单随机抽样段落同时提到抽签法与随机数法，以及样本均值和样本方差；应拆分抽样过程与统计量。","每个大小为n的子集等概率是有限总体不放回简单随机抽样条件；样本方差分母n与n−1须区分。","有限总体不放回抽样","样本均值与方差约定"),
("120-c112","DIRECT_NUMBERED","分层抽样段落要求按层比例分配样本量及计算样本统计量，分层识别与层权重统计不能混同。","分层必须覆盖总体且各层不重叠；按比例抽样存在整数舍入和样本量不足的边界。","互斥分层与比例分配","按总体层权重合并均值"),
("119-s11","DIRECT_NUMBERED","空间向量段落同时涉及夹角、平行及垂直等位置关系；必须按向量类型和对象区分判别条件。","方向向量和法向量不能为零；直线与平面平行判定需排除直线位于平面内的情形。","非零方向与法向量","直线平面位置向量判别"),
("119-s12","DIRECT_NUMBERED","源段提出点到线、点到面及平行对象之间距离；应把距离定义与正交投影计算分开。","平面方程的法向量必须非零，距离分母不可为零；平行直线或平面之间距离另需验证相互平行。","点到平面的正交距离","平行对象的距离条件"),
("119-s13","DIRECT_NUMBERED","源段明确要求条件概率及其与独立性的联系，两者分别是归一化条件和乘积判据。","条件概率分母P(B)>0；独立不是互斥，若两个事件的概率均大于零则互斥不能独立。","条件概率的样本空间限制","事件独立的乘积判据"),
("119-s14","DIRECT_NUMBERED","全概率公式直接列在课程要求中，贝叶斯公式另为了解内容；应先教分割求和再审查后验归一化。","全概率需要互斥且完备的划分；贝叶斯公式观察证据的总概率必须严格为正。","全概率的互斥完备划分","贝叶斯归一化及零证据"),
("120-a103","DIRECT_ELECTIVE_REQUIREMENT","选修A对向量组线性相关性有明确要求，存在非平凡零组合与行列式判据不能无条件混同。","只有向量数与维数满足方阵条件时可用行列式检验；零向量导致相关但不等于所有向量相等。","非平凡线性组合","有限维向量组秩检验"),
("120-a104","DIRECT_ELECTIVE_REQUIREMENT","向量空间和子空间在同一要求中出现，应将线性组合封闭性和子空间三个条件独立讲解。","候选子集必须含零向量并对加法和数乘封闭；非空曲线或仿射平面通常不是线性子空间。","向量空间线性公理","子空间封闭性和零向量"),
("120-a105","DIRECT_ELECTIVE_REQUIREMENT","源段包含三阶矩阵运算、正交矩阵和行列式，三者的定义及证明条件不可简化为一个概念。","行列式为零表示方阵奇异，但非方阵不定义普通行列式；正交矩阵满足QᵀQ=I。","三阶行列式与可逆性","正交矩阵保距条件"),
("120-a106","DIRECT_ELECTIVE_REQUIREMENT","三元线性方程组要求掌握高斯消元并用矩阵表示，行初等变换与解集保持应单列。","仅允许交换行、乘非零数及加倍数行；乘零会丢失等价信息；无解和无穷多解都可能。","增广矩阵的行操作","高斯消元的秩分类"),
("120-b105","DIRECT_ELECTIVE_REQUIREMENT","参数估计段落提出矩估计与极大似然估计，应分别处理估计量及参数约束的含义。","极大似然须基于实际分布及可行参数空间；有边界时最大值可能落在端点，不能只求导数为零。","矩估计的样本矩","似然函数与边界最优"),
("120-b106","DIRECT_ELECTIVE_REQUIREMENT","假设检验段列出正态均值方差与两总体比较；检验前提和错误类型先于公式选用。","正态假设、样本独立性、方差已知或未知及显著性水平都影响检验选择；拒绝原假设不等于证明备择绝对真。","原假设与一类错误","正态总体检验的假设前提"),
("120-b107","DIRECT_ELECTIVE_REQUIREMENT","聚类分析作为独立专题要求理解意义与方法；距离定义和变量尺度对聚类结果有决定影响。","无监督聚类标签不是客观真值；欧氏距离受单位和标准化影响，不能据此证明因果关系。","聚类距离与归一化","簇数选择与稳定性"),
("120-b108","DIRECT_ELECTIVE_REQUIREMENT","线性模型段包含一维、二维和三维建模实例，变量及矩阵维度与现实单位需要逐项审查。","从一次函数的均匀变化推广到矩阵映射须核实维数一致；投入产出模型解应满足非负性约束。","一维仿射与线性映射区别","多维矩阵模型单位审计"),
("120-ec105","THEMATIC_ELECTIVE_REQUIREMENT","投入产出模型专题说明系数与解约束生产计划，数学可解与现实非负可行是两层不同判断。","投入产出矩阵若不满足可逆条件则不能直接求唯一解；解含负产出时数学解不是合法生产计划。","投入产出平衡线性方程","非负产出与可行约束"),
("120-ec106","THEMATIC_ELECTIVE_REQUIREMENT","等级评价模型列出加权、调和与稳健平均，需区分评分权重和异常值影响而非宣称一个唯一最优平均。","调和平均需分母和正数据满足约束；权重须非负并正归一化，异常值处理需要事先约定。","加权平均的权重约束","调和与稳健评价的边界"),
("120-ec107","THEMATIC_ELECTIVE_REQUIREMENT","人口增长模型段要求理解指数模型参数、拟合与有效性；拟合和外推须分成不同的审查任务。","模型r>0持续增长的现实假设可能失效，有限样本拟合良好不保证无限时间外推可靠。","指数增长率参数解释","人口拟合残差及外推"),
("120-ec108","THEMATIC_ELECTIVE_REQUIREMENT","源段明确提出二阶多阶抽样，应与必修简单随机抽样和分层抽样区别，先后抽样概率需分层计算。","簇内样本相关时不应把所有个体视为独立简单随机样本；抽中概率与权重需按阶段核对。","多阶段抽样入样概率","簇相关与有效样本量"),
("120-ed105","THEMATIC_ILLUSTRATION","律制专题举不同音阶与频率比，十二平均律可编写理想等比频率模型但不是所有音律的唯一形式。","十二平均律的相邻半音比为2^(1/12)而非固定整数；频率和弦长的关系依赖物理边界条件。","十二平均律等比频率","不同律制与理想假设"),
("120-ed106","THEMATIC_ILLUSTRATION","节拍与分数、合奏同步与最小公倍数是选修D应用场景，不等于课标指定一套统一音符算法。","计算同步时两节拍必须有共同时间单位且周期可公度；无理数周期比时不存在有限正同步周期。","整比节拍的最小公倍数","非公度节拍的同步边界"),
("120-ed107","THEMATIC_ILLUSTRATION","绘画专题明确列透视几何为例；可将透视投影与平面仿射变换并列，但不得误作强制证明定理。","透视投影需视点及深度信息；深度为零的投影分母无定义，通常不保平行和长度。","透视投影的深度分母","仿射变换与透视差异"),
("120-ed108","THEMATIC_ILLUSTRATION","体育赛事的图论与运筹为应用主题，赛程建模需要明确场次场地和队伍冲突，非固定全国知识公式。","单循环赛程每对队伍只赛一次时有n(n−1)/2场；赛程时间或资源限制可能使理想排程不可行。","单循环赛场次数量","赛事排程约束与轮转"),
("120-ee105","LOCAL_SCHOOL_OPTION","家庭理财列为选修E学校自选示例，可原创构建复利及通胀模型但不能提升为全国统一必修。","复利周期数必须与利率单位一致；通胀调整与名义收益不是同一量，现实税费会破坏理想公式。","学校可选理财模型","利率周期及物价单位"),
("120-ee106","LOCAL_SCHOOL_OPTION","地方建筑与数学只作学校选用示例；相似测量可供自主编写，必须保留地理情境和非必修地位。","相似三角形需要角条件及相应边比例；地面不平或测量角错误会破坏建筑高度估计。","地方建筑几何测量实例","相似测高的角度假设"),
("120-ee107","LOCAL_SCHOOL_OPTION","大学先修课程包含微积分等方向但未规定具体极限知识原子；不可把自编定义视作全国高中必修。","ε-δ等严谨定义可以作为选校可选内容，其证明前提不能从课程标题自动推定已获得教师认证。","大学先修微积分选题","局部连续与极限的拓展"),
("120-ee108","LOCAL_SCHOOL_OPTION","大学概率统计先修是独立可选方向；样本与分布教学内容须由学校方案进一步细化而非官方固定清单。","高阶分布推断要核对独立同分布和参数假设；不能用选修E示例提高全国必修知识点分母。","大学先修概率统计选题","样本分布假设与适用域"),
]
def req(p,msg):
    if not p: raise ValueError(msg)
def enc(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def build():
    _,cands=prior.prior.originals()
    pages=prior.prior.previous.source_pages()
    previous={"hs-semantic-pilot-"+x[0] for x in prior.prior.DETAILS}
    previous|={x[0] for x in prior.prior.previous.SPECS}
    previous|={"hs-semantic-pilot-"+x[0] for x in prior.SPECS}
    previous &= set(cands)
    req(len(previous)==76,"prior context drift")
    rows=[];locks={}
    for suffix,cls,why,risk,left,right in SPECS:
        key="hs-semantic-pilot-"+suffix
        req(key in cands and key not in previous and key not in locks,"duplicate or unknown curriculum candidate "+key)
        v=cands[key];source=v["source"];p=source["printed_page"];lo=source["start_line"];hi=source["end_line"]
        req(1<=lo<=hi<=len(pages[p]),"bad source span")
        req(all(prior.prior.provenance.old.previous.base_scope.evidence.track_at(p,k)==v["course_track"] for k in range(lo,hi+1)),"cross-track source")
        lines=pages[p][lo-1:hi]
        lock={"page":p,"start_line":lo,"end_line":hi,"line_sha256":[hashlib.sha256(x.encode()).hexdigest() for x in lines],
            "span_sha256":hashlib.sha256("\n".join(lines).encode()).hexdigest()}
        locks[key]=lock
        req(cls in prior.CLASS and len(why)>=28 and len(risk)>=28 and len(left)>=6 and len(right)>=6,"empty review case")
        rows.append({"candidate_id":key,"course_track":v["course_track"],
            "source":lock,"source_pdf_sha256":prior.prior.provenance.old.previous.base_scope.evidence.PDF_SHA,
            "source_class":cls,"editorial_interpretation":why,"outstanding_risk":risk,
            "proposed_teaching_targets":[{"id":f"kb129-provisional-{suffix}-{j:02d}","title":title,"official_atom_id":None,
                "teacher_status":"REVIEW_PENDING","student_authoritative":False}
                for j,title in enumerate((left,right),1)],
            "teacher_status":"REVIEW_PENDING","teacher_signature":None,"official_atom_id":None,
            "student_authoritative":False,"mathematics_formally_certified":False})
    ids=previous|set(locks)
    census={}
    for t in TRACKS:
        allids={k for k,v in cands.items() if v["course_track"]==t}
        have=len(allids&ids)
        census[t]={"historical_editorial_candidates":len(allids),"source_context_checked":have,
                   "source_context_unchecked":len(allids)-have,"official_atom_denominator":None,
                   "teacher_approved":0}
    res={"batch":129,"licensed_version":"2017 edition, 2020 revision","historical_candidates":len(cands),
         "source_layout_cues":405,"context_checked_before":76,"new_context_checked":28,
         "total_context_checked":len(ids),"not_context_checked":len(cands)-len(ids),
         "official_atom_denominator":None,"per_track_official_atom_denominator":{t:None for t in TRACKS},
         "teacher_approved":0,"student_authoritative":0,"source_text_embedded":False,
         "provisional_teaching_targets":len(rows)*2,"subtargets_are_not_official_atoms":True,
         "counts_by_track":dict(sorted(collections.Counter(r["course_track"] for r in rows).items())),
         "per_track_editorial_census":census,"records":rows}
    validate(res,locks,regen=False)
    return res,locks
def validate(data,locks,regen=True):
    req(data["batch"]==129 and data["historical_candidates"]==239 and data["source_layout_cues"]==405 and
        data["context_checked_before"]==76 and data["new_context_checked"]==28 and
        data["total_context_checked"]==104 and data["not_context_checked"]==135 and
        data["provisional_teaching_targets"]==56,"unreconciled denominator")
    req(data["official_atom_denominator"] is None and data["teacher_approved"]==data["student_authoritative"]==0
        and data["source_text_embedded"] is False and data["subtargets_are_not_official_atoms"] is True
        and set(data["per_track_official_atom_denominator"])==set(TRACKS)
        and all(x is None for x in data["per_track_official_atom_denominator"].values()),"forged authority")
    req(data["counts_by_track"]=={t:4 for t in TRACKS} and len(data["records"])==28 and
        len(set(locks))==28,"source count or tracking drift")
    req(sum(x["historical_editorial_candidates"] for x in data["per_track_editorial_census"].values())==239
        and sum(x["source_context_checked"] for x in data["per_track_editorial_census"].values())==104
        and sum(x["source_context_unchecked"] for x in data["per_track_editorial_census"].values())==135
        and all(x["official_atom_denominator"] is None and x["teacher_approved"]==0 for x in data["per_track_editorial_census"].values()),"per-track denominator forged")
    ids=set();sub=set()
    for r in data["records"]:
        req(r["candidate_id"] not in ids and r["candidate_id"] in locks,"bad candidate id")
        ids.add(r["candidate_id"])
        req(r["source"]==locks[r["candidate_id"]] and r["source_class"] in prior.CLASS and
            len(r["outstanding_risk"])>=28 and len(r["editorial_interpretation"])>=28
            and r["teacher_status"]=="REVIEW_PENDING" and r["teacher_signature"] is None
            and r["official_atom_id"] is None and r["student_authoritative"] is False
            and r["mathematics_formally_certified"] is False,"forged source or teacher status")
        req(len(r["proposed_teaching_targets"])==2,"missing atomic split")
        for z in r["proposed_teaching_targets"]:
            req(z["id"] not in sub and z["official_atom_id"] is None and z["teacher_status"]=="REVIEW_PENDING"
                and z["student_authoritative"] is False,"missing or published provisional subtarget")
            sub.add(z["id"])
    req(len(sub)==56,"subtarget count drift")
    if regen:
        expected,source=build()
        req(expected==data and source==locks,"source record drift")
    return True
def render(data):
    lines=["# Batch129 curriculum source and meaning review","",
        "28 new line-hash-attested historical editorial candidates; 104/239 context checked, 135 remain.",
        "56 provisional teaching targets: NOT official mathematical atom counts.",
        "All seven official track denominators UNKNOWN. Teacher approved=0, student authority=0.",
        "Source PDF is retained exclusively on the authorized Mac; only hashes/page/line anchors are committed.",""]
    for t in TRACKS:
        q=data["per_track_editorial_census"][t]
        lines.append(f"- {t}: context {q['source_context_checked']}/{q['historical_editorial_candidates']}, remaining {q['source_context_unchecked']} / official denominator UNKNOWN")
    lines.append("")
    for r in data["records"]:
        lines.extend([f"## {r['candidate_id']} | {r['course_track']}",
            f"Printed page {r['source']['page']} lines {r['source']['start_line']}-{r['source']['end_line']}; {r['source_class']}",
            "Editorial interpretation: "+r["editorial_interpretation"],
            "Unresolved: "+r["outstanding_risk"],
            "Possible subtargets (pending): "+" / ".join(x["title"] for x in r["proposed_teaching_targets"]),""])
    return "\n".join(lines).rstrip()+"\n"
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true");a=p.parse_args()
    data,locks=build()
    for path,contents in [(OUT,enc(data)),(LOCKS,enc(locks)),(REPORT,render(data))]:
        if a.write:path.write_text(contents,encoding="utf-8")
        else:req(path.exists() and path.read_text(encoding="utf-8")==contents,"frozen source artifact drift "+str(path))
    print("Batch129: 28 new verified contexts, 104/239 reviewed; 135 remain; 7 official denominators UNKNOWN")
if __name__=="__main__":main()
