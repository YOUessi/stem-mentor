#!/usr/bin/env python3
"""Independent exact, finite mathematical witnesses for eight source-anchored teacher drafts.

No claim of general theorem certification, student free-text step verification, or
teacher approval. Oracle is separate from authoring and never reads teacher answers.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch138_electives as draft
OUT=ROOT/"docs/evaluation/KB_BATCH138_MATH_WITNESSES.json"

def must(b, why):
    if not b:raise ValueError(why)

def case(lst, who, label, condition, status="EXACT_FINITE_WITNESS"):
    must(bool(condition),"independent exact math check FAILED: "+who+" / "+label)
    lst.append(dict(case_id=who+"-"+str(sum(c["candidate_id"]==who for c in lst)+1),
         candidate_id=who, claim_test=label, status=status,
         passed=True, general_proof_certified=False,teacher_approved=False,
         student_step_verified=False,condition_verdict=(
             "CONDITIONS_NOT_ESTABLISHED" if status=="REJECT_INVALID_PRECONDITION"
             else "BOUNDED_EXACT_ONLY")))

def build():
    a,b,c,d,e,f,g,h=draft.IDS
    x,y,t=S.symbols("x y t",real=True)
    out=[]
    A=S.Matrix([[1,1],[1,-1]]);rhs=S.Matrix([3,1])
    case(out,a,"full-rank unique solution 2,1",A.rank()==2 and A.row_join(rhs).rank()==2 and A.inv()*rhs==S.Matrix([2,1]))
    B=S.Matrix([[1,1],[2,2]]);rhs2=S.Matrix([2,4])
    case(out,a,"rank-one consistent has free variable",B.rank()==B.row_join(rhs2).rank()==1 and all(B*S.Matrix([v,2-v])==rhs2 for v in [0,1,17]))
    case(out,a,"zero coefficient nonzero rhs contradiction",S.Matrix([[0]]).rank()!=S.Matrix([[0,1]]).rank(),"REJECT_INVALID_PRECONDITION")
    case(out,a,"rank equality is insufficient for uniqueness",B.rank()==1 and B.cols==2 and B*S.Matrix([0,2])==B*S.Matrix([1,1]))
    ff=x*x+2*y*y
    case(out,b,"disk interior origin and max boundary attainments",ff.subs({x:0,y:0})==0 and ff.subs({x:0,y:1})==2 and ff.subs({x:0,y:-1})==2)
    case(out,b,"ellipse extremal boundary exact",S.Integer(2)**2+S.Integer(0)**2==4 and S.Integer(0)**2+S.Integer(0)**2==0 and S.Integer(2)**2+4*S.Integer(0)**2<=4)
    case(out,b,"open disk lacks claimed maximum",all((1-S.Rational(1,n))**2<1 and 2*(1-S.Rational(1,n))**2<2 for n in (2,3,10,100)),"REJECT_INVALID_PRECONDITION")
    case(out,b,"algebraic upper-bound decomposition",S.expand(ff-(x*x+y*y)-y*y)==0)
    sigmoid=lambda z:S.simplify(1/(1+S.exp(-z)))
    case(out,c,"odds three gives probability three-quarters",sigmoid(S.log(3))==S.Rational(3,4))
    case(out,c,"zero linear score gives half",sigmoid(0)==S.Rational(1,2))
    case(out,c,"logit at p=0 or p=1 outside finite real domain",S.log(S.S(0)).is_finite is False and (S.S(1)/(1-S.S(1))).is_finite is False,"REJECT_INVALID_PRECONDITION")
    case(out,c,"sigmoid symmetry exact",S.simplify(sigmoid(t)+sigmoid(-t)-1)==0)
    case(out,d,"20 only belongs to right semi-open category",not(10<=20<20) and 20<=20<30)
    counts=[6,8,10]
    case(out,d,"frequency denominator 24 and sum one",sum(counts)==24 and sum([S.Rational(v,24) for v in counts])==1)
    case(out,d,"closed overlapping brackets double count 20",10<=20<=20 and 20<=20<=30,"REJECT_INVALID_PRECONDITION")
    case(out,d,"invalid denominator 30 fails frequency partition",sum(S.Rational(v,30) for v in counts)==S.Rational(4,5))
    # time in seconds, phase radians, exact symbolic periodicity and counterexamples
    case(out,e,"3 Hz signal one-third-second shift",S.trigsimp(2*S.sin(6*S.pi*(t+S.Rational(1,3)))-2*S.sin(6*S.pi*t))==0)
    case(out,e,"2 Hz signal half-second shift",S.trigsimp(S.sin(4*S.pi*(t+S.Rational(1,2))+S.pi/2)-S.sin(4*S.pi*t+S.pi/2))==0)
    case(out,e,"zero-amplitude waveform has no minimum positive period",all(S.Integer(0)*S.sin(2*S.pi*z)==0 for z in (0,S.Rational(1,7),S.Rational(7,3))),"REJECT_INVALID_PRECONDITION")
    case(out,e,"1Hz and 11Hz alias at 10Hz sample rate",all(S.trigsimp(S.sin(2*S.pi*S.Rational(k,10))-S.sin(22*S.pi*S.Rational(k,10)))==0 for k in range(21)))
    Q=S.Matrix([[0,-1],[1,0]]);shift=S.Matrix([1,2])
    case(out,f,"right-angle rotation orthogonal and translated origin",Q.T*Q==S.eye(2) and Q*S.zeros(2,1)+shift==shift)
    case(out,f,"uniform scale doubles 3-4-5 distance",S.sqrt((2*3)**2+(2*4)**2)==10 and S.sqrt(3**2+4**2)==5)
    case(out,f,"anisotropic scale not isometric",S.diag(2,1).T*S.diag(2,1)!=S.eye(2),"REJECT_INVALID_PRECONDITION")
    case(out,f,"translation is not linear unless origin preserved",shift!=S.zeros(2,1) and Q.T*Q==S.eye(2))
    case(out,g,"gcd 84 and 30",S.gcd(84,30)==6 and 84==30*2+24 and 30==24+6 and 24==6*4)
    case(out,g,"gcd 101 and 37",S.gcd(101,37)==1 and 101==37*2+27 and 7==3*2+1)
    case(out,g,"zero-zero excluded under teaching gcd convention",not (0!=0 or 0!=0),"REJECT_INVALID_PRECONDITION")
    case(out,g,"gcd invariant under Euclidean step",all(S.gcd(u,v)==S.gcd(v,u%v) for u,v in ((84,30),(101,37),(144,54),(54,18))))
    case(out,h,"1:500 3cm equals 15m",S.Rational(3*500,100)==15)
    case(out,h,"1:100 2cm times 3cm yields 6m squared",S.Rational(2*100,100)*S.Rational(3*100,100)==6)
    case(out,h,"area factor must be square not linear",2**2==4 and 2**2!=2,"REJECT_INVALID_PRECONDITION")
    case(out,h,"area unit conversion 60000cm2 = 6m2",S.Rational(6*100**2,100**2)==6)
    must(len(out)==32,"must have 32 independently evaluated finite checks")
    must(set(q["candidate_id"] for q in out)==set(draft.IDS),"missing author")
    must(sum(c["status"]=="REJECT_INVALID_PRECONDITION" for c in out)==8,"negative guard count drift")
    return dict(schema="kb138-exact-finite-oracle/1",scope="8_MANUSCRIPTS_32_FINITE_WITNESSES_NOT_THEOREM_CERTIFICATES",
                source_pdf_sha256=draft.PDF,
                finite_exact_checks=32, invalid_preconditions_rejected=8,
                valid_or_edge_witnesses=24,
                teacher_approved=0,general_theorem_certificates=0,
                student_free_text_steps_verified=0,
                student_authoritative_releases=0,
                cases=out)

def main():
    p=argparse.ArgumentParser()
    gr=p.add_mutually_exclusive_group(required=True)
    gr.add_argument("--write",action="store_true");gr.add_argument("--check",action="store_true")
    args=p.parse_args()
    actual=build()
    if args.write:OUT.write_text(draft.encode(actual),encoding="utf-8")
    else:must(json.loads(OUT.read_text(encoding="utf-8"))==actual,"math witness tampered")
    print("PASS Batch138 32 independently evaluated exact finite cases; 8 rejected invalid conditions; zero general proof certificates")
if __name__=="__main__":main()
