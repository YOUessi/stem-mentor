# STEM Mentor｜Batch144 授权Mac源码、教学内容与真实验收

全部源码和内容仅在授权Mac独立worktree feat/kb-batch144-seven-track-source-lessons 实作，基于GitHub Batch143远端提交 95d8ea9b1a65d2b05281e97e2be27c113e1908b2；Tang未使用。
本报告记录原始Mac执行、日志哈希和事实边界；不能用GitHub CI结果代替教师签字。

## K00/K01/课程关联
- 239个来源候选只是历史编辑线索，不是中国高中数学官方知识原子分母。
- 既有65份加新10份，共75份未审核原创候审讲义；其中34条候选直接匹配，205条尚未关联完整候审稿。
- 必修、选择性必修、选修A–E七轨国家课标原子分母仍UNKNOWN，批准/发布均0。

## K02–K06 十篇完整新增原创稿
- 必修：向量三角形法则、元素属于与单元素集合、周期与最小正周期。
- 选择性必修：等差通项与恒差条件、圆的标准方程及退化。
- 选修A：子空间闭合；选修B：线性相关非平凡系数；选修C：有效期利率与复利还款；选修D：理想纯音；选修E：机器人坐标变换顺序。
- 20道完整教师例题、30级学生安全提示、20项近/远迁移；逐步推理/反例/错误解法/适用条件和来源指纹均保存。全部REVIEW_PENDING/TEACHER_ONLY。

## K07/K08/K09 验证、检索与隔离
- 独立40/40有限或符号精确见证：20合法/边界、20失效前提，普适形式认证0。
- 编辑端本地FTS5仅暴露来源ID、课程、候审状态及排序，不作为网络权限鉴别；没有新增学生公开草案搜索接口。
- FastAPI新增 /api/knowledge/kb144-review-coverage 只返回聚合七轨状态，不返回教师例题/答案。学生证据查找仍NO_APPROVED_EVIDENCE。
- 第一轮227项专项发现11项失败：旧65份草案中某些没有title字段引发编辑检索KeyError；一个隐私断言把安全聚合布尔字段名误判泄漏。均修复后重新完整运行227项通过。

## 授权Mac实际测试
| 检查 | 真实结果 |
|---|---|
| 本批专项pytest | 227 passed；1条第三方弃用警告 |
| 完整Python后端 | 66,293 passed；5 skipped |
| Node | 111 passed |
| Chrome/Playwright | 退出码0；browser pytest 2 passed（不等同实体iPad） |
| 许可课标原始PDFKit行哈希 | 本机重算通过；原文未上传 |
| 独立数学Oracle | 40/40（含20项非法前提） |
注意：专项227项在完整Mac脚本中再次运行，不与全量测试简单叠加。

## Mac原始日志及哈希
| 日志文件 | exit | SHA256 | bytes |
|---|---:|---|---:|
| docs/evaluation/logs/KB_BATCH144_FOCUSED.log | 0 | d125ebc11c196915f0984ce54ec26a52e8a085b6f3d3a8da23c405004c346c6b | 870 |
| docs/evaluation/logs/KB_BATCH144_MAC_FULL.log | 0 | 5dad7dfcdce34e4c96e9409e389c7f599b8cbc569cee6494c03dcca197e0ac27 | 137301 |
| docs/evaluation/logs/KB_BATCH144_BROWSER.log | 0 | a645ca74eecc561c0619c4620be876bea0877faf6d771a4551cfd848d5728e46 | 2443 |

GitHub CI仅验证已提交的证据数据/日志哈希，不重放Mac本地版权PDF。GitHub远端commit及CI另行核查；不伪报已合并main。

## 后续关键缺口
- K00继续真实编号要求语义拆分/跨页重复与选学范围审核，冻结各轨官方分母；仍未完成。
- K07历史538条未形式认证证明步骤及10项数学冲突需要实质一般证明与裁决，有限见证不能代替。
- K02–K06沿205个候选缺口铺开整模块稿件；K08推进未见题Agent评测、引用与条件拒答；K09需要真实教师审校/发布门禁。
