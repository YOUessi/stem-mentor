"""Risk-marked formula OCR, multi-region routing, and frozen ROI scoring.

All external OCR/VLM calls are faked except the optional true macOS Vision
check; no real student images, no cloud or Tang service.
"""
from __future__ import annotations
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app import vision_pipeline as pipeline
from app.formula_quality import braces_balanced, formula_quality_report
from evaluations.vision_v017.layout_benchmark import (
    load_cases, make_image, score_boxes, intersection_over_union,
)

CLIENT = TestClient(app)


@pytest.mark.parametrize("source,latex,required_flag", [
    ("x^2+1=0", r"x^{\prime}2+1=0", "power_vs_prime"),
    ("x^2+1=0", r"x^{\wedge}2+1=0", "power_vs_prime"),
    ("x^2+1=0", r"X^{2}+1=0", "lowercase_x_vs_uppercase_X"),
    ("X^2+1=0", r"x^{2}+1=0", "uppercase_X_vs_lowercase_x"),
    ("x^2+1=0", r"\because x^{2}+1=0", "unexpected_reasoning_symbol"),
    ("Question: x=1", r"\operatorname{Question}:x=1",
     "instruction_leaked_into_formula"),
    ("x=1", r"\frac{x+1}{2", "unbalanced_braces"),
])
def test_formula_quality_flags_visible_errors(source, latex, required_flag):
    report = formula_quality_report(latex, source)
    assert report["state"] == "suspect"
    assert any(x["code"] == required_flag for x in report["warnings"])
    assert report["mathematically_verified"] is False
    assert report["requires_human_review"] is True


def test_latex_syntax_is_not_mathematical_proof():
    assert braces_balanced(r"\frac{x+1}{2}") is True
    assert braces_balanced(r"\frac{x+1}{2") is False
    assert braces_balanced(r"\text{\{x\}}") is True
    report = formula_quality_report(r"x^{2}+2x+1=(x+1)^{2}", "x2+2x+1=(x+1)2")
    assert report["state"] == "unverified"
    assert report["warnings"] == []
    assert report["mathematically_verified"] is False
    assert formula_quality_report("", "x=1")["state"] == "missing_formula"


def test_same_line_two_formula_spans_are_isolated_and_preserved(monkeypatch):
    raw_line = {
        "text": "已知 x²=1，y²=4，求解",
        "bbox": [.02,.2,.9,.2],
        "confidence": .94,
        "spans": [
            {"text": "x²=1", "bbox": [.12,.2,.23,.2]},
            {"text": "y²=4", "bbox": [.46,.2,.23,.2]},
        ]
    }
    monkeypatch.setattr(pipeline.providers, "run_native_ocr",
                        lambda image: ([raw_line], "ready"))
    calls = []

    def fake_formula(image, bbox):
        with Image.open(io.BytesIO(image)) as cropped:
            calls.append((bbox, cropped.size))
        latex = "x^{2}=1" if bbox[0] < .3 else "y^{2}=4"
        return ({"latex": latex, "source": "formula_ocr", "model": "mock",
                 "confidence": None}, "ready")

    monkeypatch.setattr(pipeline.providers, "call_formula_service", fake_formula)
    image = Image.new("RGB", (1200, 250), "white")
    buffer = io.BytesIO(); image.save(buffer, "PNG")
    resp = CLIENT.post("/api/vision/recognize",
                       files={"file":("two.png",buffer.getvalue(),"image/png")},
                       data={"allow_formula_service":"true"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["pipeline"] == "HYBRID_VISION_V016"
    assert data["routing"]["layout_detector"] == "native_substring_multiregion_v017"
    assert data["routing"]["formula_candidates"] == 2
    assert data["routing"]["focused_formula_regions"] == 2
    assert len(calls) == 2
    assert all(width < 350 for _bbox,(width,_height) in calls)
    assert [x["latex"] for x in data["expressions"]] == ["x^{2}=1","y^{2}=4"]
    assert all(x["quality"]["mathematically_verified"] is False
               for x in data["expressions"])
    assert data["stem"] == raw_line["text"]
    assert data["math_verified"] is False
    assert data["confirmed"] is False


def test_no_explicit_consent_blocks_all_regions(monkeypatch):
    monkeypatch.setattr(pipeline.providers,"run_native_ocr",lambda _:
        ([{"text":"x=1，y=2", "confidence":.94,"bbox":[0,.2,.9,.2],
           "spans":[{"text":"x=1","bbox":[.1,.2,.2,.2]},
                    {"text":"y=2","bbox":[.5,.2,.2,.2]}]}],"ready"))
    monkeypatch.setattr(
        pipeline.providers, "call_formula_service",
        lambda *_: (_ for _ in ()).throw(AssertionError("Unauthorized formula request")))
    image=Image.new("RGB",(400,180),"white")
    buf=io.BytesIO();image.save(buf,"PNG")
    data=CLIENT.post("/api/vision/recognize",
        files={"file":("test.png",buf.getvalue(),"image/png")}).json()
    assert data["routing"]["formula_ocr"] == {"skipped_no_consent":2}


def test_frozen_layout_manifest_has_no_real_exam_images():
    cases, sha = load_cases()
    assert len(cases) == 12
    assert len(sha) == 64
    assert sum(int(flag) for case in cases for _part,flag in case["parts"]) == 11
    assert any(sum(int(flag) for _part,flag in c["parts"]) >= 2 for c in cases)


def test_iou_one_to_one_enforces_geometry():
    region=[.1,.2,.25,.3]
    assert intersection_over_union(region,region) == pytest.approx(1.0)
    assert score_boxes([region],[region,region])["tp"] == 1
    assert score_boxes([region],[region,region])["fp"] == 1
    huge=[.01,.2,.9,.3]
    assert score_boxes([region],[huge])["tp"] == 0


@pytest.mark.skipif(sys.platform != "darwin" or not pipeline.providers.NATIVE_BIN.exists(),
                    reason="Needs Mac's compiled native Apple Vision helper")
def test_real_apple_vision_detects_multiple_inline_equations():
    cases,_ = load_cases()
    case = next(x for x in cases if x["id"] == "L002")
    raw,truth = make_image(case)
    lines,status = pipeline.providers.run_native_ocr(raw)
    assert status == "ready"
    observed=[s["bbox"] for line in lines for s in line.get("spans", [])]
    scored=score_boxes(truth,observed)
    assert scored["tp"] == 2, (lines,scored)


def test_frozen_holdout_is_separate_and_immutable():
    import hashlib
    root = Path(__file__).resolve().parents[2]
    path = root / "evaluations/vision_v017/frozen_holdout_manifest.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "61755c84f206d5e47cfc0c6eb5cd5b556d228c95b79268186a4383c48cf64a2a")
    cases, _ = load_cases(path)
    assert len(cases) == 20
    assert sum(int(flag) for case in cases for _text, flag in case["parts"]) == 20
    assert {"heiti", "arial", "songti"} <= {c["font"] for c in cases}
    assert {"clean", "lowcontrast", "blur"} <= {c["render"] for c in cases}


def test_original_tuning_manifest_unchanged():
    import hashlib
    root = Path(__file__).resolve().parents[2]
    path = root / "evaluations/vision_v017/frozen_layout_manifest.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "5027f260ad42326c853f009d7739ddfcb73d423a4509b1c1eff39aaebdc0203c")
