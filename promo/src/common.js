const IC={
 mic:'<svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="#0f4c4a" stroke-width="3.4" stroke-linecap="round"><rect x="17" y="5" width="14" height="25" rx="7"/><path d="M10 22c0 8 6 14 14 14s14-6 14-14M24 36v8M16 44h16"/></svg>',
 chart:'<svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="#0f4c4a" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 42h36"/><rect x="9" y="24" width="7" height="14" rx="2"/><rect x="20.5" y="12" width="7" height="26" rx="2"/><rect x="32" y="19" width="7" height="19" rx="2"/></svg>',
 laptop:'<svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="#0f4c4a" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="30" height="21" rx="3"/><path d="M4 38h40M20 19l-4 4 4 4M28 19l4 4-4 4"/></svg>',
 globe:'<svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="#0f4c4a" stroke-width="3.4" stroke-linecap="round"><circle cx="24" cy="24" r="18"/><ellipse cx="24" cy="24" rx="8" ry="18"/><path d="M6 24h36"/></svg>',
 mark:'<svg width="38" height="38" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="8" stroke="#fff" stroke-width="1.6"/><path d="M2 12c3-3 5 2 8-1s5-2 8-4" stroke="#e9a62a" stroke-width="1.6"/><circle cx="10" cy="10" r="2.2" fill="#e9a62a"/></svg>'
};
const CHIPS=[['mic','سخنران'],['chart','ارائه'],['laptop','کارگاه'],['globe','ارائه آنلاین']];
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const ease=x=>1-Math.pow(1-clamp(x),3);
// deterministic map graphic; p in [0,1] is animation progress
function mapSVG(p,w=960,h=520){
  let s=`<svg width="${w}" height="${h}" viewBox="0 0 960 520" style="display:block;background:linear-gradient(#fbfaf0,#f2f1df)">`;
  for(let k=0;k<9;k++){let d='M';for(let x=0;x<=960;x+=30){const y=40+k*58+26*Math.sin(x/150+k*.8)+14*Math.sin(x/62+k*1.4);d+=(x?' L':'')+x+','+y.toFixed(1)}
    s+=`<path d="${d}" fill="none" stroke="#9db8a6" stroke-opacity=".5" stroke-width="2" stroke-dasharray="1400" stroke-dashoffset="${(1-ease(p*1.4-k*.03))*1400}"/>`}
  let rd='M60 470 C300 360 520 330 900 90';
  s+=`<path d="M0 280 C200 240 300 330 520 290 S800 240 960 300" fill="none" stroke="#a9cfd0" stroke-width="16" stroke-opacity=".7" stroke-linecap="round" stroke-dasharray="1300" stroke-dashoffset="${(1-ease(p*1.6))*1300}"/>`;
  s+=`<path d="${rd}" fill="none" stroke="#e9a62a" stroke-width="5" stroke-dasharray="1100" stroke-dashoffset="${(1-ease(p*1.5-.1))*1100}"/>`;
  const pts=[[110,90],[250,150],[760,70],[860,200],[820,420],[620,470],[210,420],[90,330],[430,70],[900,330],[330,490],[700,360]];
  const inn=[[470,205],[535,170],[560,275],[400,300],[480,330],[430,225]];
  pts.forEach((q,i)=>{const a=ease(p*2.2-i*.05);s+=`<circle cx="${q[0]}" cy="${q[1]}" r="${7*a}" fill="#6fa58f" opacity=".85"/>`});
  const R=170*ease(p*1.8-.3);
  s+=`<circle cx="480" cy="260" r="${R}" fill="#e9a62a" fill-opacity=".22" stroke="#e9a62a" stroke-width="4"/>`;
  inn.forEach((q,i)=>{const a=ease(p*3-1.2-i*.12);s+=`<circle cx="${q[0]}" cy="${q[1]}" r="${17*a}" fill="#e9a62a" stroke="#12353f" stroke-width="4"/>`});
  s+=`<circle cx="480" cy="260" r="11" fill="#12353f"/><circle cx="480" cy="260" r="${26+6*Math.sin(p*20)}" fill="none" stroke="#12353f" stroke-width="2" stroke-dasharray="5 5" opacity="${ease(p*2)}"/>`;
  return s+'</svg>';
}
const CODE='<span class="k">SELECT</span> * <span class="k">FROM</span> gis_day\n<span class="k">WHERE</span> city = <span class="s">\'Urmia\'</span>\n  <span class="k">AND</span> topic = <span class="s">\'GeoAI\'</span>\n  <span class="k">AND</span> date = <span class="s">\'2026-11-19\'</span>;';
