const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:2});
await p.goto('file://'+path.resolve(__dirname,'teaser.html'));await p.waitForTimeout(800);
await p.screenshot({path:path.resolve(__dirname,'..','teaser-poster.png')});await b.close()})()
