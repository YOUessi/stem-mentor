"""Batch64: 14 draft lesson audits, 14 still-unmapped capability blocks, exact witnesses."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json,sys
import pytest
from test_attested_release_batch08 import offline_reviewer_fixture

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch64_deep_competency as D
from app import kb_batch64_exact_witnesses as E

LESSONS=D.get(D.LESSONS)
M,C=D.build()
def test_release_artifacts_replay_from_locked_mac_source_candidates():
    assert D.get(D.MATRIX)==M
    assert D.get(D.ABILITY)==C
    assert D.REPORT.read_text(encoding="utf-8")==D.render(M,C)
    D.validate(M,C)
    assert len(M["rows"])==14 and len(C["links"])==28
    assert M["teacher_example_count"]==28
    assert M["justified_steps"]==42
    assert M["authored_counterexamples"]==14
    assert M["hint_tiers"]==42
    assert C["abilities_certified"]==0 and C["all_nonatom_sections_still_unmapped"]

@pytest.mark.parametrize("i",range(14))
def test_each_teacher_only_lesson_has_attested_provisional_source_not_official(i):
    v=LESSONS[i];row=M["rows"][i]
    assert v["teacher_review"]=="REVIEW_PENDING"
    assert v["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert v["student_publishable"] is False
    assert v["proof_certification"]=="NOT_FORMALLY_CERTIFIED"
    assert v["student_answer_verified"] is False
    assert row["official_membership_confirmed"] is False
    assert row["real_teacher_approved"] is False
    assert row["source_full_clause_reviewed"] is False
    assert len(row["hypothesized_atom_ids"])==2
    assert len(v["reasoning"])>=3 and all(len(x)==2 for x in v["reasoning"])
    assert len(v["examples"])>=2
    assert len(v["hints"])==3 and v["counterexample"] and v["wrong"]
    assert v["near"] and v["far"]

@pytest.mark.parametrize("i",range(14))
def test_each_non_atom_section_keeps_independent_unmapped_status(i):
    section=D.get(D.SECTIONS)["rows"][i]
    linked=C["links"][2*i:2*i+2]
    assert all(x["official_section_anchor"]==section["anchor_id"] for x in linked)
    assert all(x["coverage_status"]=="UNMAPPED" for x in linked)
    assert all(not x["abilities_covered"] and not x["unnumbered_objectives_reviewed"]
               and not x["teacher_approved"] and not x["student_visible"]
               for x in linked)
    assert all(x["proposed_lesson_id"] in {v["lesson_id"] for v in LESSONS} for x in linked)
    assert section["numbered_atom_membership"]=="NOT_A_STANDALONE_ATOM"

@pytest.mark.parametrize("i",range(28))
def test_each_example_pointer_is_to_teacher_only_manuscript(i):
    link=C["links"][i]
    lesson=next(v for v in LESSONS if v["lesson_id"]==link["proposed_lesson_id"])
    n=int(link["proposed_example_id"][-2:])
    assert 1<=n<=len(lesson["examples"])
    assert len(lesson["examples"][n-1])==3
    assert link["linkage_kind"]=="EDITORIAL_SAMPLE_NOT_OFFICIAL_REQUIREMENT_MAPPING"

@pytest.mark.parametrize("mutation",[
    "publish","teacher_approve","certify_proof","verify_student","leak_solution",
    "remove_reason","erase_counterexample","remove_example","remove_hint",
    "change_anchor","duplicate_lesson","delete_lesson","change_source_license",
    "bad_kind","change_assumption","fake_denominator","force_competency",
    "truncate_section","change_section_status","fake_teacher_signature",
])
def test_review_and_content_gate_refuses_tampering(mutation):
    rows=deepcopy(LESSONS);source=None;sections=None
    v=rows[0]
    if mutation=="publish":v["student_publishable"]=True
    elif mutation=="teacher_approve":v["teacher_review"]="APPROVED"
    elif mutation=="certify_proof":v["proof_certification"]="CERTIFIED"
    elif mutation=="verify_student":v["student_answer_verified"]=True
    elif mutation=="leak_solution":v["teacher_solution_visibility"]="STUDENT"
    elif mutation=="remove_reason":v["reasoning"].pop()
    elif mutation=="erase_counterexample":v["counterexample"]=""
    elif mutation=="remove_example":v["examples"].pop()
    elif mutation=="remove_hint":v["hints"].pop()
    elif mutation=="change_anchor":v["loc"]=[14,14]
    elif mutation=="duplicate_lesson":rows[-1]=deepcopy(v)
    elif mutation=="delete_lesson":rows.pop()
    elif mutation=="change_source_license":v["source_license"]="UNKNOWN"
    elif mutation=="bad_kind":v["kind"]="FAKE_PROOF"
    elif mutation=="change_assumption":v["assumptions"]=[]
    elif mutation=="fake_denominator":
        import build_kb_batch63_atom_context as B
        source=deepcopy(B.build())
        source["official_atomic_denominator"]["COMPULSORY"]=99
    elif mutation=="force_competency":
        sections=deepcopy(D.get(D.SECTIONS))
        sections["rows"][0]["coverage_status"]="APPROVED"
    elif mutation=="truncate_section":
        sections=deepcopy(D.get(D.SECTIONS));sections["rows"].pop()
    elif mutation=="change_section_status":
        sections=deepcopy(D.get(D.SECTIONS));sections["rows"][0]["teacher_approved"]=True
    elif mutation=="fake_teacher_signature":v["teacher_signature"]="fake"
    with pytest.raises(ValueError):
        D.build(rows,source,sections)

@pytest.mark.parametrize("mutate",["student_publish","general_proof","false_competency","wrong_link"])
def test_manifests_reject_authority_forgery(mutate):
    m=deepcopy(M);c=deepcopy(C)
    if mutate=="student_publish":m["student_published"]=1
    if mutate=="general_proof":m["certified_general_proofs"]=1
    if mutate=="false_competency":c["abilities_certified"]=1
    if mutate=="wrong_link":c["links"][0]["proposed_lesson_id"]="MISSING"
    with pytest.raises(ValueError):D.validate(m,c)

@pytest.mark.parametrize("x,expected",[(2,True),(-2,True),(0,False),(3,False),(5,False)])
def test_integer_membership_exact(x,expected):assert E.finite_membership(x) is expected
def test_sets_subset_and_complement():
    assert E.subset_relation({1,2},{2,1,3})==(True,False,True)
    assert E.subset_relation({1},{1})==(True,True,False)
    assert E.complement({1,2,3,4},{2,4})=={1,3}
    with pytest.raises(E.FailedPremise):E.complement({1},{2})
def test_finite_sufficient_conditions_and_counterexample():
    assert E.finite_implication(tuple(range(-4,5)),lambda x:x>2,lambda x:x>0)
    assert not E.finite_implication(tuple(range(-4,5)),lambda x:x>0,lambda x:x>2)
    assert E.finite_implication(tuple(range(-4,5)),lambda x:x%2==0,lambda x:x*x%2==0)
    with pytest.raises(E.FailedPremise):
        E.finite_implication((1,2),lambda x:1,lambda x:x>0)
@pytest.mark.parametrize("a,b,am,gm,equal",[
    (1,9,F(5),F(3),False),(4,4,F(4),F(4),True),(0,0,F(0),F(0),True),(0,16,F(8),F(0),False)
])
def test_nonnegative_amgm_exact_square_cases(a,b,am,gm,equal):
    assert E.arithmetic_geometric(a,b)==(am,gm,equal)
def test_amgm_rejects_negative_or_unsupported_radicals():
    with pytest.raises(E.FailedPremise):E.arithmetic_geometric(-1,-4)
    with pytest.raises(E.FailedPremise):E.arithmetic_geometric(2,3)
def test_single_valued_function_counterexample():
    assert E.finite_function_is_single_valued([(0,0),(1,1),(1,1)])
    assert not E.finite_function_is_single_valued([(1,1),(1,-1)])
    with pytest.raises(E.FailedPremise):E.finite_function_is_single_valued([])
@pytest.mark.parametrize("base,a,b,expected",[
    (2,2,3,True),(F(1,2),2,3,False),(F(1,2),3,2,True),(3,0,1,True)
])
def test_exponent_strict_order(base,a,b,expected):
    x,y,less=E.exponent_comparison(base,a,b)
    assert (x<y) is expected and less is expected
@pytest.mark.parametrize("a",[-2,0,1])
def test_exponent_bad_bases(a):
    with pytest.raises(E.FailedPremise):E.exponent_comparison(a,0,1)
def test_exact_log_power_with_safe_denominator():
    assert E.log_power_identity(4,8,3,2)
    assert E.log_power_identity(9,3,1,2)
    assert not E.log_power_identity(4,8,1,2)
    for a,x in [(1,3),(0,4),(2,0),(-1,3)]:
        with pytest.raises(E.FailedPremise):E.log_power_identity(a,x,1,2)
@pytest.mark.parametrize("k,expected",[(0,F(0)),(2,F(0)),(4,F(0)),(-2,F(0))])
def test_tangent_on_defined_axis(k,expected):
    assert E.tangent_quadrant(k)==expected
@pytest.mark.parametrize("k",[1,3,-1,5])
def test_tangent_undefined(k):
    with pytest.raises(E.FailedPremise):E.tangent_quadrant(k)
def test_period_requires_nonconstant_sinusoid():
    assert E.normalized_period(2,4)==F(1,4)
    assert E.normalized_period(3,-3)==F(1,3)
    for a,w in [(0,3),(3,0)]:
        with pytest.raises(E.FailedPremise):E.normalized_period(a,w)
@pytest.mark.parametrize("N,n,combinations,individual",[
    (4,2,6,F(1,2)),(5,2,10,F(2,5)),(6,3,20,F(1,2)),(7,1,7,F(1,7))
])
def test_exact_simple_random_sampling(N,n,combinations,individual):
    total,group,selection=E.simple_random_sample(N,n)
    assert total==combinations and group==F(1,total) and selection==individual
def test_sampling_input_failures():
    for N,n in [(4,0),(3,5),(0,0),(-2,1),(4.0,2)]:
        with pytest.raises(E.FailedPremise):E.simple_random_sample(N,n)
def test_complex_components_vs_imaginary_terms():
    assert E.complex_parts_equal(3,2,3,2)
    assert not E.complex_parts_equal(3,2,3,-2)
    assert E.complex_parts_equal(F(1,2),-3,F(1,2),-3)
def test_linear_model_residual_and_extrapolation_do_not_prove_truth():
    y,pred,outside=E.model_residuals([(0,1),(1,3),(2,5)],2,1,3)
    assert y==[0,0,0] and pred==7 and outside
    y,pred,outside=E.model_residuals([(0,1),(1,3),(2,5)],2,1,1)
    assert pred==3 and not outside
    # Alternative polynomial agrees at 0,1,2 but gives 13 at x=3.
    x=3
    assert 2*x+1+x*(x-1)*(x-2)==13
def test_line_parallel_to_z_plane_vs_contained_or_intersecting():
    assert E.line_parallel_z_plane((0,0,1),(1,0,0)) is True
    assert E.line_parallel_z_plane((0,0,2),(0,1,0)) is True
    assert E.line_parallel_z_plane((0,0,0),(1,0,0)) is False
    assert E.line_parallel_z_plane((0,0,1),(1,0,1)) is False
    with pytest.raises(E.FailedPremise):E.line_parallel_z_plane((0,0,1),(0,0,0))
def test_no_float_or_boolean_permitted_as_exact_evidence():
    for bad in [0.5,True,False]:
        with pytest.raises(E.FailedPremise):E.finite_membership(bad)
        with pytest.raises(E.FailedPremise):E.arithmetic_geometric(bad,1)
        with pytest.raises(E.FailedPremise):E.normalized_period(1,bad)

def test_signed_nonempty_approved_retrieval_excludes_all_fourteen_new_drafts(offline_reviewer_fixture):
    """Test the real mixed-index path, not the empty-approved-set shortcut."""
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    from app.deep_knowledge import lessons
    doc, reviewers, _, _, record, save=offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids()=={doc.id}
    indexed={x.id for x in lessons()}
    for manuscript in LESSONS:
        assert manuscript["lesson_id"] not in indexed
        response=student_evidence_lookup(manuscript["title"])
        assert {hit["knowledge_id"] for hit in response["candidates"]}<={doc.id}
        assert manuscript["lesson_id"] not in json.dumps(response,ensure_ascii=False)
        assert response["teacher_solution_exposed"] is False
        assert response["unverified_content_exposed"] is False
