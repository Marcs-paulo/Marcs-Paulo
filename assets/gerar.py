# -*- coding: utf-8 -*-
"""Gera o cabecalho do perfil, em variante clara e escura.

    python assets/gerar.py

Arte propria em vez de servico de terceiro: os cartoes de estatistica mais
copiados em perfis do GitHub responderam 503 na verificacao feita antes deste
README. Um SVG versionado aqui nao sai do ar.

O painel da direita mostra as cinco camadas de um produto de hardware, da placa
ao aplicativo, com um colchete abracando todas. E o argumento do perfil: quem
escreve so uma delas depende de outra pessoa para as outras quatro.

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
                  ac2="#6366F1", grade="#FFFFFF"),
    "light": dict(bg="#FFFFFF", painel="#F6F8FA", borda="#D0D7DE",
                  texto="#1F2328", fraco="#59636E", ac="#15803D",
                  ac2="#4F46E5", grade="#000000"),
}

FONTE = "'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace"

# O SVG e servido como <img>: nao carrega fonte externa nem executa script.
# Por isso so familias do sistema, e animacao em SMIL.

PAINEL_X = 566          # onde o painel comeca; texto da esquerda nao pode passar
CAMADAS = [u"Aplicativo",
           u"API e banco de dados",
           u"Protocolo de comunica&#231;&#227;o",
           u"Firmware",
           u"Placa"]


def camadas_svg(p):
    """As cinco camadas, acendendo de baixo para cima.

    A ordem da animacao vai da placa ao aplicativo porque e o sentido em que o
    dado sobe, e o sentido em que o produto e construido.
    """
    saida = u""
    topo, alt, vao = 54, 25, 8
    for i, nome in enumerate(CAMADAS):
        y = topo + i * (alt + vao)
        atraso = (len(CAMADAS) - 1 - i) * 0.45
        saida += u"""
  <rect x="638" y="{y}" width="308" height="{h}" rx="6"
        fill="{ac}" fill-opacity="0.07" stroke="{ac}" stroke-opacity="0.28">
    <animate attributeName="fill-opacity" values="0.07;0.20;0.07"
             dur="4.5s" begin="{b}s" repeatCount="indefinite"/>
  </rect>
  <text x="654" y="{ty}" font-family="{mono}" font-size="12.5"
        fill="{texto}" fill-opacity="0.86">{n}</text>""".format(
            y=y, h=alt, ty=y + 17, n=nome, b=round(atraso, 2),
            ac=p["ac"], mono=MONO, texto=p["texto"])
    return saida


def hero(p):
    topo, alt, vao = 54, 25, 8
    base = topo + (len(CAMADAS) - 1) * (alt + vao) + alt
    return u"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 250"
     width="1000" height="250" role="img"
     aria-label="Marcos Paulo Dantas Joaquim - Engenharia de Computacao, UFRN.
                 Escreve da placa ao aplicativo.">
  <defs>
    <pattern id="g" width="26" height="26" patternUnits="userSpaceOnUse">
      <circle cx="1.5" cy="1.5" r="1.1" fill="{grade}" fill-opacity="0.06"/>
    </pattern>
  </defs>

  <rect width="1000" height="250" rx="16" fill="{bg}"/>
  <rect width="1000" height="250" rx="16" fill="url(#g)"/>
  <rect x="0.5" y="0.5" width="999" height="249" rx="16"
        fill="none" stroke="{borda}"/>

  <!-- identidade -->
  <text x="46" y="88" font-family="{fonte}" font-size="32" font-weight="700"
        fill="{texto}" letter-spacing="-0.5">Marcos Paulo Dantas Joaquim</text>
  <text x="48" y="120" font-family="{mono}" font-size="14.5" fill="{ac}"
        letter-spacing="0.4">Engenharia de Computa&#231;&#227;o &#183; UFRN</text>
  <text x="48" y="158" font-family="{fonte}" font-size="18" fill="{texto}"
        fill-opacity="0.9">Escrevo da placa ao aplicativo.</text>
  <text x="48" y="184" font-family="{fonte}" font-size="14" fill="{fraco}">
    Sem depender de outra equipe para fechar o produto.
  </text>

  <!-- painel: as camadas de um produto de hardware -->
  <rect x="{px}" y="30" width="404" height="190" rx="12"
        fill="{painel}" stroke="{borda}"/>

  <!-- o colchete que abraca as cinco -->
  <path d="M614,{t} h-8 v{h} h8" fill="none" stroke="{ac}"
        stroke-opacity="0.55" stroke-width="1.5"/>
  <text x="598" y="{meio}" font-family="{mono}" font-size="11" fill="{ac}"
        text-anchor="middle" transform="rotate(-90 598 {meio})"
        letter-spacing="1">EU ESCREVO</text>
{camadas}
</svg>
""".format(camadas=camadas_svg(p), fonte=FONTE, mono=MONO, px=PAINEL_X,
           t=topo, h=base - topo, meio=(topo + base) // 2, **p)


FONTES_WIN = {"sans": r"C:\Windows\Fonts\segoeui.ttf",
              "sansb": r"C:\Windows\Fonts\segoeuib.ttf",
              "mono": r"C:\Windows\Fonts\consola.ttf"}

PADRAO_TEXTO = re.compile(
    r'<text x="([\d.]+)" y="[\d.]+"[^>]*font-family="([^"]+)"'
    r'[^>]*font-size="([\d.]+)"([^>]*)>\s*(.*?)\s*</text>', re.S)


def conferir_larguras():
    """Texto em SVG nao avisa quando colide com o painel.

    Depende do Pillow e das fontes do Windows; se faltarem, avisa que NAO
    conferiu em vez de passar calado.
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
        if "rotate" in resto:          # o rotulo do colchete e vertical
            continue
        t = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), txt).strip()
        chave = "mono" if "mono" in ff else ("sansb" if "700" in resto else "sans")
        larg = ImageFont.truetype(FONTES_WIN[chave],
                                  int(round(float(fs)))).getlength(t)
        x = float(x)
        if 'text-anchor="middle"' in resto:
            ini, fim = x - larg / 2, x + larg / 2
        elif 'text-anchor="end"' in resto:
            ini, fim = x - larg, x
        else:
            ini, fim = x, x + larg
        estoura = (ini < PAINEL_X < fim) or fim > 960 or ini < 40
        if estoura:
            print("  COLIDE: %r vai de %.0f a %.0f" % (t[:44], ini, fim))
            problemas += 1
    print("larguras: %s" % ("%d problema(s)" % problemas if problemas
                            else "tudo cabe"))


def main():
    for nome, p in PALETAS.items():
        io.open(os.path.join(AQUI, "hero-%s.svg" % nome), "w",
                encoding="utf-8").write(hero(p))
    print("gerado: hero claro e escuro")
    conferir_larguras()


if __name__ == "__main__":
    main()
