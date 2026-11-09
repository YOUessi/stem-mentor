"""Boundary, equalities, exact arithmetic and invalid domains for Batch62."""
from fractions import Fraction as F
import pytest
from app import kb_batch62_math_scope_witnesses as W

@pytest.mark.parametrize("u,a,expected",[
  ([1,2,3],[1], [2,3]), ([],[],[]),
  ([0,1,2,3],[0,2], [1,3]),([1,2],[1,2],[]),
])
def test_complement_requires_explicit_universe(u,a,expected):
    assert W.finite_complement(u,a)["facts"]["complement"]==expected

@pytest.mark.parametrize("d,t",[
 ([1,2],[True,True]),([1,2],[True,False]),
 ([1],[False]),([1],[True])
])
def test_quantifier_negation_finite(d,t):
    p=W.finite_quantifier_negation(d,t)["facts"]
    assert p["logical_equivalence"] is True
    assert p["forall"] is not p["exists_negated"]

@pytest.mark.parametrize("a,b",[(0,0),(1,1),(1,4),(F(1,4),F(9,4)),(0,9),(12,3),(3,12)])
def test_amgm_square_identity(a,b):
    fact=W.amgm_squared_nonnegative(a,b)["facts"]
    assert fact["gap"]==F(a-b)**2 and fact["nonnegative"]
    assert fact["equality_case"]==(a==b)

@pytest.mark.parametrize("a,b,c,n",[
  (1,0,1,0),(1,-2,1,1),(1,0,-1,2),(2,3,2,0),
  (-1,0,1,2),(3,-6,3,1),(F(1,2),1,F(1,2),1),
])
def test_quadratic_root_count(a,b,c,n):
    assert W.quadratic_real_root_count(a,b,c)["facts"]["real_root_count"]==n

@pytest.mark.parametrize("base,up",[(2,True),(F(1,2),False),(F(3,2),True),(F(1,10),False)])
@pytest.mark.parametrize("n",[-5,-1,0,1,3])
def test_exponential_local_direction(base,up,n):
    facts=W.exponential_integer_power_pair(base,n)["facts"]
    assert facts["increasing_pair"]==up

@pytest.mark.parametrize("b,x",[(2,1),(F(1,2),F(1,3)),(10,1000)])
def test_valid_log_domain_not_identity(b,x):
    assert W.logarithm_real_domain(b,x)["facts"]["valid_domain"] is True

@pytest.mark.parametrize("u,v,valid",[
 ((1,0),(0,1),True),((0,0),(1,1),False),((1,2),(2,4),False),
 ((F(1,3),0),(0,F(3,2)),True),((2,3),(3,2),True)
])
def test_vector_basis_has_nonzero_determinant(u,v,valid):
    assert W.vector_basis_two_dimensions(u,v)["facts"]["is_basis"]==valid

@pytest.mark.parametrize("w,e,expected",[
 ([1,1],{0},F(1,2)),([10,10,10],{0,2},F(2,3)),
 ([1,1,1],set(),F(0)),([3,3],{0,1},F(1)),
])
def test_classical_probability_exact_equal_weight(w,e,expected):
    assert W.equally_likely_event(w,e)["facts"]["probability"]==expected

@pytest.mark.parametrize("x,h",[
 (0,0),(0,1),(2,0),(2,3),(F(2,3),F(1,5)),(-3,-2),(5,-5),
])
def test_differential_differs_from_finite_increment(x,h):
    facts=W.quadratic_differential_vs_delta(x,h)["facts"]
    assert facts["remainder"]==F(h)**2
    assert facts["equality_only_if_zero_h"] is True

@pytest.mark.parametrize("a,b,c,cos",[
 (3,4,5,F(0)),(2,2,2,F(1,2)),(5,5,6,F(7,25)),
 (F(3,2),2,F(5,2),F(0))
])
def test_cosine_law_exact_triangle(a,b,c,cos):
    facts=W.triangle_cosine_ratio(a,b,c)["facts"]
    assert facts["cosine_of_opposite_c"]==cos
    assert facts["in_real_angle_range"]

@pytest.mark.parametrize("f,args",[
 ("finite_complement",([1,2],[3])),
 ("finite_quantifier_negation",([],[])),
 ("finite_quantifier_negation",([0],[1])),
 ("amgm_squared_nonnegative",(-1,2)),
 ("quadratic_real_root_count",(0,1,1)),
 ("exponential_integer_power_pair",(1,3)),
 ("exponential_integer_power_pair",(-2,3)),
 ("exponential_integer_power_pair",(2,99)),
 ("logarithm_real_domain",(1,2)),
 ("logarithm_real_domain",(2,0)),
 ("vector_basis_two_dimensions",([1],[2])),
 ("equally_likely_event",([1,3],[0])),
 ("equally_likely_event",([1,1],[2])),
 ("triangle_cosine_ratio",(1,2,3)),
 ("triangle_cosine_ratio",(-1,2,3)),
 ("quadratic_differential_vs_delta",(0.1,2)),
 ("amgm_squared_nonnegative",(True,0)),
])
def test_invalid_math_premises_fail_closed(f,args):
    with pytest.raises(ValueError):
        getattr(W,f)(*args)

@pytest.mark.parametrize("f,args",[
 ("finite_complement",([1,2],[1])),
 ("finite_quantifier_negation",([1,2],[True,False])),
 ("amgm_squared_nonnegative",(0,3)),
 ("quadratic_real_root_count",(1,0,-4)),
 ("exponential_integer_power_pair",(2,1)),
 ("logarithm_real_domain",(2,3)),
 ("vector_basis_two_dimensions",((1,0),(0,1))),
 ("equally_likely_event",([1,1],[1])),
 ("quadratic_differential_vs_delta",(2,3)),
 ("triangle_cosine_ratio",(3,4,5)),
])
def test_witness_never_certifies_general_theorem_or_student_text(f,args):
    out=getattr(W,f)(*args)
    assert out["scope"]=="FINITE_EXACT_CASE_ONLY"
    assert out["certifies_general_theorem"] is False
    assert out["certifies_student_free_text"] is False
