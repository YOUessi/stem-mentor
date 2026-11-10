# STEM Mentor｜Batch83 课标语义复核与数学边界审查（2026-11-10）

## 环境与前置核验

唯一开发和测试环境：授权 MacBook Air。独立工作树：~/Documents/文件/stem-mentor-kb-batch83，分支 feat/kb-batch83-syllabus-math-triage，基于 Batch82 本地后续提交 b2ffeaf6b8b3ab394419d3574318bda6ebf1e90c。Mac主仓11项未提交修改不覆盖，不用Tang，不合并或强推main。先查阅GitHub #17–#27及最近PR #105–#107，确认所有终验门槛仍未达成。

授权课标：《普通高中数学课程标准（2017年版2020年修订）》。仅在Mac以原PDF与PDFKit文本验证来源SHA、页号、行号；只提交原创编辑解释，不提交课标原文复制段落。

## K00｜新增60份课标来源行原创语义审查

基于冻结428个来源锚点和前批42个审核草案，新增必修/选择性必修/选修A/B/C/D各10份来源语义编辑稿；累计102/428，剩余326个未作原创逐行语义分析。60份新增按内容性质分为24个章节标题、16个数学要求、7个混合条款、9个应用情境和4个能力要求，提出45个**未去重、未认证**的数学主题候选。

| 轨道 | 来源锚点 | 累计编辑解释 | 待逐行编辑 |
|---|---:|---:|---:|
| 必修 | 142 | 17 | 125 |
| 选择性必修 | 101 | 17 | 84 |
| 选修A | 69 | 17 | 52 |
| 选修B | 70 | 17 | 53 |
| 选修C | 29 | 17 | 12 |
| 选修D | 17 | 17 | 0 |
| 选修E | 0 | 0 | 0（无独立来源证据，不等于课程内容完成） |
| **合计** | **428** | **102** | **326** |

各行绑定原始SHA、课标页和行号、结构类型、原创语义说明、可能的数学拆分及失效条件。集合运算要保留全集条件；充分和必要条件不得颠倒箭头；等比求和要处理公比为一；连续、可导、介值、二分、原函数与微分公式均保留不同条件；选修C统计拟合不能解释为因果；选修D均为数学文化/应用专题标题，不计为10条定理。

**重要：428条是课标来源行审核义务而非官方原子分母，102份不是102篇讲义；七轨官方原子分母全部仍是未知。教师完整逐页原子化0/61、真人批准0、学生正式发布0。**

## K01｜结构和审核负面门禁

新增源数据文件：
curriculum/highschool_math/kb_batch83_semantic_authoring.json
以及生成器：
scripts/build_kb_batch83_semantic_coverage.py

仅允许新分配的60个来源行（六轨各10），不得重算此前42个；源ID、轨道、页/行SHA、PDFKit页SHA必须一致。强制章节标题不得冒充数学内容；禁止失去前提解释、无效或重复候选、教师认证伪造、学生可见性伪造、额外隐藏审核字段、把官方原子数设置为0或1。所有结果维持 REVIEW_PENDING、NOT_FORMALLY_VERIFIED、student_publishable=false。

由生成器生成 docs/evaluation/KB_BATCH83_SEMANTIC_COVERAGE.json 和 .md，以及七轨来源完成矩阵。Mac完整校验核对授权来源，GitHub CI无需分发本地PDF，仅执行确定性一致性检查。

## K07｜五组有理数精确数学区分证据

新增 backend/app/kb_batch83_math_relations.py：只用Fraction精确计算。backend/tests/test_kb_batch83_semantic_coverage.py 另以SymPy进行独立复算。结果都只叫有限条件见证，不是一般定理形式证明。

| 对照 | 正反例/数学边界 |
|---|---|
| 必要条件与极值 | f(x)=x³在0导数为零，却有f(-1)<f(0)<f(1)，故0不是极值。 |
| 等比模型与回归模型 | 数据1、3、5形成精确线性趋势，但相邻项比例3和5/3不同。 |
| 连续性与可导性 | 绝对值函数在0连续，左右差商分别是-1与1。 |
| 微分与有限增量 | f(x)=x²、x=1、h=1/2，微分为1，真实函数增量5/4，余项1/4。 |
| 定积分与几何面积 | 常值-1在[0,1]上的符号积分为-1，无符号面积为1。 |

十组历史数学冲突仍不裁决，538历史证明步骤未形式认证，182项P0中仍有134项无审查卡。不得把模型生成、精确算例和真人教师认证混同。

## K08/K09｜自动化回归与追溯

新增729项Batch83专项测试（均通过，包含在Python全量回归内），覆盖60条来源溯源与逐项反面审核状态、防跨轨污染、内容降级、结构误判及SymPy数学独立交叉检查。新增生成器一致性检查到scripts/mac_check.sh和.github/workflows/ci.yml。真实原始日志在 evaluations/results/2026-11-10-kb-batch83/，包含专项、全量Mac、浏览器各自.log及.exit。

测试脚本：bash scripts/mac_check.sh；bash scripts/mac_browser_check.sh。
**Mac实测结果（仅本批实际运行）**：Batch83专项729 passed/0 failed；Python全量 **56,794 passed、5 skipped、0 failed、1个第三方warning**；Node测试 **111/111 passed**；RAG困难负例 **40/40**、Top3 **22/22**；Mac全量EXIT 0。专项729已计入Python全量，不重复累计。浏览器单独在mac_browser.log和退出码中记录。

## 下一批待办

K00对剩余326个来源锚点继续逐项原文语义分类，特别是必修125项、选择性必修84项、选修A和B的52/53项。对已知来源的数学主题继续按对象、定义域、条件和跨轨关系合并/拆分，建立真实机器可审计的官方课程原子分母，补齐全部原创深度讲义。K07优先对剩余134个P0证明风险建可复核的完整假设、论证、失效反例及专家裁决证据。不得以文件数、自动测试或LLM流利程度代替教师审核。

## GitHub提交与CI

本批的GitHub Draft PR、完整源码SHA、Tree和GitHub Actions状态在提交后凭真实远端结果写入PR验收回执；本报告不预先虚构尚未获得的编号或CI结论。

**浏览器最终验收：** Mac Chrome/Playwright 15项脚本成功，浏览器pytest 2 passed，0 failed；mac_browser.exit=0。其输出保存在同批日志。

**本批可复核源码Blob SHA（Git原生SHA-1）**：最终修复版 `backend/tests/test_kb_batch83_semantic_coverage.py` = `beedad7482b0934f244eb9426232cf8cc012e7f6`；数学验证模块 `backend/app/kb_batch83_math_relations.py` = `17903421f8cb94db25e0b989bd8f1be7ab363db4`；语义生成器 `scripts/build_kb_batch83_semantic_coverage.py` = `72cd5ed67a2bb92b923e56c480f3967d0e9637cc`。Mac初始提交 `776128ddc226e9c335c5f0a47e2f74c0fcc327b9` 仅是修复前基线。最终修复提交和对应CI状态以GitHub PR回执及本次版本化报告后续记录为准。

## GitHub CI首轮失败与针对性修复

首轮远端CI [Actions #42835895242](https://github.com/YOUessi/stem-mentor/actions/runs/42835895242) 的Python 3.12步骤真实失败：`test_actual_mac_pdf_line_sha_for_all_new_records`无条件要求只能保存在授权Mac的课标原始PDF在GitHub runner存在。该runner不能且不应获得受版权保护的原文；首轮运行有1 failed（其余56791 passed、6 skipped），不计为成功验收。

在Mac实际修复：只对不存在原始PDF的机器将需要真实原文逐行校验的测试显式`pytest.skip`，但保留`build(verify_local_source=True)`对缺失原文、SHA不一致严格拒绝；另新增一个负例测试通过monkeypatch使来源丢失，必须抛出ValueError。**授权Mac上原PDF存在，真实60行校验照常执行，不能把CI跳过的原文核验冒充远端已完成的验证。** 其余来源SHA、状态门禁、数学精确反例和冻结产物检查仍在GitHub runner真实执行。

Mac修复后重新执行完整专项测试729 passed/0 failed；完整Python 56,794 passed、5 skipped、0 failed、1个第三方warning；Node111；浏览器回归及全部退出码在同目录日志和`.exit`中记录。最终GitHub修复版CI另在PR附回执，不事先宣称通过。
