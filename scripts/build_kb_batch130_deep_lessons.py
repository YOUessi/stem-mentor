#!/usr/bin/env python3
"""Eight independently checkable, original, teacher-side mathematics lessons."""
from __future__ import annotations
import argparse,copy,json,sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_kb_batch130_core_source as source
OUT=ROOT/'knowledge/editorial_review/kb_batch130_eight_deep_lessons.json'
ORACLE=ROOT/'docs/evaluation/KB_BATCH130_MATH_ORACLES.json'
REPORT=ROOT/'docs/evaluation/KB_BATCH130_EIGHT_DEEP_LESSONS.md'
def E(q,steps,answer):return {'question':q,'reasoned_solution':steps,'answer':answer}
def L(s,typ,formal,notation,assumptions,proof,invalid,wrong,repair,examples,hints,near,far):
    return {'suffix':s,'type':typ,'formal':formal,'notation':notation,'assumptions':assumptions,
        'reasoned_steps':proof,'nonexample_or_failure':invalid,'typical_wrong_solution':wrong,
        'why_wrong_and_repair':repair,'examples':examples,'hints':hints,
        'near_transfer':near,'far_transfer':far}
LESSONS=[
L('121-c201','Concept',
'设U为研究论域、A为U内集合；记x∈A表示x是A的一个元素，x∉A表示不是。记A⊆B表示每个x∈A都属于B。元素属于与集合包含是两个不同类型的关系。',
'符号∈为对象与集合之间的关系；⊆为集合与集合之间的关系；∅表示空集。U的选取影响元素资格。',
'明确U和A、B的元素类型；集合不计重复元素、顺序无关。允许集合本身充当另一个集合的元素，但不能省略层级。',
[('明确研究论域及元素类型','若元素是整数，{1}是集合而非整数1，必须先辨识对象层级。'),
 ('按定义检查x∈A','只需判定指定对象是否列在集合中，或满足其描述性质。'),
 ('检查A⊆B时遍历每个A内元素','必须证明全称命题；找出一个A中而不在B中的元素就足以否定包含。')],
'如A={1,2}，1∈A且{1}⊆A，但{1}∈A通常为假；把⊆误写成∈是类型错误。',
'因1∈{1,2}，就声称{1}∈{1,2}。',
'第二句的对象是集合{1}，与数字1不同；重写为{1}⊆{1,2}才成立。',
[E('A={1,3},B={2,3}，求交集与并集，并说明元素3的归属。',
  ['分别列出满足两集合都包含的元素，得3。','列出至少属于其中一个集合的元素，去重得1,2,3。','核查3∈A且3∈B。'],
  'A∩B={3}，A∪B={1,2,3}；3属于交集。'),
 E('C={{1},2}，判断{1}∈C、1∈C和{1}⊆C。',
  ['注意C的第一个元素本身是集合{1}。','对象{1}作为元素属于C；整数1不属于C。','要判断{1}⊆C需核对整数1∈C，结果为假。'],
  '{1}∈C为真，1∈C为假，{1}⊆C为假。')],
['先说明元素是整数还是集合。','写出每个命题左右的对象类型。','分别代入∈和⊆的形式定义，不凭外观判断。'],
'把A={-1,0}、B={0,1}的交并集算出并用判据说明。','在分层标签集合中，讨论“一个标签”和“只含该标签的标签集”的查询语义差别。'),
L('122-c306','Theorem',
'对定义于同一论域D的命题P(x)、Q(x)，P是Q的充要条件，当且仅当对所有x∈D有P(x)⇒Q(x)并且Q(x)⇒P(x)；即两命题真值在D上等价。',
'P⇒Q是P充分；Q⇒P是P必要；P⇔Q同时要求两个方向；量词范围均为D。',
'两命题论域一致。涉及平方、除法、开方时须单独检查变换可逆性和被除式非零。',
[('证明充分性方向','任取D中满足P的x，根据前提推导Q，不可只用一个例子说明。'),
 ('证明必要性方向','任取满足Q的x反推P，必要时因式分解或考虑多值。'),
 ('合并两个全称蕴含','只有两边均成立才能使用⇔；如果一边失败，给出域内反例。')],
'实数x²=9只保证x=±3，不等价于x=3；平方可消去符号。',
'从x²=9取正平方根得x=3，于是写成x²=9 ⇔ x=3。',
'从x²=9分解(x-3)(x+3)=0，须保留x=-3，或把原域改为x≥0才可得到该等价。',
[E('实数域中证明x²=9与“x=3或x=-3”充要。',
  ['由x²=9得(x-3)(x+3)=0。','零因子定律给出x=3或-3。','反代任一分支均得平方为9。'],
  '两命题在实数域等价。'),
 E('实数域中判断|x|=x是否等价于x≥0。',
  ['若x≥0，绝对值定义给出|x|=x。','若|x|=x且x<0，左侧=-x>0而右侧<0矛盾。','故成立时x≥0，两个方向完备。'],
  '等价，包含边界x=0。')],
['先分别列出P与Q的解集。','检查每个方向可能存在的反例。','对二次方程先做因式分解，再把两个方向写全。'],
'检查“x>1”与“x²>1”在D=R以及D=[0,∞)上的充要性差异。','把数据筛选条件“年龄至少18”与“出生年份早于某年”之间的时间边界写成严格的充要条件。'),
L('122-c311','Theorem',
'介值零点定理：若实函数f在闭区间[a,b]连续，a<b，且f(a)f(b)<0，则存在c∈(a,b)使f(c)=0；结论仅保证存在而非唯一。',
'a,b为闭区间端点；c为内部零点；连续性是在整个[a,b]上；端点异号严格小于零。',
'函数在含端点的整个闭区间连续；a<b；f(a)与f(b)均非零且异号。',
[('消除端点符号顺序','若f(a)>0>f(b)则考虑连续函数−f；下文不妨设f(a)<0<f(b)。'),
 ('逐次二分构造保号套区间','取中点m。若f(m)=0直接结束，否则保留左右端点异号的那一半；重复得到闭区间[a_n,b_n]，各端点函数值一负一正。'),
 ('用实数完备性得到极限点','区间套逐层包含，长度(b−a)/2^n趋于0；由实数区间套定理有唯一公共点c，且a_n与b_n均收敛于c。'),
 ('用连续性将符号传到极限','由f(a_n)<0与f(b_n)>0、连续性得f(c)≤0和f(c)≥0，故f(c)=0。若某步中点已为零也满足结论。'),
 ('排除端点并声明非唯一','f(a)、f(b)严格非零，故c在(a,b)内部。此证明不保证只有一个根，唯一性需另证。')],
'f(x)=1/x在[-1,1]端点异号但0处未定义，不能套用连续函数零点定理。',
'只检查f(a)<0<f(b)便宣布有根；或宣布由定理得唯一根。',
'先逐点检查[a,b]连续，再用异号给存在性。唯一性另需严格单调等额外前提。',
[E('证明x³-x-1=0在(1,2)有实根。',
  ['令f(x)=x³-x-1，它是多项式，处处连续。','计算f(1)=-1、f(2)=5，乘积负。','套用闭区间零点存在定理得到内部根。'],
  '在(1,2)至少存在一个实根。'),
 E('证明x²-2=0在(1,2)至少有一个零点。',
  ['f(x)=x²-2连续于[1,2]。','f(1)=-1，f(2)=2，符号相反。','由介值性存在c∈(1,2)，f(c)=0。'],
  '至少一根在(1,2)；具体为√2。')],
['先给出函数在整个闭区间连续的理由。','分别代入两个端点计算确切符号。','只得存在性；思考唯一性还需要什么独立条件。'],
'将f(x)=x³-3x在[-2,2]检查异号条件及零点数量的区别。','传感器高度信号在两时刻跨越警戒线，阐明为何离散采样不能自行保证物理信号连续。'),
L('123-c407','Method',
'若a>0、a≠1、b>0、b≠1且x>0，则log_a(x)=log_b(x)/log_b(a)；真数域及两个底数条件缺一不可。',
'a为旧底，b为新底，x为真数；log_b(a)是非零分母。',
'实对数范围：x>0；a,b>0且不等于1。由log_b(a)≠0保证合法相除。',
[('设y=log_a(x)','根据对数定义，a^y=x，合法底数保证一一对应。'),
 ('两边以b为底取对数','y·log_b(a)=log_b(x)，使用指数对数恒等式。'),
 ('除以非零量','a≠1保证log_b(a)≠0，因此可以解出y并得到换底公式。')],
'a=1或b=1时对数函数无定义；x≤0时实对数不存在。',
'把log_2(8)写成ln(2)/ln(8)，倒置换底公式分子分母。',
'按定义先估计答案是3，再计算ln8/ln2；核对指数正逆关系避免倒数错误。',
[E('用换底及指数定义分别求log_2(8)。',
  ['x=8>0、底2合法，选择自然对数作为新底。','得到ln8/ln2。','因为8=2³，该比值等于3。'],
  '3。'),
 E('求log_(1/4)(16)，并说明答案符号。',
  ['底1/4介于0与1之间，满足合法条件但对数函数递减。','(1/4)^(-2)=16。','由一一对应，原对数为-2。'],
  '-2。')],
['先检查真数是否正及两个底数的限制。','把对数转换为幂指数等式。','用ln x / ln a求值，再代回原指数式核对。'],
'计算log_9(3)，比较使用底3或自然底的表达。','在信息压缩的对数刻度中比较换底时单位缩放，解释为何对数底不允许1。'),
L('123-c411','Concept',
'有限样本空间Ω的每个基本结果等可能时，P(A)=|A|/|Ω|；这里的等可能针对基本结果，不保证某个多对一变换后的结果类别等可能。',
'Ω为有限基本结果集合；A⊆Ω为事件；|·|为集合元素数。',
'每个基本结果必须等可能且彼此互斥、穷尽；须明确骰子或硬币是否可区分。各枚单独公平不保证联合等可能，须另给独立性或联合分布。',
[('构造等可能基本空间','双骰用有序对(i,j)，共36种，而不是用11种和值。'),
 ('从基本结果中筛选事件','根据具体事件列举或计数满足条件的结果，每个结果只计一次。'),
 ('以基本结果数量归一化','将有利结果数除以Ω的总大小；若类别不等可能则此式不合法。')],
'独立公平骰子的和值2只对应(1,1)，和值7对应6个有序对；11种和值并不等可能。若两骰各自公平但完全相关，则36个有序点对也不等可能。',
'把和值2到12当作11个等可能样本，声称P(和值7)=1/11。',
'在36个等可能有序点数对中计数，和值7概率为6/36。',
[E('两枚相互独立的公平六面骰同时投掷，点数和为7的概率。',
  ['两枚骰子各自公平且相互独立，所以36个有序点对(i,j)等可能。','有利结果是(1,6),(2,5),(3,4),(4,3),(5,2),(6,1)，共6个。','按等可能公式得6/36。'],
  '1/6。'),
 E('两枚可区分且相互独立的公平硬币，恰有一枚正面的概率。',
  ['两枚硬币分别公平且相互独立，故HH、HT、TH、TT四种有序结果各为1/4。','有利结果HT和TH两种。','除以四得到2/4。'],
  '1/2。')],
['从物理实验出发写出真正等可能的基本结果。','先确认结果是否有序，是否存在重复计数。','最后数有利结果与总结果，勿把事件类别等分。'],
'两枚相互独立的公平骰子求和值为2的概率，并与和值为7对比。','把抽签模型推广到按人数比例抽取的分层样本，说明何时不再能对所有人等可能。'),
L('120-s103','Concept',
'导数定义：f在x0附近有定义且极限lim_(h→0)[f(x0+h)-f(x0)]/h存在为有限实数时，f在x0可导，导数f′(x0)等于该极限；h≠0。',
'x0是求导点；h为非零增量趋向0；商为平均变化率；极限是瞬时变化率。',
'必须有x0双侧邻域（或明确单侧导数的不同概念）且函数取值合法；不可把一侧导数当作双侧导数。',
[('列差商并明确h≠0','由两个函数值的变化量除以输入变化量定义平均变化率。'),
 ('化简后取双侧极限','能约分h是因为求极限时h不等于0；再核对左右极限。'),
 ('极限存在才定义导数','极限有限且相同才有瞬时变化率与切线斜率。')],
'|x|在0左右差商分别为1与-1，故f′(0)不存在；图上尖点不能硬套一个斜率。',
'认为|x|的值在0为0，因此导数也为0；或只取右侧极限。',
'函数值与变化率不同；直接计算左右差商，若不相等判不可导。',
[E('使用定义求f(x)=x²在x0=3的导数。',
  ['差商=((3+h)²-9)/h。','h≠0时展开并化简为6+h。','取h→0，极限是6。'],
  'f′(3)=6。'),
 E('用差商求f(x)=1/x在x0=2的导数。',
  ['先要求h≠0且2+h≠0。','差商=[1/(2+h)-1/2]/h=-1/[2(2+h)]。','令h→0得到-1/4。'],
  'f′(2)=-1/4。')],
['先把x0代入，写出完整差商而非立刻套公式。','只在h≠0时进行代数约分。','做双侧极限检查，尤其关注尖点和定义域边界。'],
'用定义计算f(x)=x³在x0=1的导数。','速度记录是位置对时间差商的极限；说明为何离散测量的有限差分只是估计。'),
L('120-s107','Concept',
'对过两不同点(x1,y1),(x2,y2)的非竖直直线，斜率k=(y2-y1)/(x2-x1)。竖直直线的倾斜角是π/2，但斜率不存在。',
'k是纵坐标变化量除以横坐标变化量；倾斜角α∈[0,π)且k=tanα仅在α≠π/2有效。',
'两点必须不同；若x2=x1时垂直于x轴，不能使用斜率公式分母。',
[('由直角三角形确定水平与竖直变化','过两点的水平位移为Δx、竖直位移为Δy。'),
 ('仅在Δx≠0时求比值','Δy/Δx是tanα，交换两点两差同时反号，商不变。'),
 ('处理Δx=0的合法竖直直线','此时方程x=x1仍定义直线，但不能得到有限斜率。')],
'点(2,1),(2,5)确定直线x=2，Δx=0，不允许k=4/0。',
'因竖直直线“无限陡”，把k写成∞并代入y=kx+b。',
'∞不是真实数斜率；改用x=2或一般式Ax+By+C=0。',
[E('求经过(1,2)和(3,6)的斜率、点斜式。',
  ['两点不同且Δx=3-1=2非零。','Δy=6-2=4，故k=4/2=2。','代入点(1,2)，得y-2=2(x-1)。'],
  '斜率2；直线y=2x。'),
 E('求过(0,3)和(2,3)直线的斜率、一般方程。',
  ['Δx=2非零、Δy=0。','所以k=0，直线水平。','代入过点关系，得y=3，即y-3=0。'],
  '斜率0；一般式y-3=0。')],
['先查看两个点是否相同。','再核对横坐标是否相同，避免除零。','若允许求斜率再代值；否则写直线的竖直方程。'],
'比较直线x=-1与y=-1的倾斜角及斜率。','在地图中用经纬度点求所谓斜率前，解释坐标系与经纬单位为何会影响方向判断。'),
L('120-s111','Concept',
'焦点F1,F2间距2c>0，若常数2a>2c，则满足PF1+PF2=2a的平面点集为非退化椭圆。中心放原点、焦点在x轴时x²/a²+y²/b²=1，其中b²=a²-c²>0。',
'a为长半轴、c为焦距的一半、b为短半轴；长轴方向决定标准方程分母位置。',
'两焦点不同、常数大于焦距；坐标轴与焦点方向一致；a>c>0。若c=0则为圆的特殊情况。',
[('用三角不等式核对非退化性','PF1+PF2≥F1F2=2c，若2a<2c无解；2a=2c时只有两焦点之间线段。'),
 ('选择正交坐标并写距离和','两焦点在(±c,0)，关系√((x+c)²+y²)+√((x−c)²+y²)=2a，且a>c。'),
 ( '利用平方差精确求两焦点距离','设r_+=√((x+c)²+y²)、r_-=√((x−c)²+y²)。由r_++r_-=2a、r_+²−r_-²=4cx得r_+−r_-=2cx/a，因此r_+=a+cx/a、r_-=a−cx/a，无需冒险平方增根。'),
 ('严格推导标准方程并作逆向回代','用r_+²=(a+cx/a)²同(x+c)²+y²比较，消去2cx后得(1−c²/a²)x²+y²=a²−c²，故x²/a²+y²/(a²−c²)=1。逆向若满足标准方程，则|x|≤a，因a>c保证a±cx/a>0，分别平方回代恢复两距离，和必为2a。'),
 ('核查焦点方向与参数','b²=a²−c²严格正，焦点在y轴时交换x与y的对应分母。')],
'若2a=2c，点集退化为两焦点间线段；若2a<2c为空集，不能继续写椭圆标准方程。',
'两焦点距离为4，距离和也是4，仍取b²=0画出椭圆。',
'先比大小而不是仅套公式；b²=0不满足非退化椭圆的定义。',
[E('焦点(-2,0),(2,0)，距离和6，求椭圆方程。',
  ['由焦点得c=2，距离和6得a=3>c。','b²=a²-c²=9-4=5>0。','焦点在x轴，写x²/9+y²/5=1。'],
  'x²/9+y²/5=1。'),
 E('焦点(0,-3),(0,3)，距离和10，求标准方程。',
  ['c=3，a=5；a>c。','b²=25-9=16。','焦点在y轴，长半轴分母25应落在y²下。'],
  'x²/16+y²/25=1。')],
['先检查距离和是否严格大于焦点距离。','计算a、c和b²，并标出焦点在哪条轴。','注意椭圆的长轴方向决定较大分母对应哪一个坐标。'],
'两个焦点(±4,0)、距离和10，求椭圆方程并检验顶点。','在定位系统中用两个基站到目标距离之和固定的轨迹，讨论测量误差如何改变椭圆边界。')
]
def req(v,msg):
    if not v:raise ValueError(msg)
def encode(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n'
PREREQUISITES={
  '121-c201':[],
  '122-c306':['122-c304','122-c305'],
  '122-c311':['121-c205','124-c509'],
  '123-c407':['124-c503','124-c504'],
  '123-c411':['121-c201','122-c312'],
  '120-s103':['121-c205','122-c308'],
  '120-s107':[],
  '120-s111':['120-s107','120-s109'],
}
def build():
    contexts,locks=source.build()
    cmap={r['candidate_id']:r for r in contexts['records']}
    docs=[]
    for t in LESSONS:
        k='hs-semantic-pilot-'+t['suffix'];src=cmap[k]
        docs.append({'id':'kb130-deep-'+t['suffix'],'candidate_id':k,'course_track':src['track'],
          'source_line_lock':locks[k],'source_pdf_sha256':src['source_pdf_sha256'],
          'version':'2017-2020-editorial-batch130',
          'prerequisite_candidate_ids':['hs-semantic-pilot-'+x for x in PREREQUISITES[t['suffix']]],
          'source_status':'EDITORIAL_ORIGINAL_LINE_CHECKED_NOT_OFFICIAL_ATOM',
          'objective':src['proposed_objective'],'knowledge_type':t['type'],
          'formal_definition_or_theorem':t['formal'],'notation_and_domain':t['notation'],
          'applicability_and_hypotheses':t['assumptions'],'reasoned_steps':[{'step':x,'justification':y} for x,y in t['reasoned_steps']],
          'nonexample_or_failure':t['nonexample_or_failure'],
          'typical_wrong_solution':t['typical_wrong_solution'],
          'why_wrong_and_repair':t['why_wrong_and_repair'],'teacher_examples':t['examples'],
          'student_hint_ladder':t['hints'],'near_transfer':t['near_transfer'],'far_transfer':t['far_transfer'],
          'teacher_review_status':'REVIEW_PENDING','teacher_review_evidence':None,
          'formal_proof_certified':False,'free_student_step_verified':False,
          'student_authoritative':False,'teacher_solution_visibility':'TEACHER_ONLY'})
    validate(docs,False)
    return docs
def validate(docs,regen=True):
    req(len(docs)==8 and len({d['candidate_id'] for d in docs})==8,'missing/duplicate teacher unit')
    known={'hs-semantic-pilot-'+k for k in source.R}
    for d in docs:
        suff=d['candidate_id'].removeprefix('hs-semantic-pilot-')
        deps=d.get('prerequisite_candidate_ids',[])
        req(deps==['hs-semantic-pilot-'+x for x in PREREQUISITES[suff]] and len(deps)==len(set(deps))
            and set(deps).issubset(known) and d['candidate_id'] not in deps,'orphan/cyclic/forged prerequisites')
        req(d['teacher_review_status']=='REVIEW_PENDING' and d['teacher_review_evidence'] is None and
            d['teacher_solution_visibility']=='TEACHER_ONLY' and d['student_authoritative'] is False and
            d['formal_proof_certified'] is False and d['free_student_step_verified'] is False,'forged teacher approval')
        req(len(d['reasoned_steps'])>=3 and len(d['teacher_examples'])==2 and len(d['student_hint_ladder'])==3
            and all(len(e['reasoned_solution'])>=3 for e in d['teacher_examples']),'truncated lesson')
        for k in ('formal_definition_or_theorem','notation_and_domain','applicability_and_hypotheses',
                  'nonexample_or_failure','typical_wrong_solution','why_wrong_and_repair','near_transfer','far_transfer'):
            req(len(d[k])>=20,'incomplete pedagogical field '+k)
    if regen:req(docs==build(),'deep content changed')
    return True
def exact_oracles():
    x,h=S.symbols('x h',real=True);R=S.Rational
    checks={
    '121-c201': [({1,3}&{2,3})=={3} and ({1,3}|{2,3})=={1,2,3},
                 (frozenset({1}) in {frozenset({1}),2}) and 1 not in {frozenset({1}),2}],
    '122-c306': [S.solveset(x*x-9,x,domain=S.S.Reals)==S.FiniteSet(-3,3),
                 S.solveset(S.Abs(x)-x,x,domain=S.S.Reals)==S.Interval(0,S.oo)],
    '122-c311': [1**3-1-1<0 and 2**3-2-1>0, 1**2-2<0 and 2**2-2>0],
    '123-c407': [S.simplify(S.log(8)/S.log(2)-3)==0,
                 S.simplify(S.log(16)/S.log(R(1,4))+2)==0],
    '123-c411': [R(len([(i,j) for i in range(1,7) for j in range(1,7) if i+j==7]),36)==R(1,6),
                 R(len([(i,j) for i in ('H','T') for j in ('H','T') if (i=='H')+(j=='H')==1]),4)==R(1,2)],
    '120-s103': [S.limit(((3+h)**2-9)/h,h,0)==6,
                 S.limit((1/(2+h)-R(1,2))/h,h,0)==-R(1,4)],
    '120-s107': [R(6-2,3-1)==2, R(3-3,2-0)==0],
    '120-s111': [3**2-2**2==5 and S.sqrt((3+2)**2)+S.sqrt((3-2)**2)==6,
                   5**2-3**2==16 and S.sqrt((5+3)**2)+S.sqrt((5-3)**2)==10]
    }
    negative={
    '121-c201':frozenset({1}) not in {1,2},
    '122-c306':(-3)**2==9 and -3!=3,
    '122-c311':S.simplify(1/x).subs(x,0)==S.zoo,
    '123-c407':S.log(1)==0,
    '123-c411':len([(i,j) for i in range(1,7) for j in range(1,7) if i+j==2])!=6,
    '120-s103':S.limit(S.Abs(h)/h,h,0,dir='+')!=S.limit(S.Abs(h)/h,h,0,dir='-'),
    '120-s107':2-2==0 and (5-1)!=0,
    '120-s111':S.sqrt((1+2)**2)+S.sqrt((1-2)**2)==4 and
            S.sqrt((0+2)**2+1)+S.sqrt((0-2)**2+1)>4
    }
    req(set(checks)==set(negative)=={s['suffix'] for s in LESSONS},'oracle coverage drift')
    req(all(len(a)==2 and all(bool(v) for v in a) for a in checks.values()),'worked example oracle failed')
    req(all(bool(v) for v in negative.values()),'boundary oracle failed')
    return {'batch':130,'independently_checked_teacher_examples':16,'boundary_counterexamples':8,
            'formal_general_theorems_certified':0,'free_student_steps_verified':0,'teacher_approved':0,
            'student_authoritative':0,'finite_cases_only':True,
            'example_results':{k:[bool(v) for v in a] for k,a in checks.items()},
            'counterexample_results':{k:bool(v) for k,v in negative.items()}}
def render(docs,checks):
    lines=['# Batch130 — eight complete original teacher-review mathematics manuscripts','',
        'All material remains REVIEW_PENDING / TEACHER_ONLY. The exact math examples are finite checks, not teacher approvals or formal theorem certificates.',
        f"Exact worked examples: {checks['independently_checked_teacher_examples']}; negative cases: {checks['boundary_counterexamples']}.",'' ]
    for d in docs:
        q=d['source_line_lock'];lines.extend([f"## {d['objective']} ({d['course_track']})",
           f"Original course context p.{q['page']} lines {q['start_line']}-{q['end_line']}; SOURCE NOT OFFICIAL ATOM",
           'Definition/theorem: '+d['formal_definition_or_theorem'],'Symbols and domain: '+d['notation_and_domain'],
           'All hypotheses: '+d['applicability_and_hypotheses'],
           'Editorial prerequisites (not teacher certified): '+(', '.join(d['prerequisite_candidate_ids']) or 'none: foundational'),
           '### Justified reasoning'])
        for j,z in enumerate(d['reasoned_steps'],1):lines.append(f"{j}. {z['step']} — {z['justification']}")
        lines.extend(['Failure/nonexample: '+d['nonexample_or_failure'],'Typical wrong solution: '+d['typical_wrong_solution'],
                      'Repair: '+d['why_wrong_and_repair'],'### Verified teacher-only worked examples'])
        for e in d['teacher_examples']:
            lines.append('**Question:** '+e['question'])
            for i,s in enumerate(e['reasoned_solution'],1):lines.append(f"{i}. {s}")
            lines.append('**Teacher-side answer (not for autonomous student challenge):** '+e['answer'])
        lines.append('### Student hints: gradual, answer-free')
        lines.extend([f"{i}. {h}" for i,h in enumerate(d['student_hint_ladder'],1)])
        lines.extend(['Near transfer: '+d['near_transfer'],'Far transfer: '+d['far_transfer'],''])
    return '\n'.join(lines).rstrip()+'\n'
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args()
    d=build();o=exact_oracles()
    for f,t in [(OUT,encode(d)),(ORACLE,encode(o)),(REPORT,render(d,o))]:
        if a.write:f.parent.mkdir(parents=True,exist_ok=True);f.write_text(t,encoding='utf-8')
        else:req(f.exists() and f.read_text(encoding='utf-8')==t,'manuscript/oracle drift '+str(f))
    print('Batch130: eight teacher manuscripts, sixteen independent exact worked examples, eight negative checks')
if __name__=='__main__':main()
