"""Batch80 finite exact checks of eight assumption-sensitive mathematical claims.

A success only establishes a bounded example/condition, never an arbitrary
student proof or universal theorem. No eval and no untrusted symbolic parsing.
"""
from fractions import Fraction as Q

OPS = ("log_product", "quadratic_sign", "absolute_equality",
       "uniform_stage_count", "parabola_tangent", "vector_angle",
       "total_partition", "double_angle_unit_circle")
KEYS = {
    "log_product": {"a","x","y"},
    "quadratic_sign": {"a","b","c","x"},
    "absolute_equality": {"u","v"},
    "uniform_stage_count": {"counts"},
    "parabola_tangent": {"kind","x0","h"},
    "vector_angle": {"u","v"},
    "total_partition": {"N","A","blocks"},
    "double_angle_unit_circle": {"p","q","r"},
}

def _guard(x, depth=0):
    if depth>3:
        raise ValueError("Nested input too deep")
    if type(x) is int:
        if abs(x)>256:
            raise ValueError("Input outside bounded integer interval")
    elif type(x) is list:
        if len(x)>32:
            raise ValueError("List exceeds bounded size")
        for y in x:
            _guard(y,depth+1)
    else:
        raise ValueError("Only exact integers and bounded nested integer lists allowed")

def check(op, args):
    if op not in OPS or type(args) is not dict or set(args)!=KEYS[op]:
        raise ValueError("Unknown operation or wrong input schema")
    for value in args.values():
        _guard(value)
    def fail(code):
        return "CONDITIONS_NOT_ESTABLISHED", {"failed_condition":code}
    ev={}
    if op=="log_product":
        a,x,y=args["a"],args["x"],args["y"]
        if a<=0 or a==1 or x<=0 or y<=0:
            return fail("real_log_base_and_both_individual_log_arguments")
        ev={"xy":x*y,"all_real_log_domains_valid":True}
    elif op=="quadratic_sign":
        a,b,c,x=(args[k] for k in ("a","b","c","x"))
        if a==0:
            return fail("coefficient_a_must_be_nonzero")
        completed=Q(a)*(Q(x)+Q(b,2*a))**2-Q(b*b-4*a*c,4*a)
        original=a*x*x+b*x+c
        assert completed==original
        ev={"polynomial_value":str(original),"completed_square_value":str(completed)}
    elif op=="absolute_equality":
        u,v=args["u"],args["v"]
        gap=abs(u)+abs(v)-abs(u+v)
        assert gap>=0 and (gap==0)==(u*v>=0)
        if u*v<0:
            return fail("equality_requires_uv_nonnegative")
        ev={"triangle_inequality_gap":gap,"equality_condition":True}
    elif op=="uniform_stage_count":
        counts=args["counts"]
        if not 2<=len(counts)<=16 or any(z<0 for z in counts) or len(set(counts))!=1:
            return fail("same_number_of_second_stage_choices_for_every_first_stage_branch")
        ev={"first_stage_choices":len(counts),
            "second_stage_choices_per_branch":counts[0],
            "count_by_partition":sum(counts),
            "count_by_product":len(counts)*counts[0]}
        assert ev["count_by_partition"]==ev["count_by_product"]
    elif op=="parabola_tangent":
        kind,x0,h=args["kind"],args["x0"],args["h"]
        if kind!=0 or h==0:
            return fail("differentiability_at_point_and_nonzero_finite_step")
        derivative=2*x0
        residue=(x0+h)**2-(x0*x0+derivative*h)
        assert residue==h*h
        ev={"tangent_slope":derivative,"second_order_residual":residue}
    elif op=="vector_angle":
        u,v=args["u"],args["v"]
        if len(u)!=2 or len(v)!=2 or u==[0,0] or v==[0,0]:
            return fail("two_nonzero_vectors_in_the_same_two_dimensional_space")
        dot=sum(x*y for x,y in zip(u,v))
        nu=sum(z*z for z in u);nv=sum(z*z for z in v)
        gap=nu*nv-dot**2
        assert gap==(u[0]*v[1]-u[1]*v[0])**2>=0
        ev={"dot":dot,"norm_squared_product":nu*nv,"cauchy_gap":gap}
    elif op=="total_partition":
        n,A,blocks=args["N"],args["A"],args["blocks"]
        if not 1<=n<=32 or len(A)!=len(set(A)) or any(not 1<=i<=n for i in A):
            return fail("valid_uniform_sample_space_event")
        if not 1<=len(blocks)<=n or any(type(group) is not list or not group for group in blocks):
            return fail("finite_nonempty_partition_blocks")
        flat=[v for b in blocks for v in b]
        if len(flat)!=n or set(flat)!=set(range(1,n+1)) or len(flat)!=len(set(flat)):
            return fail("pairwise_disjoint_exhaustive_partition")
        joint=sum(len(set(A).intersection(b)) for b in blocks)
        assert joint==len(A)
        ev={"event_probability":str(Q(len(A),n)),
            "sum_of_partition_intersections":str(Q(joint,n))}
    elif op=="double_angle_unit_circle":
        p,q,r=args["p"],args["q"],args["r"]
        if r<=0 or p*p+q*q!=r*r:
            return fail("unit_circle_cos_sin_parameterization_requires_pythagorean_triple")
        sine=Q(2*p*q,r*r)
        cosine=Q(p*p-q*q,r*r)
        assert sine*sine+cosine*cosine==1
        ev={"sin_double":str(sine),"cos_double":str(cosine),
            "omitted_constant_shortcut_is_not_a_general_identity":True}
    return "GUARD_PASSED_FINITE_CASE_ONLY",ev
