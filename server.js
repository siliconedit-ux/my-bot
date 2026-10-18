const http=require('http'),fs=require('fs'),path=require('path'),{WebSocketServer}=require('ws');
const ROOT=path.join(__dirname,'public'),MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css'};
const srv=http.createServer((q,r)=>{let u=decodeURIComponent(q.url.split('?')[0]);if(u==='/')u='/index.html';const f=path.join(ROOT,u);if(!f.startsWith(ROOT)){r.writeHead(403);return r.end()}
 fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);return r.end('404')}r.writeHead(200,{'Content-Type':MIME[path.extname(f)]||'application/octet-stream'});r.end(d)})});
const wss=new WebSocketServer({server:srv}),players=new Map(),G={round:0,state:'freeze',t:10,s:{ct:0,t:0},w:null};let nid=1;
const clean=s=>String(s||'Player').replace(/[<>&"']/g,'').slice(0,16)||'Player';
const send=(ws,o)=>ws.readyState===1&&ws.send(JSON.stringify(o)),bc=o=>{const s=JSON.stringify(o);wss.clients.forEach(c=>c.readyState===1&&c.send(s))};
function newRound(){G.round++;G.state='freeze';G.t=10;G.w=null;for(const p of players.values())if(p.team){p.hp=100;p.alive=true;p.inRound=true;if(p.lost){p.armor=0;p.helmet=0}p.lost=false}}
function endRound(w){G.state='end';G.t=5;G.w=w;G.s[w]++}
wss.on('connection',ws=>{const p={id:nid++,name:'Player',team:null,x:0,y:0,z:0,yw:0,cr:0,ar:0,hp:100,alive:false,inRound:false,k:0,d:0,armor:0,helmet:0,lost:false};players.set(p.id,p);send(ws,{t:'w',id:p.id});
 ws.on('message',raw=>{let m;try{m=JSON.parse(raw)}catch(e){return}
  if(m.t==='j'){p.name=clean(m.n);p.team=m.tm==='t'?'t':'ct';if(G.state==='freeze'){p.alive=true;p.inRound=true;p.hp=100}return}
  if(!p.team)return;
  if(m.t==='u'&&p.alive){p.x=+m.x||0;p.y=+m.y||0;p.z=+m.z||0;p.yw=+m.yw||0;p.cr=m.cr?1:0;p.ar=m.ar?1:0}
  else if(m.t==='h'){const v=players.get(m.id);if(!v||!v.alive||!p.alive||v.team===p.team||G.state!=='live')return;let d=Math.min(200,Math.max(1,+m.d||0));if(v.armor>0){v.armor=Math.max(0,v.armor-d*.5);d*=.6}v.hp-=d;
   if(v.hp<=0){v.alive=false;v.hp=0;v.d++;v.lost=true;p.k++;bc({t:'k',k:p.id,v:v.id,h:m.h?1:0,w:String(m.w||'').slice(0,20),kn:p.name,kt:p.team,vn:v.name})}}
  else if(m.t==='sh'&&p.alive)bc({t:'sh',id:p.id,a:m.a,b:m.b,w:m.w});
  else if(m.t==='b'){p.armor=m.a?100:0;p.helmet=m.h?1:0}
  else if(m.t==='c')bc({t:'c',n:p.name,tm:p.team,m:String(m.m||'').replace(/[<>]/g,'').slice(0,80)})});
 ws.on('close',()=>players.delete(p.id))});
setInterval(()=>{G.t-=.05;const L=[...players.values()].filter(p=>p.team&&p.inRound),n=(t,a)=>L.filter(p=>p.team===t&&(!a||p.alive)).length;
 if(G.state==='freeze'&&G.t<=0){G.state='live';G.t=115}
 else if(G.state==='live'){if(n('ct')&&n('t')){if(!n('t',1))endRound('ct');else if(!n('ct',1))endRound('t')}if(G.state==='live'&&G.t<=0)endRound('ct')}
 else if(G.state==='end'&&G.t<=0)newRound();
 const sl={ct:0,t:0},arr=[...players.values()].filter(p=>p.team).map(p=>[p.id,p.name,p.team,p.x,p.y,p.z,p.yw,p.cr,p.ar,Math.ceil(p.hp),p.alive?1:0,p.k,p.d,Math.ceil(p.armor),sl[p.team]++]);
 bc({t:'s',r:G.round,st:G.state,tm:+G.t.toFixed(2),s:G.s,w:G.w,p:arr})},50);
newRound();const PORT=process.env.PORT||3000;srv.listen(PORT,()=>console.log('Server: http://localhost:'+PORT));
