# STEM Mentor Batch123｜Mac 课程语义候审与数学检验交付报告

- 执行日期：2026-11-13。唯一开发、内容生产和真实测试设备：授权 MacBook Air；工作树：stem-mentor-kb-batch123。
- Mac 冻结源码 commit: `58e295e160b6f5cb30dd02fbd9bddbd9a3dfd115`；源码 Git Tree: `e275a341de442113ebb678b8ef773b9afd174535`。
- GitHub 对应远端源码 commit: `d8946b1375be4fb9f40fa96c642e42b6c9fc9c10`；已核对远端 Git Tree 与 Mac 冻结树一致。
- GitHub Draft PR: https://github.com/YOUessi/stem-mentor/pull/148。GitHub Actions 最终状态必须单独核验，不以本地全绿替代远端CI。
- Mac 主仓原有未提交修改保留；两份历史评测快照因测试发生未提交变化，没有混入本次交付。不在 Tang 开发，不强推，不合并 main。

## 1. K00/K01：课程来源与范围真值

- 对61页已圈定课程范围、405条排版线索维护七轨机器审计处置台账；批量建立32条来源锁定原创语义候选，总候选增至207。
- 238/405条排版线索已关联候选，167条尚未完成语义判别；未关联不是正式缺失原子个数。抽取器 TOPIC/SUBTOPIC/NUMBERED 是排版提示，不能自动提升为课程原子。
- 七轨分别计数已入 `KB_BATCH123_COVERAGE.json`，正式官方知识原子总分母仍然 UNKNOWN，正式完成百分比不计算。
- 源行哈希、本地来源指纹、分轨、先修关系、重复ID、伪APPROVED、伪官方总数、教师答案公开等均设置拒绝门禁。

## 2. K02/K03/K05/K06：原创教学讲义与题族

- 8份完整原创教师候审讲义：函数奇偶与定义域、对数换底、二分法、直线圆位置、有限极限四则、直线和平面关系、非平行空间直线距离、三阶行列式与线性相关。
- 每份包含形式定义/陈述、量词与符号、应用域、为何成立、逐步依据、边界或反例、典型错误及原因、2道教师精解、3级提示和近远迁移。
- 16道精确示例、24级提示、8组失效反例及16项近远迁移，均为 `REVIEW_PENDING / TEACHER_ONLY`；教师正式批准0。
- 对数对不同底数下数据顺序的解释，应在后续审校明确区分底数 >1 的递增与 0<底数<1 的递减；不得无条件泛化。空间直线距离讲义覆盖相交的非平行情况，标题中的“异面”术语也须教师审校。

## 3. K07/K08：数学验证和教学安全

- 独立 SymPy 有限精确校验16道教师例题、8项前提失效、8项跨主题边界。数学见证属于可复核算例，不是一般定理形式证明。
- 不能由模型断言某个学生自由解题步骤已验证；自由文本学生步骤自动认证0。
- 学生端 `student_authoritative=false`，教师完整解答不注入学生独立挑战检索。API 模型真实对照和后续教师审校均未完成。

## 4. Mac 真实测试

| 命令/验收 | 结果 |
|---|---|
| `scripts/mac_check.sh` | EXIT 0；Python 66,293 passed / 5 skipped / 1 third-party warning；Node 111/111 passed |
| `tests/test_kb_batch123_scope_depth_math.py` | 516/516 passed；专项在全量中也被执行，不能再次与全量相加 |
| `scripts/mac_browser_check.sh` | EXIT 0；Chrome/Playwright回归通过、浏览器pytest 2 passed |
| 来源、产物、数学 | 本地合法课标来源核验、两个生成器 `--check`、负例和审核安全门禁 |
| 限制 | 浏览器触控笔为模拟，非实体iPad；本轮无真实模型 API、无教师批准 |

## 5. 六份原始日志 SHA-256 与字节数

| 文件 | SHA-256 | 字节数 |
|---|---|---:|
| KB_BATCH123_MAC_CHECK_FINAL.log | `e4564053e431b389a8c5094c07da373b0270f045afbc0063a65c910f11214e1f` | 120345 |
| KB_BATCH123_MAC_CHECK_EXIT.txt | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | 2 |
| KB_BATCH123_BROWSER_CHECK_FINAL.log | `5322c034d3f640dba81a0c00345476fe89dc7992a5982625fcd1a03fd725c4eb` | 2443 |
| KB_BATCH123_BROWSER_CHECK_EXIT.txt | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | 2 |
| KB_BATCH123_TARGETED_FINAL.log | `51b91116fe6e1c16c671b2f40df9c006afa202b3501d581077d97ab014fd7026` | 660 |
| KB_BATCH123_TARGETED_EXIT.txt | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | 2 |

## 6. 下一批优先

- 重点审查剩余167条排版线索及前后页合并/多原子拆分，明确排版提示的 `非原子`、`重复`、`需拆分` 原因；不能从207份候选推断正式课标全量分母。
- 优先回查必修76条、选择性必修19条、选修A31、B29、C9、D3，分别提供页码、证据和候审原子关系。
- 集中推进172条历史待审先修关系、538条未认证证明步骤、10项数学冲突的真实逐项裁决（数字为历史队列，不能当作本批新增或本批已处理）。
- 继续整模块深度讲义、错因反例、条件验证、检索API冻结评测及教师审校；全部条件满足前保持知识库课程总任务OPEN。

**结论：此批完成了可验证的原创候审内容和安全工程交付；正式课程全量覆盖、教师批准与学生权威发布仍未完成。**
