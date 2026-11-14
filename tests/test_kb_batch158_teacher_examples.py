"""Independent real answer checking, mutation negatives, and no answer publication."""
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch158_lessons as lesson
import check_kb_batch158_teacher_examples as exact

def test_reproducible_artifact():
    result=exact.build()
    assert json.loads(exact.OUT.read_text(encoding="utf8"))==result
    assert len(result["cases"])==20
    assert all(r["scope"]=="BOUNDED_EXACT_CASE_NOT_GENERAL_PROOF" for r in result["cases"])
    assert all(not r["student_answer_exposed"] for r in result["cases"])
    assert result["teacher_approved"]==result["student_authoritative"]==0
    assert all("answer" not in x and "solution" not in x for x in result["cases"])

@pytest.mark.parametrize("i",range(20))
def test_wrong_teacher_answer_detected(i):
    rows=copy.deepcopy(lesson.build())
    rows[i//2]["teacher_examples"][i%2]["answer"]="改成错误的数值答案"
    # Current typed/schema gate only ensures structural completeness.
    # Independent semantic oracle must reject incorrect worked answers.
    with pytest.raises(ValueError,match="manuscript answer drift"):
        exact.build(rows)

@pytest.mark.parametrize("i",range(20))
def test_wrong_computed_oracle_must_fail(monkeypatch,i):
    original=exact.exact_truth_cases
    def wrong():
        cases=list(original())
        cases[i]=(False,cases[i][1])
        return cases
    monkeypatch.setattr(exact,"exact_truth_cases",wrong)
    with pytest.raises(ValueError,match="exact mathematics failed"):
        exact.build()
