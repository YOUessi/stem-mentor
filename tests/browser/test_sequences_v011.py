"""Real Mac Chrome regression for finite sequence lab and inquiry-first interaction."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
URL=os.environ.get("STEM_MENTOR_URL","http://127.0.0.1:8000")
OUT=ROOT/"artifacts/v011";OUT.mkdir(parents=True,exist_ok=True)
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
IDS=["seq-arithmetic","seq-geometric","seq-geometric-edge","seq-linear-recurrence",
     "seq-two-term","seq-partial-sum","seq-growth","seq-fixed-point"]

def param(page,key,value):
    page.locator("#labParam_"+key).evaluate(
        "(el,v)=>{el.value=String(v);el.dispatchEvent(new Event(el.tagName==='SELECT'?'change':'input',{bubbles:true}))}",value)

def run():
    report={"scene_defaults":[],"checks":[],"mobile_widths":[],"page_errors":[],"external":[],"learning_writes":[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=CHROME,headless=True,args=["--no-first-run","--disable-extensions"])
        context=browser.new_context(viewport={"width":1440,"height":950},locale="zh-CN")
        page=context.new_page()
        page.on("pageerror",lambda e:report["page_errors"].append(str(e)))
        page.on("request",lambda r:report["external"].append(r.url) if not r.url.startswith(URL) else None)
        assert page.goto(URL,wait_until="networkidle").ok
        page.locator('button[data-view="lab"]').click()
        page.wait_for_function("() => document.querySelectorAll('#labFamilies button').length===9")
        page.locator('[data-family="sequence_2d"]').click()
        assert page.locator("#labPreset option").count()==8
        assert "57" in page.locator("#labSummary").inner_text()
        assert page.locator('meta[name="theme-color"]').get_attribute("content")=="#174938"
        page.on("request",lambda r:report["learning_writes"].append(r.url) if r.method not in ("GET","HEAD") else None)

        for sid in IDS:
            page.locator("#labPreset").select_option(sid)
            page.wait_for_function("() => document.querySelector('#labPlot [data-chart=term]')!==null")
            assert page.locator("#labPlot .lab-seq-dot").count()>0
            assert page.locator(".lab-seq-prediction").count()==1
            assert not page.locator("#labAssistToggle").is_checked()
            assert page.locator('[data-chart="sum"]').count()==0
            report["scene_defaults"].append(sid)
        report["checks"].append("all 8 sequence scenes render from indexed discrete terms")

        page.locator("#labPreset").select_option("seq-arithmetic")
        assert page.locator("#labPlot .lab-seq-dot").count()==5
        assert "已展示" not in page.locator("#labMetrics").inner_text() or "5 / 12" in page.locator("#labMetrics").inner_text()
        entry=page.locator(".lab-seq-prediction")
        entry.fill("我猜想第十二项随公差每次加2")
        param(page,"d",3)
        assert page.locator(".lab-seq-prediction").input_value().startswith("我猜想")
        assert page.locator("#labPlot .lab-seq-dot").count()==5
        assert "没有使用提示" in page.locator(".lab-seq-hint").inner_text()
        page.get_by_role("button",name="需要一点启发").click()
        assert "启发 1/3" in page.locator(".lab-seq-hint").inner_text()
        page.get_by_role("button",name="需要一点启发").click()
        assert "启发 2/3" in page.locator(".lab-seq-hint").inner_text()
        page.locator("#labAssistToggle").check()
        assert page.locator('#labPlot [data-chart="sum"]').count()==1
        assert page.locator("#labPlot .lab-seq-dot").count()==24
        assert "有限和 Sₙ=" in page.locator("#labMetrics").inner_text()
        assert page.locator(".lab-seq-table tbody tr").count()==12
        page.locator(".lab-studio-layout").screenshot(path=str(OUT/"sequence-arithmetic.png"))
        report["checks"].append("prediction survives replot; graduated prompts precede opt-in sum")

        page.locator("#labPreset").select_option("seq-geometric-edge")
        assert page.locator("#labPlot .lab-seq-dot").count()==5
        page.locator("#labAssistToggle").check()
        assert "q=1" in page.locator("#labMetrics").inner_text()
        assert "Sₙ=n·a₁" in page.locator("#labMetrics").inner_text()
        param(page,"q",1)
        assert "q=0" in page.locator("#labMetrics").inner_text()
        param(page,"q",2)
        assert "q=−1" in page.locator("#labMetrics").inner_text()
        report["checks"].append("q=1, q=0, and negative alternating ratio explicit")

        page.locator("#labPreset").select_option("seq-partial-sum")
        assert page.locator('#labPlot [data-chart="sum"]').count()==0
        param(page,"kind",1)
        page.locator("#labAssistToggle").check()
        assert page.locator('#labPlot [data-chart="sum"]').count()==1
        report["checks"].append("partial sums remain opt-in and choice control updates")

        page.locator("#labPreset").select_option("seq-growth")
        page.locator("#labAssistToggle").check()
        assert page.locator('#labPlot .lab-seq-secondary.lab-seq-dot').count()>=5
        assert "有限" in page.locator("#labMetrics").inner_text()
        report["checks"].append("two finite growth sequences, no claimed infinite proof")

        page.locator("#labPreset").select_option("seq-two-term")
        assert page.locator("#labParam_a2").count()==1
        page.locator(".lab-studio-layout").screenshot(path=str(OUT/"sequence-recurrence.png"))
        report["checks"].append("second-order recurrence requires two editable initial conditions")

        page.locator("#labPreset").select_option("seq-linear-recurrence")
        page.locator(".lab-seq-stage").select_option("STUCK")
        page.get_by_role("button",name="需要一点启发").click()
        assert page.locator(".lab-seq-hint").get_attribute("data-action")=="ASK_BACKWARD_GOAL"
        assert "目标" in page.locator(".lab-seq-hint").inner_text()
        page.get_by_role("button",name="需要一点启发").click()
        page.get_by_role("button",name="需要一点启发").click()
        assert page.locator(".lab-seq-hint").get_attribute("data-action")=="OFFER_ALTERNATIVE"
        report["checks"].append("reported stuck state changes guidance instead of repeating hints")

        assert len(report["learning_writes"])==0,report["learning_writes"]
        context.close()
        for width in (390,768,1280):
            ctx=browser.new_context(viewport={"width":width,"height":840},locale="zh-CN",reduced_motion="reduce")
            mobile=ctx.new_page()
            mobile.on("pageerror",lambda e:report["page_errors"].append(str(e)))
            assert mobile.goto(URL,wait_until="networkidle").ok
            mobile.locator('button[data-view="lab"]').click()
            mobile.wait_for_function("() => document.querySelectorAll('#labFamilies button').length===9")
            mobile.locator('[data-family="sequence_2d"]').click()
            mobile.locator("#labPreset").select_option("seq-geometric")
            assert mobile.locator("#labPlot .lab-seq-dot").count()>0
            dims=mobile.evaluate("() => ({scroll:document.documentElement.scrollWidth,inner:innerWidth})")
            assert dims["scroll"]<=dims["inner"]+2,dims
            report["mobile_widths"].append(width)
            if width==390:
                mobile.locator("#labAssistToggle").check()
                assert mobile.locator(".lab-seq-table").is_visible()
                mobile.screenshot(path=str(OUT/"sequence-mobile.png"),full_page=True)
            ctx.close()
        browser.close()
    assert report["page_errors"]==[],report["page_errors"]
    assert report["external"]==[],report["external"]
    (OUT/"sequence-chrome.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("v0.11 Chrome PASS",len(report["scene_defaults"]),"scenes;",len(report["checks"]),
      "interaction groups; mobile",report["mobile_widths"],"; no external requests or learner writes.")
if __name__=="__main__":run()
