# STEM Mentor｜Batch35 实际执行报告（2026-11-08）

## 唯一环境与基线
仅授权 MacBook Air：`~/Documents/文件/stem-mentor-kb-batch35`，独立分支 `feat/kb-batch35-complete-elective-review`；基于 Batch34 Draft PR #59（本地父提交 `e2ef05825cf65251441f19ac53f7d40ee29920a8`，Git Tree `e8ae43dcd04750c0277d3705a42a72713599660c`）。未在 Tang 开发，未修改原主仓 main 的未提交文件，没有强推或合并 main。开始前重新读取 GitHub 总 Issue #17 及 #18–#27 和 Draft PR #58/#59。

## K00 / K01 / K05 / K06：将最后 29 项选修无关联编辑候选转为真实审核稿
Batch33 对官方课标 61 页做过首次内容检查，并提出 **313 项项目自编页级编辑目标**（必修 125、选择性必修 92、选修 A–E 合计 96）；**这不是官方课标的完整知识原子分母**。Batch33 发现选修目标中 47 项仅有既存讲义的待证关联，另 49 项完全无对应讲义线索。Batch34 已为其 20 项新增审核稿，本批为 **剩余 29 项**独立写稿（A7、B11、C5、D6；E 的剩余无关联候选为 0）。

新增 `knowledge/editorial_review/kb_batch35_seed.jsonl` 的 29 篇原创、逐项唯一 ID 的教师审核稿，每篇包含数学命题或定义、记号和完整声称适用前提、3 条分步推导及理由、具体反例及失效边界、典型错误与追问、**2 道教师侧完整例题**、三级非剧透提示、近/远迁移，合计 58 道教师例题、29 个反例、87 层提示、58 个迁移练习。相关主题包含定积分有向面积、概率密度与协方差、最大似然、矩阵秩、极限、统计检验、线性回归与因果、离散增长、周期模型、贷款、投入产出、采样混叠、声学谐波与聚类边界等。

`scripts/author_kb_batch35_lessons.py` 为稳定原创稿生成器，`backend/app/kb_batch35_review.py` 定义严格 Pydantic 审核门禁，`scripts/build_kb_batch35_editorial_review.py` 生成可复现的 `docs/evaluation/KB_BATCH35_EDITORIAL_COVERAGE_AUDIT.json` 和 `docs/evaluation/KB_BATCH35_REMAINING_29_ELECTIVE_MANUSCRIPTS.md`。全部保持 `REVIEW_PENDING` / `TEACHER_ONLY` / `NOT_FORMALLY_CERTIFIED`，无虚假审核签名，无学生端权威检索或完整教师答案的发布。

**本批审稿进度**：29/29 新稿结构可审计；与 Batch34 合计，过去 **49/49 个无讲义线索的项目编辑候选**现在都有教师侧审核稿。但 47 条历史旧稿关联仍待独立核准；“已有审核稿”不表示满足官方课标或真正获得教师批准。此前 287 篇深度草案未修改，因此不能把它们与 49 篇新审核稿相加后宣称已获正式批准的课程。

## K07：58 项有界数学实例与 12 种严格前提门禁
`backend/app/kb_batch35_exact_witness.py` 对 29 个主题各运行 2 个指定数学实例，共 **58 项**。使用 Python Fraction 或 SymPy 对选定数值/矩阵/积分/极限进行有界精确检验。新增 **12 类**有严格字段、类型、数值界和失效拒绝的门禁：fraction、normal_variance、time_growth、loan、sampling、regression、geometry、study、density、harmonics、io、angle。各有合法/失效对照，并增加缺参、多参、布尔伪装、巨大整数、无关 operator 的负例。

独立审查时还加固了两组此前形式上通过、但验证含义偏弱的实例：其一使用真正的二维反射/半周旋转矩阵验证固定点与非固定点；其二从原始样本重新计算含异常值数据的均值与中位数，而非把相同表达式和自身作恒等比较。

**数学检验的边界**：只证明这些规定输入的算术结果，不能据此认证一般定理、模型适用性、因果或历史断言，更不能给学生自由书写证明标记 `VERIFIED`。历史 **538 条**证明步骤仍未形式认证，**10 组**冲突未裁决；教师正式批准 **0**，学生深度内容正式发布 **0**。必修、选择性必修、选修 A–E **7 个官方知识原子分母/覆盖率继续为 null**。

## K09：Mac 真实回归、错误修复与独立验证
- 新专项：`backend/tests/test_kb_batch35_review.py`，**287 passed，0 failed**；涵盖 29 篇内容条件、身份/归属/许可、教师隔离、58 个有限验证、12 种前提门禁及大量伪审核、孤儿 ID、重复、篡改等负面用例。
- 初次强化有限算术后，新生成审核 JSON 未同步，专项产生 **286 passed、1 failed**（可复现产物漂移，不是数学断言错误）。随后重新生成审核 JSON，复跑得到 **287 passed**；另外删除 4 个源码尾部冗余空行，`git diff --check` 通过，最后再次跑专项 **287 passed**。
- 完整 `bash scripts/mac_check.sh`：Python **37,427 passed、0 failed、1 个第三方依赖 warning**；Node **111/111 passed**；教学策略 **33/33**；检索困难负例 **40/40**、Top3 **22/22**；EXIT=0。原始日志 `evaluations/results/2026-11-08-kb-batch35/mac-check.log`（保留 `mac-check-pre-hardening.log` 作为源算例增强前的对照）。
- Chrome/Playwright `bash scripts/mac_browser_check.sh`：**15 个浏览器脚本通过**、浏览器 pytest **2 passed**，EXIT=0。使用临时合成数据库，未请求外部 API；iPad pointer 只是仿真而非真实硬件测试，详见 `evaluations/results/2026-11-08-kb-batch35/browser.log`。
- CI 及 Mac 都已新增 `scripts/build_kb_batch35_editorial_review.py --check` 的重生成漂移门禁，版本化日志作为实际运行证据。

## GitHub 事实源与后续任务
Mac 源码已测提交 `adab05952808999806533690f1e6fdb3f490327f`，Git Tree `537f252d5c7618b0165d07b825f061292f3d6d3a`。对应 Draft PR #60：https://github.com/YOUessi/stem-mentor/pull/60，base 为 Batch34 Draft PR #59 的 feature branch。日志/本报告使用独立 docs commit 归档；GitHub 远端最终 HEAD/CI 应独立读取后才判定成功。无 main 合并、强推和伪教师审批。

**下一批**首先继续 K00：逐句对照原版官方课标，补完 61 页中编号及未编号要求的真正逐条归属、特别检查原第35页图形乱码，建立可核准的七轨道原子分母；对 47 条旧稿链接逐项判断准确、缺失或冲突。然后 K07 对 538 条证明步骤分级独立审查与 10 组冲突裁决，K02–K06 按全章节补齐原创深度讲义与题族，K08/K09 对新审核稿强化检索拒答、防剧透、未见题测试；真实教师审批前全部保持待审，不能宣布课程发布或任务完成。

## 堆叠 PR 远端基线核验与无内容改动的冲突修复
本批发现：Mac 端父提交 `e2ef05825cf65251441f19ac53f7d40ee29920a8` 与 GitHub 上的 Batch34 父提交 `8590e4eecb7bc6887b9d41d1415cb90a385898db` **commit SHA 不同，但 Git Tree SHA 完全相同**：`e8ae43dcd04750c0277d3705a42a72713599660c`。最初创建的 Draft PR #60 因这两条并行提交历史导致 `mergeable=false`（`.github/workflows/ci.yml` 和 `scripts/mac_check.sh` 发生虚假文本冲突），尽管实际代码文件内容一致。

核对 `git diff origin/feat/kb-batch34-review-candidate-lessons HEAD~2` 为空并核实两者父 Git Tree 完全相同后，仅在独立 Batch35 **feature 分支**追加了普通双父 merge commit `964a200c12d8812bf2f01bc13b776b52aa71f474`，将真正远端 Batch34 父提交并入已有 Batch35 分支（`git merge --no-ff -s ours origin/feat/kb-batch34-review-candidate-lessons`）。此操作保留原所有提交、不使用强推、不改主仓，且合并前后的 Batch35 源码 Git Tree **完全不变**：`ae7d4f9bb7a1a5d6d9e516ba63183959ff5d1efc`。GitHub 回读 PR #60 显示 `mergeable=true`、Draft=true、只含本批 14 个变更文件。此合并只是在两份**内容一致的来源树**之间补齐 Git 历史，不是将任何数学草案批准或发布。

GitHub Actions 在恢复正常 PR 祖先关系后触发运行 `42464313289`；最终远端 CI 状态按独立查询结果报告，不以本地绿色测试冒充远端成功。
