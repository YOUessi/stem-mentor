#!/usr/bin/env python3
"""Batch132: eight original teacher-only elective lessons and independently exact-checked worked answers."""
from __future__ import annotations
import argparse,copy,json,sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_kb_batch132_electives as source
OUT=ROOT/'knowledge/editorial_review/kb_batch132_eight_elective_lessons.json'
ORACLE=ROOT/'docs/evaluation/KB_BATCH132_MATH_ORACLES.json'
MD=ROOT/'docs/evaluation/KB_BATCH132_EIGHT_DEEP_LESSONS.md'
def E(q,steps,ans): return dict(question=q,reasoned_solution=steps,answer=ans)
def D(s,kind,formal,notation,hypotheses,steps,invalid,wrong,repair,examples,hints,near,far,prereq=()):
    return {'suffix':s,'type':kind,'formal':formal,'notation':notation,'assumptions':hypotheses,
            'reasoned_steps':steps,'nonexample_or_failure':invalid,'typical_wrong_solution':wrong,
            'why_wrong_and_repair':repair,'examples':examples,'hints':hints,'near_transfer':near,
            'far_transfer':far,'prerequisites':list(prereq)}
LESSONS=[
D('121-a205','Theorem',
'二维欧氏空间中的线性映射T(x)=Qx保持任意两点欧氏距离，当且仅当实矩阵Q满足QᵀQ=I；任意固定平移T(x)=Qx+b也保持距离。此时Q行列式只能是±1。',
'Q为2×2实矩阵，x,b为列向量；‖x‖₂=√(xᵀx)；I是单位矩阵。',
'欧氏内积及实数矩阵；若讨论Qx+b是仿射等距变换，不得错误称为线性除非b=0。',
[('充分性：计算变换后距离','‖Qx−Qy‖₂²=(x−y)ᵀQᵀQ(x−y)=‖x−y‖₂²，平方根非负得距离相同。'),
 ('必要性：从所有点对距离保留得到所有向量范数保留','取y=0，‖Qv‖₂²=‖v‖₂²对所有v成立，因此vᵀ(QᵀQ−I)v=0。'),
 ('用基向量及其和求出矩阵元','代入e₁、e₂得对角元为零，再代入e₁+e₂且矩阵对称，得非对角元为零，故QᵀQ=I。'),
 ('加入平移并求行列式约束','(Qx+b)−(Qy+b)=Q(x−y)；对QᵀQ取行列式得det(Q)²=1。')],
'非均匀缩放diag(2,1)使水平距离加倍；一般平移不满足T(0)=0，因此不是线性变换。',
'把任何旋转加平移写成一个2×2线性矩阵，并省略仿射常量b。',
'先分别验证是否保持原点和两点距离；平移应写作Qx+b，齐次坐标另有表示方式。',
[E('Q=[[0,-1],[1,0]]将(1,0)和(0,2)变为哪些点？距离是否守恒？',
   ['计算Q(1,0)=(0,1)，Q(0,2)=(-2,0)。','初始差向量为(1,-2)，长度√5。','新差向量为(2,1)，长度√5。'],'新点(0,1)、(-2,0)，距离均为√5。'),
 E('关于y轴反射Q=diag(-1,1)，求(2,1)和(0,1)的像及距离。',
   ['把两点分别乘以Q得(-2,1)、(0,1)。','原距离为2，像点距离为2。','直接算QᵀQ=I，确认一般距离守恒。'],'像点(-2,1)和(0,1)，距离仍为2。')],
['先写变换矩阵，并分别变换两点。','计算像点差向量，观察平移向量为什么消失。','比较QᵀQ与单位矩阵，而不是凭图像看似旋转。'],
'判断Q=diag(1,-1)是否也为等距变换，并给出决定它是否旋转的行列式条件。',
'在图像配准中区分相机平移与镜头缩放对物体间像素距离的影响。'),
D('121-b205','Theorem',
'对m×n实系数矩阵A与m维常数列b，Ax=b有解当且仅当rank(A)=rank([A|b])；若有解，唯一解当且仅当rank(A)=n，否则存在自由变量而有无穷多实解。',
'A为系数矩阵；[A|b]为增广矩阵；rank为列空间或行最简阶梯形非零主元数；n为未知数数量。',
'有限维实线性方程组；不得把齐次方程组必有零解的结论直接套在非齐次系统。',
[('将有解改写为列空间包含关系','Ax=b意味着b是A的各列向量的线性组合，即b∈Col(A)。'),
 ('比较添加b前后列空间维数','b∈Col(A)等价于添加b列没有增大列空间维数，故rank([A|b])=rank(A)。'),
 ('可解时讨论唯一性','任两解x₁,x₂差满足A(x₁−x₂)=0；解唯一等价于Null(A)={0}。'),
 ('由秩-零度定理判断自由变量','dim Null(A)=n−rank(A)；为0时唯一，否则对任意零空间向量沿任意倍数得无限多解。')],
'A=[1;0]、b=[0;1]时rank(A)=1、rank([A|b])=2无解；即使两秩都为1也可能有不唯一解。',
'见rank(A)=rank([A|b])就断言系统有唯一解。',
'一致性与唯一性是两个不同门槛：再计算rank(A)与未知数n的关系。',
[E('x+y=3与2x+2y=6有几个解？',
  ['两行系数成比例、常数列也同比例，两秩均1。','未知数n=2，秩1<n。','令x=t，y=3−t得无穷多个解。'],'无穷多解(x,y)=(t,3−t)。'),
 E('x+y=3与2x+2y=5有几个解？',
  ['系数行成比例故rank(A)=1。','常数不同倍，增广矩阵秩变为2。','两秩不等，因此不存在解。'],'无解。')],
['把每个方程的系数和常数分开构成矩阵。','先行消元比较两个秩，不要先算未知数。','若秩相等再和未知数个数比较以区分唯一与无限。'],
'判断x+y=3与x−y=1的解类型，并求出唯一解。','在推荐系统中把重复线性约束当新增独立信息会造成什么参数辨识问题。'),
D('122-a302','Theorem',
'微积分基本定理的一个版本：若f在闭区间[a,b]连续，定义F(x)=∫ₐˣ f(t)dt，则在(a,b)处F′(x)=f(x)；在端点讨论适当单侧导数。因而对f的任一原函数G有∫ₐᵇ f(t)dt=G(b)−G(a)。',
'f为实值连续函数；F为变上限积分；a<b；G′=f；积分为有向定积分。',
'闭区间上的连续性、Riemann可积性；对求导公式讨论内点；若仅分段连续，不得无条件在跳点取导。',
[('连续性给出定积分与局部平均值可控','F(x+h)−F(x)=∫ₓˣ⁺ʰf(t)dt，除以h为该小区间平均值。'),
 ('减去f(x)并估计误差','由连续性，t靠近x时|f(t)−f(x)|任意小，因此积分平均与f(x)之差也趋于0。'),
 ('于是证明导数等于f','差商极限存在并为f(x)，即F′(x)=f(x)。'),
 ('比较G与F并使用零导数常值','若G′=f，则(G−F)′=0，由中值定理知G−F恒定；F(a)=0，因此F(b)=G(b)−G(a)。')],
'若f在0有跳跃，F(x)=∫₀ˣf(t)dt未必在0处可导；仅知道各侧可积不够。',
'把∫₀ˣ f(t)dt的导数无条件写作f(x)，省略连续性和内点条件。',
'先核查目标点附近f的连续性；不能满足时需直接计算差商并说明单侧情况。',
[E('f(t)=2t，F(x)=∫₀ˣ2t dt；求F(3)、F′(3)。',
  ['原函数为t²，积分得F(x)=x²。','F(3)=9。','求导F′(x)=2x，故F′(3)=6=f(3)。'],'F(3)=9且F′(3)=6。'),
 E('求∫₀²t²dt并核对原函数端点差。',
  ['原函数G(t)=t³/3。','G(2)−G(0)=8/3−0。','f连续，满足基本定理前提。'],'8/3。')],
['先判断被积函数在整个目标区间是否连续。','写出变上限积分的差商及局部区间。','选一个原函数，再做两个端点的差值而不是直接代上限。'],
'将f(t)=cos t的变上限积分和导数关系重新计算一遍。',
'对离散采样的传感器输出，讨论为何插值后求积分仍有模型误差而不能完全继承连续数学假设。'),
D('122-b301','Method',
'连续实函数f在[a,b]上的有向定积分是上下带符号面积之差，而其与x轴之间的几何面积为∫ₐᵇ|f(x)|dx；函数跨零点时须分段取绝对值。',
'∫为Riemann定积分；a<b；|f|为函数逐点绝对值；几何面积非负。',
'f连续以保证积分存在；计算几何面积需判断零点或区间上函数符号，复杂边界还需确认曲线间上下关系。',
[('求出区间内的全部符号变点','在每段内用测试点或连续性论证f符号一致，不能只靠一张示意图。'),
 ('每段积分按符号处理','当f≥0，有向积分与面积相同；当f≤0，几何面积取其相反数。'),
 ('把各段非负面积相加','总几何面积等于∫|f|，而不是有向积分的绝对值；后者可能因抵消而较小。')],
'f(x)=x在[-1,1]的积分为0但几何面积为1；绝对值不能移到整个积分外再取。',
'面积=|∫₋₁¹x dx|=0，因此断言没有围成面积。',
'先按0拆成[-1,0]和[0,1]两段分别取绝对值后相加，得到1。',
[E('计算f(x)=x在[-1,1]的有向积分及几何面积。',
 ['原函数为x²/2，上下限之差是0。','零点0分成负正两段。','绝对面积为−∫₋₁⁰x dx+∫₀¹x dx=1。'],'有向积分0，几何面积1。'),
 E('对f(x)=x−1在[0,2]计算有向积分和几何面积。',
 ['原函数x²/2−x，在2与0的差为0。','零点x=1。','左右负正面积均为1/2，总面积1。'],'有向积分0，几何面积1。')],
['画出或确定函数在哪些区间为正、负。','先分别算有向积分与符号翻转点。','面积计算要对每段取绝对值，不能只取积分总值绝对值。'],
'对f(x)=x²−1在[-2,2]计算几何面积，先求出零点。',
'在财务现金流中区分正负净流量积分与总交易量，解释抵消与累计绝对量的不同。'),
D('123-a403','Method',
'非零法向量n给出平面Π：n·(r−r₀)=0；非零方向向量v给出直线r=p+tv。代入后解t[n·v]=n·(r₀−p)，可分类唯一相交、平行不交或整线包含。',
'n为平面非零法向量，r₀为平面上一点，p为直线上一点，v≠0；t为实参数。',
'空间欧氏坐标；n和v均非零；所有法向量、点和方向的维度一致。',
[('写下合法平面与直线表达','法向量非零，否则平面方程可能恒真或无解；方向非零，否则不是直线。'),
 ('代入直线参数式','得到标量线性方程t(n·v)=n·(r₀−p)。'),
 ('非零系数时求唯一交点','若n·v≠0，可解唯一t并回代直线参数。'),
 ('零系数时判断常数项','若n·v=0且右侧≠0则无解、平行；若右侧也为0则所有t成立，整条直线包含在平面中。')],
'只由n·v=0就说直线与平面平行且不相交，忽略整条直线位于平面内的情况。',
'看到直线方向与平面法向量正交，就直接认定“严格平行不相交”，未代入已知直线上的点。',
'把一个直线上点代入平面方程进一步区分包含与不相交。',
[E('平面z=0，直线(1,0,1)+t(0,0,-1)，求交点。',
 ['平面法向量n=(0,0,1)，方向v=(0,0,-1)非零。','代入z=1−t=0得t=1。','回代得到交点(1,0,0)。'],'唯一交点(1,0,0)。'),
 E('平面z=0，直线(1,0,1)+t(1,0,0)，判断位置关系。',
 ['n·v=0，所以无法得到有限唯一交参。','直线任意点z=1，而平面要求z=0。','右侧非零，判定平行不相交。'],'严格平行且不相交。')],
['先检查给出的方向向量和法向量是否为零。','把直线参数式代入平面并化简成t的一元方程。','系数为0时必须继续看常数项，才能区分平行与包含。'],
'平面z=0与直线(1,0,0)+t(1,0,0)属于哪种关系？',
'机器人轨迹检查中为什么“速度方向平行地面”并不意味着机器人必然离地。'),
D('123-a405','Method',
'含截距的一元普通最小二乘：给定n≥2个配对样本(xᵢ,yᵢ)，若Sxx=Σ(xᵢ−x̄)²>0，则唯一最小二乘斜率b₁=Sxy/Sxx，截距b₀=ȳ−b₁x̄，其中Sxy=Σ(xᵢ−x̄)(yᵢ−ȳ)。',
'n为观测对数；x̄、ȳ是样本均值；Sxx、Sxy为中心化平方和、乘积和；ŷ=b₀+b₁x。',
'所有x,y有限实数；需要n≥2且至少两个不同的x使Sxx>0；该算法是描述拟合，不自动得到因果效应。',
[('定义平方损失L(b₀,b₁)=Σ(yᵢ−b₀−b₁xᵢ)²','这是有限实数二次函数；最小化的是纵向残差平方，而不是垂直距离。'),
 ('对截距求一阶条件','∂L/∂b₀=−2Σ(yᵢ−b₀−b₁xᵢ)=0，推出b₀=ȳ−b₁x̄。'),
 ('代入并对斜率求条件','L变为Σ[(yᵢ−ȳ)−b₁(xᵢ−x̄)]²；导数为−2Sxy+2b₁Sxx。'),
 ('检查唯一极小值条件','Sxx>0使斜率方向严格凸，故b₁=Sxy/Sxx唯一；若Sxx=0，斜率与截距无法分别唯一确定。')],
'全部x相同则Sxx=0，斜率公式无定义；即便拟合相关很强也不能据此证明因果。',
'使用所有x相同的数据求出一个有限斜率并报告“完美线性关系”。',
'先检查Sxx，若为零则拒绝唯一斜率并声明参数不可辨识。',
[E('数据点(0,1),(1,3),(2,5)，求最小二乘直线。',
  ['x̄=1，ȳ=3，Sxx=2。','Sxy=(-1)(-2)+0+1·2=4。','斜率2，截距3−2·1=1。'],'ŷ=1+2x。'),
 E('数据点(0,5),(2,1)，求含截距最小二乘直线。',
  ['x̄=1，ȳ=3，Sxx=2。','Sxy=(-1)(2)+(1)(-2)=-4。','斜率−2，截距3−(-2)·1=5。'],'ŷ=5−2x。')],
['先核查每个x都不是同一个值。','列表求出x̄、ȳ、Sxx、Sxy。','只有Sxx>0才除，之后用b₀=ȳ−b₁x̄求截距。'],
'数据点(1,1),(2,4),(3,9)求拟合直线并比较真实二次函数。',
'训练集上斜率存在并不证明未来市场价格有相同趋势，说明外推验证需要什么数据。'),
D('123-b405','Theorem',
'三元线性系统Ax=b若det(A)≠0，则有唯一解，且对i=1,2,3有xᵢ=det(Aᵢ)/det(A)，Aᵢ是用b替换A第i列的矩阵；这就是克拉默法则。',
'A为3×3系数矩阵，b为3×1列向量，Aᵢ为替换第i列矩阵，det为行列式。',
'实数或适当域上的方阵，det(A)严格非零；若det(A)=0不能使用除法公式，不应直接推断无解。',
[('det(A)非零给出逆矩阵','三阶方阵det(A)≠0等价于可逆，故Ax=b有且仅有x=A⁻¹b。'),
 ('用多线性证明列替换关系','把b=Σxⱼ A的第j列代入第i列替换后的行列式。'),
 ('利用两列相同则行列式为零','当j≠i时替换列与原第j列相同，对应行列式为零；仅j=i留下xᵢdet(A)。'),
 ('合法除以非零det(A)','因此det(Aᵢ)=xᵢdet(A)，得到每个分量的公式；未假定det(A)=0情况。')],
'若A两行相同det(A)=0，系统仍可能有无限多解，也可能无解；克拉默分式不可用于这些情况。',
'计算det(A)=0后把0/0直接等于0，或者断言“无解”。',
'分母为零时停止克拉默法则，改查rank(A)和rank([A|b])。',
[E('A=diag(2,3,4)，b=(4,9,8)，求x。',
 ['det(A)=24非零。','直接解2x=4、3y=9、4z=8得x=(2,3,2)。','以替换列行列式分别为48、72、48，除24一致。'],'(2,3,2)。'),
 E('x+y=3，y=2，2z=6，求三元解。',
 ['A=[[1,1,0],[0,1,0],[0,0,2]]，det(A)=2。','第二式y=2，第三式z=3。','第一式x=1，且解唯一。'],'(1,2,3)。')],
['先按行写出系数矩阵，计算det(A)。','det(A)=0时立即停止分式并分析秩。','非零时逐列替换常数列，最后把答案代回所有方程。'],
'对A=[[1,0,0],[0,1,0],[0,0,0]]，b=(1,2,0)解释为何有解但不能用克拉默。',
'在三维标定中传感器线性方程重复可能让解不唯一，说明增加独立观测的作用。'),
D('124-b501','Concept',
'实三维向量u,v的内积u·v=Σuᵢvᵢ；叉积u×v为垂直于二者的有向向量，满足‖u×v‖=‖u‖‖v‖sinθ，其中θ在u,v均非零时为夹角。',
'向量坐标u=(u₁,u₂,u₃)，v=(v₁,v₂,v₃)；u·v为标量，u×v为向量。',
'方向和夹角讨论要求两个向量都非零；叉积运算本身可对零向量定义为零。',
[('内积按坐标求和','u·v=u₁v₁+u₂v₂+u₃v₃；非零向量时由内积除长度获得cosθ。'),
 ('按行列式形式展开叉积','u×v=(u₂v₃−u₃v₂,u₃v₁−u₁v₃,u₁v₂−u₂v₁)。'),
 ('检查正交和面积解释','直接代数可验(u×v)·u=0及(u×v)·v=0，长度等于张成平行四边形的面积。'),
 ('限制零向量夹角','若u=0或v=0，夹角公式分母为零，不能给出θ；叉积则仍为零。')],
'零向量与非零向量内积为0，但夹角没有定义；不能声称一定相互垂直且夹角90度。',
'见u·v=0就直接在零向量场景宣称夹角θ=π/2。',
'先验‖u‖‖v‖>0再讨论cosθ；叉积的代数定义与夹角定义分开。',
[E('u=(1,0,0),v=(0,1,0)，求内积、叉积和夹角。',
 ['逐项相乘加总得内积0。','叉积按坐标公式得(0,0,1)。','两向量非零，cosθ=0，因此θ=90度。'],'内积0，叉积(0,0,1)，夹角90度。'),
 E('u=(1,2,0),v=(2,0,0)，求内积、叉积及平行四边形面积。',
 ['内积1·2+2·0=2。','叉积第三分量1·0−2·2=-4，其余为0。','叉积长度4就是面积。'],'内积2，叉积(0,0,-4)，面积4。')],
['先确定你算的是标量内积还是向量叉积。','按三个分量展开，核查叉积方向和符号。','如果求夹角必须先检查两个向量均非零。'],
'对u=(1,1,0)、v=(1,-1,0)求叉积并解释其方向。',
'航迹控制中用叉积表示法向方向时，为什么零速度向量不能定义唯一朝向。'),
]
def require(ok,why):
    if not ok:raise ValueError(why)
def enc(d):return json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n'
def build():
    source_data=json.loads(source.OUT.read_text(encoding='utf-8'))
    src={r['candidate_id']:r for r in source_data['records']}
    require(len(LESSONS)==8 and len({l['suffix'] for l in LESSONS})==8,'lesson list drift')
    result=[]
    for l in LESSONS:
        cid='hs-semantic-pilot-'+l['suffix']
        require(cid in src and len(l['reasoned_steps'])>=3 and len(l['examples'])==2 and
                len(l['hints'])==3 and all(len(x)>24 for x in [l['formal'],l['notation'],l['assumptions'],l['nonexample_or_failure'],l['typical_wrong_solution'],l['why_wrong_and_repair'],l['near_transfer'],l['far_transfer']]),'incomplete lesson '+cid)
        d={'id':'kb132-deep-'+l['suffix'],'candidate_id':cid,'objective':src[cid]['proposed_objective'],
           'course_track':src[cid]['track'],'knowledge_type':l['type'],
           'formal_definition_or_theorem':l['formal'],'notation_and_domain':l['notation'],
           'applicability_and_hypotheses':l['assumptions'],
           'reasoned_steps':[{'step':x,'justification':y} for x,y in l['reasoned_steps']],
           'nonexample_or_failure':l['nonexample_or_failure'],'typical_wrong_solution':l['typical_wrong_solution'],
           'why_wrong_and_repair':l['why_wrong_and_repair'],'teacher_examples':l['examples'],
           'student_hint_ladder':l['hints'],'near_transfer':l['near_transfer'],'far_transfer':l['far_transfer'],
           'prerequisite_candidate_ids':l['prerequisites'],'source_line_lock':src[cid]['source_lock'],
           'source_pdf_sha256':src[cid]['source_pdf_sha256'],'source_status':'EDITORIAL_ORIGINAL_LINE_CHECKED_NOT_OFFICIAL_ATOM',
           'version':'2017-2020-editorial-batch132','teacher_review_status':'REVIEW_PENDING',
           'teacher_review_evidence':None,'teacher_solution_visibility':'TEACHER_ONLY',
           'student_authoritative':False,'formal_proof_certified':False,'free_student_step_verified':False}
        result.append(d)
    return result
def validate_lessons(docs):
    truth=build()
    require(type(docs) is list and len(docs)==8 and
            {d.get("id") for d in docs}=={d["id"] for d in truth}, "lesson census or IDs drift")
    by_id={d["id"]:d for d in truth}
    source_data=json.loads(source.OUT.read_text(encoding='utf-8'))
    anchored={r["candidate_id"]:r for r in source_data["records"]}
    for d in docs:
        a=by_id[d["id"]]
        require(d==a,"lesson proof or content unexpectedly changed "+d["id"])
        require(d["candidate_id"] in anchored and
                d["source_line_lock"]==anchored[d["candidate_id"]]["source_lock"] and
                d["teacher_review_status"]=="REVIEW_PENDING" and
                d["teacher_review_evidence"] is None and
                d["teacher_solution_visibility"]=="TEACHER_ONLY" and
                d["student_authoritative"] is False and
                d["formal_proof_certified"] is False and
                d["free_student_step_verified"] is False, "attempted fake lesson authority")
        require(len(d["teacher_examples"])==2 and
                all(len(e["reasoned_solution"])>=3 for e in d["teacher_examples"]) and
                len(d["student_hint_ladder"])==3 and
                len(d["reasoned_steps"])>=3, "incomplete teacher lesson")
    return True
def math_oracles():
    h=S.symbols('h',real=True);R=S.Rational
    A=S.Matrix([[1,1],[2,2]]); rank1=A.rank()
    Q=S.Matrix([[0,-1],[1,0]])
    rot=Q*S.Matrix([1,0]);rot2=Q*S.Matrix([0,2])
    qref=S.diag(-1,1)
    checks={
    '121-a205':[Q.T*Q==S.eye(2) and (rot-rot2).norm()==S.sqrt(5),
                 (qref*S.Matrix([2,1])-qref*S.Matrix([0,1])).norm()==2],
    '121-b205':[rank1==A.row_join(S.Matrix([3,6])).rank()==1 and S.simplify((3-h)+(h)-3)==0,
                 rank1==1 and A.row_join(S.Matrix([3,5])).rank()==2],
    '122-a302':[S.integrate(2*h,(h,0,3))==9 and S.diff(h**2,h).subs(h,3)==6,
                 S.integrate(h**2,(h,0,2))==R(8,3)],
    '122-b301':[S.integrate(h,(h,-1,1))==0 and S.integrate(S.Abs(h),(h,-1,1))==1,
                 S.integrate(h-1,(h,0,2))==0 and S.integrate(S.Abs(h-1),(h,0,2))==1],
    '123-a403':[(S.Matrix([1,0,1])+S.Matrix([0,0,-1])).tolist()==[[1],[0],[0]],
                S.Matrix([0,0,1]).dot(S.Matrix([1,0,0]))==0 and (S.Matrix([1,0,1])+3*S.Matrix([1,0,0]))[2]==1],
    '123-a405':[S.Matrix([-1,0,1]).dot(S.Matrix([-2,0,2]))/2==2 and 3-2*1==1,
                 S.Matrix([-1,1]).dot(S.Matrix([2,-2]))/2==-2 and 3-(-2)*1==5],
    '123-b405':[S.diag(2,3,4).det()==24 and S.diag(2,3,4).inv()*S.Matrix([4,9,8])==S.Matrix([2,3,2]),
                 S.Matrix([[1,1,0],[0,1,0],[0,0,2]]).inv()*S.Matrix([3,2,6])==S.Matrix([1,2,3])],
    '124-b501':[S.Matrix([1,0,0]).dot(S.Matrix([0,1,0]))==0 and
                 S.Matrix([1,0,0]).cross(S.Matrix([0,1,0]))==S.Matrix([0,0,1]),
                 S.Matrix([1,2,0]).dot(S.Matrix([2,0,0]))==2 and
                 S.Matrix([1,2,0]).cross(S.Matrix([2,0,0]))==S.Matrix([0,0,-4])],
    }
    negatives={
    '121-a205':(S.diag(2,1)*S.Matrix([1,0])).norm()!=S.Matrix([1,0]).norm(),
    '121-b205':rank1!=A.row_join(S.Matrix([3,5])).rank(),
    '122-a302':S.limit(S.Abs(h)/h,h,0,dir='+')!=S.limit(S.Abs(h)/h,h,0,dir='-'),
    '122-b301':S.integrate(S.Abs(h),(h,-1,1))!=abs(S.integrate(h,(h,-1,1))),
    '123-a403':S.Matrix([0,0,1]).dot(S.Matrix([1,0,0]))==0 and S.Matrix([1,0,1])[2]!=0,
    '123-a405':sum((x-1)**2 for x in [1,1])==0,
    '123-b405':S.Matrix([[1,1,0],[1,1,0],[0,0,1]]).det()==0,
    '124-b501':S.Matrix([0,0,0]).norm()==0 and S.Matrix([0,0,0]).dot(S.Matrix([1,0,0]))==0,
    }
    require(set(checks)==set(negatives)==set(l['suffix'] for l in LESSONS),'oracle coverage mismatch')
    require(all(len(v)==2 and all(bool(x) for x in v) for v in checks.values()) and
            all(bool(x) for x in negatives.values()),'independent worked example or negative oracle failed')
    return {'batch':132,'independently_checked_teacher_examples':16,
            'boundary_counterexamples':8,'formal_general_theorems_certified':0,
            'free_student_steps_verified':0,'teacher_approved':0,'student_authoritative':0,
            'finite_cases_only':True,
            'example_results':{k:[bool(x) for x in v] for k,v in checks.items()},
            'counterexample_results':{k:bool(x) for k,x in negatives.items()}}
def render(docs,checks):
    lines=['# Batch132 — eight deep original elective mathematics lesson manuscripts','',
      'REVIEW_PENDING / TEACHER_ONLY. Exact checked examples are finite cases, not a universal theorem proof or teacher endorsement.',
      f"Independently recomputed: {checks['independently_checked_teacher_examples']} examples and {checks['boundary_counterexamples']} invalid-condition cases.",'']
    for d in docs:
        a=d['source_line_lock'];lines.extend([f"## {d['objective']} ({d['course_track']})",
         f"Editorial source anchor p.{a['page']} lines {a['start_line']}-{a['end_line']} (not official atom denominator)",
         'Formal statement: '+d['formal_definition_or_theorem'],
         'Symbols and domain: '+d['notation_and_domain'],
         'All hypotheses: '+d['applicability_and_hypotheses'],
         '### Justified steps'])
        for i,s in enumerate(d['reasoned_steps'],1):lines.append(f"{i}. {s['step']} — {s['justification']}")
        lines.extend(['Failure / non-example: '+d['nonexample_or_failure'],
          'Typical incorrect reasoning: '+d['typical_wrong_solution'],
          'Repair: '+d['why_wrong_and_repair'],'### Teacher-only worked examples'])
        for e in d['teacher_examples']:
            lines.append('**Question:** '+e['question'])
            for i,s in enumerate(e['reasoned_solution'],1):lines.append(f"{i}. {s}")
            lines.append('**Teacher-only answer:** '+e['answer'])
        lines.append('### Student hints without solution')
        for i,s in enumerate(d['student_hint_ladder'],1):lines.append(f'{i}. {s}')
        lines.extend(['Near transfer: '+d['near_transfer'],'Far transfer: '+d['far_transfer'],''])
    return '\n'.join(lines).rstrip()+'\n'
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true')
    a=p.parse_args();docs=build();validate_lessons(docs);checks=math_oracles()
    for f,s in [(OUT,enc(docs)),(ORACLE,enc(checks)),(MD,render(docs,checks))]:
        if a.write:f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s,encoding='utf-8')
        else:require(f.exists() and f.read_text(encoding='utf-8')==s,'snapshot drift '+str(f))
    print('Batch132:',len(docs),'teacher draft manuscripts',checks['independently_checked_teacher_examples'],'exact examples',checks['boundary_counterexamples'],'negative cases')
if __name__=='__main__':main()
