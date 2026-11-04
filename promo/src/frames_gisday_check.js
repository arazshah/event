const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(__dirname,'reel_gisday.html'));await p.waitForTimeout(700);
const ts=[2.6,4.6,6.6,8.6,10.6,12.6,14.6,16.6,19.4,22.5,6.85,23.9];
for(let i=0;i<ts.length;i++){await p.evaluate(t=>render(t),ts[i]);await p.screenshot({path:`/tmp/g${i}.png`})}
await b.close()})()
