"""Author non-linear proof/heuristic graph metadata for curated demonstration problems."""
import json
from pathlib import Path

def graph(problem, given, goal, forward, backward, bridge, boundary, checks=None):
    nodes = [
      {'id':'given','role':'GIVEN','statement':given,'verification':'GIVEN_BY_PROBLEM','teacher_only':False},
      {'id':'goal','role':'GOAL','statement':goal,'verification':'TASK_TARGET','teacher_only':False},
      {'id':'forward','role':'FORWARD','statement':forward,'verification':'CURATED_STEP_UNCHECKED_FOR_STUDENT','teacher_only':True},
      {'id':'backward','role':'BACKWARD','statement':backward,'verification':'HEURISTIC_SUBGOAL','teacher_only':True},
      {'id':'bridge','role':'BRIDGE','statement':bridge,'verification':'CURATED_STRATEGY','teacher_only':True},
      {'id':'boundary','role':'BOUNDARY','statement':boundary,'verification':'CURATED_CONDITION','teacher_only':True},
    ]
    edges = [
      {'source':'given','target':'forward','relation':'POSSIBLE_DERIVATION','verified':False},
      {'source':'goal','target':'backward','relation':'BACKWARD_SEARCH_NOT_PROOF','verified':False},
      {'source':'forward','target':'bridge','relation':'MAY_SUPPORT','verified':False},
      {'source':'backward','target':'bridge','relation':'MAY_SUPPORT','verified':False},
      {'source':'bridge','target':'goal','relation':'PROOF_OBLIGATION','verified':False},
      {'source':'boundary','target':'bridge','relation':'CONSTRAINS_APPLICATION','verified':False},
    ]
    return {'problem_id':problem,'version':'2026-10-15.1','nodes':nodes,'edges':edges,
            'guidance':{
               'START':'先区分哪些是已知、什么是最终目标；不要马上套公式。',
               'FORWARD':'你从题目条件已经得到了什么关系？它与目标还有什么距离？',
               'STUCK':'如果暂时正推不动，先不往下算：为了达到最终目标，需要哪一个更小的中间结论？',
               'BACKWARD':'把正推得到的关系与从目标反推的中间条件放在一起，哪一个转换能连接两边？',
               'BRIDGE':'你想到的连接为什么有效？哪些条件保证它可以使用？请自己先验证。',
               'CALCULATION':'思路若已确定，先自己完成常规运算；优先检查定义域、符号和退化条件。'},
            'checks':checks or []}

records = [
graph('inequality-bridge','x,y>0 且 x+y=1','证明 1/x+1/y≥4','1/x+1/y=1/(xy)（由 x+y=1 且 xy≠0）','若分母正，目标转为 xy≤1/4','利用定和控制乘积，例如检查 (x−y)²≥0','乘除不等式前必须确认 xy>0；等号条件 x=y=1/2', ['inequality-sum-to-product']),
graph('distance-ratio','A、B 为不同定点，PA/PB=2','求 P 的轨迹','设 P(x,y) 并平方距离关系','最终想得到可识别的轨迹方程','把平方距离关系整理到标准形式','k=1 时为垂直平分线；PB 不可为 0'),
graph('ellipse-tangent','P 位于非退化椭圆上','讨论 P 处切线求法','可以用隐式微分或一般直线与曲线联立','切线应刻画该点处的局部变化关系','把已知切点融入一次关系，并与求导结果校验','P 必须在曲线上且为非奇异点', ['ellipse-tangent-at-3-0']),
graph('hyperbola-tangent','P 位于非退化双曲线上','讨论 P 处切线求法','检查隐式微分所给局部关系','由切线的局部性质反推所需一次方程','比较椭圆与双曲线的二次式符号并验证迁移','不得将旧椭圆公式不检查符号直接套用'),
graph('ellipse-focus','PA+PB=10，|AB|=6','判断轨迹及存在条件','三角不等式给出 PA+PB≥|AB|','比较距离和常数与两个定点间距离','从定和条件判定是否存在及可能的轨迹类型','等号是退化线段，小于无解'),
graph('geometric-sum','首项 a1、公比 q、项数 n','求 Sn 且说明特例','错位相减时会出现 1−q 的系数','需要先处理 q=1 是否允许除法','区分 q=1 与 q≠1 的路径','不能除以 0；n 为正整数')]
path=Path(__file__).resolve().parent/'reasoning_graphs.json'
path.write_text(json.dumps({g['problem_id']:g for g in records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Created',len(records),'structured reasoning graphs')
