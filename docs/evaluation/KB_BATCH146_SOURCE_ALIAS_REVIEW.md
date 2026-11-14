# Batch146｜历史课程线索重复来源与跨页语义人工裁决队列

依据旧版239条来源候选，识别**共享同页同源文本指纹**与**共享版式提示**，不自动合并数学知识。
同一页码与span SHA碰撞只能说明来自相同来源片段；可能是一个要求拆分的多个不同概念。
同一 cue 被复用也是证据线索，不等于相同的教育目标。此处没有完成跨页语义去重，也没有冻结官方分母。

- 历史编辑候选：239；关联完整候审稿：44；缺稿：195。
- 同页同段来源共享：7组／19个候选，需要人工逐条核对。
- 相同版式 cue 复用：17组／40次候选-线索关系，需要语义而非哈希判断。
- 这些共享cue中跨页复用：0组。**零不表示已完成跨页语义去重**，因为不同cue也可能描述相同课程目标。

## 按七轨分组（官方课程原子分母均 UNKNOWN）
| 轨道 | 编辑线索 | 共用原文段候选 | 已确认官方原子分母 |
|---|---:|---:|---|
| COMPULSORY | 75 | 2 | UNKNOWN |
| SELECTIVE_COMPULSORY | 51 | 0 | UNKNOWN |
| ELECTIVE_A | 30 | 0 | UNKNOWN |
| ELECTIVE_B | 30 | 0 | UNKNOWN |
| ELECTIVE_C | 24 | 4 | UNKNOWN |
| ELECTIVE_D | 17 | 5 | UNKNOWN |
| ELECTIVE_E | 12 | 8 | UNKNOWN |

## 同源段人工裁决队列（不自动合并）
1. 印刷页26，来源SHA `d88f89989ab699f4eb26cb6aaa4a0328efb28884e3b02d85fe43bbf0b1895ecd`：hs-semantic-pilot-120-c107, hs-semantic-pilot-120-c108；**REVIEW_PENDING**，拆并理由及教师签字缺失。
2. 印刷页65，来源SHA `2795b6d7e85c7472a3c5e50f7be967fad7d5b7bf94d20de701167f0f9a86ce15`：hs-semantic-pilot-119-ec05, hs-semantic-pilot-120-ec102；**REVIEW_PENDING**，拆并理由及教师签字缺失。
3. 印刷页65，来源SHA `9329b673756794e4dbf188506cac3aadf7bdf9374f2eb950b67ff18279ce84bc`：hs-semantic-pilot-119-ec04, hs-semantic-pilot-120-ec101；**REVIEW_PENDING**，拆并理由及教师签字缺失。
4. 印刷页70，来源SHA `72bb616409f81438d558f0a86336f65cd03226f314946570df02cd37e94d9500`：hs-semantic-pilot-119-ed02, hs-semantic-pilot-120-ed101；**REVIEW_PENDING**，拆并理由及教师签字缺失。
5. 印刷页70，来源SHA `bc7438f44a9bef9bd885ea47ba2b0c83f10178d5579c57ace329a7e78820d58d`：hs-semantic-pilot-119-ed03, hs-semantic-pilot-119-ed04, hs-semantic-pilot-120-ed102；**REVIEW_PENDING**，拆并理由及教师签字缺失。
6. 印刷页73，来源SHA `a79a98b383e495f957189f0ab1c9694c1339f6270071b721b76c901ab177661e`：hs-semantic-pilot-119-ee01, hs-semantic-pilot-119-ee02, hs-semantic-pilot-120-ee102, hs-semantic-pilot-120-ee103, hs-semantic-pilot-120-ee104；**REVIEW_PENDING**，拆并理由及教师签字缺失。
7. 印刷页73，来源SHA `ee11f8c53e8c415fa929cc883ab40316bb46aa3907474d87edd79b02b68667a9`：hs-semantic-pilot-119-ee04, hs-semantic-pilot-120-ee107, hs-semantic-pilot-120-ee108；**REVIEW_PENDING**，拆并理由及教师签字缺失。

## 跨页/跨主题处理门槛
- 对每组取得原始许可课标上下文，在Mac上审查编号要求的全句、上下段与页面连续关系。
- 人工裁定同源是同一目标、多目标拆分，或只是教学活动举例；冲突归属须保留来源证据。
- 只有完整覆盖全部官方内容要求且逐条审核完成，才能计算必修、选择性必修及A–E真正分母。
- 机器不得将239减去重复片段数直接当作官方总知识原子数；候审稿也不得自动APPROVED。
