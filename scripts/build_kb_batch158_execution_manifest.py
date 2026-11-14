#!/usr/bin/env python3
"""Mac real-run evidence, pinned stdout and exit bytes; not a CI or teacher-approval claim."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch158_lessons as lessons
import build_kb_batch158_scope_ledger as syllabus
import build_kb_batch158_page_triage as pages
import check_kb_batch158_math as math
import check_kb_batch158_teacher_examples as examples

SOURCE_COMMIT="cfa8c42bb16b01ff6f2893c5565fc313fbe9eabd"
KIND={"FOCUSED":"focused","NODE":"node","BROWSER":"browser","COMBINED":"combined","MAC_FULL":"mac_check"}
DIR=ROOT/"docs/evaluation/logs"
SCRATCH=ROOT/"docs/evaluation/kb158_logs"
OUT=ROOT/"docs/evaluation/KB_BATCH158_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH158_EXECUTION_2026-11-14.md"

def gate(ok,message):
    if not ok:raise ValueError("KB158 archived Mac evidence: "+message)
def encode(x):
    return json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+"\n"
def digest(data):return hashlib.sha256(data).hexdigest()
def paths(kind,base=DIR):
    return base/("KB_BATCH158_"+kind+".log"),base/("KB_BATCH158_"+kind+".exit")
def read_logs(base=DIR):
    raw={}
    for k in KIND:
        log,exit_file=paths(k,base)
        gate(log.exists() and exit_file.exists(),"missing paired stdout/exit "+k)
        b,e=log.read_bytes(),exit_file.read_bytes()
        gate(len(b)>150 and e.strip()==b"0","nonzero exit or empty stdout "+k)
        gate(b"\x00" not in b,"binary stdout "+k)
        raw[k]=(b.decode("utf8"),b,e)
    texts={k:v[0] for k,v in raw.items()}
    checks=[
      ("FOCUSED",r"728 passed\b"),("COMBINED",r"769 passed\b"),
      ("NODE",r"# pass 111\b"),("NODE",r"# fail 0\b"),
      ("BROWSER",r"IPAD PILOT CHROME PASS 9"),
      ("BROWSER",r"\b2 passed\b"),("BROWSER",r"Chrome browser suite passed"),
      ("MAC_FULL",r"66,?\d{3} passed, 5 skipped"),
      ("MAC_FULL",r"# pass 111\b"),("MAC_FULL",r"PASS KB158")
    ]
    for k,pattern in checks:
        gate(re.search(pattern,texts[k]) is not None,"missing verified outcome "+k+" "+pattern)
    gate("FAIL" not in texts["NODE"] and "# fail 0" in texts["NODE"],"node failure hidden")
    gate("PDF REHASHED original lines PASS" in texts["MAC_FULL"] or
         "Mac PDFKit source rehash PASS" in texts["MAC_FULL"],
         "private source not originally rehashed")
    return {k:{"path":"docs/evaluation/logs/"+paths(k)[0].name,
                "bytes":len(b),"sha256":digest(b),
                "exit_path":"docs/evaluation/logs/"+paths(k)[1].name,
                "exit_sha256":digest(e),"exit_code":0}
            for k,(t,b,e) in raw.items()},texts

def build(base=DIR):
    logs,txt=read_logs(base)
    authored=lessons.build();gate(lessons.validate(authored),"lesson schema")
    audit=lessons.audit(authored)
    l=syllabus.build();gate(syllabus.validate(l),"scope ledger")
    p=pages.build();gate(pages.validate(p),"61 page review matrix")
    m=math.build();e=examples.build()
    gate(len(authored)==10 and audit["total_teacher_only_drafts"]==175,"draft count")
    gate(audit["historical_candidates_with_drafts"]==134 and
         audit["historical_candidates_without_drafts"]==105,"239 editorial leads coverage")
    gate(m["verified_bounded_cases"]==40 and m["invalid_premise_rejected"]==20 and
         e["worked_examples_checked"]==20,"independent math cases")
    gate(l["numbered_layout_review_obligations"]==315 and
         l["unnumbered_CDE_pending_proposals"]==32 and
         p["source_pages"]==61 and p["review_completed"]==0,"K00 conservation")
    gate(all(v is None for v in l["official_atom_denominators"].values()),"fake official atoms")
    gate(audit["teacher_approved"]==audit["student_authoritative"]==0,"forged teacher approval")
    match=re.search(r"([\d,]+) passed, 5 skipped",txt["MAC_FULL"])
    gate(match is not None,"backend summary unavailable")
    count=int(match.group(1).replace(",",""))
    gate(count>=66000,"incomplete backend")
    return dict(schema="kb158-authentic-mac-execution-v1",source_commit=SOURCE_COMMIT,
        execution_date="2026-11-14",environment="authorized MacBook Air",
        logged_runs=logs,python_backend_full_passed=count,python_backend_skipped=5,
        node_passed=111,node_failed=0,browser_chrome_checks=9,browser_pytest_passed=2,
        focused_passed=728,combined_regression_passed=769,
        independent_finite_witnesses=40,independent_teacher_examples_checked=20,
        rejected_invalid_premises=20,general_proofs_certified=0,
        pending_drafts=175,new_teacher_only_drafts=10,
        historical_editorial_candidates=239,linked=134,unlinked=105,
        source_layout_markers_not_official_atoms=315,unnumbered_CDE_proposals=32,
        pending_source_relations=89,source_pages=61,
        official_atom_denominators=l["official_atom_denominators"],
        teacher_approved=0,student_authoritative=0,
        student_free_text_steps_verified=0,remote_ci_final_result="NOT_YET_VERIFIED",
        official_pdf_text_committed=False)

def markdown(x):
    return "\n".join([
       "# KB158｜Mac真实执行与课程审查证据（2026-11-14）","",
       "本批源代码Git commit："+SOURCE_COMMIT+"；最终远端PR及SHA另于GitHub核验记录。",
       "在MacBook Air独立worktree中新增10份完整原创教师候审稿：必修有理指数幂、三角和差恒等式、均值/中位数/众数；选择性必修空间距离和Pearson相关；选修A极限ε–δ、B二维联合分布、C相关与因果、D几何对称、E大学先修概率案例。",
       "10份共20道教师例题、30级学生提示、20项近远迁移，全部REVIEW_PENDING/TEACHER_ONLY。",
       "K00对61页记录315个非原子排版来源标记、32个CDE未编号提案、89条边界关系，按页分流；七轨原子分母仍UNKNOWN，没有虚假课标完成率。",
       "239条编辑线索：134条已有候审稿、105条尚未关联完整稿；累计175份教师候审、批准0、学生权威发布0。",
       "K07原有40项SymPy有限见证（20负面）外，本批增加独立20道教师例题逐题精确重算与41项反篡改/失败Oracle测试；60项有限校验不构成一般证明。",
       "本批的作者字段、课程证据哈希和受控摘要可由编辑本地FTS检索；学生端仍NO_APPROVED_EVIDENCE，教师例题/解答不进入索引。","",
       "## 真实Mac测试（测试有重叠，绝不直接求和）","",
       "| 项目 | 结果 |","|---|---|",
       f"| Python全量后端 | {x['python_backend_full_passed']:,} passed, 5 skipped |",
       "| Node | 111/111 passed |",
       "| Batch158原专项 | 728 passed |",
       "| 新增例题Oracle与防篡改单独测试 | 41 passed |",
       "| Batch158原专项＋新增Oracle合并 | 769 passed |",
       "| SymPy与独立例题有限验证 | 40+20项；20项错误前提拒绝 |",
       "| Chrome模拟与浏览器pytest | 9交互组，2 passed，非实体iPad |",
       "| 原始授权Mac PDFKit复核 | PASS，未上传PDF正文 |",
       "| 完整Mac脚本退出码 | 0 |","",
       "## 原始stdout、退出码及SHA-256","",
       "| Mac运行 | 退出码 | 日志字节 | 日志SHA256 | exit SHA256 |",
       "|---|---:|---:|---|---|",
       *[f"| {k} | {v['exit_code']} | {v['bytes']} | {v['sha256']} | {v['exit_sha256']} |"
         for k,v in sorted(x["logged_runs"].items())],
       "", "五套日志和退出码逐字节归档；负面测试会检测篡改/缺失。最终GitHub Actions结果需另行核查。",
       "",
       "## 尚缺的最终DoD","",
       "K00继续原文课程要求逐句拆分、跨页语义等价/包含裁决，冻结七轨正式原子分母；K02-K06补105条历史线索；K07核查538项未获得一般形式认证的证明步骤和10项冲突；K08完成冻结未见题API-vs规则基线评测；K09需真实教师逐篇审核后方可发布。",""])

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    a=p.parse_args()
    if a.write:
        DIR.mkdir(parents=True,exist_ok=True)
        for k,name in KIND.items():
            for ext in ("stdout.txt","exit.txt"):
                src=SCRATCH/f"{name}.{ext}"
                target=paths(k)[0 if ext=="stdout.txt" else 1]
                gate(src.exists(),"missing raw original "+src.name)
                target.write_bytes(src.read_bytes())
    x=build()
    artifacts=((OUT,encode(x)),(REPORT,markdown(x)))
    for path,body in artifacts:
        if a.write:path.write_text(body,encoding="utf8")
        else:gate(path.read_text(encoding="utf8")==body,"manifest drift "+str(path))
    print("PASS KB158 authentic Mac stdout/exit/SHA corpus; no release or teacher approval asserted")
if __name__=="__main__":main()
