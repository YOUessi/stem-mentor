"""Batch49 finite EXACT input/premise checks. Not proofs or student answer certification."""
from __future__ import annotations
from fractions import Fraction
from math import isqrt

SAMPLES={
 "sine_at_quarter":({"m":20,"amplitude":3,"period":24},"23",{"m":20,"amplitude":3,"period":0}),
 "linear_capacity_horizon":({"cap":10,"rate":2},"5",{"cap":10,"rate":0}),
 "exponential_finite_value":({"base":2,"n":5},"32",{"base":1,"n":5}),
 "rate_seconds_to_minutes":({"meters_per_sec":2},"120",{"meters_per_sec":-2}),
 "complex_modulus_sq_nonzero":({"x":1,"y":1},"2",{"x":0,"y":0}),
 "oblique_half_scale_y_length_sq":({"y":4,"denom":2},"4",{"y":4,"denom":0}),
 "skew_lines_projected_crossing":({"height":1},"SKEW_PROJECTION_CROSS",{"height":0}),
 "line_plane_z_relation":({"base_z":1,"slope_z":0,"plane_z":0,"normal_z":1},"PARALLEL_DISJOINT",{"base_z":1,"slope_z":0,"plane_z":0,"normal_z":0}),
 "displacement_length_sq":({"x1":1,"y1":1,"x2":4,"y2":5},"25",{"x1":101,"y1":1,"x2":4,"y2":5}),
 "finite_sample_mean":({"values":[10,10,50,50]},"30",{"values":[]}),
 "nonnegative_linear_horizon":({"initial":100,"decrement":10},"10",{"initial":100,"decrement":0}),
 "nonnegative_square_root":({"square":9},"3",{"square":-9}),
 "three_equal_step_linear_fit":({"y0":0,"y1":2,"y2":0,"step":1},"NOT_LINEAR",{"y0":0,"y1":2,"y2":0,"step":0}),
 "additive_recurrence_term":({"x0":2,"d":3,"n":4},"14",{"x0":2,"d":3,"n":-1}),
 "quadratic_derivative":({"a":1,"b":0,"t":3},"6",{"a":1,"b":0,"t":101}),
 "plane_line_inclusion":({"base_z":0,"slope_z":0,"plane_z":0,"normal_z":1},"CONTAINED",{"base_z":0,"slope_z":0,"plane_z":0,"normal_z":0}),
 "translation_new_xy":({"x":4,"y":0,"a":3,"b":-2},"(1,2)",{"x":4,"y":0,"a":101,"b":-2}),
}
INDEX_OP={
 1:"sine_at_quarter",2:"linear_capacity_horizon",3:"exponential_finite_value",
 4:"rate_seconds_to_minutes",5:"complex_modulus_sq_nonzero",
 6:"oblique_half_scale_y_length_sq",7:"skew_lines_projected_crossing",
 8:"line_plane_z_relation",9:"displacement_length_sq",
 10:"finite_sample_mean",11:"nonnegative_linear_horizon",
 12:"nonnegative_square_root",13:"three_equal_step_linear_fit",
 15:"additive_recurrence_term",16:"quadratic_derivative",
 17:"plane_line_inclusion",19:"translation_new_xy",
}
assert len(INDEX_OP)==len(SAMPLES)==17 and set(INDEX_OP.values())==set(SAMPLES)

def require(v):
    if not v: raise ValueError("mathematical premise not established")

def calc(op,d):
    if op=="sine_at_quarter":
        require(d["period"]>0 and d["amplitude"]>=0)
        return str(d["m"]+d["amplitude"])
    if op=="linear_capacity_horizon":
        require(d["cap"]>=0 and d["rate"]>0)
        return str(Fraction(d["cap"],d["rate"]))
    if op=="exponential_finite_value":
        require(d["base"]>1 and 0<=d["n"]<=10)
        return str(d["base"]**d["n"])
    if op=="rate_seconds_to_minutes":
        require(d["meters_per_sec"]>=0)
        return str(60*d["meters_per_sec"])
    if op=="complex_modulus_sq_nonzero":
        require((d["x"],d["y"])!=(0,0))
        return str(d["x"]**2+d["y"]**2)
    if op=="oblique_half_scale_y_length_sq":
        require(d["denom"]==2)
        return str(Fraction(d["y"]**2,d["denom"]**2))
    if op=="skew_lines_projected_crossing":
        require(d["height"]!=0)
        return "SKEW_PROJECTION_CROSS"
    if op in ("line_plane_z_relation","plane_line_inclusion"):
        require(d["normal_z"]!=0)
        if d["slope_z"]!=0:return "INTERSECTS_ONCE"
        return "CONTAINED" if d["base_z"]==d["plane_z"] else "PARALLEL_DISJOINT"
    if op=="displacement_length_sq":
        return str((d["x2"]-d["x1"])**2+(d["y2"]-d["y1"])**2)
    if op=="finite_sample_mean":
        vals=d["values"];require(len(vals)>0)
        return str(Fraction(sum(vals),len(vals)))
    if op=="nonnegative_linear_horizon":
        require(d["initial"]>=0 and d["decrement"]>0)
        return str(Fraction(d["initial"],d["decrement"]))
    if op=="nonnegative_square_root":
        n=d["square"];require(n>=0 and isqrt(n)**2==n)
        return str(isqrt(n))
    if op=="three_equal_step_linear_fit":
        require(d["step"]>0)
        return "LINEAR" if 2*d["y1"]==d["y0"]+d["y2"] else "NOT_LINEAR"
    if op=="additive_recurrence_term":
        require(0<=d["n"]<=30)
        return str(d["x0"]+d["d"]*d["n"])
    if op=="quadratic_derivative":
        return str(2*d["a"]*d["t"]+d["b"])
    if op=="translation_new_xy":
        return "("+str(d["x"]-d["a"])+","+str(d["y"]-d["b"])+")"
    raise ValueError("unsupported")

def witness(op,params):
    out=dict(status="CONDITIONS_NOT_ESTABLISHED",exact_value=None,
             general_theorem_certified=False,teacher_approved=False,
             student_freeform_step_verified=False,student_publishable=False)
    if type(op) is not str or op not in SAMPLES:
        out["status"]="UNSUPPORTED";return out
    template=SAMPLES[op][0]
    if type(params) is not dict or set(params)!=set(template):return out
    for k,v in params.items():
        if type(v) is int:
            if abs(v)>100:return out
        elif type(v) is list and k=="values":
            if len(v)>30 or any(type(x) is not int or abs(x)>100 for x in v):return out
        else:return out
    try:
        out["exact_value"]=calc(op,params)
        out["status"]="FINITE_EXACT_CASE_ONLY"
    except (ValueError,TypeError,IndexError,ZeroDivisionError,OverflowError):
        pass
    return out
