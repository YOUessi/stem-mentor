"""Batch83 independent rational arithmetic for five bounded cross-topic non-equivalence examples.

Finite witnesses only. This module neither proves the general theorem nor adjudicates the
official syllabus and is never a student solution-verification authority.
"""
from fractions import Fraction as Q

RELATIONS = (
 ("NECESSARY_CONDITION_VS_EXTREMUM", "KB80-A016-L008", "KB80-A058-L031"),
 ("GEOMETRIC_VS_REGRESSION", "KB80-A038-L027", "KB80-A066-L016"),
 ("CONTINUOUS_VS_DIFFERENTIABLE", "KB80-A039-L009", "KB80-A053-L003"),
 ("DIFFERENTIAL_VS_INCREMENT", "KB80-A053-L006", "KB80-A058-L035"),
 ("SIGNED_INTEGRAL_VS_AREA", "KB80-A059-L002", "KB80-A059-L009"),
)

def finite_witnesses():
    """All arithmetic exact. Narrative scope remains unapproved."""
    # x^3 has derivative zero at 0, but takes values below and above f(0).
    cubic = {x: Q(x) ** 3 for x in (-1, 0, 1)}
    assert cubic[-1] < cubic[0] < cubic[1]
    derivative_zero = Q(0)
    # A line through three observations need not form a geometric sequence.
    y = [Q(1) + Q(2) * x for x in range(3)]
    ratios = (y[1] / y[0], y[2] / y[1])
    assert ratios[0] != ratios[1] and y == [Q(1), Q(3), Q(5)]
    # |x| is continuous at zero, while the left and right difference quotients disagree.
    h = Q(1, 4)
    left_slope = (abs(-h) - abs(Q(0))) / (-h)
    right_slope = (abs(h) - abs(Q(0))) / h
    assert (left_slope, right_slope) == (-1, 1)
    # df=f'(1)dx=2*(1/2)=1, but exact delta f = (3/2)^2-1=5/4.
    dx = Q(1, 2)
    linear_part = Q(2) * dx
    true_increment = (Q(1) + dx) ** 2 - Q(1)
    assert true_increment - linear_part == Q(1, 4)
    # Integral of f=-1 on [0,1] is -1, whereas geometric area is +1.
    signed_integral, geometric_area = Q(-1), Q(1)
    assert signed_integral != geometric_area
    data = (
      {"op": RELATIONS[0][0], "finite_data": {"f_minus_one": str(cubic[-1]), "f_zero": str(cubic[0]), "f_one": str(cubic[1]), "f_prime_zero": str(derivative_zero)},
       "distinction": "导数为零只是局部可微极值的一项必要条件，三次函数原点不是极值。"},
      {"op": RELATIONS[1][0], "finite_data": {"observations": list(map(str,y)), "successive_ratios": list(map(str,ratios))},
       "distinction": "线性趋势可完全拟合有限观察，但相邻比不恒定，不得认作等比数列。"},
      {"op": RELATIONS[2][0], "finite_data": {"left_difference_quotient": str(left_slope), "right_difference_quotient": str(right_slope)},
       "distinction": "绝对值函数在零点连续但左右差商不同，连续性并不保证可导性。"},
      {"op": RELATIONS[3][0], "finite_data": {"differential": str(linear_part), "actual_change": str(true_increment), "remainder": str(true_increment-linear_part)},
       "distinction": "微分表示线性主部，非零增量的实际函数变化还有高阶余项。"},
      {"op": RELATIONS[4][0], "finite_data": {"signed_integral": str(signed_integral), "unsigned_area": str(geometric_area)},
       "distinction": "负常值函数在正长度区间积分为负，几何面积却为正。"},
    )
    assert len(data) == len(RELATIONS)
    return [{
        **entry, "left_anchor": relation[1], "right_anchor": relation[2],
        "evidence_scope": "FINITE_EXACT_COUNTEREXAMPLE_ONLY",
        "general_equivalence_certified": False,
        "teacher_approved": False,
    } for entry, relation in zip(data, RELATIONS)]
