# STEM Mentor｜Batch147 MacBook Air 原创课程、来源边界、数学验证与交付报告

本批仅在授权 MacBook Air 的独立工作树开发、编写与执行；没有使用 Tang、合并 main 或改写既有历史。
源码分支：feat/kb-batch147-source-depth-next；原始主仓未提交内容未进入本批。
源起Git SHA：`fad0d2a4fb3e8349f7785fd96277fdea751a8604`；本批源码SHA：`35e825141ac5f0223d1f4a1b6cb0901089907248`。

## K00/K01：课标来源与可审计缺口
- 课程基准：教育部2017年版2020年修订课标；原始许可188页PDF仅保存在Mac，源页/行PDFKit SHA重放通过，不上传版权原文。
- 历史239条只是编辑来源线索，并非国家完整官方原子分母；本批新增10份课程讲义来源绑定后，54条已联候审稿、185条缺稿。
- 建立239候选的逐条来源元数据审查图、同页区间重叠及相邻页首尾连续线索，产生89条待裁决的元数据关系记录，涉及69对不同候选；20条记录对应重复候选对的另一种关系标签。
- 同页/相邻页元数据相似只是审查提示，不自动合并或证明同一官方知识原子；七轨正式原子分母仍全部UNKNOWN，所有审核未通过。

## K02–K06：10份完整原创教师候审讲义
- 必修3篇：复数非零除数与共轭有理化；不共线三点唯一确定平面；样本空间、事件并交补和非等可能条件。
- 选择性必修2篇：正整数指标域上的数列；等差数列前n项和倒序配对证明。
- 选修A：数列极限ε-N定义；B：导数与速度加速度的单位；C：命题、开放句与量词；D：几何形态不变量和审美边界；E：机器人二维坐标变换，明确标记学校拓展示例。
- 每篇含形式陈述、全部使用前提、4步论证、非例/失效边界、典型错法与修复、2道完整教师例题、3级安全提示、近远迁移。新增20例题、30级提示、20项迁移。
- 累计95份REVIEW_PENDING/TEACHER_ONLY；没有真实教师审校；学生默认拒答未获批准证据。

## K07/K08/K09：数学正确性和Agent安全
- 独立SymPy/有限精确见证40/40，其中20合法或边界样例、20前提失效拒绝；不能当普遍定理形式证明。
- 编辑本地FTS5检索覆盖95份未审核讲义，只返回ID/轨道/审查状态及排序；学生端返回NO_APPROVED_EVIDENCE。
- FastAPI /api/knowledge/kb147-review-coverage仅暴露聚合数量，绝不返回教师详细解法。
- 初次专项运行1项失败，因校验入口名称oracle/exact不一致；修正后283项专项通过。该失败的初次原始日志未归档，不能冒称已有失败证据文件。
- 归档日志防篡改负面测试首次6项失败：临时测试目录不在仓库内，错误使用Path.relative_to(ROOT)；修复固定逻辑路径并读取测试副本。保留失败日志，修复后独立6/6通过。
- 仍有历史538条未经普适形式认证的证明步骤和10项待裁决数学冲突。

## Mac真实测试
| 项目 | 结果 |
|---|---|
| Batch147全部增量 | 283 passed（1条第三方弃用警告） |
| 独立K00复跑 | 17 passed（与283有重叠） |
| Mac脚本专项 | 266+17 passed（与增量重叠，不累计） |
| 原始PDFKit源行SHA重放 | PASS，许可原文未上传 |
| 后端Python全量 | 66,293 passed，5 skipped |
| Node | 111 passed |
| Chrome交互与浏览器pytest | Chrome 9 passed，pytest 2 passed（非实体iPad） |
| 完整Mac脚本与浏览器脚本退出 | EXIT 0 / EXIT 0 |

## 原始Mac日志与退出码字节摘要
| 日志 | exit | SHA-256 | 大小bytes |
|---|---:|---|---:|
| `docs/evaluation/logs/KB_BATCH147_FOCUSED.log` | 0 | `9ab268cd98e6332e2eb92551e21716cef2a9e501a9db8e57c6b3912af5be1474` | 1371 |
| `docs/evaluation/logs/KB_BATCH147_K00_FOCUSED.log` | 0 | `27c0bdfebd9aed45a4a7eabfb53578bc1153ad032375aa5233cde0e09a73a6d5` | 222 |
| `docs/evaluation/logs/KB_BATCH147_MAC_FULL.log` | 0 | `b695dbef946e5e94796557a37553a81ee04f25c40ea3ea85c1cc067a94da685f` | 140011 |
| `docs/evaluation/logs/KB_BATCH147_BROWSER.log` | 0 | `fdee866ec684d54c1da686c0d6be3a86ced6a6be5a50477108a2baa0063fc477` | 2443 |

### 归档证据负面测试的首次失败与修复重跑（均真实保留）
| 执行 | 退出码 | SHA-256 | 大小bytes |
|---|---:|---|---:|
| `docs/evaluation/logs/KB_BATCH147_ARCHIVE_NEGATIVE_INITIAL_FAILURE.log` | 1 | `18bc9069de0e97100ff7532646bb56d2a0e0cffff833e3566e29e5a9be0225bb` | 20542 |
| `docs/evaluation/logs/KB_BATCH147_ARCHIVE_NEGATIVE.log` | 0 | `90babf3ab035b63651f6f642d26e6c3a37e6c323504366391afbc3a507818fc3` | 98 |

本报告中版本化的日志可用于GitHub重新校验退出码、数学测试和摘要；GitHub runner不能替代授权Mac上许可课标的PDFKit重放。

## 下批优先项
- K00：继续对正式编号课程要求做逐句原子化与跨页语义判定，由真实教师审核后才能冻结七轨分母。
- K02–K06：沿185条缺稿的历史编辑线索拓展完整讲义，重新对齐正式课标与题族结构。
- K07：处理538条历史形式认证缺口、10项冲突的真实数学裁决。
- K08/K09：未见题结构检索对照、数学前提拒答、教师签核和逐章发布门禁。

当前发布状态：0教师APPROVED；0学生权威发布；0自由文本学生步骤认证。
