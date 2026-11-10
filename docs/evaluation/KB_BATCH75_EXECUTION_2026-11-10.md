# STEM Mentor｜Batch75 Mac 真实执行与验收报告（2026-11-10）

## 源码基线及环境
GitHub 仓库 YOUessi/stem-mentor；基于 Draft PR #99 Batch74 的已核实源码提交 a54e27464101bdffc4e2043a1bea4591783e2539。
唯一代码和内容生产、测试设备为授权 MacBook Air YOUTangdeMacBook-Air.local，独立 worktree 为 ~/Documents/文件/stem-mentor-kb-batch75，开发分支 feat/kb-batch75-clause-atom-splits。Mac 主仓既有11项未提交修改保持不变；未使用 Tang，未使用模型 API，未上传任何学生数据或版权课标全文。
课程标准基线《普通高中数学课程标准（2017年版2020年修订）》，原PDF SHA-256 cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195。

## K00 × K01：22段课程来源实质细拆
从 Batch74 已分诊56个非锚定区间中筛选11个混合区间和11个实质性未编号区间，全部逐项检查并细分。固定Mac PDFKit源文本子片段的页码、行范围、SHA、父区间SHA、课程轨道，以及原创项目编辑注释，输出60个可审计编辑组件，组成：26个知识候选、14个范围声明、8个课程结构、7个能力教学目标、4个已存在定理草案的指向、1个星号选学提示。课时表不能当知识原子，第29页四项立体几何定理只与Batch74旧草案关联而不重复认证。候选允许共享原文行，绝不是60个官方知识原子。

这60个组件轨道提示：必修17、选择性必修8、选修A10、选修B16、选修C6、选修D3；这22个区间里没有选修E组件，不代表选修E官方范围或知识原子数为0。选修E需要学校实际开课方案。七轨官方完整原子分母全部未知 null。全页教师完整原子化审核仍0/61。

源码和产物：scripts/build_kb_batch75_clause_splits.py；curriculum/highschool_math/k00_batch75_subspan_mac_witness.json；docs/evaluation/KB_BATCH75_EDITORIAL_SUBCLAUSE_MATRIX.json 和同名 md。真实Mac --verify-local-source 和 --check 均通过；CI只复验固定指纹，不声称访问Mac原PDF。

## K02–K06：八篇跨主题原创教师草案
新增必修逻辑充分必要条件、必修样本均值与总体推断、选择性必修条件概率、选修A均匀连续分布、选修B偏导数、选修B三阶线性方程组、选修C逆否命题、选修D轴对称等8篇原创数学教学草案，带明确论域、定义/陈述、符号、适用前提、合法推导、反例、错误解法、两道含解答的例题、三级提示及近远迁移。
合计8篇、16个原创已解例题、32个有说明的分步论证、8个反例错因、24条提示、16个近远迁移任务。对应知识/editorial review JSON 及 docs/evaluation/KB_BATCH75_CROSS_TRACK_MATH.md。
所有内容 REVIEW_PENDING、TEACHER_ONLY、NOT_FORMALLY_CERTIFIED，不作自动教师批准，不进入学生正式知识索引。

## K07 × K08 × K09：数学有限验证及防泄漏
新建8类严格受控有限实例运算，使用Python Fraction精确算术；3x3克拉默法则样例用独立SymPy逆矩阵交叉检查，命题逻辑用4行完全真值表复核；条件概率必须有非零分母，交事件概率受上界约束，连续均匀密度有非退化支撑范围，偏导必须保持变量固定；禁止奇异矩阵、错误矩阵维度、非精确浮点、伪造教师签核及未批准答案发布。
八份草案在带已批准样例的真实学生索引混合检索中进行了各自的非泄漏测试；无完整教师解答、分步论证误泄漏。所有有限实例验证都不等于一般定理形式化认证，也不认证学生自由文本步骤。
新增 backend/tests/test_kb_batch75_clause_and_cross_track.py，并在 scripts/mac_check.sh 和 .github/workflows/ci.yml 接入两项内容完整性检查。

## 真实Mac完整测试
专测：167 passed，0 failed，0 skipped，开启 KB75_VERIFY_MAC_SOURCE=1，特殊源片段SHA校验通过。
Python全量：47897 passed，4 skipped，0 failed，1条第三方依赖弃用警告；包含上述专项，不重复相加，耗时281.63秒。
Node：111/111 passed；模拟Tutor策略33/33；RAG困难负例40/40；Top3=22/22。
浏览器：15个Chrome/Playwright脚本通过；browser pytest 2 passed；使用离线临时合成数据。
原始日志与退出码位于 evaluations/results/2026-11-10-kb-batch75/，specialized_mac.exit、mac_check.exit、mac_browser_check.exit 均为0。

## 实际失败及修复
开发初期第46页来源子片段划到父区间以外(8至15行，合法至13行)，来源边界门禁拒绝；修正为8至13行并在Mac原件上重新取SHA。
初次教材草案引用输出轨道用了错误字段 curriculum_track_hint；改为真实字段 track_hint。
短标题和数学论证的初版通用字符串阈值过严，对字段设置合理独立验收并写明偏导例题主体。
新增负例时曾发生pytest重复参数装饰器导致收集失败，删除重复装饰器并重跑167专项及全量回归。
上述开发阶段错误均已修复，未作为最终成功记录，最终通过日志可重放。

## 最终缺口与下一批
真实教师批准0，学生正式深度发布0；61页教师完整原子化0页；七轨官方完整知识原子分母全null；历史538条未形式认证证明步骤与10个未裁决历史冲突继续开放。
下一批要审核选修A/B微积分与统计的跨页重叠及数学等价关系，补齐课程原子分母的教师可审证据；对真正缺失的数学原子扩充严谨原创讲义和题族、逐步检查假设，继续处理历史证明债务与冲突。不能因为本批60候选或8草案就宣称课程正式覆盖；不自动关闭#17–#27。
GitHub正式PR、commit与CI以最终远端记录为事实源。