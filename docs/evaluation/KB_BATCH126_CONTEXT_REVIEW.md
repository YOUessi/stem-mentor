# Batch126｜26项课标上下文语义审查（非教师批准）

在Mac授权原件中逐条查看对应源码行；仅将原创语义判断、页行号与SHA-256写入仓库，不转载课标段落。
**这是一份人工编写的项目候审记录，不是教师审查或形式数学证明。**
上一批239候选仅分来源强度；本批核对20个候选（其中10个此前无布局marker）及6个仍未关联编号要求。
其余219项候选未在本批逐行解释，不得把26/26写成全部课程覆盖率。
正式课程原子分母仍UNKNOWN，正式教师批准0，学生权威发布0。

## 已审的来源上下文与数学边界

|ID|课标范围及页行|证据类型|仍需核查|
|---|---|---|---|
|hs-semantic-pilot-119-c02|COMPULSORY p27 L9–10|NUMBERED_NEIGHBOR_PARTIAL|小节标题本身不能证明具体除法分母条件已被逐条教研确认。|
|hs-semantic-pilot-119-s01|SELECTIVE_COMPULSORY p38 L12–13|NUMBERED_NEIGHBOR_PARTIAL|将数列定义域一律写作全部正整数会忽略有限数列及不同起始下标。|
|hs-semantic-pilot-119-s06|SELECTIVE_COMPULSORY p38 L29–30|OPTIONAL_NUMBERED_ACTIVITY|标星内容不应无条件混入全国选择性必修最低门槛；证明起点与归纳步仍待教师检查。|
|hs-semantic-pilot-120-s112|SELECTIVE_COMPULSORY p46 L22–26|NUMBERED_NEIGHBOR_PARTIAL|该区间含多项要求，不能合并认作一个知识原子，也不能代替条件完整推导。|
|hs-semantic-pilot-123-c408|COMPULSORY p21 L19–20|NUMBERED_NEIGHBOR_PARTIAL|弧长与物理量纲属于展开讲解，不能仅用小节名证明其全部细节。|
|hs-semantic-pilot-123-c410|COMPULSORY p22 L28–30|NUMBERED_NEIGHBOR_PARTIAL|二分法算法收敛须额外验证连续性与异号端点，源行未授权遗漏前提。|
|hs-semantic-pilot-123-s401|SELECTIVE_COMPULSORY p42 L22–23|NUMBERED_NEIGHBOR_PARTIAL|唯一性证明需要基向量线性无关；不能用小节标题代替该假设。|
|hs-semantic-pilot-123-s403|SELECTIVE_COMPULSORY p47 L21–22|NUMBERED_NEIGHBOR_PARTIAL|非负与归一条件须独立核查；一段要求往往对应多个概念。|
|hs-semantic-pilot-123-s405|SELECTIVE_COMPULSORY p48 L11–13|NUMBERED_NEIGHBOR_PARTIAL|异常值敏感性没有从这几行得到完整直接结论，必须另标作者扩展。|
|hs-semantic-pilot-123-s406|SELECTIVE_COMPULSORY p47 L28–28|NUMBERED_NEIGHBOR_PARTIAL|标准化必须假设标准差严格为正；不能将相关公式直接视作已通过来源审查。|
|hs-semantic-pilot-119-c03|COMPULSORY p28 L8–8|DIRECT_TEXT_AXIOM|直接数学陈述已找到，但独立公理与定理证明不能混淆，教师尚未审核。|
|hs-semantic-pilot-119-c04|COMPULSORY p28 L9–10|DIRECT_TEXT_AXIOM|需明确讨论的是该直线上全部点；数学事实不是数值见证可证明的。|
|hs-semantic-pilot-119-c05|COMPULSORY p28 L11–12|DIRECT_TEXT_AXIOM|忽略平面不重合会产生无数公共直线的反例。|
|hs-semantic-pilot-119-c07|COMPULSORY p31 L6–8|GENERAL_PARAGRAPH_PARTIAL|概述不自动证明等可能前提；需结合后文条件和事件定义审查。|
|hs-semantic-pilot-119-c08|COMPULSORY p33 L6–10|TEACHING_GUIDANCE_ONLY|教学提示不等于独立编号课程原子，且不能用有限性替代等可能性。|
|hs-semantic-pilot-119-c09|COMPULSORY p35 L9–13|TEXT_INSUFFICIENT_VISUAL_REQUIRED|回退循环需要第35页原始流程图视觉复核，不能靠PDFKit控制字符或探究段落伪证。|
|hs-semantic-pilot-119-ec02|ELECTIVE_C p65 L1–1|CROSS_PAGE_CONTINUATION|不核查前一页第64页末段就不能认定完整命题及其选修C归属。|
|hs-semantic-pilot-119-ec06|ELECTIVE_C p65 L19–23|GENERAL_PARAGRAPH_PARTIAL|课程示例不证明某个现实经济模型有效，仍需变量单位和适用域的单独验证。|
|hs-semantic-pilot-120-c109|COMPULSORY p28 L19–20|DIRECT_TEXT_THEOREM|使用时必须保证辅助平面确实相交、所给直线不落在原平面。|
|hs-semantic-pilot-120-c110|COMPULSORY p28 L21–22|DIRECT_TEXT_THEOREM|两个截线必须存在，不能省略第三平面分别与二平面相交的前提。|
|syllabus-cue-fa79a32fcccf7f814533|COMPULSORY p21 L6–7|RESEARCH_ACTIVITY_NOT_ATOMIZED|待教师决定是否登记教学活动，不能自动计算为必修数学定理。|
|syllabus-cue-e26ca752fcfbb29bdebf|COMPULSORY p23 L9–11|RESEARCH_ACTIVITY_NOT_ATOMIZED|可产生建模任务但未对应独立固定数学命题，原先非原子判断仍待教师裁决。|
|syllabus-cue-3042834dd2faa78d959c|COMPULSORY p29 L9–9|NUMBERED_COMPETENCY_NOT_ATOMIZED|它是证明能力范围而不是唯一的特定定理；需要映射多个题族。|
|syllabus-cue-afc6ea0759e9a1f4ea48|COMPULSORY p32 L18–20|NUMBERED_APPLICATION_NOT_ATOMIZED|对应抽样方法决策题族而非单独固定公式，需要先修与任务拆分。|
|syllabus-cue-f16fb54272cc33b9200f|COMPULSORY p32 L29–29|NUMBERED_APPLICATION_NOT_ATOMIZED|应用能力范围较广，需拆成方法和具体条件，不可直接作为一个原子分母。|
|syllabus-cue-7836cdcac3c80b03c51a|SELECTIVE_COMPULSORY p44 L16–16|NUMBERED_COMPETENCY_NOT_ATOMIZED|属于横贯主题的数学思维目标，不能冒充具完整假设结论的定理。|

## 验收边界

- source-line 哈希证明使用了锁定的PDFKit抽取文本；不能取代公式、跨页、流程图的原始图片审查。
- 对第35页回退循环、选修C跨页条件、可选星号归纳法保留明确的未完成证据标签。
- 6项未关联编号要求尚未删除或变成官方知识原子，活动/能力/应用的拆分等待教师审核。
- 这些候审内容继续TEACHER_ONLY/REVIEW_PENDING，不进入学生权威RAG或直接公开完整答案。
