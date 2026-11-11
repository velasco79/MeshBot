# 06 — Histórico e decisões

## Linha do tempo (2026-10-18)

| # | Entrega | Validação |
|---|---|---|
| 1 | Node novo identificado (`/dev/ttyUSB0`, CP2102, Heltec V3 `!XXXXXXXX`); nodedb com 4 nodes; renomeado para **MeshBot (LLM)** | `--info` lido de volta |
| 2 | Papel **`CLIENT_MUTE`** (local não favorece retransmissão) | `--get device.role` + metadata |
| 3 | **Etapa 1:** pacote `meshbot` (parser `/`, registro, rate limit, dispatch) com `/teste` | 21 testes + **validado na malha pelo usuário** (RAK4631 `!YYYYYYYY`; rate limit observado no log) |
| 4 | Pesquisa de comunidades + mapeamento de fontes BR (INMET oficial, RadarMeteorológico, Cemaden/DC sem API) | requisições reais |
| 5 | **`/alerta`** (INMET oficial, filtro IBGE 3549805) + **push automático de vermelho 3×/dia** | 15 testes + smoke real + **validado na malha** (log 15:09) |
| 6 | **`/clima` MIX-60** (Open-Meteo agora + INMET hoje/amanhã, dedup) | 6 testes + smoke real (56 chars) |

## Decisões registradas

- **`CLIENT_MUTE`** em vez de ROUTER: o bot serve dados, não radioenlace; evita
  poluir a malha a partir de um ponto ruim.
- **Gatilho `/`** (definido pelo dono do projeto) em vez de palavra solta
  (padrão `cmd`/`#test` das comunidades) — `/` é inequívoco em canal de conversa.
- **Resposta ≤ 60 chars** como regra de airtime; `/clima` MIX-60 escolhido pelo
  usuário entre 4 formatos (MIX-100 descartado: 2 pacotes no ar).
- **Só alerta vermelho é proativo** (3×/dia, períodos 08h/14h/20h); amarelo/
  laranja apenas sob demanda — etiqueta aprendida da pesquisa (docs/07).
- **INMET oficial como fonte primária** (não o espelho RadarMeteorológico);
  espelho fica como fallback candidato.
- **Descartados** `quake` (USGS) e `tides` (marés) dos cardápios gringos:
  sem relevância para SJRP.
- **`/previsao` virou `/clima`**: comando único com misto agora+hoje+amanhã.
- **`/help` substitui `/cmd`** das comunidades (nome escolhido pelo dono do
  projeto); menu gerado do registro (teste de consistência obriga descrição por
  comando) e menu multi-linha é exceção justificada ao teto de 60 chars.

## Pendências (Etapa 2+)

- [ ] `/hora`, `/ping` (SNR/hops), `/malha` (nº de nodes)
- [ ] `/umidade` — níveis de URA da Defesa Civil de Rio Preto (Atenção 30–20%,
      Alerta 20–12%, Emergência <12%)
- [x] Serviço **systemd user** com linger — implementado 2026-10-22
      (`meshbot.service`, `Restart=always`; auto-recovery testado com `kill -9`)
- [ ] Fallback RadarMeteorológico no `/alerta`
- [ ] Avaliar canal dedicado de bots (padrão ESTMesh) se o tráfego crescer
- [ ] Backlog de valor: BBS store-and-forward; notícias curtas (exige IA/custo)

## Referências

- Histórico completo de decisões e commits no `git log` deste repositório
- Benchmarks: `docs/07-benchmark-comunidades.md`
