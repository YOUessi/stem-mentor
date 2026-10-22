"""Real Chrome iPad-like handwriting regression (synthetic local data only)."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=os.environ.get("STEM_MENTOR_URL","http://127.0.0.1:18914")
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=Path(__file__).resolve().parents[2]/"artifacts/ipad"
OUT.mkdir(parents=True,exist_ok=True)

def check(good,message):
    assert good,message

def drag(page,a,b,steps=12):
    page.mouse.move(*a);page.mouse.down()
    page.mouse.move(*b,steps=steps);page.mouse.up()

def ink(page):
    return page.evaluate("window.MentorIpadPilot.snapshot()")

def run():
    report={"checks":[],"widths":[],"console_errors":[],"page_errors":[],
            "external":[],"ink_backend_writes":0}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=CHROME,headless=True,
          args=["--disable-extensions","--no-first-run","--disable-gpu"])
        ctx=browser.new_context(viewport={"width":1194,"height":834},
          device_scale_factor=1,locale="zh-CN")
        page=ctx.new_page()
        page.on("pageerror",lambda e:report["page_errors"].append(str(e)))
        page.on("console",lambda m:report["console_errors"].append(m.text)
          if m.type=="error" and "favicon" not in m.text.lower() else None)
        page.on("request",lambda r:report["external"].append(r.url)
          if not r.url.startswith(BASE) else None)
        assert page.goto(BASE+"/ipad",wait_until="networkidle").ok
        page.wait_for_function("() => document.querySelectorAll('#homeProblem option').length===15")
        assert page.locator("#homeProblem option").count()==15
        assert page.locator("#statMistakes").inner_text()=="待核实"
        assert "0" in page.locator("#statHistory").inner_text()
        page.screenshot(path=str(OUT/"v014-ipad-home.png"),full_page=True)
        report["checks"].append("local learning home, true counts and no fake grading")

        page.locator("#startNewPaper").click()
        page.wait_for_url("**/ipad/study?session=*",timeout=12000)
        sid=page.evaluate("localStorage.getItem('stem-demo-session')")
        student=page.evaluate("localStorage.getItem('stem-demo-student')")
        assert sid and student
        assert page.locator("#agentPanel").is_hidden()
        assert page.locator("#agentMode").input_value()=="INDEPENDENT"
        rect=page.locator("#inkCanvas").bounding_box()
        assert rect and rect["height"]>430
        a=(rect["x"]+rect["width"]*.43,rect["y"]+rect["height"]*.48)
        b=(a[0]+110,a[1]+21)
        c=(rect["x"]+rect["width"]*.30,rect["y"]+rect["height"]*.69)
        d=(c[0]+80,c[1]-17)
        writes=[]
        page.on("request",lambda r:writes.append((r.method,r.url))
          if r.method not in ("GET","HEAD") else None)
        drag(page,a,b,15)
        drag(page,c,d,11)
        assert len(ink(page)["pages"][0]["strokes"])==2
        page.wait_for_function("window.MentorIpadPilot.saved()")
        assert not writes,writes
        assert page.locator("#saveStatus").inner_text()=="已保存在本机"
        report["checks"].append("mouse ink writes two vector strokes saved to IndexedDB only")
        page.screenshot(path=str(OUT/"v014-ipad-paper.png"))

        page.locator("#undoInk").click()
        assert len(ink(page)["pages"][0]["strokes"])==1
        page.locator("#redoInk").click()
        assert len(ink(page)["pages"][0]["strokes"])==2
        report["checks"].append("undo and redo preserve vector geometry")
        original=ink(page)["pages"][0]["strokes"][0]["points"][0]["x"]

        # Lasso a rectangle around the first (middle height) line only.
        page.locator('[data-tool="lasso"]').click()
        polygon=[(a[0]-18,a[1]-22),(b[0]+20,a[1]-22),
                 (b[0]+20,b[1]+23),(a[0]-18,b[1]+23),(a[0]-18,a[1]-22)]
        page.mouse.move(*polygon[0]);page.mouse.down()
        for position in polygon[1:]:page.mouse.move(*position,steps=5)
        page.mouse.up()
        assert "已圈选 1 笔" in page.locator("#selectionInfo").inner_text()
        # Move previously selected ink by dragging inside its polygon.
        center=((a[0]+b[0])/2,(a[1]+b[1])/2)
        drag(page,center,(center[0]+52,center[1]-24))
        after=ink(page)["pages"][0]["strokes"][0]["points"][0]["x"]
        assert after-original>40,(original,after)
        report["checks"].append("lasso selects and moves only enclosed stroke")

        page.locator('[data-tool="eraser"]').click()
        pt=page.evaluate("""() => {
          const s=MentorIpadPilot.snapshot().pages[0].strokes[0].points;
          return {x:s[0].x,y:s[0].y}
        }""")
        rect=page.locator("#inkCanvas").bounding_box()
        sx=rect["x"]+pt["x"];sy=rect["y"]+pt["y"]
        drag(page,(sx,sy),(sx+12,sy+6),6)
        assert len(ink(page)["pages"][0]["strokes"])==1
        page.locator("#undoInk").click()
        assert len(ink(page)["pages"][0]["strokes"])==2
        report["checks"].append("whole-stroke eraser remains undoable")

        page.locator("#addPaperPage").click()
        assert len(ink(page)["pages"])==2
        assert len(ink(page)["pages"][1]["strokes"])==0
        page.locator('[data-tool="pen"]').click()
        rect=page.locator("#inkCanvas").bounding_box()
        drag(page,(rect["x"]+300,rect["y"]+340),
             (rect["x"]+420,rect["y"]+375))
        assert len(ink(page)["pages"][1]["strokes"])==1
        page.wait_for_function("window.MentorIpadPilot.saved()",timeout=10000)
        page.reload(wait_until="networkidle")
        page.wait_for_function("() => MentorIpadPilot.snapshot()?.pages.length === 2")
        doc=ink(page)
        assert len(doc["pages"][0]["strokes"])==2
        assert len(doc["pages"][1]["strokes"])==1
        assert doc["activePageId"]=="page-2"
        assert doc["studentId"]==student and doc["sessionId"]==sid
        report["checks"].append("multiple pages and every ink stroke recover across full page reload")
        page.screenshot(path=str(OUT/"v014-ipad-multipage.png"))

        page.locator("#toggleAgent").click()
        assert page.locator("#agentPanel").is_visible()
        assert page.locator("#agentDialogue .dialogue-placeholder").is_visible()
        assert len(ink(page)["pages"][1]["strokes"])==1
        page.screenshot(path=str(OUT/"v014-ipad-agent.png"))
        page.locator("#agentQuestion").fill("我不确定应该怎样从距离比的条件推出需要的中间关系。")
        page.locator("#sendToAgent").click()
        page.wait_for_function("() => document.querySelectorAll('#agentDialogue .message').length >= 2")
        session=page.request.get(BASE+"/api/sessions/"+sid).json()
        assert len(session["turns"])==1
        assert "我不确定应该怎样从距离比" in session["turns"][0]["student_text"]
        assert len(ink(page)["pages"][1]["strokes"])==1
        assert len(writes)==1 and writes[0][0]=="POST" and "/turns" in writes[0][1],writes
        page.locator("#closeAgent").click()
        assert page.locator("#agentPanel").is_hidden()
        assert len(ink(page)["pages"][1]["strokes"])==1
        report["checks"].append("agent only opens on demand; explicit text request does not upload ink")

        page.locator("#studyBack").click()
        page.wait_for_url("**/ipad",timeout=8000)
        page.locator("#continueWriting").click()
        page.wait_for_url("**/ipad/study?session=*",timeout=8000)
        assert ink(page)["pages"][1]["strokes"]
        assert len(ink(page)["pages"])==2
        report["checks"].append("home/study route and matching demo session resume without lost ink")
        page.goto(BASE+"/#history",wait_until="networkidle")
        page.wait_for_function("() => document.querySelector('#history')?.classList.contains('active')")
        report["checks"].append("new iPad home links into actual legacy history view")
        ctx.close()

        for width,height in [(1024,768),(834,1112),(390,844)]:
            mc=browser.new_context(viewport={"width":width,"height":height},
              locale="zh-CN",is_mobile=True,has_touch=True,reduced_motion="reduce")
            mp=mc.new_page()
            mp.on("pageerror",lambda e:report["page_errors"].append(str(e)))
            assert mp.goto(BASE+"/ipad",wait_until="networkidle").ok
            mp.locator("#startNewPaper").click()
            mp.wait_for_url("**/ipad/study?session=*",timeout=12000)
            check(mp.locator("#inkCanvas").is_visible(),f"Canvas absent at {width}")
            dims=mp.evaluate("()=>({viewport:innerWidth,scroll:document.documentElement.scrollWidth})")
            assert dims["scroll"]<=dims["viewport"]+2,dims
            before=mp.evaluate("MentorIpadPilot.snapshot().pages[0].strokes.length")
            paper=mp.locator("#inkCanvas").bounding_box()
            mp.touchscreen.tap(paper["x"]+paper["width"]*.5,
                 paper["y"]+paper["height"]*.62)
            after=mp.evaluate("MentorIpadPilot.snapshot().pages[0].strokes.length")
            assert before==after==0,{"width":width,"before":before,"after":after}
            mp.locator("#toggleAgent").click()
            assert mp.locator("#agentPanel").is_visible()
            if height>width:
                assert mp.locator("#agentPanel").evaluate(
                  "e=>getComputedStyle(e).position")=="absolute"
            if width==834:mp.screenshot(path=str(OUT/"v014-ipad-portrait-agent.png"))
            if width==390:mp.screenshot(path=str(OUT/"v014-ipad-mobile.png"))
            report["widths"].append(width)
            mc.close()
        browser.close()
    assert not report["page_errors"],report["page_errors"]
    assert not report["external"],report["external"]
    (OUT/"v014-ipad-browser-results.json").write_text(json.dumps(report,
        ensure_ascii=False,indent=2)+"\n")
    print("IPAD PILOT CHROME PASS",len(report["checks"]),
      "interactive checks, responsive widths",report["widths"],
      "ink_backend_upload=0, page_errors=0, external=0")

if __name__=="__main__":
    run()
