"""Check the manifest stays frozen and the scoring denominator includes failures."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVAL = ROOT / "evaluations" / "formula_v016"
MANIFEST_SHA256 = "836d4c0a0ff7134a51443b5e6ea7cfd43554a714fe827df8e11d4c509eadf382"


def load_module():
    path = EVAL / "benchmark.py"
    spec = importlib.util.spec_from_file_location("formula_bench_v016", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_freeze_and_provenance():
    raw = (EVAL / "frozen_manifest.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256
    suite = json.loads(raw)
    assert "NOT_real_exam_photos" in suite["provenance"]
    assert len(suite["cases"]) == 22
    assert len({c["id"] for c in suite["cases"]}) == 22
    assert len({c["family"] for c in suite["cases"]}) >= 12
    assert {"clean", "lowcontrast", "blur", "rotate"} <= {
        x["render"] for x in suite["cases"]}


def test_latex_normalization_is_typographic_not_symbolic():
    benchmark = load_module()
    assert benchmark.norm_latex(r"\left( \frac{x}{2} \right)") == r"(\frac{x}{2})"
    assert benchmark.norm_latex(r"\frac{1}{3}") != benchmark.norm_latex(r"0.333333")
    assert benchmark.edit_distance("abc", "axc") == 1
    assert benchmark.edit_distance("", "abc") == 3


def test_scoring_includes_failures_in_denominator():
    benchmark = load_module()
    samples = [
        {"strict_exact": True, "normalized_exact": True,
         "error": None, "elapsed_ms": 10.0, "char_errors": 0, "truth_length": 4},
        {"strict_exact": False, "normalized_exact": False,
         "error": "inference failed", "elapsed_ms": 0, "char_errors": None, "truth_length": 4},
    ]
    s = benchmark.summarize(samples)
    assert s["recognized"] == 1
    assert s["inference_failures"] == 1
    assert s["strict_exact_rate_all"] == .5
    assert s["inference_ms_p50"] == 10.0
