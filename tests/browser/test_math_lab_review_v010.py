"""Review regressions discovered by inspecting actual v0.10 screenshots."""
import os
import pytest
from playwright.sync_api import sync_playwright

BASE=os.environ.get('STEM_MENTOR_URL','http://127.0.0.1:8000')

@pytest.fixture
def page():
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args=['--no-first-run','--disable-extensions'])
        try:
            ctx=b.new_context(viewport={'width':1440,'height':1000},locale='zh-CN')
            pg=ctx.new_page();pg.set_default_timeout(7000)
            assert pg.goto(BASE,wait_until='networkidle').ok
            pg.locator('[data-view="lab"]').click()
            pg.wait_for_function('document.querySelectorAll(".lab-family-tab").length===8')
            yield pg
            ctx.close()
        finally:b.close()


def select(page,key,value):
    page.locator('#labParam_'+key).select_option(str(value))


def test_selected_operator_updates_visible_math_not_a_placeholder(page):
    page.locator('[data-family="number_line"]').click()
    page.locator('#labPreset').select_option('ineq-quadratic')
    select(page,'relation',2)
    latex=page.locator('#labFormula').get_attribute('data-latex')
    assert latex and '>' in latex and '\\square' not in latex,latex
    select(page,'relation',1)
    page.wait_for_function('document.querySelector("#labFormula").dataset.latex.includes("leq")')
    page.locator('[data-family="venn_logic"]').click()
    page.locator('#labPreset').select_option('sets-complement')
    select(page,'op',4)
    page.wait_for_function('document.querySelector("#labFormula").dataset.latex==="C_U A"')
    assert 'cup' not in page.locator('#labFormula').get_attribute('data-latex')
    assert page.locator('#labFormula mjx-container svg').count()>0


def test_mobile_venn_shows_both_circles_and_readable_member_summary(page):
    page.set_viewport_size({'width':390,'height':844})
    page.locator('[data-family="venn_logic"]').click()
    box=page.locator('#labPlotBox').bounding_box()
    assert box
    for circle in page.locator('.lab-venn-outline').all():
        actual=circle.bounding_box()
        assert actual['x']>=box['x']-1 and actual['x']+actual['width']<=box['x']+box['width']+1, (actual,box)
    assert page.locator('#labAlternativeView').is_visible()
    assert page.locator('#labAlternativeView .lab-set-region-card').count()==4
    assert '只在 B' in page.locator('#labAlternativeView').inner_text()
    assert '1, 3' in page.locator('#labAlternativeView').inner_text()
    page.locator('[data-family="complex_plane"]').click()
    assert page.locator('#labAlternativeView').is_hidden()
