"""Mac Chrome regression for extrema candidates, endpoints, domain and opt-in UI."""
import os,json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
URL=os.environ.get("STEM_MENTOR_URL","http://127.0.0.1:8000")
OUT=ROOT/"artifacts/v011b";OUT.mkdir(parents=True,exist_ok=True)
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CASES=["extrema-quadratic","extrema-cubic","extrema-absolute","extrema-sine","extrema-log"]

def set_value(page,key,value):
 page.locator("#labParam_"+key).evaluate(
    "(el,v)=>{el.value=String(v);el.dispatchEvent(new Event('input',{bubbles:true}))}",value)

def choose(page,id):
 page.locator('[data-family="function_2d"]').click()
 page.locator("#labPreset").select_option(id)

def main():
 result={"scene_defaults":[],"checks":[],"widths":[],"errors":[],"external":[],"writes":[]}
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=CHROME,headless=True,
    args=["--no-first-run","--disable-extensions"])
  try:
   context=browser.new_context(viewport={"width":1440,"height":980},locale="zh-CN")
   pg=context.new_page()
   pg.on("pageerror",lambda e:result["errors"].append(str(e)))
   pg.on("request",lambda r:result["external"].append(r.url) if not r.url.startswith(URL) else None)
   assert pg.goto(URL,wait_until="networkidle").ok
   pg.locator('[data-view="lab"]').click()
   pg.wait_for_function("() => document.querySelectorAll('#labFamilies button').length===9")
   pg.on("request",lambda r:result["writes"].append(r.url) if r.method not in ("GET","HEAD") else None)
   assert pg.locator('meta[name="theme-color"]').get_attribute("content")=="#174938"
   for sid in CASES:
      choose(pg,sid)
      assert pg.locator('#labPlot [data-extrema-kind]').count()==1
      assert pg.locator('#labPlot .lab-extrema-curve').count()==1
      assert pg.locator('#labPlot .lab-extrema-endpoint').count()==2
      assert pg.locator('#labPlot [data-extrema-point]').count()==0
      assert not pg.locator('#labAssistToggle').is_checked()
      assert '全局最大值：' not in pg.locator('#labMetrics').inner_text()
      assert pg.locator('.lab-extrema-guess').count()==1
      result["scene_defaults"].append(sid)
   result["checks"].append("five opt-in closed-interval math scenes, candidate positions not pre-spoiled")
   choose(pg,'extrema-quadratic')
   pg.locator('.lab-extrema-guess').fill('我猜你不能只找导数为零的点')
   set_value(pg,'a',1);set_value(pg,'b',-2);set_value(pg,'c',0);set_value(pg,'L',-1);set_value(pg,'R',3)
   assert pg.locator('.lab-extrema-guess').input_value().startswith('我猜')
   pg.get_by_role('button',name='请求下一个思考提示').click()
   assert '提示 1/3' in pg.locator('.lab-extrema-hint').inner_text()
   pg.locator('#labAssistToggle').check()
   assert pg.locator('[data-extrema-point]').count()==3
   assert '全局最小值：-1' in pg.locator('#labMetrics').inner_text()
   assert '全局最大值：3' in pg.locator('#labMetrics').inner_text()
   assert '位置：-1，3' in pg.locator('#labMetrics').inner_text()
   pg.locator('.lab-studio-layout').screenshot(path=str(OUT/'extrema-quadratic.png'))
   result["checks"].append("vertex minimum and tied endpoint maxima after explicit opt-in")
   set_value(pg,'a',0);set_value(pg,'b',0);set_value(pg,'c',3)
   assert '常值函数' in pg.locator('#labMetrics').inner_text()
   set_value(pg,'L',3)
   assert '闭区间必须满足' in pg.locator('#labMetrics').inner_text()
   assert pg.locator('[data-extrema-point]').count()==0
   result["checks"].append("constant function and invalid closed-interval boundaries")
   choose(pg,'extrema-absolute')
   pg.locator('#labAssistToggle').check()
   assert pg.locator('[data-type="nondifferentiable"]').count()==1
   assert '不可导点' in pg.locator('#labMetrics').inner_text()
   result["checks"].append("absolute kink cannot be skipped by derivative-only technique")
   choose(pg,'extrema-cubic')
   pg.locator('#labAssistToggle').check()
   assert '驻点 2' in pg.locator('#labMetrics').inner_text()
   pg.locator('.lab-studio-layout').screenshot(path=str(OUT/'extrema-cubic.png'))
   result["checks"].append("stationary candidates compared to interval endpoints")
   choose(pg,'extrema-sine')
   pg.locator('#labAssistToggle').check()
   assert pg.locator('[data-extrema-point]').count()>=3
   result["checks"].append("sine interior extrema candidates")
   choose(pg,'extrema-log')
   pg.locator('#labAssistToggle').check()
   assert '全局最小值：' in pg.locator('#labMetrics').inner_text()
   set_value(pg,'L',5);set_value(pg,'R',4)
   assert '闭区间必须满足' in pg.locator('#labMetrics').inner_text()
   result["checks"].append("positive-domain log and invalid reversed interval")
   context.close()
   for w in [390,768,1280]:
      ctx=browser.new_context(viewport={"width":w,"height":900},locale="zh-CN",reduced_motion="reduce")
      mobile=ctx.new_page()
      mobile.on("pageerror",lambda e:result["errors"].append(str(e)))
      assert mobile.goto(URL,wait_until="networkidle").ok
      mobile.locator('[data-view="lab"]').click()
      mobile.wait_for_function("() => document.querySelectorAll('#labFamilies button').length===9")
      choose(mobile,'extrema-quadratic')
      assert mobile.locator('.lab-extrema-curve').count()==1
      if w==390:
          mobile.locator('#labAssistToggle').check()
          mobile.screenshot(path=str(OUT/'extrema-mobile.png'),full_page=True)
      dimensions=mobile.evaluate("()=>({scroll:document.documentElement.scrollWidth,screen:innerWidth})")
      assert dimensions["scroll"]<=dimensions["screen"]+2,dimensions
      result["widths"].append(w)
      ctx.close()
   assert result["errors"]==[] and result["external"]==[] and result["writes"]==[]
  finally:
   browser.close()
 (OUT/'extrema-chrome.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding="utf8")
 print("v0.11b Chrome PASS",len(result["scene_defaults"]),"scenes,",
    len(result["checks"]),"interactive groups, widths",result["widths"],
    "errors",len(result["errors"]),"external",len(result["external"]))
if __name__=="__main__":main()
