# STEM Mentor — Batch23 Mac-only verified development, 2026-11-08

**Project:** YOUessi/stem-mentor issues #17–#27. **Independent worktree:** `~/Documents/文件/stem-mentor-kb-batch23`; branch `feat/kb-batch23-core-gaps-conditions`; based on local Batch22 `5f63cac`, corresponding to remote Draft PR #48 tree. Code and all tests ran on the authorized MacBook Air. Tang never used. No original main-worktree dirty files were touched, no merge to main.

**Safety release:** all 267 strict deep lessons are `REVIEW_PENDING`, `TEACHER_ONLY`. `APPROVED=0`, student release 0, genuine teacher attestations 0, full proofs independently certified 0, official syllabus atomic coverage denominator **NULL**, percentage **NULL**. Note 178 = project engineering mapping rows, not official curriculum atomic content. 28 elective editorial gap tickets all OPEN even after all 28 acquired project-adjacent drafts; linkage does NOT certify official clause coverage.

## K02–K06: hand-authored complete topic drafts

20 **original** strict-schema draft lessons: 15 required-track subskills linked to existing course IDs and 5 optional C/D/E project-authored candidate additions, 40 teacher-side worked examples, 20 misconception and counterexample sets, 3-stage hints, near/far transfer, assumption/domain and explicit scope limits. 7 theorem, 10 method, 3 concept; all source and provenance metadata remain `PROJECT_AUTHORED`, `ENGINEERING_INTERPRETATION`, `PENDING`. No copyrighted textbook content included.

| # | engineering course | type | original lesson | track |
|---:|---|---|---|---|
| 1 | HS-MATH-174 | method | 问卷调查可行性与无应答偏差的区分 | 选修C |
| 2 | HS-MATH-175 | method | 观察记录与文献记录的口径对齐和偏差比较 | 选修C |
| 3 | HS-MATH-176 | method | 数字图像最近邻采样与格点变换的混叠边界 | 选修D |
| 4 | HS-MATH-177 | method | 矩形场地布置的净空约束与面积验算 | 选修D |
| 5 | HS-MATH-178 | concept | 多面体曲面欧拉示性数与拓扑反例 | 选修E |
| 6 | HS-MATH-003 | concept | 充分条件与必要条件的量词与反向辨析 | 必修/选择性必修 |
| 7 | HS-MATH-010 | method | 方程平方后的增根与定义域回代 | 必修/选择性必修 |
| 8 | HS-MATH-013 | theorem | 二次函数在半轴上的单调性与对称反例 | 必修/选择性必修 |
| 9 | HS-MATH-017 | method | 分段函数接点连续性与左右导数检查 | 必修/选择性必修 |
| 10 | HS-MATH-027 | concept | 正切函数的定义域、符号与周期 | 必修/选择性必修 |
| 11 | HS-MATH-038 | method | SSA模糊情形的两组三角形分支 | 必修/选择性必修 |
| 12 | HS-MATH-042 | method | 复数相除的分母非零与共轭化简 | 必修/选择性必修 |
| 13 | HS-MATH-044 | theorem | 直线垂直平面的两相交方向判定 | 必修/选择性必修 |
| 14 | HS-MATH-053 | theorem | 概率加法公式与互斥的严格边界 | 必修/选择性必修 |
| 15 | HS-MATH-065 | theorem | 裂项相消求和的参数和端点条件 | 必修/选择性必修 |
| 16 | HS-MATH-068 | theorem | 导数符号与单调性的充分条件 | 必修/选择性必修 |
| 17 | HS-MATH-090 | method | 抛物线与斜直线交点判别式及竖线例外 | 必修/选择性必修 |
| 18 | HS-MATH-096 | theorem | 条件概率的非零分母与独立判定 | 必修/选择性必修 |
| 19 | HS-MATH-099 | theorem | 二项分布的独立伯努利和与矩 | 必修/选择性必修 |
| 20 | HS-MATH-102 | method | 相关系数不等于因果效应的统计边界 | 必修/选择性必修 |

New elective gap IDs associated only as *uncertified editorial adjacency*: **018, 019, 023, 024, 026**. Five curriculum candidate map items appended by deterministic `extend_elective_batch23.py` (old engineering inventory 173 → 178); **required-track engineering mapping unchanged**. New lessons 247 → **267**, all 267 remain `REVIEW_PENDING`.

## K00 + K01: auditable scope / schema / permission guards

Reconfirmed 427 review tasks = 61 page inspections + 315 numbered marker inspections + 23 unnumbered D/E heading inspections + 28 editorial tickets. These types mathematically overlap: 427 is **not** a distinct official-atom count. Track-specific verified denominator stays `null`. Added a fail-closed Batch23 reproducible authoring generator and integrator, backed by SHA256 provenance, exact 20 authored lessons, 5 source-bound gap IDs, a frozen historical 247-document baseline, full lesson schema checks, and 28 open tickets. No author-side signed approval or student solution exposure permitted. Live semantic coverage snapshot versioned separately; historical Batch02–Batch22 snapshots preserved.

## K07 exact arithmetic and explicit limitations

Added eight tightly typed, finite rational oracles for: squaring-and-root candidates including `x=-1` extraneous rejection; finite telescoping; rectangle clearance area; binomial point mass and endpoints; parabola/line discriminant with explicit vertical-line exception; nonzero complex division; probability union with Fréchet inequalities; and square-function monotonic pairs on one half-line. No arbitrary code/expressions are evaluated. `CONDITIONS_NOT_ESTABLISHED`, `UNSUPPORTED`, and `FAILED_FINITE_INSTANCE` are distinct, all results explicitly `student_step_verified=false`, `teacher_approved=false` and `complete_theorem_certified=false`.

The 7 new theorem drafts contain **22 unverified proof steps**, all in a new claim+reason SHA256 audit queue. Historical 497 + 22 = **519 unverified steps**. Historical 127 P0 risk steps and 10 unresolved conflict pairs remain OPEN; new risk tags are human-review priorities, not proofs.

## K08/09 retrieval / testing and regression outcome

- New dedicated test module contains **1,042** tests (including many SymPy/precision/rational boundary and negative permission checks). First run: **1,041 pass, 1 fail** due incorrect test report key, repaired (other snapshot key similarly repaired).
- Initial full backend: **22,228 passed / 40 failed**, driven by live 173→178 and 247→267 count assertions, old frozen-review scripts accidentally reading the expanded live lesson corpus, and a temporary deterministic builder that did not copy the new candidate JSON. Fixed by explicit frozen-scope exclusions, separate live Batch23 audit, updating active inventory assertions, and copying the new source into isolated reproducibility tests. Historical result files were not rewritten.
- Subsequent backend: **22,262 pass / 6 fail**, then narrowed to 1 old test assertion about elective with-draft count; fixed.
- **Final Mac Python backend full test: 22,268 passed, 0 failed**, one third-party anyio/Starlette deprecation warning. Log: `evaluations/results/2026-11-08-kb-batch23/backend-final.log`.
- **37/37** Python-script CI provenance/scope/audit gates pass (`ci-gates-final.log`); they include the two new Batch23 `--check` steps.
- **111/111** Node unit tests pass (`node-final.log`). All current JS module syntax checks pass.
- Synthetic local tutor policy **33/33** and retrieval hard-negatives **40/40** pass. Both remain blocked from release of unapproved teacher solutions.
- **Browser final status: PASS.** Mac Chrome completed 16 named browser scripts (all PASS) plus two `pytest` browser-review checks (2 passed), zero page errors, zero external requests and `BROWSER_REVIEW_EXIT=0`; see `evaluations/results/2026-11-08-kb-batch23/browser-final.log`. This is browser/pointer emulation, **not** a physical iPad test. Test traffic used loopback FastAPI and a synthetic temporary DB.

## Run logs / transparency

`evaluations/results/2026-11-08-kb-batch23/` stores initial failed run logs, focused review logs, final backend/node/CI logs, policy/retrieval, and browser evidence. No genuine student data or external LLM calls were used.

## Next batch high-value dependencies

1. **K00:** independent original-source clause split and overlap deduplication; verify compulsory, selective compulsory and elective A–E per-clause denominators, maintaining NULL for unreviewed.
2. **K07:** human mathematical review of 127 historical P0, Batch21/22 high risks and new 22, adjudication of 10 historical conflicts; independent checks and actual teacher signoff before any APPROVED status.
3. **K02–K06:** deepen the required-track topic atom inventory beyond the 178 engineering coarse rows; add 20–30 specific lessons each batch with formal conditions, examples, near/far transfer and negative tests.
4. **K08/K09:** gate student RAG/API against independently attested approved atoms, teacher-only answer leak tests, unseen tasks and teacher audit; no source-laundering claims.

**No GitHub issue should be closed; PR should remain Draft.** The test-success state is a software integration checkpoint, NOT full syllabus / formal proof / teacher review completion.
