const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();
for(const [f,w,h] of [['reel',1080,1920],['post',1080,1350]]){
 const p=await b.newPage({viewport:{width:w,height:h}});
 await p.goto('file://'+path.resolve(__dirname,'poster.html')+'?fmt='+f);await p.waitForTimeout(600);
 await p.screenshot({path:path.resolve(__dirname,'..',`instagram-${f}.png`)});}
await b.close()})()
