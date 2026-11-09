# STEM Mentor｜Batch60 Mac 执行与验收记录（2026-11-09）

## 运行边界与基线

- 唯一开发/内容生产环境：授权的 MacBook Air，独立 worktree `~/Documents/文件/stem-mentor-kb-batch60`，分支 `feat/kb-batch60-elective-source-audit`，直接基于 Batch59 Draft PR #84 的 `92ea2483135ca60e1c923e833222aaa1d3d523a7`。未在 Tang 开发、未合并或覆盖 main；Mac 主仓原有 11 项未提交修改保持隔离。
- GitHub Issues #17–#27 全部保持 Open；此前 #84 为 Draft PR。完整官方分母、教师审校、正式发布与真实模型 API 均仍未完成。
- 原 PDF 仅在 Mac 读取：`/private/tmp/stem-mentor-official-math-2020-batch51.pdf`，固定 SHA256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。不得上传原 PDF、课标全文、扫描件或真实学生数据。

## K00 / K01：补齐此前未做局部来源定位的25页，但不冒充正式原子化

- 新增原创课标要求释义与**106条带PDFKit页/行、页哈希、片段哈希的非去重来源定位**，覆盖印刷第13–14、51–73页（25页）：必修5条；选修总范围3条；A27、B29、C21、D18、E3条。
- 类型：数学内容69、课程范围与政策16、轨道边界5、课程表3、教学指导7、活动3、考核相关1、学校定义选修范围2。
- 承接Batch56–59既有238条**非去重来源线索**，累计344条。此前部分定位36/61页，本批覆盖剩余25页，现为**61/61页具备至少一条局部来源定位**。但**完整全页教师原子化仍为0/61**，跨页等价及编号/未编号要求的最终拆分仍PENDING。
- 《普通高中数学课程标准（2017年版2020年修订）》的正式七轨知识原子分母**仍全部为null**；不能把344条部分指针、313条工程候选或课时表当作官方分母。E类由学校自行开发/选择，并非全国统一固定必授原子清单。
- 本批另识别**11条教学/活动/考核来源线索**，单独记录为UNMAPPED，不把非知识原子要求从能力验收中隐藏；与历史队列需进一步数学与能力等价去重，不可简单相加当唯一能力分母。
- 新增机器可重放生成器 `scripts/build_kb_batch60_elective_source_review.py`，版本化TSV、片段SHA快照、JSON覆盖报告及Markdown。Mac `--verify-source-pdf`逐页重读61页PDFKit SHA和106个片段SHA；CI因版权原件不随仓库分发，仅检查已版本化哈希、输入完整度及生成产物一致性。
- 严格拒绝轨道边界跨越、E课程伪固定全国必修范围、假教师审核、重复源位置、缺失原件/篡改指纹；全部记录仍为 `REVIEW_PENDING`、无正式证明及无学生正式发布。

## K07：14类受控精确数学验证

- `backend/app/kb_batch60_elective_math_guards.py`使用Python精确整数与`Fraction`，分别验证：针对1/n数列ε–N尾部见证、3×3克拉默计算、三维向量叉积、均匀分布区间概率、伯努利比例极大似然、样本t统计量平方、带两个自变量的最小二乘、离散复利、整数指数Cobb–Douglas模型、正数据调和平均、Logistic odds到概率、轴反射距离、单循环赛场次、带纳入概率的调查加权总量。
- 负例包括ε严格不等号/非法N、奇异矩阵、样本零方差、共线回归设计、无效连续分布区间、利率=-1、非正投入、零值调和平均、非法概率、错误赛事队数、样本纳入概率为0、浮点/布尔混入以及伪教师审核字段。
- 每类只返回`FINITE_EXACT_CASE_ONLY / NOT_FORMAL_GENERAL_PROOF`，不验证任意学生自由证明，不提升为课程定理证明或教师批准。真实教师批准0、学生深度正式发布0；历史538条尚未形式认证的证明步骤及10项未裁决冲突继续开放。

## K09：真实Mac验收、失败与修复

- 首次新worktree增量测试发现没有`.venv/bin/python`，运行返回127（非数学内容错误）；从同一授权Mac的Batch59已验证虚拟环境创建**仅本worktree使用的本地符号链接**后运行成功。该环境链接不进入Git版本。
- `PYTHONPATH=backend:. .venv/bin/python -m pytest -q backend/tests/test_kb_batch60_elective_source_and_math.py`：**195 passed，0 failed**，日志 `evaluations/results/2026-11-09-kb-batch60/incremental.log`。
- `python3 scripts/build_kb_batch60_elective_source_review.py --attest --write --verify-source-pdf /private/tmp/stem-mentor-official-math-2020-batch51.pdf`：本地原PDF SHA、61页PDFKit以及106段位置的哈希校验成功。
- Mac全量检查：****EXIT=0；Python 44,207 passed、0 failed、1 条第三方弃用警告（已含195专项），Node 111/111、Tutor 33/33、RAG hard negatives 40/40、Top3 22/22****。日志 `evaluations/results/2026-11-09-kb-batch60/mac_check.log`及`mac_check.exit`。
- 浏览器检查：****EXIT=0；Chrome/Playwright 15个独立脚本通过，浏览器pytest 2 passed、0 failed****。日志 `mac_browser.log`及`mac_browser.exit`；Chrome仅合成数据及CDP模拟，不代表实体iPad硬件测评。
- `scripts/mac_check.sh`与`.github/workflows/ci.yml`均新增Batch60可重放生成门禁；本批195专项为Python全量的一部分，不得双重累计。
- 本批**不虚报新增完整教学讲义**；该批贡献是原版课标在余下25页的局部来源定位及数学条件工具。混合签名RAG测试继承Batch58已有回归，真实API与教师审批依然未满足发布门槛。

## GitHub事实与下一批

- 本批代码/报告提交与Draft PR：****首个源码提交** `1029cf245e43fef5e13a5881443919b4762ec4dd`，已通过 Mac SSH 非强推同步至 GitHub 分支并创建 **Draft PR #85**（https://github.com/YOUessi/stem-mentor/pull/85）。**本报告/日志的最终HEAD及CI需后续独立远端核实。****。PR必须维持Draft；CI以远端真实结果为准。
- K00后续最优先：原版61页**逐页完整拆分**编号与未编号内容、表格图像复核（尤其第35页乱码图示）、跨页数学等价去重和A–E轨道审查，然后按实际证据建立官方可审计分母；**不得用61/61局部定位冒充全页审查完成**。
- K01/K06/K07：完成原有538证明步骤的逐步前提核查与10冲突裁决，按实际缺口成批修补原创讲义与题族，逐项保留教师签字状态。
- K08/K09：完成真实审核人签名发布、混合获批/未批检索撤销及生产模型API的冻结对照；记录引用、数学可靠性、拒答、P95、成本和教师审核范围。未满足正式课程覆盖、教师审校及学生安全发布前不得停止知识库续建。
