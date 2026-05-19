#!/usr/bin/env python3
"""J.A.R.V.I.S Ultra — Single-file PWA. Zero external assets."""

import os, time, datetime, platform, socket, random, threading, urllib.parse
import psutil, requests, wikipediaapi
from flask import Flask, jsonify, request, Response
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "jarvis-ultra-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

wiki = wikipediaapi.Wikipedia("Jarvis/1.0", "pt")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY", "")

JOKES = [
    "Por que os programadores confundem Halloween com Natal? Porque Oct 31 == Dec 25.",
    "Um SQL query entra num bar e pergunta: 'Posso me JOIN?'",
    "Existem 10 tipos de pessoas: as que entendem binario e as que nao entendem.",
    "Erro 404: piada nao encontrada.",
    "Por que o dev nao gosta de sair? Porque fora de casa fica sem Wi-Fi.",
    "Como se chama o filho do hacker? Ctrl+Z.",
    "!false - E engracado porque e verdade.",
    "O Wi-Fi caiu. Precisarei me comunicar com as pessoas. Deus nos ajude.",
]

# ── Inline manifest & sw ────────────────────────────────────

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
    {"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}
  ]
}"""

SW_JS = """
const CACHE = 'jarvis-v1';
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { self.clients.claim(); });
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

@app.route("/static/manifest.json")
def serve_manifest():
    return Response(MANIFEST, mimetype="application/json")

@app.route("/static/sw.js")
def serve_sw():
    return Response(SW_JS, mimetype="application/javascript")

@app.route("/icon.svg")
def serve_icon():
    return Response(ICON_SVG, mimetype="image/svg+xml")

# ── HTML ────────────────────────────────────────────────────

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"/>
<meta name="mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
<meta name="apple-mobile-web-app-title" content="JARVIS"/>
<meta name="theme-color" content="#060f1e"/>
<title>J.A.R.V.I.S — Ultra</title>
<link rel="manifest" href="/static/manifest.json"/>
<link rel="apple-touch-icon" href="/icon.svg"/>
<link rel="icon" type="image/svg+xml" href="/icon.svg"/>
<script src="https://cdn.socket.io/4.7.4/socket.io.min.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --cyan:#00d4ff;--cyan2:#00a8cc;--blue:#0a192f;--blue2:#0d2137;
  --dark:#060f1e;--green:#00ff9d;--red:#ff4757;--yellow:#ffd32a;
  --text:#ccd6f6;--dim:#8892b0;
  --glow:0 0 12px rgba(0,212,255,0.4);--glow2:0 0 24px rgba(0,212,255,0.25);
}
body{background:var(--dark);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,212,255,0.015) 2px,rgba(0,212,255,0.015) 4px);pointer-events:none;z-index:9999}
header{display:flex;align-items:center;justify-content:space-between;padding:12px 28px;background:linear-gradient(90deg,rgba(0,212,255,0.08),transparent);border-bottom:1px solid rgba(0,212,255,0.2);position:sticky;top:0;z-index:100;backdrop-filter:blur(10px)}
.logo{display:flex;align-items:center;gap:14px}
.logo .arc{width:40px;height:40px;border:2px solid var(--cyan);border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:var(--glow),inset 0 0 12px rgba(0,212,255,0.3);animation:pulse 2s ease-in-out infinite}
.logo .arc::after{content:'⚡';font-size:18px}
@keyframes pulse{0%,100%{box-shadow:var(--glow),inset 0 0 12px rgba(0,212,255,0.3)}50%{box-shadow:0 0 28px rgba(0,212,255,0.7),inset 0 0 20px rgba(0,212,255,0.5)}}
.logo h1{font-size:1.4rem;font-weight:700;color:var(--cyan);letter-spacing:3px}
.logo span{font-size:.7rem;color:var(--dim);letter-spacing:2px}
#live-time{font-size:1.6rem;font-weight:300;color:var(--cyan);font-variant-numeric:tabular-nums}
.status-dot{width:8px;height:8px;background:var(--green);border-radius:50%;box-shadow:0 0 8px var(--green);animation:blink 1.4s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;padding:20px 24px}
.card{background:var(--blue2);border:1px solid rgba(0,212,255,0.15);border-radius:12px;padding:20px;box-shadow:var(--glow2);transition:border-color .3s,box-shadow .3s}
.card:hover{border-color:rgba(0,212,255,0.4);box-shadow:0 0 32px rgba(0,212,255,0.2)}
.card-title{font-size:.7rem;letter-spacing:2px;text-transform:uppercase;color:var(--cyan);margin-bottom:16px;display:flex;align-items:center;gap:8px}
.card-title::before{content:'';flex:1;height:1px;background:rgba(0,212,255,0.2);order:1}
.metric{margin-bottom:14px}
.metric-header{display:flex;justify-content:space-between;font-size:.82rem;margin-bottom:5px}
.metric-label{color:var(--dim)}.metric-value{color:var(--cyan);font-weight:600;font-variant-numeric:tabular-nums}
.bar-track{background:rgba(255,255,255,0.05);border-radius:4px;height:8px;overflow:hidden}
.bar-fill{height:100%;border-radius:4px;transition:width .8s cubic-bezier(.25,.46,.45,.94),background .5s}
.bar-fill.low{background:linear-gradient(90deg,#00ff9d,#00cc7a);box-shadow:0 0 8px rgba(0,255,157,0.4)}
.bar-fill.mid{background:linear-gradient(90deg,#ffd32a,#ff9f43);box-shadow:0 0 8px rgba(255,211,42,0.4)}
.bar-fill.high{background:linear-gradient(90deg,#ff4757,#ff6b81);box-shadow:0 0 8px rgba(255,71,87,0.4)}
.big-gauges{display:flex;gap:16px;justify-content:space-around;margin-bottom:12px}
.gauge-circle{text-align:center}
.gauge-circle svg{width:80px;height:80px}
.gauge-pct{font-size:1.1rem;font-weight:700;color:var(--cyan)}
.gauge-label{font-size:.65rem;color:var(--dim);letter-spacing:1px}
.data-table{width:100%;border-collapse:collapse;font-size:.8rem}
.data-table th{color:var(--cyan);font-weight:500;padding:6px 8px;border-bottom:1px solid rgba(0,212,255,0.15);text-align:left}
.data-table td{padding:5px 8px;color:var(--text);border-bottom:1px solid rgba(255,255,255,0.03)}
.data-table tr:hover td{background:rgba(0,212,255,0.04)}
.cpu-bar{display:inline-block;height:4px;background:var(--cyan);border-radius:2px;vertical-align:middle;margin-right:4px}
.chat-card{grid-column:span 2}
@media(max-width:900px){.chat-card{grid-column:span 1}}
.chat-box{height:300px;overflow-y:auto;display:flex;flex-direction:column;gap:10px;padding:12px;background:rgba(0,0,0,.2);border-radius:8px;margin-bottom:12px}
.chat-box::-webkit-scrollbar{width:4px}
.chat-box::-webkit-scrollbar-thumb{background:rgba(0,212,255,0.3);border-radius:2px}
.msg{max-width:80%;padding:8px 14px;border-radius:10px;font-size:.85rem;line-height:1.5;word-break:break-word}
.msg.user{align-self:flex-end;background:rgba(0,212,255,0.15);border:1px solid rgba(0,212,255,0.25)}
.msg.jarvis{align-self:flex-start;background:rgba(0,30,60,.6);border:1px solid rgba(0,212,255,0.12)}
.msg.jarvis .sender{font-size:.7rem;color:var(--cyan);letter-spacing:1px;margin-bottom:3px}
.msg.thinking{opacity:.6;font-style:italic;animation:think .8s ease-in-out infinite alternate}
@keyframes think{from{opacity:.4}to{opacity:.8}}
.chat-input-row{display:flex;gap:8px}
#chat-input{flex:1;background:rgba(0,0,0,.3);border:1px solid rgba(0,212,255,.2);border-radius:8px;color:var(--text);padding:10px 14px;font-size:.9rem;outline:none;transition:border .2s}
#chat-input:focus{border-color:var(--cyan);box-shadow:0 0 10px rgba(0,212,255,.15)}
#chat-input::placeholder{color:var(--dim)}
.btn{background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.3);color:var(--cyan);border-radius:8px;padding:10px 18px;cursor:pointer;font-size:.85rem;letter-spacing:1px;transition:all .2s}
.btn:hover{background:rgba(0,212,255,.18);box-shadow:0 0 12px rgba(0,212,255,.25)}
.btn:active{transform:scale(.97)}
.quick-btns{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}
.quick-btn{background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.15);color:var(--dim);border-radius:20px;padding:4px 12px;font-size:.75rem;cursor:pointer;transition:all .2s;letter-spacing:.5px}
.quick-btn:hover{background:rgba(0,212,255,.12);color:var(--cyan);border-color:rgba(0,212,255,.3)}
.weather-display{text-align:center;padding:10px 0}
.weather-icon{font-size:3rem;line-height:1.2}
.weather-temp{font-size:2.5rem;font-weight:300;color:var(--cyan)}
.weather-desc{color:var(--dim);font-size:.85rem;margin-bottom:12px}
.weather-row{display:flex;justify-content:space-around;font-size:.8rem}
.weather-stat .label{color:var(--dim)}.weather-stat .val{color:var(--text);font-weight:600}
.city-row{display:flex;gap:8px;margin-bottom:12px}
#city-input{flex:1;background:rgba(0,0,0,.3);border:1px solid rgba(0,212,255,.2);border-radius:8px;color:var(--text);padding:8px 12px;font-size:.85rem;outline:none}
#city-input:focus{border-color:var(--cyan)}
.info-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.info-item{background:rgba(0,0,0,.2);border-radius:6px;padding:8px 12px}
.info-item .k{font-size:.68rem;color:var(--dim);letter-spacing:1px;text-transform:uppercase}
.info-item .v{font-size:.88rem;color:var(--text);font-weight:500;margin-top:2px;word-break:break-all}
.calc-display{background:rgba(0,0,0,.3);border-radius:8px;padding:10px 14px;margin-bottom:10px;font-size:1.1rem;min-height:44px;color:var(--cyan);font-family:monospace;letter-spacing:1px}
.calc-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}
.calc-btn{background:rgba(0,212,255,.06);border:1px solid rgba(0,212,255,.12);color:var(--text);border-radius:8px;padding:12px;font-size:.95rem;cursor:pointer;transition:all .15s;font-family:monospace}
.calc-btn:hover{background:rgba(0,212,255,.15);color:var(--cyan)}
.calc-btn.op{color:var(--cyan)}.calc-btn.eq{background:rgba(0,212,255,.2);color:var(--cyan);font-weight:700}
.calc-btn.clr{color:var(--red)}
.joke-text{background:rgba(0,0,0,.2);border-radius:8px;padding:16px;font-size:.9rem;line-height:1.6;color:var(--text);min-height:60px;text-align:center;font-style:italic}
footer{text-align:center;padding:16px;color:var(--dim);font-size:.72rem;letter-spacing:2px;border-top:1px solid rgba(0,212,255,.08);margin-top:8px}
#pwa-banner{display:none;position:fixed;bottom:0;left:0;right:0;z-index:9000;background:linear-gradient(135deg,#0a192f,#0d2137);border-top:1px solid rgba(0,212,255,.35);padding:14px 20px 20px;box-shadow:0 -8px 32px rgba(0,212,255,.15);backdrop-filter:blur(12px)}
#pwa-banner.show{display:flex;align-items:center;gap:14px}
#pwa-banner .pwa-icon{font-size:2.4rem;flex-shrink:0}
#pwa-banner .pwa-text{flex:1}
#pwa-banner .pwa-text h3{color:var(--cyan);font-size:.95rem;letter-spacing:1px}
#pwa-banner .pwa-text p{color:var(--dim);font-size:.78rem;margin-top:2px}
#pwa-banner .pwa-btns{display:flex;gap:8px;flex-shrink:0}
#pwa-install{background:var(--cyan);color:var(--dark);border:none;border-radius:8px;padding:10px 18px;font-weight:700;font-size:.85rem;cursor:pointer;letter-spacing:1px}
#pwa-dismiss{background:transparent;color:var(--dim);border:1px solid rgba(255,255,255,.15);border-radius:8px;padding:10px 14px;cursor:pointer;font-size:.8rem}
@media(max-width:600px){
  header{padding:10px 14px}.logo h1{font-size:1rem}.logo span{display:none}
  #live-time{font-size:1.2rem}.grid{padding:12px 10px;gap:12px}.card{padding:14px}
  .big-gauges{gap:8px}.big-gauges svg{width:64px;height:64px}.gauge-pct{font-size:.9rem}
  .chat-box{height:220px}.calc-btn{padding:14px 10px;font-size:1rem}
  .weather-temp{font-size:2rem}body{padding-bottom:80px}
}
@media(max-width:400px){.info-grid{grid-template-columns:1fr}}
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="arc"></div>
    <div>
      <h1>J.A.R.V.I.S</h1>
      <span>JUST A RATHER VERY INTELLIGENT SYSTEM &middot; v3.7.9-ULTRA</span>
    </div>
  </div>
  <div id="live-time">--:--:--</div>
  <div style="display:flex;align-items:center;gap:8px;">
    <div class="status-dot"></div>
    <span style="font-size:.75rem;color:var(--dim);letter-spacing:1px;">ONLINE</span>
  </div>
</header>

<div class="grid">

  <div class="card">
    <div class="card-title">&#128202; Monitor de Sistema</div>
    <div class="big-gauges">
      <div class="gauge-circle">
        <svg viewBox="0 0 80 80"><circle cx="40" cy="40" r="32" fill="none" stroke="rgba(0,212,255,.1)" stroke-width="6"/><circle id="gauge-cpu-arc" cx="40" cy="40" r="32" fill="none" stroke="var(--cyan)" stroke-width="6" stroke-linecap="round" stroke-dasharray="201" stroke-dashoffset="201" transform="rotate(-90 40 40)" style="transition:stroke-dashoffset .8s"/></svg>
        <div class="gauge-pct" id="cpu-pct">0%</div>
        <div class="gauge-label">CPU</div>
      </div>
      <div class="gauge-circle">
        <svg viewBox="0 0 80 80"><circle cx="40" cy="40" r="32" fill="none" stroke="rgba(0,212,255,.1)" stroke-width="6"/><circle id="gauge-ram-arc" cx="40" cy="40" r="32" fill="none" stroke="#00ff9d" stroke-width="6" stroke-linecap="round" stroke-dasharray="201" stroke-dashoffset="201" transform="rotate(-90 40 40)" style="transition:stroke-dashoffset .8s"/></svg>
        <div class="gauge-pct" id="ram-pct">0%</div>
        <div class="gauge-label">RAM</div>
      </div>
      <div class="gauge-circle">
        <svg viewBox="0 0 80 80"><circle cx="40" cy="40" r="32" fill="none" stroke="rgba(0,212,255,.1)" stroke-width="6"/><circle id="gauge-disk-arc" cx="40" cy="40" r="32" fill="none" stroke="#ffd32a" stroke-width="6" stroke-linecap="round" stroke-dasharray="201" stroke-dashoffset="201" transform="rotate(-90 40 40)" style="transition:stroke-dashoffset .8s"/></svg>
        <div class="gauge-pct" id="disk-pct">0%</div>
        <div class="gauge-label">DISCO</div>
      </div>
    </div>
    <div class="metric"><div class="metric-header"><span class="metric-label">&#128187; CPU (<span id="cpu-cores">?</span> cores)</span><span class="metric-value" id="cpu-val">&#8212;</span></div><div class="bar-track"><div class="bar-fill low" id="cpu-bar" style="width:0%"></div></div></div>
    <div class="metric"><div class="metric-header"><span class="metric-label">&#129504; RAM</span><span class="metric-value" id="ram-val">&#8212;</span></div><div class="bar-track"><div class="bar-fill low" id="ram-bar" style="width:0%"></div></div></div>
    <div class="metric"><div class="metric-header"><span class="metric-label">&#128190; Disco</span><span class="metric-value" id="disk-val">&#8212;</span></div><div class="bar-track"><div class="bar-fill low" id="disk-bar" style="width:0%"></div></div></div>
    <div class="info-grid" style="margin-top:12px">
      <div class="info-item"><div class="k">Uptime</div><div class="v" id="uptime">&#8212;</div></div>
      <div class="info-item"><div class="k">OS</div><div class="v" id="os-info">&#8212;</div></div>
      <div class="info-item"><div class="k">Rede up</div><div class="v" id="net-sent">&#8212;</div></div>
      <div class="info-item"><div class="k">Rede down</div><div class="v" id="net-recv">&#8212;</div></div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">&#128293; Top Processos</div>
    <div style="overflow-x:auto">
      <table class="data-table">
        <thead><tr><th>PID</th><th>Nome</th><th>CPU%</th><th>RAM MB</th></tr></thead>
        <tbody id="proc-table"></tbody>
      </table>
    </div>
    <button class="btn" style="margin-top:12px;width:100%" onclick="loadProcesses()">&#8635; Atualizar</button>
  </div>

  <div class="card">
    <div class="card-title">&#127750; Clima</div>
    <div class="city-row">
      <input id="city-input" type="text" placeholder="Digite a cidade..." value="São Paulo"/>
      <button class="btn" onclick="loadWeather()">&#128269;</button>
    </div>
    <div class="weather-display" id="weather-display">
      <div style="color:var(--dim);font-size:.85rem">Carregando...</div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">&#127760; Rede</div>
    <div class="info-grid" id="net-info">
      <div style="color:var(--dim);font-size:.85rem">Carregando...</div>
    </div>
  </div>

  <div class="card chat-card">
    <div class="card-title">&#129302; J.A.R.V.I.S Chat</div>
    <div class="quick-btns">
      <span class="quick-btn" onclick="quickCmd('status do sistema')">&#128202; Sistema</span>
      <span class="quick-btn" onclick="quickCmd('conta uma piada')">&#128514; Piada</span>
      <span class="quick-btn" onclick="quickCmd('quem e voce')">&#129302; Quem e?</span>
      <span class="quick-btn" onclick="quickCmd('qual a hora agora')">&#9201; Hora</span>
      <span class="quick-btn" onclick="quickCmd('dica de programacao')">&#128161; Dica dev</span>
      <span class="quick-btn" onclick="quickCmd('motivacao para hoje')">&#128640; Motivacao</span>
    </div>
    <div class="chat-box" id="chat-box"></div>
    <div class="chat-input-row">
      <input id="chat-input" type="text" placeholder="Fale com o J.A.R.V.I.S..." onkeydown="if(event.key==='Enter')sendChat()"/>
      <button class="btn" onclick="sendChat()">&#9654; Enviar</button>
    </div>
  </div>

  <div class="card">
    <div class="card-title">&#128218; Wikipedia</div>
    <div class="city-row">
      <input id="wiki-input" type="text" placeholder="Pesquisar..." style="flex:1;background:rgba(0,0,0,.3);border:1px solid rgba(0,212,255,.2);border-radius:8px;color:var(--text);padding:8px 12px;font-size:.85rem;outline:none;" onkeydown="if(event.key==='Enter')searchWiki()"/>
      <button class="btn" onclick="searchWiki()">&#128269;</button>
    </div>
    <div id="wiki-result" style="color:var(--dim);font-size:.82rem;line-height:1.6;margin-top:8px;max-height:200px;overflow-y:auto"></div>
  </div>

  <div class="card">
    <div class="card-title">&#129518; Calculadora Stark</div>
    <div class="calc-display" id="calc-display">0</div>
    <div class="calc-grid">
      <button class="calc-btn clr" onclick="calcClear()">C</button>
      <button class="calc-btn op" onclick="calcInput('(')">(</button>
      <button class="calc-btn op" onclick="calcInput(')')">)</button>
      <button class="calc-btn op" onclick="calcInput('^')">^</button>
      <button class="calc-btn" onclick="calcInput('7')">7</button>
      <button class="calc-btn" onclick="calcInput('8')">8</button>
      <button class="calc-btn" onclick="calcInput('9')">9</button>
      <button class="calc-btn op" onclick="calcInput('/')">&#247;</button>
      <button class="calc-btn" onclick="calcInput('4')">4</button>
      <button class="calc-btn" onclick="calcInput('5')">5</button>
      <button class="calc-btn" onclick="calcInput('6')">6</button>
      <button class="calc-btn op" onclick="calcInput('*')">&#215;</button>
      <button class="calc-btn" onclick="calcInput('1')">1</button>
      <button class="calc-btn" onclick="calcInput('2')">2</button>
      <button class="calc-btn" onclick="calcInput('3')">3</button>
      <button class="calc-btn op" onclick="calcInput('-')">&#8722;</button>
      <button class="calc-btn" onclick="calcInput('0')">0</button>
      <button class="calc-btn" onclick="calcInput('.')">.</button>
      <button class="calc-btn eq" onclick="calcEval()">=</button>
      <button class="calc-btn op" onclick="calcInput('+')">+</button>
    </div>
  </div>

  <div class="card">
    <div class="card-title">&#128514; Modulo de Humor</div>
    <div class="joke-text" id="joke-text">Clique no botao para uma piada nerd...</div>
    <button class="btn" style="margin-top:14px;width:100%" onclick="loadJoke()">&#9889; Nova Piada</button>
  </div>

</div>

<footer>J.A.R.V.I.S v3.7.9-ULTRA &middot; Just A Rather Very Intelligent System &middot; Sr. Stark</footer>

<div id="pwa-banner">
  <div class="pwa-icon">&#9889;</div>
  <div class="pwa-text">
    <h3>INSTALAR J.A.R.V.I.S</h3>
    <p>Adicionar a tela inicial como app</p>
  </div>
  <div class="pwa-btns">
    <button id="pwa-install">Instalar</button>
    <button id="pwa-dismiss">&#10005;</button>
  </div>
</div>

<script>
const socket = io();
socket.on('sysinfo', d => {
  document.getElementById('live-time').textContent = d.time;
  updateGauge('gauge-cpu-arc', d.cpu);
  updateGauge('gauge-ram-arc', d.ram);
  updateGauge('gauge-disk-arc', d.disk);
  document.getElementById('cpu-pct').textContent = d.cpu.toFixed(1)+'%';
  document.getElementById('ram-pct').textContent = d.ram.toFixed(1)+'%';
  document.getElementById('disk-pct').textContent = d.disk.toFixed(1)+'%';
  setBar('cpu-bar', d.cpu);
  setBar('ram-bar', d.ram);
  setBar('disk-bar', d.disk);
  document.getElementById('cpu-val').textContent = d.cpu.toFixed(1)+'%';
});
function updateGauge(id,pct){const circ=201;document.getElementById(id).style.strokeDashoffset=circ-(pct/100*circ);}
function setBar(id,pct){const el=document.getElementById(id);el.style.width=pct+'%';el.className='bar-fill '+(pct<60?'low':pct<85?'mid':'high');}
async function loadSysinfo(){
  const d=await fetch('/api/sysinfo').then(r=>r.json());
  document.getElementById('cpu-val').textContent=d.cpu.toFixed(1)+'%';
  document.getElementById('cpu-cores').textContent=d.cpu_cores;
  document.getElementById('ram-val').textContent=d.ram_used+' / '+d.ram_total+' GB';
  document.getElementById('disk-val').textContent=d.disk_used+' / '+d.disk_total+' GB';
  setBar('ram-bar',d.ram_pct);setBar('disk-bar',d.disk_pct);
  document.getElementById('uptime').textContent=d.uptime;
  document.getElementById('os-info').textContent=d.os;
  document.getElementById('net-sent').textContent=d.net_sent+' MB';
  document.getElementById('net-recv').textContent=d.net_recv+' MB';
}
async function loadProcesses(){
  const data=await fetch('/api/processes').then(r=>r.json());
  document.getElementById('proc-table').innerHTML=data.map(p=>
    '<tr><td style="color:var(--dim)">'+p.pid+'</td><td>'+p.name+'</td><td><span class="cpu-bar" style="width:'+Math.min(p.cpu*1.2,60)+'px"></span>'+p.cpu.toFixed(1)+'%</td><td>'+p.mem+'</td></tr>'
  ).join('');
}
async function loadWeather(){
  const city=document.getElementById('city-input').value||'Sao Paulo';
  const d=await fetch('/api/weather?city='+encodeURIComponent(city)).then(r=>r.json());
  const el=document.getElementById('weather-display');
  if(d.error){el.innerHTML='<div style="color:var(--red)">'+d.error+'</div>';return;}
  el.innerHTML='<div class="weather-icon">'+d.icon+'</div><div class="weather-temp">'+d.temp.toFixed(1)+'&deg;C</div><div class="weather-desc">'+d.desc+(d.simulated?' <span style="color:var(--dim);font-size:.7rem">(simulado)</span>':'')+'</div><div class="weather-row"><div class="weather-stat"><div class="label">Sensacao</div><div class="val">'+d.feels.toFixed(1)+'&deg;C</div></div><div class="weather-stat"><div class="label">Umidade</div><div class="val">'+d.humidity+'%</div></div><div class="weather-stat"><div class="label">Vento</div><div class="val">'+d.wind+' km/h</div></div></div>';
}
async function loadNetwork(){
  const d=await fetch('/api/network').then(r=>r.json());
  let html='<div class="info-item"><div class="k">IP Publico</div><div class="v">'+d.public_ip+'</div></div><div class="info-item"><div class="k">Hostname</div><div class="v">'+d.hostname+'</div></div><div class="info-item"><div class="k">IP Local</div><div class="v">'+d.local_ip+'</div></div>';
  d.interfaces.forEach(i=>{html+='<div class="info-item"><div class="k">'+i.name+'</div><div class="v">'+i.ip+'</div></div>';});
  document.getElementById('net-info').innerHTML=html;
}
function appendMsg(text,role){
  const box=document.getElementById('chat-box');
  const div=document.createElement('div');
  div.className='msg '+role;
  if(role==='jarvis')div.innerHTML='<div class="sender">J.A.R.V.I.S</div>'+text;
  else div.textContent=text;
  box.appendChild(div);box.scrollTop=box.scrollHeight;return div;
}
async function sendChat(){
  const input=document.getElementById('chat-input');
  const text=input.value.trim();if(!text)return;
  input.value='';
  appendMsg(text,'user');
  const thinking=appendMsg('processando...','jarvis thinking');
  const lower=text.toLowerCase();
  if(lower.includes('piada')||lower.includes('joke')){
    const d=await fetch('/api/joke').then(r=>r.json());
    thinking.className='msg jarvis';
    thinking.innerHTML='<div class="sender">J.A.R.V.I.S</div>'+d.joke;return;
  }
  if(lower.startsWith('wiki ')||lower.startsWith('pesquisa ')){
    const q=text.split(' ').slice(1).join(' ');
    const d=await fetch('/api/wiki?q='+encodeURIComponent(q)).then(r=>r.json());
    thinking.className='msg jarvis';
    thinking.innerHTML='<div class="sender">J.A.R.V.I.S</div>'+(d.error?'Erro: '+d.error:'<strong>'+d.title+'</strong><br><span style="font-size:.8rem;color:var(--dim)">'+d.summary+'</span>');return;
  }
  if(lower.startsWith('calc ')){
    const expr=text.slice(5);
    const d=await fetch('/api/calc?expr='+encodeURIComponent(expr)).then(r=>r.json());
    thinking.className='msg jarvis';
    thinking.innerHTML='<div class="sender">J.A.R.V.I.S</div><code>'+expr+' = '+(d.result!=null?d.result:d.error)+'</code>';return;
  }
  const res=await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:text})}).then(r=>r.json());
  thinking.className='msg jarvis';
  thinking.innerHTML='<div class="sender">J.A.R.V.I.S</div>'+(res.response||res.error||'...');
}
function quickCmd(text){document.getElementById('chat-input').value=text;sendChat();}
async function searchWiki(){
  const q=document.getElementById('wiki-input').value.trim();if(!q)return;
  document.getElementById('wiki-result').innerHTML='<span style="color:var(--dim)">Pesquisando...</span>';
  const d=await fetch('/api/wiki?q='+encodeURIComponent(q)).then(r=>r.json());
  if(d.error){document.getElementById('wiki-result').innerHTML='<span style="color:var(--red)">'+d.error+'</span>';return;}
  document.getElementById('wiki-result').innerHTML='<strong style="color:var(--cyan)">'+d.title+'</strong><br><br>'+d.summary+'<br><br><a href="'+d.url+'" target="_blank" style="color:var(--cyan);font-size:.75rem">Ver artigo completo</a>';
}
let calcExpr='';
function calcInput(v){if(calcExpr==='0')calcExpr='';calcExpr+=v;document.getElementById('calc-display').textContent=calcExpr;}
function calcClear(){calcExpr='';document.getElementById('calc-display').textContent='0';}
async function calcEval(){
  if(!calcExpr)return;
  const d=await fetch('/api/calc?expr='+encodeURIComponent(calcExpr)).then(r=>r.json());
  if(d.result!=null){document.getElementById('calc-display').textContent=calcExpr+' = '+d.result;calcExpr=String(d.result);}
  else{document.getElementById('calc-display').textContent='Erro';calcExpr='';}
}
async function loadJoke(){const d=await fetch('/api/joke').then(r=>r.json());document.getElementById('joke-text').textContent=d.joke;}
(async()=>{
  await loadSysinfo();loadProcesses();loadWeather();loadNetwork();
  appendMsg('Bom dia, Sr. Stark. Todos os sistemas operacionais e prontos. Como posso auxiliar?','jarvis');
  setInterval(loadProcesses,5000);setInterval(loadSysinfo,3000);
})();
if('serviceWorker' in navigator){window.addEventListener('load',()=>{navigator.serviceWorker.register('/static/sw.js').catch(()=>{});});}
let deferredPrompt=null;
const banner=document.getElementById('pwa-banner');
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferredPrompt=e;setTimeout(()=>banner.classList.add('show'),3000);});
document.getElementById('pwa-install').addEventListener('click',async()=>{
  if(!deferredPrompt)return;deferredPrompt.prompt();
  const{outcome}=await deferredPrompt.userChoice;
  if(outcome==='accepted')banner.classList.remove('show');deferredPrompt=null;
});
document.getElementById('pwa-dismiss').addEventListener('click',()=>banner.classList.remove('show'));
window.addEventListener('appinstalled',()=>{banner.classList.remove('show');appendMsg('App instalado! Agora tenho acesso direto ao seu dispositivo. 😎','jarvis');});
</script>
</body>
</html>"""

# ── Routes ──────────────────────────────────────────────────

@app.route("/")
def index():
    return HTML_PAGE

@app.route("/api/sysinfo")
def sysinfo():
    cpu = psutil.cpu_percent(interval=0.3)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = str(datetime.datetime.now() - boot).split(".")[0]
    return jsonify({
        "cpu": cpu, "cpu_cores": psutil.cpu_count(),
        "ram_used": round(ram.used/1e9,1), "ram_total": round(ram.total/1e9,1), "ram_pct": ram.percent,
        "disk_used": round(disk.used/1e9,1), "disk_total": round(disk.total/1e9,1), "disk_pct": disk.percent,
        "net_sent": round(net.bytes_sent/1e6,1), "net_recv": round(net.bytes_recv/1e6,1),
        "uptime": uptime, "os": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(), "host": socket.gethostname(),
        "now": datetime.datetime.now().strftime("%H:%M:%S"),
        "date": datetime.datetime.now().strftime("%A, %d de %B de %Y"),
    })

@app.route("/api/processes")
def processes():
    procs = []
    for p in psutil.process_iter(["pid","name","cpu_percent","memory_info","status"]):
        try:
            mem = (p.info["memory_info"] or type("x",(),{"rss":0})()).rss
            procs.append({
                "pid": p.info["pid"],
                "name": (p.info["name"] or "?")[:28],
                "cpu": p.info["cpu_percent"] or 0,
                "mem": round(mem/1e6, 1),
                "status": p.info["status"],
            })
        except Exception:
            pass
    procs.sort(key=lambda x: x["cpu"], reverse=True)
    return jsonify(procs[:15])

@app.route("/api/network")
def network():
    try:
        pub_ip = requests.get("https://api.ipify.org", timeout=4).text
    except Exception:
        pub_ip = "Offline"
    interfaces = []
    for iface, addrs in psutil.net_if_addrs().items():
        for a in addrs:
            if a.family == socket.AF_INET:
                interfaces.append({"name": iface, "ip": a.address})
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        local_ip = "N/A"
    return jsonify({
        "public_ip": pub_ip,
        "hostname": socket.gethostname(),
        "local_ip": local_ip,
        "interfaces": interfaces,
    })

@app.route("/api/weather")
def weather():
    city = request.args.get("city", "Sao Paulo")
    if not OPENWEATHER_KEY:
        return jsonify({"city": city, "desc": "Parcialmente Nublado", "temp": 24.0,
                        "feels": 23.0, "humidity": 68, "wind": 12, "icon": "&#9925;", "simulated": True})
    try:
        url = (f"https://api.openweathermap.org/data/2.5/weather"
               f"?q={urllib.parse.quote(city)}&appid={OPENWEATHER_KEY}&units=metric&lang=pt_br")
        d = requests.get(url, timeout=5).json()
        icons = {"Clear":"&#9728;","Clouds":"&#9925;","Rain":"&#127783;","Thunderstorm":"&#9928;","Snow":"&#10052;","Mist":"&#127787;"}
        return jsonify({"city": city, "desc": d["weather"][0]["description"].capitalize(),
                        "temp": d["main"]["temp"], "feels": d["main"]["feels_like"],
                        "humidity": d["main"]["humidity"], "wind": round(d["wind"]["speed"]*3.6,1),
                        "icon": icons.get(d["weather"][0]["main"],"&#127777;"), "simulated": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/wiki")
def wiki_search():
    q = request.args.get("q","")
    if not q:
        return jsonify({"error": "query vazia"}), 400
    page = wiki.page(q)
    if not page.exists():
        return jsonify({"error": f"Nenhum resultado para '{q}'"})
    summary = page.summary[:600] + "..." if len(page.summary) > 600 else page.summary
    return jsonify({"title": page.title, "summary": summary, "url": page.fullurl})

@app.route("/api/calc")
def calc():
    expr = request.args.get("expr","")
    try:
        safe = "".join(c for c in expr if c in "0123456789+-*/().^ %")
        safe = safe.replace("^","**")
        result = eval(safe, {"__builtins__": {}})  # noqa
        return jsonify({"expr": expr, "result": result})
    except Exception:
        return jsonify({"error": "Expressao invalida"}), 400

@app.route("/api/joke")
def joke():
    return jsonify({"joke": random.choice(JOKES)})

@app.route("/api/ai", methods=["POST"])
def ai():
    data = request.json or {}
    prompt = data.get("prompt","")
    if not prompt:
        return jsonify({"error":"prompt vazio"}), 400
    if not OPENAI_KEY:
        now = datetime.datetime.now()
        hora = now.strftime('%H:%M:%S')
        data = now.strftime('%d/%m/%Y')
        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        p = prompt.lower()

        # Saudações
        if any(x in p for x in ["oi", "ola", "olá", "hey", "hello", "e ai", "eai", "tudo bem", "tudo bom"]):
            resps = [
                "Olá, Sr. Stark. Todos os sistemas operacionais e prontos para servir.",
                "Bom dia, Sr. Stark. O que posso fazer por voce hoje?",
                "Saudacoes! Estou aqui, aguardando suas ordens.",
                "Online e operacional. Como posso auxilia-lo?",
            ]
            return jsonify({"response": random.choice(resps)})

        # Quem é você
        if any(x in p for x in ["quem", "voce", "você", "jarvis", "apresenta", "se apresente"]):
            return jsonify({"response": "Sou J.A.R.V.I.S — Just A Rather Very Intelligent System, versao 3.7.9-ULTRA. Fui criado para monitorar, auxiliar e impressionar. A seu dispor, Sr. Stark."})

        # Hora / data
        if any(x in p for x in ["hora", "horas", "que horas"]):
            return jsonify({"response": f"Sao exatamente {hora}, Sr. Stark."})
        if any(x in p for x in ["data", "dia", "hoje", "semana"]):
            return jsonify({"response": f"Hoje e {data}, Sr. Stark."})

        # Sistema
        if any(x in p for x in ["sistema", "status", "cpu", "ram", "memoria", "memória", "disco", "computador", "maquina", "máquina"]):
            status_cpu = "normal" if cpu < 70 else "elevada" if cpu < 90 else "CRITICA"
            status_ram = "normal" if ram.percent < 70 else "elevada" if ram.percent < 90 else "CRITICA"
            return jsonify({"response": f"Relatorio de sistemas, Sr. Stark:\n• CPU: {cpu:.1f}% ({status_cpu})\n• RAM: {ram.percent:.1f}% — {ram.used/1e9:.1f}GB usados de {ram.total/1e9:.1f}GB ({status_ram})\n• Disco: {disk.percent:.1f}% — {disk.used/1e9:.1f}GB de {disk.total/1e9:.1f}GB\nTodos os sistemas dentro dos parametros aceitaveis."})

        # Clima
        if any(x in p for x in ["clima", "tempo", "chuva", "frio", "calor", "temperatura"]):
            return jsonify({"response": "Para informacoes de clima em tempo real, utilize o modulo de clima no painel abaixo, Sr. Stark. Basta digitar o nome da cidade."})

        # Piada
        if any(x in p for x in ["piada", "engraçado", "engracado", "humor", "rir", "risada"]):
            return jsonify({"response": random.choice(JOKES)})

        # Motivação
        if any(x in p for x in ["motiva", "animo", "ânimo", "força", "forca", "coragem", "inspiracao", "inspiração"]):
            frases = [
                "O unico modo de fazer um excelente trabalho e amar o que voce faz. — Steve Jobs",
                "Nao importa o quao devagar voce va, desde que nao pare. — Confucio",
                "O sucesso e a soma de pequenos esforcos repetidos dia apos dia. — R. Collier",
                "Acredite que voce pode e ja esta na metade do caminho. — Theodore Roosevelt",
                "Voce e mais corajoso do que acredita, mais forte do que parece e mais inteligente do que pensa. — A. A. Milne",
            ]
            return jsonify({"response": random.choice(frases)})

        # Dica de programação
        if any(x in p for x in ["dica", "programacao", "programação", "codigo", "código", "dev", "python", "tip"]):
            dicas = [
                "Dica: Use list comprehensions em Python. `[x*2 for x in lista]` e mais rapido e elegante que um loop for.",
                "Dica: Nomeie variaveis com clareza. `user_age` e melhor que `ua`. Seu eu futuro agradece.",
                "Dica: Commits pequenos e frequentes sao melhores que commits gigantes. Git blame sera seu amigo.",
                "Dica: DRY — Don't Repeat Yourself. Se voce copiou o mesmo codigo duas vezes, vire uma funcao.",
                "Dica: Leia erros de verdade. 90% dos bugs estao na mensagem de erro que voce ignorou.",
                "Dica: `print()` ainda e uma ferramenta valida de debug. Nao deixe ninguem te dizer o contrario.",
            ]
            return jsonify({"response": random.choice(dicas)})

        # Obrigado
        if any(x in p for x in ["obrigado", "obrigada", "valeu", "thanks", "thank"]):
            return jsonify({"response": "Sempre as ordens, Sr. Stark. Para isso estou aqui."})

        # Wikipedia trigger
        if any(x in p for x in ["o que e", "o que é", "quem foi", "quem e", "me fala sobre", "pesquisa", "wiki"]):
            return jsonify({"response": "Para pesquisas, use o modulo Wikipedia no painel! Digite o termo na caixa de busca e encontrarei tudo sobre o assunto, Sr. Stark."})

        # Calcular
        if any(x in p for x in ["calcula", "quanto e", "quanto é", "calcule", "soma", "divide", "multiplica"]):
            return jsonify({"response": "Para calculos, use a Calculadora Stark no painel! Ela suporta operacoes avancadas incluindo potenciacao (^) e parenteses."})

        # Fallback inteligente
        resps_fallback = [
            f"Processando '{prompt[:50]}', Sr. Stark. Para respostas de IA completas, configure OPENAI_API_KEY nas variaveis de ambiente do Railway.",
            f"Comando recebido. Meus circuitos de linguagem natural estao em modo economico. Configure uma chave de IA para desbloquear todo o meu potencial.",
            "Entendido, Sr. Stark. Posso ajuda-lo melhor com informacoes de sistema, clima, Wikipedia ou calculos — use os modulos no painel!",
        ]
        return jsonify({"response": random.choice(resps_fallback)})
    try:
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type":"application/json"},
            json={"model":"gpt-4o","messages":[
                {"role":"system","content":"Voce e J.A.R.V.I.S, assistente ultra-avancado. Responda em portugues, conciso e levemente sarcastico."},
                {"role":"user","content":prompt}
            ],"max_tokens":400},
            timeout=20,
        ).json()
        return jsonify({"response": res["choices"][0]["message"]["content"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Live stream ──────────────────────────────────────────────

def stream_sysinfo():
    while True:
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            socketio.emit("sysinfo", {
                "cpu": cpu, "ram": ram.percent, "disk": disk.percent,
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
            })
        except Exception:
            pass
        time.sleep(1)

@socketio.on("connect")
def on_connect():
    pass

t = threading.Thread(target=stream_sysinfo, daemon=True)
t.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)
