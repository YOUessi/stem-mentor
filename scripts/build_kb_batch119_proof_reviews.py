#!/usr/bin/env python3
"""Six original proof-review manuscripts linked to K00 semantic candidate IDs.

Mathematically reasoned by project author, not formally machine-certified,
not approved by a teacher, and never student challenge answers.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch119_semantic_pilot as ledger
OUT=ROOT/"knowledge/editorial_review/kb_batch119_six_proof_manuscripts.json"
MD=ROOT/"docs/evaluation/KB_BATCH119_SIX_PROOF_REVIEWS.md"
ROWS=[
{"id":"S03","title":"等差数列前n项和","hypotheses":["n是正整数","等差数列的相邻差恒等于实数d，首项a1已知"],
"conclusion":"S_n=n(a_1+a_n)/2=n[2a_1+(n-1)d]/2。",
"steps":[["确定通项","由等差关系逐次相加，a_k=a_1+(k-1)d。"],
         ["成对对称求和","按正序与逆序分别写S_n，每对第k项与第n+1-k项之和均为a_1+a_n。"],
         ["化简","相加得到2S_n=n(a_1+a_n)，故S_n=n(a_1+a_n)/2。"]],
"boundary":"若相邻差并不恒定，则首尾配对之和不一定固定。",
"counterexample":"序列1,2,4三项之和为7，首尾公式3(1+4)/2=7.5不正确。"},
{"id":"S05","title":"等比数列有限和按q=1分段","hypotheses":["n为正整数","a_k=a_1q^(k-1)，公比q为固定实数；相邻商形式仅在分母非零时可用"],
"conclusion":"q≠1时S_n=a_1(1-q^n)/(1-q)；q=1时S_n=na_1。",
"steps":[["列出求和","S_n=a_1+a_1q+…+a_1q^(n-1)，即使q=0也成立。"],
         ["相减求有限和","qS_n=a_1q+…+a_1q^n，两式相减得(1-q)S_n=a_1(1-q^n)。"],
         ["合法除法","仅当q≠1时除以1-q得到通式；q=1则每项均为a_1，直接求和na_1。"]],
"boundary":"q=1不能套入分母1-q的表达式；首项为0的情形不要用相邻商定义公比。",
"counterexample":"q=1、a1=2、n=4，实际和8，而分式给出0/0未定义。"},
{"id":"A02","title":"有限实极限蕴含全数列有界","hypotheses":["a_n在实数域内","a_n按ε-N定义收敛到有限实数L"],
"conclusion":"存在实数M≥0，使每个正整数n都有|a_n|≤M。",
"steps":[["取固定误差阈值","选ε=1；收敛定义给出N，使n≥N时|a_n-L|<1。"],
         ["控制尾项","由三角不等式，n≥N时|a_n|≤|a_n-L|+|L|<1+|L|。"],
         ["处理有限首项","前N-1项是有限集合，取其绝对值最大值与1+|L|的较大者作为M。"]],
"boundary":"只在实数有限极限成立；有界是必要条件而非充分条件。",
"counterexample":"a_n=(-1)^n有界于[-1,1]，但奇偶子列极限不同，因而不收敛。"},
{"id":"A05","title":"连续函数的介值性质（闭区间）","hypotheses":["a<b","f在[a,b]连续","y位于f(a)和f(b)之间"],
"conclusion":"存在c∈[a,b]满足f(c)=y。",
"steps":[["处理端点并定向","若y是某端点函数值，取该端点；否则不妨设f(a)<y<f(b)。"],
         ["构造嵌套区间","每次取区间中点，保留两端函数值跨过y的那半段，得到长度(b-a)/2^n的嵌套闭区间。"],
         ["取公共极限点","由区间套定理，两端点列趋向同一个c∈[a,b]。"],
         ["使用连续性","两端的函数值始终夹着y，连续性令其极限都为f(c)，故f(c)=y。"]],
"boundary":"不能把闭区间连续性替换成仅端点有定义；图像有跳跃可失效。",
"counterexample":"f(x)在x<0取-1，在x≥0取1，定义于[-1,1]，端点跨过0但不存在f(c)=0。"},
{"id":"A06","title":"拉格朗日中值定理的辅助函数证明","hypotheses":["a<b","f在[a,b]连续","f在(a,b)可导"],
"conclusion":"存在c∈(a,b)，使f'(c)=[f(b)-f(a)]/(b-a)。",
"steps":[["构造去除割线的函数","设m=[f(b)-f(a)]/(b-a)，g(x)=f(x)-m(x-a)。"],
         ["核对Rolle前提","g在[a,b]连续、在(a,b)可导，而且g(a)=f(a)，g(b)=f(b)-m(b-a)=f(a)。"],
         ["应用Rolle定理","由Rolle（由极值定理与内点极值处导数为零推得），存在c∈(a,b)使g'(c)=0。"],
         ["还原斜率","g'(c)=f'(c)-m，因而f'(c)=m。"]],
"boundary":"区间内部不可导时不能直接用结论；需特别留意a<b。",
"counterexample":"f(x)=|x|定义于[-1,1]，割线斜率0，但两侧可导处导数分别-1和1，缺少可导性导致无符合条件的c。"},
{"id":"S09","title":"利用导数符号判断单调性","hypotheses":["f在[a,b]连续","f在(a,b)可导","所有x∈(a,b)都满足f'(x)≥0"],
"conclusion":"f在[a,b]非减；如果内部处处f'(x)>0，则f严格递增。",
"steps":[["任取顺序两点","对任意a≤u<v≤b，在[u,v]满足中值定理的闭区间连续与开区间可导。"],
         ["由中值定理连接差值与导数","存在c∈(u,v)，f(v)-f(u)=f'(c)(v-u)。"],
         ["使用符号条件","因为v-u>0且f'(c)≥0，故f(v)≥f(u)；严格正则严格大于。"]],
"boundary":"严格递增不要求每一点导数都>0；f'(0)=0也不能单凭此断定极值。",
"counterexample":"f(x)=x³在R严格递增且f'(0)=0，但零不是极值点。"},
]
def demand(ok,msg):
    if not ok:raise ValueError(msg)
def generate():
    atoms=json.loads(ledger.OUT.read_text())
    candidates={x["local_key"]:x for x in atoms["candidates"]}
    out=[]
    for r in ROWS:
        demand(r["id"] in candidates,"missing reviewed atom "+r["id"])
        demand(len(r["hypotheses"])>=2 and len(r["steps"])>=3 and len(r["boundary"])>=20
               and len(r["counterexample"])>=20,"incomplete proof review "+r["id"])
        out.append({
            "proof_review_id":"kb119-proof-"+r["id"].lower(),
            "candidate_id":candidates[r["id"]]["id"],
            "course_track":candidates[r["id"]]["course_track"],
            "source":candidates[r["id"]]["source"],
            "title":r["title"],"hypotheses":r["hypotheses"],
            "claim":r["conclusion"],"proof_steps":[{"claim":a,"justification":b} for a,b in r["steps"]],
            "boundary":r["boundary"],"counterexample":r["counterexample"],
            "review_status":"REVIEW_PENDING","teacher_evidence":None,
            "machine_general_proof_certified":False,"student_authoritative":False,
            "solution_visibility":"TEACHER_ONLY",
        })
    return out
def check(data):
    expect={r["candidate_id"] for r in generate()}
    demand(len(data)==len(ROWS)==6 and {r["candidate_id"] for r in data}==expect,
           "orphan, duplicate or missing proofs")
    for row in data:
        demand(row["review_status"]=="REVIEW_PENDING" and row["teacher_evidence"] is None
               and row["machine_general_proof_certified"] is False
               and row["student_authoritative"] is False
               and row["solution_visibility"]=="TEACHER_ONLY","forged proof certification")
        demand(len(row["hypotheses"])>=2 and len(row["proof_steps"])>=3
               and all(len(s["claim"])>=2 and len(s["justification"])>=12 for s in row["proof_steps"])
               and len(row["boundary"])>=20 and len(row["counterexample"])>=20,
               "missing proof prerequisites and reasoning")
    return True
def exact_oracles():
    n=s.symbols("n",integer=True,positive=True)
    q,a,d=s.symbols("q a d")
    # Finite symbolic identities, not an automatic proof of IVT or MVT.
    for k in range(1,9):
        arithmetic=s.summation(a+(s.Symbol("j")-1)*d,(s.Symbol("j"),1,k))
        demand(s.simplify(arithmetic-k*(2*a+(k-1)*d)/2)==0,"arithmetic identity")
        geom=s.summation(a*q**(s.Symbol("j")-1),(s.Symbol("j"),1,k))
        demand(s.simplify((1-q)*geom-a*(1-q**k))==0,"geometric identity")
    demand(s.diff(s.Symbol("x")**3,s.Symbol("x")).subs(s.Symbol("x"),0)==0,"stationary point")
    return {"arithmetic_n_exact":8,"geometric_n_exact":8,
            "stationary_point_counterexample":1,"finite_checks":17,
            "general_formal_proofs_certified":0}
def markdown(rows):
    chunks=["# Batch119｜6则原创定理证明逐步候审稿","",
            "以下证明为项目作者的可审查文本，**不是形式证明认证或教师APPROVED**；所有完整证明仅教师可见。",""]
    for r in rows:
        chunks+=["## "+r["title"],"", "**全部前提**："+ "；".join(r["hypotheses"]),
                 "","**命题**："+r["claim"],""]
        for i,step in enumerate(r["proof_steps"],1):
            chunks.append(f"{i}. **{step['claim']}**：{step['justification']}")
        chunks+=["","**不能使用的边界**："+r["boundary"],"",
                 "**反例**："+r["counterexample"],""]
    return "\n".join(chunks)
def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    args=p.parse_args()
    rows=generate()
    check(rows)
    proof_math=exact_oracles()
    artifacts={OUT:ledger.formatted(rows),MD:markdown(rows),
               ROOT/"docs/evaluation/KB_BATCH119_PROOF_EXACT.json":ledger.formatted(proof_math)}
    for file,content in artifacts.items():
        if args.write:file.write_text(content)
        else:demand(file.exists() and file.read_text()==content,"proof artifact drift "+str(file))
    print(f"Batch119: {len(rows)} review-pending proof manuscripts, {proof_math['finite_checks']} finite exact verifications; zero teacher approval")
if __name__=="__main__":main()
