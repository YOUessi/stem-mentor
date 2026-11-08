# STEM Mentor｜Batch29 P0 数学条件审查开发与验收（2026-11-08）

## 1. 唯一代码开发环境与 GitHub 来源基线

- **授权开发与真实测试环境**：YOUTangdeMacBook-Air.local；独立 worktree `~/Documents/文件/stem-mentor-kb-batch29`，分支 `feat/kb-batch29-p0-condition-expansion`，未在 Tang 上编写/运行代码。
- 基于 GitHub Batch28 Draft PR #53，冻结 SHA `db762e81841d01ad8a5d7bde2885ae5af7134003`。未变更 Mac main 的 11 项历史未提交修改、Batch27 的独立 worktree，未合并也未强制更新任何主分支。
- 本批**本地测试通过的源码提交**：`6100e580d70b0a41a2e51503e101170cdc4bf221`；Git Tree SHA `1af9fd5460ade509cbefa9132e6a3ae09569c5bf`。
- 代码和原创数学审查稿为项目自编；没有上传真实学生数据、版权教材全文或官方课标 PDF；无需模型 API 或 Tang GPU。
- **GitHub 源码远端**：Mac 原生 `git push` 因 `Error in the HTTP2 framing layer` 中止；经 GitHub 原生 Git Tree/Commit API 同步到 Draft PR **#54**，GitHub 源码提交 `1cec9642a983b2c0c6f61a6b54e7fa8acae79b35`；逐文件同步后，GitHub tree **`1af9fd5460ade509cbefa9132e6a3ae09569c5bf`** 与 Mac 已测试源码树 SHA 完全一致，不是未经测试的替代版本。最终浏览器报告提交由该远端源提交继续衍生。

## 2. 一整批 K07 × K01 × K09 代码与数学成果

这次不把增加数字当作内容审校。所有新工作在 **287 篇既有 REVIEW_PENDING/TEACHER_ONLY 草案**上进行，**本批新增完整讲义为 0 篇**。

| 指标 | 之前 Batch28 | 当前 Batch29 |
|---|---:|---:|
| 原始历史 P0 风险步骤 | 127 | 127 |
| 已有人工编写条件/反例的编辑审查建议 | 35 | **83（新增 48）** |
| 尚缺人工条件审查的历史 P0 | 92 | **44** |
| 本批新增受控有理数验证操作 | — | **20 类** |
| 本批正例精确 fixtures | — | **20/20** |
| 本批非法前提拒绝 fixtures | — | **20/20** |
| 历史完整自然语言证明形式认证 | 0 | **0** |
| 正式教师批准/学生端正式发布 | 0/0 | **0/0** |

- **数学对象**：同一内积空间范数、非零向量夹角、直线法向/平行/点线距离、二次顶点和根号、条件概率/贝叶斯/方差、有限级数、二倍角、投影、复数商、复合函数定义域、多项式切线、椭圆参数、线面垂直、2×2 逆矩阵及正交等距。
- **独立编写数学说明**：`docs/evaluation/KB_BATCH29_MATHEMATICAL_DERIVATIONS.md`，共 15 个有条件/推导/边界的核心命题说明及独立的证据边界声明；逐步阐释当量词、定义域、非零分母、相交直线张成等前提不成立时为何拒绝。
- **原始证明可追踪**：`knowledge/proof/batch29_p0_condition_profiles.json` 人工编写 20 类条件档案；`scripts/build_kb_batch29_p0_evidence.py` 校验原始 risk ID、历史冻结步骤的 claim/reason SHA、前 35 项不重叠、每条编辑审查独立关联原始证明文本、非法伪签字/删步/篡改。新增审查报表 `docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json` 记录 **48 条**新步骤及余下 **44 条**原始步骤，保留每一条风险 ID、来源 SHA、数学前提与反例。
- **数学验证边界**：`backend/app/kb_batch29_exact_witnesses.py` 中 20 类 Fraction/受控有限分布/有理多项式检查，只接受有限、低复杂度、显式类型输入。拒绝时使用 `CONDITIONS_NOT_ESTABLISHED`；通过时仅标记 `VERIFIED_FINITE_INSTANCE`，`student_step_verified`、`complete_theorem_certified`、`teacher_approved`、`official_curriculum_atom_verified` 始终为 false。
- **教学 Agent 不剧透**：新增档案位于 `knowledge/proof`，不写入学生深度知识主库，不修改 `prerequisite_lesson_ids` 和 `teacher_solution_visibility`。新增测试检查 287 篇现有草案保持 REVIEW_PENDING/TEACHER_ONLY，学生端没有自动提升数学证据状态。
- **自动门禁**：Mac `scripts/mac_check.sh` 与 GitHub Actions `.github/workflows/ci.yml` 均加入 `scripts/build_kb_batch29_p0_evidence.py --check`，禁止编辑档案/报表不同步及审核结果伪造。

### 代表性数学反例

1. `A=B=0` 的所谓直线方程 `Ax+By+C=0` 不是普通直线，不得用于点线距离、法向式、平行/垂直判别。
2. `b=0` 时投影系数 `(a·b)/(b·b)` 的分母为零；零向量的内积和平方范数仍有定义，但与非零向量的几何夹角未定义。
3. `P(A)=0` 时 `P(B|A)` 无定义，即便 A 是非空集合；全概率必须穷尽且事件不交，贝叶斯后验还需 `P(B)>0`。
4. `q=1` 时等比数列分式求和发生 `0/0`，但真实有限和仍是 `na`；必须分支。
5. 两条平面内方向共线时只张成一维，直线同时垂直它们**不能**推出垂直整个平面。
6. `det(A)=0` 时不能将二阶矩阵伴随矩阵除以 `det(A)`；必须独立说明不存在可逆映射。

## 3. 真实 Mac 测试和失败记录

| 验收项 | 真实结果 |
|---|---|
| Batch29 定向 pytest | **3,525 passed, 0 failed** |
| Mac 完整 Python backend pytest | **29,787 passed, 0 failed, 1 条第三方弃用警告** |
| Node JS 单元/模块回归 | **111/111** |
| 教学策略离线模拟 | **33/33** |
| 结构检索困难负例 | **40/40，Top3 22/22** |
| 来源审计/证明记录/CI 新增 `--check` | **通过** |
| JavaScript syntax 和静态工具脚本 | **通过** |
| Chrome/Playwright 浏览器完整回归 | **15 组脚本均 PASS + 浏览器 pytest 2 passed，脚本 EXIT 0；临时合成数据库，无外部请求** |

初次从仓库根运行时出现 `ModuleNotFoundError: app`（PYTHONPATH/工作目录错误），改用标准 backend 工作目录。第一次有效专项执行出现 **42 failed / 3,483 passed**，因 SymPy 返回数学等价但结构未展开的复数表达式，原测试错误地用结构相等 `==`。修复为 `sympy.simplify(lhs-rhs)==0`，完整保留全部样本，重新运行得到 **3,525 passed**；另修复 zsh 退出码变量名 `status` 只读。版本化失败详情和原始/最终日志见：

- `evaluations/results/2026-11-08-kb-batch29/initial-failures-and-fixes.md`
- `evaluations/results/2026-11-08-kb-batch29/python-initial-failure.log`
- `evaluations/results/2026-11-08-kb-batch29/python-targeted.log`
- `evaluations/results/2026-11-08-kb-batch29/mac-check.log`
- `evaluations/results/2026-11-08-kb-batch29/browser.log`（须以最终实际退出结果核实）

**浏览器验收已实际完成**：Mac `scripts/mac_browser_check.sh` 返回退出码 **0**，15 组独立 Chrome/Playwright 脚本成功、浏览器 pytest **2 passed in 11.82s**，无外部请求；iPad 部分只是指针模拟而非真实设备。源提交 GitHub CI [run #42444334328](https://github.com/YOUessi/stem-mentor/actions/runs/42444334328) 在报告生成时仍为 `in_progress`，最终结论须继续独立读取，不可提前宣称 Success。

## 4. 本批没有解决的系统性阻断

- K00：61 页课标来源的历史提取 **315 vs 317 编号位置**仍未由独立原始版面审查裁定；工程候选、出版页码或表格不是官方原子分母。必修、选择性必修与选修 A–E 的**可审核官方知识原子分母、正式覆盖率仍为 null**。
- K01/K02–K06：既有 287 篇深度草案仍未教师审核；133 篇原无先修图边、Batch26 31 条编辑候选待核准，102 篇仍无编辑边候选；本批未新增讲义/题族，不假装内容全覆盖。
- K07：127 条 P0 中现有 83 条得到**编辑前提建议**，44 条尚无此层审查；全部 **538 条自然语言证明步骤仍 NOT_FORMALLY_VERIFIED**；10 组历史冲突没有真实专家裁决。
- K08/K09：无真实教师签名或形式/独立审校证明，本批不会把编辑材料授权到学生端，所有 #17–#27 保持 OPEN。

## 5. 下一批高价值开发

继续核查最后 **44 条历史 P0**，优先处理微积分中值/极限量词、统计最大似然边界、空间几何非退化性与建模假设；对 10 组历史冲突逐条进行独立数学反例和核验。与之并行推进 K00 课标原文逐页人工/机器交叉审计，精确拆分无编号内容及必修/选择性必修/选修 A–E 的官方分母，之后再逐章扩展完整原创讲义、题族、先修与安全教学检索。**教师批准前保持 Draft，不合并 main，不关闭任何未验收任务。**
