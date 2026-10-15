"""Independent real-Chrome smoke test for the restored green STEM Mentor v0.5 UI."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
URL=os.environ.get("STEM_MENTOR_URL","http://127.0.0.1:8000")
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=ROOT/"artifacts/ui"
OUT.mkdir(parents=True,exist_ok=True)

def run():
    result={"theme":"green v0.5","screens":[],"interaction_checks":[],"page_errors":[]}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=CHROME,
          args=["--disable-gpu","--no-first-run","--disable-extensions"])
        for width,height in [(1440,1000),(768,1024),(390,844)]:
            ctx=browser.new_context(viewport={"width":width,"height":height},
                                    locale="zh-CN",device_scale_factor=1)
            page=ctx.new_page()
            page.on("pageerror",lambda err:result["page_errors"].append(str(err)))
            assert page.goto(URL,wait_until="networkidle").ok
            page.locator("#problemTitle").get_by_text("两个定点与距离之比").wait_for()
            assert page.locator(".brand-mark").inner_text()=="∴"
            assert page.locator("#commandPalette").count()==0
            assert page.locator("#chat").count()==1
            assert page.locator(".mode").count()==3
            css=page.evaluate("""() => ({
              bg: getComputedStyle(document.body).backgroundColor,
              sidebar: getComputedStyle(document.querySelector(".sidebar")).backgroundColor,
              horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 2
            })""")
            assert css["bg"]=="rgb(247, 248, 245)",(width,css)
            assert css["sidebar"]=="rgb(255, 255, 255)",(width,css)
            assert not css["horizontalOverflow"],(width,css)
            page.screenshot(path=str(OUT/f"green-restored-{width}.png"),full_page=True)
            result["screens"].append({"width":width,"height":height,"background":css["bg"]})
            if width==1440:
                page.locator('[data-mode="ANALYZE"]').click()
                page.locator('button.selected[data-mode="ANALYZE"]').wait_for()
                result["interaction_checks"].append("mode switch")
                page.locator("#studentInput").fill("我准备先分析固定点与动点之间的关系")
                page.locator("#sendBtn").click()
                page.locator(".chat-row.teacher").first.wait_for()
                assert page.locator(".map-node").count()>0
                result["interaction_checks"].append("student reasoning and feedback")
                page.locator('[data-view="methods"]').click()
                page.locator("#methodList .item-card").first.wait_for()
                assert page.locator("#methodList .item-card").count()>=8
                result["interaction_checks"].append("method library")
                page.locator('[data-view="review"]').click()
                page.locator("#reviewList .item-card").first.wait_for()
                result["interaction_checks"].append("exam micro-knowledge")
                page.locator('[data-view="workspace"]').click()
                page.locator("#problemSelect").select_option("ellipse-tangent")
                page.locator("#startBtn").click()
                page.locator("#problemTitle").get_by_text("椭圆上一点的切线").wait_for()
                result["interaction_checks"].append("start another exercise")
            ctx.close()
        browser.close()
    assert not result["page_errors"],result["page_errors"]
    (OUT/"green-restored-smoke.json").write_text(
      json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("Restored green UI passed Chrome:",result)

if __name__=="__main__":
    run()
