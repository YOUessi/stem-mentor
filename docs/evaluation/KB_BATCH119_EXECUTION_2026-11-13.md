# STEM Mentor / Batch119：七轨语义原子先导、六份证明逐步审查与数学门禁

## 执行条件和GitHub来源

- 唯一代码与内容生产、测试环境：授权的 MacBook Air。独立 worktree：`~/Documents/文件/stem-mentor-kb-batch119`，feature branch：`feat/kb-batch119-semantic-atom-pilot`。
- 启动时已通过GitHub原生连接核查 master issue #17、子任务 #18–#27：11项均为 Open；上一轮 Draft PR #143 的远端HEAD为 `6494d0cd46426f954e7a6304e782fce1b8f090c1`。
- 代码以Mac本地Batch118冻结证据提交 `ceaa52ab478cf316cd2d22752efb8f3805097473` 为基础创建新worktree。Mac主仓有原有未提交修改；仅在新worktree开发和测试，没有覆盖它们。Tang未参与。
- 对比GitHub远端#143时发现Git对象历史不同，但源码树除本批14个变更文件外完全相等。为防止PR引入上批重复差异，执行**仅添加已核对远端父节点的非强制双亲合并提交** `b0b5740b6c289d0142901a3fd4e0e2d4f74505f6`，其两个父SHA是本批源码提交 `54a24c91c2b9a8d76ff64fd1a5e885dcd4d833a7` 和Batch118远端 `6494d0cd46426f954e7a6304e782fce1b8f090c1`。合并前后Git Tree **完全相同**，实测源码未被改变，原生Git push已成功，PR #144最终diff为14个本批文件。不曾强制推送或合并main。
- 标准来源为《普通高中数学课程标准（2017年版2020年修订）》，本机合法PDF文件SHA-256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`，188个物理页面；保留旧课程内容核对范围的印刷13–73页61页来源指纹。**不上传版权原件、PDF全文或真实学生数据。**

## K00/K01：从405个排版线索向真正的语义候选迈进

- 对照Mac本机PDFKit私有来源行，人工编写**49条互异语义教学候选**，涉及19个印刷页；覆盖必修9、选择性必修16、选修A6、B4、C6、D4、E4。
- 每条候选保留稳定的候审ID、概念/定理/方法类型、数学适用条件、至少一个失效/非例、课程分轨、先修候选链接、原始印刷页+物理页号、行区间SHA-256、冻结页SHA-256、对应排版线索ID，以及公式原图重检标志。
- 本批候选实际与历史405条来源排版线索中的**68条**关联；337条排版线索尚未关联。候选可以来自同一来源行的不同语义；无排版线索的行也可建立独立、哈希锁定的候选。不能以68/405声称课程覆盖率。
- **49是编辑性先导集合的大小，不是官方七轨数学原子分母**。所有七轨正式分母保留 `null/UNKNOWN`、全轨完成 `false`，教师批准和学生端权威发布均0。
- E轨内容为学校可选扩展示例，绝不能当作全体高中生必修课程。数学排版存在风险的6条候选明确保留原始图像重检要求。
- 执行脚本 `scripts/build_kb_batch119_semantic_pilot.py --write/--check [--verify-local-source]`；Mac校对61页原始来源指纹和本批49条行跨度哈希；CI离线校验冻结来源哈希结构和拒绝伪审批，不声称离线校验等价于公式图像审核。

## K07：六份逐步证明原稿与32次有限精确见证

- 六个项目原创、明确假设的数学定理审稿：等差前n项和、等比分段有限和、实收敛数列有界、介值定理、中值定理、导数符号判断单调。
- 每份均列出定理适用条件、逐步推导与原因、失效边界、反例；保留 `REVIEW_PENDING`、`TEACHER_ONLY`、`machine_general_proof_certified=false`。尤其等比前n项和 `q=1` 分支、导数零点不必是极值点、中值定理的连续/可导前提均不能遗漏。
- 数学脚本：15项独立选定的有限精确核验；6份证明另以SymPy核验等差有限和8项、等比有限和8项、驻点反例1项，共17项。合计**32项有限精确见证，不是32份定理证明**。没有任何一般定理由符号计算自动认证。
- 六份完整证明不作为学生挑战自由检索直接答案。教师正式数学审校及学生自然语言步骤核查均尚未完成。

## K08/K09：负面回归与验收边界

- 新增测试 `tests/test_kb_batch119_semantic_pilot.py` 和 `tests/test_kb_batch119_proof_reviews.py`：总计**113项通过**（本批两文件，0失败），包括逐条来源与数学条件、七轨分母真实性、非法source SHA、跨轨行、孤儿先修、虚构审批、伪造证明认证、教师答案可见性等故障注入。
- 将构建器、严格一致性检查与专项pytest写入 `scripts/mac_check.sh` 和 `.github/workflows/ci.yml`；两个构建器 `--check` 及Mac `--verify-local-source` 已通过。JS语法与Shell语法检查通过。
- 上述113项是独立运行的专项验收数字，后续完整Python将重复运行它们，不能重复相加成不同覆盖。

## 仍未完成的验收门槛

- **七轨官方完整原子分母仍UNKNOWN**：405排版线索、49语义编辑候选与506份历史候审深度稿属于不同对象，不得互相替换或冒充全量课程完成率。
- 本批没有新增正式批准/上线单元。此前历史未审先修172条、证明未认证538条、数学冲突10项需要独立清账；本批六份证明原稿不等于消除这538条历史债务。
- 尚未完成所有61个内容页的逐项数学审核，也没有真实教师批准任何知识单元；学生权威知识发布仍为0。
- 下一批应优先解决剩余337条来源线索和所有未与线索绑定的正文数学要求，完成跨页去重/同一原子跨轨等价分析，然后继续成组原创讲义、独立数学真值验证和历史先修/证明审查。
- GitHub PR #144继续保持 Draft，不合并main、不强推、不改动Tang，不能仅凭CI软件通过声称产品教学完成。

## 完整Mac/浏览器最终验收（2026-11-13，已完成）

- **冻结代码commit**：`b0b5740b6c289d0142901a3fd4e0e2d4f74505f6`；对应源码Git Tree：`67fb110178a199c45021744484ac7099d4c38f8a`。最终日志提交不会修改该源码树中的任何程序、数据或测试文件。
- **Mac真实完整验收**：`bash scripts/mac_check.sh` 退出码 **0**；后端Python **66,293 passed / 5 skipped / 0 failed / 1 warning**，耗时 1131.66 秒，警告来自第三方 Starlette/AnyIO 弃用接口。Node.js **111 passed / 0 failed**。
- **Batch119新增专项**：候选数据及负面门禁 **96 passed**、证明审校及精确边界 **17 passed**，合计 **113 passed**；这是根脚本另外执行的根目录专项，与上文 backend/pytest 的 66,293 属于不同pytest调用，不能用同一测试计算两次课程覆盖。
- **Mac Chrome/Playwright**：`bash scripts/mac_browser_check.sh` 退出码 **0**；包含响应式渲染、极值与边界条件、触控/笔压模拟、前端交互及独立browser pytest **2 passed**；这是浏览器模拟而非真实Apple Pencil硬件认证。
- **失败与保护**：本轮最终完整脚本及浏览器均无失败。根worktree已有未提交修改未触碰；当前独立worktree由测试自动刷新的两份 `evaluations/results/2026-10-15-*.json` 未加入交付暂存区，不覆盖、不作为新知识证据。合法课标PDF原件及私人PDFKit文本未上传。
- **明确待审数学边界**：有限幂级数求和恒等式可在代数上讨论 `q=0`，但高中通常所称“等比数列”按逐项比值定义要求相关项非零，不能把代数扩展直接冒充正式等比数列定义；第S04/S05条和证明稿保留 `REVIEW_PENDING`，下批优先统一此处术语与教材适用域并加回归。在教师签署前不得权威发布。
- **官方原子分母仍UNKNOWN**：当前49条仅编辑候选，405条仅排版线索，剩余337条线索没有与这些候选链接，所有七轨正式分母和学生权威发布均未完成。

### 版本化原始证据 SHA-256

- `docs/evaluation/logs/KB_BATCH119_MAC_CHECK_FINAL.log` — `04cebe583cda176e9daa288efaaf749548b4c6c02ee56d2ba1af3110596c32f4`
- `docs/evaluation/logs/KB_BATCH119_MAC_CHECK_FINAL_EXIT.txt` — `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- `docs/evaluation/logs/KB_BATCH119_BROWSER_FINAL.log` — `b3b4ef833f350a92e08171ef6811160b74160fe1c37e3535bcef6f69fb286096`
- `docs/evaluation/logs/KB_BATCH119_BROWSER_FINAL_EXIT.txt` — `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`

**GitHub交付**：Draft PR #144。最终交付SHA以GitHub PR远端HEAD为准；不得因为源码/测试通过而合并或标注教师批准。
