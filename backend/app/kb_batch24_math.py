"""Bounded exact-rational oracles for Batch24 math examples.

All outcomes concern FINITE INPUTS ONLY, never whole-proof soundness, official
syllabus equivalence, teacher approval, or arbitrary free-form student steps.
No eval, exec, symbolic string parsing or network calls.
"""
from fractions import Fraction
from math import comb
import re

SUPPORTED=frozenset({
 "strict_inequality_scale","quadratic_discriminant","am_gm_nonnegative",
 "finite_geometric_sum","hypergeometric_point_mass","slope_nonvertical",
 "finite_quantifier_negation","two_by_two_expected_cell"
})
_NUM=re.compile(r"^[+-]?\d{1,8}(?:/[1-9]\d{0,7})?$")
def _rational(value):
    if isinstance(value,bool) or not isinstance(value,(int,str)):
        raise ValueError("Only bounded exact integer/fraction data accepted")
    s=str(value)
    if not _NUM.fullmatch(s):raise ValueError("Untrusted rational input")
    v=Fraction(s)
    if abs(v.numerator)>1_000_000 or v.denominator>1_000_000:
        raise ValueError("Rational magnitude beyond finite oracle budget")
    return v
def _integer(value):
    v=_rational(value)
    if v.denominator!=1:raise ValueError("Expected exact integer")
    return int(v)
def _serialize(v):
    return str(v) if isinstance(v,Fraction) else v
def evaluate(op,payload):
    base=dict(operation=op,student_step_verified=False,complete_theorem_certified=False,
              teacher_approved=False,scope="EXACT_FINITE_INPUT_ONLY")
    if op not in SUPPORTED:return dict(base,status="UNSUPPORTED",reason="Unknown or free-text proof operation")
    if not isinstance(payload,dict):return dict(base,status="CONDITIONS_NOT_ESTABLISHED",reason="No validated finite parameters")
    expected={
      "strict_inequality_scale":{"a","b","c"},
      "quadratic_discriminant":{"a","b","c"},
      "am_gm_nonnegative":{"a","b"},
      "finite_geometric_sum":{"a1","q","n"},
      "hypergeometric_point_mass":{"N","K","n","k"},
      "slope_nonvertical":{"x1","x2","y1","y2"},
      "finite_quantifier_negation":{"truth_values"},
      "two_by_two_expected_cell":{"row","column","total"}
    }[op]
    if set(payload)!=expected:return dict(base,status="CONDITIONS_NOT_ESTABLISHED",reason="Missing or unexpected input fields")
    try:
        if op=="finite_quantifier_negation":
            seq=payload["truth_values"]
            if not isinstance(seq,list) or not(1<=len(seq)<=64) or any(type(x)!=bool for x in seq):
                raise ValueError("A finite, nonempty list of booleans is required")
            w=dict(not_forall=not all(seq),exists_counterexample=any(not x for x in seq),
                   not_exists=not any(seq),forall_negated=all(not x for x in seq),
                   finite_domain_size=len(seq))
        elif op=="hypergeometric_point_mass":
            N,K,n,k=(_integer(payload[x]) for x in ("N","K","n","k"))
            if not(1<=N<=100 and 0<=K<=N and 0<=n<=N and max(0,n-(N-K))<=k<=min(n,K)):
                raise ValueError("Invalid sampling count or hypergeometric support")
            p=Fraction(comb(K,k)*comb(N-K,n-k),comb(N,n))
            w=dict(probability=_serialize(p),support_min=max(0,n-(N-K)),
                   support_max=min(n,K),total_combinations=comb(N,n))
        elif op=="finite_geometric_sum":
            a,q=(_rational(payload[x]) for x in ("a1","q"))
            n=_integer(payload["n"])
            if not(1<=n<=80):raise ValueError("n must be 1..80")
            if abs(a.numerator)>1000 or a.denominator>1000 or abs(q.numerator)>1000 or q.denominator>1000:
                raise ValueError("Resource limit for rational powers")
            s=sum((a*q**j for j in range(n)),Fraction())
            closed=n*a if q==1 else a*(1-q**n)/(1-q)
            if s!=closed:raise ArithmeticError("Independent finite sum mismatch")
            if s.numerator.bit_length()>25000 or s.denominator.bit_length()>25000:
                raise ValueError("Exact result exceeds guard")
            w=dict(sum=_serialize(s),formula=_serialize(closed),branch="Q_EQUALS_ONE" if q==1 else "Q_NOT_ONE")
        elif op=="strict_inequality_scale":
            a,b,c=(_rational(payload[x]) for x in ("a","b","c"))
            if not(a<b and c!=0):
                raise ValueError("Requires a<b and nonzero scaling factor")
            w=dict(scaled_left=_serialize(a*c),scaled_right=_serialize(b*c),
                   reversed=c<0,strict_inequality_valid=(a*c>b*c if c<0 else a*c<b*c))
        elif op=="quadratic_discriminant":
            a,b,c=(_rational(payload[x]) for x in ("a","b","c"))
            if a==0:raise ValueError("a=0 makes the expression linear, not quadratic")
            d=b*b-4*a*c
            w=dict(discriminant=_serialize(d),real_root_count=2 if d>0 else 1 if d==0 else 0,
                   leading_coefficient=_serialize(a))
        elif op=="am_gm_nonnegative":
            a,b=(_rational(payload[x]) for x in ("a","b"))
            if a<0 or b<0:raise ValueError("Real AM-GM requires a,b>=0")
            # ((a+b)/2)^2-ab = (a-b)^2/4; both sides nonnegative.
            delta=(a-b)**2/4
            if (a+b)**2/4-a*b!=delta:raise ArithmeticError("AM-GM algebra mismatch")
            w=dict(arithmetic_mean=_serialize((a+b)/2),squared_gap=_serialize(delta),
                   equality=a==b)
        elif op=="slope_nonvertical":
            x1,x2,y1,y2=(_rational(payload[x]) for x in ("x1","x2","y1","y2"))
            if x1==x2:raise ValueError("Vertical or coincident points: no finite slope")
            w=dict(slope=_serialize((y2-y1)/(x2-x1)),delta_x=_serialize(x2-x1))
        else:
            row,col,total=(_integer(payload[x]) for x in ("row","column","total"))
            if not(0<total<=100_000 and 0<=row<=total and 0<=col<=total):
                raise ValueError("Invalid contingency table margins")
            e=Fraction(row*col,total)
            if e<=0:raise ValueError("Expected cell count zero")
            w=dict(expected=_serialize(e),total=total,
                   asymptotic_p_value_supported=False)
        return dict(base,status="VERIFIED_FINITE_INSTANCE",witness=w)
    except (ValueError,TypeError,KeyError,ZeroDivisionError,OverflowError) as ex:
        return dict(base,status="CONDITIONS_NOT_ESTABLISHED",reason=str(ex))
    except ArithmeticError as ex:
        return dict(base,status="FAILED_FINITE_INSTANCE",reason=str(ex))
