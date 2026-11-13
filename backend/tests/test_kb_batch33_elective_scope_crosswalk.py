"""Batch33 K00/K01/K07/K09 source, candidate, crosswalk and bounded math guards."""
from __future__ import annotations
import copy
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys
import pytest
from app.kb_batch33_elective_finite_math import OPS,finite,guarded_evaluate

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch33_elective_scope as scope
import build_kb_batch33_draft_crosswalk as crosswalk
import build_kb_batch33_math_finite_audit as mathaudit

AUDIT=json.loads(scope.REPORT.read_text())
LINKS=json.loads(crosswalk.REPORT.read_text())
FIN=json.loads(mathaudit.OUT.read_text())
FIX=json.loads(mathaudit.SOURCE.read_text())["fixtures"]
VALID={x["op"]:x["valid"] for x in FIX}
INVALID={x["op"]:x["invalid"] for x in FIX}

def test_full_source_report_is_reproducible_but_not_approved():
    assert json.loads(scope.build())==AUDIT
    assert AUDIT["summary"]["total_pages_inspected_text_or_visual"]==61
    assert AUDIT["summary"]["new_pages_inspected_text"]==24
    assert AUDIT["summary"]["remaining_uninspected_pages"]==0
    assert AUDIT["summary"]["remaining_pages_not_exhaustively_clause_mapped"]==61
    assert AUDIT["summary"]["batch33_editorial_candidates"]==96
    assert AUDIT["summary"]["all_provisional_editorial_candidates"]==313
    assert AUDIT["summary"]["cumulative_provisional_track_counts"]==dict(
        COMPULSORY=125,SELECTIVE_COMPULSORY=92,ELECTIVE_A=28,
        ELECTIVE_B=29,ELECTIVE_C=19,ELECTIVE_D=16,ELECTIVE_E=4)
    assert all(v is None for v in AUDIT["official_denominators_by_track"].values())
    assert AUDIT["summary"]["teacher_approved_lessons"]==0
    assert AUDIT["summary"]["student_published_deep_lessons"]==0
    assert not AUDIT["evidence_boundary"]["numbered_and_unnumbered_requirements_all_mapped"]

@pytest.mark.parametrize("r",AUDIT["editorial_goals"],ids=lambda x:x["editorial_id"])
def test_all_96_candidate_provenance_and_strict_pending_status(r):
    page=r["source_printed_page"]
    assert page in scope.PDFKIT_PAGES and r["source_mac_pdfkit_page_sha256"]==scope.PDFKIT_PAGES[page]
    assert r["source_original_pdf_sha256"]==scope.SOURCE
    assert r["syllabus_track"] in scope.allowed_tracks(page)
    assert r["source_anchor_level"]=="PAGE_SECTION_ONLY_NOT_INDIVIDUAL_CLAUSE_VERIFIED"
    assert not r["official_clause_alignment_verified"]
    assert r["official_atom_id"] is None and r["approved_lesson_id"] is None
    assert r["teacher_review"]=="PENDING" and not r["student_publishable"]
    assert r["student_solution_visibility"]=="NONE"
    if r["syllabus_track"]=="ELECTIVE_E":
        assert r["elective_E_local_exemplar_not_nationally_mandated"]

@pytest.mark.parametrize("page",range(13,74))
def test_each_61_page_inspection_is_not_clause_coverage(page):
    p=AUDIT["pages"][page-13]
    assert p["printed_page"]==page
    assert p["official_atom_count"] is None
    assert p["unnumbered_clause_completeness"]=="UNKNOWN"
    assert p["original_teacher_page_review"]=="PENDING"
    if page==35:
        assert p["page35_damaged_visual_source_pending"]

def test_editorial_seed_is_pinned_and_two_existing_reports_unchanged(monkeypatch):
    monkeypatch.setattr(scope,"SEED_SHA","0"*64)
    with pytest.raises(ValueError,match="seed drift"):
        scope.build()

@pytest.mark.parametrize("line",[
    "57|ELECTIVE_B|参数估计|method|错误地将A课程主题当作B新主题进行编号",
    "64|ELECTIVE_C|参变数|method|跨专题错误归档不属于已经核对的部分",
    "73|ELECTIVE_E|赛事安排|method|本页面不允许任意转换学校自设主题的条目",
    "50|ELECTIVE_A|数列极限|concept|这个页面不在本批核对的选修课程正文",
    "73|ELECTIVE_E|全国统一章节|theorem|误将学校自定义课程设置成全国统一强制知识",
    "62|COMPULSORY|正交设计|method|选择性选修不能替代必修高中数学课程内容",
])
def test_mixed_section_pages_and_track_leakage_rejected(line):
    seed=scope.SEED.read_text()
    with pytest.raises(ValueError):
        scope.parse(seed+"\n"+line)

def test_pinned_source_ledger_cannot_be_swapped():
    bad=copy.deepcopy(scope.b31.read_ledger())
    bad["source"]["sha256"]="a"*64
    with pytest.raises(ValueError,match="substitution"):
        scope.build(ledger=bad)

def test_crosswalk_is_review_only_not_index_or_curriculum_coverage():
    assert json.loads(crosswalk.build())==LINKS
    assert LINKS["summary"]["total_deep_lessons_existing"]==287
    assert LINKS["summary"]["suggested_related_draft_pairs"]==47
    assert LINKS["summary"]["no_suggested_related_draft"]==49
    assert LINKS["summary"]["approved_lessons"]==0
    assert LINKS["summary"]["official_atom_denominator"] is None
    assert not LINKS["policy"]["student_exposed"]
    assert not LINKS["policy"]["search_index_modified"]

@pytest.mark.parametrize("link",LINKS["links"],ids=lambda x:x["editorial_candidate_id"])
def test_every_curated_pair_is_a_non_authoritative_suggestion(link):
    assert link["teacher_review"]=="PENDING"
    assert link["association_status"]=="HUMAN_REVIEW_REQUIRED_NOT_CLAUSE_COVERAGE"
    assert not link["curriculum_atom_covered"]
    assert not link["mathematically_equivalent_content_certified"]
    assert not link["draft_solution_visible_to_student"]
    assert not link["exact_official_clause_alignment_verified"]
    assert link["related_draft_lesson_id"] in crosswalk.lessons()

@pytest.mark.parametrize("mutation",[
    "duplicate","missing_lesson","missing_candidate","short_reason","faked_approval"
])
def test_unreliable_pairing_cannot_enter_crosswalk(mutation):
    original=crosswalk.TSV.read_text()
    row=next(x for x in original.splitlines() if x.startswith("KB33-"))
    atom,lesson,reason=row.split("|")
    if mutation=="duplicate":append=row
    elif mutation=="missing_lesson":append=f"KB33-A-P052-A002|no_such_lesson|{reason}"
    elif mutation=="missing_candidate":append=f"KB33-A-P052-A999|{lesson}|{reason}"
    elif mutation=="short_reason":append=f"KB33-A-P052-A002|{lesson}|ok"
    else:append=f"KB33-A-P052-A002|{lesson}|该内容已经完全覆盖并已审核不用再检查"
    with pytest.raises(ValueError):
        crosswalk.build(seed=original+"\n"+append)

def test_math_fixtures_have_precise_scope_and_refuse_bad_premise():
    assert json.loads(mathaudit.build())==FIN
    assert len(FIN["mathematical_evidence"])==5
    assert FIN["summary"]["valid_instances"]==FIN["summary"]["invalid_premises_rejected"]==5
    assert FIN["summary"]["universal_theorems_formally_certified"]==0
    for op in OPS:
        good=guarded_evaluate(op,VALID[op]);bad=guarded_evaluate(op,INVALID[op])
        assert good["status"]=="VERIFIED_FINITE_INSTANCE" and good["witness"]
        assert bad["status"]=="CONDITIONS_NOT_ESTABLISHED" and bad["witness"] is None
        for field in ("whole_theorem_certified","teacher_approved",
                      "student_freeform_step_verified","official_atomic_goal_certified",
                      "student_solution_release_authorized"):
            assert good[field] is False and bad[field] is False

@pytest.mark.parametrize("mutation",["fake_release","fake_approval","new_op","bad_atom","wrong_answer","weak_justification"])
def test_math_audit_rejects_forgery_unknown_atom_and_invalid_witness(mutation):
    d=json.loads(mathaudit.SOURCE.read_text())
    if mutation=="fake_release":d["student_publishable"]=True
    elif mutation=="fake_approval":d["teacher_approved"]=True
    elif mutation=="new_op":d["fixtures"][0]["op"]="LLM_STEP_JUDGE"
    elif mutation=="bad_atom":d["fixtures"][0]["editorial_id"]="KB33-NO-ATOM"
    elif mutation=="wrong_answer":d["fixtures"][0]["valid"]["n"]=-1
    else:d["fixtures"][0]["math_justification"]="显然"
    with pytest.raises(ValueError):
        mathaudit.build(fixtures=d)

@pytest.mark.parametrize("a,b,x0,n",[
    (a,b,x0,n) for a,b,x0,n in product((-2,-1,0,1,2),(-2,0,2),(-3,0,3),(0,1,2,3,6))
])
def test_affine_recurrence_exact_direct_against_closed_form(a,b,x0,n):
    z=finite("affine_recurrence",dict(a=a,b=b,x0=x0,n=n))
    q=F(x0)
    for _ in range(n):q=F(a)*q+F(b)
    assert z["direct"]==z["closed_form"]==q

@pytest.mark.parametrize("principal,rate,n",[
    (p,r,n) for p,r,n in product((0,1,37,100),("0","1/5","-1/2"),range(7))
])
def test_compound_growth_exact_against_direct_repeated_product(principal,rate,n):
    z=finite("compound_growth",dict(principal=principal,rate=rate,n=n))
    assert z["amount"]==F(principal)*(1+F(rate))**n

@pytest.mark.parametrize("p,q",product(range(1,22),range(1,22)))
def test_rhythm_sync_is_smallest_shared_positive_multiple(p,q):
    z=finite("rhythm_sync",dict(p=p,q=q))
    n=z["first_sync"]
    assert n%p==0 and n%q==0
    assert all(k%p or k%q for k in range(1,n))

@pytest.mark.parametrize("matrix",[
    [[1,0],[0,1]],[[0,1],[-1,0]],[[-1,0],[0,1]],[[0,-1],[-1,0]],
])
def test_orthogonal_matrices_preserve_small_grid_distances(matrix):
    z=finite("orthogonal_matrix_2d",dict(matrix=matrix))
    assert z["gram_identity"] and abs(z["determinant"])==1
    for x,y in product(range(-2,3),repeat=2):
        vx=matrix[0][0]*x+matrix[0][1]*y
        vy=matrix[1][0]*x+matrix[1][1]*y
        assert vx*vx+vy*vy==x*x+y*y

@pytest.mark.parametrize("a,b,c,d",[
    (a,b,c,d) for a,b,c,d in product((-2,-1,0,1,2),repeat=4)
    if a*d-b*c !=0
][:320])
def test_unique_linear_system_has_exact_back_substitution(a,b,c,d):
    z=finite("unique_linear_system_2d",dict(matrix=[[a,b],[c,d]],rhs=[3,-2]))
    assert a*z["x"]+b*z["y"]==3
    assert c*z["x"]+d*z["y"]==-2

@pytest.mark.parametrize("bad",["__import__('os').system('true')",True,1.5,"1/0","1e9","99999",None])
def test_no_untrusted_expression_or_unbounded_numeric_input(bad):
    p=dict(VALID["compound_growth"],rate=bad)
    assert guarded_evaluate("compound_growth",p)["status"]=="CONDITIONS_NOT_ESTABLISHED"
