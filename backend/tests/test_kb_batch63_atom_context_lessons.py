"""Batch63 source-window integrity, teacher-only lesson quality, bounded mathematics."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json, sys
import pytest
import sympy as sp
from test_attested_release_batch08 import offline_reviewer_fixture

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch63_atom_context as C
import validate_kb_batch63_risk_lessons as L
from app import kb_batch63_exact_checks as E

W=C.B61.load(C.WINDOWS)
A=C.B61.load(C.OUT)
M=C.B61.load(L.COVER)
RAW=L.load()

def test_source_evidence_windows_are_all_attested_and_not_certified():
    C.validate(W,A)
    assert len(W["rows"])==45
    assert len({r["anchor_id"] for r in W["rows"]})==45
    assert sum(r["reaches_page_end"] for r in W["rows"])==12
    assert W["includes_copyright_text"] is False
    assert all(r["full_clause_or_cross_page_verified"] is False
               for r in W["rows"])

@pytest.mark.parametrize("n",range(45))
def test_each_hashed_source_window_does_not_fake_full_clause(n):
    row=W["rows"][n]
    assert len(row["source_window_sha256"])==64
    assert row["source_line_sha256"] in [x["source_line_sha256"]
        for x in C.B62.build()["rows"]]
    assert row["window_line_count"]==row["end_line"]-row["start_line"]+1
    assert row["status"]=="MAC_PDFKIT_WINDOW_ONLY_REVIEW_PENDING"
    assert row["original_source_text_committed"] is False
    assert row["full_clause_or_cross_page_verified"] is False
    assert row["source_image_manually_reviewed"] is False

@pytest.mark.parametrize("n",range(62))
def test_each_editorial_atom_hypothesis_is_distinct_from_official_syllabus(n):
    p=A["proposals"][n]
    assert p["candidate_id"].startswith("KB63-P")
    assert p["official_atomic_membership"]=="UNDETERMINED"
    assert p["teacher_review"]=="REVIEW_PENDING"
    assert p["student_publishable"] is False
    assert p["teacher_signature"] is None
    assert p["proof_certification"]=="NOT_CERTIFIED"
    assert p["math_equivalence"]=="NOT_REVIEWED"
    assert p["content_lesson_complete"] is False
    assert len(p["proposed_scope_condition"])>12

def test_seven_track_denominators_are_not_made_up():
    assert A["official_atomic_denominator"]=={track:None for track in C.B61.TRACKS}
    assert A["parent_substantive_scopes"]==31
    assert A["provisional_candidate_count"]==62
    assert A["nonatom_blocks_still_unmapped"]==14
    assert A["provisional_parent_track_counts"]=={"COMPULSORY":30,"ELECTIVE_B":1}
    assert A["formally_approved_lessons"]==A["student_published_lessons"]==0

@pytest.mark.parametrize("tamper",[
    "mutate_window_sha","mutate_window_line","false_source_complete",
    "false_image_review","false_copyright_present","delete_window",
    "duplicate_window","change_window_line_count","incorrect_page",
    "bad_window_status","force_official_denominator",
    "force_teacher_approval","force_student_publish",
    "force_math_equivalence","force_formal_proof",
    "delete_proposal","duplicate_proposal","claim_lesson_complete",
    "claim_full_source","claim_provisional_is_official"
])
def test_stale_or_forged_context_atom_certification_blocked(tamper):
    w=deepcopy(W);a=deepcopy(A)
    if tamper=="mutate_window_sha":w["rows"][0]["source_window_sha256"]="a"*64
    elif tamper=="mutate_window_line":w["rows"][0]["start_line"]=2
    elif tamper=="false_source_complete":w["rows"][0]["full_clause_or_cross_page_verified"]=True
    elif tamper=="false_image_review":w["rows"][0]["source_image_manually_reviewed"]=True
    elif tamper=="false_copyright_present":w["includes_copyright_text"]=True
    elif tamper=="delete_window":w["rows"].pop()
    elif tamper=="duplicate_window":w["rows"][-1]=deepcopy(w["rows"][0])
    elif tamper=="change_window_line_count":w["rows"][0]["window_line_count"]=999
    elif tamper=="incorrect_page":w["rows"][0]["printed_page"]=999
    elif tamper=="bad_window_status":w["rows"][0]["status"]="APPROVED"
    elif tamper=="force_official_denominator":a["official_atomic_denominator"]["COMPULSORY"]=100
    elif tamper=="force_teacher_approval":a["formally_approved_lessons"]=1
    elif tamper=="force_student_publish":a["proposals"][0]["student_publishable"]=True
    elif tamper=="force_math_equivalence":a["proposals"][0]["math_equivalence"]="CERTIFIED"
    elif tamper=="force_formal_proof":a["proposals"][0]["proof_certification"]="PROVED"
    elif tamper=="delete_proposal":a["proposals"].pop()
    elif tamper=="duplicate_proposal":a["proposals"][-1]=deepcopy(a["proposals"][0])
    elif tamper=="claim_lesson_complete":a["proposals"][0]["content_lesson_complete"]=True
    elif tamper=="claim_full_source":a["proposals"][0]["full_source_context_verified"]=True
    elif tamper=="claim_provisional_is_official":a["proposals"][0]["official_atomic_membership"]="INCLUDED"
    with pytest.raises(ValueError):
        C.validate(w,a)

def test_machine_generated_source_reports_are_reproducible():
    assert C.OUT.read_text(encoding="utf-8")==C.canonical(A)
    assert C.REPORT.read_text(encoding="utf-8")==C.render(W,A)
    assert C.WINDOWS.read_text(encoding="utf-8")==C.canonical(W)
    assert A==C.build(W)

def test_all_twelve_original_manuscripts_pass_provenance_and_quality_contract():
    assert len(RAW)==12
    L.validate(M)
    assert M["teacher_only_lessons"]==12
    assert M["minimum_worked_examples"]==24
    assert M["justified_steps"]==36
    assert M["negative_counterexamples"]==12
    assert M["total_hints"]==36
    assert M["curriculum_equivalences_confirmed"]==0
    assert M["formal_general_proofs_certified"]==0
    assert M["student_visible_lessons"]==0
    assert M["original_teacher_side_content_not_indexed_for_students"] is True

@pytest.mark.parametrize("n",range(12))
def test_each_review_pending_lesson_has_assumptions_proofs_examples_hints(n):
    a=RAW[n];m=M["rows"][n]
    assert a["loc"]==list(L.LOCATIONS[n])
    assert a["teacher_review"]=="REVIEW_PENDING"
    assert a["student_publishable"] is False
    assert a["teacher_solution_visibility"]=="TEACHER_ONLY"
    assert len(a["assumptions"])>=2
    assert len(a["reasoning"])>=3
    assert len(a["examples"])>=2
    assert len(a["hints"])==3
    assert a["counterexample"] and a["wrong"] and a["why_wrong"]
    assert a["near"] and a["far"]
    assert m["source_window_sha256"] and m["real_teacher_approved"] is False
    assert m["source_link_status"]=="PROVISIONAL_SCOPE_ONLY_NOT_ATOM_EQUIVALENCE"

@pytest.mark.parametrize("tamper",[
    "approve","publish","certify","verify_student","leak_solution",
    "delete_steps","replace_step_with_unjustified","delete_example",
    "delete_hint","erase_counterexample","erase_assumption",
    "erase_misconception","delete_lesson","duplicate_lesson",
    "wrong_source","claim_official","add_unreviewed_field",
])
def test_teacher_only_manuscript_gate_rejects_forged_status(tamper):
    rows=deepcopy(RAW);r=rows[0]
    if tamper=="approve":r["teacher_review"]="APPROVED"
    elif tamper=="publish":r["student_publishable"]=True
    elif tamper=="certify":r["proof_certification"]="PROVED"
    elif tamper=="verify_student":r["student_answer_verified"]=True
    elif tamper=="leak_solution":r["teacher_solution_visibility"]="STUDENT"
    elif tamper=="delete_steps":r["reasoning"].pop()
    elif tamper=="replace_step_with_unjustified":r["reasoning"][0][1]="嗯"
    elif tamper=="delete_example":r["examples"].pop()
    elif tamper=="delete_hint":r["hints"].pop()
    elif tamper=="erase_counterexample":r["counterexample"]=""
    elif tamper=="erase_assumption":r["assumptions"].clear()
    elif tamper=="erase_misconception":r["why_wrong"]=""
    elif tamper=="delete_lesson":rows.pop()
    elif tamper=="duplicate_lesson":rows[-1]=deepcopy(rows[0])
    elif tamper=="wrong_source":r["loc"]=[73,21]
    elif tamper=="claim_official":r["source_license"]="OFFICIAL_ATOM_CERTIFIED"
    elif tamper=="add_unreviewed_field":r["teacher_signed"]=True
    with pytest.raises(ValueError):
        L.build(lessons=rows)

def test_teacher_manuscript_crosswalk_report_reproducible():
    assert L.COVER.read_text(encoding="utf-8")==L.canonical(M)
    assert L.REPORT.read_text(encoding="utf-8")==L.render(M)

def test_twelve_independent_finite_witnesses_are_explicitly_bounded():
    r=E.run_review_witnesses()
    assert r=={
      "domain":"FINITE_EXACT_CASE_ONLY",
      "negative_multiplier":True,"quantifier":True,
      "quadratic_between":-1,"rational_real_power":True,
      "trig_identity":True,"bisection":"3/2","planar_basis":["1","2"],
      "ssa_solutions":2,"complex_quotient":["11/5","-2/5"],"skew":"SKEW",
      "weighted_probability":"3/10","differential":["4","5","1"],
      "is_general_proof":False,"can_certify_student_open_text":False}

@pytest.mark.parametrize("a,b,c,expected",[
    (2,5,-3,True),(-4,-1,-2,True),(F(1,2),F(2,3),-1,True)
])
def test_reversing_strict_inequality_exact(a,b,c,expected):
    assert E.negative_multiplier(a,b,c) is expected

@pytest.mark.parametrize("a,b,c",[(2,5,0),(2,5,1),(5,2,-1)])
def test_negative_multiplier_rejects_failed_premises(a,b,c):
    with pytest.raises(E.FailedPremise):E.negative_multiplier(a,b,c)

@pytest.mark.parametrize("values",[
    [],[True],[False],[True,False],[True,True,False],[False,False,False]
])
def test_quantifier_denials_with_explicit_finite_domains(values):
    assert E.finite_quantifier_negation(values)
def test_non_boolean_quantifier_rejected():
    with pytest.raises(E.FailedPremise):E.finite_quantifier_negation(["True"])

@pytest.mark.parametrize("x,sign",[(0,1),(F(3,2),-1),(1,0),(2,0),(3,1)])
def test_quadratic_root_interval_sign(x,sign):
    assert E.quadratic_two_root_sign(1,1,2,x)==sign
def test_quadratic_distinct_root_assumptions():
    with pytest.raises(E.FailedPremise): E.quadratic_two_root_sign(0,1,2,0)
    with pytest.raises(E.FailedPremise): E.quadratic_two_root_sign(1,1,1,0)

@pytest.mark.parametrize("base,m,n,allowed",[
    (-8,2,3,True),(-1,1,2,False),(0,-1,2,False),(0,0,1,False),
    (0,2,3,True),(-8,1,3,True),(9,1,2,True)
])
def test_real_rational_power_domain(base,m,n,allowed):
    assert E.rational_base_allowed(base,m,n) is allowed
def test_unreduced_rational_power_rejected():
    with pytest.raises(E.FailedPremise): E.rational_base_allowed(-8,2,6)

@pytest.mark.parametrize("theta",[sp.pi/4,sp.pi/3,sp.pi])
def test_trig_quotient_identity_when_defined(theta):
    assert E.trig_tangent_identity(theta)
def test_trig_denominator_zero():
    with pytest.raises(E.FailedPremise):E.trig_tangent_identity(sp.pi/2)

def test_bisection_half_step_sign_and_interval():
    a,mid,(fa,fb,fmid)=E.quadratic_bisection_one_step()
    assert (a,mid)==(F(1),F(3,2))
    assert (fa,fb,fmid)==(-1,2,sp.Rational(1,4))

@pytest.mark.parametrize("u,v,w,expected",[
    ((1,0),(1,1),(3,2),(F(1),F(2))),
    ((2,0),(0,3),(4,6),(F(2),F(2)))
])
def test_unique_noncollinear_coordinates(u,v,w,expected):
    assert E.vector_basis_coefficients(u,v,w)==expected
def test_collinear_basis_is_not_invertible():
    with pytest.raises(E.FailedPremise):
        E.vector_basis_coefficients((1,2),(2,4),(0,1))

@pytest.mark.parametrize("a,b,count",[
    (5,8,2),(5,12,0),(5,10,1),(5,5,1)
])
def test_ssa_30_degree_ambiguity(a,b,count):
    assert E.ssa_A_30_degrees(a,b)==count

@pytest.mark.parametrize("numerator,denominator,answer",[
    ((1,1),(1,-1),(F(0),F(1))),
    ((3,4),(1,2),(F(11,5),F(-2,5)))
])
def test_exact_complex_division(numerator,denominator,answer):
    assert E.complex_divide(numerator,denominator)==answer
def test_complex_division_by_zero_denied():
    with pytest.raises(E.FailedPremise):E.complex_divide((1,1),(0,0))

@pytest.mark.parametrize("z,relation",[(1,"SKEW"),(0,"INTERSECT_AT_ORIGIN"),(-1,"SKEW")])
def test_spatial_lines_need_three_coordinates(z,relation):
    assert E.spatial_lines_location(z)==relation

def test_finite_unequal_basic_probabilities():
    w={"a":F(1,10),"b":F(2,10),"c":F(7,10)}
    assert E.finite_event_probability(w,["a","b"])==F(3,10)
    with pytest.raises(E.FailedPremise):
        E.classical_count_only_if_equiprobable(w,["a","b"])
    assert E.classical_count_only_if_equiprobable({i:F(1,6) for i in range(6)},[0,2,4])==F(1,2)

def test_invalid_probability_mass_and_event_rejected():
    with pytest.raises(E.FailedPremise): E.finite_event_probability({"a":F(2,10)},["a"])
    with pytest.raises(E.FailedPremise): E.finite_event_probability({"a":1},["b"])
    with pytest.raises(E.FailedPremise): E.classical_count_only_if_equiprobable({"a":1},["b"])

@pytest.mark.parametrize("x,h,answer",[
    (2,1,(F(4),F(5),F(1))),
    (-1,F(1,2),(F(-1),F(-3,4),F(1,4))),
    (3,0,(F(0),F(0),F(0)))
])
def test_square_differential_is_linear_part_plus_remainder(x,h,answer):
    assert E.square_finite_increment(x,h)==answer

def test_new_teacher_manuscripts_remain_outside_student_signed_index(offline_reviewer_fixture):
    # Existing test-only RSA signing fixture exercises the nonempty approved
    # index, not just the default empty-index early return.
    from app.attested_releases import approved_lesson_ids
    from app.deep_retrieval import student_evidence_lookup
    from app.deep_knowledge import lessons
    doc, reviewers, _, _, record, save=offline_reviewer_fixture
    save([record(0), record(1)])
    assert approved_lesson_ids()=={doc.id}
    known_ids={x.id for x in lessons()}
    for manuscript in RAW:
        assert manuscript["lesson_id"] not in known_ids
        res=student_evidence_lookup(manuscript["title"])
        assert set(hit["knowledge_id"] for hit in res["candidates"])<={doc.id}
        assert manuscript["lesson_id"] not in json.dumps(res,ensure_ascii=False)
        assert res["teacher_solution_exposed"] is False
        assert res["unverified_content_exposed"] is False


@pytest.mark.parametrize("event",[
    ["a","a"], ("a","a"), ["a","b","a"]
])
def test_repeated_outcome_cannot_inflate_finite_event_probability(event):
    weights={"a":F(1,10),"b":F(9,10)}
    with pytest.raises(E.FailedPremise):
        E.finite_event_probability(weights,event)
    with pytest.raises(E.FailedPremise):
        E.classical_count_only_if_equiprobable({"a":F(1,2),"b":F(1,2)},event)

@pytest.mark.parametrize("bad_angle",[sp.Symbol("x"), sp.pi*sp.Symbol("k"), 1.0])
def test_symbolic_or_inexact_angle_not_promoted_to_exact_trig_witness(bad_angle):
    with pytest.raises(E.FailedPremise):
        E.trig_tangent_identity(bad_angle)

def test_booleans_and_inexact_floats_not_accepted_as_probability_mass():
    for bad in (True,F(1,2),0.5):
        weights={"a":bad,"b":1-bad}
        if type(bad) is F:
            assert E.finite_event_probability(weights,["a"])==F(1,2)
            continue
        with pytest.raises(E.FailedPremise):
            E.finite_event_probability(weights,["a"])

def test_reject_event_without_collection_semantics():
    with pytest.raises(E.FailedPremise):
        E.finite_event_probability({"a":F(1)}, "a")
