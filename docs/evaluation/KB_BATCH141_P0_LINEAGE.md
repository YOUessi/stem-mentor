# Batch141｜47条历史P0高风险证明步骤：新式来源锁定卡的完整补齐

**范围说明：迁移并重新锁定的是KB29/KB30已有数学前提审查内容，绝非新增47份数学证明。**
127/127 P0原本已有KB28/29/30编辑记录；从另一种来源卡格式的80/127补到127/127。
全部47条的原始数学陈述、理由、原始步骤SHA与早期编辑记录SHA均被逐项检查。
独立的精确有限案例另行覆盖12条步骤、共24个案例；余35条仅建立来源一致性卡。
这不是全量538条历史证明步骤的形式认证，也不能关闭既有10项数学冲突。
七轨正式知识原子分母仍UNKNOWN；教师批准0；学生权威发布0。

## math.hs.calculus.tangent-line#3

原始SHA-256: `22515d6f53186a912efbe626afaefb4a866bd83ce608b2ee1ade88c701eaf488`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `e9bc1a3d60601f805b4023020391d7b25f9b137a308a7800eb682efee57762ba`）
原始命题步骤: 过点 (x₀,f(x₀)) 且斜率 m 的直线满足 y−f(x₀)=m(x−x₀)。
历史说明（未独立认证）: 直线点斜式与可导点的切线斜率定义结合。
### 必须前提
函数在所讨论的 x0 须可导且导数有限，切线使用点 (x0,f(x0)) 与斜率 f'(x0)；这里的受控多项式检查只证明有理输入实例，不替代一般函数的可导性证明。
### 不适用反例/边界
取 f(x)=|x| 且 x0=0，左右差商不同，没有有限导数，不能取普通点斜式的切线斜率；缺失所求点也无法核验。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.complex.operations#2

原始SHA-256: `ec8f5b7ba6d3de1097dc510c0587911ab5ad6251a012a2a88123824cfdb0c4f3`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `349f69da0b2aebf2789072a3ac4d54f0854b71573570e7daa96613eccc84adff`）
原始命题步骤: (a+bi)(a−bi)=a²−(bi)²=a²+b²，且它是非负实数。
历史说明（未独立认证）: 使用平方差公式并把 i² 替换为 −1。
### 必须前提
复数 w=c+di 的共轭乘积 w·conj(w)=c²+d²；只有 c、d 不同时为零时，c²+d²>0，才可同乘非零共轭并约去分母。
### 不适用反例/边界
取 w=0+0i，其共轭仍为零，c²+d²=0；即使式子形式上能写出，也绝不能把零除法当作复数合法运算。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.complex.operations#3

原始SHA-256: `b55367f3d234011f6726b7bd09575d923b749649ce6e3c3f364f7dda676cad10`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `6ebc524e7cc6d536c821258f701529d6b6fe88a84aa8e994b1f8d006086255a9`）
原始命题步骤: 若 w=c+di≠0，则 c²+d²>0，可用共轭 c−di 约去分母得到给定商式。
历史说明（未独立认证）: 分子分母同乘非零的 w̅，不改变商；再展开乘积整理。
### 必须前提
复数 w=c+di 的共轭乘积 w·conj(w)=c²+d²；只有 c、d 不同时为零时，c²+d²>0，才可同乘非零共轭并约去分母。
### 不适用反例/边界
取 w=0+0i，其共轭仍为零，c²+d²=0；即使式子形式上能写出，也绝不能把零除法当作复数合法运算。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.calculus.differentiable-continuous#1

原始SHA-256: `9bdd828d6eca6152b1af69dc0e9f21477c1b44ce85355ef33de419e58a99a60c`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `ef0f281cd340320b29fa789e9cd69126c80ae37f515871c4c54838d5ad3f9fa7`）
原始命题步骤: 将函数值差写作 f(a+h)-f(a)=h·[(f(a+h)-f(a))/h]，h≠0。
历史说明（未独立认证）: 这是对非零 h 的代数恒等式，没有在 h=0 时除零。
### 必须前提
必须在 a 的邻域内定义 f，并仅对 h≠0 使用商式；在该点可导意味着差商有有限极限，乘回趋零的 h 才推出函数值差趋零。端点导数需要明确单侧定义。
### 不适用反例/边界
在 h=0 代入差商会除零；令 f(0)=0 而 f(x)=1 (x≠0)，此时 f 在 0 不连续，差商 1/h 无有限极限。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.calculus.second-derivative-convexity#3

原始SHA-256: `06b77362b65510ae1fd60eab47363f35c16cc076b81132c664df05a32b88a323`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `77d8c71dd9f30918524a8b131be2cae60b57147c14ca20638b4235f14091b0fc`）
原始命题步骤: 由f'非减得到 (f(z)-f(x))/(z-x)≤(f(y)-f(z))/(y-z)，交叉乘正数得到 f(z)≤((y-z)/(y-x))f(x)+((z-x)/(y-x))f(y)。
历史说明（未独立认证）: 斜率单调为凸性不等式；端点z=x,y直接取等号。
### 必须前提
要求 x<z<y 为同一区间内三点，f 在其间连续、内点可导，f′非减；交叉相乘的 z−x、y−z 和 y−x 必须严格为正。端点 z=x 或 z=y 另取等号。
### 不适用反例/边界
取 f(t)=−t²，x=−1,z=0,y=1，得 f(z)=0>−1，反驳凸性弦不等式；若颠倒点次序，乘负数需改变不等号方向。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.finance.annuity-present-value#3

原始SHA-256: `4137d5386349e888d1707ad29cb98c5be76b14e36856f80936215145116f0820`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `c33e56fdfad37351c7b7f81ae525464fbfb38e4a7c44eeeb8bd0944cb6b85a95`）
原始命题步骤: 当i≠0时q≠1，等比求和为q(1-q^n)/(1-q)=[1-(1+i)^{-n}]/i。
历史说明（未独立认证）: 代数整理并保证分母i非零。
### 必须前提
期数 n 为正整数，期利率 i 满足 1+i>0 以确保正常贴现；使用公比求和分式的这一支必须 i≠0，即 q=(1+i)⁻¹≠1。
### 不适用反例/边界
i=0 时每期贴现因子为 1，现值系数为 n，不能用 [1−(1+i)⁻ⁿ]/i 的 0/0；i=−1 时贴现因子根本不存在。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.function.epsilon-delta-square#2

原始SHA-256: `19c0423859af8ab752125b4fc7470915b0cc12d2ed1aa3e2c8680545fcb24168`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `76c5b66a9af8389d2e008b8bb4d718731b1cecce72b4d8fd303d4ee555e71fc7`）
原始命题步骤: 由 |x+a|≤|x-a|+2|a|<1+2|a|，取 δ=min(1,ε/(1+2|a|))。
历史说明（未独立认证）: δ>0 且只依赖 a 与给定 ε，分母恒正。
### 必须前提
a 为给定实数，ε>0；令 δ=min(1,ε/(1+2|a|))>0，仅从 0<|x−a|<δ 得到 |x+a|<1+2|a|，从而 |x²−a²|<ε。
### 不适用反例/边界
若未先控制 |x−a|<1，仅设 δ=ε/(1+2|a|) 的估计步骤并不自动有效；若 ε≤0，则 δ 不是有效的正邻域半径。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.geometry.euclidean-isometries#2

原始SHA-256: `6d31db6e3c4960cc35f560bfc0829a33ed5b0ea0bb69bb174147aad591d7c555`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `cedf27616a24d6861059d750a4948c696b5005f4fc84e00e0afd79d4ef8a382b`）
原始命题步骤: 平方范数为(Qv)^T(Qv)=v^TQ^TQv=v^Tv，故两点距离保持。
历史说明（未独立认证）: 利用正交条件Q^TQ=I，平方根取非负。
### 必须前提
实二维线性变换 Q 必须满足 Q^TQ=I 才保持范数及点积；通过非零向量的余弦公式讨论角度时，必须另外排除零向量。这里只独立抽检范数，不冒充一般角度证明。
### 不适用反例/边界
Q=diag(2,1) 把 (1,0) 长度从 1 变成 2，不是等距变换；即便 Q 正交，零向量与任何向量的夹角仍无定义。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.geometry.euclidean-isometries#3

原始SHA-256: `60b1997fa9bccad83c890bef93361cf814fdaa5ad55e4fc08709f3795699a229`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `1f15871b0ba00fa48b104b9f16782d85da3e53c2c848bbfac2b8e3f5661ab2f6`）
原始命题步骤: 对非零向量u,v，(Qu)·(Qv)=u^TQ^TQv=u·v，且范数不变，因此夹角余弦不变。
历史说明（未独立认证）: 余弦定义为点积除以两向量模长乘积。
### 必须前提
实二维线性变换 Q 必须满足 Q^TQ=I 才保持范数及点积；通过非零向量的余弦公式讨论角度时，必须另外排除零向量。这里只独立抽检范数，不冒充一般角度证明。
### 不适用反例/边界
Q=diag(2,1) 把 (1,0) 长度从 1 变成 2，不是等距变换；即便 Q 正交，零向量与任何向量的夹角仍无定义。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.matrix.gaussian-row-equivalence#2

原始SHA-256: `5115a6a4bde020dfdfadec0baba36e3d07e8df673659775e48d8bbae6dc0c217`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `5f06506d42fe96b3e18b6a26096716aa7550559f230b90174603fd176c3f431e`）
原始命题步骤: 将一行等式乘 λ≠0 的新方程可除以 λ 恢复原式。
历史说明（未独立认证）: 双向等价使用非零数乘法的可逆性。
### 必须前提
方程系统的某一行乘以标量 λ 必须 λ≠0 才有反向除法；行交换与一行加另一行倍数也须说明逆变换，适用于同一系数域。
### 不适用反例/边界
将 x=1 的整行乘以 λ=0 变成 0=0，会增加全部实数作为解；这种变换只保留旧解，不保证解集相等。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.matrix.inverse-two-by-two#3

原始SHA-256: `c98427f511176e2fd71550b111afe600dedb7a3af3343295c0c4d8b72d333efa`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `27f8d8109c1e8e99c51b9ce4a4d1c5f07dbe94ff43fc0853730d2eedc8f87ef1`）
原始命题步骤: 若 Δ=0 且 A 非零，则行或列线性相关，存在 v≠0 使 Av=0；若 A=0 也显然成立。
历史说明（未独立认证）: 二阶行列式为零时齐次系统有非零解，可由线性方程消元检验。
### 必须前提
二维实方阵只有 det A=ad-bc≠0 时存在显式逆矩阵，双侧乘积为单位阵；若 det=0，则核非平凡，不能将伴随矩阵除以0；奇异情形需要单独证明而非计算逆。
### 不适用反例/边界
A=[[1,2],[2,4]] 行列式为 0，存在非零向量(-2,1) 被映射为零；不能写 A^{-1}=adj(A)/0。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.model.input-output-triangular#2

原始SHA-256: `95a10cff5b8347a8fb13c7fa801cf493105779e58298765c580879dc2d21a3dc`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `7aa7b54a35225c72d4a47277d33f0003cf32dbe1aec1b3dd4d332d8ba5f699d5`）
原始命题步骤: 因1-b>0，第二式唯一给出x2=d2/(1-b)≥0。
历史说明（未独立认证）: 非零分母保证可解；非负分子与正分母保证非负性。
### 必须前提
参数 b<1 使 1−b>0；需求量 d₂≥0，且方程的右端没有额外负项，才能从 x₂=d₂/(1−b) 推出唯一且非负的 x₂。
### 不适用反例/边界
取 b=1,d₂=1 时方程 0·x₂=1 无解；取 b=2,d₂=1 虽有唯一解 x₂=−1，却不满足非负经济产量。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.model.time-rescaling#4

原始SHA-256: `749eaa77e98964bb993d337fbf62e6e7d62978e98446f678147973e8c6fd301c`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `57a739b9b359ded431043bdf75968f9ee80733ba68c0c8142c572077f9dd8771`）
原始命题步骤: 二次代入：a(su)²+b(su)+c=(as²)u²+(bs)u+c。
历史说明（未独立认证）: 平方项需要s²，不能只乘s。
### 必须前提
对任意实 a,b,c,s,u，a(su)²+b(su)+c=(as²)u²+(bs)u+c 是代数恒等式；若宣称 t=su 是等价的可逆参数替换，必须另外要求 s≠0。
### 不适用反例/边界
令 s=0：代数代入仍成立，但所有 u 被映到 t=0，无法反向恢复原时间变量；仅把二次系数乘 s 而非 s² 则会算错。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.multivariable.partial-polynomial#3

原始SHA-256: `5984a38901d29abb238ff018c6e59a58fba62c2a8964952ab61f8e68f8cec3f3`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `2daf5d70be4902540628b83767e246e40c7e3e01760dd8b769eccd0cbb3a03d6`）
原始命题步骤: 按 y 偏导差商， [f(x,y+h)-f(x,y)]/h=x²+6y+3h，取 h→0 得 ∂f/∂y=x²+6y。
历史说明（未独立认证）: 固定 x，按定义展开平方。
### 必须前提
固定 x 只让 y 变化，按 h≠0 的差商展开，假设 f(x,y)=x²y+3y² 且变量为实数；取 h→0 才得到偏导 x²+6y。
### 不适用反例/边界
若让 x 同时随 h 改变，就计算方向导数而不是保持 x 不变的 y 偏导；把 h=0 代入尚未化简的差商会除零。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.sequence.fibonacci-golden-ratio#3

原始SHA-256: `e0c08cc8ea53f9777a767c2b2bedd7da0f676b4e03bcbe06c4bf376ed6d2f975`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `f96809f013dbc2482053c3747b518fe782759a2a8ca2f7207c040b3ddb7106a2`）
原始命题步骤: 由于|ψ/φ|<1，F_{n+1}/F_n = φ·[1-(ψ/φ)^{n+1}]/[1-(ψ/φ)^n]。
历史说明（未独立认证）: 提取φ^n，分母在n≥1不为0。
### 必须前提
采用 F₀=0,F₁=1，n≥1，φ=(1+√5)/2，ψ=(1−√5)/2；Binet 表达式成立且 Fₙ>0，分母 1−(ψ/φ)ⁿ 不为零，才能取比值。
### 不适用反例/边界
n=0 时 F₀=0，因此 F₁/F₀ 未定义；若仅凭 |ψ/φ|<1 而省略 Fₙ 非零检查，就存在未证的除法步骤。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.statistics.bernoulli-mle#2

原始SHA-256: `43d27ba1841d143d69eff5f4e7d6ba821764b3f2c8e623f11befd64d2f75e9dd`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `cd5129f7aba459b3f560a1b77b7aa5a56a2949eaf7b1cd9079021886b29e3e1f`）
原始命题步骤: 当 0<k<n，log L=k log p+(n-k)log(1-p)，其导数 k/p-(n-k)/(1-p)=0 给 p=k/n。
历史说明（未独立认证）: 在开区间合法取对数和求导；严格二阶导数 -k/p²-(n-k)/(1-p)²<0。
### 必须前提
n∈正整数且 0<k<n，观测为独立同分布 Bernoulli(p) 样本，p∈(0,1)；log L 的导数零点 p=k/n 且二阶导数严格负。
### 不适用反例/边界
当 k=0 时 log(p) 项前系数为0，直接写 k log p 并在 p=0 求导没有意义；若观测不是同一 Bernoulli 参数，似然的二项形式也不成立。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.elective.statistics.bernoulli-mle#3

原始SHA-256: `34248c565d5c75caccac1cf9cf61a4bd7ad828a2bf26384037f079adc9c8ba8b`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `556f9d97703ec01d6f3d7cb0708a061c53c1de2a1189ade6cf20168d47d94e83`）
原始命题步骤: 因 log L 严格凹，内点 k/n 为唯一极大值；若 k=0，则 L=(1-p)^n 在 [0,1] 最大于 p=0；若 k=n，则 L=p^n 最大于 p=1。
历史说明（未独立认证）: 端点必须单独讨论，不能把 0/0 的对数微分套用于边界。
### 必须前提
n≥1，0≤k≤n，p∈[0,1]；当 0<k<n 时内部最大值为 k/n，当 k=0 或 n 时用原始似然函数单独处理边界；对数似然不能在 p=0 或1直接套开区间求导。
### 不适用反例/边界
全零观测 k=0 的 MLE 为 p=0；若只求解 k/p−(n−k)/(1−p)=0 会遗漏边界甚至产生 0/0。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.extension.circle-polar#1

原始SHA-256: `57d10a3d5abe2a8976b5e033e276dac8059ef28e9f355ea26aa1d0b55a2c59b8`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `1e0e86489c4413ca0202e5ddc6ac67285f1ff2195faaba14503a0da9f85cbf4e`）
原始命题步骤: 圆上任意点 T=(x₀,y₀) 满足 |T|²=R²，圆在 T 的切线法向量为 T，故切线是 T·X=R²。
历史说明（未独立认证）: 圆的梯度 ∇(x²+y²−R²)=2T 非零，切线与半径正交。
### 必须前提
欧氏平面圆心原点、半径 R>0，T 在圆上满足 T·T=R²；梯度 2T≠0，故切线法向量 T 非零且切线方程 T·X=R²。
### 不适用反例/边界
当 R=0 时 T=0，所谓切线方程 0=0 代表整平面，不能视作退化圆上一点的普通切线。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.extension.circle-polar#3

原始SHA-256: `af740ecae546c1997e0c23671265bcee41c61f7032d54f33149a53b4d57b715e`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `53b74c9a4b4f3e25486b7492dffe8ea18613cbdb02eb4f0655354a12fb82f42b`）
原始命题步骤: 当 |P|>R，极线到圆心距离 R²/|P|<R，故与圆有两交点；当 0<|P|<R 则距离>R 无交点。
历史说明（未独立认证）: 极线的非零法向量是 P，使用圆与直线距离判据即可判定交点数。
### 必须前提
半径 R>0、极点 P≠0；极线 P·X=R² 的法向量为 P，圆心到直线距离是 R²/|P|；按 |P| 与 R 的大小分类，等于时相切。
### 不适用反例/边界
P=0 时等式 0=R² 无解且距离公式分母为0，不能宣称存在一条极线；若 |P|=R 应是一交点而非两交点。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.extension.cross-product#3

原始SHA-256: `3a2d6fcb70cfc880852126eeb9a07d342cb151d95bb87fa8fa1d65e8ae06b960`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `632a4753843ddc88e7ca754b692d480e8dff98219c0728651da4a3a36716d0be`）
原始命题步骤: 外积三个分量平方相加并整理得 |u|²|v|²−(u·v)²。
历史说明（未独立认证）: 这是三维拉格朗日恒等式，可直接由坐标平方和展开校验，非零时结合点积角公式得面积大小。
### 必须前提
u,v∈R³ 使用标准右手欧氏外积，分量由行列式定义；|u×v|²=|u|²|v|²−(u·v)² 对零向量也成立，但角度及夹角正弦形式另外需要两向量非零。
### 不适用反例/边界
二维一般向量不能无定义地直接使用三分量外积；令 u=0 时面积0成立，但用 |u||v| 作分母求 sin θ 会除零。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.function.composition-domain#3

原始SHA-256: `1d987f5a601370c4f6ed7af7c68669369afb8a9e0f9f12ae00798063818881b9`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `592c3174a3499bf93627153903122c3b5776d91824d4801d35534503cde04463`）
原始命题步骤: 反过来，若 x∈D_g 且 g(x)∈D_f，则内层和外层两次求值均合法，得到 f(g(x))。
历史说明（未独立认证）: 两项条件充分且必要，恰构成所称自然定义域。
### 必须前提
复合函数自然定义域是 {x∈Dg:g(x)∈Df}；两个映射均需有明确输入/输出域与对应值，外层输入必须与内层结果匹配。有限映射实例是定义域规则的见证而非任意函数的证明。
### 不适用反例/边界
g(2)=7 而 f 仅在 {2,4} 定义时，虽然 x=2 属于 Dg，f(g(2)) 依然未定义；仅检查内层定义域不够。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.line-circle#3

原始SHA-256: `aae41cbc1a755da3f2631f648502da33ec3f31ebafd6b0a901adc00dcd705c72`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `e52e99afd69afee9efbc3affe49dd7c6a91e056fff9cab09b592401beefe9f14`）
原始命题步骤: 当 d=r 时仅有 HP=0 一个交点 H；当 d>r 时右侧负数无实解，因此没有交点。
历史说明（未独立认证）: 平方非负限制排除了负的实数平方。
### 必须前提
直线非零法向量、圆半径 r>0；投影垂足 H 到圆心距离 d≥0，在直线方向的偏移平方等于 r²−d²，因此 d=r 一点、d>r 零点。
### 不适用反例/边界
若直线一般式 A=B=0，则点线距离无法定义；若 r²−d²<0 却取其实数平方根，就产生不存在的实交点。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.line-equation#2

原始SHA-256: `b7541fc18f50da3183c0898cade2420db051055287439fe9487bd34a40b4ea1b`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `ebb9c847da16b97d2676c13f757c073f216ab4442684f517aa200c85dabdb6f6`）
原始命题步骤: 把数量积展开，得到 a(x−x₀)+b(y−y₀)=0。
历史说明（未独立认证）: 垂直向量的数量积为零，且 n 非零限定一维线性解集。
### 必须前提
二维实平面中法向量 (A,B) 必须非零，P0 是给定直线上一点；n·(P-P0)=0 才是一维仿射直线，其逆向判别依赖非零法向量的正交补恰为一维。
### 不适用反例/边界
若 A=B=0，方程 0=0 代表整个平面，或 0=C≠0 代表空集，不能称为通过指定点的唯一直线。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.line-equation#3

原始SHA-256: `15f182b323195a927e9e1459327e1a37639b4e781116a77093c039b317ba2ee3`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `e182b4fdb71258d54c1ee8affb42340214574b238524d6f01563f6d533a0c93e`）
原始命题步骤: 反过来任一点满足这个方程，其位移与 n 垂直，必落在过 P₀ 且法向量为 n 的直线上。
历史说明（未独立认证）: 在二维空间中，与非零向量垂直的位移构成唯一的一维方向。
### 必须前提
二维实平面中法向量 (A,B) 必须非零，P0 是给定直线上一点；n·(P-P0)=0 才是一维仿射直线，其逆向判别依赖非零法向量的正交补恰为一维。
### 不适用反例/边界
若 A=B=0，方程 0=0 代表整个平面，或 0=C≠0 代表空集，不能称为通过指定点的唯一直线。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.line-general#1

原始SHA-256: `7fbae69e34c96bf05bfbf194a45cf7c216f70756eb0688434c3c4989263d3cd8`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `26f1f4b7c9d499654ff54b2e6766c5edf8794e116514827178348dc708e8d05a`）
原始命题步骤: 若 P 在直线上，则沿线位移向量 P−P₀=(x−x₀,y−y₀) 与法向量 n 垂直。
历史说明（未独立认证）: 法向量定义为与直线方向正交的非零向量。
### 必须前提
二维实平面中法向量 (A,B) 必须非零，P0 是给定直线上一点；n·(P-P0)=0 才是一维仿射直线，其逆向判别依赖非零法向量的正交补恰为一维。
### 不适用反例/边界
若 A=B=0，方程 0=0 代表整个平面，或 0=C≠0 代表空集，不能称为通过指定点的唯一直线。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.line-general#2

原始SHA-256: `f1fda80e41f0411fa6b94a3a99aa6225d665d7a797d8aaeee2e67a26731ff094`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `8d8ff81aa64d879e3b1d82dd17a7b7120f4d9c618b7020c0ed556c8219e009e8`）
原始命题步骤: 数量积零条件给出 n·(P−P₀)=A(x−x₀)+B(y−y₀)=0。
历史说明（未独立认证）: 使用平面数量积的坐标计算公式及非零法向量条件。
### 必须前提
二维实平面中法向量 (A,B) 必须非零，P0 是给定直线上一点；n·(P-P0)=0 才是一维仿射直线，其逆向判别依赖非零法向量的正交补恰为一维。
### 不适用反例/边界
若 A=B=0，方程 0=0 代表整个平面，或 0=C≠0 代表空集，不能称为通过指定点的唯一直线。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.line-general#3

原始SHA-256: `c8f6c9996900306967d7baa5a43cbc6831c59ecd1634009aebe84e4bb8c7ec0e`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `120cc287644ba80fa3b5cae0ba654fa7b81d8eaf276c7ac76421b8e1f834a400`）
原始命题步骤: 反过来该线性方程的解集恰是所有与 n 正交、经过 P₀ 的点，故代表一条唯一直线。
历史说明（未独立认证）: 在平面内非零法向量的正交补是一维方向空间。
### 必须前提
二维实平面中法向量 (A,B) 必须非零，P0 是给定直线上一点；n·(P-P0)=0 才是一维仿射直线，其逆向判别依赖非零法向量的正交补恰为一维。
### 不适用反例/边界
若 A=B=0，方程 0=0 代表整个平面，或 0=C≠0 代表空集，不能称为通过指定点的唯一直线。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.line-relations#1

原始SHA-256: `144b774d9f21d1e0e1b459cf875b896b7ae525e6612500f3ddb4b25887c2b80a`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `fcb369f5e81dc2ae02bded37fd3b5775150f33ac47a1af2549058e5af904bdd8`）
原始命题步骤: 每条直线的法向量为 nᵢ=(aᵢ,bᵢ)，方向向量可取 dᵢ=(-bᵢ,aᵢ)。
历史说明（未独立认证）: 一般式的非零系数提供非零法向量，旋转90°可得方向向量。
### 必须前提
每条直线须有非零法向量，二维方向向量 d=(-B,A) 因而非零；行列式零判别方向平行，点积零判别方向垂直。两条直线方向平行不意味着它们是不同的平行线，亦可重合。
### 不适用反例/边界
一般式 0x+0y+1=0 不是直线；即使两个法向量行列式为零，两直线仍可能重合，不能直接说它们无公共点。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.line-relations#2

原始SHA-256: `b2cdf7e2a1b4c82eabbab17d51aa5707fe9937ea9a48468dbb8b37d10c0b6d03`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `9995005016f2ef541bd6b76dc4417994b9d0ad1d03c674a0e4ceef33529faf3a`）
原始命题步骤: 两个方向向量线性相关当且仅当二维行列式为零，等价 a₁b₂−a₂b₁=0。
历史说明（未独立认证）: 非零二维向量平行的充要条件是对应 2×2 行列式为零。
### 必须前提
每条直线须有非零法向量，二维方向向量 d=(-B,A) 因而非零；行列式零判别方向平行，点积零判别方向垂直。两条直线方向平行不意味着它们是不同的平行线，亦可重合。
### 不适用反例/边界
一般式 0x+0y+1=0 不是直线；即使两个法向量行列式为零，两直线仍可能重合，不能直接说它们无公共点。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.line-relations#3

原始SHA-256: `2afddbcdd24eafe305337757337e04dd84324da54712dd635ceba09e45fb1e90`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `0ab874b6854f90b2987bd1b2827fd91e80a5a2f1accbecc61981342ca4b69b45`）
原始命题步骤: 方向向量互相垂直当且仅当 d₁·d₂=b₁b₂+a₁a₂=0。
历史说明（未独立认证）: 非零向量垂直当且仅当数量积为零，旋转不会改变夹角。
### 必须前提
每条直线须有非零法向量，二维方向向量 d=(-B,A) 因而非零；行列式零判别方向平行，点积零判别方向垂直。两条直线方向平行不意味着它们是不同的平行线，亦可重合。
### 不适用反例/边界
一般式 0x+0y+1=0 不是直线；即使两个法向量行列式为零，两直线仍可能重合，不能直接说它们无公共点。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.point-line-distance#3

原始SHA-256: `89491fe984cd7b7d919220eb301cd39f283718373587ef150f3771d1cfdc6e86`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `bbe4b6daa35b0726c875eb58373736f4b3990510565dd1c21419e707819cc603`）
原始命题步骤: 所求最短距离等于垂直投影长度的绝对值，因此代入上一步得到给定公式。
历史说明（未独立认证）: 向量分解为沿直线和垂直直线的正交分量，垂直长度最短。
### 必须前提
点 Q=(x,y) 和直线 Ax+By+C=0 都在欧氏平面，(A,B) 不可同时为零；距离是有定义的法向投影的绝对长度，不带符号。
### 不适用反例/边界
A=B=0 令距离分母 sqrt(A²+B²)=0；此时 0x+0y+C=0 根本不是一条普通直线，不能计算点线距。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.space-dot#1

原始SHA-256: `d7a70ddbcc1411a682bc30238a90b6ec54b55d5a2b71ecf40494d30e88a7f420`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `d75efccfeadcc33899b2fd8a171456b1a0653c01476fac36b03bc2917716eaf6`）
原始命题步骤: 由三维正交坐标中的勾股定理展开 |a−b|²=Σ_i(a_i−b_i)²=|a|²+|b|²−2Σ_i a_ib_i。
历史说明（未独立认证）: 逐坐标平方求和等价于沿三条相互垂直的基向量计算位移长度。
### 必须前提
u、v 必须属于同一有限维实欧氏内积空间；平方范数展开只用正交坐标及双线性，不要求 u、v 非零或互相垂直。勾股等价命题由交叉项等于零推出。
### 不适用反例/边界
把不同维向量直接相加没有定义；把平方和恒等式说成仅在两非零向量夹角为90°时有定义也不正确，零向量情形应保留。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.space-dot#2

原始SHA-256: `6cf4215be9fd74bf7c7780e7384d5a08868c3668f1c56658f94c14d9398ddd4f`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `2043f30adaf7e8d9b4ac49013ce6741190be0fca313a2299d8ec8ab437f83114`）
原始命题步骤: 以向量 a、b 为边构成平面三角形，余弦定理同样给出 |a−b|²=|a|²+|b|²−2|a||b|cosθ。
历史说明（未独立认证）: 两个非零向量张成一个至多二维平面，平面余弦定理适用。
### 必须前提
u、v 是同一实欧氏内积空间中的非零向量，才能在 cosθ=(u·v)/(|u||v|) 中作除法；若其中一方为零，数量积仍有定义，但夹角不能由该式定义。
### 不适用反例/边界
取 u=(0,0)、v=(1,0)，u·v=0，却不能据此断言两向量夹角为 90°；零向量没有方向。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.geometry.space-dot#3

原始SHA-256: `4ebbf9d0ae09722bdecd5688243898537b0a8082631a365b364c31ad2d267d4c`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `6d412ee84d38058a8e6c1cd9f7a0142b37ff9d2c6dd7cc2deef2d641b7c0d6ad`）
原始命题步骤: 比较两种 |a−b|² 展开并除以 2，即 Σ_i a_ib_i=|a||b|cosθ；因 |a||b|>0，数量积为零等价 cosθ=0。
历史说明（未独立认证）: 除以非零模长合法；在 0≤θ≤π 内 cosθ=0 等价 θ=π/2。
### 必须前提
u、v 是同一实欧氏内积空间中的非零向量，才能在 cosθ=(u·v)/(|u||v|) 中作除法；若其中一方为零，数量积仍有定义，但夹角不能由该式定义。
### 不适用反例/边界
取 u=(0,0)、v=(1,0)，u·v=0，却不能据此断言两向量夹角为 90°；零向量没有方向。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.probability.multiplication#2

原始SHA-256: `1d683653c5ab1c5b877a135235863474e6bb22b8b61362f5f981d35e3b86db46`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `392521b585b009420197f3dbd365bb98da5778bdf3d68771c6bab6e69c8a1ee9`）
原始命题步骤: 将等式两侧同乘正数 P(A)，得到 P(A∩B)=P(A)P(B|A)。
历史说明（未独立认证）: 前置条件 P(A)>0 已满足，合法地消去分母。
### 必须前提
有限概率空间需权重非负且总和1；P(B|A)=P(A∩B)/P(A) 的条件是 P(A)>0，不能用独立性代替该条件；乘法公式从此定义同乘正数得到。
### 不适用反例/边界
取样本权重 P(0)=1、P(1)=0、A={1}，则 P(A)=0；即使集合 A 非空，也不能定义 P(B|A) 为实数比值。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.space.parallel-perpendicular-criteria#3

原始SHA-256: `2850c8e5642bb20d395fa42e4dff820e056729d17597109ceabc56c9f826a29a`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `59e5840f5bb5c9dd8777fa22d9e54930bc626b3243ce6e5571cb5fb6c09073cc`）
原始命题步骤: 若两个平面的非零法向量正交，则其夹角为直角，两个平面的二面角也为直角，故两平面垂直。
历史说明（未独立认证）: 平面间角由法向量夹角的锐角代表确定，点积为0等价法向量夹角90°。
### 必须前提
两平面在欧氏三维空间均有非零法向量 n₁,n₂，平面夹角定义为两法向夹角的锐角或补角；当 n₁·n₂=0 时两平面夹角为90°。
### 不适用反例/边界
写入零法向量会使二面角定义失效；法向平行只意味着平面平行或重合，不能判成垂直。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.space.perpendicular-plane#1

原始SHA-256: `f9d49638115d85be2403d7900420e51abfe2501a54485de4f58c7cad314674df`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `cbbed09a132ae79b92d735591ac85c1ad1abe2f99af649b03b6148f91ea470d4`）
原始命题步骤: 令 u 为 l 的非零方向向量，v₁、v₂ 为平面内相交两线的非零方向向量。
历史说明（未独立认证）: 相交且不同方向保证 v₁、v₂ 线性无关。
### 必须前提
u 为非零直线方向向量；平面内两条确实相交且方向不平行的直线，其非零方向 v,w 张成整个平面；只有 u 同时垂直 v,w 才能推出 u 垂直平面。
### 不适用反例/边界
若两条给定直线其实平行，例如 v=(1,0,0)、w=(2,0,0)，u=(0,1,0) 虽垂直两者，却仍在 xy 平面内，不垂直该平面。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.space.perpendicular-plane#2

原始SHA-256: `28b35866e0af519cb84498e9167d65a2df5764d479f7bf7d99dee94dd672d6e4`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `aea737a41c80d12c4520f03baa4df527f18421a4aba2f697911774374e0ef745`）
原始命题步骤: 根据前提有 u·v₁=0 和 u·v₂=0，任意平面内方向 w 可写为 αv₁+βv₂。
历史说明（未独立认证）: 两条不平行的平面方向向量张成整个二维平面方向子空间。
### 必须前提
u 为非零直线方向向量；平面内两条确实相交且方向不平行的直线，其非零方向 v,w 张成整个平面；只有 u 同时垂直 v,w 才能推出 u 垂直平面。
### 不适用反例/边界
若两条给定直线其实平行，例如 v=(1,0,0)、w=(2,0,0)，u=(0,1,0) 虽垂直两者，却仍在 xy 平面内，不垂直该平面。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.space.perpendicular-plane#3

原始SHA-256: `f2bf19336c31643c3f40c9c674c76edb3636e45781c5d79d9d037727d788aaac`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `b8f0a23150a18ca8f6da9dda78c98530c8e69d1c3e929da5379d86892e269a1b`）
原始命题步骤: 由数量积分配律 u·w=α(u·v₁)+β(u·v₂)=0，故 u 与平面内任意方向垂直。
历史说明（未独立认证）: u 是平面的法向方向，所以其所属直线与平面垂直。
### 必须前提
u 为非零直线方向向量；平面内两条确实相交且方向不平行的直线，其非零方向 v,w 张成整个平面；只有 u 同时垂直 v,w 才能推出 u 垂直平面。
### 不适用反例/边界
若两条给定直线其实平行，例如 v=(1,0,0)、w=(2,0,0)，u=(0,1,0) 虽垂直两者，却仍在 xy 平面内，不垂直该平面。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.space.point-line-distance#3

原始SHA-256: `92e8951aed98a2705bb895480699fb039ea2462443de179dc27660c2ba930501`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `7cfe56a1270777eebd69715cdff56249a257feae6007967181648e061e65a095`）
原始命题步骤: 对任意 t，P−(Q+t u)=w⊥+(w∥−t u)，两分量正交，距离平方至少为 |w⊥|²。
历史说明（未独立认证）: 选择 t=(w·u)/|u|² 使沿线分量消失；展开平方得所述 d² 公式。
### 必须前提
过 Q 的直线方向 u∈R³ 必须非零，P 与 Q 在同一欧氏空间；分解 w=P−Q 为沿 u 的投影和正交残差，选 t=(w·u)/|u|²，距离平方为 |w|²−(w·u)²/|u|²≥0。
### 不适用反例/边界
u=0 时投影系数除零；若沿线参数没有覆盖全部实数，所求将是射线/线段距离而不一定等于整条直线的距离。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.space.solid-volumes#1

原始SHA-256: `fc3139e78c40dfd01e4ab475880037d6f9d8c9747293576703849c2ade649c08`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `9a0c38305f7d0a4c92bb396b3ccf17e0400c02740396c72621b1f9fe41d1a82f`）
原始命题步骤: 对于柱体，每个与底面平行的截面面积是常量 B，因此高度范围内的体积累加为 ∫₀ʰ B dt=Bh。
历史说明（未独立认证）: 体积可通过层状切片或卡瓦列里原理计算，截面恒等是关键前提。
### 必须前提
柱体以底面为参考，B 为固定有限非负横截面积，高度 h≥0；平行底面的切片面积恒 B，才可按体积切片公式得到 Bh。
### 不适用反例/边界
圆锥或锥台的平行截面面积会变化，不能直接用 B·h 作为一般立体的体积；B 不能理解成侧面积。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.space.solid-volumes#2

原始SHA-256: `d747891bdbd96eed3b287f0919a46fdc1cd65921dd54a69a2a64a5772051b4fd`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `11e00f6360d57101ce36908f2c9a2b1708a78703ae076094f907df0f5d9402d5`）
原始命题步骤: 对于以顶点为起点的锥体，相似截面线性比例 t/h，因此面积比例为 (t/h)²。
历史说明（未独立认证）: 相似平面图形的面积按对应长度的平方缩放。
### 必须前提
锥体高度 h>0，按距顶点垂直高度 t∈[0,h] 取与底面平行截面，相似比为 t/h；截面面积缩放为平方比例 B(t/h)²。
### 不适用反例/边界
若截平面不与底面平行，相似比例不能直接设 t/h；若 h=0，比例分母为零且不构成非退化的锥体。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.space.solid-volumes#3

原始SHA-256: `9d398feb47b9900c75ae16b56602b57b8dc4c8485fa67634e287eb8faa81f7f9`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `c8d5e2c640ef35fc998fb353841c9e2e3b3f7dca539384d033a153c6c436a513`）
原始命题步骤: 切片积分得到 V=∫₀ʰ B(t/h)² dt=(B/h²)[t³/3]₀ʰ=Bh/3。
历史说明（未独立认证）: 积分 t² 的原函数为 t³/3，高度 h>0 使分母合法。
### 必须前提
锥体底面积 B≥0 且高 h>0，切片面积为 B(t/h)²；积分基本公式 ∫₀ʰt²dt=h³/3 成立，才能得到 V=Bh/3。
### 不适用反例/边界
h=0 时从一开始使用 B/h² 不合法，尽管极限体积可能是0；若面积随高度不是二次比例，结论不适用于任意形体。
独立精确有限案例: 有（但不是量词证明）
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.triangle.sine-law#3

原始SHA-256: `7b124a60d5e58c7d4d99cb919dbe88e4a0d49a32d7a5ff9cb169528d15a043bc`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `a706d35c2ab8abe64dfe1065027f68eaf6180779ae73eeef79f6f2d127909e70`）
原始命题步骤: 由于 a,b,c 均非零，等式两边同除以 abc/2，得到 sin A/a=sin B/b=sin C/c。
历史说明（未独立认证）: 除以正数合法，倒数得到 a/sin A=b/sin B=c/sin C。
### 必须前提
非退化欧氏三角形，a,b,c>0 且角 A,B,C∈(0,π)，故 sin A,sin B,sin C>0；所用双向除法均合法。
### 不适用反例/边界
若三点共线，出现 sin A=0，虽可能形式上写出含0等式，但 a/sin A 无定义，不能说正弦定理的分式照样成立。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.trig.double-angle-reduction#3

原始SHA-256: `90e73b04d50c7222425f4246f42ada05e787b8950770b0d604737ea4d39809c5`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `763878f1e1fa6a91f11367ba50f9cde215112988b9931dd333c9002ca7f900eb`）
原始命题步骤: 再使用 sin²x+cos²x=1，可得 cos2x=1−2sin²x=2cos²x−1，并移项得到降幂公式。
历史说明（未独立认证）: 基本平方关系为恒等式，除数仅为常数 2，故每步全域合法。
### 必须前提
正弦余弦来自同一实角，其坐标必须满足 cos²x+sin²x=1；cos2x、sin2x 与降幂公式不需分母变量，分母2 非零。有限有理单位圆点只检验一个代数实例。
### 不适用反例/边界
把 c=s=1 冒充某角的余弦与正弦就违反 c²+s²=1，不能从任意两个数构造真实同角的二倍角公式。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.vector.linear-operations#1

原始SHA-256: `fa2f16a81a81780583fe3300a83ee8a6f6e5272305f0162ae52533ba31f63ed1`
历史编辑档案: docs/evaluation/KB_BATCH30_P0_COMPLETION_AUDIT.json（record SHA-256 `5e9a19113f2e1a2a8f83f45beeb05347bde496bac656696e42b6f09578450a65`）
原始命题步骤: 将 u 和 v 看作两个连续位移，最终横、纵坐标增量分别是 u₁+v₁ 和 u₂+v₂。
历史说明（未独立认证）: 平面坐标逐轴叠加位移就是首尾相接向量加法。
### 必须前提
u,v 作为同一欧氏平面的有向位移，使用一致的坐标轴/单位/方向；首尾相接后的位移分量分别相加，这与位移起点无关。
### 不适用反例/边界
若把一个向量的坐标按旋转了90°的局部坐标轴给出，另一个按全局坐标轴给出，未经坐标转换直接相加会算错实际位移。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

## math.hs.vector.projection#2

原始SHA-256: `cbc9cca4f8cceb36718566cc2b7c35029784348ed36dfd6bb1cc8e654e74c876`
历史编辑档案: docs/evaluation/KB_BATCH29_P0_CONDITION_REVIEW.json（record SHA-256 `d321b009c4c660ad9961cfefa3fd31a00f57170daa5a81988b428a1cd44865a1`）
原始命题步骤: 展开得到 a·b−t(b·b)=0；由于 b≠0，b·b=|b|²>0。
历史说明（未独立认证）: 数量积双线性与正定性保证分母非零，可以合法求 t=(a·b)/(b·b)。
### 必须前提
a 与 b 在同一实内积空间，b 必须非零以保证 b·b>0；投影系数 t=(a·b)/(b·b) 是法向残差为零的唯一解。a 可以是零向量。
### 不适用反例/边界
当 b=0 时 b·b=0，投影方向没有唯一的一维子空间，公式的分母为零；不能据 a·b=0 说这个商已定义。
独立精确有限案例: 本批无
数学证明/教师状态: NOT_FORMALLY_VERIFIED / REVIEW_PENDING；学生不可发布。

