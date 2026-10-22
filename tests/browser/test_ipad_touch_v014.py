from playwright.sync_api import sync_playwright
import os
BASE=os.getenv("STEM_MENTOR_URL","http://127.0.0.1:8000")
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=CHROME,args=['--no-first-run'])
 ctx=browser.new_context(viewport={"width":1024,"height":768},is_mobile=True,has_touch=True,device_scale_factor=1)
 page=ctx.new_page();errors=[]
 page.on("pageerror",lambda err:errors.append(str(err)))
 page.goto(BASE+"/ipad",wait_until="networkidle")
 page.locator("#startNewPaper").click()
 page.wait_for_url("**/ipad/study?session=*")
 cdp=ctx.new_cdp_session(page)
 rect=page.locator("#inkCanvas").bounding_box()
 origin=(rect["x"]+rect["width"]*.52,rect["y"]+rect["height"]*.55)
 def tp(x,y,i):return {"x":round(x),"y":round(y),"id":i}
 a=tp(origin[0]-60,origin[1],1);b=tp(origin[0]+60,origin[1],2)
 c=tp(origin[0]-120,origin[1],1);d=tp(origin[0]+120,origin[1],2)
 before=page.evaluate("MentorIpadPilot.view()")
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[a,b]})
 page.wait_for_timeout(200)
 cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[c,d]})
 page.wait_for_timeout(250)
 cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
 page.wait_for_timeout(200)
 after=page.evaluate("MentorIpadPilot.view()")
 strokes=page.evaluate("MentorIpadPilot.snapshot().pages[0].strokes.length")
 print('PINCH',before,'=>',after,'ink_strokes',strokes,'errors',errors,flush=True)
 assert after["zoom"]>before["zoom"]*1.5
 assert strokes==0
 # CDP synthetic pen pointer should be treated as ink and preserve non-default pressure.
 cx=round(origin[0]);cy=round(origin[1]+42)
 for typ,dx,force in [('mousePressed',0,.35),('mouseMoved',40,.55),('mouseMoved',80,.8),('mouseReleased',80,.8)]:
   cdp.send("Input.dispatchMouseEvent",{"type":typ,"x":cx+dx,"y":cy,"button":"left",
      "buttons":1 if typ!="mouseReleased" else 0,"pointerType":"pen",
      "clickCount":1 if typ in ("mousePressed","mouseReleased") else 0,"force":force})
   page.wait_for_timeout(70)
 data=page.evaluate("MentorIpadPilot.snapshot()")
 print('CDP PEN',len(data["pages"][0]["strokes"]),data["pages"][0]["strokes"][0]["points"][:3] if data["pages"][0]["strokes"] else [],flush=True)
 assert len(data["pages"][0]["strokes"])==1
 pressures=[x["p"] for x in data["pages"][0]["strokes"][0]["points"]]
 assert len(pressures)>=3
 assert max(pressures)-min(pressures)>0.3
 print('iPad pointer emulation PASS: two-finger pinch, no unintended touch ink, pen pressure samples; NOT physical device validation')
 assert not errors,errors
 ctx.close();browser.close()
