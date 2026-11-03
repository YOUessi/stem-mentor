# STEM Mentor｜Batch17：跨必修、选择性必修、选修 C/D 深度内容与课程候选全量关联

日期：2026-11-03。MacBook Air 独立 worktree `stem-mentor-kb-batch17`，分支 `feat/kb-batch17-cross-track-depth`，基线 Batch16 本地提交 `5bb38da84edb8703b04575cd99c7fa4fd4f5ca7d`。Mac 主仓的 **11 项**未提交改动仍保留，未在 Tang 开发或训练。

## 本批从 GitHub 问题和真实代码检查所得依赖

总 issue #17 与 #18–#27 均 OPEN；已存在 Batch16 Draft PR #42，采用堆叠式 Draft PR 路线，不自动合并。官方课标逐条审定与学生侧发布仍未完成。Batch16 冻结分母：213 深度草案、150 工程节点、132 项**项目自编的不完整课程目标候选**、119 个目标有编辑提案 / 141 条提案边、13 个目标无提案。

## 新增的 11 个原创知识单元（全部 REVIEW_PENDING / TEACHER_ONLY）

| 课程目标候选 | 知识类型 | 主题 |
| --- | --- | --- |
| COMPULSORY-002 | theorem | 子集/真子集、空集与集合相等的双向包含证明 |
| COMPULSORY-010 | concept | 定义域一致性与函数三种表征 |
| COMPULSORY-016 | concept | 正实底数、实指数定义与零/负底数边界 |
| SELECTIVE_COMPULSORY-018 | theorem | 三维向量基底存在唯一性，非零与线性无关区别 |
| ELECTIVE_C-002 | concept | 经典二值逻辑的同一律、矛盾律、排中律 |
| ELECTIVE_C-004 | method | 直接、逆否与反证法及前提 |
| ELECTIVE_C-005 | concept | 命题公理系相容与独立的反模型 |
| ELECTIVE_C-009 | method | 相关、预测、信度与因果识别边界 |
| ELECTIVE_C-011 | method | 问卷抽样框、响应率、缺失偏差、报告 |
| ELECTIVE_D-007 | theorem | 公共格点同步节拍的 gcd/lcm 证明 |
| ELECTIVE_D-010 | method | 单循环赛图模型、轮次下界与轮转构造 |

每篇均明确假设、符号、有效域、反例、常见错因、分步数学证明**草案**（仅适用于 theorem），或概念/方法依据；两道只对教师可见的例题、三层提示、近/远迁移及项目自编许可证信息。本批新增 **22 道**教师侧例题，**12 条待独立认证的证明步骤**，没有以符号测试替代真实教师审核。

原始独立内容：`scripts/author_kb_batch17.py` → `curriculum/highschool_math/author_draft_batch17.json`；由 `scripts/build_kb_batch17_lessons.py` 经严格 Schema 校验再渲染为 `knowledge/deep/v1/cross_track_batch17.json`。所有哈希在 `docs/evaluation/KB_BATCH17_EDITORIAL_AUDIT.json` 冻结。课程工程节点：`HS-MATH-151`–`161`；`extend_cross_track_batch17.py` 接入现有课程构造器。

## 13 个原无提案目标的处理

11 条得到新原创数学单元，另外 2 条明确以已经存在的草案提出**待人工审查的部分重叠关联**：选修 B-003→中值定理单调性草案、选修 E-006→微积分基本定理草案。编辑关联目标由 **119/132→132/132**，提案边 **141→154**；并未证明课程教学深度足够。**不把 132/132 称为国家课标覆盖率**：132 个学习目标只是项目自编、未签审、尚不完整的纸质页码定位样本。官方完整原子知识分母、官方覆盖率保持 `null`，所有链接 `TOPIC_OVERLAP_PARTIAL_UNKNOWN`，教师签署 0、学生深度知识发布 0。

当前 **224 篇草案**（136 theorem / 70 concept / 18 method），**161 个工程主题**（64 必修、46 选择性必修、51 选修拓展），**451 条定理分步证明义务仍未整体形式化认证**；原 10 项历史数学版本冲突和 23 项语义深度缺口仍 OPEN。原 26 方法卡和 71 画板不能冒充完整教材。

## 数学、安全与版本化验收

- 新增 `backend/tests/test_kb_batch17_cross_track.py`：**5166 passed**，包括 4096 对 6 元有限集合、625 组节拍周期、125 组空间基底向量、指数幂条件、命题逻辑、图论赛程、取样均值及伪教师审核/学生端泄漏负例。
- Mac Python 全量：先 53 failed / 11481 passed（课程计数快照、能力限制缺字段），再 6 failed / 11539 passed（遗留硬编码及构建隔离），修复后第三轮 **11545 passed, 1 third-party deprecation warning**，详见 `evaluations/results/2026-11-03-kb-batch17/python-first.log`、`python-second.log`、`python-final.log`。
- Mac Node：**111 passed**，`node.log`。
- 所有 GitHub CI 中本地知识/数学/发布审计 `--check` 命令均通过，`ci-gates-final.log`，没有忽略旧 Batch16 的历史结果。Batch16 旧审计保持源 SHA 与旧分母冻结；Batch17 用独立新增审计表示实时分母。
- Chrome 页面与 iPad 指针模拟使用 `bash scripts/mac_browser_check.sh`；不代表真实硬件 Apple Pencil 验收。日志：`browser-final.log`。
- 全部用户原始数据和教师完整证明都不会进入学生端 API；`student_evidence_lookup` 对未签核内容仍返回 `NO_APPROVED_EVIDENCE`。没有真实云端模型请求。
- `git diff --check` 通过；所有修改均在独立 worktree；主仓 11 个原有变更未触及。

## 本轮修复的具体工程问题

修复课程节点增量后的老测试固化分母、Mac 浏览器目录展示旧数字、构建隔离缺少新候选 JSON、项目工程主题新增条目缺失 `capability_limits`；重算当前动态审计但保留历史 Batch16 源 hash；Batch02 历史 39→29+10 清单不受新源数据污染。CI 新加 Batch17 源文件完整性、Schema 渲染以及 fail-closed 审核检查。

## 下一批优先级 / 严格 DoD

1. **K00** 独立逐页核对国家数学课程标准，建立必修/选择性必修/明确选修 A–E 的**官方逐项证据分母**，不要以当前 132 个项目候选充当官方全部。
2. **K02–K05** 针对现存 23 个语义深度缺口继续写完整分步讲义及必要证明，扩充尚未采样的真正课程原子条目。
3. **K07/K09** 将 451 条尚未形式认证的步骤按风险分组，优先核验数列、极限、几何退化、概率条件；10 组旧版本冲突由独立教师核对裁决。
4. **K08** 在真实教研身份、可信签名和撤销机制完善后，才可让 Approved-only RAG 与云端 Tutor 在实际授权学生情形下运行；未见题需要独立评测，模型回答不得自动认证。

代码库和 PR 才是正式交付与下一次执行基准；未签审全部保持 `REVIEW_PENDING`，不得擅自合并。
