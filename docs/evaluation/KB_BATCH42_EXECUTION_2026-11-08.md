# STEM Mentor｜Batch42 执行证据（2026-11-08）

## GitHub 与本地事实源

- 代码唯一事实源：`YOUessi/stem-mentor`；本批 Draft PR #67：`https://github.com/YOUessi/stem-mentor/pull/67`。
- 独立 Mac worktree：`/Users/youtang/Documents/文件/stem-mentor-kb-batch42`；分支 `feat/kb-batch42-editorial-coverage-matrix`，基于 Batch41 分支 `be223817e66769cf6a325fd59a4bc24160ac79ea`。
- 已经完成 Mac 本地数学源码/数据/测试的提交 SHA：`4be4e3488ffea60959025531b9263ca0259f0f08`，Git Tree `f789b2c84c82ffb6d84ae5defc7cb3f3e50eee4a`。该源码提交已成功 `git push`，随后创建 Draft PR。
- Mac 主仓原有的 11 项工作树修改及其他项目均未触碰，没有在 Tang 上编码、生产数据或测试；未重写主分支，也没有合并 PR。
- 版本化记录及测试原始日志采用本文件和 `evaluations/results/2026-11-08-kb-batch42/`。

## 实际内容与代码变更（K00/K01/K02/K03/K04/K06/K07/K08/K09）

1. 以 SHA256 冻结 Batch31/32/33 课程项目编辑目标原始 TSV 与历史稿源，在 `kb_batch42_coverage.py` 中逐行重建完整 **313 个项目编辑目标**（轨道、印刷页、源行号、草稿源、旧稿关联、审核/发布标志），同时导出 `KB_BATCH42_PROJECT_SCOPE_MATRIX.json` 与缺口 Markdown。**313 不是课标官方分母**，任何一个课程轨道的官方分母与正式覆盖率均为 `null`。
2. 七个 track 的项目目标计数分别为必修 125、选择性必修 92、选修 A 28/B 29/C 19/D 16/E 4，合计 313。当前直接关联独立审核稿的项目目标 **133**，仅有历史未经等价认证关联 **12**，无直接编辑关联 **168**。该关联统计不代表单元已被认证为完整教学内容。
3. `kb_batch42_core_extension.jsonl` 新增 20 篇原创必修/选择性必修教师审核稿（各 10 篇）：集合成员/并交集/全称及存在量词、函数零点/二次函数符号/指数单调性、单位圆/正切定义域、数列/等差与等比、常函数和恒等函数求导、局部与整体最值、三维坐标/法向量、条件概率/合法分布列。每篇均含适用范围、先修、三步数学论证或方法依据、反例与错因、2 道教师例题、3 层提示、近远迁移，总计 **40 例题、20 反例、60 条提示、40 个迁移任务**；全部为 `REVIEW_PENDING`。
4. `kb_batch42_exact.py` 对上述主题提供 **20 类有限精确数学实例/条件拒绝算子**，采用整数、`Fraction`、集合运算等有界计算，拒绝字段注入、布尔冒充整数、零分母、无意义几何退化及超界输入。只有受控具体实例可标 `FINITE_EXACT_CASE_ONLY`；一般定理不认证，学生自由文本步骤不验证。
5. `kb_batch42_review.py` 使用 Pydantic 执行来源 ID、重复稿、文档结构、许可/审核权限的独立门禁；`kb_batch42_coverage.py` 的学生查询默认无审核稿，`editor_goal_lookup` 要求明确本地编辑权限且不返回解答。CI 和 Mac check 接入可复现 SHA 和生成物漂移校验。
6. 额外产出 20 篇完整生成 Markdown、20 条 JSON 审核摘要、精确算子适用条件与例外，以及 313 目标逐条 JSON 与剩余高优缺口清单。不上传学生真实信息或教材全文。

## Mac 真实验收

- 首次执行系统 `/usr/bin/python3 -m pytest` 发现系统 Python 没安装 pytest（**环境调用错误，非源码测试失败**）；随后切换原项目 Mac `.venv/bin/python`，Batch42 专项 **432 passed / 0 failed**。
- 原项目 `bash scripts/mac_check.sh`：校验全部已冻结来源/审计工件，Python 全量 **38,565 passed / 0 failed / 1 条第三方依赖警告**；Node **111/111 passed**；策略模拟 **33/33 passed**；结构检索困难负例 **40/40**，Top3 **22/22**，整体 EXIT=0。
- `bash scripts/mac_browser_check.sh`：Chrome/Playwright **15 个浏览器脚本全部通过**；浏览器 pytest **2 passed / 0 failed**，整体 EXIT=0。测试使用临时合成 SQLite；iPad 压感/手势是浏览器指针模拟而非实机认证。
- `scripts/mac_check.sh` 会更新两份 2026-10-15 旧评测文件里的 `generated_at` 时间戳；本批已将这种非语义漂移恢复到分支原样，不误记为产品代码变更。
- 源码/数据的提交与上述测试均在同一个 Mac 工作树进行，没有调用实际模型 API，也没有将有限实例当作证明认证。
- 日志：`evaluations/results/2026-11-08-kb-batch42/targeted.log`、`mac_check.log`、`browser.log`。

## 验收边界与下一批

- 七轨道官方知识原子完整分母仍 `null`，课标正式覆盖率不能计算。313 为尚不完整的项目编辑候选。现有深度草案 287 篇，不因新增审核稿改变“真实教师批准=0、正式学生深度发布=0”的事实。
- 历史 **538 条未形式认证证明步骤、10 组未裁决冲突**继续保持未完成；此前 127 项 P0 有条件审查提议，但这不是形式认证。
- 下一批应优先把 **168 个无直接编辑稿的项目目标**按照必修 90、选择性必修 78 分模块审查，剔除官方不要求/重复、核对官方印刷页及未编号要求、对真实缺稿单元补原创证明、反例和题族；独立复核 12 条仅旧关联是否范围匹配。对 313 候选以外的官方课程要求仍要持续查漏，不能按 313/313 自动结题。
- K07 继续独立审核 538 条旧证明步骤与 10 冲突，K08 继续检验未批准稿不会被外部模型 prompt / 学生 RAG 召回；待真实教师签字才允许状态变更。PR 必须保持 Draft。
