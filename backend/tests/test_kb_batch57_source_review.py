"""Batch57 78 source pointers + 9 bounded exact mathematical witness families."""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import sys

import pytest
from app.kb_batch57_exact_witnesses import exact_witness, ConditionsNotEstablished, FIELDS

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch57_source_review as G

AUDIT=G.build()
ROWS=AUDIT["rows"]
VALID={
    "unique_plane_from_points":{"p":(0,0,0),"q":(1,0,0),"r":(0,1,0)},
    "line_plane_relation":{"plane_normal":(0,0,1),"plane_offset":0,
                         "line_point":(0,0,1),"line_direction":(1,0,0)},
    "nonzero_vector_orthogonality":{"u":(3,4),"v":(-4,3)},
    "triangle_cosine_law":{"side_a":3,"side_b":4,"opposite_c":5},
    "complex_exact_division":{"real_a":2,"imag_a":4,"real_b":1,"imag_b":-1},
    "classical_equiprobable_event":{"universe":(0,1,2,3),"event":(1,3),"equiprobable":True},
    "binary_joint_independence":{"p11":Fraction(1,4),"p10":Fraction(1,4),
                                 "p01":Fraction(1,4),"p00":Fraction(1,4)},
    "stratified_weighted_mean":{"population_sizes":[1,3],
                                "sample_means":[10,20],"random_design_confirmed":False},
    "sample_variance_conventions":{"values":[1,3,5]},
}

def test_partial_source_audit_never_certifies_official_denominators():
    assert AUDIT["new_source_spans"]==78
    assert AUDIT["batch56_source_spans_kept_separately"]==52
    assert AUDIT["combined_nonunique_source_spans"]==130
    assert AUDIT["pages_newly_partially_annotated"]==list(range(25,37))
    assert AUDIT["pages_partially_annotated_combined"]==list(range(15,37))
    assert AUDIT["starred_optional_not_exam"]==3
    assert AUDIT["source_image_gaps_not_interpreted"]==2
    assert AUDIT["teacher_approved"]==AUDIT["student_published"]==0
    assert AUDIT["project_editorial_candidates_not_official_atoms"]==313
    assert AUDIT["unverified_historical_proof_steps"]==538
    assert AUDIT["unresolved_math_conflicts"]==10
    assert AUDIT["full_teacher_reviewed_page_atomizations"]==0
    assert set(AUDIT["official_atomic_denominator"])==set(G.TRACKS)
    assert all(v is None for v in AUDIT["official_atomic_denominator"].values())

@pytest.mark.parametrize("i",range(78))
def test_each_span_attested_to_exact_page_not_promoted(i):
    r=ROWS[i]; snap=G.load(G.SNAP)
    assert snap["attestations"][r["source_span_id"]]==r["source_span_pdfkit_sha256"]
    assert r["source_pdf_sha256"]==G.PDF_SHA
    assert r["pdf_page_index"]==r["printed_page"]+7
    assert r["teacher_review"]=="REVIEW_PENDING"
    assert r["full_page_human_review"]=="PENDING"
    assert r["cross_page_mathematical_deduplication"]=="PENDING"
    assert r["official_atom_certified"] is False
    assert r["mathematical_scope_equivalence_certified"] is False
    assert r["formal_general_proof_certified"] is False
    assert r["student_publishable"] is False

@pytest.mark.parametrize("p,n",sorted(G.EXPECT.items()))
def test_page_evidence_bounded_and_distinct(p,n):
    rows=[r for r in ROWS if r["printed_page"]==p]
    assert len(rows)==n
    assert len({r["source_span_id"] for r in rows})==n

@pytest.mark.parametrize("page",[27,29])
def test_optional_star_not_exam_and_never_automatic_atom(page):
    items=[r for r in ROWS if r["printed_page"]==page and r["starred_optional"]]
    assert len(items)==(2 if page==27 else 1)
    assert all(r["exam_requirement_status"]=="EXPLICITLY_OPTIONAL_NOT_EXAM"
               and not r["official_atom_certified"] for r in items)

@pytest.mark.parametrize("page",[34,35])
def test_unreadable_diagram_source_is_explicitly_unverified(page):
    items=[r for r in ROWS if r["printed_page"]==page
           and r["source_kind"]=="PDFKIT_UNREADABLE_FIGURE"]
    assert len(items)==1
    assert items[0]["semantic_source_readability"]=="VISUAL_REVIEW_REQUIRED"
    assert items[0]["exam_requirement_status"]=="NOT_A_CONTENT_ATOM"

def test_selective_track_boundary_is_not_compulsory_atom():
    boundary=next(x for x in ROWS if x["source_kind"]=="TRACK_BOUNDARY")
    assert (boundary["printed_page"],boundary["track"])==(36,"SELECTIVE_COMPULSORY")
    assert boundary["exam_requirement_status"]=="NOT_A_CONTENT_ATOM"
    assert not boundary["official_atom_certified"]

def test_source_content_is_not_copyright_pdf_text():
    assert all(19<=len(x["original_editorial_paraphrase"])<=150 for x in ROWS)
    assert not AUDIT["source_passages_or_pdf_committed"]
    assert not G.load(G.SNAP)["readable_image_semantics_attested"]

def test_tsv_and_json_regeneration_reproducible():
    assert G.OUTPUT.read_text(encoding="utf8")==json.dumps(
        AUDIT,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    assert G.REPORT.read_text(encoding="utf8")==G.render(AUDIT)
    assert "官方知识原子分母" in G.render(AUDIT)

def test_duplicate_or_removed_span_is_rejected():
    rows=G.parse()
    rows[1]["line_start"]=rows[0]["line_start"]
    rows[1]["line_end"]=rows[0]["line_end"]
    with pytest.raises(ValueError,match="duplicate source span"): G.build(rows=rows)
    with pytest.raises(ValueError,match="partial source span inventory"):
        G.build(rows=G.parse()[:-1])

def test_star_optional_flag_and_extra_star_location_rejected():
    rows=G.parse()
    x=next(z for z in rows if z["source_kind"]=="OPTIONAL_STARRED")
    x["optional_flag"]="N"
    with pytest.raises(ValueError,match="optional-star"):G.build(rows=rows)
    rows=G.parse();rows[0]["source_kind"]="OPTIONAL_STARRED";rows[0]["optional_flag"]="Y"
    with pytest.raises(ValueError,match="scope mismatch"):G.build(rows=rows)

def test_no_readable_diagram_semantics_can_be_forged():
    rows=G.parse()
    x=next(z for z in rows if z["source_kind"]=="PDFKIT_UNREADABLE_FIGURE")
    x["line_start"]=2
    with pytest.raises(ValueError,match="figure evidence"):G.build(rows=rows)
    snap=G.load(G.SNAP);snap["readable_image_semantics_attested"]=True
    with pytest.raises(ValueError,match="image semantics forged"):G.build(snapshot=snap)

def test_track_promotion_and_editorial_approval_rejected():
    rows=G.parse();rows[0]["track"]="SELECTIVE_COMPULSORY"
    with pytest.raises(ValueError,match="wrong curriculum track"):G.build(rows=rows)
    old=G.load(G.OLD);old["official_atomic_denominator"]["COMPULSORY"]=78
    with pytest.raises(ValueError,match="wrongly promoted"):G.build(old=old)
    overlay=G.load(G.OVERLAY);overlay["rows"][4]["teacher_approved"]=True
    with pytest.raises(ValueError,match="forged teacher approval"):G.build(overlay=overlay)
    risk=G.load(G.RISK);risk["conflicts_resolved"]=1
    with pytest.raises(ValueError,match="risk inventory drift"):G.build(risk=risk)

def test_pdf_and_span_provenance_negative(tmp_path):
    fake=tmp_path/"syllabus.pdf";fake.write_bytes(b"%PDF fake source")
    with pytest.raises(ValueError,match="PDF absent or SHA mismatch"):
        G.verify_original(tmp_path,fake,G.parse(),G.load(G.PAGE))
    snap=G.load(G.SNAP);snap["attestations"].pop(next(iter(snap["attestations"])))
    with pytest.raises(ValueError):G.build(snapshot=snap)
    pages=G.load(G.PAGE);pages["pages"][0]["pdf_page_index"]=999
    # Actual page mutated to a referenced page to force bound source-index validation.
    pages["pages"][12]["pdf_page_index"]=999
    with pytest.raises(ValueError,match="wrong PDF index"):G.build(pages=pages)

@pytest.mark.parametrize("i",[0,2,17,20,28,35,43,50,58,64,71,74,77])
def test_student_retrieval_and_tutor_never_publish_unapproved_source(i):
    from app.deep_retrieval import student_evidence_lookup
    from app.model_tutor_draft import draft_next_question
    query=ROWS[i]["candidate_id"]
    got=student_evidence_lookup(query,limit=3)
    assert got["status"]=="NO_APPROVED_EVIDENCE"
    assert got["candidates"]==[] and not got["teacher_solution_exposed"]
    draft=draft_next_question(query,mode="GUIDE",help_requested=True,
           consent_to_cloud=True,operator_scope="EDITOR_LOCAL",
           provider_url="https://api.openai.com/v1/chat/completions",
           provider_model="offline-test-do-not-call")
    assert draft.status=="BLOCKED" and draft.reason=="NO_APPROVED_MATH_EVIDENCE"
    assert not draft.model_called and not draft.student_visible

@pytest.mark.parametrize("op",list(FIELDS))
def test_exact_math_witnesses_never_pretend_formal_proof(op):
    r=exact_witness(op,**VALID[op])
    assert r["status"]=="FINITE_EXACT_CASE_ONLY"
    assert r["scope"]=="NOT_FORMAL_GENERAL_PROOF"
    assert r["teacher_approved"] is False
    assert r["student_solution_verified"] is False
    assert r["official_atom_certified"] is False
    with pytest.raises(ConditionsNotEstablished):
        exact_witness(op,**(VALID[op]|{"teacher_approved":True}))
    for k in FIELDS[op]:
        with pytest.raises(ConditionsNotEstablished):
            exact_witness(op,**{a:b for a,b in VALID[op].items() if a!=k})

@pytest.mark.parametrize("bad",[
    ((0,0,0),(1,1,1),(2,2,2)),((1,1,1),(1,1,1),(0,0,1)),
    ((0,0,0),(0,0,0),(0,0,0))
])
def test_plane_requires_three_noncollinear_points(bad):
    with pytest.raises(ConditionsNotEstablished):
        exact_witness("unique_plane_from_points",p=bad[0],q=bad[1],r=bad[2])

def test_line_plane_three_distinct_relations_and_zero_direction():
    base=dict(plane_normal=(0,0,1),plane_offset=0,line_direction=(1,0,0))
    assert exact_witness("line_plane_relation",**base,line_point=(0,0,1))["result"]["relation"]=="PARALLEL_DISJOINT"
    assert exact_witness("line_plane_relation",**base,line_point=(0,0,0))["result"]["relation"]=="CONTAINED"
    assert exact_witness("line_plane_relation",**(base|{"line_direction":(0,0,1)}),
                         line_point=(0,0,1))["result"]["relation"]=="INTERSECTS"
    with pytest.raises(ConditionsNotEstablished):
        exact_witness("line_plane_relation",**(base|{"line_direction":(0,0,0)}),
                      line_point=(0,0,0))

@pytest.mark.parametrize("a,b",[((1,0),(0,0)),((0,0),(0,1)),((0,0),(0,0))])
def test_zero_vectors_do_not_prove_perpendicular(a,b):
    with pytest.raises(ConditionsNotEstablished):
        exact_witness("nonzero_vector_orthogonality",u=a,v=b)

@pytest.mark.parametrize("a,b,c",[(1,2,3),(1,1,2),(0,3,4),(-1,2,2),(2,2,5)])
def test_cosine_rule_rejects_degenerate_triangle(a,b,c):
    with pytest.raises(ConditionsNotEstablished):
        exact_witness("triangle_cosine_law",side_a=a,side_b=b,opposite_c=c)

def test_law_cosine_exact_and_complex_division_roundtrip():
    r=exact_witness("triangle_cosine_law",**VALID["triangle_cosine_law"])["result"]
    assert r["cos_opposite_c"]==0 and r["side_sum_check"] and r["SSA_ambiguity_not_resolved"]
    q=exact_witness("complex_exact_division",**VALID["complex_exact_division"])["result"]
    assert q["quotient_real"]==-1 and q["quotient_imag"]==3 and q["multiplied_back"]
    with pytest.raises(ConditionsNotEstablished):
        exact_witness("complex_exact_division",real_a=1,imag_a=1,real_b=0,imag_b=0)

@pytest.mark.parametrize("univ,event,equal",[
    ([1,2],[1],False),([1,1],[1],True),([1,2],[3],True),
    ([True,1],[1],True),([],[],True),([1,2],[1,1],True)
])
def test_classical_model_must_verify_sample_space_and_equiprobable(univ,event,equal):
    with pytest.raises(ConditionsNotEstablished):
        exact_witness("classical_equiprobable_event",universe=univ,event=event,
                      equiprobable=equal)

def test_mutually_exclusive_is_not_always_independent():
    mutually_exclusive=exact_witness("binary_joint_independence",
        p11=0,p10=Fraction(1,2),p01=Fraction(1,2),p00=0)["result"]
    assert mutually_exclusive["mutually_exclusive"] and not mutually_exclusive["independent"]
    independent=exact_witness("binary_joint_independence",**VALID["binary_joint_independence"])["result"]
    assert independent["independent"] and not independent["mutually_exclusive"]
    with pytest.raises(ConditionsNotEstablished):
        exact_witness("binary_joint_independence",p11=1,p10=1,p01=0,p00=0)

def test_sampling_weights_and_variance_denominator():
    r=exact_witness("stratified_weighted_mean",**VALID["stratified_weighted_mean"])["result"]
    assert r["weighted_estimate"]==Fraction(35,2)
    assert r["weights"]==(Fraction(1,4),Fraction(3,4))
    assert not r["unbiasedness_certified"]
    with pytest.raises(ConditionsNotEstablished):
        exact_witness("stratified_weighted_mean",population_sizes=[0,1],sample_means=[2,3],
                      random_design_confirmed=False)
    v=exact_witness("sample_variance_conventions",values=[1,3,5])["result"]
    assert v["mean"]==3 and v["population_denominator_n"]==Fraction(8,3)
    assert v["sample_denominator_n_minus_1"]==4

@pytest.mark.parametrize("op",list(FIELDS))
def test_unverified_student_free_text_never_accepted(op):
    with pytest.raises(ConditionsNotEstablished):
        exact_witness(op,student_free_text="trivial / QED")

@pytest.mark.parametrize("op,field",[
    ("unique_plane_from_points","p"),("line_plane_relation","plane_offset"),
    ("nonzero_vector_orthogonality","u"),("triangle_cosine_law","side_a"),
    ("complex_exact_division","real_a"),("binary_joint_independence","p00"),
    ("stratified_weighted_mean","sample_means"),("sample_variance_conventions","values")
])
def test_float_input_rejected(op,field):
    args=deepcopy(VALID[op])
    if type(args[field]) in (tuple,list):
        xs=list(args[field]);xs[0]=0.5;args[field]=xs
    else:args[field]=0.5
    with pytest.raises(ConditionsNotEstablished):exact_witness(op,**args)
