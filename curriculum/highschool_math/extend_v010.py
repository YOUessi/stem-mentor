"""v0.10 fixed mathematical presets and explicit, partial curriculum evidence."""
from copy import deepcopy


def param(key,label,lo,hi,value,step=.1):
    return dict(key=key,label=label,min=lo,max=hi,value=value,step=step)


def choice(key,label,labels,default=0,start=0):
    values=[{'value':i+start,'label':text} for i,text in enumerate(labels)]
    return dict(key=key,label=label,min=start,max=start+len(values)-1,
                value=default,step=1,options=values)


def extra_presets():
    z=[param('re','z 的实部 Re z',-5,5,3),param('im','z 的虚部 Im z',-5,5,2)]
    w=[param('wr','w 的实部 Re w',-5,5,1),param('wi','w 的虚部 Im w',-5,5,-1)]
    def ends(prefix='',lo=-2,hi=3):
        return [param(prefix+'lo','区间'+prefix+'左端点',-8,8,lo),
                choice(prefix+'lc','左端点类型',['开端点','闭端点','负无穷'],1),
                param(prefix+'hi','区间'+prefix+'右端点',-8,8,hi),
                choice(prefix+'rc','右端点类型',['开端点','闭端点','正无穷'],1)]
    relation=choice('relation','比较关系',['< 0','≤ 0','> 0','≥ 0'],1)
    probe=param('probe','数轴探针 x',-10,10,0)
    definitions=[
      ('complex-point','complex_plane','复数点、模、辐角与共轭',r'z=a+bi,\quad |z|=\sqrt{a^2+b^2}',z,
       '拖动复数点或使用方向键。主辐角以 atan2 表示；零复数辐角未定义，共轭点可主动显示。'),
      ('complex-operations','complex_plane','复数的加减乘除',r'z\circ w,\quad z,w\in\mathbb C',z+w+[
        choice('op','复数运算',['z + w','z − w','z × w','z ÷ w'])],
       '先观察两个输入复数，预测结果所在位置，再打开结果核对；除数精确为零时除法未定义。'),
      ('complex-rotation','complex_plane','复数的旋转与伸缩',r'z\mapsto\rho(\cos\theta+i\sin\theta)z',z+[
        param('theta','旋转角 θ（度）',-720,720,90,1),param('rho','缩放比例 ρ',0,3,1)],
       '以原点为旋转中心，支持负角与多圈；比例为零时坍缩到原点，不能据此赋予辐角。'),
      ('sets-operations','venn_logic','有限集合：交、并、差与对称差',r'A,B\subseteq U',[
        param('n','全集 U 的元素个数',1,12,8,1),choice('op','集合运算',['A ∪ B','A ∩ B','A ∖ B','A △ B'])],
       '在成员表中编辑 A、B。四块区域按实际成员排列，不以圆面积代表元素个数；结果需主动显示。'),
      ('sets-complement','venn_logic','补集与德摩根关系',r'C_U(A\cup B)=C_UA\cap C_UB',[
        param('n','全集 U 的元素个数',1,12,8,1),
        choice('op','相对于 U 的补集',['Cᵤ A','Cᵤ(A ∪ B)','Cᵤ(A ∩ B)'],4,start=4)],
       '补集永远相对于明确的有限全集 U；缩小全集会移除越界成员，不以屏幕外空间当全集。'),
      ('interval-single','number_line','实数区间：开闭端点与无穷射线',r'x\in I',ends()+[probe],
       '空心点排除端点，实心点包含端点。逆序为空；同端点只有两边都闭才是单点；无穷永不闭合。'),
      ('interval-operations','number_line','区间的交、并、差与补集',r'A,B\subseteq\mathbb R',ends('a',-3,1)+ends('b',1,4)+[
        choice('op','区间运算',['A ∩ B','A ∪ B','A ∖ B','ℝ ∖ A']),probe],
       '输入区间始终可见；主动显示运算结果。补集相对整条实数轴，不是当前图形显示窗口。'),
      ('ineq-linear','number_line','一元一次不等式与方向',r'ax+b\;\square\;0',[
        param('a','一次系数 a',-4,4,2),param('b','常数项 b',-6,6,-2),relation,probe],
       '先预测解集朝向，再显示数轴核对；负系数需翻向，a=0 退化为常值真假判断。'),
      ('ineq-quadratic','number_line','一元二次不等式及退化情况',r'ax^2+bx+c\;\square\;0',[
        param('a','二次系数 a',-4,4,1),param('b','一次系数 b',-6,6,0),
        param('c','常数项 c',-6,6,-1),relation,probe],
       '区分两个实根、重根、无实根和退化为一次/常值；结果为解集而不是一张可能断裂的抛物线。'),
      ('ineq-absolute','number_line','绝对值不等式与距离',r'|x-h|\;\square\;r',[
        param('h','中心 h',-5,5,0),param('r','右侧数 r（允许负数）',-3,5,2),
        choice('relation','比较关系',['< r','≤ r','> r','≥ r'],1),probe],
       '先把绝对值看成数轴距离；r<0 与 r=0 必须单独讨论，区分空集、单点和整条实数轴。')
    ]
    return [dict(id=id,tool=tool,title=title,equation=id,latex=latex,params=deepcopy(params),
            description=desc,source='PROJECT_AUTHORED',expert_review='PENDING',
            simulation=True,assist_default=False)
            for id,tool,title,latex,params,desc in definitions]


EVIDENCE={
 '复数与复平面':['complex-point','complex-operations'],
 '复数模与辐角':['complex-point','complex-rotation'],
 '复数加减乘除及几何意义':['complex-operations','complex-rotation'],
 '集合及其表示':['sets-operations','interval-single'],
 '交集并集补集':['sets-complement','sets-operations','interval-operations'],
 '等式性质与不等式性质':['ineq-linear'],
 '一元二次不等式':['ineq-quadratic'],
 '含参数不等式':['ineq-linear','ineq-quadratic','ineq-absolute'],
 '不等式等价变换和定义域':['ineq-linear','interval-single']
}
LIMITS={
 '复数与复平面':'仅有限坐标的复平面和基本运算；非任意复方程求解或证明。',
 '复数模与辐角':'提供主辐角与多圈旋转观察；零复数没有辐角，不等于复分析课程。',
 '复数加减乘除及几何意义':'数值四则与旋转伸缩；不存在自动生成推导或学生掌握判定。',
 '集合及其表示':'有限全集成员表及固定实区间；任意集合描述语言与无限集合逻辑未实现。',
 '交集并集补集':'有限集合与实区间交并差补；通用谓词逻辑推理未实现。',
 '等式性质与不等式性质':'只观察一次不等式系数符号与方向；一般等式变换证明未实现。',
 '一元二次不等式':'固定二次多项式的数值解集与边界；没有任意表达式解析或证明。',
 '含参数不等式':'仅固定一次、二次、绝对值数值参数探索；通用符号参数分类与高阶不等式未实现。',
 '不等式等价变换和定义域':'数轴区间及负系数翻向；复杂分式/指数/对数不等式等价变换未实现。'
}


def apply_coverage(rows,presets):
    known={p['id']:p for p in presets}
    for row in rows:
        ids=EVIDENCE.get(row['concept'])
        if ids is None:continue
        if not all(id in known for id in ids):raise ValueError('Missing v0.10 evidence')
        row.update(available_presets=list(ids),status='INTERACTIVE_FOUNDATION',
                   capability='可打开具体受控数学场景',capability_limits=LIMITS[row['concept']],
                   recommended_tool=known[ids[0]]['tool'])
    return rows
