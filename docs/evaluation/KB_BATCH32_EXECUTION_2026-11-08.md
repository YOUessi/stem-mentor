# STEM Mentor｜Batch32 Mac 实际开发与验收（2026-11-08）

开发环境严格限于授权 MacBook Air：独立工作树 ~/Documents/文件/stem-mentor-kb-batch32；分支 feat/kb-batch32-core-selective-atom-audit，基于 GitHub Batch31 PR #56 HEAD 8582af29e3f6f468dcf60576ffaf82b933eaff8e。原始 Mac 主仓已有未提交修改全部保护，未在 Tang 开发，没有合并 main，也没有提交受版权保护的课标 PDF、学生数据或模型密钥。

## K00：原版课标逐页初查与编辑原子

- 在 Mac 核对教育部 2017 年版/2020 年修订官方数学课标 PDF（188 页），SHA256 为 cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195。
- 使用 macOS PDFKit 独立读取、通过 CryptoKit SHA256 记录印刷页 29–50 共 **22 页**页面提取文本的逐页摘要；源页 SHA、原版 PDF SHA、原来 61 页 pypdf 账本 SHA 与原创编辑候选 TSV SHA 被构建器固定。
- 联合 Batch31 已检查的 15 页，61 页课程审计范围中现有 **37 页经过至少文本/图像内容检查，24 页没有内容检查**。这不是教师认证或完整编号/未编号要求核准。印刷页 35 的 PDFKit 文本包含控制字符乱码和不可读图形，明确留待独立视觉检查，不伪造这个图的学习目标；第 36、37、49 页虽已读但未产生单技能提案。
- 新增 **130 项原创、逐页绑定的单技能编辑学习目标候选**，其中必修 **38 项**、选择性必修 **92 项**。联合 Batch31 已有 87 项，累计 217 项编辑提案（必修 125、选必 92）。覆盖概率统计、数据抽样/统计建模、空间几何判定、数列、导数、空间向量、解析几何、组合概率与回归统计。
- 所有条目为 PENDING，官方原子 ID=null，教师审核=0，学生发布=false。全部必修/选择性必修/选修 A–E 的**正式官方课程原子分母及覆盖率仍 null**。317 个编号位置、217 个自编候选、287 篇历史讲义均不能冒充官方完整分母。
- 文件：curriculum/highschool_math/k00_batch32_compulsory_selective_editorial.tsv、scripts/build_kb_batch32_source_atoms.py、docs/evaluation/KB_BATCH32_K00_CORE_SELECTIVE_ATOM_AUDIT.json。新负例拒绝篡改来源、课程 track、页码、候选重复、选学星号错配、审核伪签名或非授权发布；星号审查粒度为四个**具体学习目标**，非简单页面白名单。

## K07：六类有边界的有限精确验证

- 新增六种 Python Fraction / 整数组合数有限实例：等差数列有限和、有限等可能条件概率、超几何不放回抽样、点到直线距离的精确平方、组合数与帕斯卡关系、非退化一元线性最小二乘。
- 六个候选课程条目各关联一个合法实例及一个非法前提拒绝；完整手写推导、适用条件和反例见 docs/evaluation/KB_BATCH32_MATH_CONDITIONS_AND_DERIVATIONS.md。
- 验证器 backend/app/kb_batch32_selective_finite_math.py，审核链接 knowledge/proof/kb_batch32_selective_finite_fixture_links.json；生成脚本 scripts/build_kb_batch32_math_links.py 及报告 docs/evaluation/KB_BATCH32_MATH_FINITE_LINK_AUDIT.json。所有结果仅为 VERIFIED_FINITE_INSTANCE 或 CONDITIONS_NOT_ESTABLISHED；whole_theorem_certified=false、student_freeform_step_verified=false、teacher_approved=false、official_curriculum_atom_verified=false。未将编辑候选放入学生 Agent 的权威课程索引。

## K01/K09：真实 Mac 测试和已修复失败

- 新增专项 backend/tests/test_kb_batch32_curriculum_math.py 的 **2,120 项**。首次结果 **2,119 passed / 1 failed**：发现星号选学规则仅按来源页判定，错误内容有机会冒充选学。已收紧为逐项目的精确星号白名单，再跑 **2,120 passed / 0 failed**。首轮及最终结果分别留档于 evaluations/results/2026-11-08-kb-batch32/targeted-first-failure.log 和 targeted-final.log。
- Mac 真实运行 bash scripts/mac_check.sh，包含新增两个生成 --check、历史全部审计门禁、全量 Python 后端及教学策略/检索回归、Node 测试：**Python 35,672 passed / 0 failed / 1 条第三方弃用 warning；Node 111/111 passed；策略与检索均通过**，退出码 0。原始日志：evaluations/results/2026-11-08-kb-batch32/mac-check.log。回归期间临时更新的旧历史结果文件仅在本批独立工作树恢复，没有触碰主仓。
- Mac Chrome + Playwright 浏览器完整脚本回归 **15 项通过、0 失败**；浏览器 pytest **2 passed**，测试脚本最终退出码 **0**，原始日志是 evaluations/results/2026-11-08-kb-batch32/browser.log。使用临时合成数据库，无外部请求；iPad 触控与笔压为 Chrome 仿真，**不是物理设备验收**，也不代表真实学习增益。

## GitHub 源码验收与下一批

经过 Mac 完整 Python/Node 测试的源码提交：476c79e9866092c4ba65d3b072ba2d9e041e346b，Git tree 5b8c6f46e29f64e9ea6c92aee3cc66777be48665。Mac 直接 git push 已成功；新建并保持 **Draft PR #57**：https://github.com/YOUessi/stem-mentor/pull/57，base 是 Batch31 feature branch，未合并 main。后续若追加本报告与浏览器日志，须单独核查最终提交 SHA、树与远端 CI，不能将历史成功认作新提交验证。

仍未达到的真实门槛：本批新增**完整教学讲义 0 篇**；已有 **287 篇**仍全部待真实教师审核，**538 条**自然语言证明步骤尚未形式认证（其中 127 条高风险 P0 有编辑审查稿而非形式证明），**10 组历史冲突**尚未裁决；教师正式批准 **0**，学生端深度讲义发布 **0**。官方课标完整知识原子分母和全部轨道覆盖率仍未知。

**下一批：**继续独立核对课标剩余 24 页，特别是选修 A–E 印刷 p51–73；重审 p35 图形乱码；建立逐条编号及未编号要求的精确页内锚点及可审计分母；将 217 个原创编辑目标与 287 篇草案做逐条缺口映射，然后成批写深度原创讲义、题族与迁移；推进 538 步证明独立认证、10 个冲突裁决，获取真实教师审核后才允许发布。#17–27 不关闭，PR 维持 Draft。
