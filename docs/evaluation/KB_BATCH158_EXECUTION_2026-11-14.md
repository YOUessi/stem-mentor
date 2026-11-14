# KB158｜Mac真实执行与课程审查证据（2026-11-14）

本批源代码Git commit：ad9bb26d499a9a801c2255edf3169d8fc923a27c；最终远端PR及SHA另于GitHub核验记录。
在MacBook Air独立worktree中新增10份完整原创教师候审稿：必修有理指数幂、三角和差恒等式、均值/中位数/众数；选择性必修空间距离和Pearson相关；选修A极限ε–δ、B二维联合分布、C相关与因果、D几何对称、E大学先修概率案例。
10份共20道教师例题、30级学生提示、20项近远迁移，全部REVIEW_PENDING/TEACHER_ONLY。
K00对61页记录315个非原子排版来源标记、32个CDE未编号提案、89条边界关系，按页分流；七轨原子分母仍UNKNOWN，没有虚假课标完成率。
239条编辑线索：134条已有候审稿、105条尚未关联完整稿；累计175份教师候审、批准0、学生权威发布0。
K07原有40项SymPy有限见证（20负面）外，本批增加独立20道教师例题逐题精确重算与41项反篡改/失败Oracle测试；60项有限校验不构成一般证明。
本批的作者字段、课程证据哈希和受控摘要可由编辑本地FTS检索；学生端仍NO_APPROVED_EVIDENCE，教师例题/解答不进入索引。

## 真实Mac测试（测试有重叠，绝不直接求和）

| 项目 | 结果 |
|---|---|
| Python全量后端 | 66,293 passed, 5 skipped |
| Node | 111/111 passed |
| Batch158原专项 | 728 passed |
| 新增例题Oracle与防篡改单独测试 | 41 passed |
| Batch158原专项＋新增Oracle合并 | 769 passed |
| SymPy与独立例题有限验证 | 40+20项；20项错误前提拒绝 |
| Chrome模拟与浏览器pytest | 9交互组，2 passed，非实体iPad |
| 原始授权Mac PDFKit复核 | PASS，未上传PDF正文 |
| 完整Mac脚本退出码 | 0 |

## 原始stdout、退出码及SHA-256

| Mac运行 | 退出码 | 日志字节 | 日志SHA256 | exit SHA256 |
|---|---:|---:|---|---|
| BROWSER | 0 | 2443 | 74fcb3c21615a0edd0d6ccf476d98420eeb8ae7dbb3d7dd6ea1427a194e5bfb8 | 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa |
| COMBINED | 0 | 1431 | 0e8a07d949a72c5d378ca5e67340c980f35c1f0a758469760908dd454c65d128 | 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa |
| FOCUSED | 0 | 1431 | da7d761869d8005e45be27ffb96136924924be80ae1e6d3766fabd42ab7554f3 | 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa |
| MAC_FULL | 0 | 156690 | f5883d04e7d4eed5d8efa21aa3186f0e64bac973689c756a358237898e61f5fb | 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa |
| NODE | 0 | 20924 | 54019ded3ec356e7683e3e354bee82e7cf6575f00dcec0a75bb2e1f4b0f4a9d1 | 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa |

五套日志和退出码逐字节归档；负面测试会检测篡改/缺失。最终GitHub Actions结果需另行核查。

## 尚缺的最终DoD

K00继续原文课程要求逐句拆分、跨页语义等价/包含裁决，冻结七轨正式原子分母；K02-K06补105条历史线索；K07核查538项未获得一般形式认证的证明步骤和10项冲突；K08完成冻结未见题API-vs规则基线评测；K09需真实教师逐篇审核后方可发布。
