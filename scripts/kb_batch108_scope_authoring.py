"""Original editorial readings of printed pages 18/55; never official frozen atoms."""
from __future__ import annotations

def C(page, lo, hi, key, kind, title, precondition, invalid, interpretation):
    return dict(page=page, start=lo, end=hi, key=key, kind=kind,
                title=title, mathematical_preconditions=precondition,
                invalid_generalization=invalid, editorial_note=interpretation)

# Exhaustive structural (not pedagogical) partitions, including headers/footers.
PARTITIONS = {
    18: [(1,1,"HEADER"),(2,3,"PRIOR_PAGE_TEACHING_CONTINUATION"),
         (4,5,"EQUALITY_INEQUALITY_TEACHING"),(6,11,"QUADRATIC_GRAPH_TEACHING"),
         (12,15,"GENERAL_PEDAGOGICAL_GUIDANCE"),(16,16,"ACADEMIC_REQUIREMENTS_HEADER"),
         (17,20,"SETS_AND_REPRESENTATIONS_ACHIEVEMENT"),
         (21,22,"LOGIC_LANGUAGE_ACHIEVEMENT"),(23,24,"FUNCTION_EQUATION_ACHIEVEMENT"),
         (25,25,"COMPETENCY_GUIDANCE"),(26,26,"NEXT_THEME_HEADER"),
         (27,27,"NEXT_PAGE_CONTINUATION"),(28,28,"FOOTER")],
    55: [(1,1,"SYSTEMS_HEADER"),(2,4,"GAUSSIAN_ELIMINATION"),
         (5,5,"HOMOGENEOUS_SYSTEM"),(6,7,"NONHOMOGENEOUS_CONSISTENCY"),
         (8,8,"GENERAL_SOLUTION"),(9,10,"CRAMER_RULE"),
         (11,11,"GEOMETRY_HEADER"),(12,12,"PLANE_EQUATIONS"),
         (13,13,"LINE_EQUATIONS"),(14,15,"GEOMETRIC_RELATIONS_AND_DISTANCE"),
         (16,16,"ISOMETRY_HEADER"),(17,18,"PLANE_ISOMETRIES"),
         (19,19,"PLANE_SYMMETRIES"),(20,20,"PLANE_ISOMETRY_MATRICES"),
         (21,22,"SPACE_ISOMETRIES"),(23,23,"SPACE_SYMMETRIES"),
         (24,24,"SPACE_ISOMETRY_MATRICES"),(25,25,"FOOTER")]
}
CANDIDATES=[
C(18,2,3,"collaborative_guidance","PEDAGOGY","自主学习与合作学习的课堂组织",
  "教学组织建议，不等同于学生必需证明的一条数学定理。","将学习形式当作单独数学公式或可通过符号程序证明的命题。","承接上一页教学建议，不建立新的数学知识原子。"),
C(18,4,5,"equality_inequality","METHOD","等式变形与不等式变形条件辨析",
  "乘以负数时不等号反向，等式两边乘同一实数仍可得等式；约去因子需要非零。","把除以未知数或负数乘除当成无条件保序的等价步骤。","源文为教学建议；此处选取原理作原创教学研究候选。"),
C(18,6,11,"quadratic_function","METHOD","用二次函数图象解释二次方程与不等式",
  "二次项系数不为零，按定义域实数上的函数值与横轴位置判断。","图象仅相切横轴时仍误认为必有两个不同的实根。","课标此处讨论教学组织，不把函数图像、方程、不等式合并成一个原子。"),
C(18,12,15,"pedagogy_guidance","PEDAGOGY","数学抽象与逻辑推理学习习惯",
  "本条是综合教学指导，不是独立的数学充要条件。","将学习习惯措辞改写成有形式证明证书的数学定理。","仅供教师培训和教学策略检索，非官方数学知识分母。"),
C(18,17,20,"set_language","CONCEPT","集合成员、集合关系和三种表征的转换",
  "必须先明确全集及成员条件，有限集合可以列举，图形表达不能凭外观判定成员。","把集合元素a与单元素集合{a}等同，或把图示当作普遍证明。","学业要求包含多种能力动词，教师需拆分后再冻结原子。"),
C(18,21,22,"logic_quantifier","CONCEPT","常用逻辑用语的命题表达",
  "否定全称命题需要转换为存在量词，否定谓词部分也须相应变更。","将∀x P(x)的否定错误写作∀x 非P(x)。","学业要求含表达、论证、交流，不能机械合并为一个概念。"),
C(18,23,24,"function_view","METHOD","用函数符号联系方程与不等式",
  "方程f(x)=0的解必须位于函数定义域；不等式的严格端点须单独核对。","忽略定义域，直接从图的延长线读取无效根。","学业要求含性质和联系，候选与前页主题有交叉。"),
C(18,25,25,"competency_marker","PEDAGOGY","数学抽象、逻辑推理、运算素养目标",
  "素养目标是课程能力描述，并不是学生掌握一条可独立证明的定理。","把综合素养目标算作可批准数学原子或考试单选题型。","必须作为元数据跟踪，而非充当课标数学分母。"),
C(55,2,4,"gaussian_row","THEOREM","高斯消元中可逆初等行变换保持解集",
  "行交换可逆；倍乘操作的倍数必须非零；加倍数的一行到另一行可逆。","把某一行乘零仍视为解集不变的可逆变换。","对应选修A三元线性方程组，原创建议按变换合法性拆分。"),
C(55,5,5,"homogeneous_kernel","THEOREM","三元齐次系统非零解与行列式退化",
  "仅讨论实数3×3系数矩阵；零解总是存在，非零解条件另判。","误以为齐次系统无解，或把detA=0当作只有零解。","非零解条件来自线性代数原理，非原文逐字命题。"),
C(55,6,7,"consistency_rank","THEOREM","三元非齐次方程组的秩相容性",
  "系数矩阵为3×3、增广矩阵为3×4，比较实数域上的矩阵秩。","系数矩阵秩小于增广矩阵秩仍声称存在共同解。","采用Rouché–Capelli判据解释学业内容，教师须审核表述难度。"),
C(55,8,8,"affine_solution","CONCEPT","非齐次线性方程组的一般解结构",
  "已知一个特解且相同系数矩阵的齐次解集合；系统若不相容则无特解。","把任意向量都加在特解上，而不要求属于齐次核空间。","与上一行有解判定相关但不应合并为一项。"),
C(55,9,10,"cramer","THEOREM","三元克拉默法则的非零行列式前提",
  "实数3×3方阵detA不等于零，替换列的行列式定义明确。","行列式为零仍进行detAi/detA除法，造成未定义运算。","只能说明可逆情况下唯一解；奇异系统应转消元或秩判定。"),
C(55,12,12,"plane_eq","CONCEPT","空间平面方程的法向量条件",
  "一般式ax+by+cz+d=0中(a,b,c)不同时为零。","把零法向量的0x+0y+0z+1=0当作真实平面。","从空间非零法向量表征转换为平面标量方程，注意符号单位。"),
C(55,13,13,"line_eq","CONCEPT","空间直线的点向式与非零方向",
  "直线r(t)=p+tv中方向v必须非零；t遍历全体实数。","方向向量为零时仍声称可以生成一条直线。","要区分参数式与两平面交线的方程表达。"),
C(55,14,15,"point_plane_dist","THEOREM","三维点到平面的非负距离公式",
  "平面法向量非零，欧氏空间中的距离为绝对值除以法向量长度。","遗漏绝对值产生负距离，或在零法向量时除零。","原文还提到点线距离，当前仅选取平面情形作为完整候选。"),
C(55,17,18,"planar_reflection","METHOD","平面轴反射是距离保持变换",
  "以x轴为反射轴，点(x,y)映射(x,-y)，在欧氏距离下保距。","把非等比伸缩(x,2y)误称为轴反射。","选择简单坐标轴情形避免暗示已覆盖任意轴。"),
C(55,19,19,"symmetry_set","CONCEPT","图形对称需按集合不变性判定",
  "先确定平面点集S和选定等距变换T，必须满足T(S)=S。","仅仅变换后形状大小相同，就断言原点集逐点不动。","形状看似一样和变换前后点集严格相等的区别必须独立说明。"),
C(55,20,20,"rotation_matrix","THEOREM","平面旋转矩阵保长度和内积",
  "实平面、绕原点旋转，矩阵列正交且长度为1。","把任意det=1矩阵都认作正交旋转矩阵。","二维旋转角度和列正交条件应有数学证明，有限检验只作回归。"),
C(55,21,22,"space_isometry","METHOD","三维平移与正交变换组成的等距变换",
  "对三维实向量x作Qx+t且QᵀQ=I，平移向量t固定。","以一般可逆矩阵取代正交矩阵便直接声称保欧氏距离。","此处仅处理空间等距变换代表类型，不覆盖变换群全课程。")
]
assert len(CANDIDATES)==20
