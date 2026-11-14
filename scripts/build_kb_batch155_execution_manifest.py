#!/usr/bin/env python3
"""KB155 immutable raw-Mac-log evidence; every claimed PASS checked in original output.

GitHub CI verifies committed log byte SHA, but cannot re-open private syllabus.
Do not infer formal proof, teacher approval, or national syllabus completion.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
import build_kb_batch155_review_matrix as matrix
import build_kb_batch155_eight_line_locks as eight
import audit_kb_batch155_draft_readiness as audit
import check_kb_batch155_exact_cases as exact
SOURCE_COMMIT="4fa4737503e3092c0980e8f2881671b11ba92927"
LOG_DIR=ROOT/"docs/evaluation/logs"
PREFIX="KB_BATCH155"
LOG_NAMES=("FOCUSED","NODE","BROWSER","MAC_FULL")
OUT=ROOT/"docs/evaluation/KB_BATCH155_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH155_EXECUTION_2026-11-14.md"
def need(v,s):
    if not v:raise ValueError("KB155 authentic Mac run evidence: "+s)
def encode(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+"\n"
def sha(b):return hashlib.sha256(b).hexdigest()
def read_runs(logdir=LOG_DIR):
    entries={}; texts={}
    for name in LOG_NAMES:
        lp=logdir/f"{PREFIX}_{name}.log";ep=logdir/f"{PREFIX}_{name}.exit"
        need(lp.is_file() and ep.is_file(),f"missing {name} actual log or exit")
        raw=lp.read_bytes();code=ep.read_bytes()
        need(len(raw)>100 and code==b"0\n",f"nonzero/empty {name}")
        content=raw.decode("utf-8")
        need("\x00" not in content,f"binary {name}")
        entries[name]=dict(path=f"docs/evaluation/logs/{lp.name}",
            sha256=sha(raw),bytes=len(raw),exit_path=f"docs/evaluation/logs/{ep.name}",
            exit_sha256=sha(code),exit_code=0)
        texts[name]=content
    def has(s,needle,msg):
        need(re.search(needle,s) is not None,msg+" not in authentic output")
    has(texts["FOCUSED"],r"\b917 passed\b","new focused 746+171 tests")
    need("KB155 PASS: 61 source pages" in texts["FOCUSED"] and
        "eight missing source-line locks reconciled" in texts["FOCUSED"] and
        "KB155 exact finite: 30/30" in texts["FOCUSED"],
        "Mac private original / math guards not in focused log")
    need("# pass 111" in texts["NODE"] and "# fail 0" in texts["NODE"],
        "Node frontend 111 real passes")
    need("IPAD PILOT CHROME PASS 9" in texts["BROWSER"] and
        "Chrome browser suite passed" in texts["BROWSER"],"browser Chrome execution")
    has(texts["BROWSER"],r"\b2 passed\b","browser pytest")
    has(texts["MAC_FULL"],r"\b66,?293 passed, 5 skipped\b","66,293 Mac full backend regression")
    need("Mac PDFKit source rehash PASS" in texts["MAC_FULL"] and
         "# pass 111" in texts["MAC_FULL"],"original Mac source replay and Node regressions")
    return entries
def build(logdir=LOG_DIR):
    logs=read_runs(logdir)
    g=matrix.build();matrix.validate(g)
    e=json.loads(eight.OUT.read_text(encoding="utf-8"));eight.validate(e)
    a=audit.build();audit.validate(a)
    x=exact.run()
    need(len(g["source_marker_obligations"])==315 and
         len(g["unnumbered_CDE_editorial_obligations"])==32 and
         len(g["old_draft_proposal_lineage_reconciliations"])==41,"source graph mismatch")
    need(a["all_drafts_with_full_field_presence"]==145 and
         a["rehashed_eight_missing_line_locks"]==8 and
         a["inherited_41_proposal_line_locks"]==35 and
         a["legacy_source_lock_shapes"]==6 and
         a["direct_source_span_shapes"]==96,"145-draft provenance mismatch")
    need(x["exact_finite_checks"]==30 and x["formal_general_proofs_certified"]==0,
         "math proof status drift")
    return dict(schema="kb155-authentic-mac-test-and-provenance-record/1",
        source_commit=SOURCE_COMMIT,environment="AUTHORIZED_MACBOOK_AIR_ONLY",
        date="2026-11-14",official_source_pdf_pages=188,
        source_pages_indexed=61,numbered_source_markers_not_atoms=315,
        unnumbered_CDE_proposals_not_atoms=32,provisional_41_atom_proposals=41,
        editorial_source_leads=239,matched_pending_drafts=104,missing_pending_drafts=135,
        teacher_only_drafts=145,new_teacher_drafts_this_batch=0,
        historical_review_audit_null_source_sha=41,
        historical_drafts_reconciled_to_existing_source_locks=41,
        drafts_without_direct_line_sha_before_reconciliation=43,
        old_proposal_drafts_with_inherited_line_sha=35,
        new_mac_rehashed_draft_source_locks=8,
        independently_checked_exact_math_cases=30,
        legal_cases=15,invalid_premise_cases=15,
        current_math_conflicts_pending=10,historical_proof_steps_without_general_certification=538,
        official_atom_denominators={t:None for t in matrix.TRACKS},
        official_course_completion_rate=None,teacher_approved=0,student_authoritative=0,
        teacher_solution_exposed_to_students=False,free_text_student_steps_certified=0,
        general_formal_theorem_certificates=0,mac_backend_passed=66293,
        mac_backend_skipped=5,focused_passed=917,node_passed=111,
        chrome_simulated_checks=9,browser_pytest_passed=2,
        known_limits=[
            "30 exact finite cases do not constitute general theorem proofs",
            "No new complete manuscripts this iteration: 145 previous drafts remain teacher-only",
            "Real teacher official knowledge atom denominators still unresolved",
            "Full Mac source replay available only locally; CI verifies immutable hashes",
            "Physical iPad is not tested by simulated Chrome interactions",
            "Initial test expectation failed for 41 old null source_sha fields; reconciled and re-tested; initial failed console output not archived",
        ],logs=logs)
def render(v):
    p=["# KB155｜Mac源码/验收与来源缺口实际执行（2026-11-14）","",
       f"独立Mac工作树，源码Git commit `{SOURCE_COMMIT}`。基于Batch154（8fc3b14）；未使用Tang、未改变主仓未提交修改、未合并main/强推。","",
       "## K00/K01：真实来源行与课程分母状态","",
       "315个编号排版锚、41项来源提案、239条历史编辑线索、32项未编号C/D/E编辑提案逐条映射到61个课标印刷页（13–73）；89条来源相邻/重叠关系不自动语义合并。以上五种人群**互相重叠、不可相加**，全国七轨正式课程原子分母全部UNKNOWN。",
       "145份候审稿（104条历史编辑线索已关联，135条缺稿）全部为REVIEW_PENDING。新增完整深度讲义0，不虚构内容建设完成。","",
       "## K01历史证据缺口实际修复","",
       "发现历史深度库存表41份提案的source_sha为null，但既有41条原始候审提案已保留页/行SHA锁；本批建立41条关系恢复表，未修改原始记录。",
       "另发现145份真实教学记录中43份没有直接行SHA，35份经已有41条提案锁补齐来源关系，另外8份在**Mac私有PDFKit原始课标逐行重哈希**，与现有源span SHA严格一致；只存哈希与定位，不上传原文。",
       "全145份逐篇字段检查：9类正文存在、至少4项分步理由、2道教师例题、3级学生提示、近远迁移；**该数字仅为结构字段存在率，不代表内容数学正确率、官方覆盖率或教师认可。**",
       "",
       "## K07/K08/K09：有限数学证据与学生拒答","",
       "新增15对独立SymPy/精确有理数测试：15合法样本与15无效前提案例，30/30通过。没有新增一般形式化证明证书，538条历史未认证证明步骤与10项冲突仍待实质裁决。API仅新增安全聚合来源状态路由，学生无已批准证据时NO_APPROVED_EVIDENCE；教师解答继续隔离。",
       "",
       "## 原始Mac测试（结果不得重复相加）","",
       "| 测试 | 真实结果 |","|---|---|",
       "| 145份内容/315来源等本批增量测试 | 917 passed（原先746+171） |",
       "| Mac完整后端回归 | 66,293 passed，5 skipped |",
       "| Node | 111 passed |",
       "| Chrome模拟交互 | 9组通过，浏览器pytest 2 passed |",
       "| 原始课标PDFKit重哈希 | PASS（仅Mac，未导出版权原文） |",
       "| Mac完整脚本退出码 | 0 |",
       "",
       "真实发现并修复：初次专项有41个断言失败，因为旧内容审计确有41个NULL source_sha；替代用原始提案锁溯源且新增41条回归。初始控制台失败未归档，不声称保存其日志。另43个实际讲义缺行SHA已分别继承35条旧证据及8条Mac真实重哈希恢复。",
       "已保留真实原始stdout与exit码，并对每项记录字节长度及SHA-256（CI离线复核，不假装在CI重新打开私有官方课标）。",
       "",
       "| 日志 | Exit | 字节 | SHA-256 |","|---|---:|---:|---|"]
    for name,r in sorted(v["logs"].items()):
        p.append(f"| {name} | {r['exit_code']} | {r['bytes']} | `{r['sha256']}` |")
    p+=["","## 后续严格未完成项","",
        "K00：原课标所有编号/未编号数学要求需真人逐句拆分与跨页去重，七轨正式原子分母仍UNKNOWN；沿135个无完整稿历史线索扩充高质量讲义。",
        "K07：538条未获一般认证的历史证明步骤和10项数学冲突待教师/数学验证。",
        "K08/K09：需要真实未知题Agent对规则baseline的可复现评测、真人教师审校，再开放任何学生权威知识。",
        "当前教师批准0，正式学生知识发布0；自动化续建应继续。",""]
    return "\n".join(p)
def main():
    p=argparse.ArgumentParser()
    o=p.add_mutually_exclusive_group(required=True)
    o.add_argument("--write",action="store_true");o.add_argument("--check",action="store_true")
    a=p.parse_args()
    v=build();doc=render(v)
    if a.write:
        OUT.write_text(encode(v),encoding="utf-8")
        REPORT.write_text(doc,encoding="utf-8")
    else:
        need(OUT.exists() and OUT.read_text(encoding="utf-8")==encode(v),"record checksum/metadata drift")
        need(REPORT.exists() and REPORT.read_text(encoding="utf-8")==doc,"execution report drift")
    print("KB155 authentic Mac four-log SHA/exit attestation PASS; teacher approval 0")
if __name__=="__main__":main()
