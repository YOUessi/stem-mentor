"""Offline tests: review signature verification, stale release, and student RAG leakage."""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from app.attested_releases import approved_lesson_ids, lesson_digest, _canonical
from app.deep_knowledge import lessons
from app.deep_retrieval import student_evidence_lookup, editor_draft_full

OPENSSL = shutil.which("openssl")


@pytest.fixture
def offline_reviewer_fixture(tmp_path, monkeypatch):
    if not OPENSSL:
        pytest.skip("OpenSSL unavailable: real student release remains disabled")
    # Only temporary *test* identities. Never pretend these are real teachers.
    reviewers = []
    private_keys = []
    for idx in (1, 2):
        private_key = tmp_path / f"test-only-key-{idx}.pem"
        public_key = tmp_path / f"test-only-public-{idx}.pem"
        subprocess.run([OPENSSL, "genrsa", "-out", str(private_key), "2048"],
                       check=True, capture_output=True, timeout=8)
        subprocess.run([OPENSSL, "rsa", "-in", str(private_key), "-pubout",
                        "-out", str(public_key)], check=True, capture_output=True, timeout=8)
        reviewers.append({
            "reviewer_id": f"test-teacher-{idx}", "key_id": f"test-key-{idx}",
            "role": "MATH_TEACHER", "active": True,
            "public_key_pem": public_key.read_text(),
        })
        private_keys.append(private_key)
    key_file, ledger_file = tmp_path / "trusted.json", tmp_path / "attestations.json"
    key_file.write_text(json.dumps({"reviewers": reviewers}), encoding="utf8")
    ledger_file.write_text(json.dumps({"attestations": []}), encoding="utf8")
    monkeypatch.setenv("STEM_MENTOR_TRUSTED_REVIEWERS_PATH", str(key_file))
    monkeypatch.setenv("STEM_MENTOR_REVIEW_ATTESTATIONS_PATH", str(ledger_file))
    monkeypatch.setenv("STEM_MENTOR_ENABLE_APPROVED_RAG", "1")
    doc = next(d for d in lessons() if d.id == "math.hs.triangle.ssa-ambiguity")
    def record(idx, doc=doc, **changes):
        payload = {
            "knowledge_id": doc.id, "content_sha256": lesson_digest(doc),
            "version": doc.version, "reviewer_id": reviewers[idx]["reviewer_id"],
            "key_id": reviewers[idx]["key_id"], "issued_at": "2026-11-03T03:00:00+00:00",
            "decision": "APPROVE",
        }
        payload.update(changes)
        data = tmp_path / f"test-review-payload-{idx}.json"
        signature = tmp_path / f"test-review-{idx}.bin"
        data.write_bytes(_canonical(payload))
        subprocess.run([OPENSSL, "dgst", "-sha256", "-sign", str(private_keys[idx]),
                        "-out", str(signature), str(data)],
                       check=True, capture_output=True, timeout=8)
        return {"payload":payload, "signature_base64":base64.b64encode(signature.read_bytes()).decode()}
    def save(records):
        ledger_file.write_text(json.dumps({"attestations": records}, ensure_ascii=False), encoding="utf8")
    return doc, reviewers, key_file, ledger_file, record, save


def test_no_developer_approval_sneaks_into_student_response(monkeypatch):
    monkeypatch.delenv("STEM_MENTOR_ENABLE_APPROVED_RAG", raising=False)
    assert approved_lesson_ids() == frozenset()
    x = student_evidence_lookup("SSA 多解")
    assert x["status"] == "NO_APPROVED_EVIDENCE"
    assert not x["candidates"]


def test_two_independent_signatures_required_and_only_hint_released(offline_reviewer_fixture):
    doc, reviewers, key_file, ledger_file, record, save = offline_reviewer_fixture
    assert approved_lesson_ids() == frozenset()
    save([record(0)])
    assert approved_lesson_ids() == frozenset()
    save([record(0), record(1)])
    assert approved_lesson_ids() == {doc.id}
    result = student_evidence_lookup("正弦定理 SSA 多解")
    assert result["status"] == "APPROVED_HINTS_ONLY"
    assert [x["knowledge_id"] for x in result["candidates"]] == [doc.id]
    allowed = {"knowledge_id", "curriculum_ids", "title", "version", "hint",
               "condition_status", "approval_evidence"}
    assert set(result["candidates"][0]) == allowed
    assert result["candidates"][0]["condition_status"] == "CONDITIONS_NOT_ESTABLISHED"
    raw = json.dumps(result["candidates"],ensure_ascii=False)
    for restricted in ("worked_examples", "proof_steps", "teacher_solution",
                       "counterexamples", "rationale_steps", "misconceptions"):
        assert restricted not in raw
    assert result["teacher_solution_exposed"] is False


@pytest.mark.parametrize("tamper", ["signature","hash","reviewer","duplicate","revoke","future","active","wrong_key"])
def test_release_fails_closed_on_tamper(offline_reviewer_fixture, tamper):
    doc, reviewers, key_file, ledger_file, record, save = offline_reviewer_fixture
    a, b = record(0), record(1)
    if tamper == "signature":
        b["signature_base64"] = base64.b64encode(bytes(256)).decode()
    elif tamper == "hash":
        b["payload"]["content_sha256"] = "0"*64
    elif tamper == "reviewer":
        b["payload"]["reviewer_id"] = "forged"
    elif tamper == "duplicate":
        save([a, b, b])
    elif tamper == "revoke":
        b = record(1, decision="REVOKE")
    elif tamper == "future":
        b = record(1, issued_at="2090-01-01T00:00:00+00:00")
    elif tamper == "active":
        reviewers[1]["active"] = False
        key_file.write_text(json.dumps({"reviewers":reviewers}),encoding="utf8")
    elif tamper == "wrong_key":
        b["payload"]["key_id"] = "untrusted"
    if tamper != "duplicate":
        save([a,b])
    assert approved_lesson_ids() == frozenset()
    assert student_evidence_lookup("SSA 多解")["candidates"] == []


def test_repo_local_attestation_rejected_and_malformed_external_rejected(offline_reviewer_fixture, monkeypatch):
    doc, reviewers, keys, ledger, record, save = offline_reviewer_fixture
    save([record(0),record(1)])
    assert approved_lesson_ids() == {doc.id}
    # The repository's own source files must never serve as trust authority.
    monkeypatch.setenv("STEM_MENTOR_TRUSTED_REVIEWERS_PATH", str(
        Path(__file__).resolve().parents[2] / "knowledge/deep/v1/core_foundations_v1.json"
    ))
    assert approved_lesson_ids() == frozenset()
    monkeypatch.setenv("STEM_MENTOR_TRUSTED_REVIEWERS_PATH", str(keys))
    ledger.write_text("{invalid-json", encoding="utf8")
    assert approved_lesson_ids() == frozenset()


def test_review_is_exact_version_and_cannot_patch_draft_approval(offline_reviewer_fixture):
    doc, reviewers, keys, ledger, record, save = offline_reviewer_fixture
    a, b = record(0), record(1)
    save([a,b])
    assert doc.review.status == "REVIEW_PENDING"
    assert approved_lesson_ids() == {doc.id}
    # Signatures are tied to every byte of the model's canonical fields.
    edited = doc.model_copy(update={"title":doc.title+" edited"})
    assert lesson_digest(edited) != lesson_digest(doc)
    # An editorial preview remains explicitly unapproved in source provenance.
    full = editor_draft_full(doc.id,scope="EDITOR_LOCAL")
    assert full["review_status"] == "REVIEW_PENDING"


def test_empty_search_and_invalid_controls_remain_closed():
    for q in ("","  ","a"*161,"\x00control"):
        with pytest.raises(ValueError):
            student_evidence_lookup(q)
