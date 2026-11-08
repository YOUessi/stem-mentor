"""Bounded exact witnesses: never certifies general theorems or student free-text reasoning."""
from __future__ import annotations
from fractions import Fraction

FIELDS = {
    "finite_propositional": ("include_p","include_imp"),
    "response_mean_gap": ("v1","v2","v3","v4","responded"),
    "conditional_group_weight": ("n_a","mean_a","n_b","mean_b"),
    "equal_temperament_octaves": ("f0","steps"),
    "reflection_translation_order": ("x","y","dx","dy"),
    "pinhole_project": ("f","x","y","z"),
    "round_robin_schedule": ("teams",),
}
VALID = {
    "finite_propositional":{"include_p":1,"include_imp":1},
    "response_mean_gap":{"v1":10,"v2":20,"v3":30,"v4":40,"responded":2},
    "conditional_group_weight":{"n_a":2,"mean_a":10,"n_b":2,"mean_b":30},
    "equal_temperament_octaves":{"f0":440,"steps":24},
    "reflection_translation_order":{"x":2,"y":3,"dx":1,"dy":0},
    "pinhole_project":{"f":3,"x":2,"y":4,"z":2},
    "round_robin_schedule":{"teams":5},
}
INVALID = {
    "finite_propositional":{"include_p":2,"include_imp":1},
    "response_mean_gap":{"v1":10,"v2":20,"v3":30,"v4":40,"responded":0},
    "conditional_group_weight":{"n_a":0,"mean_a":10,"n_b":2,"mean_b":30},
    "equal_temperament_octaves":{"f0":440,"steps":7}, # only full octaves are exact rational in bounded operator
    "reflection_translation_order":{"x":2,"y":3,"dx":101,"dy":0},
    "pinhole_project":{"f":3,"x":2,"y":4,"z":0},
    "round_robin_schedule":{"teams":1},
}
def _schedule(n:int):
    # A fixed player and n-1 rotating players produce a 1-factorization of K_n for even n.
    count = n if n%2==0 else n+1
    dummy = n if count>n else None
    ring = list(range(count))
    rounds = []
    for _ in range(count-1):
        pairs = []
        for j in range(count//2):
            a,b = ring[j],ring[-1-j]
            if a!=dummy and b!=dummy:
                pairs.append(tuple(sorted((a,b))))
        rounds.append(pairs)
        ring = [ring[0],ring[-1],*ring[1:-1]]
    return rounds

def witness(op:str, params:dict):
    unsupported={"status":"UNSUPPORTED","teacher_approved":"false","student_freeform_step_verified":"false",
                 "general_theorem_certified":"false"}
    if op not in FIELDS:
        return unsupported
    bad=dict(unsupported,status="CONDITIONS_NOT_ESTABLISHED")
    if not isinstance(params,dict) or set(params)!=set(FIELDS[op]):
        return bad
    limit = 1000 if op=="equal_temperament_octaves" else 100
    if any(type(v) is not int or abs(v)>limit for v in params.values()):
        return bad
    p=params
    try:
        if op=="finite_propositional":
            if any(p[key] not in (0,1) for key in FIELDS[op]):return bad
            models=[(pv,qv) for pv in (0,1) for qv in (0,1)
                    if (not p["include_p"] or pv==1) and
                    (not p["include_imp"] or pv==0 or qv==1)]
            answer=f"{len(models)}|{int(bool(models) and all(q for _,q in models))}"
        elif op=="response_mean_gap":
            k=p["responded"]
            if not (1<=k<=4):return bad
            values=[p["v1"],p["v2"],p["v3"],p["v4"]]
            gap=Fraction(sum(values[:k]),k)-Fraction(sum(values),4)
            answer=str(gap)
        elif op=="conditional_group_weight":
            if p["n_a"]<=0 or p["n_b"]<=0:return bad
            # Descriptive weighted arithmetic, NOT an identification of missingness mechanisms.
            answer=str(Fraction(p["n_a"]*p["mean_a"]+p["n_b"]*p["mean_b"],
                                p["n_a"]+p["n_b"]))
        elif op=="equal_temperament_octaves":
            if p["f0"]<=0 or p["steps"]%12!=0 or abs(p["steps"])>36:return bad
            octaves=p["steps"]//12
            answer=str(Fraction(p["f0"])*(Fraction(2)**octaves))
        elif op=="reflection_translation_order":
            a=(p["dx"]-p["x"],p["dy"]+p["y"])
            b=(-p["dx"]-p["x"],p["dy"]+p["y"])
            answer=f"{a[0]},{a[1]}|{b[0]},{b[1]}"
        elif op=="pinhole_project":
            if p["f"]<=0 or p["z"]<=0:return bad
            answer=f"{Fraction(p['f']*p['x'],p['z'])},{Fraction(p['f']*p['y'],p['z'])}"
        elif op=="round_robin_schedule":
            n=p["teams"]
            if not (2<=n<=30):return bad
            rounds=_schedule(n)
            edges=[edge for game_round in rounds for edge in game_round]
            if len(edges)!=n*(n-1)//2 or len(edges)!=len(set(edges)):
                return bad
            if any(len({team for pair in r for team in pair})!=2*len(r) for r in rounds):
                return bad
            if len(rounds)!=(n-1 if n%2==0 else n):
                return bad
            answer=f"{len(rounds)}|{len(edges)}"
        return dict(unsupported,status="FINITE_EXACT_CASE_ONLY",exact_value=answer,
                    inference_certified="false",citation_id="kb-batch39-"+op)
    except (ValueError,ZeroDivisionError,OverflowError):
        return bad
