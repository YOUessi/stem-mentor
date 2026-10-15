"""Real Chrome checks for premium Study Studio UI (macOS, no LLM API)."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
URL=os.environ.get("STEM_MENTOR_URL","http://127.0.0.1:8000")
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ART=ROOT/"artifacts"/"ui"
ART.mkdir(parents=True,exist_ok=True)

def assert_no_overflow(page,label):
    dimensions=page.evaluate("""() => ({
      scroll: document.documentElement.scrollWidth,
      viewport: window.innerWidth,
      body: document.body.scrollWidth,
      width: document.documentElement.clientWidth
    })""")
    assert dimensions["scroll"]<=dimensions["viewport"]+2,(label,dimensions)
    return dimensions

def run():
    findings={"desktop":{},"responsive":{},"interactions":{},"errors":[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=CHROME,
                                  args=["--disable-gpu","--no-first-run","--disable-extensions"])
        context=browser.new_context(viewport={"width":1440,"height":900},locale="zh-CN",device_scale_factor=1)
        page=context.new_page()
        page.on("pageerror",lambda exc:findings["errors"].append(str(exc)))
        assert page.goto(URL,wait_until="networkidle").ok
        assert page.locator("#problemTitle").inner_text()!="读取题目中…"
        assert page.locator("#toast").is_hidden(), "No initial toast should cover the exercise"
        findings["desktop"]["dimensions"]=assert_no_overflow(page,"desktop")
        assert page.locator(".mode.selected").count()==1
        page.screenshot(path=str(ART/"study-studio-v06-desktop.png"),full_page=True)

        page.locator("#commandTrigger").click()
        assert page.locator("#commandPalette").is_visible()
        page.locator("#commandSearch").fill("数学方法库")
        page.keyboard.press("Enter")
        assert page.locator("#methods").is_visible()
        assert not page.locator("#commandPalette").is_visible()
        findings["interactions"]["command_palette"]=True
        page.keyboard.press("Meta+k")
        assert page.locator("#commandPalette").is_visible()
        page.keyboard.press("Escape")
        assert not page.locator("#commandPalette").is_visible()
        page.locator('button[data-view="workspace"]').click()
        page.locator('button[data-mode="ANALYZE"]').click()
        page.wait_for_function('document.querySelector(\'[data-mode="ANALYZE"]\').classList.contains("selected")')
        findings["interactions"]["mode_switch"]=True

        # Never send secret/private students. Only synthetic draft and curated math.
        draft="我先观察有哪些固定点和动点，再思考哪些关系保持不变。"
        page.locator("#studentInput").fill(draft)
        page.reload(wait_until="networkidle")
        assert page.locator("#studentInput").input_value()==draft
        findings["interactions"]["draft_restored"]=True
        page.locator("#sendBtn").click()
        page.locator(".chat-row.teacher").last.wait_for()
        assert page.locator("#studentInput").input_value()==""
        assert page.locator(".map-node").count()>=1
        findings["interactions"]["submitted_and_timeline"]=True
        assert "已记录" not in page.locator("#sessionStatus").inner_text()

        # Keyboard-accessible split handle, persists layout.
        grip=page.locator("#splitHandle")
        before=int(grip.get_attribute("aria-valuenow"))
        grip.focus();page.keyboard.press("ArrowRight")
        after=int(grip.get_attribute("aria-valuenow"))
        assert after>before,(before,after)
        page.reload(wait_until="networkidle")
        assert int(page.locator("#splitHandle").get_attribute("aria-valuenow"))==after
        findings["interactions"]["split_resizes_and_persists"]=True
        page.screenshot(path=str(ART/"study-studio-v06-conversation.png"),full_page=True)
        context.close()
        for width,height in [(390,844),(768,1024),(1024,900),(1280,900)]:
            mobile=browser.new_context(viewport={"width":width,"height":height},
                                      device_scale_factor=1,locale="zh-CN",
                                      is_mobile=width<=390,has_touch=width<=390)
            pg=mobile.new_page()
            pg.on("pageerror",lambda exc:findings["errors"].append(str(exc)))
            assert pg.goto(URL,wait_until="networkidle").ok
            dims=assert_no_overflow(pg,str(width))
            findings["responsive"][str(width)]=dims
            assert pg.locator("#problemTitle").is_visible()
            if width==390:
                pg.screenshot(path=str(ART/"study-studio-v06-mobile.png"),full_page=True)
                pg.locator('button[data-mode="INDEPENDENT"]').click()
                pg.wait_for_function('document.querySelector(\'[data-mode="INDEPENDENT"]\').classList.contains("selected")')
                assert pg.locator("#studentInput").count()==1
                findings["interactions"]["mobile_mode_switch"]=True
            mobile.close()
        browser.close()
    assert not findings["errors"],findings["errors"]
    path=ART/"study-studio-v06-browser-results.json"
    path.write_text(json.dumps(findings,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("Chrome UI checks passed:",json.dumps({"responsive":list(findings["responsive"]),"interactions":findings["interactions"],"errors":findings["errors"]},ensure_ascii=False))
    return findings

if __name__=="__main__":
    run()
