"""Batch105 original editorial interpretations of two source pages; not official atomization.

All ranges are 1-based PDFKit lines on physical printed pages, and all lesson
crosslinks are candidate editorial assistance only. No copyrighted source text.
"""
from __future__ import annotations

def A(page,lo,hi,track,kind,title,meaning,precondition,invalid,check,related=()):
    return dict(page=page,start=lo,end=hi,track=track,kind=kind,
                title=title,editorial_interpretation=meaning,
                mathematical_preconditions=precondition,
                misleading_generalization=invalid,
                finite_oracle_key=check,related_draft_ids=list(related))

ATOM_CANDIDATES=[
 A(15,11,11,"COMPULSORY","CONCEPT","集合的属于关系",
   "对于确定的集合A和对象x，命题x∈A必须能判断真或假；属于是元素与集合的关系，不是集合之间的包含关系。",
   "先确定对象和集合的论域以及集合成员判定规则。","把1∈{1,3}误写为{1}∈{1,3}。","membership",("math.hs.batch91.01",)),
 A(15,12,13,"COMPULSORY","METHOD","集合的符号语言表示",
   "把自然语言的共同条件翻译为集合描述法时应保留整数/实数等论域，例如{n∈Z:0≤n<6且n为偶数}={0,2,4}。",
   "明确取值论域、上下界以及不等式是否含等号。","不指定n∈Z便把区间内所有实数也算作偶整数。","set_notation"),
 A(15,14,14,"COMPULSORY","CONCEPT","全集与空集",
   "空集不含元素；补集总要相对于固定全集U讨论，U\\∅=U且∅是U的子集。",
   "全集U需先给定，且补集中的集合确为U的子集。","离开全集直接写绝对补集，或把∅当作含0的集合。","empty_universe",("math.hs.batch91.01",)),
 A(15,16,16,"COMPULSORY","CONCEPT","包含关系与集合相等",
   "A⊆B表示每个A元素也属于B；A=B的充要条件是A⊆B且B⊆A。",
   "集合的相等由成员完全一致决定，不应以元素排列先后判断。","仅由A⊆B就推出A=B，忽略严格包含的可能。","subset_equality"),
 A(15,18,19,"COMPULSORY","CONCEPT","并集的逐元素定义",
   "x∈A∪B当且仅当x∈A或x∈B，包括同时属于两集合；并集不是只取公共元素。",
   "A与B是处于同一明确论域下、成员可判断的集合。","把A∪B直接误算成A∩B，遗漏仅属于其中一个集合的元素。","union",("math.hs.batch94.01",)),
 A(15,18,19,"COMPULSORY","CONCEPT","交集的逐元素定义",
   "x∈A∩B当且仅当x同时属于A与B；交集不同于至少属于一个集合的并集。",
   "A与B的元素关系必须处于可比较的共同论域。","把交集当成两个集合的所有元素。","intersection",("math.hs.batch94.01",)),
 A(15,20,21,"COMPULSORY","CONCEPT","相对全集的补集",
   "若A⊆U，则A在U内的补集是U中不属于A的所有元素；改变U可能改变补集。",
   "必须固定U和A⊆U，符号补集不可脱离U。","把U={1,2,3}与V={1,2,3,4}下同一A的补集视为相等。","complement",("math.hs.batch104.01",)),
 A(15,22,23,"COMPULSORY","METHOD","Venn图区分交并补",
   "Venn图的重叠区域代表交集，两个圆内的全部区域代表并集，全集框中圆外区域代表相对补集。",
   "图形必须包含声明的全集及集合标签；依照元素关系而非圆的大小判断。","只根据区域面积断言元素数量或集合包含关系。","venn",("math.hs.batch94.01",)),
 A(52,10,20,"ELECTIVE_A","CONCEPT","数列极限的ε–N量词定义",
   "a_n→L是指对每个ε>0存在正整数N，所有n≥N均满足|a_n-L|<ε；N可依赖ε。",
   "数列以正整数为索引；量词先后顺序不可颠倒。","只检查一个大n或把N设成对所有ε固定的常数。","sequence_eps_n",("math.hs.batch100.07",)),
 A(52,21,21,"ELECTIVE_A","THEOREM","收敛数列必有界",
   "实数数列若收敛于有限极限，则存在M使全部项的绝对值不超过M；其逆命题一般不成立。",
   "极限必须是有限实数；对有限前缀同样需要检查。","仅因(-1)^n有界就断言它收敛。","convergent_bounded",("math.hs.batch91.11",)),
 A(52,22,29,"ELECTIVE_A","THEOREM","单调有界数列收敛",
   "实数数列若单调递增且有上界，或单调递减且有下界，则收敛于有限实数极限。",
   "要求实数完备性，单调和对应方向有界都不可缺失。","把无上界的递增数列n认作收敛数列。","monotone_bounded",("math.hs.batch96.09",)),
 A(52,30,30,"ELECTIVE_A","METHOD","数列极限四则运算",
   "当a_n→a且b_n→b时，和差积的极限可逐项运算；商法则额外要求b≠0及分母尾项非零。",
   "两数列均收敛于有限实数，商的极限分母非零。","从0/0推导出任意商极限，忽略b=0边界。","sequence_arithmetic",("math.hs.batch94.10",)),
 A(52,31,31,"ELECTIVE_A","CONCEPT","自然常数e的典型极限表征",
   "一种数列极限表征为(1+1/n)^n→e；有限n的数值不等同于常数e。",
   "n取正整数，讨论n趋于无穷而非n=0。","把n=1时的有限项数值2直接写为极限常数e，混淆极限与取值。","e_sequence"),
 A(52,33,38,"ELECTIVE_A","CONCEPT","函数极限的ε–δ量词定义",
   "lim(x→a)f(x)=L意指对每个ε>0存在δ>0，使定义域中所有0<|x-a|<δ均有|f(x)-L|<ε。",
   "a须是定义域的聚点；去心邻域与f(a)可能无定义须分清。","要求f(a)存在且等于L才承认函数极限。","function_eps_delta",("math.hs.batch100.08",)),
 A(52,39,39,"ELECTIVE_A","METHOD","函数极限的四则运算",
   "当f与g在同一点趋近具有有限极限，和差积可分别取极限；商需分母函数极限不为零。",
   "只在定义域的共同去心邻域中运算，商要求尾端分母非零。","在g(x)→0时不加证明直接把极限相除。","function_arithmetic",("math.hs.batch97.04",)),
 A(52,40,45,"ELECTIVE_A","THEOREM","sin x除以x的基本极限",
   "当x以弧度计量且趋于0，x≠0时sin(x)/x→1；不表示x=0处原式有定义。",
   "自变量使用弧度制；仅讨论去心邻域内的极限。","由极限等于1就把sin(π)/π误算成1。","sinc_limit"),
 A(52,46,48,"ELECTIVE_A","THEOREM","(1+x)^(1/x)的基本极限",
   "在实数范围内x→0且x>-1、x≠0时，(1+x)^(1/x)趋于e。",
   "底数1+x必须为正；指数1/x要求x≠0。","把x=1时的有限值2写成e，或在x=-2处使用实指数。","exp_limit"),
]
assert len(ATOM_CANDIDATES)==17

# Whole-page structural cover: includes surrounding preambles, headings and footer.
# Structural spans are NOT equivalent to mathematical atom candidates above.
PAGE_PARTITIONS={
 15:[(1,3,"CONTENT_INTRO"),(4,9,"SETS_OVERVIEW"),(10,14,"SETS_MEMBERSHIP_NOTATION"),
     (15,16,"INCLUSION"),(17,23,"SET_OPERATIONS"),(24,27,"LOGIC_CONTINUES_NEXT_PAGE")],
 52:[(1,8,"ELECTIVE_A_CONTINUED_SCOPE"),(9,31,"SEQUENCE_LIMIT_REQUIREMENTS"),
     (32,48,"FUNCTION_LIMIT_REQUIREMENTS"),(49,49,"PAGE_FOOTER")],
}
CROSS_PAGE_BRIDGES=[
 dict(from_page=14,from_lines=[27,31],to_page=15,to_lines=[1,9],
      track="COMPULSORY",interpretation="必修预备知识目录的过渡说明与第15页集合内容要求相接；不能仅据章节导语计算数学原子。"),
 dict(from_page=51,from_lines=[24,27],to_page=52,to_lines=[2,8],
      track="ELECTIVE_A",interpretation="选修A微积分总述跨页续接；第52页随后展开数列与函数极限的具体要求，不能把总述计为另一条定理。"),
]
