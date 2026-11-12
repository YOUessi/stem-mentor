"""Independent finite/symbolic checks for all ten Batch108 lessons.

No finite witness is a proof certificate for the authored universal theorem.
"""
import pytest
import sympy as sp

M = sp.Matrix


def exact_witness(case):
    if case == "elementary_rows":
        a=M([[1,1,0],[0,1,1],[1,0,1]]);b=M([3,4,5]);sol=a.inv()*b
        e=M([[1,2,0],[0,1,0],[0,0,1]])
        positive=(e*a*sol==e*b and e.det()!=0)
        zero=M([[0,0,0],[0,1,0],[0,0,1]])
        negative=(zero.det()==0 and (zero*a).rank()<a.rank())
    elif case=="homogeneous_nonzero":
        a=M([[1,2,3],[2,4,6],[1,1,1]]);v=a.nullspace()[0]
        positive=(a.det()==0 and a*v==M.zeros(3,1) and v!=M.zeros(3,1))
        negative=(M.eye(3).det()!=0 and M.eye(3).nullspace()==[])
    elif case=="rank_consistency":
        a=M([[1,0,0],[0,1,0],[0,0,0]])
        yes=M([2,3,0]);no=M([2,3,1]);positive=(a.rank()==a.row_join(yes).rank())
        negative=(a.rank()!=a.row_join(no).rank())
    elif case=="affine_kernel":
        a=M([[1,1,0],[0,1,1],[0,0,0]]);p=M([1,0,2]);v=a.nullspace()[0]
        positive=(a*(p+7*v)==a*p and a*v==M.zeros(3,1))
        negative=(a*(p+M([1,0,0]))!=a*p)
    elif case=="cramer":
        a=M([[2,0,0],[0,3,0],[0,0,5]]);b=M([4,9,10]);x=a.inv()*b
        d=[]
        for i in range(3):
            ai=a.copy();ai[:,i]=b;d.append(ai.det()/a.det())
        positive=(M(d)==x and a.det()!=0)
        negative=(M.diag(1,1,0).det()==0)
    elif case=="plane_normal":
        n=M([2,-1,3]);p=M([1,2,0]);q=p+M([1,2,0])
        positive=(n.dot(q-p)==0 and n!=M.zeros(3,1))
        negative=(M.zeros(3,1).dot(q-p)==0)
    elif case=="line_direction":
        p=M([1,3,-2]);v=M([2,0,1]);positive=(p+2*v!=p+3*v)
        negative=(p+2*M.zeros(3,1)==p+3*M.zeros(3,1))
    elif case=="point_plane_distance":
        n=M([3,0,4]);p=M([3,0,4]);q=M.zeros(3,1)
        foot=p-n*(n.dot(p-q)/n.dot(n))
        positive=(n.dot(foot-q)==0 and (p-foot).norm()==sp.Rational(25,5))
        negative=(n.dot(-p-q)/n.norm()<0)
    elif case=="reflection":
        j=M.diag(1,-1);u=M([2,3]);v=M([-1,4]);k=M.diag(1,2)
        positive=((j*u-j*v).norm()==(u-v).norm() and j.T*j==sp.eye(2))
        negative=((k*u-k*v).norm()!=(u-v).norm())
    elif case=="rotation":
        t=sp.symbols('t',real=True)
        r=M([[sp.cos(t),-sp.sin(t)],[sp.sin(t),sp.cos(t)]])
        h=M([[1,2],[0,1]])
        positive=(sp.simplify(r.T*r-sp.eye(2))==M.zeros(2,2))
        negative=(h.det()==1 and h.T*h!=sp.eye(2))
    else:raise AssertionError(case)
    return bool(positive),bool(negative)

CASES=["elementary_rows","homogeneous_nonzero","rank_consistency","affine_kernel",
       "cramer","plane_normal","line_direction","point_plane_distance",
       "reflection","rotation"]

@pytest.mark.parametrize("case",CASES)
def test_independent_exact_positive(case):
    assert exact_witness(case)[0], case

@pytest.mark.parametrize("case",CASES)
def test_independent_invalid_generalization(case):
    assert exact_witness(case)[1], case
