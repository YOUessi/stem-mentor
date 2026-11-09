# Batch51｜K00 原始课标证据页覆盖与 12 条非等价旧稿关联

## 证据与严格边界

- 原件 SHA256：`cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`；Mac 上对原始 PDF 的 61 个课程内容印刷页进行了 PDFKit 逐页提取和 SHA 指纹校验，原文未入库。
- 来源存在 317 个编号标记**出现次数**及 D/E 23 个未编号主题提纲，**340 不是官方原子数，也不是完整课程目标数**。
- 自编 313 个编辑候选（301 份直接待审、12 条仅历史关联）也**不是**正式课程分母；七轨道的官方原子分母和正式覆盖率继续为 null。
- 逐页文本指纹仅证明读取了锁定 PDF 的页面，不证明教研已逐页审查；完整教师批准 0，学生端正式发布 0。

## 15 个编号抽取器盲区页（按原件起始内容初筛）

| 印刷页 | 现有编号出现 | D/E主题 | 项目候选 | 初筛性质（不代表正式审查） |
|---:|---:|---:|---:|---|
| 13 | 0 | 0 | 0 | COURSE_STRUCTURE |
| 14 | 0 | 0 | 0 | COURSE_HOURS_TABLE |
| 18 | 0 | 0 | 0 | TEACHING_GUIDANCE_WITH_CONTENT |
| 24 | 0 | 0 | 0 | TEACHING_GUIDANCE_WITH_CONTENT |
| 30 | 0 | 0 | 4 | GEOMETRY_TEACHING_GUIDANCE_WITH_CONTENT |
| 34 | 0 | 0 | 5 | ACHIEVEMENT_REQUIREMENTS |
| 35 | 0 | 0 | 0 | PDFKIT_TEXT_CORRUPTION_VISUAL_REVIEW_REQUIRED |
| 36 | 0 | 0 | 0 | MODELLING_ACTIVITY_GUIDANCE |
| 37 | 0 | 0 | 0 | SELECTIVE_STRUCTURE_TABLE |
| 41 | 0 | 0 | 2 | ACHIEVEMENT_REQUIREMENTS |
| 45 | 0 | 0 | 2 | GEOMETRY_TEACHING_GUIDANCE |
| 49 | 0 | 0 | 0 | PROBABILITY_TEACHING_GUIDANCE |
| 50 | 0 | 0 | 3 | MODELLING_CONTENT_REQUIREMENTS |
| 51 | 0 | 0 | 0 | ELECTIVE_TRACK_SELECTION_RULES |
| 65 | 0 | 0 | 5 | ALTERNATE_ARABIC_NUMBERING_MISSED_BY_MARKER_EXTRACTOR |

其中 34、41、50 页包含对学习或内容的要求而无原编号标记；65 页存在不同于旧提取正则的阿拉伯式章节编号。35 页 PDFKit 字符流损坏，但在 Mac 上通过原件页面渲染已**确实看到数学建模循环图、探究活动和必修课题研究要求**；该观察不等于教师逐条审核。

## 第 35 页新发现的 7 条原子化编辑候选（全部非官方认证）

原件图像只在 Mac 临时目录读取，未提交版权页面；图像 SHA256 与 7 条原创改写见 `curriculum/highschool_math/k00_batch51_page35_modelling_candidate_split.json`。候选包括问题数学化、假设与变量、模型求解、现实检验与修订、计算正确性与现实适切性、探究猜想与证据、完整课题研究。它们仍须与 34–36 页去重、逐条教师审核，**不加入已核准官方原子分母，不算完整新讲义**。

## 12 条历史旧稿关联：只能做待审来源定位

| 编辑候选 | 轨道 | 印刷页 | 课标来源核查类别 | 教师/数学等价 |
|---|---|---:|---|---|
| KB33-A-P052-A001 | ELECTIVE_A | 52 | DIRECT_SCOPE | REVIEW_PENDING / NOT_CERTIFIED |
| KB33-A-P052-A002 | ELECTIVE_A | 52 | DIRECT_SCOPE | REVIEW_PENDING / NOT_CERTIFIED |
| KB33-A-P052-A003 | ELECTIVE_A | 52 | DIRECT_SCOPE | REVIEW_PENDING / NOT_CERTIFIED |
| KB33-A-P053-A002 | ELECTIVE_A | 53 | PARTIAL_DERIVATION | REVIEW_PENDING / NOT_CERTIFIED |
| KB33-A-P053-A004 | ELECTIVE_A | 53 | DIRECT_SCOPE | REVIEW_PENDING / NOT_CERTIFIED |
| KB33-A-P057-A002 | ELECTIVE_A | 57 | TOPIC_ONLY_NOT_EXPLICIT | REVIEW_PENDING / NOT_CERTIFIED |
| KB33-B-P058-A004 | ELECTIVE_B | 58 | TOPIC_ONLY_NOT_EXPLICIT | REVIEW_PENDING / NOT_CERTIFIED |
| KB33-B-P059-A002 | ELECTIVE_B | 59 | TOPIC_ONLY_NOT_EXPLICIT | REVIEW_PENDING / NOT_CERTIFIED |
| KB33-C-P065-A001 | ELECTIVE_C | 65 | DIRECT_SCOPE | REVIEW_PENDING / NOT_CERTIFIED |
| KB33-C-P066-A004 | ELECTIVE_C | 66 | DIRECT_SCOPE | REVIEW_PENDING / NOT_CERTIFIED |
| KB33-D-P071-A002 | ELECTIVE_D | 71 | CONTEXTUAL_APPLICATION | REVIEW_PENDING / NOT_CERTIFIED |
| KB33-E-P073-A004 | ELECTIVE_E | 73 | LOCAL_ELECTIVE_OPTION | REVIEW_PENDING / NOT_CERTIFIED |

## 下一批处理顺序

1. 结合原件图像对 35 页重读；复查 34/41/50/65 页未编号内容，抽取语义完整的原创教学目标草案并保留行/页锚。
2. 扩展到 61 页的每条编号要求、未编号要求、学业要求及探究任务，标注主题/领域/可选性/年份/课程轨道；教师独立核对后冻结每轨原子分母。
3. 将 12 条历史关联分别替换为独立数学范围核查，证明类逐步审查前提与结论、反例和越界条件，不得借相同页码判定数学等价。
4. 课程未获教师签字前，始终禁用未批准内容的正式学生 RAG 和挑战答案输出。
