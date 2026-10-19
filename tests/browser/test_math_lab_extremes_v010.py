"""All scene defaults, discrete options and deterministic boundary cases.
No learner writes are allowed after entering the independent math laboratory.
"""
import json
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
BASE=os.environ.get('STEM_MENTOR_URL','http://127.0.0.1:8000')
OUT=ROOT/'artifacts/v010';OUT.mkdir(parents=True,exist_ok=True)
NEW_PREFIXES=('complex-','sets-','interval-','ineq-')


def set_value(p,key,v):
    p.locator('#labParam_'+key).evaluate('(el,v)=>{el.value=String(v);el.dispatchEvent(new Event(el.tagName==="SELECT"?"change":"input",{bubbles:true}))}',v)


def check_svg(p,case):
    assert p.locator('#labMetrics .lab-error').count()==0,case
    assert p.locator('#labMetrics .lab-metric').count()>0,case
    bad=p.locator('#labPlot').evaluate('''e=>Array.from(e.querySelectorAll('*')).flatMap(n=>Array.from(n.attributes)).filter(a=>/^(d|points|x|y|cx|cy|r|x1|y1|x2|y2)$/.test(a.name)&&/(NaN|Infinity)/.test(a.value)).map(a=>a.name+'='+a.value)''')
    assert not bad,(case,bad)
    for poly in p.locator('#labPlot polygon').all():
        for pair in poly.get_attribute('points').split():
            parts=pair.split(',');assert len(parts)==2,(case,pair)
            assert all(math.isfinite(float(v)) for v in parts),(case,pair)


def run():
    report={'default_scenes':[],'minmax':[],'option_choices':[],'boundaries':[],'runtime_errors':[],'writes':[],'external':[]}
    with sync_playwright() as engine:
        browser=engine.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args=['--no-first-run','--disable-extensions'])
        try:
            ctx=browser.new_context(viewport={'width':1440,'height':1024},locale='zh-CN',reduced_motion='reduce')
            p=ctx.new_page();p.on('pageerror',lambda e:report['runtime_errors'].append(str(e)))
            p.goto(BASE,wait_until='networkidle');p.locator('[data-view="lab"]').click()
            p.wait_for_function('document.querySelectorAll(".lab-family-tab").length>=8')
            p.on('request',lambda r:report['writes'].append(r.url) if r.method not in ('GET','HEAD') else None)
            p.on('request',lambda r:report['external'].append(r.url) if not r.url.startswith(BASE) else None)
            cat=p.request.get(BASE+'/api/math-lab/catalog').json()
            for item in cat['presets']:
                p.locator('[data-family="'+item['tool']+'"]').click()
                p.locator('#labPreset').select_option(item['id'])
                check_svg(p,item['id']);report['default_scenes'].append(item['id'])
                if not item['id'].startswith(NEW_PREFIXES):continue
                assert not p.locator('#labAssistToggle').is_checked()
                p.locator('#labAssistToggle').check()
                for mode in ['min','max']:
                    for param in item['params']:set_value(p,param['key'],param[mode])
                    check_svg(p,item['id']+mode);report['minmax'].append(item['id']+':'+mode)
                # Reset so each operator is checked at the same documented input.
                p.locator('#labReset').click();p.locator('#labAssistToggle').check()
                for param in item['params']:
                    for option in param.get('options',[]):
                        set_value(p,param['key'],option['value'])
                        check_svg(p,(item['id'],param['key'],option['value']))
                        assert p.locator('#labParam_'+param['key']).input_value()==str(option['value'])
                        report['option_choices'].append([item['id'],param['key'],option['value']])
            cases=[
              ('ineq-quadratic',{'a':1.8,'b':1.2,'c':.2,'relation':1},'{-0.333333}'),
              ('ineq-quadratic',{'a':0,'b':0,'c':0,'relation':1},'ℝ'),
              ('ineq-quadratic',{'a':0,'b':0,'c':0,'relation':0},'∅'),
              ('ineq-quadratic',{'a':-1,'b':2,'c':-1,'relation':3},'{1}'),
              ('ineq-quadratic',{'a':1,'b':0,'c':1,'relation':1},'∅'),
              ('ineq-quadratic',{'a':1,'b':0,'c':1,'relation':2},'ℝ'),
              ('ineq-linear',{'a':0,'b':-2,'relation':0},'ℝ'),
              ('ineq-absolute',{'h':2,'r':0,'relation':1},'{2}'),
              ('ineq-absolute',{'h':2,'r':0,'relation':3},'ℝ'),
              ('ineq-absolute',{'h':2,'r':0,'relation':0},'∅'),
              ('ineq-absolute',{'h':2,'r':-1,'relation':1},'∅'),
              ('interval-operations',{'alo':1,'ahi':1,'alc':1,'arc':1,'op':3},'(−∞, 1) ∪ (1, +∞)'),
            ]
            p.locator('[data-family="number_line"]').click()
            for scene,values,expected in cases:
                p.locator('#labPreset').select_option(scene)
                for k,v in values.items():set_value(p,k,v)
                p.locator('#labAssistToggle').check();check_svg(p,scene)
                assert p.locator('#labSolutionText').text_content()==expected,(scene,values,p.locator('#labSolutionText').text_content())
                report['boundaries'].append({'scene':scene,'params':values,'expected':expected})
            # Finite-set membership editor uses the true universe and supports keyboard activation.
            p.locator('[data-family="venn_logic"]').click();p.locator('#labPreset').select_option('sets-operations')
            for box in p.locator('#labSetEditor input').all():
                if box.is_checked():box.uncheck()
            p.locator('#labAssistToggle').check()
            assert p.locator('#labSetResult').get_attribute('data-values')==''
            p.locator('[data-set="A"][data-member="1"]').focus();p.keyboard.press('Space')
            assert p.locator('#labSetResult').get_attribute('data-values')=='1'
            p.locator('[data-set="A"][data-member="1"]').focus();p.keyboard.press('Space')
            assert p.locator('#labSetResult').get_attribute('data-values')==''
            user=p.evaluate('localStorage.getItem("stem-demo-student")')
            dash=p.request.get(BASE+'/api/students/'+user+'/dashboard').json()
            assert dash['episodes_count']==0 and dash['independent_mastery_verified'] is False
            assert len(report['default_scenes'])>=49
            assert len(report['minmax'])==20
            assert not report['runtime_errors'],report['runtime_errors']
            assert not report['writes'],report['writes']
            assert not report['external'],report['external']
            ctx.close()
        finally:browser.close()
    (OUT/'extreme-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    print('v0.10 extremes PASS: 49 default scenes, 20 min/max combinations,',len(report['option_choices']),'discrete choices,',len(report['boundaries']),'exact boundaries; no external requests or learning writes')

if __name__=='__main__':run()
