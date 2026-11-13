# Batch127 K00/K01 — source interpretation audit

All review records are editorial only. A source line hash is not mathematics proof, a teacher sign-off, or a universal mandatory atom.

Context cases in Batch127: 28; distinct accumulated context-reviewed candidates: 48/239; untouched: 191.
Seven-track official atom denominators: UNKNOWN. Teacher approved: 0. Student authoritative: 0.

## hs-semantic-pilot-119-c01 | COMPULSORY
Page 27, lines 4-7 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 本段是复数的概念、代数表示及相等含义的课程要求，代数式的实虚部相等判据属于可教学内容。
**Math/scope risk:** 须在学生练习中限定i²=-1与实部虚部分别为实数；这里不等于自动批准任意复数计算证明。

## hs-semantic-pilot-119-c06 | COMPULSORY
Page 31, lines 10-13 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 该要求同时涉及有限样本空间、样本点、事件以及并交互斥的运算，不能合成一个原子。
**Math/scope risk:** 有限样本点的定义与古典概型的等可能假设不能混淆，样本空间的结果应不重不漏。

## hs-semantic-pilot-120-c101 | COMPULSORY
Page 26, lines 3-4 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 向量加减的几何表示及运算法则有直接课程要求，三角形法则是可拆分的具体教学方法。
**Math/scope risk:** 箭头的首尾连接、坐标分量相加及零向量方向的表述仍需独立校验。

## hs-semantic-pilot-120-c102 | COMPULSORY
Page 26, lines 5-7 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 数乘的几何意义及向量共线均有要求，线性运算性质应独立分拆而非作为数乘定义的一部分。
**Math/scope risk:** 共线判据u=λv若用v为方向基准必须注明v≠0，零向量不能给出唯一方向。

## hs-semantic-pilot-119-s02 | SELECTIVE_COMPULSORY
Page 38, lines 14-15 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 数列的等差概念与通项公式出现在编号要求中，公差由相邻差恒定确定。
**Math/scope risk:** 数列首项和起始下标须统一，有限等差数列的最后一项不能要求不存在的下一项。

## hs-semantic-pilot-119-s03 | SELECTIVE_COMPULSORY
Page 38, lines 16-17 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 该段明确要求掌握等差数列前n项和及与通项的关系，可以拆成公式与差分关系两个对象。
**Math/scope risk:** 必须限定n为实际项数且n≥1，误把末项当首项会使求和数值错误。

## hs-semantic-pilot-119-s04 | SELECTIVE_COMPULSORY
Page 38, lines 21-22 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 等比数列的概念和通项公式有课程要求，但当前段落没有完整固定公比取值范围。
**Math/scope risk:** 初项为零、q为零以及比值法对零项不可定义的歧义必须保留待专家确认。

## hs-semantic-pilot-119-s05 | SELECTIVE_COMPULSORY
Page 38, lines 23-24 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 编号要求明确探索等比前n项和以及它和通项的联系，应区分q=1分支。
**Math/scope risk:** 有限几何求和式可代数扩展到q=0，不能据此断言该零公比情形自动满足选用的等比数列定义。

## hs-semantic-pilot-119-a01 | ELECTIVE_A
Page 52, lines 9-20 | FORMAL_DEFINITION_REQUIRED
**Editorial reading:** 选修A的数列极限段落包含ε-N形式量词以及若干收敛示例，需单列正式定义。
**Math/scope risk:** 应写∀ε>0存在N使所有n≥N满足不等式；数字试验不是全称证明，PDFKit公式存在排版损失。

## hs-semantic-pilot-119-a02 | ELECTIVE_A
Page 52, lines 21-21 | EXPLICIT_PROOF_REQUIREMENT
**Editorial reading:** 独立段落要求探索并证明收敛数列有界，因此属于需要完整证明前提的定理教学。
**Math/scope risk:** 证明必须把有限前缀上界与N以后的尾项界结合，不能用极限值直接作为所有项上界。

## hs-semantic-pilot-119-a03 | ELECTIVE_A
Page 52, lines 22-29 | MATHEMATICAL_FACT_AND_EXAMPLES
**Editorial reading:** 该段以多个单调有界示例引入单调收敛事实；示例不能替代对所有实数序列的论证。
**Math/scope risk:** 数列必须在实数系且同时单调、有界；若只单调无界则可能发散。

## hs-semantic-pilot-119-a04 | ELECTIVE_A
Page 52, lines 32-38 | FORMAL_DEFINITION_REQUIRED
**Editorial reading:** 函数极限段落包含ε-δ定义与典型示例，概念依赖去心邻域与接近点的定义域。
**Math/scope risk:** 要明确0<|x-a|<δ而非只含x=a；公式抽取有乱码，需原始PDF图像审查。

## hs-semantic-pilot-119-b01 | ELECTIVE_B
Page 58, lines 25-27 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 导数与微分下的具体要求同时包含二阶导数的概念、意义和常见函数求导。
**Math/scope risk:** 二阶导数需要一阶导数在邻域内可微，不能在不可导点机械地再求导。

## hs-semantic-pilot-119-b02 | ELECTIVE_B
Page 58, lines 28-30 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 中值定理应用要求涉及单调分析与不等式证明，并非单条公式的复制练习。
**Math/scope risk:** 中值定理要求闭区间连续和开区间可导，导数符号需在整个目标区间可靠成立。

## hs-semantic-pilot-119-b03 | ELECTIVE_B
Page 59, lines 11-13 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 二元函数以具体情境建立概念和定义域，下一要求再引入偏导数；应拆成两条原子。
**Math/scope risk:** 二元定义域是R²子集，某点可代入不代表对所有方向都可微。

## hs-semantic-pilot-119-b04 | ELECTIVE_B
Page 59, lines 12-13 | EXPLICIT_NUMBERED_REQUIREMENT
**Editorial reading:** 偏导数的定义与简单求导示例具直接依据，固定其他变量后计算一维差商。
**Math/scope risk:** 偏导存在并不足以证明总可微；零分母以及被固定变量的定义域边界需检查。

## hs-semantic-pilot-119-ec01 | ELECTIVE_C
Page 64, lines 21-25 | EXPLICIT_THEME_PARAGRAPH
**Editorial reading:** 数学定义、命题与推理及前提结论在专题正文中阐明，但该段跨页继续，须结合下一页。
**Math/scope risk:** 应将定义与可判真假命题区别，前提真假与蕴含真值不可混为一谈。

## hs-semantic-pilot-119-ec03 | ELECTIVE_C
Page 65, lines 2-5 | EXPLICIT_THEME_PARAGRAPH
**Editorial reading:** 专题正文要求理解矛盾律、排中律及其推理作用，列举了两种逻辑原则的辨析。
**Math/scope risk:** 不能把P∨¬P与¬(P∧¬P)当作同一个语法式；所讨论经典逻辑前提要说明。

## hs-semantic-pilot-119-ec04 | ELECTIVE_C
Page 65, lines 6-10 | EXPLICIT_THEME_PARAGRAPH
**Editorial reading:** 该段覆盖演绎、归纳、类比及必然与或然推理，应拆分成推理模式与证据强度。
**Math/scope risk:** 从有限归纳实例得出的经验猜想不能自动推为全称定理，演绎规则须保证前提可靠。

## hs-semantic-pilot-119-ec05 | ELECTIVE_C
Page 65, lines 11-13 | EXPLICIT_THEME_PARAGRAPH
**Editorial reading:** 专题要求认识常用证明方法，直接证法和反证法是候选教材细化示例而非课标列出的唯一方法。
**Math/scope risk:** 反证法依赖反设到矛盾的合法步骤，不能用结论本身作隐含前提。

## hs-semantic-pilot-119-ed01 | ELECTIVE_D
Page 69, lines 9-20 | THEMATIC_APPLICATION_NOT_FIXED_ATOM
**Editorial reading:** 选修D将简洁、对称、周期等数学表达作为审美主题，正文举例只是可能的教学情境。
**Math/scope risk:** 不能从美感描述推出唯一形式数学命题；轨迹的现实近似与理想数学曲线需分开。

## hs-semantic-pilot-119-ed02 | ELECTIVE_D
Page 70, lines 2-7 | THEMATIC_APPLICATION_NOT_FIXED_ATOM
**Editorial reading:** 数学审美专题列举对称对象，允许设计几何变换判别题，不足以固定全部对称定理。
**Math/scope risk:** 轴对称、中心对称、平移对称是不同变换；自然或建筑形体未必严格对称。

## hs-semantic-pilot-119-ed03 | ELECTIVE_D
Page 70, lines 8-11 | THEMATIC_APPLICATION_NOT_FIXED_ATOM
**Editorial reading:** 周期美的段落用昼夜、海浪和图案等示例开展数学表征，但不直接认证严格周期模型。
**Math/scope risk:** 有限观测或季节变化不证明f(t+T)=f(t)对所有t成立；须区分近似和严格周期。

## hs-semantic-pilot-119-ed04 | ELECTIVE_D
Page 70, lines 8-11 | THEMATIC_APPLICATION_NOT_FIXED_ATOM
**Editorial reading:** 同一周期段落可用于音乐和图案的建模活动，不提供采样周期的独立数学定义。
**Math/scope risk:** 时间采样别名和实际信号周期不能等同，不能把文字举例误归为单独全国标准知识点。

## hs-semantic-pilot-119-ee01 | ELECTIVE_E
Page 73, lines 16-17 | LOCAL_OPTIONAL_EXAMPLE
**Editorial reading:** 选修E是学校开设的示例方向，其中机器人与数学仅是可选专题之一。
**Math/scope risk:** 不能把机器人坐标变换列为全国必修，更不能把示例等同全国统一内容分母。

## hs-semantic-pilot-119-ee02 | ELECTIVE_E
Page 73, lines 16-17 | LOCAL_OPTIONAL_EXAMPLE
**Editorial reading:** 初等数论是选修E拓展视野的示例主题，没有确定同余运算的官方固定教学颗粒度。
**Math/scope risk:** 若开发同余课程，定义、模非零与等价关系需作者单独建构，并标记学校自选。

## hs-semantic-pilot-119-ee03 | ELECTIVE_E
Page 73, lines 18-20 | LOCAL_OPTIONAL_EXAMPLE
**Editorial reading:** 家庭理财作为选修E日常生活主题示例，可开展复利和实际利率建模，而非强制核心公式。
**Math/scope risk:** 现实利率模型须注明计息周期、税费与通胀；理想模型不能被宣称为现实精确预测。

## hs-semantic-pilot-119-ee04 | ELECTIVE_E
Page 73, lines 21-22 | LOCAL_OPTIONAL_EXAMPLE
**Editorial reading:** 大学先修概率统计位列选修E大学先修主题，并非每名高中生都必须完成的课程知识原子。
**Math/scope risk:** 要在学校自选计划中明确具体目标，不能让高阶内容覆盖高中必修概率统计。
