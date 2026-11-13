"""Twelve exact, narrowly scoped P0 premise guards. No general proof certification."""
from __future__ import annotations
from fractions import Fraction as F

OPERATIONS=("space_distance","line_plane_strict_parallel","two_circle_points","parabola_focus",
 "ellipse_tangent","real_log_quotient","real_quadratic_roots","orthogonal_pythagoras",
 "finite_union_bound","discrete_covariance","ellipse_focal_parameter","real_circle_radius")

class MissingCondition(ValueError):
    pass

def require(ok,why):
    if not ok: raise MissingCondition(why)

def q(v):
    if type(v) is dict:
        require(set(v)=={"num","den"} and type(v["num"]) is int and type(v["den"]) is int
                and v["den"]!=0,"Invalid exact rational object")
        return F(v["num"],v["den"])
    require(type(v) is int or type(v) is F,"Nonexact or boolean number")
    return F(v)

def seq(v,n=None):
    require(type(v) in (list,tuple) and (n is None or len(v)==n),"Wrong vector/list length")
    require(len(v)>0,"Empty vector")
    return tuple(q(x) for x in v)

def dot(u,v):
    require(len(u)==len(v),"Vector dimensions disagree")
    return sum((x*y for x,y in zip(u,v)),F(0))

def calc(op,p):
    require(op in OPERATIONS,"Unsupported mathematical claim")
    require(type(p) is dict,"Instance must be a mapping")
    if op=="space_distance":
        u,v=seq(p["u"],3),seq(p["v"],3)
        d2=sum((x-y)**2 for x,y in zip(u,v))
        require(d2==q(p["distance_squared"]),"Squared Euclidean distance wrong")
        return {"distance_squared":str(d2)}
    if op=="line_plane_strict_parallel":
        n,v,x=seq(p["normal"],3),seq(p["direction"],3),seq(p["point"],3)
        d=q(p["plane_offset"])
        require(dot(n,n)>0 and dot(v,v)>0,"Plane normal/direction zero")
        require(dot(n,v)==0,"Direction does not lie parallel to plane")
        require(dot(n,x)!=d,"Line is inside the plane; not strictly disjoint")
        return {"normal_dot_direction":"0","disjoint":True}
    if op=="two_circle_points":
        r1,r2=q(p["r1"]),q(p["r2"])
        c1,c2=seq(p["c1"],2),seq(p["c2"],2)
        require(r1>0 and r2>0,"Both circle radii must be positive")
        d2=sum((x-y)**2 for x,y in zip(c1,c2))
        require((r1-r2)**2 < d2 < (r1+r2)**2,
                "Two distinct intersections require strict triangle inequalities")
        return {"center_distance_squared":str(d2),"intersection_count":2}
    if op=="parabola_focus":
        p0=q(p["p"])
        require(p0!=0,"Degenerate zero p")
        focus=seq(p["focus"],2)
        require(focus==(p0,F(0)) and q(p["directrix_x"])==-p0,
                "Focus/directrix cannot be inferred from the supplied p")
        return {"focus":[str(p0),"0"],"directrix_x":str(-p0)}
    if op=="ellipse_tangent":
        a,b=q(p["a"]),q(p["b"])
        require(a>0 and b>0,"Semiaxes must be positive")
        x0,y0=seq(p["tangent_point"],2)
        x,y=seq(p["line_point"],2)
        require(x0*x0/a**2+y0*y0/b**2==1,"Claimed tangency point is not on ellipse")
        require(x0*x/a**2+y0*y/b**2==1,"Claimed point is not on tangent line")
        return {"point_on_ellipse":True,"point_on_tangent":True}
    if op=="real_log_quotient":
        a,x,y=q(p["base"]),q(p["x"]),q(p["y"])
        require(a>0 and a!=1 and x>0 and y>0,"Real logarithm domain violated")
        m,n=p["exp_x"],p["exp_y"]
        require(type(m) is int and type(n) is int and -12<=m<=12 and -12<=n<=12,
                "Only bounded integral logarithm witness exponents supported")
        require(a**m==x and a**n==y,"Power witnesses mismatch")
        require(q(p["claimed_difference"])==m-n,"Logarithm difference wrong")
        return {"integer_log_difference":m-n,"ratio":str(x/y)}
    if op=="real_quadratic_roots":
        a,b,c=(q(p[k]) for k in ("a","b","c"))
        require(a!=0,"Not a quadratic equation")
        delta=b*b-4*a*c
        require(delta>=0,"No real roots")
        roots=seq(p["roots"],2)
        require(all(a*t*t+b*t+c==0 for t in roots),"Proposed roots invalid")
        require(roots[0]+roots[1]==-b/a and roots[0]*roots[1]==c/a,
                "Missing or duplicated roots")
        return {"discriminant":str(delta)}
    if op=="orthogonal_pythagoras":
        u,v=seq(p["u"]),seq(p["v"])
        require(len(u)==len(v) and len(u) in (2,3),"Expected equal 2D or 3D vectors")
        require(dot(u,v)==0,"Vectors not orthogonal")
        require(dot(tuple(x+y for x,y in zip(u,v)),tuple(x+y for x,y in zip(u,v)))
                ==dot(u,u)+dot(v,v),"Squared-norm identity fails")
        return {"dot_product":"0"}
    if op=="finite_union_bound":
        w=seq(p["weights"])
        require(all(x>=0 for x in w) and sum(w)==1,"Not a probability mass function")
        a,b=p["A"],p["B"]
        require(type(a) in (list,tuple) and type(b) in (list,tuple),"Events must be explicit index sets")
        require(all(type(i) is int and 0<=i<len(w) for i in a+b),"Event index outside sample space")
        require(len(set(a))==len(a) and len(set(b))==len(b),"Duplicate event indices")
        pu=sum((w[i] for i in set(a)|set(b)),F(0))
        rhs=sum((w[i] for i in a),F(0))+sum((w[i] for i in b),F(0))
        require(pu<=rhs,"Union bound violated")
        return {"union_probability":str(pu),"sum_bound":str(rhs)}
    if op=="discrete_covariance":
        xs,ys,ws=seq(p["xs"]),seq(p["ys"]),seq(p["weights"])
        require(len(xs)==len(ys)==len(ws) and all(t>=0 for t in ws) and sum(ws)==1,
                "Invalid joint sample / probability weights")
        ex=sum((w*x for w,x in zip(ws,xs)),F(0))
        ey=sum((w*y for w,y in zip(ws,ys)),F(0))
        cov=sum((w*(x-ex)*(y-ey) for w,x,y in zip(ws,xs,ys)),F(0))
        require(cov==q(p["claimed_covariance"]),"Finite covariance identity incorrect")
        return {"covariance":str(cov)}
    if op=="ellipse_focal_parameter":
        a,b=q(p["a"]),q(p["b"])
        require(a>b>0,"This focal-axis convention requires a>b>0")
        c2=a*a-b*b
        require(q(p["c_squared"])==c2,"Focal parameter wrong")
        return {"c_squared":str(c2)}
    if op=="real_circle_radius":
        D,E,C=(q(p[k]) for k in ("D","E","C"))
        r2=(D*D+E*E)/4-C
        require(r2>0,"Zero or negative radius squared is not a nondegenerate circle")
        require(r2==q(p["radius_squared"]),"Square completion radius is wrong")
        return {"radius_squared":str(r2)}
    raise AssertionError("Unknown operation")

def check(op,instance):
    try: return "FINITE_EXACT_WITNESS_ONLY",calc(op,instance)
    except (KeyError,TypeError,MissingCondition,ValueError,OverflowError,ZeroDivisionError,IndexError) as exc:
        return "CONDITIONS_NOT_ESTABLISHED",{"reason":str(exc)}
