"""Tests for Gem Quest Adventure.

1. Generates 22,500 questions (every age level and subject) and checks each one,
   including recomputing generated math answers.
2. Reachability: every coin and gem in every level can be collected with the
   game's own physics using ADULT settings (single jump, no stepping stones).
3. A bot plays every level at every age level (Little, Kid, Adult): it walks,
   jumps pits and creatures, rides the rafts, answers the Wise Owl (right and
   wrong), fights the Big Octopus and reaches the treasure chest.
4. Octopus checks: a head bounce hurts him, the tentacle sweep and ink hurt you,
   and beating him opens the wall and drops gems.
5. A full 6-level adventure with 1, 3 and 6 players: turns, standings, final
   podium, and resuming a saved adventure after a reload.
"""
import sys, glob
from playwright.sync_api import sync_playwright
CH = (glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome') or [None])[0]
URL = 'file://' + __file__.rsplit('/tests/', 1)[0] + '/index.html'
fails = 0
def check(ok, name, info=''):
    global fails
    print(('PASS ' if ok else 'FAIL ') + name, '' if ok else info, flush=True)
    if not ok: fails += 1

QCHECK = r"""
(()=>{
  const GQ=__AQ, bad=[], seen={};
  for(const L of GQ.AGES){ for(const c of ['math','words','science','world','fun']){ const key=L.key+'/'+c; seen[key]=new Set();
    for(let i=0;i<1500;i++){
      const q=GQ.GEN[L.key][c](); seen[key].add(q.q+'|'+q.choices[q.ans]); const why=[];
      if(q.choices.length!==L.nch) why.push('choices '+q.choices.length);
      if(new Set(q.choices).size!==q.choices.length) why.push('duplicate choices');
      if(!(q.ans>=0&&q.ans<q.choices.length)) why.push('bad ans');
      if(q.choices.some(x=>x===''||/undefined|NaN|null/.test(x))||/undefined|NaN/.test(q.q)) why.push('bad text');
      const a=q.choices[q.ans].replace(/,/g,''); let m;
      if((m=/^(\d+) × (\d+) = \?$/.exec(q.q))&&+a!==m[1]*m[2]) why.push('mult');
      if((m=/^(\d+) ÷ (\d+) = \?$/.exec(q.q))&&+a!==m[1]/m[2]) why.push('div');
      if((m=/^(\d+) \+ (\d+) = \?$/.exec(q.q))&&+a!==(+m[1])+(+m[2])) why.push('add');
      if((m=/^(\d+) − (\d+) = \?$/.exec(q.q))&&+a!==m[1]-m[2]) why.push('sub');
      if((m=/^What is (\d+)% of (\d+)\?$/.exec(q.q))&&+a!==m[1]*m[2]/100) why.push('pct');
      if((m=/^Solve for x: (\d+)x \+ (\d+) = (\d+)$/.exec(q.q))&&(+m[1])*(+a)+(+m[2])!==+m[3]) why.push('algebra');
      if((m=/^Round (\d+) to the nearest ten\.$/.exec(q.q))&&+a!==Math.round(m[1]/10)*10) why.push('round');
      if(why.length) bad.push({key,q:q.q,ch:q.choices,why});
    } } }
  return {nbad:bad.length,bad:bad.slice(0,8)};
})()
"""

JS = r"""
window.setupA=function(ages){ const Q=__AQ; Q.S.players=ages.map((a,i)=>({name:'P'+(i+1),hero:i%6,age:a})); Q.newAdventure(); };
window.resetP=function(x,y){ const P=__AQ.P; Object.assign(P,{x,y,vx:0,vy:0,ground:true,wasGround:true,coyote:7,jbuf:0,inv:0,dbl:false,sx:1,sy:1,mover:null}); };
window.reach=function(lv){
  const Q=__AQ, T=16; setupA([2]); Q.A.lvl=lv; Q.startRun(); const LV=Q.LV, P=Q.P;
  LV.crits.length=0; LV.chestX=-99999; LV.gates.forEach(g=>{ g.open=true; for(let y=0;y<8;y++){ LV.t[y][g.tx]=' '; LV.t[y][g.tx+1]=' '; } }); if(LV.boss) LV.boss.state='calm';
  const starts=[];
  for(let tx=0;tx<LV.W;tx++) for(let ty=1;ty<LV.H;ty++){ const c=LV.t[ty][tx], up=LV.t[ty-1][tx]; if((c==='#'||c==='=')&&up===' ') starts.push({x:tx*T+3,y:ty*T-P.h}); }
  const out=[];
  for(const it of LV.treasure){
    let ok=false;
    const near=starts.filter(s=>Math.abs(s.x-it.x)<7*T);
    const tryRun=(setup,dir,delay)=>{ it.got=false; setup(); for(const k in Q.down) Q.down[k]=false; Q.state='play';
      for(let f=0;f<150;f++){ Q.down.right=dir>0; Q.down.left=dir<0; if(f===delay) Q.hit.add('jump'); Q.step(); if(it.got) return true; if(Q.state!=='play') return false; } return false; };
    outer: for(const s of near) for(const dir of [1,-1,0]) for(const delay of [0,4,8,14,20,30,-1]){ if(tryRun(()=>resetP(s.x,s.y),dir,delay)){ ok=true; break outer; } }
    if(!ok) for(const m of LV.movers) for(const ph of [0,1.6,3.1,4.7]) for(const dir of [0,1,-1]) for(const delay of [-1,0,20,60]){ if(tryRun(()=>{ m.ph=ph; m.x=m.x0+(m.x1-m.x0)*(0.5-0.5*Math.cos(ph)); resetP(m.x+16,m.y-P.h); },dir,delay)){ ok=true; break; } }
    out.push({x:Math.floor(it.x/T),row:Math.floor(it.y/T),ok});
  }
  for(const k in Q.down) Q.down[k]=false;
  return {n:out.length,bad:out.filter(o=>!o.ok)};
};
window.bot=function(lv,age,maxFrames){
  const Q=__AQ,P=Q.P,T=16; setupA([age]); Q.A.lvl=lv; Q.startRun();
  let frames=0,falls=0,lastX=-1,stuck=0,gates=0,maxHurt=0;
  const solid=c=>c==='#'||c==='G'||c==='W';
  while(frames<maxFrames&&Q.state!=='idle'){
    frames++;
    if(Q.state==='quiz'){ const g=Q.gateQ; if(!g.done) Q.answer(gates%2?(g.q.ans+1)%g.q.choices.length:g.q.ans); gates++; Q.closeGate(); continue; }
    if(Q.state==='chest'){ Q.step(); continue; }
    if(Q.state!=='play') return {fail:'state '+Q.state,frames};
    const LV=Q.LV, tile=(tx,ty)=>(tx<0||tx>=LV.W)?'#':(ty<0||ty>=LV.H)?' ':LV.t[ty][tx];
    const px=P.x+P.w, feetRow=Math.floor((P.y+P.h-1)/T);
    let right=true,left=false,jump=false,hold=false;
    const aheadTx=Math.floor((px+4)/T);
    for(let r=feetRow-1;r<=feetRow;r++) if(solid(tile(aheadTx,r))) jump=true;
    const gTx=Math.floor((px+6)/T); let ground=false; for(let r=LV.top;r<LV.H;r++) if(solid(tile(gTx,r))) ground=true;
    // a raft pit: wait for the raft, ride it, then step off
    const raft=LV.movers.find(m=>gTx*T>=m.x0-2&&gTx*T<m.x1+m.w+2);
    if(!ground&&raft&&!P.mover){ jump=false; if(P.ground) right=raft.x<=raft.x0+3; }
    else if(!ground&&!raft) jump=true;
    if(P.mover){ jump=false; const m=P.mover; right=m.x>=m.x1-1; }
    for(const c of LV.crits) if(c.alive&&c.st==='walk'&&c.x>P.x-6&&c.x-P.x<34&&c.y+c.h>P.y-30) jump=true;
    const B=LV.boss;
    if(B&&B.state==='fight'){
      const h=Q.octoHead(B), platY=5*T, onPlat=P.ground&&Math.abs(P.y+P.h-platY)<1;
      if(onPlat){ right=false; if(h.y>=60&&B.inv<=0&&B.bob>0) { jump=true; } }
      else if(P.ground){ right=P.x<119*T; left=false; if(P.x>114*T&&P.x<119.5*T) jump=true; if(P.x>=121*T){ right=false; left=true; } }
      else { right=P.vy<0||P.x<h.x+8; left=P.x>h.x+30; hold=false; }
      if(B.sweepLen>0&&P.ground&&!onPlat) jump=true;
    }
    Q.down.right=right; Q.down.left=left; Q.down.jump=hold;
    if(jump&&P.ground) Q.hit.add('jump');
    Q.step();
    if(P.inv===90) falls++;
    if(Math.abs(P.x-lastX)<0.01&&!(B&&B.state==='fight')&&!P.mover&&right) stuck++; else stuck=0; lastX=P.x;
    if(stuck>300) return {fail:'stuck at tile '+Math.floor(P.x/T),frames};
  }
  for(const k in Q.down) Q.down[k]=false;
  const p=Q.A.players[0];
  return {ok:Q.state==='idle'&&document.querySelector('#result').classList.contains('active'),frames,falls,gates,coins:p.coins,gems:p.gems,boss:Q.LV.boss?Q.LV.boss.state:null};
};
"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CH, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 960, 'height': 540})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto(URL); pg.wait_for_timeout(400)
    pg.evaluate("window.__AQmanual=true; window.__AQfast=true"); pg.evaluate(JS + ";0")
    r = pg.evaluate(QCHECK)
    check(r['nbad'] == 0, 'questions: 22,500 generated questions are well-formed and correct', r['bad'])
    for L in range(6):
        r = pg.evaluate(f"reach({L})")
        check(not r['bad'], f'level {L+1}: all {r["n"]} treasures reachable with ADULT jumping', r['bad'])
    for L in range(6):
        for age in (0, 1, 2):
            r = pg.evaluate(f"bot({L},{age},20000)")
            check(bool(r.get('ok')), f'bot finishes level {L+1} as {["Little","Kid","Adult"][age]}', r)
            print('     ', r, flush=True)
    # octopus mechanics
    r = pg.evaluate("""(()=>{ const Q=__AQ,P=Q.P; setupA([1]); Q.A.lvl=5; Q.startRun(); const LV=Q.LV,B=LV.boss; Q.state='play';
      P.x=110*16; P.y=8*16-22; Q.step(); const awake=B.state==='fight';
      // head bounce
      let h=Q.octoHead(B); resetP(h.x+25,h.y-20); P.vy=2; P.ground=false; const hp0=B.hp; Q.step(); Q.step(); const bounced=B.hp===hp0-1&&P.vy<0;
      // tentacle sweep hurts on the ground
      P.inv=0; B.inv=0; resetP(B.x-80,8*16-22); const hp1=P.hp; B.sweep=0; B.sweepLen=150; B.cd=999; Q.step(); const swept=P.hp<hp1;
      // ink hurts
      P.inv=0; resetP(108*16,8*16-22); const hp2=P.hp; B.sweep=0; B.sweepLen=0; B.ink.push({x:P.x,y:P.y+4,vx:0,vy:0,w:8,h:8}); Q.step(); const inked=P.hp<hp2||P.inv>0;
      // finish him
      while(B.hp>0){ B.inv=0; h=Q.octoHead(B); resetP(h.x+25,h.y-20); P.vy=2; P.ground=false; Q.step(); Q.step(); }
      const open=LV.t[3][132]===' '&&LV.t[3][133]===' ', drops=LV.drops.length;
      return {awake,bounced,swept,inked,calm:B.state==='calm',open,drops}; })()""")
    check(all(r.values()), 'octopus: wakes, head bounce hurts him, tentacle and ink hurt you, beating him opens the way and drops gems', r)
    # full adventures
    for ages in ([0], [0, 1, 2], [0, 1, 2, 0, 1, 2]):
        r = pg.evaluate(f"""(()=>{{ const Q=__AQ; setupA({ages}); const seen=[]; let guard=0;
          while(guard++<200){{ const scr=document.querySelector('.screen.active').id; seen.push(scr);
            if(scr==='turn') {{ document.querySelector('#goBtn').click(); Q.RUN.coins=3; Q.RUN.gems=Q.LV.kind==='gem'?2:0; Q.finishRun(); }}
            else if(scr==='result'||scr==='standings') document.querySelector(scr==='result'?'#resBtn':'#stBtn').click();
            else break; }}
          const A=Q.A; return {{end:document.querySelector('#end').classList.contains('active'),turns:seen.filter(s=>s==='turn').length,stand:seen.filter(s=>s==='standings').length,
            totals:A.players.map(p=>[p.coins,p.gems]),podium:document.querySelectorAll('.pod').length,saved:Q.S.adv}}; }})()""")
        n = len(ages)
        ok = r['end'] and r['turns'] == 6 * n and r['stand'] == 5 and r['podium'] == n and all(t == [18, 6] for t in r['totals']) and r['saved'] is None
        check(ok, f'full 6-level adventure with {n} player(s): turns, standings, podium', r)
    # resume after reload
    pg.evaluate("setupA([0,2]); document.querySelector('#goBtn').click(); __AQ.RUN.coins=4; __AQ.finishRun();")
    pg.reload(); pg.wait_for_timeout(400); pg.evaluate("window.__AQmanual=true; window.__AQfast=true"); pg.evaluate(JS + ";0")
    vis = pg.evaluate("!document.querySelector('#contBtn').hidden")
    pg.click('#contBtn'); pg.wait_for_timeout(200)
    r = pg.evaluate("({scr:document.querySelector('.screen.active').id,name:document.querySelector('#turnName').textContent,coins:__AQ.A.players[0].coins})")
    check(vis and r == {'scr': 'turn', 'name': 'P2', 'coins': 4}, 'saved adventure resumes at the next player\'s turn', (vis, r))
    # layout: the game fills the screen on phones and tablets
    for (w, h) in [(915, 412), (412, 915), (1280, 800), (640, 360)]:
        pg.set_viewport_size({'width': w, 'height': h}); pg.wait_for_timeout(100)
        pg.evaluate("window.__AQmanual=true; setupA([1]); __AQ.startRun(); __AQ.draw();")
        m = pg.evaluate("(()=>{ const c=document.querySelector('#cv').getBoundingClientRect(); return {w:c.width|0,h:c.height|0,fits:c.right<=innerWidth+1&&c.bottom<=innerHeight+1} })()")
        check(m['fits'] and (m['w'] >= w - 2 or m['h'] >= h - 2), f'game fits {w}x{h}', m)
    check(not errs, 'no page errors', errs[:5])
    b.close()
print('FAILURES:', fails)
sys.exit(1 if fails else 0)
