# STEM Mentor｜Batch107 课标来源、10份数学深度讲义与严格门禁执行报告

> 所有新内容均为原创 `REVIEW_PENDING / TEACHER_ONLY`，无教师正式审核通过，无学生权威发布。来源候选、有限数学实例及工程草案均不等于官方已批准课程原子。

## 一、事实源与Mac独立工作树

- 唯一开发、内容生产和实际测试环境：MacBook Air `YOUTangdeMacBook-Air.local`，独立worktree `~/Documents/文件/stem-mentor-kb-batch107`；未在Tang开发、未改写主分支。
- GitHub Draft PR [#132](https://github.com/YOUessi/stem-mentor/pull/132)，源分支 `feat/kb-batch107-official-17-54-lessons`；堆叠在 Batch106 的 PR #131（父HEAD `8773d08d6d940c175220aff691a399ef0da7bb7c`），非main。
- Mac最终数学修复后源码提交：`f33816c20b6ee4c57bea4aff5fc3c00a38e825ce`；同树GitHub原生非强推提交 `22040838d50985d20049efbfacc47fec02974f4c`；经过Git核实两者的源码Tree均为 `bd0f1bad8cd3a19b63463bcde7a1004045ea98da`。commit SHA不同仅因祖先提交对象不同。
- Mac主仓既有11项未提交修改没有触碰；另有两份由旧评测自动生成的历史快照修改未纳入提交。
- 来源基线：教育部《普通高中数学课程标准（2017年版2020年修订）》，Mac原PDF SHA256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。不提交课标PDF或版权教材全文。

## 二、K00/K01：课标行级来源与可重建审核

- 本批校核印刷页17（必修）和54（选修A），各27条PDFKit原文行，共54行、16个连续无重复无遗漏来源结构区段；保留16→17及53→54两个跨页关联。
- **23条原创候审要求解释**：COMPULSORY 11条、ELECTIVE_A 12条，保留来源页行锁、精确摘要、数学前提、不当推广与有限正反见证。未把23当作23个教师批准原子。
- `scripts/build_kb_batch107_source.py` 严格拒绝非法来源范围、重复oracle、页行漂移、缺行/重叠区段、伪官方ID、伪教师批准、跨轨污染；`--check`校验源码生成的JSON/Markdown证据矩阵。
- 对Batch106历史构建器加入截至该批次的稿件过滤，后续新增讲义不会悄然改变已经冻结的历史报告分母。
- 官方七轨课程知识原子分母**全部UNKNOWN**；正式教师逐页完整原子化**0/61页**。

## 三、K02–K06：实质性教学内容与防剧透

- **10份原创新讲义**（4定理、3概念、3方法）：二次方程判别式、二次不等式分类、函数零点的对象类型、元素和单元素集合、三维外积、非零向量正交投影、三维三向量线性相关、正交矩阵保内积/长度、曲线夹域非负面积、矩阵乘法维度及非交换性。
- 各份提供前提、正确陈述、逐步证明（仅定理）或合法性解释、条件失效反例、错误推理与修复、符号定义、2个分步教师例题、3级分层提示以及近远迁移。合计20例题、30条提示、20条近远迁移任务、5条候审ID先修链接。
- 工程候审深度文档为**411旧+10新=421份**，不等于421个官方原子或421份教师通过讲义。`student_evidence_lookup`拒绝这些未批准内容，教师完整解答不会泄露给学生独立挑战。

## 四、K07：数学前提修复和拒绝回归

- 23个不同的来源候选分别执行有限精确／SymPy见证及非法泛化拒绝；10份讲义引用其中对应的10个键。有限验证不能认定为全称定理形式证明，也不代表未见学生自由步骤已验证。
- **实质数学错误修复**：原三维叉积证明在 `u=0, v≠0` 情况错误使用 `v=ku`。现在先单独处理零首向量，再对非零u的线性相关情形使用标量倍数论证，附零向量边界精确回归。
- **实际回归故障**：首次专项227项中16项失败：重复oracle负测在触发重复键错误前被来源行锁截断，导致期望拒绝原因不符。新增全局键唯一性预检并复测，最终**227 passed**。
- 首次全量验证还因Batch106历史工件受后续稿件增量影响而报漂移；修复后全量通过，随后补充上述零向量证明修复，并完成最终全量复测，退出码为0。

## 五、Mac真实验收

- 修复后最终 `scripts/mac_check.sh`：**64705 passed / 5 skipped / 1 warning / 0 failed**，整套退出码 **0**，耗时 **678.56 s**。Node **111/111 passed**，本批专项 **227 passed**（包含在Python全量，不重复累加）。
- Mac Chrome/Playwright多视口、数值和离线检查通过；浏览器pytest **2 passed**，不冒充真实物理iPad。没有真实模型API/GPU调用。
- 来源PDF/PDFKit SHA、两套Batch107构建器`--check`、Schema与学生端拒绝回归真实执行。GitHub源码修复提交的CI [#43160575911](https://github.com/YOUessi/stem-mentor/actions/runs/43160575911) 经独立核实为 **success**；新增此报告的证据提交仍须以后续远端CI实际状态为准。

### 原始测试日志与SHA-256

| 原始日志 | SHA-256 | 文件大小（bytes） |
|---|---|---:|
| [`KB_BATCH107_MAC_BROWSER_FINAL.log`](logs/KB_BATCH107_MAC_BROWSER_FINAL.log) | `0757d973bc7f4dd25401cb95cf88e9d5b6a0622e50deb03bc139b5dcbb026242` | 2443 |
| [`KB_BATCH107_MAC_CHECK_FINAL.log`](logs/KB_BATCH107_MAC_CHECK_FINAL.log) | `afec5ff488f65fe355e45e19bfa46477242bab551a4737b345342e0bf0794246` | 112164 |
| [`KB_BATCH107_MAC_CHECK_FIRST_FAIL.log`](logs/KB_BATCH107_MAC_CHECK_FIRST_FAIL.log) | `70c3f1ac8489e3283ff22332712900ce7d16092ca90bf6b24804ec685db22711` | 18781 |
| [`KB_BATCH107_MAC_CHECK_PRE_MATH_FIX.log`](logs/KB_BATCH107_MAC_CHECK_PRE_MATH_FIX.log) | `c50c5374dc281b0bf849d5b321fe39705d7309af8a80fe0d08cf0b2338ebd862` | 112159 |
| [`KB_BATCH107_MAC_FOCUSED_FINAL.log`](logs/KB_BATCH107_MAC_FOCUSED_FINAL.log) | `830fca82645e7bb74984736580a592d8f570e1a2e4220a8c092e9e575efe724b` | 340 |
| [`KB_BATCH107_MAC_FOCUSED_FIRST_FAIL.log`](logs/KB_BATCH107_MAC_FOCUSED_FIRST_FAIL.log) | `e5bd36e7862c0773b452414235483beb1200c408211e581d07973346721619c9` | 29340 |

## 六、剩余门槛与下一整批

- 74项工程临时主题未完成成对比较，172条历史文本先修关系未验证，538条历史证明步骤未认证，10项数学冲突待裁决；K00官方七轨分母未建立、教师完整页原子化0/61，教师批准0、学生权威发布0。
- Batch108继续官方来源印刷页18、55的跨页锁与正式课程原子候选，批量建立可审计分母，优先处理证明前提/先修依赖的高风险案例，同时生成跨主题完整题族与审校、检索负例，不以工程文档数量冒充课标覆盖。
- PR继续保持 Draft；只有全部领域官方范围、形式/条件门禁、教师审核与学生端集成分别达标才可考虑关闭总任务。
