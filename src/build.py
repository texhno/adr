"""Builds the ADR refresher trainer site (index.html, sw.js) in the repo root from the files in src/.
Usage (from the repo root): ../.venv/Scripts/python.exe src/build.py [artifact_fragment.html]"""
import json, sys, pathlib, hashlib
import pymupdf

SRC = pathlib.Path(__file__).resolve().parent
SITE = SRC.parent
sys.path.insert(0, str(SRC))
from topics import TOPICS

with open(SRC / "questions.json", encoding="utf-8") as f:
    qs = json.load(f)
ans = {}
for line in (SRC / "answers.tsv").read_text(encoding="utf-8").splitlines():
    n, letter, flag, why = line.rstrip("\n").split("\t")
    ans[int(n)] = ("abc".index(letter), flag == "⚠", why)
topic_of = {n: ti for ti, (_, _, l) in enumerate(TOPICS) for n in l}
assert sorted(topic_of) == [q["n"] for q in qs]

def img_entry(name):
    jpg = name.replace(".png", ".jpg")
    pm = pymupdf.Pixmap(str(SITE / "img" / jpg))
    return ["img/" + jpg, pm.width, pm.height]

data = {
    "t": [{"id": tid, "name": name} for tid, name, _ in TOPICS],
    "q": [{"n": q["n"], "q": q["q"], "o": q["opts"], "c": ans[q["n"]][0], "f": int(ans[q["n"]][1]),
           "w": ans[q["n"]][2], "t": topic_of[q["n"]],
           "i": [img_entry(i) for i in q.get("imgs", [])]} for q in qs],
}
DATA = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

CSS = (SRC / "trener.css").read_text(encoding="utf-8")

BODY = """<div class="wrap">
<main id="home">
  <header>
    <h1>Тренажер ADR (ДОПНВ)</h1>
    <p class="lead">Курс перепідготовки: <b>__N__ офіційних питань</b> з Тестів МВС. Відповіді й пояснення — за текстом ДОПНВ.</p>
  </header>
  <section class="exam" aria-labelledby="exam-h">
    <h2 id="exam-h">Іспит, як справжній</h2>
    <div class="facts">
      <div class="fact"><div class="v num">15</div><div class="l">випадкових питань</div></div>
      <div class="fact"><div class="v num">30 хв</div><div class="l">на все</div></div>
      <div class="fact"><div class="v num">≤2</div><div class="l">помилки</div></div>
    </div>
    <button type="button" class="btn main" id="go-exam">Почати іспит</button>
  </section>
  <div class="modes">
    <button type="button" class="mode" id="go-mist"><b>Робота над помилками</b><span id="go-mist-n">поки немає</span></button>
    <button type="button" class="mode" id="go-all"><b>Усі питання</b><span>__N__ вперемішку, з поясненнями</span></button>
  </div>
  <section class="block" aria-labelledby="prog-h">
    <h2 id="prog-h">Ваш прогрес</h2>
    <div class="prog">
      <div class="pbox"><div class="v num" id="st-learn">0</div><div class="l">з __N__ питань востаннє відповіли правильно</div><div class="meter"><i id="st-learn-bar" style="width:0%"></i></div></div>
      <div class="pbox"><div class="v num" id="st-exam">—</div><div class="l" id="st-exam-l">іспитів ще не було</div></div>
    </div>
  </section>
  <section class="block" aria-labelledby="top-h">
    <h2 id="top-h">Тренування за темами</h2>
    <p class="lead" style="margin-bottom:10px">Після кожної відповіді одразу видно, чи правильно, і пояснення.</p>
    <div class="topics" id="topics"></div>
  </section>
  <section class="block" id="hist-box" hidden aria-labelledby="hist-h">
    <h2 id="hist-h">Останні іспити</h2>
    <ul class="hist" id="hist"></ul>
  </section>
  <div class="reset">
    <button type="button" class="btn small ghost" id="reset">Скинути прогрес</button>
    <span id="reset-ask" hidden>Видалити всі відповіді й історію іспитів? <button type="button" class="btn small" id="reset-yes">Так, скинути</button> <button type="button" class="btn small ghost" id="reset-no">Ні</button></span>
  </div>
  <p class="foot">Прогрес зберігається тільки в цьому браузері на цьому телефоні. МВС відповідей не публікує, тому їх визначено за текстом ДОПНВ; позначка <b>⚠ уточнити</b> — питання, яке краще перепитати в навчальному центрі. Джерело: <a href="https://mvs.gov.ua/normativno-pravovi-akti/nakaz-mvs-vid-04092026-834-pro-vnesennia-zmin-do-testiv-z-pitan-doroznyogo-perevezennia-nebezpecnix-vantaziv" target="_blank" rel="noopener">Тести МВС, розділ V «Курс перепідготовки»</a>. Нумерація своя: у документі МВС після № 198 номери 151–198 повторюються.</p>
</main>

<main id="quiz" hidden>
  <div class="qbar">
    <div class="row">
      <button type="button" class="btn small ghost" id="q-stop">Завершити</button>
      <span class="ttl" id="q-title"></span>
      <span class="score num" id="q-score"></span>
      <span class="timer" id="q-timer" hidden></span>
      <span class="pos num" id="q-pos"></span>
    </div>
    <div class="track"><i id="q-bar" style="width:0%"></i></div>
    <div class="confirm" id="q-confirm" hidden><span>Завершити іспит зараз? Питання без відповіді зарахуються як помилки.</span><button type="button" class="btn small main" id="q-confirm-yes">Завершити</button><button type="button" class="btn small" id="q-confirm-no">Продовжити</button></div>
  </div>
  <div class="card" id="q-card"></div>
  <div class="next"><button type="button" class="btn main" id="q-next">Далі</button></div>
  <p class="hint" id="q-hint"></p>
</main>

<main id="res" hidden>
  <div class="verdict">
    <p class="big" id="r-big"></p>
    <p class="lead" id="r-sub"></p>
    <div class="rbtns" id="r-btns"></div>
  </div>
  <section class="block">
    <h2 id="r-h"></h2>
    <div class="rlist" id="r-list"></div>
  </section>
</main>
</div>
"""

JS = r"""
(function(){
if(!Element.prototype.closest){Element.prototype.closest=function(sel){var el=this;while(el&&el.nodeType===1){var m=el.matches||el.webkitMatchesSelector||el.msMatchesSelector;if(m&&m.call(el,sel))return el;el=el.parentElement}return null}}
var D=window.__ADR, Q=D.q, T=D.t, byN={}, LET=['а','б','в'];
Q.forEach(function(q){byN[q.n]=q});
var store=null; try{store=window.localStorage;store.getItem('adr-prog')}catch(e){store=null}
function load(k,d){try{var v=store&&store.getItem(k);return v?JSON.parse(v):d}catch(e){return d}}
function save(k,v){try{store&&store.setItem(k,JSON.stringify(v))}catch(e){}}
var prog=load('adr-prog',{}), hist=load('adr-exams',[]);
function $(id){return document.getElementById(id)}
var views={home:$('home'),quiz:$('quiz'),res:$('res')};
function show(v){for(var k in views)views[k].hidden=k!==v;window.scrollTo(0,0)}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function shuffle(a){a=a.slice();for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),t=a[i];a[i]=a[j];a[j]=t}return a}
function mark(n,ok){var p=prog[n]||[0,0,0];p[ok?0:1]++;p[2]=ok?1:0;prog[n]=p;save('adr-prog',prog)}
function isLearned(n){return prog[n]&&prog[n][2]===1}
function mistakes(){return Q.filter(function(q){return prog[q.n]&&prog[q.n][2]===0}).map(function(q){return q.n})}
function p2(x){return x<10?'0'+x:''+x}
function each(list,fn){Array.prototype.forEach.call(list,fn)}
function mmss(s){return Math.floor(s/60)+':'+p2(s%60)}
function fmtDate(t){var d=new Date(t);return p2(d.getDate())+'.'+p2(d.getMonth()+1)+' '+p2(d.getHours())+':'+p2(d.getMinutes())}
function word(n,a,b,c){var m=n%10,h=n%100;return (m===1&&h!==11)?a:(m>=2&&m<=4&&(h<10||h>=20))?b:c}

function renderHome(){
  var learned=Q.filter(function(q){return isLearned(q.n)}).length;
  $('st-learn').textContent=learned;
  $('st-learn-bar').style.width=(learned/Q.length*100).toFixed(1)+'%';
  var passed=hist.filter(function(h){return h.ok}).length;
  $('st-exam').textContent=hist.length?passed+' з '+hist.length:'—';
  $('st-exam-l').textContent=hist.length?'іспитів складено':'іспитів ще не було';
  var m=mistakes();
  $('go-mist').disabled=!m.length;
  $('go-mist-n').textContent=m.length?m.length+' '+word(m.length,'питання','питання','питань')+', де ви помилились':'поки немає';
  var h='';
  T.forEach(function(t,ti){
    var list=Q.filter(function(q){return q.t===ti}), ok=list.filter(function(q){return isLearned(q.n)}).length;
    h+='<button type="button" class="topic" data-t="'+ti+'"><span class="tr"><span class="tn">'+esc(t.name)+'</span><span class="tc num">'+ok+' / '+list.length+'</span></span><span class="meter"><i style="width:'+(ok/list.length*100).toFixed(1)+'%"></i></span></button>';
  });
  $('topics').innerHTML=h;
  $('hist-box').hidden=!hist.length;
  $('hist').innerHTML=hist.slice(-5).reverse().map(function(x){
    return '<li><span class="num">'+fmtDate(x.d)+'</span><span class="num">'+x.e+' '+word(x.e,'помилка','помилки','помилок')+' · '+mmss(x.s)+'</span><span class="'+(x.ok?'pass':'fail')+'">'+(x.ok?'склали':'не склали')+'</span></li>';
  }).join('');
}

var S=null, tick=null;
function start(mode,list,title){
  if(tick){clearInterval(tick);tick=null}
  S={mode:mode,list:list,i:0,ans:{},t0:Date.now(),title:title,right:0,wrong:0,done:false};
  $('q-title').textContent=title;
  $('q-timer').hidden=mode!=='exam';
  $('q-score').hidden=false;
  $('q-confirm').hidden=true;
  if(mode==='exam'){S.end=Date.now()+30*60*1000;tick=setInterval(updTimer,1000);updTimer()}
  show('quiz');renderQ();
}
function updTimer(){
  if(!S||S.done)return;
  var s=Math.max(0,Math.round((S.end-Date.now())/1000));
  $('q-timer').textContent=mmss(s);
  $('q-timer').classList.toggle('low',s<=300);
  if(s<=0)finish(true);
}
function optsHtml(q,mine,reveal){
  return '<div class="opts">'+q.o.map(function(o,k){
    var c='opt';
    if(reveal){if(k===q.c)c+=' ok';else if(k===mine)c+=' bad';else c+=' dim'}
    else if(k===mine)c+=' sel';
    return '<button type="button" class="'+c+'" data-k="'+k+'"'+(reveal?' disabled':'')+'><span class="l">'+LET[k]+'</span><span>'+esc(o)+'</span></button>';
  }).join('')+'</div>';
}
function qHead(q,showFlag){
  var h='<div class="qh"><span class="n num">№ '+q.n+'</span>'+(showFlag&&q.f?'<span class="flag">⚠ уточнити</span>':'')+'</div><p class="qt">'+esc(q.q)+'</p>';
  q.i.forEach(function(im){h+='<img src="'+im[0]+'" width="'+im[1]+'" height="'+im[2]+'" decoding="async" alt="Малюнок до питання № '+q.n+'">'});
  return h;
}
function whyHtml(q,ok){return '<p class="why '+(ok?'good':'badw')+'"><b>'+(ok?'Правильно.':'Неправильно, правильна — '+LET[q.c]+').')+'</b> '+esc(q.w)+'</p>'}
function renderQ(){
  var n=S.list[S.i], q=byN[n], exam=S.mode==='exam', mine=S.ans[n];
  $('q-pos').textContent=(S.i+1)+' / '+S.list.length;
  $('q-bar').style.width=(S.i/S.list.length*100)+'%';
  $('q-score').textContent='✓ '+S.right+'  ✗ '+S.wrong;
  $('q-card').innerHTML=qHead(q,false)+optsHtml(q,mine,false);
  var last=S.i===S.list.length-1, nx=$('q-next');
  nx.textContent=last?(exam?'Завершити іспит':'Підсумок'):'Далі';
  nx.hidden=true;
  $('q-hint').textContent='Натисніть на відповідь — одразу побачите, чи правильно, і пояснення.';
}
function choose(k){
  if(!S||S.done)return;
  var n=S.list[S.i], q=byN[n], card=$('q-card');
  if(S.ans[n]!=null)return;
  S.ans[n]=k; var ok=k===q.c; if(ok)S.right++;else S.wrong++; mark(n,ok);
  each(card.querySelectorAll('.opt'),function(b){
    var j=+b.dataset.k; b.disabled=true; b.classList.remove('sel');
    b.classList.add(j===q.c?'ok':j===k?'bad':'dim');
  });
  if(q.f)card.querySelector('.qh').insertAdjacentHTML('beforeend','<span class="flag">⚠ уточнити</span>');
  card.insertAdjacentHTML('beforeend',whyHtml(q,ok));
  $('q-score').textContent='✓ '+S.right+'  ✗ '+S.wrong;
  var nx=$('q-next'); nx.hidden=false; nx.disabled=false; 
  $('q-hint').textContent='';
}
$('q-card').addEventListener('click',function(e){var b=e.target.closest('.opt');if(b&&!b.disabled)choose(+b.dataset.k)});
$('q-next').addEventListener('click',function(){
  if(!S)return;
  if(S.i<S.list.length-1){S.i++;renderQ();window.scrollTo(0,0)}else finish(false);
});
$('q-stop').addEventListener('click',function(){
  if(!S)return;
  if(S.mode==='exam'){$('q-confirm').hidden=false;return}
  if(Object.keys(S.ans).length)finish(false);else{S=null;renderHome();show('home')}
});
$('q-confirm-yes').addEventListener('click',function(){finish(false)});
$('q-confirm-no').addEventListener('click',function(){$('q-confirm').hidden=true});
document.addEventListener('keydown',function(e){
  if(views.quiz.hidden||!S||e.ctrlKey||e.metaKey||e.altKey)return;
  var k={'1':0,'2':1,'3':2,'а':0,'б':1,'в':2,'a':0,'b':1,'c':2}[String(e.key||'').toLowerCase()];
  if(k!=null){var b=$('q-card').querySelector('.opt[data-k="'+k+'"]');if(b&&!b.disabled){e.preventDefault();choose(k)}}
});

function finish(timeout){
  if(!S||S.done)return;
  S.done=true; if(tick){clearInterval(tick);tick=null}
  var exam=S.mode==='exam', sec=Math.round((Date.now()-S.t0)/1000), shown, wrong=[];
  if(exam){
    sec=Math.min(sec,1800);
    S.list.forEach(function(n){if(S.ans[n]!==byN[n].c)wrong.push(n)});
    var ok=wrong.length<=2;
    hist.push({d:Date.now(),ok:ok,e:wrong.length,s:sec}); if(hist.length>50)hist=hist.slice(-50); save('adr-exams',hist);
    $('r-big').className='big '+(ok?'pass':'fail');
    $('r-big').textContent=ok?'Склали':'Не склали';
    $('r-sub').textContent=(timeout?'Час вийшов. ':'')+'Помилок: '+wrong.length+' з 15 (можна до 2). Час: '+mmss(sec)+'.';
    shown=S.list;
    $('r-h').textContent=wrong.length?'Розбір білета':'Усі відповіді правильні';
  }else{
    shown=S.list.filter(function(n){return S.ans[n]!=null});
    shown.forEach(function(n){if(S.ans[n]!==byN[n].c)wrong.push(n)});
    $('r-big').className='big';
    $('r-big').textContent=(shown.length-wrong.length)+' з '+shown.length;
    $('r-sub').textContent=S.title+': правильних відповідей. '+(wrong.length?'Нижче — питання, де була помилка.':'Без жодної помилки.');
    $('r-h').textContent=wrong.length?'Помилки':'';
    shown=wrong;
  }
  $('r-list').innerHTML=shown.map(function(n){
    var q=byN[n],a=S.ans[n],ok=a===q.c;
    if(exam&&ok)return '<div class="card"><div class="qh"><span class="n num">№ '+n+'</span><span class="pass" style="font-size:13px">✓ правильно</span></div><p class="qt" style="margin:0;font-weight:500;font-size:15px">'+esc(q.q)+'</p></div>';
    return '<div class="card">'+qHead(q,true)+optsHtml(q,a,true)+(a==null?'<p class="why badw"><b>Без відповіді.</b> '+esc(q.w)+'</p>':whyHtml(q,ok))+'</div>';
  }).join('');
  var b='';
  if(exam)b+='<button type="button" class="btn main" data-go="exam">Новий білет</button>';
  else if(wrong.length)b+='<button type="button" class="btn main" data-go="redo">Ще раз ці помилки</button>';
  b+='<button type="button" class="btn" data-go="home">До меню</button>';
  $('r-btns').innerHTML=b;
  S.wrongList=wrong;
  show('res');
}
$('r-btns').addEventListener('click',function(e){
  var b=e.target.closest('[data-go]');if(!b)return;
  var g=b.dataset.go;
  if(g==='exam')startExam();
  else if(g==='redo')start('mist',shuffle(S.wrongList),'Робота над помилками');
  else{renderHome();show('home')}
});

function startExam(){start('exam',shuffle(Q.map(function(q){return q.n})).slice(0,15),'Іспит')}
$('go-exam').addEventListener('click',startExam);
$('go-all').addEventListener('click',function(){start('all',shuffle(Q.map(function(q){return q.n})),'Усі питання')});
$('go-mist').addEventListener('click',function(){var m=mistakes();if(m.length)start('mist',shuffle(m),'Робота над помилками')});
$('topics').addEventListener('click',function(e){
  var b=e.target.closest('.topic');if(!b)return;
  var ti=+b.dataset.t;
  start('topic',Q.filter(function(q){return q.t===ti}).map(function(q){return q.n}),T[ti].name);
});
$('reset').addEventListener('click',function(){$('reset-ask').hidden=false});
$('reset-no').addEventListener('click',function(){$('reset-ask').hidden=true});
$('reset-yes').addEventListener('click',function(){prog={};hist=[];save('adr-prog',prog);save('adr-exams',hist);$('reset-ask').hidden=true;renderHome()});
renderHome();
})();
"""

N = str(len(qs))
body = BODY.replace("__N__", N)
head_links = ""
scripts = f"<script>window.__ADR={DATA};</script>\n<script>{JS}</script>\n"

# artifact fragment (the publish skeleton adds doctype/head/body)
frag = ('<title>Тренажер ДОПНВ</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
        + head_links + f"<style>{CSS}</style>\n" + body + scripts)
if len(sys.argv) > 1:
    pathlib.Path(sys.argv[1]).write_text(frag, encoding="utf-8")

# standalone site
SITE.mkdir(parents=True, exist_ok=True)
full = ('<!doctype html>\n<html lang="uk">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="theme-color" content="#e8740c">\n<title>Тренажер ДОПНВ</title>\n'
        + head_links + f"<style>{CSS}</style>\n</head>\n<body>\n" + body + scripts + "</body>\n</html>\n")
SW_REG = ("<script>if('serviceWorker' in navigator&&location.protocol==='https:'){window.addEventListener('load',function(){"
          "navigator.serviceWorker.register('sw.js').catch(function(){})})}</script>\n")
full = full.replace("</body>", SW_REG + "</body>")
(SITE / "index.html").write_text(full, encoding="utf-8")
imgs = sorted("img/" + f.name for f in (SITE / "img").iterdir())
ver = hashlib.sha1((full + "".join(imgs)).encode("utf-8")).hexdigest()[:10]
SW = r"""// Offline cache: the page itself is network-first (so updates show at once), pictures are cache-first.
var C = 'adr-__VER__';
var FILES = ['./', 'index.html'].concat(__IMGS__);
self.addEventListener('install', function (e) {
  self.skipWaiting();
  e.waitUntil(caches.open(C).then(function (c) { return c.addAll(FILES); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== C; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  if (r.mode === 'navigate' || /\/$|index\.html$/.test(new URL(r.url).pathname)) {
    e.respondWith(fetch(r).then(function (res) {
      var copy = res.clone(); caches.open(C).then(function (c) { c.put(r, copy); }); return res;
    }).catch(function () { return caches.match(r).then(function (m) { return m || caches.match('index.html'); }); }));
    return;
  }
  e.respondWith(caches.match(r).then(function (m) { return m || fetch(r); }));
});
""".replace("__VER__", ver).replace("__IMGS__", json.dumps(imgs))
(SITE / "sw.js").write_text(SW, encoding="utf-8")
print(SITE / "index.html", len(full), "imgs", len(list((SITE / "img").iterdir())))
