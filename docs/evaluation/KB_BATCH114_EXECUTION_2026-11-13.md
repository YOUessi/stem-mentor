# STEM Mentor｜Batch114 执行与验收报告（2026-11-13）

## 事实源与环境

- 仓库：`YOUessi/stem-mentor`；追踪 #17–#27；Draft PR [#139](https://github.com/YOUessi/stem-mentor/pull/139)，堆叠在 Batch113 的 Draft PR #138 上。
- **唯一开发/内容/测试设备：MacBook Air**，独立 worktree `~/Documents/文件/stem-mentor-kb-batch114`，分支 `feat/kb-batch114-official-24-61-statistics`；没有在 Tang 上进行知识库开发，未强推、未合并 main。
- 本批独立可复现源码修复 HEAD（日志提交前）：`f6c7ea0259622eae2e48510c2263c8e17250ea44`。最终GitHub远端 HEAD 在证据提交后以 PR 为准。
- 主工作树既有未提交改动未被覆盖。两份旧评测自动生成快照 `evaluations/results/2026-10-15-policy-and-retrieval.json` 和 `2026-10-15-v05-retrieval.json` 保留在Mac、未纳入任何本批提交。

## K00 / K01：课标来源与七轨分母

来源为本机合法访问的《普通高中数学课程标准（2017年版2020年修订）》原始 PDF，不将整本PDF上传GitHub。源文件 SHA-256：`cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。本批核对印刷 **24页（29条PDFKit来源行）与61页（26条）**，合计55条行、19个连续结构段；形成 **21条编辑性来源锚定候选**（必修10、选修B11），其中19条配有限精确数学见证，另外2条属于教学/概览说明，不应冒充数学证明。

已登记 **14/61页** 的来源结构候审，剩余47页未登记；**教师正式逐页原子化0/61**。七轨 `COMPULSORY, SELECTIVE_COMPULSORY, ELECTIVE_A–E` 的官方课程知识原子分母均为 **UNKNOWN（JSON null）**。禁止将21条编辑候选、14个已审结构页、113条旧工程映射或图形/方法卡冒充官方全量分母和覆盖率。

新增或重审来源字段严格拒绝伪造审批、非法课标轨道、来源漂移、重复知识ID、不合法输入字段以及遗漏结构行；所有候选 `REVIEW_PENDING`。

## K02–K06：8份原创完整教师候审讲义

新增4份定理、3份概念、1份方法，内容为：指数与对数函数互逆及合法底数/真数、余弦差公式的点积推导、零点/二分法连续与端点异号前提、函数不同表征与同一性、连续随机变量密度与概率积分、连续均匀分布矩及a<b退化、二维离散联合/边缘分布与独立性、卡方/t分布自由度与矩存在条件。

全部8份有正式陈述、完整假设、符号、先修描述、分步证明（仅定理型）或合法性解释、适用边界、错因和反例。配套 **16道教师分步例题、24层提示、16项近/远迁移任务、8组反例**。新增12个证明步骤均 **未认证**。教师侧完整答案不进学生自主挑战权威检索。

**实际数学纠错：** 若把连续密度的区间公式 `P(a≤X≤b)=∫_a^b f(x)dx` 无条件推广至 `a>b` 会得到负定积分，但该事件为空，概率为0。现已在正式讲义、适用前提、理由链、课标编辑候选和独立负面测试中强制明确 **a≤b**；例 `f(x)=2x` 于 `[0,1]` 时反向积分 `∫_1^(1/2)2x dx=-3/4` 不等于事件概率0。此处的有限反例不构成一般证明认证。

**实际计数纠错：** 先前生成器只扫描 `batch*.json`，导致深度讲义总数误报195（历史187+本批8）；漏掉24个非batch前缀资源包内的 **287份** 草案。现在扫描全部 `knowledge/deep/v1/*.json` 并排除当前生成包：**历史474+本批8=482份工程候审深度文档**，增加跨全部JSON文件的唯一ID和真实分母回归。482是工程草案数量，**不是482个教师认证课程原子**。

## K07–K09：独立验证与失败留痕

- Mac `PYTHONPATH=backend .venv/bin/python scripts/build_kb_batch114.py --check --verify-local-source`：通过；校验课标文件本地SHA、PDFKit行SHA、来源位置/结构、输出工件漂移。
- Mac最终专项 `backend/tests/test_kb_batch114_full_guard.py` + `test_kb_batch114_independent_examples.py`：**121 passed / 0 failed**，包括16道教师例题对应的独立精确算术/符号实例及反向积分负例；不能用来认证一般定理。
- Mac完整 Python/Node `scripts/mac_check.sh`：****65,794 Python passed / 5 skipped / 1 warning; Node 111/111 passed; complete mac_check.sh exit 0****。
- Mac完整 Chrome/Playwright `scripts/mac_browser_check.sh`：退出码 **0**，包含多宽度/交互、iPad模拟触控与笔压（非真实Apple Pencil硬件）；浏览器pytest **2 passed**。
- 版本化原始日志保留：`KB_BATCH114_FOCUSED_INITIAL.log`（原102项），`KB_BATCH114_SOURCE_CHECK_FINAL.log`，`KB_BATCH114_FOCUSED_FINAL.log`，`KB_BATCH114_BROWSER_FINAL.log`，`KB_BATCH114_MAC_CHECK_PRE_RECOUNT.log`，`KB_BATCH114_MAC_CHECK_INTERRUPTED_FOR_DOMAIN_FIX.log`，`KB_BATCH114_MAC_CHECK_FINAL.log`。最终文件哈希：

| Mac 原始日志 | SHA-256 |
|---|---|
| KB_BATCH114_BROWSER_FINAL.log | 12924aa0633f15308e3de217d3708e494064147bde30f67c7b05b7bdf376b253 |
| KB_BATCH114_FOCUSED_FINAL.log | a04f25539669cfe2fb1df6f219b00acc6ddefaf1cbcd20eb2764338ed1fe2330 |
| KB_BATCH114_FOCUSED_INITIAL.log | 7c4d0079453a07c2bb80dbc405e594caed443848a47cf7d4ed0e0121c9ab7db8 |
| KB_BATCH114_MAC_CHECK_FINAL.log | ca743e85bf7c3618d1cb6a6cc1245fcd9e894d8734b312e03d066864e19d0ba1 |
| KB_BATCH114_MAC_CHECK_INTERRUPTED_FOR_DOMAIN_FIX.log | 5924d1ca0e76b8b17d318feec326031207555f9424ed38a99c5c3691d354f828 |
| KB_BATCH114_MAC_CHECK_PRE_RECOUNT.log | 117c07ad32cea9cadb6e989cd0a1601369d2600440f2c06361dec84746d4b750 |
| KB_BATCH114_SOURCE_CHECK_FINAL.log | a66ec816af810bba93344bed3f5be88f3f5a888e6b34bbf5516f52a110b0d400 |。
- 第一轮前置完整测试本身为 **65,775 passed / 5 skipped / Node111 passed**，但外层zsh脚本错误使用只读变量 `status`，导致包装进程退出1；该包装退出不是pytest失败，故不把它当作最终完整验收。第二轮因发现反向积分条件遗漏而有意中断（日志保留）；随后重新从头运行所有门禁与完整测试。不得将中断流程冒充最终通过。
- 当前全部正式教师批准、学生权威放行、学生自由文本证明证书、形式数学证明证书均为 **0**。有限实例验证、结构完整和机器审核与教师审查保持隔离。

## 遗留缺口与下一批

官方七轨知识原子分母仍未知，47/61页来源结构缺口、教师逐页原子化仍0/61；历史 **172条文本先修关联待审核、538条证明步骤未认证、10项数学冲突**。十项冲突涉及函数复合定义域/奇偶/分段/零点介值、点线距离、二项/超几何分布、相关回归、正弦面积、向量线性运算等，暂不擅自裁决。当前知识库和 Agent 仍未达到学生权威发布条件。

下一批将先完成印刷25、62页的可追溯来源核查，**并改进覆盖方法，不再把每批只审2页当作逼近官方原子分母的充分进展**；建立可逐章节审校的官方要求候选台账（按必修、选择性必修、选修A–E明确标明未知数与欠缺证据），对风险P0的复合函数定义域、介值/零点、概率独立与先修边做成批次独立判错/反例，并持续铺开题族与教师候审内容。没有真实教师签字前不发布为APPROVED。

## 远端证据

GitHub源码采用原生非强制git push；PR #139保持 Open/Draft。已在 #17–#27 写入与各Issue直接对应的进展，最终完整测试证据及 SHA 哈希已归档；最终远端 commit/tree 由 GitHub PR #139 的 HEAD 与本地 Git Tree 核验，后续以 GitHub 为唯一事实源。GitHub Actions 的状态必须以实际运行状态为准，不将运行中视为通过。
