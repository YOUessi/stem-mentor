"""Bounded exact cases for p25–36 syllabus scope; neither general proof nor teacher review.

No eval, no arbitrary expressions, floats, bool-as-int, cloud calls or student proof parsing.
"""
from __future__ import annotations
from fractions import Fraction

class ConditionsNotEstablished(ValueError):
    pass

def require(ok,msg):
    if not ok: raise ConditionsNotEstablished(msg)

def rat(x):
    require(type(x) in (int,Fraction),"exact int or Fraction only")
    z=Fraction(x)
    require(abs(z.numerator)<=10**7 and z.denominator<=10**7,
            "numeric magnitude/denominator outside supported bound")
    return z

def positive_count(x):
    require(type(x) is int and 1<=x<=100000,"positive bounded integer count needed")
    return x

def vec(x,n):
    require(type(x) in (list,tuple) and len(x)==n,"fixed-dimensional vector required")
    return tuple(rat(v) for v in x)

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])

FIELDS={
    "unique_plane_from_points":("p","q","r"),
    "line_plane_relation":("plane_normal","plane_offset","line_point","line_direction"),
    "nonzero_vector_orthogonality":("u","v"),
    "triangle_cosine_law":("side_a","side_b","opposite_c"),
    "complex_exact_division":("real_a","imag_a","real_b","imag_b"),
    "classical_equiprobable_event":("universe","event","equiprobable"),
    "binary_joint_independence":("p11","p10","p01","p00"),
    "stratified_weighted_mean":("population_sizes","sample_means","random_design_confirmed"),
    "sample_variance_conventions":("values",),
}

def exact_witness(op,**args):
    require(op in FIELDS,"unknown or unsupported math operator")
    require(set(args)==set(FIELDS[op]),"required fields mismatch / unauthorized metadata")
    if op=="unique_plane_from_points":
        p,q,r=(vec(args[k],3) for k in FIELDS[op])
        n=cross(sub(q,p),sub(r,p))
        require(any(n),"three points must be noncollinear")
        result={"normal":n,"normal_dot_point":dot(n,p),
                "plane_is_uniquely_determined_in_R3":True}
    elif op=="line_plane_relation":
        n=vec(args["plane_normal"],3); d=rat(args["plane_offset"])
        p=vec(args["line_point"],3);v=vec(args["line_direction"],3)
        require(any(n) and any(v),"nonzero plane normal and line direction required")
        ndv=dot(n,v); ndp=dot(n,p)-d
        rel="INTERSECTS" if ndv else ("CONTAINED" if not ndp else "PARALLEL_DISJOINT")
        result={"relation":rel,"direction_dot_normal":ndv,
                "point_plane_offset":ndp,"not_automatically_perpendicular":True}
    elif op=="nonzero_vector_orthogonality":
        a=vec(args["u"],2);b=vec(args["v"],2)
        require(any(a) and any(b),"nonzero vectors needed for angle/perpendicular claim")
        result={"dot_product":dot(a,b),"is_perpendicular":dot(a,b)==0,
                "angle_computed":False}
    elif op=="triangle_cosine_law":
        a,b,c=(rat(args[k]) for k in FIELDS[op])
        require(a>0 and b>0 and c>0 and a+b>c and a+c>b and b+c>a,
                "strict nondegenerate triangle inequalities required")
        cos_c=(a*a+b*b-c*c)/(2*a*b)
        require(-1<cos_c<1,"triangle angle cosine out of strict interval")
        result={"cos_opposite_c":cos_c,"side_sum_check":a*a+b*b-2*a*b*cos_c==c*c,
                "SSA_ambiguity_not_resolved":True}
    elif op=="complex_exact_division":
        ar,ai,br,bi=(rat(args[k]) for k in FIELDS[op])
        denom=br*br+bi*bi
        require(denom>0,"complex divisor must be nonzero")
        rr=(ar*br+ai*bi)/denom;ii=(ai*br-ar*bi)/denom
        result={"quotient_real":rr,"quotient_imag":ii,
                "multiplied_back":(rr*br-ii*bi,rr*bi+ii*br)==(ar,ai)}
    elif op=="classical_equiprobable_event":
        u,e=args["universe"],args["event"]
        require(type(u) in (tuple,list) and type(e) in (tuple,list)
                and 1<=len(u)<=40 and len(e)<=40,"bounded sample space/events only")
        require(all(type(x) is int for x in tuple(u)+tuple(e)),
                "bounded integer labeled outcomes only")
        require(len(set(u))==len(u) and len(set(e))==len(e) and set(e)<=set(u),
                "distinct members of sample space required")
        require(args["equiprobable"] is True,"finite outcomes alone do not ensure equiprobability")
        result={"probability":Fraction(len(e),len(u)),
                "equi_likelihood_explicitly_assumed":True,"independence_certified":False}
    elif op=="binary_joint_independence":
        a,b,c,d=(rat(args[k]) for k in FIELDS[op])
        require(all(z>=0 for z in (a,b,c,d)) and a+b+c+d==1,
                "2x2 joint probabilities must be nonnegative and sum to one")
        pa=a+b;pb=a+c
        result={"P_A":pa,"P_B":pb,"P_both":a,
                "independent":a==pa*pb,"mutually_exclusive":a==0,
                "statistical_population_claim":False}
    elif op=="stratified_weighted_mean":
        sizes,means=args["population_sizes"],args["sample_means"]
        require(type(sizes) in (tuple,list) and type(means) in (tuple,list)
                and 2<=len(sizes)<=12 and len(sizes)==len(means),
                "at least two strata with matching sample summaries required")
        ns=[positive_count(x) for x in sizes]; mus=[rat(x) for x in means]
        require(type(args["random_design_confirmed"]) is bool,
                "sampling-design flag must be explicit bool")
        estimate=sum(Fraction(n,sum(ns))*m for n,m in zip(ns,mus))
        result={"weighted_estimate":estimate,
                "weights":tuple(Fraction(n,sum(ns)) for n in ns),
                "unbiasedness_certified":False,
                "sampling_design_confirmed_by_input_only":args["random_design_confirmed"]}
    elif op=="sample_variance_conventions":
        vals=args["values"]
        require(type(vals) in (tuple,list) and 2<=len(vals)<=30,
                "sample variance denominator n-1 requires at least two values")
        xs=[rat(x) for x in vals]
        mean=sum(xs)/len(xs);sum_sq=sum((x-mean)**2 for x in xs)
        result={"mean":mean,"population_denominator_n":sum_sq/len(xs),
                "sample_denominator_n_minus_1":sum_sq/(len(xs)-1),
                "unbiased_population_estimator_not_certified":True}
    else:raise AssertionError("unreachable")
    return {"status":"FINITE_EXACT_CASE_ONLY","scope":"NOT_FORMAL_GENERAL_PROOF",
            "teacher_approved":False,"student_solution_verified":False,
            "official_atom_certified":False,"result":result}
