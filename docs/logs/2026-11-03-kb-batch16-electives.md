# STEM Mentor｜Batch16：选修 B/C/D/E 12 篇原创结构化数学草案与严格编辑态审计

开发日期：2026-11-03。只在授权 MacBook Air 的独立 worktree `stem-mentor-kb-batch16` / `feat/kb-batch16-elective-cde` 开发，父提交为 Batch15 `03cc4402858dab4417e5c523957343248cd8588f`。Mac 主仓未提交的 v0.13 变更原样保留；Tang 未参与。所有草案坚持 `REVIEW_PENDING`、`TEACHER_ONLY`，不存在真正的教研签名或学生已发布内容。

## 新增数学内容（12 篇）

| 方向 | 课程目标候选 | 知识主题 |
| --- | --- | --- |
| 选修 B | B-001 | 数列极限、函数极限与点连续性的序列判据，区分单个路径与全称量词 |
| 选修 B | B-002 | 二阶导数与凸性，严格凸的非必要条件边界 `x^4` |
| 选修 B | B-004 | 连续非负函数的面积、黎曼和与原函数积分公式，区分有向积分与绝对值面积 |
| 选修 B | B-014 | 时间单位变更对线性、指数和二次模型系数的影响 |
| 选修 C | C-006 | 固定名义利率、有效年利率与复利递推，严格计息周期条件 |
| 选修 C | C-007 | 两部门上三角投入产出模型，逆矩阵存在性与非负解 |
| 选修 C | C-008 | 离散人口 logistic 递推区间不变性，以及过大增长率的越界反例 |
| 选修 D | D-002 | 平移、正交旋转和反射的欧氏距离不变量 |
| 选修 D | D-004 | 斐波那契比值趋向黄金比例，区分极限与任何有限项的精确值 |
| 选修 D | D-006 | 十二平均律的相邻半音等比频率模型 |
| 选修 E | E-002 | 正方形四个保向旋转组成的四阶循环群，不混淆反射群 |
| 选修 E | E-004 | 期末等额现金流现值、零利率分支与期初/期末时间位置 |

每篇均有准确条件与符号、逐步说明（共 **48 条待独立认证证明步骤**）、显式反例、主要常见错误、2 道带核对的教师例题（共 **24 题**）、3 层启发提示、近迁移和远迁移、先修列表与原创许可。原始编辑态数据位于 `curriculum/highschool_math/author_draft_batch16.json`，由 `scripts/build_kb_batch16_lessons.py` 严格等值渲染到 `knowledge/deep/v1/elective_b_c_d_e_batch16.json`。

## 课程映射与可信度

- 工程知识节点从 **138 → 150**（必修 61、选择性必修 45、选修拓展 44）；**此数字不是国家课程标准官方原子条目分母**。
- 学习目标候选仍为 **132 条**，有编辑态关联建议的目标 **107 → 119**；关联边 **129 → 141**；仍有 **13 条**未有建议。所有关联均属于 `TOPIC_OVERLAP_PARTIAL_UNKNOWN`，未经过教师审定。
- 深度草案 **201 → 213**，定理型草案 **121 → 133**；独立完整证明认证 **0**；证明步骤义务队列 **391 → 439**，保持 `NOT_FORMALLY_VERIFIED`。
- 10 项旧历史数学冲突、23 项人工标记的语义深度缺口继续保持开放；没有用本轮新增内容自动关闭。
- 审核通过的真实教师知识 **0**；学生已发布深度课程 **0**；真实云端模型 API 请求 **0**；国家课标原子总分母仍 **null**。
- 选修 C/D/E 都不应被当作全国统一高考必修内容；地方课程、学校任选与大学预科扩展要进一步核对正式范围。现有页面锚点/原创候选未获独立课标审签。

## 工程与验证

- 新增独立专项 `backend/tests/test_kb_batch16_electives.py`：**577 项通过**；覆盖严格有理数、SymPy 子命题、保守测试边界与未经审核内容泄露拦截。数学子命题验证不等于通篇自然语言证明完成。
- `curriculum/highschool_math/extend_elective_batch16.py` 实现新候选工程 ID 合并及唯一性/可信状态限制；`scripts/build_kb_batch13_proposals.py` 以显式课程候选 ID、内容版本 SHA 重新生成编辑匹配建议（非名称模糊猜测）。
- `scripts/audit_kb_batch16_content.py` 按源文 SHA、课程类别、知识数量、学生可见性及严格零审批状态出具可复验报告 `docs/evaluation/KB_BATCH16_EDITORIAL_AUDIT.json`。
- 重建受增量影响的当前状态审计（课程、证明义务、旧冲突、语义缺口、学生保护与 API 零调用）；历史 Batch15 的固定版本结果保持内容不可变并用原文件 SHA256 门禁验证，不反向改写历史验收指标。
- 修复先前测试对最新全局工程/草案数的固定断言，以及编译器/构建器隔离目录缺失本批数据源的回归问题。
- 本批 CI 强制追加源码与渲染等值检查、保守覆盖审计，并沿用完整 Python、Node、模拟 Tutor 与学生安全拒绝测试。

## 可复验命令与日志

在本独立 worktree 使用授权 Mac Python 虚拟环境，执行：

```bash
export PYTHONPATH=backend
.venv/bin/python scripts/build_kb_batch16_lessons.py --check
.venv/bin/python scripts/audit_kb_batch16_content.py --check
.venv/bin/python scripts/build_kb_batch13_proposals.py --check
.venv/bin/python scripts/build_kb_batch07_audit.py --check
.venv/bin/python -m pytest backend/tests/test_kb_batch16_electives.py -q
.venv/bin/python -m pytest backend/tests -q
node --test tests/node/*.test.cjs
bash scripts/mac_browser_check.sh
```

专有日志保存在 `evaluations/results/2026-11-03-kb-batch16/`。第一次全套 Python 执行出现扩展课程引起的旧数量冻结与测试夹具缺文件错误（20 failed, 6253 passed，当时 `--maxfail=20`），修复后第二次 3 failed / 6354 passed，第三次 **6357 passed，1 warning**，详见三个日志。Node 全量 **111 passed**。专项 **577 passed**；其他数学证明仍待独立教研复查。

## 发布前复审修订与最终复验

正式提交前检查完整定理证明时，发现 **正方形 C4 旋转群**草案仅给出四种旋转的构造，未显式排除第五种角度；已经补上“任何保持正方形的旋转必须将任一顶点送到四个顶点之一”的必要性论证，保证“恰好四种”的结论不是未经证明的断言。同时强化 Fibonacci 比值测试，从宽松浮点误差阈值改为 **Binet 精确误差恒等式** `F_(n+1)/F_n - φ = ψ^n/F_n`（通过 SymPy 独立复核）。这是本批新增的数学质量修订，并未把此复核提升为教师正式认证。

新增最终复验日志 `evaluations/results/2026-11-03-kb-batch16/python-focused-recheck.log`、`python-final.log`、`node-final.log`、`browser-final.log`、`validation-final.log`；最终结果分别为 **577 passed**、**6357 passed (1 warning)**、**111 passed**；Chrome 完整历史浏览器回归 **PASS**，包含 iPad 手写和触控模拟（非真实设备）。历史首轮及次轮失败日志保留，以便审计恢复过程。以上仍属工程/有界数学检查，不替代真实教师签审。

## 下一批实际工作

继续补齐选修 C/D/E 在 132 项项目自编候选中剩余的 13 项无编辑关系目标，完善每章先修和参数退化例题，审查 B 课程更复杂的积分应用和 C/D/E 建模内容；随后逐条审查高风险的 439 条证明步骤，完整校对官方课标、处理 10 项冲突，构建真正可实名签审的教师工作流。发布前必须保持学生检索 Approved-only 和出题自主挑战不剧透。
