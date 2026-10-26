const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const fmt=process.argv[2],[w,h]=fmt=='reel'?[1080,1920]:[1080,1350];const FPS=30,DUR=12;
const dir=process.argv[3];fs.mkdirSync(dir,{recursive:true});
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:w,height:h}});
await p.goto('file://'+path.resolve(__dirname,'scene.html')+'?fmt='+fmt);await p.waitForTimeout(700);
for(let i=0;i<FPS*DUR;i++){await p.evaluate(t=>render(t),i/FPS);
 await p.screenshot({path:`${dir}/${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:93});}
await b.close()})()
