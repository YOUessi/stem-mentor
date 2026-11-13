"""Batch58 K08 mixed signed/unsigned index: real ephemeral RSA, no cloud egress.

Only TEST identities in OS temporary paths. These signatures never represent
real teachers. They permit exercising a branch that production currently has
zero real approved records and previous batch smoke tests could not reach.
"""
from __future__ import annotations

import base64
import json
import subprocess

import httpx
import pytest

from test_attested_release_batch08 import offline_reviewer_fixture
from app.attested_releases import approved_lesson_ids, lesson_digest, _canonical
from app.deep_knowledge import lessons
from app.deep_retrieval import editor_draft_search, student_evidence_lookup
from app.model_tutor_draft import draft_next_question

APPROVED_A = "math.hs.triangle.ssa-ambiguity"
APPROVED_B = "math.hs.triangle.sine-law"
UNAPPROVED = "math.hs.triangle.ssa-two-solutions"
QUERY = "正弦定理 SSA"


def sign_second_lesson(tmp_path, reviewers, *, decision="APPROVE"):
    doc = next(x for x in lessons() if x.id == APPROVED_B)
    output = []
    for idx in (0, 1):
        payload = {
            "knowledge_id": doc.id, "content_sha256": lesson_digest(doc),
            "version": doc.version,
            "reviewer_id": reviewers[idx]["reviewer_id"],
            "key_id": reviewers[idx]["key_id"],
            "issued_at": "2026-11-03T03:00:00+00:00",
            "decision": decision if idx == 1 else "APPROVE",
        }
        plain = tmp_path / f"kb58-test-payload-{idx}.json"
        signature = tmp_path / f"kb58-test-signature-{idx}.bin"
        plain.write_bytes(_canonical(payload))
        subprocess.run(["openssl", "dgst", "-sha256", "-sign",
                        str(tmp_path / f"test-only-key-{idx + 1}.pem"),
                        "-out", str(signature), str(plain)], check=True, capture_output=True, timeout=8)
        output.append({"payload": payload,
                       "signature_base64": base64.b64encode(signature.read_bytes()).decode()})
    return output


def test_mixed_index_real_signed_release_filters_before_limit(
        offline_reviewer_fixture, tmp_path):
    doc, reviewers, _, _, record, save = offline_reviewer_fixture
    assert doc.id == APPROVED_A
    b = sign_second_lesson(tmp_path, reviewers)
    save([record(0), record(1), *b])
    assert approved_lesson_ids() == {APPROVED_A, APPROVED_B}
    ranked = editor_draft_search(QUERY, scope="EDITOR_LOCAL", limit=10)
    assert any(x["knowledge_id"] == UNAPPROVED for x in ranked)
    assert all(x["review_status"] == "REVIEW_PENDING" for x in ranked)
    for limit in (1, 2, 3, 8):
        result = student_evidence_lookup(QUERY, limit=limit)
        ids = [x["knowledge_id"] for x in result["candidates"]]
        assert result["status"] == "APPROVED_HINTS_ONLY"
        assert len(ids) == min(limit, 2)
        assert set(ids) <= {APPROVED_A, APPROVED_B}
        assert UNAPPROVED not in ids
        assert not result["teacher_solution_exposed"]
        assert not result["unverified_content_exposed"]
        assert all(row["condition_status"] == "CONDITIONS_NOT_ESTABLISHED"
                   and row["approval_evidence"] == "TWO_EXTERNAL_SIGNATURES"
                   for row in result["candidates"])
        for row in result["candidates"]:
            assert set(row) == {
                "knowledge_id", "curriculum_ids", "title", "version",
                "hint", "condition_status", "approval_evidence",
            }
            original = next(d for d in lessons() if d.id == row["knowledge_id"])
            assert row["hint"] == original.hint_ladder[0]
            assert "worked_examples" not in json.dumps(row, ensure_ascii=False)
            assert "proof_steps" not in json.dumps(row, ensure_ascii=False)


def test_partial_revocation_removes_only_revoked_lesson(
        offline_reviewer_fixture, tmp_path):
    _, reviewers, _, _, record, save = offline_reviewer_fixture
    b = sign_second_lesson(tmp_path, reviewers, decision="REVOKE")
    save([record(0), record(1), *b])
    assert approved_lesson_ids() == {APPROVED_A}
    result = student_evidence_lookup(QUERY)
    assert [x["knowledge_id"] for x in result["candidates"]] == [APPROVED_A]
    assert UNAPPROVED not in json.dumps(result, ensure_ascii=False)


def test_invalid_signature_in_mixed_ledger_blocks_entire_release(
        offline_reviewer_fixture, tmp_path, monkeypatch):
    _, reviewers, _, _, record, save = offline_reviewer_fixture
    b = sign_second_lesson(tmp_path, reviewers)
    b[1]["signature_base64"] = base64.b64encode(b"tampered").decode()
    save([record(0), record(1), *b])
    assert approved_lesson_ids() == frozenset()
    assert student_evidence_lookup(QUERY)["status"] == "NO_APPROVED_EVIDENCE"
    # Attempting cloud opt-in still must stop before touching HTTP.
    monkeypatch.setenv("STEM_MENTOR_ENABLE_MODEL_DRAFT", "1")
    monkeypatch.setenv("STEM_TUTOR_API_KEY", "test-key-do-not-use")
    mock = httpx.MockTransport(lambda request: pytest.fail("network must not be called"))
    draft = draft_next_question(
        QUERY, operator_scope="EDITOR_LOCAL", mode="GUIDE",
        help_requested=True, consent_to_cloud=True,
        provider_url="https://api.openai.com/v1/chat/completions",
        provider_model="test-only-model", transport=mock)
    assert draft.status == "BLOCKED"
    assert draft.reason == "NO_APPROVED_MATH_EVIDENCE"
    assert draft.student_visible is False and draft.model_called is False


def test_signed_mixed_index_mock_prompt_excludes_unsigned_teacher_data(
        offline_reviewer_fixture, tmp_path, monkeypatch):
    _, reviewers, _, _, record, save = offline_reviewer_fixture
    save([record(0), record(1), *sign_second_lesson(tmp_path, reviewers)])
    assert approved_lesson_ids() == {APPROVED_A, APPROVED_B}
    monkeypatch.setenv("STEM_MENTOR_ENABLE_MODEL_DRAFT", "1")
    monkeypatch.setenv("STEM_TUTOR_API_KEY", "kb58-mock-credential-only")
    captured = []
    def mock_provider(request):
        payload = json.loads(request.content)
        captured.append(payload)
        outer = json.loads(payload["messages"][1]["content"])
        hints = outer["approved_minimal_hints"]
        assert len(hints) == 2
        assert {i["evidence_id"] for i in hints} == {APPROVED_A, APPROVED_B}
        original = json.dumps(payload, ensure_ascii=False)
        for forbidden in ("worked_examples", "proof_steps", "teacher_solution",
                          "counterexamples", "misconceptions", "reviewer_id"):
            assert forbidden not in original
        for doc in lessons():
            if doc.id == UNAPPROVED:
                # Unreviewed first-tier hints must not be silently added.
                assert doc.hint_ladder[0] not in [h["hint"] for h in hints]
        choice = {"evidence_id": APPROVED_B,
                  "follow_up_question": "请先指出正弦定理要求哪条边对应哪个角？",
                  "explain_conditions_first": True}
        return httpx.Response(200, json={"choices": [{
            "finish_reason": "stop",
            "message": {"content": json.dumps(choice, ensure_ascii=False)}}]})
    draft = draft_next_question(
        QUERY, operator_scope="EDITOR_LOCAL", mode="GUIDE",
        help_requested=True, consent_to_cloud=True,
        provider_url="https://api.openai.com/v1/chat/completions",
        provider_model="test-only-model",
        transport=httpx.MockTransport(mock_provider))
    assert len(captured) == 1
    assert draft.model_called and draft.editor_only
    assert draft.status == "MODEL_DRAFT_REVIEW_REQUIRED"
    assert not draft.student_visible and not draft.model_claims_verified


@pytest.mark.parametrize("q", ["正弦定理 SSA", "正弦定理", "三角形 SSA 多解",
                               "SSA 两解", "余弦定理"])
def test_default_unsigned_corpus_stays_closed(q, monkeypatch):
    monkeypatch.delenv("STEM_MENTOR_ENABLE_APPROVED_RAG", raising=False)
    assert approved_lesson_ids() == frozenset()
    got = student_evidence_lookup(q, limit=3)
    assert got["status"] == "NO_APPROVED_EVIDENCE"
    assert got["candidates"] == []
