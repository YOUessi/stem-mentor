"""Browser UI integration against real FastAPI TestClient, without Chromium network access.

Local/manual: python tests/browser/test_ui.py
Requires playwright Python and a local Chromium binary. This test is separate from CI
because GitHub Action's default runner does not install a browser.
"""
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[2]
SCREENSHOTS=Path(os.environ.get("STEM_MENTOR_SCREENSHOT_DIR",str(ROOT/"artifacts"/"browser")))
SCREENSHOTS.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"backend"))
from app.main import app


def page_with_backend(browser,client,viewport,errors):
    page=browser.new_page(viewport=viewport,device_scale_factor=1)
    page.on("pageerror",lambda err:errors.append(str(err)))
    html=(ROOT/"apps/web/index.html").read_text(encoding="utf8")
    html=html.replace('<link rel="stylesheet" href="/assets/styles.css" />','').replace('<script src="/assets/app.js" defer></script>','')
    page.set_content(html)
    page.evaluate("""() => {
        const store = new Map();
        Object.defineProperty(window,'localStorage',{configurable:true,value:{
            getItem:k=>store.has(k)?store.get(k):null,
            setItem:(k,v)=>store.set(k,String(v)),
            removeItem:k=>store.delete(k)
        }});
    }""")
    def forward(path,method,body):
        response=client.request(method,path,json=body if body else None)
        return {"ok":response.is_success,"status":response.status_code,"statusText":response.reason_phrase,"data":response.json()}
    page.expose_function("backendRequest",forward)
    page.evaluate("""() => { window.fetch = async (path,options={}) => {
        const response=await window.backendRequest(path,options.method||'GET',options.body?JSON.parse(options.body):null);
        return {ok:response.ok,status:response.status,statusText:response.statusText,
            json:async()=>response.data};
    } }""")
    page.add_style_tag(content=(ROOT/"apps/web/styles.css").read_text(encoding="utf8"))
    page.add_script_tag(content=(ROOT/"apps/web/app.js").read_text(encoding="utf8"))
    page.evaluate("document.dispatchEvent(new Event('DOMContentLoaded'))")
    page.locator("#problemTitle").get_by_text("两个定点与距离之比").wait_for(timeout=10000)
    return page


def run():
    with TemporaryDirectory() as tmp:
        os.environ["STEM_MENTOR_DB"]=str(Path(tmp)/"browser.sqlite3")
        with TestClient(app) as client, sync_playwright() as playwright:
            browser=playwright.chromium.launch(executable_path=os.environ.get("CHROMIUM_EXECUTABLE","/usr/bin/chromium"),headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
            errors=[]
            page=page_with_backend(browser,client,{"width":1510,"height":940},errors)
            page.locator('[data-mode="ANALYZE"]').click()
            page.locator("#studentInput").fill("我先梳理已知和目标")
            page.locator("#sendBtn").click()
            page.locator(".chat-row.teacher").last.wait_for()
            assert page.locator("#mindMap .map-node").count()>=1
            assert "一组点" in page.locator(".chat-row.teacher .bubble").last.inner_text()
            page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
            page.screenshot(path=str(SCREENSHOTS/"stem-mentor-workspace.png"),full_page=True)

            page.locator('[data-mode="INDEPENDENT"]').click()
            page.locator('button.selected[data-mode="INDEPENDENT"]').wait_for()
            page.locator("#studentInput").fill("我自己再试着建坐标")
            page.locator("#sendBtn").click()
            page.wait_for_function("document.querySelectorAll('.chat-row.teacher').length===2")
            assert "不会提前" in page.locator(".chat-row.teacher .bubble").last.inner_text()

            page.locator("#problemSelect").select_option("ellipse-tangent")
            page.locator("#startBtn").click()
            page.locator("#studentInput").fill("判别式法比较繁琐")
            page.locator("#sendBtn").click()
            page.wait_for_function("document.querySelectorAll('.chat-row.teacher').length===1")
            page.once("dialog",lambda d:d.accept("这次我发现应该比较切点条件"))
            page.locator("#completeBtn").click()
            page.wait_for_function("document.querySelector('#sessionStatus').textContent.includes('已经记录')")
            page.locator("#reviewSuggestion").wait_for(state="visible")

            page.locator("#problemSelect").select_option("hyperbola-tangent")
            page.locator("#startBtn").click()
            page.locator('[data-tool="recall"]').click()
            page.wait_for_function("document.querySelector('.chat-row.teacher') !== null")
            assert "椭圆上一点的切线" in page.locator(".chat-row.teacher .bubble").last.inner_text()

            page.locator('[data-view="history"]').click()
            page.locator("#historyList .item-card").first.wait_for()
            assert "真实学习记录" in page.locator("#historyList").inner_text()
            page.locator('[data-view="review"]').click()
            page.locator("#reviewList .item-card").first.wait_for()
            page.locator("#reviewList .item-card").first.locator("input").fill("垂直平分线")
            page.locator("#reviewList .item-card").first.locator("button").click()
            page.locator("#reviewList .item-card").first.get_by_text("本次已记录").wait_for()
            page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
            page.screenshot(path=str(SCREENSHOTS/"stem-mentor-reviews.png"),full_page=True)
            page.locator('[data-view="methods"]').click()
            page.locator("#methodList .item-card").first.wait_for()
            assert page.locator("#methodList .item-card").count()>=4
            page.locator("#methodQuery").fill("切线")
            page.locator("#methodSearchBtn").click()
            page.wait_for_function("document.querySelectorAll('#methodList .item-card').length>=1")
            assert "切线" in page.locator("#methodList").inner_text()
            assert page.locator("#thinkingStage").count()==1
            assert page.locator("#mathVerifyBtn").count()==1
            page.locator('[data-view="workspace"]').click()
            # This check needs GUIDE; previous steps deliberately left the tutor in INDEPENDENT.
            page.locator('[data-mode="GUIDE"]').click()
            page.locator('button.selected[data-mode="GUIDE"]').wait_for()
            page.locator("#problemSelect").select_option("inequality-bridge")
            page.locator("#startBtn").click()
            page.locator("#thinkingStage").select_option("STUCK")
            page.locator("#studentInput").fill("我已经合并成一个分式")
            page.locator("#sendBtn").click()
            page.wait_for_function("document.querySelector('.chat-row.teacher') !== null")
            assert "目标" in page.locator(".chat-row.teacher .bubble").last.inner_text() or "结论" in page.locator(".chat-row.teacher .bubble").last.inner_text()
            page.locator(".math-check summary").click()
            page.locator("#mathLeft").fill("1/x+1/y")
            page.locator("#mathRight").fill("1/(x*y)")
            page.locator("#mathVerifyBtn").click()
            page.wait_for_function("document.querySelector('#mathResult').textContent.length > 5")
            assert "EQUIVALENT_ON_DOMAIN" in page.locator("#mathResult").inner_text()

            mobile=page_with_backend(browser,client,{"width":390,"height":844},errors)
            mobile.locator("#toast").evaluate("(node) => { node.hidden=true; }")
            mobile.screenshot(path=str(SCREENSHOTS/"stem-mentor-mobile.png"),full_page=True)
            assert mobile.evaluate("document.body.scrollWidth <= window.innerWidth + 2")
            assert errors==[],f"Browser runtime errors: {errors}"
            browser.close()
            print("PASS: Chromium real DOM: modes/turns/stages/real memory/review/methods/mobile")
            print("PASS: Browser page errors: 0")

if __name__=="__main__":
    run()
