const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const fmt='x',[w,h]=[1080,1920];const FPS=30,DUR=24;
const dir=process.argv[3];fs.mkdirSync(dir,{recursive:true});
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:w,height:h}});
await p.goto('file://'+path.resolve(__dirname,'reel_gisday.html'));await p.waitForTimeout(700);
for(let i=0;i<FPS*DUR;i++){await p.evaluate(t=>render(t),i/FPS);
 await p.screenshot({path:`${dir}/${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:93});}
await b.close()})()
