# STEM Mentor｜Batch146 真实Mac开发、数学内容、源码与验收记录

仅授权MacBook Air参与知识库源码、数学内容与测试。独立 worktree：
`~/Documents/文件/stem-mentor-kb-batch146`，分支 `feat/kb-batch146-rigorous-math-cases`。
基于已核实GitHub Batch144 commit `c07c2d0a45dccb01319f5b594539d28cf0355782`；本批源码commit `d3ea06ec07b723fcda8196f83237442f189e53c7`。
主仓原有未提交修改、其他worktree未覆盖；Tang未参与开发。

## K00/K01 来源与真实覆盖边界
- 私有原始课标PDFKit来源行在Mac重新哈希，与提交的来源位置和SHA-256一致；版权原文未入库。
- 239是**历史编辑课程线索**而非国家课标知识原子分母：44条关联稿，195条缺完整候审稿。
- K00别名专项审计：7个同页同源段组牵涉19条候选，17个共享版式cue组、其中跨页共用cue为0组；该0不代表完成跨页语义核对；全部保留人工裁决，自动合并为0。
- 原有75份加新增10份共85份原创教师候审稿，选修E内容明确是学校选修示例。
- 必修、选择性必修及选修A–E的真正官方原子分母全部 UNKNOWN；正式教师批准0、学生权威发布0。

## K02–K06 十份真实原创内容
- 必修：复数代数形式相等与实虚部；二分法保留异号区间；弧度与圆弧长度。
- 选择性必修：数学归纳法；有序排列与无序组合。
- 选修A：拉格朗日中值定理；选修B：连续概率密度；选修C：相容性和完备性。
- 选修D：黄金分割精确比与斐波那契近似；选修E：学校自主选修的整数同余。
- 每单元严格保留适用域和假设、分步依据、错误用法/反例、20道完整教师例题、30层安全提示、20个近远迁移任务。均REVIEW_PENDING/TEACHER_ONLY。

## K07/K08/K09 数学与权限核验
- 独立SymPy有限/精确样例40/40：20合法/边界见证，20无效前提拒绝。有限见证并非全称命题形式证明。
- 本地编辑FTS5临时索引包含85份稿件但检索结果只列ID/轨道/状态/排名，不能作网络授权凭证；学生未批准证据一律拒答。
- FastAPI `/api/knowledge/kb146-review-coverage`只返回七轨聚合及UNKNOWN分母，无教师解答。
- 首轮266项负面回归出现10项失败：source PDF SHA字段可被篡改而没有被validator拒绝。首次失败的原始日志未归档，此数字为当时调试记录；已补充原始PDF SHA强制验证，复跑266项成功的日志已归档。
- 仍有历史538个未认证证明步骤、10项未裁决数学冲突；自动批准/发布一律为0。

## 授权Mac真实测试
| 项目 | 结果 |
|---|---|
| 独立本批专项 | 266 passed（1条Starlette第三方弃用警告） |
| K00来源重复片段专项 | 44 passed，7组共同原文段仍待语义裁决 |
| 已归档日志防篡改回归 | 5 passed，覆盖退出码、日志缺失、假通过数字、PDF重放假标记 |
| 脚本内专项 | 266 passed；与独立专项重复，不累计 |
| 全量后端Python | 66,293 passed，5 skipped |
| Node | 111 passed |
| Chrome/Playwright + browser pytest | exit 0，2 passed；不是实体iPad验证 |
| 原始Mac私有PDFKit逐行SHA | PASS，未上传PDF原文 |
| 数学独立Oracle | 40/40；不等于普适形式认证 |

## 真实执行日志与字节哈希
| 日志 | exit | SHA256 | bytes |
|---|---:|---|---:|
| `docs/evaluation/logs/KB_BATCH146_FOCUSED.log` | 0 | `20162152176c5fc0bb02403e297856b852ad788f849d6c238603e6c0b3c454f1` | 870 |
| `docs/evaluation/logs/KB_BATCH146_K00_FOCUSED.log` | 0 | `dfa2935ee9f7ca0c213f197accb60de6d4aa18cdef307ade0b8e817280d4f5c0` | 99 |
| `docs/evaluation/logs/KB_BATCH146_MAC_FULL.log` | 0 | `0122f2a4954a64d65fc18cfda18ce7e47842a470b0d68a90fcc2565efad2dbfb` | 138517 |
| `docs/evaluation/logs/KB_BATCH146_BROWSER.log` | 0 | `bdcf4d6af36a02c203eddf1762e4f80c530f08429459bd26d380622019e7dec0` | 2443 |

GitHub Actions只能检查**提交的日志哈希和Schema/数学CI**，不能冒充重放Mac独有的授权PDF。最终GitHub Actions是否通过须单独查看对应commit和workflow。

## 下一批
- K00：真实编号要求的原子拆分、相邻页去重、课程内容与选修边界审计，争取冻结可追溯的七轨分母。
- K02–K06：对195条仍无候审深度稿的编辑线索继续逐模块补内容，同时防止误将线索直接当官方知识点。
- K07：538历史未形式认证步骤与10冲突的真实数学裁决；K08未见题检索/拒答；K09教师审签与发布门禁。
