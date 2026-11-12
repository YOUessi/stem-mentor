"""Batch107 source provenance and independent exact math negative tests."""
from __future__ import annotations
from copy import deepcopy
import json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch107_source_authoring import CANDIDATES,PARTITIONS
import build_kb_batch107_source as B
from app.kb_batch107_math import check


@pytest.fixture(scope="module")
def report():
    return B.build()


def test_source_page_partitions_conserve_every_pdfkit_line(report):
    assert report["pages"]==[17,54]
    assert report["page_line_counts"]=={"17":27,"54":27}
    assert report["full_source_line_partition_count"]==16
    for p in (17,54):
        coverage=[line for r in report["source_line_partitions"] if r["page"]==p
                  for line in range(r["start"],r["end"]+1)]
        assert coverage==list(range(1,28))


def test_no_official_denominator_or_approval(report):
    assert len(report["candidates"])==23
    assert report["counts_by_seven_tracks"]["COMPULSORY"]==11
    assert report["counts_by_seven_tracks"]["ELECTIVE_A"]==12
    assert len(report["official_atom_denominators_by_seven_tracks"])==7
    assert set(report["official_atom_denominators_by_seven_tracks"].values())=={None}
    assert report["whole_source_page_teacher_atomizations"]==0
    assert report["teacher_approved"]==0
    assert report["student_authoritative_releases"]==0
    assert report["formal_universal_proof_certificates"]==0


@pytest.mark.parametrize("index",range(23))
def test_every_candidate_source_and_math_witness(index,report):
    row=report["candidates"][index]
    author=CANDIDATES[index]
    assert row["title"]==author["title"]
    assert row["page"]==author["page"]
    assert row["start"]==author["start"]
    assert row["end"]==author["end"]
    assert row["source_pdf_sha256"]==report["source_pdf_sha256"]
    assert len(row["source_page_pdfkit_sha256"])==64
    assert row["track"]==("COMPULSORY" if row["page"]==17 else "ELECTIVE_A")
    assert row["teacher_review_status"]=="REVIEW_PENDING"
    assert row["official_atom_id"] is None
    assert row["student_authoritative_release"] is False
    assert row["is_general_math_proof"] is False
    math=check(author["oracle_key"])
    assert row["bounded_math_check"]==math
    assert math["finite_exact_positive_passed"] and math["invalid_generalization_rejected"]
    assert not math["arbitrary_student_step_verified"]
    assert not math["universal_proof_certified"]


@pytest.mark.parametrize("index",range(23))
def test_reject_forged_authority_any_candidate(index):
    altered=deepcopy(CANDIDATES)
    altered[index]["teacher_review_status"]="APPROVED"
    with pytest.raises(ValueError,match="schema drift"):
        B.build(candidates=altered)


@pytest.mark.parametrize("index",range(23))
def test_reject_out_of_bounds_sources(index):
    altered=deepcopy(CANDIDATES)
    altered[index]["end"]=99
    with pytest.raises(ValueError,match="out-of-range"):
        B.build(candidates=altered)


@pytest.mark.parametrize("index",range(23))
def test_reject_oracle_key_substitution_by_duplicate(index):
    altered=deepcopy(CANDIDATES)
    altered[index]["oracle_key"]=CANDIDATES[(index+1)%23]["oracle_key"]
    with pytest.raises(ValueError,match="duplicate oracle"):
        B.build(candidates=altered)


@pytest.mark.parametrize("index",range(23))
def test_reject_thin_math_conditions(index):
    altered=deepcopy(CANDIDATES)
    altered[index]["mathematical_preconditions"]="P"
    with pytest.raises(ValueError,match="thin mathematics"):
        B.build(candidates=altered)


@pytest.mark.parametrize("modification",["missing","overlap","reordered","wrong_page","missing_tail"])
def test_partition_completeness_failure(modification):
    changed=deepcopy(PARTITIONS)
    if modification=="missing":
        changed[17].pop(0)
    elif modification=="overlap":
        changed[17].insert(1,(1,2,"DUPLICATE_HEADER"))
    elif modification=="reordered":
        changed[54][0],changed[54][1]=changed[54][1],changed[54][0]
    elif modification=="wrong_page":
        changed[99]=changed.pop(54)
    else:
        changed[54][-1]=(27,26,"BAD_FOOTER")
    with pytest.raises(ValueError):
        B.build(partitions=changed)


@pytest.mark.parametrize("kind",["unknown","None","False","positive_number"])
def test_unsupported_student_oracle_must_not_pass(kind):
    arg={"unknown":"LLM_APPROVED","None":None,"False":False,"positive_number":1}[kind]
    with pytest.raises(ValueError):
        check(arg)


def test_deterministic_report_and_source_original_vs_official_text(report):
    assert B.OUT.read_text(encoding="utf8")==B.canonical(report)
    assert B.MARKDOWN.read_text(encoding="utf8")==B.markdown(report)
    assert report["candidates"][0]["source_partition_type"]=="CROSS_PAGE_MATH_CONTINUATION"
    # The only teaching-note candidate must be identified as non-atomic guidance.
    row=next(x for x in report["candidates"] if x["oracle_key"]=="singleton")
    assert row["source_partition_type"]=="NON_ATOMIC_TEACHING_GUIDANCE"
    assert row["teacher_review_status"]=="REVIEW_PENDING"


def test_reject_candidate_spanning_two_source_sections():
    altered=deepcopy(CANDIDATES)
    altered[10]["start"]=16
    with pytest.raises(ValueError,match="straddle"):
        B.build(candidates=altered)


def test_reject_wrong_pdf_page_fingerprint(tmp_path,monkeypatch):
    meta=json.loads(B.META.read_text(encoding="utf8"))
    next(x for x in meta["pages"] if x["printed_page"]==54)["pdfkit_text_sha256"]="0"*64
    path=tmp_path/"source.json"
    path.write_text(json.dumps(meta),encoding="utf8")
    monkeypatch.setattr(B,"META",path)
    # Without raw-text source validation the fingerprint registry can be
    # corrupted and must be caught by version-control provenance SHA.
    # This test intentionally uses local verify mode where PDF text is known.
    with pytest.raises(ValueError,match="source fingerprint registry drift"):
        B.build(verify_local_source=True)


@pytest.mark.parametrize("index",range(23))
def test_in_bounds_wrong_clause_source_range_rejected(index):
    changed=deepcopy(CANDIDATES)
    item=changed[index]
    # Preserve legal page but alter the exact source clause attachment.
    if item["start"]<item["end"]:item["end"]=item["start"]
    else:item["end"]+=1 if item["end"]<27 else -1
    with pytest.raises(ValueError):
        B.build(candidates=changed)


def test_reject_same_math_title_with_distinct_keys():
    changed=deepcopy(CANDIDATES)
    changed[1]["title"]=changed[0]["title"]
    with pytest.raises(ValueError,match="duplicate title"):
        B.build(candidates=changed)
