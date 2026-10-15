"""Generate project-authored, unreviewed v0.5 curriculum examples. Idempotent."""
from __future__ import annotations
import json
from pprint import pformat
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CARDS=ROOT/"knowledge/corpus/methods.json"
GRAPHS=ROOT/"knowledge/reasoning_graphs.json"
CATALOG=ROOT/"backend/app/catalog.py"

# id, title, subject, aliases, method_ids, structures, required, prereqs, explanation, boundary, first hint
ITEMS=[
("method-angle-bisector","角平分线定理：内分线段比例","高中数学·平面几何",["内角平分线","分线段成比例"],["angle_bisector"],["triangle","angle_bisector","side_ratio"],["triangle","angle_bisector"],["相似三角形"],"三角形内角平分线与对边交点，把对边分成与邻边成比例的两段。适合将角条件转换为线段比例。","只适用于明确的内角平分线与对应边；外角平分线需单独处理。","题目中的角等分条件，能不能转成某种线段比例？"),
("method-sine-area","两边与夹角求三角形面积","高中数学·解三角形",["面积 1/2 ab sinC","正弦面积公式"],["triangle_area_sine"],["triangle","sas_case","area_target"],["triangle","sas_case"],["三角形面积","正弦函数"],"已知两边与其夹角时，可将一边作底，另一边乘夹角正弦作高，从而求面积；关键是必须知道两边的夹角。","给定不是夹角时不得直接将其代入；角值对应关系需要核对。","你能利用其中一边与夹角写出高吗？"),
("method-sine-rule","正弦定理：边角关系与隐含多解","高中数学·解三角形",["正弦定理","外接圆半径","SSA二解"],["sine_rule"],["triangle","side_angle_pair"],["triangle"],["三角形内角和"],"对非退化三角形，有 a/sin A=b/sin B=c/sin C=2R。SSA 条件中单看一个正弦值不能保证角唯一。","分母正弦不得为零；SSA 的第二个候选角需检查内角和。","你掌握的是一组对边角关系，还是相邻边夹角关系？"),
("method-cosine-rule","余弦定理：两边夹角或三边","高中数学·解三角形",["余弦定理","三边求角","SAS","SSS"],["cosine_law"],["triangle","sss_case"],["triangle"],["向量数量积"],"三边已知时，可由余弦定理求一个角；两边及夹角已知时，可求第三边。在平面非退化三角形中，SSS 确定形状。","必须检验三角形不等式；不要将 SSA 多解问题与 SSS 混淆。","现有条件是三条边，还是两边和一个夹角？"),
("method-median-theorem","中线长与阿波罗尼斯中线定理","高中数学·平面几何",["中线长公式","中线定理","阿波罗尼斯定理"],["median_theorem"],["triangle","median","side_lengths"],["triangle","median"],["勾股定理","向量法"],"三角形中，顶点到对边中点的中线长度满足 2(b²+c²)=a²+4m²，其中 a 为对边长，b、c 为另外两边。","此定理是中线长度关系，并非阿波罗尼斯圆的定距离比轨迹。","若出现中点及三边平方，能否用中线关系连接它们？"),
("method-locus-midpoint","中点轨迹：仿射映射","高中数学·解析几何",["中点坐标公式","中点轨迹"],["midpoint_locus"],["midpoint","locus","affine_relation"],["midpoint","locus"],["坐标变换"],"若定点 A 和动点 P 的中点 M 是研究对象，则 M=(A+P)/2；可以把 P 的约束变换为 M 的轨迹。","A 必须是定点；映射与坐标比例须一致。","能否从中点坐标反过来表示动点？"),
("method-parabola-tangent","抛物线切线：隐式微分与条件","高中数学·圆锥曲线",["抛物线切线","y²=4px"],["parabola_tangent","implicit_derivative"],["quadratic_curve","parabola","point_on_curve","tangent_at_point"],["parabola","point_on_curve","tangent_at_point"],["隐式求导"],"对非退化抛物线 y²=4px，曲线上 (x0,y0) 处切线由 yy0=2p(x+x0) 给出，且需要检查 p≠0。","非曲线上点、p=0 的退化情况不可直接套用。","曲线和切点已知时，能否从隐式导数得到局部线性关系？"),
("method-derivative-monotonicity","用导数符号研究单调区间","高中数学·函数与导数",["单调性","导数符号表"],["derivative_sign"],["function","derivative","monotonicity"],["function","derivative"],["导数定义","不等式"],"在适当的连续和可导条件下，分析导数正负即可判定区间上的单调性，需正确划分临界点与定义域。","区间端点与不可导点需单独考虑；不能仅凭某一点的导数符号判定整个区间。","你要研究的是函数值还是变化方向？导数符号能帮你回答什么？"),
("method-interval-extrema","闭区间最值：驻点与端点都要检查","高中数学·函数与导数",["闭区间最值","端点最值","导数极值"],["interval_extrema"],["function","closed_interval","extrema"],["function","closed_interval","extrema"],["单调性","端点"],"连续函数在闭区间上的最大最小值，须比较区间内候选驻点、不可导点和两端点的函数值。","不可将局部驻点直接认作全局最值；闭区间连续性是必要背景。","最值是否一定出现在导数为零的地方？区间端点呢？"),
("method-log-domain","对数真数与定义域","高中数学·函数",["对数真数大于零","log定义域"],["log_domain"],["log_expression","log_argument_positive"],["log_expression"],["实数范围内的对数"],"实数对数 log_a(f(x)) 必须满足 f(x)>0，底数 a>0 且 a≠1，先确定定义域再执行等价变形。","真数=0 或真数<0 时实数对数无定义；变形可能引入伪根。","对数表达式出现时，第一件该检查的限制是什么？"),
("method-log-base","对数底数的合法条件","高中数学·函数",["底数不为1","对数底数限制"],["log_base"],["log_expression","log_base_condition"],["log_expression"],["指数函数"],"实数对数的底数满足 a>0 且 a≠1；底数变化要注意对数函数单调性方向。","底数在 0 与 1 之间时对数函数递减；a=1 不合法。","你检查了真数，那么底数有哪些不可忽略的限制？"),
("method-arithmetic-series","等差数列求和与平均数思想","高中数学·数列",["等差数列前n项和","首末项平均"],["arithmetic_series"],["arithmetic_sequence","sum_n_terms"],["arithmetic_sequence","sum_n_terms"],["等差数列通项"],"等差数列的前 n 项和等于项数乘首末项平均：S_n=n(a1+an)/2；亦可由错位配对得到。","项数 n 是正整数；不能把等比求和的公比特例混用。","把数列正着与倒着相加，会不会出现同一个和？"),
("method-induction","数学归纳法：起点与归纳步骤","高中数学·数列与证明",["归纳法","n到n+1"],["induction"],["integer_parameter","prove_all_n"],["integer_parameter","prove_all_n"],["命题逻辑"],"证明对所有正整数 n 成立的命题，先验证初始情形，再假设某个 n 成立并证明 n+1 的情形。","只验证有限多个例子不是证明；归纳假设不可偷换对象。","你要证明的是某一个 n 还是所有正整数 n？"),
("method-cauchy","柯西不等式与等号条件","高中数学·不等式",["柯西施瓦茨","Cauchy-Schwarz"],["cauchy"],["vector_or_sum","square_bound"],["vector_or_sum"],["平方非负"],"柯西–施瓦茨不等式将平方和与内积平方联系起来，可用于估计和式或向量夹角。","使用前核对项对应和等号条件；并非出现平方就一定最优。","目标中有没有平方和与乘积的结构？"),
("method-vector-dot","向量数量积判断垂直","高中数学·平面向量",["向量垂直","点积为零"],["dot_product"],["vectors","orthogonality"],["vectors","orthogonality"],["向量坐标"],"对两个非零向量，垂直当且仅当数量积为零；可从角度或坐标两种途径理解。","零向量的方向角未定义，不能从零数量积盲推两非零向量夹角。","向量垂直对应哪种代数关系？"),
("strategy-reverse-subgoal","逆向分解目标：构造中间命题","通用数学思维",["逆向思考","目标拆解","目标桥梁"],["backward_goal"],["target","subgoal"],[],["充分条件与必要条件"],"正推受阻时，先研究结论成立的充分条件，形成一个可验证的中间目标，再用已有条件寻找桥梁。","由结论推出的必要条件不等于能证明原结论；需辨别推理方向。","如果想要目标成立，你可以先完成哪个较小的结论？"),
("strategy-counterexample","反例检验：区分猜想与定理","通用数学思维",["反例","边界例子","不能套公式"],["counterexample"],["conjecture","boundary_check"],[],["反证法"],"提出方法猜想后，测试定义域、等号、特殊参数和极端情形，用反例修正适用条件。","反例用于否定全称命题，不代替对正确命题的普遍证明。","有没有一种退化或边界情况，可以快速检验你的猜想？"),
("method-ssa-branch","SSA 不唯一：角的两个候选","高中数学·解三角形",["已知两边一角","SSA不同解"],["sine_rule","case_split"],["triangle","ssa_case","multiple_solutions"],["triangle","ssa_case"],["正弦定理"],"由正弦定理得到一个角的正弦后，满足内角和的锐角/钝角两个候选都要检查；SSA 有可能出现 0、1 或 2 个有效解。","不能把 SSA 误当 SSS；每个角候选都应检查其他角为正。","已求出的 sinB，是否总能唯一确定角 B？")
]
def build_card(t):
    card_id,title,subject,aliases,methods,structures,requires,pre,content,boundary,hint=t
    if len(content) <= 45: content += ' 使用前要核对所需条件，并解释这些条件与目标之间的联系。'
    return {'id':card_id,'kind':'strategy' if card_id.startswith('strategy') else 'method',
      'title':title,'subject':subject,'aliases':aliases,'methods':methods,'structures':structures,
      'requires':requires,'prerequisites':pre,'content':content,'boundary':boundary,'hint':hint,
      'source':{'kind':'ORIGINAL_AUTHORING','reference':'STEM Mentor 自编数学教学材料 v0.5',
       'permission':'PROJECT_AUTHORED','expert_review':'PENDING'},'version':'2026-10-15.2'}

def problem(id,title,subject,prompt,goal,known,methods,structures,analysis,guide,micro):
    return {'id':id,'title':title,'subject':subject,'prompt':prompt,'goal':goal,'known':known,
     'method_tags':methods,'structure_tags':structures,'analysis':analysis,'guide':guide,'micro_point_id':micro}
P=[
problem('triangle-sas','两边夹角求三角形面积','高中数学 · 解三角形',
 '已知三角形 AB=5、AC=8、∠A=60°，求面积；思考为什么题目强调夹角。',
 '根据条件选取面积模型',['AB=5','AC=8','∠A 为夹角'],
 ['triangle_area_sine'],['triangle','sas_case','area_target'],
 ['已知的两边和哪个角具有对应关系？','你要的是面积还是边长？','有哪些表示高的方式？'],
 ['你能从一边作底，另一边作高吗？','如果正推受阻，反问面积公式里缺少的是哪个量？','尝试连接已知角与高。'],'triangle-included-angle'),
problem('triangle-ssa','正弦定理中的 SSA 多解','高中数学 · 解三角形',
 '在三角形 ABC 中，a=8、b=10、A=30°，讨论满足条件的三角形可能有几个。',
 '检查由 SSA 条件带来的多解性',['已知两边 a、b','已知 a 的对角 A','没有给出夹角'],
 ['sine_rule','case_split'],['triangle','ssa_case','multiple_solutions'],
 ['已知的是 SAS、SSS 还是 SSA？','正弦定理给出一个角的正弦值后，角是否唯一？','另一个可能的角满足内角和吗？'],
 ['先列出所需边角比例关系。','卡住时从目标反推：要判定解数，需要检查哪些角候选？','只需验证每个候选角的合法性，数值计算留给你。'],'ssa-angle-ambiguity'),
problem('triangle-sss','三边确定三角形','高中数学 · 解三角形',
 '在三角形 ABC 中给出三边长度 5、6、7，讨论是否存在三角形，以及如何求夹角。',
 '检查三角形不等式并选择求角方法',['三边长度已知','无角度给出'],
 ['cosine_law'],['triangle','sss_case','unique_triangle'],
 ['这与 SSA 条件有什么根本不同？','三边先满足什么存在条件？','哪种定理可以由三边求一个角？'],
 ['先检查三角形不等式。','要求一个角，应该把哪个角看成目标变量？','自己写出余弦关系并检查范围。'],'triangle-validity'),
problem('parabola-tangent','抛物线曲线上一点的切线','高中数学 · 圆锥曲线',
 '对抛物线 y²=4x，在曲线上点 (1,2) 处求切线。',
 '利用曲线上一点和隐式导数分析切线',['y²=4x','切点 (1,2) 在曲线上'],
 ['parabola_tangent','implicit_derivative'],['quadratic_curve','parabola','point_on_curve','tangent_at_point'],
 ['题目给了切点，它满足什么约束？','切线描述局部什么关系？','这与椭圆切线题的相似处在哪里？'],
 ['先核对切点在曲线上。','从切线目标反推，需要知道这个点处的哪种局部信息？','你能用隐式求导或局部线性化自己完成吗？'],'conic-point-valid'),
problem('derivative-extrema','闭区间函数最值','高中数学 · 函数与导数',
 '求 f(x)=x³−3x 在闭区间 [-2,2] 上的最大值与最小值。',
 '比较所有候选驻点与端点',['f(x)=x³−3x','区间 [-2,2] 是闭区间'],
 ['derivative_sign','interval_extrema'],['function','derivative','closed_interval','extrema'],
 ['最大最小值与局部极值有什么区别？','闭区间有哪几类候选点？','导数能提供什么信息？'],
 ['先找可能的内部候选点。','从最值目标倒推，还缺少哪些点的函数值？','请独立比较端点与内部候选点。'],'closed-interval-endpoints'),
problem('log-domain','含对数方程的定义域','高中数学 · 函数',
 '求解 log₂(x−1)=1 时，先讨论 x 的合法范围。',
 '先限定定义域，再进行等价运算',['底数为 2','真数为 x−1'],
 ['log_domain','log_base'],['log_expression','log_argument_positive','log_base_condition'],
 ['为什么对数方程不能立即两边指数化？','真数满足什么条件？','底数是否还有限制？'],
 ['先确定使对数有定义的 x 范围。','逆向看：代回原方程需要满足哪些条件？','自己求解并验根。'],'log-positive-argument'),
problem('arithmetic-sum','等差数列前 n 项和','高中数学 · 数列',
 '首项为 2、公差为 3 的等差数列，求前 n 项和，n 为正整数。',
 '从首末项配对建立求和思想',['首项=2','公差=3','n 为正整数'],
 ['arithmetic_series'],['arithmetic_sequence','sum_n_terms'],
 ['条件中的公差意味着什么？','如何写出末项？','可否把首末两项配对？'],
 ['先列出第一项和最后一项。','从目标反推，你需要首末项的什么关系？','运用配对并自己化简。'],'arithmetic-n-positive'),
problem('median-length','三角形中线长','高中数学 · 平面几何',
 '在三角形 ABC 中，M 是 BC 中点，已知三边长，讨论如何求中线 AM。',
 '从中点结构寻找平方关系',['M 为 BC 中点','三边长可用于平方关系'],
 ['median_theorem'],['triangle','median','side_lengths'],
 ['题目特意给了中点，意味着什么？','中线长可以用什么量表达？','有没有熟悉的平方关系？'],
 ['试着设向量或投影得到中线关系。','从 AM 反推，哪两个已知边的平方可以连接它？','解释中点为什么重要。'],'median-not-circle'),
problem('vector-orthogonality','向量数量积与垂直','高中数学 · 平面向量',
 '已知向量 a=(1,2)、b=(2,-1)，判断它们是否垂直，并解释使用条件。',
 '认识坐标数量积与几何垂直的关系',['给出两个平面向量坐标'],
 ['dot_product'],['vectors','orthogonality'],
 ['向量正交的几何含义是什么？','坐标下如何表达数量积？','零向量出现时有什么边界？'],
 ['先列出数量积。','从垂直目标反推，需要满足哪个标量条件？','确认两向量非零后自己判定。'],'nonzero-vector')
]
MICRO={
 'triangle-included-angle': ('夹角与正弦面积公式','在 S=ab sinθ/2 中，θ 应当是两边的什么角？',['夹角']),
 'ssa-angle-ambiguity':('反正弦值不保证唯一角','三角形 SSA 解题时，已求 sinB 后是否一定唯一确定角 B？',['不一定','可能两个','有两解']),
 'triangle-validity':('三角形三边存在条件','三条边长度能构成三角形时，最长边与其余两边要满足什么关系？',['小于','三角不等式']),
 'closed-interval-endpoints':('闭区间最值别漏端点','函数在闭区间求最大最小值时，除了区间内驻点还必须比较哪里？',['端点','两端']),
 'log-positive-argument':('实数对数真数限制','实数对数 log_a(f(x)) 的真数必须满足什么条件？',['大于0','>0','正数']),
 'arithmetic-n-positive':('项数 n 的取值','求前 n 项和时，n 作为项数通常取什么集合？',['正整数','大于0的整数']),
 'median-not-circle':('中线定理与阿波罗尼斯圆有别','“中线定理”是否等于“到两定点距离比不变的圆”？',['不是','不等于','不同']),
 'nonzero-vector':('垂直定义与零向量','数量积为 0 推出夹角为 90° 时，对向量的长度有什么要求？',['非零','不是零'])
}
def make_graph(p):
    n=[{'id':'given','role':'GIVEN','statement':'；'.join(p['known']),
        'verification':'GIVEN_BY_PROBLEM','teacher_only':False},
       {'id':'goal','role':'GOAL','statement':p['goal'],
        'verification':'TASK_TARGET','teacher_only':False}]
    for name,desc in [('forward','可基于题目已知条件做正向探索'),
       ('backward','从目标寻找充分的中间条件，非已证关系'),
       ('bridge','尝试连接正推关系与逆向子目标'),
       ('boundary','方法使用前核对特殊条件与定义域')]:
        n.append({'id':name,'role':name.upper(),'statement':desc,
                  'verification':'SCAFFOLD_UNVERIFIED','teacher_only':True})
    edges=[{'source':a,'target':b,'relation':relation,'verified':False} for a,b,relation in [
      ('given','forward','POSSIBLE_DERIVATION'),('goal','backward','BACKWARD_SEARCH_NOT_PROOF'),
      ('forward','bridge','MAY_SUPPORT'),('backward','bridge','MAY_SUPPORT'),
      ('bridge','goal','PROOF_OBLIGATION'),('boundary','bridge','CONSTRAINS_APPLICATION')]]
    return {'problem_id':p['id'],'version':'2026-10-15.2','nodes':n,'edges':edges,
       'guidance':{'START':p['analysis'][0],'FORWARD':p['guide'][0],
         'STUCK':p['guide'][1],'BACKWARD':'已从目标分析所需条件，如何和已知的关系建立连接？',
         'BRIDGE':'你想到的连接真的成立吗？请先检验条件和方向。',
         'CALCULATION':'剩余计算请先自己完成，核对定义域和特殊值。'},'checks':[]}

def run():
    orig=json.loads(CARDS.read_text(encoding='utf8'))
    by_id={x['id']:x for x in orig}
    for t in ITEMS:by_id[t[0]]=build_card(t)
    CARDS.write_text(json.dumps(list(by_id.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    graphs=json.loads(GRAPHS.read_text(encoding='utf8'))
    for p in P:graphs[p['id']]=make_graph(p)
    GRAPHS.write_text(json.dumps(graphs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    script="# Project-authored v0.5 curriculum extension, generated by knowledge/build_v05.py\nPROBLEMS.update("+pformat({p['id']:p for p in P},width=96,sort_dicts=False)+")\nMICRO_POINTS.update("+pformat({k:{'id':k,'title':v[0],'topic':k,'question':v[1],'answer_hint':'请用概念和完整条件表述，避免只背关键词。','acceptable':v[2]} for k,v in MICRO.items()},width=96,sort_dicts=False)+")\n"
    txt=CATALOG.read_text(encoding='utf8')
    marker='# Project-authored v0.5 curriculum extension'
    if marker in txt:txt=txt[:txt.index(marker)].rstrip()+'\n\n'
    CATALOG.write_text(txt+'\n'+script,encoding='utf8')
    print('Corpus',len(by_id),'graphs',len(graphs),'new problems',len(P),'micro',len(MICRO))
if __name__=='__main__':run()
