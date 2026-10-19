"""Real Chrome probability/statistics tests: 9 scenes, boundaries, mobile, no model API.

All data synthetic. The math core has separate deterministic Node unit tests.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
BASE=os.environ.get("STEM_MENTOR_URL","http://127.0.0.1:8000")
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=ROOT/"artifacts"/"v012";OUT.mkdir(parents=True,exist_ok=True)
SCENES=("prob-choose","prob-permute","prob-tree","prob-binomial",
        "prob-hypergeo","prob-normal","stats-bernoulli","stats-summary","stats-regression")

def set_param(page,name,value):
    page.locator("#labParam_"+name).evaluate(
        "(e,v)=>{e.value=String(v);e.dispatchEvent(new Event('input',{bubbles:true}))}",value)

def choose(page,scene,family):
    page.locator('[data-family="'+family+'"]').click()
    page.locator("#labPreset").select_option(scene)
    page.wait_for_function("() => document.querySelector('#labMetrics .lab-metric')!==null")

def main():
    report={"scenes":[],"checks":[],"responsive":[],"errors":[],"external":[],"writes":[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=CHROME,headless=True,
           args=["--no-first-run","--disable-extensions","--disable-gpu"])
        try:
            ctx=browser.new_context(viewport={"width":1440,"height":1000},locale="zh-CN")
            page=ctx.new_page()
            page.on("pageerror",lambda e:report["errors"].append(str(e)))
            page.on("request",lambda r:report["external"].append(r.url)
                    if not r.url.startswith(BASE) else None)
            assert page.goto(BASE,wait_until="networkidle").ok
            page.locator('[data-view="lab"]').click()
            page.wait_for_function("() => document.querySelectorAll('#labFamilies button').length===11")
            page.on("request",lambda r:report["writes"].append(r.url)
                    if r.method not in ("GET","HEAD") else None)
            assert page.locator('meta[name="theme-color"]').get_attribute("content")=="#174938"
            assert "71" in page.locator("#labSummary").inner_text()
            for family in ("probability_2d","statistics_2d"):
                page.locator('[data-family="'+family+'"]').click()
                n=6 if family=="probability_2d" else 3
                assert page.locator("#labPreset option").count()==n
                for option in page.locator("#labPreset option").all():
                    sid=option.get_attribute("value")
                    page.locator("#labPreset").select_option(sid)
                    assert sid in SCENES
                    assert page.locator("#labPlot line, #labPlot rect, #labPlot path, #labPlot circle").count()>0
                    assert page.locator("#labMetrics .lab-metric").count()>0
                    assert not page.locator("#labAssistToggle").is_checked()
                    report["scenes"].append(sid)
            assert len(report["scenes"])==9
            report["checks"].append("9 configured probability and statistics scenes with default hidden results")

            choose(page,"prob-choose","probability_2d")
            set_param(page,"k",30)
            page.locator("#labAssistToggle").check()
            assert "k>n" in page.locator("#labMetrics").inner_text()
            choose(page,"prob-permute","probability_2d")
            page.locator("#labAssistToggle").check()
            assert "排列数" in page.locator("#labMetrics").inner_text()
            report["checks"].append("combination and permutation impossible outcomes are explicit")

            choose(page,"prob-tree","probability_2d")
            set_param(page,"p",0)
            page.locator("#labAssistToggle").check()
            txt=page.locator("#labMetrics").inner_text()
            assert "联合概率" in txt and "第二阶段" in txt
            assert "NaN" not in txt and "Infinity" not in txt
            page.locator(".lab-studio-layout").screenshot(path=str(OUT/"probability-tree.png"))
            report["checks"].append("conditional event tree normalizes even when first-event probability vanishes")

            choose(page,"prob-binomial","probability_2d")
            set_param(page,"p",0)
            page.locator("#labAssistToggle").check()
            assert "归一化ΣP=1" in page.locator("#labMetrics").inner_text()
            set_param(page,"p",1)
            assert "归一化ΣP=1" in page.locator("#labMetrics").inner_text()
            page.locator(".lab-studio-layout").screenshot(path=str(OUT/"probability-binomial.png"))
            report["checks"].append("binomial endpoint p=0/1 and normalization")

            choose(page,"prob-hypergeo","probability_2d")
            page.locator("#labAssistToggle").check()
            assert "归一化ΣP=" in page.locator("#labMetrics").inner_text()
            set_param(page,"K",30)
            assert "参数不满足概率模型" in page.locator("#labMetrics").inner_text()
            report["checks"].append("hypergeometric without replacement rejects impossible population")

            choose(page,"prob-normal","probability_2d")
            assert page.locator("#labPlot .lab-prob-density").count()==1
            assert "密度" in page.locator("#labMetrics").inner_text()
            page.locator("#labAssistToggle").check()
            assert "近似区间概率" in page.locator("#labMetrics").inner_text()
            set_param(page,"L",4);set_param(page,"R",-1)
            assert "无效观测区间" in page.locator("#labMetrics").inner_text()
            report["checks"].append("normal density distinguished from area; reversed interval invalid")

            choose(page,"stats-bernoulli","statistics_2d")
            set_param(page,"p",1)
            page.locator("#labAssistToggle").check()
            assert "模拟频率=1" in page.locator("#labMetrics").inner_text()
            set_param(page,"p",0)
            assert "模拟频率=0" in page.locator("#labMetrics").inner_text()
            report["checks"].append("seeded frequency is labeled as simulation, not exact probability")

            choose(page,"stats-summary","statistics_2d")
            page.locator("#labAssistToggle").check()
            text=page.locator("#labMetrics").inner_text()
            for expected in ("样本均值=2.6","中位数=2","众数=2",
                             "总体方差(分母n)=1.84","样本方差(分母n−1)=2.3"):
                assert expected in text,(expected,text)
            page.locator(".lab-studio-layout").screenshot(path=str(OUT/"stats-sample.png"))
            report["checks"].append("synthetic five-point summary uses correct variance denominators")

            choose(page,"stats-regression","statistics_2d")
            set_param(page,"slope",2);set_param(page,"intercept",1);set_param(page,"noise",0)
            page.locator("#labAssistToggle").check()
            metrics=page.locator("#labMetrics").inner_text()
            assert "样本回归斜率=2" in metrics,metrics
            assert "相关系数 r=1" in metrics,metrics
            assert "因果" in metrics
            page.locator(".lab-studio-layout").screenshot(path=str(OUT/"stats-regression.png"))
            report["checks"].append("zero-noise regression recovers synthetic slope but not causation")
            assert report["writes"]==[],report["writes"]
            ctx.close()
            for width in (390,768,1280):
                mobile=browser.new_context(viewport={"width":width,"height":850},
                      locale="zh-CN",reduced_motion="reduce")
                pg=mobile.new_page()
                pg.on("pageerror",lambda e:report["errors"].append(str(e)))
                assert pg.goto(BASE,wait_until="networkidle").ok
                pg.locator('[data-view="lab"]').click()
                pg.wait_for_function("() => document.querySelectorAll('#labFamilies button').length===11")
                choose(pg,"stats-summary","statistics_2d")
                dims=pg.evaluate("() => ({scroll:document.documentElement.scrollWidth,viewport:innerWidth})")
                assert dims["scroll"]<=dims["viewport"]+2,dims
                report["responsive"].append(width)
                if width==390:
                    pg.screenshot(path=str(OUT/"probability-mobile.png"),full_page=True)
                mobile.close()
        finally:
            browser.close()
    assert len(report["scenes"])==9
    assert not report["errors"] and not report["external"] and not report["writes"]
    (OUT/"chrome-results.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("v0.12 Chrome PASS:",len(report["scenes"]),"scenes;",
      len(report["checks"]),"checks; responsive",report["responsive"],
      "JS errors",len(report["errors"]),"external",len(report["external"]),"learner writes",len(report["writes"]))

if __name__=="__main__":main()
