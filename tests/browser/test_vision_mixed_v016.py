"""Mac-only Chrome check for focused math OCR crop + explicit human approval."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
URL = os.getenv("STEM_MENTOR_URL", "http://127.0.0.1:18916")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def main():
    with tempfile.TemporaryDirectory(prefix="stem-mixed-ui-") as temp:
        picture = Path(temp) / "mixed-question.png"
        img = Image.new("RGB", (1250, 270), "white")
        font = ImageFont.truetype(
            "/System/Library/Fonts/Supplemental/Arial.ttf", 49)
        ImageDraw.Draw(img).text(
            (35, 75), "Question: x^2 + 2x + 1 = (x+1)^2",
            font=font, fill="black")
        img.save(picture)

        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=CHROME, headless=True)
            try:
                for viewport in (
                    {"width": 1280, "height": 860},
                    {"width": 390, "height": 844},
                ):
                    page = browser.new_page(viewport=viewport)
                    page_errors = []
                    page.on("pageerror", lambda error: page_errors.append(str(error)))
                    page.goto(URL + "/vision", wait_until="domcontentloaded")
                    page.locator("#questionImage").set_input_files(str(picture))
                    assert not page.locator("#sendFormula").is_checked()
                    assert not page.locator("#allowVlm").is_checked()
                    page.locator("#runRecognition").click()
                    page.wait_for_function(
                        "document.querySelector('#routeInfo').textContent.includes('已精确定位')",
                        timeout=20000,
                    )
                    page.wait_for_function(
                        "Array.from(document.querySelectorAll('.formula-crop'))"
                        ".some(c => c.width > 100 && c.height > 10)",
                        timeout=10000,
                    )
                    assert "Question:" in page.locator("#questionStem").input_value()
                    assert "x^2" in page.locator(".formula-card small").first.inner_text()
                    assert not page.locator("#createPaper").is_enabled()
                    assert "数学 OCR" in page.locator("#engineStatus").inner_text()
                    assert not page_errors, page_errors

                    # Explicit edit/confirmation before a simulation session is created.
                    page.locator("#questionStem").fill(
                        "已知 x²+2x+1=(x+1)²，说明恒等式成立。")
                    page.locator(".formula-input").first.fill(
                        r"x^{2}+2x+1=(x+1)^{2}")
                    page.locator("#confirmQuestion").click()
                    page.wait_for_function(
                        "!document.querySelector('#createPaper').disabled",
                        timeout=15000,
                    )
                    label = "desktop" if viewport["width"] > 500 else "mobile"
                    out = ROOT / "artifacts" / "vision"
                    out.mkdir(parents=True, exist_ok=True)
                    page.screenshot(
                        path=str(out / ("mixed-v016-" + label + ".png")),
                        full_page=True,
                    )
                    page.locator("#createPaper").click()
                    page.wait_for_url("**/ipad/study?session=*", timeout=15000)
                    page.wait_for_function(
                        "document.querySelector('#paperProblemText')"
                        ".textContent.includes('已知')",
                        timeout=15000,
                    )
                    assert not page_errors, page_errors
                    page.close()
                print("PASS v0.16 desktop+mobile: formula crop preview → manual edit → iPad", flush=True)
            finally:
                browser.close()


if __name__ == "__main__":
    main()
