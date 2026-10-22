"""Contract/security tests for optional GPU formula worker without loading a GPU model."""
import base64
import io

from fastapi.testclient import TestClient
from PIL import Image

from services import formula_worker as worker


client = TestClient(worker.app)


def image_b64():
    image = Image.new("RGB", (90, 40), "white")
    buf = io.BytesIO()
    image.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def test_worker_requires_server_token(monkeypatch):
    monkeypatch.delenv("STEM_FORMULA_SERVICE_TOKEN", raising=False)
    response = client.post("/recognize", json={"image_base64": image_b64()})
    assert response.status_code == 503
    monkeypatch.setenv("STEM_FORMULA_SERVICE_TOKEN", "secret-local-only")
    response = client.post("/recognize", json={"image_base64": image_b64()})
    assert response.status_code == 401


def test_worker_safely_rejects_invalid_image(monkeypatch):
    monkeypatch.setenv("STEM_FORMULA_SERVICE_TOKEN", "secret-local-only")
    response = client.post(
        "/recognize", json={"image_base64": "YWFhYWFhYWFhYXg!"},
        headers={"X-Formula-Token": "secret-local-only"})
    assert response.status_code == 422


def test_mock_model_outputs_not_a_proof(monkeypatch):
    monkeypatch.setenv("STEM_FORMULA_SERVICE_TOKEN", "secret-local-only")

    class FakeResult:
        json = {"res": {"rec_formula": r"\frac{x^2+1}{2}"}}

    class FakeModel:
        def predict(self, input, batch_size):
            assert input.ndim == 3 and input.shape[-1] == 3
            assert batch_size == 1
            return [FakeResult()]

    monkeypatch.setattr(worker, "get_model", lambda: FakeModel())
    response = client.post(
        "/recognize", json={"image_base64": image_b64()},
        headers={"X-Formula-Token": "secret-local-only"})
    assert response.status_code == 200
    data = response.json()
    assert data["latex"] == r"\frac{x^2+1}{2}"
    assert data["math_verified"] is False
    assert data["confidence"] is None
    assert isinstance(data["elapsed_ms"], float)
