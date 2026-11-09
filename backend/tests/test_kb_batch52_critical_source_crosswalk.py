"""Batch52: K00 requirement triage from four critical syllabus pages; fail-closed.

No inferred official atom denominator, proof certification, teacher approval,
student publication, or source-level equivalence is permitted.
"""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location(
    "kb52_gate", ROOT/"scripts/build_kb_batch52_critical_requirement_crosswalk.py")
G=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)
PAGES=G.load(G.PAGES)
OVERLAY=G.load(G.OVERLAY)
BASE=G.load(G.B51)
RESULT=G.assemble()


def test_source_page_crosswalk_counts_and_identity():
    assert RESULT["source_pdf_sha256"] == G.PDF_SHA
    assert RESULT["by_page"] == {"34":8,"41":8,"50":5,"65":7}
    assert RESULT["new_triage_candidates"] == 28
    assert RESULT["without_same_page_editorial_link"] == 9
    assert RESULT["project_editorial_candidates_unchanged"] == 313
    assert RESULT["source_page35_other_7_split_candidates_not_duplicated"] == 7
    assert RESULT["teacher_approved"] == RESULT["student_published"] == 0
    assert all(v is None for v in RESULT["official_atomic_denominator"].values())
    assert len(RESULT["official_atomic_denominator"]) == 7


@pytest.mark.parametrize("index",range(28))
def test_each_paraphrase_is_original_source_tied_and_pending(index):
    row=RESULT["rows"][index]
    assert row["candidate_id"].startswith("KB52-")
    assert len(row["original_editorial_paraphrase"])>=20
    assert row["source_pdf_sha256"]==G.PDF_SHA
    assert row["pdf_page_index"]==row["printed_page"]+7
    src=next(p for p in PAGES["pages"] if p["printed_page"]==row["printed_page"])
    assert row["source_page_pdfkit_text_sha256"]==src["pdfkit_text_sha256"]
    assert row["source_section_triage"]==G.SECTION_BY_PAGE[row["printed_page"]]
    assert row["track"]==G.TRACK_BY_PAGE[row["printed_page"]]
    assert row["cross_page_deduplication"]=="PENDING"
    assert row["teacher_review"]=="REVIEW_PENDING"
    assert row["official_atom_certified"] is False
    assert row["mathematical_scope_certified"] is False
    assert row["student_publishable"] is False
    assert row["full_teacher_lesson_new"] is False
    assert row["source_passages_committed"] is False


@pytest.mark.parametrize("index",range(28))
def test_all_related_editorial_ids_are_only_discovery_not_certification(index):
    row=RESULT["rows"][index]
    links=row["related_editorial_ids_not_equivalence"]
    if links:
        assert row["linkage_status"]=="RELATED_SCOPE_UNVERIFIED"
    else:
        assert row["linkage_status"]=="NO_SAME_PAGE_EDITORIAL_LINK_UNVERIFIED"
    for eid in links:
        legacy=next(x for x in OVERLAY["rows"] if x["editorial_id"]==eid)
        assert legacy["printed_page"]==row["printed_page"]
        assert legacy["track"]==row["track"]
        assert legacy["official_clause_verified"] is False
        assert legacy["teacher_approved"] is False


@pytest.mark.parametrize("page,count",sorted(G.PAGE_COUNTS.items()))
def test_four_critical_source_pages_are_not_omitted(page,count):
    rows=[r for r in RESULT["rows"] if r["printed_page"]==page]
    assert len(rows)==count
    assert len({r["candidate_id"] for r in rows})==count
    assert all(r["teacher_review"]=="REVIEW_PENDING" for r in rows)


@pytest.mark.parametrize("tag",["excluded_middle","noncontradiction"])
@pytest.mark.parametrize("p",[False,True])
def test_classical_two_valued_logic_examples_are_tautologies_only(tag,p):
    # These finite truth tables are teaching *examples*, not model-free proof certification.
    proposition=(p or not p) if tag=="excluded_middle" else not(p and not p)
    assert proposition is True


def test_inverse_and_contrapositive_must_not_be_confused():
    implications=[]
    for p in (False,True):
        for q in (False,True):
            implication=(not p) or q
            inverse=p or (not q)   # not(p) -> not(q): p OR not(q)
            contrapositive=q or (not p)  # not(q) -> not(p): q OR not(p)
            assert implication == contrapositive
            implications.append(implication != inverse)
    assert any(implications), "original and inverse are not generally equivalent"


@pytest.mark.parametrize("bad",[
    ("duplicate ID",lambda rows:rows.__setitem__(1,(34,"01",*rows[1][2:]))),
    ("missing page",lambda rows:rows.__setitem__(1,(99,"02",*rows[1][2:]))),
    ("bad identifier",lambda rows:rows.__setitem__(1,(34,"x2",*rows[1][2:]))),
    ("bad knowledge kind",lambda rows:rows.__setitem__(1,(34,"02","PROVEN_THEOREM",*rows[1][3:]))),
    ("invalid paraphrase",lambda rows:rows.__setitem__(1,(34,"02","CONCEPT","短",rows[1][4]))),
    ("orphan related editorial",lambda rows:rows.__setitem__(2,(34,"03",rows[2][2],rows[2][3],["DOES-NOT-EXIST"]))),
    ("same-page mismatch",lambda rows:rows.__setitem__(2,(34,"03",rows[2][2],rows[2][3],["KB32-S-P041-A001"]))),
    ("duplicate old link",lambda rows:rows.__setitem__(2,(34,"03",rows[2][2],rows[2][3],["KB32-C-P034-A002","KB32-C-P034-A002"]))),
])
def test_malformed_crosswalk_never_passes(bad):
    name,mutation=bad
    rows=deepcopy(G.CANDIDATES)
    mutation(rows)
    with pytest.raises(ValueError):
        G.assemble(proposals=rows)


def test_unreviewed_source_page_cannot_be_falsely_approved():
    data=deepcopy(PAGES)
    data["pages"][21]["full_page_human_review"]="APPROVED"
    with pytest.raises(ValueError,match="false source human review"):
        G.assemble(pages=data)


@pytest.mark.parametrize("target",["pdf","missing_page","page_index","page_hash"])
def test_original_pdf_source_drift_must_fail(target):
    data=deepcopy(PAGES)
    if target=="pdf":
        data["official_pdf_sha256"]="1"*64
    elif target=="missing_page":
        data["pages"]=data["pages"][:-1]
    elif target=="page_index":
        row=next(x for x in data["pages"] if x["printed_page"]==34)
        row["pdf_page_index"]+=1
    else:
        row=next(x for x in data["pages"] if x["printed_page"]==34)
        row["pdfkit_text_sha256"]=""
    with pytest.raises((ValueError,KeyError)):
        G.assemble(pages=data)


@pytest.mark.parametrize("kind",["approved","student","official","count","id"])
def test_existing_editorial_inventory_cannot_be_promoted_or_tampered(kind):
    data=deepcopy(OVERLAY)
    if kind=="approved":
        data["summary"]["teacher_approved"]=1
    elif kind=="student":
        data["summary"]["student_published"]=1
    elif kind=="official":
        data["summary"]["official_atom_denominator"]=313
    elif kind=="count":
        data["summary"]["project_candidates"]=312
    elif kind=="id":
        data["rows"][1]["editorial_id"]=data["rows"][0]["editorial_id"]
    with pytest.raises(ValueError):
        G.assemble(overlay=data)


@pytest.mark.parametrize("kind",["official","track","page"])
def test_upstream_page_gate_mutation_is_rejected(kind):
    data=deepcopy(BASE)
    if kind=="official":
        data["review_gate"]["official_atomic_knowledge_denominator"]=317
    elif kind=="track":
        data["track_evidence"][0]["official_atomic_denominator"]=114
    else:
        data["source_page_denominator"]=60
    with pytest.raises(ValueError):
        G.assemble(baseline=data)


def test_generated_artifact_is_deterministic():
    text=(G.OUTPUT).read_text(encoding="utf-8")
    assert json.loads(text)==RESULT
    assert G.assemble()==G.assemble()
    assert G.REPORT.read_text(encoding="utf-8").count("REVIEW_PENDING")>=28


def test_school_selected_elective_is_not_compulsory():
    rows=[r for r in RESULT["rows"] if r["printed_page"]==65]
    assert len(rows)==7
    assert all(r["track"]=="ELECTIVE_C" for r in rows)
    assert "学校选择" in rows[-1]["original_editorial_paraphrase"]
    assert all(not r["official_atom_certified"] for r in rows)
