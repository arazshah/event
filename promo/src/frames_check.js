const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(__dirname,'scene.html')+'?fmt=reel');await p.waitForTimeout(600);
let i=0;for(const t of [1.4,3.5,5.4,7.2,9.2,11.5]){await p.evaluate(t=>render(t),t);await p.screenshot({path:`/tmp/f${i++}.png`,clip:{x:0,y:0,width:1080,height:1920}})}
await b.close()})()
