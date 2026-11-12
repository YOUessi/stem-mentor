# STEM Mentor｜Batch106 官方课标跨页数学条件与6份完整候审讲义执行记录

> **交付安全边界**：MacBook Air 独立工作树真实开发/验证；全部原子候选和新增讲义为 REVIEW_PENDING、TEACHER_ONLY，0项教师批准、0项学生权威发布。原子解释、脚本检查与有限数学见证不能替代正式官方分母、全域形式证明或教师审校。

## 1. 设备、源文件与源码事实

- 唯一开发与测试：Mac `YOUTangdeMacBook-Air.local`；独立工作树 `~/Documents/文件/stem-mentor-kb-batch106`；独立分支 `feat/kb-batch106-official-scope-conditions`，原主仓11项历史修改未触碰。未在Tang开发、未强推/合并main。
- 以 Batch105 远端提交 `608e55c5e2d00153d1dd449ef1ab6a5e9ddd660d` 的 Git Tree `d4e37737ce0714c8b3b47f4bc8e9b4be11d54121` 为源码基线；Mac本地对应的 `8cc5d2f...` 提交树完全一致。由于先前GitHub connector历史与Mac提交历史不同，交付使用相同源树、远端父提交，防止污染堆叠PR的diff。
- Mac Python 3.13.13、Node v22.23.1。来源为教育部《普通高中数学课程标准（2017年版2020年修订）》授权检查缓存原件 SHA-256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`；本次不上传课标PDF、版权教材全文或真实学生信息。

## 2. K00/K01 官方来源定位、拒绝门禁和后向一致性

- 基于印刷页15→16（必修量词/逻辑/不等式）、52→53（选修A连续/导数/积分）的连续来源跨页审查，新增 **2条跨页上下文桥、14个无重叠来源结构段，覆盖页16的29行和页53的28行（共57行）**；本地验证原PDF及PDFKit页摘要，CI仅验证冻结的来源摘要。
- 独立编写 **25条候审课程要求解释（必修10项，选修A15项）**：每条具有来源页与行范围、预设条件、误用泛化、不适用情形及受控数学检查。其余五个轨道本批未新建；七轨正式分母均为 UNKNOWN。25并非官方已认证原子数量。
- 约束构建器拒绝跨轨、伪造官方ID或教师批准、无效来源范围/条款映射、重复标题、不可追溯旧讲义ID、缺行/重叠的来源段、伪造跨页内容。加强 Batch104/105 历史重建器的版本冻结，使本批新增讲义不倒灌改变已版本化旧批次覆盖报告。

## 3. K02/K05/K06 数学内容与K07证据

- **6份完整原创候审数学讲义**：①量词否定的语义与反例见证（方法）；②基本不等式的非负域与等号条件（定理）；③介值定理的二分构造与连续性前提（定理）；④二分法的迭代不变量与误差上界（方法）；⑤二阶导数存在性的左右边界（概念）；⑥定积分的有向面积与黎曼和（概念）。合计 **2定理、2方法、2概念**。
- 6份均具备分型必需的定义/陈述、量词与假设、适用边界、逐步证明或逐步解释、反例/错因、**12道分步教师例题、18条分级提示、近远迁移、1条显式候审先修链接**。教师解答不进入学生自主挑战检索；异常伪批准由负例测试拒绝。
- 25条课标要求候选各附 **1组有限/符号数学见证及不当泛化拒绝**；6份讲义各附独立边界检查。没有获得任何普遍形式证明证书，也不验证任意自由文本学生步骤。
- 新增文件：`scripts/kb_batch106_scope_authoring.py`、`scripts/build_kb_batch106_scope_conditions.py`、`scripts/kb_batch106_deep_authoring.py`、`scripts/build_kb_batch106_deep.py`、`backend/app/kb_batch106_math.py`、`backend/tests/test_kb_batch106_scope_conditions.py`、`backend/tests/test_kb_batch106_teacher_depth.py`，以及源码生成的 JSON/Markdown/审计矩阵。Mac/CI均增加 `--check` 门禁。

## 4. Mac实际测试与可重复复验

- `bash scripts/mac_check.sh`：**退出码0**。Python全量 **64,468 passed、5 skipped、1条第三方弃用警告、0 failed**（728.81秒）；Node **111/111 passed**。无GPU/API调用。
- 两个Batch106专项测试文件独立运行：**214 passed、0 failed**（已包含于全量64,468，不重复累加）。覆盖25候选、6讲义数学条件、来源漂移、七轨伪造、结构坏例、可重复构建、非授权答案泄露、先修边无效状态。
- Chrome/Playwright跨视口/数值/离线测试通过；浏览器pytest **2 passed**（均为模拟浏览器，不声称真实物理iPad验证）。
- `.venv/bin/python scripts/build_kb_batch106_scope_conditions.py --check --verify-local`、`.venv/bin/python scripts/build_kb_batch106_deep.py --check` 和 `git diff --check` 真实通过。

### 完整原始日志与SHA-256

| 测试 | 路径 | SHA-256 |
|---|---|---|
| Mac full check | `docs/evaluation/logs/KB_BATCH106_MAC_CHECK_FINAL.log` | `4e31e8a5c348e7e5a167cd8b14099e636b407d29194343350f331614fed372c4` |
| Focused 106 tests | `docs/evaluation/logs/KB_BATCH106_FOCUSED_FINAL.log` | `199d9c89e8f7f47cb4887b352be3b7c3985b97bb5ee45fdafed5a1884c1ce9f1` |
| Chrome/Playwright and browser pytest | `docs/evaluation/logs/KB_BATCH106_MAC_BROWSER_FINAL.log` | `ef146ee99ea35618ddb771b527231adac4a4cccf5c5cef59797e28e029de379e` |

## 5. 后续关键缺口与下一批

- 七轨官方课程原子分母 **全部未知**，完整教师逐页原子化 **0/61页**；这14个来源结构段也不构成认证的完整数学知识原子。
- 此前仍有 **74项临时主题成对比较未完成、172条历史文本先修待审、538条历史证明步骤未认证、10项数学冲突未裁决**。本批新增的工程深度文档后总量411份，不等于411个已批准课标知识原子。
- 教师正式批准0，学生权威发布0，教学Agent尚不能把这些候审知识当作权威来源；需继续构建可审核的七轨冻结分母，做范围否定测试、证明条件重核和先修图谱语义审核。
- 下一批：从印刷页16→17、53→54继续逐条拆分、建立完整的课标要求候选及教师核对队列；继续成组补充高频讲义与题族、精确验证器、RAG拒答与防剧透回归，严格区分官方分母/工程标签/教师批准。
