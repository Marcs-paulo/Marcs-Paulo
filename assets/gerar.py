# -*- coding: utf-8 -*-
"""Gera o cabecalho e o rodape do perfil, em variante clara e escura.

    python assets/gerar.py

Por que arte propria em vez de servico de terceiro: os cartoes de estatistica
mais copiados em perfis do GitHub responderam 503 na verificacao feita antes
deste README. Servico de terceiro cai, e cai justamente no dia em que alguem
importante abre o perfil. Um SVG versionado aqui nao depende de ninguem.

O motivo grafico nao e decoracao. No painel do hero o pacote de dado desce para
a fila local quando comeca a faixa SEM REDE e volta para a linha quando ela
termina - a frase de abertura do perfil, desenhada.

ATENCAO: edite este script, nunca os .svg. Sao dois arquivos quase identicos
por tema; mexer neles a mao deixa claro e escuro fora de sincronia.
"""

import io
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))

PALETAS = {
    "dark":  dict(bg="#0D1117", painel="#12171F", borda="#30363D",
                  texto="#E6EDF3", fraco="#8B949E", ac="#22C55E",
                  ac2="#6366F1", alerta="#F59E0B", grade="#FFFFFF"),
    "light": dict(bg="#FFFFFF", painel="#F6F8FA", borda="#D0D7DE",
                  texto="#1F2328", fraco="#59636E", ac="#15803D",
                  ac2="#4F46E5", alerta="#B45309", grade="#000000"),
}

FONTE = "'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace"

# O SVG e servido como <img>: nao carrega fonte externa nem executa script.
# Por isso so familias do sistema, e animacao em SMIL.

PAINEL_X = 586


def pilula(x, y, texto, p, largura):
    return u"""  <g>
    <rect x="{x}" y="{y}" width="{w}" height="26" rx="13"
          fill="{ac}" fill-opacity="0.10" stroke="{ac}" stroke-opacity="0.35"/>
    <text x="{tx}" y="{ty}" font-family="{mono}" font-size="12.5"
          fill="{ac}" text-anchor="middle">{t}</text>
  </g>""".format(x=x, y=y, w=largura, tx=x + largura / 2.0, ty=y + 17.5,
                 t=texto, mono=MONO, ac=p["ac"])


def hero(p):
    trilha = ("M604,104 H688 C706,104 706,158 724,158 "
              "H836 C854,158 854,104 872,104 H956")
    pacotes = u""
    for i in range(6):
        pacotes += u"""
    <rect x="-4" y="-4" width="8" height="8" rx="2" fill="{ac}">
      <animateMotion dur="4.4s" begin="{b}s" repeatCount="indefinite"
                     path="{tr}" keyPoints="0;1" keyTimes="0;1" calcMode="linear"/>
      <animate attributeName="opacity" dur="4.4s" begin="{b}s"
               repeatCount="indefinite"
               values="0;1;1;1;1;0" keyTimes="0;0.06;0.4;0.7;0.94;1"/>
    </rect>""".format(ac=p["ac"], b=round(i * 0.72, 2), tr=trilha)

    return u"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 250"
     width="1000" height="250" role="img"
     aria-label="Marcos Paulo Dantas Joaquim - Engenharia de Computacao, UFRN">
  <defs>
    <pattern id="g" width="26" height="26" patternUnits="userSpaceOnUse">
      <circle cx="1.5" cy="1.5" r="1.1" fill="{grade}" fill-opacity="0.07"/>
    </pattern>
    <linearGradient id="fio" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"    stop-color="{ac}" stop-opacity="0"/>
      <stop offset="0.5"  stop-color="{ac}" stop-opacity="1"/>
      <stop offset="1"    stop-color="{ac2}" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <rect width="1000" height="250" rx="16" fill="{bg}"/>
  <rect width="1000" height="250" rx="16" fill="url(#g)"/>
  <rect x="0.5" y="0.5" width="999" height="249" rx="16"
        fill="none" stroke="{borda}"/>

  <!-- identidade -->
  <text x="46" y="82" font-family="{fonte}" font-size="33" font-weight="700"
        fill="{texto}" letter-spacing="-0.6">Marcos Paulo Dantas Joaquim</text>
  <text x="48" y="118" font-family="{mono}" font-size="16" fill="{ac}"
        letter-spacing="0.4">Engenharia de Computa&#231;&#227;o &#183; UFRN</text>
  <text x="48" y="150" font-family="{fonte}" font-size="16.5" fill="{fraco}">
    Sistemas que precisam funcionar quando a infraestrutura falha.
  </text>
{p1}
{p2}
{p3}

  <!-- painel: o padrao que se repete nos projetos -->
  <rect x="586" y="34" width="384" height="182" rx="12"
        fill="{painel}" stroke="{borda}"/>
  <text x="604" y="58" font-family="{mono}" font-size="11.5"
        fill="{fraco}" letter-spacing="1.4">OFFLINE-FIRST</text>

  <!-- janela sem rede -->
  <rect x="688" y="70" width="184" height="126" rx="8"
        fill="{alerta}" fill-opacity="0.09"
        stroke="{alerta}" stroke-opacity="0.45" stroke-dasharray="4 4"/>
  <text x="780" y="88" font-family="{mono}" font-size="11" fill="{alerta}"
        text-anchor="middle" letter-spacing="1">SEM REDE</text>

  <!-- a linha e a fila -->
  <line x1="604" y1="104" x2="956" y2="104" stroke="{borda}" stroke-width="1.5"/>
  <line x1="604" y1="104" x2="956" y2="104" stroke="url(#fio)" stroke-width="2">
    <animate attributeName="stroke-opacity" values="0.25;0.9;0.25"
             dur="3.6s" repeatCount="indefinite"/>
  </line>
  <line x1="724" y1="158" x2="836" y2="158" stroke="{ac}" stroke-width="1.5"
        stroke-opacity="0.35" stroke-dasharray="3 4"/>
  <text x="780" y="178" font-family="{mono}" font-size="11" fill="{fraco}"
        text-anchor="middle">fila local</text>

  <text x="604" y="96" font-family="{mono}" font-size="11" fill="{fraco}">dado</text>
  <text x="956" y="96" font-family="{mono}" font-size="11" fill="{ac}"
        text-anchor="end">sincronizado</text>
{pacotes}

  <!-- nada se perde -->
  <text x="604" y="206" font-family="{fonte}" font-size="12.5" fill="{fraco}">
    A rede cai. Nenhuma leitura se perde.
  </text>
</svg>
""".format(pacotes=pacotes, fonte=FONTE, mono=MONO,
           p1=pilula(48, 172, "C++ / ESP-IDF", p, 128),
           p2=pilula(188, 172, "React Native", p, 118),
           p3=pilula(318, 172, "Rust / Tauri", p, 116),
           **p)


def rodape(p):
    return u"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 96"
     width="1000" height="96" role="img" aria-label="Vamos conversar">
  <defs>
    <linearGradient id="r" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"   stop-color="{ac}"  stop-opacity="0"/>
      <stop offset="0.5" stop-color="{ac}"  stop-opacity="0.85"/>
      <stop offset="1"   stop-color="{ac2}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="40" y="30" width="920" height="2" rx="1" fill="url(#r)">
    <animate attributeName="opacity" values="0.35;1;0.35" dur="4s"
             repeatCount="indefinite"/>
  </rect>
  <text x="500" y="66" font-family="{mono}" font-size="13.5" fill="{fraco}"
        text-anchor="middle" letter-spacing="0.3">
    Natal &#183; RN &#183; Brasil &#8212; aberto a sistemas embarcados, IoT e mobile
  </text>
</svg>
""".format(mono=MONO, **p)


FONTES_WIN = {"sans": r"C:\Windows\Fonts\segoeui.ttf",
              "sansb": r"C:\Windows\Fonts\segoeuib.ttf",
              "mono": r"C:\Windows\Fonts\consola.ttf"}

PADRAO_TEXTO = re.compile(
    r'<text x="([\d.]+)" y="[\d.]+"[^>]*font-family="([^"]+)"'
    r'[^>]*font-size="([\d.]+)"([^>]*)>\s*(.*?)\s*</text>', re.S)


def conferir_larguras():
    """Texto em SVG nao avisa quando colide - o painel comeca em x=586.

    Depende do Pillow e das fontes do Windows; se faltarem, apenas avisa em vez
    de fingir que conferiu.
    """
    try:
        from PIL import ImageFont
    except ImportError:
        print("(Pillow ausente: larguras NAO conferidas)")
        return
    if not all(os.path.exists(v) for v in FONTES_WIN.values()):
        print("(fontes do sistema ausentes: larguras NAO conferidas)")
        return

    s = io.open(os.path.join(AQUI, "hero-dark.svg"), encoding="utf-8").read()
    problemas = 0
    for x, ff, fs, resto, txt in PADRAO_TEXTO.findall(s):
        t = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), txt).strip()
        chave = "mono" if "mono" in ff else ("sansb" if "700" in resto else "sans")
        fonte = ImageFont.truetype(FONTES_WIN[chave], int(round(float(fs))))
        larg = fonte.getlength(t)
        x = float(x)
        if 'text-anchor="middle"' in resto:
            ini, fim = x - larg / 2, x + larg / 2
        elif 'text-anchor="end"' in resto:
            ini, fim = x - larg, x
        else:
            ini, fim = x, x + larg
        if ini < PAINEL_X < fim or fim > 970 or ini < 40:
            print("  COLIDE: %r vai de %.0f a %.0f" % (t[:40], ini, fim))
            problemas += 1
    print("larguras: %s" % ("%d problema(s)" % problemas if problemas
                            else "tudo cabe"))


def main():
    for nome, p in PALETAS.items():
        io.open(os.path.join(AQUI, "hero-%s.svg" % nome), "w",
                encoding="utf-8").write(hero(p))
        io.open(os.path.join(AQUI, "rodape-%s.svg" % nome), "w",
                encoding="utf-8").write(rodape(p))
    print("gerado: hero e rodape, claro e escuro")
    conferir_larguras()


if __name__ == "__main__":
    main()
