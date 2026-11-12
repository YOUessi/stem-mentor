"""Finite *independent* exact witnesses for Batch104; not universal proof."""
from __future__ import annotations
from fractions import Fraction as F

def witness(index: int) -> dict:
    if type(index) is not int or index not in range(12):
        raise ValueError("unknown Batch104 witness")
    if index == 0:
        U = {1,2,3,4}; A={1,2}; B={2,3}
        yes = (U-(A|B) == (U-A)&(U-B) == {4}
               and U-(A&B)==(U-A)|(U-B)=={1,3,4})
        no = (U-(A|B)) != ((U-A)|(U-B))
    elif index == 1:
        yes = all(n%2==0 for n in range(-40,41) if n%4==0)
        no = 2%2==0 and 2%4!=0
    elif index == 2:
        a,b,c=-2,1,-3
        yes = a<b and a*c>b*c
        no = (a*c<b*c) is False and a*0==b*0
    elif index == 3:
        def q(x):return x*x-4*x+3
        yes = q(0)>0 and q(2)<0 and q(4)>0 and q(1)==q(3)==0
        no = (-3*3+4)<0 and (-0*0+4)>0 and (0*0+4)>0
    elif index == 4:
        mapping={1:2,2:2,3:4}
        yes = len(mapping)==3 and len(set(mapping.values()))==2
        invalid_pairs=((1,2),(1,3),(2,4))
        images_of_one={output for inp,output in invalid_pairs if inp==1}
        no = len(images_of_one)==2 and images_of_one=={2,3}
    elif index == 5:
        f=lambda x: x*x if x<=1 else 2*x-1
        g=lambda x: x if x<0 else x+2
        yes = f(F(1))==1 and f(F(999,1000))==F(999,1000)**2 and f(F(1001,1000))==F(1002,1000)
        no = g(F(-1,1000))==F(-1,1000) and g(F(1,1000))==F(2001,1000)
    elif index == 6:
        yes = 2**3==8 and 3**2==9
        def real_log_domain(base,argument):
            return base>0 and base!=1 and argument>0
        no = not real_log_domain(1,8) and not real_log_domain(-2,4) and not real_log_domain(2,0)
    elif index == 7:
        s=F(8,1)*F(1,2)/5
        yes = s==F(4,5) and s>F(1,2) and s<1
        no = F(9,1)*F(1,2)/4>1
    elif index == 8:
        u=(1,2);v=(2,-1);z=(0,0)
        dot=lambda a,b:sum(x*y for x,y in zip(a,b))
        yes = dot(u,v)==0 and sum(x*x for x in u)>0 and sum(y*y for y in v)>0
        no = dot(z,v)==0 and sum(t*t for t in z)==0
    elif index == 9:
        omega=set(range(1,7)); A={4,5,6};B={2,4,6}
        yes = F(len(A&B),len(B))==F(2,3)
        event_a={1}; event_b={2}
        no=(len(event_a&event_b)==0 and
            F(len(event_a),len(omega))*F(len(event_b),len(omega))==F(1,36)
            and F(len(event_a&event_b),len(omega))!=F(1,36))
    elif index == 10:
        outcomes=((0,1),(1,0)); prob=(F(1,2),F(1,2))
        expectation=lambda xs:sum((p*v for p,v in zip(prob,xs)),F(0))
        yes = expectation([a+b for a,b in outcomes])==1 and expectation([a for a,b in outcomes])+expectation([b for a,b in outcomes])==1
        no = expectation([a*b for a,b in outcomes])==0 and expectation([a for a,b in outcomes])*expectation([b for a,b in outcomes])==F(1,4)
    else:
        a=2;q=3;n=4
        yes=sum(a*q**k for k in range(n))==a*(1-q**n)//(1-q)==80
        no = sum(2*1**k for k in range(4))==8 and (1-1)==0
    if not yes or not no:
        raise AssertionError(f"Batch104 exact counterexample failed at {index}")
    return {"index":index,"exact_positive":True,"invalid_case_rejected":True,
            "universally_certified":False,"student_response_verified":False,
            "teacher_approved":False,"scope":"FINITE_EXACT_WITNESS_ONLY"}
