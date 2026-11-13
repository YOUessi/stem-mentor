# STEM Mentor · Batch117（2026-11-13）Mac 原创数学内容与全源范围审计

## 事实源、权限及隔离

- 仅在已授权 **MacBook Air** 的独立工作树 `~/Documents/文件/stem-mentor-kb-batch117` 开发和测试，工作分支 `feat/kb-batch117-syllabus-atom-review`，起点为已核实的 Batch116 远端 HEAD `a108eeb531811a415ae1fe31e8f69fa4cd1c9d30`。**未在 Tang 上创建、编辑或测试知识库**。
- 源课标为《普通高中数学课程标准（2017年版2020年修订）》本地授权原件，SHA256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。源PDF及原文不提交；只提交来源指纹、索引及完全自创讲义。
- Mac 主仓与其他 worktree 均不覆盖、不强推、不合并 main。测试自动产生的 `evaluations/results/2026-10-15-policy-and-retrieval.json` 及 `...v05-retrieval.json` 两份历史快照是本地未暂存差异，不纳入本批提交。
- 批次每个新增内容为 `REVIEW_PENDING / TEACHER_ONLY`；没有真实教师签字，也没有按学生权威事实发布或认证自由作答步骤。

## K00 / K01：从61页局部范围延伸到188页的**诚实范围导航**

- 复核已保存的188物理PDF页原始SHA锁定台账，新增 `scripts/build_kb_batch117_scope_segments.py` 与 `docs/evaluation/KB_BATCH117_WHOLE_PDF_SCOPE.json/.md`，将**188个物理PDF页**连贯索引成6个**编辑性章节线索**：前言与课程框架0–19（20页）、既有课程内容范围20–80（61页）、学业质量81–86（6页）、实施建议87–106（20页）、附录核心素养107–113（7页）、附录教学评价实例114–187（74页）。这些章界用Mac PDFKit查看原件标题核对；**不意味着尾部附录可以自动排除出数学教学素材，更不是188条课程原子**。
- `curriculum/highschool_math/k00_batch117_source_triage.json` 对旧61页逐页锁定PDFKit文本指纹与非空行数，18页保留之前结构审计状态，**另43页新增机器行数/指纹索引但未声称人工结构审校完成**。
- 第35印刷页公式/控制字符抽取失真，第51/69/73页跨轨，第21/22/58/59页数学公式图像风险均显式进入审校队列。选修E从印刷73页**中段**开始，不能整页归轨。
- 七轨必修、选择性必修和选修A–E的**正式课程知识原子分母全部 UNKNOWN**；逐页教师正式原子化0，正式教师批准0。不能把61页/188页、498份工程讲义或8条候审来源链接当作官方分母。

## K04 / K06：8份完整原创组合计数与概率候审讲义

新增 `knowledge/deep/v1/batch117_selective_counting.json`、`scripts/kb_batch117_lessons.py` 与同版教师阅读稿 `KB_BATCH117_LESSONS.md`，全部针对选择性必修来源印刷第46、47页，附版本、工程课程ID、来源行范围、适用条件、符号、先修、反例、常见错法、3级提示、近远迁移、两道完整教师例题与教师隔离状态。

| 类别 | 新增原创内容 | 主要边界 |
|---|---|---|
| 方法 | 分类加法计数；分步乘法计数 | 分类不重不漏；后续分支数依赖前序选择时不能硬乘 |
| 定理 | 排列数；组合数；二项式定理；全概率公式；超几何分布 | 有序/无序；零长度选择；乘法可交换性；完备互斥分支、非零分母；有限总体无放回和支持范围 |
| 概念 | 条件概率及独立性 | P(B)>0；条件方向；正概率互斥不独立 |

交付规模：8份深度稿、16道教师例题、24级提示、16项近/远迁移、8组反例、15条**未认证**定理证明步骤。历史工程深度草案490份，本批后498份，均不是正式教师认证课程原子。

## K07 / K08 / K09：独立数学检查、历史快照防漂移、教学端安全

- 本批脚本保存8种内容风险的正反有限精确见证共16例；新增与教师解答分离的独立验证 `tests/test_kb_batch117_example_oracles.py` 对**全部16道例题答案**逐一做SymPy/Fraction/精确枚举检查，并对8类错误泛化提供负面边界实例。有限见证不等同一般定理的形式证明。
- 结构和学生权限专项 `tests/test_kb_batch117.py` 检查知识类型、来源、审核字段、防伪教师批准、先修依赖无环、分级提示不含完整答案、公开层不包含候审教师解答；`tests/test_kb_batch117_scope_segments.py` 检查188个物理页无重复漏页、六段章界及七轨分母仍未知。
- 修复真实历史审计问题：Batch115冻结分母原先受到后续新增知识包影响，导致第一次全量检查在 `KB_BATCH115_AUDIT.json` 处失败。现按编号仅统计对应批次以前的历史知识包；Batch117同样预先采用历史快照冻结，并增加未来Batch118/120不改变Batch117分母的回归测试。
- 更新 `.github/workflows/ci.yml` 与 `scripts/mac_check.sh`，把新内容构建、整份PDF结构门禁、237项专项回归纳入Mac/CI。所有新稿仍不得作为学生权威检索知识；教师参考解答保持教师侧。

## Mac原始验收日志

- 首次完整检查：**exit 1**；历史Batch115冻结审计因后续知识扩展漂移，已根因定位并修复，失败日志完整留存。
- 修复后的首轮完整 `mac_check.sh`：**exit 0，Python 66,285 passed / 5 skipped / 1 warning；Node 111/111**，包括原Batch117专项201通过。Chrome/Playwright单独完整包装器 **exit 0**，浏览器pytest 2通过。
- 扩展后专项测试：`237 passed`，包含新增加的全部16个教师例题独立数值检查、8个条件负例、188页结构完整性检查及未来批次防漂移回归。
- 包含**最终所有脚本与新增测试**的第二轮Mac全量验证：见下方最终交付附记（必须有真实外层Shell退出码与日志才能声明）。
- 所有日志按其真实成功/失败状态保存，数学前提有限见证不能冒充通用定理证明，浏览器模拟不代表真实Apple Pencil硬件测试。

## 下一轮必须继续的工作

1. 以官方章/节为主，不再按页数冒充知识原子，重点处理旧61页中43页结构审校、PDF印刷第35页公式图像、跨轨第51/69/73页，并从课标全文核实章节及选修E的计数边界。
2. 开始建立真正的七轨**原子化逐章分母**与已覆盖/缺失矩阵；对每条概念、定理、方法保留条件、来源、数学证明和真实审核状态，不能推断为0或用工程草案数替换。
3. 分批审查历史172条先修关系、538条未认证证明步骤与10项数学冲突；优先对P0证明和条件失效例补独立验证。
4. 完成选择性必修概率统计其余离散型分布、二项分布期望/方差、正态分布与回归及各选修轨完整内容，继续以学生隔离、迁移题族、CI门禁验证。
5. 正式教师批准和学生端权威发布仍为0；未全部达标前不将PR设为Ready、不合并main、不关闭#17–#27。

## 独立复验、GitHub源码身份及审计备注（交付前复核）

- 本批最终代码提交（还不含本执行报告和日志）：`28fd4a57399dc194e90ef6d6a3181ec4afd9877d`，18个代码、生成数据、课程草稿及负面回归文件。Mac原生git push成功，非强推，远端已核验相同HEAD。
- 对应独立 [GitHub Draft PR #142](https://github.com/YOUessi/stem-mentor/pull/142)，基于Batch116 `a108eeb531811a415ae1fe31e8f69fa4cd1c9d30`。首次远端核验：范围生成器 Git Blob `beba3792e4360e382891b4f5608f7a78f029bb45`、本批原创教学稿 JSON Blob `fcf8fb804962144cf5b16791ced4ec9c6a7de8eb`，均与 Mac `git hash-object` 完全一致。
- 修复后的第二次完整Mac回归（已独立得到外层Shell退出码0）：Python **66,285 passed / 5 skipped / 1 warning**，Node **111/111**。其后对提交中全部新增测试/生成器再执行237个专项，**237 passed / 0 failed**。考虑到第二次长测试运行期间最后加入了防未来漂移负例和Markdown末尾稳定性修补，另开第三次**冻结最终源码全量回归**以排除时间交错误差；最终退出码单独存档，未完成不得称最终通过。
- 第一轮失败是冻结的Batch115历史审计将未来知识包算入其2026-11-13之前分母；在构建器中基于批次编号排除未来包，而不是重写冻结审计结果。原失败保存，新增未来Batch118/120回归防止重犯。
- 11个Issue #17–#27的本批更新评论均实际通过GitHub API写入；保持Open，所有未审校及未认证项目仍列为待办。
- 已完成Chrome/Playwright完整回归（退出码0），浏览器pytest2/2；这是软件/模拟设备的验证，不是独立真实学生实验、实机iPad验收或数学专家认证。


## 最终冻结源码验收与第35页图像追溯（2026-11-13）
- 第三次冻结源码 Mac 全量执行完成：外层Shell **exit 0**；Python **66,285 passed / 5 skipped / 1第三方警告**；Node **111/111**。独立Chrome/Playwright退出码0，浏览器pytest 2通过。专项237通过。
- 早期完整回归 **exit 1** 的生成快照漂移日志未删；本轮修复后多次完整运行均成功，不将原始失败改写为通过。
- 额外实际检视课标原图第35印刷页，确认PDFKit乱码源于一张带“检验不合格→重建模型”回边的建模流程图；只解除内容类型的歧义，**未**将该页升级为教师正式原子审校。详情见 KB_BATCH117_PAGE35_VISUAL_ATTESTATION.md。
- GitHub正式交付前原始日志SHA-256：

  - KB_BATCH117_MAC_CHECK_FIRST_FAILURE.log：5a3566d94fbeed0597af6a761fbb68562a00d7393de6e4a1a8737e2c25317fe4
  - KB_BATCH117_MAC_CHECK_FIRST_EXIT.txt：4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865
  - KB_BATCH117_MAC_CHECK_VERIFIED_FINAL.log：3a7db97522fd4ae1fe9918c3fbc0c980dc5f3e918c1a53a479fe6ce34cf4756e
  - KB_BATCH117_MAC_CHECK_VERIFIED_EXIT.txt：9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa
  - KB_BATCH117_MAC_CHECK_RELEASE_FINAL.log：c220c79268c9525c40553b6418cb0eca96dbfef1c8624b67983965e23831fbfd
  - KB_BATCH117_MAC_CHECK_RELEASE_EXIT.txt：9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa
  - KB_BATCH117_BROWSER_FINAL.log：911ab485c9ffa142d7494a9e0d476d6c6446306ddd0b0a7bb821f86f1625a8d1
  - KB_BATCH117_BROWSER_EXIT.txt：9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa
  - KB_BATCH117_FOCUSED_EXPANDED_FINAL.log：565279c125d1dc17e67b9c6ff45625bb05c69f45a2c4da33dc4eb93f18ed5978
  - KB_BATCH117_FOCUSED_FINAL.log：5f929367a937555737f0d804a9d08b170074eb0bda19fa741528d2c1568f7d91
  - KB_BATCH117_FOCUSED_FIRST.log：0c1dd3c5fa9b177c031c25fc3d90d22a938d833b37df1f37f05f7744419d6b6b
  - KB_BATCH117_EXAMPLE_ORACLES.log：2abafb29e0244d61bca8212b003812e32e9301f743dba4aeedd20a803386527c
