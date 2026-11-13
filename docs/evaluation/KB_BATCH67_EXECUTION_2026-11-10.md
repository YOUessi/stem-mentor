# STEM Mentor｜Batch67 源码、数学审查与 Mac 验收记录（2026-11-10）

## 事实源和环境

- 唯一开发/内容构建/测试设备：授权的 **YOUTangdeMacBook-Air.local**；独立 worktree `~/Documents/文件/stem-mentor-kb-batch67`，分支 `feat/kb-batch67-cross-page-curricular-review`。
- GitHub Batch66 基线：`a59faee4ab0ec3cfba2165af72ab68fd50795237`；本批源码提交 **`554041a0223e9cdab4386eba971024567d300333`**；源码 tree **`2a53187ef561eef609bd3dfc6928565a6d762358`**。
- 主仓 main 原有 11 项未提交修改均不碰；Tang 未使用；未合并/重写 main、未提交版权课标原文或真实学生数据。
- PDFKit 原始课标提取结果仅在 Mac `/private/tmp` 进行 SHA 重验，GitHub 提交的只是原创说明、坐标及来源哈希。Mac 本地源图示无法由文本哈希替代视觉审核。

## K00+K01：本批源审查成果

1. **6组跨页词形相似候选**：对照 Mac 保留的课标来源行、PDFKit 页指纹、窗口SHA，分别记录数学对象/前提、两侧候选、原创正例及典型错误。涉及一般函数与对数、一般单调性与对数底数、基本不等式与三角恒等式的适用域、方程除式与二次不等式等。不用“词形重叠”自动判定数学等价，也不擅自合并候选；`0`项教师确认等价。
2. **14项未编号教学/内容/学业栏目**：每项保持原页面行 SHA、教师侧原创测评 ID，附一个待确认的可观测能力目标和一个独立验收阻断原因。所有 `UNMAPPED`，既有14份测评均不充当官方条款覆盖证明。
3. **七轨机器可审计分母状态**：428个启发式来源起点分轨：必修142、选择性必修101、选修A69/B70/C29/D17/E0；项目内部62个暂定拆分：必修60、选修B2、其余0。**七轨官方数学原子分母全部 null**，不能用已拆分的62项或早期113条工程映射当分母，也不能把启发式选修E=0理解成没有课程。
4. **审查门禁**：完整来源条款获教师审核 `0/61页`、数学等价认证0、自动合并0、教师正式批准0、学生正式发布0。第35页建模流程图仍标记人工视觉审查待办；14项能力栏目仍未正式映射。

源码及生成文件：
- `scripts/build_kb_batch67_clause_review.py`：可重放来源审查和分母矩阵；`--check` 比对版本化快照，`--verify-local` 仅Mac验证本地课标指纹。
- `docs/evaluation/KB_BATCH67_CLAUSE_CONTRAST_REVIEW.json`：6项数学对象/定义域对比，不将有限见证冒充一般证明。
- `docs/evaluation/KB_BATCH67_UNNUMBERED_OBJECTIVE_QUEUE.json`：14项能力与学业审查阻断。
- `docs/evaluation/KB_BATCH67_SEVEN_TRACK_COVERAGE.json`：七轨未知正式分母以及启发式线索数。
- `docs/evaluation/KB_BATCH67_SOURCE_AND_MATH_REVIEW.md`：逐项人工可复核说明。
- `backend/tests/test_kb_batch67_clause_review.py`、`scripts/mac_check.sh`、`.github/workflows/ci.yml`：增量测试/CI门禁。

## K07 有界数学见证

6种独立可重放的整数/有理数实例条件核查：一般多项式的负数/零处定义与对数的定义域；底数为2与1/2时单调方向不同；均值不等式的非负变量边界与正切的非零分母约束；除以未知数引发的丢根；二次函数符号的区间差异。每个案例都附原创问题、错法和失败原因。

**这些是受限输入检查，不是对课标全文的形式化证明、教师签核，也不认证学生任意自由步骤。** 538条历史未形式认证证明步骤、10组冲突仍未完成。

## Mac 实际回归（最终冻结源码后执行）

| 检查 | 结果 | 版本化原始日志 |
| --- | --- | --- |
| Batch67 增量测试 | **533 passed，0 failed**（覆盖428条起点状态、62条暂定原子、14栏目、6跨页区分、6数学见证、负面门禁） | `incremental.log` / `.exit=0` |
| Python 全量（已含上述533项，不重复累计） | **46,545 passed，0 failed，1条第三方弃用警告** | `mac_check.log` / `.exit=0` |
| Node | **111/111 passed** | `mac_check.log` |
| Tutor 策略 | **33/33 passed** | `mac_check.log` |
| RAG hard negative / Top3 | **40/40 / 22/22** | `mac_check.log` |
| Chrome/Playwright 合成浏览器脚本 | **15个脚本通过，0外部请求与页面错误** | `mac_browser_check.log` |
| browser pytest | **2 passed** | `mac_browser_check.log` |
| Mac完整验收 | **EXIT 0** | `mac_check.exit` |
| Mac浏览器验收 | **EXIT 0** | `mac_browser_check.exit` |

日志位于 `evaluations/results/2026-11-10-kb-batch67/`。
- `incremental.log` SHA256 = `37e6c71294f300f98fc02ca6484e44e3e23cb19b17ccd9e37f622d8cfeae2ffd`
- `mac_check.log` SHA256 = `9737d620f521286b562e4909c00a41ec90656953553d6caba17f73a9f09b9c38`
- `mac_browser_check.log` SHA256 = `65c5c4ea20eed4fd58c68a55d43143a2d1779a95084ac0fe5cd0425fe9deda6e`

早期定向测试 **532 passed / 1 failed**：新测试误查了不存在的通用 `source_window_sha256` 字段（实际为左右两侧独立哈希字段）。修复测试断言后，重放 **533 passed**，再完成 Mac 全量和浏览器回归。早期错误可从项目工作记录审计，未生成可声称为原始日志的本地文件；最终成功原始日志已版本化。

## 未解决阻断与下一批

- `K00`：对61页课标逐页人工/教师全文原子化，标记标题、非编号要求、选修A–E以及第35页流程图信息；正式七轨分母与真实缺口矩阵仍未建立。
- `K01/K06`：对14项栏目建立真正的任务→评分量规→教师审核证据，不能以一份题卡推断整栏能力达标。
- `K02–K05`：从**选择性必修和选修A–E**的课标实质性缺口批量建设高质量原创教学单元、完整定理前提、分步证明、近远变式、反例与错解；现有31篇内部候选草案并非官方全域课程覆盖。
- `K07`：从538步历史未认证推导与10组冲突按P0顺序审查，逐步骤核查数学前提，保持未审核状态。
- `K08/K09`：全部未经批准内容保留教师侧，正式学生索引不得泄漏；进一步完成真实API冻结对照评测及真实教师签核。

本批可复现工程测试通过，但**尚未完成正式官方覆盖、完整数学形式认证或真实教学发布**。继续保留独立 Draft PR，禁止自动合并。
