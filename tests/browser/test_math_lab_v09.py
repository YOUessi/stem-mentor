"""Real Chrome v0.9 scene behavior; isolated server supplied by the runner."""
import os,json,math
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
BASE=os.environ.get('STEM_MENTOR_URL','http://127.0.0.1:8000')
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
OUT=ROOT/'artifacts'/'v09';OUT.mkdir(parents=True,exist_ok=True)

def value(page,key,v):
    page.locator('#labParam_'+key).evaluate('(e,v)=>{e.value=String(v);e.dispatchEvent(new Event("input",{bubbles:true}))}',v)

def select(page,family,id):
    page.locator('[data-family="'+family+'"]').click()
    page.locator('#labPreset').select_option(id)

def run():
    report={'checks':[],'page_errors':[],'external_requests':[],'widths':[]}
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path=CHROME,headless=True,args=['--disable-gpu','--no-first-run','--disable-extensions'])
        context=b.new_context(viewport={'width':1440,'height':980},locale='zh-CN')
        page=context.new_page()
        page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
        page.on('request',lambda r:report['external_requests'].append(r.url) if not r.url.startswith(BASE) else None)
        assert page.goto(BASE,wait_until='networkidle').ok
        page.locator('[data-view="lab"]').click()
        page.wait_for_function('document.querySelectorAll("#labFamilies button").length===5')
        assert page.locator('meta[name="theme-color"]').get_attribute('content')=='#174938'
        catalog=page.request.get(BASE+'/api/math-lab/catalog').json()
        assert len(catalog['presets'])==39
        report['checks'].append('green layout, 39-scene catalog and fifth vector family')

        select(page,'vector_2d','vec2d-add')
        assert page.locator('.lab-vector-handle').count()==2
        assert not page.locator('#labAssistToggle').is_checked()
        assert page.locator('.lab-resultant').count()==0
        page.locator('#labAssistToggle').check()
        assert page.locator('.lab-resultant').count()>=1
        before=page.locator('#labParam_ax').input_value()
        point=page.locator('.lab-vector-handle[data-handle="a"]').first
        point.scroll_into_view_if_needed();r=point.bounding_box();assert r
        x,y=r['x']+r['width']/2,r['y']+r['height']/2
        page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+43,y-18,steps=6);page.mouse.up()
        assert page.locator('#labParam_ax').input_value()!=before
        report['checks'].append('vector drag synchronizes sliders; resultant requires explicit opt-in')
        page.locator('#labPreset').select_option('vec2d-projection')
        value(page,'bx',0);value(page,'by',0);page.locator('#labAssistToggle').check()
        assert '未定义' in page.locator('#labMetrics').inner_text()
        assert page.locator('.lab-projection').count()==0
        value(page,'bx',2);value(page,'ax',3);value(page,'ay',2)
        assert page.locator('.lab-projection').count()>0
        page.locator('.lab-studio-layout').screenshot(path=str(OUT/'vectors.png'))
        report['checks'].append('zero-target vector rejects projection and direction')

        select(page,'function_2d','unit-circle')
        assert page.locator('#lab2dControls').is_hidden(), 'Unit circle must not expose a nonfunctional zoom control'
        value(page,'theta',90)
        assert '未定义' in page.locator('#labMetrics').inner_text()
        assert page.locator('.lab-unit-point').count()==1
        value(page,'theta',-450)
        metrics=page.locator('#labMetrics').inner_text()
        assert '−' in metrics or '-' in metrics
        assert page.locator('.lab-linked-sin').count()==1
        assert page.locator('.lab-linked-cos').count()==1
        page.locator('.lab-studio-layout').screenshot(path=str(OUT/'unit-circle.png'))
        report['checks'].append('unit circle degree/radian, negative turns, sin/cos and undefined tangent')

        page.locator('#labPreset').select_option('derivative-quadratic')
        assert page.locator('.lab-tangent').count()==0
        page.locator('#labAssistToggle').check()
        assert page.locator('.lab-tangent').count()>0
        value(page,'x',1);value(page,'h',.01)
        assert '2.010' in page.locator('#labMetrics').inner_text()
        value(page,'h',0)
        assert page.locator('.lab-secant').count()==0
        assert page.locator('.lab-tangent').count()>0
        value(page,'h',.3)
        page.locator('.lab-studio-layout').screenshot(path=str(OUT/'derivative.png'))
        report['checks'].append('true secant versus analytic tangent; h=0 has no secant')
        page.locator('#labPreset').select_option('derivative-abs')
        page.locator('#labAssistToggle').check()
        value(page,'x',0)
        assert page.locator('.lab-tangent').count()==0
        assert '不可导' in page.locator('#labMetrics').inner_text()
        page.locator('#labPreset').select_option('derivative-log')
        page.locator('#labAssistToggle').check()
        value(page,'x',.5);value(page,'h',-1)
        assert page.locator('.lab-secant').count()==0
        assert '定义域' in page.locator('#labMetrics').inner_text()
        report['checks'].append('absolute corner and log-domain violations never produce fake lines')

        select(page,'space_3d','3d-section-prism')
        value(page,'nx',1);value(page,'ny',1);value(page,'nz',1);value(page,'t',2)
        polygon=page.locator('.lab-section-polygon')
        assert polygon.count()==1
        assert len(polygon.get_attribute('points').split())==6
        assert '六边形' in page.locator('#labMetrics').inner_text()
        assert '20.785' in page.locator('#labMetrics').inner_text()
        before=page.locator('#labMetrics').inner_text();pts=polygon.get_attribute('points')
        page.locator('#labYaw').evaluate('(e)=>{e.value="115";e.dispatchEvent(new Event("input",{bubbles:true}))}')
        assert polygon.get_attribute('points')!=pts
        assert page.locator('#labMetrics').inner_text()==before
        page.locator('.lab-studio-layout').screenshot(path=str(OUT/'section-hexagon.png'))
        value(page,'nx',0);value(page,'ny',0);value(page,'nz',0)
        assert '零法向量' in page.locator('#labMetrics').inner_text()
        assert page.locator('.lab-section-polygon').count()==0
        value(page,'nz',1);value(page,'t',10)
        assert '无交' in page.locator('#labMetrics').inner_text()
        report['checks'].append('actual six-edge cube section, angle invariant area, zero normal and empty cut')
        page.locator('#labPreset').select_option('3d-section-pyramid')
        value(page,'t',2)
        assert '4.000' in page.locator('#labMetrics').inner_text()
        value(page,'t',4)
        assert '点' in page.locator('#labMetrics').inner_text()
        assert page.locator('.lab-section-polygon').count()==0
        page.locator('#labPreset').select_option('3d-section-sphere')
        value(page,'r',2);value(page,'t',1)
        assert '9.425' in page.locator('#labMetrics').inner_text()
        value(page,'t',2)
        assert '相切' in page.locator('#labMetrics').inner_text()
        report['checks'].append('pyramid cross-section/apex and sphere circle/tangent distinguished')

        # Leaving a draggable scene must remove its DOM0 handlers, not corrupt a later 2D plot.
        select(page,'function_2d','fn-linear')
        assert page.locator('#labPlot').evaluate('(e)=>e.onpointerdown===null')
        select(page,'function_2d','unit-circle');page.locator('#labReset').click()
        assert page.locator('#labParam_theta').input_value()=='35'
        assert not page.locator('#labAssistToggle').is_checked()
        report['checks'].append('scene reset and event cleanup prevent cross-tool corruption')
        context.close()
        for width in [390,768,1280]:
            ctx=b.new_context(viewport={'width':width,'height':950},locale='zh-CN')
            pg=ctx.new_page();pg.on('pageerror',lambda e:report['page_errors'].append(str(e)))
            assert pg.goto(BASE,wait_until='networkidle').ok
            pg.locator('[data-view="lab"]').click();pg.wait_for_selector('[data-family="vector_2d"]')
            select(pg,'space_3d','3d-section-sphere');pg.locator('#labAssistToggle').check()
            dims=pg.evaluate('({v:innerWidth,s:document.documentElement.scrollWidth})')
            assert dims['s']<=dims['v']+2,dims
            if width==390:pg.screenshot(path=str(OUT/'mobile.png'),full_page=True)
            report['widths'].append(width);ctx.close()
        b.close()
    assert not report['page_errors'],report['page_errors']
    assert not report['external_requests'],report['external_requests']
    (OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('v0.9 Browser PASS:',len(report['checks']),'checks, widths',report['widths'],'errors=0 external=0')
if __name__=='__main__':run()
