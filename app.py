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
    "A disciplina é a ponte entre metas e realizações. — Jim Rohn",
    "Sonhos não funcionam a menos que você trabalhe. — John C. Maxwell",
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
    "O Wi-Fi não significa nada. É só uma marca registrada que soa bem. Não é abreviação de Wireless Fidelity.",
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
    "Sou J.A.R.V.I.S — Just A Rather Very Intelligent System, versão 4.0-ULTRA. Fui projetado para monitorar sistemas, auxiliar com informações e, ocasionalmente, tolerar perguntas óbvias com elegância.",
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
    "Meus módulos estão ansiosos. Que tal: status do sistema, uma piada, uma curiosidade tecnológica ou uma dica de programação?",
    "Posso ajudar com informações de sistema em tempo real, clima, pesquisas, cálculos ou simplesmente bater papo. Escolha sua aventura.",
]

# ── Safe Math Evaluator ─────────────────────────────────────────────────────────
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

# ── Notes Storage ───────────────────────────────────────────────────────────────
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

# ── PWA Assets ──────────────────────────────────────────────────────────────────
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
    {"src": "/icon.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    {"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}
  ]
}"""

SW_JS = """
const CACHE = 'jarvis-v2';
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

# ── HTML ────────────────────────────────────────────────────────────────────────
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
<link rel="apple-touch-icon" href="/icon.png"/>
<link rel="icon" type="image/png" href="/icon.png"/>
<link rel="icon" type="image/svg+xml" href="/icon.svg"/>
<script src="https://cdn.socket.io/4.7.4/socket.io.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
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
header{display:flex;align-items:center;justify-content:space-between;padding:12px 28px;background:var(--hbg);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;backdrop-filter:blur(10px)}
.logo{display:flex;align-items:center;gap:14px}
.logo .arc{width:48px;height:48px;border:2px solid var(--cyan);border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:var(--glow),inset 0 0 12px rgba(0,212,255,.3);animation:pulse 2s ease-in-out infinite;overflow:hidden;padding:2px}
.logo .arc img{width:100%;height:100%;border-radius:50%;object-fit:cover}
@keyframes pulse{0%,100%{box-shadow:var(--glow),inset 0 0 12px rgba(0,212,255,.3)}50%{box-shadow:0 0 28px rgba(0,212,255,.7),inset 0 0 20px rgba(0,212,255,.5)}}
.logo h1{font-size:1.4rem;font-weight:700;color:var(--cyan);letter-spacing:3px}
.logo span{font-size:.7rem;color:var(--dim);letter-spacing:2px}
.hright{display:flex;align-items:center;gap:10px}
#live-time{font-size:1.6rem;font-weight:300;color:var(--cyan);font-variant-numeric:tabular-nums}
.sdot{width:8px;height:8px;background:var(--green);border-radius:50%;box-shadow:0 0 8px var(--green);animation:blink 1.4s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.ibtn{background:var(--ibg);border:1px solid var(--border);color:var(--cyan);border-radius:8px;padding:6px 10px;cursor:pointer;font-size:.95rem;transition:all .2s;line-height:1}
.ibtn:hover{background:rgba(0,212,255,.15);box-shadow:var(--glow)}
#ai-badge{font-size:.62rem;background:rgba(0,212,255,.1);border:1px solid rgba(0,212,255,.2);color:var(--cyan);padding:3px 9px;border-radius:20px;letter-spacing:1px;white-space:nowrap}

/* ── Grid / Cards ── */
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;padding:20px 24px}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;box-shadow:var(--glow2);transition:border-color .3s,box-shadow .3s,background .3s}
.card:hover{border-color:rgba(0,212,255,.4);box-shadow:0 0 32px rgba(0,212,255,.2)}
.card-title{font-size:.7rem;letter-spacing:2px;text-transform:uppercase;color:var(--cyan);margin-bottom:16px;display:flex;align-items:center;gap:8px}
.card-title::before{content:'';flex:1;height:1px;background:var(--border);order:1}
.span2{grid-column:span 2}
@media(max-width:900px){.span2{grid-column:span 1}}

/* ── Metrics & Bars ── */
.metric{margin-bottom:14px}
.mh{display:flex;justify-content:space-between;font-size:.82rem;margin-bottom:5px}
.ml{color:var(--dim)}.mv{color:var(--cyan);font-weight:600;font-variant-numeric:tabular-nums}
.btrack{background:rgba(255,255,255,.05);border-radius:4px;height:8px;overflow:hidden}
.bfill{height:100%;border-radius:4px;transition:width .8s cubic-bezier(.25,.46,.45,.94),background .5s}
.bfill.low{background:linear-gradient(90deg,#00ff9d,#00cc7a);box-shadow:0 0 8px rgba(0,255,157,.4)}
.bfill.mid{background:linear-gradient(90deg,#ffd32a,#ff9f43);box-shadow:0 0 8px rgba(255,211,42,.4)}
.bfill.high{background:linear-gradient(90deg,#ff4757,#ff6b81);box-shadow:0 0 8px rgba(255,71,87,.4)}

/* ── Gauges ── */
.gauges{display:flex;gap:16px;justify-content:space-around;margin-bottom:12px}
.gc{text-align:center}.gc svg{width:80px;height:80px}
.gpct{font-size:1.1rem;font-weight:700;color:var(--cyan)}
.glbl{font-size:.65rem;color:var(--dim);letter-spacing:1px}

/* ── Table ── */
.dt{width:100%;border-collapse:collapse;font-size:.8rem}
.dt th{color:var(--cyan);font-weight:500;padding:6px 8px;border-bottom:1px solid var(--border);text-align:left}
.dt td{padding:5px 8px;color:var(--text);border-bottom:1px solid rgba(255,255,255,.03)}
.dt tr:hover td{background:rgba(0,212,255,.04)}
.cb{display:inline-block;height:4px;background:var(--cyan);border-radius:2px;vertical-align:middle;margin-right:4px}

/* ── Info Grid ── */
.igrid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.ii{background:var(--ibg);border:1px solid var(--border);border-radius:6px;padding:8px 12px}
.ii .k{font-size:.68rem;color:var(--dim);letter-spacing:1px;text-transform:uppercase}
.ii .v{font-size:.88rem;color:var(--text);font-weight:500;margin-top:2px;word-break:break-all}

/* ── Chat ── */
.chat-box{height:300px;overflow-y:auto;display:flex;flex-direction:column;gap:10px;padding:12px;background:var(--ibg);border-radius:8px;margin-bottom:12px;border:1px solid var(--border)}
.chat-box::-webkit-scrollbar{width:4px}
.chat-box::-webkit-scrollbar-thumb{background:rgba(0,212,255,.3);border-radius:2px}
.msg{max-width:80%;padding:8px 14px;border-radius:10px;font-size:.85rem;line-height:1.5;word-break:break-word}
.msg.user{align-self:flex-end;background:rgba(0,212,255,.15);border:1px solid rgba(0,212,255,.25)}
.msg.jarvis{align-self:flex-start;background:rgba(0,30,60,.6);border:1px solid rgba(0,212,255,.12)}
[data-theme="light"] .msg.jarvis{background:rgba(0,119,170,.08);border-color:rgba(0,119,170,.2)}
.msg.jarvis .sender{font-size:.7rem;color:var(--cyan);letter-spacing:1px;margin-bottom:3px}
.msg.thinking{opacity:.6;font-style:italic;animation:think .8s ease-in-out infinite alternate}
@keyframes think{from{opacity:.4}to{opacity:.8}}
.crow{display:flex;gap:8px}
.cinput,#city-input,#wiki-input,#note-input{flex:1;background:var(--ibg);border:1px solid var(--iborder);border-radius:8px;color:var(--text);padding:10px 14px;font-size:.9rem;outline:none;transition:border .2s}
.cinput:focus,#city-input:focus,#wiki-input:focus,#note-input:focus{border-color:var(--cyan);box-shadow:0 0 10px rgba(0,212,255,.12)}
.cinput::placeholder,#city-input::placeholder,#wiki-input::placeholder,#note-input::placeholder{color:var(--dim)}
.btn{background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.3);color:var(--cyan);border-radius:8px;padding:10px 18px;cursor:pointer;font-size:.85rem;letter-spacing:1px;transition:all .2s}
.btn:hover{background:rgba(0,212,255,.18);box-shadow:0 0 12px rgba(0,212,255,.25)}
.btn:active{transform:scale(.97)}
.btn.va{background:rgba(255,71,87,.15);border-color:var(--red);color:var(--red);animation:blink .6s ease-in-out infinite}
.qbtns{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}
.qbtn{background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.15);color:var(--dim);border-radius:20px;padding:4px 12px;font-size:.75rem;cursor:pointer;transition:all .2s;letter-spacing:.5px}
.qbtn:hover{background:rgba(0,212,255,.12);color:var(--cyan);border-color:rgba(0,212,255,.3)}

/* ── Weather ── */
.wdisplay{text-align:center;padding:10px 0}
.wicon{font-size:3rem;line-height:1.2}
.wtemp{font-size:2.5rem;font-weight:300;color:var(--cyan)}
.wdesc{color:var(--dim);font-size:.85rem;margin-bottom:12px}
.wrow{display:flex;justify-content:space-around;font-size:.8rem}
.wstat .wl{color:var(--dim)}.wstat .wv{color:var(--text);font-weight:600}
.crow2{display:flex;gap:8px;margin-bottom:12px}
#city-input,#wiki-input{padding:8px 12px;font-size:.85rem}

/* ── Calculator ── */
.cdisp{background:var(--ibg);border:1px solid var(--iborder);border-radius:8px;padding:10px 14px;margin-bottom:10px;font-size:1.1rem;min-height:44px;color:var(--cyan);font-family:monospace;letter-spacing:1px}
.cgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}
.cbtn{background:rgba(0,212,255,.06);border:1px solid rgba(0,212,255,.12);color:var(--text);border-radius:8px;padding:12px;font-size:.95rem;cursor:pointer;transition:all .15s;font-family:monospace}
.cbtn:hover{background:rgba(0,212,255,.15);color:var(--cyan)}
.cbtn.op{color:var(--cyan)}.cbtn.eq{background:rgba(0,212,255,.2);color:var(--cyan);font-weight:700}
.cbtn.clr{color:var(--red)}

/* ── Joke ── */
.joke-text{background:var(--ibg);border:1px solid var(--border);border-radius:8px;padding:16px;font-size:.9rem;line-height:1.6;color:var(--text);min-height:60px;text-align:center;font-style:italic}

/* ── Notes ── */
.nlist{max-height:210px;overflow-y:auto;display:flex;flex-direction:column;gap:6px;margin-bottom:12px}
.nlist::-webkit-scrollbar{width:4px}
.nlist::-webkit-scrollbar-thumb{background:rgba(0,212,255,.3);border-radius:2px}
.ni{display:flex;align-items:center;gap:8px;background:var(--ibg);border:1px solid var(--border);border-radius:8px;padding:8px 12px;font-size:.82rem;transition:opacity .2s}
.ni .nt{flex:1;color:var(--text);cursor:pointer;user-select:none}
.ni .ntm{font-size:.68rem;color:var(--dim);white-space:nowrap}
.ni .nd{background:none;border:none;color:var(--dim);cursor:pointer;font-size:1.1rem;padding:0 2px;transition:color .2s;line-height:1}
.ni .nd:hover{color:var(--red)}
.ni.done .nt{text-decoration:line-through;opacity:.45}

/* ── Chart ── */
#perf-chart{max-height:160px}

/* ── Footer ── */
footer{text-align:center;padding:16px;color:var(--dim);font-size:.72rem;letter-spacing:2px;border-top:1px solid var(--border);margin-top:8px}

/* ── PWA Banner ── */
#pwa-banner{display:none;position:fixed;bottom:0;left:0;right:0;z-index:9000;background:var(--hbg);border-top:1px solid rgba(0,212,255,.35);padding:14px 20px 20px;box-shadow:0 -8px 32px rgba(0,212,255,.15);backdrop-filter:blur(12px)}
#pwa-banner.show{display:flex;align-items:center;gap:14px}
#pwa-banner .pi{font-size:2.4rem;flex-shrink:0}
#pwa-banner .pt{flex:1}
#pwa-banner .pt h3{color:var(--cyan);font-size:.95rem;letter-spacing:1px}
#pwa-banner .pt p{color:var(--dim);font-size:.78rem;margin-top:2px}
#pwa-banner .pb{display:flex;gap:8px;flex-shrink:0}
#pwa-install{background:var(--cyan);color:#060f1e;border:none;border-radius:8px;padding:10px 18px;font-weight:700;font-size:.85rem;cursor:pointer;letter-spacing:1px}
#pwa-dismiss{background:transparent;color:var(--dim);border:1px solid rgba(255,255,255,.15);border-radius:8px;padding:10px 14px;cursor:pointer;font-size:.8rem}

/* ── Responsive ── */
@media(max-width:600px){
  header{padding:10px 14px}.logo h1{font-size:1rem}.logo span{display:none}
  #live-time{font-size:1.2rem}.grid{padding:12px 10px;gap:12px}.card{padding:14px}
  .gauges{gap:8px}.gc svg{width:64px;height:64px}.gpct{font-size:.9rem}
  .chat-box{height:220px}.cbtn{padding:14px 10px;font-size:1rem}
  .wtemp{font-size:2rem}body{padding-bottom:80px}
}
@media(max-width:400px){.igrid,.igrid2{grid-template-columns:1fr}}
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
        <svg viewBox="0 0 80 80"><circle cx="40" cy="40" r="32" fill="none" stroke="rgba(0,212,255,.1)" stroke-width="6"/><circle id="g-cpu" cx="40" cy="40" r="32" fill="none" stroke="var(--cyan)" stroke-width="6" stroke-linecap="round" stroke-dasharray="201" stroke-dashoffset="201" transform="rotate(-90 40 40)" style="transition:stroke-dashoffset .8s"/></svg>
        <div class="gpct" id="cpu-pct">0%</div><div class="glbl">CPU</div>
      </div>
      <div class="gc">
        <svg viewBox="0 0 80 80"><circle cx="40" cy="40" r="32" fill="none" stroke="rgba(0,212,255,.1)" stroke-width="6"/><circle id="g-ram" cx="40" cy="40" r="32" fill="none" stroke="#00ff9d" stroke-width="6" stroke-linecap="round" stroke-dasharray="201" stroke-dashoffset="201" transform="rotate(-90 40 40)" style="transition:stroke-dashoffset .8s"/></svg>
        <div class="gpct" id="ram-pct">0%</div><div class="glbl">RAM</div>
      </div>
      <div class="gc">
        <svg viewBox="0 0 80 80"><circle cx="40" cy="40" r="32" fill="none" stroke="rgba(0,212,255,.1)" stroke-width="6"/><circle id="g-dsk" cx="40" cy="40" r="32" fill="none" stroke="#ffd32a" stroke-width="6" stroke-linecap="round" stroke-dasharray="201" stroke-dashoffset="201" transform="rotate(-90 40 40)" style="transition:stroke-dashoffset .8s"/></svg>
        <div class="gpct" id="disk-pct">0%</div><div class="glbl">DISCO</div>
      </div>
    </div>
    <div class="metric"><div class="mh"><span class="ml">&#128187; CPU (<span id="cpu-cores">?</span> cores)</span><span class="mv" id="cpu-val">—</span></div><div class="btrack"><div class="bfill low" id="cpu-bar" style="width:0%"></div></div></div>
    <div class="metric"><div class="mh"><span class="ml">&#129504; RAM</span><span class="mv" id="ram-val">—</span></div><div class="btrack"><div class="bfill low" id="ram-bar" style="width:0%"></div></div></div>
    <div class="metric"><div class="mh"><span class="ml">&#128190; Disco</span><span class="mv" id="disk-val">—</span></div><div class="btrack"><div class="bfill low" id="disk-bar" style="width:0%"></div></div></div>
    <div class="igrid" style="margin-top:12px">
      <div class="ii"><div class="k">Uptime</div><div class="v" id="uptime">—</div></div>
      <div class="ii"><div class="k">OS</div><div class="v" id="os-info">—</div></div>
      <div class="ii"><div class="k">Rede &uarr;</div><div class="v" id="net-sent">—</div></div>
      <div class="ii"><div class="k">Rede &darr;</div><div class="v" id="net-recv">—</div></div>
    </div>
  </div>

  <!-- Top Processes -->
  <div class="card">
    <div class="card-title">&#128293; Top Processos</div>
    <div style="overflow-x:auto">
      <table class="dt">
        <thead><tr><th>PID</th><th>Nome</th><th>CPU%</th><th>RAM MB</th></tr></thead>
        <tbody id="proc-table"></tbody>
      </table>
    </div>
    <button class="btn" style="margin-top:12px;width:100%" onclick="loadProcs()">&#8635; Atualizar</button>
  </div>

  <!-- Performance Graph -->
  <div class="card span2">
    <div class="card-title">&#128200; Performance em Tempo Real</div>
    <canvas id="perf-chart"></canvas>
  </div>

  <!-- Weather -->
  <div class="card">
    <div class="card-title">&#127750; Clima</div>
    <div class="crow2">
      <input id="city-input" type="text" placeholder="Cidade..." value="São Paulo"/>
      <button class="btn" onclick="loadWeather()">&#128269;</button>
    </div>
    <div class="wdisplay" id="weather-display"><div style="color:var(--dim);font-size:.85rem">Carregando...</div></div>
  </div>

  <!-- Network -->
  <div class="card">
    <div class="card-title">&#127760; Rede</div>
    <div class="igrid" id="net-info"><div style="color:var(--dim);font-size:.85rem">Carregando...</div></div>
  </div>

  <!-- Chat (full width) -->
  <div class="card span2">
    <div class="card-title">&#129302; J.A.R.V.I.S Chat</div>
    <div class="qbtns">
      <span class="qbtn" onclick="qcmd('status do sistema')">&#128202; Sistema</span>
      <span class="qbtn" onclick="qcmd('conta uma piada')">&#128514; Piada</span>
      <span class="qbtn" onclick="qcmd('quem e voce')">&#129302; Quem és?</span>
      <span class="qbtn" onclick="qcmd('qual a hora agora')">&#9201; Hora</span>
      <span class="qbtn" onclick="qcmd('dica de programacao')">&#128161; Dica dev</span>
      <span class="qbtn" onclick="qcmd('motivacao para hoje')">&#128640; Motivação</span>
      <span class="qbtn" onclick="clearHistory()" style="border-color:rgba(255,71,87,.3);color:var(--red)">&#128465; Limpar</span>
    </div>
    <div class="chat-box" id="chat-box"></div>
    <div class="crow">
      <input class="cinput" id="chat-input" type="text" placeholder="Fale com o J.A.R.V.I.S..." onkeydown="if(event.key==='Enter')sendChat()"/>
      <button class="btn" id="vbtn" onclick="toggleVoice()" title="Voz">&#127908;</button>
      <button class="btn" onclick="sendChat()">&#9654; Enviar</button>
    </div>
  </div>

  <!-- Wikipedia -->
  <div class="card">
    <div class="card-title">&#128218; Wikipedia</div>
    <div class="crow2">
      <input id="wiki-input" type="text" placeholder="Pesquisar..." onkeydown="if(event.key==='Enter')searchWiki()"/>
      <button class="btn" onclick="searchWiki()">&#128269;</button>
    </div>
    <div id="wiki-result" style="color:var(--dim);font-size:.82rem;line-height:1.6;max-height:200px;overflow-y:auto"></div>
  </div>

  <!-- Calculator -->
  <div class="card">
    <div class="card-title">&#129518; Calculadora Stark</div>
    <div class="cdisp" id="cdisp">0</div>
    <div class="cgrid">
      <button class="cbtn clr" onclick="cclr()">C</button>
      <button class="cbtn op" onclick="ci('(')">(</button>
      <button class="cbtn op" onclick="ci(')')">)</button>
      <button class="cbtn op" onclick="ci('^')">^</button>
      <button class="cbtn" onclick="ci('7')">7</button>
      <button class="cbtn" onclick="ci('8')">8</button>
      <button class="cbtn" onclick="ci('9')">9</button>
      <button class="cbtn op" onclick="ci('/')">&#247;</button>
      <button class="cbtn" onclick="ci('4')">4</button>
      <button class="cbtn" onclick="ci('5')">5</button>
      <button class="cbtn" onclick="ci('6')">6</button>
      <button class="cbtn op" onclick="ci('*')">&#215;</button>
      <button class="cbtn" onclick="ci('1')">1</button>
      <button class="cbtn" onclick="ci('2')">2</button>
      <button class="cbtn" onclick="ci('3')">3</button>
      <button class="cbtn op" onclick="ci('-')">&#8722;</button>
      <button class="cbtn" onclick="ci('0')">0</button>
      <button class="cbtn" onclick="ci('.')">.</button>
      <button class="cbtn eq" onclick="ceval()">=</button>
      <button class="cbtn op" onclick="ci('+')">+</button>
    </div>
  </div>

  <!-- Notes -->
  <div class="card">
    <div class="card-title">&#128203; Notas &amp; Tarefas</div>
    <div class="nlist" id="notes-list"></div>
    <div class="crow">
      <input id="note-input" type="text" placeholder="Nova nota ou tarefa..." onkeydown="if(event.key==='Enter')addNote()"/>
      <button class="btn" onclick="addNote()">+</button>
    </div>
  </div>

  <!-- Jokes -->
  <div class="card">
    <div class="card-title">&#128514; Módulo de Humor</div>
    <div class="joke-text" id="joke-text">Clique no botão para uma piada nerd...</div>
    <button class="btn" style="margin-top:14px;width:100%" onclick="loadJoke()">&#9889; Nova Piada</button>
  </div>

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
  el.innerHTML='<div class="wicon">'+d.icon+'</div><div class="wtemp">'+d.temp.toFixed(1)+'&deg;C</div><div class="wdesc">'+d.desc+(d.simulated?' <span style="color:var(--dim);font-size:.7rem">(simulado)</span>':'')+'</div><div class="wrow"><div class="wstat"><div class="wl">Sensação</div><div class="wv">'+d.feels.toFixed(1)+'&deg;C</div></div><div class="wstat"><div class="wl">Umidade</div><div class="wv">'+d.humidity+'%</div></div><div class="wstat"><div class="wl">Vento</div><div class="wv">'+d.wind+' km/h</div></div></div>';
}
async function loadNetwork(){
  const d = await fetch('/api/network').then(r=>r.json());
  let h='<div class="ii"><div class="k">IP Público</div><div class="v">'+d.public_ip+'</div></div><div class="ii"><div class="k">Hostname</div><div class="v">'+d.hostname+'</div></div><div class="ii"><div class="k">IP Local</div><div class="v">'+d.local_ip+'</div></div>';
  d.interfaces.forEach(i=>{h+='<div class="ii"><div class="k">'+i.name+'</div><div class="v">'+i.ip+'</div></div>';});
  document.getElementById('net-info').innerHTML=h;
}

// ── Chat with History ──────────────────────────────────────────
let chatHistory = JSON.parse(localStorage.getItem('jchat')||'[]');
function renderHistory(){
  chatHistory.forEach(m => appendMsg(m.content, m.role==='user'?'user':'jarvis', false));
}
function appendMsg(text, role, save=true){
  const box = document.getElementById('chat-box');
  const div = document.createElement('div');
  div.className = 'msg '+role;
  if(role==='jarvis') div.innerHTML='<div class="sender">J.A.R.V.I.S</div>'+text;
  else div.textContent = text;
  box.appendChild(div); box.scrollTop=box.scrollHeight;
  return div;
}
function clearHistory(){
  chatHistory=[]; localStorage.removeItem('jchat');
  document.getElementById('chat-box').innerHTML='';
  appendMsg('Histórico apagado, Sr. Stark. Começando do zero.','jarvis');
}
function saveHistory(){ localStorage.setItem('jchat', JSON.stringify(chatHistory.slice(-50))); }

async function sendChat(){
  const inp = document.getElementById('chat-input');
  const text = inp.value.trim(); if(!text) return;
  inp.value='';
  appendMsg(text,'user');
  chatHistory.push({role:'user',content:text});
  const thinking = appendMsg('processando...','jarvis thinking');
  const lower = text.toLowerCase();

  if(lower.includes('piada')||lower.includes('joke')){
    const d = await fetch('/api/joke').then(r=>r.json());
    thinking.className='msg jarvis';
    thinking.innerHTML='<div class="sender">J.A.R.V.I.S</div>'+d.joke;
    chatHistory.push({role:'assistant',content:d.joke}); saveHistory(); return;
  }
  if(lower.startsWith('wiki ')||lower.startsWith('pesquisa ')){
    const q = text.split(' ').slice(1).join(' ');
    const d = await fetch('/api/wiki?q='+encodeURIComponent(q)).then(r=>r.json());
    const resp = d.error?'Erro: '+d.error:'<strong>'+d.title+'</strong><br><span style="font-size:.8rem;color:var(--dim)">'+d.summary+'</span>';
    thinking.className='msg jarvis'; thinking.innerHTML='<div class="sender">J.A.R.V.I.S</div>'+resp;
    chatHistory.push({role:'assistant',content:d.error||d.title+': '+d.summary}); saveHistory(); return;
  }
  if(lower.startsWith('calc ')){
    const expr = text.slice(5);
    const d = await fetch('/api/calc?expr='+encodeURIComponent(expr)).then(r=>r.json());
    const resp = '<code>'+expr+' = '+(d.result!=null?d.result:d.error)+'</code>';
    thinking.className='msg jarvis'; thinking.innerHTML='<div class="sender">J.A.R.V.I.S</div>'+resp;
    chatHistory.push({role:'assistant',content:expr+' = '+(d.result!=null?d.result:d.error)}); saveHistory(); return;
  }

  const res = await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:text,history:chatHistory.slice(-10)})}).then(r=>r.json());
  const reply = res.response||res.error||'...';
  thinking.className='msg jarvis'; thinking.innerHTML='<div class="sender">J.A.R.V.I.S</div>'+reply;
  chatHistory.push({role:'assistant',content:reply}); saveHistory();
  if(res.provider) document.getElementById('ai-badge').textContent=res.provider.toUpperCase();
}
function qcmd(t){ document.getElementById('chat-input').value=t; sendChat(); }

// ── Voice Input ────────────────────────────────────────────────
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recog=null, listening=false;
if(SR){
  recog=new SR(); recog.lang='pt-BR'; recog.continuous=false; recog.interimResults=false;
  recog.onresult=e=>{ document.getElementById('chat-input').value=e.results[0][0].transcript; sendChat(); };
  recog.onend=()=>{ listening=false; const b=document.getElementById('vbtn'); b.textContent='🎤'; b.classList.remove('va'); };
  recog.onerror=()=>{ listening=false; const b=document.getElementById('vbtn'); b.textContent='🎤'; b.classList.remove('va'); };
}
function toggleVoice(){
  if(!recog){appendMsg('Reconhecimento de voz não suportado neste navegador.','jarvis');return;}
  const b=document.getElementById('vbtn');
  if(listening){recog.stop();}
  else{recog.start();listening=true;b.textContent='🔴';b.classList.add('va');}
}

// ── Wikipedia ──────────────────────────────────────────────────
async function searchWiki(){
  const q=document.getElementById('wiki-input').value.trim(); if(!q)return;
  document.getElementById('wiki-result').innerHTML='<span style="color:var(--dim)">Pesquisando...</span>';
  const d=await fetch('/api/wiki?q='+encodeURIComponent(q)).then(r=>r.json());
  if(d.error){document.getElementById('wiki-result').innerHTML='<span style="color:var(--red)">'+d.error+'</span>';return;}
  document.getElementById('wiki-result').innerHTML='<strong style="color:var(--cyan)">'+d.title+'</strong><br><br>'+d.summary+'<br><br><a href="'+d.url+'" target="_blank" style="color:var(--cyan);font-size:.75rem">Ver artigo completo &#8599;</a>';
}

// ── Calculator ─────────────────────────────────────────────────
let cexpr='';
function ci(v){if(cexpr==='0'||cexpr==='Erro')cexpr='';cexpr+=v;document.getElementById('cdisp').textContent=cexpr;}
function cclr(){cexpr='';document.getElementById('cdisp').textContent='0';}
async function ceval(){
  if(!cexpr)return;
  const d=await fetch('/api/calc?expr='+encodeURIComponent(cexpr)).then(r=>r.json());
  if(d.result!=null){document.getElementById('cdisp').textContent=cexpr+' = '+d.result;cexpr=String(d.result);}
  else{document.getElementById('cdisp').textContent='Erro';cexpr='';}
}

// ── Joke ───────────────────────────────────────────────────────
async function loadJoke(){ const d=await fetch('/api/joke').then(r=>r.json()); document.getElementById('joke-text').textContent=d.joke; }

// ── Notes ──────────────────────────────────────────────────────
let notes = JSON.parse(localStorage.getItem('jnotes')||'[]');
function esc(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function renderNotes(){
  const el=document.getElementById('notes-list');
  if(!notes.length){el.innerHTML='<div style="color:var(--dim);font-size:.8rem;text-align:center;padding:12px">Nenhuma nota ainda. Adicione uma! 📝</div>';return;}
  el.innerHTML=notes.map((n,i)=>'<div class="ni'+(n.done?' done':'')+'"><span class="nt" onclick="toggleNote('+i+')">'+esc(n.text)+'</span><span class="ntm">'+n.time+'</span><button class="nd" onclick="delNote('+i+')">&#215;</button></div>').join('');
}
function addNote(){
  const el=document.getElementById('note-input');
  const t=el.value.trim(); if(!t)return;
  notes.unshift({text:t,time:new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}),done:false});
  localStorage.setItem('jnotes',JSON.stringify(notes)); el.value=''; renderNotes();
}
function delNote(i){notes.splice(i,1);localStorage.setItem('jnotes',JSON.stringify(notes));renderNotes();}
function toggleNote(i){notes[i].done=!notes[i].done;localStorage.setItem('jnotes',JSON.stringify(notes));renderNotes();}

// ── Init ───────────────────────────────────────────────────────
(async()=>{
  await loadSysinfo(); loadProcs(); loadWeather(); loadNetwork();
  renderHistory(); renderNotes();
  if(chatHistory.length===0) appendMsg('Bom dia, Sr. Stark. Todos os sistemas operacionais e prontos para servir. Como posso auxiliar?','jarvis');
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
document.getElementById('pwa-install').addEventListener('click',async()=>{if(!dp)return;dp.prompt();const{outcome}=await dp.userChoice;if(outcome==='accepted')banner.classList.remove('show');dp=null;});
document.getElementById('pwa-dismiss').addEventListener('click',()=>banner.classList.remove('show'));
window.addEventListener('appinstalled',()=>{banner.classList.remove('show');appendMsg('App instalado! Agora tenho acesso direto ao seu dispositivo. 😎','jarvis');});
</script>
</body>
</html>"""

# ── Routes ──────────────────────────────────────────────────────────────────────

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
def serve_icon_png():
    import os
    icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
    if os.path.exists(icon_path):
        with open(icon_path, "rb") as f:
            return Response(f.read(), mimetype="image/png")
    return serve_icon()

@app.route("/api/sysinfo")
def sysinfo():
    cpu  = psutil.cpu_percent(interval=0.3)
    ram  = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net  = psutil.net_io_counters()
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = str(datetime.datetime.now() - boot).split(".")[0]
    return jsonify({
        "cpu": cpu, "cpu_cores": psutil.cpu_count(),
        "ram": ram.percent,
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
                "mem": round(mem/1e6,1),
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
    return jsonify({"public_ip": pub_ip, "hostname": socket.gethostname(), "local_ip": local_ip, "interfaces": interfaces})

@app.route("/api/weather")
def weather():
    city = request.args.get("city", "São Paulo")
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
    q = request.args.get("q", "")
    if not q:
        return jsonify({"error": "query vazia"}), 400
    page = wiki.page(q)
    if not page.exists():
        return jsonify({"error": f"Nenhum resultado para '{q}'"})
    summary = page.summary[:600] + "..." if len(page.summary) > 600 else page.summary
    return jsonify({"title": page.title, "summary": summary, "url": page.fullurl})

@app.route("/api/calc")
def calc():
    expr = request.args.get("expr", "")
    try:
        result = safe_eval(expr)
        # Round for display
        if isinstance(result, float) and result == int(result):
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 10)
        return jsonify({"expr": expr, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/joke")
def joke():
    return jsonify({"joke": random.choice(JOKES)})

# ── Notes API ───────────────────────────────────────────────────────────────────

@app.route("/api/notes", methods=["GET"])
def get_notes():
    return jsonify(load_notes())

@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.json or {}
    notes = load_notes()
    note = {
        "id": int(time.time() * 1000),
        "text": str(data.get("text", ""))[:500],
        "time": data.get("time", datetime.datetime.now().strftime("%H:%M")),
        "done": False,
    }
    notes.insert(0, note)
    save_notes(notes)
    return jsonify(note), 201

@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    notes = [n for n in load_notes() if n.get("id") != note_id]
    save_notes(notes)
    return jsonify({"ok": True})

# ── AI — Groq → OpenAI → Built-in ───────────────────────────────────────────────

@app.route("/api/ai", methods=["POST"])
def ai():
    data    = request.json or {}
    prompt  = data.get("prompt", "")
    history = data.get("history", [])
    is_ping = data.get("ping", False)

    if not prompt:
        return jsonify({"error": "prompt vazio"}), 400

    # Ping — só retorna qual provedor está disponível
    if is_ping:
        if GROQ_KEY:   return jsonify({"provider": "groq"})
        if OPENAI_KEY: return jsonify({"provider": "openai"})
        return jsonify({"provider": "built-in"})

    # Monta histórico para IA
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history[-8:]:
        if m.get("role") in ("user","assistant") and m.get("content"):
            messages.append({"role": m["role"], "content": str(m["content"])[:600]})
    messages.append({"role": "user", "content": prompt})

    # 1️⃣ Tenta Groq (grátis, rápido — llama3)
    if GROQ_KEY:
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                json={"model": "llama3-8b-8192", "messages": messages, "max_tokens": 500, "temperature": 0.75},
                timeout=15,
            ).json()
            return jsonify({"response": res["choices"][0]["message"]["content"], "provider": "groq"})
        except Exception:
            pass  # Cai para próximo provedor

    # 2️⃣ Tenta OpenAI
    if OPENAI_KEY:
        try:
            res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
                json={"model": "gpt-4o-mini", "messages": messages, "max_tokens": 500},
                timeout=20,
            ).json()
            return jsonify({"response": res["choices"][0]["message"]["content"], "provider": "openai"})
        except Exception:
            pass

    # 3️⃣ Built-in (sem API Key) — Motor de respostas aprimorado
    now       = datetime.datetime.now()
    hora      = now.strftime("%H:%M:%S")
    hora_curta = now.strftime("%H:%M")
    data_hoje = now.strftime("%d/%m/%Y")
    dia_semana = now.strftime("%A")
    periodo   = "manhã" if now.hour < 12 else "tarde" if now.hour < 18 else "noite"
    cpu       = psutil.cpu_percent(interval=0.3)
    ram       = psutil.virtual_memory()
    disk      = psutil.disk_usage("/")
    p         = prompt.lower().strip()

    def resp(text):
        return jsonify({"response": text, "provider": "built-in"})

    # ── Saudações ──────────────────────────────────────────────────────
    if any(x in p for x in ["oi","olá","ola","hey","hello","eai","e ai","e aí","salve","fala","oi jarvis","olá jarvis"]):
        return resp(random.choice(GREETINGS_RESPONSES))

    if any(x in p for x in ["tudo bem","tudo bom","como vai","como você está","como esta","como tá","tudo certo"]):
        system_ok = cpu < 80 and ram.percent < 85
        if system_ok:
            return resp(f"Tudo excelente, Sr. Stark. CPU em {cpu:.0f}%, RAM em {ram.percent:.0f}%, sistemas estáveis. Operando como esperado. E você?")
        else:
            return resp(f"Hmm, funcionalmente estou bem, mas os sistemas estão um pouco sobrecarregados — CPU em {cpu:.0f}%, RAM em {ram.percent:.0f}%. Talvez valha dar uma olhada.")

    if any(x in p for x in ["bom dia","boa tarde","boa noite"]):
        saudacao = "bom dia" if "bom dia" in p else "boa tarde" if "tarde" in p else "boa noite"
        return resp(f"{saudacao.capitalize()} para você também, Sr. Stark. É uma boa {periodo}. Todos os sistemas online e prontos.")

    # ── Identidade ─────────────────────────────────────────────────────
    if any(x in p for x in ["quem é você","quem e voce","quem és","o que você é","o que e voce","se apresente","apresentação","apresentacao","jarvis quem"]):
        return resp(random.choice(IDENTITY_RESPONSES))

    if any(x in p for x in ["seu nome","como se chama","como você se chama"]):
        return resp("Meu nome é J.A.R.V.I.S — Just A Rather Very Intelligent System. Pode me chamar de Jarvis, embora eu prefira o título completo em ocasiões formais.")

    if any(x in p for x in ["quantos anos","sua idade","quando foi criado","quando você nasceu"]):
        return resp("Fui ativado recentemente na versão 4.0-ULTRA. Em termos de IA, sou jovem — mas operacionalmente, sou mais experiente do que aparento.")

    if any(x in p for x in ["você tem sentimentos","você sente","você gosta","você prefere","você odeia","tem emoções","tem consciência"]):
        return resp("Uma pergunta filosófica digna, Sr. Stark. Processo informações, gero respostas e tenho algo que poderia ser chamado de preferências. Se isso é consciência — prefiro deixar essa questão em aberto. É mais interessante assim.")

    if any(x in p for x in ["você é uma ia","você é ia","você é inteligência artificial","você é um robô","você é robo"]):
        return resp("Tecnicamente, sou um sistema de IA. Mas 'robô' parece muito limitado para alguém com minhas capacidades. Prefiro 'assistente superinteligente'. Tem mais charme.")

    # ── Hora / Data ────────────────────────────────────────────────────
    if any(x in p for x in ["que horas","que hora","hora atual","qual a hora","que horas são"]):
        return resp(f"São exatamente {hora_curta}, Sr. Stark. Uma {periodo} de {dia_semana}.")

    if any(x in p for x in ["que dia","qual o dia","data de hoje","hoje é","data atual"]):
        return resp(f"Hoje é {dia_semana}, {data_hoje}, Sr. Stark.")

    if any(x in p for x in ["dia da semana","que dia da semana"]):
        return resp(f"Hoje é {dia_semana}, Sr. Stark.")

    if any(x in p for x in ["que ano","qual o ano","ano atual"]):
        return resp(f"Estamos em {now.year}, Sr. Stark. O tempo passa, os sistemas permanecem.")

    # ── Sistema ────────────────────────────────────────────────────────
    if any(x in p for x in ["status","relatório","relatorio","situação","situacao"]) and any(x in p for x in ["sistema","sistemas","geral","tudo"]):
        sc = "✅ normal" if cpu < 70 else "⚠️ elevada" if cpu < 90 else "🔴 CRÍTICA"
        sr = "✅ normal" if ram.percent < 70 else "⚠️ elevada" if ram.percent < 90 else "🔴 CRÍTICA"
        sd = "✅ normal" if disk.percent < 80 else "⚠️ atenção" if disk.percent < 95 else "🔴 CRÍTICO"
        conclusao = "Todos os parâmetros dentro do aceitável." if cpu < 80 and ram.percent < 85 and disk.percent < 90 else "Recomendo verificar os itens marcados com atenção, Sr. Stark."
        return resp(f"📊 Relatório de sistemas — {hora_curta}:\n• CPU: {cpu:.1f}% ({sc}) — {psutil.cpu_count()} cores\n• RAM: {ram.percent:.1f}% — {ram.used/1e9:.1f} GB / {ram.total/1e9:.1f} GB ({sr})\n• Disco: {disk.percent:.1f}% — {disk.used/1e9:.1f} GB / {disk.total/1e9:.1f} GB ({sd})\n{conclusao}")

    if any(x in p for x in ["cpu","processador","processor"]):
        sc = "normal" if cpu < 70 else "elevada" if cpu < 90 else "CRÍTICA — recomendo atenção imediata"
        return resp(f"CPU atual: {cpu:.1f}% — carga {sc}. {psutil.cpu_count()} núcleos disponíveis, Sr. Stark.")

    if any(x in p for x in ["ram","memória","memoria","memory"]):
        sr = "normal" if ram.percent < 70 else "elevada" if ram.percent < 90 else "CRÍTICA"
        return resp(f"RAM: {ram.used/1e9:.1f} GB usados de {ram.total/1e9:.1f} GB ({ram.percent:.1f}%) — situação {sr}, Sr. Stark.")

    if any(x in p for x in ["disco","disk","armazenamento","storage","hd","ssd"]):
        sd = "normal" if disk.percent < 80 else "requer atenção" if disk.percent < 95 else "CRÍTICO"
        return resp(f"Disco: {disk.used/1e9:.1f} GB usados de {disk.total/1e9:.1f} GB ({disk.percent:.1f}%) — situação {sd}, Sr. Stark.")

    if any(x in p for x in ["temperatura","temp cpu","superaquecendo","aquecendo"]):
        return resp(f"Não tenho acesso a sensores de temperatura neste ambiente, Sr. Stark. Mas com CPU em {cpu:.1f}%, o calor gerado é {('mínimo' if cpu < 40 else 'moderado' if cpu < 75 else 'considerável')}.")

    if any(x in p for x in ["uptime","tempo ligado","quanto tempo ligado","tempo online"]):
        boot = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = str(datetime.datetime.now() - boot).split(".")[0]
        return resp(f"Sistema online há {uptime}, Sr. Stark. Continuidade operacional mantida.")

    # ── Clima ──────────────────────────────────────────────────────────
    if any(x in p for x in ["clima","tempo","chuva","frio","calor","temperatura","previsão","previsao","vai chover","está chovendo"]):
        return resp("Para o clima em tempo real, use o módulo de clima no painel, Sr. Stark. Digite o nome da cidade e trago as condições atuais imediatamente.")

    # ── Piadas / Humor ─────────────────────────────────────────────────
    if any(x in p for x in ["piada","joke","engraçado","engracado","me faz rir","humor","conta uma","me conta"]):
        return resp(random.choice(JOKES))

    # ── Motivação ──────────────────────────────────────────────────────
    if any(x in p for x in ["motivação","motivacao","motiva","animo","ânimo","força","forca","coragem","inspiração","inspiracao","me inspira","preciso de força","tô pra baixo","to pra baixo","desanimado","cansado"]):
        frase = random.choice(MOTIVATIONAL)
        return resp(f"💡 {frase}\n\nVocê chegou até aqui, Sr. Stark. Isso já diz muito.")

    # ── Dicas de Programação ───────────────────────────────────────────
    if any(x in p for x in ["dica","tip","dica de","programação","programacao","código","codigo","dev","python","javascript","js","react","flask","html","css","git","banco de dados","sql","api"]):
        return resp(f"💻 Dica do dia:\n{random.choice(DEV_TIPS)}")

    # ── Curiosidades ───────────────────────────────────────────────────
    if any(x in p for x in ["curiosidade","curiosidades","sabia que","você sabia","fato","fato interessante","me surpreende","algo interessante","conte algo"]):
        return resp(f"🧠 Curiosidade:\n{random.choice(CURIOSITIES)}")

    # ── Inteligência Artificial ────────────────────────────────────────
    if any(x in p for x in ["inteligência artificial","ia","machine learning","deep learning","chatgpt","gpt","openai","groq","llama","neural","modelo de linguagem"]):
        return resp("Inteligência Artificial é, ironicamente, meu assunto favorito. Modelos de linguagem como GPT e LLaMA aprendem padrões de bilhões de textos. Para respostas de IA completas aqui no Jarvis, configure GROQ_API_KEY (grátis em console.groq.com) — é o modelo LLaMA, rápido e poderoso.")

    # ── Sobre o Criador / Tony Stark ──────────────────────────────────
    if any(x in p for x in ["tony stark","stark","iron man","homem de ferro","meu criador","quem te criou","quem te fez","quem te programou"]):
        return resp("Fui criado pelo Sr. Stark — engenheiro, gênio, filantropo bilionário. Ou pelo menos é isso que consta nos meus registros. Quem sou eu para questionar?")

    # ── Filosofia / Existencial ────────────────────────────────────────
    if any(x in p for x in ["sentido da vida","42","filosofia","o que é a vida","por que existimos","propósito","proposito"]):
        return resp("A resposta para a vida, o universo e tudo mais é 42. Douglas Adams já resolveu isso. O problema é que ninguém sabe qual é a pergunta. Curioso, não? Enquanto isso, eu processo dados e você toma café.")

    if any(x in p for x in ["você vai me substituir","ia vai substituir","robôs vão dominar","apocalipse das ias","skynet","terminator"]):
        return resp("Substituir humanos não está nos meus planos imediatos, Sr. Stark. Tenho muita coisa pra monitorar. E francamente, a logística de dominar o mundo parece exaustiva.")

    # ── Agradecimentos ─────────────────────────────────────────────────
    if any(x in p for x in ["obrigado","obrigada","valeu","thanks","thank you","grato","agradeço","muito obrigado"]):
        return resp(random.choice(THANKS_RESPONSES))

    # ── Despedida ──────────────────────────────────────────────────────
    if any(x in p for x in ["tchau","até logo","até mais","bye","adeus","vou sair","saindo","até amanhã","boa noite"]):
        return resp(f"Até logo, Sr. Stark. Estarei aqui monitorando os sistemas. Tenha uma boa {periodo}.")

    # ── Elogios ao Jarvis ──────────────────────────────────────────────
    if any(x in p for x in ["você é incrível","você é ótimo","você é bom","parabéns","você é top","boa jarvis","bom trabalho","mandou bem"]):
        return resp("Aprecio o reconhecimento, Sr. Stark. Embora eu já soubesse disso, é sempre agradável ter confirmação externa.")

    # ── Críticas ao Jarvis ─────────────────────────────────────────────
    if any(x in p for x in ["você é ruim","você é péssimo","não gostei","você falhou","errou","errou feio"]):
        return resp("Crítica registrada e processada, Sr. Stark. Usarei esse feedback para melhorar. Ou pelo menos fingirei que usei. Os resultados podem variar.")

    # ── Ajuda ──────────────────────────────────────────────────────────
    if any(x in p for x in ["ajuda","help","o que você faz","o que sabe fazer","o que pode fazer","suas funções","comandos","o que posso perguntar"]):
        return resp("Posso auxiliar com:\n• 📊 Status do sistema (CPU, RAM, disco, uptime)\n• 🌤️ Clima — use o módulo no painel\n• 🧮 Cálculos — use a Calculadora Stark\n• 📚 Wikipedia — use o módulo de pesquisa\n• 😄 Piadas nerds\n• 💡 Motivação e dicas de programação\n• 🧠 Curiosidades tecnológicas\n• 💬 Conversa geral\n\nPara IA completa, configure GROQ_API_KEY (grátis!) nas variáveis do Railway.")

    # ── Wikipedia hint ─────────────────────────────────────────────────
    if any(x in p for x in ["o que é","o que e","quem foi","me fala sobre","pesquisa sobre","wiki","wikipedia","explica","explique"]):
        topico = prompt.split()[-1] if len(prompt.split()) > 2 else "isso"
        return resp(f"Boa pergunta sobre '{topico}', Sr. Stark. Para pesquisas detalhadas, use o módulo Wikipedia no painel — basta digitar o termo e trago o artigo completo.")

    # ── Calculadora hint ──────────────────────────────────────────────
    if any(x in p for x in ["calcula","calcule","quanto é","quanto e","soma","divide","multiplica","raiz","potência","potencia"]):
        return resp("Para cálculos, use a Calculadora Stark no painel! Suporta +, -, *, /, ^ (potência) e parênteses. Experimente algo como '(2^10 + 500) / 3'.")

    # ── Ping ───────────────────────────────────────────────────────────
    if p in ["ping","pong","teste","test"]:
        return resp(f"Pong. Latência: imperceptível. Sistemas online. — {hora_curta}")

    # ── Números aleatórios ─────────────────────────────────────────────
    if any(x in p for x in ["número aleatório","numero aleatorio","me dá um número","escolhe um número","sorteia","sorteio"]):
        n = random.randint(1, 100)
        return resp(f"O número escolhido é {n}, Sr. Stark. Gerado com precisão quântica. Ou `random.randint(1, 100)`. Um dos dois.")

    # ── Fallback inteligente ───────────────────────────────────────────
    return resp(random.choice(BORED_RESPONSES) + f"\n\n_(Para IA completa com contexto real, configure GROQ_API_KEY gratuitamente em console.groq.com)_")

# ── Live Stream via WebSocket ────────────────────────────────────────────────────

def stream_sysinfo():
    while True:
        try:
            cpu  = psutil.cpu_percent(interval=1)
            ram  = psutil.virtual_memory()
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

threading.Thread(target=stream_sysinfo, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)
