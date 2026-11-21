"""
Prepara a foto para virar retrato ASCII sobre fundo preto.

  1. tira o fundo (rembg), ou usa o canal alfa se a foto ja vier recortada
  2. suaviza a pele sem borrar os contornos (filtro bilateral)
  3. estica os tons so dentro da pessoa
  4. reforca os tracos finos (olhos, sobrancelha, barba) com diferenca de gaussianas
  5. corta um quadrado da cabeca ate as maos

Sai uma imagem em tons de cinza onde BRANCO = muita tinta (caractere denso)
e PRETO = vazio, porque o retrato e desenhado em verde sobre fundo preto.

    python scripts/preparar_foto.py <foto.jpg|recorte.png> [saida.png]

O avatar atual saiu do desenho do Marcos (fundo em circulo creme) com:

    FUNDO_COR=246,241,227 SEM_MAOS_Y=0.58 CORTE=0.14,0.06,0.86,0.78 \
        python scripts/preparar_foto.py desenho-recorte.png
    python scripts/retrato_ascii.py

A foto original nao vai para o repositorio; so o retrato ASCII gerado vai.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
ENTRADA = sys.argv[1]
SAIDA = sys.argv[2] if len(sys.argv) > 2 else os.path.join(AQUI, "..", "data", "retrato-preparado.png")

# corte (fracao da largura/altura da foto): cabeca, ombros e maos
CORTE = tuple(float(v) for v in os.environ.get("CORTE", "0.19,0.2,0.81,0.82").split(","))
GAMA = 1.1           # >1 deixa cabelo, barba e camisa escuros (pouca tinta)
PISO = 0.12          # pessoa nunca fica totalmente vazia: cabelo e camisa preta viram pontinhos
PESO_TRACO = 0.75    # quanto os tracos escuros sao empurrados para o vazio
PESO_BORDA = 0.55    # contorno da silhueta aceso, para a camisa preta nao sumir

img = Image.open(ENTRADA)
if img.mode == "RGBA" and np.array(img)[..., 3].min() < 250:
    recorte = img
else:
    from rembg import remove  # so precisa no primeiro uso
    recorte = remove(img.convert("RGBA"))

rgb = np.array(recorte.convert("RGB"))
alfa = np.array(recorte.split()[-1]).astype(np.float32) / 255.0

# desenho com fundo liso (ex.: o circulo creme): FUNDO_COR="r,g,b" apaga essa cor,
# ficando so com a maior regiao conectada (a pessoa)
if os.environ.get("FUNDO_COR"):
    cor = np.array([float(v) for v in os.environ["FUNDO_COR"].split(",")], np.float32)
    dist = np.linalg.norm(rgb.astype(np.float32) - cor, axis=2)
    pessoa = ((dist > 28) & (alfa > 0.5)).astype(np.uint8)
    pessoa = cv2.morphologyEx(pessoa, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, rot, est, _ = cv2.connectedComponentsWithStats(pessoa)
    maior = 1 + np.argmax(est[1:, cv2.CC_STAT_AREA])
    pessoa = (rot == maior).astype(np.uint8)
    pessoa = cv2.morphologyEx(pessoa, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    alfa = cv2.GaussianBlur(pessoa.astype(np.float32), (0, 0), 1.0)

cinza = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

suave = cinza
for _ in range(3):
    suave = cv2.bilateralFilter(suave, 9, 35, 9)
# contraste local (CLAHE) so para achar os tracos: barba, sobrancelha, olhos
local = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(suave)

dentro = alfa > 0.5
lo, hi = np.percentile(suave[dentro], [3, 88])
tom = np.clip((suave.astype(np.float32) - lo) / (hi - lo), 0, 1) ** GAMA

fino = cv2.GaussianBlur(local, (0, 0), 1.4).astype(np.float32)
grosso = cv2.GaussianBlur(local, (0, 0), 5).astype(np.float32)
tracos = np.clip((grosso - fino) / 30.0, 0, 1)

borda = cv2.morphologyEx((alfa > 0.5).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((5, 5), np.uint8))
borda = cv2.GaussianBlur(borda.astype(np.float32), (0, 0), 1.2)

tinta = np.clip(tom - PESO_TRACO * tracos, 0, 1)
tinta = np.maximum(tinta, PISO)
tinta = np.maximum(tinta, PESO_BORDA * np.clip(borda * 2, 0, 1))

# SEM_MAOS_Y=0.58: abaixo dessa altura (fracao da imagem), tudo que for claro
# (maos, braco, relogio, pulseira) vira camisa preta
if os.environ.get("SEM_MAOS_Y"):
    h0 = int(float(os.environ["SEM_MAOS_Y"]) * tinta.shape[0])
    claro = np.zeros(tinta.shape, np.uint8)
    claro[h0:] = (cinza[h0:] > 60) & (alfa[h0:] > 0.5)
    claro = cv2.dilate(claro, np.ones((9, 9), np.uint8))
    tinta[claro > 0] = PISO
    # sem as maos, a camisa nao tem fim de baixo: esmaece ate sumir
    alfa = alfa * np.clip(1 - (np.arange(tinta.shape[0])[:, None] - h0) / (0.25 * tinta.shape[0]), 0, 1)

tinta *= cv2.GaussianBlur(alfa, (0, 0), 1.0)

h, w = tinta.shape
x0, y0, x1, y1 = (int(CORTE[0] * w), int(CORTE[1] * h), int(CORTE[2] * w), int(CORTE[3] * h))
lado = min(x1 - x0, y1 - y0)
quadro = tinta[y0:y0 + lado, x0:x0 + lado]

os.makedirs(os.path.dirname(os.path.abspath(SAIDA)), exist_ok=True)
Image.fromarray((quadro * 255).astype(np.uint8), mode="L").save(SAIDA)
print("gerado", SAIDA, quadro.shape)
