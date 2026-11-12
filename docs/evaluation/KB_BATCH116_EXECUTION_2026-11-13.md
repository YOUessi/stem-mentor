# STEM Mentor · Batch116 执行与验收记录（2026-11-13）

## 交付边界与源码事实

- **仅 MacBook Air 开发和测试**：独立工作树 `stem-mentor-kb-batch116`，分支 `feat/kb-batch116-all-page-ledger`。
- 测试代码 HEAD：`99deb589f59c98a9407f3f118f0b0b777ee7a493`；基础提交：Batch115 `a593435952a55c155e497f063567f63a175e8dea`。
- Draft PR：<https://github.com/YOUessi/stem-mentor/pull/141>。最终增加本报告与原始日志的交付提交 SHA 以 PR HEAD 为准。
- 绝不对主分支强推/合并、使用 Tang 开发或将未审稿标记 APPROVED。Mac 现有两份历史评测快照的本地修改**未提交**。
- 源课标采用教育部《普通高中数学课程标准（2017年版2020年修订）》本地保留原件；其 SHA-256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。不入库版权课标全文。

## K00 + K01：解决来源总范围错误

此前来源索引只覆盖**印刷页13–73，61页**。本批从合法原件通过 macOS Swift PDFKit **独立指纹化188个物理PDF页**；额外127个物理页仅获得来源指纹，不能推断为127页课程知识内容，更不能据此计算课程覆盖率。

- `docs/evaluation/KB_BATCH116_FULL_PDF_FINGERPRINTS.json`：188页来源哈希/索引，不嵌入原件正文。
- `docs/evaluation/KB_BATCH116_SOURCE_INVENTORY.json`：61个既有印刷页与结构登记、课程轨道提示、每页审核状态、缺口队列。已登记18/61、剩43/61；这是**结构核验**，不是教师完整原子化。
- `docs/evaluation/KB_BATCH116_REVIEW_QUEUE.md`：按章节组织审校队列，标记跨轨页51、69、73、图像核对风险页35，以及选修E在第73页后段开始的事实；谨防课程范围超出既有61页。
- `scripts/build_kb_batch116_inventory.py` 和 `scripts/kb_batch116_full_pdf_manifest.swift`：重新从本机原件核验来源身份、来源指纹和历史61页的匹配；缺失/变造来源不得静默继续。
- `backend/tests/test_kb_batch116_inventory_math.py` 与CI门禁：拒绝重复/缺失来源页、跨轨误归属、伪教师审核、伪证明证书、凭空填写课标原子分母及来源文字未经许可入库。

本轮发现并修复一次真实轨道边界错误：**选修E实际从印刷第73页的后半部分开始**，不能仅从第74页开始算，也不能因为其属学校自主开发就把官方统一课程原子分母假设为0。

**七轨官方原子分母仍全部 UNKNOWN**；正式教师逐页原子化0/61，教师批准0，学生端权威发布0。项目历史草案总数不得作为分母或批准总数。

## K07：数学条件审查

`scripts/build_kb_batch116_condition_audit.py` 生成 `docs/evaluation/KB_BATCH116_CONDITION_AUDIT.json`，包含**28种高风险条件案例，每例正负各一组，56次有限精确见证**。覆盖消元除零、平方增根、对数定义域、符号反向、连续性/二分法前提、奇异线性系统、概率条件分母、向量零值、统计推断、OLS退化与连续密度区间方向等。

**数学验证严格限定为 `FINITE_EXACT_CASE_ONLY`**，不是一般定理形式证明；未审学生自由步骤、未签字教师审核以及被自动认证的普遍证明均为0。每个条件检查附有无效泛化提示与负面见证，便于教师后续逐项审查。

## 测试结果与原始证据

| 验收层 | 实测 | 结果 |
|---|---|---|
| Mac `scripts/mac_check.sh` 全量 Python | **66,277 passed，5 skipped，1 warning**；760.11s | 外层退出码0 |
| Node 单元 | **111 passed，0 failed** | 通过（包含在全量脚本） |
| Batch116来源/数学专项 | **359 passed，0 failed**；1.36s | 外层退出码0 |
| Chrome/Playwright 浏览器全面回归 | v0.9–v0.12、学习交互、移动端模拟、iPad笔压模拟等 | 浏览器包装器退出码0 |
| Browser pytest | **2 passed**；6.48s | 通过（属于浏览器套件） |

原始日志文件与 SHA-256（不是人工生成的通过数字）：

- `logs/KB_BATCH116_MAC_CHECK_FINAL.log` — `d67c1122b1e575020b6e9f31b7871419d7783b43c4b122dc5099e062dbfc847c`
- `logs/KB_BATCH116_FOCUSED_FINAL.log` — `43206f4a0cd8d6b3dd5893d00afabb1f343cf07c747bd3acee2027c74f61b3f0`
- `logs/KB_BATCH116_BROWSER_FINAL.log` — `09ca40e72dfc65e2956f1e55bfe84fbf7090cfc4977b6ba61fdf00047b5c20bd`

机器生成证据 SHA-256：61页结构台账 `abef8d41bd36ce1c459b5adceaff5a534de65e7dc1571e2d0008578a4b5fb0e1`；188页指纹 `541279e39649baf45817d92b446eec926432630d0fd2be740c641c2e27fc04e2`；数学条件审计 `2791c0967c200bfe1c6d32ffcfc8b65808d88b996a479609a87ac18bfb9fc8f3`。

### 已发现和纠正的真实问题

- 源范围遗漏：原61页不等于整个PDF；已生成完整188物理页的可核验指纹。
- 第73页轨道转换错误：选修E起点在页内，修复索引、门禁和回归断言。
- 开发期间的Python续行缩进、SymPy符号布尔判别及测试用语问题已经纠正；最终359项专项与全量测试通过。
- 最终Chrome模拟iPad输入**不代表真实iPad/Apple Pencil设备测试**。
- 测试后两份 `evaluations/results/2026-10-15-*.json` 历史评测快照出现的非本批工作树差异保留未暂存/提交，不作为本批源码成果。

## 本批仍未达成的验收与下一批

1. 在Mac上完成43个未结构核验页面的跨页、公式、课程轨道校正，并验证原188物理页中是否存在此前漏掉的课程章节；第35页PDF文本抽取失真需要查原始图像。
2. 建立教师可复查的**七轨真正课程知识原子总分母**，分必修、选择性必修、选修A–E报告已覆盖/未覆盖，不允许使用草案数代替。
3. 审查历史172条先修关系、538条未经认证证明步骤、10项数学冲突，形成带前提/证据/反例的纠错闭环。
4. 在批准门禁不放松的前提下继续扩展全主题原创深度讲义、教师题族及学生提示阶梯，并以RAG未审批隔离和负面回归验证教学Agent行为。
5. 正式教师审批和学生端权威发布均维持0；完整验收前Draft PR不合并main、不关闭#17–#27。

本报告的Mac测试源码SHA为报告提交之前的`99deb58...`。GitHub最终交付SHA应由远端PR HEAD校验；任何GitHub Actions仍进行中的检查均不得冒充通过。
