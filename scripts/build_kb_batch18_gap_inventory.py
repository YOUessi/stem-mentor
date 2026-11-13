#!/usr/bin/env python3
"""Original editorial gap candidates located against the 2020 standard.

Absence of a dedicated objective in the original 132-item sample does not
prove the absence of related lessons or make an optional E example mandatory.
Each ticket needs source and lesson-depth review, and remains OPEN.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# (track, printed page, original paraphrase of a missing dedicated objective,
#  nearest existing project objective id or none, why separate audit is needed)
GAPS = [
 ("A",52,"单独追踪自然常数 e 的收敛数列定义与有界性条件","ELECTIVE_A-003","原目标只讨论单调有界收敛性，未明确 e 的具体构造"),
 ("A",53,"微分 dy 与线性近似的物理含义、误差边界","ELECTIVE_A-008","求导定义未单列微分概念与应用"),
 ("A",54,"正交矩阵、长度内积保持和逆矩阵","ELECTIVE_A-015","三阶矩阵运算未单列正交变换"),
 ("A",55,"平面等距变换的矩阵表示与群复合","ELECTIVE_A-015","矩阵基础与等距变换专题层次不同"),
 ("A",55,"空间等距变换及其矩阵不变量","ELECTIVE_A-018","平面方程目标不包含空间等距变换"),
 ("A",55,"非齐次三元方程组解存在条件与秩判定","ELECTIVE_A-017","高斯消元目标尚未单列可解性判据"),
 ("A",56,"连续随机变量及常见密度模型的条件和矩","ELECTIVE_A-018","现有选修 A 18 条中未单列概率统计"),
 ("A",57,"正态总体方差检验与前提条件",None,"选修 A 样本遗漏此统计推断细分"),
 ("A",57,"总体分布拟合优度检验及期望频数条件",None,"选修 A 样本遗漏此统计推断细分"),
 ("B",59,"等高线法求闭凸多边形上仿射目标的最值","ELECTIVE_B-006","现有驻点目标不等同约束多边形极值"),
 ("B",60,"两条异面直线距离和公共垂线存在条件","ELECTIVE_B-007","向量相关目标未单列异面直线距离"),
 ("B",62,"聚类分析的距离选择、算法与失效场景","ELECTIVE_B-013","回归估计不能替代聚类分析"),
 ("B",62,"正交表和正交试验设计的可解释性条件","ELECTIVE_B-011","参数估计目标未涵盖正交设计"),
 ("B",63,"三维线性模型及变量单位一致性","ELECTIVE_B-014","一维时间尺度模型不足以覆盖多维线性建模"),
 ("C",66,"凯恩斯式收支关系模型及解的稳定性","ELECTIVE_C-007","投入产出模型不是收入消费投资模型"),
 ("C",66,"生产函数中对数线性近似的经济限制","ELECTIVE_C-006","复利模型与生产函数用途不同"),
 ("C",67,"等级评分和均值模型中的尺度假设","ELECTIVE_C-009","信度预测不包含等级尺度边界"),
 ("C",68,"社会调查方案可行性评估与风险控制","ELECTIVE_C-010","问卷抽样框不足以表达可行性验收"),
 ("C",68,"观察调查与文案调查的偏差对照","ELECTIVE_C-011","调查报告不等于调查方法选择"),
 ("D",70,"音乐中的泛音与共鸣的周期模型","ELECTIVE_D-005","声音叠加不等同于乐器机制"),
 ("D",71,"曲式平移反射与组合结构的数学解释","ELECTIVE_D-007","节拍同步目标尚未涵盖曲式结构"),
 ("D",72,"视觉透视中投影与不变量的几何限制","ELECTIVE_D-001","形状识别未覆盖绘画透视"),
 ("D",72,"计算机艺术的几何变换与采样模型","ELECTIVE_D-002","对称变换与数字艺术算法不相同"),
 ("D",73,"体育器材与场馆设计的几何约束","ELECTIVE_D-008","运动轨迹不等于场馆规划"),
 ("E",73,"球面几何的曲率及欧氏结论失效","ELECTIVE_E-003","选修 E 举例主题，属任选，非所有学校必修"),
 ("E",73,"闭曲面分类的欧拉示性数探究","ELECTIVE_E-002","仅对称与群不能覆盖拓扑示例"),
 ("E",73,"差分方程的递推稳定性与数列动力学","ELECTIVE_E-003","初等数论与差分专题需要分开审核"),
 ("E",73,"概率论与数理统计大学先修中的抽样分布","ELECTIVE_E-008","既有候选仅为概要，不是完整先修"),
]
def build():
    clauses = json.loads((ROOT/"curriculum/highschool_math/official_numbered_clause_evidence_batch18.json").read_text())
    objectives = json.loads((ROOT/"curriculum/highschool_math/source_anchored_skill_candidates_batch12.json").read_text())
    valid = {x["id"] for x in objectives["items"]}
    page = {p["printed_page"]:p for p in clauses["pages"]}
    tickets = []
    for seq,(code,p,label,related,note) in enumerate(GAPS,1):
        track = "ELECTIVE_"+code
        ref = "HS-STD2020-"+related if related else None
        if ref is not None and ref not in valid: raise ValueError("Unknown existing editorial candidate: "+ref)
        if track not in page[p]["tracks_present"]: raise ValueError("Source page and track mismatch")
        tickets.append({
            "id":f"STD2020-EDITORIAL-GAP-{seq:03d}", "track":track,
            "printed_page":p, "pdf_page_index":p+7,
            "source_page_text_sha256":page[p]["pdf_text_sha256"],
            "original_project_paraphrase":label,
            "nearest_existing_editorial_objective":ref,
            "why_not_equivalent":note,
            "standard_status":"OPTIONAL_LOCAL_CHOICE_EXAMPLE" if code=="E" else "SOURCE_TOPIC_LOCATED_REQUIREMENT_SPLIT_PENDING",
            "lesson_depth_check":"NOT_ASSESSED",
            "review_status":"HUMAN_CURRICULUM_REVIEW_PENDING",
            "gap_status":"OPEN_EDITORIAL_CANDIDATE_NOT_PROVEN_MISSING",
            "student_publishable":False,
        })
    return {
        "schema_version":"1.0", "source_url":clauses["source"]["url"],
        "scope":"ORIGINAL_EDITORIAL_GAP_TRIAGE_NOT_OFFICIAL_ATOMIC_DENOMINATOR",
        "source_pdf_sha256":clauses["source"]["sha256"],
        "summary":{"tickets":len(tickets),"not_verified_missing":len(tickets),
                   "by_track":{f"ELECTIVE_{t}":sum(x["track"]==f"ELECTIVE_{t}" for x in tickets)
                               for t in "ABCDE"},
                   "teacher_resolved":0, "official_complete_denominator":None},
        "tickets":tickets,
    }
def main():
    o=build()
    path=ROOT/"curriculum/highschool_math/k00_gap_tickets_batch18.json"
    path.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(o["summary"],ensure_ascii=False))
if __name__=="__main__":main()
