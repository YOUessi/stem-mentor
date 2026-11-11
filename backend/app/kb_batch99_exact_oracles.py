"""Exact finite witnesses for Batch99 editorial topics; NOT formal proofs.

Each callable checks its own preconditions. No LLM judgement or auto-approval.
"""
from __future__ import annotations
from fractions import Fraction as F

def q(value):
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError("exact rational input required")
    return F(value)

def vector(values, dimension):
    if len(values) != dimension:
        raise ValueError("vector dimension mismatch")
    return tuple(q(x) for x in values)

def dot(a,b):
    if len(a) != len(b):
        raise ValueError("dot-product dimension mismatch")
    return sum((x*y for x,y in zip(a,b)),F(0))

def two_point_direction(a,b):
    a,b = vector(a,2),vector(b,2)
    d = tuple(y-x for x,y in zip(a,b))
    if d==(0,0): raise ValueError("two distinct points required")
    return d

def angle_cosine_3d(a,b):
    a,b = vector(a,3),vector(b,3)
    norms = dot(a,a)*dot(b,b)
    if norms==0: raise ValueError("zero vector has undefined angle")
    return (dot(a,b)**2)/norms, dot(a,b) == 0

def line_intersection_xy(a,d,b,e):
    a,d,b,e = [vector(x,2) for x in (a,d,b,e)]
    if dot(d,d)==0 or dot(e,e)==0: raise ValueError("nonzero directions")
    determinant = d[0]*e[1]-d[1]*e[0]
    if determinant==0: raise ValueError("parallel/collinear branch is separate")
    diff=(b[0]-a[0], b[1]-a[1])
    t=(diff[0]*e[1]-diff[1]*e[0])/determinant
    return (a[0]+t*d[0],a[1]+t*d[1])

def line_plane_classify(point,direction,normal,offset):
    p,d,n=vector(point,3),vector(direction,3),vector(normal,3)
    c=q(offset)
    if dot(d,d)==0 or dot(n,n)==0: raise ValueError("nonzero direction and normal")
    slope=dot(d,n);residual=dot(p,n)-c
    if slope==0:return "CONTAINED" if residual==0 else "PARALLEL_DISJOINT"
    return "ONE_INTERSECTION"

def orthogonal_matrix_2d(matrix):
    if len(matrix)!=2:raise ValueError("2 by 2 matrix required")
    a,b=vector(matrix[0],2),vector(matrix[1],2)
    return dot(a,a)==dot(b,b)==1 and dot(a,b)==0

def reflection_fixed_point(Q,b):
    """Only for diagonal (1,-1) reflection linear part; disallow other matrices."""
    if not orthogonal_matrix_2d(Q) or Q != ((1,0),(0,-1)):
        raise ValueError("requires exact diagonal reflection Q")
    b=vector(b,2)
    # (I-Q)x=b --> 0*x=b_x, 2*y=b_y.
    return b[0]==0

def determinant_3d(M):
    a,b,c=(vector(row,3) for row in M)
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])

def is_orthogonal_3d(M):
    rows=tuple(vector(row,3) for row in M)
    return all(dot(rows[i],rows[j]) == (1 if i==j else 0) for i in range(3) for j in range(3))

def epsilon_n_guarantee(c,eps,N):
    c,eps=q(c),q(eps)
    if c<0 or eps<=0 or isinstance(N,bool) or not isinstance(N,int) or N<=0:
        raise ValueError("c>=0, epsilon>0, N positive integer")
    return c/N < eps

def epsilon_delta_square_at_two(eps,delta):
    eps,delta=q(eps),q(delta)
    if eps<=0 or delta<=0:raise ValueError("strictly positive epsilon and delta")
    # For |x-2|<δ<=1, |x+2|<5, so |x²-4|<5δ <= ε.
    return delta<=1 and 5*delta<=eps

def quadratic_range(a,b,c,lo,hi):
    a,b,c,lo,hi=map(q,(a,b,c,lo,hi))
    if lo>hi:raise ValueError("closed interval endpoints reversed")
    candidates=[lo,hi]
    if a!=0:
        root=-b/(2*a)
        if lo<=root<=hi:candidates.append(root)
    ys=[a*x*x+b*x+c for x in candidates]
    return min(ys),max(ys)

def integral_affine(a,b,lo,hi):
    a,b,lo,hi=map(q,(a,b,lo,hi))
    if lo>hi:raise ValueError("signed integral requires ordered domain for this checker")
    return a*(hi*hi-lo*lo)/2+b*(hi-lo)

def rectangle_linear_extrema(a,b,c,xlo,xhi,ylo,yhi):
    a,b,c,xlo,xhi,ylo,yhi=map(q,(a,b,c,xlo,xhi,ylo,yhi))
    if xlo>xhi or ylo>yhi:raise ValueError("nonempty closed rectangle required")
    values=[a*x+b*y+c for x in (xlo,xhi) for y in (ylo,yhi)]
    return min(values), max(values)

def bivariate_covariance_determinant(sx,sy,rho):
    sx,sy,rho=map(q,(sx,sy,rho))
    if sx<=0 or sy<=0 or abs(rho)>=1:
        raise ValueError("nondegenerate joint normal requires sigma positive and |rho|<1")
    return sx*sx*sy*sy*(1-rho*rho)

def check(index):
    """Independent exact positive and negative witness for a selected Batch99 scope."""
    if isinstance(index,bool) or not isinstance(index,int) or not 1<=index<=12:
        raise ValueError("unsupported witness index")
    def rejects(fn):
        try:fn()
        except ValueError:return True
        return False
    checks={
        1:(lambda:two_point_direction((0,0),(2,2))==(2,2),
           lambda:two_point_direction((1,1),(1,1))),
        2:(lambda:angle_cosine_3d((1,0,0),(0,1,0))==(F(0),True),
           lambda:angle_cosine_3d((0,0,0),(1,0,0))),
        3:(lambda:line_intersection_xy((0,0),(1,0),(0,0),(0,1))==(0,0),
           lambda:line_intersection_xy((0,0),(1,0),(0,1),(1,0))),
        4:(lambda:line_plane_classify((0,0,0),(1,0,0),(0,0,1),0)=="CONTAINED" and
                   line_plane_classify((0,0,1),(1,0,0),(0,0,1),0)=="PARALLEL_DISJOINT",
           lambda:line_plane_classify((0,0,1),(0,0,0),(0,0,1),0)),
        5:(lambda:reflection_fixed_point(((1,0),(0,-1)),(0,2)) and
                   not reflection_fixed_point(((1,0),(0,-1)),(1,0)),
           lambda:reflection_fixed_point(((2,0),(0,-1)),(0,0))),
        6:(lambda:is_orthogonal_3d(((0,-1,0),(1,0,0),(0,0,1))) and
                   not is_orthogonal_3d(((2,0,0),(0,F(1,2),0),(0,0,1))),
           lambda:is_orthogonal_3d(((1,0),(0,1)))),
        7:(lambda:epsilon_n_guarantee(2,F(1,10),21) and
                   not epsilon_n_guarantee(2,F(1,10),20),
           lambda:epsilon_n_guarantee(2,0,20)),
        8:(lambda:epsilon_delta_square_at_two(F(1,10),F(1,50)) and
                   not epsilon_delta_square_at_two(F(1,10),F(1,5)),
           lambda:epsilon_delta_square_at_two(F(1,10),0)),
        9:(lambda:quadratic_range(1,-2,0,0,3)==(-1,3),
           lambda:quadratic_range(1,-2,0,3,0)),
        10:(lambda:integral_affine(1,0,-1,1)==0 and integral_affine(1,0,-1,0)==F(-1,2),
            lambda:integral_affine(1,0,1,-1)),
        11:(lambda:rectangle_linear_extrema(1,1,0,0,1,0,1)==(0,2),
            lambda:rectangle_linear_extrema(1,1,0,1,0,0,1)),
        12:(lambda:bivariate_covariance_determinant(2,3,F(1,2))==27,
            lambda:bivariate_covariance_determinant(2,3,1))
    }
    yes, bad=checks[index]
    result=bool(yes())
    rejection=rejects(bad)
    if not result or not rejection:
        raise AssertionError(f"independent finite mathematical witness failed at {index}")
    return {"index":index,"finite_positive_case":result,
            "invalid_premise_rejected":rejection,
            "general_theorem_certified":False,"teacher_approved":False,
            "student_publishable":False}

def verify_all():
    return [check(i) for i in range(1,13)]
