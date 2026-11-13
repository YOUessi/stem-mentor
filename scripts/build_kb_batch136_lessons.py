#!/usr/bin/env python3
"""Original teacher-only deep manuscripts for twelve still-missing bounded atoms.
All source associations are provisional; no teacher approval or formal proof is claimed.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as atoms
import build_kb_batch135_lessons as prior

OUT=ROOT/"knowledge/editorial_review/kb_batch136_twelve_deep_lessons.json"
MD=ROOT/"docs/evaluation/KB_BATCH136_TWELVE_DEEP_LESSONS.md"
SAFE=ROOT/"knowledge/editorial_review/kb_batch136_student_safe_index.json"
L={}

def add(slug, formal, domain, assumptions, steps, legal, failure, wrong, repair, examples, hints, near, far):
    if slug in L:raise ValueError("duplicate authored slug")
    L[slug]=locals().copy()
    del L[slug]["slug"]

add("c_set_membership",
"元素与集合的属于关系写为a∈A；a∉A表示a不是A的元素。属于是对象与集合之间的关系，不等同于集合之间的包含关系。",
"在讨论域U中a为对象，A⊆U为集合；单元素集合{a}是一个集合，不等于它的元素a。",
"先辨明命题两侧的类型：∈左侧应为被判定的元素，右侧应为集合；集合可以作为另一集合的元素，但要明确层次。",
["定义集合A={1,3}，其元素恰为数字1和3。","据元素判定可得1∈A且2∉A，判断只依赖元素是否列入集合。","数字1与集合{1}不是同一数学对象，尽管二者联系紧密。","若要判断{1}⊆A需比较两个集合的元素，不能将它替换为1∈A。"],
"集合成员资格由集合外延定义，可逐个检查；集合包含需要另一种量词定义。",
"对于A={1,3}，1∈A为真，但{1}∈A为假；不应把元素1和单元素集合{1}混同。",
"把1∈{1,3}误写成1⊆{1,3}，或把{1}⊆{1,3}误认作{1}∈{1,3}。",
"先检查左右对象的类型，再判断元素是否属于或一个集合是否完全包含在另一个集合中。",
[("若A={2,4}，判断2∈A及{2}∈A。","真、假。",["A只含数字2和4。","数字2属于A。","单元素集合{2}不是A的一个元素。"]),
("若B={{1},2}，判断{1}∈B及1∈B。","真、假。",["B有两个元素：集合{1}与数字2。","{1}恰是B的元素。","数字1不是B直接列出的元素。"])],
["先写出集合内部直接包含哪些对象。","注意数字1与集合{1}的类型区别。","只有对象真的在右侧集合中才使用∈。"],
"比较2∈{{2}}与{2}∈{{2}}并说明差异。",
"在程序中区分数字、数组与集合对象时，如何避免类型混淆？")

add("c_set_subset",
"A⊆B当且仅当对所有x都有x∈A⇒x∈B；A=B当且仅当A⊆B且B⊆A。空集是任意集合的子集。",
"A、B为相同讨论范围内的集合；⊆允许相等；真子集A⊊B须A⊆B且A≠B。",
"包含关系是全称条件；证A⊆B需逐一覆盖A中所有元素；反驳只需找到一个x∈A且x∉B。",
["展开A⊆B的定义：每一个A中的元素必须属于B。","若A=∅，不存在违反蕴含式的元素，故∅⊆B。","若A⊆B且B⊆A，任一x属于A恰等价于属于B。","由集合外延公理，两个集合元素相同因而相等。"],
"用全称量词和集合外延准则证明，空集情况由全称命题空真处理。",
"A={1,4},B={1,2,3}时，元素4是反例，因此A⊄B；仅看到1属于B不足以证子集。",
"把A⊆B理解为只要两个集合有公共元素，或者把等于自身误认为不是子集。",
"找集合A的所有元素，核查是否都在B中；判断真子集再额外核查不相等。",
[("A={1,2},B={1,2,3}，A是B的什么子集？","真子集。",["1和2都属于B。","所以A⊆B。","3∈B但不在A，故A≠B。"]),
("判断∅⊆{5}与{5}⊆∅。","前者真，后者假。",["空集中没有违反包含的元素。","故∅⊆{5}。","5∈{5}但5∉∅，否定第二个包含。"])],
["子集不是成员资格，先写全称蕴含。","寻找B缺少的某个A元素作为反例。","判断真子集要比子集多检查不相等。"],
"比较A={a}和B={a}时⊆与⊊的真假。",
"用数据库筛选的“所有选课学生都注册学校”关系表达子集判断。")

add("c_sufficiency",
"命题p是q的充分条件，当且仅当p⇒q恒为真；p是q的必要条件，当且仅当q⇒p恒为真。必要与充分的方向相反。",
"p、q是在固定论域中取真值的命题或谓词；讨论谓词蕴含时，应对论域中所有对象成立。",
"判断蕴含必须明确前提和结论，不得将某个特例的相关性当作全称蕴含。",
["将“p是q的充分条件”写成p⇒q。","将“p是q的必要条件”写成q⇒p，这是充要条件方向上的逆转。","以整数n为例，n为4的倍数必为偶数，因此前者是后者的充分条件。","偶数不必为4的倍数，例如n=2，因此“偶数”不是“4的倍数”的充分条件。"],
"蕴含的方向由逻辑定义确定；普遍结论要证明，逆向否定只需一个反例。",
"对整数n，n是偶数不能推出n是4的倍数；n=2提供逆命题失效见证。",
"把充分条件与必要条件的箭头方向同时写成p⇒q。",
"用“满足p一定满足q”检验充分；用“不满足p则不能满足q”检验p是否为必要。",
[("在整数中，n为6的倍数是n为3的倍数的什么条件？","充分但非必要条件。",["6k=3(2k)，所以充分。","n=3满足后者不满足前者。","因此并非必要。"]),
("在实数中，x>2是x>0的什么条件？","充分但非必要条件。",["x>2必有x>0。","例如x=1满足x>0但不满足x>2。","所以只充分不必要。"])],
["用箭头把两个条件连接起来。","先检查条件成立时结论必然成立吗？","必要性要反过来检查，并尝试找反例。"],
"判断x=0对x²=0是必要还是充分条件。",
"在安全系统中“拥有权限”是执行受限操作的必要条件还是充分条件？需考虑其他约束。")

add("c_equivalence",
"对同一论域的命题p与q，p⇔q当且仅当p⇒q且q⇒p均成立；方程解集等价要求正反两个方向都不丢失或增加解。",
"量词和论域固定，p与q可以含实变量；等价与等式外形相似不同。",
"做等价变换时每步都必须可逆，平方、除以变量等操作通常需要额外前提。",
["先证明从p出发必能推出q，此为充分性。","再从q出发推出p，此为必要性。","两向都成立时才可写⇔，仅有一向只能使用⇒。","例如x=2⇒x²=4成立，但反向失败，因为x=−2也满足x²=4。"],
"逻辑等价由两条蕴含组成；代数等价必须保留论域与每一步的可逆条件。",
"实数范围中x²=4不能等价写为x=2，丢失x=−2的解。",
"把等号两端平方后自动使用⇔，或从ab=ac不检查a≠0就消去a。",
"逐步标记⇒或⇔，并把可能引入增根/失根的步骤用代入原式核查。",
[("实数x满足x²=9是否等价于x=3？","否，x=−3也是解。",["x=3能推出x²=9。","x²=9分解为(x−3)(x+3)=0。","得到x=±3，故非等价。"]),
("实数x满足2x=6是否等价于x=3？","是。",["从2x=6除以非零常数2得x=3。","反向乘以2得到2x=6。","两向均成立。"])],
["分别写出命题p⇒q与q⇒p。","检查变形能否无条件逆转。","遇到平方或约分，特别检查潜在反例。"],
"判断√(x²)=x与x≥0的等价关系。",
"在程序优化前后验证逻辑谓词的真值表是否一致。")

add("c_quantifier",
"全称命题∀x∈D,P(x)意为D内每个x满足P；存在命题∃x∈D,P(x)意为至少有一个x满足P。二者量词与域必须明确。",
"D为给定集合，P是定义在D上的谓词；“至少一个”不代表“唯一一个”。",
"证明∀必须覆盖整个域，证明∃只需构造有效见证；反驳∀需反例，反驳∃须证无见证。",
["确定D、谓词P(x)，不要省略量词的变量范围。","例如∀x∈R,x²≥0由实数平方非负成立。","命题∃x∈R,x²=4由见证x=2成立，也可取x=−2。","对∀x∈R,x>0，只需给出x=0这个反例即可否定。"],
"全称和存在是逻辑定义；一个具体见证足以证存在，但不足以证明全称。",
"∃整数n使n²=2为假；用某个实数解不能替代整数域的有效见证。",
"看到数个成功样本就声称∀成立，或把“存在”错误理解成“只有一个”。",
"写明论域；全称用推导、存在用见证，并用反例与穷尽论证区分各自否定。",
[("∀x∈R,x²+1>0是真是假？","真。",["任何实数x满足x²≥0。","因此x²+1≥1>0。","对整个实数域成立。"]),
("∃整数n使2n=3是真是假？","假。",["若2n=3则n=3/2。","3/2不是整数。","所以整数域内没有见证。"])],
["先标出变量x的论域D。","想证明存在就寻找一个满足条件的对象。","要反驳全称只需构造一个确实属于D的反例。"],
"判断∀n∈N,n²≥n是否成立，注明N是否包含0。",
"测试属性时为什么有限随机样本不能证明全称正确？")

add("c_function_mapping",
"函数f:D→Y要求对每一个x∈D恰有一个f(x)∈Y；不同自变量可以有相同函数值，不要求一一对应。值域为{f(x):x∈D}，可能是真子集Y。",
"D非空讨论为常见高中函数场景，Y为陪域，x为自变量；定义域D、对应法则、陪域需明确。",
"每个定义域元素必须有像且只能有一个像；同一个输入对应两个不同输出就不构成函数。",
["设D={1,2,3}，规则f(x)=x²，则f(1)=1,f(2)=4,f(3)=9。","同一规则对每一个D元素给出唯一输出，满足函数定义。","若D={−1,1}，x²两个输入都映成1，这仍是合法函数。","若声称同一个x=1同时映成1与2，则违反唯一性，不能称该对应为函数。"],
"函数存在唯一性是定义条件，不要求单射或满射；输出必须属于指定陪域。",
"关系y²=x在x=4时存在y=2与y=−2，若不加选支规则不能作为实数域的单值函数y(x)。",
"将“两个输入有相同输出”误判为不是函数，或把一个输入的两个输出混成函数。",
"列表检查每个x是否有且只有一个像，随后区分陪域与实际值域。",
[("f:{−1,1}→{0,1}由f(x)=x²给出，是否为函数？","是。",["两个输入均有定义。","f(−1)=f(1)=1，输出属于陪域。","允许不同输入共用输出。"]),
("在D={1}上规定1↦2和1↦3，是否为函数？","否。",["同一输入1出现两个不同像。","违反函数定义的唯一性。","必须修正规则。"])],
["逐个检查定义域里的每个x。","检查是否恰好只有一个对应y。","不同x对应相同y并不违反定义。"],
"给出D={0,1,2}上一个函数并求它的值域。",
"机器学习模型的输入批次中，一个输入获得两个冲突预测时怎样界定随机模型与确定函数？")

add("c_piecewise",
"分段函数按互不冲突的自变量区域选取相应表达式；求f(x)必须先判断x落在哪个区域。分界处连续性须分别考察左右极限与函数值。",
"函数定义域是各分段条件的并集；每一点的适用分支应唯一，除非重叠处数值一致且规则明确。",
"分段区间覆盖定义域，不得漏掉端点或在重叠端点给出两个不同函数值。",
["设f(x)=x+1(x<0)，x²(x≥0)，两个区域互不相交且覆盖R。","求f(−2)选x<0支得到−1；求f(2)选x≥0支得到4。","在x=0有f(0)=0，但左极限为1，右极限为0。","左右极限不同，故在x=0不连续；函数仍然是良定义的分段函数。"],
"条件分支的判定先于代入，连续性需要左右极限存在相等且与函数值相等。",
"若给x≤0时f(x)=1，x≥0时f(x)=2，则x=0有冲突取值，不是单值函数。",
"无视x的符号一律套第一个表达式，或认为分段函数必连续。",
"先画分段域并标注端点归属，再代入；连续性独立检查左右极限。",
[("f(x)=x+1(x<0),x²(x≥0)，求f(−2),f(2),f(0)。","−1、4、0。",["−2<0故得−1。","2≥0故得4。","0归第二支，f(0)=0。"]),
("g(x)=2x(x<1),3(x≥1)，判断x=1连续性。","不连续。",["左极限lim_{x→1−}2x=2。","右极限为3，g(1)=3。","左右极限不等，因此不连续。"])],
["先在数轴上写出每个表达式适用区间。","处理分界点要看是否取到等号。","检查连续要比较左右极限和实际函数值。"],
"把|x−2|写成分段式，求2处函数值与左右极限。",
"累进计费模型分段计算要如何避免阈值边界重复计费？")

add("c_monotonicity",
"函数f在区间I上严格递增指∀x1,x2∈I且x1<x2时f(x1)<f(x2)；非递减将末尾的<改成≤。严格递减则反向不等。",
"I须包含在f定义域内；比较的是同一区间上任意一对自变量而不是单个样本差值。",
"严格递增与非递减不同；如果用导数判定，需满足区间连续及内点可导等相应定理前提。",
["固定区间I和任意x1<x2，严格递增定义要求f(x1)<f(x2)。","f(x)=2x+1有f(x2)−f(x1)=2(x2−x1)>0，故在R上严格递增。","f(x)=x²在[0,∞)上，差值(x2−x1)(x1+x2)>0（当0≤x1<x2），所以严格递增。","在全R上不成立：−2<−1但f(−2)=4>1=f(−1)。"],
"使用定义比较任意两点，证明中分母与乘法的符号必须合法；不能由局部图像直接推广全域。",
"f(x)=x²在R上不是单调递增；在x<0区间，x增加时函数反而减小。",
"抽两个增长样例就声称所有x都递增，或混淆严格递增与含平坦区间的非递减。",
"优先用任意x1<x2的差值符号论证，再严格注明所选区间。",
[("f(x)=3x−4在实数上是否严格递增？","是。",["任取x1<x2。","f(x2)−f(x1)=3(x2−x1)>0。","满足严格递增定义。"]),
("f(x)=x²在[−2,0]上是否严格递减？","是。",["取−2≤x1<x2≤0。","x1²−x2²=(x1−x2)(x1+x2)>0（端点均合法）。","故f(x1)>f(x2)。"])],
["先明确讨论的是哪个区间I。","任取x1<x2并比较f(x2)−f(x1)。","差值的正负可能随区间改变。"],
"验证x³在R上严格递增，注意导数在0为零并不否定严格递增。",
"以成本曲线为例区分整体单调与局部单调，并解释采样不能证明全域规律。")

add("c_exponential_exp",
"对实数a>0且a≠1，指数函数f(x)=a^x定义在R上，值域(0,∞)；a>1时严格递增，0<a<1时严格递减。",
"a是正实底数且不为1；x∈R；a^x>0。指数律a^{x+y}=a^x a^y在同一合法底数下成立。",
"实数指数幂需要正底数；禁止对负底数任意实指数套用这些定理。",
["对a>0且a≠1，实指数通过正底数的连续延拓定义且始终为正。","任意x2>x1时a^{x2}/a^{x1}=a^{x2−x1}。","若a>1则a^{x2−x1}>1，因此a^{x2}>a^{x1}。","若0<a<1则a^{x2−x1}<1，因此a^{x2}<a^{x1}；且a^0=1。"],
"指数律及正底数有序性支撑单调性；证明从有理指数延拓到实数指数需连续性构造。",
"底数a=1时函数恒为1，无严格单调性；底数a=−2时对x=1/2不具备实值。",
"把0<a<1的指数函数错判为递增，或把底数为负也写成对所有实数有定义。",
"先确认底数范围，使用指数律比较正比值而不是只画少数点。",
[("求f(x)=2^x在x=−1,0,2处的值。","1/2、1、4。",["2^{−1}=1/2。","2^0=1。","2²=4，且随x递增。"]),
("求f(x)=(1/2)^x在x=0,1,2处的值。","1、1/2、1/4。",["(1/2)^0=1。","(1/2)^1=1/2。","(1/2)²=1/4，随x递减。"])],
["先核对底数是否正且不等于1。","观察指数增加时正比值a^{Δx}大于还是小于1。","求值时注意负指数意味着倒数。"],
"比较3^x与3^{x+1}的大小并证明。",
"解释指数式复利模型在负增长率时应怎样重新定义合法底数。")

add("c_logarithm_law",
"当a>0,a≠1且M,N>0时，log_a(MN)=log_a M+log_a N，log_a(M/N)=log_a M−log_a N；对t∈R有log_a(M^t)=t log_a M。",
"对数真数M、N必须严格为正，底数a必须大于0且不为1；对数值本身可为负。",
"使用对数乘除法则前必须逐项检查真数为正，不能只检查乘积为正。",
["设u=log_a M,v=log_a N，则M=a^u,N=a^v。","由正底数指数律MN=a^{u+v}，取对数得到log_a(MN)=u+v。","又M/N=a^{u−v}且N>0，因此log_a(M/N)=u−v。","当M>0时M^t=a^{ut}，得到幂法则；所有步骤需保证定义域合法。"],
"对数与正指数互逆；指数律、对数唯一性及M,N>0保证推导可逆。",
"log_2(−2)+log_2(−2)在实数域不存在，虽(−2)(−2)=4>0，却不能直接写成log_2 4。",
"忽略真数正性，用log(xy)=log x+log y套入两个负数。",
"先写a>0,a≠1,M>0,N>0，再用指数定义证明乘除法则。",
[("计算log_2 8+log_2 4。","5。",["8=2³所以log_2 8=3。","4=2²所以log_2 4=2。","和为5，也等于log_2 32。"]),
("计算log_3 27−log_3 9。","1。",["27=3³，9=3²，真数均正。","分别得3与2。","差为1=log_3 3。"])],
["先检查底数与每一个真数合法。","把每一个对数换成指数方程。","乘法对应指数相加，除法对应指数相减。"],
"化简log_5(25x)−log_5 x，明确x的范围。",
"在连续增长模型取对数线性化数据时，为什么零值与负值需要特殊处理？")

add("c_radian",
"弧度定义：圆心角θ（弧度）的绝对值等于对应弧长s除以半径r（r>0）；整圆2π弧度即360°，扇形弧长s=r|θ|。",
"r>0，s≥0，θ以弧度计；有向角可正可负但几何弧长非负。",
"角度和弧度是两种单位，同一公式中必须统一；以度为单位不能直接将数值代入s=rθ。",
["半径为r的整圆周长2πr，对应整圆弧度定义为2π。","将圆周弧长按比例缩放，中心角对应弧长s=r|θ|。","因此π弧度=180°，1°=π/180弧度。","若θ为负表示方向，几何弧长仍取r|θ|，而不是负长度。"],
"圆弧与圆心角的比例定义在正半径圆上合法；采用一致单位才可代入弧长公式。",
"半径r=0时s/r没有定义；90°直接代入s=r×90将与实际四分之一周长不符。",
"把90°当作90弧度使用弧长公式，或负有向角产生负的几何弧长。",
"先把角度转换为弧度，再乘正半径并对有向角取绝对值。",
[("半径2，中心角90°，求短弧长。","π。",["90°=π/2弧度。","r=2>0。","s=2×π/2=π。"]),
("半径3，对应有向角−π/3，求几何弧长。","π。",["有向角为负不影响弧长非负。","|θ|=π/3。","s=3×π/3=π。"])],
["先确认角的数值单位是度还是弧度。","把角度乘以π/180转换为弧度。","半径乘弧度绝对值给出几何弧长。"],
"求半径5、圆心角72°的扇形弧长。",
"机器人航向角用角度或弧度存储时如何防止控制器单位错误？")

add("sc_derivative_def",
"函数f在x0处可导指极限f'(x0)=lim_{h→0}[f(x0+h)−f(x0)]/h存在且有限；可导必连续，但连续不一定可导。",
"x0是定义域内的内点，h≠0且x0+h在定义域；在孤立点或端点需另约定单侧导数。",
"计算差商时不能令h=0；需要从双侧趋近0，左右导数相等才能有普通导数。",
["以f(x)=x²为例，差商=((x0+h)²−x0²)/h=2x0+h，其中约去h前须h≠0。","当h→0时差商趋于2x0，因此f'(x0)=2x0。","若导数存在，f(x0+h)−f(x0)=h[(f(x0+h)−f(x0))/h]→0，所以f连续。","对于g(x)=|x|在0处，右差商为1，左差商为−1，故尽管连续却不可导。"],
"通过极限定义直接证明，不在h=0执行除法；可导推出连续是乘积极限。",
"|x|在0处连续但左、右导数不同，不存在普通导数。",
"把差商在h=0代入，或者只求右导数就宣布双侧导数存在。",
"固定非零h计算差商并化简，再分别检查双侧趋近0的极限。",
[("按定义求f(x)=x²在x0=3处的导数。","6。",["差商=((3+h)²−9)/h=6+h (h≠0)。","当h→0时趋于6。","因此f'(3)=6。"]),
("求g(x)=|x|在x0=0处是否可导。","不可导。",["h>0时|h|/h=1。","h<0时|h|/h=−1。","两个单侧极限不同，故普通导数不存在。"])],
["先写差商，不要直接代入h=0。","化简时只能在h≠0的范围内约分。","左右趋于0的极限一致才存在双侧导数。"],
"用定义求x³在x0=1处的导数。",
"在位移-时间曲线出现尖角时，为什么瞬时速度可能不可定义？")

def require(ok,msg):
    if not ok:raise ValueError(msg)

def build():
    inv=json.loads(atoms.OUT.read_text(encoding="utf-8"))
    atoms.validate(inv)
    records={r["id"]:r for r in inv["records"]}
    existing=set()
    for f in ("kb_batch133_six_core_lessons.json","kb_batch134_eight_proof_lessons.json","kb_batch135_eight_deep_lessons.json"):
        for r in json.loads((ROOT/"knowledge/editorial_review"/f).read_text(encoding="utf-8")):
            existing.add(r.get("source_candidate_id",r.get("candidate_id")))
    rows=[]
    for slug,d in L.items():
        src=records["kb133-proposal-"+slug]
        require(src["id"] not in existing,"duplicate prior lesson "+slug)
        rows.append({
            "id":"kb136-deep-"+slug,
            "source_candidate_id":src["id"],
            "course_track":src["track"],
            "knowledge_type":src["knowledge_type"],
            "source_span_sha256":src["source_lock"]["span_sha256"],
            "source_pdf_sha256":src["source_pdf_sha256"],
            "standard_version":"2017-2020-editorial-bounded",
            "formal_definition_or_theorem":d["formal"],
            "notation_and_domain":d["domain"],
            "applicability_and_hypotheses":d["assumptions"],
            "reasoned_steps":[{"step":f"步骤{i}","justification":s} for i,s in enumerate(d["steps"],1)],
            "why_method_is_legal":d["legal"],
            "nonexample_or_failure":d["failure"],
            "typical_wrong_solution":d["wrong"],
            "why_wrong_and_repair":d["repair"],
            "teacher_examples":[{"question":q,"answer":a,"reasoned_solution":sol}
                for q,a,sol in d["examples"]],
            "student_hint_ladder":d["hints"],
            "near_transfer":d["near"],"far_transfer":d["far"],
            "teacher_review_status":"REVIEW_PENDING","teacher_review_evidence":None,
            "teacher_solution_visibility":"TEACHER_ONLY",
            "source_status":"PROVISIONAL_PDFKIT_SOURCE_PROPOSAL_NOT_OFFICIAL_ATOM",
            "formal_proof_certified":False,"free_student_step_verified":False,
            "student_authoritative":False
        })
    return rows

def validate(rows):
    require(rows==build(),"authoring drift, source mismatch or forged approval")
    require(len(rows)==12 and len({x["id"] for x in rows})==12,"manuscript count")
    for x in rows:
        require(len(x["reasoned_steps"])>=4 and len(x["student_hint_ladder"])==3,"proof/hints shallow")
        require(len(x["teacher_examples"])==2 and all(len(e["reasoned_solution"])>=3 for e in x["teacher_examples"]),"example incomplete")
        for field in ("formal_definition_or_theorem","notation_and_domain","applicability_and_hypotheses",
                      "why_method_is_legal","nonexample_or_failure","typical_wrong_solution","why_wrong_and_repair",
                      "near_transfer","far_transfer"):
            minimum=15 if field in ("near_transfer","far_transfer") else 20
            require(len(x[field])>=minimum,"shallow "+field)
        require(x["teacher_review_status"]=="REVIEW_PENDING" and
                x["teacher_review_evidence"] is None and
                x["teacher_solution_visibility"]=="TEACHER_ONLY" and
                not x["formal_proof_certified"] and not x["student_authoritative"] and
                not x["free_student_step_verified"],"forged review/publish/proof status")
    return True

def safe_export(rows):
    validate(rows)
    return {"status":"NO_APPROVED_MATERIAL","publishable_count":0,"items":[],
            "teacher_solution_excluded":True}

def render(rows):
    out=["# Batch136｜十二份原创高中数学深度教师候审讲义","",
         "**官方七轨知识原子分母仍未冻结；来源仅为Mac PDFKit行摘要候选，不得视为教师审核或一般定理形式证明。**",""]
    for r in rows:
        out += ["## "+r["id"]+" · "+r["course_track"],
                "**定义/命题**："+r["formal_definition_or_theorem"],
                "**符号/定义域**："+r["notation_and_domain"],
                "**全部前提**："+r["applicability_and_hypotheses"],""]
        out += [f"{i}. **{s['step']}**：{s['justification']}" for i,s in enumerate(r["reasoned_steps"],1)]
        out += ["","**数学合法性**："+r["why_method_is_legal"],
                "**无效/边界反例**："+r["nonexample_or_failure"],
                "**典型错解**："+r["typical_wrong_solution"],
                "**错因及纠正**："+r["why_wrong_and_repair"],""]
        for i,e in enumerate(r["teacher_examples"],1):
            out += [f"**教师例题{i}**："+e["question"],"**答案（教师侧）**："+e["answer"]]
            out += ["- "+s for s in e["reasoned_solution"]]
        out += ["**分层提示（不得直接泄露教师答案）**"]+["- "+s for s in r["student_hint_ladder"]]
        out += ["**近迁移**："+r["near_transfer"],"**远迁移**："+r["far_transfer"],
                "**课标来源锁摘要（供教师复核，非原文）**："+r["source_span_sha256"],""]
    return "\n".join(out).rstrip()+"\n"

def main():
    a=argparse.ArgumentParser()
    g=a.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    args=a.parse_args()
    if args.write:
        rows=build();validate(rows)
        OUT.write_text(atoms.stable_json(rows),encoding="utf-8")
        MD.write_text(render(rows),encoding="utf-8")
        SAFE.write_text(atoms.stable_json(safe_export(rows)),encoding="utf-8")
    else:
        rows=json.loads(OUT.read_text(encoding="utf-8"))
        validate(rows)
        require(MD.read_text(encoding="utf-8")==render(rows),"markdown drift")
        require(json.loads(SAFE.read_text(encoding="utf-8"))==safe_export(rows),"safe export drift")
    print("PASS: Batch136 12 original source-linked teacher-only lessons")
if __name__=="__main__":main()
