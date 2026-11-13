# STEM Mentor · Batch111 — 官方课标21/58页、三角与微积分极限审计（2026-11-12）

## 项目边界与开发环境

- 任务：#17（总任务）/ #18–#27（K00–K09）；从 Batch110 Draft PR #135 续建。
- **唯一开发/内容生产/测试设备**：MacBook Air，独立 worktree `~/Documents/文件/stem-mentor-kb-batch111`，分支 `feat/kb-batch111-trig-limit-source-guards`。未在 Tang 编辑/测试，未改动 Mac 主工作树及其他已有工作树。
- 从 Batch110 本地 Git Tree `2f15fbd5f5aa48f1925197d3a3425dcaf9fa4c52` 衍生；该树与远端 Batch110 `549d46eac956ddc4a531261b4859d68111b12c4f` 的源码树一致，实际 fetch 后独立比对。待正式同步时以 **远端 Batch110 commit** 为 PR 基线，不覆盖 main。
- 官方课标：教育部《普通高中数学课程标准（2017年版2020年修订）》；本地受控原始 PDF SHA-256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。仅存储 PDFKit 行号和哈希、原创讲义，不上传全文、学生信息或第三方版权教材。

## K00 / K01：课程来源、类型及七轨分母审计

- 官方课标印刷第 **21页**（PDF索引28）与 **58页**（PDF索引65），分别为 **32行/36行 PDFKit来源文本，合计68行**。
- 手工原创课程解释形成 **15个不重叠结构区段**、**20项带明确条件和失败泛化的编辑候审要求**：必修10，选修B10，选择性必修/选修A/C/D/E本轮0。17项有有限精确或受控数值数学见证，其余3项是教学目标/星号历史活动，不应伪装为需要证明的定理。
- **页21对数逆函数与弧度、单位圆、正切**；页58选修B数列极限、单调有界、函数极限、连续性、二阶导、中值定理、三角不等式、极值、微分。
- PDFKit输出在页21分数换行异常；不能把断行文本误认为完整数学公式。保持 **21→22和58→59** 跨页未完成标记，任何有疑义的公式需要教师对照 PDF 图像。
- 审计代码 `scripts/kb_batch111_content.py`、`scripts/build_kb_batch111.py`；冻结结果 `KB_BATCH111_SCOPE.json` 与 `KB_BATCH111_COVERAGE.json`，含真实来源SHA、分轨计数、负面泛化和空的正式分母。
- **官方七轨知识原子分母仍全部 UNKNOWN**。在本轮合并对照的最近三个批次中仅 **6/61 来源页**作过行结构对照（19/20/21与56/57/58），并不是全量课程覆盖率；全体 61 页教师正式认证原子化为 0。
- Schema和构建器拒绝：遗漏/重叠来源行、错误 PDF 页/哈希、不合法课程类型、偷渡 APPROVED/官方原子ID、跨必修和选修B、不满足教学字段、循环/前向先修ID、重复课程候选ID、错误归属。
- 候审来源和结构统计不等于教师审定的正式原子。

## K02–K06：八份原创完整教师侧候审讲义

1. **指数与对数互为反函数**：单调一一对应、正真数条件、逆映射与定义域。
2. **角度与弧度换算**：一周2π/360°、带符号角与单位输入错因。
3. **单位圆三角函数**：sin/cos坐标定义、值域和正切分母合法性。
4. **正切定义域**：断点π/2+kπ、仅在定义区间谈连续与严格递增。
5. **数列极限ε定义**：任意ε、选取统一的N、有界非收敛反例。
6. **单调有界收敛**：实数完备性、上确界与ε证明、缺任一条件的反例。
7. **拉格朗日中值定理**：闭区间连续/开区间可导、Rolle辅助函数证明、|x|尖点。
8. **sin(x)<x（x>0）**：差值导数非负、在非零开区间严格正的积分论证、x=0/x<0边界。

- 类型：**4 theorem / 3 concept / 1 method**；8个版本1.0.0 `REVIEW_PENDING` / `TEACHER_ONLY` 的原创建议文档（`knowledge/deep/v1/batch111_trig_limits.json`）。
- 每份具有明确陈述、符号和适用域、至少3条解释/带依据的证明候选、反例/错因、**2道带步骤及校验的教师例题**、**3级提示阶梯**、近/远迁移题；批次新增 **16例题、24级提示、16迁移、8反例**。
- 新增 **4条**前向索引不允许的本批有向先修约束，**12条新证明步骤均仅为候审**，不宣称形式化证书。
- 8份本轮讲义入库后工程深度草案总数为 **457份**，并不代表457个教师批准的独立官方原子。旧的172条文本先修、538历史未认证证明、10项数学冲突仍未解决。
- student_evidence_lookup 按真实标题检索仍为 `NO_APPROVED_EVIDENCE`，并拒绝教师侧答案和校验内容下发。未批准知识只用于教师审稿，不用作学生权威事实。

## K07 / K09：独立数学检验、回归门禁与原始失败

- `scripts/build_kb_batch111.py --verify-local-source` 已在 Mac 检查源 PDF 文件字节SHA，页21、22、58、59本地PDFKit缓存及元数据SHA，并核对来源行数。
- 有限实例覆盖：对数正真数、底数单调性、角度/弧度、单位圆、正切断点、数列ε与交替振荡、Rolle/MVT条件、正弦严格不等式、闭区间端点极值、微分≠有限增量。
- 新增 `backend/tests/test_kb_batch111_math_source_guard.py`：按来源20项、讲义8份、伪权限/版权/结构/跨轨负面场景和精确分数、SymPy/反例覆盖。**首轮143项中141通过、2失败**：
  - 伪造顶层 lesson 字段 `review_status` 曾被构建器默默忽略；修复为 authoring 字段集合白名单拒绝，禁止静默升权。
  - SymPy `log(8,1/2)` 未直接归约到 Python `-3` 的结构比较；修正独立测试为 `simplify(log(y,a)-x)==0`，检验数学相等而非表达式打印结构。
- 修复后专项 **143 passed / 0 failed**，初始失败日志和成功日志分别归档：`logs/KB_BATCH111_FOCUSED_INITIAL_FAILURE.log` 与 `logs/KB_BATCH111_FOCUSED_FINAL.log`。此前两次错误均有真实可追溯测试结果，没有隐瞒。
- Mac `scripts/mac_check.sh` 和 GitHub CI 已加入新批次可重建检查；本机执行同时用 `--verify-local-source`，远端只能核对版本化 SHA 锁而非私有 PDF 字节；Chrome/Playwright/Node/Python全量仍以最终真实日志及独立GitHub CI结果为准。
- **最终 Mac Python/Node 全量验收**：实际完整运行 `scripts/mac_check.sh`，退出码 **0**，Python **65,418 passed / 5 skipped / 1 third-party warning / 0 failed**（1065.93秒），Node **111/111 passed**，包含本批143项专项；本次没有调用模型 API。Chrome 独立完整回归 `scripts/mac_browser_check.sh` **exit 0**，既有绿色界面、数学实验室、iPad触控/笔压模拟及末尾浏览器pytest **2 passed**；浏览器模拟不是物理iPad设备验收。
- 所有 SymPy、分数精确计算、有限样例对照都不是对任意实参数的形式证明；任何一般定理和任意学生自由文本解题步骤仍未教师认证。

## 依赖/未完成与下一批

- #18 K00：七轨课程的官方原子完整分母未知；需从当前页簇继续逐页审定、去重与跨轨证据核实，并对 PDFKit 公式视觉校对。
- #19 K01：候审结构门禁已有，但最终批准需要真实教师ID、版本化审校证据；此批未擅自升权。
- #20–#23 K02–K05：本轮扩展三角、极限与经典微积分条件，但概率统计、建模、选修C/D/E的全域正式内容仍需大批次系统补齐。
- #24 K06：按每个正式原子对齐的完整题族分母仍未冻结。
- #25 K07：优先从538个历史步骤选择高风险缺条件/除零/退化论证，交叉裁决10项冲突；本轮新增12步骤必须继续候审。
- #26 K08：学生 RAG 权威素材不足，真实 API 正确率/延迟/成本评测不可伪造。
- #27 K09：整库教师审校、证据引用、隐私版权、未见题集和真实学习增益尚未满足正式发布门槛。
- 下一批：第22/59页严格跨页语义审核，随后成组补充三角恒等与数列/微积分课程，继续高风险证明的量词前提反例、正式原子审定与 RAG 教师/学生分层测试。保持 Draft，不合并主分支。

## 本批真实运行日志哈希（Mac 本地原始字节）

- `docs/evaluation/logs/KB_BATCH111_FOCUSED_INITIAL_FAILURE.log` · SHA-256 `06b2a998884503db51b743a946e36c0b36b9eac8abe6d15d7ad594b9f987497a`
- `docs/evaluation/logs/KB_BATCH111_FOCUSED_FINAL.log` · SHA-256 `0cf763ca12b32bc3fab85db16a4840028048dd9e820924bddf5b57f5af42b5c8`
- `docs/evaluation/logs/KB_BATCH111_MAC_CHECK.log` · SHA-256 `345ee2a594c9a18da30faaad6df659a771ab709ef86dec8884752ab8a4e7358a`

## 浏览器真实验收及失败试验（同一 Mac）

- 完整浏览器命令：`bash scripts/mac_browser_check.sh`，**exit 0**，覆盖绿色学习工作台、数学实验室全历史Chrome脚本、跨屏响应式、模拟iPad 9项交互、双指手势/触控笔压力、独立browser pytest 2 passed。使用隔离临时SQLite及随机空闲端口，自动清理服务；无真实学生数据。
- 初次单独运行 `pytest -q tests/browser` 未启动服务，产生 `ERR_CONNECTION_REFUSED`；随后误用纯静态HTTP服务，导致 `/assets/ipad/*.js` 404和页面导航超时。**均属测试环境启动错误，不能宣称此两次试验通过**，原始静态服务器失败日志保留。最终改用仓库规定的 `mac_browser_check.sh` 启动真实FastAPI + 隔离数据库后成功。
- 本批新定理有12条候审证明步骤，无一步因有限样例而升为形式证明。逐步审核条件、正式课程分母和教师审稿仍是上线阻断。

### 完整浏览器证据 SHA-256

- `docs/evaluation/logs/KB_BATCH111_MAC_BROWSER_FINAL.log` · SHA-256 `cfb9517150328910fb6ed0c97fe88698506ee96c3fe38e119023e57cea856786`
- `docs/evaluation/logs/KB_BATCH111_BROWSER_STATIC_SERVER_FAILURE.log` · SHA-256 `beba205bdee43d480ee08548410cb111c10fe57de50fc53b0349fbd6945b1751`
- `docs/evaluation/logs/KB_BATCH111_BROWSER_STATIC_SERVER.log` · SHA-256 `c7a0ce8b0cb76ff54959619d8508e926719063dcd4fe162a52e8bd34f2f94355`
