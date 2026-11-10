# Batch76｜26项跨轨数学语义比对（项目编辑候选，非正式去重）

- 26/26条Batch75知识候选均已与既有教学草案比较；29项历史跨页链接仍为待裁决线索。
- 每项列出数学前提差别与可区分两者的反例/边界；不会把相关话题当作数学等价。
- **没有裁定任何一个课程官方知识原子**；七轨分母均保持null，0/61页教师完整原子审核。
- 任何SAME_TOPIC_UNCERTIFIED都需要真实教研审核，不得自动合并。

| 候选及课程轨道 | 旧草案 | 关系候选 | 定义域/数学前提区别 |
|---|---|---|---|
| KB75-P016-S02（COMPULSORY） | KB75-M01 | SAME_TOPIC_UNCERTIFIED | 必要条件与充分条件需要固定论域并分别检查P⇒Q与Q⇒P |
| KB75-P016-S03（COMPULSORY） | KB75-M07 | RELATED_DISTINCT | 含量词命题的否定要交换全称与存在,而命题逆否要求逻辑蕴含形式 |
| KB75-P027-S01（COMPULSORY） | KB75-M08 | RELATED_DISTINCT | 复数乘法对应以原点为中心的旋转伸缩而y轴反射是共轭后再取负实部 |
| KB75-P032-S02（COMPULSORY） | KB75-M02 | SAME_TOPIC_UNCERTIFIED | 样本统计量与总体参数的差异不因增加观测数自动消失;需要抽样机制 |
| KB75-P046-S03（SELECTIVE_COMPULSORY） | KB75-M03 | PARTIAL_TOPIC_OVERLAP | 条件概率定义要求P(B)>0,离散随机变量和正态分布涉及不同样本空间与分布假设 |
| KB75-P046-S04（SELECTIVE_COMPULSORY） | KB75-M02 | RELATED_DISTINCT | 样本均值只是描述中心;回归还需要拟合假设,列联分析则针对分类变量 |
| KB75-P052-S02（ELECTIVE_A） | KB75-M05 | RELATED_DISTINCT | 数列n趋于正无穷与函数x趋于某实点的极限在变量域和量词上不同 |
| KB75-P052-S03（ELECTIVE_A） | KB75-M05 | RELATED_DISTINCT | 连续需要点值存在并等于极限,仅有邻域差商或极限并不充分 |
| KB75-P052-S04（ELECTIVE_A） | KB75-M05 | PARTIAL_TOPIC_OVERLAP | 偏导要固定另一自变量;原函数积分定理需连续性等前提,不是对所有函数直接互换运算 |
| KB75-P056-S02（ELECTIVE_A） | KB75-M04 | SAME_TOPIC_UNCERTIFIED | 连续密度f(x)值非点概率;均匀分布只是连续分布的特殊例 |
| KB75-P056-S03（ELECTIVE_A） | KB75-M04 | RELATED_DISTINCT | 二维边缘概率必须对另一变量求和或积分;区间一维密度不能直接代替联合分布 |
| KB75-P056-S04（ELECTIVE_A） | KB75-M02 | RELATED_DISTINCT | 参数检验需抽样分布与误差假设,回归不能从样本均值推得因果关系 |
| KB75-P058-S02（ELECTIVE_B） | KB75-M05 | SAME_TOPIC_UNCERTIFIED | 偏导的另一变量固定是定义的一部分,沿曲线的全导数另有链式法则 |
| KB75-P058-S03（ELECTIVE_B） | KB75-M05 | RELATED_DISTINCT | 一元导数是单变量差商极限,偏导是限定方向,微分与定积分有额外条件 |
| KB75-P060-S01（ELECTIVE_B） | KB75-M08 | RELATED_DISTINCT | 三维叉积的方向依赖取向且仅在三维欧氏空间采用通常叉积;内积是标量 |
| KB75-P060-S02（ELECTIVE_B） | KB75-M06 | PARTIAL_TOPIC_OVERLAP | det(A)≠0表征可逆,但矩阵本身的行列式与线性方程组唯一解是不同对象 |
| KB75-P060-S03（ELECTIVE_B） | KB75-M06 | SAME_TOPIC_UNCERTIFIED | Ax=b唯一解需要系数矩阵满列秩,方阵情况下等价于非零行列式 |
| KB75-P061-S02（ELECTIVE_B） | KB75-M04 | RELATED_DISTINCT | 一维连续均匀密度只给单变量分布;二维联合模型必须另给依赖结构 |
| KB75-P061-S03（ELECTIVE_B） | KB75-M02 | RELATED_DISTINCT | 回归系数涉及多个自变量与可辨识性,样本均值本身不能确定偏回归系数 |
| KB75-P061-S04（ELECTIVE_B） | KB75-M02 | RELATED_DISTINCT | 无监督聚类标签不自动等于因果组别;正交试验设计与样本平均数目标不同 |
| KB75-P063-S02（ELECTIVE_B） | KB75-M06 | RELATED_DISTINCT | 解析几何曲线是点集约束,回归模型还含噪声与统计拟合条件 |
| KB75-P063-S03（ELECTIVE_B） | KB75-M04 | RELATED_DISTINCT | 指数增长一般不周期,三角函数周期模型具有非零周期;对有限观测不能仅凭单调性判定模型 |
| KB75-P063-S04（ELECTIVE_B） | KB75-M05 | RELATED_DISTINCT | 参数曲线斜率dy/dx=(dy/dt)/(dx/dt)要求dx/dt非零;不能除零 |
| KB75-P064-S03（ELECTIVE_C） | KB75-M07 | PARTIAL_TOPIC_OVERLAP | 定义规定符号对象,命题可判真假;逆否证明仅适用于蕴含命题 |
| KB75-P066-S02（ELECTIVE_C） | KB75-M02 | RELATED_DISTINCT | 从样本统计量到社会因果模型需额外识别假设且不得偷换量纲 |
| KB75-P069-S03（ELECTIVE_D） | KB75-M08 | PARTIAL_TOPIC_OVERLAP | 轴对称是严格保距映射,视觉和谐是设计评价,不能自动认证轴对称 |

## 不可自动结案
- 源材料仍需独立全文教师审查。538个历史证明步骤与10组冲突保持开放。
