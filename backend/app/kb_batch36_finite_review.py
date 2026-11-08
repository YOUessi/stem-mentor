"""Finite, exact arithmetic crosschecks for *specific* Batch36 review risks.

Every operator rejects unsupported freeform proof and invalid premises; these are not
general theorem certificates or authentic teacher reviews.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import combinations
from math import comb, gcd
from typing import Any

SPECS = {
    "epsilon_1_over_n": ("eps_num", "eps_den", "N"),
    "matrix_dims": ("a_rows", "a_cols", "b_rows", "b_cols"),
    "cramer_2x2": ("a", "b", "c", "d"),
    "annuity_present_value": ("rate_num", "rate_den", "n"),
    "triangular_density": ("coeff", "right_endpoint"),
    "mvt_square": ("a", "b"),
    "binomial_upper_tail": ("n", "k", "p_num", "p_den"),
    "two_point_regression": ("x1", "x2", "y1", "y2"),
    "ivt_square_root_two": ("a", "b"),
    "nonzero_line_normal": ("nx", "ny"),
    "two_point_mean": ("x1", "x2"),
    "rhythm_lcm": ("a", "b"),
}
VALID = {
    "epsilon_1_over_n": {"eps_num": 1, "eps_den": 10, "N": 11},
    "matrix_dims": {"a_rows": 2, "a_cols": 3, "b_rows": 3, "b_cols": 4},
    "cramer_2x2": {"a": 1, "b": 2, "c": 3, "d": 4},
    "annuity_present_value": {"rate_num": 1, "rate_den": 10, "n": 2},
    "triangular_density": {"coeff": 2, "right_endpoint": 1},
    "mvt_square": {"a": 1, "b": 3},
    "binomial_upper_tail": {"n": 4, "k": 3, "p_num": 1, "p_den": 2},
    "two_point_regression": {"x1": 0, "x2": 2, "y1": 1, "y2": 5},
    "ivt_square_root_two": {"a": 1, "b": 2},
    "nonzero_line_normal": {"nx": 0, "ny": 1},
    "two_point_mean": {"x1": 1, "x2": 3},
    "rhythm_lcm": {"a": 3, "b": 4},
}
INVALID = {
    "epsilon_1_over_n": {"eps_num": 1, "eps_den": 10, "N": 10},
    "matrix_dims": {"a_rows": 2, "a_cols": 3, "b_rows": 2, "b_cols": 4},
    "cramer_2x2": {"a": 1, "b": 2, "c": 2, "d": 4},
    "annuity_present_value": {"rate_num": -1, "rate_den": 1, "n": 2},
    "triangular_density": {"coeff": -2, "right_endpoint": 1},
    "mvt_square": {"a": 3, "b": 1},
    "binomial_upper_tail": {"n": 4, "k": 5, "p_num": 1, "p_den": 2},
    "two_point_regression": {"x1": 2, "x2": 2, "y1": 1, "y2": 5},
    "ivt_square_root_two": {"a": 3, "b": 4},
    "nonzero_line_normal": {"nx": 0, "ny": 0},
    "two_point_mean": {"x1": 1000001, "x2": 3},
    "rhythm_lcm": {"a": -3, "b": 4},
}
def witness(op: str, p: dict[str, Any]) -> dict[str, str]:
    if op not in SPECS:
        return {"status": "UNSUPPORTED", "reason": "Unknown exact operator"}
    fields = SPECS[op]
    if not isinstance(p, dict) or set(p) != set(fields):
        return {"status": "CONDITIONS_NOT_ESTABLISHED", "reason": "Missing or extra field"}
    if any(type(p[k]) is not int or abs(p[k]) > 1_000_000 for k in fields):
        return {"status": "CONDITIONS_NOT_ESTABLISHED", "reason": "Not a bounded exact integer"}
    try:
        v = compute(op, p)
    except (ZeroDivisionError, ValueError, OverflowError):
        return {"status": "CONDITIONS_NOT_ESTABLISHED", "reason": "Failed mathematical domain premise"}
    return {
        "status": "FINITE_EXACT_CASE_ONLY",
        "exact_value": str(v),
        "teacher_approved": "false",
        "general_theorem_certified": "false",
        "student_freeform_step_verified": "false",
    }

def compute(op: str, p: dict[str, int]) -> Fraction | int | str:
    def pos(x: int) -> None:
        if x <= 0:
            raise ValueError("Expected positive integer")
    if op == "epsilon_1_over_n":
        pos(p["eps_num"]); pos(p["eps_den"]); pos(p["N"])
        e = Fraction(p["eps_num"], p["eps_den"])
        if Fraction(1, p["N"]) >= e:
            raise ValueError("N is not a strict epsilon witness")
        return Fraction(1, p["N"])
    if op == "matrix_dims":
        for k in SPECS[op]: pos(p[k])
        if p["a_cols"] != p["b_rows"]: raise ValueError("Dimensions incompatible")
        return f'{p["a_rows"]}x{p["b_cols"]}'
    if op == "cramer_2x2":
        det = p["a"]*p["d"] - p["b"]*p["c"]
        if det == 0: raise ValueError("Singular matrix")
        return det
    if op == "annuity_present_value":
        pos(p["rate_den"]); pos(p["n"])
        if p["n"] > 50: raise ValueError("Out of finite scope")
        rate = Fraction(p["rate_num"], p["rate_den"])
        if rate <= -1: raise ValueError("Invalid discount factor")
        q = 1+rate
        return sum((Fraction(100, 1) / (q**k) for k in range(1, p["n"]+1)), Fraction(0))
    if op == "triangular_density":
        pos(p["right_endpoint"])
        if p["coeff"] < 0 or Fraction(p["coeff"]*p["right_endpoint"]**2, 2) != 1:
            raise ValueError("Density not normalized or negative")
        return 1
    if op == "mvt_square":
        if p["a"] >= p["b"]: raise ValueError("Degenerate ordered interval")
        c = Fraction(p["a"] + p["b"], 2)
        if 2*c != Fraction(p["b"]**2-p["a"]**2, p["b"]-p["a"]):
            raise ValueError("Bad example witness")
        return c
    if op == "binomial_upper_tail":
        n,k,nu,de = (p[x] for x in SPECS[op])
        if not (1<=n<=10 and 0<=k<=n and de>0 and 0<=nu<=de):
            raise ValueError("Invalid binomial parameters")
        prob = Fraction(nu,de)
        return sum((comb(n,j)*prob**j*(1-prob)**(n-j) for j in range(k,n+1)), Fraction(0))
    if op == "two_point_regression":
        if p["x1"] == p["x2"]: raise ValueError("Zero regression variance")
        return Fraction(p["y2"]-p["y1"], p["x2"]-p["x1"])
    if op == "ivt_square_root_two":
        if p["a"] >= p["b"] or (p["a"]**2-2)*(p["b"]**2-2) > 0:
            raise ValueError("No guaranteed bracket for this example")
        return f'{p["a"]}..{p["b"]}'
    if op == "nonzero_line_normal":
        if p["nx"] == p["ny"] == 0: raise ValueError("Zero normal")
        return p["nx"]**2 + p["ny"]**2
    if op == "two_point_mean":
        return Fraction(p["x1"]+p["x2"], 2)
    if op == "rhythm_lcm":
        pos(p["a"]); pos(p["b"])
        return p["a"] // gcd(p["a"],p["b"]) * p["b"]
    raise ValueError("Unsupported mathematical operator")
