"""External API draft pathway: test with mock transport, NEVER actual cloud."""
import json
from dataclasses import asdict

import httpx
import pytest

from app import model_tutor_draft as gateway


FAKE_EVIDENCE = {
    "status": "APPROVED_HINTS_ONLY",
    "teacher_solution_exposed": False,
    "unverified_content_exposed": False,
    "candidates": [{
        "knowledge_id": "math.hs.sequence.geometric-sum",
        "curriculum_ids": ["HS-MATH-064"],
        "title": "等比数列有限和",
        "version": "1.0.0",
        "hint": "先问相邻项的比值是否相同。",
        "condition_status": "CONDITIONS_NOT_ESTABLISHED",
        "approval_evidence": "TWO_EXTERNAL_SIGNATURES",
    }],
}


def setup_fake(monkeypatch):
    monkeypatch.setattr(gateway, "student_evidence_lookup", lambda q, limit=3: FAKE_EVIDENCE)
    monkeypatch.setenv("STEM_MENTOR_ENABLE_MODEL_DRAFT", "1")
    monkeypatch.setenv("STEM_TUTOR_API_KEY", "test-only-mock-key")


def call(**kwargs):
    return gateway.draft_next_question(
        "等比数列求和怎样入手？", operator_scope="EDITOR_LOCAL",
        help_requested=True, consent_to_cloud=True, mode="GUIDE",
        provider_url="https://api.openai.com/v1/chat/completions",
        provider_model="test-model",
        **kwargs,
    )


def mock_response(payload=None, status=200, reason="stop"):
    payload = payload or {
        "evidence_id": "math.hs.sequence.geometric-sum",
        "follow_up_question": "你能先写出前四项并找出共同的比例吗？",
        "explain_conditions_first": True,
    }
    return httpx.Response(status, json={
        "choices": [{"finish_reason": reason,
                     "message": {"content": json.dumps(payload, ensure_ascii=False)}}]})


def test_default_no_approval_no_model_call(monkeypatch):
    # No real approvals exist; even with all model knobs set there is no egress.
    monkeypatch.setenv("STEM_MENTOR_ENABLE_MODEL_DRAFT", "1")
    monkeypatch.setenv("STEM_TUTOR_API_KEY", "test-only-mock-key")
    record = []
    r = call(transport=httpx.MockTransport(lambda req: record.append(req) or mock_response()))
    assert r.status == "BLOCKED"
    assert r.reason == "NO_APPROVED_MATH_EVIDENCE"
    assert not record and r.question_draft is None


@pytest.mark.parametrize("kwargs,reason", [
    ({"operator_scope": ""}, "EDITOR_ONLY"),
    ({"operator_scope": "STUDENT"}, "EDITOR_ONLY"),
    ({"mode": "HIDDEN"}, "INVALID_MODE"),
    ({"mode": "INDEPENDENT", "help_requested": False}, "PROTECT_INDEPENDENCE"),
    ({"mode": "ANALYZE", "help_requested": False}, "NO_HELP_REQUEST"),
    ({"consent_to_cloud": False}, "NO_EXPLICIT_CLOUD_CONSENT"),
    ({"question": ""}, "INVALID_QUESTION"),
    ({"question": "x" * 161}, "INVALID_QUESTION"),
    ({"question": "秘密\n题目"}, "CONTROL_CHARACTERS"),
])
def test_early_gates_never_contact_provider(monkeypatch, kwargs, reason):
    setup_fake(monkeypatch)
    flags = dict(operator_scope="EDITOR_LOCAL", mode="GUIDE", help_requested=True,
                 consent_to_cloud=True, question="求等比数列前 n 项和",
                 provider_url="https://api.openai.com/v1/chat/completions",
                 provider_model="test-model")
    flags.update(kwargs)
    called = []
    v = gateway.draft_next_question(
        **flags, transport=httpx.MockTransport(lambda req: called.append(req) or mock_response()))
    assert v.reason == reason and not called and not v.student_visible


@pytest.mark.parametrize("url", [
    "http://api.openai.com/v1/chat/completions", "https://127.0.0.1/v1/chat/completions",
    "https://169.254.169.254/v1/chat/completions",
    "https://api.openai.com.evil.com/v1/chat/completions",
    "https://evil:pass@api.openai.com/v1/chat/completions",
    "https://api.openai.com/v1/chat/completions?key=x",
    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions#fragment",
    "https://api.openai.com/v1/chat/completions/",
    "https://localhost/v1/chat/completions",
])
def test_unallowlisted_endpoint_never_network(monkeypatch, url):
    setup_fake(monkeypatch)
    called = []
    result = gateway.draft_next_question(
        "等比数列", operator_scope="EDITOR_LOCAL", mode="GUIDE",
        help_requested=True, consent_to_cloud=True,
        provider_url=url, provider_model="test-model",
        transport=httpx.MockTransport(lambda req: called.append(req) or mock_response()))
    assert result.reason == "PROVIDER_NOT_ALLOWLISTED" and not called


@pytest.mark.parametrize("key", ["", " ", "abc\nsecret", "x" * 513, "中文密钥"])
def test_bad_credentials_never_network(monkeypatch, key):
    setup_fake(monkeypatch)
    monkeypatch.setenv("STEM_TUTOR_API_KEY", key)
    v = call(transport=httpx.MockTransport(lambda req: pytest.fail("unexpected HTTP call")))
    assert v.reason == "MISSING_OR_INVALID_CREDENTIAL" and not v.model_called


@pytest.mark.parametrize("name", ["", "my model", "xxx@evil", "x" * 81, "模型"])
def test_bad_model_never_network(monkeypatch, name):
    setup_fake(monkeypatch)
    v = gateway.draft_next_question(
        "数列", operator_scope="EDITOR_LOCAL", mode="GUIDE",
        help_requested=True, consent_to_cloud=True,
        provider_url="https://api.openai.com/v1/chat/completions",
        provider_model=name,
        transport=httpx.MockTransport(lambda req: pytest.fail("unexpected HTTP call")))
    assert v.reason == "MODEL_NOT_CONFIGURED"


def test_disabled_even_if_evidence_available(monkeypatch):
    setup_fake(monkeypatch)
    monkeypatch.delenv("STEM_MENTOR_ENABLE_MODEL_DRAFT", raising=False)
    assert call().reason == "MODEL_DRAFT_DISABLED"


def test_approved_only_does_not_leak_teacher_material(monkeypatch):
    setup_fake(monkeypatch)
    network = []
    def respond(request):
        network.append(request)
        assert request.url.host == "api.openai.com"
        assert request.headers["authorization"] == "Bearer test-only-mock-key"
        assert "test-only-mock-key" not in request.content.decode()
        data = json.loads(request.content)
        assert data["max_tokens"] <= 160 and data["temperature"] == 0
        assert [m["role"] for m in data["messages"]] == ["system", "user"]
        body = json.loads(data["messages"][1]["content"])
        assert body["student_question"] == "等比数列求和怎样入手？"
        assert body["approved_minimal_hints"][0]["condition_status"] == "CONDITIONS_NOT_ESTABLISHED"
        combined = json.dumps(data, ensure_ascii=False)
        for forbidden in ("teacher_solution", "proof_steps", "worked_examples",
                          "student_id", "profile", "history", "reviewer_id", "private_key"):
            assert forbidden not in combined
        return mock_response()
    v = call(transport=httpx.MockTransport(respond))
    assert len(network) == 1 and v.model_called and v.editor_only
    assert v.status == "MODEL_DRAFT_REVIEW_REQUIRED"
    assert v.model_claims_verified is False and v.student_visible is False
    assert v.question_draft["evidence_id"] == "math.hs.sequence.geometric-sum"
    assert not asdict(v)["student_visible"]


@pytest.mark.parametrize("payload,finish,expected", [
    ({"evidence_id": "hallucinated-id",
      "follow_up_question": "你能先写出首项和公比吗？",
      "explain_conditions_first": True}, "stop", "HALLUCINATED_EVIDENCE_ID"),
    ({"evidence_id": "math.hs.sequence.geometric-sum",
      "follow_up_question": "答案是 20", "explain_conditions_first": True}, "stop", None),
    ({"evidence_id": "math.hs.sequence.geometric-sum",
      "follow_up_question": "x" * 181, "explain_conditions_first": True}, "stop", None),
    ({"evidence_id": "math.hs.sequence.geometric-sum",
      "follow_up_question": "你可以先写出数列前四项吗？",
      "explain_conditions_first": True, "solution": "q=1 的答案"}, "stop", None),
    ({"evidence_id": "math.hs.sequence.geometric-sum",
      "follow_up_question": "你可以先写出数列前四项吗？",
      "explain_conditions_first": "yes"}, "stop", None),
    ({"evidence_id": "math.hs.sequence.geometric-sum",
      "follow_up_question": "你可以先写出数列前四项吗？",
      "explain_conditions_first": True}, "length", None),
])
def test_model_output_validation_and_unsafe_never_student_visible(monkeypatch, payload, finish, expected):
    setup_fake(monkeypatch)
    v = call(transport=httpx.MockTransport(lambda req: mock_response(payload, reason=finish)))
    if expected == "HALLUCINATED_EVIDENCE_ID":
        assert v.reason == "PROVIDER_UNVERIFIED_OUTPUT"
    else:
        assert v.status == "BLOCKED"
    assert v.student_visible is False
    assert v.question_draft is None


@pytest.mark.parametrize("failure", [
    lambda req: httpx.Response(500, text="private student password secret"),
    lambda req: httpx.Response(302, headers={"Location": "http://127.0.0.1/"}),
    lambda req: httpx.Response(200, content=b"not JSON"),
    lambda req: httpx.Response(200, json={"choices": []}),
    lambda req: httpx.Response(200, content=b"x" * 12001),
    lambda req: (_ for _ in ()).throw(httpx.ConnectError("secret leak")),
])
def test_provider_error_is_fail_closed(monkeypatch, failure):
    setup_fake(monkeypatch)
    v = call(transport=httpx.MockTransport(failure))
    assert v.status == "BLOCKED" and v.reason == "PROVIDER_UNVERIFIED_OUTPUT"
    assert v.question_draft is None and not v.student_visible
    assert "secret" not in str(v)


def test_two_allowed_providers(monkeypatch):
    setup_fake(monkeypatch)
    for url in sorted(gateway.PROVIDER_ENDPOINTS):
        v = gateway.draft_next_question(
            "等比数列", mode="INDEPENDENT", help_requested=True,
            consent_to_cloud=True, operator_scope="EDITOR_LOCAL",
            provider_url=url, provider_model="mock-model",
            transport=httpx.MockTransport(lambda req: mock_response()))
        assert v.status == "MODEL_DRAFT_REVIEW_REQUIRED" and not v.student_visible


def test_condition_status_always_unverified(monkeypatch):
    setup_fake(monkeypatch)
    bad = {**FAKE_EVIDENCE, "candidates": [{**FAKE_EVIDENCE["candidates"][0],
                                           "condition_status": "VERIFIED"}]}
    monkeypatch.setattr(gateway, "student_evidence_lookup", lambda q, limit=3: bad)
    r = call(transport=httpx.MockTransport(lambda req: pytest.fail("network should be blocked")))
    assert r.reason == "UNEXPECTED_CONDITION_STATUS"
