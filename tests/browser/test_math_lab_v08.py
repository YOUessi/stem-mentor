"""macOS Chrome high-school mathematics lab UI smoke, fixture correctness, responsive checks.

Deliberately checks actual navigation/rendering, not evidence of educational effectiveness.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
BASE=os.environ.get("STEM_MENTOR_URL","http://127.0.0.1:8000")
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=ROOT/"artifacts"/"ui";OUT.mkdir(parents=True,exist_ok=True)
V08_IDS=['fn-linear', 'fn-quadratic', 'fn-cubic', 'fn-exp', 'fn-log', 'fn-sin', 'fn-cos', 'fn-tan', 'fn-abs', 'fn-inverse', 'fn-sqrt', 'fn-piecewise', 'conic-line', 'conic-circle', 'conic-ellipse', 'conic-hyperbola', 'conic-parabola', 'conic-intersection', 'tri-free', 'tri-right', 'tri-ssa', '3d-point', '3d-vectors', '3d-plane', '3d-prism', '3d-pyramid', '3d-sphere', '3d-cylinder', '3d-cone']

def set_range(page,key,value):
    page.locator("#labParam_"+key).evaluate(
      "(input, val) => {input.value=String(val);input.dispatchEvent(new Event('input',{bubbles:true}))}",value)

def main():
    report={"scenes_tested":[],"interaction_checks":[],"widths":[],"errors":[],"external":[]}
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,executable_path=CHROME,
          args=["--disable-gpu","--no-first-run","--disable-extensions"])
        desktop=browser.new_context(viewport={"width":1440,"height":980},locale="zh-CN")
        page=desktop.new_page()
        page.on("pageerror",lambda e:report["errors"].append(str(e)))
        page.on("request",lambda r:report["external"].append(r.url) if not r.url.startswith(BASE) else None)
        assert page.goto(BASE,wait_until="networkidle").ok
        page.locator('button[data-view="lab"]').click()
        page.wait_for_function("() => document.querySelectorAll('#labPreset option').length>=12")
        assert page.locator("#lab").is_visible()
        assert page.locator("#labSummary").inner_text().find("113")>=0
        assert "39" in page.locator("#labSummary").inner_text()
        assert "174938" in page.locator('meta[name="theme-color"]').get_attribute("content")
        report["interaction_checks"].append("Standalone green lab navigation and 113-topic catalog")

        page.wait_for_selector("#labFormula mjx-container svg",timeout=17000)
        for family in ["function_2d","conic_2d","triangle_2d","space_3d"]:
            page.locator('button[data-family="'+family+'"]').click()
            for option in page.locator("#labPreset option").all():
                scene=option.get_attribute("value")
                if scene not in V08_IDS: continue
                page.locator("#labPreset").select_option(scene)
                page.wait_for_function("() => document.querySelector('#labPlot .lab-axis, #labPlot .lab-3d-x, #labPlot .lab-triangle') !== null")
                assert page.locator("#labTitle").inner_text()
                assert page.locator("#labMetrics .lab-metric").count()>0
                report["scenes_tested"].append(scene)
        assert len(report["scenes_tested"])==29,report["scenes_tested"]
        report["interaction_checks"].append("All 29 configured scenes rendered with metrics, no JS errors")

        page.locator('button[data-family="function_2d"]').click()
        page.locator("#labPreset").select_option("fn-quadratic")
        page.locator(".lab-studio-layout").screenshot(path=str(OUT/"highschool-v08-functions.png"))
        set_range(page,"h",2)
        assert "顶点 (2.00" in page.locator("#labMetrics").inner_text()
        page.locator("#labPreset").select_option("fn-log")
        set_range(page,"a",1)
        assert "底数为 1" in page.locator("#labMetrics").inner_text()
        page.locator("#lab2dZoom").evaluate(
          "(n)=>{n.value='1.3';n.dispatchEvent(new Event('input',{bubbles:true}))}")
        assert page.locator("#labPlot .lab-axis").count()==2
        report["interaction_checks"].append("Function curve parameters, discontinuity and 2D zoom")

        page.locator('button[data-family="conic_2d"]').click()
        page.locator("#labPreset").select_option("conic-ellipse")
        page.locator(".lab-studio-layout").screenshot(path=str(OUT/"highschool-v08-conics.png"))
        assert page.locator("#labPlot .lab-focus").count()==2
        page.locator("#labPreset").select_option("conic-hyperbola")
        assert page.locator("#labPlot .lab-construction").count()>=2
        page.locator("#labPreset").select_option("conic-parabola")
        assert page.locator("#labMetrics").inner_text().find("准线")>=0
        report["interaction_checks"].append("Conic focus, asymptotes and directrix")

        page.locator('button[data-family="triangle_2d"]').click()
        page.locator("#labPreset").select_option("tri-free")
        before=page.locator("#labMetrics").inner_text()
        v=page.locator("#labPlot .lab-drag-vertex").first
        v.scroll_into_view_if_needed()
        b=v.bounding_box();assert b
        xy=(b["x"]+b["width"]/2,b["y"]+b["height"]/2)
        page.mouse.move(*xy);page.mouse.down();page.mouse.move(xy[0]+45,xy[1]+20,steps=6);page.mouse.up()
        assert page.locator("#labMetrics").inner_text()!=before
        page.locator("#labPreset").select_option("tri-right")
        assert "直角在 A" in page.locator("#labMetrics").inner_text()
        page.locator("#labPreset").select_option("tri-ssa")
        page.locator(".lab-studio-layout").screenshot(path=str(OUT/"highschool-v08-triangles.png"))
        assert "符合条件" in page.locator("#labMetrics").inner_text()
        assert page.evaluate("MentorLabTriangle.ssaCandidates(6,8,40).length")==2
        assert page.evaluate("MentorLabTriangle.ssaCandidates(4,8,40).length")==0
        assert page.evaluate("MentorLabTriangle.ssaCandidates(8,8,40).length")==1
        report["interaction_checks"].append("Draggable triangle, constrained right angle, SSA 0/1/2 solutions")

        page.locator('button[data-family="space_3d"]').click()
        page.locator("#labPreset").select_option("3d-point")
        assert page.locator("#lab3dControls").is_visible()
        assert page.locator("#labPlot .lab-3d-x").count()>0
        assert page.locator("#labPlot .lab-3d-y").count()>0
        assert page.locator("#labPlot .lab-3d-z").count()>0
        x_before=page.locator("#labPlot .lab-3d-dot").first.get_attribute("cx")
        page.locator("#labYaw").evaluate(
          "(n)=>{n.value='120';n.dispatchEvent(new Event('input',{bubbles:true}))}")
        x_after=page.locator("#labPlot .lab-3d-dot").first.get_attribute("cx")
        assert x_after!=x_before
        def assert_valid_arrowheads():
            for candidate in page.locator("#labPlot .lab-3d-arrowhead").all():
                point_pairs=candidate.get_attribute("points").split()
                assert len(point_pairs)==3,point_pairs
                for pair in point_pairs:
                    coords=pair.split(",")
                    assert len(coords)==2,point_pairs
                    x,y=[float(x) for x in coords]
                    assert -100<=x<=860 and -100<=y<=560,point_pairs
        assert_valid_arrowheads()
        page.locator("#labPreset").select_option("3d-plane")
        page.locator(".lab-studio-layout").screenshot(path=str(OUT/"highschool-v08-space3d.png"))
        assert_valid_arrowheads()
        assert page.locator("#labPlot .lab-3d-plane").count()>0
        page.locator("#labPreset").select_option("3d-prism")
        assert page.locator("#labPlot .lab-3d-solid-face").count()>=5
        page.locator("#labPreset").select_option("3d-sphere")
        assert page.locator("#labPlot .lab-3d-wire").count()>=4
        report["interaction_checks"].append("XYZ coordinates, view angle, vector/plane/solid projection")

        page.locator("#labLevel").select_option("必修")
        assert "必修" in page.locator(".lab-results-count").inner_text() or page.locator(".lab-topic-item").count()>0
        page.locator("#labCoverage").select_option("PLANNED")
        planned=page.locator(".lab-topic-item").count()
        assert planned>4
        page.locator("#labTopicSearch").fill("集合")
        assert page.locator(".lab-topic-item").count()>0
        assert page.locator(".lab-topic-button").count()==0
        page.locator("#labLevel").select_option("all")
        page.locator("#labCoverage").select_option("all")
        page.locator("#labTopicSearch").fill("")
        page.locator('button[data-family="space_3d"]').click()
        page.locator("#labPreset").select_option("3d-plane")
        page.screenshot(path=str(OUT/"highschool-v08-desktop.png"),full_page=True)
        report["interaction_checks"].append("Knowledge matrix planned vs active status and search filters")

        page.locator('button[data-view="workspace"]').click()
        assert page.locator("#workspace").is_visible()
        assert page.locator("#studentInput").is_visible()
        assert page.locator("#geometryPanel").count()==1
        report["interaction_checks"].append("Legacy green tutoring workspace and 3D lab coexist")

        desktop.close()
        for w,h in [(390,844),(768,960),(1024,860),(1280,860)]:
            context=browser.new_context(viewport={"width":w,"height":h},locale="zh-CN")
            pg=context.new_page()
            pg.on("pageerror",lambda e:report["errors"].append(str(e)))
            assert pg.goto(BASE,wait_until="networkidle").ok
            pg.locator('button[data-view="lab"]').click()
            pg.wait_for_function("() => document.querySelectorAll('#labPreset option').length>=12")
            pg.locator('button[data-family="space_3d"]').click()
            pg.locator("#labPreset").select_option("3d-vectors")
            width=pg.evaluate("""() => ({
              viewport:innerWidth, scroll:document.documentElement.scrollWidth,
              toolScroll:document.querySelector('#labPlotBox').scrollWidth
            })""")
            assert width["scroll"]<=width["viewport"]+2,width
            assert pg.locator("#labPlot .lab-3d-vector").count()>0
            report["widths"].append(w)
            if w==390:pg.screenshot(path=str(OUT/"highschool-v08-mobile.png"),full_page=True)
            context.close()
        browser.close()
    assert not report["errors"],report["errors"]
    assert not report["external"],report["external"]
    (OUT/"highschool-v08-browser-results.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("High-school lab: 29/29 scene renders, "+str(len(report["interaction_checks"]))+
          " interactive checks, widths="+str(report["widths"])+", zero page errors and external requests.")

if __name__=="__main__":
    main()
