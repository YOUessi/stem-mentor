# Batch133 | 有边界的课标要求→拟议知识原子拆解

本文件是项目原创课程编目提议。**不是完整课程原子分母，不是课标原文，未经教师审核。**
受保护的原始课标仅在 Mac 本地逐行哈希校验，仓库只存 SHA-256 与作者原创释义。
GitHub CI 离线验证无法证明作者的释义忠于原文，必须与教师审查区别。
本批: 41 条拟议原子；41 个有定位的来源行区间。
七轨正式原子分母: UNKNOWN；APPROVED 0；学生可发布 0。

- COMPULSORY: 23 个项目拟议原子（官方分母 UNKNOWN）
- SELECTIVE_COMPULSORY: 11 个项目拟议原子（官方分母 UNKNOWN）
- ELECTIVE_A: 7 个项目拟议原子（官方分母 UNKNOWN）
- ELECTIVE_B: 0 个项目拟议原子（官方分母 UNKNOWN）
- ELECTIVE_C: 0 个项目拟议原子（官方分母 UNKNOWN）
- ELECTIVE_D: 0 个项目拟议原子（官方分母 UNKNOWN）
- ELECTIVE_E: 0 个项目拟议原子（官方分母 UNKNOWN）

## 逐项可审查的范围、前提与失效条件

### kb133-proposal-c_set_membership · COMPULSORY
来源: 印刷页 15，PDFKit 行 10–14；区间 SHA-256 `6100451cff60e8b094efa588e824e30c8d218f62e4614f3a25d87c35eeeb9deb`
知识类型: Concept；作者拟议学习目标: 区分元素属于集合与集合包含关系
适用前提: 元素类型与集合元素的判定域必须明确
失效边界/反例: 数字2属于{2}但通常不把2写作{2}的子集
先修: 待课程图谱补充；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_set_subset · COMPULSORY
来源: 印刷页 15，PDFKit 行 15–16；区间 SHA-256 `d6b4659b401e6393815fd5ef18b965677a2d9300521049972d60a7f9b994cefc`
知识类型: Concept；作者拟议学习目标: 识别子集与集合相等的充要条件
适用前提: 两个对象都必须是集合且量词遍历各自元素
失效边界/反例: {1}属于{{1}}不推出{1}是{{1}}的子集
先修: kb133-proposal-c_set_membership；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_union_intersection · COMPULSORY
来源: 印刷页 15，PDFKit 行 17–19；区间 SHA-256 `8992e8855703ff0a2e5b59843c474d161e5cb72619ae61cb4f4f2ac4ee2a6ac3`
知识类型: Method；作者拟议学习目标: 按或和且的逻辑分别计算并集与交集
适用前提: 两集合在同一讨论全集内进行元素判定
失效边界/反例: A={1}且B={2}时交集为空而并集非空
先修: kb133-proposal-c_set_membership；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_complement · COMPULSORY
来源: 印刷页 15，PDFKit 行 20–23；区间 SHA-256 `558cfa1874fdb495e431bb37d0428b55b6adbc026e6ccd6f2260d91549721733`
知识类型: Concept；作者拟议学习目标: 在给定全集中定义补集并用图表示
适用前提: 必须指定全集U且A是U的子集
失效边界/反例: 若U={1,2}而A={1}则补集为{2}而非全体实数去掉1
先修: kb133-proposal-c_set_subset；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_sufficiency · COMPULSORY
来源: 印刷页 16，PDFKit 行 7–11；区间 SHA-256 `2d1443471a662319498ef71e09460aac56ca359375ac903eb0bef3a47f282e0c`
知识类型: Concept；作者拟议学习目标: 辨别P为Q的充分条件与必要条件
适用前提: 逻辑蕴涵方向必须固定并区分前后件
失效边界/反例: x>2足以推出x>1但x>1不足以推出x>2
先修: 待课程图谱补充；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_equivalence · COMPULSORY
来源: 印刷页 16，PDFKit 行 12–13；区间 SHA-256 `6c6d6ddbc9ec3e4e5eadb1184b67de7158e51365466d52fc500774ea93125309`
知识类型: Theorem；作者拟议学习目标: 判断两个性质是否构成充要条件
适用前提: 两个方向的逻辑蕴涵均须独立证明
失效边界/反例: x²=4推出x=2不成立因x=-2也满足
先修: kb133-proposal-c_sufficiency；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_quantifier · COMPULSORY
来源: 印刷页 16，PDFKit 行 14–15；区间 SHA-256 `f2557f8a064b3e0ff4e327eb6c1d5ce5e6ca50dd9671a4fd8b6716dc62ed9ffe`
知识类型: Concept；作者拟议学习目标: 识别全称量词与存在量词及论域
适用前提: 谓词P(x)必须有确定论域
失效边界/反例: 对正实数成立的1/x>0不可扩大为对所有实数成立
先修: 待课程图谱补充；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_quantifier_negation · COMPULSORY
来源: 印刷页 16，PDFKit 行 16–18；区间 SHA-256 `9c9d757cb9c798cad309f8b6ef9712a76774d216480be03141ed169c94c01b98`
知识类型: Method；作者拟议学习目标: 对含量词命题逐层进行逻辑否定
适用前提: 否定必须同时交换量词并否定谓词
失效边界/反例: 并非所有实数平方为正不能写成所有实数平方非正
先修: kb133-proposal-c_quantifier；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_inequality_product · COMPULSORY
来源: 印刷页 16，PDFKit 行 24–28；区间 SHA-256 `e7714938a0655109b505c89b5dba4bd41e87646e8c81070d0ab2e549b924f165`
知识类型: Theorem；作者拟议学习目标: 在非负实数条件下运用均值不等式
适用前提: a和b均非负且等号当且仅当a=b
失效边界/反例: a=-1时√ab可能无实数意义不能直接使用
先修: 待课程图谱补充；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_quadratic_roots · COMPULSORY
来源: 印刷页 17，PDFKit 行 9–11；区间 SHA-256 `5f48b23cd0e9ca7896d8a3e3f1700b19a58e065bda24ef7ac2417768b5afec4a`
知识类型: Method；作者拟议学习目标: 由判别式判断实二次方程根的个数
适用前提: 二次系数必须非零且系数为实数
失效边界/反例: a=0时不能用二次判别式分类
先修: 待课程图谱补充；跨页复用组: FUNCTION_ZERO_AND_EQUATION_LINK
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_quadratic_sign · COMPULSORY
来源: 印刷页 17，PDFKit 行 12–17；区间 SHA-256 `06e97fbbc8ef8cd6a9ace6f6ec0e97d18e09c2c2b910352b928213778b5544ef`
知识类型: Method；作者拟议学习目标: 结合抛物线开口和零点求一元二次不等式解集
适用前提: a不为0且需区别严格与非严格不等号
失效边界/反例: x²<0在实数域没有解不能误给出区间
先修: kb133-proposal-c_quadratic_roots；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_function_mapping · COMPULSORY
来源: 印刷页 19，PDFKit 行 13–17；区间 SHA-256 `e7f35b9a5a5b41078e974c5751271f5345857fbe0e5cdb4ce89ffcb8bcb4604e`
知识类型: Concept；作者拟议学习目标: 用对应规则和定义域描述函数
适用前提: 每个定义域元素恰有一个对应值
失效边界/反例: x=1对应正负两个不同y值不构成单值函数
先修: 待课程图谱补充；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_piecewise · COMPULSORY
来源: 印刷页 19，PDFKit 行 18–20；区间 SHA-256 `4ed2e9bafb00f3e8315868af3b1dceb54c655a6f957ba994eb0b5b765c5c5725`
知识类型: Method；作者拟议学习目标: 依据分段条件选择正确解析式
适用前提: 必须检查定义域及交界点是否被覆盖或重复
失效边界/反例: x=0若无任何分段适用不能自动代入左式
先修: kb133-proposal-c_function_mapping；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_monotonicity · COMPULSORY
来源: 印刷页 19，PDFKit 行 21–23；区间 SHA-256 `940732f9eaff61274a00d4f6f09ac292d6d27c66b903b2d9df65999bf0adde7d`
知识类型: Concept；作者拟议学习目标: 用量词正确叙述指定区间上的单调性
适用前提: 必须固定区间并对任意x1<x2比较
失效边界/反例: f=x²在整个实轴不是单调递增
先修: kb133-proposal-c_function_mapping；跨页复用组: MONOTONICITY_DIFFERENT_METHODS
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_parity · COMPULSORY
来源: 印刷页 19，PDFKit 行 24–24；区间 SHA-256 `65150f2ffa1696eb67ab2d6c75dea4d1cc073746a376e257646dfad4cff4bcf3`
知识类型: Concept；作者拟议学习目标: 区分偶函数奇函数与定义域对称前提
适用前提: 定义域须关于0对称才可全域比较f(-x)
失效边界/反例: f(x)=x在(0,1)上不能判为奇函数
先修: kb133-proposal-c_function_mapping；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_period · COMPULSORY
来源: 印刷页 19，PDFKit 行 25–25；区间 SHA-256 `f33fb1f7fffce381d06531a2cc55dd338e147bd6ff554a6eeed24ce46c6463be`
知识类型: Concept；作者拟议学习目标: 从周期定义检查非零周期平移
适用前提: 必须保证平移后的点仍处于定义域且周期非零
失效边界/反例: f(x)=x没有任何非零周期
先修: kb133-proposal-c_function_mapping；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_exponential_exp · COMPULSORY
来源: 印刷页 20，PDFKit 行 19–30；区间 SHA-256 `5601c5d060ad72153c4c6df038351f890f81eb4265127d57517deeee4bf2d54e`
知识类型: Concept；作者拟议学习目标: 区分实数指数函数的底数条件与单调性
适用前提: 指数底数a必须严格大于0且不等于1
失效边界/反例: a=-2时a^x并非对每个实数x均有实数值
先修: kb133-proposal-c_function_mapping；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_logarithm_law · COMPULSORY
来源: 印刷页 20，PDFKit 行 31–33；区间 SHA-256 `48fc34f4702baccbe9482de524d605d94dc2193dcee57f661e991de58ba1f9a2`
知识类型: Method；作者拟议学习目标: 在真数严格正的前提下使用对数运算法则和换底
适用前提: 真数>0且底数>0且不等于1
失效边界/反例: log(0)未定义且log(x+y)不能一般拆成两个对数
先修: kb133-proposal-c_exponential_exp；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_log_inverse · COMPULSORY
来源: 印刷页 21，PDFKit 行 1–5；区间 SHA-256 `317c6823df36d1f002553a4b1b19d4a36a477daf8f24322f6fb8507da18e8df9`
知识类型: Theorem；作者拟议学习目标: 论证同底指数与对数互为反函数
适用前提: 底数>0且不等于1及对数真数>0
失效边界/反例: 当底数a=1时指数不是一一对应故不存在反函数
先修: kb133-proposal-c_logarithm_law；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_radian · COMPULSORY
来源: 印刷页 21，PDFKit 行 18–20；区间 SHA-256 `003cadd2bf9f1632624ab929d78ced30582e7fec51d651fe6c430b1f42077334`
知识类型: Method；作者拟议学习目标: 通过弧长与半径定义角的弧度并互换度数
适用前提: 圆半径必须正且角度弧度单位一致
失效边界/反例: 把90度直接输入要求弧度的sin会得到错误值
先修: 待课程图谱补充；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_tangent_domain · COMPULSORY
来源: 印刷页 21，PDFKit 行 21–26；区间 SHA-256 `b10d35fc8083b056d411e5cefa5cd4285bdb9c7b5571a8bc271964a80ebd1941`
知识类型: Concept；作者拟议学习目标: 用单位圆解释三角函数并排除正切无定义点
适用前提: tan定义为sin/cos时必须cos不为0
失效边界/反例: tan(pi/2)在实数范围未定义
先修: kb133-proposal-c_radian；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_cosine_difference · COMPULSORY
来源: 印刷页 22，PDFKit 行 12–17；区间 SHA-256 `2597ad23392d57416b33415fedcc5a374cba80c1c17697109bf743adf7571d7c`
知识类型: Theorem；作者拟议学习目标: 在单位圆及向量内积下论证两角差余弦公式
适用前提: 角均采用弧度并正确使用旋转及单位圆
失效边界/反例: 把cos(a-b)写成cos(a)-cos(b)通常不成立
先修: kb133-proposal-c_radian；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-c_zero_theorem · COMPULSORY
来源: 印刷页 22，PDFKit 行 27–30；区间 SHA-256 `7c739c5b9528a95ab7621e06927f0fde1d64001a2d02c3a4a4a9ead3795daef4`
知识类型: Theorem；作者拟议学习目标: 在连续性与端点异号前提下确认区间内有零点
适用前提: f在闭区间连续且f(a)f(b)<0
失效边界/反例: f在0跳跃由-1变1却没有取0说明不连续时不能套用
先修: kb133-proposal-c_function_mapping；跨页复用组: FUNCTION_ZERO_AND_EQUATION_LINK
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-sc_sequence_model · SELECTIVE_COMPULSORY
来源: 印刷页 38，PDFKit 行 11–13；区间 SHA-256 `30489f5df9400d10a107aa026a9a5eb807335197f6c9b032bc8e77bad7111684`
知识类型: Concept；作者拟议学习目标: 将数列看作正整数集上的特殊函数
适用前提: 明确下标起点和定义域为正整数或指定子集
失效边界/反例: 只定义a_1但没给出后继项不能声称已定义全部数列
先修: 待课程图谱补充；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-sc_arith_progression · SELECTIVE_COMPULSORY
来源: 印刷页 38，PDFKit 行 14–20；区间 SHA-256 `f1e7745fc598df85fe187767ecf74d41b90fa1648717a5a349b88682e5896f58`
知识类型: Theorem；作者拟议学习目标: 推导等差数列通项与有限前n项和公式
适用前提: 有限n为正整数且各相邻差固定
失效边界/反例: 1,2,4不是等差数列不能套等差求和
先修: kb133-proposal-sc_sequence_model；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-sc_geom_progression · SELECTIVE_COMPULSORY
来源: 印刷页 38，PDFKit 行 21–27；区间 SHA-256 `1d3ad821c0c705117cfe35edce352f47586991126417f89af3d22d0e7f510800`
知识类型: Theorem；作者拟议学习目标: 通过错位相减证明有限等比和并单独处理q=1
适用前提: n正整数且符合所采用的等比数列定义
失效边界/反例: q=1时不能除以1-q且q=0需区别有限幂级数与标准等比定义
先修: kb133-proposal-sc_sequence_model；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-sc_induction_optional · SELECTIVE_COMPULSORY
来源: 印刷页 38，PDFKit 行 28–30；区间 SHA-256 `33d95bf2fac9a4c7e2922e727730746feab11873b476a6004dec1163a7cba6f5`
知识类型: Method；作者拟议学习目标: 以基例和归纳步骤建立数学归纳法证明
适用前提: 必须明确自然数起点且完成两个证明义务
失效边界/反例: 只证明n=1和n=2不代表已证明全部n
先修: kb133-proposal-sc_sequence_model；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-sc_derivative_def · SELECTIVE_COMPULSORY
来源: 印刷页 39，PDFKit 行 8–13；区间 SHA-256 `ca66817ca8954254c492c53c78def35a6588d0ac1691d30b37bd646477e16c5e`
知识类型: Concept；作者拟议学习目标: 由差商极限解释瞬时变化率与切线斜率
适用前提: 双侧极限需存在且为有限实数
失效边界/反例: 绝对值函数在0处左右导数不一致不可导
先修: kb133-proposal-c_function_mapping；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-sc_derivative_rules · SELECTIVE_COMPULSORY
来源: 印刷页 39，PDFKit 行 14–25；区间 SHA-256 `8c92570f756a8198e6f11d39598d4eb1723df8b58793b9820c0ec5ae35a9a027`
知识类型: Method；作者拟议学习目标: 对可导函数合法应用四则与简单复合求导
适用前提: 除法求导要求分母在点处不为零
失效边界/反例: d(1/x)/dx不能在x=0处使用
先修: kb133-proposal-sc_derivative_def；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-sc_derivative_monotone · SELECTIVE_COMPULSORY
来源: 印刷页 39，PDFKit 行 26–29；区间 SHA-256 `7a57dc095e46689e1aff6eeb2653cbb1d822eda35536c67ca833feeab326d5c9`
知识类型: Theorem；作者拟议学习目标: 以导数符号作为区间单调性充分条件
适用前提: 在区间可导且导数符号具有全区间保证
失效边界/反例: f'(0)=0不能说明f在0邻域为常数
先修: kb133-proposal-sc_derivative_rules；跨页复用组: MONOTONICITY_DIFFERENT_METHODS
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-sc_extreme_point · SELECTIVE_COMPULSORY
来源: 印刷页 39，PDFKit 行 30–33；区间 SHA-256 `38fb63a485aad49f9d5f4d8fc110a854ccfd0cafc871eed6a7eaf1b49bea6667`
知识类型: Method；作者拟议学习目标: 比较临界点和闭区间端点判定极值与最值
适用前提: 内点导数零仅为可导极值的必要非充分条件
失效边界/反例: f=x³在0处导数为0但0不是极值
先修: kb133-proposal-sc_derivative_rules；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-sc_space_distance · SELECTIVE_COMPULSORY
来源: 印刷页 42，PDFKit 行 13–17；区间 SHA-256 `445bb438cf5c26f4f2f4b9bfad794f371bac50a7928dd4d0b3a9106c9222634c`
知识类型: Theorem；作者拟议学习目标: 通过坐标差平方和推导三维两点距离
适用前提: 空间坐标轴两两正交且采用同一长度单位
失效边界/反例: 非正交坐标基不能直接按坐标差平方和计算
先修: 待课程图谱补充；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-sc_space_basis · SELECTIVE_COMPULSORY
来源: 印刷页 42，PDFKit 行 21–23；区间 SHA-256 `3503e15fa5e9e2b4e30d508da79a152d98a501d1022105d033429ae216c0c18a`
知识类型: Theorem；作者拟议学习目标: 在三维正交基下唯一展开空间向量
适用前提: 必须使用三条线性无关的基向量
失效边界/反例: 三个共面向量不能唯一展开所有空间向量
先修: kb133-proposal-sc_space_distance；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-sc_space_projection · SELECTIVE_COMPULSORY
来源: 印刷页 42，PDFKit 行 24–26；区间 SHA-256 `cd2771c99c1ebc5ea274cca206f644f8aa7c9bd3661abe77bc79ea2009c1bfea`
知识类型: Method；作者拟议学习目标: 以点积和非零向量定义投影与数量积
适用前提: 投影到指定向量时被投影轴必须非零
失效边界/反例: 向零向量投影会出现除以零
先修: kb133-proposal-sc_space_basis；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-a_sequence_limit · ELECTIVE_A
来源: 印刷页 52，PDFKit 行 9–21；区间 SHA-256 `625a33b9ba5985da4086892be4f3f09df3abafa9772b696104a5ca125946111f`
知识类型: Concept；作者拟议学习目标: 由epsilon-N定义序列极限并证明收敛必有界
适用前提: 每个epsilon>0存在阈值N约束全部后续项
失效边界/反例: a_n=(-1)^n有界但不收敛不能反推有界即收敛
先修: kb133-proposal-sc_sequence_model；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-a_monotone_convergence · ELECTIVE_A
来源: 印刷页 52，PDFKit 行 22–29；区间 SHA-256 `213a9a645ce73d6de941a3ffdb1fb4e5de36d2806885b35667c0f8241a4c931a`
知识类型: Theorem；作者拟议学习目标: 理解实数完备性下的单调有界收敛结论
适用前提: 须同为单调与有界两个条件
失效边界/反例: a_n=n单调但无上界不收敛
先修: kb133-proposal-a_sequence_limit；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-a_limits_quotient · ELECTIVE_A
来源: 印刷页 52，PDFKit 行 30–31；区间 SHA-256 `7331c304719979c8dd71514e8fe13b8ec4be140ee7f316570b53d7f18ce1f11e`
知识类型: Theorem；作者拟议学习目标: 掌握收敛数列极限四则与商的非零分母条件
适用前提: 使用商法则必须确认分母的极限非零
失效边界/反例: 1除以(1/n)所得n发散
先修: kb133-proposal-a_sequence_limit；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-a_function_limit · ELECTIVE_A
来源: 印刷页 52，PDFKit 行 32–39；区间 SHA-256 `63a862a1d5e07381370ee86b31def4d34a3b67fc393eb8170109a86a8fd59ff9`
知识类型: Concept；作者拟议学习目标: 理解函数有限极限epsilon-delta的去心邻域定义
适用前提: 考虑极限点的去心邻域且函数在该邻域有定义
失效边界/反例: 仅f(a)=L不能证明x趋于a时极限为L
先修: kb133-proposal-c_function_mapping；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-a_continuity · ELECTIVE_A
来源: 印刷页 53，PDFKit 行 1–4；区间 SHA-256 `71a0bbbdf5327da65e069070ff1cc42fc31a1af7498c76cd8a16372a59f0cd62`
知识类型: Theorem；作者拟议学习目标: 将函数连续性与区间介值性质联系
适用前提: 闭区间连续才能保证介值结论
失效边界/反例: 阶跃函数端点异号却跳过0
先修: kb133-proposal-a_function_limit；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-a_mean_value · ELECTIVE_A
来源: 印刷页 53，PDFKit 行 10–14；区间 SHA-256 `91f14980ff51ebb0e62806cb98ecf806747b3fd7caa81418fa92941e938cd81e`
知识类型: Theorem；作者拟议学习目标: 利用闭区间连续开区间可导的中值定理讨论不等式
适用前提: a<b且f在[a,b]连续在(a,b)可导
失效边界/反例: 绝对值函数跨0不可导无法直接套拉格朗日中值定理
先修: kb133-proposal-sc_derivative_def；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。

### kb133-proposal-a_integral_area · ELECTIVE_A
来源: 印刷页 53，PDFKit 行 18–27；区间 SHA-256 `e47ae8dc002dbccc9c4ef9810a73537ea85ccbdc89beddf4672500bbb4ed0e02`
知识类型: Method；作者拟议学习目标: 由定积分有向符号和原函数公式计算累计变化
适用前提: 原函数F导数在积分区间为f
失效边界/反例: 对f(x)=x在[-1,1]积分为0不等于几何面积1
先修: kb133-proposal-a_continuity；跨页复用组: 无
状态: REVIEW_PENDING / TEACHER_ONLY；不代表官方原子确认。
