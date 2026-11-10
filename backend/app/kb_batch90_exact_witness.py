"""Finite exact witnesses for selected Batch90 mathematical editorial contrasts.

Only bounded authored arithmetic examples are checked; not claims of general theorem
proof, official curricular equivalence, student-answer verification or teacher approval.
No string expression evaluation or user-facing solution retrieval.
"""
from fractions import Fraction as F

try:
    import sympy as sp
except ImportError:
    sp = None

SUPPORTED = {
    "empty_set", "union_intersection", "quadratic_sign",
    "exponent_inverse", "arithmetic_sequence", "stationary_not_extremum",
    "line_circle_separation", "dependent_events", "compound_growth",
    "spatial_dot", "conditioned_die", "weighted_mean", "octave_ratio",
    "derivative_polynomial", "plane_normal", "least_squares"
}

def need(ok, reason):
    if not ok:
        raise ValueError(reason)

def integer(x):
    need(type(x) is int, "integer required")
    return x

def frac_pair(p):
    need(type(p) in (tuple, list) and len(p)==2, "rational pair required")
    numerator, denominator = integer(p[0]), integer(p[1])
    need(denominator!=0, "zero rational denominator")
    return F(numerator, denominator)

def vector(v, dim):
    need(type(v) in (tuple,list) and len(v)==dim, "vector dimension mismatch")
    return tuple(integer(x) for x in v)

def canonical_set(v):
    need(type(v) is list and all(type(x) is int for x in v)
         and len(set(v))==len(v), "finite-set fixture invalid")
    return set(v)

def evaluate(op, args):
    need(op in SUPPORTED and type(args) is dict, "unsupported exact witness")
    try:
        if op == "empty_set":
            need(args == {"marker": "valid"}, "set fixture invalid")
            value = "empty=0;singleton=1"
            need(len(set()) == 0 and len({frozenset()}) == 1, "set cardinality bug")
        elif op == "union_intersection":
            a,b=canonical_set(args["a"]),canonical_set(args["b"])
            value = f"union={len(a|b)};intersection={len(a&b)}"
        elif op == "quadratic_sign":
            a,b,c=integer(args["a"]),integer(args["b"]),integer(args["c"])
            need(a!=0, "quadratic leading coefficient zero")
            xs=[integer(x) for x in args["xs"]]
            need(len(xs)==2, "two witnesses needed")
            value=",".join(str(a*x*x+b*x+c) for x in xs)
        elif op == "exponent_inverse":
            base, arg = integer(args["base"]), integer(args["argument"])
            need(base>0 and base!=1 and arg>0, "real logarithm domain")
            k=0; power=1
            while power < arg and k<100:
                power*=base;k+=1
            need(power==arg,"argument is not an integral power of base")
            value=f"exp={base**k};log={k}"
        elif op == "arithmetic_sequence":
            a,d,n=integer(args["a"]),integer(args["d"]),integer(args["n"])
            need(n>0, "n must be positive integer")
            value=f"term={a+(n-1)*d};sum={n*(2*a+(n-1)*d)//2}"
        elif op == "stationary_not_extremum":
            need(args == {"name":"x_cubed","point":0}, "not the audited polynomial")
            # f'(0)=0 but f(-1)<f(0)<f(1): no local extremum.
            value=f"derivative={3*0*0};neighbors={-1**3},{0**3},{1**3}"
        elif op == "line_circle_separation":
            radius_squared=integer(args["radius_squared"])
            offset=integer(args["line_offset"])
            need(radius_squared>0, "real nondegenerate circle required")
            value=f"distance_sq={offset*offset};radius_sq={radius_squared};disjoint={offset*offset>radius_squared}"
        elif op == "dependent_events":
            sample=canonical_set(args["sample"])
            a=canonical_set(args["a"]); b=canonical_set(args["b"])
            need(len(sample)>0 and a<=sample and b<=sample, "valid finite sample needed")
            both=F(len(a&b),len(sample))
            independent=F(len(a)*len(b),len(sample)**2)
            value=f"intersection={both};product={independent};independent={both==independent}"
        elif op == "compound_growth":
            principal=integer(args["principal"])
            ratio=frac_pair(args["ratio"])
            n=integer(args["periods"])
            need(principal>=0 and ratio>0 and n>=0, "nonnegative principal and periodic growth domain")
            value=str(principal*ratio**n)
        elif op == "spatial_dot":
            a,b=vector(args["a"],3),vector(args["b"],3)
            value=str(sum(i*j for i,j in zip(a,b)))
        elif op == "conditioned_die":
            sample=canonical_set(args["sample"])
            a,b=canonical_set(args["a"]),canonical_set(args["b"])
            need(a<=sample and b<=sample and len(b)>0 and len(sample)>0, "conditional denominator zero")
            value=str(F(len(a&b),len(b)))
        elif op == "weighted_mean":
            values=args["values"];weights=args["weights"]
            need(type(values) is list and type(weights) is list
                 and len(values)==len(weights)>0, "weight vector shape invalid")
            xs=[integer(x) for x in values]
            ws=[frac_pair(w) for w in weights]
            need(all(w>=0 for w in ws) and sum(ws)==1, "nonnegative normalized weights needed")
            value=str(sum(x*w for x,w in zip(xs,ws)))
        elif op == "octave_ratio":
            need(sp is not None, "sympy unavailable")
            n,base=integer(args["half_steps"]),integer(args["octave"])
            need(n>=0 and base>1, "positive octave ratio with nonnegative step count")
            value=str(sp.simplify(sp.Pow(base,sp.Rational(1,12))**n))
        elif op == "derivative_polynomial":
            need(sp is not None, "sympy unavailable")
            need(args["power"] in (2,3) and type(args["power"]) is int,
                 "only controlled polynomial powers supported")
            point=integer(args["point"])
            x=sp.Symbol("x",real=True)
            value=str(sp.diff(x**args["power"],x).subs(x,point))
        elif op == "plane_normal":
            normal=vector(args["normal"],3)
            point=vector(args["point"],3)
            query=vector(args["query"],3)
            need(any(normal), "zero normal invalid")
            value=str(sum(n*(q-p) for n,p,q in zip(normal,point,query)))
        elif op == "least_squares":
            xs=args["xs"];ys=args["ys"]
            need(type(xs) is list and type(ys) is list and len(xs)==len(ys)>1,
                 "regression samples invalid")
            xs=[integer(x) for x in xs];ys=[integer(y) for y in ys]
            xmean=F(sum(xs),len(xs));ymean=F(sum(ys),len(ys))
            denom=sum((x-xmean)**2 for x in xs)
            need(denom!=0, "constant predictor cannot identify slope")
            slope=sum((x-xmean)*(y-ymean) for x,y in zip(xs,ys))/denom
            intercept=ymean-slope*xmean
            value=f"slope={slope};intercept={intercept}"
        else:
            raise ValueError("no implementation")
        return {"status":"VERIFIED_FINITE_INSTANCE","exact_value":value,
                "general_theorem_formally_certified":False,
                "teacher_approved":False,"student_free_text_verified":False}
    except (ValueError, KeyError, IndexError, TypeError, ZeroDivisionError) as e:
        return {"status":"CONDITIONS_NOT_ESTABLISHED","reason":str(e),
                "general_theorem_formally_certified":False,
                "teacher_approved":False,"student_free_text_verified":False}

# Author-controlled frozen examples. Invalid fixtures deliberately violate prerequisites.
CASES = (
 ("KB90-REL-002","empty_set",{"marker":"valid"},{"marker":"not_a_set"},"empty=0;singleton=1"),
 ("KB90-REL-003","union_intersection",{"a":[1,2],"b":[2,3]},{"a":[1,1],"b":[2,3]},"union=3;intersection=1"),
 ("KB90-REL-007","quadratic_sign",{"a":1,"b":0,"c":-1,"xs":[2,0]},{"a":0,"b":0,"c":-1,"xs":[2,0]},"3,-1"),
 ("KB90-REL-008","exponent_inverse",{"base":2,"argument":8},{"base":1,"argument":8},"exp=8;log=3"),
 ("KB90-REL-012","arithmetic_sequence",{"a":2,"d":3,"n":4},{"a":2,"d":3,"n":0},"term=11;sum=26"),
 ("KB90-REL-013","stationary_not_extremum",{"name":"x_cubed","point":0},{"name":"absolute_value","point":0},"derivative=0;neighbors=-1,0,1"),
 ("KB90-REL-015","line_circle_separation",{"radius_squared":4,"line_offset":3},{"radius_squared":-1,"line_offset":3},"distance_sq=9;radius_sq=4;disjoint=True"),
 ("KB90-REL-016","dependent_events",{"sample":[1,2,3,4,5,6],"a":[2,4,6],"b":[4,5,6]},{"sample":[],"a":[],"b":[]},"intersection=1/3;product=1/4;independent=False"),
 ("KB90-REL-017","compound_growth",{"principal":100,"ratio":[21,20],"periods":2},{"principal":100,"ratio":[21,0],"periods":2},"441/4"),
 ("KB90-REL-018","spatial_dot",{"a":[1,2,5],"b":[3,4,2]},{"a":[1,2],"b":[3,4,2]},"21"),
 ("KB90-REL-019","conditioned_die",{"sample":[1,2,3,4,5,6],"a":[2,4,6],"b":[4,5,6]},{"sample":[1,2],"a":[2],"b":[]},"2/3"),
 ("KB90-REL-020","weighted_mean",{"values":[1,3],"weights":[[1,4],[3,4]]},{"values":[1,3],"weights":[[-1,1],[2,1]]},"5/2"),
 ("KB90-REL-021","octave_ratio",{"half_steps":12,"octave":2},{"half_steps":12,"octave":0},"2"),
 ("KB90-REL-022","derivative_polynomial",{"power":2,"point":2},{"power":1,"point":2},"4"),
 ("KB90-REL-023","plane_normal",{"normal":[1,2,3],"point":[1,0,0],"query":[1,0,0]},{"normal":[0,0,0],"point":[1,0,0],"query":[1,0,0]},"0"),
 ("KB90-REL-024","least_squares",{"xs":[1,2,3],"ys":[2,4,6]},{"xs":[2,2,2],"ys":[2,4,6]},"slope=2;intercept=0")
)
def check_all():
    results={}
    for relation,op,valid,invalid,expected in CASES:
        assert relation not in results and op in SUPPORTED, "invalid frozen case catalog"
        good=evaluate(op,valid);bad=evaluate(op,invalid)
        assert good["status"]=="VERIFIED_FINITE_INSTANCE" and good["exact_value"]==expected, (
            relation,op,good,expected)
        assert bad["status"]=="CONDITIONS_NOT_ESTABLISHED", (relation,op,bad)
        results[relation]={
            "operation":op,"good":good,"invalid":bad,
            "evidence_scope":"EXACT_FINITE_FIXTURE_ONLY_NOT_GENERAL_PROOF",
            "student_authoritative_index_eligible":False,
            "teacher_approved":False
        }
    assert len(results)==16
    return results
