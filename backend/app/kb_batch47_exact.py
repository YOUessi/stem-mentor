"""Batch47: bounded exact witnesses; never general theorem/teacher/student proof certification."""
from __future__ import annotations
from fractions import Fraction
from math import comb,ceil

OPS=(
 "parallel_directions","supplementary_angle_directions","auxiliary_section_direction",
 "parallel_plane_sections","normal_line_directions","perpendicular_plane_line",
 "separate_line_plane","two_intersecting_directions_parallel_plane",
 "plane_contains_normal","sample_frequency","census_coverage",
 "fixed_sample_random_means","no_replacement_draws","stratified_mean",
 "budget_capacity","unequal_histogram_density","sample_arithmetic_mean",
 "percentile_nearest_rank","percentile_linear","binomial_likelihood",
)
SAMPLES={
 "parallel_directions":({"u":[1,0,0],"v":[3,0,0]},"PARALLEL_DIRECTIONS",{"u":[0,0,0],"v":[3,0,0]}),
 "supplementary_angle_directions":({"u":[1,0,0],"v":[1,1,0],"a":[-1,0,0],"b":[1,1,0]},"SUPPLEMENTARY",{"u":[1,0,0],"v":[1,1,0],"a":[0,1,0],"b":[1,1,0]}),
 "auxiliary_section_direction":({"p":[0,0,1],"d":[1,0,0],"n":[0,0,1],"beta":[0,1,0],"off":0},"PARALLEL_SECTION",{"p":[0,0,0],"d":[1,0,0],"n":[0,0,1],"beta":[0,1,0],"off":0}),
 "parallel_plane_sections":({"n":[0,0,1],"other":[0,0,2],"cut":[0,1,0],"first":0,"second":2},"PARALLEL_SECTIONS",{"n":[0,0,1],"other":[0,0,2],"cut":[0,0,1],"first":0,"second":2}),
 "normal_line_directions":({"n":[0,0,1],"d1":[0,0,2],"d2":[0,0,-3]},"PARALLEL_DIRECTIONS",{"n":[0,0,1],"d1":[0,0,0],"d2":[0,0,-3]}),
 "perpendicular_plane_line":({"n1":[0,1,0],"n2":[1,0,0],"u":[1,0,0]},"PERP_TO_SECOND_PLANE",{"n1":[0,1,0],"n2":[1,0,0],"u":[1,0,1]}),
 "separate_line_plane":({"p":[0,0,1],"d":[1,0,0],"n":[0,0,1],"off":0},"PARALLEL_DISTINCT",{"p":[0,0,0],"d":[1,0,0],"n":[0,0,1],"off":0}),
 "two_intersecting_directions_parallel_plane":({"p":[0,0,1],"d1":[1,0,0],"d2":[0,1,0],"n":[0,0,1],"off":0},"PARALLEL_PLANES",{"p":[0,0,1],"d1":[1,0,0],"d2":[2,0,0],"n":[0,0,1],"off":0}),
 "plane_contains_normal":({"n1":[0,1,0],"n2":[0,0,1],"d":[0,0,3]},"PERPENDICULAR_PLANES",{"n1":[0,1,0],"n2":[0,0,1],"d":[1,0,0]}),
 "sample_frequency":({"n":4,"k":3},"3/4",{"n":0,"k":0}),
 "census_coverage":({"N":30,"observed":30},"COUNT_EQUAL_ONLY_NOT_FRAME_VERIFIED",{"N":30,"observed":31}),
 "fixed_sample_random_means":({"a":[1,3],"b":[3,7]},"2;5",{"a":[1,3],"b":[3]}),
 "no_replacement_draws":({"N":6,"draws":[2,4,2,1],"n":3},"2,4,1",{"N":6,"draws":[2,4,2,1],"n":4}),
 "stratified_mean":({"n1":2,"n2":8,"m1":10,"m2":20},"18",{"n1":0,"n2":8,"m1":10,"m2":20}),
 "budget_capacity":({"budget":70,"fixed":20,"unit":5},"10",{"budget":70,"fixed":20,"unit":0}),
 "unequal_histogram_density":({"count1":4,"width1":1,"count2":6,"width2":2},"4;3",{"count1":4,"width1":0,"count2":6,"width2":2}),
 "sample_arithmetic_mean":({"values":[2,4,8]},"14/3",{"values":[]}),
 "percentile_nearest_rank":({"values":[0,10,20,30],"p":50},"10",{"values":[0,10,20,30],"p":0}),
 "percentile_linear":({"values":[0,10,20,30],"p":25},"15/2",{"values":[0,10,20,30],"p":-1}),
 "binomial_likelihood":({"n":4,"k":3,"p_num":1,"p_den":2},"1/4",{"n":4,"k":3,"p_num":1,"p_den":0}),
}
assert tuple(SAMPLES)==OPS

def dot(u,v): return sum(x*y for x,y in zip(u,v))
def cross(u,v):
    return [u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
def nz(u):return any(u)
def parallel(u,v):return not any(cross(u,v))
def require(condition):
    if not condition:raise ValueError("mathematical premise not established")
def vec(v):
    require(type(v) is list and len(v)==3 and all(type(x) is int for x in v))
    return v
def scalar(x): return str(x)
def mean(seq):return Fraction(sum(seq),len(seq))
def calc(op,d):
    if op in OPS[:9]:
        for k in d:
            if isinstance(d[k],list):vec(d[k])
    if op=="parallel_directions":
        require(nz(d["u"]) and nz(d["v"]) and parallel(d["u"],d["v"]))
        return "PARALLEL_DIRECTIONS" # coincidence unknown without positions
    if op=="supplementary_angle_directions":
        u,v,a,b=(d[k] for k in ("u","v","a","b"))
        require(all(nz(x) for x in (u,v,a,b)) and parallel(u,a) and parallel(v,b))
        require(not parallel(u,v)) # exclude collinear 0/180 deg angles
        signs=dot(u,a)*dot(v,b)
        return "SAME" if signs>0 else "SUPPLEMENTARY"
    if op=="auxiliary_section_direction":
        p,direction,n,b=(d[k] for k in ("p","d","n","beta"))
        require(nz(direction) and nz(n) and nz(b) and not parallel(n,b))
        require(dot(p,b)==d["off"] and dot(direction,b)==0)
        require(dot(direction,n)==0 and dot(p,n)!=0)
        require(parallel(direction,cross(n,b)))
        return "PARALLEL_SECTION"
    if op=="parallel_plane_sections":
        n,other,cut=(d[k] for k in ("n","other","cut"))
        require(nz(n) and nz(other) and nz(cut) and parallel(n,other))
        require(nz(cross(n,cut)) and nz(cross(other,cut)))
        # distinguish n·x=first versus other·x=second by proportionality
        idx=next(i for i,x in enumerate(n) if x!=0)
        require(d["first"]*other[idx]!=d["second"]*n[idx])
        return "PARALLEL_SECTIONS"
    if op=="normal_line_directions":
        n,u,v=(d[k] for k in ("n","d1","d2"))
        require(nz(n) and nz(u) and nz(v) and parallel(n,u) and parallel(n,v))
        return "PARALLEL_DIRECTIONS"
    if op=="perpendicular_plane_line":
        n1,n2,u=(d[k] for k in ("n1","n2","u"))
        require(all(nz(v) for v in (n1,n2,u)) and dot(n1,n2)==0)
        require(dot(u,n1)==0 and dot(u,cross(n1,n2))==0 and parallel(u,n2))
        return "PERP_TO_SECOND_PLANE"
    if op=="separate_line_plane":
        p,u,n=(d[k] for k in ("p","d","n"))
        require(nz(u) and nz(n) and dot(u,n)==0 and dot(p,n)!=d["off"])
        return "PARALLEL_DISTINCT"
    if op=="two_intersecting_directions_parallel_plane":
        p,u,v,n=(d[k] for k in ("p","d1","d2","n"))
        require(nz(n) and nz(cross(u,v)) and dot(u,n)==0 and dot(v,n)==0)
        require(dot(p,n)!=d["off"])
        return "PARALLEL_PLANES"
    if op=="plane_contains_normal":
        n1,n2,u=(d[k] for k in ("n1","n2","d"))
        require(all(nz(v) for v in (n1,n2,u)))
        require(dot(n1,n2)==0 and dot(u,n1)==0 and parallel(u,n2))
        return "PERPENDICULAR_PLANES"
    if op=="sample_frequency":
        require(0<d["n"]<=100 and 0<=d["k"]<=d["n"])
        return scalar(Fraction(d["k"],d["n"]))
    if op=="census_coverage":
        require(0<d["N"]<=100 and 0<=d["observed"]<=d["N"])
        return "COUNT_EQUAL_ONLY_NOT_FRAME_VERIFIED" if d["observed"]==d["N"] else "PARTIAL_COUNT_ONLY"
    if op=="fixed_sample_random_means":
        require(len(d["a"])==len(d["b"])>0)
        return scalar(mean(d["a"]))+";"+scalar(mean(d["b"]))
    if op=="no_replacement_draws":
        require(1<=d["N"]<=100 and 1<=d["n"]<=d["N"])
        seq=[]
        for x in d["draws"]:
            require(1<=x<=d["N"])
            if x not in seq:seq.append(x)
        require(len(seq)>=d["n"])
        return ",".join(map(str,seq[:d["n"]]))
    if op=="stratified_mean":
        require(d["n1"]>0 and d["n2"]>0)
        return scalar(Fraction(d["n1"]*d["m1"]+d["n2"]*d["m2"],d["n1"]+d["n2"]))
    if op=="budget_capacity":
        require(d["budget"]>=d["fixed"]>=0 and d["unit"]>0)
        return str((d["budget"]-d["fixed"])//d["unit"])
    if op=="unequal_histogram_density":
        require(d["count1"]>=0 and d["count2"]>=0 and d["width1"]>0 and d["width2"]>0)
        return scalar(Fraction(d["count1"],d["width1"]))+";"+scalar(Fraction(d["count2"],d["width2"]))
    if op=="sample_arithmetic_mean":
        require(len(d["values"])>0)
        return scalar(mean(d["values"]))
    if op=="percentile_nearest_rank":
        require(len(d["values"])>0 and 1<=d["p"]<=100)
        seq=sorted(d["values"])
        return str(seq[(len(seq)*d["p"]+99)//100-1])
    if op=="percentile_linear":
        require(len(d["values"])>0 and 0<=d["p"]<=100)
        seq=sorted(d["values"])
        position=Fraction((len(seq)-1)*d["p"],100)
        floor=position.numerator//position.denominator
        frac=position-floor
        return scalar(Fraction(seq[floor]) if floor==len(seq)-1 else (1-frac)*seq[floor]+frac*seq[floor+1])
    if op=="binomial_likelihood":
        n,k,p,q=(d[k] for k in ("n","k","p_num","p_den"))
        require(1<=n<=100 and 0<=k<=n and q>0 and 0<=p<=q)
        prob=Fraction(p,q)
        return scalar(comb(n,k)*prob**k*(1-prob)**(n-k))
    raise ValueError("unsupported")

def witness(op,params):
    result={"status":"CONDITIONS_NOT_ESTABLISHED","exact_value":None,
      "general_theorem_certified":False,"student_freeform_step_verified":False,
      "teacher_approved":False,"student_publishable":False}
    if type(op) is not str or op not in SAMPLES:
        result["status"]="UNSUPPORTED"
        return result
    shape=SAMPLES[op][0]
    if type(params) is not dict or set(params)!=set(shape):
        return result
    def safe(v):
        if type(v) is int:return -100<=v<=100
        if type(v) is list:return 0<=len(v)<=30 and all(type(x) is int and -100<=x<=100 for x in v)
        return False
    if not all(safe(v) for v in params.values()):return result
    try:
        result["exact_value"]=calc(op,params)
        result["status"]="FINITE_EXACT_CASE_ONLY"
    except (ValueError,TypeError,IndexError,ZeroDivisionError,OverflowError):
        pass
    return result
