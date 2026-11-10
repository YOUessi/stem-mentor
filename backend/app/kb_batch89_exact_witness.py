"""Batch89 bounded EXACT math witnesses for twelve distinct unlinked P0 steps.

Inputs here are explicitly fixed audit fixtures, NOT a general-purpose proof
checker; never certify a theorem or a student's unrestricted solution.
"""
from fractions import Fraction as F
from sympy import Matrix
NAMES=("induction","orthogonal_pythagorean","sum_squares","parallelogram",
       "ellipse_parametric","quadratic_vertex","log_inverse","sin_sum",
       "three_basis_unique","expectation_linearity","vector_rank","matrix_inverse")


DOMAIN_CASES={
    "induction":((8,),(-1,)),
    "orthogonal_pythagorean":(((3,0),(0,4)),((1,0),(1,0))),
    "sum_squares":((4,),(-1,)),
    "parallelogram":(((1,2),(2,-1)),((1,2),(1,2,3))),
    "ellipse_parametric":((3,2),(0,2)),
    "quadratic_vertex":((2,-8,3),(0,-8,3)),
    "log_inverse":((3,-2),(1,-2)),
    "sin_sum":(((F(3,5),F(4,5)),(F(5,13),F(12,13))),((2,0),(F(5,13),F(12,13)))),
    "three_basis_unique":((((1,0,0),(0,1,0),(0,0,1)),),(((1,0,0),(2,0,0),(0,0,1)),)),
    "expectation_linearity":((((0,0,F(1,2)),(2,2,F(1,2))),),(((0,0,F(1,2)),),)),
    "vector_rank":(( ((1,0),(0,1),(1,1)), ),( ((1,0),(0,1,2)), )),
    "matrix_inverse":((((2,1),(1,1)),),(((1,2),(2,4)),)),
}

def exact_number(x):
    return (type(x) is int or type(x) is F)

def conditions_established(op, *args):
    """Finite input contract; rejects missing domain assumptions and invalid shapes."""
    if op not in DOMAIN_CASES:
        return False
    if op in ("induction","sum_squares"):
        return len(args)==1 and type(args[0]) is int and args[0]>=0
    if op=="orthogonal_pythagorean" or op=="parallelogram":
        if len(args)!=2: return False
        a,b=args
        if not (isinstance(a,(tuple,list)) and isinstance(b,(tuple,list))
                and len(a)==len(b)>0 and all(exact_number(v) for v in (*a,*b))):
            return False
        return op=="parallelogram" or sum(x*y for x,y in zip(a,b))==0
    if op=="ellipse_parametric":
        return len(args)==2 and all(exact_number(v) for v in args) and args[0]>0 and args[1]>0
    if op=="quadratic_vertex":
        return len(args)==3 and all(exact_number(v) for v in args) and args[0]!=0
    if op=="log_inverse":
        return len(args)==2 and all(exact_number(v) for v in args) and args[0]>0 and args[0]!=1 and type(args[1]) is int
    if op=="sin_sum":
        return (len(args)==2 and all(isinstance(x,(tuple,list)) and len(x)==2 for x in args)
            and all(exact_number(v) for x in args for v in x)
            and all(x[0]**2+x[1]**2==1 for x in args))
    if op=="three_basis_unique":
        if len(args)!=1 or not isinstance(args[0],(tuple,list)): return False
        rows=args[0]
        return (len(rows)==3 and all(len(r)==3 and all(exact_number(v) for v in r) for r in rows)
                and Matrix(rows).det()!=0)
    if op=="expectation_linearity":
        if len(args)!=1 or not isinstance(args[0],(tuple,list)): return False
        rows=args[0]
        return (len(rows)>0 and all(len(r)==3 and all(exact_number(v) for v in r) for r in rows)
            and all(r[2]>=0 for r in rows) and sum(r[2] for r in rows)==1)
    if op=="vector_rank":
        if len(args)!=1 or not isinstance(args[0],(tuple,list)): return False
        rows=args[0]
        return (len(rows)>0 and len(rows[0])>0
            and all(isinstance(r,(tuple,list)) and len(r)==len(rows[0])
                     and all(exact_number(v) for v in r) for r in rows))
    if op=="matrix_inverse":
        if len(args)!=1 or not isinstance(args[0],(tuple,list)): return False
        rows=args[0]
        return (len(rows)==2 and all(isinstance(r,(tuple,list)) and len(r)==2
            and all(exact_number(v) for v in r) for r in rows)
            and Matrix(rows).det()!=0)
    return False

def packet(op,positive,negative,evidence):
    assert positive is True and negative is True, (op,positive,negative)
    good,bad=DOMAIN_CASES[op]
    assert conditions_established(op,*good) is True, op
    assert conditions_established(op,*bad) is False, op
    return {"operation":op,"status":"FINITE_EXACT_WITNESS_ONLY",
        "valid_fixture_passed":True,"invalid_premise_rejected":True,
        "finite_evidence":str(evidence),"general_theorem_certified":False,
        "student_free_text_verified":False,"teacher_approved":False,
        "authoritative_student_index":False}

def check_all():
    out=[]
    n=8
    out.append(packet(NAMES[0],sum(k for k in range(1,n+1))==n*(n+1)//2,
        -1<0, "n=8, sum=36; n=-1 outside n>=0 induction domain"))
    u,v=(3,0),(0,4)
    out.append(packet(NAMES[1],sum(a*b for a,b in zip(u,v))==0 and
        sum((a+b)**2 for a,b in zip(u,v))==sum(a*a+b*b for a,b in zip(u,v)),
        (1*1)!=0,"orthogonal (3,0),(0,4): squared norm=25; equal directions not orthogonal"))
    n=4
    out.append(packet(NAMES[2],sum(k*k for k in range(1,n+1))==n*(n+1)*(2*n+1)//6,
        -1<0,"n=4, sum squares=30; negative index rejected"))
    u,v=(1,2),(2,-1)
    norm2=lambda v:sum(a*a for a in v)
    out.append(packet(NAMES[3],norm2(tuple(a+b for a,b in zip(u,v)))+
        norm2(tuple(a-b for a,b in zip(u,v)))==2*(norm2(u)+norm2(v)),
        len((1,2))!=len((1,2,3)),"u=(1,2),v=(2,-1), diagonal-square sum=20"))
    a,b=F(3),F(2); ca,sa=F(3,5),F(4,5); x,y=a*ca,b*sa
    out.append(packet(NAMES[4], ca**2+sa**2==1 and x*x/(a*a)+y*y/(b*b)==1,
        F(0)==0,"ellipse (a,b)=(3,2), (x,y)=(9/5,8/5); a=0 invalid"))
    a,b,c=F(2),F(-8),F(3); h=-b/(2*a); k=c-b*b/(4*a)
    out.append(packet(NAMES[5],(h,k)==(2,-5) and a*h*h+b*h+c==k,
        F(0)==0,"quadratic vertex=(2,-5), a=0 makes division undefined"))
    a=F(3); power=a**(-2)
    out.append(packet(NAMES[6],power==F(1,9) and power>0,
        F(1)==1,"a=3,k=-2,a^k=1/9; a=1 not invertible exponent"))
    sa,ca=F(3,5),F(4,5);sb,cb=F(5,13),F(12,13)
    sum_sin=sa*cb+ca*sb
    out.append(packet(NAMES[7],sa*sa+ca*ca==1 and sb*sb+cb*cb==1 and sum_sin==F(56,65),
        F(2)**2+F(0)**2!=1,"unit-circle rational trig components: sin(alpha+beta)=56/65"))
    basis=Matrix.eye(3); y=Matrix([2,-1,3]); coeff=basis.inv()*y
    bad=Matrix([[1,2,0],[0,0,0],[0,0,1]])
    out.append(packet(NAMES[8],basis.det()==1 and basis*coeff==y and list(coeff)==[2,-1,3],
        bad.det()==0,"identity basis unique coefficients=(2,-1,3), dependent basis det=0"))
    joint=[(0,0,F(1,2)),(2,2,F(1,2))]
    ex=sum((x*p for x,y,p in joint),F(0))
    ey=sum((y*p for x,y,p in joint),F(0))
    combined=sum(((x+y)*p for x,y,p in joint),F(0))
    out.append(packet(NAMES[9],ex==ey==1 and combined==ex+ey==2 and sum(p for _,_,p in joint)==1,
        sum((F(1,2),))!=1,"dependent Y=X: E(X+Y)=2, independence not required"))
    data=Matrix([[1,0],[0,1],[1,1]])
    out.append(packet(NAMES[10],data.rank()==2 and data.rows==3,
        len((1,2))!=len((1,2,3)),"3 vectors in R2 span rank 2, not rank 3"))
    A=Matrix([[2,1],[1,1]]); inv=Matrix([[1,-1],[-1,2]])
    singular=Matrix([[1,2],[2,4]])
    out.append(packet(NAMES[11],A.det()==1 and A*inv==Matrix.eye(2) and inv*A==Matrix.eye(2),
        singular.det()==0,"A det 1 and inverse exact; singular det=0"))
    assert len(out)==len(NAMES)==12
    return out

