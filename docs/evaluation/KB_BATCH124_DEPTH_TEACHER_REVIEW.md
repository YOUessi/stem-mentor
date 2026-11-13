# Batch124 — eight teacher-only complete original lessons

These are deliberately REVIEW_PENDING; finite SymPy witnesses are not a universal proof or teacher approval.

## 指数函数图像的描点和单调方向

Track: COMPULSORY · hs-semantic-pilot-124-c502
**Statement:** 给定实数a>0且a≠1，函数f(x)=a^x定义在R上、取值在(0,∞)；若a>1则严格递增，若0<a<1则严格递减。图像经过(0,1)，且在实数范围内不与x轴相交。
**Symbols:** a为正且不为1的底数，x为实指数，f(x)为对应正值，R为实数集合；x1、x2表示任意满足x1<x2的两个输入。
**Applicability:** 必须区分a>1和0<a<1；图形描点仅作观察，单调性使用指数律和底数条件解释。
**Justification:** 设x2>x1，则f(x2)/f(x1)=a^(x2−x1)>0；当a>1比值>1，当0<a<1比值<1。这对所有实数输入成立，因此给出单调性的理由。

1. 确认合法底数 — 检查a>0且a≠1；负数底数的任意实数幂未必有实值。
2. 用正指数差比较 — 任取x2>x1，比值a^(x2−x1)相对于1的位置决定大小次序。
3. 描点并核对形态 — 标出(0,1)以及两个一正一负的输入点；图像形态须与全域单调方向一致。

**Boundary:** 当a=1时是常数1而非通常定义的指数函数；a=0不能对负实指数定义；有限描点本身不构成单调证明。
**Typical wrong reasoning:** 错误解法：因为2^1>2^0，所以断言所有正底数指数函数都递增。
**Why wrong:** 底数0<a<1时，a^2<a^1；比较方向由底数而不是指数的数值符号决定。

**Teacher-only example 1:** 画出y=2^x在x=−2,0,2的点并判单调。
- 计算f(−2)=1/4、f(0)=1、f(2)=4。
- 底数2>1，结合正指数差性质可判断严格递增。
- Answer (teacher only): 三个点为(−2,1/4),(0,1),(2,4)，严格递增。
- Independent exact witness: 2^(-2)=1/4，2^2=4。

**Teacher-only example 2:** 判断g(x)=(1/2)^x的单调方向并求g(−2),g(1)。
- 底数1/2处于(0,1)，所以全域递减。
- 负指数g(−2)=4，正指数g(1)=1/2。
- Answer (teacher only): 全域严格递减；4和1/2。
- Independent exact witness: (1/2)^(-2)=4。

**Student hint ladder (does not reveal full teacher answer):**
1. 先检查底数处于哪一个区间。
2. 计算任意x2>x1时函数值的比值。
3. 用(0,1)和另一组点检查你的单调方向。
**Near transfer:** 对底数3和1/3，比较x=−1与x=2处的函数值。
**Far transfer:** 某传感器信号每小时按0.8比例衰减，解释为何时间增长时总量下降；并说明负时间外推是否符合现实情境。

## 实对数函数的定义域、反函数关系与单调性

Track: COMPULSORY · hs-semantic-pilot-124-c503
**Statement:** 对a>0且a≠1，实对数函数y=log_a(x)定义于x>0，并由a^y=x唯一确定。它与指数函数y=a^x互为反函数，图像关于直线y=x对称；a>1递增，0<a<1递减。
**Symbols:** a是实数底数，x是正实自变量，y=log_a(x)为唯一实指数；指数映射以R为定义域，以正实数为值域。
**Applicability:** 真数x必须严格为正，底数a必须为正且不等于1；单调方向不可只按画图猜测。
**Justification:** 当a>1时指数函数一一且严格递增，逆函数保持增序；0<a<1时指数函数一一且严格递减，其逆函数仍严格递减。交换点(x,y)坐标得到关于y=x的对称。

1. 检查实数对数前提 — 排除x≤0、a≤0和a=1；这些条件会使实数反函数的定义失效。
2. 转成指数方程 — 令y=log_a(x)，由定义有a^y=x；先求唯一的y。
3. 核对图像和单调 — 对指数图上的(x,a^x)交换两坐标；判断逆函数增减与底数一致。

**Boundary:** 当x=0时对数无实数值；不能因log_a(1)=0而误以为log_a(0)=1；x<0在实数范围同样不可定义。
**Typical wrong reasoning:** 错误解法：因为log_2(8)=3，断言log_(1/2)(8)也等于3。
**Why wrong:** 对数以底数为参数，(1/2)^3=1/8而不是8；底数改变可能颠倒单调方向。

**Teacher-only example 1:** 计算log_2(8)并写出指数逆关系。
- 寻找使2^y=8的实数指数y。
- 2^3=8，所以log_2(8)=3。
- Answer (teacher only): 3；同时2^3=8。
- Independent exact witness: 2^3=8。

**Teacher-only example 2:** 计算log_(1/2)(4)，并指出该对数函数的单调方向。
- 解(1/2)^y=4=2^2。
- 因此−y=2，y=−2；底数介于0和1，函数递减。
- Answer (teacher only): −2；严格递减。
- Independent exact witness: (1/2)^(-2)=4。

**Student hint ladder (does not reveal full teacher answer):**
1. 真数和底数是否合法？
2. 将对数写成等价指数式。
3. 用底数所在区间判定逆函数的增减。
**Near transfer:** 求log_3(1/9)，同时指出其定义域和值域。
**Far transfer:** 某声音强度以对数刻度表示，说明零强度和负强度不能直接送入实对数，且改变对数底数需要更新标尺。

## 正弦模型振幅、周期、相位与现实单位

Track: COMPULSORY · hs-semantic-pilot-124-c506
**Statement:** 非退化模型f(t)=A sin(ωt+φ)中A≠0、ω≠0，振幅为|A|，最小正周期为2π/|ω|，水平相位移动为−φ/ω；若t有时间单位则ω的量纲为弧度每单位时间。
**Symbols:** A是有符号振幅系数，ω是非零角频率，φ是弧度相位，t为自变量；周期T>0满足f(t+T)=f(t)。
**Applicability:** 所给公式没有额外垂直偏移；A和ω必须非零方能将振幅、最小正周期与平移写为通常的非退化形式。
**Justification:** 因sin(z+2π)=sin z，令ωT=±2π得到最小正周期2π/|ω|；|sin z|≤1给振幅|A|；令ωt+φ=ω(t+φ/ω)给平移参数。

1. 辨认三个参数 — 把函数整理为A sin(ωt+φ)并明确正弦内部的角度以弧度计算。
2. 求振幅和周期 — 读出|A|以及T=2π/|ω|，不能把ω的负号带进正周期。
3. 核对相位和单位 — 以t+φ/ω重写内部角度，若t以秒计则ω单位为rad/s。

**Boundary:** ω=0时为常数，没有最小正周期；A=0时零函数同样无最小正周期；只有一段近似正弦数据不能证明系统长期严格周期。
**Typical wrong reasoning:** 错误解法：把sin(2t+π/6)的水平移动直接写成−π/6，而没有除以2。
**Why wrong:** 内部角度增量是ω乘以时间位移，真正的平移必须是−φ/ω，不能拿相位角直接当时间。

**Teacher-only example 1:** 求3sin(2t+π/6)的振幅、周期和水平移动。
- 振幅是3，周期2π/2=π。
- 写成3sin[2(t+π/12)]，故向左π/12。
- Answer (teacher only): 振幅3；周期π；左移π/12。
- Independent exact witness: ω=2；φ/ω=π/12。

**Teacher-only example 2:** 求−2sin(−4t+π/2)的振幅及最小正周期。
- 绝对振幅|−2|=2。
- 角频率|−4|=4，正周期为π/2。
- Answer (teacher only): 振幅2；最小正周期π/2。
- Independent exact witness: 4×(π/2)=2π。

**Student hint ladder (does not reveal full teacher answer):**
1. 先读出A、ω、φ而不是只看符号。
2. 周期永远为正，用|ω|。
3. 把内部角度因式分解求相位平移。
**Near transfer:** 对2cos(5t−π)写出振幅与周期，并解释改用余弦不改变周期公式。
**Far transfer:** 用简谐运动记录解释为何把频率Hz直接填入ω的数值会错过2π因子；标注时间轴单位。

## 余弦差公式的单位圆向量证明

Track: COMPULSORY · hs-semantic-pilot-124-c507
**Statement:** 对任意实数α、β，都有cos(α−β)=cosα cosβ+sinα sinβ。证明可以通过旋转不变的单位向量内积完成，整个证明不用除以sin或cos。
**Symbols:** α、β是任意实弧度角；u=(cosα,sinα)、v=(cosβ,sinβ)为长度1的单位向量；u·v是欧氏内积。
**Applicability:** 两向量始终为单位向量，夹角差可按旋转相对角解释；定理没有正切式的分母非零限制。
**Justification:** 由坐标定义u·v=cosαcosβ+sinαsinβ；由平面内积的角度形式u·v=|u||v|cos(α−β)=cos(α−β)，两表达相等。

1. 构造单位圆向量 — u=(cosα,sinα)、v=(cosβ,sinβ)，直接用sin²+cos²=1确保两者长度为1。
2. 使用坐标内积 — 逐项相乘相加得到cosαcosβ+sinαsinβ。
3. 使用几何内积 — 两向量夹角的有向差经过余弦变成cos(α−β)，模均为1；联立两式即得。

**Boundary:** α或β使cos为零时公式依旧成立；若先经tan(α−β)证明，cosαcosβ可能为零，要另外补充端点情况。
**Typical wrong reasoning:** 错误解法：把cos(α−β)展成cosα−cosβ，或把余弦差公式写成含负号的内积。
**Why wrong:** 差公式的正号来自旋转角差的内积；取α=β立刻可用cos0=1核验错误的展开。

**Teacher-only example 1:** 通过差角公式精确计算cos(π/3−π/6)。
- 代入cosπ/3=1/2、cosπ/6=√3/2。
- 代入sinπ/3=√3/2、sinπ/6=1/2，相加√3/2。
- Answer (teacher only): √3/2。
- Independent exact witness: 独立核验cos(π/6)=√3/2。

**Teacher-only example 2:** 计算cos(0−π)，并验证内积形式。
- 原式cos(−π)=−1。
- 右边cos0 cosπ+sin0 sinπ=(1)(−1)+0=−1。
- Answer (teacher only): −1。
- Independent exact witness: 单位向量(1,0)与(−1,0)的内积为−1。

**Student hint ladder (does not reveal full teacher answer):**
1. 先画两个单位圆向量，不要套正切。
2. 将内积写成坐标形式。
3. 再将内积写成模与夹角形式比较。
**Near transfer:** 用余弦差公式推导cos(α+β)，并核对α=π/2的特殊情况。
**Far transfer:** 在二维机器人朝向测量中，用两个归一化朝向向量的内积估计相对夹角余弦；解释为什么仅有余弦不能区分顺逆时针。

## 基本几何体体积公式的高度与半径前提

Track: COMPULSORY · hs-semantic-pilot-124-c516
**Statement:** 半径r≥0、高h≥0的直圆柱体积V=πr²h；同底同高的直圆锥体积V=πr²h/3。棱柱一般用底面积乘垂直高；公式中的h绝非斜高。
**Symbols:** r是圆形底面的半径，h是底面至顶点或另一底面的垂直距离，π是圆周率，V是三维体积。
**Applicability:** 采用欧氏空间理想直圆柱或直圆锥，底面是圆，高垂直底面；必须给出一致的长度单位。
**Justification:** 圆柱截面积恒为πr²，沿高度累计得πr²h。圆锥距顶点z处横截面半径按相似三角形为rz/h（h>0），积分0到h得πr²h/3。

1. 识别底面半径和垂直高 — 检查斜长与垂直高度的区别，并把半径与垂高的计量单位统一。
2. 计算圆底面积 — 圆底面积为πr²，半径平方后的计量单位是面积单位，不能和长度混用。
3. 根据形状取系数 — 柱体乘h；锥体多乘1/3，来自相似截面面积沿高的累计。

**Boundary:** r=0或h=0的几何体退化且体积为零；积分推导使用h>0，退化边界靠直接几何解释。斜圆锥须明确其截面关系。
**Typical wrong reasoning:** 错误解法：圆锥半径3、垂直高度4时把斜母线长度5错当作公式中的高度h直接代入。
**Why wrong:** 母线与底面不垂直；把它代入体积公式会把正确的12π错算成15π，违反公式要求使用垂直高这一数学前提。

**Teacher-only example 1:** 求半径2、高3的直圆柱体积。
- 底面积π×2²=4π。
- 乘以垂直高3，得12π。
- Answer (teacher only): 12π立方单位。
- Independent exact witness: π×4×3=12π。

**Teacher-only example 2:** 求半径3、垂高4的直圆锥体积。
- 底面积π×9。
- 乘以4并除以3，得12π。
- Answer (teacher only): 12π立方单位。
- Independent exact witness: π×9×4/3=12π。

**Student hint ladder (does not reveal full teacher answer):**
1. 先画出底面与垂直的高。
2. 底面积是多少？
3. 锥体与同底同高柱体积的比是多少？
**Near transfer:** 若圆锥半径加倍、垂高不变，体积变成原来的几倍？解释原因。
**Far transfer:** 估算圆柱储水桶容量时，把厘米转成米并把立方米换算成升；分析钢桶外径不能直接代入内部容积的原因。

## 同一样本空间事件并集概率的容斥关系

Track: COMPULSORY · hs-semantic-pilot-124-c521
**Statement:** 对同一概率空间的任意事件A、B，有P(A∪B)=P(A)+P(B)−P(A∩B)。如果A∩B为空集，才可简化为P(A∪B)=P(A)+P(B)。
**Symbols:** Ω是样本空间；A、B为事件；∪表示并，∩表示交，P为满足概率公理的概率测度。
**Applicability:** 所有事件须来自同一个概率空间；不要求独立或等可能；仅在互斥条件下交集概率才能省略。
**Justification:** 把A∪B分成互不相交的A\B、B\A、A∩B三部分。由有限可加性相加，再分别写P(A)=P(A\B)+P(A∩B)及P(B)=P(B\A)+P(A∩B)，消去多算的一次交集。

1. 确认同一样本空间 — 先明确事件与基本结果，不混用来自不同实验或条件下的概率。
2. 找出重叠部分 — 写出A∩B；若不为空，直接相加会把属于交集的样本结果计算两遍。
3. 利用互斥分解 — 由概率可加性得到并集公式，并检查结果位于[0,1]。

**Boundary:** 独立并不意味着互斥；只有独立且至少一个事件概率为零时交集概率才为零。两个事件相同也完全合法。
**Typical wrong reasoning:** 错误解法：在掷一枚公平六面骰子的实验中，事件A={1,2,3}、B={3,4}，直接算3/6+2/6=5/6。
**Why wrong:** 数字3同时属于两个事件，重复计数一次；并集实际只有四个不同结果，概率为4/6。

**Teacher-only example 1:** 公平六面骰子：A={1,2,3}，B={3,4}，求P(A∪B)。
- 两事件概率分别3/6与2/6，交集{3}概率1/6。
- 代入公式得到(3+2−1)/6=4/6。
- Answer (teacher only): 2/3。
- Independent exact witness: 集合并集{1,2,3,4}大小4。

**Teacher-only example 2:** 公平六面骰子：奇数A={1,3,5}，质数B={2,3,5}，求P(A∪B)。
- 交集{3,5}大小2。
- (3+3−2)/6=4/6。
- Answer (teacher only): 2/3。
- Independent exact witness: 并集{1,2,3,5}大小4。

**Student hint ladder (does not reveal full teacher answer):**
1. 先求A∩B而不是直接相加。
2. 将并集分为重叠和不重叠区域。
3. 代入P(A)+P(B)−P(A∩B)，再检查上界1。
**Near transfer:** 从一副52张扑克牌取一张，求抽到红牌或A的概率，写清交集有几张。
**Far transfer:** 检测系统误报事件与传感器失效事件可能同时发生：解释为何不能把两个故障率直接相加当总故障率。

## 用抛物线焦点准线定义解决距离应用

Track: SELECTIVE_COMPULSORY · hs-semantic-pilot-124-s502
**Statement:** 固定焦点F不在准线l上，平面点P满足|PF|=d(P,l)的轨迹为非退化抛物线。标准情形F=(0,p)，l:y=−p且p>0，轨迹满足x²=4py。
**Symbols:** F是固定焦点；l是固定直线准线；P=(x,y)是动点；d(P,l)是点到直线的非负垂直距离；p为正实数。
**Applicability:** 焦点不得落在准线上；标准式选取p>0，若需要其他朝向须先平移旋转或改变符号。
**Justification:** 由距离定义得sqrt(x²+(y−p)²)=|y+p|。两边都是非负数，所以可安全平方，消去y²+p²并得到x²=4py；反向须检查符号条件，p>0且y=x²/(4p)≥0保证y+p>0。

1. 建立焦点与准线坐标 — 把焦点写作(0,p)、准线写作y=−p，并明确p>0。
2. 写出相等距离 — 点到焦点用欧氏距离的平方根表达式，点到水平准线用竖直坐标之差的绝对值。
3. 平方并做反向核查 — 平方推得x²=4py；利用y≥0验证每个代数解也满足未平方的非负距离等式。

**Boundary:** p=0时焦点位于准线上，定义退化为直线集合而非标准抛物线；只验证个别点不能代替对整个轨迹的证明。
**Typical wrong reasoning:** 错误解法：仅从点到焦点与直线距离的平方相等就宣称任何p包括0都定义同样的抛物线。
**Why wrong:** 平方可能隐去符号和退化信息；p=0改变几何轨迹，失去非退化焦点准线定义。

**Teacher-only example 1:** F=(0,1)，准线y=−1，检验P=(2,1)是否在抛物线上。
- 焦点距离sqrt((2−0)²+(1−1)²)=2。
- 准线距离|1+1|=2；也满足x²=4y。
- Answer (teacher only): 是；两距离均为2。
- Independent exact witness: 2²=4×1。

**Teacher-only example 2:** 仍用同一抛物线，判断原点是否在轨迹上。
- 原点到焦点距离1。
- 到准线距离|0+1|=1，满足距离定义。
- Answer (teacher only): 是；两距离均为1。
- Independent exact witness: 0²=4×0。

**Student hint ladder (does not reveal full teacher answer):**
1. 先确认焦点有没有落在准线上。
2. 分别写出点到焦点和点到准线距离。
3. 平方后反向检验，不能忽略绝对值。
**Near transfer:** 焦点(0,2)且准线y=−2时写出轨迹方程，并检查(4,2)。
**Far transfer:** 卫星反射面截线常近似采用抛物线：解释焦点准线只是理想几何模型，制造误差不一定精确满足定义。

## 空间内积和叉积几何意义的非零条件

Track: ELECTIVE_B · hs-semantic-pilot-124-b501
**Statement:** 在三维欧氏空间，u·v=|u||v|cosθ，|u×v|=|u||v|sinθ（0≤θ≤π）。叉积u×v方向由右手定则确定，且垂直于u、v。
**Symbols:** u、v是三维实向量；θ是仅对u、v均非零时定义的夹角；·为标量内积；×为三维向量叉积。
**Applicability:** 讨论夹角必须假设两个向量均非零；叉积可计算零向量但其方向此时不可定义；右手定则依赖三维定向坐标系。
**Justification:** 先把向量差的模平方展开并与余弦定理比较，得到u·v=|u||v|cosθ。叉积坐标由三组二阶行列式构造，与u、v分别点乘后成对抵消为0；展开其平方模得到拉格朗日恒等式|u×v|²=|u|²|v|²−(u·v)²，非零向量时等于|u|²|v|²sin²θ，故模取非负值。

1. 推导内积与余弦关系 — 将|u−v|²展开为|u|²+|v|²−2u·v，再同余弦定理比较；对非零向量除以两模即可得cosθ。
2. 构造三维叉积并验证垂直 — 写出三个二阶行列式坐标，分别与u、v点乘，相反项完全抵消得到两个零。
3. 展开叉积平方模 — 逐项展开得到|u×v|²=|u|²|v|²−(u·v)²；θ∈[0,π]确保sinθ≥0，再开非负平方根，方向依据右手定则。

**Boundary:** 当u与v非零且平行时叉积为零，但两向量的长度仍可严格为正；零向量不存在唯一角度，不能把夹角公式延用到这一退化情形。
**Typical wrong reasoning:** 错误解法：认为u×v就是|u||v|sinθ这个实数，或者把两个向量顺序反过来仍得到相同的叉积。
**Why wrong:** 叉积是有方向的三维向量，且v×u=−(u×v)；公式|u×v|才是非负标量。

**Teacher-only example 1:** u=(1,0,0)，v=(0,1,0)，求内积和叉积。
- 坐标内积为0。
- 叉积按右手规则为(0,0,1)，模为1。
- Answer (teacher only): u·v=0，u×v=(0,0,1)。
- Independent exact witness: 两个向量长度均1且夹角90度。

**Teacher-only example 2:** u=(1,2,0)，v=(3,0,0)，求内积、叉积与叉积模。
- 内积1×3+2×0=3。
- 叉积(0,0,−6)，模为6。
- Answer (teacher only): 内积3；叉积(0,0,−6)；模6。
- Independent exact witness: 坐标行列式与勾股计算核验。

**Student hint ladder (does not reveal full teacher answer):**
1. 先判定输出应该是数还是向量。
2. 直接用三维坐标公式计算。
3. 检查叉积是否与原向量内积都为0。
**Near transfer:** 交换前题u、v的顺序，再求叉积；说明结果为什么会变号。
**Far transfer:** 机器人末端的转矩为位置向量与力的叉积：讨论力作用线穿过参考点时叉积为零是否表示力也为零。


## Math verification boundaries
{
  "batch": 124,
  "lesson_count": 8,
  "exact_worked_cases_passed": 16,
  "independent_negative_checks_passed": 8,
  "cross_topic_exact_checks_passed": 8,
  "general_formal_theorems_proven": 0,
  "student_free_text_steps_certified": 0,
  "teacher_approved": 0,
  "student_authoritative": 0,
  "per_lesson": {
    "B501": {
      "worked_examples": 2,
      "negative_cases": 1,
      "cross_topic": 1
    },
    "C502": {
      "worked_examples": 2,
      "negative_cases": 1,
      "cross_topic": 1
    },
    "C503": {
      "worked_examples": 2,
      "negative_cases": 1,
      "cross_topic": 1
    },
    "C506": {
      "worked_examples": 2,
      "negative_cases": 1,
      "cross_topic": 1
    },
    "C507": {
      "worked_examples": 2,
      "negative_cases": 1,
      "cross_topic": 1
    },
    "C516": {
      "worked_examples": 2,
      "negative_cases": 1,
      "cross_topic": 1
    },
    "C521": {
      "worked_examples": 2,
      "negative_cases": 1,
      "cross_topic": 1
    },
    "S502": {
      "worked_examples": 2,
      "negative_cases": 1,
      "cross_topic": 1
    }
  }
}
