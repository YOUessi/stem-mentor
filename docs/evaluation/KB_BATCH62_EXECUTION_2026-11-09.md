# STEM Mentor｜Batch62 Mac 开发、内容审核和测试回执

日期：2026-11-09。唯一开发环境：授权 MacBook Air，独立 worktree ~/Documents/文件/stem-mentor-kb-batch62，分支 feat/kb-batch62-anchor-triage；起始 GitHub PR #86 SHA：38e869a95cd397b2e0c69493134b8025960eb76a。本批源码提交 bc63b36b6175b5d66d4351bce44acb3977809cb8。未使用 Tang、未合并或修改 main，主仓原11处未提交修改保持隔离。

## K00：56 条来源起点实质审查

Mac 使用锁定课程标准PDF，SHA256 cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195，核对 PDFKit 页哈希和所有56处来源行哈希。版权PDF/原文从未上传。已逐一检查 Batch61 尚无来源区间位置重叠的56处候选，补充原创数学主题释义、特定适用边界、审查类型和下一步动作。

机器可审计分类：11个上层主题标题、5个内容栏目、4个学业要求栏目、5个教学提示栏目、27个子条范围、4个直接课程目标。**31个实质性主题/子条**包含明确数学错误风险与前提边界：充分/必要方向、非负基本不等式、二次方程非零最高系数、指数/对数定义域、单位圆正切奇点、二分法连续性/变号与不保证唯一根、向量基底非共线、概率等可能不能由样本空间有限性推出、微分与真实增量之别等。

新增独立 **14个非知识原子栏目能力/教学矩阵**（学业4、教学5、内容5），全部显式 UNMAPPED，避免误把 NOT_A_CONTENT_ATOM 解释成无需覆盖审查；未编号段落、跨页关系和第35页图示仍待教师及视觉审查。没有把这56处冒充已经补齐来源区间；没有把428机器起点、344非去重来源线索或31候选范围当官方知识原子数。七轨正式分母继续全 null，完整教师页审核0/61、正式教师批准0、学生深度发布0。

## K01/K07/K08/K09

- 重放式来源与审核门禁生成器：scripts/build_kb_batch62_anchor_triage.py，输出可审查JSON、Markdown、单独能力台账；锁定原始来源行指纹及Batch61注册和待审队列SHA，防伪造正式审核、签名、内容完整度、跨页等价、数学认证、学生发布和伪造轨道。接入Mac脚本及GitHub CI。
- 新增10类 Fraction 有限实例数学边界核验：集合补集、有限量词否定、非负AM-GM平方差、二次方程判别式、指数相邻整数幂方向、对数域、二维基底行列式、等可能古典概率、二次函数微分/实际增量差、三角形余弦值。均在假设失败时拒绝；返回 FINITE_EXACT_CASE_ONLY，不认证一般定理或任意学生自由证明。
- 对8个未审核来源起点实际调用学生检索与Tutor提问路径，均 NO_APPROVED_EVIDENCE/BLOCKED、不调用外部API；该结果只代表零已审核内容下的默认阻断，不能冒充真实云端或混合签名条件下的生产验收。既有Batch58混合签名RAG测试仍在本批全量回归内。

## Mac真实测试

- 增量pytest：**270 passed，0 failed**（含来源、Schema、负例、受控数学与安全路径），见 evaluations/results/2026-11-09-kb-batch62/incremental.log、incremental.exit=0。
- Python全量：**45079 passed，0 failed、1条第三方弃用警告**；包括上述270增量案例。
- Node：**111/111**；Tutor **33/33**；RAG hard negatives **40/40**、Top3 **22/22**。
- bash scripts/mac_check.sh：**EXIT 0**，见同目录mac_check.log、mac_check.exit。
- 浏览器 Chrome/Playwright **15个脚本通过**、browser pytest **2 passed**；bash scripts/mac_browser_check.sh **EXIT 0**。完整证据见mac_browser.log与mac_browser.exit。仅使用合成数据及CDP模拟，不代表真实硬件。
- 本批修复前不存在隐瞒的数学失败：创建新独立栏目的产物后第一次手工调用 --check 遇到尚未生成该文件的 FileNotFoundError，随后先生成再复验通过；初始worktree缺少本地虚拟环境链接，已只对worktree建立指向既有Mac环境的符号链接，不改写全局环境。最终测试结果以上述成功日志为准。

## 不得提前关闭的里程碑

下一批逐条补证31项主题/子条的全文数学前提与跨页等价审查、14条学业/教学栏目的能力覆盖；审校第35页图形、全部未编号句子和选修E的学校自主范围。在冻结七轨独立原子分母后批量新增完整原创讲义、题族与提示梯度。538条历史证明步骤未形式认证，10组数学冲突未裁决；真实教师签核、生产API对照及学生发布全部待办。所有本批记录保持 REVIEW_PENDING，PR保持Draft，Issues #17–#27 保持Open。
