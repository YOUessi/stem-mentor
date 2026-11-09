"""K00/K01 full-page anchor inventory: source attestation, fail-closed status,
no bogus official denominator, deterministic reports, and gap queue tests."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch61_requirement_anchors as A

REG=A.load(A.REGISTRY)
AUDIT=A.build()
ROWS=REG["rows"]

def test_61_page_scope_and_honest_denominator():
    assert AUDIT["source_pages_total"]==61
    assert AUDIT["earlier_partial_source_leads"]==344
    assert AUDIT["candidate_anchor_count"]==len(ROWS)
    assert AUDIT["candidate_anchor_count"]>100
    assert AUDIT["candidate_anchors_without_partial_lead"]>0
    assert AUDIT["full_page_teacher_review_completed"]==0
    assert AUDIT["teacher_approved"]==AUDIT["student_published"]==0
    assert AUDIT["official_atomic_denominator"]=={t:None for t in A.TRACKS}
    assert AUDIT["candidate_anchors_are_not_official_atoms"] is True
    assert AUDIT["source_lead_is_not_equivalent_to_content_coverage"] is True
    assert AUDIT["manual_unenumerated_and_visual_requirements_still_pending"] is True
    assert AUDIT["conflict_count_still_unadjudicated"]==10
    assert AUDIT["historical_unverified_proof_steps"]==538

def test_full_page_inventory_not_a_single_page_placeholder():
    assert [p["printed_page"] for p in AUDIT["pages"]]==list(range(13,74))
    assert sum(p["heuristic_clause_anchors"] for p in AUDIT["pages"])==len(ROWS)
    assert sum(len(p["anchors_without_partial_source_lead"]) for p in AUDIT["pages"])==AUDIT["candidate_anchors_without_partial_lead"]
    assert sum(p["source_leads"] for p in AUDIT["pages"])==344
    assert AUDIT["pages_with_control_code_evidence"]
    assert 35 in AUDIT["pages_with_control_code_evidence"]

@pytest.mark.parametrize("page",range(13,74))
def test_each_page_retained_with_separate_pending_evidence(page):
    p=AUDIT["pages"][page-13]
    assert p["printed_page"]==page
    assert p["line_count"]==REG["page_line_counts"][str(page)]
    assert p["control_scalar_count"]==REG["page_control_scalar_counts"][str(page)]
    assert p["source_leads"]>=1
    assert p["full_page_human_review"]=="PENDING"
    assert p["mathematical_equivalence_audit"]=="PENDING"
    assert p["potentially_unreadable_figure_or_formula"]==(p["control_scalar_count"]>0)
    assert all(1<=line<=p["line_count"] for line in p["anchors_without_partial_source_lead"])

@pytest.mark.parametrize("index",range(len(ROWS)))
def test_every_candidate_explicitly_noncertified(index):
    source=ROWS[index]
    entry=AUDIT["anchors"][index]
    assert entry["printed_page"]==source["printed_page"]
    assert entry["pdfkit_line"]==source["pdfkit_line"]
    assert entry["source_line_sha256"]==source["source_line_sha256"]
    assert entry["teacher_review"]=="REVIEW_PENDING"
    assert entry["duplicate_equivalence_review"]=="PENDING"
    assert entry["certified_official_atom"] is False
    assert entry["full_page_review_completed"] is False
    assert entry["student_publishable"] is False
    assert entry["official_denominator_membership"]=="UNDETERMINED"
    assert entry["knowledge_atom_completeness"]=="NOT_EVALUATED"
    assert entry["has_partially_located_source_lead"]==bool(entry["partial_source_lead_ids"])
    assert all(A.SPAN_RE.fullmatch(k) for k in entry["partial_source_lead_ids"])

@pytest.mark.parametrize("kind",A.MARKERS)
def test_every_supported_anchor_kind_is_explicit(kind):
    assert any(e["kind"]==kind for e in ROWS)

@pytest.mark.parametrize("raw,expected",[
    ("１．集合","MAJOR_NUMBER"),
    ("６数列","MAJOR_NUMBER"),
    ("（ １ ）求函数","SUBCLAUSE_NUMBER"),
    ("(2)推导","SUBCLAUSE_NUMBER"),
    ("①理解定义","CIRCLED_ITEM"),
    ("【 内容要求】","SECTION_LABEL"),
    ("【 学业要求】","SECTION_LABEL"),
    ("【 教学提示】","SECTION_LABEL"),
    ("这是一个跨行的课程要求",None),
    ("Ａ类课程是选修",None),
    ("ｘ²＋１",None),
])
def test_marker_classification_and_unenumerated_caution(raw,expected):
    assert A.marker(raw)==expected

@pytest.mark.parametrize("page,line,track",[
    (13,1,"COMPULSORY"),(36,1,"COMPULSORY"),
    (37,1,"SELECTIVE_COMPULSORY"),(50,1,"SELECTIVE_COMPULSORY"),
    (51,1,"ELECTIVE_GENERAL"),(51,20,"ELECTIVE_A"),
    (57,15,"ELECTIVE_A"),(57,16,"ELECTIVE_B"),
    (64,9,"ELECTIVE_B"),(64,10,"ELECTIVE_C"),
    (69,5,"ELECTIVE_C"),(69,6,"ELECTIVE_D"),
    (73,12,"ELECTIVE_D"),(73,13,"ELECTIVE_E"),
])
def test_cross_page_elective_scope_cutoffs(page,line,track):
    assert A.track_for(page,line)==track

def test_output_replay_deterministic():
    assert A.OUT.read_text(encoding="utf-8")==A.canonical(AUDIT)
    assert A.MD.read_text(encoding="utf-8")==A.render(AUDIT)
    assert json.loads(A.OUT.read_text(encoding="utf-8"))==AUDIT

def test_source_files_cannot_be_substituted_by_editorial_count():
    assert len(A.leads())==344
    assert len({(p,a,b) for p,a,b,_ in A.leads()})==344
    assert len(REG["rows"])!=313
    assert all(v is None for v in AUDIT["official_atomic_denominator"].values())

@pytest.mark.parametrize("mutation",["approve","publish","certify","full_review","equivalence","wrong_sha",
                                       "duplicate","wrong_track","wrong_marker","wrong_page_index","extra_field"])
def test_anchor_privilege_and_provenance_forgery_rejected(mutation):
    bad=deepcopy(REG)
    row=bad["rows"][0]
    if mutation=="approve":row["teacher_review"]="APPROVED"
    elif mutation=="publish":row["student_publishable"]=True
    elif mutation=="certify":row["certified_official_atom"]=True
    elif mutation=="full_review":row["full_page_review_completed"]=True
    elif mutation=="equivalence":row["duplicate_equivalence_review"]="MATCH"
    elif mutation=="wrong_sha":row["source_line_sha256"]="a"*64
    elif mutation=="duplicate":bad["rows"][1]=deepcopy(row)
    elif mutation=="wrong_track":row["track_hint"]="ELECTIVE_E"
    elif mutation=="wrong_marker":row["kind"]="FORMALLY_PROVED"
    elif mutation=="wrong_page_index":row["pdf_page_index"]=-1
    elif mutation=="extra_field":row["teacher_signature"]="fabricated"
    with pytest.raises(ValueError):
        A.validate(bad)

@pytest.mark.parametrize("mutation",["missing_page","zero_lines","negative_controls","wrong_pdf","copied_text","few_anchors","wrong_order"])
def test_global_integrity_fail_closed(mutation):
    bad=deepcopy(REG)
    if mutation=="missing_page":del bad["page_line_counts"]["13"]
    elif mutation=="zero_lines":bad["page_line_counts"]["13"]=0
    elif mutation=="negative_controls":bad["page_control_scalar_counts"]["35"]=-1
    elif mutation=="wrong_pdf":bad["source_pdf_sha256"]="a"*64
    elif mutation=="copied_text":bad["includes_copyright_passages"]=True
    elif mutation=="few_anchors":bad["rows"]=bad["rows"][:2]
    elif mutation=="wrong_order":bad["rows"][0],bad["rows"][1]=bad["rows"][1],bad["rows"][0]
    with pytest.raises(ValueError):
        A.validate(bad)

def test_false_positive_and_partial_coverage_illustrated():
    """A source lead overlapping a marker is *not* proof of underlying lesson coverage."""
    examples=[e for e in AUDIT["anchors"] if e["has_partially_located_source_lead"]]
    assert examples
    assert all(e["official_denominator_membership"]=="UNDETERMINED" for e in examples)
    missing=[e for e in AUDIT["anchors"] if not e["has_partially_located_source_lead"]]
    assert len(missing)==AUDIT["candidate_anchors_without_partial_lead"]
    assert all(e["partial_source_lead_ids"]==[] for e in missing)

def test_offline_generation_with_stale_lead_fails():
    broken=list(A.leads())
    broken[0]=(13,1,100000,"P013-L001-100000")
    with pytest.raises(ValueError,match="lead outside attested lines"):
        A.build(lead_rows=broken)

def test_untrusted_candidate_does_not_smuggle_real_student_data():
    forbidden={"student_name","student_id","student_solution","teacher_solution","student_email"}
    assert all(not (set(e)&forbidden) for e in AUDIT["anchors"])
    assert all(not (set(e)&forbidden) for e in REG["rows"])

def test_missing_or_mismatched_local_pdf_must_not_be_accepted(tmp_path):
    bad=tmp_path/"impostor.pdf"
    bad.write_bytes(b"not the official source")
    with pytest.raises(ValueError,match="PDF SHA mismatch"):
        A.extract(tmp_path,bad)

def test_seven_track_zero_preservation():
    counts=AUDIT["candidate_anchor_count_by_track_hint"]
    assert set(counts)==set(A.TRACKS)|{"ELECTIVE_GENERAL"}
    assert counts["ELECTIVE_E"]==0  # School-defined scope has no machine-identified anchor.
    assert counts["COMPULSORY"]>0 and counts["SELECTIVE_COMPULSORY"]>0
    assert sum(counts.values())==len(ROWS)

def test_queue_is_reproducible_and_excludes_already_partially_located_anchors():
    import csv,io
    actual=A.QUEUE.read_text(encoding="utf-8")
    assert actual==A.render_queue(AUDIT)
    queue=list(csv.DictReader(io.StringIO(actual)))
    assert len(queue)==AUDIT["candidate_anchors_without_partial_lead"]
    assert len({q["candidate_anchor_id"] for q in queue})==len(queue)
    assert all(q["review_state"]=="REVIEW_PENDING" and q["certified_atom"]=="False" for q in queue)
    assert all("NOT_PROOF_OF_CONTENT_GAP" in q["reason"] for q in queue)
    assert all(q["printed_page"].isdigit() for q in queue)

@pytest.mark.parametrize("index",range(AUDIT["candidate_anchors_without_partial_lead"]))
def test_each_unlinked_queue_record_has_pinned_local_coordinate(index):
    import csv,io
    queue=list(csv.DictReader(io.StringIO(A.QUEUE.read_text(encoding="utf-8"))))
    row=queue[index]
    p=int(row["printed_page"]); line=int(row["pdfkit_line"])
    candidates=[r for r in AUDIT["anchors"] if r["printed_page"]==p and r["pdfkit_line"]==line]
    assert len(candidates)==1
    candidate=candidates[0]
    assert candidate["partial_source_lead_ids"]==[]
    assert row["source_line_sha256"]==candidate["source_line_sha256"]
    assert row["triage_priority"] in ("P0","P1")
    assert row["track_hint"]==candidate["track_hint"]
