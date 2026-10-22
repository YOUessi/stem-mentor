"""Mac Chrome authentic transfer workflow; only synthetic accounts and offline API."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
BASE=os.environ.get("STEM_MENTOR_URL","http://127.0.0.1:8000")
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=ROOT/"artifacts/v013"
OUT.mkdir(parents=True,exist_ok=True)

def request(c,method,path,body=None):
    r=c.request.fetch(BASE+path,method=method,data=body)
    assert r.ok,(method,path,r.status,r.text())
    return r.json()

def run():
    checks=[]
    errors=[]
    external=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=CHROME,
            args=["--disable-extensions","--no-first-run"])
        ctx=browser.new_context(viewport={"width":1440,"height":980},locale="zh-CN")
        page=ctx.new_page()
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.on("request",lambda r:external.append(r.url) if not r.url.startswith(BASE) else None)
        uid=request(ctx,"POST","/api/students",{"alias":"v0.13合成学生"})["id"]
        old=request(ctx,"POST","/api/sessions",{
            "student_id":uid,"problem_id":"ellipse-tangent","mode":"INDEPENDENT"})["id"]
        request(ctx,"POST","/api/sessions/"+old+"/turns",{
            "student_text":"我先把椭圆的切点条件列出来"})
        episode=request(ctx,"POST","/api/sessions/"+old+"/complete",{
            "reflection":"复盘：切点必须在曲线上；数学正确性没有被自动验证"})["episode"]["id"]
        current=request(ctx,"POST","/api/sessions",{
            "student_id":uid,"problem_id":"hyperbola-tangent","mode":"INDEPENDENT"})["id"]
        page.add_init_script("localStorage.setItem('stem-demo-student',"+json.dumps(uid)+");"+
            "localStorage.setItem('stem-demo-session',"+json.dumps(current)+");")
        assert page.goto(BASE,wait_until="networkidle").ok
        page.locator("#transferDetails summary").click()
        page.wait_for_selector('.transfer-panel button:text("冻结我的无提示尝试")',timeout=10000)
        assert "椭圆上一点" not in page.locator("#transferBody").inner_text()
        assert page.locator("#transferPanel").count()==0  # existing layout not replaced
        assert "SIMULATION · v0.14" in page.content()
        checks.append("hidden historical problem title before independent baseline")
        page.locator(".transfer-panel textarea").fill(
            "我先检查这个双曲线切点的合法条件，再考虑从局部变化反推切线结构。")
        page.locator(".transfer-panel button",has_text="冻结我的无提示尝试").click()
        page.get_by_role("button",name="主动请求旧题回忆").wait_for(timeout=10000)
        assert "椭圆上一点的切线" in page.locator("#transferBody").inner_text()
        checks.append("real same-student episode becomes available after baseline")
        page.get_by_role("button",name="主动请求旧题回忆").click()
        page.locator(".transfer-panel h3",has_text="第三阶段").wait_for(timeout=15000)
        page.locator(".transfer-panel textarea").fill(
            "我发现要先核对切点的曲线方程，然后比较双曲线与椭圆中符号的变化。")
        page.get_by_role("button",name="记录回忆后的思路").click()
        page.get_by_text("本轮迁移练习已记录完毕").wait_for(timeout=10000)
        assert page.locator(".transfer-record").count()==2
        checks.append("baseline, real recall event and after-recall idea recorded")
        page.screenshot(path=str(OUT/"v013-green-transfer-desktop.png"),full_page=True)
        api=request(ctx,"GET","/api/sessions/"+current+"/transfer")
        assert len(api["records"])==2
        assert api["math_verified"] is False
        assert api["history_candidate"]["source_episode_id"]==episode
        assert [r["evidence_status"] for r in api["records"]]==[
            "NO_IN_APP_HINTS_OBSERVED_NOT_PROOF","STUDENT_POST_RECALL_NOT_VERIFIED"]
        checks.append("persistent evidence status never claims mathematical correctness")
        page.reload(wait_until="networkidle")
        page.locator("#transferDetails summary").click()
        page.wait_for_selector(".transfer-record",timeout=12000)
        assert page.locator(".transfer-record").count()==2
        page.locator('[data-view="history"]').click()
        page.get_by_text("已记录无提示尝试 1 次").wait_for()
        checks.append("reload and history summary reflect authentic records, not mastery")
        ctx.close()

        mobile=browser.new_context(viewport={"width":390,"height":844},
            locale="zh-CN",reduced_motion="reduce")
        pm=mobile.new_page()
        pm.on("pageerror",lambda e:errors.append(str(e)))
        mid=request(mobile,"POST","/api/students",{"alias":"v0.13移动合成"})["id"]
        msid=request(mobile,"POST","/api/sessions",{
            "student_id":mid,"problem_id":"hyperbola-tangent","mode":"INDEPENDENT"})["id"]
        pm.add_init_script("localStorage.setItem('stem-demo-student',"+json.dumps(mid)+");"+
            "localStorage.setItem('stem-demo-session',"+json.dumps(msid)+");")
        assert pm.goto(BASE,wait_until="networkidle").ok
        pm.locator("#transferDetails summary").click()
        pm.locator(".transfer-panel textarea").fill("我先独立分析题目中哪些是已知，哪些是必须证明的目标。")
        assert pm.locator(".transfer-panel button",has_text="冻结我的无提示尝试").is_visible()
        dims=pm.evaluate("() => ({inner:innerWidth,scroll:document.documentElement.scrollWidth})")
        assert dims["scroll"]<=dims["inner"]+2,dims
        pm.screenshot(path=str(OUT/"v013-green-transfer-mobile.png"),full_page=True)
        checks.append("390px green screen, no horizontal overflow")
        mobile.close()
        browser.close()
    assert errors==[],errors
    assert external==[],external
    result={"checks":checks,"runtime_errors":errors,"external_requests":external,
            "verified_student_mastery":False}
    (OUT/"chrome-transfer-v013.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("Transfer Chrome checks PASSED:",len(checks),"checks, 0 page errors, 0 external requests")

if __name__=="__main__":
    run()
