# STEM Mentor Batch99｜七轨课程审计、概念无损修复、范围与数学边界证据

日期：2026-11-12（Mac 本地时间）。本轮仅在 MacBook Air 独立 worktree 实际开发及验证。GitHub 事实源以远端提交与 Draft PR 为准；**不得合并 main，不得发布未获教师批准的教材或学生完整答案**。

## 基线与交付

- 基线源码 `63c687e7b2bb0e7fb89b8b9ea0b0bf0f33fcbb74`（Batch98，Draft PR #123）。
- 本轮核心源码 commit：`60c9c06e2bc8c445f0ea1fc66f770811dbdfd26b`，在 `feat/kb-batch99-editorial-math-validity`。
- 独立工作树：`~/Documents/文件/stem-mentor-kb-batch99`，主仓先前未提交修改保持不触碰。
- 真实课程正式七轨原子分母仍 **UNKNOWN**，无权把300个临时编辑主题等同于官方知识原子。
- K00：来源锁定32项原创范围解释，通过来源 SHA、Schema、边界/反例结构检查；临时300主题状态为166对比待原子化、24单项待原子化、44单项编辑待核定、66深度草案、0无单项编辑，另有134未完成成对语义比较。
- K00：独立审计66份深度草案工程轨道，49 `MATCH_EDITORIAL_ONLY`、7 `CROSS_TRACK_EDITORIAL_ONLY`、10 `TRACK_UNRESOLVED`；原弱规则漏报3项（Batch98.09/.10/.11）。这些是**编辑判定，不是课标权威归属**。
- K01：对Batch95–98中14个概念型作者稿修复 `statement` 字段跨生成器→JSON→Markdown丢失，保持 `definition` 和 `statement` 两者，无自动升级为 APPROVED。
- K03/K04：修正 `det(Q)=-1` 与滑移反射区别，修复一般非退化二维正态分布术语并补联合密度式及 `σ_x>0, σ_y>0, |ρ|<1` 等条件。
- K07：12类可调用、精确有理数有限证据及无效前提拒绝，包括直线/空间几何、正交变换、极限条件、二次函数闭区间极值、仿射定积分、矩形线性优化与协方差行列式；这些检查**并非形式证明**。
- K08/K09：学生检索仍仅返回未批准证据状态，教师完整解答不泄漏；66份讲义的132条文本先修已明确报告为 `TEXT_ONLY_UNRESOLVED`，正式可用的已审 ID 边为0。

## 实际验收（Mac）

- 来源、七轨、先修三项生成器 `--check`：已执行通过（`logs/KB_BATCH99_GATES.log`）。
- Batch99专项 pytest：**116 passed**（`logs/KB_BATCH99_FOCUSED.log`），涵盖非法来源、重复来源、伪造审核、课程轨道误绑、字段无损性、无效数学条件、先修绑定、学生提示防泄漏。
- Chrome/Playwright及浏览器回归：脚本组通过，浏览器 pytest **2 passed**；日志 `logs/KB_BATCH99_BROWSER_CHECK.log`。
- 完整 `scripts/mac_check.sh`：最终退出码及Python/Node测试数量，见同批 `logs/KB_BATCH99_MAC_CHECK_FINAL.log`，已真实执行完成：**Python 63,246 passed / 5 skipped / 1 warning；Node 111/111 passed；mac_check.sh exit 0**（Mac 运行进程 92775，完整日志已归档）。
- GitHub 核心代码通过原生连接器同步（Mac HTTPS git push 因网络超时 exit 128）；远端源码 core commit `31b1341072b25384870b4702cfe3841ae3e16ae8` 的 Tree `5afffdd8cb25d5bfc7877f35400d31fd4fa1db4c` 与 Mac 核心提交的 Tree 完全一致，30/30 源码 Blob SHA 均核验一致。正式 GitHub Actions 状态须独立复核，不得将 Mac 结果冒充 CI。

## 风险、失败模式与下一批

1. 300仍是临时编辑来源主题，正式七轨课程原子分母未知；需保留课标页/条款证据并逐页教研核定，不得靠数量假定覆盖率。
2. 66份讲义仍无正式审核；132条文本先修全部未解析，不可用于学生正式先修路径。
3. 7条跨轨及10条子轨未解，需要源页与专家核定；数学有限验证不等于命题一般证明；历史P0证明步骤仍未清零。
4. 下一批 K00/K01 先建立权威页/条目→课程原子一对多映射、子轨归属人工审核队列及 Schema Gate；随后跨主题扩展完整讲义、题族、错误反例与审校；K08 保留 APPROVED 严格查询门禁；K09 汇总原始测试和未见题。

## Git 提交保护与环境差异

- Mac主仓原有11项未提交修改未触碰；本worktree全量测试写动 `evaluations/results/2026-10-15-policy-and-retrieval.json` 和 `2026-10-15-v05-retrieval.json` 两份历史快照，**没有纳入交付提交，也没有重置这些文件**。
- 无Tang参与；仅本机Mac生成、读取、测试，GitHub connector只负责无法通过Mac HTTPS git push时的原生同步，未用于内容生产与测试。
- 已确认 Mac Python全量/Node/浏览器测试通过；远端CI为独立门槛，未完成前不得声称CI成功。
