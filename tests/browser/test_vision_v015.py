"""Live Chrome UI check for photo OCR review -> iPad session (synthetic only).
Run with STEM_MENTOR_URL=http://127.0.0.1:<port> python tests/browser/test_vision_v015.py
"""
import os
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
URL = os.environ.get("STEM_MENTOR_URL", "http://127.0.0.1:18915")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = ROOT / "artifacts" / "vision"
OUT.mkdir(parents=True, exist_ok=True)


def sample_image(path):
    im = Image.new("RGB", (1100, 350), "white")
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 44)
    draw.text((35, 35), "Question: Given AB = AC", fill="black", font=font)
    draw.text((35, 135), "Prove AD is perpendicular to BC", fill="black", font=font)
    draw.text((35, 235), "x^2 + 2x + 1 = (x + 1)^2", fill="black", font=font)
    im.save(path)


def main():
    with tempfile.TemporaryDirectory(prefix="mentor-vision-ui-") as tmp:
        picture = Path(tmp) / "synthetic_math.png"
        sample_image(picture)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=CHROME, headless=True)
            try:
                for viewport in [{"width": 1360, "height": 900},
                                 {"width": 390, "height": 844}]:
                    page = browser.new_page(viewport=viewport)
                    errors = []
                    page.on("pageerror", lambda e: errors.append(str(e)))
                    page.goto(URL + "/vision", wait_until="domcontentloaded")
                    assert page.locator("h1").inner_text().startswith("拍下题目")
                    assert not page.locator("#allowVlm").is_checked()
                    assert not page.locator("#sendFormula").is_checked()
                    page.locator("#questionImage").set_input_files(str(picture))
                    page.locator("#runRecognition").click()
                    page.wait_for_function("!document.querySelector(\"#runRecognition\").disabled", timeout=30000)
                    stem = page.locator("#questionStem").input_value()
                    assert "AB" in stem and "AC" in stem, stem
                    assert not page.locator("#createPaper").is_enabled()
                    page.locator("#addFormula").click()
                    page.locator(".formula-input").last.fill(r"\frac{x^2+1}{2}")
                    page.locator(".latex-preview svg").last.wait_for(timeout=15000)
                    # Correct the maths manually: typed equation is not trusted as proof.
                    page.locator("#questionStem").fill(
                        "已知 AB=AC，D 为 BC 中点，求证 AD 垂直 BC。"
                    )
                    page.locator("#confirmQuestion").click()
                    page.wait_for_function("!document.querySelector(\"#createPaper\").disabled", timeout=15000)
                    page.screenshot(
                        path=str(OUT / ("vision-desktop.png" if viewport["width"] > 500
                                        else "vision-mobile.png")),
                        full_page=True,
                    )
                    page.locator("#createPaper").click()
                    page.wait_for_url("**/ipad/study?session=*", timeout=15000)
                    page.wait_for_function("document.querySelector(\"#paperProblemText\").textContent.includes(\"已知\")", timeout=15000)
                    assert not errors, errors
                    page.close()
                print("v0.15 Chrome desktop+mobile camera OCR/confirm/session flow passed")
            finally:
                browser.close()


if __name__ == "__main__":
    main()
