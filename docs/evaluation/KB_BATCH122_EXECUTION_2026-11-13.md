# STEM Mentor Batch122：Mac 源码、课程与数学验收记录

- 日期：2026-11-13，开发/内容/测试机器仅授权 MacBook Air，独立工作树 stem-mentor-kb-batch122。
- 冻结源代码提交：fc9c3f0bc0826d68f0a2d0e0b7e2245c1c850b72，冻结源代码 Git Tree：6ad470addd387580a7ccdbacbad0944622043c90。以下日志在该源代码版本运行完毕后归档。
- GitHub Draft PR：https://github.com/YOUessi/stem-mentor/pull/147。远端 CI 状态必须另行核对，不因 Mac 全绿推断 CI 通过。

## 一、内容、课标与边界

- K00：32条原创语义候审提案，累计175条；有精确来源哈希、课标归属、应用条件及无效情形。
- K00/K01：405条课标排版线索均机器留痕；206条已关联候审提案、199条未关联。TOPIC/SUBTOPIC/NUMBERED仅为抽取标签，并非官方课程原子。七轨正式官方课程原子分母均 UNKNOWN。
- K02–K05：8份原创教师候审数学讲义：补集、充要条件、分段函数、连续函数零点存在、二项分布、超几何分布、Pearson相关系数、齐次线性系统。每份有形式陈述、前提、解释步骤、退化或反例、错法、2道教师例题、三级提示、近远迁移。
- K06/K07：16道例题有限精确检查、8项失效条件反例、8项跨主题边界检验。一般定理形式化认证0、自由文本学生步骤认证0。有限算例不能替代一般证明。
- K08/K09：拒绝伪来源、伪官方分母、跨轨、先修孤儿、伪教师批准和完整教师解答泄漏。内容 REVIEW_PENDING / TEACHER_ONLY；真实教师批准0；学生权威发布0。
- 主仓已有未提交修改仍保留；不使用 Tang；不强推、不合并 main；不上传学生隐私或课标整页版权文本。

## 二、Mac 本轮真实测试

| 命令 / 验收 | 结果 |
|---|---|
| scripts/mac_check.sh | 外层 EXIT 0；Python backend 66293 passed, 5 skipped, 1 warning；Node 111/111 passed，0 failed |
| Batch122 定向 pytest | 503 passed，计入 mac_check.sh 内的专项部分；不与 backend 全量混算 |
| scripts/mac_browser_check.sh | 外层 EXIT 0；Chrome/Playwright 多场景回归及 browser pytest 2 passed |
| 课标与数学 | 本地来源原件验证、生成器 --check、结构门禁、数学边界和负面回归 |
| 适用限制 | 浏览器模拟触控笔并非实体 iPad 测试；模型API未调用；数学有限见证不等于教师审核 |

## 三、原始日志及SHA-256

| 文件 | SHA-256 | 字节 |
|---|---|---:|
| KB_BATCH122_MAC_CHECK_FINAL.log | a02fcfdf30706b9af4d4c76b8360e0eac5ed4a26d73d4ed1398e536f70482225 | 119577 |
| KB_BATCH122_MAC_BROWSER_FINAL.log | 6b4a0a715b070baf0a04146a56fcc254920d6735c186aee8a746fa97c6e2346d | 2528 |
| KB_BATCH122_MAC_CHECK_EXIT.txt | 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa | 2 |
| KB_BATCH122_BROWSER_EXIT.txt | 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa | 2 |

## 四、未关联来源线索的下一批集中页

| 轨道 | 线索数 | 印刷页分布最密集处 |
|---|---:|---|
| COMPULSORY | 88 | p22(10), p32(10), p20(9) |
| SELECTIVE_COMPULSORY | 25 | p44(7), p42(5), p47(4) |
| ELECTIVE_A | 36 | p57(10), p55(9), p53(6) |
| ELECTIVE_B | 34 | p60(13), p62(8), p58(5) |
| ELECTIVE_C | 11 | p68(5), p66(3), p69(2) |
| ELECTIVE_D | 5 | p72(3), p71(1), p73(1) |
| ELECTIVE_E | 0 | 无 |

这些是待判别的排版线索，不是缺少的数学原子数量。下一批优先必修p22/p32/p20、选择性必修p44/p42/p47、选修A p57/p55、选修B p60/p62，人工核对跨页、复合公式与课程要求，再决定拆分、合并、非原子剔除。继续原子分母全量建设、数学前提和关系审查、整模块讲义与题族扩展。

历史待审先修172、未认证证明步骤538、数学冲突10（历史快照，待新一轮审计复核）。七轨课标正式原子总分母未知，教师批准和学生权威发布仍为0。当前只能宣告代码级候审交付，不能宣告知识库正式完成。
