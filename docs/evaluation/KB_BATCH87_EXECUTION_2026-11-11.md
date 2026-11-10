# STEM Mentor｜Batch87：90个课程来源补全 + 七轨300候选审计 + 七份跨域数学原创建设（2026-11-11）

## 工作环境、来源与正式权限

仅在授权MacBook Air独立工作树 ~/Documents/文件/stem-mentor-kb-batch87 开发和测试，分支 feat/kb-batch87-anchor-completion，基线Batch86 SHA b152628d43029c8c068899ac7675c723a5ea63fc（PR #111，Draft）。Mac主仓11项既存未提交变更不修改；不使用Tang、不合并或强推main。

先读取GitHub总任务#17和全部子任务#18–#27（11个均Open）。原始课标为教育部《普通高中数学课程标准（2017年版2020年修订）》，Mac原始PDF SHA256 cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195。原始PDF和有版权的标准段落不上传GitHub；在Mac使用PDFKit原始页、行SHA核验。GitHub CI没有课标原PDF，不得伪称云端做过原PDF逐行复核。

审核与权限：全部新增内容 REVIEW_PENDING、TEACHER_ONLY、NOT_FORMALLY_VERIFIED；教师批准0、一般定理形式认证0、自由学生步骤认证0、正式学生发布0。只有独立教师真实审校后才可考虑审核状态提升。

## K00/K01：90项原创数学来源语义解释，所有428个锚点已有草案

本批新写必修43、选择性必修19、选修A11、选修B17，共90个有具体数学语义及风险边界的原创锚点。项目来源锚点的项目级释义由338/428增加至428/428。七轨来源锚点分母：必修142、选择性必修101、选修A69、选修B70、选修C29、选修D17、选修E0。

在428个已解释锚点中，187个属于数学要求、155个课程标题、33个应用语境、30个混合条款、23个能力目标。来源仅能形成300个未裁决语义等价的数学候选标签：必修75、选择性必修66、选修A60、选修B60、选修C31、选修D8、选修E0。300标签仅是待教师拆分的项目内部主题，逐字标签不重复不等于数学语义互异，课程章节标题/能力要求也不能当作定义或定理。

注意：428不是官方数学知识原子分母，300也不是官方数学知识原子分母！七轨经过逐章跨页数学审核的正式原子分母仍全为未知/null；真实教师全页原子化审查仍为0/61页。选修E目前没有本项目已识别锚点，不代表其官方知识内容为零。

新增原创来源及确定性审查文件：
- scripts/author_kb_batch87_source.py、curriculum/highschool_math/kb_batch87_semantic_authoring.json。
- scripts/build_kb_batch87_semantic_review.py、docs/evaluation/KB_BATCH87_SEMANTIC_COVERAGE.json 和 .md。
- scripts/build_kb_batch87_candidate_census.py、docs/evaluation/KB_BATCH87_PROVISIONAL_ATOM_CENSUS.json 和 .md。
以上覆盖保持来源页行SHA、课程归属、版本、未审核标记及正式课标分母未知状态。

## K02–K06：七个跨主题完整教师侧数学单元草案

| ID | 新增原创教学内容 | 主要不可忽略前提 |
|---|---|---|
| KB87-M01 | 古典概型和有限等可能样本点 | 不等概率不能直接用个数比 |
| KB87-M02 | 分层总体均值加权合成 | 不等权层不能简单平均 |
| KB87-M03 | 超几何无放回概率及均值 | 有放回不适用 |
| KB87-M04 | 皮尔逊样本相关系数 | 任一方差为0时r未定义 |
| KB87-M05 | 二解释变量OLS最小二乘 | 设计矩阵列不满秩时系数不唯一 |
| KB87-M06 | 理想抛体参数曲线斜率 | 水平速度为0不能除以dx/dt |
| KB87-M07 | 2×2列联表的卡方统计量 | 零边际或小期望频数不可忽略 |

每个单元都有正式定义及符号、适用假设、4步有依据的推导、反例/错误方法、2道完整教师侧原创解答、三级非剧透提示及近远迁移。共7份讲义、14道教师例题、28段论证、7类失效边界、21条分级提示与14项迁移。
相关文件：scripts/author_kb_batch87_lessons.py、knowledge/editorial_review/kb_batch87_guarded_math_authoring.json、scripts/build_kb_batch87_math_lessons.py、knowledge/editorial_review/kb_batch87_guarded_math_teacher_drafts.json、docs/evaluation/KB_BATCH87_GUARDED_MATH_LESSONS.md。

## K07：七个条件限定的精确计算验收

新代码 backend/app/kb_batch87_exact_oracles.py 给出7个正向有限见证及7个非法前提拒绝：
1. 有限公平六面骰奇数事件概率 1/2；未核实等概率拒绝。
2. 两层人口80/20、层均值10/30，加权总体均值14；零人数层拒绝。
3. 超几何N=8,K=3,n=2,k=1，概率15/28；n>N拒绝。
4. 成对样本(1,2,3)、(2,4,6)的皮尔逊r=1；常数变量拒绝。
5. 满秩二元解释变量OLS唯一系数(1,2,3)；完全共线拒绝。
6. 抛体vx=2,v0=10,g=2,t=3时斜率2；vx=0拒绝。
7. 2×2列联表[[12,8],[6,14]]的χ²=40/11；零边际拒绝。
独立SymPy与有理数检查验证指定算例，未知操作显式UNSUPPORTED。有限算例不等于定理普适证明，不认证统计模型本身、真实教师批准或学生自由文本答案。

历史538条自然语言证明步骤仍未一般形式认证；独立P0源步骤已关联审稿材料64/182、仍缺118；10组数学冲突未裁决。不得将本批7份来源链接讲义当作新增7项P0审稿卡或形式认证。

## K08/K09：机器门禁、非空学生检索防泄漏

新增 backend/tests/test_kb_batch87_source_and_lessons.py：对90来源锚点逐行核验SHA、轨道、数学单元与角色；利用大量参数化负例拒绝伪教师签名、非法学生发布、课程分母篡改、重复来源、数学前提遗漏。对7教师单元逐份做内容字段、条件验证、正负例、改写篡改测试。
对非空合成批准索引实际测试学生检索不能直接取到未批准单元的教师答案和证明文本；同时检测300个临时数学标签不能冒充正式知识原子总数。

更新 scripts/mac_check.sh 与 .github/workflows/ci.yml：新增3个batch87生成器的冻结输出检查。Mac检查另强制原始PDFKit来源逐行SHA比对；GitHub CI不要求上传版权原PDF。

## 测试与远端交付证据

本批最初专项：**1,097 passed / 0 failed**（93.56秒）；在候选分母与非法前提测试扩展后，同一Mac重新执行专项：**1,100 passed / 0 failed**（87.15秒）。专项测试包含于全量Python，不能重复累计。

Mac冻结源码全量执行 **60,813 passed / 5 skipped / 0 failed / 1 第三方弃用警告**（810.08秒）；Tutor策略 **33/33**；RAG困难负例 **40/40**、Top3 **22/22**、contract_valid=True；Node **111/111**；独立Google Chrome/Playwright **15项脚本成功**，额外浏览器pytest **2 passed**。`mac_full_check.exit`、`mac_browser.exit`、`mac_specialty_final.exit` 都为 **0**。浏览器测试使用临时合成数据库，没有宣称真机iPad覆盖。

全部原始日志和退出码：`evaluations/results/2026-11-11-kb-batch87/`。本轮不是教师审核，机器算例未升级为一般形式证明。

本批Mac源码提交SHA、GitHub Draft PR、最终远端Tree与GitHub Actions完成后，在下方追加实际核实信息；若推送/CI受阻则明确记录，不以本地测试替代远端CI。

## 下一批

首先把300个待裁决数学主题逐章、跨页、跨轨拆分与数学语义等价对照，识别能力要求/数学知识/活动要求、完成正式分母的可审核草案，继续明确未知/缺失；不得拿来源解释完毕当作课程建设完成。继续扩大真正高质量课程讲义与题族，按独立历史来源审查118个未关联P0步骤、538历史证明及10组冲突。教师真实签核、学生提示权限验证、条件论证均完成之前，不发布、不开启正式学生权威内容，也不关闭主任务#17–#27及持续续建任务。

### 最终格式一致性与源码冻结专项复验
发布前检测到两份自动生成Markdown存在末尾多余空行（git diff --check拒绝），修复其两个生成器的最终换行规范，并重新生成确定性内容。这是排版修正，不改变任何数学陈述或测试输入。修正后在Mac重新执行Batch87专项 **1,100 passed / 0 failed（147.82秒）**，日志 `mac_specialty_release.log`、退出码 `mac_specialty_release.exit=0`。先前 60,813 项Python全量、Node、Tutor与Chrome验收是在排版修正前运行；除此两份Markdown排版没有代码或内容变化，最终 GitHub CI 必须作为新提交的独立全量验收。
