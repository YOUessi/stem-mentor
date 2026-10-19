"""Curated engineering coverage matrix for high-school mathematics.
NOT a verbatim restatement of an official examination syllabus.
"""
import json
from extend_v09 import apply_coverage
from extend_v010 import apply_coverage as foundation_coverage
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SRC="https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf"
# (learning level, curriculum theme, unit, concept titles, visualization tool id, ready titles)
GROUPS=[
("必修","预备知识","集合与常用逻辑用语",["集合及其表示","交集并集补集","充分条件与必要条件","全称量词与存在量词","命题真假与逻辑关系"],"venn_logic",[]),
("必修","预备知识","不等式与代数",["等式性质与不等式性质","一元二次不等式","含参数不等式","基本不等式","不等式等价变换和定义域"],"number_line",[]),
("必修","函数","函数基本概念与性质",["函数映射和定义域","函数值域","单调性","奇偶性","周期性","零点与方程","分段函数"],"function_2d",["函数映射和定义域","单调性","奇偶性","周期性","零点与方程"]),
("必修","函数","基本初等函数",["一次函数","二次函数","幂函数","指数函数","对数函数","绝对值函数","函数变换与复合"],"function_2d",["一次函数","二次函数","幂函数","指数函数","对数函数","绝对值函数","函数变换与复合"]),
("必修","函数","三角函数",["弧度制和单位圆","正弦余弦函数图像","正切函数","诱导公式","和差与倍角公式","三角恒等变换","三角函数图像变换"],"function_2d",["正弦余弦函数图像","正切函数","三角函数图像变换"]),
("必修","几何与代数","平面向量与解三角形",["平面向量的表示","向量加减与数乘","向量数量积","向量投影与夹角","正弦定理","余弦定理","SSA 二解与三角形存在性","三角形面积与几何关系"],"triangle_2d",["正弦定理","余弦定理","SSA 二解与三角形存在性","三角形面积与几何关系"]),
("必修","几何与代数","复数",["复数与复平面","复数模与辐角","复数加减乘除及几何意义"],"complex_plane",[]),
("必修","几何与代数","立体几何初步",["空间点线面位置关系","平行与垂直的判定","直线与平面距离","棱柱棱锥与棱台","圆柱圆锥球","表面积与体积","空间截面与展开图"],"space_3d",["空间点线面位置关系","平行与垂直的判定","棱柱棱锥与棱台","圆柱圆锥球"]),
("必修","概率与统计","概率基础",["样本空间与随机事件","互斥和对立事件","古典概型","概率加法与乘法基本关系"],"probability_tree",[]),
("必修","概率与统计","数据与统计",["数据的收集与抽样","频数分布与直方图","均值中位数众数","方差标准差","百分位数与样本估计"],"statistics_plot",[]),
("必修","数学建模与探究","综合应用",["数学建模流程","数据模型与检验","问题提出与合作探究"],"modeling_workspace",[]),
("选择性必修","函数","数列与导数",["数列概念与递推","等差数列","等比数列","数列求和与数列模型","导数的几何意义","导数与切线","导数判断单调性","极值与最值","函数零点和参数讨论"],"function_2d",["导数的几何意义","导数与切线","导数判断单调性","极值与最值","函数零点和参数讨论"]),
("选择性必修","几何与代数","空间向量与立体几何",["空间直角坐标系","空间向量与坐标运算","空间向量数量积","直线方向向量","平面法向量","直线平面夹角","二面角","空间距离计算","空间多面体与投影"],"space_3d",["空间直角坐标系","空间向量与坐标运算","空间向量数量积","直线方向向量","平面法向量","直线平面夹角","二面角","空间距离计算","空间多面体与投影"]),
("选择性必修","几何与代数","平面解析几何",["倾斜角与直线斜率","直线方程","两直线的位置关系","点到直线距离","直线与圆的位置关系","圆与圆的位置关系","椭圆定义及几何性质","双曲线定义及几何性质","抛物线定义及几何性质","圆锥曲线焦点与准线","圆锥曲线与直线联立","圆锥曲线的切线与法线"],"conic_2d",["倾斜角与直线斜率","直线方程","直线与圆的位置关系","椭圆定义及几何性质","双曲线定义及几何性质","抛物线定义及几何性质","圆锥曲线焦点与准线"]),
("选择性必修","概率与统计","计数原理",["分类加法计数原理","分步乘法计数原理","排列与组合","二项式定理"],"combinatorics",[]),
("选择性必修","概率与统计","概率分布与统计推断",["条件概率与独立性","全概率公式","离散型随机变量","二项分布","超几何分布","正态分布","回归分析与相关性","独立性检验"],"probability_plot",[]),
("选择性必修","数学建模与探究","综合应用",["数学探究活动","数据驱动的建模","对模型进行验证与评价"],"modeling_workspace",[]),
("选修拓展","数学拓展","竞赛或专题延伸",["三角形五心与综合几何","圆锥曲线极线与换一半法则","参数方程与极坐标","更一般的二次曲面","数学归纳法","向量外积","算法与数学证明"],"enrichment",[]),
]
def make():
    rows=[]
    for level,theme,unit,names,tool,ready in GROUPS:
        for name in names:
            rows.append({"id":"HS-MATH-"+str(len(rows)+1).zfill(3),
              "level":level,"theme":theme,"unit":unit,"concept":name,
              "recommended_tool":tool,
              "status":"INTERACTIVE_FOUNDATION" if name in ready else "PLANNED",
              "capability":"探索示意与数形关系，非完整教学验证" if name in ready else "未实现专项交互",
              "source":{"standard":"普通高中数学课程标准（2017年版2020年修订）",
                        "uri":SRC,"mapping_type":"ENGINEERING_INTERPRETATION","teacher_review":"PENDING"},
              "notes":"按数学对象可视化和数学核心素养整理，考查范围请以地区/年份为准。"})
    presets=json.loads((ROOT/"visual_presets.json").read_text(encoding="utf8"))["presets"]
    rows=apply_coverage(rows,presets)
    rows=foundation_coverage(rows,presets)
    assert len({v["id"] for v in rows})==len(rows)
    data={"version":"2026-10-19.1","subject":"高中数学",
          "curriculum_reference":"普通高中数学课程标准（2017年版2020年修订）",
          "reference_url":SRC,
          "scope_note":"产品工程覆盖清单，不是教育部官方逐条课标原文、也不是某省高考命题细目；需教师审核。",
          "coverage":rows}
    (ROOT/"curriculum_map.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    from collections import Counter
    print("Curriculum concepts:",len(rows),"interactive foundations:",
          sum(r["status"]=="INTERACTIVE_FOUNDATION" for r in rows))
    print("Levels",Counter(r["level"] for r in rows))
    print("Tool groups",Counter(r["recommended_tool"] for r in rows))
if __name__=="__main__":make()
