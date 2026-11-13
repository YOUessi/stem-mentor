# STEM Mentor Batch124｜Mac 七轨课标候审与数学可靠性验收

- 日期：2026-11-13；唯一开发、原创内容与实测设备：授权 MacBook Air。独立 worktree：`~/Documents/文件/stem-mentor-kb-batch124`。
- 冻结源码 commit：`e5d620447e8dae25bb97da5fd1c351a9e8ca0586`；源码 Git Tree：`4064f1ee46c8a7e754e733e93b09504101b2dc71`。归档提交在此基础上仅增添测试证据与本报告。
- PR: https://github.com/YOUessi/stem-mentor/pull/149；为避免2,000余文件的累积差异，PR以Batch123的`feat/kb-batch123-source-semantics-and-proof`为叠加审查基线，保持Draft；不自动合并。
- Mac主仓既有未提交修改未动；不在Tang开发、不强制推送、不改写分支历史。
- **重要：正式教师批准0、学生权威发布0、七轨官方完整课程原子分母均为UNKNOWN。**

## 1. K00/K01：覆盖及真实性

- 405条**课标排版线索**的处置台账维护完成，来源行哈希与课标原件本地核对；本批新增32个原创语义候审目标，累计239个工程候审目标。
- 270/405条排版线索关联候审目标、135条尚未完成正式语义判别（关联率66.7%，**不是官方知识覆盖率**）。
- 3条建模/方法活动线索标记为 `NON_ATOM_ACTIVITY_EDITORIAL_PROPOSAL_PENDING_REVIEW`，尚待人工确认；不得直接从“非原子候选”中删除或当作“正式已排除”。
- 逐轨机器可核对计数：

| 课程轨道 | 本批候选新增 | 累计候选 | 已关联排版线索 | 待判别线索 | 正式原子分母 |
|---|---:|---:|---:|---:|---|
| COMPULSORY | 25 | 75 | 76/127 | 51 | UNKNOWN |
| ELECTIVE_A | 3 | 30 | 41/69 | 28 | UNKNOWN |
| ELECTIVE_B | 2 | 30 | 43/70 | 27 | UNKNOWN |
| ELECTIVE_C | 0 | 24 | 20/29 | 9 | UNKNOWN |
| ELECTIVE_D | 0 | 17 | 14/17 | 3 | UNKNOWN |
| ELECTIVE_E | 0 | 12 | 4/4 | 0 | UNKNOWN |
| SELECTIVE_COMPULSORY | 2 | 51 | 72/89 | 17 | UNKNOWN |

- 课程来源真实、分轨错误、先修孤儿、伪造分母、虚假批准等均采用fail-closed拒绝门禁；版面提示不是原子知识点。

## 2. K02–K06：完整原创候审讲义与教学题族

- 8篇教师侧原创讲义：指数函数单调性；对数定义域与反函数；正弦模型振幅周期相位；余弦差角公式的向量证明；直圆柱/圆锥体积；两事件容斥；抛物线焦点准线；三维内积/叉积。
- 每篇均包含正式陈述、符号与前提、逐步论证、边界和反例/误区、2个教师例题、3级不剧透提示、近远迁移。
- 共16道教师侧例题、24级学生提示、8项边界/典型错误、近远迁移共16项。候审内容标记`REVIEW_PENDING / TEACHER_ONLY`，不得由机械完整度自动升级。
- 数学边界：正弦模型A或ω为零时不存在最小正周期；圆锥积分推导单独限定h>0；焦点在准线上时是退化集合而非通常抛物线；零向量的夹角或零叉积方向不可随意定义；对数的真数严格大于零。

## 3. K07–K09：证据核验和真实测试

- 独立有限精确SymPy等验证：16个教师例题、8个负面前提、8个跨主题精确见证。**一般定理形式证明认证0、学生自由文本步骤自动认证0**。
- 学生自主挑战不会检索到教师完整解答；未获教师审核的候审内容不能作学生端权威知识引用。真实模型API冻结对照、教师专家审核和实体iPad设备实验尚缺。
- Mac源码冻结后运行：

| 检查 | 实测 |
|---|---|
| `scripts/mac_check.sh` | EXIT 0；backend Python **66293 passed / 5 skipped**；Node **111/111 passed** |
| `tests/test_kb_batch124_scope_depth_math.py` | **505/505 passed**；包含在全量后台验证中，不和全量计数相加 |
| `scripts/mac_browser_check.sh` | EXIT 0；Chrome/Playwright多屏、计算、交互及边界回归完成，浏览器pytest 2 passed |
| 限制 | 浏览器触控和笔压为模拟检查；没有真实学生数据或版权教材全文进入仓库 |

## 4. 原始日志清单（可机器复核）

| 文件 | SHA-256 | 字节 |
|---|---|---:|
| `KB_BATCH124_MAC_CHECK_FINAL.log` | `e5f859c2ebb70ec557a5cac991eaa6a99a1c744e3672a1b2eb9f23a32a05a40a` | 121173 |
| `KB_BATCH124_MAC_CHECK_EXIT.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | 2 |
| `KB_BATCH124_BROWSER_CHECK_FINAL.log` | `7f958e488a2b12ac8baa9b7abbfe1c367dc4d5c81277bbb60941129b3ad88e97` | 2443 |
| `KB_BATCH124_BROWSER_CHECK_EXIT.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | 2 |
| `KB_BATCH124_TARGETED_FINAL.log` | `6e8a63bc5ba01db0a4086f6cbd6a14653452f64ba1532927e187735bd93b7507` | 661 |
| `KB_BATCH124_TARGETED_EXIT.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | 2 |

## 5. 未完成的验收及下一批

- 下一批继续处理135条来源排版线索：必修51、选择性必修17、选修A28、B27、C9、D3。重点按印刷页、原句证据与语义目标分拆，不用候选计数填充课标原子分母。
- 优先清理172条历史待审先修关系、538条历史未认证证明步骤和10项历史数学冲突；以上为此前队列规模，**本批未宣称消除**。每项按前提→推导→不适用证据审校，并扩大真实验证范围。
- 继续原创整模块深度讲义、题族与真实K08 API/规则基线比较。只有课程覆盖、证明/先修审校、真实教师批准、学生端安全与发布验收全部达标才可关闭总任务。

**结论：本批完成了可验证的原创候审内容、来源安全门禁、Mac真实测试及审计记录；全量知识库尚未达到课程/教师审校的上线门槛。**
