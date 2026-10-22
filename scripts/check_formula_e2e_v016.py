"""Mac-only, opt-in E2E check using fully synthetic images.

Runs Apple Vision on Mac + dedicated PP-FormulaNet OCR through existing SSH
loopback tunnel to Tang. Never uploads real student data or invokes cloud VLM.

Usage:
    .venv/bin/python scripts/check_formula_e2e_v016.py --url http://127.0.0.1:18916
Output: local artifacts/vision/formula_e2e_v016.json (gitignored).
"""
from __future__ import annotations

import argparse
import io
import json
import time
from pathlib import Path

import httpx
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]


def make_synthetic_line(text: str) -> bytes:
    image = Image.new("RGB", (1250, 270), "white")
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 49)
    ImageDraw.Draw(image).text((35, 75), "Question: " + text,
                              fill="black", font=font)
    output = io.BytesIO()
    image.save(output, "PNG")
    return output.getvalue()


def run(url: str) -> dict:
    target = url.rstrip("/")
    cases = [
        ("ascii_caret", "x^2 + 2x + 1 = (x+1)^2"),
        ("real_superscript", "x² + 2x + 1 = (x+1)²"),
    ]
    with httpx.Client(timeout=60) as client:
        status_response = client.get(target + "/api/vision/status")
        status_response.raise_for_status()
        status = status_response.json()
        if not status["local_ocr"]["ready"]:
            raise RuntimeError("Native Apple Vision OCR is unavailable on Mac")
        if status["formula_service"]["reachable"] is not True:
            raise RuntimeError("Tang inference tunnel is currently unreachable")

        samples = []
        for case_id, original in cases:
            begin = time.perf_counter()
            response = client.post(
                target + "/api/vision/recognize",
                files={"file": (case_id + ".png", make_synthetic_line(original), "image/png")},
                data={
                    "allow_formula_service": "true",
                    "allow_cloud_vlm": "false",
                    "diagram_present": "false",
                },
            )
            response.raise_for_status()
            reply = response.json()
            elapsed = round((time.perf_counter() - begin) * 1000, 1)
            candidates = reply["expressions"]
            if reply["routing"]["focused_formula_regions"] < 1:
                raise RuntimeError(case_id + ": Vision did not identify a formula substring")
            if reply["routing"]["formula_ocr"].get("ready", 0) < 1:
                raise RuntimeError(case_id + ": GPU OCR did not return a result")
            if reply["math_verified"] or not reply["needs_human_review"]:
                raise RuntimeError(case_id + ": model output must never be declared verified")
            samples.append({
                "id": case_id,
                "synthetic_original": original,
                "apple_vision_stem": reply["stem"],
                "formula_source": candidates[0]["source"],
                "formula_latex": candidates[0]["latex"],
                "formula_bbox_source": candidates[0]["bbox_source"],
                "formula_candidate_region": candidates[0]["bbox"],
                "end_to_end_elapsed_ms": elapsed,
                "model_math_verified": False,
            })
            print(case_id, "time_ms=", elapsed,
                  "candidate=", repr(candidates[0]["latex"]), flush=True)

    return {
        "kind": "mac_to_tang_synthetic_formula_e2e_v016",
        "not_real_exam": True,
        "not_semantic_accuracy": True,
        "cloud_vlm_used": False,
        "overall_quality_verified": False,
        "samples": samples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:18916")
    args = parser.parse_args()
    result = run(args.url)
    folder = ROOT / "artifacts" / "vision"
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / "formula_e2e_v016.json"
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("Synthetic E2E evidence:", destination)


if __name__ == "__main__":
    main()
