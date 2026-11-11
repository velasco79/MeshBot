# 01 — Arquitetura

## Visão

```
        malha LoRa (LongFast)                       internet
              │                                        │
   ┌──────────┴──────────┐              ┌──────────────┴──────────────┐
   │ Heltec V3 !XXXXXXXX │   USB serial │ Linux (host) — processo     │
   │ firmware 2.7.26     │◄────────────►│ meshbot (Python)            │
   │ papel CLIENT_MUTE   │   /dev/ttyUSB0│  parser → COMMANDS → reply  │
   └─────────────────────┘              │  + thread push (30 min)     │
                                        └─────────────────────────────┘
```

O rádio é apenas antena/serial: **toda a lógica vive no host**, em Python,
usando a biblioteca oficial `meshtastic` (API de cliente sobre a serial).

## Estrutura de módulos

```
meshbot/
├── parser.py     texto do mesh → ("nome", [args]) — gatilho "/"   [puro]
├── commands.py   COMMANDS: dict nome→handler — registro central   [puro]
├── ratelimit.py  1 resposta por node a cada 10 s                    [puro]
├── inmet.py      avisos INMET p/ SJRP + detecção de vermelho      [fetch injetável]
├── clima.py      condição atual (Open-Meteo) + previsão (INMET)   [fetch injetável]
├── push.py       VermelhoPusher — difusão 3×/dia de alerta vermelho [relógio injetável]
├── bot.py        MeshBot: assina meshtastic.receive, despacha     [casca fina]
└── __main__.py   CLI, conexão serial, thread do push              [casca fina]
```

**Regra de ouro:** lógica em módulos puros com dependências injetáveis
(`fetch=`, `clock=`, `send=`) — 100% testável sem rádio e sem rede.
`bot.py`/`__main__.py` são cola fina e sobem contra o hardware real a cada etapa
(foi assim que apareceram 2 bugs de API que o fake não cobria — ver 04-operacao).

## Fluxo de uma mensagem

1. Biblioteca recebe pacote → publica `meshtastic.receive` (pypubsub).
2. `MeshBot.on_packet`: filtra `TEXT_MESSAGE_APP`, ignora o próprio node
   (anti-loop) e texto sem `/`.
3. Rate limit por node (10 s) → resolve handler em `COMMANDS`.
4. Comando desconhecido → dica curta; handler → resposta ≤ 60 chars.
5. Resposta **onde foi chamado**: PM→PM (`destinationId`), canal→mesmo canal
   (`channelIndex` do pacote; LongFast = 0).

## Fluxo do push vermelho (thread, a cada 30 min)

`VermelhoPusher.tick()`: para cada período (08h/14h/20h) ainda não enviado hoje,
consulta `vermelho_ativo()`; se houver aviso VERMELHO do INMET para SJRP,
difunde no canal 0 e marca o período. No start, `mark_past_periods()` evita
reenviar períodos já passados após restart.

## Decisões de arquitetura

| Decisão | Justificativa |
|---|---|
| Lógica no host, não no firmware | iteração rápida, APIs de internet, sem PlatformIO/flash |
| Rádio em `CLIENT_MUTE` | instalação em local que não favorece sinal: não repacota tráfego alheio, mas recebe tudo e transmite as próprias respostas |
| Resposta ≤ 60 chars | 1 pacote no ar; airtime é o recurso escasso do LoRa compartilhado |
| Responder onde foi chamado | não vaza PM para o broadcast; não polui canal com resposta a PM |
| Só vermelho é proativo | etiqueta da comunidade (pesquisa): difusão automática só para grande perigo |
| Registro `COMMANDS` em dict | adicionar comando = 1 função + 1 linha + teste (aberto/fechado) |
