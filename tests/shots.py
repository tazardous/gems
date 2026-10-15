"""Saves screenshots of every screen to the folder given as the first argument."""
import sys, glob
from playwright.sync_api import sync_playwright
CH=(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome') or [None])[0]
URL='file://'+__file__.rsplit('/tests/',1)[0]+'/index.html'
out=sys.argv[1] if len(sys.argv)>1 else 'shots'
SETUP="(()=>{ const Q=__AQ; Q.S.players=[{name:'Kellan',hero:0,age:0},{name:'Diana',hero:1,age:0},{name:'Mason',hero:2,age:1},{name:'Grandpa',hero:4,age:2}]; })()"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CH,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':915,'height':412},device_scale_factor=2)
    pg.goto(URL); pg.wait_for_timeout(300); pg.evaluate("window.__AQfast=true")
    pg.screenshot(path=f'{out}/01_title.png')
    pg.evaluate(SETUP); pg.evaluate("__AQ.renderSetup(); __AQ.show('setup')"); pg.screenshot(path=f'{out}/02_setup.png')
    pg.evaluate("__AQ.newAdventure()"); pg.screenshot(path=f'{out}/03_turn.png')
    pg.evaluate("window.__AQmanual=true")
    for L,xs in enumerate([[3,30],[3,40],[3,44],[3,30],[3,56],[3,40]]):
        for k,x in enumerate(xs):
            pg.evaluate(f"(()=>{{ const Q=__AQ; Q.A.lvl={L}; Q.A.turn={L%4}; Q.startRun(); const P=Q.P; P.x={x}*16; P.y=8*16-22; for(let i=0;i<60;i++) Q.step(); Q.draw(); }})()")
            pg.screenshot(path=f'{out}/1{L}_level{L+1}_{k}.png')
    pg.evaluate("(()=>{ const Q=__AQ; Q.A.lvl=5; Q.startRun(); const P=Q.P; P.x=114*16; P.y=8*16-22; for(let i=0;i<150;i++) Q.step(); Q.LV.boss.sweep=1; Q.LV.boss.sweepT=0; for(let i=0;i<75;i++) Q.step(); Q.draw(); })()")
    pg.screenshot(path=f'{out}/20_octopus.png')
    pg.evaluate("(()=>{ const Q=__AQ; const B=Q.LV.boss; B.hp=1; B.inv=0; const h=Q.octoHead(B); Object.assign(Q.P,{x:h.x+25,y:h.y-20,vy:2,ground:false,inv:0}); Q.step(); Q.step(); for(let i=0;i<40;i++) Q.step(); Q.draw(); })()")
    pg.screenshot(path=f'{out}/21_octopus_calm.png')
    pg.evaluate("(()=>{ const Q=__AQ; Q.A.lvl=1; Q.A.turn=3; Q.startRun(); Q.RUN.coins=27; Q.RUN.right=2; Q.RUN.asked=3; Q.finishRun(); })()"); pg.screenshot(path=f'{out}/30_result.png')
    pg.evaluate("document.querySelector('#resBtn').click()"); pg.screenshot(path=f'{out}/31_standings.png')
    pg.evaluate("(()=>{ const Q=__AQ; Q.A.players.forEach((p,i)=>{p.coins=[40,35,52,61][i]; p.gems=[8,9,6,7][i];}); Q.A.over=true; document.querySelector('#stBtn').click(); })()")
    pg.evaluate("(()=>{ const Q=__AQ; Q.A.lvl=5; Q.A.turn=3; Q.startRun(); Q.finishRun(); document.querySelector('#resBtn').click(); })()"); pg.screenshot(path=f'{out}/32_end.png')
    pg.close()
    pg=b.new_page(viewport={'width':412,'height':915},device_scale_factor=2); pg.goto(URL); pg.wait_for_timeout(200); pg.evaluate("window.__AQfast=true")
    pg.evaluate(SETUP); pg.evaluate("__AQ.newAdventure()"); pg.screenshot(path=f'{out}/40_turn_portrait.png')
    b.close()
