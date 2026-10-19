"""Live Chrome regressions for v0.10; run with an isolated synthetic database."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
URL=os.environ.get('STEM_MENTOR_URL','http://127.0.0.1:8000')
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
OUT=ROOT/'artifacts/v010';OUT.mkdir(parents=True,exist_ok=True)


def parameter(page,key,value):
    page.locator('#labParam_'+key).evaluate('(el,v)=>{el.value=String(v);el.dispatchEvent(new Event(el.tagName==="SELECT"?"change":"input",{bubbles:true}))}',value)


def choose(page,family,id):
    page.locator('[data-family="'+family+'"]').click()
    page.locator('#labPreset').select_option(id)


def visible_result(page):
    page.locator('#labAssistToggle').check()


def run():
    result={'checks':[],'errors':[],'external':[],'widths':[]}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=CHROME,args=['--disable-extensions','--no-first-run'])
        try:
            context=browser.new_context(viewport={'width':1440,'height':1000},locale='zh-CN')
            page=context.new_page();page.set_default_timeout(12000)
            page.on('pageerror',lambda e:result['errors'].append(str(e)))
            page.on('request',lambda r:result['external'].append(r.url) if not r.url.startswith(URL) else None)
            assert page.goto(URL,wait_until='networkidle').ok
            page.locator('[data-view="lab"]').click()
            page.wait_for_function('() => document.querySelectorAll(".lab-family-tab").length>0')
            families=page.locator('.lab-family-tab').evaluate_all('(xs)=>xs.map(x=>x.dataset.family)')
            assert {'complex_plane','venn_logic','number_line'}<=set(families),families
            assert len(families)==8
            assert '49' in page.locator('#labSummary').inner_text()
            result['checks'].append('catalog exposes all 49 scenes and three new tool families')

            choose(page,'complex_plane','complex-point')
            assert not page.locator('#labAssistToggle').is_checked()
            assert page.locator('.lab-complex-result').count()==0
            z=page.locator('[data-handle="z"]').first;z.focus()
            before=float(page.locator('#labParam_re').input_value())
            page.keyboard.press('ArrowRight');page.keyboard.press('ArrowRight')
            assert abs(float(page.locator('#labParam_re').input_value())-before-.2)<1e-8
            assert page.evaluate('document.activeElement.getAttribute("data-handle")')=='z'
            z=page.locator('[data-handle="z"]').first;z.scroll_into_view_if_needed()
            b=z.bounding_box();start=(b['x']+b['width']/2,b['y']+b['height']/2)
            page.mouse.move(*start);page.mouse.down();page.mouse.move(start[0]-35,start[1]-18,steps=7);page.mouse.up()
            assert float(page.locator('#labParam_re').input_value())!=before+.2
            parameter(page,'re',0);parameter(page,'im',0)
            assert '辐角未定义' in page.locator('#labMetrics').inner_text()
            result['checks'].append('complex point continuous keyboard drag and zero argument')

            choose(page,'complex_plane','complex-operations')
            parameter(page,'re',1);parameter(page,'im',2);parameter(page,'wr',3);parameter(page,'wi',-4)
            assert page.locator('#labParam_op').evaluate('(x)=>x.tagName')=='SELECT'
            parameter(page,'op',2)
            assert page.locator('.lab-complex-result').count()==0
            visible_result(page)
            assert page.locator('.lab-complex-result').get_attribute('data-value')=='11,2'
            page.locator('.lab-studio-layout').screenshot(path=str(OUT/'complex.png'))
            parameter(page,'op',3);parameter(page,'wr',0);parameter(page,'wi',0)
            assert '除数为零' in page.locator('#labMetrics').inner_text()
            assert page.locator('.lab-complex-result').count()==0
            choose(page,'complex_plane','complex-rotation')
            parameter(page,'re',2);parameter(page,'im',0);parameter(page,'theta',90);visible_result(page)
            point=page.locator('.lab-complex-result').get_attribute('data-value')
            values=[float(v) for v in point.split(',')]
            assert abs(values[0])<1e-9 and abs(values[1]-2)<1e-9
            result['checks'].append('complex operations and rotation are opt-in and handle zero division')

            choose(page,'venn_logic','sets-operations')
            assert page.locator('#lab2dControls').is_hidden()
            assert page.locator('#labSetEditor input[type=checkbox]').count()==16
            assert page.locator('#labSetResult').is_hidden()
            visible_result(page)
            assert page.locator('#labSetResult').get_attribute('data-values')=='1,2,3,4,5,6'
            parameter(page,'op',1)
            assert page.locator('#labSetResult').get_attribute('data-values')=='2,5'
            page.locator('[data-set="A"][data-member="4"]').check()
            assert page.locator('#labSetResult').get_attribute('data-values')=='2,4,5'
            assert page.locator('[data-set="A"][data-member="4"]').is_checked()
            choose(page,'venn_logic','sets-complement');parameter(page,'op',5);visible_result(page)
            assert page.locator('#labSetResult').get_attribute('data-values')=='7,8'
            assert '德摩根' in page.locator('#labSetResult').inner_text()
            page.locator('.lab-studio-layout').screenshot(path=str(OUT/'sets.png'))
            parameter(page,'n',4)
            assert page.locator('#labSetEditor input[type=checkbox]').count()==8
            assert '移除' in page.locator('#labExtraControls').inner_text()
            assert page.locator('#labSetResult').get_attribute('data-values')==''
            result['checks'].append('actual finite members, complement universe and editable Venn regions')

            choose(page,'number_line','interval-single')
            assert page.locator('#labExtraControls').is_hidden()
            parameter(page,'lo',1);parameter(page,'hi',1);parameter(page,'lc',1);parameter(page,'rc',1)
            assert '{1}' in page.locator('#labMetrics').inner_text()
            parameter(page,'lc',0)
            assert '∅' in page.locator('#labMetrics').inner_text()
            parameter(page,'lo',-2);parameter(page,'hi',3);parameter(page,'lc',2);parameter(page,'rc',1)
            assert page.locator('[data-infinite-end="left"]').count()>0
            assert page.locator('[data-handle="lo"]').count()==0
            parameter(page,'lc',1)
            endpoint=page.locator('[data-handle="lo"]').first;endpoint.focus()
            before=float(page.locator('#labParam_lo').input_value())
            page.keyboard.press('ArrowRight');page.keyboard.press('ArrowRight')
            assert abs(float(page.locator('#labParam_lo').input_value())-before-.2)<1e-8
            result['checks'].append('interval open/closed singleton empty rays and keyboard endpoint adjustment')

            choose(page,'number_line','interval-operations')
            visible_result(page)
            assert page.locator('#labSolutionText').text_content()=='{1}'
            parameter(page,'arc',0)
            assert page.locator('#labSolutionText').text_content()=='∅'
            parameter(page,'op',1)
            assert '∪' not in page.locator('#labSolutionText').text_content() # B includes common endpoint
            parameter(page,'blc',0)
            assert '∪' in page.locator('#labSolutionText').text_content()
            parameter(page,'op',3)
            assert '∞' in page.locator('#labSolutionText').text_content()
            page.locator('.lab-studio-layout').screenshot(path=str(OUT/'intervals.png'))
            result['checks'].append('union keeps missing boundary and complement is relative to R')

            choose(page,'number_line','ineq-linear')
            assert page.locator('#labSolutionText').count()==0
            parameter(page,'a',-2);parameter(page,'b',4);visible_result(page)
            assert page.locator('#labSolutionText').text_content()=='[2, +∞)'
            parameter(page,'a',0);parameter(page,'b',0)
            assert page.locator('#labSolutionText').text_content()=='ℝ'
            parameter(page,'relation',0)
            assert page.locator('#labSolutionText').text_content()=='∅'
            choose(page,'number_line','ineq-quadratic');parameter(page,'a',1);parameter(page,'b',-2);parameter(page,'c',1);visible_result(page)
            assert page.locator('#labSolutionText').text_content()=='{1}'
            parameter(page,'relation',0)
            assert page.locator('#labSolutionText').text_content()=='∅'
            parameter(page,'b',0);parameter(page,'c',-1);parameter(page,'relation',1)
            page.locator('.lab-studio-layout').screenshot(path=str(OUT/'inequality.png'))
            choose(page,'number_line','ineq-absolute');parameter(page,'r',-1);visible_result(page)
            assert page.locator('#labSolutionText').text_content()=='∅'
            parameter(page,'relation',2)
            assert page.locator('#labSolutionText').text_content()=='ℝ'
            result['checks'].append('linear quadratic and absolute inequalities expose correct degenerate solutions')
            context.close()

            for width in [390,768,1280]:
                ctx=browser.new_context(viewport={'width':width,'height':900},locale='zh-CN',has_touch=width==390,is_mobile=width==390)
                pg=ctx.new_page();pg.on('pageerror',lambda e:result['errors'].append(str(e)))
                assert pg.goto(URL,wait_until='networkidle').ok
                pg.locator('[data-view="lab"]').click()
                pg.wait_for_function('() => document.querySelectorAll(".lab-family-tab").length===8')
                for family,id in [('complex_plane','complex-operations'),('venn_logic','sets-operations'),('number_line','ineq-quadratic')]:
                    choose(pg,family,id);visible_result(pg)
                    d=pg.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')
                    assert d['scroll']<=d['width']+2,(width,id,d)
                    if width==390 and family=='complex_plane':
                        point=pg.locator('[data-handle="z"]').first
                        point.scroll_into_view_if_needed();bounds=point.bounding_box()
                        xy={'x':bounds['x']+bounds['width']/2,'y':bounds['y']+bounds['height']/2}
                        original=float(pg.locator('#labParam_re').input_value())
                        cdp=ctx.new_cdp_session(pg)
                        cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[xy]})
                        cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':xy['x']-18,'y':xy['y']+10}]})
                        cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
                        assert float(pg.locator('#labParam_re').input_value())!=original
                        cdp.detach();result['checks'].append('390px real Chrome touch input drags a complex endpoint')
                    if width==390 and family=='venn_logic':pg.screenshot(path=str(OUT/'mobile.png'),full_page=True)
                result['widths'].append(width);ctx.close()
            assert not result['errors'],result['errors']
            assert not result['external'],result['external']
        finally:browser.close()
    (OUT/'browser-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    print('v0.10 Chrome PASS:',len(result['checks']),'interaction groups; widths',result['widths'],'page errors=0, external requests=0')


if __name__=='__main__':run()
