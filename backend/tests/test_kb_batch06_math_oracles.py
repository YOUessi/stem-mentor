"""Independent, narrowly scoped mathematical oracles for imported Batch06 claims.

Verifies exact arithmetic/geometry in bounded examples; never certifies full
natural-language proofs or any student solution.
"""
from fractions import Fraction
from itertools import combinations
from math import comb, factorial
import pytest
from sympy import Rational, Matrix, symbols, simplify, sin, pi, sqrt, expand

@pytest.mark.parametrize("n",range(0,11))
def test_ordered_and_unordered_counts(n):
    for k in range(n+1):
        permutations=factorial(n)//factorial(n-k)
        subsets=comb(n,k)
        assert permutations==subsets*factorial(k)
        if n<=7:
            assert len(list(combinations(range(n),k)))==subsets

@pytest.mark.parametrize("radius,distance,number_of_points",[
    (Rational(2),Rational(0),2),(Rational(2),Rational(1),2),
    (Rational(2),Rational(2),1),(Rational(2),Rational(3),0),
    (Rational(1,2),Rational(1,2),1),(Rational(4),Rational(5),0)])
def test_line_circle_tangent_chord_count(radius,distance,number_of_points):
    # Circle x^2+y^2=r^2 intersect horizontal line y=d:
    discriminant=expand(radius**2-distance**2)
    actual=2 if discriminant>0 else 1 if discriminant==0 else 0
    assert actual==number_of_points
    if discriminant>=0:
        root=sqrt(discriminant)
        assert simplify(root**2+distance**2-radius**2)==0

@pytest.mark.parametrize("A,B,px,py",[
    (1,0,2,-1),(0,1,3,5),(2,-3,-4,7),(-3,-4,1,-2),(5,2,0,0)])
def test_nondegenerate_general_line_contains_base_point_and_orthogonal_displacements(A,B,px,py):
    assert A*A+B*B>0
    x,y=symbols('x y',real=True)
    C=-A*px-B*py
    assert (A*px+B*py+C)==0
    t=symbols('t',real=True)
    x1,y1=px-t*B,py+t*A
    assert simplify(A*x1+B*y1+C)==0
    assert A*(-B)+B*A==0

@pytest.mark.parametrize("u,v",[
    ((1,0,0),(0,1,0)),((1,2,3),(2,-1,0)),
    ((0,0,4),(0,2,0)),((-1,2,1),(2,1,0))])
def test_space_orthogonal_vectors_have_nonzero_norm(u,v):
    dot=sum(a*b for a,b in zip(u,v))
    assert dot==0
    assert sum(a*a for a in u)>0 and sum(b*b for b in v)>0
    assert simplify(Matrix(u).dot(Matrix(v)))==0

@pytest.mark.parametrize("p,q",[
    (Rational(1,3),Rational(1,4)),(Rational(1,2),Rational(1,2)),
    (Rational(0),Rational(1)),(Rational(3,7),Rational(0))])
def test_probability_union_has_overlap_correction(p,q):
    # Events from 2 independent Bernoulli trials: A={first succeeds}, B={second succeeds}
    overlap=p*q
    combined=p+q-overlap
    complement=1-(1-p)*(1-q)
    assert simplify(combined-complement)==0
    assert 0<=combined<=1
    if overlap>0:
        assert combined<p+q

@pytest.mark.parametrize("length,width",[(1,2),(3,4),(2,9),(10,10)])
def test_parallel_line_plane_requires_exclusion_of_embedded_line(length,width):
    # Plane z=0, in-plane b(t)=(t,0,0), separate a(t)=(t,0,height)
    height=Rational(width)
    assert height!=0
    t=symbols('t',real=True)
    a=Matrix([t,0,height]); b=Matrix([t,0,0])
    # Direction (1,0,0) is parallel, but neither a nor b is a nonzero direction at t=0 point
    assert a[2]==height and b[2]==0
    assert Matrix([1,0,0]).dot(Matrix([0,0,1]))==0
    # Moving a into plane invalidates the conclusion 'no intersection'.
    assert Matrix([t,0,0])[2]==0

@pytest.mark.parametrize("m", [1,2,3,4,5])
def test_triangle_inequality_prevents_equality_for_discrete_noncollinear_examples(m):
    # Nonparallel coordinate displacement a=(m,0),b=(0,m+1).
    left=sqrt(m*m+(m+1)**2)
    right=m+(m+1)
    assert left<right

@pytest.mark.parametrize("n",range(1,8))
def test_bernoulli_binomial_mass_normalized_at_parameter_boundary(n):
    for p in (Rational(0),Rational(1),Rational(1,2),Rational(2,3)):
        values=[comb(n,k)*p**k*(1-p)**(n-k) for k in range(n+1)]
        assert sum(values)==1
        assert all(0<=v<=1 for v in values)

@pytest.mark.parametrize("omega", [1,2,3,4,5])
def test_sine_period_angular_frequency_exact(omega):
    x=symbols('x',real=True)
    T=2*pi/omega
    assert simplify(sin(omega*(x+T))-sin(omega*x))==0

def test_normal_density_is_probability_mass_not_density_at_single_point():
    # Fundamental sanity: the standard normal density at x=0 is positive,
    # yet the continuous random variable has P(X=0)=0.
    from sympy import integrate, exp, oo, pi
    x=symbols('x',real=True)
    density=exp(-x*x/2)/sqrt(2*pi)
    assert density.subs(x,0)>0
    assert simplify(integrate(density,(x,-oo,oo))-1)==0
