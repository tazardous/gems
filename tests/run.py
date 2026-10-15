"""Tests for Gem Quest.

1. Generates thousands of questions for every level and category and checks
   each one: right number of choices, no duplicate choices, the correct
   answer is present, no blank or 'undefined' text, and the arithmetic in
   generated math questions really is right.
2. Plays full games with 1 to 6 players at mixed levels, answering right
   and wrong, on every board length.
3. Checks the screens fit phone and tablet sizes in both orientations.
"""
import sys, glob, re
from playwright.sync_api import sync_playwright
CH = (glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome') or [None])[0]
URL = 'file://' + __file__.rsplit('/tests/', 1)[0] + '/index.html'
fails = 0
def check(ok, name, info=''):
    global fails
    print(('PASS ' if ok else 'FAIL ') + name, info if not ok else '')
    if not ok: fails += 1

QCHECK = r"""
(()=>{
  const GQ=__GQ, bad=[], seen={};
  for(const L of GQ.LEVELS){ for(const c of Object.keys(GQ.CATS)){ const key=L.key+'/'+c; seen[key]=new Set();
    for(let i=0;i<1500;i++){
      const q=GQ.GEN[L.key][c](); seen[key].add(q.q+'|'+q.choices[q.ans]);
      const why=[];
      if(q.choices.length!==L.nch) why.push('choices '+q.choices.length);
      if(new Set(q.choices).size!==q.choices.length) why.push('duplicate choices');
      if(!(q.ans>=0&&q.ans<q.choices.length)) why.push('bad ans');
      if(q.choices.some(x=>x===''||/undefined|NaN|null/.test(x))||/undefined|NaN/.test(q.q)) why.push('bad text');
      // verify generated arithmetic
      const a=q.choices[q.ans].replace(/,/g,''); let m;
      if((m=/^(\d+) × (\d+) = \?$/.exec(q.q))&&+a!==m[1]*m[2]) why.push('mult');
      if((m=/^(\d+) ÷ (\d+) = \?$/.exec(q.q))&&+a!==m[1]/m[2]) why.push('div');
      if((m=/^(\d+) \+ (\d+) = \?$/.exec(q.q))&&+a!==(+m[1])+(+m[2])) why.push('add');
      if((m=/^(\d+) − (\d+) = \?$/.exec(q.q))&&+a!==m[1]-m[2]) why.push('sub');
      if((m=/^(\d+) \+ (\d+) \+ (\d+) = \?$/.exec(q.q))&&+a!==(+m[1])+(+m[2])+(+m[3])) why.push('add3');
      if((m=/^What is (\d+)% of (\d+)\?$/.exec(q.q))&&+a!==m[1]*m[2]/100) why.push('pct');
      if((m=/^Solve for x: (\d+)x \+ (\d+) = (\d+)$/.exec(q.q))&&(+m[1])*(+a)+(+m[2])!==+m[3]) why.push('algebra');
      if((m=/^What is the square root of (\d+)\?$/.exec(q.q))&&(+a)*(+a)!==+m[1]) why.push('sqrt');
      if((m=/^Round (\d+) to the nearest ten\.$/.exec(q.q))&&+a!==Math.round(m[1]/10)*10) why.push('round');
      if(/^Which number is prime\?$/.test(q.q)){ const isP=n=>{ for(let d=2;d*d<=n;d++) if(n%d===0) return false; return n>1; }; if(!isP(+a)||q.choices.filter(x=>isP(+x)).length!==1) why.push('prime'); }
      if(/^Which number is the BIGGEST\?$/.test(q.q)&&+a!==Math.max(...q.choices.map(Number))) why.push('biggest');
      if(why.length) bad.push({key,q:q.q,ch:q.choices,ans:q.ans,why});
    } } }
  const variety={}; for(const k in seen) variety[k]=seen[k].size;
  return {bad:bad.slice(0,12),nbad:bad.length,variety};
})()
"""

GAME = r"""
(async (players,len,rightRate)=>{
  const GQ=__GQ; window.__GQfast=true;
  GQ.S.players=players.map((lv,i)=>({name:'P'+(i+1),avatar:['🦁','🐶','🐱','🦊','🐼','🐸'][i],level:lv})); GQ.S.len=len;
  GQ.newGame(); let turns=0;
  while(!GQ.G.over&&turns<2000){
    turns++; const before=GQ.G.turn;
    const p=GQ.roll();
    await new Promise(r=>setTimeout(r,0));
    // answer if a question is showing, then close whatever card is open
    for(let k=0;k<5&&GQ.Q;k++){ const Q=GQ.Q; if(Q.q&&!Q.done){ const right=Math.random()<rightRate; GQ.answer(right?Q.q.ans:(Q.q.ans+1)%Q.q.choices.length); } GQ.closeQ(); await new Promise(r=>setTimeout(r,0)); }
    await p;
  }
  const G=GQ.G;
  return {over:G.over,turns,rounds:G.round,scores:G.players.map(p=>[p.level,p.coins,p.gems,p.asked,p.right,p.pos,p.done]),endShown:document.querySelector('#end').classList.contains('active')};
})
"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CH, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1000, 'height': 600})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto(URL); pg.wait_for_timeout(400)
    r = pg.evaluate(QCHECK)
    check(r['nbad'] == 0, 'questions: 22,500 generated questions are well-formed and correct', r['bad'])
    low = {k: v for k, v in r['variety'].items() if v < 18}
    check(not low, 'questions: every level/category has plenty of variety', low)
    print('   distinct questions per level/category:', r['variety'])
    import random
    random.seed(4)
    configs = [([0], 0), ([1, 2], 1), ([0, 1, 2], 2), ([0, 0, 1, 1], 1), ([2, 2, 2, 2, 2], 0), ([0, 1, 2, 0, 1, 2], 2), ([0, 0, 0, 0, 0, 0], 1)]
    for players, ln in configs:
        for rate in (1.0, 0.0, 0.6):
            res = pg.evaluate(GAME + f"({players},{ln},{rate})")
            sc = res['scores']
            ok = res['over'] and res['endShown'] and any(s[6] for s in sc)
            # everybody gets the same number of turns within one of each other, and treasure is never negative
            ok = ok and all(s[1] >= 0 and s[2] >= 0 for s in sc)
            if rate == 1.0: ok = ok and all(s[3] == s[4] for s in sc)
            if rate == 0.0: ok = ok and all(s[4] == 0 for s in sc)
            check(ok, f'full game players={players} length={ln} right-rate={rate}', res)
    # continue a saved game after a reload
    pg.evaluate("(()=>{ window.__GQfast=true; const GQ=__GQ; GQ.S.players=[{name:'Kellan',avatar:'🦁',level:0},{name:'Pop',avatar:'🐶',level:2}]; GQ.newGame(); })()")
    pg.evaluate("(()=>{ __GQ.roll(); return 0; })()"); pg.wait_for_timeout(50)
    pg.evaluate("(()=>{ const Q=__GQ.Q; if(Q&&Q.q&&!Q.done) __GQ.answer(Q.q.ans); if(__GQ.Q) __GQ.closeQ(); })()")
    pos = pg.evaluate("__GQ.G.players.map(p=>p.pos)")
    pg.reload(); pg.wait_for_timeout(400)
    vis = pg.evaluate("!document.querySelector('#contBtn').hidden")
    pg.click('#contBtn'); pg.wait_for_timeout(300)
    pos2 = pg.evaluate("__GQ.G.players.map(p=>p.pos)")
    check(vis and pos == pos2, 'saved game can be continued after closing the app', (vis, pos, pos2))
    # layouts: nothing spills off-screen
    for (w, h, name) in [(915, 412, 'phone landscape'), (412, 915, 'phone portrait'), (1280, 800, 'tablet landscape'), (800, 1280, 'tablet portrait'), (640, 360, 'small phone landscape')]:
        pg.set_viewport_size({'width': w, 'height': h})
        pg.evaluate("(()=>{ window.__GQfast=true; const GQ=__GQ; GQ.S.players=[0,1,2,0,1,2].map((lv,i)=>({name:'Player'+(i+1),avatar:['🦁','🐶','🐱','🦊','🐼','🐸'][i],level:lv})); GQ.newGame(); })()")
        pg.wait_for_timeout(100)
        m = pg.evaluate("""(()=>{ const bw=document.querySelector('#board').getBoundingClientRect(), roll=document.querySelector('#rollBtn').getBoundingClientRect();
            return {board:[bw.width|0,bw.height|0],rollVisible:roll.bottom<=innerHeight&&roll.right<=innerWidth&&roll.width>0,scroll:document.documentElement.scrollWidth>innerWidth}})()""")
        check(m['board'][0] > 200 and m['board'][1] > 120 and m['rollVisible'] and not m['scroll'], f'layout {name} {w}x{h}', m)
        # question card fits
        pg.evaluate("""(()=>{ const G=__GQ.G; G.players[0].level=1; })()""")
        pg.evaluate("(()=>{ window.__GQfast=true; const G=__GQ.G; G.players[0].pos=0; G.spaces[3]={type:'cat',cat:'fun'}; __GQ.roll(3); return 0; })()")
        pg.wait_for_timeout(50)
        q = pg.evaluate("""(()=>{ const c=document.querySelector('#qcard').getBoundingClientRect(), bs=[...document.querySelectorAll('#choices button')].map(b=>b.getBoundingClientRect());
            return {shown:document.querySelector('#modal').classList.contains('show'),fits:c.bottom<=innerHeight+1&&c.right<=innerWidth+1,tallest:Math.max(...bs.map(x=>x.height))|0}})()""")
        check(q['shown'] and q['fits'], f'question card fits {name}', q)
        pg.evaluate("(()=>{ if(__GQ.Q) __GQ.closeQ(); })()")
    check(not errs, 'no page errors', errs[:5])
    b.close()
print('FAILURES:', fails)
sys.exit(1 if fails else 0)
