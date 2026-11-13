#!/usr/bin/env python3
"""Batch133: original, bounded requirement-to-atom *proposals*, never an official census.

Mac-only --write/--check-mac replays protected source PDFKit lines. CI --check-offline
validates recorded commitments, counts, boundaries and gates without reading PDF.
No copyrighted source passages are emitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_kb_batch132_electives as b132

OUT = ROOT / "curriculum/highschool_math/k00_batch133_atomic_proposals.json"
INDEX = ROOT / "knowledge/editorial_review/kb_batch133_teacher_only_index.json"
REPORT = ROOT / "docs/evaluation/KB_BATCH133_REQUIREMENT_ATOM_DECOMPOSITION.md"
TRACKS = tuple(b132.TRACKS)
SOURCE_SHA = b132.prior.previous.prev.prior.prior.provenance.old.previous.base_scope.evidence.PDF_SHA
# Frozen fingerprint from original-line replay on authorized Mac; offline tampering fails CI.
EXPECTED_LOCK_DIGEST = "084394bd90a61e862ef7d59e6a65d38b03d8214232d515d0a8f720af9544f7cb"

# Each row is author-written, not copied from the protected syllabus.
# id | track | printed page | first/last PDFKit line | type | objective | mathematical precondition | invalid counterexample | prereqs
SPECS = """
c_set_membership|COMPULSORY|15|10|14|Concept|区分元素属于集合与集合包含关系|元素类型与集合元素的判定域必须明确|数字2属于{2}但通常不把2写作{2}的子集|
c_set_subset|COMPULSORY|15|15|16|Concept|识别子集与集合相等的充要条件|两个对象都必须是集合且量词遍历各自元素|{1}属于{{1}}不推出{1}是{{1}}的子集|c_set_membership
c_union_intersection|COMPULSORY|15|17|19|Method|按或和且的逻辑分别计算并集与交集|两集合在同一讨论全集内进行元素判定|A={1}且B={2}时交集为空而并集非空|c_set_membership
c_complement|COMPULSORY|15|20|23|Concept|在给定全集中定义补集并用图表示|必须指定全集U且A是U的子集|若U={1,2}而A={1}则补集为{2}而非全体实数去掉1|c_set_subset
c_sufficiency|COMPULSORY|16|7|11|Concept|辨别P为Q的充分条件与必要条件|逻辑蕴涵方向必须固定并区分前后件|x>2足以推出x>1但x>1不足以推出x>2|
c_equivalence|COMPULSORY|16|12|13|Theorem|判断两个性质是否构成充要条件|两个方向的逻辑蕴涵均须独立证明|x²=4推出x=2不成立因x=-2也满足|c_sufficiency
c_quantifier|COMPULSORY|16|14|15|Concept|识别全称量词与存在量词及论域|谓词P(x)必须有确定论域|对正实数成立的1/x>0不可扩大为对所有实数成立|
c_quantifier_negation|COMPULSORY|16|16|18|Method|对含量词命题逐层进行逻辑否定|否定必须同时交换量词并否定谓词|并非所有实数平方为正不能写成所有实数平方非正|c_quantifier
c_inequality_product|COMPULSORY|16|24|28|Theorem|在非负实数条件下运用均值不等式|a和b均非负且等号当且仅当a=b|a=-1时√ab可能无实数意义不能直接使用|
c_quadratic_roots|COMPULSORY|17|9|11|Method|由判别式判断实二次方程根的个数|二次系数必须非零且系数为实数|a=0时不能用二次判别式分类|
c_quadratic_sign|COMPULSORY|17|12|17|Method|结合抛物线开口和零点求一元二次不等式解集|a不为0且需区别严格与非严格不等号|x²<0在实数域没有解不能误给出区间|c_quadratic_roots
c_function_mapping|COMPULSORY|19|13|17|Concept|用对应规则和定义域描述函数|每个定义域元素恰有一个对应值|x=1对应正负两个不同y值不构成单值函数|
c_piecewise|COMPULSORY|19|18|20|Method|依据分段条件选择正确解析式|必须检查定义域及交界点是否被覆盖或重复|x=0若无任何分段适用不能自动代入左式|c_function_mapping
c_monotonicity|COMPULSORY|19|21|23|Concept|用量词正确叙述指定区间上的单调性|必须固定区间并对任意x1<x2比较|f=x²在整个实轴不是单调递增|c_function_mapping
c_parity|COMPULSORY|19|24|24|Concept|区分偶函数奇函数与定义域对称前提|定义域须关于0对称才可全域比较f(-x)|f(x)=x在(0,1)上不能判为奇函数|c_function_mapping
c_period|COMPULSORY|19|25|25|Concept|从周期定义检查非零周期平移|必须保证平移后的点仍处于定义域且周期非零|f(x)=x没有任何非零周期|c_function_mapping
c_exponential_exp|COMPULSORY|20|19|30|Concept|区分实数指数函数的底数条件与单调性|指数底数a必须严格大于0且不等于1|a=-2时a^x并非对每个实数x均有实数值|c_function_mapping
c_logarithm_law|COMPULSORY|20|31|33|Method|在真数严格正的前提下使用对数运算法则和换底|真数>0且底数>0且不等于1|log(0)未定义且log(x+y)不能一般拆成两个对数|c_exponential_exp
c_log_inverse|COMPULSORY|21|1|5|Theorem|论证同底指数与对数互为反函数|底数>0且不等于1及对数真数>0|当底数a=1时指数不是一一对应故不存在反函数|c_logarithm_law
c_radian|COMPULSORY|21|18|20|Method|通过弧长与半径定义角的弧度并互换度数|圆半径必须正且角度弧度单位一致|把90度直接输入要求弧度的sin会得到错误值|
c_tangent_domain|COMPULSORY|21|21|26|Concept|用单位圆解释三角函数并排除正切无定义点|tan定义为sin/cos时必须cos不为0|tan(pi/2)在实数范围未定义|c_radian
c_cosine_difference|COMPULSORY|22|12|17|Theorem|在单位圆及向量内积下论证两角差余弦公式|角均采用弧度并正确使用旋转及单位圆|把cos(a-b)写成cos(a)-cos(b)通常不成立|c_radian
c_zero_theorem|COMPULSORY|22|27|30|Theorem|在连续性与端点异号前提下确认区间内有零点|f在闭区间连续且f(a)f(b)<0|f在0跳跃由-1变1却没有取0说明不连续时不能套用|c_function_mapping
sc_sequence_model|SELECTIVE_COMPULSORY|38|11|13|Concept|将数列看作正整数集上的特殊函数|明确下标起点和定义域为正整数或指定子集|只定义a_1但没给出后继项不能声称已定义全部数列|
sc_arith_progression|SELECTIVE_COMPULSORY|38|14|20|Theorem|推导等差数列通项与有限前n项和公式|有限n为正整数且各相邻差固定|1,2,4不是等差数列不能套等差求和|sc_sequence_model
sc_geom_progression|SELECTIVE_COMPULSORY|38|21|27|Theorem|通过错位相减证明有限等比和并单独处理q=1|n正整数且符合所采用的等比数列定义|q=1时不能除以1-q且q=0需区别有限幂级数与标准等比定义|sc_sequence_model
sc_induction_optional|SELECTIVE_COMPULSORY|38|28|30|Method|以基例和归纳步骤建立数学归纳法证明|必须明确自然数起点且完成两个证明义务|只证明n=1和n=2不代表已证明全部n|sc_sequence_model
sc_derivative_def|SELECTIVE_COMPULSORY|39|8|13|Concept|由差商极限解释瞬时变化率与切线斜率|双侧极限需存在且为有限实数|绝对值函数在0处左右导数不一致不可导|c_function_mapping
sc_derivative_rules|SELECTIVE_COMPULSORY|39|14|25|Method|对可导函数合法应用四则与简单复合求导|除法求导要求分母在点处不为零|d(1/x)/dx不能在x=0处使用|sc_derivative_def
sc_derivative_monotone|SELECTIVE_COMPULSORY|39|26|29|Theorem|以导数符号作为区间单调性充分条件|在区间可导且导数符号具有全区间保证|f'(0)=0不能说明f在0邻域为常数|sc_derivative_rules
sc_extreme_point|SELECTIVE_COMPULSORY|39|30|33|Method|比较临界点和闭区间端点判定极值与最值|内点导数零仅为可导极值的必要非充分条件|f=x³在0处导数为0但0不是极值|sc_derivative_rules
sc_space_distance|SELECTIVE_COMPULSORY|42|13|17|Theorem|通过坐标差平方和推导三维两点距离|空间坐标轴两两正交且采用同一长度单位|非正交坐标基不能直接按坐标差平方和计算|
sc_space_basis|SELECTIVE_COMPULSORY|42|21|23|Theorem|在三维正交基下唯一展开空间向量|必须使用三条线性无关的基向量|三个共面向量不能唯一展开所有空间向量|sc_space_distance
sc_space_projection|SELECTIVE_COMPULSORY|42|24|26|Method|以点积和非零向量定义投影与数量积|投影到指定向量时被投影轴必须非零|向零向量投影会出现除以零|sc_space_basis
a_sequence_limit|ELECTIVE_A|52|9|21|Concept|由epsilon-N定义序列极限并证明收敛必有界|每个epsilon>0存在阈值N约束全部后续项|a_n=(-1)^n有界但不收敛不能反推有界即收敛|sc_sequence_model
a_monotone_convergence|ELECTIVE_A|52|22|29|Theorem|理解实数完备性下的单调有界收敛结论|须同为单调与有界两个条件|a_n=n单调但无上界不收敛|a_sequence_limit
a_limits_quotient|ELECTIVE_A|52|30|31|Theorem|掌握收敛数列极限四则与商的非零分母条件|使用商法则必须确认分母的极限非零|1除以(1/n)所得n发散|a_sequence_limit
a_function_limit|ELECTIVE_A|52|32|39|Concept|理解函数有限极限epsilon-delta的去心邻域定义|考虑极限点的去心邻域且函数在该邻域有定义|仅f(a)=L不能证明x趋于a时极限为L|c_function_mapping
a_continuity|ELECTIVE_A|53|1|4|Theorem|将函数连续性与区间介值性质联系|闭区间连续才能保证介值结论|阶跃函数端点异号却跳过0|a_function_limit
a_mean_value|ELECTIVE_A|53|10|14|Theorem|利用闭区间连续开区间可导的中值定理讨论不等式|a<b且f在[a,b]连续在(a,b)可导|绝对值函数跨0不可导无法直接套拉格朗日中值定理|sc_derivative_def
a_integral_area|ELECTIVE_A|53|18|27|Method|由定积分有向符号和原函数公式计算累计变化|原函数F导数在积分区间为f|对f(x)=x在[-1,1]积分为0不等于几何面积1|a_continuity
""".strip()

# Do not confuse two curricular occurrences of the same underlying idea with two approved atoms.
REUSE_GROUPS = {
    "c_quadratic_roots": "FUNCTION_ZERO_AND_EQUATION_LINK",
    "c_zero_theorem": "FUNCTION_ZERO_AND_EQUATION_LINK",
    "c_monotonicity": "MONOTONICITY_DIFFERENT_METHODS",
    "sc_derivative_monotone": "MONOTONICITY_DIFFERENT_METHODS",
}
def stable_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"

def assert_ok(b, message):
    if not b: raise ValueError(message)

def spec_rows():
    rows = []
    for line in SPECS.splitlines():
        fields=line.split("|")
        assert_ok(len(fields)==10, "bad source specification: "+line)
        slug,t,p,lo,hi,kind,objective,assumption,negative,prereq=fields
        assert_ok(t in TRACKS and kind in {"Concept","Theorem","Method"},"bad track/type "+slug)
        rows.append(dict(slug=slug, track=t, printed_page=int(p), start_line=int(lo), end_line=int(hi),
                         knowledge_type=kind, objective=objective, hypothesis=assumption,
                         false_inference=negative, prerequisites=[v for v in prereq.split(",") if v]))
    assert_ok(len({r["slug"] for r in rows})==len(rows),"duplicate atom ID")
    return rows

def line_lock(pages, r):
    ls=pages[r["printed_page"]][r["start_line"]-1:r["end_line"]]
    assert_ok(len(ls)==r["end_line"]-r["start_line"]+1 and all(ls),"PDFKit protected lines missing")
    return {"printed_page":r["printed_page"],"start_line":r["start_line"],"end_line":r["end_line"],
            "line_sha256":[hashlib.sha256(x.encode("utf-8")).hexdigest() for x in ls],
            "span_sha256":hashlib.sha256("\n".join(ls).encode("utf-8")).hexdigest()}

def build(pages):
    specs=spec_rows()
    rows=[]
    for r in specs:
        rec={k:v for k,v in r.items() if k not in ("printed_page","start_line","end_line")}
        rec["id"]="kb133-proposal-"+rec.pop("slug")
        rec["prerequisite_proposals"]=["kb133-proposal-"+x for x in rec.pop("prerequisites")]
        rec["cross_page_reuse_group"]=REUSE_GROUPS.get(r["slug"])
        rec["source_lock"]=line_lock(pages,r)
        rec.update(source_role="CURRICULUM_CONTENT_CANDIDATE", source_pdf_sha256=SOURCE_SHA,
                   source_evidence_status="PDFKIT_LINE_REHASHED_SEMANTIC_PENDING",
                   official_atom_id=None, atomization_review="REVIEW_PENDING",
                   teacher_approval=None, teacher_solution_visibility="TEACHER_ONLY",
                   formal_proof_certified=False, student_authoritative=False)
        rows.append(rec)
    counts=Counter(x["track"] for x in rows)
    return dict(schema_version="kb133/1",batch=133,
        inventory_scope="BOUNDED_CONTENT_REQUIREMENT_TO_ATOM_PROPOSALS_UNREVIEWED",
        source_pdf_sha256=SOURCE_SHA,
        does_not_reproduce_official_text=True, proposed_count=len(rows),
        source_spans_count=len({(x["source_lock"]["printed_page"],x["source_lock"]["start_line"],x["source_lock"]["end_line"]) for x in rows}),
        official_atom_denominator=None, full_source_census_complete=False,
        track_denominators={t:None for t in TRACKS},
        by_track_proposals={t:counts[t] for t in TRACKS},
        teacher_approved_count=0, student_authoritative_count=0,
        records=rows)

def validate(d,original_pages=None):
    assert_ok(d["schema_version"]=="kb133/1" and d["batch"]==133 and
              d["inventory_scope"]=="BOUNDED_CONTENT_REQUIREMENT_TO_ATOM_PROPOSALS_UNREVIEWED" and
              d["does_not_reproduce_official_text"] is True and
              d["source_pdf_sha256"]==SOURCE_SHA and
              d["full_source_census_complete"] is False and
              d["official_atom_denominator"] is None and
              d["teacher_approved_count"]==d["student_authoritative_count"]==0,"false official scope or authority")
    assert_ok(set(d["track_denominators"])==set(TRACKS) and all(v is None for v in d["track_denominators"].values()),"forged track denominator")
    specs=spec_rows()
    assert_ok(len(d["records"])==len(specs)==d["proposed_count"],"record count drift")
    expected_ids={"kb133-proposal-"+r["slug"] for r in specs}
    assert_ok({r["id"] for r in d["records"]}==expected_ids,"missing or duplicate ids")
    by_id={r["id"]:r for r in d["records"]}
    assert_ok(d["source_spans_count"]==len({(r["printed_page"],r["start_line"],r["end_line"]) for r in specs}),"source spans wrong")
    assert_ok(d["by_track_proposals"]=={t:sum(r["track"]==t for r in specs) for t in TRACKS},"track count drift")
    for s in specs:
        r=by_id["kb133-proposal-"+s["slug"]]
        assert_ok(r["track"]==s["track"] and r["knowledge_type"]==s["knowledge_type"] and
                  r["objective"]==s["objective"] and r["hypothesis"]==s["hypothesis"] and
                  r["false_inference"]==s["false_inference"],"altered reasoning: "+r["id"])
        assert_ok(len(r["objective"])>=10 and len(r["hypothesis"])>=12 and len(r["false_inference"])>=12,"shallow proposal")
        assert_ok(r["prerequisite_proposals"]==["kb133-proposal-"+x for x in s["prerequisites"]] and
                  all(x in expected_ids and x!=r["id"] for x in r["prerequisite_proposals"]),"invalid prereq")
        assert_ok(r["cross_page_reuse_group"]==REUSE_GROUPS.get(s["slug"]),"overlap drift")
        assert_ok(r["source_pdf_sha256"]==SOURCE_SHA and
                  r["source_role"]=="CURRICULUM_CONTENT_CANDIDATE" and
                  r["source_evidence_status"]=="PDFKIT_LINE_REHASHED_SEMANTIC_PENDING" and
                  r["official_atom_id"] is None and r["atomization_review"]=="REVIEW_PENDING" and
                  r["teacher_approval"] is None and r["teacher_solution_visibility"]=="TEACHER_ONLY" and
                  r["formal_proof_certified"] is False and r["student_authoritative"] is False,"forged approval")
        lock=r["source_lock"]
        assert_ok((lock["printed_page"],lock["start_line"],lock["end_line"])==
                  (s["printed_page"],s["start_line"],s["end_line"]),"source span changed")
        assert_ok(len(lock["line_sha256"])==lock["end_line"]-lock["start_line"]+1 and
                  bool(re.fullmatch("[0-9a-f]{64}",lock["span_sha256"])) and
                  all(re.fullmatch("[0-9a-f]{64}",x) for x in lock["line_sha256"]),"invalid source hash")
        if original_pages is not None:
            assert_ok(lock==line_lock(original_pages,s),"original PDFKit source altered: "+r["id"])
    locks={r["id"]:r["source_lock"] for r in d["records"]}
    digest=hashlib.sha256(stable_json(locks).encode("utf-8")).hexdigest()
    assert_ok(digest==EXPECTED_LOCK_DIGEST,"offline source commitment does not match Mac-frozen digest")
    return True

def safe_student_export(d):
    validate(d)
    # Not an authorized fact index: intentionally contains no objectives, proof or answers.
    return {"status":"NO_AUTHORITATIVE_UNITS", "source_batch":133,"publishable_count":0,
            "items":[], "requires_real_teacher_approval":True}

def render(d):
    lines=["# Batch133 | 有边界的课标要求→拟议知识原子拆解","",
      "本文件是项目原创课程编目提议。**不是完整课程原子分母，不是课标原文，未经教师审核。**",
      "受保护的原始课标仅在 Mac 本地逐行哈希校验，仓库只存 SHA-256 与作者原创释义。",
      "GitHub CI 离线验证无法证明作者的释义忠于原文，必须与教师审查区别。",
      f"本批: {d['proposed_count']} 条拟议原子；{d['source_spans_count']} 个有定位的来源行区间。",
      "七轨正式原子分母: UNKNOWN；APPROVED 0；学生可发布 0。",""]
    for t in TRACKS:
        n = d["by_track_proposals"][t]
        lines.append(f"- {t}: {n} 个项目拟议原子（官方分母 UNKNOWN）")
    lines+=["","## 逐项可审查的范围、前提与失效条件",""]
    for r in d["records"]:
        l=r["source_lock"]
        lines.extend([f"### {r['id']} · {r['track']}",
            f"来源: 印刷页 {l['printed_page']}，PDFKit 行 {l['start_line']}–{l['end_line']}；区间 SHA-256 `{l['span_sha256']}`",
            f"知识类型: {r['knowledge_type']}；作者拟议学习目标: {r['objective']}",
            f"适用前提: {r['hypothesis']}",
            f"失效边界/反例: {r['false_inference']}",
            f"先修: {', '.join(r['prerequisite_proposals']) or '待课程图谱补充'}；跨页复用组: {r['cross_page_reuse_group'] or '无'}",
            "状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。",""])
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check-mac",action="store_true");g.add_argument("--check-offline",action="store_true")
    a=p.parse_args()
    if a.write:
        pages=b132.prior.previous.prev.prior.prior.previous.source_pages()
        d=build(pages);validate(d,pages)
        OUT.write_text(stable_json(d),encoding="utf-8")
        INDEX.write_text(stable_json(safe_student_export(d)),encoding="utf-8")
        REPORT.write_text(render(d),encoding="utf-8")
        print(f"WROTE {len(d['records'])} provisional atoms; {d['source_spans_count']} source spans; all official denominators UNKNOWN")
    else:
        d=json.loads(OUT.read_text(encoding="utf-8"))
        pages=b132.prior.previous.prev.prior.prior.previous.source_pages() if a.check_mac else None
        validate(d,pages)
        assert_ok(json.loads(INDEX.read_text())==safe_student_export(d),"student index leaked pending content")
        assert_ok(REPORT.read_text(encoding="utf-8")==render(d),"report tampered")
        print(("MAC ORIGINAL SOURCE REPLAY" if a.check_mac else "CI OFFLINE COMMITMENT GATE"),
              f"PASS {len(d['records'])} unapproved proposals, 0 student-authoritative")
if __name__=="__main__":main()
