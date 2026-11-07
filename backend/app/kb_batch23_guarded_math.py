"""Restricted exact arithmetic witnesses for Batch23's teacher-side drafts.

This is NOT a proof checker, teacher-review engine, or free-form expression parser.
It never asserts normality, causal validity, curriculum authority or lesson release.
"""
from fractions import Fraction as Q
from math import comb
SUPPORTED=('squared_equation_candidate','telescoping_finite_sum','court_clearance_area',
           'binomial_point_mass','parabola_line_discriminant','complex_divide',
           'two_event_union','quadratic_monotonic_pair')

def _q(x):
    if isinstance(x,bool) or not isinstance(x,(str,int,Q)):
        raise ValueError('Only rational literals')
    if isinstance(x,str) and (not 1<=len(x)<=30 or any(c not in '+-0123456789/' for c in x)):
        raise ValueError('Unsafe expression')
    r=Q(x)
    if abs(r.numerator)>10**7 or r.denominator>10**7:
        raise ValueError('Outside bounded exact arithmetic')
    return r

def _int(x,lo,hi):
    if isinstance(x,bool) or not isinstance(x,int) or not lo<=x<=hi:
        raise ValueError('Bounded integer required')
    return x

def _result(status, checks=(), witness=None, reason=''):
    return dict(status=status,checked_conditions=list(checks),witness=witness,reason=reason,
                scope='FINITE_RATIONAL_WITNESS_ONLY_NOT_GENERAL_MATHEMATICAL_PROOF',
                complete_theorem_certified=False,teacher_approved=False,
                student_step_verified=False,student_publishable=False)

def evaluate(op, values):
    if op not in SUPPORTED:
        return _result('UNSUPPORTED',reason='No trusted finite operation for this claim')
    if not isinstance(values,dict):
        return _result('CONDITIONS_NOT_ESTABLISHED',reason='Structured fields required')
    try:
        if op=='squared_equation_candidate':
            x=_q(values['x'])
            if x+2<0:
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='Radicand must be nonnegative')
            squared=(x*x==x+2)
            original=(squared and x>=0)
            return _result('VERIFIED_FINITE_INSTANCE' if original else 'FAILED_FINITE_INSTANCE',
                ('x+2≥0','√t is nonnegative','exact squared candidate'),
                {'squared_equation_holds':squared,'original_equation_holds':original})
        if op=='telescoping_finite_sum':
            n=_int(values['n'],1,1000)
            s=sum((Q(1,k*(k+1)) for k in range(1,n+1)),Q(0))
            v=Q(n,n+1)
            return _result('VERIFIED_FINITE_INSTANCE' if s==v else 'FAILED_FINITE_INSTANCE',
                ('n positive integer','all k(k+1)≠0','rational summation'),
                {'sum':str(s),'formula':str(v)})
        if op=='court_clearance_area':
            w,l,m=(_q(values[k]) for k in ('width','length','margin'))
            if w<=0 or l<=0 or m<0:
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='w,l>0 and m≥0')
            area=(w+2*m)*(l+2*m)
            return _result('VERIFIED_FINITE_INSTANCE',('rectangular enclosure only','w,l>0,m≥0'),
                {'area':str(area),'added_clearance_area':str(area-w*l)},
                reason='No official sport regulations or safety compliance verified')
        if op=='binomial_point_mass':
            n=_int(values['n'],1,100)
            k=_int(values['k'],0,n)
            p=_q(values['p'])
            if not 0<=p<=1:
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='p∈[0,1]')
            point=Q(comb(n,k))*p**k*(1-p)**(n-k)
            return _result('VERIFIED_FINITE_INSTANCE',
                ('n positive integer','0≤k≤n','0≤p≤1','iid Bernoulli assumption NOT verified'),
                {'probability':str(point),'expectation':str(n*p),'variance':str(n*p*(1-p))})
        if op=='parabola_line_discriminant':
            m,b=_q(values['m']),_q(values['b'])
            delta=m*m+4*b
            count=2 if delta>0 else 1 if delta==0 else 0
            return _result('VERIFIED_FINITE_INSTANCE',
                ('finite line slope','parabola y=x²','quadratic leading coefficient 1'),
                {'discriminant':str(delta),'distinct_real_intersections':count},
                reason='Vertical line x=c cannot be represented as y=mx+b')
        if op=='complex_divide':
            a,b,c,d=(_q(values[k]) for k in ('a','b','c','d'))
            den=c*c+d*d
            if den==0:
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='Nonzero complex divisor required')
            return _result('VERIFIED_FINITE_INSTANCE',
                ('real rational components','c²+d²>0'),
                {'real':str((a*c+b*d)/den),'imag':str((b*c-a*d)/den)})
        if op=='two_event_union':
            pa,pb,pab=(_q(values[k]) for k in ('pa','pb','pab'))
            if not (0<=pa<=1 and 0<=pb<=1 and max(Q(0),pa+pb-1)<=pab<=min(pa,pb)):
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='Not a valid two-event probability triple')
            return _result('VERIFIED_FINITE_INSTANCE',('probability consistency bounds','exact inclusion-exclusion'),
                {'union_probability':str(pa+pb-pab)})
        if op=='quadratic_monotonic_pair':
            x,y=_q(values['x']),_q(values['y'])
            if x>=y or not (0<=x or y<=0):
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='Need x<y within one signed half-line')
            direction='strict_increase' if x>=0 else 'strict_decrease'
            valid=(x*x<y*y) if x>=0 else (x*x>y*y)
            return _result('VERIFIED_FINITE_INSTANCE' if valid else 'FAILED_FINITE_INSTANCE',
                ('two points from same half-line','x<y','exact squares'),
                {'direction':direction,'fx':str(x*x),'fy':str(y*y)})
    except (KeyError,ValueError,TypeError,ZeroDivisionError,OverflowError):
        return _result('CONDITIONS_NOT_ESTABLISHED',reason='Missing or unsafe finite rational conditions')
    return _result('UNSUPPORTED')
