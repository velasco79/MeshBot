# 07 — Benchmark: o que comunidades fazem no exterior

Pesquisa de 2026-10-18 que fundamentou o cardápio de comandos. Fontes primárias
linkadas; nada aqui foi implementado às cegas.

## Projetos de referência

### OKMesh / Dakota Snapshot — Oklahoma, EUA
<https://github.com/dakotasnapshot/meshbot> · <https://okmesh.org/okmesh-open-source-tools/>
- Comandos: `cmd` (descoberta), `wx`, `forecast`, `alerts` (NWS), `quake` (USGS),
  `sun`, `nodes`, `ping`, `time`, `whoami`, `info`, `joke`, `fortune`.
- Filosofia: "rádio + computador, sem nuvem, sem chave de API"; formato
  mesh-friendly < 200 chars; dedup e rate limit embutidos.
- Modos de resposta: `dm` (padrão recomendado), `all`, `channel`.
- Ecossistema: bridge Meshtastic↔Matrix e alertas EAS via Home Assistant
  ("EAS over Meshtastic" — mesmo conceito do nosso push vermelho).
- **Aprovamos para SJRP:** descoberta por lista, clima+alertas como núcleo,
  DM como modo conservador, rate limit.

### 868meshbot — Alemanha/UE
<https://github.com/868meshbot/meshbot>
- Nasceu sob duty cycle de 10% da banda 868 MHz: foco declarado em
  "low bandwidth, efficient, purposeful, helpful".
- `#test` / `#tst-detail` (SNR/RSSI/hops), `#weather`, `#tides`, `#whois`,
  **`#bbs`** (quadro de mensagens store-and-forward).
- **Aprovamos:** diagnóstico de enlace (`/ping` com SNR/hops no backlog) e BBS
  como o caso de uso "sem internet" de maior valor. **Descartamos:** marés
  (SJRP é interior).

### BotTastic — Burlington/Harvard, EUA
<https://www.bottastic.org/botinfo.html>
- `history` (mensagens perdidas do canal público), `pingme count delay`
  (teste de conexão agendado), checagem de chave duplicada, página web do
  histórico do canal.
- **Aprovamos:** diagnóstico de saúde da malha. **Backlog:** histórico de canal
  (airtime + privacidade).

### meshing-around / meshforge — UE (51 comandos)
<https://github.com/Nursedude/meshing_around_meshforge>
- Perfis regionais (Hawaii, US, Europe, ANZ) com **palavra-chave de emergência
  local** (112 na UE); detecção de alerta por proximidade; opera até via MQTT
  sem rádio.
- **Aprovamos o conceito:** emergência é regional — no Brasil, 199/Defesa Civil
  (presente na resposta do `/alerta`).

### ack-news-bot + MeshMonitor — EUA
<https://github.com/tungstenec-max/ack-news-bot> · topic `meshmonitor` no GitHub
- Notícias locais resumidas por IA entregues pela malha; scripts de broadcast
  agendado (clima em horários fixos; alertas NOAA NEW/UPDATED/CLEARED; até
  alerta de avião/navio via ADS-B/AIS).
- **Cautela:** broadcast agendado é popular mas polêmico — mantivemos o
  proativo restrito a alerta vermelho.

### Convenções de canal — ESTMesh (Estônia) e r/meshtastic
<https://wiki.estmesh.ee/en/docs/meshtastic>
- LongFast = conversa; **canal dedicado "Bot"** para testes/bots.
- Hop limit 3–5 (7 desestabiliza a malha).
- Discussão "Automated message etiquette": comunidade prefere **sob demanda**;
  alertas oficiais no canal público, o resto em canal dedicado; "comece com o
  mais valioso, colha feedback, cresça devagar".

## Síntese aplicada ao MeshBot

| Padrão internacional | Decisão em SJRP |
|---|---|
| `cmd`/lista como descoberta | `/cmd` no backlog (gatilho `/` já definido pelo projeto) |
| Clima + alertas oficiais = núcleo | `/clima` + `/alerta` ✅ implementados |
| Alertas de emergência proativos | só **vermelho**, 3×/dia ✅ |
| Diagnóstico de enlace | `/ping` SNR/hops no backlog |
| BBS store-and-forward | backlog Etapa 3 (maior valor "sem internet") |
| Terremoto/marés | ❌ descartados (sem contexto local) |
| Canal de bots dedicado | avaliar se tráfego crescer |
