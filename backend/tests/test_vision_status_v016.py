"""The capabilities endpoint must not expose URL / tokens or overclaim native iPad OCR."""
from fastapi.testclient import TestClient
from app.main import app


def test_status_reports_capability_not_model_quality(monkeypatch):
    monkeypatch.setenv("STEM_FORMULA_SERVICE_URL", "http://127.0.0.1:18931/recognize")
    monkeypatch.setenv("STEM_FORMULA_SERVICE_TOKEN", "do-not-echo")
    monkeypatch.setenv("STEM_VLM_API_URL", "https://example.invalid/v1/chat/completions")
    monkeypatch.setenv("STEM_VLM_API_KEY", "private-bearer-token")
    monkeypatch.setenv("STEM_VLM_MODEL", "synthetic-test")
    reply = TestClient(app).get("/api/vision/status")
    assert reply.status_code == 200
    data = reply.json()
    assert data["engine"] == "HYBRID_VISION_V016"
    assert data["local_ocr"]["device"] == "mac_host"
    assert data["local_ocr"]["ipad_native"] is False
    assert data["formula_service"]["configured"] is True
    assert data["vlm"]["configured"] is True
    assert "private-bearer" not in reply.text
    assert "do-not-echo" not in reply.text
    assert "example.invalid" not in reply.text
    assert data["consent_required"] == {"formula_service": True, "cloud_vlm": True}


def test_formula_probe_distinguishes_available_from_configured(monkeypatch):
    from app import vision_api

    class DummyResponse:
        status_code = 200

        def json(self):
            return {"status": "ready", "model_loaded": True}

    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        return DummyResponse()

    monkeypatch.setenv("STEM_FORMULA_SERVICE_URL",
                       "http://127.0.0.1:18931/recognize")
    monkeypatch.setattr(vision_api.httpx, "get", fake_get)
    status = TestClient(app).get("/api/vision/status").json()["formula_service"]
    assert status == {"configured": True, "reachable": True, "model_loaded": True}
    assert calls == ["http://127.0.0.1:18931/health"]


def test_formula_probe_reports_offline_and_never_checks_remote_hosts(monkeypatch):
    import httpx
    from app import vision_api

    def offline(*args, **kwargs):
        raise httpx.ConnectError("offline")
    monkeypatch.setattr(vision_api.httpx, "get", offline)
    monkeypatch.setenv("STEM_FORMULA_SERVICE_URL",
                       "http://127.0.0.1:18931/recognize")
    status = TestClient(app).get("/api/vision/status").json()["formula_service"]
    assert status["configured"] is True
    assert status["reachable"] is False

    def forbidden(*args, **kwargs):
        raise AssertionError("Must not perform remote network health check")
    monkeypatch.setattr(vision_api.httpx, "get", forbidden)
    monkeypatch.setenv("STEM_FORMULA_SERVICE_URL",
                       "https://example.com/recognize")
    status = TestClient(app).get("/api/vision/status").json()["formula_service"]
    assert status["configured"] is True
    assert status["reachable"] is None
