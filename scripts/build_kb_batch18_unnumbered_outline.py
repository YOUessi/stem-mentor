#!/usr/bin/env python3
"""Page-anchored editorial index of D/E requirements without numbered clauses.

D's source headings are finite; E is school-selected/open-ended. All headings
are paraphrases, not verbatim copyrighted curricular prose or endorsed atoms.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=[
 (69,"数学简洁性与形状构造"),
 (70,"几何对称与变换"),
 (70,"周期及图案规律"),
 (70,"和谐比例与数学比例"),
 (70,"声波的周期函数"),
 (71,"音乐律制与频率数列"),
 (71,"乐曲节拍的有理数"),
 (71,"不同乐器的振动机制"),
 (71,"乐曲结构的数学变换"),
 (72,"绘画中的投影与比例"),
 (72,"其他美术作品几何"),
 (72,"计算机生成艺术的数学"),
 (72,"艺术家采用的数学方法"),
 (72,"运动轨迹与优化"),
 (73,"体育成绩及统计解释"),
 (73,"赛事安排与运筹模型"),
 (73,"运动器材和场馆几何"),
]
E=[
 (73,"选校拓展视野类数学"),
 (73,"日常生活中的数学"),
 (73,"地方特色数学自主开发"),
 (73,"大学先修：微积分"),
 (73,"大学先修：解析几何与线性代数"),
 (73,"大学先修：概率论与数理统计"),
]
def build():
    source=json.loads((ROOT/"curriculum/highschool_math/official_numbered_clause_evidence_batch18.json").read_text())
    pages={p["printed_page"]:p for p in source["pages"]}
    items=[]
    for track,topics in (("ELECTIVE_D",D),("ELECTIVE_E",E)):
        for j,(printed,title) in enumerate(topics,1):
            if track not in pages[printed]["tracks_present"]:
                raise ValueError("Topic track absent from scanned page")
            items.append({
                "id":f"STD2020-{track}-TOPIC-{j:02d}",
                "track":track, "printed_page":printed, "pdf_page_index":printed+7,
                "page_text_sha256":pages[printed]["pdf_text_sha256"],
                "project_authored_heading":title,
                "source_kind":"UNNUMBERED_TOPIC_OUTLINE",
                "offering_type":"SCHOOL_SELECTED_EXAMPLE_OR_OPTION" if track=="ELECTIVE_E" else "CURRICULUM_THEME_SUBTOPIC",
                "atom_decomposition_review":"PENDING",
                "teacher_review":"PENDING",
                "student_available":False,
            })
    return {
        "schema_version":"1.0", "source_pdf_sha256":source["source"]["sha256"],
        "scope":"UNNUMBERED_D_E_OUTLINE_NOT_ATOMIC_COUNT",
        "summary":{"ELECTIVE_D_subtopic_headings":len(D),"ELECTIVE_E_scoped_examples_or_modules":len(E),
                   "teacher_verified_knowledge_atoms":0,"fully_complete":False},
        "items":items
    }
def main():
    x=build()
    p=ROOT/"curriculum/highschool_math/official_unnumbered_de_outline_batch18.json"
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(x["summary"])
if __name__=="__main__":main()
