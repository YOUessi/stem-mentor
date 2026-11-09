# STEM Mentor｜Batch72 Mac-only 独立能力/活动/教学证据审计（2026-11-10）

## 一、源码基线和研发边界

唯一研发及测试机器：授权 MacBook Air（YOUTangdeMacBook-Air.local）。独立 worktree：/Users/youtang/Documents/文件/stem-mentor-kb-batch72；独立分支：feat/kb-batch72-independent-competency-evidence。上一批 GitHub Draft PR #96 HEAD 为 0d299894f703ec2c13c44f946b91a7fa9a80d415，Git Tree 7a60bb336a08936d67f74e5f9d106596d7e3dfaa。Batch72 内容源码提交 c82e2d3f357d0d8e2451be696519fe6917bb5130，源码 Tree 8ab41a3e5c8d8f591cace6bedcd2b585a71a03c5。最终交付 SHA 以 GitHub 验证后为准。

未使用 Tang、外部模型 API 或真实学生数据；未修改 main 已有11项未提交变更、未强推/合并 main。官方依据：《普通高中数学课程标准（2017年版2020年修订）》，本批绝不提交有版权的课标逐段原文。

## 二、课程来源、真实边界与交付

沿用仓库已有 KB58 非知识原子类课标片段 28 项：学业要求 11、活动要求 3、教学建议 14，均为必修课程印刷第18–36页的**局部来源片段**。已有14项学业/活动测评提案分别绑定各自来源 ID；本批新增14项原创 TEACHING_ACTION 教学/观察方案，为其余14项教学建议建立独立候选证据链接。**28/28仅指候选链接完整、来源可追溯，不等于28项能力已正式覆盖，更不等于28个数学知识原子**。正式能力覆盖已认证0/28；七轨官方知识原子分母依然全部null。

新增14项教学方案覆盖二次不等式图数互证、三维直线投影、非正交基底、复数几何表示、异面直线、线面垂直条件、统计样本与总体、古典概型等可能前提、抽样代表性、频率与概率、数学建模闭环、有限正例与全称猜想、研究课题证据和结题诚信。每份均包含4步课堂引导、数学实例、错误推断、失败边界、可观察匿名证据模板、3级提示、近远迁移和6分分项量规，且仍为 REVIEW_PENDING/TEACHER_ONLY。

新增文件：
- scripts/build_kb_batch72_independent_evidence.py：课程源哈希、28源片段/14既有测评链接、14项新教学观察方案和数学实例可重放校验；
- knowledge/editorial_review/kb_batch72_teaching_practices.json：14份原创教师稿和空白匿名观察模板；
- docs/evaluation/KB_BATCH72_INDEPENDENT_REQUIREMENTS.json 与 .md：28项来源/证据关联的待审台账；
- backend/tests/test_kb_batch72_independent_evidence.py：正反例、来源伪造、审核越权及非空学生检索回归；
- scripts/mac_check.sh 与 .github/workflows/ci.yml：生成产物漂移检查与CI。

Mac 本地独立重算10个PDFKit页面SHA和28个来源跨度SHA全部成功。数据仅含项目原创课标释义、位置和哈希；并未完成整页教师全文审查。14个有限精确数学测试不能认证任何一般数学定理或学生自由解题步骤。14份新增教师稿不进入正式学生可引用库。

## 三、真实Mac测试与原始日志

环境：macOS授权 MacBook Air；Python 3.13.13，Node v22.23.1。原始证据位于 evaluations/results/2026-11-10-kb-batch72/，逐条退出码可检查。

| 项目 | 真实执行 | 日志及退出码 |
| --- | --- | --- |
| Batch72专项（包含10页本地源PDFKit指纹与14次非空批准基线学生检索） | **187 passed、0 failed** | specialized.log、specialized.exit=0 |
| Mac Python全量 | **47,287 passed、1 skipped、0 failed、1第三方依赖DeprecationWarning** | mac_check.log、mac_check.exit=0 |
| Node测试 | **111/111** | mac_check.log |
| Tutor规则基线 | **33/33** | mac_check.log |
| RAG困难负例与Top3 | **40/40、22/22** | mac_check.log |
| Chrome/Playwright脚本 | **15个脚本通过**；browser pytest **2 passed** | mac_browser_check.log、mac_browser_check.exit=0 |
| 完整检查 | **EXIT 0** | mac_check.exit |
| 浏览器检查 | **EXIT 0** | mac_browser_check.exit |

专项187项已计入Python全量通过部分；全量额外跳过一个依赖Mac专有本地PDFKit提取的用例，另在专项命令设置 KB72_VERIFY_LOCAL_SOURCE=1 后运行成功。浏览器仅Chrome模拟与合成临时数据库，不声称真实iPad测试。

开发过程中记录并修复的真实失败：首先发现从文档级而非行级读取来源PDF SHA的KeyError；其次内容门禁一处统一长度要求不适合短名称/错误陈述，经逐项扩写和按字段设阈值处理；最后专项初次为173 passed、1 failed，失败是测试没有构造**非空**正式批准索引，改为使用项目既有离线双审核fixture后重新执行，187/187通过。为避免受控数学示例被随意改写而仍通过数值检查，额外冻结14项数学示例文本哈希。没有放松教师内容隔离门禁。

全量脚本运行会改写两个含绝对路径的旧评估结果文件，**只在本批独立worktree**恢复无关快照噪声，保留原始测试记录；主仓11项本来未提交内容完整保留。报告与测试日志均以Git版本化证据交付；正式GitHub CI结果须独立复核，不能用本地EXIT 0替代。

## 四、未完成的全课程硬门槛

- 已有61/61页仅部分课标来源定位，428个启发式条款起点，62项内部临时拆分假设；皆不可作为正式知识原子分母。
- 必修、选择性必修、选修A–E七轨官方完整知识原子分母均为null；完成全页教师原子化审核0/61。
- 本批28项非知识原子片段有候选证据链接，正式教师核验覆盖仍0；此前其他未编号要求亦未因此自动认证。
- 历史538条未形式认证证明步骤、10组数学冲突仍开放；全项目真实教师批准0、学生正式深度发布0。
- 下一批应逐页核验课程标准的完整连续条款、第35页图示及跨页等价，分轨明确知识与能力/活动/教学要求的独立分母；把已经产出的原创草案按真正缺口扩展至全量、严格验证数学结论并邀请真人教师签核。无数学依据不自动认证，也不能仅靠数量宣称已完成完整高中数学知识库。
