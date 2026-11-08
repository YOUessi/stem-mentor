"""Batch29 exact finite witnesses: NEVER universal theorem or student-step certificates.
Only bounded rational, finite-probability and polynomial operands are accepted.
"""
from fractions import Fraction as F
from math import comb

def f(x):
    if isinstance(x, bool) or not isinstance(x, (str, int)) or len(str(x)) > 25:
        raise ValueError("Only bounded exact rational operands")
    z = F(str(x))
    if abs(z.numerator) > 1000000 or z.denominator > 1000000:
        raise ValueError("Operand out of finite audit bounds")
    return z

def vec(x, n=None):
    if not isinstance(x, list) or not 1 <= len(x) <= 3 or (n is not None and len(x) != n):
        raise ValueError("Dimension mismatch")
    return tuple(f(v) for v in x)

def dot(x, y):
    return sum((a*b for a,b in zip(x,y)),F(0))

def norm2(x): return dot(x,x)

def finite_probability(d):
    weights = [f(z) for z in d["weights"]]
    if not 1 <= len(weights) <= 8 or any(z<0 for z in weights) or sum(weights)!=1:
        raise ValueError("Finite probability law required")
    n=len(weights)
    def event(key):
        a=d[key]
        if not isinstance(a,list) or any(not isinstance(z,int) or isinstance(z,bool) or not 0<=z<n for z in a) or len(a)!=len(set(a)):
            raise ValueError("Events must be finite subsets of sample space")
        return set(a)
    return weights,event

def witness(op,d):
    if op=="metric_expansion":
        u=vec(d["u"]);v=vec(d["v"],len(u))
        plus=tuple(a+b for a,b in zip(u,v));minus=tuple(a-b for a,b in zip(u,v))
        return dict(plus_norm2=norm2(plus),minus_norm2=norm2(minus),
                    cross_term=2*dot(u,v),pythagorean_iff=norm2(plus)==norm2(u)+norm2(v),
                    parallelogram=norm2(plus)+norm2(minus)==2*(norm2(u)+norm2(v)))
    if op=="dot_angle_guard":
        u=vec(d["u"]);v=vec(d["v"],len(u))
        if not norm2(u) or not norm2(v): raise ValueError("Angle undefined for a zero vector")
        return dict(dot=dot(u,v),norm_product2=norm2(u)*norm2(v),
                    cauchy_gap=norm2(u)*norm2(v)-dot(u,v)**2,perpendicular=dot(u,v)==0)
    if op=="line_general":
        A,B=f(d["A"]),f(d["B"])
        if A==B==0: raise ValueError("Zero line normal")
        x0,y0=f(d["x0"]),f(d["y0"])
        x,y=f(d["x"]),f(d["y"])
        return dict(normal_norm2=A*A+B*B,evaluation=A*(x-x0)+B*(y-y0),
                    direction=(-B,A),point_on_line=A*(x-x0)+B*(y-y0)==0)
    if op=="line_relations":
        A,B,C,D=f(d["A"]),f(d["B"]),f(d["C"]),f(d["D"])
        if A==B==0 or C==D==0: raise ValueError("Both normals must be nonzero")
        det=A*D-B*C
        return dict(det=det,dot=A*C+B*D,parallel=det==0,perpendicular=A*C+B*D==0)
    if op=="point_line_distance":
        A,B,C,x,y=map(f,(d["A"],d["B"],d["C"],d["x"],d["y"]))
        den=A*A+B*B
        if not den: raise ValueError("Nonzero normal required")
        return dict(distance_squared=(A*x+B*y+C)**2/den,squared_denominator=den)
    if op=="quadratic_vertex":
        a,b,c,x=map(f,(d["a"],d["b"],d["c"],d["x"]))
        if not a: raise ValueError("Not quadratic")
        h=-b/(2*a);k=c-b*b/(4*a)
        return dict(vertex=h,extremal_value=k,value=a*x*x+b*x+c,
                    completed_square=a*(x-h)**2+k,extremum_kind="MIN" if a>0 else "MAX")
    if op=="quadratic_sign":
        a,r1,r2,x=map(f,(d["a"],d["r1"],d["r2"],d["x"]))
        if not a or not r1<r2: raise ValueError("Nonzero quadratic leading coefficient and two ordered distinct roots required")
        val=a*(x-r1)*(x-r2)
        return dict(value=val,is_outside=x<r1 or x>r2,
                    sign_matches_leading=(val*a>0) if x not in (r1,r2) else None)
    if op=="conditional_probability":
        weights,event=finite_probability(d);A=event("A");B=event("B")
        pa=sum((weights[i] for i in A),F(0))
        if not pa: raise ValueError("Condition event must have positive probability")
        pab=sum((weights[i] for i in A & B),F(0))
        return dict(p_a=pa,p_intersection=pab,p_b_given_a=pab/pa,multiplication_identity=pa*(pab/pa)==pab)
    if op=="bayes_partition":
        weights,event=finite_probability(d);B=event("B")
        cells=d["partition"]
        if not isinstance(cells,list) or len(cells)<2: raise ValueError("Partition requires at least two events")
        pset=[set(x) for x in cells]
        if any(not x for x in pset) or any(x&y for i,x in enumerate(pset) for y in pset[i+1:]) or set.union(*pset)!=set(range(len(weights))):
            raise ValueError("Complete disjoint nonempty event partition required")
        pb=sum((weights[i] for i in B),F(0))
        if not pb: raise ValueError("Bayes observation must have positive probability")
        priors=[sum((weights[i] for i in cell),F(0)) for cell in pset]
        if any(not p for p in priors): raise ValueError("Conditional event prior must be positive")
        posterior=[sum((weights[i] for i in cell&B),F(0))/pb for cell in pset]
        return dict(p_b=pb,priors=priors,posterior=posterior,normalizes=sum(posterior)==1)
    if op=="variance_affine_covariance":
        weights,event=finite_probability(d)
        X=[f(x) for x in d["X"]];Y=[f(x) for x in d["Y"]]
        if len(X)!=len(weights) or len(Y)!=len(weights):raise ValueError("Finite samples mismatch")
        a=f(d["a"]);b=f(d["b"])
        E=lambda vals:sum((p*x for p,x in zip(weights,vals)),F(0))
        EX=E(X);EY=E(Y)
        vx=E([(x-EX)**2 for x in X]);vy=E([(y-EY)**2 for y in Y])
        cov=E([(x-EX)*(y-EY) for x,y in zip(X,Y)])
        z=[x+y for x,y in zip(X,Y)]
        az=[a*x+b for x in X]
        return dict(cov=cov,variance_x=vx,variance_y=vy,variance_sum=E([(x-E(z))**2 for x in z]),
                    variance_sum_formula=vx+vy+2*cov,variance_affine=E([(x-E(az))**2 for x in az]),
                    variance_affine_formula=a*a*vx)
    if op=="finite_series":
        n=d["n"]; q=f(d["q"]);a=f(d["a"]);diff=f(d["diff"])
        if not isinstance(n,int) or isinstance(n,bool) or not 1<=n<=100:raise ValueError("Finite natural length n>=1")
        geo=sum((a*q**j for j in range(n)),F(0))
        closed=a*n if q==1 else a*(1-q**n)/(1-q)
        arith=sum((a+j*diff for j in range(n)),F(0))
        square=sum(k*k for k in range(1,n+1))
        return dict(geometric=geo,geometric_closed=closed,arithmetic=arith,arithmetic_closed=n*(2*a+(n-1)*diff)/2,
                    square_sum=square,square_closed=n*(n+1)*(2*n+1)//6)
    if op=="double_angle":
        c,s=f(d["c"]),f(d["s"])
        if c*c+s*s!=1:raise ValueError("Unit-circle cosine and sine must be consistent")
        return dict(cos2=c*c-s*s,cos2_alternative=1-2*s*s,sin2=2*s*c,
                    cosine_reduction=(1+(c*c-s*s))/2)
    if op=="vector_projection":
        a=vec(d["a"]);b=vec(d["b"],len(a))
        if not norm2(b):raise ValueError("Projection direction cannot be zero")
        coeff=dot(a,b)/norm2(b);p=tuple(coeff*x for x in b)
        residual=tuple(x-y for x,y in zip(a,p))
        return dict(projection_coeff=coeff,projection=list(p),residual_dot_direction=dot(residual,b),
                    residual_squared=norm2(residual))
    if op=="complex_quotient":
        a,b,c,e=map(f,(d["a"],d["b"],d["c"],d["d"]))
        denom=c*c+e*e
        if denom==0:raise ValueError("Cannot divide by zero complex number")
        real=(a*c+b*e)/denom;imag=(b*c-a*e)/denom
        return dict(denominator=denom,real=real,imag=imag,product_re=real*c-imag*e,product_im=real*e+imag*c)
    if op=="finite_composition":
        g=d["g"];h=d["f"];x=str(d["x"])
        if not isinstance(g,dict) or not isinstance(h,dict) or any(len(s)>20 for s in (*g.keys(),*h.keys())):raise ValueError("Finite function mappings")
        if x not in g or str(g[x]) not in h:raise ValueError("Both domains must admit evaluation")
        return dict(intermediate=str(g[x]),output=h[str(g[x])],outer_domain_ok=True)
    if op=="polynomial_tangent":
        coeff=[f(x) for x in d["coeff"]]; x=f(d["x"])
        if not isinstance(d["coeff"],list) or not 1<=len(coeff)<=6:raise ValueError("Bounded polynomial")
        polynomial=sum((a*x**i for i,a in enumerate(coeff)),F(0))
        derivative=sum((i*a*x**(i-1) for i,a in enumerate(coeff) if i),F(0))
        return dict(f_x=polynomial,derivative=derivative,tangent_intercept=polynomial-derivative*x)
    if op=="ellipse_parametric":
        a,b,c,s=map(f,(d["a"],d["b"],d["c"],d["s"]))
        if a<=0 or b<=0 or c*c+s*s!=1:raise ValueError("Positive semiaxes and unit-circle parameters")
        return dict(x=a*c,y=b*s,ellipse_normalized=(a*c/a)**2+(b*s/b)**2)
    if op=="plane_perpendicular":
        u=vec(d["u"],3);v=vec(d["v"],3);w=vec(d["w"],3)
        cross=(v[1]*w[2]-v[2]*w[1],v[2]*w[0]-v[0]*w[2],v[0]*w[1]-v[1]*w[0])
        if not norm2(u) or not norm2(cross):raise ValueError("Nonzero line and independent plane directions required")
        if dot(u,v) or dot(u,w):raise ValueError("Line must be perpendicular to both independent spanning directions")
        return dict(dot_with_v=dot(u,v),dot_with_w=dot(u,w),plane_direction_cross_norm2=norm2(cross),
                    u_parallel_plane_normal=norm2(cross)*norm2(u)==dot(u,cross)**2)
    if op=="matrix_inverse_2":
        a,b,c,e=map(f,(d["a"],d["b"],d["c"],d["d"]))
        det=a*e-b*c
        if not det:raise ValueError("Singular matrix has no inverse")
        inv=(e/det,-b/det,-c/det,a/det)
        return dict(determinant=det,inverse=list(inv),
                    left_identity=(a*inv[0]+b*inv[2],a*inv[1]+b*inv[3],c*inv[0]+e*inv[2],c*inv[1]+e*inv[3]))
    if op=="orthogonal_isometry":
        q=d["Q"]
        if not isinstance(q,list) or len(q)!=2 or any(not isinstance(r,list) or len(r)!=2 for r in q):raise ValueError("2x2 matrix")
        a,b,c,e=map(f,(*q[0],*q[1]));x,y=vec(d["u"],2)
        if a*a+c*c!=1 or b*b+e*e!=1 or a*b+c*e!=0:raise ValueError("Q must be orthogonal")
        return dict(det=a*e-b*c,norm2_original=x*x+y*y,norm2_transformed=(a*x+b*y)**2+(c*x+e*y)**2)
    raise KeyError("Unsupported finite condition operation")

SUPPORTED=frozenset((
    "metric_expansion","dot_angle_guard","line_general","line_relations","point_line_distance",
    "quadratic_vertex","quadratic_sign","conditional_probability","bayes_partition",
    "variance_affine_covariance","finite_series","double_angle","vector_projection",
    "complex_quotient","finite_composition","polynomial_tangent","ellipse_parametric",
    "plane_perpendicular","matrix_inverse_2","orthogonal_isometry"
))
def evaluate(op, d):
    safety=dict(complete_theorem_certified=False,student_step_verified=False,
                teacher_approved=False,official_curriculum_atom_verified=False)
    if op not in SUPPORTED:return dict(status="UNSUPPORTED",reason="Unknown operation",**safety)
    try:
        w=witness(op,d)
        # JSON-compatible exact rationals, no float rounding.
        def normalize(x):
            if isinstance(x,F): return str(x)
            if isinstance(x,(list,tuple)):return [normalize(t) for t in x]
            if isinstance(x,dict):return {k:normalize(v) for k,v in x.items()}
            return x
        return dict(status="VERIFIED_FINITE_INSTANCE",operation=op,witness=normalize(w),**safety)
    except (ValueError,TypeError,KeyError,ZeroDivisionError,OverflowError,IndexError) as exc:
        return dict(status="CONDITIONS_NOT_ESTABLISHED",operation=op,reason=str(exc),**safety)
