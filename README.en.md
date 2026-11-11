# MeshBot 🤖📡

**🇧🇷 Português: este README em [README.md](README.md) · documentação completa em [`docs/`](docs/)**

A public-utility bot for a **Meshtastic** LoRa mesh network. It runs on a
Heltec V3 node connected via USB to any Linux host and answers **`/` commands**
in the open LongFast channel — designed for minimal LoRa airtime (one packet
per reply) and built exclusively on official, free data sources (no API keys).

Live in São José do Rio Preto/SP mesh, but fully customizable for any community.

## Commands

| Command | Reply (real example) | Source |
|---|---|---|
| `/teste` | `Teste recebido com sucesso!` | — |
| `/alerta` | `sem alertas INMET p/ SJRP (emergencia: 199)` or `INMET laranja: Tempestade ate 15/10 23:59` | INMET (official BR meteo agency) |
| `/clima` | `Cidade: SJRP` ↵ `T:27C \| U: 39% \| V: 11km/h` ↵ `Hoje: 16-26C \| Amanha: 14-27C` | Open-Meteo + INMET |
| `/tel` | emergency phone numbers (190/192/193/199/180/188), one per line | static |
| `/rpt` | regional amateur-radio repeaters (freq / offset / tone) | static |
| `/help` | command menu, one per line | auto-generated |

**Automatic push:** a **RED** (great danger) INMET alert for the city is
broadcast to the channel up to 3×/day (≥08h, ≥14h, ≥20h) without being asked.
Yellow/orange alerts are on-demand only.

## How it works

```
mesh nodes --LoRa--> [Heltec V3] --USB--> [Linux: Python bot] --HTTPS--> INMET / Open-Meteo
```

The bot listens to every text packet on the mesh (role `CLIENT_MUTE`: it
participates but never relays other nodes' traffic), parses `/commands`, and
replies **where it was called** (PM → PM, channel → same channel). Hard rules:
10-second rate limit per node, replies ≤ 228 bytes (1 LoRa packet), and it
never dies because of a bad packet (every handler is isolated).

## Quick start

Full human step-by-step (hardware, firmware, node config, systemd,
customization, troubleshooting): **[SETUP.md](SETUP.md)** (PT-BR) —
English walkthrough below.

```bash
# 1. prerequisites: Meshtastic 2.7.x firmware on the node, your user in `dialout`
python3 -m venv ~/.venvs/meshbot && ~/.venvs/meshbot/bin/pip install "meshtastic>=2.7,<2.8"

# 2. one-time node setup (nothing else may hold the serial port)
CLI=~/.venvs/meshbot/bin/meshtastic
$CLI --port /dev/ttyUSB0 --set-owner "MeshBot" --set-owner-short "BOT"
$CLI --port /dev/ttyUSB0 --set device.role CLIENT_MUTE
$CLI --port /dev/ttyUSB0 --set device.tzdef "GMT3"   # POSIX string, then reboot
$CLI --port /dev/ttyUSB0 --reboot

# 3. run
cd meshbot && ~/.venvs/meshbot/bin/python -m meshbot --port /dev/ttyUSB0
```

Then send `/teste` from the mobile app (BLE) — the bot answers in seconds.

For production, run it under a systemd **user** service with `Restart=always`
(see SETUP.md §5): the bot self-heals from USB unplug, crashes and host
reboots, and re-syncs the node clock (the radio has no RTC battery).

## Project layout

```
meshbot/
├── parser.py      "/" trigger, case-insensitive            [pure]
├── commands.py    COMMANDS registry + HELP descriptions    [pure]
├── ratelimit.py   1 reply per node per 10 s                 [pure]
├── inmet.py       official INMET alerts (IBGE filter)       [injectable fetch]
├── clima.py       current conditions + 2-day forecast       [injectable fetch]
├── push.py        RED-alert broadcast, 3 periods/day         [injectable clock]
├── bot.py         dispatch, chunking (228 B), serial watchdog
└── __main__.py    CLI entry, clock sync, threads
```

55 tests (`pytest -q`), no radio required. Adding a command = handler +
description; a test fails if you forget the description, and `/help` updates
itself.

## Documentation

| Doc (PT-BR) | Contents |
|---|---|
| [SETUP.md](SETUP.md) | Full walkthrough from zero to first reply |
| [docs/01-arquitetura.md](docs/01-arquitetura.md) | Architecture and design decisions |
| [docs/02-comandos.md](docs/02-comandos.md) | Command reference and reply rules |
| [docs/03-fontes-de-dados.md](docs/03-fontes-de-dados.md) | APIs used, verified pitfalls, rejected sources |
| [docs/04-operacao.md](docs/04-operacao.md) | Operations, systemd, troubleshooting (real incidents) |
| [docs/05-desenvolvimento.md](docs/05-desenvolvimento.md) | TDD guide, adding commands |
| [docs/06-historico-e-decisoes.md](docs/06-historico-e-decisoes.md) | Timeline and decisions |
| [docs/07-benchmark-comunidades.md](docs/07-benchmark-comunidades.md) | What mesh communities abroad do |

## Why

Mesh communities need shared, low-airtime utilities that work without apps or
accounts. Weather alerts from the official national agency, emergency numbers
and local repeater data, one `/command` away, in under 60 characters.

## License

Private repository — public license to be decided by the owner.
