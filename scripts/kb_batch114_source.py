"""Batch114 editorial locators for the pinned curriculum PDF, printed pp.24 and 61.
Do not reproduce source passages, infer teacher approval or official atomic denominators.
"""
def C(p,lo,hi,key,kind,title,pre,invalid):
    return dict(page=p,start=lo,end=hi,key=key,kind=kind,title=title,
      mathematical_preconditions=pre,invalid_generalization=invalid,
      editorial_note="项目作者对来源范围的原创解释；原PDF在Mac私有缓存，行号不是教师认证的知识原子。")
PARTITIONS={
24:[(1,1,"HEADER"),(2,3,"LOG_INVERSE"),(4,5,"UNIT_CIRCLE"),(6,8,"TRIG_IDENTITY"),
    (9,11,"FUNCTION_MODELS"),(12,15,"TECHNOLOGY_APPLICATION"),(16,18,"HISTORY_AND_PEDAGOGY"),
    (19,22,"ACHIEVEMENT_FUNCTION_DEFINITION"),(23,26,"ACHIEVEMENT_PROPERTIES"),
    (27,28,"ACHIEVEMENT_MODEL_AND_ROOT"),(29,29,"FOOTER")],
61:[(1,1,"TOPIC_HEADER"),(2,10,"OVERVIEW"),(11,13,"CONTENT_OUTLINE"),
    (14,16,"CONTINUOUS_RANDOM_VARIABLE"),(17,19,"IMPORTANT_DISTRIBUTIONS"),
    (20,21,"MOMENTS"),(22,25,"JOINT_DISTRIBUTION"),(26,26,"FOOTER")]
}
CANDIDATES=[
C(24,2,3,"log_inverse","THEOREM","指数与对数互逆必须有合法底数和正数真数","底数大于零且不等于一；指数的值域为正数，对数真数严格为正。","把底数一当作可逆函数或把负数当作实数对数输入。"),
C(24,4,5,"circle_trig","CONCEPT","单位圆可定义任意实数角对应的正弦和余弦","同一单位正交坐标系和实数角是定义三角函数的条件。","仅把锐角三角形对边比当作三角函数的完整定义。"),
C(24,6,8,"cos_difference","THEOREM","两角差余弦由单位向量点积推导","角度采用一致单位，单位向量在同一欧氏内积空间定义。","将两角差余弦错误写为两个同角函数的简单差值。"),
C(24,9,11,"model_interpretation","METHOD","从现实语境选择幂指对三角函数模型","明确输入输出量纲和假设区间，数据拟合与现实可靠性分别检查。","通过有限个点就保证模型可以无限外推。"),
C(24,12,15,"function_plot","METHOD","图像和数值计算只能辅助发现函数规律","数值采样需要规定采样间隔、输入范围与精度误差。","把画图仪上的像素交点当作一般根存在的形式证明。"),
C(24,12,15,"numeric_solver","METHOD","函数近似求根需要单独报告误差和前提","连续函数在异号闭区间有根，但未必唯一或处处可微。","函数不连续或两端同号却无条件宣称二分必得零点。"),
C(24,16,18,"history_activity","PEDAGOGY","数学史写作教学活动不应当作数学证明","历史资料、评价活动和数学定理的事实证据类型不同。","因为存在教学活动就认定任何数学命题已被严格证明。"),
C(24,19,22,"representation","CONCEPT","函数对应规则、表达式和图像须连同定义域一起比较","同一函数须定义域一致且每个输入输出一致。","解析式相同但定义域不同仍断言是同一个函数。"),
C(24,23,26,"monotonicity","METHOD","函数单调与奇偶性质不能只凭有限样本判断","单调性需要指定同一区间上任意一对输入；奇偶性需要定义域对称。","从两个采样点的上升就断言区间整体严格递增。"),
C(24,27,28,"root_graph","METHOD","从函数角度理解方程零点和近似解法","二分至少需要全区间连续与端点异号；唯一性需要额外条件。","仅凭图像显示有一处近似交点就推断全区间唯一实根。"),
C(61,2,10,"statistics_overview","PEDAGOGY","概率统计专题总览只是范围指引而非完整知识证明","专题概览不能替代逐条公式定义、适用条件和反例的核对。","把总览里出现的名词直接算作已核准完整讲义。"),
C(61,11,13,"regression_overview","CONCEPT","线性回归属于统计模型而非任意关系的确定性定律","数据与误差结构、可识别性、残差假设需在统计建模中说明。","某数据集残差恰为零就断定未来预测准确无误。"),
C(61,11,13,"clustering_overview","METHOD","聚类分析的分组依赖特征尺度和算法选择","距离和特征标准化改变分组时应独立检验稳定性。","认为聚类标签天然具有因果解释或者真实地面类别。"),
C(61,11,13,"design_overview","METHOD","正交试验设计与全因子试验不能混为同一形式","因素水平与正交表平衡条件需明确；不能自动保证全部交互效应可辨识。","任意小样本实验都宣称可无偏估计全部高阶交互作用。"),
C(61,14,16,"continuous_density","CONCEPT","连续型随机变量概率是密度积分而非单点高度","密度非负并在全域积分为一，积分区间给概率。","将概率密度在单点的数值直接当作该单点的概率。"),
C(61,17,19,"normal_standardize","METHOD","正态分布线性标准化必须正确使用标准差","方差为正且标准差等于方差的正平方根；不能用方差直接缩放。","错误地把正态分布的方差σ²直接当成标准差σ使用。"),
C(61,17,19,"chi_t_moments","CONCEPT","卡方和t分布矩的存在条件依赖自由度","t分布均值要求自由度大于一，方差要求大于二。","向自由度二的t分布套用有限方差公式。"),
C(61,20,21,"uniform_moments","THEOREM","连续均匀分布的矩公式需要区间长度正","端点a<b且密度合法归一化；退化常量需另行定义。","忽视区间两个端点相等时密度公式分母为零的不合法性。"),
C(61,22,25,"joint_marginal","THEOREM","离散二维随机变量边缘分布通过联合分布求和","联合分布非负且全部支持点总概率等于一。","遗漏联合表某一列仍断言计算了完整边缘概率。"),
C(61,23,25,"covariance_independence","CONCEPT","零协方差一般不推出随机变量独立","有限矩存在才可谈协方差；独立性须检查联合分布因子分解。","只因线性相关系数为零就认为不存在非线性依赖。"),
C(61,11,13,"parameter_inference","METHOD","参数估计和假设检验必须区分检验假设与证据","需要预先指定总体模型、样本机制与显著性解释。","把观测所得p值错误解释为原假设成立的后验概率。")
]
