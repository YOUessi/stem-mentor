"""Six independent narrow theorem-identity checks for the Batch05 six draft theorems.

These verify selected mathematical subclaims, NOT complete proofs, all domain
assumptions, or teacher review. Students must not receive DRAFT teacher content.
"""
from __future__ import annotations

from fractions import Fraction
import pytest
from sympy import I, Matrix, diff, symbols, simplify, sin, cos, trigsimp, limit

from app.deep_knowledge import lessons

a, b, c, d, x, h = symbols("a b c d x h", real=True)


def check_trigonometric_double_angle():
    return all(
        trigsimp(expr) == 0
        for expr in (
            sin(2*x) - 2*sin(x)*cos(x),
            cos(2*x) - (cos(x)**2 - sin(x)**2),
            sin(x)**2 - (1-cos(2*x))/2,
            cos(x)**2 - (1+cos(2*x))/2,
        )
    )


def check_vector_projection_orthogonality():
    u, v = Matrix([a, b]), Matrix([c, d])
    v_sq = v.dot(v)
    assert v_sq != 0  # formal rational expression; b≠0 is a required premise
    p = (u.dot(v)/v_sq)*v
    return simplify((u-p).dot(v)) == 0 and simplify(p[0]*v[1]-p[1]*v[0]) == 0


def check_complex_multiplication_and_guarded_division():
    z, w = a+b*I, c+d*I
    product = (a*c-b*d)+(a*d+b*c)*I
    quotient = ((a*c+b*d)+(b*c-a*d)*I)/(c*c+d*d)
    return (
        simplify(z*w-product) == 0
        and simplify((c*c+d*d)*z-w*((a*c+b*d)+(b*c-a*d)*I)) == 0
        and simplify((z/w)-quotient) == 0
    )


def check_line_plane_membership_distinction():
    n, direction = Matrix([0, 0, 1]), Matrix([1, 0, 0])
    q_outside, q_inside = Matrix([0, 0, 2]), Matrix([0, 0, 0])
    return (
        n.dot(direction) == 0
        and n.dot(q_outside) != 0
        and n.dot(q_inside) == 0
        and Matrix([1, 0, 0]).dot(Matrix([0, 1, 0])) == 0
    )


def check_probability_multiplication():
    omega, event_a, event_b = set(range(1,7)), {1,2,3}, {2,3,4}
    p_a = Fraction(len(event_a),len(omega))
    p_b_given_a = Fraction(len(event_a&event_b),len(event_a))
    p_intersection = Fraction(len(event_a&event_b),len(omega))
    return (
        p_a>0 and p_intersection==p_a*p_b_given_a
        and Fraction(len(event_a&event_b),len(omega))
            != Fraction(len(event_a)*len(event_b),len(omega)**2)
    )


def check_tangent_first_order_remainder():
    f = x**3
    x0, m = 2, diff(f,x).subs(x,2)
    residual = (f.subs(x,x0+h)-f.subs(x,x0)-m*h)
    return m == 12 and simplify(residual-6*h**2-h**3)==0 and limit(residual/h,h,0)==0


CASES = (
    ("math.hs.trig.double-angle-reduction", check_trigonometric_double_angle),
    ("math.hs.vector.projection", check_vector_projection_orthogonality),
    ("math.hs.complex.operations", check_complex_multiplication_and_guarded_division),
    ("math.hs.space.parallel-perpendicular-criteria", check_line_plane_membership_distinction),
    ("math.hs.probability.multiplication", check_probability_multiplication),
    ("math.hs.calculus.tangent-line", check_tangent_first_order_remainder),
)


@pytest.mark.parametrize("lesson_id,oracle", CASES)
def test_narrow_theorem_subclaim_math_without_declaring_proof(lesson_id,oracle):
    doc = next(x for x in lessons() if x.id==lesson_id)
    assert doc.kind == "theorem"
    assert doc.review.status == "REVIEW_PENDING"
    assert doc.teacher_solution_visibility == "TEACHER_ONLY"
    assert oracle()
