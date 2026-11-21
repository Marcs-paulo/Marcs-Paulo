#!/usr/bin/env python3
"""
Baixa as contribuicoes diarias do ultimo ano direto do calendario publico do
GitHub (a mesma pagina que o perfil usa; nao precisa de token) e grava
data/contribuicoes.json com os dias e os numeros derivados: total, sequencia
atual, maior sequencia, melhor dia e total por mes.

Roda todo dia pelo workflow .github/workflows/atualizar-perfil.yml.
"""
import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

USUARIO = os.environ.get("USUARIO_GH", "Marcs-paulo")
URL = f"https://github.com/users/{USUARIO}/contributions"
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "contribuicoes.json")


def baixar_dias():
    r = requests.get(URL, headers={"User-Agent": "perfil-readme/1.0"}, timeout=30)
    r.raise_for_status()
    sopa = BeautifulSoup(r.text, "html.parser")
    celulas = sopa.select("td.ContributionCalendar-day")
    if not celulas:
        sys.exit("calendario nao encontrado: o HTML do GitHub pode ter mudado")
    dicas = {t.get("for"): t.get_text(strip=True) for t in sopa.find_all("tool-tip")}
    dias = []
    for td in celulas:
        data = td.get("data-date")
        if not data:
            continue
        texto = dicas.get(td.get("id"), "")
        m = re.match(r"(\d+)", texto.replace(",", ""))
        dias.append({"data": data, "total": int(m.group(1)) if m else 0})
    dias = sorted(dias, key=lambda d: d["data"])
    # o calendario do GitHub mostra 53 semanas inteiras (ate 371 dias);
    # ficam so os ultimos 365, contando o dia mais recente
    fim = datetime.date.fromisoformat(dias[-1]["data"])
    inicio = (fim - datetime.timedelta(days=364)).isoformat()
    return [d for d in dias if d["data"] >= inicio]


def sequencia_atual(dias):
    i = len(dias) - 1
    if dias[i]["total"] == 0:  # hoje ainda nao acabou
        i -= 1
    n = 0
    while i >= 0 and dias[i]["total"] > 0:
        n, i = n + 1, i - 1
    return n


def maior_sequencia(dias):
    maior = atual = 0
    for d in dias:
        atual = atual + 1 if d["total"] > 0 else 0
        maior = max(maior, atual)
    return maior


def montar(dias):
    meses = {}
    for d in dias:
        meses[d["data"][:7]] = meses.get(d["data"][:7], 0) + d["total"]
    melhor = max(dias, key=lambda d: d["total"])
    return {
        "usuario": USUARIO,
        "gerado_em": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": sum(d["total"] for d in dias),
        "dias_ativos": sum(1 for d in dias if d["total"] > 0),
        "sequencia_atual": sequencia_atual(dias),
        "maior_sequencia": maior_sequencia(dias),
        "melhor_dia": melhor,
        "meses": [{"mes": k, "total": v} for k, v in sorted(meses.items())],
        "dias": dias,
    }


if __name__ == "__main__":
    dados = montar(baixar_dias())
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w") as f:
        json.dump(dados, f, indent=1)
    print(f"gravado {SAIDA}: {dados['total']} contribuicoes, sequencia {dados['sequencia_atual']}")
