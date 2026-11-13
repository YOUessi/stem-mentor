"""Bounded DAG, original teacher manuscripts, math witnesses, anti-authority gates."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import build_kb_batch133_atomization as base
import build_kb_batch134_graph as graph
import build_kb_batch134_lessons as lesson
import check_kb_batch134_math as oracle
@pytest.fixture(scope="module")
def source():return json.loads(base.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def ledger():return json.loads(graph.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def drafts():return json.loads(lesson.OUT.read_text(encoding="utf-8"))
@pytest.fixture(scope="module")
def evidence():return json.loads(oracle.OUT.read_text(encoding="utf-8"))
def test_all_offline_gates(source,ledger,drafts,evidence):
    assert base.validate(source) and graph.validate(ledger) and lesson.validate(drafts) and oracle.validate(evidence)
    assert graph.MD.read_text(encoding="utf-8")==graph.render(ledger)
    assert lesson.MD.read_text(encoding="utf-8")==lesson.render(drafts)
    assert json.loads(lesson.SAFE.read_text())==lesson.safe_export(drafts)
def test_bounded_coverage_is_honest(ledger):
    assert ledger["proposed_nodes"]==41
    assert ledger["proposed_direct_edges"]==32
    assert ledger["max_dag_depth"]>0
    assert ledger["official_atom_denominators"]=={t:None for t in base.TRACKS}
    assert ledger["full_source_census_complete"] is False
    assert ledger["student_authoritative_releases"]==ledger["teacher_approvals"]==0
@pytest.mark.parametrize("row",range(41))
def test_each_graph_node_uses_existing_source_lock_and_human_review(row,source,ledger):
    x=ledger["editorial_nodes"][row]
    parent={r["id"]:r for r in source["records"]}[x["candidate_id"]]
    assert x["source_span_sha256"]==parent["source_lock"]["span_sha256"]
    assert x["teacher_review"]=="REVIEW_PENDING"
    assert x["formal_prerequisite_correctness"]=="UNVERIFIED"
    assert x["official_atom_id"] is None and not x["student_authoritative"]
@pytest.mark.parametrize("row",range(41))
def test_broken_graph_node_rejected(row,source):
    x=copy.deepcopy(source["records"])
    x[row]["prerequisite_proposals"]=["fictional-id"]
    with pytest.raises(ValueError,match="orphan"):
        graph.analyze(x)
@pytest.mark.parametrize("row",range(41))
def test_self_cycle_rejected(row,source):
    x=copy.deepcopy(source["records"]); x[row]["prerequisite_proposals"].append(x[row]["id"])
    with pytest.raises(ValueError,match="self prereq"):
        graph.analyze(x)
@pytest.mark.parametrize("row",range(41))
def test_record_forged_approval_rejected(row,ledger):
    d=copy.deepcopy(ledger);d["editorial_nodes"][row]["teacher_review"]="APPROVED"
    with pytest.raises(ValueError):graph.validate(d)
@pytest.mark.parametrize("track",base.TRACKS)
def test_forged_denominator_rejected(track,ledger):
    d=copy.deepcopy(ledger);d["official_atom_denominators"][track]=10
    with pytest.raises(ValueError):graph.validate(d)
def test_two_node_cycle_rejected(source):
    records=copy.deepcopy(source["records"])
    a=records[0]["id"];b=records[1]["id"]
    records[0]["prerequisite_proposals"].append(b)
    assert a in records[1]["prerequisite_proposals"]
    with pytest.raises(ValueError,match="cycle"):graph.analyze(records)
@pytest.mark.parametrize("grp",list(graph.EXPECTED_REUSE))
def test_reuse_group_injection_rejected(grp,source):
    records=copy.deepcopy(source["records"])
    for r in records:
        if r["cross_page_reuse_group"] is None:
            r["cross_page_reuse_group"]=grp;break
    with pytest.raises(ValueError,match="reuse"):graph.analyze(records)
@pytest.mark.parametrize("row",range(8))
def test_eight_complete_teacher_manuscripts(row,drafts,source):
    x=drafts[row]
    assert x["source_candidate_id"] in {r["id"] for r in source["records"]}
    assert len(x["reasoned_steps"])>=4
    assert len(x["teacher_examples"])==2
    assert len(x["student_hint_ladder"])==3
    assert x["teacher_review_status"]=="REVIEW_PENDING"
    assert x["teacher_solution_visibility"]=="TEACHER_ONLY"
@pytest.mark.parametrize("row",range(8))
@pytest.mark.parametrize("key,forgery",[
    ("student_authoritative",True),("teacher_review_status","APPROVED"),
    ("teacher_review_evidence",{"signature":"fake"}),
    ("formal_proof_certified",True),("free_student_step_verified",True),
    ("teacher_solution_visibility","STUDENT"),
])
def test_no_self_publishing(row,key,forgery,drafts):
    x=copy.deepcopy(drafts);x[row][key]=forgery
    with pytest.raises(ValueError):lesson.validate(x)
@pytest.mark.parametrize("row",range(8))
def test_missing_proof_rejected(row,drafts):
    x=copy.deepcopy(drafts);x[row]["reasoned_steps"].clear()
    with pytest.raises(ValueError):lesson.validate(x)
@pytest.mark.parametrize("row",range(8))
def test_answer_removed_or_modified_rejected(row,drafts):
    x=copy.deepcopy(drafts);x[row]["teacher_examples"][1]["answer"]="?"
    with pytest.raises(ValueError):lesson.validate(x)
@pytest.mark.parametrize("row",range(24))
def test_exact_finite_oracle_case_recalculated(row,evidence):
    recalculated=oracle.cases()
    assert recalculated[row]==evidence["cases"][row]
    assert recalculated[row]["status"]=="EXACT_PASS"
    assert not recalculated[row]["teacher_approval"]
def test_all_example_links_and_negative_coverage(drafts,evidence):
    groups={x["id"]:[] for x in drafts}
    for t in evidence["cases"]:groups[t["lesson_id"]].append(t["kind"])
    assert all(v.count("POS")==2 and v.count("NEG")==1 for v in groups.values())
    assert not evidence["theorem_general_proof_certified"]
    assert not evidence["student_free_text_verified"]
def test_forged_math_proof_rejected(evidence):
    x=copy.deepcopy(evidence);x["theorem_general_proof_certified"]=True
    with pytest.raises(ValueError):oracle.validate(x)
def test_student_export_has_no_teacher_answers(drafts):
    safe=json.loads(lesson.SAFE.read_text())
    assert safe==lesson.safe_export(drafts)
    assert safe["items"]==[] and safe["publishable_count"]==0
    assert "teacher_examples" not in json.dumps(safe)
