"""Independent bounded exact witnesses for Batch107 editorial source candidates.

These compute *finite examples or exact symbolic identities* only. They never
certify general theorems, student free-text reasoning or teacher approval.
"""
from __future__ import annotations

from sympy import Matrix, Rational as Q, symbols, sqrt, pi, integrate, Abs, eye, simplify

x = symbols("x", real=True)


def check(key: str) -> dict:
    if not isinstance(key, str):
        raise ValueError("unsupported bounded witness: invalid key type")
    if key == "amgm_opt":
        good = Q(3)*Q(7) <= Q(25) and Q(5)*Q(5) == Q(25)
        bad = Q(11)*Q(-1) >= 0  # invalid if domain of nonnegative parts ignored
        detail = "Nonnegative parts summing to 10 have product <=25; negative part fails."
    elif key == "quad_two":
        f = x*x-5*x+6
        good = simplify(f.subs(x,2))==0 and simplify(f.subs(x,3))==0 and 25-24>0
        bad = (0-4 > 0)  # x²+1 cannot be asserted to have two real roots
        detail = "Positive discriminant and two distinct real roots; x²+1 violates."
    elif key == "quad_tangent":
        f=(x-1)**2
        good = f.subs(x,1)==0 and 4-4==0
        bad = (0-4==0)  # x²+1 has negative discriminant
        detail = "Repeated root has discriminant zero, not every quadratic does."
    elif key == "quad_none":
        good = (0-4 < 0) and (x*x+1).subs(x,0)>0
        bad = (25-24 < 0)  # x²-5x+6 has positive discriminant
        detail = "Negative discriminant has no real roots; positive discriminant differs."
    elif key == "zero_graph":
        good = (x*x-4).subs(x,2)==0
        bad = (x*x+1).subs(x,0)==0
        detail = "A zero is an x-axis intersection; x²+1 has no zero at 0."
    elif key == "quad_positive":
        f=x*x-5*x+6
        good = f.subs(x,0)>0 and f.subs(x,Q(5,2))<0
        bad = f.subs(x,Q(5,2))>0
        detail = "Upward parabola positive outside two roots, negative between."
    elif key == "quad_nonnegative":
        f=(x-1)**2
        good = f.subs(x,1)==0 and f.subs(x,3)>0
        bad = f.subs(x,1)>0
        detail = "For squared factor, >= includes repeated root; > excludes it."
    elif key == "quad_linear":
        good = (2*2-4==0) and (2*3-4!=0)
        bad = (2*3-4==0)
        detail = "When quadratic coefficient is zero, solve bx+c=0 instead."
    elif key == "ineq_sets":
        good = {0,3} == {0,3} and 2 not in {0,3}
        bad = 2 in {0,3}
        detail = "A solution set lists values satisfying inequality; not all real numbers."
    elif key == "graph_sign":
        f=x*x-1
        good = f.subs(x,0)<0 and f.subs(x,2)>0
        bad = f.subs(x,0)>0
        detail = "Function sign, equation zero and graph x-axis location are related."
    elif key == "singleton":
        good = 2 in {2} and {2} != 2
        bad = ({2}==2)
        detail = "Membership of an object is not identity with its singleton set."
    elif key == "signed_area":
        good = integrate(2*x-1,(x,0,1))==0 and integrate(Abs(2*x-1),(x,0,1))==Q(1,2)
        bad = integrate(Abs(2*x-1),(x,0,1))==0
        detail = "Geometric area uses absolute vertical difference; signed area cancels."
    elif key == "solid_volume":
        good = simplify(integrate(pi*x*x,(x,0,1))-pi/3)==0
        bad = simplify(integrate(pi*x,(x,0,1))-pi/3)==0
        detail = "Disk volume integrates pi times radius squared, not the radius."
    elif key == "work_integral":
        good = integrate(x,(x,0,2))==2
        bad = 2*2==2
        detail = "Variable force work is integral over displacement, not final force times distance."
    elif key == "centroid_integral":
        good = integrate(x,(x,0,2))/integrate(1,(x,0,2))==1
        bad = integrate(x,(x,0,2))/integrate(1,(x,0,2))==2
        detail = "Centroid of uniform segment is mass-normalized first moment."
    elif key == "dot_product":
        u,v=Matrix([1,0,0]),Matrix([0,1,0])
        good = u.dot(v)==0
        bad = Matrix([1,0,0]).dot(Matrix([1,0,0]))==0
        detail = "Orthogonal nonzero vectors have dot product zero; a vector with itself does not."
    elif key == "cross_product":
        u,v=Matrix([1,0,0]),Matrix([0,1,0])
        good = u.cross(v)==Matrix([0,0,1]) and u.cross(v).dot(u)==0
        bad = u.cross(u)==Matrix([0,0,1])
        detail = "Cross product is perpendicular, with zero result on parallel vectors."
    elif key == "projection":
        u,v=Matrix([2,3,0]),Matrix([1,0,0])
        proj=(u.dot(v)/v.dot(v))*v
        good = proj==Matrix([2,0,0])
        bad = proj==Matrix([0,3,0])
        detail = "Projection formula requires nonzero target; projection is along target vector."
    elif key == "linear_dependence":
        u,v,w=Matrix([1,0,0]),Matrix([0,1,0]),Matrix([1,1,0])
        good = Matrix.hstack(u,v,w).det()==0
        bad = eye(3).det()==0
        detail = "Three 3D vectors linearly dependent iff determinant zero."
    elif key == "subspace":
        u=Matrix([1,0,0]);v=Matrix([0,1,0]); w=Matrix([0,0,1])
        good = (2*u-3*v)==Matrix([2,-3,0])
        bad = w==2*u-3*v
        detail = "Span of e1,e2 stays in plane z=0; e3 is not in this subspace."
    elif key == "matrix_multiply":
        a=Matrix([[1,1],[0,1]]);b=Matrix([[1,0],[0,2]])
        good = a*b==Matrix([[1,2],[0,2]])
        bad = a*b==b*a
        detail = "Matrix multiplication is dimension-sensitive and generally noncommutative."
    elif key == "orthogonal":
        q=Matrix([[0,-1,0],[1,0,0],[0,0,1]])
        good = q.T*q==eye(3) and (q*Matrix([3,4,0])).dot(q*Matrix([3,4,0]))==25
        bad = Matrix.diag(2,1,1).T*Matrix.diag(2,1,1)==eye(3)
        detail = "Orthogonal Q preserves squared length; arbitrary diagonal scaling does not."
    elif key == "determinant":
        good = Matrix.diag(1,2,3).det()==6
        bad = Matrix.diag(1,0,3).det()!=0
        detail = "A zero determinant marks singular matrix; nonzero determinant permits inverse."
    else:
        raise ValueError("unsupported bounded witness: "+key)
    if not bool(good) or bool(bad):
        raise ValueError("finite witness or negative rejection failed for "+key)
    return {
        "oracle_key":key,
        "finite_exact_positive_passed":True,
        "invalid_generalization_rejected":True,
        "computed_explanation":detail,
        "universal_proof_certified":False,
        "arbitrary_student_step_verified":False,
        "teacher_approved":False,
    }
