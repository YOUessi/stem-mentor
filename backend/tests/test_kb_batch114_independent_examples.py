"""Independent exact probes for Batch114's sixteen *teacher-side* worked examples.

These are bounded instances only; they neither certify a general theorem nor a teacher review.
"""
import json
from pathlib import Path

import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
R = sp.Rational
x = sp.Symbol("x", real=True)

# The probes are authored independently of the worked-example answer strings.
# Exactly two instances per lesson, in the same lesson order.
EXAMPLE_PROBES = [
    ("114.01.1 log inverse and domain", sp.log(9 - 1, 2) == 3 and 9 > 1),
    ("114.01.2 decreasing log base", sp.log(R(1, 4), R(1, 2)) == 2),
    ("114.02.1 cosine difference", sp.simplify(sp.cos(sp.pi / 3 - sp.pi / 6) - sp.sqrt(3)/2) == 0),
    ("114.02.2 equal angles", sp.cos(sp.pi / 4 - sp.pi / 4) == 1),
    ("114.03.1 bisection twice", (R(5,4)**2 - 2 < 0) and (R(3,2)**2 - 2 > 0) and (R(3,2)-R(5,4)==R(1,4))),
    ("114.03.2 midpoint worst error", R(2, 2**4)/2 == R(1,16)),
    ("114.04.1 absolute square equals square", sp.simplify(sp.Abs(x)**2 - x**2) == 0),
    ("114.04.2 equal formulas differing domains", (-1 in sp.S.Reals) and (-1 not in sp.Interval(0, sp.oo))),
    ("114.05.1 triangular density integral", sp.integrate(2*x, (x, R(1,2), 1)) == R(3,4)),
    ("114.05.2 short uniform interval", sp.integrate(2, (x, 0, R(1,4))) == R(1,2)),
    ("114.06.1 uniform (2,8) moments", sp.integrate(x, (x, 2, 8))/6 == 5 and sp.integrate((x-5)**2, (x, 2, 8))/6 == 3),
    ("114.06.2 uniform (-1,1) probability and variance", sp.integrate(R(1,2), (x, 0, 1)) == R(1,2) and sp.integrate(x*x/2, (x, -1, 1)) == R(1,3)),
    ("114.07.1 independent table", sum([R(1,4)]*4)==1 and R(1,4)==R(1,2)*R(1,2)),
    ("114.07.2 square dependent", R(1,3) != R(1,3)**2 and sum(R(v,3) for v in (-1,0,1))==0),
    ("114.08.1 chi-square three moments", sum([1]*3) == 3 and sum([2]*3) == 6),
    ("114.08.2 t variance existence", R(4,4-2) == 2 and 2-2 == 0),
]

@pytest.mark.parametrize("label,condition", EXAMPLE_PROBES, ids=[a for a,_ in EXAMPLE_PROBES])
def test_independent_exact_worked_example(label, condition):
    assert condition is sp.S.true or condition is True, label

def test_deep_pack_history_counts_all_json_not_only_batch_prefix():
    from app.deep_knowledge import DEEP_DIR
    import build_kb_batch114 as B
    pack = DEEP_DIR / "batch114_functions_statistics.json"
    # The Batch114 snapshot is frozen: later batch packs must not be counted
    # as part of the already-published historical denominator.
    import re
    historical_paths = sorted(
        p for p in DEEP_DIR.glob("*.json")
        if p != pack and not (
            (m := re.match(r"batch(\d+)", p.name)) and int(m.group(1)) >= 115
        )
    )
    history = [item for p in historical_paths for item in json.loads(p.read_text())]
    current = json.loads(pack.read_text())
    audit = json.loads((ROOT / "docs/evaluation/KB_BATCH114_AUDIT.json").read_text())
    assert len(history) > 400  # Detect accidentally counting only batch-prefixed files.
    assert len({z["id"] for z in history + current}) == len(history + current)
    assert audit["prior_deep_drafts"] == len(history)
    assert audit["total_deep_drafts"] == len(history) + len(current)
    assert len(current) == 8
    assert all(not l["review"]["status"]=="APPROVED" for l in current)

def test_formal_and_teacher_gates_still_closed():
    from app.deep_retrieval import student_evidence_lookup
    docs = json.loads((ROOT/"knowledge/deep/v1/batch114_functions_statistics.json").read_text())
    for doc in docs:
        result=student_evidence_lookup(doc["title"])
        assert result["status"] == "NO_APPROVED_EVIDENCE"
        assert not result["teacher_solution_exposed"]
        assert not result.get("citations")


def test_density_reversed_endpoints_refused_as_probability():
    # A true definite integral changes sign if the limits are reversed,
    # but the event {1 <= X <= 1/2} is empty, with probability zero.
    backwards=sp.integrate(2*x,(x,1,R(1,2)))
    assert backwards==-R(3,4) and backwards!=0
    doc=json.loads((ROOT/"knowledge/deep/v1/batch114_functions_statistics.json").read_text())[4]
    assert "a≤b" in doc["statement"]
    assert any("a≤b" in condition for condition in doc["assumptions"])
