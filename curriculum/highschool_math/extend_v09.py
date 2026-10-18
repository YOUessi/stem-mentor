"""v0.9 authored presets and auditable, scene-level curriculum coverage."""

def param(key,label,lo,hi,value,step=.1):
    return dict(key=key,label=label,min=lo,max=hi,value=value,step=step)

def extra_presets():
    vector=[param('ax','a 的 x 坐标',-3.5,3.5,2),param('ay','a 的 y 坐标',-3.5,3.5,1),
            param('bx','b 的 x 坐标',-3.5,3.5,-1),param('by','b 的 y 坐标',-3.5,3.5,2),
            param('k','数乘系数 k',-2,2,1)]
    normal=[param('nx','平面法向量 n_x',-2,2,0),param('ny','平面法向量 n_y',-2,2,0),
            param('nz','平面法向量 n_z',-2,2,1),param('t','平面位置 t',-6,12,2)]
    definitions=[
        ('vec2d-add','vector_2d','平面向量：加减与数乘',r'\vec a+\vec b,\quad k\vec a',vector,
         '拖动两个向量的端点；自主打开合向量和平行四边形，检验自己的猜想。'),
        ('vec2d-projection','vector_2d','平面向量：数量积与投影',r'\operatorname{proj}_{\vec b}\vec a=\frac{\vec a\cdot\vec b}{|\vec b|^2}\vec b',vector[:-1],
         '投影到非零向量；零向量夹角与投影方向未定义，不能盲套公式。'),
        ('unit-circle','function_2d','单位圆：弧度、象限与三角函数',r'P(\cos\theta,\sin\theta),\quad x^2+y^2=1',
         [param('theta','角度 θ（度，包含多圈与负角）',-720,720,35,1)],
         '拖动单位圆上 P 点，观察角度与弧度、正弦余弦联动；90/270 度的正切无定义。'),
        ('derivative-quadratic','function_2d','动态导数：二次函数割线到切线',r'f(x)=x^2',
         [param('x','基点 x',-2,2,.7,.05),param('h','增量 h（可正可负）',-1.5,1.5,.8,.01)],
         '逐渐缩小非零 h，比较差商与解析导数；h=0 时割线本身未定义。'),
        ('derivative-cubic','function_2d','动态导数：三次函数与驻点',r'f(x)=x^3-3x',
         [param('x','基点 x',-2,2,.5,.05),param('h','增量 h',-1.5,1.5,.5,.01)],
         '割线斜率与解析切线斜率分别显示；驻点的导数为零不自动意味着最大值。'),
        ('derivative-log','function_2d','动态导数：对数函数与定义域',r'f(x)=\ln x,\quad x>0',
         [param('x','基点 x（严格大于零）',.1,3,1,.05),param('h','增量 h',-1.5,1.5,.5,.01)],
         'x+h 也必须为正，跨出定义域时不画错误割线。'),
        ('derivative-abs','function_2d','动态导数：绝对值函数不可导点',r'f(x)=|x|',
         [param('x','基点 x',-2,2,0,.05),param('h','增量 h（检查左右）',-1.5,1.5,.5,.01)],
         '在 x=0 比较左右差商；折点不可导，不展示虚假的唯一切线。'),
        ('3d-section-prism','space_3d','空间截面：平面切长方体',r'n_xx+n_yy+n_zz=t',normal,
         '长方体 x,y∈[-2,2]、z∈[0,4]；逐边计算交点，可出现三至六边形、线段、点或无交。'),
        ('3d-section-pyramid','space_3d','空间截面：平面切四棱锥',r'n_xx+n_yy+n_zz=t',normal,
         '底面为 [-2,2]²、高4；改变平面倾角与高度观察实际截面，贴合底面、过顶点需单独判定。'),
        ('3d-section-sphere','space_3d','空间截面：球与平面的交集',r'x^2+y^2+z^2=R^2,\quad \vec n\cdot\vec x=t',
         [param('r','球半径 R',.5,3,2)]+[param('nx','n_x',-2,2,0),param('ny','n_y',-2,2,0),param('nz','n_z',-2,2,1),param('t','平面位置 t',-6,6,1)],
         '交集可能为圆、相切点或空集；零法向量不是合法平面。')
    ]
    return [dict(id=id,tool=tool,title=title,equation=id,latex=latex,params=ps,description=desc,
        source='PROJECT_AUTHORED',expert_review='PENDING',simulation=True,assist_default=False)
        for id,tool,title,latex,ps,desc in definitions]

# Explicit scene IDs: no speculative promotion just because a general plotter exists.
EVIDENCE={
 '函数映射和定义域':['fn-log','fn-sqrt','fn-inverse'],
 '函数值域':['fn-quadratic','fn-sin'],
 '单调性':['fn-exp','fn-log','derivative-cubic'],
 '奇偶性':['fn-abs','fn-cos','fn-sin'],
 '周期性':['unit-circle','fn-sin','fn-cos'],
 '零点与方程':['fn-quadratic','fn-cubic'],
 '分段函数':['fn-piecewise'],
 '一次函数':['fn-linear'],'二次函数':['fn-quadratic'],
 '幂函数':['fn-quadratic','fn-sqrt'],
 '指数函数':['fn-exp'],'对数函数':['fn-log'],
 '绝对值函数':['fn-abs','derivative-abs'],
 '函数变换与复合':['fn-quadratic','fn-sin'],
 '弧度制和单位圆':['unit-circle'],
 '正弦余弦函数图像':['fn-sin','fn-cos','unit-circle'],
 '正切函数':['fn-tan','unit-circle'],
 '诱导公式':['unit-circle'],
 '三角函数图像变换':['fn-sin','fn-cos'],
 '平面向量的表示':['vec2d-add'],
 '向量加减与数乘':['vec2d-add'],
 '向量数量积':['vec2d-projection'],
 '向量投影与夹角':['vec2d-projection'],
 '正弦定理':['tri-free','tri-ssa'],'余弦定理':['tri-free'],
 'SSA 二解与三角形存在性':['tri-ssa'],'三角形面积与几何关系':['tri-free','tri-right'],
 '空间点线面位置关系':['3d-point','3d-plane','3d-section-prism'],
 '棱柱棱锥与棱台':['3d-prism','3d-pyramid'],
 '圆柱圆锥球':['3d-cylinder','3d-cone','3d-sphere'],
 '表面积与体积':['3d-prism','3d-pyramid','3d-sphere'],
 '空间截面与展开图':['3d-section-prism','3d-section-pyramid','3d-section-sphere'],
 '导数的几何意义':['derivative-quadratic','derivative-cubic'],
 '导数与切线':['derivative-quadratic','derivative-log','derivative-abs'],
 '导数判断单调性':['derivative-cubic'],
 '极值与最值':['derivative-cubic','fn-quadratic'],
 '函数零点和参数讨论':['fn-quadratic','fn-cubic'],
 '空间直角坐标系':['3d-point'],
 '空间向量与坐标运算':['3d-vectors'],
 '空间向量数量积':['3d-vectors'],
 '直线方向向量':['3d-vectors'],
 '平面法向量':['3d-plane','3d-section-prism'],
 '空间多面体与投影':['3d-prism','3d-pyramid','3d-point'],
 '倾斜角与直线斜率':['conic-line'],
 '直线方程':['conic-line'],'直线与圆的位置关系':['conic-intersection'],
 '椭圆定义及几何性质':['conic-ellipse'],
 '双曲线定义及几何性质':['conic-hyperbola'],
 '抛物线定义及几何性质':['conic-parabola'],
 '圆锥曲线焦点与准线':['conic-ellipse','conic-hyperbola','conic-parabola']
}
LIMITS={
 '圆锥曲线焦点与准线':'可显示椭圆和双曲线焦点、抛物线焦点和准线；其他准线尚未实现。',
 '诱导公式':'通过终边、负角和多圈角观察符号变化；尚无专门证明与推导。',
 '函数映射和定义域':'提供实数函数定义域观察；集合间映射箭头图尚未实现。',
 '空间截面与展开图':'已实现凸多面体和球的平面截面；展开图未实现。',
 '函数变换与复合':'仅固定初等函数的参数变换；任意复合函数解析器未实现。',
 '幂函数':'只支持平方和平方根等固定子情形；任意幂指数未实现。',
 '表面积与体积':'当前显示部分实体体积与截面积；通用表面积计算未实现。',
 '棱柱棱锥与棱台':'已有长方体和四棱锥；棱台未实现。',
 '极值与最值':'固定函数驻点和曲线观察；闭区间端点比较及一般最值验证未实现。',
 '空间向量与坐标运算':'空间坐标、数量积和夹角；通用三维向量运算编辑尚未实现。',
 '直线方向向量':'仅向量的方向表示；空间直线方程、点线距离未实现。',
 '正弦定理':'提供边角读数与 SSA 存在性；不是定理证明。',
 '余弦定理':'边长角度可以数值核对；没有自动生成证明。'
}

def apply_coverage(rows,presets):
    by_id={p['id']:p for p in presets}
    for row in rows:
        ids=list(EVIDENCE.get(row['concept'],[]))
        if not all(id in by_id for id in ids): raise ValueError('Coverage refers to nonexistent scene')
        row['available_presets']=ids
        row['status']='INTERACTIVE_FOUNDATION' if ids else 'PLANNED'
        row['capability']='可打开具体受控数学场景' if ids else '尚无对应专项交互场景'
        row['capability_limits']=LIMITS.get(row['concept'],
            '仅数值观察和固定预设，不等于完整教学、数学证明或学生掌握验证。' if ids else '尚待开发；不将通用三维/二维画板冒充此知识点的专项支持。')
        if ids: row['recommended_tool']=by_id[ids[0]]['tool']
    return rows
