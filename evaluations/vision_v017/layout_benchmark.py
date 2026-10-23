"""Frozen Mac Apple Vision *formula-region* detection benchmark.

This evaluates OCR substring localization on project-authored synthetic printed
math lines. It NEVER measures GPU formula recognition, semantic correctness,
real past exam questions, handwriting, or actual iPad on-device OCR.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = HERE / "frozen_layout_manifest.json"
CJK_FONT = Path("/System/Library/Fonts/STHeiti Medium.ttc")
LATIN_FONT = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
SONGTI_FONT = Path("/System/Library/Fonts/Supplemental/Songti.ttc")


def load_cases(manifest_path: Path = MANIFEST):
    raw = manifest_path.read_bytes()
    info = json.loads(raw)
    if info["version"] not in ("v017_layout_synthetic", "v017_unseen_holdout_20261023"):
        raise ValueError("Unexpected frozen benchmark version")
    if info["provenance"] not in (
        "self_authored_printed_math_lines_only",
        "self_authored_synthetic_holdout_not_real_exam",
    ):
        raise ValueError("Unrecognized data provenance")
    ids = [case["id"] for case in info["cases"]]
    assert len(ids) == len(set(ids))
    return info["cases"], hashlib.sha256(raw).hexdigest()


def make_image(case: dict) -> tuple[bytes, list[list[float]]]:
    if not CJK_FONT.is_file() or not LATIN_FONT.is_file():
        raise RuntimeError("This benchmark needs actual Mac system fonts")
    contains_han = any(any("\u3400" <= ch <= "\u9fff" for ch in part)
                       for part, _ in case["parts"])
    requested_font = case.get("font")
    font_path = {"heiti": CJK_FONT, "songti": SONGTI_FONT,
                 "arial": LATIN_FONT}.get(requested_font,
                     CJK_FONT if contains_han else LATIN_FONT)
    font = ImageFont.truetype(str(font_path), 48)
    image = Image.new("RGB", (1650, 210), "white")
    draw = ImageDraw.Draw(image)
    position = 35.0
    truth: list[list[float]] = []
    for content, marked_formula in case["parts"]:
        if position + font.getlength(content) > 1600:
            raise ValueError("Frozen case too wide: " + case["id"])
        draw.text((position, 63), content, font=font, fill="black")
        if marked_formula:
            x0, y0, x1, y1 = draw.textbbox((position, 63), content, font=font)
            margin = 2
            truth.append([
                max(0, x0 - margin) / image.width,
                max(0, y0 - margin) / image.height,
                (x1 - x0 + 2 * margin) / image.width,
                (y1 - y0 + 2 * margin) / image.height,
            ])
        position += float(font.getlength(content))
    rendering = case.get("render", "clean")
    if rendering == "lowcontrast":
        image = ImageEnhance.Contrast(image).enhance(.53)
    elif rendering == "blur":
        image = image.filter(ImageFilter.GaussianBlur(.8))
    elif rendering != "clean":
        raise ValueError("Unsupported frozen image styling: " + rendering)
    output = io.BytesIO()
    image.save(output, "PNG")
    return output.getvalue(), truth


def intersection_over_union(a: list[float], b: list[float]) -> float:
    ax1, ay1, aw, ah = a
    bx1, by1, bw, bh = b
    ax2, ay2 = ax1 + aw, ay1 + ah
    bx2, by2 = bx1 + bw, by1 + bh
    width = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    height = max(0.0, min(ay2, by2) - max(ay1, by1))
    intersection = width * height
    union = aw * ah + bw * bh - intersection
    return intersection / union if union > 0 else 0


def score_boxes(truth: list[list[float]], predicted: list[list[float]],
                min_iou: float = .4) -> dict:
    """One-to-one match, penalizing oversized full-line detections."""
    used_t = set()
    used_p = set()
    matches: list[dict] = []
    edges = []
    for ti, true_box in enumerate(truth):
        for pi, pred_box in enumerate(predicted):
            iou = intersection_over_union(true_box, pred_box)
            width_ratio = pred_box[2] / max(1e-10, true_box[2])
            if iou >= min_iou and width_ratio <= 1.5:
                edges.append((iou, ti, pi))
    for iou, ti, pi in sorted(edges, reverse=True):
        if ti in used_t or pi in used_p:
            continue
        used_t.add(ti)
        used_p.add(pi)
        matches.append({"truth_index": ti, "prediction_index": pi,
                        "iou": round(iou, 4)})
    return {
        "tp": len(matches),
        "fp": len(predicted) - len(matches),
        "fn": len(truth) - len(matches),
        "matches": matches,
    }


def evaluate(binary: Path, image_dir: Path, manifest_path: Path = MANIFEST) -> dict:
    cases, manifest_sha = load_cases(manifest_path)
    if not binary.is_file():
        raise RuntimeError("Apple Vision OCR binary not found: " + str(binary))
    image_dir.mkdir(parents=True, exist_ok=True)
    data = []
    for case in cases:
        raw, target = make_image(case)
        path = image_dir / (case["id"] + ".png")
        path.write_bytes(raw)
        result = subprocess.run(
            [str(binary), str(path)],
            capture_output=True, text=True, timeout=30, check=True,
        )
        output = json.loads(result.stdout)
        spans = [span for line in output.get("lines", [])
                 for span in line.get("spans", [])]
        pred_boxes = [x["bbox"] for x in spans]
        matched = score_boxes(target, pred_boxes)
        item = {
            "id": case["id"],
            "kind": case["class"],
            "formula_truth_boxes": target,
            "formula_span_predictions": spans,
            "recognized_lines": [x.get("text", "") for x in output.get("lines", [])],
            "scoring": matched,
        }
        data.append(item)
        print(f"{case['id']} {case['class']}: "
              f"tp={matched['tp']} fp={matched['fp']} fn={matched['fn']}", flush=True)
    tp = sum(x["scoring"]["tp"] for x in data)
    fp = sum(x["scoring"]["fp"] for x in data)
    fn = sum(x["scoring"]["fn"] for x in data)
    return {
        "schema": "synthetic_apple_vision_inline_math_roi_v017",
        "provenance": "project_authored_synthetic_images_not_real_exam_or_handwriting",
        "manifest_sha256": manifest_sha,
        "scoring": {
            "min_iou": .4, "max_width_ratio": 1.5,
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(tp / (tp + fp), 4) if tp + fp else None,
            "recall": round(tp / (tp + fn), 4) if tp + fn else None,
        },
        "cases": data,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, default=ROOT /
                        "backend/native/.build/vision_ocr")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=ROOT /
                        "artifacts/vision/v017_layout_eval.json")
    parser.add_argument("--image-dir", type=Path, default=ROOT /
                        "artifacts/vision/v017_layout_cases")
    args = parser.parse_args()
    results = evaluate(args.binary, args.image_dir, args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print("FINAL:", json.dumps(results["scoring"]))
    print("Saved local evidence:", args.output)
