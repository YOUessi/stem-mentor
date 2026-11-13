"""Curated EXACT arithmetic witnesses for Batch78 teacher-only review cards.

This does not certify general proofs, arbitrary student text, or any official
curriculum atom. No parsing/eval of user-supplied mathematical expressions.
"""
from fractions import Fraction as F
from math import comb
from sympy import Integer, Rational, Matrix, symbols, sqrt, simplify, diff, log

CASE_OPS=("log_quotient","change_base","quadratic","hypergeometric",
          "quotient","mvt","ellipse","line_plane","point_line","inverse2",
          "cramer3","projection","conditional","complement","circle","angle")
X=symbols("x",real=True)
GOOD={
 "log_quotient":{"a":2,"x":12,"y":3},
 "change_base":{"a":2,"b":4,"x":8},
 "quadratic":{"a":2,"b":-5,"c":2},
 "hypergeometric":{"N":8,"K":3,"n":2,"k":1},
 "quotient":{"c":2,"x":1},
 "mvt":{"a":1,"b":3},
 "ellipse":{"a":3,"b":2,"point":[3,0]},
 "line_plane":{"u":[1,0,0],"n":[0,0,1],"P":[0,0,0],"Q":[0,0,0]},
 "point_line":{"a":3,"b":4,"c":-12,"P":[0,0]},
 "inverse2":{"A":[[1,2],[3,4]]},
 "cramer3":{"A":[[2,0,0],[0,3,0],[0,0,5]],"b":[4,6,10]},
 "projection":{"a":[3,4],"b":[1,0]},
 "conditional":{"N":6,"A":[1,2,3],"B":[3,4]},
 "complement":{"N":4,"A":[1,2],"B":[1,3]},
 "circle":{"r":5,"y":3},
 "angle":{"u":[1,0,0],"n":[0,0,1]},
}
BAD={
 "log_quotient":{"a":2,"x":-4,"y":-2},
 "change_base":{"a":1,"b":4,"x":8},
 "quadratic":{"a":0,"b":2,"c":-4},
 "hypergeometric":{"N":5,"K":1,"n":4,"k":3},
 "quotient":{"c":2,"x":-2},
 "mvt":{"a":-2,"b":2},
 "ellipse":{"a":3,"b":2,"point":[0,0]},
 "line_plane":{"u":[1,0,0],"n":[0,0,1],"P":[0,0,1],"Q":[0,0,0]},
 "point_line":{"a":0,"b":0,"c":1,"P":[0,0]},
 "inverse2":{"A":[[1,2],[2,4]]},
 "cramer3":{"A":[[1,0,0],[0,1,0],[0,0,0]],"b":[0,0,0]},
 "projection":{"a":[3,4],"b":[0,0]},
 "conditional":{"N":6,"A":[],"B":[3,4]},
 "complement":{"N":4,"A":[1,2],"B":[1,2]},
 "circle":{"r":0,"y":0},
 "angle":{"u":[1,0,0],"n":[0,0,0]},
}
assert len(GOOD)==len(BAD)==len(CASE_OPS)==16

def _integers_only(value):
    if type(value) is int:return
    if type(value) in (list,tuple):
        if len(value)>16:raise ValueError("Fixture too large")
        for x in value:_integers_only(x)
        return
    if type(value) is dict:
        if len(value)>16:raise ValueError("Fixture too large")
        for k,v in value.items():
            if type(k) is not str:raise ValueError("Keys must be strings")
            _integers_only(v)
        return
    raise ValueError("No float, bool, arbitrary expression, object or untrusted string")

def _norm(v,n):
    if len(v)!=n or any(type(z) is not int for z in v):
        raise ValueError("Wrong vector dimensions")
    return [Integer(z) for z in v]

def check(op: str, inp: dict):
    """Return finite exact certificate or explicit conditions-not-established.

    All arithmetic uses integers, rationals, symbolic identities. Does not claim
    anything about mathematical correctness of the historical original proof.
    """
    if op not in CASE_OPS or type(inp) is not dict:
        raise ValueError("Unknown math operation")
    _integers_only(inp)
    ok="VERIFIED_FINITE_INSTANCE"
    no="CONDITIONS_NOT_ESTABLISHED"
    evidence={}
    if op=="log_quotient":
        a,x,y=inp["a"],inp["x"],inp["y"]
        if a<=0 or a==1 or x<=0 or y<=0:return no,{"failed_condition":"both_real_log_arguments_positive_and_base_valid"}
        evidence["log_identity"]=str(simplify(log(Rational(x,y),a)-log(x,a)+log(y,a)))
        if evidence["log_identity"]!="0":raise AssertionError("Incorrect log identity")
    elif op=="change_base":
        a,b,x=inp["a"],inp["b"],inp["x"]
        if min(a,b,x)<=0 or a==1 or b==1:return no,{"failed_condition":"both_bases_valid"}
        lhs=log(x,a);rhs=log(x,b)/log(a,b)
        evidence["difference"]=str(simplify(lhs-rhs))
        if simplify(lhs-rhs)!=0:raise AssertionError("Change of base violated")
    elif op=="quadratic":
        a,b,c=inp["a"],inp["b"],inp["c"]
        if a==0:return no,{"failed_condition":"quadratic_leading_coefficient_nonzero"}
        delta=b*b-4*a*c
        evidence["delta"]=delta
        if delta>=0:
            roots=[(-Integer(b)+s*sqrt(delta))/(2*a) for s in (-1,1)]
            if any(simplify(a*r*r+b*r+c)!=0 for r in roots):raise AssertionError("Invalid roots")
            evidence["distinct_real_roots"]=1 if delta==0 else 2
        else:evidence["distinct_real_roots"]=0
    elif op=="hypergeometric":
        N,K,n,k=[inp[z] for z in ("N","K","n","k")]
        if N<1 or not (0<=K<=N and 0<=n<=N and max(0,n-N+K)<=k<=min(n,K)):
            return no,{"failed_condition":"feasible_sample_support"}
        p=F(comb(K,k)*comb(N-K,n-k),comb(N,n))
        evidence["probability"]=str(p)
        if not 0<=p<=1:raise AssertionError("Invalid probability")
    elif op=="quotient":
        c,x0=inp["c"],inp["x"]
        if x0+c==0:return no,{"failed_condition":"denominator_nonzero_at_derivative_point"}
        u=X*X+1;v=X+c
        derivative=diff(u/v,X).subs(X,x0)
        formula=((diff(u,X)*v-u*diff(v,X))/v**2).subs(X,x0)
        if simplify(derivative-formula)!=0:raise AssertionError("Quotient rule")
        evidence["exact_derivative"]=str(derivative)
    elif op=="mvt":
        a,b=inp["a"],inp["b"]
        if a>=b or a<0:return no,{"failed_condition":"positive_derivative_on_open_interval_of_square"}
        evidence["f_b_minus_f_a"]=b*b-a*a
        if not b*b>a*a:raise AssertionError("MVT monotonicity")
    elif op=="ellipse":
        a,b=inp["a"],inp["b"]
        x0,y0=_norm(inp["point"],2)
        if a<=0 or b<=0 or simplify(x0*x0/Rational(a*a)+y0*y0/Rational(b*b))!=1:
            return no,{"failed_condition":"nondegenerate_ellipse_point_membership"}
        evidence["tangent_equation"]=f"({x0}/{a*a})*x+({y0}/{b*b})*y=1"
        if x0==0 and y0==0:raise AssertionError("Zero gradient")
    elif op=="line_plane":
        u,n,P,Q=[_norm(inp[k],3) for k in ("u","n","P","Q")]
        du=sum(u[i]*n[i] for i in range(3))
        dp=sum((P[i]-Q[i])*n[i] for i in range(3))
        if all(t==0 for t in u) or all(t==0 for t in n) or du!=0 or dp!=0:
            return no,{"failed_condition":"nonzero_vectors_and_point_membership_and_direction"}
        evidence["linear_identity"]=[int(dp),int(du)]
    elif op=="point_line":
        a,b,c=inp["a"],inp["b"],inp["c"]
        p=_norm(inp["P"],2)
        if a*a+b*b==0:return no,{"failed_condition":"nonzero_line_normal"}
        value=simplify(abs(a*p[0]+b*p[1]+c)/sqrt(a*a+b*b))
        evidence["distance"]=str(value)
        if value<0:raise AssertionError("Negative distance")
    elif op=="inverse2":
        A=inp["A"]
        if len(A)!=2 or any(len(row)!=2 for row in A):raise ValueError("2x2 only")
        m=Matrix(A)
        if m.det()==0:return no,{"failed_condition":"nonzero_determinant"}
        inv=m.inv()
        if m*inv!=Matrix.eye(2) or inv*m!=Matrix.eye(2):raise AssertionError("Inverse")
        evidence["inverse"]=[[str(x) for x in row] for row in inv.tolist()]
    elif op=="cramer3":
        A=inp["A"];b=inp["b"]
        if len(A)!=3 or any(len(row)!=3 for row in A) or len(b)!=3:
            raise ValueError("3x3 only")
        m=Matrix(A);v=Matrix(b)
        if m.det()==0:return no,{"failed_condition":"nonzero_determinant"}
        xs=[]
        for i in range(3):
            mi=m.copy();mi[:,i]=v
            xs.append(mi.det()/m.det())
        if m*Matrix(xs)!=v:raise AssertionError("Cramer")
        evidence["solution"]=[str(z) for z in xs]
    elif op=="projection":
        a,b=inp["a"],inp["b"]
        if len(a)!=len(b) or len(a) not in (2,3):raise ValueError("dimension mismatch")
        aa=Matrix(a);bb=Matrix(b)
        denom=bb.dot(bb)
        if denom==0:return no,{"failed_condition":"projection_nonzero_direction"}
        p=(aa.dot(bb)/denom)*bb
        if (aa-p).dot(bb)!=0:raise AssertionError("Projection residual")
        evidence["projection"]=[str(z) for z in p]
    elif op in ("conditional","complement"):
        N=inp["N"]
        samples_a, samples_b = inp["A"], inp["B"]
        if not isinstance(samples_a, list) or not isinstance(samples_b, list):
            raise ValueError("Events must be explicitly enumerated lists")
        if len(samples_a) != len(set(samples_a)) or len(samples_b) != len(set(samples_b)):
            return no,{"failed_condition":"duplicated_event_outcome"}
        A,B=set(samples_a),set(samples_b)
        if N<1 or any(not 1<=x<=N for x in A|B):
            return no,{"failed_condition":"uniform_sample_space"}
        if op=="conditional":
            if not A:return no,{"failed_condition":"condition_event_nonzero"}
            pa=F(len(A),N);pba=F(len(A&B),len(A))
            if pa*pba!=F(len(A&B),N):raise AssertionError("Conditional formula")
            evidence["intersection"]=str(pa*pba)
        else:
            if F(len(A&B),N)!=F(len(A)*len(B),N*N):
                return no,{"failed_condition":"independence_not_established"}
            ac=set(range(1,N+1))-A;bc=set(range(1,N+1))-B
            if F(len(ac&bc),N)!=F(len(ac)*len(bc),N*N):
                raise AssertionError("Complement independence")
            evidence["double_complement_intersection"]=str(F(len(ac&bc),N))
    elif op=="circle":
        r,y=inp["r"],inp["y"]
        if r<=0:return no,{"failed_condition":"positive_circle_radius"}
        sign=r*r-y*y
        evidence["intersection_count"]=(2 if sign>0 else 1 if sign==0 else 0)
    elif op=="angle":
        u=_norm(inp["u"],3);n=_norm(inp["n"],3)
        du=sum(x*x for x in u);dn=sum(x*x for x in n)
        if du==0 or dn==0:return no,{"failed_condition":"nonzero_line_and_plane_normals"}
        dp=sum(u[i]*n[i] for i in range(3))
        value=simplify(abs(dp)/sqrt(du*dn))
        if not (0<=value<=1):raise AssertionError("Invalid angle sine")
        evidence["sin_theta"]=str(value)
    return ok,evidence
