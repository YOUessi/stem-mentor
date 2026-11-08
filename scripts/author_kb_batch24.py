#!/usr/bin/env python3
"""Reproducibly materialize 20 original Batch24 lesson drafts on the authorized Mac.

Never infer official syllabus equivalence, proof certification or teacher approval.
The JSONL source is manually authored, not scraped textbook prose.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.deep_knowledge import DeepLesson

SOURCE = ROOT / "curriculum/highschool_math/author_seed_batch24.jsonl"
OUT = ROOT / "knowledge/deep/v1/core_foundation_batch24.json"
STANDARD = "https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf"
PREREQUISITES = {
 "004":"量词、逻辑否定与真值定义","006":"实数大小关系、正负数及零的乘法",
 "008":"实二次方程和因式分解、一次不等式","009":"非负实数、平方根及平方非负",
 "011":"集合表示、实数运算定义域与函数映射","014":"函数定义域、负号代入和代数恒等式",
 "020":"整数幂、实数n次根与零的倒数","024":"函数映射与复合输入输出",
 "028":"弧度制、单位圆与正余弦的坐标定义","029":"单位圆和二维旋转的线性表达",
 "036":"三角形面积和外接圆圆周角性质","046":"几何面积、相似比及垂直高度",
 "052":"有限集合、互斥事件及概率可加性","064":"数列递推、有限和与等比数列定义",
 "070":"一元一次方程、配方、实数平方根","074":"空间点坐标、向量数乘和非零向量",
 "080":"平面坐标、方向向量与正切定义域","087":"圆锥曲线方程、两点距离",
 "100":"组合数、无放回抽样及等可能子集","103":"条件概率、边际频率和抽样独立性"
}
def build():
    entries = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(entries) != 20 or len({r[0] for r in entries}) != 20:
        raise ValueError("Batch24 must contain 20 independent authored lessons")
    result = []
    for row in entries:
        if len(row) != 13:
            raise ValueError("Incomplete lesson-author row")
        tag, code, kind, title, claim, assumptions, steps, wrong, examples, boundary, hints, near, far = row
        cid = f"HS-MATH-{code}"
        if code not in PREREQUISITES or kind not in ("theorem", "concept", "method"):
            raise ValueError("Unrecognized core prerequisite or knowledge type")
        if len(steps)<3 or len(examples)!=2 or any(len(x)!=4 for x in examples):
            raise ValueError("Insufficient mathematical reasoning or worked examples")
        if len(wrong)!=3 or len(hints)!=3 or len(set(hints))!=3:
            raise ValueError("Counterexample and safe hints required")
        if any(len(x[0])<12 or len(x[1])<12 for x in steps):
            raise ValueError("Reasoning must be substantive and separately justified")
        doc = dict(
            id=f"math.hs.batch24.{tag.lower()}",curriculum_ids=[cid],kind=kind,
            title=title,version="1.0.0",notation=[claim],
            prerequisites=[PREREQUISITES[code]],prerequisite_lesson_ids=[],
            definition=claim if kind=="concept" else None,
            statement=claim if kind!="concept" else None,assumptions=assumptions,
            proof_steps=[dict(claim=a,reason=b) for a,b in steps] if kind=="theorem" else [],
            rationale_steps=[a+" 理由："+b for a,b in steps] if kind!="theorem" else [],
            boundaries=[boundary],
            counterexamples=[dict(false_claim=wrong[0],example=wrong[1],explanation=wrong[2])],
            worked_examples=[dict(question=q,steps=[s1,s2],answer=ans,
              check="教师侧须独立回代或以精确算术检验这一实例；不构成完整定理的形式认证。")
              for q,s1,s2,ans in examples],
            misconceptions=[dict(error=wrong[0],why_wrong=wrong[2],
              repair_question="指出此错解遗漏的假设、量词或不等价操作，并用一个实例说明如何修复。")],
            hint_ladder=hints,transfer=dict(near=near,far=far),
            provenance=dict(kind="PROJECT_AUTHORED",permission="PROJECT_AUTHORED",
              curriculum_standard="普通高中数学课程标准（2017年版2020年修订）",
              standard_url=STANDARD,author_role="PROJECT_AUTHOR"),
            review=dict(status="REVIEW_PENDING",reviewer_id=None,reviewed_at=None,review_record=None),
            teacher_solution_visibility="TEACHER_ONLY"
        )
        parsed = DeepLesson.model_validate(doc)
        if parsed.model_dump(mode="json") != doc:
            raise ValueError("Author draft does not satisfy strict lesson schema")
        result.append(doc)
    if len({x["curriculum_ids"][0] for x in result})!=20:
        raise ValueError("Each batch topic needs distinct engineering topic anchor")
    return json.dumps(result,ensure_ascii=False,indent=2)+"\n"
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    body=build()
    if a.check:
        if OUT.read_text(encoding="utf-8")!=body:
            raise SystemExit("Batch24 authored materialization drift")
    else:
        OUT.write_text(body,encoding="utf-8")
    print("PASS: Batch24 20 original teacher-only REVIEW_PENDING draft lessons")
if __name__=="__main__":
    main()
