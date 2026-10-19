"""All scenes plus parameter extremes and no dishonest grading side effects."""
import os,json,math
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
BASE=os.environ.get('STEM_MENTOR_URL','http://127.0.0.1:8000')
OUT=ROOT/'artifacts'/'v09';OUT.mkdir(parents=True,exist_ok=True)

def run():
    report={'default_scenes':[],'extreme_checks':[],'runtime_errors':[]}
    with sync_playwright() as engine:
        browser=engine.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args=['--no-first-run','--disable-extensions'])
        context=browser.new_context(viewport={'width':1440,'height':960},locale='zh-CN',reduced_motion='reduce')
        p=context.new_page();p.on('pageerror',lambda e:report['runtime_errors'].append(str(e)))
        p.goto(BASE,wait_until='networkidle');p.locator('[data-view="lab"]').click()
        p.wait_for_function('document.querySelectorAll("#labFamilies button").length>=8')
        catalog=p.request.get(BASE+'/api/math-lab/catalog').json()
        for item in catalog['presets']:
            # Preserve this suite's exact v0.9 39 scenes and 20 extremes. v0.10 has its own complete suite.
            if item['tool'] in {'complex_plane','venn_logic','number_line','sequence_2d','probability_2d','statistics_2d'} or item['id'].startswith('extrema-'):continue
            p.locator('[data-family="'+item['tool']+'"]').click()
            p.locator('#labPreset').select_option(item['id'])
            assert p.locator('#labMetrics .lab-error').count()==0,item['id']
            assert p.locator('#labMetrics .lab-metric').count()>0,item['id']
            assert p.locator('#labPlot line, #labPlot path, #labPlot circle').count()>0,item['id']
            report['default_scenes'].append(item['id'])
            if item.get('assist_default') is not False:continue
            p.locator('#labAssistToggle').check()
            for mode in ['min','max']:
                for param in item['params']:
                    p.locator('#labParam_'+param['key']).evaluate('(el,v)=>{el.value=String(v);el.dispatchEvent(new Event("input",{bubbles:true}))}',param[mode])
                assert p.locator('#labMetrics .lab-error').count()==0,(item['id'],mode)
                bad=p.locator('#labPlot').evaluate('''e=>Array.from(e.querySelectorAll('*')).flatMap(n=>Array.from(n.attributes)).filter(a=>/^(d|points|x|y|cx|cy|r|x1|y1|x2|y2)$/.test(a.name)&&/(NaN|Infinity)/.test(a.value)).map(a=>a.name+'='+a.value)''')
                assert not bad,(item['id'],mode,bad)
                for poly in p.locator('#labPlot polygon').all():
                    for pair in poly.get_attribute('points').split():
                        vals=pair.split(',');assert len(vals)==2,(item['id'],pair)
                        assert all(math.isfinite(float(v)) for v in vals)
                report['extreme_checks'].append(item['id']+':'+mode)
        # Concept tools are read-only: exploration does not create fake solved questions or grades.
        student=p.evaluate('localStorage.getItem("stem-demo-student")')
        dashboard=p.request.get(BASE+'/api/students/'+student+'/dashboard').json()
        assert dashboard['episodes_count']==0
        assert dashboard['independent_mastery_verified'] is False
        assert len(report['default_scenes'])==39
        assert len(report['extreme_checks'])==20
        assert report['runtime_errors']==[]
        context.close();browser.close()
    (OUT/'extreme-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('v0.9 extremes PASS: 39 scenes, 20 parameter extreme sets, no nonfinite SVG and no fabricated learning records')
if __name__=='__main__':run()
