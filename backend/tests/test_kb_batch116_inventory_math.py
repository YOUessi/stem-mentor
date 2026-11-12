"""Batch116: whole-excerpt provenance scope, zero-authority gates, exact boundary cases."""
from copy import deepcopy
from pathlib import Path
import sys
import json
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "backend")]
import build_kb_batch116_inventory as S
import build_kb_batch116_condition_audit as M

@pytest.fixture(scope="module")
def inventory():
    return S.inventory()

def test_machine_auditable_excerpt_only(inventory):
    assert inventory["source_extent"] == "PARTIAL_PRINTED_PAGES_13_TO_73_NOT_ENTIRE_STANDARD"
    assert inventory["source_page_count"] == 61
    assert inventory["full_original_pdf_physical_pages"] == 188
    assert inventory["physical_pages_outside_legacy_61_excerpt"] == 127
    assert inventory["whole_pdf_pages_provenance_fingerprinted"] == 188
    assert inventory["structure_reviewed_count"] == 18
    assert inventory["structure_unreviewed_count"] == 43
    assert len(inventory["unreviewed_printed_pages"]) == 43
    assert inventory["teacher_fully_atomized_pages"] == 0
    assert inventory["teacher_approvals"] == inventory["student_authority_releases"] == 0
    assert inventory["known_outside_extent"]
    assert set(inventory["seven_track_official_atom_denominators"]) == set(S.TRACKS)
    assert all(n is None for n in inventory["seven_track_official_atom_denominators"].values())
    assert all(v is None for v in inventory["seven_track_certified_coverage"].values())

@pytest.mark.parametrize("i", range(188))
def test_every_physical_pdf_page_has_provenance_not_atom_authority(i):
    full=json.loads(S.FULL_MANIFEST.read_text())
    row=full["pages"][i]
    assert row["pdf_page_index"]==i and len(row["pdfkit_utf8_sha256"])==64
    assert row["has_extractable_text"] is True
    assert row["legacy_61_page_excerpt"] is (20<=i<=80)
    assert all("text" not in k.lower() or k in ("has_extractable_text",) for k in row)

@pytest.mark.parametrize("change", ("missing_page","duplicate_page","falsified_sha","injected_content","fake_pdf_count","false_legacy_extent","fake_source_sha"))
def test_full_pdf_provenance_forgery_rejected(change):
    full=json.loads(S.FULL_MANIFEST.read_text())
    if change=="missing_page":full["pages"].pop()
    elif change=="duplicate_page":full["pages"][100]=full["pages"][99]
    elif change=="falsified_sha":full["pages"][20]["pdfkit_utf8_sha256"]="0"*64
    elif change=="injected_content":full["pages"][100]["text"]="copied copyrighted text"
    elif change=="fake_pdf_count":full["pdf_page_count"]=61
    elif change=="false_legacy_extent":full["pages"][110]["legacy_61_page_excerpt"]=True
    elif change=="fake_source_sha":full["pdf_sha256"]="0"*64
    with pytest.raises(ValueError):S.inventory(full_manifest=full)

@pytest.mark.parametrize("p", range(13,74))
def test_each_source_page_attested_without_fabricated_certification(inventory,p):
    row=inventory["pages"][p-13]
    assert row["printed_page"]==p and row["pdf_page_index"]==p+7
    assert len(row["pdfkit_text_sha256"])==64
    assert row["source_group_hint"] and row["track_hint"]
    assert row["complete_teacher_atomization"] is False
    assert row["official_atom_count"] is None
    assert row["teacher_approval_record"] is None
    assert row["authoritative_student_release"] is False
    assert bool(row["prior_structure_review_artifact"]) == (row["structure_review_status"]=="PROVISIONAL_STRUCTURAL_REVIEW")

@pytest.mark.parametrize("p", (35,51,69,73))
def test_manual_visual_and_track_boundaries(inventory,p):
    row=inventory["pages"][p-13]
    assert len(row["manual_visual_review_flags"])>=1
    if p in (51,69):assert row["track_hint"]=="MULTI_TRACK_TRANSITION"
    if p==73:assert row["track_hint"]=="ELECTIVE_D"

def test_local_source_verified_on_mac():
    if not S.PDF.is_file():pytest.skip("SHA-locked licensed source only exists on authorized Mac")
    assert S.inventory(verify_local_source=True)["source_page_count"]==61

@pytest.mark.parametrize("tamper", ("duplicate","missing","pdf_index","sha","forged_denominator",
                                     "forged_review","track_overlap","track_gap","track_switch","wrong_pdf_sha"))
def test_fake_source_or_approval_rejected(tamper, monkeypatch):
    reg=json.loads(S.REGISTRY.read_text())
    pages=deepcopy(reg["pages"])
    groups=list(S.GROUPS)
    kwargs={}
    if tamper=="duplicate":pages[-1]=pages[0]
    elif tamper=="missing":pages.pop()
    elif tamper=="pdf_index":pages[0]["pdf_page_index"]+=1
    elif tamper=="sha":pages[0]["pdfkit_text_sha256"]="0"*64
    elif tamper=="forged_denominator":kwargs["denominators"]={t:1 for t in S.TRACKS}
    elif tamper=="forged_review":kwargs["teacher_approvals"]=1
    elif tamper=="track_overlap":groups[1]=(14,18,"COMPULSORY","overlap")
    elif tamper=="track_gap":groups[1]=(16,18,"COMPULSORY","gap")
    elif tamper=="track_switch":groups[-1]=(70,73,"ELECTIVE_E","false_track")
    elif tamper=="wrong_pdf_sha":
        reg["official_pdf_sha256"]="0"*64
        monkeypatch.setattr(S,"PDF_SHA","0"*64)
    kwargs.update({"source_pages":pages, "groups":groups})
    with pytest.raises(ValueError):
        S.inventory(**kwargs)

def test_generation_is_frozen_and_no_raw_copyright(inventory):
    assert S.OUT.read_text()==S.render(inventory)
    assert S.QUEUE.read_text()==S.review_queue(inventory)
    assert "copyright_source_text" not in S.OUT.read_text()
    assert "188个物理PDF页" in S.QUEUE.read_text()

def test_all_exact_cases_are_explicitly_noncertifying():
    a=M.audit()
    assert a["case_count"]==28
    assert a["positive_cases"]==a["negative_cases"]==28
    assert a["universal_proof_certificates"]==0 and a["teacher_approvals"]==0
    assert a["student_free_text_certificates"]==0
    assert len({r["id"] for r in a["cases"]})==28
    assert all(r["math_validation_status"]=="FINITE_EXACT_CASE_ONLY" and
               not r["general_proof_certified"] and not r["teacher_approved"]
               for r in a["cases"])
    assert M.DEST.read_text()==json.dumps(a,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"

@pytest.mark.parametrize("i", range(28))
def test_each_positive_exact_witness(i):
    name,_,_,yes,_=M.CASES[i]
    assert bool(yes()), name

@pytest.mark.parametrize("i", range(28))
def test_each_negative_boundary_witness(i):
    name,_,_,_,no=M.CASES[i]
    assert bool(no()), name

@pytest.mark.parametrize("i", range(28))
def test_tampered_math_witness_is_rejected(i):
    cases=list(M.CASES)
    c=list(cases[i]);c[4]=lambda: False;cases[i]=tuple(c)
    with pytest.raises(ValueError,match="exact witness failed"):
        M.audit(cases)

def test_duplicate_math_case_rejected():
    cases=list(M.CASES)
    cases[-1]=cases[0]
    with pytest.raises(ValueError,match="duplicate IDs"):
        M.audit(cases)
