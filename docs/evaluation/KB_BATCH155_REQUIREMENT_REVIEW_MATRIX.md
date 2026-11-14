# KB155｜全量已检出来源的机器可审核任务矩阵（非课标原子总数）

**来源锚不是知识原子；行重叠不是语义相同；候审讲义不是教师批准。**
来源PDF SHA-256: `cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195`。仅包含原创转述与来源元数据，不存储版权课标原文。

| 来源人口 | 本批机器对账结果 | 不能解释为 |
|---|---:|---|
| 61页中的编号排版标记 | 315 | 正式原子分母 |
| 已有暂定原子提案 | 41 | 已批准的原子 |
| 未编号C/D/E暂定提案 | 32 | 全国统一必修 |
| 历史编辑来源线索 | 239 | 未去重的知识总数 |
| 编辑候审讲义 | 145 | 上线可教原子 |
| 旧审计source_sha为空、已定位原提案source_lock | 41 | 重新数学认证或教师签字 |
| 跨页/同页待裁决来源关系 | 89 | 已确认等价/重复 |

## 七轨缺口（历史编辑线索，不是官方完成率）

| 轨道 | 编号标记 | 无相关行提案标记 | 编辑线索缺稿 | 候审讲义 | 未编号CDE提案 | 官方原子分母 |
|---|---:|---:|---:|---:|---:|---|
| COMPULSORY | 114 | 44 | 42 | 56 | 0 | UNKNOWN |
| SELECTIVE_COMPULSORY | 82 | 25 | 31 | 31 | 0 | UNKNOWN |
| ELECTIVE_A | 52 | 16 | 19 | 18 | 0 | UNKNOWN |
| ELECTIVE_B | 51 | 29 | 20 | 10 | 0 | UNKNOWN |
| ELECTIVE_C | 16 | 10 | 14 | 10 | 2 | UNKNOWN |
| ELECTIVE_D | 0 | 0 | 6 | 11 | 17 | UNKNOWN |
| ELECTIVE_E | 0 | 0 | 3 | 9 | 13 | UNKNOWN |

## 先核对高风险来源页

| 课标印刷页 | 编号来源 | 未关联行标记 | 编辑线索缺稿 | 来源风险 |
|---:|---:|---:|---:|---|
| 60 | 13 | 10 | 5 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 32 | 12 | 9 | 3 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 44 | 11 | 8 | 6 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 22 | 10 | 8 | 5 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 68 | 8 | 7 | 5 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 58 | 8 | 8 | 1 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 73 | 0 | 0 | 5 | CROSSPAGE_ELECTIVE_D_CONTINUATION, MIDPAGE_TRACK_TRANSITION, ZERO_NUMBERED_MARKERS_NOT_ZERO_REQUIREMENTS |
| 62 | 11 | 6 | 5 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 28 | 5 | 5 | 6 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 55 | 14 | 4 | 6 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 20 | 9 | 4 | 4 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 42 | 13 | 3 | 7 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 57 | 7 | 5 | 1 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 47 | 12 | 4 | 3 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 59 | 9 | 4 | 3 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 26 | 17 | 4 | 2 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 27 | 8 | 4 | 2 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 43 | 10 | 3 | 4 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 48 | 10 | 3 | 4 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 54 | 9 | 3 | 4 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 56 | 4 | 4 | 1 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 66 | 5 | 3 | 3 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 72 | 0 | 0 | 1 | CROSSPAGE_ELECTIVE_D_CONTINUATION, ZERO_NUMBERED_MARKERS_NOT_ZERO_REQUIREMENTS |
| 16 | 10 | 2 | 4 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 69 | 0 | 0 | 0 | MIDPAGE_TRACK_TRANSITION, ZERO_NUMBERED_MARKERS_NOT_ZERO_REQUIREMENTS |
| 23 | 4 | 2 | 2 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 39 | 11 | 1 | 5 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 21 | 6 | 1 | 3 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 29 | 2 | 2 | 0 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |
| 19 | 8 | 1 | 2 | NUMBERED_NO_ATOM_OR_LEAD_LINE_OVERLAP |

## 可执行审核顺序

1. 教研人员依据本地合法课标PDF的哈希/页码/行号，确认该来源是否真包含知识要求；未编号文字不能被跳过。
2. 逐句拆分数学对象、量词、限制条件与方法适用边界；正式知识ID仅在人工确认后赋值。
3. 审核89条来源关系的语义是否等价（含跨页衔接），禁止依据行重叠自动合并。
4. 依未匹配的135条历史编辑线索建设分模块原创讲义、题族及反例；审核数学证明后交教师签字。
5. 未完成七轨原子分母与真人审校前：正式课程覆盖率UNKNOWN、APPROVED=0、学生权威发布=0。

此文件由 `scripts/build_kb_batch155_review_matrix.py` 从已锁定的既有来源/稿件资产再生。完整315个编号记录、32个未编号来源提案、89条来源关系与61页审查队列见同名JSON。
