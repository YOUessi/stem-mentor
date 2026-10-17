"""Real macOS Chrome end-to-end study tools, no LLM API and no external CDN."""
import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
BASE=os.environ.get("STEM_MENTOR_URL","http://127.0.0.1:8000")
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=ROOT/"artifacts"/"ui"
OUT.mkdir(parents=True,exist_ok=True)

def run():
    results={"tests":[],"page_errors":[],"external_requests":[]}
    with sync_playwright() as engine:
        browser=engine.chromium.launch(headless=True,executable_path=CHROME,
               args=["--disable-extensions","--no-first-run","--disable-gpu"])
        context=browser.new_context(viewport={"width":1440,"height":1000},locale="zh-CN")
        page=context.new_page()
        page.on("pageerror",lambda e:results["page_errors"].append(str(e)))
        page.on("request",lambda r:results["external_requests"].append(r.url)
                if not r.url.startswith(BASE) else None)
        response=page.goto(BASE,wait_until="networkidle")
        assert response.ok
        page.wait_for_function("() => document.querySelector('#problemFormula')?.hidden === false")
        page.wait_for_selector("#problemFormula mjx-container svg",timeout=18000)
        assert page.locator("#geometryPanel").is_visible()
        assert page.locator("meta[name='theme-color']").get_attribute("content")=="#174938"
        assert page.locator(".brand-mark").inner_text()=="∴"
        assert "font" not in " ".join(results["external_requests"]).lower()
        results["tests"].append("MathJax offline SVG formula and original green theme")

        geometry=page.locator("#geometryDetails")
        geometry.locator("summary").click()
        assert geometry.get_attribute("open") is not None
        first=page.locator("#geometryReadout").inner_text()
        assert "PA / PB" in first
        point=page.locator("#geometrySvg [data-drag-point=true]").first
        point.scroll_into_view_if_needed()
        rect=point.bounding_box()
        assert rect
        xx=rect["x"]+rect["width"]/2
        yy=rect["y"]+rect["height"]/2
        page.mouse.move(xx,yy)
        page.mouse.down()
        page.mouse.move(xx+95,yy-32,steps=7)
        page.mouse.up()
        changed=page.locator("#geometryReadout").inner_text()
        assert changed!=first,(first,changed)
        assert page.locator("#geometrySvg .geotrace").count()==0
        results["tests"].append("Free exploration changes actual distance readout without giving locus")

        page.locator("#geometryConstrain").click()
        page.locator("#geometryReadout").get_by_text("PA / PB",exact=False).wait_for()
        restricted=page.locator("#geometryReadout").inner_text()
        match=re.search(r"PA / PB ≈ ([0-9.]+)",restricted)
        assert match and abs(float(match.group(1))-2)<.06,restricted
        page.locator("#geometrySvg [data-drag-point=true]").first.scroll_into_view_if_needed()
        drag=page.locator("#geometrySvg [data-drag-point=true]").first.bounding_box()
        center=(drag["x"]+drag["width"]/2,drag["y"]+drag["height"]/2)
        page.mouse.move(*center)
        page.mouse.down()
        page.mouse.move(center[0]-38,center[1]+35,steps=9)
        page.mouse.up()
        assert page.locator("#geometrySvg .geotrace").count()>=1
        assert "圈" not in page.locator("#geometryIntro").inner_text()
        results["tests"].append("Opt-in condition exploration produces only self-traced path")

        editor=page.locator("#studentInput")
        editor.fill("我先列出距离关系，尝试公式：\\(\\frac{x+y}{xy}\\)")
        page.locator("#mathPreviewDetails summary").click()
        page.wait_for_selector("#studentMathPreview mjx-container svg",timeout=17000)
        original_draft=page.locator("#studentInput").input_value()
        page.reload(wait_until="networkidle")
        page.wait_for_function("(expected) => document.querySelector('#studentInput')?.value===expected",
                               arg=original_draft)
        assert page.locator("#studentInput").input_value()==original_draft
        page.locator("#mathPreviewDetails summary").click()
        page.wait_for_selector("#studentMathPreview mjx-container svg",timeout=17000)
        assert page.locator("#studentMathPreview a").count()==0
        results["tests"].append("User formula typesetting stays local and separate from grading")

        stages=[("FORWARD","先从两个定点和动点的关系正向分析"),
                ("STUCK","我算到这里卡住了，不知道怎样继续"),
                ("BACKWARD","我考虑从题目求轨迹这个目标倒推")]
        for idx,(stage,thought) in enumerate(stages):
            page.locator("#thinkingStage").select_option(stage)
            page.locator("#studentInput").fill(thought)
            page.locator("#sendBtn").click()
            page.wait_for_function("n => document.querySelectorAll('.chat-row.teacher').length >= n",arg=idx+1)
            page.wait_for_function("n => document.querySelectorAll('.mind-timeline .map-node').length >= n",arg=idx+1)
        assert page.locator("#mindMap svg .mind-vertex").count()==5
        assert "数学正确性尚未验证" in page.locator("#mindMapDetail").inner_text() if not page.locator("#mindMapDetail").is_hidden() else True
        results["tests"].append("Reasoning graph tracks FORWARD, STUCK and BACKWARD without teacher solution")

        page.locator("#thoughtLinkLabel").fill("我想把正向条件与逆向目标联系起来")
        page.get_by_role("button",name="连接我的两步思路").click()
        page.locator('.mind-vertex[data-id="student-step-1"]').click()
        page.locator('.mind-vertex[data-id="student-step-3"]').click()
        page.wait_for_function("document.querySelectorAll('.mind-user-link').length === 1")
        assert "待验证" in page.locator("#mindMap").inner_text()
        page.evaluate("window.scrollTo(0,0)")
        page.wait_for_timeout(140)
        page.screenshot(path=str(OUT/"green-tools-v07-desktop.png"),full_page=True)
        page.reload(wait_until="networkidle")
        page.wait_for_selector(".mind-user-link",timeout=16000)
        assert page.locator("#mindMap svg .mind-vertex").count()==5
        results["tests"].append("Student-proposed link persists through reload and remains unverified")

        page.locator("#problemSelect").select_option("ellipse-focus")
        page.locator("#startBtn").click()
        page.wait_for_function("() => document.querySelector('#problemTitle').textContent.includes('椭圆定义')")
        page.wait_for_function("() => document.querySelector('#geometryPanel').hidden === false")
        page.locator("#geometryDetails summary").click()
        assert "PA + PB" in page.locator("#geometryReadout").inner_text()
        assert page.locator("#geometrySvg .geocurve").count()==0
        page.locator("#geometryConstrain").click()
        match=re.search(r"PA \+ PB ≈ ([0-9.]+)",page.locator("#geometryReadout").inner_text())
        assert match and abs(float(match.group(1))-10)<.06
        page.locator("#geometryClear").click()
        assert page.locator("#geometrySvg .geotrace").count()==0
        results["tests"].append("Ellipse foci exploration is controlled without auto-drawing answer")

        page.locator("#problemSelect").select_option("geometric-sum")
        page.locator("#startBtn").click()
        page.wait_for_function("() => document.querySelector('#geometryPanel').hidden")
        page.wait_for_selector("#problemFormula mjx-container svg",timeout=15000)
        results["tests"].append("Non-geometric task retains rendered givens without irrelevant canvas")

        context.close()
        mobile=browser.new_context(viewport={"width":390,"height":844},locale="zh-CN",
                   is_mobile=True,has_touch=True,device_scale_factor=1)
        pm=mobile.new_page()
        pm.on("pageerror",lambda e:results["page_errors"].append(str(e)))
        assert pm.goto(BASE,wait_until="networkidle").ok
        pm.wait_for_selector("#problemFormula mjx-container svg",timeout=16000)
        dims=pm.evaluate("""() => ({
          viewport:innerWidth, scroll:document.documentElement.scrollWidth
        })""")
        assert dims["scroll"]<=dims["viewport"]+2,dims
        pm.locator("#geometryDetails summary").click()
        assert pm.locator("#geometrySvg").is_visible()
        assert pm.locator(".mind-mobile-anchors").is_visible()
        assert not pm.locator(".mind-graph-canvas").is_visible()
        pm.screenshot(path=str(OUT/"green-tools-v07-mobile.png"),full_page=True)
        results["tests"].append("390px mobile: green layout, formula and geometry visible without horizontal overflow")
        mobile.close()
        browser.close()
    assert results["page_errors"]==[],results["page_errors"]
    assert results["external_requests"]==[],results["external_requests"]
    results["count"]=len(results["tests"])
    (OUT/"green-tools-v07-browser-results.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("GREEN v0.7 Chrome test:",results["count"],"passed; page errors:",len(results["page_errors"]),
          "; external requests:",len(results["external_requests"]))

if __name__=="__main__":
    run()
