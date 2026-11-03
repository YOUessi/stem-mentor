"""Independent *limited* mathematical checks for the ten contested lesson versions.

Never use these tests to adjudicate a disputed version, certify a full proof,
mark teacher_review APPROVED, or verify an arbitrary student's steps.
"""
from math import comb
from sympy import Matrix, Rational, cos, pi, simplify, sqrt, sin

CONFLICT_IDS = (
    "math.hs.function.composition-domain",
    "math.hs.function.parity",
    "math.hs.function.piecewise",
    "math.hs.function.zero-ivt",
    "math.hs.geometry.point-line-distance",
    "math.hs.probability.binomial-distribution",
    "math.hs.probability.hypergeometric",
    "math.hs.statistics.correlation-regression",
    "math.hs.triangle.area-sine",
    "math.hs.vector.linear-operations",
)

def conflict_subclaim_checks():
    """Finite exact-arithmetic and guard-condition examples; NEVER whole proofs."""
    checks = {}
    def add(key, guard, observations, excluded, note):
        if key not in CONFLICT_IDS:
            raise ValueError("Unknown conflict")
        checks[key] = {
            "required_guard": guard,
            "exact_observations": [{"claim": n, "passed": bool(p)} for n, p in observations],
            "counterexample_to_unguarded_claim": excluded,
            "scope": "FINITE_CASE_OR_LOCAL_SYMBOLIC_TEST_NOT_WHOLE_PROOF",
            "teacher_review": "PENDING",
            "full_natural_language_proof_certified": False,
            "source_versions_adjudicated": False,
            "next_reviewer_task": note,
        }

    # D(f o g) = {x in Dg : g(x) in Df}; the algebraic cancellation
    # (x^2-1)/(x-1) -> x+1 does NOT restore x=1.
    add(CONFLICT_IDS[0], "x in D_g AND g(x) in D_f",
        [("log(x-1) at x=2 is defined", 2-1 > 0),
         ("log(x-1) at x=1 is not defined", not (1-1 > 0)),
         ("cancelled rational at excluded pole x=1 stays excluded",
          not (1-1 != 0))],
        "Using intersection D_f intersect D_g or simplifying away forbidden poles.",
        "Reconcile candidate and active full-domain statements, including log and removable holes.")

    D = (-2, -1, 0, 1, 2)
    add(CONFLICT_IDS[1], "symmetric domain D=-D before f(-x)=+/-f(x)",
        [("finite symmetric domain", set(D) == {-x for x in D}),
         ("square even on symmetric domain", all((-x)**2==x**2 for x in D)),
         ("zero function both even and odd", all(0 == -0 for x in D)),
         ("positive half-line is not origin symmetric", not (-1 > 0))],
        "Formula x² restricted to (0,+infinity) is not an even function in the standard definition.",
        "Keep the zero-function both-even-and-odd boundary and verify domain conditions.")

    add(CONFLICT_IDS[2], "each input has exactly one output; branch domains cover stated D",
        [("overlapping boundary with contradictory outputs rejected",
          len({0, 1}) != 1),
         ("partition x<0 and x>=0 covers integers once",
          all((int(x<0)+int(x>=0))==1 for x in range(-20,21))),
         ("piecewise x/x has no forced discontinuity at 0",
          all((x if x<0 else x)==x for x in range(-20,21)))],
        "Two clauses at x=0 assigning different values do not define a function.",
        "Check branch cover, disjointness or consistency, and continuity separately.")

    add(CONFLICT_IDS[3], "closed-interval continuity AND strict opposite signs",
        [("same-sign endpoints can hide two roots",
          (Rational(-2)**2-1)>0 and (Rational(2)**2-1)>0 and
          (Rational(-1)**2-1)==0 and (Rational(1)**2-1)==0),
         ("discontinuous sign-flipping step has no zero",
          all((-1 if x<0 else 1)!=0 for x in range(-10,11))),
         ("continuous x changes sign and has a zero",
          (-1)<0 and 1>0 and 0==0)],
        "Sign change without continuity gives no IVT guarantee; same signs do not rule out roots.",
        "Review source wording: existence only, not uniqueness or necessity.")

    add(CONFLICT_IDS[4], "A²+B²>0 for line Ax+By+C=0",
        [("3x+4y-5 origin distance = 1",
          simplify(abs(-5)/sqrt(3**2+4**2)-1)==0),
         ("zero normal is invalid", 0**2+0**2==0),
         ("normal scaling invariance",
          simplify(abs(-10)/sqrt(6**2+8**2)-1)==0)],
        "A=B=0 is not a line even when C=0.",
        "Check nonzero normal and every use of square root denominator.")

    p = Rational(1,2)
    add(CONFLICT_IDS[5], "n>=0 integer, 0<=p<=1, independent identically distributed Bernoulli trials",
        [("two independent fair trials exactly one success",
          comb(2,1)*p*(1-p)==Rational(1,2)),
         ("same outcome repeated twice has P(exactly one)=0", 0!=Rational(1,2)),
         ("PMF sums to 1 including boundaries",
          all(sum(comb(3,k)*q**k*(1-q)**(3-k) for k in range(4))==1
              for q in (Rational(0),Rational(1,4),Rational(1))))],
        "Perfectly correlated Bernoulli trials are not Binomial(2,1/2).",
        "Verify independence and constant p; do not silently reuse the binomial PMF.")

    hyper = Rational(comb(2,1)*comb(2,1),comb(4,2))
    add(CONFLICT_IDS[6], "0<=K<=N, 0<=n<=N, integer parameters, sampling without replacement",
        [("N4 K2 n2 k1 gives 2/3", hyper==Rational(2,3)),
         ("binomial-with-replacement would give 1/2", hyper != Rational(1,2)),
         ("hypergeometric PMF normalizes for small finite populations",
          all(sum(Rational(comb(K,k)*comb(N-K,n-k),comb(N,n))
                  for k in range(max(0,n-(N-K)), min(K,n)+1))==1
              for N in range(1,7) for K in range(N+1) for n in range(N+1)))],
        "Replacing without-replacement draws by independent Bernoulli draws changes the law.",
        "Check feasibility range, replacement model, and endpoint conventions.")

    xs = (-1,0,1)
    ys = tuple(x*x for x in xs)
    sx = sum(xs); sy=sum(ys)
    cross=sum((x-Rational(sx,3))*(y-Rational(sy,3)) for x,y in zip(xs,ys))
    add(CONFLICT_IDS[7], "sample variance in both variables must be positive for Pearson r",
        [("nonlinear dependence can yield zero covariance", cross==0),
         ("sample y values not constant", len(set(ys))>1),
         ("sample x values not constant", len(set(xs))>1)],
        "r=0 does not imply independence or causation (here Y=X²).",
        "Distinguish correlation from independence and causal effect.")

    area = Rational(1,2)*2*3*sin(2*pi/3)
    add(CONFLICT_IDS[8], "side lengths nonnegative, included angle 0<=theta<=pi",
        [("a=2 b=3 theta=120 degrees gives area 3sqrt3/2",
          simplify(area-Rational(3,2)*sqrt(3))==0),
         ("collinear included angle area zero", sin(pi)==0 and sin(0)==0),
         ("area nonnegative for theta 0..pi",
          all(sin(pi*k/12)>=0 for k in range(13)))],
        "Angle not between the two named sides cannot be substituted for included angle.",
        "Check included angle and triangle degeneracy boundary.")

    u, v = Matrix([2,-1,3]), Matrix([-4,5,0])
    z = Matrix([0,0,0])
    add(CONFLICT_IDS[9], "coordinate vector addition/scalar multiplication within same vector space",
        [("distributive law for exact integers", 3*(u+v)==3*u+3*v),
         ("zero vector not a direction",
          sum(a*a for a in z)==0),
         ("nonzero norm supports normalization",
          sum(a*a for a in u)>0),
         ("zero additive identity", u+z==u)],
        "Zero vector cannot be normalized and need not determine a direction.",
        "Review kind mismatch (theorem versus concept) before resolving duplicate IDs.")

    if set(checks) != set(CONFLICT_IDS):
        raise ValueError("All ten contested IDs must have independent limited checks")
    if any(not all(z["passed"] for z in v["exact_observations"]) for v in checks.values()):
        raise AssertionError("At least one exact guard or counterexample check failed")
    return checks
