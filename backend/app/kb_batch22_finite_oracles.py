"""Editorial exact-instance oracles for selected Batch22 formulas.

Never claim a whole theorem is proved; never evaluate arbitrary expressions.
These finite rational checks are not student free-text verification, an LLM
judge, or a permission to publish unreviewed lessons.
"""
from fractions import Fraction
from math import gcd

SUPPORTED=('planar_isometry','triangular_density','chi_square_variance_stat',
           'pearson_gof','keynes_equilibrium','pinhole_projection','normal_mean_moments')

def _q(value):
    if isinstance(value,bool) or not isinstance(value,(str,int,Fraction)):
        raise ValueError('Expected bounded integer/rational literal, not arbitrary expression')
    if isinstance(value,str):
        if not 1<=len(value)<=32 or any(c not in '0123456789-+/' for c in value):
            raise ValueError('Only rational literals are supported')
    q=Fraction(value)
    if abs(q.numerator)>10**9 or q.denominator>10**9:
        raise ValueError('Rational literal exceeds finite verifier bounds')
    return q

def _result(status, *, checks=(), witness=None, reason=''):
    return {'status':status,'checked_conditions':list(checks),'witness':witness,
            'reason':reason,'scope':'EXACT_FINITE_INSTANCE_ONLY_NOT_PROOF_CERTIFICATION',
            'student_step_verified':False,'teacher_approved':False}

def evaluate(operation, values):
    if operation not in SUPPORTED:
        return _result('UNSUPPORTED',reason='No oracle for this claim')
    if not isinstance(values,dict):
        return _result('CONDITIONS_NOT_ESTABLISHED',reason='Input must be a structured object')
    try:
        if operation=='planar_isometry':
            x,y=_q(values['x']),_q(values['y'])
            q=values.get('Q')
            if not isinstance(q,list) or len(q)!=2 or any(not isinstance(row,list) or len(row)!=2 for row in q):
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='Q must be a 2×2 matrix')
            a,b=q[0];c,d=q[1]
            a,b,c,d=map(_q,(a,b,c,d))
            if (a*a+c*c,b*b+d*d,a*b+c*d)!=(1,1,0):
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='QᵀQ≠I, cannot assert isometry')
            lhs=(a*x+b*y)**2+(c*x+d*y)**2
            return _result('VERIFIED_FINITE_INSTANCE' if lhs==x*x+y*y else 'FAILED_FINITE_INSTANCE',
                    checks=('real rational 2×2 Q','QᵀQ=I','exact point squared norm'),
                    witness={'squared_norm':str(lhs),'original':str(x*x+y*y)})
        if operation=='triangular_density':
            t=_q(values['t'])
            F=Fraction(0) if t<=0 else Fraction(1) if t>=1 else t*t
            return _result('VERIFIED_FINITE_INSTANCE',
                checks=('f(x)=2x on [0,1] else 0','t is rational','piecewise integral'),
                witness={'F(t)':str(F),'E[X]':'2/3','Var[X]':'1/18'})
        if operation=='chi_square_variance_stat':
            n=values['n']
            if isinstance(n,bool) or not isinstance(n,int) or n<2 or n>100000:
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='n≥2 integer required')
            s2,sigma2=_q(values['sample_variance']),_q(values['null_variance'])
            if s2<0 or sigma2<=0:
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='S²≥0 and σ₀²>0 required')
            stat=(n-1)*s2/sigma2
            return _result('VERIFIED_FINITE_INSTANCE',
                checks=('n≥2','S²≥0','σ₀²>0','normal/iid assumptions NOT checked'),
                witness={'T':str(stat),'df':n-1},
                reason='Only the statistic arithmetic is verified, not normality, χ² law or rejection')
        if operation=='pearson_gof':
            obs=values.get('observed');p=values.get('probabilities')
            if not(isinstance(obs,list) and isinstance(p,list) and len(obs)==len(p) and 2<=len(obs)<=128):
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='Aligned categorical vectors required')
            if any(isinstance(v,bool) or not isinstance(v,int) or v<0 for v in obs):
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='Counts must be nonnegative integers')
            ps=list(map(_q,p))
            if sum(ps)!=1 or any(v<=0 for v in ps) or sum(obs)<1:
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='Probabilities must be >0, sum 1 and n>0')
            n=sum(obs);e=[n*v for v in ps];stat=sum(((o-v)**2/v for o,v in zip(obs,e)),Fraction(0))
            return _result('VERIFIED_FINITE_INSTANCE',
                checks=('positive expected counts','exhaustive probabilities sum 1','exact Pearson statistic','large sample approximation NOT checked'),
                witness={'T':str(stat),'E':[str(v) for v in e],'min_expected_at_least_5':min(e)>=5},
                reason='Do not infer significance or a justified χ² approximation from this computation')
        if operation=='keynes_equilibrium':
            a,b,I=map(_q,(values['a'],values['b'],values['I']))
            if not Fraction(0)<=b<Fraction(1):
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='0≤b<1 required for claimed stability')
            Y=(a+I)/(1-b)
            if Y!=a+b*Y+I:
                return _result('FAILED_FINITE_INSTANCE',reason='Failed exact equilibrium substitution')
            return _result('VERIFIED_FINITE_INSTANCE',
                checks=('0≤b<1','exact affine fixed point','not empirical validation'),
                witness={'Y*':str(Y),'multiplier':str(1/(1-b))})
        if operation=='pinhole_projection':
            X,Y,Z,f=map(_q,(values['X'],values['Y'],values['Z'],values['f']))
            if Z<=0 or f<=0:
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='Visible model requires f>0 and Z>0')
            return _result('VERIFIED_FINITE_INSTANCE',
                checks=('Z>0','f>0','ideal pinhole camera only'),
                witness={'x':str(f*X/Z),'y':str(f*Y/Z)})
        if operation=='normal_mean_moments':
            n=values['n']
            if isinstance(n,bool) or not isinstance(n,int) or n<1 or n>100000:
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='n positive integer required')
            mu,sigma=map(_q,(values['mu'],values['sigma']))
            if sigma<=0:
                return _result('CONDITIONS_NOT_ESTABLISHED',reason='σ>0 required')
            return _result('VERIFIED_FINITE_INSTANCE',
                checks=('n positive integer','σ>0','normal and iid assumptions NOT checked'),
                witness={'E[mean]':str(mu),'Var[mean]':str(sigma*sigma/n)},
                reason='Algebraic moments only; exact sampling distribution is an unverified theorem')
    except (KeyError,ValueError,TypeError,ZeroDivisionError,OverflowError):
        return _result('CONDITIONS_NOT_ESTABLISHED',reason='Missing or unsafe finite rational conditions')
    return _result('UNSUPPORTED')
