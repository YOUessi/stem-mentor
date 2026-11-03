"""Editorial K00 gap register from paper pages, NOT official atom certification."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"curriculum/highschool_math/k00_source_gap_candidates_batch18.json"
SOURCE=ROOT/"docs/evaluation/KB_BATCH18_SOURCE_MARKERS.json"
# Each description is independently authored, never a quotation from the standard.
ROWS=[
("SELECTIVE_COMPULSORY",40,"数学史专题","收集微积分创立、发展中的重要思想和数学史材料，组织研究与报告成果"),
("ELECTIVE_A",56,"连续随机变量与密度","区分离散分布与连续分布，理解连续型分布函数与概率密度的适用条件"),
("ELECTIVE_A",56,"重要连续分布","研究均匀、正态、卡方和 t 分布的定义、参数及条件使用"),
("ELECTIVE_A",56,"连续分布数字特征","理解均值、方差等数字特征及相关分布参数与存在性条件"),
("ELECTIVE_A",56,"二维离散随机向量","研究联合分布、协方差、相关系数以及变量独立性的判定条件"),
("ELECTIVE_A",57,"二维正态分布","辨析二维正态随机向量的联合分布与协方差参数解释"),
("ELECTIVE_A",57,"参数估计","理解矩估计和极大似然估计的对象、假设与有限样本局限"),
("ELECTIVE_A",57,"正态假设检验","研究正态总体均值和方差检验、双总体均值比较及一类错误"),
("ELECTIVE_A",57,"分布拟合优度检验","区分拟合优度的原假设、统计量适用条件与结论限制"),
("ELECTIVE_A",57,"二元线性回归模型","区分简单回归与二元预测变量回归并核对参数可识别性"),
]

def build():
    src=json.loads(SOURCE.read_text(encoding="utf8"))
    if src["verified_official_atomic_denominator"] is not None:
        raise ValueError("source evidence cannot be falsely complete")
    missing={(x["track"],x["printed_page"]) for x in src["unrepresented_source_pages"]}
    if any((track,page) not in missing for track,page,*_ in ROWS):
        raise ValueError("source page now has editorial items; redo gap evidence")
    return {
        "scope":"SOURCE_PAGE_OMISSION_EDITORIAL_SUBSKILLS_NOT_OFFICIAL_ATOM_COUNT",
        "standard_pdf_sha256":src["standard_pdf_sha256"],
        "source_register":"docs/evaluation/KB_BATCH18_SOURCE_MARKERS.json",
        "review_status":"REVIEW_PENDING",
        "teacher_approved":0,
        "official_atomic_denominator":None,
        "automatically_inserted_into_original_132":False,
        "omitted_source_pages":[{"track":t,"printed_page":p} for t,p in sorted(missing)],
        "summary":{"new_gap_candidates":len(ROWS),
                   "by_track":{"SELECTIVE_COMPULSORY":1,"ELECTIVE_A":len(ROWS)-1}},
        "items":[{"id":f"KB18-GAP-{i:03d}","track":track,"printed_page":page,
                  "project_topic":topic,"editorial_missing_objective":objective,
                  "evidence_kind":"MANUALLY_LOCATED_COURSE_PAGE_EDITORIAL_SPLIT",
                  "source_review":"PRELIMINARY_NO_TEACHER_SIGNOFF",
                  "student_content_available":False,"teacher_approved":False,
                  "verified_official_atom_id":None,"status":"OPEN"}
                for i,(track,page,topic,objective) in enumerate(ROWS,1)]}

def validate(data):
    if data["official_atomic_denominator"] is not None or data["teacher_approved"]!=0:
        raise ValueError("unsafe unverified scope approval")
    if data["automatically_inserted_into_original_132"] is not False:
        raise ValueError("old editorial denominator altered without re-review")
    if len(data["items"])!=data["summary"]["new_gap_candidates"]:
        raise ValueError("mismatched gap register")
    if any(x["status"]!="OPEN" or x["teacher_approved"] or x["student_content_available"]
           or x["verified_official_atom_id"] is not None for x in data["items"]):
        raise ValueError("fabricated approval/release")
    return True

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");args=p.parse_args()
    data=build();validate(data)
    rendered=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
    if args.check:
        if OUT.read_text(encoding="utf8")!=rendered:raise ValueError("source gap report drift")
    else:OUT.write_text(rendered,encoding="utf8")
    print(f"K00 gap register {'check PASS' if args.check else 'built'}: "
          f"{len(ROWS)} new editorial review targets; zero teacher approvals")
if __name__=="__main__":main()
