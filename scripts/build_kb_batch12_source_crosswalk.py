#!/usr/bin/env python3
"""Source-anchored ORIGINAL editorial atomization candidates from the HS 2020 mathematics standard.

Only the referenced printed-page sections are inspected. The list is a sampled
subset, NOT the complete official standard, and none of the records is an
officially numbered atom, an audited teacher lesson, or certified coverage.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "curriculum/highschool_math/source_anchored_skill_candidates_batch12.json"
URL = "https://jyj.changdu.gov.cn/cdsjyj/c101476/202205/764ee1914e3c45aaba8e372f1b628a34/files/75676dfa9af0442db1457404a884a69f.pdf"
# Each paraphrase (not a quotation) records the printed page and section in the standard.
# R = compulsory (required); S = selective compulsory; A-E = elective tracks.
ROWS = """
R|15|集合的概念与表示|用元素属于关系及列举法或描述法表达有限或无限集合
R|15|集合的基本关系|判断子集、真子集及集合相等，辨析空集的性质
R|15|集合的基本运算|在指定全集下计算并集、交集、补集
R|16|常用逻辑用语|区分充分条件、必要条件及充要条件的推理方向
R|16|常用逻辑用语|正确否定含全称量词与存在量词的命题
R|16|等式与不等关系|确定不等式运算时加减与乘除的合法条件
R|16|基本不等式|使用非负变量的算术几何均值关系并核验等号成立条件
R|17|二次方程与不等式|联结二次函数的图像、零点以及一元二次不等式解集
R|19|函数概念|用集合对应关系定义函数，区分定义域、对应规则与值域
R|19|函数概念|比较图象、列表、解析式三种表征并判断是否属于同一函数
R|19|分段函数|按输入所在区间选定函数分支并检查端点归属
R|19|函数性质|用符号语言判断单调区间和最大最小值
R|19|函数性质|检验奇偶性前确认定义域关于原点对称
R|19|函数性质|结合三角函数图象识别周期及最小正周期
R|20|幂函数|比较典型幂函数的定义域、奇偶性和增长规律
R|20|指数函数|从有理指数扩展认识实指数并检查底数合法性
R|20|指数函数|根据底数区分指数函数的增减性和基本性质
R|20|对数函数|用指数与对数的互逆关系检查真数和底数条件
R|20|对数函数|使用换底公式和对数运算法则处理简单函数问题
R|21|三角函数|将角度制与弧度制相互转换并检验符号方向
R|21|三角函数|通过单位圆定义正弦余弦与正切并排除正切奇点
R|21|三角函数|根据单位圆推导诱导公式并检查象限符号
R|22|三角恒等变换|由同角恒等式推导两角和差及倍角的基本关系
R|22|三角函数模型|辨别正弦函数的振幅角频率相位并建模
R|23|函数应用|借助函数图像及二分逼近求方程的近似零点
R|25|平面向量|区分向量与模长并进行加减及数乘的几何运算
R|26|平面向量|从正交基底表达平面向量并用数量积判断垂直
R|26|解三角形|利用正弦余弦定理建立三角形边角条件并分析多解
R|27|复数|将复数表示为有序实数对并核验四则运算的定义
R|28|立体几何|识别空间几何体的结构特征与直观图的局限
R|29|立体几何|理解线线线面面面平行与垂直位置关系
R|31|概率|在有限样本空间上识别事件并交及互斥关系
R|31|概率|对等可能样本点使用古典概型并检查等可能条件
R|31|概率|区分事件独立与互斥并验证对应概率关系
R|32|统计|区分总体、样本、样本量和抽样框
R|32|统计|利用简单随机与分层随机抽样构建样本
R|32|统计|通过样本均值方差与百分位数描述数据特征
R|33|数学建模活动|明确变量模型假设并解释函数模型失效条件
S|38|数列|把数列视为定义在正整数集上的函数并使用列表与通项表征
S|38|等差数列|建立等差数列通项及前n项和并明确项数
S|38|等比数列|建立等比数列通项及分情况求和公式
S|38|数学归纳法|区分基例与归纳步，证明自然数命题
S|39|导数|从平均变化率理解瞬时变化率与切线斜率
S|39|导数运算|使用基本求导公式与四则法则
S|39|复合函数求导|在课程指定的简单线性内函数条件下求复合导数
S|39|导数的应用|判定多项式的单调区间与极值候选
S|39|闭区间最值|比较驻点与区间端点获得极值和最值
S|43|直线与方程|区分直线倾斜角、斜率及竖直线例外
S|43|直线与方程|推导点斜式、两点式与一般式的等价适用条件
S|43|直线与方程|根据斜率和方向判断直线平行或垂直
S|44|直线与圆|求点到直线距离及两平行线间距离
S|44|圆与方程|区分圆标准方程和一般方程的半径合法性
S|44|圆锥曲线|从焦点几何定义建立椭圆标准方程与性质
S|44|圆锥曲线|辨析抛物线与双曲线的焦点条件、标准方程和退化参数
S|42|空间向量|在空间直角坐标系中推导两点距离并检查坐标一致性
S|42|空间向量|用空间向量基本定理将向量表示为一组基的线性组合
S|42|空间向量|运用线性运算与数量积解决空间向量分量问题
S|43|空间几何|根据方向向量与法向量分析空间位置关系
S|43|空间几何|使用向量求点面距离与线面夹角并验证非零向量
S|44|平面解析几何|判断直线与圆以及两圆的位置关系
S|45|圆锥曲线|结合图形与方程研究椭圆抛物线和双曲线的基本性质
S|46|计数原理|区分分类相加与分步相乘的计数方法
S|46|排列与组合|判断是否考虑顺序并计算排列数和组合数
S|47|二项式定理|使用组合恒等式证明二项式展开并计算系数
S|47|条件概率|核对条件事件概率非零后使用条件概率乘法公式
S|47|概率分布|用离散随机变量分布列计算数学期望和方差
S|47|概率分布|区分有放回与无放回的二项及超几何模型
S|48|正态分布|解释正态密度的均值和方差及连续随机变量的概率含义
S|48|线性回归|用样本相关系数与最小二乘模型区分相关和因果
S|48|统计列联表|构建两乘两列联表并解释独立性检验的条件
A|52|数列极限|使用ε-N语言验证收敛数列的一个具体极限
A|52|数列极限|证明收敛数列有界并辨析逆命题不成立
A|52|数列极限|理解单调有界序列的收敛判据及必要假设
A|52|数列极限|掌握收敛数列极限四则运算的条件
A|52|函数极限|用ε-δ语言陈述点处函数极限
A|52|函数极限|应用合法的极限四则运算与两个基本三角和指数极限
A|53|连续函数|区分点处连续、闭区间连续与介值性质
A|53|导数与微分|区分差商极限的导数与可导性条件
A|53|导数与微分|理解拉格朗日中值定理的完整前提与证明要求
A|53|导数与微分|用导数和中值定理研究不等式及单调性
A|53|定积分|经由黎曼和理解定积分的定义、面积和单位
A|53|定积分|在连续与可微条件下正确使用微积分基本定理
A|54|空间向量与代数|用内积和外积辨析向量的平行、垂直与方向
A|54|空间向量与代数|判断向量组线性相关并识别向量空间和子空间
A|54|矩阵与行列式|进行三阶矩阵基本运算并核对维度约束
A|54|矩阵与行列式|用行列式判断线性方程组的可逆情形
A|55|三元方程组|使用高斯消元求齐次和非齐次三元方程组并识别参数解
A|55|空间直线与平面|构造空间直线或平面方程并检查法向量非零
B|58|极限|由典型数列和函数例子区分数列极限、函数极限与连续性
B|58|导数与微分|用二阶导数研究弯曲性与变化率
B|58|导数与微分|理解中值定理并应用于函数单调性与不等式
B|59|定积分|在连续性前提下使用积分计算面积、体积与黎曼和
B|59|二元函数|在开域内计算简单二元函数的偏导数
B|59|二元函数|判断多元驻点与实际约束域的极值
B|60|空间向量与代数|判断三维空间向量组的线性相关与向量分解
B|60|矩阵与行列式|使用三阶矩阵与行列式解线性方程组
B|61|应用统计|辨析连续分布密度与概率质量函数
B|61|应用统计|区分二维联合分布、独立性与协方差
B|61|参数估计|在样本假设下比较矩估计和极大似然估计
B|62|假设检验|解释零假设、检验统计量和显著性而不把p值当作后验概率
B|62|回归与聚类|在建模条件下用最小二乘估计二元回归模型
B|63|模型|在不同时间变量的尺度下拟合线性、指数和二次模型
B|63|参数模型|用参数方程表达运动轨迹并检查参数范围
C|64|逻辑推理初步|分清数学定义、命题、充分和必要条件
C|65|逻辑推理初步|解释同一律、矛盾律和排中律在不同推理中的角色
C|65|逻辑推理初步|区分演绎推理与归纳类比猜想的证明力度
C|65|逻辑推理初步|使用直接证明、反证或构造反例的适用前提
C|65|逻辑推理初步|了解公理系统的相容性与独立性等基本术语
C|66|经济数学模型|建立复利模型并解释时间单位和利率假设
C|66|经济数学模型|用线性方程组探索投入产出模型
C|67|社会数学模型|识别人口增长模型的假设与现实失效边界
C|67|社会数学模型|在信度评价中区分分数预测与因果解释
C|68|社会调查|设计调查对象、抽样框及避免偏差的问卷
C|68|社会调查|用抽样设计与描述统计构造可核查调查报告
D|69|美与数学|用圆和圆锥曲线描述常见形状的简洁性
D|70|美与数学|分析反射、旋转、平移等几何对称及其不变量
D|70|美与数学|对周期现象建立带周期和相位的函数模型
D|70|美与数学|辨析黄金分割与斐波那契数列的真实适用情形
D|70|音乐中的数学|联系正弦频率、振幅和叠加描述声音
D|71|音乐中的数学|用等比数列分析十二平均律的频率比例
D|71|音乐中的数学|用分数和最小公倍数表达节拍的同步
D|72|体育运动中的数学|根据向量分解解释运动轨迹和速度
D|72|体育运动中的数学|分析运动数据的样本、估计与局限性
D|72|体育运动中的数学|用基本运筹和图论构造赛事安排
E|73|拓展视野|将机器人位姿或动作几何作为建模探索主题
E|73|拓展视野|通过对称与群研究有限对称变换
E|73|拓展视野|以初等数论和数列差分形成探究性课题
E|73|日常生活|在家庭理财模型中解释利率、期限和现金流
E|73|地方特色|通过地区建筑的几何关系建立模型并验证
E|73|大学数学先修|在课程任选条件下探索微积分基本问题
E|73|大学数学先修|根据学习目标讨论线性代数与解析几何先修
E|73|大学数学先修|根据学习目标讨论概率论与数理统计先修
""".strip()

TRACKS = {"R":"COMPULSORY","S":"SELECTIVE_COMPULSORY","A":"ELECTIVE_A",
          "B":"ELECTIVE_B","C":"ELECTIVE_C","D":"ELECTIVE_D","E":"ELECTIVE_E"}
# The same short code "C" cannot represent both compulsory and elective C.
# Source rows use 'R' for compulsory; keep this assertion to prevent silent scope corruption.
assert len(TRACKS) == 7

def source_rows():
    rows = []
    sequence = Counter()
    for line in ROWS.splitlines():
        parts = line.split("|")
        if len(parts) != 4:
            raise ValueError(f"Malformed authored skill row: {line!r}")
        raw_track, printed_page, section, objective = parts
        track = TRACKS[raw_track]
        page = int(printed_page)
        limits = {
          "COMPULSORY":(13,35),"SELECTIVE_COMPULSORY":(36,50),
          "ELECTIVE_A":(51,57),"ELECTIVE_B":(58,63),
          "ELECTIVE_C":(64,68),"ELECTIVE_D":(69,72),"ELECTIVE_E":(73,73)
        }
        low,high=limits[track]
        if not low<=page<=high:
            raise ValueError(f"Incorrect standard page/track: {line}")
        sequence[track]+=1
        rows.append({
          "id":f"HS-STD2020-{track}-{sequence[track]:03d}",
          "track":track,
          "section":section,
          "editorial_learning_objective":objective,
          "source":{
            "document":"普通高中数学课程标准（2017年版2020年修订）",
            "url":URL,
            "printed_page":page,
            "source_kind":"PUBLIC_OFFICIAL_STANDARD_PAGE_LOCATION",
            "passage_review":"SOURCE_SECTION_LOCATED_NOT_TEACHER_SIGNED"
          },
          "content_status":"CURRICULUM_CANDIDATE_NOT_DEEP_LESSON",
          "atomic_status":"PROJECT_EDITORIAL_SPLIT_NOT_AN_OFFICIAL_NUMBERED_ATOM",
          "teacher_review":"PENDING",
          "linked_deep_lesson_ids":[],
          "verified_official_atom_id":None,
          "notes":"本条为原创学习目标拆解，不代表课标官方逐条编号或已完成内容；仍需对照原文核查词义与层次。"
        })
    ids=[r["id"] for r in rows]
    if len(ids)!=len(set(ids)):
        raise ValueError("Duplicate candidate IDs")
    if len({(r["track"],r["section"],r["editorial_learning_objective"]) for r in rows})!=len(rows):
        raise ValueError("Duplicate editorial content")
    return rows

def document():
    values = source_rows()
    summary=Counter(row["track"] for row in values)
    return {
      "schema_version":"1.0.0",
      "status":"SOURCE_ANCHORED_EDITORIAL_SAMPLE_REVIEW_PENDING",
      "is_complete_official_atomic_inventory":False,
      "verified_official_atomic_denominator":None,
      "source_url":URL,
      "project_authorship":"PROJECT_AUTHORED_PARAPHRASES_NO_OFFICIAL_TEXT_REPRODUCTION",
      "summary":{
        "candidate_learning_objectives":len(values),
        "by_track":{key:summary.get(key,0) for key in (
          "COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B",
          "ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")},
        "teacher_approved":0,
        "active_deep_lesson_links":0,
        "remaining_official_coverage_unknown":True
      },
      "items":values,
      "warnings":[
        "This is a sampled source-page-anchored ORIGINAL editorial checklist, not an exhaustive extraction of the 2017/2020 standard.",
        "Official content requirements have not been assigned official atomic IDs; printed-page coordinates assist review but do not certify lesson completeness.",
        "Some elective E topics are examples and locally selectable, not nationally mandated uniform detailed coverage.",
        "No independently approved content or student-visible teaching evidence is created by this artifact."
      ]
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    payload=json.dumps(document(),ensure_ascii=False,indent=2)+"\n"
    if args.check:
        if OUT.read_text(encoding="utf-8")!=payload:
            raise AssertionError("Batch12 standard source crosswalk out of date")
        print("PASS source-anchored scope checklist", len(source_rows()))
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(payload,encoding="utf-8")
        print("WROTE",OUT,len(source_rows()))
