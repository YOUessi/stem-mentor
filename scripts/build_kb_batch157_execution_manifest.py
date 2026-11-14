#!/usr/bin/env python3
"""Authentic logged Mac run evidence; byte-for-byte archive and negative verification."""
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch157_lessons as content
import build_kb_batch157_scope_ledger as scope
import check_kb_batch157_math as exact
SOURCE_COMMIT="ab3b93e4bd8ba91d7779715efb3927bc019dcdcb"
DIR=ROOT/"docs/evaluation/logs";PREFIX="KB_BATCH157"
CODE={"FOCUSED_INITIAL":1,"FOCUSED":0,"NODE":0,"BROWSER":0,"MAC_FULL":0}
OUT=ROOT/"docs/evaluation/KB_BATCH157_TEST_MANIFEST.json"
REPORT=ROOT/"docs/evaluation/KB_BATCH157_EXECUTION_2026-11-14.md"
def gate(ok,msg):
    if not ok:raise ValueError("KB157 Mac log validation: "+msg)
def sha(bs):return hashlib.sha256(bs).hexdigest()
def serialize(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
def collect(logdir=DIR):
    runs={};txt={}
    for kind,code in CODE.items():
        log=logdir/f"{PREFIX}_{kind}.log";exitfile=logdir/f"{PREFIX}_{kind}.exit"
        gate(log.is_file() and exitfile.is_file(),"missing logfile and exit "+kind)
        raw=log.read_bytes();ex=exitfile.read_bytes()
        gate(len(raw)>150 and ex.strip()==str(code).encode(),"faked outcome "+kind)
        try:body=raw.decode("utf8")
        except UnicodeDecodeError as e:raise ValueError("log not UTF8 "+kind) from e
        gate("\x00" not in body,"binary log "+kind)
        runs[kind]={"log_path":"docs/evaluation/logs/"+log.name,"sha256":sha(raw),"bytes":len(raw),
                    "exit_path":"docs/evaluation/logs/"+exitfile.name,"exit_sha256":sha(ex),
                    "exit_code":code}
        txt[kind]=body
    for k,pat in [("FOCUSED_INITIAL",r"313 passed, 1 warning, 334 errors"),
                  ("FOCUSED",r"647 passed, 1 warning"),
                  ("NODE",r"# pass 111"),("BROWSER",r"Chrome browser suite passed"),
                  ("MAC_FULL",r"66,?293 passed, 5 skipped")]:
        gate(re.search(pat,txt[k]) is not None,"missing original test count "+k)
    gate("ledger.markdown(result)" in txt["FOCUSED_INITIAL"] and "AssertionError" in txt["FOCUSED_INITIAL"],
         "first failed case was not preserved")
    gate("# fail 0" in txt["NODE"] and "# tests 111" in txt["NODE"],"Node failures hidden")
    gate("GREEN v0.7 Chrome test: 9 passed" in txt["BROWSER"] and
         re.search(r"\b2 passed\b",txt["BROWSER"]) is not None,"Chrome/pytest incomplete")
    for s in ["PASS KB157 ten source-locked deep drafts","PASS KB157 315 numbered obligations",
              "PASS 10 independently authored, unpublished KB157 drafts",
              "40/40 independent bounded exact case checks","647 passed","# pass 111",
              "Mac PDFKit source rehash PASS"]:
        gate(s in txt["MAC_FULL"],"Mac full script did not execute "+s)
    return runs
def build(logdir=DIR):
    runs=collect(logdir)
    new=content.build();gate(content.validate(new),"lesson schema")
    audit=content.audit(new);k00=scope.build();gate(scope.validate(k00),"K00 data")
    m=exact.build()
    gate(audit["total_teacher_only_drafts"]==165 and
         audit["historical_candidates_with_drafts"]==124 and
         audit["historical_candidates_without_drafts"]==115,"draft/lead count")
    gate(m["verified_bounded_cases"]==40 and m["invalid_premise_rejected"]==20 and
         m["formal_general_proofs_certified"]==0,"finite math scope")
    gate(k00["numbered_layout_review_obligations"]==315 and
         k00["unnumbered_CDE_pending_proposals"]==32 and
         all(x is None for x in k00["official_atom_denominators"].values()),"official count forged")
    gate(audit["teacher_approved"]==audit["student_authoritative"]==0,"review forged")
    gate(set(json.loads(content.LOCKS.read_text()))==set(content.IDS),"Mac source locks not present")
    return dict(schema="kb157-real-mac-byte-evidence-v1",source_commit=SOURCE_COMMIT,
       execution_date="2026-11-14",environment="Authorized MacBook Air Python3.13 Node Chrome",
       runs=runs,backend_passed=66293,backend_skipped=5,node_passed=111,
       focused_passed=647,focused_initial_passed=313,focused_initial_errors=334,
       chrome_simulated_checks=9,browser_pytest_passed=2,
       independent_finite_math_witnesses=40,rejected_invalid_premise_cases=20,
       original_pdf_rehash="AUTHORIZED_MAC_PDFKIT_PASS",
       copyrighted_standard_text_committed=False,
       pending_manuscripts=165,new_complete_teacher_drafts=10,
       historical_editorial_candidates=239,linked_editorial_leads=124,unlinked_editorial_leads=115,
       numbered_layout_marker_obligations_not_atoms=315,unnumbered_CDE_proposals_pending=32,
       official_atom_denominators=k00["official_atom_denominators"],
       general_proofs_certified=0,free_student_steps_verified=0,teacher_approved=0,
       student_authoritative=0,
       source_only_github_ci_failure=dict(run_id=43592314363,source_commit=SOURCE_COMMIT,
          passed=646,failed=1,cause="PRIVATE_MAC_PDFKIT_CACHE_UNAVAILABLE_ON_LINUX",
          fix="MAC_REPLAYS_ORIGINAL_PDFKIT_LINUX_CHECKS_COMMITTED_HASHES"),
       remote_CI_conclusion="NOT_CONFIRMED_IN_MAC_RUN")
def markdown(x):
    out=[
      "# KB157｜授权Mac原创高中数学知识库开发及完整真实验收（2026-11-14）","",
      "源代码 SHA: "+SOURCE_COMMIT+"。独立Mac feature worktree，不改脏main、不使用Tang、不强推或合并主分支。",
      "新增十篇原创教师候审讲义：必修集合列举与描述、指数时间尺度、经验概率；选择性必修抛物线/双曲线参数退化、正态标准化；选修A自然常数e有限序列/B闭区间极值/C演绎归纳/D周期模型/E复利选修案例。",
      "每篇均含正式定义或定理、全部假设、4条分步论证、适用边界和反例、典型错解及修复、2道原创教师例题、3级无剧透提示及近远迁移。新增20题、30级提示、20项迁移。",
      "新增K00七轨315条逐来源行哈希可审计标记审查义务、32项CDE非编号提案与89条历史边界关系。原始PDF仅在授权Mac上PDFKit复核；315绝不是官方知识原子分母，所有七轨官方分母UNKNOWN。",
      "239条历史编辑候选中124条已关联候审稿，115条未关联；全部165份仍REVIEW_PENDING/TEACHER_ONLY，教师批准0、学生权威发布0。",
      "新增40/40独立SymPy精确有限校验，20项有效/边界、20项失效前提/错误泛化拒绝；不构成一般形式证明、真人审核或学生自由解题认证。",
      "编辑端本地FTS检索和仅聚合状态API，学生请求保持NO_APPROVED_EVIDENCE，教师完整解答不进入学生查询索引。","",
      "## 实际Mac测试（包含交叉重复，不能简单相加）","",
      "| 项目 | 结果 |","|---|---|",
      "| Python后端全量 | 66,293 passed, 5 skipped |",
      "| Node | 111 passed, 0 failed |",
      "| Batch157专项回归 | 647 passed，1条第三方弃用警告 |",
      "| 初始专项失败保留 | 313 passed，334 errors（同一K00表格输出顺序根因），退出码1；修复后647通过 |",
      "| 独立有限数学核验 | 40/40，20项失效前提 |",
      "| Chrome模拟 / 浏览器pytest | 9 checks / 2 passed（非实体iPad） |",
      "| 完整Mac验收 | EXIT 0 |","",
      "## GitHub源码CI失败与修复（非Mac测试）","",
      "首次源代码提交的GitHub Actions #43592314363 FAILED：646项通过、1项失败。失败项是直接在Linux runner读取Mac私有 `/private/tmp/kb117_pdfkit_lines_private.json`，与数学断言失败不同。",
      "修复：Linux runner仅对仓库中已锁定的十组PDF行哈希、页码/行范围及作者候审数据执行一致性门禁；Mac保留且强制实际原始PDFKit行重放，绝不将私有PDF或课标全文上传CI。修改后Mac专项647/647通过。远端新Commit CI终态需再次独立核验。",
      "证据归档验收补充：首次联合运行662项通过、14项共因setup错误，原因为报告按dict插入顺序列出5套日志，而JSON manifest使用sort_keys；修复后使用固定顺序，加入JSON roundtrip负面回归。再次Mac联合运行676项通过，新加入的独立顺序回归随后复跑，不把这些重叠测试算作新讲义。","",
      "## 实际Mac stdout与exit原始哈希","",
      "| 日志类型 | 退出码 | stdout字节数 | stdout SHA256 | exit SHA256 |",
      "|---|---:|---:|---|---|"]
    for k in CODE:
        v=x["runs"][k]
        out.append(f'| {k} | {v["exit_code"]} | {v["bytes"]} | {v["sha256"]} | {v["exit_sha256"]} |')
    out +=["","版本化Manifest与五套stdout/exit逐字节锁定；CI是远端独立运行，不把Linux CI冒充Mac。",
      "## 下批","",
      "K00继续官方课程要求逐句拆分、跨页语义去重和人工审校，冻结七轨实际原子分母；K02–K06按115条剩余历史候选继续整模块扩展。",
      "K07历史538条一般形式未认证证明步骤和10项数学冲突仍需实质评审；K08未见题的规则baseline和真实API还缺独立对照，教师审核为正式发布必要条件。",""]
    return "\n".join(out)
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    a=p.parse_args();v=build()
    for path,contents in [(OUT,serialize(v)),(REPORT,markdown(v))]:
        if a.write:path.write_text(contents,encoding="utf8")
        else:gate(path.read_text(encoding="utf8")==contents,"manifest/report changed "+str(path))
    print("PASS KB157 independent verified authentic Mac logs, actual exit codes and SHA256")
if __name__=="__main__":main()
