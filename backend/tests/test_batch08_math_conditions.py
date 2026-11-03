"""Independent exact counterexamples/domain guards, not formal proof certification."""
from __future__ import annotations
from fractions import Fraction
from math import comb

import pytest
from sympy import Symbol, diff, simplify, sqrt

x = Symbol("x", real=True)


@pytest.mark.parametrize("mask_a",range(16))
@pytest.mark.parametrize("mask_b",range(16))
def test_demorgan_for_all_4_element_subsets(mask_a,mask_b):
    U = {0,1,2,3}
    A = {i for i in U if (mask_a >> i) & 1}
    B = {i for i in U if (mask_b >> i) & 1}
    assert U-(A|B) == (U-A)&(U-B)
    assert U-(A&B) == (U-A)|(U-B)


@pytest.mark.parametrize("a,b", [
    (-2,-5),(-1,-3),(-1,1),(0,0),(0,7),(2,3),(5,-2),(10,15)
])
def test_amgm_requires_nonnegative_real_numbers(a,b):
    if a >= 0 and b >= 0:
        assert (a+b)**2 >= 4*a*b
        assert a+b >= 2*float(sqrt(a*b)) - 1e-12
    else:
        assert a < 0 or b < 0


@pytest.mark.parametrize("p,q",[
    (0,0),(0,1),(2,3),(-2,3),(10,-4),(-7,-5)
])
def test_finite_geometric_sum_with_separate_q_equals_one(p,q):
    actual = sum(p*q**i for i in range(1,9))
    if q == 1:
        assert actual == 8*p
    else:
        assert actual*(1-q) == p*q*(1-q**8)


@pytest.mark.parametrize("a,b,c", [
    (1,2,3),(2,0,4),(-3,2,-1),(0,0,0),(-1,-1,7),(4,9,-5)
])
def test_polynomial_product_derivative_rule(a,b,c):
    f = x*x+a*x+b
    g = x**3+c*x+1
    assert simplify(diff(f*g,x) - (diff(f,x)*g+f*diff(g,x))) == 0


@pytest.mark.parametrize("u,v,w",[
    (1,0,0),(1,3,2),(0,3,-4),(5,-4,3),(-2,-2,0),(1,1,1)
])
def test_vector_projection_requires_nonzero_direction(u,v,w):
    direction = [u,v,w]
    norm = sum(t*t for t in direction)
    vector = [2,-1,4]
    if norm == 0:
        with pytest.raises(ZeroDivisionError):
            _ = Fraction(1,norm)
    else:
        coefficient = Fraction(sum(a*b for a,b in zip(vector,direction)),norm)
        projection = [coefficient*t for t in direction]
        residual = [Fraction(t)-z for t,z in zip(vector,projection)]
        assert sum(a*b for a,b in zip(residual,direction)) == 0


@pytest.mark.parametrize("r,d",[(1,0),(1,1),(2,0),(2,1),(3,2),(3,3),(3,4),(5,-1)])
def test_circle_chord_real_length_guard(r,d):
    if d < 0 or d > r:
        assert not (0 <= d <= r)
        return
    half_chord_sq = r*r-d*d
    assert half_chord_sq >= 0
    if d == r:
        assert half_chord_sq == 0
    else:
        assert half_chord_sq > 0


@pytest.mark.parametrize("data,scale,offset",[
    ((1,2,3),1,0), ((1,2,3),-1,7), ((0,2,4),2,-4),
    ((-2,1,5),0,10), ((2,2,2),5,1), ((0,1,3,9),-3,2)
])
def test_variance_affine_scaling_exact(data,scale,offset):
    def mean(values):
        return sum(map(Fraction,values))/len(values)
    def variance(values):
        mu = mean(values)
        return sum((Fraction(z)-mu)**2 for z in values)/len(values)
    transformed = [scale*z+offset for z in data]
    assert variance(transformed) == scale**2 * variance(data)
    assert mean(transformed) == scale*mean(data)+offset


@pytest.mark.parametrize("parts,likelihood",[
    ((Fraction(1,2),Fraction(1,2)),(Fraction(1,3),Fraction(2,3))),
    ((Fraction(1,3),Fraction(2,3)),(Fraction(0),Fraction(1))),
    ((Fraction(1,4),Fraction(3,4)),(Fraction(1),Fraction(0))),
    ((Fraction(1),Fraction(0)),(Fraction(1),Fraction(1))),
    ((Fraction(0),Fraction(1)),(Fraction(0),Fraction(0))),
])
def test_bayes_partition_denominator_guard(parts,likelihood):
    assert sum(parts) == 1
    marginal = sum(p*q for p,q in zip(parts,likelihood))
    if marginal == 0:
        assert all(p*q == 0 for p,q in zip(parts,likelihood))
        return
    posteriors = [(p*q)/marginal for p,q in zip(parts,likelihood)]
    assert sum(posteriors) == 1
    assert all(0 <= z <= 1 for z in posteriors)


@pytest.mark.parametrize("A,B", [
    ((0,1,2),(2,3)), ((1,2),(3,4)), ((),(1,2)), ((1,),(1,)),
    ((0,2,3),(0,2,3)), ((1,2,3),()), ((),())
])
def test_inclusion_exclusion_finite_sets(A,B):
    A,B = set(A),set(B)
    assert len(A|B) == len(A)+len(B)-len(A&B)
    if A&B:
        assert len(A|B) < len(A)+len(B)


@pytest.mark.parametrize("a,b",[(1,0),(-1,0),(0,1),(2,3),(-4,-1)])
def test_logarithm_outer_domain_cannot_be_ignored(a,b):
    # f(t)=ln(t), g(x)=a*x+b. The domain of f composed g
    # additionally requires a*x+b > 0, regardless of g's total domain.
    val = a*2+b
    if val <= 0:
        assert not (val > 0)
    else:
        assert val > 0


@pytest.mark.parametrize("n,k",[(0,0),(1,0),(1,1),(3,0),(3,1),(3,2),(3,3),(8,4)])
def test_binomial_combinatorial_identity_boundary(n,k):
    assert comb(n,k) == comb(n,n-k)
    assert comb(n,k) >= 1
    if 0 < k < n:
        assert comb(n,k) == comb(n-1,k-1)+comb(n-1,k)
