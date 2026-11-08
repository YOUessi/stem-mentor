"""Batch31 K00/K01/K07 source atomicity, prerequisite safety and independent finite math."""
from __future__ import annotations
import copy
import json
import sys
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import pytest
from app.kb_batch31_core_exact_instances import OPS,evaluate,do

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch31_atomic_core as source
import build_kb_batch31_graph as graph

SOURCE=json.loads(source.REPORT.read_text(encoding="utf8"))
GRAPH=json.loads(graph.OUT.read_text(encoding="utf8"))
FIX=json.loads((ROOT/"knowledge/proof/batch31_core_instance_fixtures.json").read_text(encoding="utf8"))
F_BY_OP={x["op"]:x for x in FIX["fixtures"]}

def test_source_original_87_candidates_review_only():
    assert json.loads(source.build())==SOURCE
    s=SOURCE["summary"]
    assert (s["original_editorial_atomic_candidate_count"],s["new_atomic_candidate_pages"])==(87,12)
    assert s["assistant_rendered_page_total"]==9
    assert s["batch31_visual_page_sha_count"]==8
    assert s["remaining_pages_uninspected"]==46
    assert (s["teacher_verified_atomic_items"],s["teacher_approved_lessons"],s["student_published_lessons"])==(0,0,0)
    assert all(v is None for v in SOURCE["by_track_official_denominators"].values())
    assert all(x["teacher_review"]=="PENDING" and not x["student_publishable"] and
               not x["matched_teacher_approved_lesson_ids"] and x["official_atomic_id"] is None
               for x in SOURCE["items"])
    assert set(x["source_printed_page"] for x in SOURCE["items"])=={15,16,17,19,20,21,22,23,25,26,27,28}
    assert any(x["optional_starred_non_exam"] for x in SOURCE["items"])
    assert all(x["track"]=="COMPULSORY" for x in SOURCE["items"])

@pytest.mark.parametrize("candidate",SOURCE["items"],ids=lambda x:x["id"])
def test_each_source_atom_has_unique_pinned_provenance_no_publish(candidate):
    assert candidate["source_pdf_sha256"]==source.SOURCE_SHA
    assert candidate["source_pdf_index_zero_based"]==candidate["source_printed_page"]+7
    assert len(candidate["source_page_extracted_sha256"])==64
    if candidate["source_printed_page"] in source.VISUAL_RENDER_SHA:
        page=next(x for x in SOURCE["pages"] if x["printed_page"]==candidate["source_printed_page"])
        assert page["assistant_render_sha256"]==source.VISUAL_RENDER_SHA[candidate["source_printed_page"]]
    assert candidate["review_status"]=="EDITORIAL_ATOM_CANDIDATE_REVIEW_PENDING"
    assert candidate["official_clause_anchor_status"]=="PAGE_LEVEL_ONLY_NOT_INDEPENDENTLY_MAPPED"

@pytest.mark.parametrize("bad_seed",[
    "15|集合运算|method|N|在共同论域内求两个集合的并集\n15|集合运算|method|N|在共同论域内求两个集合的并集",
    "14|集合运算|method|N|非法页码不能进入已检查的课标单元表",
    "15|集合运算|proof|N|不存在的知识类型应被严格拒绝",
    "15|集合运算|method|Y|太短",
    "15|集合运算|method|NO|错误的选修标记不应进入知识库",
    "28|空间向量|method|N|跨页置换会导致来源次序错误\n15|集合运算|method|N|在共同论域内求两个集合的并集",
])
def test_source_seed_attack_refused(bad_seed):
    with pytest.raises(ValueError):source.build(seed=bad_seed)

@pytest.mark.parametrize("field,value",[
    ("tracks_present",["ELECTIVE_A"]),
    ("pdf_page_index",0),
    ("pdf_text_sha256","a"*64)
])
def test_source_wrong_track_or_page_index_rejected(field,value):
    payload=copy.deepcopy(source.read_ledger())
    for p in payload["pages"]:
        if p["printed_page"]==15:
            p[field]=value;break
    with pytest.raises(ValueError):source.build(ledger=payload)

def test_source_not_equated_with_official_denom():
    assert sum(SOURCE["by_track_editorial_candidate_counts"].values())==87
    assert SOURCE["summary"]["full_official_atomic_denominator"] is None
    assert SOURCE["summary"]["official_content_coverage_rate"] is None
    assert SOURCE["page_inspection_status_counts"]["AWAITING_ORIGINAL_CONTENT_INSPECTION"]==46

def test_graph_32_new_prerequisite_proposals_are_isolated():
    assert json.loads(graph.build())==GRAPH
    s=GRAPH["summary"]
    assert (s["new_editorial_proposals"],s["editorial_proposals_total"],s["still_no_editorial_candidate"])==(32,63,70)
    assert (s["teacher_approved_proposals"],s["student_visible_proposals"])==(0,0)
    assert s["combined_candidate_graph_acyclic"] and not s["authoritative_graph_modified"]
    assert len(GRAPH["new_proposals"])==32
    assert all(x["teacher_review"]=="PENDING" and not x["applied_to_authoritative_lesson_graph"]
               for x in GRAPH["new_proposals"])

@pytest.mark.parametrize("proposal",GRAPH["new_proposals"],ids=lambda x:x["lesson_id"])
def test_new_proposal_has_math_reason_and_is_not_graph(proposal):
    assert len(proposal["rationale"])>=28
    assert proposal["lesson_id"]!=proposal["prerequisite_lesson_id"]
    assert proposal["teacher_review"]=="PENDING"
    assert proposal["applied_to_authoritative_lesson_graph"] is False

@pytest.mark.parametrize("tamper",["fake_approval","bad_parent","duplicate","cycle","student_release","bad_reason"])
def test_graph_forgery_or_error_rejected(tamper):
    d=copy.deepcopy(GRAPH["new_proposals"])
    old=dict(json.loads(graph.BASE.read_text(encoding="utf-8")))
    if tamper=="fake_approval":d[0]["teacher_review"]="APPROVED"
    if tamper=="bad_parent":d[0]["prerequisite_lesson_id"]="untrusted.fake.prerequisite"
    if tamper=="duplicate":d[0]["lesson_id"]=d[1]["lesson_id"];d[0]["prerequisite_lesson_id"]=d[1]["prerequisite_lesson_id"]
    if tamper=="cycle":
        # make a 2-node cycle from currently unlinked candidate lessons
        d[0]["prerequisite_lesson_id"]=d[1]["lesson_id"]
        d[1]["prerequisite_lesson_id"]=d[0]["lesson_id"]
    if tamper=="student_release":old["student_publishable"]=True
    if tamper=="bad_reason":d[0]["rationale"]="ok"
    old["items"]+=d
    from app.kb_batch26_graph import validate_editorial_graph,EditorGraphError
    with pytest.raises(EditorGraphError):validate_editorial_graph(old)

def test_graph_endpoint_stays_editor_only():
    from app.kb_batch26_graph import editor_prerequisite_proposals
    with pytest.raises(PermissionError):editor_prerequisite_proposals(GRAPH["new_proposals"][0]["lesson_id"])

def test_fixture_set_exactly_matches_ops_no_formal_claim():
    assert len(FIX["fixtures"])==len(OPS)==12
    assert set(F_BY_OP)==set(OPS)
    assert F_BY_OP["geometric_sum"]["k00_page"] is None
    assert F_BY_OP["geometric_sum"]["source_alignment"]=="CROSS_TOPIC_BOUNDED_VERIFIER_NOT_MAPPED_TO_THIS_BATCH_SOURCE"
    assert FIX["official_atomic_denominator"] is None
    assert FIX["teacher_approved"] is FIX["student_publishable"] is False

@pytest.mark.parametrize("op",OPS)
def test_valid_case_and_invalid_condition(op):
    f=F_BY_OP[op]
    a=evaluate(op,f["valid"]);b=evaluate(op,f["invalid"])
    assert (a["status"],b["status"])==("VERIFIED_FINITE_INSTANCE","CONDITIONS_NOT_ESTABLISHED")
    assert a["witness"] is not None and b["witness"] is None
    for z in [a,b]:
        for k in ("complete_theorem_certified","student_step_verified","teacher_approved",
                  "official_curriculum_atom_verified"):
            assert z[k] is False

@pytest.mark.parametrize("v",["__import__('os')","2**100","2/0","0001",True,1.0,"1e3","[1,2]"])
def test_math_parser_refuses_untrusted_expressions(v):
    assert evaluate("quadratic_discriminant",{"a":v,"b":1,"c":1})["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("a,b",product(range(0,20),repeat=2))
def test_agm_400_nonnegative_exact_cases(a,b):
    v=do("agm_squared_witness",{"a":a,"b":b})
    assert v["squared_gap"]==Q((a-b)**2)
    assert v["valid"]
    assert v["equality"]==(a==b)

@pytest.mark.parametrize("q,n",product([-3,-2,-1,0,1,2,3],range(1,18)))
def test_geometric_sum_all_q_branches(q,n):
    v=do("geometric_sum",{"first":2,"q":q,"n":n})
    assert v["direct"]==v["closed"]
    assert v["used_nonzero_denominator"]==(q!=1)

@pytest.mark.parametrize("a,b,c",product(range(-5,6),range(-3,4),range(-3,4)))
def test_quadratic_integer_discriminant_property(a,b,c):
    if a==0:
        assert evaluate("quadratic_discriminant",{"a":a,"b":b,"c":c})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:
        v=do("quadratic_discriminant",{"a":a,"b":b,"c":c})
        d=b*b-4*a*c
        assert v["discriminant"]==d
        assert v["distinct_real_roots"]==(2 if d>0 else 1 if d==0 else 0)

@pytest.mark.parametrize("a,b",product(range(-7,8),range(-7,8)))
def test_inequality_sign_reversal_negative_finite_grid(a,b):
    result=evaluate("strict_inequality_scale",{"a":a,"b":b,"multiplier":-3})
    if a<b:
        assert result["status"]=="VERIFIED_FINITE_INSTANCE"
        assert result["witness"]["left"]>result["witness"]["right"]
    else:
        assert result["status"]=="CONDITIONS_NOT_ESTABLISHED"

@pytest.mark.parametrize("a,b",product(range(-5,6),range(-5,6)))
def test_complex_division_finite_grid_nonzero(a,b):
    if a==0 and b==0:
        assert evaluate("complex_division",{"a":1,"b":2,"c":a,"d":b})["status"]=="CONDITIONS_NOT_ESTABLISHED"
    else:
        w=do("complex_division",{"a":1,"b":2,"c":a,"d":b})
        real,imag=w["real"],w["imag"]
        assert real*a-imag*b==1
        assert real*b+imag*a==2

@pytest.mark.parametrize("values",list(product([False,True],repeat=5)))
def test_quantifier_finite_de_morgan_truth_table(values):
    v=do("finite_quantifier",{"predicate_values":list(values)})
    assert v["not_forall"]==v["exists_not"]
    assert v["forall"]==all(values)

def test_unsolved_student_essay_is_never_marked_verified():
    z=evaluate("some student free-form 3-step proof",{"text":"凭感觉此式正确"})
    assert z["status"]=="CONDITIONS_NOT_ESTABLISHED"
    assert z["complete_theorem_certified"] is False
    assert z["student_step_verified"] is False
