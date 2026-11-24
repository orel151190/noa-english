"""Smoke tests (Playwright, Python). Run: pip install playwright && playwright install chromium && python tests/smoke_test.py"""
import pathlib
from playwright.sync_api import sync_playwright
URL = (pathlib.Path(__file__).parent.parent / 'index.html').resolve().as_uri()
MODES = ['body','house','write','letter','pic','odd','learn','case','talk','say','colors','phon','snd']
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
    pg = b.new_context(viewport={'width':360,'height':780}, permissions=['microphone']).new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(300)
    assert pg.evaluate("document.documentElement.scrollWidth") <= 361, 'horizontal scroll at 360px'
    for m in MODES:
        pg.wait_for_timeout(450); pg.click('#navHome'); pg.click(f'[data-id={m}]'); pg.wait_for_timeout(300)
    # audio coverage
    assert pg.evaluate("WORDS.filter(w=>!AUDIO['w:'+w.w]).length") == 0, 'word without audio'
    assert pg.evaluate("BODY.filter(b=>!AUDIO['t:'+b[0]]).length") == 0, 'body part without audio'
    assert pg.evaluate("TALK.filter(t=>!AUDIO['q:'+t.q]).length") == 0, 'question without audio'
    assert pg.evaluate("AZ.filter(L=>!AUDIO['S:'+L]).length") == 0, 'letter sound missing'
    # correct answer -> speak panel -> parent approve -> star
    pg.wait_for_timeout(450); pg.click('#navHome'); pg.click('[data-id=pic]'); pg.wait_for_timeout(400)
    pg.evaluate("[...document.querySelectorAll('.opt')].find(b=>b.dataset.v===document.querySelector('#sp .en').textContent).click()")
    pg.wait_for_timeout(500); assert pg.locator('.spk').count() == 1, 'speak panel missing'
    pg.click('#skip'); pg.wait_for_timeout(400)
    assert pg.locator('.slot.on').count() == 0, 'skip must not give a star'
    assert pg.locator('.spk').count() == 0, 'skip must move to the next question'
    # wrong answers are never approved, even after many tries
    res = pg.evaluate('''async()=>{ const box=document.createElement('div'); document.body.appendChild(box);
      play=async()=>{}; say=async()=>{}; playBlob=async()=>{}; let done=null;
      listenAndRecord=async(sr,on)=>{ on&&on(); return {heard:['hello']}; };
      speakPanel(box,{target:'apple',autoModel:false,onDone:ok=>{done=ok;}});
      for(let i=0;i<5;i++){ box.querySelector('#mic').click(); await new Promise(r=>setTimeout(r,1300)); }
      listenAndRecord=async(sr,on)=>{ on&&on(); return {heard:['apple']}; };
      const before=done; box.querySelector('#mic').click(); await new Promise(r=>setTimeout(r,1500));
      box.remove(); return [before, done]; }''')
    assert res[0] is None and res[1] is True, f'wrong answer approved or right answer rejected: {res}'
    # reward: one star only after 10 successful tasks
    pg.evaluate("for(let i=0;i<9;i++) success(()=>{})"); pg.wait_for_timeout(1600)
    assert not pg.is_visible('#ov'), 'star overlay before 10 tasks'
    assert pg.locator('.prog i.on').count() == 9, 'progress dots'
    pg.evaluate("success(()=>{})"); pg.wait_for_timeout(1800)
    assert pg.is_visible('#ov'), 'no star overlay after 10 tasks'
    pg.click('#ovBtn'); pg.wait_for_timeout(300)
    assert pg.locator('.prog i.on').count() == 0, 'progress not reset'
    # full session
    pg.wait_for_timeout(450); pg.click('#navHome'); pg.click('[data-id=session]'); pg.wait_for_timeout(300)
    for _ in range(pg.evaluate('SESSION_ORDER.length')): pg.evaluate('sessionNext()'); pg.wait_for_timeout(120)
    assert 'סיימת' in pg.inner_text('h1'), 'session did not finish'
    assert not errs, errs
    print('ALL SMOKE TESTS PASSED'); b.close()
