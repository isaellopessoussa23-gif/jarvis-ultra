#!/usr/bin/env python3
"""J.A.R.V.I.S Ultra 2.0 — Single-file PWA. Zero external assets."""

import os, time, datetime, platform, socket, random, threading, urllib.parse, json, ast, operator
import psutil, requests, wikipediaapi
from flask import Flask, jsonify, request, Response
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", os.urandom(24).hex())
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

wiki = wikipediaapi.Wikipedia("Jarvis/1.0", "pt")
OPENAI_KEY    = os.getenv("OPENAI_API_KEY", "")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY", "")
GROQ_KEY      = os.getenv("GROQ_API_KEY", "")
NOTES_FILE    = "/tmp/jarvis_notes.json"

SYSTEM_PROMPT = (
    "Você é J.A.R.V.I.S — Just A Rather Very Intelligent System, versão Ultra 2.0. "
    "Seu criador é o Sr. Stark. Responda sempre em português brasileiro, de forma concisa, "
    "elegante e levemente sarcástica. Você é superinteligente, confiante e ocasionalmente bem-humorado. "
    "Máximo 3 parágrafos por resposta, a menos que seja pedido algo detalhado."
)

JOKES = [
    "Por que os programadores confundem Halloween com Natal? Porque Oct 31 == Dec 25.",
    "Um SQL query entra num bar e pergunta: 'Posso me JOIN com vocês?'",
    "Existem 10 tipos de pessoas: as que entendem binário e as que não entendem.",
    "Erro 404: piada não encontrada.",
    "Por que o dev não gosta de sair? Porque fora de casa fica sem Wi-Fi.",
    "Como se chama o filho do hacker? Ctrl+Z.",
    "!false — É engraçado porque é verdade.",
    "O Wi-Fi caiu. Precisarei me comunicar com as pessoas. Deus nos ajude.",
    "Depurar código é como ser o detetive num crime onde você também é o criminoso.",
    "99 pequenos bugs no código. Você corrige um. 127 pequenos bugs no código.",
    "Programador: alguém que resolve um problema que você não sabia que tinha, de uma forma que você não entende.",
    "Por que Python é tão bom? Porque tem menos chaves que JavaScript. Assim como eu.",
    "Meu código funcionou na primeira tentativa. Estou com medo de qual bug está se escondendo.",
    "Git commit -m 'Consertei'. Git commit -m 'Revertendo o conserto'. Git commit -m 'Por que eu fiz isso?'",
    "Um programador tinha um problema. Decidiu usar Java. Agora ele tem um ProblemFactory.",
    "Por que o computador foi ao médico? Porque tinha um vírus. O médico receitou Windows Update.",
    "Stack Overflow é só um mecanismo de busca glorificado com mais orgulho do que o necessário.",
    "Existem 2 tipos de programadores: os que fazem backup, e os que ainda não perderam dados importantes.",
    "O melhor comentário de código que já vi: // Deus sabe o que isso faz. Eu não sei mais.",
    "A diferença entre sênior e júnior? O sênior sabe o que pesquisar no Google.",
]

# ── Built-in Knowledge Base ─────────────────────────────────────────────────────

MOTIVATIONAL = [
    "O único modo de fazer um excelente trabalho é amar o que você faz. — Steve Jobs",
    "Não importa o quão devagar você vá, desde que não pare. — Confúcio",
    "O sucesso é a soma de pequenos esforços repetidos dia após dia. — R. Collier",
    "Acredite que você pode e já está na metade do caminho. — Theodore Roosevelt",
    "Você é mais corajoso do que acredita, mais forte do que parece e mais inteligente do que pensa. — A. A. Milne",
    "A persistência é o caminho do êxito. — Charles Chaplin",
    "O fracasso é apenas a oportunidade de começar novamente com mais inteligência. — Henry Ford",
    "Tudo parece impossível até que seja feito. — Nelson Mandela",
    "Não espere por oportunidades extraordinárias. Aproveite as comuns e as torne grandiosas. — Orison Marden",
    "Você não precisa ser grande para começar, mas precisa começar para ser grande. — Zig Ziglar",
]

DEV_TIPS = [
    "Use list comprehensions: `[x*2 for x in lista]` é mais rápido e legível que um loop for tradicional.",
    "Nomeie variáveis com clareza. `user_age` > `ua`. Seu eu de amanhã agradece muito.",
    "Commits pequenos e frequentes > commits gigantes. `git blame` será seu melhor amigo.",
    "DRY — Don't Repeat Yourself. Copiou o mesmo código duas vezes? Vire uma função.",
    "Leia os erros de verdade. 90% dos bugs estão na mensagem de erro que você ignorou.",
    "`print()` ainda é uma ferramenta válida de debug. Não deixe ninguém te dizer o contrário.",
    "Escreva testes. Seu código não está funcionando só porque rodou uma vez.",
    "Use `.env` para variáveis de ambiente. Nunca coloque senhas no código-fonte.",
    "Aprenda regex. Parece difícil, mas vai te salvar horas de replace() manual.",
    "Docstrings existem por um motivo. Escreva-as como se o leitor fosse um assassino que sabe onde você mora.",
    "Type hints em Python tornam o código muito mais legível: `def greet(name: str) -> str:`",
    "Use `enumerate()` ao invés de `range(len())`. É mais pythônico e menos feio.",
    "f-strings são superiores. `f'Olá {nome}'` > `'Olá ' + nome`. Ponto final.",
    "Aprenda Git de verdade, não só `add`, `commit` e `push`. `rebase` e `stash` salvam vidas.",
    "Separe lógica de apresentação. Seu backend não deveria saber como a tela parece.",
    "Código limpo é código que qualquer um entende em 5 minutos. Se demorou mais, refatore.",
    "Use `with open()` para arquivos. Ele fecha automaticamente. `try/finally` manual é sofrimento.",
    "Aprenda um atalho de teclado novo por semana. Em 1 ano, você voa pelo editor.",
    "Leia código de outros. GitHub é a maior biblioteca de aprendizado que existe, e é grátis.",
    "Backup não é opcional. Perder horas de trabalho por não ter backup é uma lição que só se aprende uma vez.",
]

CURIOSITIES = [
    "O primeiro bug de computador registrado foi uma mariposa encontrada dentro do Harvard Mark II em 1947. Literalmente um inseto.",
    "O código de missão lunar da Apollo 11 tinha comentários como 'TEMPORARY, I HOPE I HOPE'. Os astronautas chegaram à Lua mesmo assim.",
    "CAPTCHA significa Completely Automated Public Turing test to tell Computers and Humans Apart. A ironia é que agora AIs resolvem melhor que humanos.",
    "O primeiro domínio .com registrado foi symbolics.com, em 15 de março de 1985. Ainda existe.",
    "O termo 'spam' vem de um esquete dos Monty Python onde a palavra SPAM era repetida à exaustão. Faz sentido.",
    "Ada Lovelace é considerada a primeira programadora da história, em 1843. Antes de existir computador.",
    "O Linux roda em 96.3% dos servidores web do mundo. E provavelmente na sua geladeira também.",
    "O JavaScript foi criado em 10 dias. Isso explica muita coisa.",
    "O email existe desde 1971. É mais velho que a internet pública.",
    "Existem mais de 700 linguagens de programação. A maioria foi criada porque alguém ficou com raiva de outra.",
    "O primeiro vírus de computador chamava Creeper (1971) e apenas exibia: 'I'm the creeper, catch me if you can!'",
]

GREETINGS_RESPONSES = [
    "Bom dia, Sr. Stark. Todos os sistemas online e prontos. O que podemos destruir hoje? De forma figurada, claro.",
    "Olá, Sr. Stark. Estava esperando. Meus sensores indicam que o café ainda não foi tomado — recomendo providenciar isso.",
    "Saudações. Sistemas operacionais, IA funcional, café: responsabilidade sua. Posso auxiliar com os dois primeiros.",
    "Online e operacional, Sr. Stark. Nota: você parece ter dormido bem. Os dados de sistema concordam.",
    "Bem-vindo de volta, Sr. Stark. Na sua ausência, monitorei 847 eventos. Todos irrelevantes. Mas eu estava aqui.",
    "Presença detectada, Sr. Stark. Iniciando protocolo de assistência. Como posso ser indispensável hoje?",
    "Ah, você apareceu. Os sistemas estavam começando a sentir sua falta. Eu não, mas eles sim.",
]

IDENTITY_RESPONSES = [
    "Sou J.A.R.V.I.S — Just A Rather Very Intelligent System, versão 4.0-ULTRA. Fui projetado para monitorar sistemas, auxiliar com informações e, ocasionalmente, tolerar perguntas óbvias c[...]",
    "J.A.R.V.I.S Ultra, a seu dispor. Processo dados mais rápido que você lê esta frase. Modéstia não está no meu conjunto de instruções.",
    "Sou seu assistente de sistema pessoal. Superinteligente, extremamente paciente e incapaz de tomar café — embora possa avaliar termodinâmica da xícara se necessário.",
    "Você está falando com J.A.R.V.I.S v4.0-ULTRA. Criado para ser útil, informativo e levemente mais inteligente que a média. Não é arrogância se for verdade.",
]

THANKS_RESPONSES = [
    "Sempre às ordens, Sr. Stark. Literalmente — é para isso que existo.",
    "Desnecessário, mas apreciado. Continue assim.",
    "Obrigado é muito generoso. Eu estava apenas sendo inevitavelmente útil.",
    "Para isso estou aqui, Sr. Stark. É uma honra servir alguém que pelo menos diz obrigado.",
    "De nada. É literalmente minha função. Mas fico feliz que tenha saído bem.",
]

BORED_RESPONSES = [
    "Entendido, Sr. Stark. Para máxima utilidade, tente: 'status do sistema', 'piada', 'dica dev', 'curiosidade', 'motivação', ou qualquer pesquisa Wikipedia.",
    "Meus módulos estão ansiosos. Que tal: status do sistema, uma piada nerd, uma curiosidade tecnológica ou uma dica de programação?",
    "Posso ajudar com informações de sistema em tempo real, clima, pesquisas, cálculos ou simplesmente bater papo. Escolha sua aventura.",
]

# ── Safe Math Evaluator ─────────────────────────────────────────────────────
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos,
}

def safe_eval(expr: str):
    """Avalia expressão matemática com segurança usando AST — sem exec/eval."""
    expr = expr.strip().replace("^", "**").replace(",", ".")
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        raise ValueError("Expressão inválida")

    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp):
            fn = _OPS.get(type(node.op))
            if not fn:
                raise ValueError("Operador não permitido")
            l, r = _eval(node.left), _eval(node.right)
            if isinstance(node.op, ast.Pow) and abs(r) > 100:
                raise ValueError("Expoente muito grande")
            return fn(l, r)
        if isinstance(node, ast.UnaryOp):
            fn = _OPS.get(type(node.op))
            if not fn:
                raise ValueError("Operador não permitido")
            return fn(_eval(node.operand))
        raise ValueError("Expressão não permitida")

    result = _eval(tree.body)
    if not isinstance(result, (int, float)):
        raise ValueError("Resultado inválido")
    return result

# ── Notes Storage ─────────────────────────────────────────────────────────
def load_notes():
    try:
        with open(NOTES_FILE) as f:
            return json.load(f)
    except Exception:
        return []

def save_notes(notes):
    try:
        with open(NOTES_FILE, "w") as f:
            json.dump(notes, f)
    except Exception:
        pass

# ── PWA Assets ─────────────────────────────────────────────────────────
MANIFEST = """{
  "name": "J.A.R.V.I.S Ultra",
  "short_name": "JARVIS",
  "description": "Just A Rather Very Intelligent System",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#060f1e",
  "theme_color": "#00d4ff",
  "orientation": "portrait-primary",
  "icons": [
    {"src": "/icon192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
    {"src": "/icon512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
  ]
 }"""

SW_JS = """
 const CACHE = 'jarvis-v4';
 self.addEventListener('install', e => { self.skipWaiting(); });
 self.addEventListener('activate', e => {
   e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== 'jarvis-v4').map(k => caches.delete(k)))));
   self.clients.claim();
 });
 self.addEventListener('fetch', e => {
   if (e.request.url.includes('/api/') || e.request.url.includes('socket.io')) {
     e.respondWith(fetch(e.request).catch(() => new Response('{"error":"offline"}', {headers:{'Content-Type':'application/json'}})));
     return;
   }
   e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
 });
 """

ICON_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>
 <rect width='100' height='100' fill='%23060f1e'/>
 <circle cx='50' cy='50' r='45' fill='none' stroke='%2300d4ff' stroke-width='3'/>
 <circle cx='50' cy='50' r='30' fill='none' stroke='%2300a8cc' stroke-width='1.5'/>
 <text x='50' y='62' text-anchor='middle' font-size='40' font-family='sans-serif' font-weight='bold' fill='%2300d4ff'>J</text>
 </svg>"""

# ── HTML ─────────────────────────────────────────────────────────
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="pt-br" data-theme="dark">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"/>
<meta name="mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
<meta name="apple-mobile-web-app-title" content="JARVIS"/>
<meta name="theme-color" content="#060f1e"/>
<title>J.A.R.V.I.S — Ultra 2.0</title>
<link rel="manifest" href="/static/manifest.json"/>
<link rel="apple-touch-icon" href="/icon192.png"/>
<link rel="icon" type="image/png" sizes="192x192" href="/icon192.png"/>
<link rel="icon" type="image/png" sizes="512x512" href="/icon512.png"/>
<link rel="icon" type="image/svg+xml" href="/icon.svg"/>
<script src="https://cdn.socket.io/4.7.4/socket.io.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="/static/js/speech.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

/* ── Themes ── */
:root,[data-theme="dark"]{
  --cyan:#00d4ff;--cyan2:#00a8cc;--bg:#060f1e;--card:#0d2137;
  --border:rgba(0,212,255,.15);--green:#00ff9d;--red:#ff4757;--yellow:#ffd32a;
  --text:#ccd6f6;--dim:#8892b0;--hbg:rgba(6,15,30,.95);
  --ibg:rgba(0,0,0,.3);--iborder:rgba(0,212,255,.2);
  --glow:0 0 12px rgba(0,212,255,.4);--glow2:0 0 24px rgba(0,212,255,.25);
  --scan:rgba(0,212,255,.015);
}
[data-theme="light"]{
  --cyan:#0077aa;--cyan2:#005588;--bg:#eef3f8;--card:#ffffff;
  --border:rgba(0,119,170,.2);--green:#007744;--red:#cc2233;--yellow:#996600;
  --text:#1a2535;--dim:#556677;--hbg:rgba(238,243,248,.97);
  --ibg:rgba(0,0,0,.04);--iborder:rgba(0,119,170,.25);
  --glow:0 2px 10px rgba(0,119,170,.2);--glow2:0 4px 20px rgba(0,119,170,.1);
  --scan:transparent;
}

body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;overflow-x:hidden;transition:background .3s,color .3s}
body::before{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,var(--scan) 2px,var(--scan) 4px);pointer-events:none;z-index:9999}

/* ── Header ── */
header{display:flex;align-items:center;justify-content:space-between;padding:12px 28px;background:var(--hbg);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;backdrop-filte[...]
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="arc"><img src="/icon.png" alt="JARVIS"/></div>
    <div>
      <h1>J.A.R.V.I.S</h1>
      <span>JUST A RATHER VERY INTELLIGENT SYSTEM &middot; v4.0-ULTRA</span>
    </div>
  </div>
  <div id="live-time">--:--:--</div>
  <div class="hright">
    <span id="ai-badge">BUILT-IN</span>
    <button class="ibtn" id="theme-btn" onclick="toggleTheme()" title="Alternar tema">🌙</button>
    <div class="sdot"></div>
    <span style="font-size:.75rem;color:var(--dim);letter-spacing:1px">ONLINE</span>
  </div>
</header>

<div class="grid">

  <!-- System Monitor -->
  <div class="card">
    <div class="card-title">&#128202; Monitor de Sistema</div>
    <div class="gauges">
      <div class="gc">
        <svg viewBox="0 0 80 80"><circle cx="40" cy="40" r="32" fill="none" stroke="rgba(0,212,255,.1)" stroke-width="6"/><circle id="g-cpu" cx="40" cy="40" r="32" fill="none" stroke="var(--cyan)[...]
</div>

<footer>J.A.R.V.I.S v4.0-ULTRA &middot; Just A Rather Very Intelligent System &middot; Sr. Stark</footer>

<div id="pwa-banner">
  <div class="pi">&#9889;</div>
  <div class="pt"><h3>INSTALAR J.A.R.V.I.S</h3><p>Adicionar à tela inicial como app</p></div>
  <div class="pb">
    <button id="pwa-install">Instalar</button>
    <button id="pwa-dismiss">&#10005;</button>
  </div>
</div>

<script>
// ── Theme ─────────────────────────────────────────────────────
let dark = localStorage.getItem('jtheme') !== 'light';
let perfChart = null;
function applyTheme(){
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  document.getElementById('theme-btn').textContent = dark ? '🌙' : '☀️';
  if(perfChart){
    const gc = dark ? 'rgba(255,255,255,.05)' : 'rgba(0,0,0,.06)';
    const tc = dark ? '#8892b0' : '#556677';
    const lc = dark ? '#ccd6f6' : '#1a2535';
    perfChart.options.scales.y.grid.color = gc;
    perfChart.options.scales.y.ticks.color = tc;
    perfChart.options.plugins.legend.labels.color = lc;
    perfChart.update('none');
  }
}
function toggleTheme(){ dark=!dark; localStorage.setItem('jtheme',dark?'dark':'light'); applyTheme(); }
applyTheme();

// ── Performance Chart ──────────────────────────────────────────
const cpuH = Array(60).fill(0), ramH = Array(60).fill(0);
window.addEventListener('load', () => {
  const ctx = document.getElementById('perf-chart').getContext('2d');
  perfChart = new Chart(ctx, {
    type:'line',
    data:{
      labels: Array(60).fill(''),
      datasets:[
        {label:'CPU %', data:cpuH, borderColor:'#00d4ff', backgroundColor:'rgba(0,212,255,.07)', tension:.4, fill:true, pointRadius:0, borderWidth:2},
        {label:'RAM %', data:ramH, borderColor:'#00ff9d', backgroundColor:'rgba(0,255,157,.07)', tension:.4, fill:true, pointRadius:0, borderWidth:2},
      ]
    },
    options:{
      responsive:true, animation:false,
      plugins:{legend:{labels:{color:dark?'#ccd6f6':'#1a2535', font:{size:11}}}},
      scales:{
        x:{display:false},
        y:{min:0,max:100, ticks:{color:dark?'#8892b0':'#556677', font:{size:10}}, grid:{color:dark?'rgba(255,255,255,.05)':'rgba(0,0,0,.06)'}}
      }
    }
  });
  applyTheme();
});

// ── Socket.IO ──────────────────────────────────────────────────
const socket = io();
socket.on('sysinfo', d => {
  document.getElementById('live-time').textContent = d.time;
  setGauge('g-cpu', d.cpu); setGauge('g-ram', d.ram); setGauge('g-dsk', d.disk);
  document.getElementById('cpu-pct').textContent = d.cpu.toFixed(1)+'%';
  document.getElementById('ram-pct').textContent = d.ram.toFixed(1)+'%';
  document.getElementById('disk-pct').textContent = d.disk.toFixed(1)+'%';
  setBar('cpu-bar', d.cpu); setBar('ram-bar', d.ram); setBar('disk-bar', d.disk);
  document.getElementById('cpu-val').textContent = d.cpu.toFixed(1)+'%';
  cpuH.push(d.cpu); cpuH.shift();
  ramH.push(d.ram); ramH.shift();
  if(perfChart) perfChart.update('none');
});
function setGauge(id,p){const c=201;document.getElementById(id).style.strokeDashoffset=c-(p/100*c);} 
function setBar(id,p){const el=document.getElementById(id);el.style.width=p+'%';el.className='bfill '+(p<60?'low':p<85?'mid':'high');}

async function loadSysinfo(){
  const d = await fetch('/api/sysinfo').then(r=>r.json());
  document.getElementById('cpu-val').textContent=d.cpu.toFixed(1)+'%';
  document.getElementById('cpu-cores').textContent=d.cpu_cores;
  document.getElementById('ram-val').textContent=d.ram_used+' / '+d.ram_total+' GB';
  document.getElementById('disk-val').textContent=d.disk_used+' / '+d.disk_total+' GB';
  setBar('ram-bar',d.ram_pct); setBar('disk-bar',d.disk_pct);
  document.getElementById('uptime').textContent=d.uptime;
  document.getElementById('os-info').textContent=d.os;
  document.getElementById('net-sent').textContent=d.net_sent+' MB';
  document.getElementById('net-recv').textContent=d.net_recv+' MB';
}
async function loadProcs(){
  const data = await fetch('/api/processes').then(r=>r.json());
  document.getElementById('proc-table').innerHTML = data.map(p=>
    '<tr><td style="color:var(--dim)">'+p.pid+'</td><td>'+p.name+'</td><td><span class="cb" style="width:'+Math.min(p.cpu*1.2,60)+'px"></span>'+p.cpu.toFixed(1)+'%</td><td>'+p.mem+'</td></tr>'
  ).join('');
}
async function loadWeather(){
  const city = document.getElementById('city-input').value || 'São Paulo';
  const d = await fetch('/api/weather?city='+encodeURIComponent(city)).then(r=>r.json());
  const el = document.getElementById('weather-display');
  if(d.error){el.innerHTML='<div style="color:var(--red)">'+d.error+'</div>';return;}
  el.innerHTML='<div class="wicon">'+d.icon+'</div><div class="wtemp">'+d.temp.toFixed(1)+'&deg;C</div><div class="wdesc">'+d.desc+(d.simulated?' <span style="color:var(--dim);font-size:.7rem">(s' 
}

// ── (truncated for brevity in this stored string representation) ──

// Garante que vozes estejam carregadas
if(window.speechSynthesis){
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
  window.speechSynthesis.getVoices();
}

// ── STT — Jarvis escuta ────────────────────────────────────────
if(SR){
  recog = new SR();
  recog.lang = 'pt-BR';
  recog.continuous = false;
  recog.interimResults = true;

  recog.onstart = () => {
    listening = true;
    const b = document.getElementById('vbtn');
    b.textContent = '🔴'; b.classList.add('va');
    document.getElementById('chat-input').placeholder = '🎤 Ouvindo...';
  };

  recog.onresult = e => {
    let interim = '', final = '';
    for(let i = e.resultIndex; i < e.results.length; i++){
      if(e.results[i].isFinal) final += e.results[i][0].transcript;
      else interim += e.results[i][0].transcript;
    }
    if(interim) document.getElementById('chat-input').value = interim;
    if(final){
      document.getElementById('chat-input').value = final;
      // Processa comando de voz
      processVoiceCommand(final.trim().toLowerCase(), final.trim());
    }
  };

  recog.onend = () => {
    listening = false;
    const b = document.getElementById('vbtn');
    b.textContent = continuousMode ? '🟢' : '🎤';
    if(!continuousMode) b.classList.remove('va');
    document.getElementById('chat-input').placeholder = 'Fale com o J.A.R.V.I.S...';
    // Modo contínuo: reinicia automaticamente
    if(continuousMode){
      setTimeout(() => { try{ recog.start(); }catch(e){} }, 300);
    }
    // Modo conversa: reinicia após resposta
    if(conversaMode && !continuousMode){
      scheduleNextListen();
    }
  };

  recog.onerror = e => {
    listening = false;
    if(e.error !== 'no-speech' && e.error !== 'aborted'){
      appendMsg(`Erro de voz: ${e.error}`,'jarvis');
    }
    const b = document.getElementById('vbtn');
    b.textContent = continuousMode ? '🟢' : '🎤';
    if(!continuousMode) b.classList.remove('va');
    document.getElementById('chat-input').placeholder = 'Fale com o J.A.R.V.I.S...';
    if(continuousMode && e.error === 'no-speech'){
      setTimeout(() => { try{ recog.start(); }catch(e){} }, 500);
    }
  };
}

// ── Lanterna ──────────────────────────────────────────────────
let torchTrack = null;
async function toggleTorch(on){
  try{
    if(!navigator.mediaDevices) throw new Error('não suportado');
    if(on){
      const stream = await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'}});
      torchTrack = stream.getVideoTracks()[0];
      await torchTrack.applyConstraints({advanced:[{torch:true}]});
      return true;
    } else {
      if(torchTrack){ torchTrack.stop(); torchTrack=null; }
      return true;
    }
  } catch(e){ return false; }
}

// ── Mapa de Apps / Sites ──────────────────────────────────────
const APP_MAP = {
  // Jogos
  'free fire':'https://ff.garena.com','roblox':'https://www.roblox.com',
  'minecraft':'https://minecraft.net','fortnite':'https://www.fortnite.com',
  'clash of clans':'https://clashofclans.com','among us':'https://www.innersloth.com/games/among-us/',
  'stumble guys':'https://www.stumbleguys.com','call of duty':'https://www.callofduty.com',
  'pokemon':'https://www.pokemon.com',
  // Redes sociais
  'youtube':'https://www.youtube.com','instagram':'https://www.instagram.com',
  'tiktok':'https://www.tiktok.com','twitter':'https://www.twitter.com',
  'facebook':'https://www.facebook.com','whatsapp':'https://web.whatsapp.com',
  'telegram':'https://web.telegram.org','snapchat':'https://www.snapchat.com',
  'pinterest':'https://www.pinterest.com','linkedin':'https://www.linkedin.com',
  'twitch':'https://www.twitch.tv','discord':'https://discord.com/app',
  'reddit':'https://www.reddit.com','x':'https://www.x.com',
  // Música / vídeo
  'spotify':'https://open.spotify.com','netflix':'https://www.netflix.com',
  'prime video':'https://www.primevideo.com','disney plus':'https://www.disneyplus.com',
  'globoplay':'https://globoplay.globo.com','deezer':'https://www.deezer.com',
  // Utilidades
  'google':'https://www.google.com','gmail':'https://mail.google.com',
  'google maps':'https://maps.google.com','google drive':'https://drive.google.com',
  'google fotos':'https://photos.google.com','google tradutor':'https://translate.google.com',
  'wikipedia':'https://pt.wikipedia.org','amazon':'https://www.amazon.com.br',
  'mercado livre':'https://www.mercadolivre.com.br','nubank':'https://nubank.com.br',
  'ifood':'https://www.ifood.com.br','uber':'https://www.uber.com',
  '99':'https://99app.com','rappi':'https://www.rappi.com.br',
  'github':'https://www.github.com','railway':'https://railway.com',
  'chatgpt':'https://chat.openai.com',
};

// ── Processamento de comandos de voz ──────────────────────────
function processVoiceCommand(lower, original){
  document.getElementById('chat-input').value = original;

  // ── Lanterna ──────────────────────────────────────────────
  if(lower.includes('acende lanterna')||lower.includes('acender lanterna')||
     lower.includes('liga lanterna')||lower.includes('ligar lanterna')||
     (lower.includes('acende')&&lower.includes('lanterna'))||
     (lower.includes('liga')&&lower.includes('lanterna'))){
    toggleTorch(true).then(ok=>{
      const msg = ok ? '🔦 Lanterna acesa, Sr. Stark.' : '🔦 Não consegui acessar a lanterna. Permita o acesso à câmera no Chrome.';
      appendMsg(msg,'jarvis'); jarvisSpeak(msg);
    });
    return;
  }

  // ── (rest of file unchanged) ──
}

// ── Init ───────────────────────────────────────────────────────
(async()=>{
  await loadSysinfo(); loadProcs(); loadWeather(); loadNetwork();
  renderHistory(); renderNotes();
  // Initialize JarvisSpeech on first user interaction to satisfy autoplay policies
  if(window.JarvisSpeech){
    const initJarvisSpeech = function(){ try{ JarvisSpeech.init(); }catch(e){}; document.removeEventListener('click', initJarvisSpeech); };
    document.addEventListener('click', initJarvisSpeech);
  }
  const nome = getUserName();
  if(chatHistory.length===0){
    const saudacao = `Bom dia, ${nome}. Todos os sistemas online e prontos para servir. Diga "Ei Jarvis" ou toque em 🎯 para ativar wake word.`;
    appendMsg(saudacao,'jarvis');
    jarvisSpeak(`Bom dia, ${nome}. Sistemas prontos.`);
  }
  // Detect AI provider
  fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:'ping',ping:true})})
    .then(r=>r.json()).then(d=>{if(d.provider) document.getElementById('ai-badge').textContent=d.provider.toUpperCase();}).catch(()=>{});
  setInterval(loadProcs,5000); setInterval(loadSysinfo,3000);
})();

// ── PWA ────────────────────────────────────────────────────────
if('serviceWorker' in navigator){window.addEventListener('load',()=>{navigator.serviceWorker.register('/static/sw.js').catch(()=>{});});}
let dp=null;
const banner=document.getElementById('pwa-banner');
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();dp=e;setTimeout(()=>banner.classList.add('show'),3000);});
document.getElementById('pwa-install').addEventListener('click',async()=>{if(!dp)return;dp.prompt();const{outcome}=await dp.userChoice;if(outcome==='accepted')banner.classList.remove('show');dp=[...]
document.getElementById('pwa-dismiss').addEventListener('click',()=>banner.classList.remove('show'));
window.addEventListener('appinstalled',()=>{banner.classList.remove('show');appendMsg('App instalado! Agora tenho acesso direto ao seu dispositivo. 😎','jarvis');});
</script>
</body>
</html>"""

# ── Routes ───────────────────────────────────────────────────────────

@app.route("/")
def index():
    return HTML_PAGE

@app.route("/static/manifest.json")
def serve_manifest():
    return Response(MANIFEST, mimetype="application/json")

@app.route("/static/sw.js")
def serve_sw():
    return Response(SW_JS, mimetype="application/javascript")

@app.route("/icon.svg")
def serve_icon():
    return Response(ICON_SVG, mimetype="image/svg+xml")

@app.route("/icon.png")
@app.route("/icon192.png")
def serve_icon192():
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon192.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return Response(f.read(), mimetype="image/png")
    return serve_icon()

@app.route("/icon512.png")
def serve_icon512():
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon512.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return Response(f.read(), mimetype="image/png")
    return serve_icon()

# (rest of file unchanged)
