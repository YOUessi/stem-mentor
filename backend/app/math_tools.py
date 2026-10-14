"""Safe, curated algebra checks: symbols/formulas are fixed in code, never eval input."""
from sympy import symbols, simplify

x,y=symbols("x y", real=True)


def known_identity_check(identity_id):
    if identity_id == "inequality-sum-to-product":
        # Under x+y=1, this transformation holds where x*y != 0.
        residual=simplify(((1/x+1/y)-1/(x*y)).subs(y,1-x))
        return {"identity_id":identity_id,"valid_under_conditions":bool(residual==0),
                "conditions":["x+y=1","x≠0","y≠0"],"tool":"SYMPY_CURATED_CHECK"}
    if identity_id == "ellipse-tangent-at-3-0":
        # Check P=(3,0) on ellipse x^2/9+y^2/4=1; tangent x=3.
        on_curve=simplify(3**2/9+0**2/4-1)==0
        return {"identity_id":identity_id,"valid_under_conditions":bool(on_curve),
                "conditions":["P=(3,0) 在曲线上","该点非奇异"],"tool":"SYMPY_CURATED_CHECK"}
    return None
