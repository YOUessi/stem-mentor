"""Finite exact arithmetic witnesses for Batch41. Never a general theorem verifier."""
from __future__ import annotations
from fractions import Fraction

FIELDS = {
    "set_complement_mask":("universe","subset"),
    "amgm_square_gap":("a","b"),
    "inequality_scale":("a","b","c"),
    "quadratic_roots_count":("a","b","c"),
    "radical_fraction_domain":("x",),
    "log_product_powers":("base","u","v"),
    "classical_probability":("good","total"),
    "event_union":("total","a","b","intersection"),
    "event_independent":("total","a","b","intersection"),
    "weighted_population_mean":("n1","mean1","n2","mean2"),
    "sample_variance_unbiased_2":("x","y"),
    "arithmetic_term":("a1","d","n"),
    "arithmetic_sum":("a1","d","n"),
    "geometric_sum":("a1","q","n"),
    "complex_division":("ar","ai","br","bi"),
    "plane_normal_dot":("ux","uy","uz","vx","vy","vz","wx","wy","wz"),
    "square_increase":("left","right"),
}
VALID={
    "set_complement_mask":{"universe":7,"subset":5},
    "amgm_square_gap":{"a":4,"b":9},
    "inequality_scale":{"a":1,"b":2,"c":-3},
    "quadratic_roots_count":{"a":1,"b":-5,"c":6},
    "radical_fraction_domain":{"x":-2},
    "log_product_powers":{"base":2,"u":2,"v":3},
    "classical_probability":{"good":3,"total":6},
    "event_union":{"total":6,"a":3,"b":3,"intersection":2},
    "event_independent":{"total":4,"a":2,"b":2,"intersection":1},
    "weighted_population_mean":{"n1":80,"mean1":4,"n2":20,"mean2":9},
    "sample_variance_unbiased_2":{"x":1,"y":3},
    "arithmetic_term":{"a1":5,"d":-2,"n":4},
    "arithmetic_sum":{"a1":3,"d":2,"n":4},
    "geometric_sum":{"a1":4,"q":1,"n":5},
    "complex_division":{"ar":1,"ai":1,"br":1,"bi":-1},
    "plane_normal_dot":{"ux":1,"uy":0,"uz":0,"vx":0,"vy":1,"vz":0,"wx":0,"wy":0,"wz":1},
    "square_increase":{"left":1,"right":3},
}
INVALID={
    "set_complement_mask":{"universe":3,"subset":5},
    "amgm_square_gap":{"a":-1,"b":9},
    "inequality_scale":{"a":2,"b":1,"c":-3},
    "quadratic_roots_count":{"a":0,"b":0,"c":0},
    "radical_fraction_domain":{"x":1},
    "log_product_powers":{"base":1,"u":2,"v":3},
    "classical_probability":{"good":7,"total":6},
    "event_union":{"total":6,"a":1,"b":2,"intersection":3},
    "event_independent":{"total":4,"a":2,"b":2,"intersection":3},
    "weighted_population_mean":{"n1":0,"mean1":4,"n2":20,"mean2":9},
    "sample_variance_unbiased_2":{"x":10**9,"y":3},
    "arithmetic_term":{"a1":5,"d":-2,"n":0},
    "arithmetic_sum":{"a1":3,"d":2,"n":-1},
    "geometric_sum":{"a1":4,"q":1,"n":0},
    "complex_division":{"ar":1,"ai":1,"br":0,"bi":0},
    "plane_normal_dot":{"ux":1,"uy":0,"uz":0,"vx":2,"vy":0,"vz":0,"wx":0,"wy":0,"wz":1},
    "square_increase":{"left":-1,"right":3},
}
def _out(status:str,value:str|None=None):
    return {"status":status,"exact_value":value,
            "general_theorem_certified":False,"student_freeform_step_verified":False,
            "teacher_approved":False,"student_publishable":False}

def witness(name:str,payload:dict):
    if name not in FIELDS:
        return _out("UNSUPPORTED")
    if not isinstance(payload,dict) or set(payload)!=set(FIELDS[name]):
        return _out("CONDITIONS_NOT_ESTABLISHED")
    if any(type(x) is not int or abs(x)>1000 for x in payload.values()):
        return _out("CONDITIONS_NOT_ESTABLISHED")
    v=payload
    try:
        if name=="set_complement_mask":
            u,s=v["universe"],v["subset"]
            if not (0<=u<1024 and 0<=s<1024 and s&~u==0): raise ValueError()
            result=str(u&~s)
        elif name=="amgm_square_gap":
            a,b=v["a"],v["b"]
            if min(a,b)<0:raise ValueError()
            result=str((a-b)**2) # exact nonnegative equivalent (a+b)^2-4ab
        elif name=="inequality_scale":
            a,b,c=v["a"],v["b"],v["c"]
            if not a<b:raise ValueError()
            result="<" if a*c<b*c else ">" if a*c>b*c else "="
        elif name=="quadratic_roots_count":
            a,b,c=v["a"],v["b"],v["c"]
            if a==0:raise ValueError()
            delta=b*b-4*a*c
            result="2" if delta>0 else "1" if delta==0 else "0"
        elif name=="radical_fraction_domain":
            x=v["x"]
            if x+2<0 or x==1:raise ValueError()
            result="DEFINED" # sqrt(x+2)/(x-1)
        elif name=="log_product_powers":
            a,u,w=v["base"],v["u"],v["v"]
            if not (2<=a<=10 and abs(u)<=8 and abs(w)<=8):raise ValueError()
            # actual x=a^u, y=a^v positive; exponent uniqueness proves log_a(xy)=u+v
            assert Fraction(a)**u * Fraction(a)**w == Fraction(a)**(u+w)
            result=str(u+w)
        elif name=="classical_probability":
            g,n=v["good"],v["total"]
            if not (n>0 and 0<=g<=n):raise ValueError()
            result=str(Fraction(g,n))
        elif name in {"event_union","event_independent"}:
            n,a,b,k=(v[z] for z in ("total","a","b","intersection"))
            if not (n>0 and 0<=a<=n and 0<=b<=n and max(0,a+b-n)<=k<=min(a,b)):
                raise ValueError()
            result=str(Fraction(a+b-k,n)) if name=="event_union" else str(Fraction(k,n)==Fraction(a,n)*Fraction(b,n)).lower()
        elif name=="weighted_population_mean":
            n1,m1,n2,m2=(v[z] for z in ("n1","mean1","n2","mean2"))
            if n1<=0 or n2<=0:raise ValueError()
            result=str(Fraction(n1*m1+n2*m2,n1+n2))
        elif name=="sample_variance_unbiased_2":
            x,y=v["x"],v["y"]
            mean=Fraction(x+y,2)
            result=str((x-mean)**2+(y-mean)**2) # n-1=1
        elif name in {"arithmetic_term","arithmetic_sum"}:
            a,d,n=(v[z] for z in ("a1","d","n"))
            if not 1<=n<=40:raise ValueError()
            last=a+(n-1)*d
            result=str(last if name=="arithmetic_term" else Fraction(n*(a+last),2))
        elif name=="geometric_sum":
            a,q,n=(v[z] for z in ("a1","q","n"))
            if not 1<=n<=20 or abs(q)>10:raise ValueError()
            result=str(a*n if q==1 else Fraction(a*(1-q**n),1-q))
            assert int(result)==sum(a*q**k for k in range(n))
        elif name=="complex_division":
            ar,ai,br,bi=(v[z] for z in ("ar","ai","br","bi"))
            den=br*br+bi*bi
            if not den:raise ValueError()
            result=f"{Fraction(ar*br+ai*bi,den)}|{Fraction(ai*br-ar*bi,den)}"
        elif name=="plane_normal_dot":
            u=tuple(v[z] for z in ("ux","uy","uz"))
            s=tuple(v[z] for z in ("vx","vy","vz"))
            w=tuple(v[z] for z in ("wx","wy","wz"))
            cross=(u[1]*s[2]-u[2]*s[1],u[2]*s[0]-u[0]*s[2],u[0]*s[1]-u[1]*s[0])
            if cross==(0,0,0) or w==(0,0,0):raise ValueError()
            result=str(sum(x*y for x,y in zip(u,w))==0 and sum(x*y for x,y in zip(s,w))==0).lower()
        elif name=="square_increase":
            a,b=v["left"],v["right"]
            if not (0<=a<b):raise ValueError()
            result=str(b*b-a*a)
        else:
            return _out("UNSUPPORTED")
        return _out("FINITE_EXACT_CASE_ONLY",result)
    except (ValueError,ArithmeticError,OverflowError,AssertionError,ZeroDivisionError):
        return _out("CONDITIONS_NOT_ESTABLISHED")
