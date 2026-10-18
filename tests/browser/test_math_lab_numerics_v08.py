"""Independent numerical and extreme-value checks for 2D, triangle and 3D renderers."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

URL=os.environ.get("STEM_MENTOR_URL","http://127.0.0.1:8000")
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def main():
    errors=[]
    with sync_playwright() as p:
      browser=p.chromium.launch(executable_path=CHROME,headless=True,
        args=["--disable-extensions","--no-first-run","--disable-gpu"])
      page=browser.new_page(viewport={"width":1440,"height":920},locale="zh-CN")
      page.on("pageerror",lambda e:errors.append(str(e)))
      assert page.goto(URL,wait_until="networkidle").ok
      page.locator('button[data-view="lab"]').click()
      page.wait_for_function("() => document.querySelectorAll('#labPreset option').length>=12")
      numbers=page.evaluate("""() => {
        const res={};
        const F=window.MentorLab2D.familyFunction;
        res.quadratic_vertex=F('fn-quadratic',{a:2,h:1,k:-3})(1);
        res.log_at_one=F('fn-log',{a:2})(1);
        res.log_negative=F('fn-log',{a:2})(-2);
        res.invalid_log=F('fn-log',{a:1})(3);
        res.sqrt_below=F('fn-sqrt',{h:2,k:1})(1);
        const triangle=window.MentorLabTriangle.metrics([0,0],[3,0],[0,4]);
        res.triangle=triangle;
        res.ssa_0=window.MentorLabTriangle.ssaCandidates(4,8,40).length;
        res.ssa_1=window.MentorLabTriangle.ssaCandidates(8,8,40).length;
        res.ssa_2=window.MentorLabTriangle.ssaCandidates(6,8,40).length;
        const proj=window.MentorLab3D.makeProjection(38,36,1);
        res.project_origin=proj.project([0,0,0]);
        res.project_z=proj.project([0,0,1]);
        return {
            ...res,
            log_negative_is_nan:Number.isNaN(res.log_negative),
            invalid_log_is_nan:Number.isNaN(res.invalid_log),
            sqrt_below_is_nan:Number.isNaN(res.sqrt_below)
        };
      }""")
      assert abs(numbers["quadratic_vertex"]+3)<1e-12
      assert abs(numbers["log_at_one"])<1e-12
      assert numbers["log_negative_is_nan"]
      assert numbers["invalid_log_is_nan"]
      assert numbers["sqrt_below_is_nan"]
      t=numbers["triangle"]
      assert abs(t["a"]-5)<1e-12
      assert abs(t["b"]-4)<1e-12
      assert abs(t["c"]-3)<1e-12
      assert abs(t["area"]-6)<1e-12
      assert abs(t["alpha"]-90)<1e-10
      assert (numbers["ssa_0"],numbers["ssa_1"],numbers["ssa_2"])==(0,1,2)
      assert numbers["project_origin"][:2]==[380,239]
      assert numbers["project_z"][1]<239

      page.locator('button[data-family="conic_2d"]').click()
      page.locator("#labPreset").select_option("conic-ellipse")
      # Foci are at +/- sqrt(a^2-b^2) when a > b. One world x-unit = 48 screen px.
      foci=[float(e.get_attribute("cx")) for e in page.locator("#labPlot .lab-focus").all()]
      radius=math.sqrt(16-4)
      assert len(foci)==2 and abs(abs(foci[0]-380)-48*radius)<.06
      assert abs(abs(foci[1]-380)-48*radius)<.06
      page.locator("#labPreset").select_option("conic-parabola")
      xcoords=[float(e.get_attribute("cx")) for e in page.locator("#labPlot .lab-focus").all()]
      assert len(xcoords)>=2 and any(abs(v-428)<.01 for v in xcoords),xcoords

      page.locator('button[data-family="space_3d"]').click()
      page.locator("#labPreset").select_option("3d-plane")
      def polygon_status():
        polys=page.locator("#labPlot polygon")
        for e in polys.all():
          vertices=e.get_attribute("points").split()
          assert len(vertices)>=3
          for xy in vertices:
            pair=xy.split(",")
            assert len(pair)==2,vertices
            coords=[float(x) for x in pair]
            assert all(math.isfinite(x) for x in coords)
      polygon_status()
      for params in [{"p":-2,"q":2,"r":-3},{"p":2,"q":-2,"r":3}]:
        for k,v in params.items():
          page.locator("#labParam_"+k).evaluate(
             "(n,v)=>{n.value=String(v);n.dispatchEvent(new Event('input',{bubbles:true}))}",v)
        polygon_status()
      # Actual pointer rotation updates camera angle and value slider.
      svg=page.locator("#labPlot")
      svg.scroll_into_view_if_needed()
      rect=svg.bounding_box()
      assert rect
      start=(rect["x"]+rect["width"]/2,rect["y"]+rect["height"]/2)
      before=page.locator("#labYaw").input_value()
      page.mouse.move(*start);page.mouse.down()
      page.mouse.move(start[0]+85,start[1]+15,steps=7);page.mouse.up()
      after=page.locator("#labYaw").input_value()
      assert before!=after,(before,after)
      polygon_status()

      for kind in ["3d-prism","3d-pyramid","3d-cylinder","3d-cone","3d-sphere"]:
        page.locator("#labPreset").select_option(kind)
        svg=page.locator("#labPlot")
        assert svg.locator("line,path,polygon,circle").count()>20
        polygon_status()
      assert errors==[],errors
      browser.close()
    print("Mathlab numerical checks PASSED: domains, triangle identities, SSA branches, conic foci, 3D projection, drag rotation and polygon coordinates.")

if __name__=="__main__":
  main()
