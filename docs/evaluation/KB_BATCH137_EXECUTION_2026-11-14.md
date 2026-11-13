# STEM Mentor Batch137｜Mac-only 41条限定候审稿闭环、边界Oracle和检索隔离执行记录

> 日期：2026-11-14（Mac 本地），仓库 `YOUessi/stem-mentor`，#17 #18–#27。
> 开发与测试唯一设备：`YOUTangdeMacBook-Air.local`（MacBook Air）。
> 独立 worktree：`~/Documents/文件/stem-mentor-kb-batch137`。
> 分支：`feat/kb-batch137-seven-manuscript-closure`，上一批源码树基点 `a86041bf4c1e29320abb9fead52b4036a024f5e6`。
> Mac 本地源码 commit：`9a838891982eff514cc9c5599e400e827768b888`，源码 Git Tree：`1f6de5aeba4df33e6b774a2f2db50033b700c7bb`。
> GitHub 原生对象提交：`c9a802927b358b80dbc4a79635cbcd7af4a51c9a`，源码 Git Tree **完全相同**；Draft PR [#163](https://github.com/YOUessi/stem-mentor/pull/163)，叠加基线 Draft PR #162，未动main。

## 交付范围：有限41候选，不是七轨正式课标完整分母

- 新增7份**原创、完整、教师候审**深度讲义：数列定义与递推初值、数学归纳法、求导运算法则、空间基底唯一展开、单调有界收敛定理、函数极限ε-δ、连续性。
- 每份有形式定义/准确论域、完整条件、分步证明或演绎（含必要时指出实数完备性）、不适用反例、错误论证与修复、两道教师例题（分步求解）、三级不泄答案的提示、近远迁移。
- 新增原创教师例题14道、分层提示21级、近迁移7、远迁移7；独立SymPy/精确整数验证**21例**：14个有效、7个失效前提/反例。数学工具只核查列出的有限见证，**绝不**标记为一般定理形式证明。
- 41个被冻结的Batch133有限提案：原来34份有稿+7份缺稿，现 **41/41 有完整候审稿**；共82道教师例题、123级提示、123项历史+本轮有限精确核验。必修23、选择性必修11、选修A7；选修B/C/D/E在这个有限提案集为0，**不**代表这些官方课程轨道缺内容或已完成。
- 正式课程原子分母：**必修/选择性必修/选修A–E全部UNKNOWN**。本轮没有全国课标全量清点成果，不得把41/41表示为高中数学课程覆盖率。所有稿件 `REVIEW_PENDING`/`TEACHER_ONLY`，0正式教师批准、0一般定理证明认证、0学生权威知识发布、0自由学生文本步骤认证。
- 新增41份冻结候审稿的SQLite FTS5本地编辑预检索，仅返回草案ID/来源/轨道/未验证条件状态；教师全解不入FTS，草案内容无公开HTTP路径。新增匿名只读汇总路由 `GET /api/knowledge/kb137-review-coverage`，学生证据检索默认拒答 `NO_APPROVED_EVIDENCE`。注意 `scope=EDITOR_LOCAL`只是开发误用保护，**不是真实授权机制**，不得外放此本地函数。

## 测试命令与真实结果

- `.venv/bin/python scripts/build_kb_batch137_lessons.py --check`：PASS。
- `.venv/bin/python scripts/check_kb_batch137_math.py --check`：PASS，14正例+7负例。
- `.venv/bin/python scripts/build_kb_batch137_coverage.py --check`：PASS，41条有限提案全部有稿，正式课程分母不能伪造。
- `PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch137_closure.py`：**188 passed，0 failed**，1条第三方Starlette/anyio弃用警告；真实退出码0；原始日志 `docs/evaluation/logs/KB_BATCH137_FOCUS.log`，退出码 `KB_BATCH137_FOCUS.exit`。
- `bash scripts/mac_browser_check.sh`：Chrome/Playwright模拟真实回归**EXIT 0**，包含浏览器pytest **2 passed**；真实iPad笔压不是实机验收；日志 `docs/evaluation/logs/KB_BATCH137_BROWSER.log` 与退出码 `KB_BATCH137_BROWSER.exit`。
- `bash scripts/mac_check.sh`：整套Mac Python/Node全量回归**另行执行中**。在原始日志 `docs/evaluation/logs/KB_BATCH137_MAC_CHECK.log` 与 `.exit` 真实完成前，不得宣称全量通过；不得把188专项与后端全量数字相加。

## 实际发现和修复

1. 独立SymPy检查在无穷大上使用差值 `oo - oo` 不能判相等，导致真实失效；已改为精确检查 `S.oo` 同一常量后再进行有界代数比较；重新运行21/21见证通过。
2. 课标提案与正式原子不能混淆：审核账本强制所有七轨正式分母NULL，禁止候审稿审批/学生发布。
3. Mac原生 `git push` HTTPS低速超时（退出码128）；通过 GitHub 原生 Git blob/tree/commit/ref 接口非强制快进同步。14个Blob SHA全部与Mac一致；首次远端树SHA不同，经审查发现可执行 `scripts/mac_check.sh` 应为Git mode `100755`，修复模式后 Git Tree 完全一致；远端commit与Mac commit元数据不同但内容树一致。未强制推送、未重写历史、未合并main，Mac主仓原有脏文件保留，Tang没有参与。

## 未通过的最终验收门槛与下一批

- 官方七轨全国课标原子总数仍未冻结；必须用原版2017/2020标准和真正的条款/章节关系逐一拆分、去重，进行来源语义教师复核，不能引用项目拟议原子作为全国分母。
- 历史538条未认证证明步骤、172条先修关系、10项数学冲突仍需最新源码复核及逐项证明，不能从21有限实例推断已解决。
- 全量选修B–E、概率统计、空间解析几何、建模等远未覆盖；补充新的课标源锁定原子并继续原创深度课程与教学题族。
- 正式教师签名审核、认证数学推理、真实API教学冻结对照、学生自由文本验证、真实教学效果验收均未达到；所有未经签批材料仍只在候审隔离层。

**本报告与测试日志按真实执行逐项更新；不得把未来的跑完状态倒填为既成事实。**
