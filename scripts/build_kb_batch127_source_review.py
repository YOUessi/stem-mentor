#!/usr/bin/env python3
"""Batch127: independently contextualised curriculum excerpts, no automatic atom promotion."""
from __future__ import annotations
import argparse, collections, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch125_provenance as provenance
import build_kb_batch126_context_evidence as previous
OUT=ROOT/"docs/evaluation/KB_BATCH127_SOURCE_REVIEW.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH127_SOURCE_REVIEW.md"
LOCKS=ROOT/"curriculum/highschool_math/k00_batch127_source_line_locks.json"
# ID suffix, relationship, original editorial interpretation, unresolved boundary.
# Text composed by reading the authorized PDFKit line windows on Mac, not copied from it.
DETAILS=[
("119-c01","EXPLICIT_NUMBERED_REQUIREMENT","本段是复数的概念、代数表示及相等含义的课程要求，代数式的实虚部相等判据属于可教学内容。","须在学生练习中限定i²=-1与实部虚部分别为实数；这里不等于自动批准任意复数计算证明。"),
("119-c06","EXPLICIT_NUMBERED_REQUIREMENT","该要求同时涉及有限样本空间、样本点、事件以及并交互斥的运算，不能合成一个原子。","有限样本点的定义与古典概型的等可能假设不能混淆，样本空间的结果应不重不漏。"),
("120-c101","EXPLICIT_NUMBERED_REQUIREMENT","向量加减的几何表示及运算法则有直接课程要求，三角形法则是可拆分的具体教学方法。","箭头的首尾连接、坐标分量相加及零向量方向的表述仍需独立校验。"),
("120-c102","EXPLICIT_NUMBERED_REQUIREMENT","数乘的几何意义及向量共线均有要求，线性运算性质应独立分拆而非作为数乘定义的一部分。","共线判据u=λv若用v为方向基准必须注明v≠0，零向量不能给出唯一方向。"),
("119-s02","EXPLICIT_NUMBERED_REQUIREMENT","数列的等差概念与通项公式出现在编号要求中，公差由相邻差恒定确定。","数列首项和起始下标须统一，有限等差数列的最后一项不能要求不存在的下一项。"),
("119-s03","EXPLICIT_NUMBERED_REQUIREMENT","该段明确要求掌握等差数列前n项和及与通项的关系，可以拆成公式与差分关系两个对象。","必须限定n为实际项数且n≥1，误把末项当首项会使求和数值错误。"),
("119-s04","EXPLICIT_NUMBERED_REQUIREMENT","等比数列的概念和通项公式有课程要求，但当前段落没有完整固定公比取值范围。","初项为零、q为零以及比值法对零项不可定义的歧义必须保留待专家确认。"),
("119-s05","EXPLICIT_NUMBERED_REQUIREMENT","编号要求明确探索等比前n项和以及它和通项的联系，应区分q=1分支。","有限几何求和式可代数扩展到q=0，不能据此断言该零公比情形自动满足选用的等比数列定义。"),
("119-a01","FORMAL_DEFINITION_REQUIRED","选修A的数列极限段落包含ε-N形式量词以及若干收敛示例，需单列正式定义。","应写∀ε>0存在N使所有n≥N满足不等式；数字试验不是全称证明，PDFKit公式存在排版损失。"),
("119-a02","EXPLICIT_PROOF_REQUIREMENT","独立段落要求探索并证明收敛数列有界，因此属于需要完整证明前提的定理教学。","证明必须把有限前缀上界与N以后的尾项界结合，不能用极限值直接作为所有项上界。"),
("119-a03","MATHEMATICAL_FACT_AND_EXAMPLES","该段以多个单调有界示例引入单调收敛事实；示例不能替代对所有实数序列的论证。","数列必须在实数系且同时单调、有界；若只单调无界则可能发散。"),
("119-a04","FORMAL_DEFINITION_REQUIRED","函数极限段落包含ε-δ定义与典型示例，概念依赖去心邻域与接近点的定义域。","要明确0<|x-a|<δ而非只含x=a；公式抽取有乱码，需原始PDF图像审查。"),
("119-b01","EXPLICIT_NUMBERED_REQUIREMENT","导数与微分下的具体要求同时包含二阶导数的概念、意义和常见函数求导。","二阶导数需要一阶导数在邻域内可微，不能在不可导点机械地再求导。"),
("119-b02","EXPLICIT_NUMBERED_REQUIREMENT","中值定理应用要求涉及单调分析与不等式证明，并非单条公式的复制练习。","中值定理要求闭区间连续和开区间可导，导数符号需在整个目标区间可靠成立。"),
("119-b03","EXPLICIT_NUMBERED_REQUIREMENT","二元函数以具体情境建立概念和定义域，下一要求再引入偏导数；应拆成两条原子。","二元定义域是R²子集，某点可代入不代表对所有方向都可微。"),
("119-b04","EXPLICIT_NUMBERED_REQUIREMENT","偏导数的定义与简单求导示例具直接依据，固定其他变量后计算一维差商。","偏导存在并不足以证明总可微；零分母以及被固定变量的定义域边界需检查。"),
("119-ec01","EXPLICIT_THEME_PARAGRAPH","数学定义、命题与推理及前提结论在专题正文中阐明，但该段跨页继续，须结合下一页。","应将定义与可判真假命题区别，前提真假与蕴含真值不可混为一谈。"),
("119-ec03","EXPLICIT_THEME_PARAGRAPH","专题正文要求理解矛盾律、排中律及其推理作用，列举了两种逻辑原则的辨析。","不能把P∨¬P与¬(P∧¬P)当作同一个语法式；所讨论经典逻辑前提要说明。"),
("119-ec04","EXPLICIT_THEME_PARAGRAPH","该段覆盖演绎、归纳、类比及必然与或然推理，应拆分成推理模式与证据强度。","从有限归纳实例得出的经验猜想不能自动推为全称定理，演绎规则须保证前提可靠。"),
("119-ec05","EXPLICIT_THEME_PARAGRAPH","专题要求认识常用证明方法，直接证法和反证法是候选教材细化示例而非课标列出的唯一方法。","反证法依赖反设到矛盾的合法步骤，不能用结论本身作隐含前提。"),
("119-ed01","THEMATIC_APPLICATION_NOT_FIXED_ATOM","选修D将简洁、对称、周期等数学表达作为审美主题，正文举例只是可能的教学情境。","不能从美感描述推出唯一形式数学命题；轨迹的现实近似与理想数学曲线需分开。"),
("119-ed02","THEMATIC_APPLICATION_NOT_FIXED_ATOM","数学审美专题列举对称对象，允许设计几何变换判别题，不足以固定全部对称定理。","轴对称、中心对称、平移对称是不同变换；自然或建筑形体未必严格对称。"),
("119-ed03","THEMATIC_APPLICATION_NOT_FIXED_ATOM","周期美的段落用昼夜、海浪和图案等示例开展数学表征，但不直接认证严格周期模型。","有限观测或季节变化不证明f(t+T)=f(t)对所有t成立；须区分近似和严格周期。"),
("119-ed04","THEMATIC_APPLICATION_NOT_FIXED_ATOM","同一周期段落可用于音乐和图案的建模活动，不提供采样周期的独立数学定义。","时间采样别名和实际信号周期不能等同，不能把文字举例误归为单独全国标准知识点。"),
("119-ee01","LOCAL_OPTIONAL_EXAMPLE","选修E是学校开设的示例方向，其中机器人与数学仅是可选专题之一。","不能把机器人坐标变换列为全国必修，更不能把示例等同全国统一内容分母。"),
("119-ee02","LOCAL_OPTIONAL_EXAMPLE","初等数论是选修E拓展视野的示例主题，没有确定同余运算的官方固定教学颗粒度。","若开发同余课程，定义、模非零与等价关系需作者单独建构，并标记学校自选。"),
("119-ee03","LOCAL_OPTIONAL_EXAMPLE","家庭理财作为选修E日常生活主题示例，可开展复利和实际利率建模，而非强制核心公式。","现实利率模型须注明计息周期、税费与通胀；理想模型不能被宣称为现实精确预测。"),
("119-ee04","LOCAL_OPTIONAL_EXAMPLE","大学先修概率统计位列选修E大学先修主题，并非每名高中生都必须完成的课程知识原子。","要在学校自选计划中明确具体目标，不能让高阶内容覆盖高中必修概率统计。"),
]
REL={r[1] for r in DETAILS}
def req(q,msg):
 if not q:raise ValueError(msg)
def dump(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def originals():
 old,res=provenance.audit()
 cand,_,_=provenance.originals()
 return old,{x["id"]:x for x in cand}
def audited():
 old,cand=originals();grades={x["candidate_id"]:x["evidence_grade"] for x in old["records"]}
 pages=previous.source_pages();already={x[0] for x in previous.SPECS}
 seen=set(); rows=[];locks={}
 for suf,rel,why,risk in DETAILS:
  key="hs-semantic-pilot-"+suf
  req(key not in seen and key not in already and key in cand,"duplicate / previously reviewed case")
  seen.add(key);obj=cand[key];source=obj["source"];page=source["printed_page"]
  lo,hi=source["start_line"],source["end_line"]
  req(1<=lo<=hi<=len(pages[page]),"invalid range")
  req(obj["review_status"]=="REVIEW_PENDING" and obj["student_authoritative"] is False,"source escaped review")
  require_track=provenance.old.previous.base_scope.evidence.track_at
  req(all(require_track(page,j)==obj["course_track"] for j in range(lo,hi+1)),"cross-track source")
  req(len(why)>=28 and len(risk)>=28,"empty editorial judgement")
  ls=pages[page][lo-1:hi]
  locks[key]={"page":page,"start_line":lo,"end_line":hi,
    "line_sha256":[hashlib.sha256(t.encode()).hexdigest() for t in ls],
    "span_sha256":hashlib.sha256("\n".join(ls).encode()).hexdigest()}
  rows.append({"id":key,"course_track":obj["course_track"],"source":locks[key],
    "prior_grade":grades[key],"interpretation_class":rel,"editorial_interpretation":why,
    "unresolved_risk":risk,"candidate_objective":obj["proposed_objective"],
    "curriculum_pdf_sha256":provenance.old.previous.base_scope.evidence.PDF_SHA,
    "teacher_status":"REVIEW_PENDING","teacher_signature":None,
    "official_atom_id":None,"proof_machine_certified":False,"student_authoritative":False})
 req(len(rows)==28 and len(seen)==28,"28 contextual cases required")
 result={"batch":127,"cases":28,"previous_editorial_candidates":239,
   "context_reviewed_prior_batch":20,"new_context_reviewed":28,
   "distinct_context_reviewed_total":48,"unreviewed_editorial_candidates":191,
   "source_marker_total":405,"official_atom_total_denominator":None,
   "official_atom_per_track":{t:None for t in sorted(previous.TRACKS)},
   "teacher_approved":0,"student_authoritative":0,
   "review_is_not_formal_math_proof":True,"source_text_embedded":False,
   "counts_by_track":dict(sorted(collections.Counter(x["course_track"] for x in rows).items())),
   "counts_by_relation":dict(sorted(collections.Counter(x["interpretation_class"] for x in rows).items())),
   "records":rows}
 validate(result,locks,regen=False)
 return result,locks
def validate(result,locks,regen=True):
 req(result["batch"]==127 and result["cases"]==len(DETAILS)==28
     and result["previous_editorial_candidates"]==239
     and result["distinct_context_reviewed_total"]==48
     and result["unreviewed_editorial_candidates"]==191
     and result["source_marker_total"]==405,"source denominator drift")
 req(result["official_atom_total_denominator"] is None and result["teacher_approved"]==0
     and result["student_authoritative"]==0
     and result["source_text_embedded"] is False and result["review_is_not_formal_math_proof"] is True
     and all(x is None for x in result["official_atom_per_track"].values()),"fabricated census")
 req(len(result["records"])==28 and len({x["id"] for x in result["records"]})==28
     and set(locks)=={x["id"] for x in result["records"]},"duplicate or missing case")
 req(dict(sorted(collections.Counter(x["course_track"] for x in result["records"]).items()))==result["counts_by_track"]
     and dict(sorted(collections.Counter(x["interpretation_class"] for x in result["records"]).items()))==result["counts_by_relation"],"count drift")
 for r in result["records"]:
  req(r["interpretation_class"] in REL and r["source"]==locks[r["id"]]
      and r["teacher_status"]=="REVIEW_PENDING" and r["teacher_signature"] is None
      and r["official_atom_id"] is None and r["student_authoritative"] is False
      and r["proof_machine_certified"] is False and len(r["unresolved_risk"])>=28,"forged review or source")
 if regen:
  expected,original=audited()
  req(expected==result and original==locks,"unreviewed source manuscript mutation")
 return True
def report(d):
 s=["# Batch127 K00/K01 — source interpretation audit","",
    "All review records are editorial only. A source line hash is not mathematics proof, a teacher sign-off, or a universal mandatory atom.","",
    f"Context cases in Batch127: {d['cases']}; distinct accumulated context-reviewed candidates: {d['distinct_context_reviewed_total']}/239; untouched: {d['unreviewed_editorial_candidates']}.",
    "Seven-track official atom denominators: UNKNOWN. Teacher approved: 0. Student authoritative: 0.",""]
 for r in d["records"]:
  s += [f"## {r['id']} | {r['course_track']}",
    f"Page {r['source']['page']}, lines {r['source']['start_line']}-{r['source']['end_line']} | {r['interpretation_class']}",
    f"**Editorial reading:** {r['editorial_interpretation']}",
    f"**Math/scope risk:** {r['unresolved_risk']}",""]
 return "\n".join(s)
def main():
 a=argparse.ArgumentParser();g=a.add_mutually_exclusive_group(required=True)
 g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
 z=a.parse_args()
 d,locks=audited()
 for path,data in ((OUT,dump(d)),(LOCKS,dump(locks)),(REPORT,report(d))):
  if z.write:path.write_text(data,encoding="utf-8")
  else:req(path.exists() and path.read_text(encoding="utf-8")==data,"published evidence drift "+str(path))
 print("Batch127 28 source dossiers across 7 tracks; 48 cumulative context cases; 191 unreviewed")
if __name__=="__main__":main()
