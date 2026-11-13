"""Batch99: editorial census, lossless 14 concept claims, seven-track and exact guards."""
from copy import deepcopy
from fractions import Fraction as F
import importlib
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "backend")]
import build_kb_batch99_scope_matrix as S
import build_kb_batch99_seven_track_guard as T
from app.kb_batch99_exact_oracles import (
    verify_all, check, quadratic_range, bivariate_covariance_determinant,
    reflection_fixed_point, epsilon_n_guarantee, line_plane_classify)
from app.deep_knowledge import DeepLesson, lessons
from app.deep_retrieval import student_evidence_lookup

def test_batch99_32_strict_source_hashes_and_no_authority():
    data, scopes = S.build()
    assert len(scopes) == 32
    assert len({x["anchor"] for x in scopes}) == 32
    assert data["remaining_without_individual_editorial"] == 0
    assert data["remaining_without_pairwise_semantic_comparison"] == 134
    assert data["official_atom_denominator"] is None
    assert all(x is None for x in data["official_atom_denominators_by_track"].values())
    assert data["stage_counts"] == {
        "FULL_DEEP_DRAFT_PENDING_TEACHER": 66,
        "INDIVIDUAL_SCOPE_EDITORIAL_PENDING": 44,
        "INDIVIDUAL_SCOPE_NOT_ATOMIZED": 24,
        "PAIR_COMPARISON_NOT_ATOMIZED": 166,
    }
    assert len(data["candidates"]) == sum(data["stage_counts"].values()) == 300
    for item in scopes:
        assert item["teacher_approval"] is None
        assert item["official_atom_id"] is None
        assert not item["student_publishable"]
        assert len(item["nonexample"]) >= 28
    assert data["teacher_approved"] == data["student_authoritative_releases"] == 0

@pytest.mark.parametrize("change", ("missing","duplicate","fake","short"))
def test_32_scope_guard_rejects_missing_duplicate_or_bad(change):
    rows = deepcopy(S.ROWS)
    if change == "missing":
        rows.pop()
    elif change == "duplicate":
        rows[-1]["anchor"] = rows[0]["anchor"]
    elif change == "fake":
        rows[0]["anchor"] = "NOT_AN_OFFICIAL_SOURCE"
    else:
        rows[0]["assumptions"] = "无"
    with pytest.raises(ValueError):
        S.build(rows=rows)

def test_scope_generated_files_strictly_match_authoring():
    x,scopes = S.build()
    assert S.OUTPUT.read_text(encoding="utf8") == S.stable(x)
    assert S.SCOPES.read_text(encoding="utf8") == S.stable(scopes)
    assert S.MARKDOWN.read_text(encoding="utf8") == S.markdown(x,scopes)

def test_all_66_draft_tracks_are_disaggregated_and_not_official():
    x = T.build()
    assert x["total_deep_drafts_audited"] == 66
    assert sum(x["classification_counts"].values()) == 66
    assert x["teacher_approved"] == x["student_authoritative_releases"] == 0
    assert all(t in x["official_atom_denominators_by_track"] for t in T.TRACKS)
    assert all(v is None for v in x["official_atom_denominators_by_track"].values())
    assert x["legacy_missed_cross_track"] == 3
    assert {"math.hs.batch98.09", "math.hs.batch98.10", "math.hs.batch98.11"}.issubset(
        set(x["legacy_missed_lesson_ids"]))
    assert "math.hs.batch97.08" in x["unresolved_lesson_ids"]
    for row in x["lessons"]:
        assert row["classification"] == T.classify(
            row["source_track"],row["declared_engineering_track"])
        assert not row["student_authoritative_index_eligible"]

def test_generic_elective_subtrack_is_not_silently_a_match():
    engineering = {"level":"选修拓展","unit":"竞赛或专题延伸"}
    assert T.map_engineering_track(engineering) is None
    assert T.classify("ELECTIVE_B",None) == "TRACK_UNRESOLVED"
    engineering["unit"] = "选修C课程深度内容"
    assert T.classify("ELECTIVE_B", T.map_engineering_track(engineering)) == "CROSS_TRACK_EDITORIAL_ONLY"
    engineering["level"] = "必修"
    assert T.map_engineering_track(engineering) == "COMPULSORY"
    with pytest.raises(ValueError):
        T.classify("WRONG_SUBTRACK","COMPULSORY")

def test_track_report_determinism():
    x=T.build()
    assert T.OUT.read_text(encoding="utf8")==json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert T.MD.read_text(encoding="utf8")==T.markdown(x)

@pytest.mark.parametrize("batch", (95,96,97,98))
def test_no_concept_author_statement_loss_across_generator_json_markdown(batch):
    rows=importlib.import_module(f"kb_batch{batch}_authoring").RECORDS
    name=({95:"16",96:"12",97:"12",98:"12"})[batch]
    pack=ROOT/f"knowledge/deep/v1/batch{batch}_deep_scope_{name}.json"
    docs=json.loads(pack.read_text(encoding="utf8"))
    path=ROOT/f"docs/evaluation/KB_BATCH{batch}_DEEP_LESSONS.md"
    md=path.read_text(encoding="utf8")
    concepts=[(i,x) for i,x in enumerate(rows) if x["kind"]=="concept"]
    assert concepts
    for i,x in concepts:
        doc=DeepLesson.model_validate(docs[i])
        assert doc.definition==x["definition"]
        assert doc.statement==x["statement"]
        assert x["definition"] in md
        assert x["statement"] in md
        assert doc.review.status=="REVIEW_PENDING"
        assert doc.teacher_solution_visibility=="TEACHER_ONLY"

def test_14_concept_loss_repaired_total():
    counts=[sum(x["kind"]=="concept" for x in importlib.import_module(
        f"kb_batch{i}_authoring").RECORDS) for i in range(95,99)]
    assert counts==[3,3,5,3] and sum(counts)==14

def test_batch98_mathematics_repairs_not_conflating_standard_bivariate_and_reflections():
    rows=importlib.import_module("kb_batch98_authoring").RECORDS
    reflective=rows[6]
    gaussian=rows[8]
    assert "滑移反射" in " ".join(reflective["steps"])
    assert "det(Q)=−1仅表示反向" in reflective["definition"]
    assert "一般非退化二维正态" in gaussian["title"]
    assert "2πσxσy√(1−ρ²)" in gaussian["definition"]
    assert "u²−2ρuv+v²" in gaussian["definition"]
    assert bivariate_covariance_determinant(2,3,F(1,2))==27
    with pytest.raises(ValueError):
        bivariate_covariance_determinant(2,3,1)
    # det(Q)=-1 for both; translation decides if there are any fixed points.
    assert reflection_fixed_point(((1,0),(0,-1)),(0,0))
    assert not reflection_fixed_point(((1,0),(0,-1)),(1,0))

@pytest.mark.parametrize("i",range(1,13))
def test_twelve_exact_positive_and_invalid_premise_witnesses(i):
    x=check(i)
    assert x["finite_positive_case"] and x["invalid_premise_rejected"]
    assert x["student_publishable"] is False
    assert x["general_theorem_certified"] is False

@pytest.mark.parametrize("bad", (True,False,0,13,"3",1.0,None))
def test_illegal_oracle_dispatch_rejected(bad):
    with pytest.raises(ValueError): check(bad)

@pytest.mark.parametrize("a",(-3,-1,0,1,2,4))
@pytest.mark.parametrize("b",(-3,0,2,4))
@pytest.mark.parametrize("c",(-2,0,3))
def test_quadratic_closed_interval_exact_contains_all_grid_values(a,b,c):
    lo,hi=F(-3,2),F(5,2)
    vmin,vmax=quadratic_range(a,b,c,lo,hi)
    for i in range(41):
        x=lo+(hi-lo)*F(i,40)
        y=a*x*x+b*x+c
        assert vmin<=y<=vmax
    assert vmin<=vmax

def test_epsilon_n_strict_endpoint_and_no_zero_division():
    assert not epsilon_n_guarantee(2,F(1,10),20)
    assert epsilon_n_guarantee(2,F(1,10),21)
    with pytest.raises(ValueError): epsilon_n_guarantee(2,0,20)
    with pytest.raises(ValueError): line_plane_classify((0,0,0),(0,0,0),(0,0,1),0)

@pytest.mark.parametrize("key",("math.hs.batch98.03","math.hs.batch98.09","math.hs.batch98.12"))
def test_student_can_never_consume_repaired_teacher_only_content(key):
    doc=next(x for x in lessons() if x.id==key)
    res=student_evidence_lookup(doc.title)
    assert res["status"]=="NO_APPROVED_EVIDENCE"
    assert res["teacher_solution_exposed"] is False
    assert doc.review.status=="REVIEW_PENDING"
    assert all(x.answer not in json.dumps(res,ensure_ascii=False)
               for x in doc.worked_examples)

def test_all_66_prerequisite_descriptions_are_explicitly_unresolved_not_graph_edges():
    import build_kb_batch99_prerequisite_gap as PG
    report=PG.build()
    assert report["total_deep_draft_lessons"]==66
    assert report["textual_prerequisite_descriptions"]==132
    assert report["resolved_prerequisite_id_references"]==0
    assert report["status_counts"]=={"TEXT_ONLY_UNRESOLVED":66}
    assert report["teacher_approved"]==report["student_authoritative_releases"]==0
    assert all(not r["student_authoritative"] and not r["prerequisite_lesson_ids"]
               for r in report["lessons"])
    assert PG.OUT.read_text(encoding="utf8")==json.dumps(report,ensure_ascii=False,
                                            sort_keys=True,indent=2)+"\n"
    assert PG.MD.read_text(encoding="utf8")==PG.markdown(report)

@pytest.mark.parametrize("invalid",("missing","unknown","duplicate","self","authority"))
def test_no_prerequisite_editorial_assumptions_promoted_to_trusted_edges(invalid):
    import build_kb_batch99_prerequisite_gap as PG
    data=json.loads(next((ROOT/"knowledge/deep/v1").glob("batch98_deep_scope_*.json")).read_text())
    p=deepcopy(data[0]); known={row["id"] for row in data}
    if invalid=="missing":p["prerequisites"]=[]
    elif invalid=="unknown":p["prerequisite_lesson_ids"]=["invented.lesson.id"]
    elif invalid=="duplicate":p["prerequisite_lesson_ids"]=[data[1]["id"]]*2
    elif invalid=="self":p["prerequisite_lesson_ids"]=[p["id"]]
    else:p["review"]["status"]="APPROVED"
    with pytest.raises(ValueError):
        PG.checked_lesson(p,known)
