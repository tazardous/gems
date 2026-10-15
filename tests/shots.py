"""Saves screenshots of every screen to the folder given as the first argument."""
import sys, glob
from playwright.sync_api import sync_playwright
CH=(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome') or [None])[0]
URL='file://'+__file__.rsplit('/tests/',1)[0]+'/index.html'
out=sys.argv[1] if len(sys.argv)>1 else 'shots'
SETUP="(()=>{ const GQ=__GQ; GQ.S.players=[{name:'Kellan',avatar:'🦁',level:0},{name:'Diana',avatar:'🦄',level:0},{name:'Mason',avatar:'🦊',level:1},{name:'Grandpa',avatar:'🐢',level:2}]; GQ.S.len=1; })()"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CH,args=['--no-sandbox'])
    for (w,h,tag) in [(915,412,'land'),(412,915,'port')]:
        pg=b.new_page(viewport={'width':w,'height':h},device_scale_factor=2)
        pg.goto(URL); pg.wait_for_timeout(300)
        pg.screenshot(path=f'{out}/{tag}_1_title.png')
        pg.evaluate(SETUP); pg.evaluate("__GQ.renderSetup(); __GQ.show('setup')"); pg.screenshot(path=f'{out}/{tag}_2_setup.png')
        pg.evaluate("window.__GQfast=true; __GQ.newGame(); const G=__GQ.G; G.players.forEach((p,i)=>{p.pos=[5,8,8,12][i]; p.coins=[7,4,9,12][i]; p.gems=[1,0,2,1][i];}); __GQ.show('game');")
        pg.evaluate("(()=>{ const G=__GQ.G; G.turn=0; })()")
        pg.evaluate("document.querySelector('#rollBtn').click()"); pg.wait_for_timeout(200)
        pg.evaluate("(()=>{ if(__GQ.Q) __GQ.closeQ(); })()"); pg.wait_for_timeout(200)
        pg.screenshot(path=f'{out}/{tag}_3_board.png')
        for lv,name in [(0,'little'),(1,'kid'),(2,'adult')]:
            pg.evaluate(f"(()=>{{ const G=__GQ.G; const i=G.turn; G.players[i].level={lv}; G.players[i].pos=0; G.spaces[2]={{type:'{'gem' if lv==1 else 'cat'}',cat:'{['math','world','science'][lv]}'}}; __GQ.roll(2); return 0; }})()")
            pg.wait_for_timeout(250); pg.screenshot(path=f'{out}/{tag}_4_q_{name}.png')
            pg.evaluate("(()=>{ const Q=__GQ.Q; if(Q&&Q.q) __GQ.answer((Q.q.ans+1)%Q.q.choices.length); })()"); pg.wait_for_timeout(150)
            if lv==0: pg.screenshot(path=f'{out}/{tag}_5_q_little_wrong.png')
            pg.evaluate("(()=>{ if(__GQ.Q) __GQ.closeQ(); })()"); pg.wait_for_timeout(100)
        pg.evaluate("(()=>{ const G=__GQ.G; G.players.forEach(p=>p.done=true); G.finisher=0; G.turn=G.players.length-1; })()")
        pg.evaluate("(()=>{ const G=__GQ.G; G.players[0].pos=G.n-2; G.players[0].done=false; G.finisher=null; G.turn=0; __GQ.roll(1); return 0; })()"); pg.wait_for_timeout(200)
        pg.evaluate("(()=>{ if(__GQ.Q) __GQ.closeQ(); })()"); pg.wait_for_timeout(300)
        pg.screenshot(path=f'{out}/{tag}_6_end.png')
        pg.close()
    b.close()
