# STEM Mentor｜Batch120 执行与验收记录（2026-11-13）

## Mac 源码冻结与 GitHub 上下文
- 唯一开发、内容生产和测试设备：MacBook Air；独立 worktree：/Users/youtang/Documents/文件/stem-mentor-kb-batch120。
- 冻结源码 commit: 21bde63408b18b18d7c36fe6d714bb49a92217ef；Git tree: 344024dcda98c27304a4641a1553ff613fe519f5；与 Draft PR #145 首次交付 tree 一致。PR 在证据交付前 HEAD 为 8b0169fc79bb884f34a7a0397181aa282ba2fb2f。后续只补日志与验收报告，不修改已测试源码。
- 未在 Tang 开发，未修改或合并 main，未强推。主仓历史未提交修改不动；自动测试改动的两份旧评测 JSON 不纳入提交。

## 实质交付（K00、K01、K06、K07、K08、K09）
- 本批新增 64 条原创七轨语义课程候审原子，连同先前 Batch119 的49条，累计113条；全部来源锁定，含课程轨道、页码、行哈希、目标、先修、条件和反例。
- 与405条来源排版线索关联的累积数量144条，尚有261条未关联。排版线索不等于正式知识原子；官方七轨总分母一律 UNKNOWN。
- 六套原创定理证明+题族（详见 KB_BATCH120_PROOF_FAMILIES.md），包括平面向量独立基分解、余弦定理、空间距离与三维正交基展开。逐步证明附前提、退化反例；每套2道教师侧完整例题、3级提示、近远迁移。
- 12道例题通过独立 SymPy 精确核对；32对正面/反面有限精确数学见证，总计64次有限检查。有限见证并非通用定理形式证明，更非学生任意步骤认证。
- q=0 可用于有限幂级数代数表达式，但不是高中常规非零相邻比值定义的等比数列；q=1另行分类讨论。术语仍待真实教师裁决。
- 源哈希、轨道、候选先修ID、非法审核字段和学生答案泄漏负例均纳入门禁。本批新增内容维持 REVIEW_PENDING / TEACHER_ONLY；教师批准0，学生权威知识发布0。

## 在 Mac 真实执行的测试
- bash scripts/mac_check.sh：外层退出码0；其中后端 Python pytest 66293 passed / 5 skipped / 1 third-party deprecation warning / 0 failed；Node 111 passed / 0 failed。
- 本批独立专项 pytest：142个课程门禁测试+33个证明/例题测试=175 passed / 0 failed。这175项与后端全量 pytest 是独立命令，不混淆或重复计算。
- bash scripts/mac_browser_check.sh：外层退出码0，Chrome/Playwright完整回归通过，浏览器pytest 2 passed；iPad触控、笔压为浏览器模拟，非实体硬件验证。
- 无外部模型API、真实学生数据或未经许可的教材文字提交。第三方弃用警告保留在原始日志。

## 原始证据及 SHA-256
| 文件 | SHA-256 | 字节 |
|---|---|---:|
| docs/evaluation/logs/KB_BATCH120_MAC_CHECK_FINAL.log | b71a03f5db85848879fab445808c4c6d32244a19f978ac60f3652b2cc67306f5 | 117946 |
| docs/evaluation/logs/KB_BATCH120_MAC_CHECK_EXIT.txt | e432c692893a6084b0de1a2f61b2b6b58c76467f569e718103e1ad2475ca86cc | 17 |
| docs/evaluation/logs/KB_BATCH120_BROWSER_FINAL.log | 810cfb6a49a17f4d0d3059bcefb0bb0bf65e9ced6553f5e0426eee676df8d3a7 | 2443 |
| docs/evaluation/logs/KB_BATCH120_BROWSER_EXIT.txt | cd7bb7b450e28b0363caa1125cee49f03510a088e23f9073ae70351e72a7f067 | 15 |

## 七轨候审计数（非官方知识原子分母）
| 轨道 | 本批新增候选 | 累计候选 | 正式分母 |
|---|---:|---:|---|
| COMPULSORY | 12 | 21 | UNKNOWN |
| ELECTIVE_A | 8 | 14 | UNKNOWN |
| ELECTIVE_B | 8 | 12 | UNKNOWN |
| ELECTIVE_C | 8 | 14 | UNKNOWN |
| ELECTIVE_D | 8 | 12 | UNKNOWN |
| ELECTIVE_E | 8 | 12 | UNKNOWN |
| SELECTIVE_COMPULSORY | 12 | 28 | UNKNOWN |

## 未完成与风险
- 七轨正式官方分母 UNKNOWN×7，真实教师原子化/签名未完成。
- 405条排版线索中261条未关联；历史172条待审先修、538条未认证证明步骤、10项数学冲突不能自动视为清零。
- 所有候审稿须经过专业教师人工审阅；形式化检验外的命题和学生步骤仍未验证；不允许进入学生权威知识检索。
- 远端GitHub CI最终状态须独立核验，不可把Mac本地通过视作GitHub workflow通过。

## 下一批（K00→K01/K07→K02–K06→K08/K09）
1. 对未关联261条来源线索做语义拆分/合并、跨页去重及七轨独立分母审查；使用来源图像复核转轨、公式排版错位，不凭关键词猜测知识点。
2. 对历史高风险先修和证明批量审查，区分条件正确、有限见证和不支持形式验证，记录真实错误与反例。
3. 将新的原子候选转为按章成组的完整原创讲义和题族，增加合法性解释、两道例题、错法、提示、近远变式。
4. 更新Agent检索索引和学生防剧透测试，保持0自动审批；全量Mac测试、原始证据和GitHub Draft PR快进交付。
