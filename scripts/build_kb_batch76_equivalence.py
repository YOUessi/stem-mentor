#!/usr/bin/env python3
"""Review all 26 Batch75 syllabus atom candidates without fabricating equivalence.

This is a project-editorial comparison queue, NOT an official syllabus denominator
or teacher-certified claim. Never auto-merge evidence or publish teacher answers.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
import build_kb_batch75_clause_splits as B75

ROOT=Path(__file__).resolve().parents[1]
MATRIX=ROOT/"docs/evaluation/KB_BATCH75_EDITORIAL_SUBCLAUSE_MATRIX.json"
PREV=ROOT/"knowledge/editorial_review/kb_batch75_cross_track_teacher_drafts.json"
QUEUE=ROOT/"docs/evaluation/KB_BATCH53_CROSS_PAGE_REVIEW_QUEUE.json"
OUT=ROOT/"docs/evaluation/KB_BATCH76_CROSS_TRACK_COMPARISON_QUEUE.json"
MD=ROOT/"docs/evaluation/KB_BATCH76_CROSS_TRACK_COMPARISON_QUEUE.md"

# Each line records a HUMAN-REVIEW CANDIDATE and the precise difference in
# definitions/objects/assumptions; NEVER treat the annotation as certification.
# Format ID | topic | comparison target | relationship | necessary boundary | falsifying / separating example.
DATA="""KB75-P016-S02|条件方向|KB75-M01|SAME_TOPIC_UNCERTIFIED|必要条件与充分条件需要固定论域并分别检查P⇒Q与Q⇒P|n为2的倍数并不能推出n为4的倍数
KB75-P016-S03|量词命题|KB75-M07|RELATED_DISTINCT|含量词命题的否定要交换全称与存在,而命题逆否要求逻辑蕴含形式|否定∀x∈R,x²≥0是∃x∈R,x²<0而不是对每个x取另一个全称
KB75-P027-S01|复数几何|KB75-M08|RELATED_DISTINCT|复数乘法对应以原点为中心的旋转伸缩而y轴反射是共轭后再取负实部|乘i使1变成i,不是关于y轴反射得到-1
KB75-P032-S02|抽样推断|KB75-M02|SAME_TOPIC_UNCERTIFIED|样本统计量与总体参数的差异不因增加观测数自动消失;需要抽样机制|只调查班级最高分的学生即使人数较多也可能有偏
KB75-P046-S03|条件概率与分布|KB75-M03|PARTIAL_TOPIC_OVERLAP|条件概率定义要求P(B)>0,离散随机变量和正态分布涉及不同样本空间与分布假设|连续正态变量P(X=0)=0,不能对该零概率事件直接套用初等条件概率除法
KB75-P046-S04|相关回归与列联|KB75-M02|RELATED_DISTINCT|样本均值只是描述中心;回归还需要拟合假设,列联分析则针对分类变量|均值相同的两组数据可以有完全不同的相关结构
KB75-P052-S02|数列与函数极限|KB75-M05|RELATED_DISTINCT|数列n趋于正无穷与函数x趋于某实点的极限在变量域和量词上不同|(-1)^n是有界数列但不收敛,与函数某点的极限并不等价
KB75-P052-S03|连续性|KB75-M05|RELATED_DISTINCT|连续需要点值存在并等于极限,仅有邻域差商或极限并不充分|f(x)=x²(x≠0),f(0)=1,在0处极限为0但不连续
KB75-P052-S04|导数微分定积分|KB75-M05|PARTIAL_TOPIC_OVERLAP|偏导要固定另一自变量;原函数积分定理需连续性等前提,不是对所有函数直接互换运算|绝对值函数在0不可导,不能用全区间处处可导作为无条件前提
KB75-P056-S02|连续分布|KB75-M04|SAME_TOPIC_UNCERTIFIED|连续密度f(x)值非点概率;均匀分布只是连续分布的特殊例|f(x)=2x(0≤x≤1)是合法密度但并不均匀
KB75-P056-S03|联合边缘分布|KB75-M04|RELATED_DISTINCT|二维边缘概率必须对另一变量求和或积分;区间一维密度不能直接代替联合分布|二维事件概率的联合质量不必等于两个边缘概率的乘积
KB75-P056-S04|统计推断与回归|KB75-M02|RELATED_DISTINCT|参数检验需抽样分布与误差假设,回归不能从样本均值推得因果关系|两个变量随共同时间趋势上升可相关但无直接因果
KB75-P058-S02|二元偏导|KB75-M05|SAME_TOPIC_UNCERTIFIED|偏导的另一变量固定是定义的一部分,沿曲线的全导数另有链式法则|f(x,y)=xy沿y=x的导数2x并非其x偏导在y=x的值x
KB75-P058-S03|一元微积分|KB75-M05|RELATED_DISTINCT|一元导数是单变量差商极限,偏导是限定方向,微分与定积分有额外条件|在y=x路径上的f(x,y)=xy导数2x不是固定y所得x
KB75-P060-S01|三维向量|KB75-M08|RELATED_DISTINCT|三维叉积的方向依赖取向且仅在三维欧氏空间采用通常叉积;内积是标量|e1×e2=e3而e2×e1=-e3,不能当作内积交换律
KB75-P060-S02|行列式可逆|KB75-M06|PARTIAL_TOPIC_OVERLAP|det(A)≠0表征可逆,但矩阵本身的行列式与线性方程组唯一解是不同对象|A有两行相等则det=0,不能写逆矩阵
KB75-P060-S03|线性系统唯一解|KB75-M06|SAME_TOPIC_UNCERTIFIED|Ax=b唯一解需要系数矩阵满列秩,方阵情况下等价于非零行列式|A=0,b=0解不唯一;A=0,b≠0无解
KB75-P061-S02|二维连续分布|KB75-M04|RELATED_DISTINCT|一维连续均匀密度只给单变量分布;二维联合模型必须另给依赖结构|相同两个边缘均匀分布可有独立或完全依赖两种不同联合分布
KB75-P061-S03|估计与多元回归|KB75-M02|RELATED_DISTINCT|回归系数涉及多个自变量与可辨识性,样本均值本身不能确定偏回归系数|两个解释变量完全相同时设计矩阵列线性相关
KB75-P061-S04|聚类与试验设计|KB75-M02|RELATED_DISTINCT|无监督聚类标签不自动等于因果组别;正交试验设计与样本平均数目标不同|按身高聚类得到群组不证明身高导致成绩变化
KB75-P063-S02|曲线模型选择|KB75-M06|RELATED_DISTINCT|解析几何曲线是点集约束,回归模型还含噪声与统计拟合条件|y=x²的三点可以被多条不同高次多项式插值
KB75-P063-S03|指数与周期|KB75-M04|RELATED_DISTINCT|指数增长一般不周期,三角函数周期模型具有非零周期;对有限观测不能仅凭单调性判定模型|2^t无非零周期但sin(t)有周期2π
KB75-P063-S04|参数曲线|KB75-M05|RELATED_DISTINCT|参数曲线斜率dy/dx=(dy/dt)/(dx/dt)要求dx/dt非零;不能除零|x=t²,y=t³在t=0时dx/dt=0,不能用该分式求斜率
KB75-P064-S03|定义与证明|KB75-M07|PARTIAL_TOPIC_OVERLAP|定义规定符号对象,命题可判真假;逆否证明仅适用于蕴含命题|圆的定义本身不是有真值且待证明的定理
KB75-P066-S02|经济社会建模|KB75-M02|RELATED_DISTINCT|从样本统计量到社会因果模型需额外识别假设且不得偷换量纲|销量上升和气温上升的相关不直接证明气温是唯一原因
KB75-P069-S03|审美与数学对称|KB75-M08|PARTIAL_TOPIC_OVERLAP|轴对称是严格保距映射,视觉和谐是设计评价,不能自动认证轴对称|形状看上去平衡并不说明每点关于同一直线有对应反射点"""

def canon(d):return json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
def audit():
 source=json.loads(MATRIX.read_text(encoding="utf8"))
 older=json.loads(PREV.read_text(encoding="utf8"))
 cross=json.loads(QUEUE.read_text(encoding="utf8"))
 atoms={r["id"]:r for r in source["records"] if r["role"]=="KNOWLEDGE_CANDIDATE"}
 lessons={x["id"] for x in older["teacher_drafts"]}
 assert len(atoms)==26 and len(lessons)==8 and cross["cross_page_topic_links"]>=29
 cases=[]
 for line in DATA.splitlines():
  cid,topic,target,relation,boundary,counter=line.split("|")
  a=atoms[cid]; assert target in lessons
  assert relation in {"SAME_TOPIC_UNCERTIFIED","PARTIAL_TOPIC_OVERLAP","RELATED_DISTINCT"}
  assert len(boundary)>15 and len(counter)>14 and topic
  cases.append(dict(id="KB76-"+cid,source_editorial_subspan_id=cid,
    subject=topic,comparison_existing_draft_id=target,
    proposed_relation=relation,relation_not_teacher_certified=True,
    mathematical_boundary=boundary,separating_counterexample=counter,
    printed_page=a["printed_page"],source_segment_id=a["source_segment_id"],
    source_subspan_sha256=a["local_source_subspan_sha256"],
    source_pdf_sha256=a["source_pdf_sha256"],track_hint=a["track_hint"],
    official_count_contribution=None,review_status="REVIEW_PENDING",
    teacher_signature=None,mathematical_equivalence_certified=False,
    teacher_only=True,student_publishable=False))
 assert len(cases)==26 and {r["source_editorial_subspan_id"] for r in cases}==set(atoms)
 out=dict(schema_version="kb76-provisional-math-equivalence-review-v1",
   source_editorial_matrix_sha256=hashlib.sha256(MATRIX.read_bytes()).hexdigest(),
   previous_review_queue_sha256=hashlib.sha256(QUEUE.read_bytes()).hexdigest(),
   source_pdf_sha256=source["source_pdf_sha256"],all_26_candidates_audited=True,
   previous_cross_page_topic_links=cross["cross_page_topic_links"],
   teacher_full_page_reviews=0,teacher_approved=0,student_published=0,
   official_denominators={k:None for k in source["official_denominators"]},
   statement="Editorial boundary evidence only. No formal equivalence or count certified.",
   project_relation_counts=dict(sorted(Counter(z["proposed_relation"] for z in cases).items())),
   track_counts=dict(sorted(Counter(z["track_hint"] for z in cases).items())),
   cases=cases)
 validate(out);return out

def validate(d):
 source=json.loads(MATRIX.read_text(encoding="utf8"))
 index={r["id"]:r for r in source["records"] if r["role"]=="KNOWLEDGE_CANDIDATE"}
 assert d["source_editorial_matrix_sha256"]==hashlib.sha256(MATRIX.read_bytes()).hexdigest()
 assert d["previous_review_queue_sha256"]==hashlib.sha256(QUEUE.read_bytes()).hexdigest()
 assert d["source_pdf_sha256"]==source["source_pdf_sha256"]
 assert d["teacher_full_page_reviews"]==d["teacher_approved"]==d["student_published"]==0
 assert d["official_denominators"]==source["official_denominators"] and all(v is None for v in d["official_denominators"].values())
 assert d["all_26_candidates_audited"] is True and len(d["cases"])==26
 assert {r["source_editorial_subspan_id"] for r in d["cases"]}==set(index)
 for row in d["cases"]:
  src=index[row["source_editorial_subspan_id"]]
  assert row["source_subspan_sha256"]==src["local_source_subspan_sha256"]
  assert row["source_segment_id"]==src["source_segment_id"]
  assert row["track_hint"]==src["track_hint"]
  assert row["source_pdf_sha256"]==src["source_pdf_sha256"]
  assert row["printed_page"]==src["printed_page"]
  assert row["comparison_existing_draft_id"] in {x["id"] for x in json.loads(PREV.read_text(encoding="utf8"))["teacher_drafts"]}
  assert row["proposed_relation"] in {"SAME_TOPIC_UNCERTIFIED","PARTIAL_TOPIC_OVERLAP","RELATED_DISTINCT"}
  assert row["official_count_contribution"] is None
  assert row["relation_not_teacher_certified"] is True and row["mathematical_equivalence_certified"] is False
  assert row["review_status"]=="REVIEW_PENDING" and row["teacher_signature"] is None
  assert row["teacher_only"] is True and row["student_publishable"] is False
  assert len(row["mathematical_boundary"])>15 and len(row["separating_counterexample"])>14
 assert d["project_relation_counts"]==dict(sorted(Counter(z["proposed_relation"] for z in d["cases"]).items()))
 assert d["track_counts"]==dict(sorted(Counter(z["track_hint"] for z in d["cases"]).items()))
 return True

def markdown(d):
 rows=["# Batch76｜26项跨轨数学语义比对（项目编辑候选，非正式去重）","",
  "- 26/26条Batch75知识候选均已与既有教学草案比较；29项历史跨页链接仍为待裁决线索。",
  "- 每项列出数学前提差别与可区分两者的反例/边界；不会把相关话题当作数学等价。",
  "- **没有裁定任何一个课程官方知识原子**；七轨分母均保持null，0/61页教师完整原子审核。",
  "- 任何SAME_TOPIC_UNCERTIFIED都需要真实教研审核，不得自动合并。",
  "", "| 候选及课程轨道 | 旧草案 | 关系候选 | 定义域/数学前提区别 |", "|---|---|---|---|"]
 for r in d["cases"]:
  rows.append(f"| {r['source_editorial_subspan_id']}（{r['track_hint']}） | {r['comparison_existing_draft_id']} | {r['proposed_relation']} | {r['mathematical_boundary']} |")
 rows+=["","## 不可自动结案","- 源材料仍需独立全文教师审查。538个历史证明步骤与10组冲突保持开放。",""]
 return "\n".join(rows)

def main():
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args()
 d=audit();m=markdown(d)
 if a.check:
  assert OUT.read_text(encoding="utf8")==canon(d)
  assert MD.read_text(encoding="utf8")==m
 else:
  OUT.write_text(canon(d),encoding="utf8")
  MD.write_text(m,encoding="utf8")
 print("KB76 cross-track candidate boundary reviews",len(d["cases"]),d["project_relation_counts"])
if __name__=="__main__":main()
