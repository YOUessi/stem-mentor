"""Real Chrome UI against Mac FastAPI with mocked OCR (no GPU needed).

Validates v0.17 quality warnings, safe DOM text rendering, multi-formula
review, manual confirmation and existing /ipad/study handoff.
"""
from __future__ import annotations
import io
import json
import os
import tempfile
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


URL = os.environ.get("STEM_MENTOR_URL", "http://127.0.0.1:18917")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT = Path(__file__).resolve().parents[2]


def draft():
    return {
        "pipeline": "HYBRID_VISION_V016",
        "stem": "已知 x^2=1，y^2=4，求解",
        "expressions": [
            {
                "id": "expr-1-1", "latex": r"x^{\prime}2=1",
                "raw_text": "x^2=1", "bbox": [.1,.2,.2,.18],
                "bbox_source": "apple_vision_substring", "source": "formula_ocr",
                "quality": {
                    "state": "suspect", "mathematically_verified": False,
                    "warnings": [{
                        "code": "power_vs_prime",
                        "message": "原文包含 ^，但结果含 prime/wedge，可能把幂次识别成撇号或逻辑运算。",
                    }],
                },
                "verified": False,
            },
            {
                "id": "expr-1-2", "latex": r"y^{2}=4",
                "raw_text": "y^2=4", "bbox": [.55,.2,.2,.18],
                "bbox_source": "apple_vision_substring", "source": "formula_ocr",
                "quality": {"state": "unverified", "warnings": [],
                            "mathematically_verified": False},
                "verified": False,
            },
        ],
        "routing": {"local_ocr": "ready", "formula_candidates": 2,
                    "focused_formula_regions": 2,
                    "formula_ocr": {"ready": 2},
                    "vlm": "skipped_not_needed"},
        "uncertain_fields": ["formula_has_detected_anomalies"],
        "math_verified": False,
        "needs_human_review": True,
        "confirmed": False,
        "diagram": {"relations": []},
    }


def main():
    with tempfile.TemporaryDirectory(prefix="mentor-risk-ui-") as temp:
        path = Path(temp) / "test.png"
        Image.new("RGB", (1200, 280), "white").save(path)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=CHROME, headless=True)
            try:
                for size in ({"width": 1280, "height": 900},
                             {"width": 390, "height": 844}):
                    page = browser.new_page(viewport=size)
                    errors = []
                    page.on("pageerror", lambda x: errors.append(str(x)))
                    page.route("**/api/vision/recognize",
                        lambda route: route.fulfill(status=200,
                            content_type="application/json",
                            body=json.dumps(draft(), ensure_ascii=False)))
                    page.goto(URL + "/vision", wait_until="domcontentloaded")
                    page.locator("#questionImage").set_input_files(str(path))
                    page.locator("#runRecognition").click()
                    page.locator(".formula-card").first.wait_for()
                    assert page.locator(".formula-card").count() == 2
                    assert page.locator(".formula-risk strong").count() == 1
                    assert "幂次" in page.locator(".formula-risk").first.inner_text()
                    assert "1 处公式识别风险" in page.locator("#status").inner_text()
                    assert "2 处已精确定位" in page.locator("#routeInfo").inner_text()
                    page.wait_for_function(
                        "Array.from(document.querySelectorAll('.formula-crop'))"
                        ".every(x => x.width > 0 && x.height > 0)",
                        timeout=10000)
                    assert not page.locator("#createPaper").is_enabled()
                    page.locator(".formula-input").first.fill(r"x^{2}=1")
                    assert page.locator(".formula-risk[data-edited=true]").count() == 1
                    page.locator("#confirmQuestion").click()
                    page.wait_for_function(
                        "!document.querySelector('#createPaper').disabled",
                        timeout=10000)
                    page.locator("#createPaper").click()
                    page.wait_for_url("**/ipad/study?session=*", timeout=15000)
                    page.wait_for_function(
                        "document.querySelector('#paperProblemText')"
                        ".textContent.includes('已知')", timeout=15000)
                    assert not errors, errors
                    page.close()
                print("PASS v0.17 Chrome desktop + mobile risk-review workflow")
            finally:
                browser.close()


if __name__ == "__main__":
    main()
