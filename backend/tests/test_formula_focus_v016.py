"""Hybrid OCR: preserve printed problem text, crop only identified formula span.

Synthetic fixtures; no Paddle API, no real student data, and no external calls.
"""
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont
from fastapi.testclient import TestClient

from app import vision_pipeline as pipeline
from app import vision_providers as providers
from app.main import app

client = TestClient(app)


def synthetic_mixed_image():
    image = Image.new("RGB", (1200, 250), "white")
    out = io.BytesIO()
    image.save(out, "PNG")
    return out.getvalue()


def sample_line(*, focus):
    line = {
        "text": "Question: x^2 + 2x + 1 = (x+1)^2",
        "confidence": .6,
        "bbox": [.02, .18, .85, .25],
        "source": "apple_vision",
    }
    if focus:
        line["spans"] = [{
            "text": "x^2 + 2x + 1 = (x+1)^2",
            "bbox": [.26, .18, .58, .25],
        }]
    else:
        line["spans"] = []
    return line


def submit(*, consent=True):
    return client.post(
        "/api/vision/recognize",
        files={"file": ("synthetic.png", synthetic_mixed_image(), "image/png")},
        data={"allow_formula_service": str(consent).lower()},
    )


def test_focus_only_sends_substring_pixels(monkeypatch):
    monkeypatch.setattr(providers, "run_native_ocr",
                        lambda _: ([sample_line(focus=True)], "ready"))
    captured = []

    def stub(image_png, box):
        with Image.open(io.BytesIO(image_png)) as img:
            captured.append((img.size, box))
        return ({"latex": r"x^{2}+2x+1=(x+1)^{2}",
                 "source": "formula_ocr", "model": "mock",
                 "confidence": None, "verified": False}, "ready")

    monkeypatch.setattr(providers, "call_formula_service", stub)
    response = submit()
    assert response.status_code == 200
    result = response.json()
    assert result["pipeline"] == "HYBRID_VISION_V016"
    assert result["routing"]["focused_formula_regions"] == 1
    assert result["routing"]["formula_ocr"] == {"ready": 1}
    assert len(captured) == 1
    (width, height), box = captured[0]
    assert width < 720, f"focused crop unexpectedly wide: {width}"
    assert width > 500
    assert height < 100
    assert box == [.26, .18, .58, .25]
    assert result["expressions"][0]["bbox_source"] == "apple_vision_substring"
    assert result["expressions"][0]["raw_text"].startswith("x^2")
    assert result["stem"].startswith("Question:")
    assert result["confirmed"] is False
    assert result["math_verified"] is False


def test_no_consent_prevents_formula_server_even_with_span(monkeypatch):
    monkeypatch.setattr(providers, "run_native_ocr",
                        lambda _: ([sample_line(focus=True)], "ready"))

    def forbidden(*args):
        raise AssertionError("formula service invoked without consent")

    monkeypatch.setattr(providers, "call_formula_service", forbidden)
    result = submit(consent=False).json()
    assert result["routing"]["formula_ocr"] == {"skipped_no_consent": 1}
    assert result["expressions"][0]["latex"] == ""


def test_no_span_does_not_claim_precise_formula_box(monkeypatch):
    monkeypatch.setattr(providers, "run_native_ocr",
                        lambda _: ([sample_line(focus=False)], "ready"))
    monkeypatch.setattr(providers, "call_formula_service",
                        lambda *_: (None, "not_configured"))
    result = submit().json()
    assert result["routing"]["focused_formula_regions"] == 0
    assert result["expressions"][0]["bbox_source"] == "apple_vision_line"
    assert "formula_latex_not_verified" in result["uncertain_fields"]


@pytest.mark.parametrize("box", [
    [1, 2, 3], [0.1, float("nan"), .4, .5], [0, 0, 0, 0],
])
def test_reject_unsafe_crop_regions(box):
    with pytest.raises(pipeline.VisionInputError):
        pipeline.crop_region(synthetic_mixed_image(), box)


@pytest.mark.skipif(sys.platform != "darwin" or not providers.NATIVE_BIN.exists(),
                    reason="Apple Vision native integration requires compiled macOS binary")
def test_mac_apple_vision_reports_true_formula_substring():
    image = Image.new("RGB", (1250, 270), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial.ttf", 49)
    draw.text((35, 75), "Question: x^2 + 2x + 1 = (x+1)^2",
              font=font, fill="black")
    out = io.BytesIO()
    image.save(out, "PNG")
    lines, state = providers.run_native_ocr(out.getvalue())
    assert state == "ready"
    assert len(lines) >= 1
    assert "Question:" in lines[0]["text"]
    assert lines[0]["spans"]
    region = lines[0]["spans"][0]
    assert region["text"].startswith("x")
    assert region["bbox"][0] > lines[0]["bbox"][0] + .1
    assert region["bbox"][2] < lines[0]["bbox"][2]


def test_formula_service_failure_short_circuits_remaining_crops(monkeypatch):
    rows = [sample_line(focus=True) for _ in range(3)]
    monkeypatch.setattr(providers, "run_native_ocr", lambda _: (rows, "ready"))
    requests = []

    def fail_once(image, bbox):
        requests.append(bbox)
        return None, "failed"

    monkeypatch.setattr(providers, "call_formula_service", fail_once)
    result = submit().json()
    assert len(requests) == 1
    assert result["routing"]["formula_candidates"] == 3
    assert result["routing"]["formula_ocr"] == {
        "failed": 1, "skipped_service_unavailable": 2,
    }
    assert all(not item["latex"] for item in result["expressions"])
    assert "formula_latex_not_verified" in result["uncertain_fields"]


def test_low_confidence_prose_does_not_trigger_math_remote(monkeypatch):
    text_line = [{"text": "Question number one", "confidence": 0.05,
                  "bbox": [.02, .1, .8, .2], "spans": []}]
    monkeypatch.setattr(providers, "run_native_ocr", lambda _: (text_line, "ready"))

    def should_not_call(*args):
        raise AssertionError("Mathematical OCR must not be used for plain prose")

    monkeypatch.setattr(providers, "call_formula_service", should_not_call)
    data = submit(consent=True).json()
    assert data["routing"]["formula_candidates"] == 0
    assert data["routing"]["formula_ocr"] == {"not_needed": 1}
    assert "low_confidence_text" in data["uncertain_fields"]
