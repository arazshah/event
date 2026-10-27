const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1620},deviceScaleFactor:2});
await p.goto('file://'+path.resolve(__dirname,'poster4.html'));await p.waitForTimeout(900);
await p.screenshot({path:path.resolve(__dirname,'..','poster-gisday.png')});await b.close()})()
