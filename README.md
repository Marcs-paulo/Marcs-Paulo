<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Marcs-paulo/Marcs-Paulo/main/assets/hero-dark.svg">
  <img src="https://raw.githubusercontent.com/Marcs-paulo/Marcs-Paulo/main/assets/hero-light.svg" alt="Marcos Paulo Dantas Joaquim — Engenharia de Computação, UFRN. Escrevo da placa ao aplicativo." width="100%">
</picture>

<a href="https://www.linkedin.com/in/marcos-paulo-dantas-joaquim-244319254">
  <img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
<a href="mailto:mp.dantasjoaquim0102@gmail.com">
  <img src="https://img.shields.io/badge/mp.dantasjoaquim0102@gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="E-mail" /></a>

</div>

<br>

Estudei técnico em redes no interior do Ceará e hoje faço Engenharia de
Computação na UFRN. Foi no técnico que peguei o primeiro microcontrolador, e
desde então quase tudo que eu construí tem uma placa em algum lugar.

O que eu sei fazer, e o que eu gosto de fazer, é o produto inteiro: a placa, o
firmware, o protocolo que ela usa para conversar, o servidor que recebe e o
aplicativo que a pessoa abre. Já escrevi as duas pontas do mesmo sistema, e é
por isso que eu costumo resolver o problema que fica no meio, entre quem faz
hardware e quem faz software.

## Como eu trabalho

**Meço antes de escolher.** Num projeto pessoal eu precisava de um modelo de
busca semântica. Em vez de pegar o mais citado, montei um conjunto de perguntas
reais e medi os candidatos contra um método lexical simples, que usei como piso.
O modelo mais popular ficou 37% abaixo desse piso, e eu descartei. Prefiro
perder um dia medindo a carregar uma escolha ruim por seis meses.

**Registro por que, não só o quê.** Uma vez publiquei um número de desempenho
que estava contaminado: eu não tinha reiniciado o serviço entre duas medições e
a memória da GPU não foi liberada. Refiz o teste limpo, o número caiu de 15,9
para 3,4, e eu corrigi o registro em vez de apagar. Quem for mexer depois
precisa saber o que já foi tentado e o que deu errado.

**Projeto para quem não é técnico.** O que eu construo vai parar na mão de
agricultor, professora, terapeuta. Se a pessoa precisa de manual para usar, eu
errei alguma coisa antes.

## O que eu uso

```
todo dia      C++ e ESP-IDF · React Native · TypeScript · Python
já entreguei  Rust · Tauri · Go · PHP
dados         PostgreSQL · SQLite · Firebase · Supabase
ferramentas   PlatformIO · Expo · Git
```

A linguagem é a parte fácil. Rust e Tauri eu aprendi porque o projeto pediu, e
foi assim com quase todas as outras.

## SIS · irrigação inteligente

**Cofundador. Firmware, aplicativo e plataforma de dados, desde 2023.**

Irrigação por gotejamento que decide sozinha quando e quanto irrigar, com base
agronômica, em propriedade que não tem internet. Escrevi o firmware da placa, o
aplicativo em React Native e a camada de dados, e conduzi os ensaios de campo
com cultura de verdade.

O projeto nasceu no ensino técnico e virou empresa. A Agritech, do Grupo
Brisanet, chamou a equipe para estagiar por causa dele.

O código é fechado. A propriedade intelectual é de cinco sócios e a patente
ainda não foi depositada, então eu não publico o mecanismo. Arquitetura e
decisões de projeto eu converso sem problema.

## Outros projetos

**NeuroBeep** · Plataforma de neurofeedback para robótica assistiva, cooperação
UFRN–UFPE. Ela abre a robótica educacional para criança que não consegue
executar o gesto que toda interface pressupõe. Cuido da parte que roda sem rede
e do formato dos dados, para outro laboratório conseguir reaproveitar. Os
repositórios públicos são as primeiras versões do aplicativo; hoje o projeto é
bem maior, em Tauri, e ainda não foi publicado.
[`app`](https://github.com/Marcs-paulo/NeuroApp) ·
[`versões iniciais`](https://github.com/Marcs-paulo/NeuroBeep) ·
[`firmware`](https://github.com/Marcs-paulo/teste_neurobeep)

**NaraEdu** · Boneca que registra ocorrência de sala de aula por voz, no
Laboratório TEAM da UFRN. A professora não tem tempo de anotar durante a aula,
então o registro passa para um objeto que já está ali: um gesto, a voz, e
pronto. Firmware em ESP32-S3 e a especificação da API.

**Motor** · Automação da bomba que puxa água do poço para as caixas de casa,
com rádio de longo alcance e controle pelo celular. Começou como problema
doméstico e é o tipo de projeto que eu gosto: restrição concreta e alguém usando
todo dia. [`repositório`](https://github.com/Marcs-paulo/Motor)

## Formação

**Engenharia de Computação** · UFRN, Natal/RN · em curso

**Técnico em Redes de Computadores** · EEEP Prof.ª Maria Célia Pinheiro Falcão,
Pereiro/CE · concluído

**Estágio em desenvolvimento de sistemas de irrigação** · Agritech, Grupo
Brisanet · 2024

<br>

Estou em Natal e aberto a vagas em sistemas embarcados, IoT e mobile. Se o
problema envolve uma placa e alguém do outro lado esperando funcionar, me chama:
**mp.dantasjoaquim0102@gmail.com**
