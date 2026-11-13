# STEM Mentor · Batch112 — 官方课标22/59页、三角恒等与黎曼积分系统续建（2026-11-12）

## 可追溯开发基线

- GitHub源分支：`feat/kb-batch111-verified-delivery`，远端已验证基线提交 `662d32b770b67996e24b78a1b3ef537518464198`（Batch111 Draft PR #136）。
- 本批唯一开发/内容/测试环境：MacBook Air，独立 worktree `~/Documents/文件/stem-mentor-kb-batch112`，分支 `feat/kb-batch112-trig-integral-rigor`；Mac 主工作树与现有未提交修改不改写，不使用 Tang。
- 读取了总任务 #17 与 #18–#27（11个均 open），以及最新 Draft PR #136。GitHub为最终事实源，提交/PR和Issue更新需按实测状态填写。
- 来源：本地缓存《普通高中数学课程标准（2017年版2020年修订）》 PDF SHA-256 `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`，`curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json`中的每页 PDFKit SHA 与本地内容逐项核对。不上传版权PDF全文或学生记录。

## K00 / K01：来源机器审计与不虚报覆盖

- 印刷页 **22（PDF索引29）/ 59（PDF索引66）**：共**59条PDFKit来源行（31+28，其中各含1行印刷页码页脚）**，对应 **11 个连续非重叠结构区段**。
- **20项项目原创的课程要求编辑候选**：必修10、选修B10；另外五轨此批均0。共有 **18项**独立有限精确或可控实例见证；其余2项是课程概述（教学目标），不伪造为数学定理。
- 本批识别页22同角三角函数式子中的分数换行以及页59牛顿—莱布尼茨积分上下限的PDFKit格式截断；锁定来源字节哈希而非依赖自动还原的公式做正式认证。课标页22→23、59→60存在跨页延续，均仍须教师核对原始图像。
- 完整七轨课程知识原子分母 **UNKNOWN**；本批统计的**8/61页**仅指最近四个批次（19–22与56–59）进行了文本结构审计，不是覆盖率、更不是教师完成的逐页原子化；教师正式完成页仍为0。
- 代码：`scripts/kb_batch112_source.py` 和 `scripts/build_kb_batch112.py`，产生 `docs/evaluation/KB_BATCH112_SCOPE.json`、`KB_BATCH112_COVERAGE.json`，拒绝来源漂移、漏行/重叠、跨轨归属、额外审批字段、重复候选ID、假官方原子与伪分母。

## K02–K06：八份独立原创教师候审深度单元

1. 参数正弦模型的振幅、周期、零振幅/零频率退化及时间量纲；
2. 同角正弦余弦平方和恒等式的单位圆证明、除以余弦的定义域限制；
3. 两角差余弦公式的单位向量内积/旋转证明及符号反例；
4. 连续函数变号区间二分法、区间不变量、n次二分中点误差界及跳跃函数反例；
5. 等分右端点黎曼和，求和公式、极限与有限n的近似误差；
6. 连续导数条件下牛顿—莱布尼茨公式，中值定理→望远镜和→黎曼和逐步推导；
7. 二元偏导的定义、方向限制与两个偏导都存在却不连续的反例；
8. 紧凸多边形上的仿射函数顶点极值定理、凸组合推理和非线性反例。

- 类型：**4定理 + 3方法 + 1概念**；8份 `REVIEW_PENDING/TEACHER_ONLY`，各含至少2道逐步校验的教师例题、3层不剧透提示、近迁移和远迁移、适用前提、具体反例与误因，总计**16例题、24提示层、16迁移练习、8套反例**。
- 另新增 **12条未经形式验证的候审定理证明步骤**，2条前向先修依赖；独立符号验证仅评估具体有限实例，不能当作一般证明或真实教师批准。
- 生成内容：`knowledge/deep/v1/batch112_trig_limits.json`（该文件名系沿用上一批兼容模板，实际八份内容同时覆盖三角、二分、积分和优化）、`docs/evaluation/KB_BATCH112_LESSONS.md`；审计 `KB_BATCH112_AUDIT.json`。

## K07 / K08 / K09：可复现回归与发布隔离

- 版本化构建器 `--check --verify-local-source` 对本地PDF原始字节、跨页哈希、结构完整性、历史草案唯一ID、七轨归属和证据假设进行一致性检查。GitHub CI只做版本化来源锁一致性，Mac再做原始PDF字节对照。
- `backend/tests/test_kb_batch112_trig_integral_guard.py`：来源20项逐一非权威性、8份完整Schema、8份Student RAG拒绝未审知识、伪审批和学生可见性/许可拒绝、课程分母伪造拒绝、18类正反实例、不同参数的真实数学等式及反例。
- 官方分母仍未确定，0教师正式批准，0学生权威发布；历史 **172**条未审先修、**538**条未认证证明步骤、**10**项冲突未解决。本批12条新增候审证明也不视为已认证。
- `scripts/mac_check.sh` 与 `.github/workflows/ci.yml` 新增Batch112构建门禁；本批专用测试不等于整库教师审校。
- GitHub远端CI需独立运行后再声明通过，Draft PR不自动转正。

## 测试记录

- 首次本批专项 `PYTHONPATH=backend .venv/bin/python -m pytest -q backend/tests/test_kb_batch112_trig_integral_guard.py`：**128 passed / 0 failed**。
- Batch112源构建 `--verify-local-source` 和 `--check --verify-local-source`：均成功，结果为**59行、20候选、18有限见证、8完整深度草案、12候审证明步骤**。
- 全量Mac Python/Node与浏览器验收：本节在测试真实完成后填入结果和日志SHA，不因运行中或错误的初次尝试提前宣称通过。

## 未完成与下一批优先级

1. K00：继续印刷页23、60及与前页的跨页文本/图像复核；以整个61页课程来源分轨完成真正的原子清单和机器可审计分母，而不是按内部候选数量虚报完成率。
2. K01/K07：以10项冲突和538条历史未认证证明步骤为高风险队列，按假设缺失、除零/负根/域限制、伪逆命题、端点与退化条件分别验证。
3. K02–K06：继续扩展数列和微积分、概率/统计、建模、几何、选修C/D/E，逐项接上题族、反例、完整先修与不同解题提示阶段。
4. K08/K09：检索证据链和学生RAG拒答必须按冻结且已批准来源测试；没有教师审校绝不放开独立挑战的完整答案。真实API与学习增益测试在可用环境下独立记录。

## 2026-11-12 Mac 终验与原图公式交叉审查补充

- **最终可核实完整命令**：Mac独立工作树执行 bash scripts/mac_check.sh，控制台进程PID 50700的最终输出为 FINAL_MAC_CHECK_EXIT=0，进程自身退出码0，运行1235.71秒。原始日志为 docs/evaluation/logs/KB_BATCH112_MAC_CHECK_FINAL.log。
- **Python完整测试**：65,554 passed，5 skipped，0 failed，1条第三方警告；pytest用时1093.11秒。**Node**：111 passed，0 failed。Batch112针对性新增测试128 passed，已包含于全量Python统计，不重复计数。
- **真实浏览器脚本回归**：scripts/mac_browser_check.sh Mac Chrome/Playwright模拟布局、交互、iPad指针仿真、极值与学生数据隔离全部通过，末尾浏览器pytest 2 passed；日志KB_BATCH112_BROWSER_FINAL.log。iPad为浏览器模拟，不宣称真实Apple Pencil硬件测试。
- **首次命令封装问题可复现留证**：KB_BATCH112_MAC_CHECK_INITIAL_WRAPPER_ERROR.log虽然记录了65,554 Python通过及Node 111/111，但上层命令封装没有提供可靠退出码，因而重新完整执行并记录退出码0。另保留浏览器首次封装错误日志；不将工具包装问题误报为数学回归通过或失败。
- **K00 PDF原图目视交叉核对**：Mac PDFKit将本地SHA锁定的官方PDF第29、66索引页渲染到临时PNG，确认印刷第22页同角公式的分式布局以及第59页Newton–Leibniz积分上下限；独立记录见 docs/evaluation/KB_BATCH112_FORMULA_VISUAL_REVIEW.md。**这仅是AI辅助目视转写，不属于教师审核或正式数学内容认证**。
- **新增查明的真实缺口**：课标第59页二元二次函数在闭圆和椭圆上求极值不属于本批已写的“仿射函数在紧凸多边形顶点取极值”定理，仍应在K00/K05保留待建条目，不能错误归并。
- **源码与发布边界**：Mac已测试Batch112源码树 a91b274805d5ca172cd823d6521ed202bb461b00；GitHub初始源码提交4dfbf5d356a4f53924b9bb6eae89a6c2cb1048d8，对应GitHub Actions 43222395936 的源码检查 completed/success。追加本执行报告和原始证据后必须重新核实远端HEAD及最新CI；PR #137保持Draft，不合并main。
- **Git Blob/独立SHA-256见证**（以下为Mac原文件，不可用报表数值代替原始日志）：
  - KB_BATCH112_MAC_CHECK_FINAL.log：Git Blob be3daa9ca71a4004c252328235e7fe31cefe229d；SHA-256 b69454b755458d59d711f8dae40de0550781e8d93bfa6e8421b5100d782ae04b
  - KB_BATCH112_MAC_CHECK_INITIAL_WRAPPER_ERROR.log：Git Blob f07857d8b7b7dbfc3299acf27a3d87975b693ede；SHA-256 c1542d246e2359332c1e0393261eb160ea8c70848f253eefac0a50942fa9e822
  - KB_BATCH112_BROWSER_FINAL.log：Git Blob 881158e4a04f77a565daee1966b8895591253e6e；SHA-256 d2fa6eb604e9b618d9a13a689ac9d3b268a3b28385eee1cfc1c5ee9f9a35af33
  - KB_BATCH112_BROWSER_INITIAL_WRAPPER_ERROR.log：Git Blob 0012b849765c3f80b402e79a3f6444cc791f5cad；SHA-256 ba898953eea7bac23db6a2d43e8e6b6924a485fd7c30fe89e40de9ad8b10bab8
  - KB_BATCH112_FORMULA_VISUAL_REVIEW.md：Git Blob df0f34134def5b41c3cb317186fe08106f9ad355；SHA-256 81e05efbb76137ca23a2ae2c280cf488f056f227efc6e096bce5d4b21cd1987d

**剩余硬门槛**：官方七轨课程原子总分母仍全部UNKNOWN；61页尚无教师正式完成原子化的记录；172条历史先修关系、538条历史证明步骤、10项数学冲突仍待正式审核；新增12条候审证明步骤也不以有限实例自动升级。教师批准0、学生权威发布0。后续优先23/60页跨页审查、二次闭圆/椭圆极值、完整七轨课程原子分母、危险证明条件/先修图谱、独立教师审核和真实Agent证据检索。
