# Passo a passo completo — do zero ao bot respondendo na malha

Este guia assume **zero conhecimento prévio** do projeto. Tempo estimado:
40–60 min. Se travar em algum passo, procure a tabela de troubleshooting no
fim e em [docs/04-operacao.md](docs/04-operacao.md).

## O que você vai montar

Um node Meshtastic (neste projeto: **Heltec V3**) ligado por USB a um
computador Linux com internet. Um programa Python (o **MeshBot**) segura a
porta serial, escuta o canal aberto e responde comandos `/` com respostas
curas (1 pacote LoRa). Opcionalmente difunde alerta meteorológico vermelho.

```
[antena 433 MHz]
      |
[Heltec V3] ==USB==> [Linux + Python] ==internet==> INMET / Open-Meteo
   recebe e envia          |
   pacotes LoRa            +--> log bot.log / systemd (reinicia sozinho)
```

## 1. Pré-requisitos

| Item | O quê | Observação |
|---|---|---|
| Hardware | Node Meshtastic com porta USB (testado: Heltec V3 433 MHz) | Qualquer ESP32/nRF com Meshtastic funciona |
| Antena | 433 MHz sintonizada | **Nunca ligue o rádio sem antena** |
| Host | Linux com Python ≥ 3.11 e internet | Testado em Debian/Ubuntu; um Raspberry Pi basta |
| Permissão serial | seu usuário no grupo `dialout` | `sudo usermod -aG dialout $USER` e relogue |
| Firmware | Meshtastic 2.7.x no node | Instale com o [Client for USB](https://meshtastic.org/e/) ou `esptool` |
| Malha | pelo menos mais um node por perto para testar | ou o app Meshtastic no celular via BLE |

## 2. Instalar o ambiente

```bash
# código
git clone <url-deste-repositorio> ~/meshbot && cd ~/meshbot

# venv com a biblioteca Meshtastic
python3 -m venv ~/.venvs/meshbot
~/.venvs/meshbot/bin/pip install "meshtastic>=2.7,<2.8"

# (opcional, para rodar os testes)
~/.venvs/meshbot/bin/pip install pytest
```

## 3. Configurar o node (uma vez só)

Com o node no USB e **nenhum outro programa conectado** (feche o app Meshtastic
por USB — a porta serial é exclusiva):

```bash
CLI=~/.venvs/meshbot/bin/meshtastic

$CLI --port /dev/ttyUSB0 --info                 # confere se enxerga o radio

$CLI --port /dev/ttyUSB0 --set-owner "MeshBot" --set-owner-short "BOT"

# papel CLIENT_MUTE: participa da malha mas nao retransmite (ideal p/ bot)
$CLI --port /dev/ttyUSB0 --set device.role CLIENT_MUTE

# fuso do display (POSIX! a firmware ignora IDs IANA como America/Sao_Paulo)
$CLI --port /dev/ttyUSB0 --set device.tzdef "GMT3"
$CLI --port /dev/ttyUSB0 --reboot               # o fuso SO vale apos reboot
```

> ⚠️ O node não tem bateria de RTC: após cada reboot o relógio volta a zero.
> O MeshBot sincroniza a hora com o computador na inicialização e a cada
> 30 min — por isso o node deve ficar no USB do host.

## 4. Rodar o bot

```bash
cd ~/meshbot
~/.venvs/meshbot/bin/python -m meshbot --port /dev/ttyUSB0
```

Saída esperada:

```
... meshbot INFO relogio do radio sincronizado com o host
MeshBot conectado em /dev/ttyUSB0 — aguardando /teste
```

**Teste na malha:** pelo celular (BLE) ou outro node, mande `/teste` no canal
aberto. Em segundos o bot responde `Teste recebido com sucesso!`.

Teste os demais: `/help`, `/clima`, `/alerta`, `/tel`, `/rpt`.

## 5. Rodar para sempre (systemd de usuário)

`~/.config/systemd/user/meshbot.service`:

```ini
[Unit]
Description=MeshBot - bot de comandos / na malha Meshtastic
Wants=network-online.target
After=network-online.target

[Service]
WorkingDirectory=%h/meshbot
ExecStart=%h/.venvs/meshbot/bin/python -m meshbot --port /dev/ttyUSB0
Restart=always
RestartSec=5
StandardOutput=append:%h/meshbot/bot.log
StandardError=append:%h/meshbot/bot.log

[Install]
WantedBy=default.target
```

```bash
loginctl enable-linger $USER          # mantem o servico vivo sem login
systemctl --user daemon-reload
systemctl --user enable --now meshbot
systemctl --user status meshbot       # active (running)
```

`Restart=always` cobre as duas quedas reais já observadas: USB arrancado e
crash. Há também um watchdog interno (60 s) que encerra o processo quando a
serial morre em silêncio — o systemd religa em ~5 s.

## 6. Personalizar para a SUA comunidade

| Onde | O quê |
|---|---|
| `meshbot/commands.py` | textos de `/tel` e `/rpt` (telefones/repetidoras locais) |
| `meshbot/clima.py` + `meshbot/inmet.py` | cidade: coordenadas Open-Meteo, código IBGE, constante `CIDADE` |
| `meshbot/commands.py` → `COMMANDS`/`HELP` | comando novo: handler + descrição (um teste garante que `/help` lista sozinho) |
| `meshbot/push.py` | períodos do push de alerta vermelho |

Depois de mudar código: `systemctl --user restart meshbot`.

## 7. Troubleshooting rápido

| Sintoma | Causa/solução |
|---|---|
| `could not open port` / `Permission denied` | usuário sem grupo `dialout`, ou app Meshtastic USB conectado |
| Bot "não responde" | 1) rate limit de 10 s por node; 2) `systemctl --user status meshbot`; 3) outro processo na serial |
| Resposta chega cortada | texto >228 bytes vira 2 pacotes e pode chegar parcial — compacte a resposta |
| API do INMET responde vazia | falta header `User-Agent` (já tratado em `inmet.py`) |
| Display do node 3 h adiantado | `tzdef` precisa de string POSIX **e** reboot (passo 3) |
| Node volta 00:00 após reboot | sem bateria de RTC — o bot re-sincroniza sozinho |

O banco completo de armadilhas (com o erro literal de cada uma) está em
[docs/04-operacao.md](docs/04-operacao.md).

## 8. Testes e desenvolvimento

```bash
~/.venvs/meshbot/bin/python -m pytest -q        # 55 testes, nao precisam de radio
```

Guia de contribuição (TDD, como adicionar comando):
[docs/05-desenvolvimento.md](docs/05-desenvolvimento.md).
