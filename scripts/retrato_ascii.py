"""
Transforma o retrato preparado (preparar_foto.py) em arte ASCII verde.

Gera dois arquivos:
  data/retrato.txt   - as linhas de texto, lidas por gerar_cartoes.py
  retrato-ascii.svg  - o retrato sozinho, numa janela de terminal que "imprime"
                       linha por linha e para (animacao SMIL, roda dentro de <img>)

    python scripts/retrato_ascii.py [retrato-preparado.png]

COLUNAS=150 muda o detalhe; ESTATICO=1 gera sem animacao (para previa).
"""
import html
import os
import sys

from PIL import Image, ImageEnhance

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
ENTRADA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "data", "retrato-preparado.png")
TXT = os.path.join(RAIZ, "data", "retrato.txt")
SVG = os.path.join(RAIZ, "retrato-ascii.svg")

COLUNAS = int(os.environ.get("COLUNAS", 170))
LARG_ARTE = 800
CEL_L = LARG_ARTE / COLUNAS
CEL_A = CEL_L * 15 / 8               # caractere monoespacado ~ 8:15
LINHAS = round(COLUNAS * 8 / 15)
RAMPA = " .'`:-=+*cs#%@"             # vazio -> denso
GAMA = 0.9                           # <1 acende os meios-tons
CONTRASTE = 1.15

FUNDO, FUNDO2, MOLDURA = "#050805", "#0b120b", "#1f3a1f"
TINTA, APAGADO = "#60c460", "#4d6b4d"


def linhas_ascii():
    im = Image.open(ENTRADA).convert("L")
    im = ImageEnhance.Contrast(im).enhance(CONTRASTE)
    im = im.resize((COLUNAS, LINHAS), Image.LANCZOS)
    px = im.load()
    saida = []
    for y in range(LINHAS):
        fila = []
        for x in range(COLUNAS):
            v = (px[x, y] / 255.0) ** GAMA
            i = int(v * (len(RAMPA) - 1) + 0.5)
            fila.append(RAMPA[max(0, min(len(RAMPA) - 1, i))])
        saida.append("".join(fila).rstrip())
    return saida


def svg_terminal(linhas):
    pad, barra, status = 20, 30, 30
    larg = LARG_ARTE + pad * 2
    alt = barra + LINHAS * CEL_A + status + pad
    topo = barra + pad * 0.35
    estatico = bool(os.environ.get("ESTATICO"))
    dur = 5.5 / LINHAS
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{larg}" height="{alt:.0f}" viewBox="0 0 {larg} {alt:.0f}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{FUNDO2}"/>'
        f'<stop offset="1" stop-color="{FUNDO}"/></linearGradient></defs>',
        f'<rect width="{larg}" height="{alt:.0f}" rx="12" fill="url(#bg)" stroke="{MOLDURA}"/>',
        f'<line x1="0" y1="{barra}" x2="{larg}" y2="{barra}" stroke="{MOLDURA}"/>',
    ]
    for i, cor in enumerate(["#1f3a1f", "#2f6b2f", "#60c460"]):
        p.append(f'<circle cx="{pad + i * 16}" cy="{barra / 2}" r="5" fill="{cor}"/>')
    p.append(f'<text x="{larg / 2}" y="{barra / 2 + 4}" fill="{APAGADO}" font-size="12" text-anchor="middle">'
             f'marcos@sis: ~$ ./retrato.sh</text>')
    for n, linha in enumerate(linhas):
        y = topo + n * CEL_A
        txt = (f'<text xml:space="preserve" x="{pad}" y="{y + CEL_A * 0.74:.1f}" fill="{TINTA}" '
               f'font-size="{CEL_A * 0.86:.1f}" textLength="{len(linha) * CEL_L:.1f}" lengthAdjust="spacing">'
               f'{html.escape(linha)}</text>')
        if estatico:
            p.append(txt)
            continue
        ini = n * dur
        p.append(f'<clipPath id="l{n}"><rect x="{pad}" y="{y:.1f}" height="{CEL_A:.2f}" width="0">'
                 f'<animate attributeName="width" from="0" to="{LARG_ARTE}" begin="{ini:.3f}s" dur="{dur:.3f}s" '
                 f'fill="freeze"/></rect></clipPath><g clip-path="url(#l{n})">{txt}</g>')
    ys = barra + LINHAS * CEL_A + pad * 0.35
    p.append(f'<line x1="0" y1="{ys:.1f}" x2="{larg}" y2="{ys:.1f}" stroke="{MOLDURA}"/>')
    p.append(f'<text x="{pad}" y="{ys + 19:.1f}" fill="{APAGADO}" font-size="13">marcos@sis:~$ whoami '
             f'<tspan fill="{TINTA}">Marcos Paulo</tspan></text>')
    cursor_x = pad + len("marcos@sis:~$ whoami Marcos Paulo ") * 13 * 0.6
    p.append(f'<rect x="{cursor_x:.1f}" y="{ys + 7:.1f}" width="8" height="14" fill="{TINTA}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.51;1" dur="1s" '
             f'repeatCount="indefinite"/></rect></svg>')
    return "".join(p)


if __name__ == "__main__":
    linhas = linhas_ascii()
    os.makedirs(os.path.dirname(TXT), exist_ok=True)
    with open(TXT, "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(SVG, "w") as f:
        f.write(svg_terminal(linhas))
    print(f"gerado {TXT} e {SVG}: {COLUNAS}x{LINHAS}")
