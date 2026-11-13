"""Seven bounded mathematical witnesses for Batch40 syllabus-scope distinctions.

No freeform expressions, no theorem certification, no student-step approval.
"""
from __future__ import annotations
from fractions import Fraction
from math import lcm

FIELDS = {
    "reciprocal_epsilon_n": ("p", "q"),
    "quadratic_increment_vs_differential": ("x", "h"),
    "tail_probability_vs_posterior": ("p0", "q0", "p1", "q1", "prior", "prior_den"),
    "cobb_douglas_positive_example": ("A", "L", "K"),
    "integer_rhythm_lcm": ("a", "b"),
    "affine_first_order_difference": ("a", "b", "x0", "n"),
    "polynomial_upper_limit_integral": ("x",),
}
VALID = {
    "reciprocal_epsilon_n": {"p": 1, "q": 12},
    "quadratic_increment_vs_differential": {"x": 2, "h": 1},
    "tail_probability_vs_posterior": {
        "p0": 1, "q0": 20, "p1": 1, "q1": 2, "prior": 1, "prior_den": 10
    },
    "cobb_douglas_positive_example": {"A": 2, "L": 3, "K": 5},
    "integer_rhythm_lcm": {"a": 4, "b": 6},
    "affine_first_order_difference": {"a": 1, "b": 3, "x0": 2, "n": 4},
    "polynomial_upper_limit_integral": {"x": 3},
}
INVALID = {
    "reciprocal_epsilon_n": {"p": 0, "q": 12},
    "quadratic_increment_vs_differential": {"x": 2, "h": 0},
    "tail_probability_vs_posterior": {
        "p0": 1, "q0": 20, "p1": 1, "q1": 2, "prior": 0, "prior_den": 10
    },
    "cobb_douglas_positive_example": {"A": 2, "L": 0, "K": 5},
    "integer_rhythm_lcm": {"a": 4, "b": 0},
    "affine_first_order_difference": {"a": 1, "b": 3, "x0": 2, "n": -1},
    "polynomial_upper_limit_integral": {"x": True},
}

def witness(kind: str, values: dict) -> dict:
    base = {
        "status": "UNSUPPORTED", "value": None,
        "proof_certified": False, "teacher_approved": False,
        "student_step_verified": False, "student_publishable": False,
    }
    if kind not in FIELDS:
        return base
    bad = dict(base, status="CONDITIONS_NOT_ESTABLISHED")
    fields = FIELDS[kind]
    if not isinstance(values, dict) or set(values) != set(fields):
        return bad
    if any(type(values[k]) is not int or abs(values[k]) > 100 for k in fields):
        return bad
    v = values
    try:
        if kind == "reciprocal_epsilon_n":
            if v["p"] <= 0 or v["q"] <= 0:
                return bad
            epsilon = Fraction(v["p"], v["q"])
            N = v["q"] // v["p"] + 1
            result = f"N={N};1/N={Fraction(1, N)};epsilon={epsilon}"
        elif kind == "quadratic_increment_vs_differential":
            if v["h"] == 0:
                return bad
            delta = 2*v["x"]*v["h"] + v["h"]**2
            dy = 2*v["x"]*v["h"]
            result = f"delta={delta};dy={dy};error={delta-dy}"
        elif kind == "tail_probability_vs_posterior":
            if (not 0 < v["p0"] <= v["q0"] or
                not 0 < v["p1"] <= v["q1"] or
                not 0 < v["prior"] < v["prior_den"]):
                return bad
            prob = Fraction(v["p0"], v["q0"])
            alt = Fraction(v["p1"], v["q1"])
            prior = Fraction(v["prior"], v["prior_den"])
            posterior = (prob*prior)/(prob*prior+alt*(1-prior))
            result = f"P(E|H0)={prob};P(H0|E)={posterior}"
        elif kind == "cobb_douglas_positive_example":
            if min(v.values()) <= 0:
                return bad
            result = f"Q={v['A']*v['L']*v['K']};log_inputs_positive=true"
        elif kind == "integer_rhythm_lcm":
            if v["a"] <= 0 or v["b"] <= 0:
                return bad
            result = f"discrete_lcm={lcm(v['a'],v['b'])}"
        elif kind == "affine_first_order_difference":
            if v["n"] < 0 or v["n"] > 20:
                return bad
            xn = v["x0"]
            for _ in range(v["n"]):
                xn = v["a"]*xn + v["b"]
            closed = (v["x0"] + v["n"]*v["b"] if v["a"] == 1 else
                      Fraction(v["x0"]*v["a"]**v["n"]) +
                      Fraction(v["b"]*(v["a"]**v["n"]-1), v["a"]-1))
            if Fraction(xn) != closed:
                return bad
            result = f"x_n={xn};branch={'a=1' if v['a']==1 else 'a!=1'}"
        else:
            x = v["x"]
            result = f"integral_0_x_t2={Fraction(x**3,3)};derivative_at_x={x*x}"
    except (ValueError, ZeroDivisionError, OverflowError):
        return bad
    return dict(base, status="FINITE_EXACT_CASE_ONLY", value=result,
                scope="Only the declared exact example is checked; no general theorem proof.")
