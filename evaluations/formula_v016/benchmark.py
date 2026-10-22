"""Reproducible formula-image benchmark. No ground-truth leakage into model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics
import time
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "frozen_manifest.json"


def norm_latex(value: str) -> str:
    """Typographic normalization only, NOT mathematical equivalence."""
    import re
    out = re.sub(r"\s+", "", value)
    for command in (r"\left", r"\right", r"\displaystyle", r"\textstyle"):
        out = out.replace(command, "")
    for command in (r"\,", r"\;", r"\!", r"\:", r"\quad", r"\qquad"):
        out = out.replace(command, "")
    return out


def edit_distance(a: str, b: str) -> int:
    previous = list(range(len(b) + 1))
    for i, char in enumerate(a, 1):
        current = [i]
        for j, other in enumerate(b, 1):
            current.append(min(
                previous[j] + 1,
                current[-1] + 1,
                previous[j - 1] + (char != other),
            ))
        previous = current
    return previous[-1]


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ranked = sorted(values)
    rank = (len(ranked) - 1) * q
    low = int(rank)
    high = min(low + 1, len(ranked) - 1)
    return round(ranked[low] + (ranked[high] - ranked[low]) * (rank - low), 2)


def summarize(samples: list[dict]) -> dict:
    success = [x for x in samples if x["error"] is None]
    elapsed = [x["elapsed_ms"] for x in success]
    return {
        "samples": len(samples),
        "recognized": len(success),
        "inference_failures": len(samples) - len(success),
        "strict_exact_count": sum(x["strict_exact"] for x in success),
        "normalized_exact_count": sum(x["normalized_exact"] for x in success),
        "strict_exact_rate_all": round(sum(x["strict_exact"] for x in success) / len(samples), 4) if samples else None,
        "normalized_exact_rate_all": round(sum(x["normalized_exact"] for x in success) / len(samples), 4) if samples else None,
        "character_error_rate": (
            round(sum(x["char_errors"] for x in success) /
                  max(1, sum(x["truth_length"] for x in success)), 4)
            if success else None),
        "inference_ms_p50": percentile(elapsed, 0.5),
        "inference_ms_p95": percentile(elapsed, 0.95),
        "inference_ms_max": max(elapsed, default=None),
    }


def bench(images: Path, out: Path, model_name: str, device: str) -> dict:
    raw = MANIFEST.read_bytes()
    manifest = json.loads(raw)
    index = json.loads((images / "image_index.json").read_text())
    manifest_sha = hashlib.sha256(raw).hexdigest()
    if index.get("manifest_sha256") != manifest_sha:
        raise RuntimeError("Manifest/image-index mismatch; rerender the frozen suite")
    index_files = {x["id"]: x for x in index["samples"]}
    cases = manifest["cases"]
    for item in cases:
        file_info = index_files[item["id"]]
        file = images / file_info["file"]
        if hashlib.sha256(file.read_bytes()).hexdigest() != file_info["sha256"]:
            raise RuntimeError("Image SHA mismatch: " + item["id"])

    import paddle
    from paddleocr import FormulaRecognition
    startup = time.perf_counter()
    engine = FormulaRecognition(model_name=model_name, device=device)
    startup_ms = round((time.perf_counter() - startup) * 1000, 2)
    print(f"Loaded {model_name}, device={paddle.device.get_device()}, startup_ms={startup_ms}", flush=True)
    measurements: list[dict] = []
    for idx, item in enumerate(cases, start=1):
        path = images / index_files[item["id"]]["file"]
        t0 = time.perf_counter()
        prediction, error = "", None
        try:
            response = engine.predict(input=str(path), batch_size=1)
            first = next(iter(response), None)
            payload = first.json if first is not None else {}
            prediction = payload.get("res", {}).get("rec_formula", "")
            if not isinstance(prediction, str) or not prediction.strip():
                raise ValueError("Model returned empty formula")
        except Exception as exc:
            error = type(exc).__name__ + ": " + str(exc)[:230]
        ms = round((time.perf_counter() - t0) * 1000, 2)
        normalized_pred = norm_latex(prediction)
        normalized_truth = norm_latex(item["latex"])
        entry = {
            "id": item["id"], "family": item["family"],
            "render": item["render"], "latex_truth": item["latex"],
            "latex_prediction": prediction, "elapsed_ms": ms,
            "error": error, "strict_exact": error is None and prediction == item["latex"],
            "normalized_exact": error is None and normalized_pred == normalized_truth,
            "char_errors": edit_distance(normalized_pred, normalized_truth) if error is None else None,
            "truth_length": len(normalized_truth),
        }
        measurements.append(entry)
        print(f"{idx:02d}/{len(cases)} {item['id']} {item['family']} {item['render']} "
              f"exact={entry['normalized_exact']} ms={ms} err={error or 'none'}", flush=True)
        # Save a partial result with explicit completed_count and no inflated denominator.
        if idx % 5 == 0:
            out.parent.mkdir(parents=True, exist_ok=True)
            (out.parent / "in_progress.json").write_text(json.dumps({
                "completed_count": len(measurements),
                "expected_count": len(cases),
                "samples": measurements,
            }, ensure_ascii=False, indent=2) + "\n")

    groups = defaultdict(list)
    for sample in measurements:
        groups["family:" + sample["family"]].append(sample)
        groups["render:" + sample["render"]].append(sample)
    result = {
        "schema": "formula-benchmark-v016-1",
        "provenance": manifest["provenance"],
        "warning": "Synthetic exam-style images only; NOT measured on real exams, manuscripts or students",
        "manifest_sha256": manifest_sha,
        "render_engine": index["render_engine"],
        "model_name": model_name,
        "paddle_version": paddle.__version__,
        "device": str(paddle.device.get_device()),
        "host": platform.platform(),
        "model_startup_ms": startup_ms,
        "metrics": summarize(measurements),
        "group_metrics": {k: summarize(v) for k, v in sorted(groups.items())},
        "samples": measurements,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["metrics"], indent=2), flush=True)
    print(f"Wrote evidence: {out}", flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", type=Path, default=HERE / "generated")
    parser.add_argument("--out", type=Path, default=HERE / "local_results.json")
    parser.add_argument("--model", default="PP-FormulaNet_plus-M")
    parser.add_argument("--device", default="gpu:0")
    args = parser.parse_args()
    bench(args.images, args.out, args.model, args.device)
