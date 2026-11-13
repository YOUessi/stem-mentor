# Batch130 — Mac original-source contextual review

53 manually reasoned contextual review cases; 157/239 previously drafted editorial candidates checked, 82 still unchecked.
Each associated fingerprint can be compared to the original privately held Mac PDFKit lines.
A line hash is not a proof of complete normative support. Single source line may be a fragment.
Official denominator UNKNOWN in all seven tracks; teacher approved=0; student authority=0.

- COMPULSORY: 63/75 reviewed, 12 pending; official atom denominator UNKNOWN
- SELECTIVE_COMPULSORY: 32/51 reviewed, 19 pending; official atom denominator UNKNOWN
- ELECTIVE_A: 12/30 reviewed, 18 pending; official atom denominator UNKNOWN
- ELECTIVE_B: 12/30 reviewed, 18 pending; official atom denominator UNKNOWN
- ELECTIVE_C: 14/24 reviewed, 10 pending; official atom denominator UNKNOWN
- ELECTIVE_D: 12/17 reviewed, 5 pending; official atom denominator UNKNOWN
- ELECTIVE_E: 12/12 reviewed, 0 pending; official atom denominator UNKNOWN

## hs-semantic-pilot-121-c201 (COMPULSORY)
Original PDF printed p.15 lines 11-11; SHA256 93e9e0dbbe63a2d8d571c32520e33e8cadd941605163fc512edb18a4aaa0721e
Objective (editorial): 集合的元素属于关系与对象判定
Context interpretation (pending): 集合与元素的属于关系；先选定对象是否为元素，不可混同子集与成员。
Invalid edge / negative case: 3∈{1,2}为假；{1}∈{1,2}为假，但{1}⊆{1,2}为真。

## hs-semantic-pilot-121-c202 (COMPULSORY)
Original PDF printed p.15 lines 18-18; SHA256 ff5dbf429128bbf700887e0a0264bdd31c9079f577601b71754614acf354d24d
Objective (editorial): 集合并交的元素判据与韦恩图核对
Context interpretation (pending): 并交运算依赖元素判据；图示是辅助而不是替代元素所属证明。
Invalid edge / negative case: 集合{1,2}与{2,3}交集为{2}，不是{1,2,3}。

## hs-semantic-pilot-121-c203 (COMPULSORY)
Original PDF printed p.16 lines 17-17; SHA256 99412f64576d15a88fd53422b1ea5a41f848adede7e1b21e8a6cab44dfe8929c
Objective (editorial): 全称量词命题的正确否定
Context interpretation (pending): 全称命题的否定必须把任意改成存在并否定谓词。
Invalid edge / negative case: 「所有实数平方为正」的否定是存在x使x²≤0；x=0为见证。

## hs-semantic-pilot-121-c204 (COMPULSORY)
Original PDF printed p.17 lines 16-16; SHA256 aa6b349a9288b6ac13e616bf2fb7f02fca25109765e52eb7db49541be3145f8e
Objective (editorial): 一元二次不等式按抛物线符号区间求解
Context interpretation (pending): 二次不等式利用抛物线符号区间之前先核对开口系数和实根数。
Invalid edge / negative case: x²+1>0在实数域恒真，不能擅自假设两个实根。

## hs-semantic-pilot-121-c205 (COMPULSORY)
Original PDF printed p.19 lines 14-14; SHA256 8f69593d2cd68e8aca4c99ddfb91b6a57f87c9c57bb7217478885ea0658cf939
Objective (editorial): 函数的对应法则与定义域检查
Context interpretation (pending): 函数是从定义域到陪域的单值对应；同一输入不准出现两个不同输出。
Invalid edge / negative case: x=0同时指定f(0)=1与f(0)=2的关系不是函数。

## hs-semantic-pilot-122-c301 (COMPULSORY)
Original PDF printed p.15 lines 12-12; SHA256 a9d757e4e0643189031fa8d2ddad7f326702dfd0df518128254b8b71f19baab6
Objective (editorial): 集合的列举法与描述法之间的等价转换
Context interpretation (pending): 列举与描述法需要指向同一论域；重复列举不产生新集合元素。
Invalid edge / negative case: {x∈Z:0<x<3}={1,2}，若把论域改为R则不相等。

## hs-semantic-pilot-122-c302 (COMPULSORY)
Original PDF printed p.15 lines 14-14; SHA256 0003e0c06fb4f2d0e560dbf06e0765b5c4d6377262ec2fa541485707f5e0a472
Objective (editorial): 全集和空集须相对明确的研究论域
Context interpretation (pending): 空集没有元素；全集相对于给定问题定义，不能省略研究范围。
Invalid edge / negative case: 全集U={1,2}时{3}不可能是U的子集。

## hs-semantic-pilot-122-c303 (COMPULSORY)
Original PDF printed p.15 lines 20-20; SHA256 2ef655b14624d06985f8cf103d940e98dadc347a545f519f5ae111d9a2a4e4c4
Objective (editorial): 集合补集相对全集的元素判断
Context interpretation (pending): 补集运算必须包含指定全集U和U内子集A；变更U将变更结果。
Invalid edge / negative case: U={1,2,3},A={1}的补集为{2,3}，不是无限整数集。

## hs-semantic-pilot-122-c304 (COMPULSORY)
Original PDF printed p.16 lines 8-8; SHA256 2634c47beec268359cc41f4e0087987a6dc8f98d6ae311f5487180c3396d7c34
Objective (editorial): 充分必要条件的必要性方向
Context interpretation (pending): 对命题P是Q的必要条件，核验方向应为Q⇒P。
Invalid edge / negative case: 整数为偶数是可被4整除的必要条件，反方向不成立。

## hs-semantic-pilot-122-c305 (COMPULSORY)
Original PDF printed p.16 lines 10-10; SHA256 05221cfd3966fca303eed59e768e5090840d00c3474e72f8ea2c6a9ca5ecdce4
Objective (editorial): 充分条件的正确蕴含方向
Context interpretation (pending): 对命题P是Q的充分条件，核验方向应为P⇒Q。
Invalid edge / negative case: 可被4整除充分保证偶数，偶数不充分保证可被4整除。

## hs-semantic-pilot-122-c306 (COMPULSORY)
Original PDF printed p.16 lines 12-12; SHA256 ec0dd62319f4a37d076327225d2f486934a128eeb6fe153c93d5b78495b504d6
Objective (editorial): 充要条件的双向蕴含核验
Context interpretation (pending): 充要条件要求两个方向都真，单方向的蕴含不能当成等价。
Invalid edge / negative case: x²=4与x=2不是充要：x=-2也是平方等于4。

## hs-semantic-pilot-122-c307 (COMPULSORY)
Original PDF printed p.19 lines 20-20; SHA256 ef0dcc75994c88ae3faee11dee718920dfda97e32d36e2b4856314d6674081d4
Objective (editorial): 分段函数按输入归属分支求值
Context interpretation (pending): 分段函数按自变量归属唯一分支求值，接缝点的左右规则须清楚。
Invalid edge / negative case: f(x)=x(x<0),x+1(x≥0)时f(0)=1，不是0。

## hs-semantic-pilot-122-c308 (COMPULSORY)
Original PDF printed p.19 lines 22-22; SHA256 4fc888c340a99704cd53ac6214dd08aef22bc011ce2734b456aaf157f2c6a9a5
Objective (editorial): 函数单调性与极值的区间量词
Context interpretation (pending): 单调性是给定区间任意两点的比较，不由单个采样对替代。
Invalid edge / negative case: f(x)=x²在整个实数域并不单调，虽然在[0,∞)递增。

## hs-semantic-pilot-122-c309 (COMPULSORY)
Original PDF printed p.20 lines 26-26; SHA256 db598df3a853c88029ea8d00e0be79c02043fea88bf9f1c5155c5c6d95594466
Objective (editorial): 指数增长模型底数和时间尺度检查
Context interpretation (pending): 指数函数模型需确认底数正且不等于1，现实增长还须时间单位一致。
Invalid edge / negative case: y=(-2)^x在全部实数上不是实值指数函数。

## hs-semantic-pilot-122-c310 (COMPULSORY)
Original PDF printed p.21 lines 22-22; SHA256 af93f4d2df9812feae30e8eb042ef2af70770ea6fddab840dbfcdec87e3ee8c8
Objective (editorial): 单位圆三角函数的坐标定义与正切边界
Context interpretation (pending): 单位圆坐标分别对应sin、cos；tan需cos不为零。
Invalid edge / negative case: 在θ=π/2处sinθ有定义，但tanθ无定义。

## hs-semantic-pilot-122-c311 (COMPULSORY)
Original PDF printed p.22 lines 29-29; SHA256 0e2783329b4956f2f8806538d7a0bb6e59e7aeb2fd1f436395cc0d9b94b324f1
Objective (editorial): 连续函数异号端点的零点存在性
Context interpretation (pending): 零点存在定理需要闭区间连续及两端严格异号才给出开区间内零点。
Invalid edge / negative case: f(x)=1/x在[-1,1]两端异号但不连续，区间内无零点。

## hs-semantic-pilot-122-c312 (COMPULSORY)
Original PDF printed p.31 lines 17-17; SHA256 1ff93c882726cdc1c6ecb4d94f92bcfa9203cc14f8ba22fd5c4fb6fd9eedc58d
Objective (editorial): 用样本频率近似概率须陈述随机机制
Context interpretation (pending): 频率估计概率依赖可重复稳定随机机制，单次频率不等于真概率。
Invalid edge / negative case: 一枚公平硬币一次抛出正面频率是0或1，理论概率仍1/2。

## hs-semantic-pilot-123-c401 (COMPULSORY)
Original PDF printed p.15 lines 22-22; SHA256 8e884c699d5f08fe68adb3e5138a39ec019c588d01eb398edaec6f9b60bbd0f6
Objective (editorial): 使用韦恩图核对集合交并补的成员关系
Context interpretation (pending): 韦恩图以交并补的元素关系为准，不可用不按比例的图形面积推概率。
Invalid edge / negative case: A={1,2},B={2,3}，A∪B含3个元素而非4个。

## hs-semantic-pilot-123-c402 (COMPULSORY)
Original PDF printed p.16 lines 18-18; SHA256 7e52b53474751c488a86b9c758c4f4b1e8a432056ef0cd59b651b63e47b2d5e3
Objective (editorial): 全称命题的否定由存在反例表达
Context interpretation (pending): 存在量词命题的否定应为全称并否定性质，且论域与原命题严格一致。
Invalid edge / negative case: 「存在实数x使x²<0」的否定是所有实数x都有x²≥0。

## hs-semantic-pilot-123-c403 (COMPULSORY)
Original PDF printed p.17 lines 13-13; SHA256 6f6cb0afe080f7497a5bdebff2fb8444dd7285e88ec86c376335ade3abb8e937
Objective (editorial): 二次函数符号图解一元二次不等式
Context interpretation (pending): 图解二次不等式需要将抛物线与x轴交点、重根或无根情形区分。
Invalid edge / negative case: (x-1)²<0无解，不能把x=1当作解。

## hs-semantic-pilot-123-c404 (COMPULSORY)
Original PDF printed p.19 lines 24-24; SHA256 65150f2ffa1696eb67ab2d6c75dea4d1cc073746a376e257646dfad4cff4bcf3
Objective (editorial): 函数奇偶性须在关于原点对称的定义域上判断
Context interpretation (pending): 奇偶性必须先保证定义域关于原点对称，再核验f(-x)=±f(x)。
Invalid edge / negative case: f(x)=x²但只在x≥0定义时不称偶函数。

## hs-semantic-pilot-123-c405 (COMPULSORY)
Original PDF printed p.19 lines 25-25; SHA256 f33fb1f7fffce381d06531a2cc55dd338e147bd6ff554a6eeed24ce46c6463be
Objective (editorial): 周期函数的非零周期与最小正周期区别
Context interpretation (pending): 周期是非零平移保持函数值，最小正周期不一定存在。
Invalid edge / negative case: 常值函数所有正数都是周期，却没有最小正周期。

## hs-semantic-pilot-123-c406 (COMPULSORY)
Original PDF printed p.20 lines 21-21; SHA256 b547879065874e9af65999bae5ee56ce7ac5adf3c11073cfc8b16ae5aaaade12
Objective (editorial): 实数范围有理数指数幂的底数和根式条件
Context interpretation (pending): 实数有理指数幂的根式定义需要对负底、偶次根进行区分。
Invalid edge / negative case: (-1)^(1/2)在实数范围未定义。

## hs-semantic-pilot-123-c407 (COMPULSORY)
Original PDF printed p.20 lines 32-32; SHA256 6bf09af01e478c708a0624cc11c292f2c66ad82bbd3ad1d4e672f4846912b940
Objective (editorial): 对数换底公式的底数合法性核验
Context interpretation (pending): 换底公式的真数和新旧底必须正，底不等于1；对数分母非零。
Invalid edge / negative case: log_1 2无定义，不能套换底公式。

## hs-semantic-pilot-123-c409 (COMPULSORY)
Original PDF printed p.22 lines 14-14; SHA256 840a85700e346303fbb391352c0802f9ecf2bf9d1db720002b461fe5f2db4c49
Objective (editorial): 两角和差三角函数公式的推导与全实数角适用范围
Context interpretation (pending): 和差角公式是全实角恒等式；若推导中使用正切要另核对分母。
Invalid edge / negative case: tan(π/2)无定义，不能把正切加法式当作全实角恒等式。

## hs-semantic-pilot-123-c411 (COMPULSORY)
Original PDF printed p.31 lines 14-14; SHA256 9e6831927016d1439752d5c35ef0a0b9a8fee417a0cbbdaa76a16f7e69b435a2
Objective (editorial): 有限等可能样本空间上的古典概率计数
Context interpretation (pending): 古典概型需要有限、等可能基本结果；结果类别不代表等可能。
Invalid edge / negative case: 两骰点数和为2与和为7不等可能，不能按11种和值等分。

## hs-semantic-pilot-123-c412 (COMPULSORY)
Original PDF printed p.32 lines 25-25; SHA256 e00c3adccaa4753ec397145e28d1e1486905d4ba7f9fb8ad6cc5ee3c8750c6dc
Objective (editorial): 样本均值中位数众数估计总体位置的限制
Context interpretation (pending): 平均数、中位数和众数对应不同集中趋势，异常值使均值失真。
Invalid edge / negative case: 样本{1,2,100}的均值为103/3，而中位数是2。

## hs-semantic-pilot-124-c501 (COMPULSORY)
Original PDF printed p.19 lines 18-18; SHA256 5f38377ec5ea7c88c09b4ce847a77aa9f474aff6fc12ef27c11f47c6df9f711d
Objective (editorial): 按任务选择函数的解析式、表格和图像表征
Context interpretation (pending): 函数模型的图表解析式应保持同一定义域和单位，不可把有限描点当恒等证明。
Invalid edge / negative case: 仅通过(0,0),(1,1)不能确定函数在所有实数上是f(x)=x。

## hs-semantic-pilot-124-c502 (COMPULSORY)
Original PDF printed p.20 lines 29-29; SHA256 e930c7837461a569746d654a387e16c30b1a4734078ed77a5cba6e0183588255
Objective (editorial): 指数函数图像的描点和单调方向
Context interpretation (pending): 指数函数底数a>1时递增，0<a<1时递减；绘制需核对图像范围。
Invalid edge / negative case: y=(1/2)^x递减，并非所有指数函数递增。

## hs-semantic-pilot-124-c503 (COMPULSORY)
Original PDF printed p.20 lines 34-34; SHA256 4e2e9721f626c9ed37532262546d4c23a80a5bf5150308517daff4e49ede9e2c
Objective (editorial): 实对数函数的定义域、反函数关系与单调性
Context interpretation (pending): 对数函数真数x>0；底数a>0且a≠1，其单调性依底数分段。
Invalid edge / negative case: log_2(-1)实数域无定义，不能画到负x轴。

## hs-semantic-pilot-124-c504 (COMPULSORY)
Original PDF printed p.21 lines 3-3; SHA256 e0cf4c96cfc79d70b06243ce35a30590b95956b4ce536dadec0eaa42dbae6811
Objective (editorial): 指数函数与对数函数互为反函数的条件
Context interpretation (pending): 对数与指数互为反函数须维持x、y对应的域和底数合法性。
Invalid edge / negative case: log_1 x不构成函数，不能作y=1^x的反函数。

## hs-semantic-pilot-124-c505 (COMPULSORY)
Original PDF printed p.21 lines 27-27; SHA256 229741b5852a46cc94929debbd2878ead4add5e1b50e94c26d2f2bb2d2fa9235
Objective (editorial): 三角函数在主周期上的图像性质判读
Context interpretation (pending): 正弦余弦正切图像的周期及正切渐近线不同，不可整套套用同一周期。
Invalid edge / negative case: tan x的最小正周期为π，cos x为2π。

## hs-semantic-pilot-124-c506 (COMPULSORY)
Original PDF printed p.22 lines 2-2; SHA256 d26b96953f83a8fcafc23621c84a6b53a7394d13061b08669e468d8bea6bce23
Objective (editorial): 正弦模型振幅、周期、相位与现实单位
Context interpretation (pending): 正弦模型的振幅取|A|，角频率ω≠0才有2π/|ω|的最小正周期。
Invalid edge / negative case: A=0时常值函数无最小正周期，不能填2π/|ω|。

## hs-semantic-pilot-124-c507 (COMPULSORY)
Original PDF printed p.22 lines 13-13; SHA256 ba449b3cffb1f514e3cffca65dad24497570039aa4f52f7b975c79bbfb105015
Objective (editorial): 余弦差公式的单位圆向量证明
Context interpretation (pending): 差角余弦公式来自单位圆内积，所有实角有效；不能遗漏减号方向。
Invalid edge / negative case: cos(π/2-π/2)=1，而cos(π/2)cos(π/2)-sin(π/2)sin(π/2)=-1。

## hs-semantic-pilot-124-c508 (COMPULSORY)
Original PDF printed p.22 lines 16-16; SHA256 b370665847fa7deab42f7e1a9c43ec248e6a5ae7142fc8810eb11221f8c53f63
Objective (editorial): 和差角公式到积化和差的等价变换
Context interpretation (pending): 三角恒等变换需说明代数等价和原定义域，消去分母可能引入无定义点。
Invalid edge / negative case: 把sin x/cos x改写tan x时须排除cos x=0。

## hs-semantic-pilot-124-c509 (COMPULSORY)
Original PDF printed p.22 lines 28-28; SHA256 aa5f7bcea5d2b608679c40b919d5a2fc75a6cbfb50cc7da59a545b3b4b7525c8
Objective (editorial): 函数零点与方程实根的同一性
Context interpretation (pending): 函数零点是定义域内满足f(x)=0的输入，与方程根为同一个集合。
Invalid edge / negative case: f(x)=1/x没有零点，x=0却是禁止输入而非根。

## hs-semantic-pilot-124-c510 (COMPULSORY)
Original PDF printed p.23 lines 3-3; SHA256 211c94267074ab8d0539cf182f3ad7cb5cc82ea84ff5e920de2e327fdc5feba4
Objective (editorial): 真实问题建模中的变量、单位与适用域
Context interpretation (pending): 建模须明确量的单位与物理定义域，数学表达式不自动支持无限外推。
Invalid edge / negative case: 人口指数模型不能在未说明范围时推断无限时间人口。

## hs-semantic-pilot-124-c511 (COMPULSORY)
Original PDF printed p.23 lines 6-6; SHA256 1bbbe93269832a299e2292f76faa556eb7d594aa4a9a6b1f8d61901b5de35296
Objective (editorial): 比较不同函数增长速度时先统一量纲与区间
Context interpretation (pending): 比较增长先给相同尺度和正参数范围，再区分局部交叉与渐近增长。
Invalid edge / negative case: 在小区间内x²可小于或大于2^x，不能凭一个点给全局排名。

## hs-semantic-pilot-124-c512 (COMPULSORY)
Original PDF printed p.25 lines 22-22; SHA256 5f76bf9943cd13d30a7590f52c41583e92bc9ac4f5768e37cd8c137e5ea67e95
Objective (editorial): 位移和受力作为平面自由向量的建模前提
Context interpretation (pending): 力、速度、位移的向量表示必须区分物理单位和方向，不把不同量相加。
Invalid edge / negative case: 5m位移与5N力不能直接相加成10。

## hs-semantic-pilot-124-c513 (COMPULSORY)
Original PDF printed p.25 lines 24-24; SHA256 5e61e5b1154a31e10c0c903d03140f640e95dd7ff8c1ccbc6992693986ebdf74
Objective (editorial): 平面向量的长度方向和零向量区别
Context interpretation (pending): 平面向量有模和方向；零向量模为0但方向不确定。
Invalid edge / negative case: 零向量和非零向量之间的夹角不能定义。

## hs-semantic-pilot-119-s15 (SELECTIVE_COMPULSORY)
Original PDF printed p.48 lines 14-18; SHA256 511baee1a725b1c7a54a131bf78e8b209085a65edacda8b97ceeb22327e1967c
Objective (editorial): 一元回归最小二乘斜率与截距
Context interpretation (pending): 最小二乘斜率需样本自变量离差平方和严格正；预测不等于因果。
Invalid edge / negative case: 所有x_i都相等时带截距回归斜率无法唯一确定。

## hs-semantic-pilot-119-s16 (SELECTIVE_COMPULSORY)
Original PDF printed p.48 lines 19-21; SHA256 c9b8973fd5a0e97a1e4250f0f0e53608c4afec0e15cb26971090dc280e90ba22
Objective (editorial): 二乘二列联表与独立性检验
Context interpretation (pending): 二乘二列联表必须有合法的非负计数；独立性检验不能直接宣布因果。
Invalid edge / negative case: 样本量为0或边际频数为0时通常卡方近似条件不满足。

## hs-semantic-pilot-120-s101 (SELECTIVE_COMPULSORY)
Original PDF printed p.38 lines 18-20; SHA256 216bea8f5d7341aa38e5ea06aeb71fa13ad5b36f022d4551b39b734f8ab2e3f9
Objective (editorial): 等差结构的建模与线性函数联系
Context interpretation (pending): 等差数列公差相同，取n从规定起始整数递推；与一次函数只是在离散点联系。
Invalid edge / negative case: {n²}相邻差为2n+1，不是等差数列。

## hs-semantic-pilot-120-s102 (SELECTIVE_COMPULSORY)
Original PDF printed p.38 lines 25-27; SHA256 500a38f9dfafa177fe2693ac124a4d28fdd454dd97f2104c32cbe722cb8b441e
Objective (editorial): 等比递推的增长模型及指数联系
Context interpretation (pending): 等比数列公比按标准定义需合法且相邻项商有定义；与指数函数关系保留离散域。
Invalid edge / negative case: 数列1,0,0不能按相邻项商定义非零公比等比数列。

## hs-semantic-pilot-120-s103 (SELECTIVE_COMPULSORY)
Original PDF printed p.39 lines 9-13; SHA256 7a1a8fb4fb139e830d749f72e55295a298510858cdc0b6d96b75bb6b34812eb0
Objective (editorial): 平均变化率到瞬时变化率的极限过渡
Context interpretation (pending): 平均变化率到导数须说明h→0极限存在；图像看似光滑不足证明导数存在。
Invalid edge / negative case: f(x)=|x|在0左右差商分别±1，故不可导。

## hs-semantic-pilot-120-s104 (SELECTIVE_COMPULSORY)
Original PDF printed p.39 lines 15-21; SHA256 fed20d84ccb916026aaf00653d35b7f2f9578433a52a68e22619910b83e2a904
Objective (editorial): 常见幂函数按定义求导的定义域核验
Context interpretation (pending): 常见函数用定义求导逐个核验定义域；根函数和倒数函数在边界不适用。
Invalid edge / negative case: 1/x在x=0未定义，√x在0没有有限双侧实导数。

## hs-semantic-pilot-120-s105 (SELECTIVE_COMPULSORY)
Original PDF printed p.42 lines 14-17; SHA256 2df559aa7a85d6b1d546f88be6409cf42797a3d6a3feed24cdf25225e8a4f23c
Objective (editorial): 空间两点间坐标距离公式
Context interpretation (pending): 空间两点距离由各坐标差平方和开方得到，三维坐标轴必须正交单位尺度一致。
Invalid edge / negative case: 两点相同时距离为0，不能做以距离为分母的方向单位化。

## hs-semantic-pilot-120-s106 (SELECTIVE_COMPULSORY)
Original PDF printed p.42 lines 22-25; SHA256 33e576842508af009b742c40d4ef97510c3d06e67d09d53636e0c8c928a7ab7b
Objective (editorial): 空间向量正交基分解的唯一性
Context interpretation (pending): 空间向量在正交标准基上的展开唯一；若基退化则不可以直接按正交公式投影。
Invalid edge / negative case: 三向量中有零向量或线性相关时不构成空间基。

## hs-semantic-pilot-120-s107 (SELECTIVE_COMPULSORY)
Original PDF printed p.43 lines 22-23; SHA256 0ecbe750560f850e58214cdcaf6bbcb08b6e49ee6694cfa5a3fc1af95a00e9c9
Objective (editorial): 直线倾斜角与斜率的定义域
Context interpretation (pending): 斜率是直线倾斜的正切，竖直直线倾斜角有定义但斜率无定义。
Invalid edge / negative case: x=2是合法竖直直线，却不能写成y=kx+b。

## hs-semantic-pilot-120-s108 (SELECTIVE_COMPULSORY)
Original PDF printed p.43 lines 24-24; SHA256 f14e1245865fc0aabf58f9c2b1c6930c3f37c879ef95cf79a5b0295c652e5095
Objective (editorial): 两直线斜率判断平行或垂直
Context interpretation (pending): 以斜率判平行垂直须分开核验竖直、水平直线和重合情形。
Invalid edge / negative case: x=1与x=2平行但两者都没有斜率。

## hs-semantic-pilot-120-s109 (SELECTIVE_COMPULSORY)
Original PDF printed p.43 lines 25-26; SHA256 1fb94ea18e785fd1c29271e4e7d486f450af5e9e38e5da00dfb49c310dc4b32a
Objective (editorial): 直线点斜式与一般式转换
Context interpretation (pending): 点斜式要求斜率存在，一般式Ax+By+C=0要求(A,B)不全零。
Invalid edge / negative case: A=B=0,C=1得到0=1不是直线。

## hs-semantic-pilot-120-s110 (SELECTIVE_COMPULSORY)
Original PDF printed p.43 lines 27-28; SHA256 a527785553949d95ebafa64de626ce5e8b2e67d80e50f2eb9c7d8cc619153d94
Objective (editorial): 直线交点的线性方程组判别
Context interpretation (pending): 两直线交点解方程组可能无解、唯一或无穷多解，分清平行和重合。
Invalid edge / negative case: x=0与x=1无交点；两条相同直线有无穷多公共点。

## hs-semantic-pilot-120-s111 (SELECTIVE_COMPULSORY)
Original PDF printed p.44 lines 12-13; SHA256 afefccad2872a0a11279e7454e66c5ace300348d8c3e85a1d6ae37851480f0b7
Objective (editorial): 椭圆作为两焦点距离和为定长的点集
Context interpretation (pending): 椭圆距离和定义须常数大于两焦点距离；等于时退化线段。
Invalid edge / negative case: 两焦点相距4而距离和为4不构成非退化椭圆。
