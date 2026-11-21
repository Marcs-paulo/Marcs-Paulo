#!/usr/bin/env python3
"""
Desenha os cartoes do README do perfil como SVGs animados em cards/.

Visual: preto e verde (o verde #60c460 e o mesmo da identidade da SIS), com
Instrument Serif nos titulos, Geist no texto e Geist Mono nos rotulos.

Cada cartao e um SVG mostrado por <img>, entao so pode usar o que o GitHub
permite ali: CSS com animacao, SMIL e fontes embutidas em data URI (sem JS e
sem buscar nada de fora). As fontes ficam em fonts/ (SIL OFL).

Os numeros vivos vem de data/contribuicoes.json (buscar_contribuicoes.py).
O retrato vem de data/retrato.txt (retrato_ascii.py, rodado so uma vez).
O workflow .github/workflows/atualizar-perfil.yml roda tudo todo dia.

    python scripts/gerar_cartoes.py        # ESTATICO=1 para ver tudo parado
"""
import base64
import datetime
import json
import os
import re
from html import escape

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
DADOS = os.path.join(RAIZ, "data", "contribuicoes.json")
RETRATO = os.path.join(RAIZ, "data", "retrato.txt")
SAIDA = os.path.join(RAIZ, "cards")
FONTES = os.path.join(RAIZ, "fonts")
USUARIO = "Marcs-paulo"
ESTATICO = bool(os.environ.get("ESTATICO"))

# ---- paleta -----------------------------------------------------------------
PRETO = "#070a07"        # fundo dos cartoes
PAINEL = "#0d140d"       # fundo levemente mais claro
LINHA = "#1c2b1c"        # bordas e divisorias
TEXTO = "#e9f3e9"
TEXTO_2 = "#b3c6b3"
APAGADO = "#6c836c"
VERDE = "#60c460"        # verde SIS (96,196,96)
VERDE_VIVO = "#9cf09c"
VERDE_MEIO = "#2f7a2f"
VERDE_FUNDO = "#123312"
W = 880                  # largura da coluna do README no GitHub

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, -apple-system, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

ARQ_FONTES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}

CSS = """
@keyframes sobe{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes surge{from{opacity:0}to{opacity:1}}
@keyframes cresce{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes estoura{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes pisca{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes cutuca{0%,100%{transform:none}50%{transform:translateX(4px)}}
@keyframes diagonal{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}
@keyframes entra{0%{opacity:0;transform:translateY(80px) scale(.6) rotate(-8deg)}55%{opacity:1;transform:translateY(-10px) scale(1.05) rotate(2deg)}78%{transform:translateY(3px) scale(.98)}100%{opacity:1;transform:none}}
@keyframes desliza{from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:none}}
@keyframes rola{from{transform:translateY(60px)}to{transform:none}}
@keyframes brilho{0%{transform:translateX(-260px) skewX(-20deg)}22%,100%{transform:translateX(420px) skewX(-20deg)}}
@keyframes onda{0%{opacity:.7;transform:scale(.2)}100%{opacity:0;transform:scale(2.4)}}
@keyframes varre{0%{transform:translateY(-40px)}100%{transform:translateY(460px)}}
.s{opacity:0;animation:sobe .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:surge .9s ease-out both}
.c{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:cresce .8s cubic-bezier(.2,.7,.2,1) both}
.e{opacity:0;transform-box:fill-box;transform-origin:center;animation:estoura .4s ease-out both}
.vivo{animation:pisca 1.6s ease-in-out infinite}
.cu{transform-box:fill-box;animation:cutuca 1.8s ease-in-out infinite}
.dg{transform-box:fill-box;animation:diagonal 1.8s ease-in-out infinite}
.en{opacity:0;transform-box:fill-box;transform-origin:50% 60%;animation:entra 1.1s cubic-bezier(.2,.8,.2,1) both}
.dz{opacity:0;transform-box:fill-box;animation:desliza .6s cubic-bezier(.2,.7,.2,1) both}
.ro{transform-box:fill-box;animation:rola .8s cubic-bezier(.15,.8,.2,1) both}
.br{animation:brilho 5s ease-in-out infinite}
.on{opacity:0;transform-box:fill-box;transform-origin:center;animation:onda 1s ease-out both}
.vr{animation:varre 6s linear infinite}
@media (prefers-reduced-motion: reduce){.s,.f,.c,.e,.vivo,.cu,.dg,.en,.dz,.ro,.on{animation:none!important;opacity:1!important;transform:none!important}.br,.on,.vr{display:none}}
"""
PARADO = (".s,.f,.c,.e,.vivo,.cu,.dg,.en,.dz,.ro{animation:none!important;opacity:1!important;"
          "transform:none!important}.br,.on,.vr{display:none}")

ESPACO = 12              # espaco entre cartoes, embutido nos SVGs


def fontes(chaves):
    css = []
    for k in chaves:
        fam, estilo, peso, arq = ARQ_FONTES[k]
        b64 = base64.b64encode(open(os.path.join(FONTES, arq), "rb").read()).decode()
        css.append(f"@font-face{{font-family:'{fam}';font-style:{estilo};font-weight:{peso};"
                   f"src:url(data:font/woff;base64,{b64}) format('woff')}}")
    return "".join(css)


def svg(w, h, corpo, chaves, rotulo, esq=0, dir_=0, baixo=ESPACO):
    """Cartao w x h desenhado em x=esq num canvas transparente; as margens fazem as linhas encaixarem."""
    if esq:
        corpo = f'<g transform="translate({esq:.3f} 0)">{corpo}</g>'
    w, h = w + esq + dir_, h + baixo
    css = fontes(chaves) + CSS + (PARADO if ESTATICO else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" viewBox="0 0 {w:.3f} {h}" '
            f'role="img" aria-label="{escape(rotulo)}"><title>{escape(rotulo)}</title>'
            f"<style>{css}</style>{corpo}</svg>")


def grava(nome, conteudo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), "w") as f:
        f.write(conteudo)
    print(f"gravado cards/{nome} ({len(conteudo) // 1024} KB)")


def atraso(s):
    return f'style="animation-delay:{s:.2f}s"'


def quebra(texto, n):
    linhas, linha = [], ""
    for p in texto.split():
        if linha and len(linha) + 1 + len(p) > n:
            linhas.append(linha)
            linha = p
        else:
            linha = f"{linha} {p}".strip()
    return linhas + [linha] if linha else linhas


def linhas_texto(x, y, linhas, alt, attrs):
    return "".join(f'<text x="{x}" y="{y + i * alt}" {attrs}>{escape(l)}</text>' for i, l in enumerate(linhas))


def fundo(w, h, rx=14):
    return (f'<rect width="{w}" height="{h}" rx="{rx}" fill="{PRETO}"/>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="none" stroke="{LINHA}"/>')


# ---- 1 · capa com o retrato ----------------------------------------------------
def capa():
    h = 420
    linhas = open(RETRATO).read().splitlines()
    colunas = max(len(l) for l in linhas)
    cel_l = 800 / colunas
    cel_a = cel_l * 15 / 8
    retrato = []
    for i, l in enumerate(linhas):
        if not l.strip():
            continue
        retrato.append(
            f'<text class="f" style="animation-delay:{0.25 + i * 0.022:.3f}s;animation-duration:.35s" '
            f'xml:space="preserve" x="0" y="{i * cel_a + cel_a * 0.74:.1f}" fill="{VERDE}" '
            f'font-size="{cel_a * 0.86:.1f}" textLength="{len(l) * cel_l:.1f}" lengthAdjust="spacing">'
            f'{escape(l)}</text>')
    escala = 0.43
    alt_arte = len(linhas) * cel_a * escala
    corpo = f"""
<defs>
  <linearGradient id="reflexo" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="600" y2="0">
    <stop offset="0" stop-color="{VERDE}"/><stop offset=".42" stop-color="{VERDE}"/>
    <stop offset=".5" stop-color="{VERDE_VIVO}"/><stop offset=".58" stop-color="{VERDE}"/>
    <stop offset="1" stop-color="{VERDE}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-600 0;600 0;600 0"
      keyTimes="0;.45;1" dur="7s" begin="1.6s" repeatCount="indefinite"/>
  </linearGradient>
  <radialGradient id="aura" cx=".5" cy=".45" r=".5">
    <stop offset="0" stop-color="{VERDE}" stop-opacity=".16"/><stop offset="1" stop-color="{VERDE}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="grade" width="22" height="22" patternUnits="userSpaceOnUse">
    <path d="M22 0H0V22" fill="none" stroke="{VERDE}" stroke-opacity=".05"/>
  </pattern>
  <linearGradient id="feixe" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{VERDE}" stop-opacity="0"/><stop offset="1" stop-color="{VERDE}" stop-opacity=".10"/>
  </linearGradient>
  <clipPath id="caixa"><rect width="{W}" height="{h}" rx="14"/></clipPath>
</defs>
{fundo(W, h)}
<g clip-path="url(#caixa)">
  <rect width="{W}" height="{h}" fill="url(#grade)"/>
  <ellipse cx="690" cy="215" rx="230" ry="210" fill="url(#aura)"/>
  <rect class="vr" x="500" y="0" width="380" height="40" fill="url(#feixe)"/>
</g>
<g class="f" {atraso(0)}>
  <rect class="vivo" x="48" y="49" width="8" height="8" rx="2" fill="{VERDE}"/>
  <text x="66" y="57" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{APAGADO}">ENGENHARIA DE COMPUTAÇÃO · UFRN</text>
</g>
<text class="s" {atraso(0.15)} x="44" y="168" font-family="{SERIF}" font-size="92" letter-spacing="-2" fill="{TEXTO}">Marcos Paulo</text>
<text class="s" {atraso(0.3)} x="44" y="250" font-family="{SERIF}" font-style="italic" font-size="70" letter-spacing="-1.5" fill="url(#reflexo)">Dantas Joaquim</text>
<g class="s" {atraso(0.55)}>
  {linhas_texto(48, 304, ["Hoje: firmware ESP32 e app da SIS, irrigação", "que decide quando regar sem internet."], 27, f'font-family="{SANS}" font-size="18" fill="{TEXTO_2}"')}
</g>
<g class="f" {atraso(0.8)}>
  <text x="48" y="384" font-family="{MONO}" font-size="13" fill="{TEXTO}">Natal/RN · embarcados &amp; IoT</text>
  <text class="dg" x="266" y="384" font-family="{MONO}" font-size="13" fill="{VERDE}">&#8599;</text>
</g>
<g transform="translate(520 {(h - alt_arte) / 2:.1f}) scale({escala})" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  {''.join(retrato)}
</g>
"""
    grava("capa.svg", svg(W, h, corpo, ["serif", "serif-i", "sans", "mono"],
                          "Marcos Paulo Dantas Joaquim. Engenharia de Computação na UFRN. "
                          "Hoje: firmware ESP32 e app da SIS, irrigação que decide quando regar sem internet."))


# ---- 2 · tres frentes ----------------------------------------------------------
BLOCO_W, BLOCO_H = W / 3 - 8, 210


def conta(num, palavra, x, y, attrs, inicio, dur=1.1, quadros=18):
    """Numero sobe de 0 ate o valor com quadros <set> do SMIL (funciona dentro de <img>)."""
    m = re.match(r"([\d.]+)(.*)", num)
    if not m:  # texto (ex.: UFRN): aparece sem contar
        return f'<text x="{x}" y="{y}" {attrs}>{escape(num)} <tspan font-style="italic">{escape(palavra)}</tspan></text>'
    val, suf = float(m.group(1)), m.group(2)
    casas = len(m.group(1).split(".")[1]) if "." in m.group(1) else 0
    cauda = f' <tspan font-style="italic">{escape(palavra)}</tspan>'
    if ESTATICO:
        return f'<text x="{x}" y="{y}" {attrs}>{escape(num)}{cauda}</text>'
    out = []
    for i in range(quadros + 1):
        e = 1 - (1 - i / quadros) ** 3
        txt = num if i == quadros else f"{val * e:.{casas}f}{suf}"
        liga = inicio + dur * i / quadros
        desliga = "" if i == quadros else \
            f'<set attributeName="opacity" to="0" begin="{inicio + dur * (i + 1) / quadros:.3f}s"/>'
        out.append(f'<text x="{x}" y="{y}" {attrs} opacity="0">{escape(txt)}{cauda}'
                   f'<set attributeName="opacity" to="1" begin="{liga:.3f}s"/>{desliga}</text>')
    return "".join(out)


def bloco(nome, rotulo, cor, tinta, borda, num, palavra, texto, inicio, pos):
    linhas = quebra(texto, 34)
    corpo_txt = "".join(
        f'<text class="s" {atraso(inicio + 0.75 + i * 0.1)} x="24" y="{150 + i * 20}" font-family="{SANS}" '
        f'font-size="14" fill="{tinta}" opacity=".9">{escape(l)}</text>' for i, l in enumerate(linhas))
    contorno = f'<rect x=".75" y=".75" width="{BLOCO_W - 1.5}" height="{BLOCO_H - 1.5}" rx="13.5" fill="none" stroke="{borda}" stroke-width="1.5"/>' if borda else ""
    corpo = f"""
<defs>
  <clipPath id="card"><rect width="{BLOCO_W}" height="{BLOCO_H}" rx="14"/></clipPath>
  <clipPath id="fenda"><rect x="0" y="62" width="{BLOCO_W}" height="62"/></clipPath>
  <linearGradient id="vidro" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g class="en" {atraso(inicio)}>
  <g clip-path="url(#card)">
    <rect width="{BLOCO_W}" height="{BLOCO_H}" fill="{cor}"/>
    <circle class="on" {atraso(inicio + 0.5)} cx="{BLOCO_W - 40}" cy="{BLOCO_H - 40}" r="60" fill="none" stroke="{tinta}" stroke-opacity=".45" stroke-width="2"/>
    <rect class="br" style="animation-delay:{inicio + 1.4:.2f}s" x="0" y="-20" width="90" height="{BLOCO_H + 40}" fill="url(#vidro)" transform="translate(-260 0)"/>
  </g>
  {contorno}
  <text class="dz" {atraso(inicio + 0.35)} x="24" y="38" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{tinta}">{rotulo}</text>
  <g class="dz" {atraso(inicio + 0.5)}><text class="cu" style="animation-delay:{inicio + 1.3:.2f}s" x="250" y="38" font-family="{MONO}" font-size="14" fill="{tinta}">&#8594;</text></g>
  <g clip-path="url(#fenda)"><g class="ro" {atraso(inicio + 0.45)}>
    {conta(num, palavra, 22, 110, f'font-family="{SERIF}" font-size="40" fill="{tinta}"', inicio + 0.45)}
  </g></g>
  {corpo_txt}
</g>
"""
    grava(f"{nome}.svg", svg(BLOCO_W, BLOCO_H, corpo, ["serif", "serif-i", "sans", "mono"],
                             f"{rotulo}: {num} {palavra}. {texto}", esq=4 * pos, dir_=8 - 4 * pos))


# ---- 3 · atividade (barras por mes) ---------------------------------------------
MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()


def atividade(d):
    h = 340
    meses = d["meses"][-12:]
    melhor = max(meses[:-1] or meses, key=lambda m: m["total"])
    topo = max(melhor["total"], 1)
    x0, x1, base, alt_max, vao = 40, 600, 292, 140, 10
    bw = (x1 - x0 - vao * (len(meses) - 1)) / len(meses)
    barras = []
    for i, m in enumerate(meses):
        parcial = i == len(meses) - 1
        destaque = m is melhor
        bh = max(4, round(min(m["total"], topo) / topo * alt_max))
        x = x0 + i * (bw + vao)
        cor = VERDE if destaque else (LINHA if parcial else VERDE_MEIO)
        nome = MESES[int(m["mes"][5:]) - 1]
        a = 2.2 + i * 0.07
        barras.append(
            f'<rect class="c" style="animation-delay:{a:.2f}s" x="{x:.1f}" y="{base - bh}" width="{bw:.1f}" '
            f'height="{bh}" rx="4" fill="{cor}"><title>{nome}: {m["total"]}</title></rect>'
            f'<text class="f" style="animation-delay:{a:.2f}s" x="{x + bw / 2:.1f}" y="{base + 22}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{APAGADO}">{nome}</text>')
        if destaque:
            barras.append(f'<text class="e" style="animation-delay:3.2s" x="{x + bw / 2:.1f}" y="{base - bh - 10}" '
                          f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{VERDE}">{m["total"]}</text>')
    atual, maior = d["sequencia_atual"], d["maior_sequencia"]
    if atual and atual >= maior:
        seq = (f'{atual} <tspan font-style="italic">dias</tspan>', "de sequência agora, e a maior")
    elif atual:
        seq = (f'{atual} <tspan font-style="italic">dias</tspan>', f"de sequência agora, a maior foi {maior}")
    else:
        seq = (f'{maior} <tspan font-style="italic">dias</tspan>', "na maior sequência do ano")
    numeros = [
        seq,
        (f'{d["dias_ativos"]}<tspan fill="{APAGADO}"> / {len(d["dias"])}</tspan>', "dias com contribuição"),
        (f'{d["melhor_dia"]["total"]}', "no dia mais cheio"),
    ]
    lado = []
    for i, (grande, pequeno) in enumerate(numeros):
        y = 104 + i * 92
        lado.append(f'<g class="s" {atraso(2.6 + i * 0.15)}>'
                    f'<text x="650" y="{y}" font-family="{SERIF}" font-size="40" fill="{TEXTO}">{grande}</text>'
                    f'<text x="650" y="{y + 24}" font-family="{SANS}" font-size="13" fill="{APAGADO}">{pequeno}</text></g>')
        if i < 2:
            lado.append(f'<rect class="f" {atraso(2.6)} x="650" y="{y + 44}" width="190" height="1" fill="{LINHA}"/>')
    corpo = f"""
{fundo(W, h)}
<text class="f" {atraso(1.9)} x="40" y="58" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{APAGADO}">OS ÚLTIMOS 12 MESES NO GITHUB</text>
<text class="s" {atraso(2.0)} x="38" y="114" font-family="{SERIF}" font-size="52" fill="{TEXTO}">{d["total"]:,} <tspan font-style="italic" fill="{VERDE}">contribuições</tspan></text>
{''.join(barras)}
{''.join(lado)}
"""
    grava("atividade.svg", svg(W, h, corpo, ["serif", "serif-i", "sans", "mono"],
                               f'{d["total"]} contribuições nos últimos 12 meses'))


# ---- 4 · stack ---------------------------------------------------------------------
STACK = [
    ("HARDWARE & FIRMWARE", ["C++", "ESP-IDF", "ESP32-S3", "PlatformIO", "LoRa", "BLE", "Linux"]),
    ("APPS & WEB", ["TypeScript", "React Native", "Flutter", "Tauri", "Rust", "Go", "PHP"]),
    ("DADOS & INFRA", ["Python", "PostgreSQL", "SQLite", "Supabase", "Firebase", "Delphi/Firebird"]),
]


def stack():
    linhas = []
    y, n = 112, 0
    for i, (titulo, itens) in enumerate(STACK):
        linhas.append(f'<text class="dz" {atraso(5.0 + i * 0.12)} x="40" y="{y + 5}" font-family="{MONO}" '
                      f'font-size="11" letter-spacing="1" fill="{APAGADO}">{escape(titulo)}</text>')
        x = 210
        for item in itens:
            larg = 22 + len(item) * 7.5
            if x + larg > W - 36:  # nao cabe: continua na linha de baixo
                x, y = 210, y + 38
            linhas.append(
                f'<g class="e" {atraso(5.1 + n * 0.04)}><rect x="{x}" y="{y - 14}" width="{larg:.0f}" height="28" rx="14" '
                f'fill="{VERDE_FUNDO if i != 1 else PAINEL}" stroke="{VERDE_MEIO}"/>'
                f'<text x="{x + larg / 2:.1f}" y="{y + 4.5}" text-anchor="middle" font-family="{MONO}" font-size="13" '
                f'fill="{VERDE_VIVO if i != 1 else TEXTO}">{escape(item)}</text></g>')
            x += larg + 8
            n += 1
        y += 52
    h = y + 16
    corpo = f"""
{fundo(W, h)}
<text class="s" {atraso(4.8)} x="40" y="62" font-family="{SERIF}" font-size="34" fill="{TEXTO}">Ferramentas <tspan font-style="italic" fill="{VERDE}">do dia a dia</tspan></text>
{''.join(linhas)}
"""
    grava("stack.svg", svg(W, h, corpo, ["serif", "serif-i", "mono"],
                           "Stack: " + "; ".join(f"{t}: {', '.join(i)}" for t, i in STACK)))


# ---- 5 · repositorios ---------------------------------------------------------------
REPO_W, REPO_H = W / 3 - 8, 176
# (nome, descricao, linha de baixo, repositorio publico para contar estrelas ou None)
REPOS = [
    ("SIS", "Irrigação por gotejamento que decide a rega sozinha, sem internet. Sou cofundador.",
     "C++ · ESP32 · Flutter", None),
    ("NaraEdu", "Boneca com ESP32-S3 que registra ocorrências da sala por voz e gesto. Laboratório TEAM.",
     "C++ · ESP32-S3 · API", None),
    ("NeuroBeep", "Crianças com limitação motora guiam um robô por neurofeedback. Cuido do firmware.",
     "C++ · JavaScript · BLE", "NeuroBeep"),
]
CORES_REPO = [VERDE, VERDE_VIVO, VERDE_MEIO]


def cartao_repo(i, nome, desc, linha, estrelas):
    a = 4.6 + i * 0.12
    meta = f"{linha}  ·  ★ {estrelas}" if estrelas else linha
    corpo = f"""
{fundo(REPO_W, REPO_H)}
<g class="s" {atraso(a)}>
  <rect x="24" y="30" width="8" height="8" rx="2" fill="{CORES_REPO[i]}"/>
  <text x="40" y="39" font-family="{SANS}" font-weight="600" font-size="18" fill="{TEXTO}">{escape(nome)}</text>
  {linhas_texto(24, 72, quebra(desc, 34), 21, f'font-family="{SANS}" font-size="14" fill="{TEXTO_2}"')}
  <text x="24" y="{REPO_H - 24}" font-family="{MONO}" font-size="12" fill="{APAGADO}">{escape(meta)}</text>
</g>
"""
    grava(f"repo-{nome}.svg", svg(REPO_W, REPO_H, corpo, ["sans", "sans-b", "mono"], f"{nome}: {desc}",
                                  esq=4 * i, dir_=8 - 4 * i))


def titulo_secao(texto, italico, tema):
    cor = TEXTO if tema == "escuro" else PRETO
    corpo = (f'<text class="s" {atraso(4.4)} x="2" y="46" font-family="{SERIF}" font-size="34" fill="{cor}">'
             f'{escape(texto)} <tspan font-style="italic" fill="{VERDE if tema == "escuro" else VERDE_MEIO}">'
             f'{escape(italico)}</tspan></text>')
    grava(f"titulo-codando-{tema}.svg", svg(W, 64, corpo, ["serif", "serif-i"], f"{texto} {italico}", baixo=0))


# ---- 6 · grafico de contribuicoes em verde ------------------------------------------
TONS = ["#111a11", "#173d17", "#21612a", "#2f8a36", VERDE, VERDE_VIVO]


def nivel(c):
    return 0 if c == 0 else 1 if c <= 2 else 2 if c <= 5 else 3 if c <= 10 else 4 if c <= 20 else 5


def grafico(d):
    dias = d["dias"]
    primeiro = datetime.date.fromisoformat(dias[0]["data"])
    sobra = (primeiro.weekday() + 1) % 7  # domingo = 0
    cel, passo, gx, gy = 12, 15, 44, 96
    celulas, meses, vistos = [], [], set()
    for i, dia in enumerate(dias):
        col, lin = divmod(i + sobra, 7)
        data = datetime.date.fromisoformat(dia["data"])
        if data.day <= 7 and lin == 0 and (data.year, data.month) not in vistos:
            vistos.add((data.year, data.month))
            meses.append((col, MESES[data.month - 1]))
        c = dia["total"]
        celulas.append(
            f'<rect class="e" style="animation-delay:{1.0 + col * 0.03 + lin * 0.02:.2f}s" x="{gx + col * passo}" '
            f'y="{gy + lin * passo}" width="{cel}" height="{cel}" rx="3" fill="{TONS[nivel(c)]}">'
            f'<title>{dia["data"]}: {c} contribuição{"ões" if c != 1 else ""}</title></rect>'.replace("contribuiçãoões", "contribuições"))
    ncols = (len(dias) + sobra + 6) // 7
    direita = gx + ncols * passo - 3
    rot = "".join(f'<text x="{gx + col * passo}" y="{gy + 7 * passo + 16}" font-family="{MONO}" font-size="11" '
                  f'fill="{APAGADO}">{m}</text>' for col, m in meses if col < ncols - 12)
    lx = direita - len(TONS) * 14
    legenda = "".join(f'<rect x="{lx + i * 14}" y="{gy + 7 * passo + 6}" width="11" height="11" rx="2.5" fill="{c}"/>'
                      for i, c in enumerate(TONS))
    h = gy + 7 * passo + 44
    corpo = f"""
{fundo(W, h)}
<text class="s" {atraso(0.8)} x="42" y="62" font-family="{SERIF}" font-size="34" fill="{TEXTO}">Todo dia, <tspan font-style="italic" fill="{VERDE}">em verde</tspan></text>
<text class="f" {atraso(0.8)} x="{direita}" y="60" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{APAGADO}">ATUALIZADO TODO DIA</text>
{''.join(celulas)}
<g class="f" {atraso(2.4)}>{rot}
<text x="{lx - 8}" y="{gy + 7 * passo + 16}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{APAGADO}">menos</text>
{legenda}
<text x="{lx + len(TONS) * 14 + 2}" y="{gy + 7 * passo + 16}" font-family="{MONO}" font-size="11" fill="{APAGADO}">mais</text></g>
"""
    grava("grafico.svg", svg(W, h, corpo, ["serif", "serif-i", "mono"],
                             f'Gráfico de contribuições: {d["total"]} no último ano'))


def info_github():
    """Estrelas dos repositorios e total de repositorios publicos; sem rede, segue sem eles."""
    estrelas, publicos = {}, None
    try:
        import requests
        cab = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.environ.get("GITHUB_TOKEN") else {}
        r = requests.get(f"https://api.github.com/users/{USUARIO}", headers=cab, timeout=10)
        if r.ok:
            publicos = r.json().get("public_repos")
        for *_, nome in REPOS:
            if not nome:
                continue
            r = requests.get(f"https://api.github.com/repos/{USUARIO}/{nome}", headers=cab, timeout=10)
            if r.ok:
                estrelas[nome] = r.json().get("stargazers_count", 0)
    except Exception as e:
        print(f"sem dados do GitHub: {e}")
    return estrelas, publicos


if __name__ == "__main__":
    dados = json.load(open(DADOS))
    estrelas, publicos = info_github()
    anos_sis = datetime.date.today().year - 2023
    capa()
    grafico(dados)
    atividade(dados)
    bloco("sis", "IRRIGAÇÃO", VERDE, PRETO, None, str(anos_sis), "anos de SIS",
          "Começou numa feira de ciências em 2023 e virou estágio na Agritech (Brisanet).", 3.1, 0)
    bloco("formacao", "FORMAÇÃO", VERDE_MEIO, TEXTO, None, "UFRN", "+ redes",
          "Engenharia de Computação na UFRN. Antes, técnico em Redes de Computadores.", 3.35, 1)
    bloco("aberto", "CÓDIGO ABERTO", PAINEL, VERDE, VERDE_MEIO, str(publicos or 23), "repositórios",
          "Firmware do robô NeuroBeep, app BLE, automação da bomba d'água e soluções da OBI.", 3.6, 2)
    titulo_secao("O que estou", "codando", "escuro")
    titulo_secao("O que estou", "codando", "claro")
    for i, (nome, desc, linha, repo) in enumerate(REPOS):
        cartao_repo(i, nome, desc, linha, estrelas.get(repo, 0))
    stack()
