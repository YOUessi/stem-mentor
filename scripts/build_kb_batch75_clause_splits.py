#!/usr/bin/env python3
"""Original project subclause suggestions from Mac-attested PDFKit text.
Editorial evidence only; neither official atomization nor teacher approval.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import build_kb_batch74_unmarked_review as B74
import build_kb_batch73_page_partition as B73
ROOT=Path(__file__).resolve().parents[1]
PARENT=B74.OUTPUT
WITNESS=ROOT/"curriculum/highschool_math/k00_batch75_subspan_mac_witness.json"
OUT=ROOT/"docs/evaluation/KB_BATCH75_EDITORIAL_SUBCLAUSE_MATRIX.json"
MD=ROOT/"docs/evaluation/KB_BATCH75_EDITORIAL_SUBCLAUSE_MATRIX.md"
# segment-key|inclusive PDFKit lines|editorial role|project-authored paraphrase|optional draft id
SPLITS="""
013-001|1-6|COURSE_STRUCTURE|必修课程主题及学分概览
013-001|7-17|COURSE_STRUCTURE|主题一的建议课时与学习领域表
014-001|2-26|COURSE_STRUCTURE|其余必修主题课时建议表续篇
014-001|27-31|SKILL_OR_COMPETENCY|初高中数学的学习方法与能力衔接
016-001|2-4|SKILL_OR_COMPETENCY|使用逻辑符号准确推理论证和交流
016-001|5-6|KNOWLEDGE_CANDIDATE|必要充分及充要条件的区别与联系
016-001|5-6|KNOWLEDGE_CANDIDATE|量词命题与否定及论域范围
025-001|1-3|SKILL_OR_COMPETENCY|函数思维的代数求解与综合素养
025-001|4-7|SCOPE|必修几何代数及形数结合的主题边界
027-001|1-2|KNOWLEDGE_CANDIDATE|复数运算和几何意义的连接
027-001|3-3|ADVANCED_FLAG|星号复数三角表示是另立层级的选学范围
029-001|1-3|EXISTING_DRAFT_LINK|平面外直线平行平面判定|KB74-SP-01
029-001|4-5|EXISTING_DRAFT_LINK|平面内两相交线判定面面平行|KB74-SP-02
029-001|6-7|EXISTING_DRAFT_LINK|平面内两相交线判定线面垂直|KB74-SP-03
029-001|8-8|EXISTING_DRAFT_LINK|平面包含垂线判定面面垂直|KB74-SP-04
032-001|2-4|SCOPE|数据获取抽样统计图表与样本估计主题
032-001|3-4|KNOWLEDGE_CANDIDATE|抽样推断需要代表性与定义总体
037-001|1-18|COURSE_STRUCTURE|选必各主题课程时数结构和机动课时
037-001|19-26|SCOPE|数列与导数在函数主题的内容定位
046-001|2-7|SKILL_OR_COMPETENCY|解析几何建模与方程求解能力
046-001|8-13|SCOPE|选必计数概率统计的学习范围说明
046-001|10-13|KNOWLEDGE_CANDIDATE|条件概率离散分布正态分布的前提差异
046-001|11-13|KNOWLEDGE_CANDIDATE|相关回归及列联分析的适用条件
050-001|1-3|SKILL_OR_COMPETENCY|概率统计主题综合学业素养目标
050-001|4-4|SCOPE|选择性必修建模和数学探究主题入口
051-020|20-23|COURSE_STRUCTURE|选修A专题学分安排不是知识原子
051-020|24-27|SCOPE|选修A微积分从极限出发的学习路径
052-001|2-6|SCOPE|选修A微积分直观教学与模型范围说明
052-001|7-8|KNOWLEDGE_CANDIDATE|数列极限和函数极限定义对象差别
052-001|7-8|KNOWLEDGE_CANDIDATE|连续函数的定义前提和失效情形
052-001|7-8|KNOWLEDGE_CANDIDATE|导数微分与定积分的联系和区分
056-001|2-11|SCOPE|选修A从连续分布走向统计推断的专题
056-001|12-13|KNOWLEDGE_CANDIDATE|连续型随机变量与密度区间概率
056-001|12-13|KNOWLEDGE_CANDIDATE|二维随机变量联合分布边缘化
056-001|12-13|KNOWLEDGE_CANDIDATE|参数估计检验和多元回归的条件
057-016|16-19|COURSE_STRUCTURE|选修B专题安排与学分结构
057-016|20-23|SCOPE|选修B微积分与函数极限联系
058-001|2-6|SCOPE|选修B微积分和二元函数教学顺序
058-001|7-7|KNOWLEDGE_CANDIDATE|二元函数偏导与固定另一自变量
058-001|7-7|KNOWLEDGE_CANDIDATE|一元极限导数微分和定积分差别
060-001|2-3|KNOWLEDGE_CANDIDATE|空间向量代数内积外积条件
060-001|2-3|KNOWLEDGE_CANDIDATE|三阶矩阵行列式可逆和退化条件
060-001|2-3|KNOWLEDGE_CANDIDATE|三元线性方程组解的唯一性条件
061-001|1-10|SCOPE|选修B应用统计拓展与场景选择
061-001|11-13|KNOWLEDGE_CANDIDATE|连续分布与二维联合分布模型
061-001|11-13|KNOWLEDGE_CANDIDATE|估计检验及二元回归的统计条件
061-001|11-13|KNOWLEDGE_CANDIDATE|聚类分析正交设计及误用边界
063-001|2-6|SCOPE|选修B现实模型的背景假设与适用域
063-001|7-8|KNOWLEDGE_CANDIDATE|线性模型和二次曲线模型区别
063-001|7-8|KNOWLEDGE_CANDIDATE|指数增长和三角周期模型区别
063-001|7-8|KNOWLEDGE_CANDIDATE|参变数模型的参数区间与轨迹
064-010|10-12|COURSE_STRUCTURE|选修C专题与学分结构
064-010|13-18|SKILL_OR_COMPETENCY|逻辑论证与推理表述的学习能力
064-010|19-20|KNOWLEDGE_CANDIDATE|数学定义命题与证明方法的区分
066-001|2-5|SKILL_OR_COMPETENCY|经济社会模型使用范围及批判意识
066-001|6-6|KNOWLEDGE_CANDIDATE|经济和社会模型的假设与局限
068-001|1-2|SCOPE|社会调查主题仅为跨页片段待合并
069-006|6-8|COURSE_STRUCTURE|选修D艺术与运动四专题学分结构
069-006|9-14|SCOPE|美学主题的数学刻画边界
069-006|15-16|KNOWLEDGE_CANDIDATE|对称周期简洁和谐作为不同数学视角
""".strip()
def canon(x):return json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
def specs():
 d={}
 for line in SPLITS.splitlines():
  key,interval,role,label,*ref=line.split("|")
  a,b=map(int,interval.split("-"))
  d.setdefault(key,[]).append((a,b,role,label,ref[0] if ref else None))
 return d
def mac_hash(page,a,b):
 raw=(Path("/private/tmp")/f"kb56_page_{page}.txt").read_bytes()
 inv=B73.load(B73.PAGES)
 expected=next(p["pdfkit_text_sha256"] for p in inv["pages"] if p["printed_page"]==page)
 assert sha256(raw).hexdigest()==expected, "source PDFKit changed"
 lines=raw.decode().splitlines()
 return sha256("\n".join(lines[a-1:b]).encode()).hexdigest()
def build(w,verify_mac=False):
 review=B73.load(PARENT)
 selected=[r for r in review["records"] if r["classification"] in
           ("SUBSTANTIVE_UNNUMBERED","MIXED_REQUIRES_SPLIT")]
 plan=specs()
 assert len(selected)==len(plan)==22
 assert {r["segment_id"][6:9]+"-"+r["segment_id"][11:14] for r in selected}==set(plan)
 assert w["source_pdf_sha256"]==B74.PDF_SHA
 rows=[]
 for seg in selected:
  key=seg["segment_id"][6:9]+"-"+seg["segment_id"][11:14]
  for n,(a,b,role,label,linked) in enumerate(plan[key],1):
   assert seg["first_line"]<=a<=b<=seg["last_line"]
   assert role in ("COURSE_STRUCTURE","SKILL_OR_COMPETENCY","SCOPE",
                   "KNOWLEDGE_CANDIDATE","ADVANCED_FLAG","EXISTING_DRAFT_LINK")
   assert len(label)>=10
   id=f"KB75-P{seg['printed_page']:03d}-S{n:02d}"
   z=w["subspans"][id]
   assert z["source_segment_id"]==seg["segment_id"] and z["first_line"]==a and z["last_line"]==b
   assert re.fullmatch("[a-f0-9]{64}",z["sha256"])
   if verify_mac:assert z["sha256"]==mac_hash(seg["printed_page"],a,b),"Mac subspan source drift"
   if linked:assert seg["printed_page"]==29 and linked in [f"KB74-SP-{i:02d}" for i in range(1,5)]
   rows.append(dict(id=id,source_segment_id=seg["segment_id"],printed_page=seg["printed_page"],
        first_line=a,last_line=b,role=role,project_authored_paraphrase=label,
        linked_existing_teacher_draft=linked,track_hint=seg["track_hint"],
        source_pdf_sha256=B74.PDF_SHA,parent_span_sha256=seg["span_sha256"],
        local_source_subspan_sha256=z["sha256"],teacher_review="REVIEW_PENDING",
        mathematical_equivalence="UNDETERMINED",formal_certification="NOT_FORMALLY_CERTIFIED",
        completed_full_clause_review=False,official_atom_contribution=None,
        student_publishable=False))
 assert len(rows)==len(set(r["id"] for r in rows))
 roles=dict(sorted(Counter(r["role"] for r in rows).items()))
 tracks=dict(sorted(Counter(r["track_hint"] for r in rows).items()))
 report=dict(schema_version="kb75-mac-editorial-subspans-v1",source_pdf_sha256=B74.PDF_SHA,
   parent_triage_sha256=sha256(PARENT.read_bytes()).hexdigest(),
   mac_frozen_witness_sha256=sha256(WITNESS.read_bytes()).hexdigest(),
   source_segments=len(selected),editorial_components=len(rows),
   role_counts=roles,project_track_counts=tracks,
   official_denominators={t:None for t in B73.TRACKS},
   teacher_full_page_reviews=0,teacher_approved=0,student_published=0,
   records=rows)
 md="\n".join(["# Batch75｜高优先级课标来源片段逐行编辑拆分","",
  f"- 22段高风险来源共拆为{len(rows)}个项目原创编辑组件，来源及子片段SHA记录在JSON中。",
  "- 组件共用来源行时允许重叠；不推断官方数学知识点数，不复印课标原文。",
  "- 课程课时表与能力目标分别归档，选修各轨保留原有轨道提示。",
  "- 七轨正式原子分母全部null，教师全页审核0/61，教师批准0，学生发布0。","",
  "## 项目编辑组件类别",*[f"- {k}: {v}" for k,v in roles.items()],"",
  "## 轨道范围提示（不等于官方分母）",*[f"- {k}: {v}" for k,v in tracks.items()],"",
  "## 下一步","- 真实教师对照完整跨页课标进行数学等价和官方原子化审核。",
  "- 仅在审核课程原子、准确条件和证明后开放学生检索；选修E须另有学校实际开课计划。",""])
 validate_matrix(report,w)
 return report,md
def validate_matrix(matrix, frozen_witness):
 """Fail closed when a derived coverage matrix is tampered with or overclaimed."""
 assert matrix["source_pdf_sha256"]==B74.PDF_SHA
 assert matrix["parent_triage_sha256"]==sha256(PARENT.read_bytes()).hexdigest()
 assert matrix["mac_frozen_witness_sha256"]==sha256(WITNESS.read_bytes()).hexdigest()
 assert matrix["source_segments"]==22 and matrix["editorial_components"]==len(matrix["records"])
 assert matrix["teacher_full_page_reviews"]==0
 assert matrix["teacher_approved"]==matrix["student_published"]==0
 assert matrix["official_denominators"]=={t:None for t in B73.TRACKS}
 assert matrix["role_counts"]==dict(sorted(Counter(r["role"] for r in matrix["records"]).items()))
 assert matrix["project_track_counts"]==dict(sorted(Counter(r["track_hint"] for r in matrix["records"]).items()))
 assert len(matrix["records"])==len({r["id"] for r in matrix["records"]})
 parent={r["segment_id"]:r for r in B73.load(PARENT)["records"]}
 for r in matrix["records"]:
  assert r["id"] in frozen_witness["subspans"]
  att=frozen_witness["subspans"][r["id"]]
  seg=parent[r["source_segment_id"]]
  assert att["source_segment_id"]==r["source_segment_id"]
  assert (att["first_line"],att["last_line"])==(r["first_line"],r["last_line"])
  assert r["local_source_subspan_sha256"]==att["sha256"]
  assert r["parent_span_sha256"]==seg["span_sha256"]
  assert r["source_pdf_sha256"]==B74.PDF_SHA and r["track_hint"]==seg["track_hint"]
  assert r["teacher_review"]=="REVIEW_PENDING"
  assert r["mathematical_equivalence"]=="UNDETERMINED"
  assert r["formal_certification"]=="NOT_FORMALLY_CERTIFIED"
  assert r["official_atom_contribution"] is None
  assert r["completed_full_clause_review"] is False
  assert r["student_publishable"] is False
 return True

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--check",action="store_true")
 ap.add_argument("--bootstrap-mac",action="store_true")
 ap.add_argument("--verify-local-source",action="store_true")
 args=ap.parse_args()
 if args.bootstrap_mac:
  assert not WITNESS.exists(),"frozen witness already exists"
  r=B73.load(PARENT)
  spans={}
  for seg in r["records"]:
   key=seg["segment_id"][6:9]+"-"+seg["segment_id"][11:14]
   for n,(a,b,*_) in enumerate(specs().get(key,[]),1):
    spans[f"KB75-P{seg['printed_page']:03d}-S{n:02d}"]=dict(source_segment_id=seg["segment_id"],
         first_line=a,last_line=b,sha256=mac_hash(seg["printed_page"],a,b))
  WITNESS.write_text(canon(dict(source_pdf_sha256=B74.PDF_SHA,subspans=spans)),encoding="utf8")
 x,m=build(B73.load(WITNESS),verify_mac=args.verify_local_source)
 if args.check:
  assert OUT.read_text(encoding="utf8")==canon(x), "component matrix changed"
  assert MD.read_text(encoding="utf8")==m, "markdown report changed"
 else:
  OUT.write_text(canon(x),encoding="utf8")
  MD.write_text(m,encoding="utf8")
 print("Batch75",x["source_segments"],"source segments",x["editorial_components"],"editorial proposals; none officially certified")
if __name__=="__main__":main()
