# STEM Mentor｜Batch109 Mac 开发、验证与交付执行记录（2026-11-12）

## 事实源、环境和保护范围

- 项目 `YOUessi/stem-mentor`，关联 Master #17 和 K00–K09 #18–#27。
- 所有源码、源标准本地核验、数学检查、Python/Node/浏览器回归均在 **YOUTangdeMacBook-Air.local** 的 `~/Documents/文件/stem-mentor-kb-batch109` 独立 worktree 完成；不在 Tang 上开发。
- 来源：教育部《普通高中数学课程标准（2017年版2020年修订）》本地PDF；SHA-256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`，使用原版字节及 PDFKit 页指纹/行坐标逐项验证，**未提交版权PDF**。
- 基准源码树 `aacb74a3860a282ba8c8be6992bda264d79775e6`（与上游 Batch108 GitHub 最终树一致）；本批源码/测试/原始日志的 Mac 本地 commit `e7ca600aa19bc0ee6b0eb9e58e06073c7160c565`，Git Tree `4d791b214b735da3d38aef23502d04a1cbe4a42e`。本报告在后续独立提交中补入。
- 主工作树既有未提交文件完全不动。Mac 本 worktree 跑全量回归后产生的 `evaluations/results/2026-10-15-policy-and-retrieval.json` 与 `evaluations/results/2026-10-15-v05-retrieval.json` 改动保持未提交，不混入本批。

## K00 官方来源核查与范围候选

- 印刷第 **19页（函数）** 与 **56页（概率统计/拓展）**：合计 **54条 PDFKit 来源文本行**，分配到 **28个连续、不重叠的结构段**，并核实与 19→20、56→57 的跨页关系。
- 形成 **20项来源行与页指纹锁定的原创课程要求候选**，其中5项是教学/结构主题，不冒充数学定理；15项具有**有限精确数值或符号正例及不当泛化拒绝证据**。
- 按 `COMPULSORY` / `ELECTIVE_A` 来源提示分类并保留扩展与工程旧 ID 之间的不同口径。**它们不是20个正式官方课程原子**。
- 机器可审计7轨名称：必修、选择性必修、选修 A/B/C/D/E；**7轨官方知识原子分母仍全部 UNKNOWN**，教师认证完整逐页原子化仍为0/61页。禁止用20个候选、441份工程文档或113条旧映射伪造覆盖率。
- 证据：`docs/evaluation/KB_BATCH109_SCOPE.json`、`KB_BATCH109_SCOPE.md`；可复建器 `scripts/build_kb_batch109_scope.py`，来源作者数据单独保存。

## K01/K02/K04/K06/K07/K08/K09 实际增量

- 原创完整结构候审 `DeepLesson` **10份**（3定理、4概念、3方法），覆盖：函数定义域/值域与单值映射、三种表征、分段函数、严格递增端点最值、奇偶函数、周期函数、连续均匀分布、正态标准化、联合/边缘分布、独立性与零协方差的区别。
- 新增**20道分步教师例题、30级不剧透提示、20项近远迁移任务、10个反例、12条候审证明步骤、6条候审先修 ID 边**。
- 所有知识 `REVIEW_PENDING / TEACHER_ONLY`，未经教师真实签署不变为 `APPROVED`；学生独立挑战/权威检索不能访问教师完整答案。例题/有限 SymPy 校验不等于一般定理被形式证明。
- 数学关键负例：不对称定义域下的奇偶性、一个输入多个输出、分段定义端点重叠、局部单调错误外推、误将零平移视作正周期、均匀密度在 a=b 处除零、正态 N(μ,σ²) 混淆方差与标准差、联合与边缘概率直接相乘、协方差为零却非独立。
- K01/K09修复历史 Batch108 产物构建器将未来Batch109文件纳入历史冻结分母导致的漂移；源行重复/错轨、伪教师审批、条件擦除、伪造七轨知识原子、无证据发布等均新增负面回归；GitHub CI 和 `mac_check.sh` 增加本批重建门禁。
- 候审完整讲义 `knowledge/deep/v1/batch109_function_probability.json`、可复建作者数据及 `KB_BATCH109_LESSONS_AUDIT.json`。

## Mac 实测记录（不重复计算专项）

| 验证 | 已观测结果 |
|---|---|
| `bash scripts/mac_check.sh` | **exit 0** |
| Python全量pytest | **65,108 passed; 5 skipped; 1 third-party deprecation warning; 0 failed**（799.84秒） |
| Node test | **111/111 passed** |
| Batch109三文件专项重测 | **192 passed**（已包含于全量Python） |
| Chrome/Playwright | mac_check 浏览器模拟套件通过：6项传输检查、9项iPad交互模拟等 |
| 浏览器pytest | **2 passed**，浏览器日志退出码0 |
| 源PDF页/证据一致性 | 来源复建器 `--check --verify-local-source` PASS |
| 讲义机器字段/索引一致性 | `--check` PASS |
| 真实教师审核/普适证明认证 | **0 / 0**，不能用测试通过代替 |

保留第一次失败运行的原始日志：Batch108构建器将后继新增候审讲义纳入历史快照，导致 `KB_BATCH108_LESSONS_AUDIT.json` 漂移；修复后重新执行全量并成功。这个失败不是模型数学推理或课程知识错误，但历史统计冻结是必要安全门禁。

完整原始证据及 SHA-256：
- `docs/evaluation/logs/KB_BATCH109_MAC_CHECK_FINAL.log` — `7decdde582940d7502babc12993205d05e4d44f3badca31b9be95fb48b47e97d`
- `docs/evaluation/logs/KB_BATCH109_MAC_CHECK_FIRST_FAIL.log` — `a2dac19d766ba35bb4e387afddf92e8e3eaf786ef54cffbd674b76206a191f63`
- `docs/evaluation/logs/KB_BATCH109_MAC_BROWSER_FINAL.log` — `664a6eefc78287318f837c42e3941692ed40207e4d803e3bdbed7d719a60c390`

## 未完成及真实依赖

- **官方7轨正式分母 UNKNOWN、0/61页获教师完整原子化核验**。新增课标要求只是编辑候选。
- **74项**临时工程主题还缺成对比较；**172条**旧文本先修标签待语义审核；**538条**历史证明步骤未认证，另加本批12条新候审证明步骤；**10项**数学冲突待裁决。
- 工程候审深度文件数达到441，**不是**教师审校通过的完整课程原子数量；教师通过0、正式学生权威发布0。
- 待 GitHub 远端CI独立验收，不能把 Mac pass 冒充 GitHub pass。

## 下一大批

1. **K00/K01**：课标印刷20/57页跨页继续逐行提取来源/教学段/候审原子，先补真正七轨模块与原子级分母及缺口，区别选学、必修、选修。
2. **K07**：优先审查538历史证明步骤中的高风险前提、10项冲突，并加入严谨不当逆推、零除与定义域反例。
3. **K02–K06**：按K00缺口继续建设高频函数、概率统计、计数、建模的完整课程内容及题族，扩大机器可审计知识语义覆盖。
4. **K08/K09**：教师候审的检索必须拒绝权威发布、学生提示不能泄露教师答案；待真实教师审校后才允许逐章放行，独立测试需持续记录。
