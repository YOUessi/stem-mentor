# STEM Mentor Batch69｜完整开发、数学边界与Mac回归证据（2026-11-10）

> **仅限教师审核的Draft交付。** 本轮在唯一授权MacBook Air的独立worktree开发并测试；未使用Tang、未碰主仓11项未提交修改、未合并main。GitHub以 [Draft PR #94](https://github.com/YOUessi/stem-mentor/pull/94) 为事实源。

## 1. 基线与源码

- 上游：Batch68 Draft PR #93，GitHub commit `0c403e7c8dcac05714a445096234427cf06d4f5e`，Tree `0fa81a264d1a98f8b04956dc3f32f8fbaeee3d77`。
- Mac独立开发源码commit：`733b98fbdcec24490ff502cfb44b405fdcc2e6fc`；完整源码Tree：`69c39bbdb9650fa1b06990eb80a5cede88965841`。
- Mac git push因 `Recv failure: Operation timed out` 失败后，在GitHub原生接口建立Draft分支并逐文件上传Git Blob，**逐个校对8个Blob SHA及Tree与Mac完全一致**；远端源码commit：`b3fe88ae20536291efb85eb20da8c57fa46f4c9d`。两个commit的历史元数据不同，但Tree相同。最终报告与日志追加为后续commit。
- 仅使用项目已存在的Mac虚拟环境和本地原版课程标准PDFKit指纹；未上传PDF或课标全文、真实学生数据及第三方教材内容。

## 2. 具体新增成果

### K00/K01：62项内部暂定候选与教师稿追溯

- 对 `curriculum/highschool_math/k00_batch63_provisional_atom_proposals.json` 中62条暂定拆分建立行级来源索引 `KB_BATCH69_ALL62_CANDIDATE_LINEAGE.json`。
- **31条第一候选关联Batch64/65已有的父级范围稿**，标签 `PARENT_SCOPE_DRAFT_NOT_ATOM_CERTIFIED`：并不将父级草案误记为完整官方知识原子。
- **31条第二候选有教师侧独立草案引用**：前批Batch68有20篇，本批Batch69补11篇；`SECOND_CANDIDATE_LESSON_PENDING`。
- 所有数据通过源锚点页码、行级及窗口SHA回溯本地课标，增量11个来源位置Mac现场复验。62/62仅表示内部候选有稿件引用，**不能作为正式课标覆盖分母**。
- 官方七轨（必修、选择性必修、选修A/B/C/D/E）知识原子分母仍全部 `null`，0/61页完成教师全面原子化审查，14项能力/教学要求仍未映射、选修E校本范围不能机械计零。

### K02–K06：11篇全新原创教师侧数学草案

1. 相对全集的补集运算及越域失败案例；
2. 对数换底的所有底数、真数与除零边界；
3. 三角恒等式除以余弦与平方根的象限符号；
4. 周期函数回归参数、时间单位与模型外推；
5. 数学建模残差、插值和外推的逻辑区分；
6. 纯虚数非零边界与零复数术语约定；
7. 复数除法的分母非零与共轭合法变形；
8. 三维空间异面直线与共面/平行区别；
9. 二维投影相交并不推出三维直线相交；
10. 直线垂直于平面内两相交直线的必要前提；
11. 简单随机抽样中子集等可能与抽样框覆盖偏差。

每份给出数学陈述、适用前提、符号、先修关联、3条待审分步论证、2道原创例题含教师侧解答、失效例、典型错误和错因、三级提示、近远迁移各1项。合计 **11篇/22题/33条说明/11组反例错因/33条提示/22项近远迁移**。所有状态 `REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED`，没有伪造教师签核、正式数学证明或学生发布权限。

### K07/K08：数学验证与Agent拒绝

- 新增11个独立整数/`Fraction`/受控SymPy有限数学见证，覆盖对数换底、正弦/余弦、共轭复数除法、外推非唯一、线面方向、空间投影等；均仅为 `FINITE_EXACT_INSTANCE_ONLY`，不能把有限实例等同于一般证明。
- 增量测试包含所有62条未认证原子状态、11条来源SHA伪造拒绝、11条教师批准伪造拒绝、11条原子批准伪造拒绝、空字段/重复/错误范围负例、以及11条**非空批准索引**的学生RAG防剧透检查。未经教师审核的知识与答案均未进入批准检索结果。
- 遗留538条历史未形式认证步骤和10组未裁决数学冲突均保持待审；未调用真实模型API，不宣称在线生产评测或自由文本证明认证。

## 3. 实际测试及失败修复

| 检查 | 最终Mac结果 | 证据 |
|---|---:|---|
| 本批pytest专项 | **134 passed，0 failed** | 冻结内容后独立重测，约16秒 |
| 完整Python pytest | **46,889 passed，0 failed，1条第三方弃用警告** | `evaluations/results/2026-11-10-kb-batch69/mac_check.log` |
| Node | **111/111 passed** | 同上 |
| Tutor策略 | **33/33 passed** | 同上 |
| RAG困难负例/Top3 | **40/40及22/22 passed** | 同上 |
| Chrome/Playwright | **15个测试脚本通过**；浏览器pytest **2 passed** | `evaluations/results/2026-11-10-kb-batch69/mac_browser_check.log` |
| Mac完整脚本 | **exit 0** | `mac_check.exit` |
| Mac浏览器脚本 | **exit 0** | `mac_browser_check.exit` |
| 原版课标源SHA校验 | **本批11个来源锚点通过** | `build_kb_batch69_remaining.py --check --verify-local` |
| GitHub Actions | **另行核实最终提交运行结果** | Draft PR #94 |

首轮内容生成遭遇 `Insufficient explanatory depth`：发现两条过短的符号/提示字段并补全。首轮来源链检验由于误把窗口SHA与行级SHA直接相等而被拒绝；已改为分别核验相应SHA。增量首次测试 **133 passed / 1 failed**，失败是纯虚数例题解答不够具体，实际扩写后 **134 passed**。最终完整Mac和浏览器回归均在内容冻结后执行。以上失败未掩盖，也未通过降低验证强度绕过。

### 版本化文件

- `scripts/build_kb_batch69_remaining.py`：生成、来源审计、数学有界验证及拒绝伪造门禁。
- `knowledge/editorial_review/kb_batch69_remaining_authoring.tsv`：原创新增作者手稿。
- `knowledge/editorial_review/kb_batch69_remaining_lessons.json`：机器可审查候选稿。
- `docs/evaluation/KB_BATCH69_ALL62_CANDIDATE_LINEAGE.json`：62条内部候选全覆盖对照与审核空缺。
- `docs/evaluation/KB_BATCH69_TEACHER_REVIEW.md`：教师侧逐篇内容。
- `backend/tests/test_kb_batch69_remaining.py`：正向、失败分支、RAG检索隔离回归。
- `.github/workflows/ci.yml` 及 `scripts/mac_check.sh`：加入可重放快照与本地来源检查。
- `evaluations/results/2026-11-10-kb-batch69/`：原始Mac脚本输出、退出码和来源工作树基线。

## 4. 仍不满足的最终发布验收与下一批计划

**不可关闭主Issue #17和K00–K09**：正式七轨课程分母未建立，全页课标逐条教师审查0/61，14项教学/学业目标没有完整独立验收链接，538旧数学证明步骤未认证、10组冲突未裁决，教师批准0、学生正式深度发布0。

下一批须优先将61页完整课标按数学对象、量词、适用范围拆为独立条款，处理跨页数学等价去重并形成按课程轨道可审计的真实分母；逐项落地14项未映射教学/学业要求及第35页建模图示视觉核对。随后依据**确认缺失的真实数学原子**继续成批生成跨轨完整讲义、题族、证明与不适用例，并进行真实教师签核及独立模型API对照；不得把本批62条内部候选链接或现有工程目录误报为官方全量完成。
