"""Batch88 finite, assumption-guarded contrast witnesses; not a general theorem prover."""
from __future__ import annotations
from fractions import Fraction as Q
import sympy as sp

SUPPORTED = (
    "MVT_QUADRATIC", "RIEMANN_RIGHT_SUM", "SIGNED_VS_UNSIGNED_AREA",
    "MATRIX_MULTIPLICATION_SHAPE", "LINEAR_SUBSPACE_AFFINE",
    "UNIFORM_VARIANCE", "COVARIANCE_2D_POSITIVE_DEFINITE",
    "JOINT_DISTRIBUTION_INDEPENDENCE", "CRAMER_DIAGONAL",
    "SUFFICIENT_NOT_NECESSARY", "STATIONARY_NONEXTREMUM",
)
# Examples are independent checks only for explicitly supported mathematical statements.
def _int(x):
    if type(x) is not int: raise ValueError("exact integer required")
    return x

def evaluate(operation: str, *data):
    if operation not in SUPPORTED:
        return {"status": "UNSUPPORTED"}
    try:
        if operation == "MVT_QUADRATIC":
            a,b,c = map(_int, data)
            if a >= b or not a < c < b:
                raise ValueError("MVT requires a < c < b")
            slope=Q(b*b-a*a, b-a)
            derivative=2*c
            value=(slope, Q(derivative))
            expected_equal=(slope == derivative)
        elif operation == "RIEMANN_RIGHT_SUM":
            (n,)=map(_int,data)
            if n < 1: raise ValueError("positive subdivisions required")
            value = (Q(n+1,2*n), Q(1,2))
            expected_equal = (value[0]==value[1])
        elif operation == "SIGNED_VS_UNSIGNED_AREA":
            if data: raise ValueError("no arguments accepted")
            x=sp.symbols("x",real=True)
            signed=sp.integrate(x,(x,-1,1))
            unsigned=sp.integrate(sp.Abs(x),(x,-1,1))
            value=(signed,unsigned)
            expected_equal=(signed == unsigned)
        elif operation == "MATRIX_MULTIPLICATION_SHAPE":
            rows,inner,left_inner,cols = map(_int,data)
            if min(rows,inner,left_inner,cols) <= 0:
                raise ValueError("positive dimensions required")
            if inner != left_inner: raise ValueError("matrix inner dimensions disagree")
            value=(rows,cols)
            expected_equal=True
        elif operation == "LINEAR_SUBSPACE_AFFINE":
            (height,) = map(_int,data)
            value={"contains_origin":height==0,
                   "is_subspace":height==0}
            expected_equal=(height==0)
        elif operation == "UNIFORM_VARIANCE":
            a,b=map(_int,data)
            if a>=b: raise ValueError("a < b required for proper uniform density")
            value=Q((b-a)**2,12)
            expected_equal=True
        elif operation == "COVARIANCE_2D_POSITIVE_DEFINITE":
            a,b,d=map(_int,data)
            # symmetric 2-by-2 [[a,b],[b,d]], positive definite iff a>0 and det>0
            value={"determinant":a*d-b*b,"positive_definite":a>0 and a*d-b*b>0}
            expected_equal=value["positive_definite"]
        elif operation == "JOINT_DISTRIBUTION_INDEPENDENCE":
            p00,p01,p10,p11=map(_int,data)
            # integer weights are non-negative counts. Normalize by their positive total.
            if min(p00,p01,p10,p11)<0 or sum((p00,p01,p10,p11))<=0:
                raise ValueError("nonnegative positive-total weights required")
            total=p00+p01+p10+p11
            value={
                "row_marginal":(Q(p00+p01,total), Q(p10+p11,total)),
                "col_marginal":(Q(p00+p10,total), Q(p01+p11,total)),
                "independent":p00*total==(p00+p01)*(p00+p10)
                and p01*total==(p00+p01)*(p01+p11)
                and p10*total==(p10+p11)*(p00+p10)
                and p11*total==(p10+p11)*(p01+p11)
            }
            expected_equal=value["independent"]
        elif operation == "CRAMER_DIAGONAL":
            a,b,c,x,y,z=map(_int,data)
            if a*b*c==0: raise ValueError("singular diagonal coefficient")
            det=a*b*c
            value=(Q(a*x*b*c,det),Q(a*b*y*c,det),Q(a*b*c*z,det))
            # Cramer's rule inverse, with b=(a*x,b*y,c*z)
            expected_equal=(value==(Q(x),Q(y),Q(z)))
        elif operation == "SUFFICIENT_NOT_NECESSARY":
            (n,) = map(_int,data)
            value={"divisible_by_4":n%4==0,"even":n%2==0}
            expected_equal=(not value["divisible_by_4"] or value["even"])
        elif operation == "STATIONARY_NONEXTREMUM":
            (t,) = map(_int,data)
            value={"derivative_at_t":3*t*t,
                   "x_cubed_has_local_extremum_at_t":False}
            expected_equal=(value["derivative_at_t"]==0 and not value["x_cubed_has_local_extremum_at_t"])
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        return {"status":"CONDITIONS_NOT_ESTABLISHED","reason":str(exc)}
    return {"status":"FINITE_EXACT_WITNESS","operation":operation,
            "value":value,"comparison_result":expected_equal,
            "general_theorem_certified":False,"teacher_approved":False}
