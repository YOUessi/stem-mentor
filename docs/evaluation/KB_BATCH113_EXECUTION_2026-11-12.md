# STEM Mentor · Batch113 执行与数学质量报告（2026-11-12）

## 交付性质与来源

- 代码与内容仅在授权的 MacBook Air 独立 worktree `~/Documents/文件/stem-mentor-kb-batch113` 中修改和测试，分支 `feat/kb-batch113-official-23-60-math`；基线 Git commit `a681823e04b4eeefd9c02c197732575bba2095d9`（Batch112 Draft）；没有改动主仓的未提交数据，没有使用 Tang 开发。
- 课标基线：教育部《普通高中数学课程标准（2017 年版 2020 年修订）》。本批仅做印刷页 23、60 的来源结构与数学要求候选复核。PDF 原件保存在 Mac；GitHub 存来源 hash、行级证据、原创编写内容，不存受版权保护的全文。
- `scripts/kb_batch113_source.py` 为来源审计候选及区段；`scripts/kb_batch113_lesson_authoring.py` 为原创数学编写真源；`scripts/build_kb_batch113.py` 检验来源、生成知识数据/审计/覆盖报告并维护哈希；`backend/tests/test_kb_batch113_full_guard.py` 独立执行异常输入、精确算术、符号边界、学生防泄漏回归。
- Mac 和 GitHub CI 均增加 `build_kb_batch113.py --check` 门禁；Mac 还执行 `--verify-local-source`，对本地官方课标 PDFKit 原始行进行校验。

## K00 / K01：来源与分母真实性

- 课标印刷页23（必修）与60（选修B）共55条原始 PDFKit 文本行、11个连续非重叠来源结构区段，新增22条来源锁定的 **候审数学要求**（必修11、选修B11），其中20组有限精确/有界数学见证、2组为教学模型边界反思。
- 机器拒绝：来源行遗漏/重叠、越页、轨道错误、重复键、篡改 PDF hash、伪造教师批准、伪造通用证明认证、虚构官方原子 ID、缺失前提、孤儿关联/非法编辑结构。
- 七轨 `COMPULSORY / SELECTIVE_COMPULSORY / ELECTIVE_A–E` 正式官方知识原子 **总分母均为 UNKNOWN**。22项候审来源解释不是22份教师认证官方原子，不能计算官方课程完成率。
- 最近五批10页来源复核仅代表 `10/61` 页源结构编辑覆盖，**不代表教师逐页原子化**；教师完整逐页原子化为 `0/61`。第59页闭圆/椭圆极值缺口单独回填至本批教学草案，不伪造成本批第60页的来源。

## K02–K06：九份独立原创教学草案

1. 指数、线性、对数的渐近增长次序及域边界（定理）；
2. 线性/指数现实模型选择、残差与外推失效（方法）；
3. 数学定义域与现实模型有效域（概念）；
4. 参数量纲和时间尺度换算（方法）；
5. 非零方向向量的正交投影及零向量拒绝（方法）；
6. 异面直线的距离、非平行前提与平行退化（定理）；
7. 三阶行列式为零和列向量线性相关的等价性（定理）；
8. 高斯消元的可逆行操作、零主元和零倍缩放失效（方法）；
9. **闭圆/闭椭圆上二元二次函数的全局极值**（方法；修复第59页遗留的圆/椭圆极值内容缺口）。

每份草案含正式陈述或定义、符号、完整适用条件、推导/理由、反例与错因、2道项目原创教师例题、3级提示、近/远迁移。合计9份深度草案、18道教师例题、27级提示、18项迁移及9组失效反例；3个定理的9条论证步骤仍为 **候审**，不是机器形式化证明证书。

新增知识全部 `REVIEW_PENDING / TEACHER_ONLY`、未审核证据不可进入学生权威知识检索；教师完整答案不能在独立挑战阶段泄漏。教师审批为0、正式发布为0、任意学生自由步骤认证为0。

## K07：独立数学条件验证

- 渐近增长：利用二项式项为整数指数比构造上界，再用相邻整数夹逼推广到实数；明确 `log₂x` 正定义域。
- 时间单位：使用精确分数验证月倍率1.1转换为季度倍率1.331，不把样本拟合误认为无限外推的现实定律。
- 正交投影与异面距离：验证残差点积为零、投影分母非零，平行方向叉积为零时拒绝使用异面直线距离公式。
- 三阶行列式：用奇异矩阵同时构造有解与无解的非齐次方程，反驳“行列式为零就一定无解”的错误泛化。
- 高斯消元：给出零倍行操作破坏解集等价的反例。
- 闭椭圆二次函数：结合内点驻点与全周期边界参数化，分别核对单位圆 `x²+4y²` 及半轴 `(2,1)` 椭圆 `x²−y²` 的全域极值；禁止以凸多边形顶点法替代一般二次函数闭椭圆极值。
- 这些自动数学验证只能保证受支持的**有限实例/精确表达式**，不自动将一般定理升级为形式证明或教师批准。

## 测试与交付证据

- 本批专项及数学负例初始日志、修复后专项日志：`docs/evaluation/logs/KB_BATCH113_FOCUSED_INITIAL.log` 和 `KB_BATCH113_FOCUSED_FINAL.log`。
- Mac 全量命令：`bash scripts/mac_check.sh`，日志 `docs/evaluation/logs/KB_BATCH113_MAC_CHECK_FINAL.log`。
- Chrome + Playwright 浏览器命令：`bash scripts/mac_browser_check.sh`，日志 `docs/evaluation/logs/KB_BATCH113_BROWSER_FINAL.log`。
- 源/产物可复现检查：`PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch113.py --check --verify-local-source`。
- **Mac全量**：`bash scripts/mac_check.sh` 返回退出码0；Python **65,665 passed / 5 skipped / 0 failed / 1第三方弃用警告**（1021.24秒）；Node **111 passed / 0 failed**。
- **Batch113专项**：初次运行 **101 passed / 1 failed**；原因是测试错误地以为 SymPy 的 `0/0` 会抛 `ZeroDivisionError`，实际上返回 `nan`。修正断言为 `is sp.nan` 后 **102 passed / 0 failed**；已保留初始失败原始证据。
- **Chrome/Playwright完整回归**：`bash scripts/mac_browser_check.sh` 退出码0；覆盖数学实验室、极端参数、响应式视图、iPad 模拟触摸和笔压；末尾浏览器 pytest **2 passed**。iPad为模拟交互，不声称真实硬件通过。
- **来源/构建门禁**：`.venv/bin/python scripts/build_kb_batch113.py --check --verify-local-source` 成功，真实 Mac PDFKit 源行校验、输出物一致性及Schema 负面拒绝均通过。
- **源码提交（首次、未附运行报告）**：`a08e89934e84bfbac9a1339185bd162cd2d6d72b`；Git Tree `97e1a4c24702d5cc27fcc6c43facb38be407a2e3`。最终日志/报告 commit 单独快进补充，均不对main合并或强推。
- **原始测试日志Git Blob / SHA-256**：
  - `KB_BATCH113_FOCUSED_INITIAL.log`：blob `ac332a6cc8e55f2fc8bb2049805afd134678e5f6`；sha256 `9ca21ff2f16a1130edb62c85660d11fce965e085616fe7672afffe9de8097a11`；1050 bytes。
  - `KB_BATCH113_FOCUSED_FINAL.log`：blob `453ffd8019b7c2fccbbf2ae76ae22a672f43f755`；sha256 `43bb0e786e9114f181af4373e592ae0d2bbc8f6a396552f9761c9e9f0f6ffbc0`；180 bytes。
  - `KB_BATCH113_MAC_CHECK_FINAL.log`：blob `87c0ada7c02ae959fba2b944e11af9077c2a6152`；sha256 `0b7f78b9f764aacad8a99005e3356db5ec9d98212ad21e5fad5b7f5a1d452cde`；114122 bytes。
  - `KB_BATCH113_BROWSER_FINAL.log`：blob `d134beb2ce93a748cdda79d4439c1dc0498bea97`；sha256 `869931359862bf097a880320a716935a1c889254840eca38344d7c89a32c51ee`；2442 bytes。

## 尚未完成以及下一批

- 全部七轨官方课程总分母仍未知；历史先修关系172条、未认证证明步骤538条、数学冲突10项均未因此批自动变为已解决。
- 后续应继续来源第24、61页及跨页关系，但不应一直只追页数；应并行制定完整官方课标原子分母与审核人可检查的逐页验收清单、按高风险排序处理证明/先修关系，并将逐章真正通过教师审核的材料接入学生可用证据 RAG。
- 仍必须由真实教师正式校核、确认数学证明与学生可见性；任何未经审核内容不能标为 APPROVED。
