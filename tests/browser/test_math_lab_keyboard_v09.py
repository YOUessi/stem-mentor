"""Keyboard regression: redrawing an SVG must not lose the active handle.

A production change that drops focus after one key must fail this test.
Run only against an isolated synthetic-data test server.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE=os.environ.get('STEM_MENTOR_URL','http://127.0.0.1:8000')
ROOT=Path(__file__).resolve().parents[2]
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def run():
    result={'checks':[], 'errors':[]}
    with sync_playwright() as engine:
        browser=engine.chromium.launch(executable_path=CHROME,headless=True,
            args=['--no-first-run','--disable-extensions'])
        try:
            context=browser.new_context(viewport={'width':1360,'height':1000},locale='zh-CN')
            page=context.new_page()
            page.on('pageerror',lambda e:result['errors'].append(str(e)))
            assert page.goto(BASE,wait_until='networkidle').ok
            page.locator('[data-view="lab"]').click()
            page.wait_for_selector('[data-family="vector_2d"]')
            page.locator('[data-family="vector_2d"]').click()
            page.locator('#labPreset').select_option('vec2d-add')
            point=page.locator('.lab-vector-handle[data-handle="a"]')
            point.focus()
            start=float(page.locator('#labParam_ax').input_value())
            page.keyboard.press('ArrowRight')
            page.keyboard.press('ArrowRight')
            actual=float(page.locator('#labParam_ax').input_value())
            focus=page.evaluate('({tag:document.activeElement.tagName, handle:document.activeElement.getAttribute("data-handle")})')
            print('VECTOR_KEYS',{'before':start,'after':actual,'focus':focus},flush=True)
            assert abs(actual-start-.2)<1e-8, ('Two keypresses must move by 0.2; SVG redraw lost focus',start,actual,focus)
            assert focus['handle']=='a'
            before_y=float(page.locator('#labParam_ay').input_value())
            page.keyboard.press('ArrowUp')
            assert abs(float(page.locator('#labParam_ay').input_value())-before_y-.1)<1e-8
            result['checks'].append('vector continuous keyboard adjustment preserves active endpoint')

            page.locator('[data-family="function_2d"]').click()
            page.locator('#labPreset').select_option('unit-circle')
            page.locator('.lab-unit-point').focus()
            initial=float(page.locator('#labParam_theta').input_value())
            page.keyboard.press('ArrowRight')
            page.keyboard.press('ArrowRight')
            angle=float(page.locator('#labParam_theta').input_value())
            assert angle==initial+2, ('Unit-circle keypresses must accumulate after SVG redraw',initial,angle)
            assert page.evaluate('document.activeElement.getAttribute("data-handle")')=='theta'
            result['checks'].append('unit-circle continuous keyboard rotation preserves focus')
            assert result['errors']==[],result['errors']
            context.close()
        finally:
            browser.close()
    output=ROOT/'artifacts/v09/keyboard-results.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('v0.9 keyboard PASS: 2 continuous keyboard interactions; page errors=0')


if __name__=='__main__':
    run()
