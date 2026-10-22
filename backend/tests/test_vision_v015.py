"""Synthetic-only regression tests for v0.15 photo-to-question integration."""
import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app import vision_pipeline as pipeline

client = TestClient(app)


def image_bytes(format="PNG"):
    image = Image.new("RGB", (640, 360), "white")
    out = io.BytesIO()
    image.save(out, format)
    return out.getvalue()


def upload(data=None, **form):
    return client.post(
        "/api/vision/recognize",
        files={"file": ("math.png", data if data is not None else image_bytes(), "image/png")},
        data=form,
    )


def fake_lines():
    return [
        {"text": "如图，已知 AB = AC", "confidence": .93,
         "bbox": [.03, .05, .75, .12], "source": "apple_vision"},
        {"text": "求证 AD ⊥ BC", "confidence": .89,
         "bbox": [.03, .22, .6, .12], "source": "apple_vision"},
    ]


def test_page_and_static_vision_assets():
    assert client.get("/vision").status_code == 200
    assert "拍照识题" in client.get("/vision").text
    assert client.get("/assets/vision/vision.js").status_code == 200
    assert client.get("/ipad").status_code == 200
    assert 'href="/vision"' in client.get("/ipad").text


def test_no_service_invoked_without_consent(monkeypatch):
    monkeypatch.setattr(pipeline.providers, "run_native_ocr", lambda _: (fake_lines(), "ready"))

    def do_not_call(*_args):
        raise AssertionError("External recognition is prohibited by default")

    monkeypatch.setattr(pipeline.providers, "call_formula_service", do_not_call)
    monkeypatch.setattr(pipeline.providers, "call_diagram_vlm", do_not_call)
    result = upload().json()
    assert result["stem"].startswith("如图")
    assert result["routing"]["visual_review_recommended"]
    assert result["routing"]["vlm"] == "skipped_no_consent"
    assert result["routing"]["formula_ocr"]["skipped_no_consent"] >= 1
    assert all(not e["latex"] for e in result["expressions"])
    assert result["needs_human_review"] and not result["math_verified"]
    assert not result["image"]["stored_on_server"]
    assert not result["diagram"]["relations"]


def test_formula_and_vlm_opt_in_are_not_proofs(monkeypatch):
    monkeypatch.setattr(pipeline.providers, "run_native_ocr", lambda _: (fake_lines(), "ready"))
    monkeypatch.setattr(
        pipeline.providers, "call_formula_service",
        lambda image, bbox: (
            {"latex": "AB=AC", "source": "formula_ocr",
             "model": "synthetic-stub", "confidence": None, "verified": False},
            "ready",
        ),
    )
    monkeypatch.setattr(
        pipeline.providers, "call_diagram_vlm",
        lambda image: (
            {"entities": ["A", "B", "C"], "relations": [
                {"type": "looks_perpendicular", "objects": ["AD", "BC"],
                 "source": "vlm_observation", "status": "observed_unverified",
                 "is_given": False}],
             "verified": False, "source": "vlm_observation"},
            "ready",
        ),
    )
    reply = upload(diagram_present="true", allow_cloud_vlm="true",
                   allow_formula_service="true")
    assert reply.status_code == 200
    data = reply.json()
    assert data["routing"]["formula_consent"]
    assert data["routing"]["vlm"] == "ready"
    assert data["expressions"][0]["latex"] == "AB=AC"
    assert data["expressions"][0]["needs_review"]
    assert data["diagram"]["relations"][0]["is_given"] is False
    assert not data["diagram"]["verified"]


def test_vlm_skipped_if_no_visual_need_even_with_consent(monkeypatch):
    monkeypatch.setattr(
        pipeline.providers, "run_native_ocr",
        lambda _: ([{"text": "计算 1+1", "confidence": .98,
                     "bbox": [.1, .1, .3, .1]}], "ready"),
    )
    monkeypatch.setattr(
        pipeline.providers, "call_diagram_vlm",
        lambda _: (_ for _ in ()).throw(AssertionError("Needless cloud call")),
    )
    result = upload(allow_cloud_vlm="true").json()
    assert result["routing"]["vlm"] == "skipped_not_needed"


def test_upload_validation():
    assert upload(data=b"not an image").status_code == 422
    assert upload(data=b"").status_code == 422
    assert upload(data=b"x" * (pipeline.MAX_FILE_BYTES + 1)).status_code == 422
    assert upload(data=image_bytes("GIF")).status_code == 422


def test_confirm_is_human_acknowledgement_not_math_proof():
    empty = client.post("/api/vision/confirm", json={"stem": " "})
    assert empty.status_code == 422
    response = client.post(
        "/api/vision/confirm",
        json={"stem": "已知 AB=AC，求证 AD⊥BC",
              "expressions": [{"latex": r"\frac{x+1}{2}"}]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["confirmed"] is True
    assert data["math_verified"] is False
    assert data["diagram_verified"] is False
    assert r"\frac{x+1}{2}" in data["custom_problem"]


def test_no_formula_no_ocr_reports_missing_not_invented(monkeypatch):
    monkeypatch.setattr(pipeline.providers, "run_native_ocr",
                        lambda _: ([], "not_installed"))
    response = upload()
    assert response.status_code == 200
    data = response.json()
    assert data["stem"] == ""
    assert "local_ocr_unavailable" in data["uncertain_fields"]
    assert "question_text_missing" in data["uncertain_fields"]
    assert data["expressions"] == []
