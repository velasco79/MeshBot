# 04 — Operação

## Requisitos

- Host Linux, usuário no grupo `dialout` (acesso a `/dev/ttyUSB0`)
- Venv: `~/.venvs/meshbot` (Python 3.14, `meshtastic` 2.7.11, `pytest`)
- Rádio Heltec V3 `!XXXXXXXX` em `/dev/ttyUSB0` (CP2102), papel `CLIENT_MUTE`
- Internet no host (apenas para `/alerta` e `/clima`; o resto funciona offline)

## Subir / parar

O bot roda como **serviço systemd de usuário** (`meshbot.service`,
`Restart=always`, `RestartSec=5`, log em append no `bot.log`; linger ativo →
sobrevive a logout e reboot da máquina):

```bash
systemctl --user status meshbot        # estado + PID
systemctl --user restart meshbot       # depois de mudar código
systemctl --user stop meshbot          # parar (ex.: liberar a serial p/ CLI)
journalctl --user -u meshbot -f        # eventos do serviço (boot/crash/restart)
tail -f ~/meshbot/bot.log   # log da aplicação
```

Auto-recuperação comprovada em 2026-10-22: `kill -9` no processo → systemd
religou em ~5 s com re-sincronismo de relógio no boot. USB arrancado/reconectado
mata o processo (serial some) e o serviço religa sozinho no próximo retry —
era a causa das quedas silenciosas de 2026-10-19 e 2026-10-21.

⚠️ **A porta serial é exclusiva:** com o bot rodando, CLI e app Meshtastic
conectados por USB no mesmo rádio falham. Para usar a CLI, pare o serviço
primeiro (`systemctl --user stop meshbot`) e suba de novo depois. Use
BLE/celular para testar na malha.

## Logs

Tudo vai para `bot.log` (fora do git):

```
... meshbot INFO /alerta de <num-do-remetente> -> 'sem alertas INMET p/ SJRP (emergencia: 199)'
... meshbot INFO rate limit: /teste ignorado de <num-do-remetente>
... meshbot INFO push vermelho enviado ao canal
```

`<num-do-remetente>` = `!YYYYYYYY` (RAK4631 de teste). Erros de handler são capturados
por `try/except` com `log.exception` — o bot nunca cai por mensagem ruim.

## Testes

```bash
~/.venvs/meshbot/bin/python -m pytest -q        # 42 testes, não precisam de rádio
```

## Checklist pós-mudança de código

1. `pytest -q` verde
2. **Rodar contra o rádio real pelo menos uma vez** — fake de teste não cobre
   divergência de API (foi assim que apareceram os 2 bugs abaixo)
3. Commit; se mudou comportamento visível, atualizar `docs/02-comandos.md`

## Troubleshooting (armadilhas já pagas)

| Sintoma | Causa/Solução |
|---|---|
| `SerialInterface.__init__() got an unexpected keyword 'port'` | lib 2.7.x usa `devPath=`, não `port=` |
| `AttributeError: myNodeNum` | atributo real é `myInfo.my_node_num` (snake_case) |
| `MeshInterfaceError: Data payload too big` | `sendText` **não fragmenta sozinho**; acima de 228 bytes de texto a lib lança erro. `_chunks()` em `bot.py` quebra a resposta em blocos ≤ 228 (UTF-8, preferindo quebras de linha) e envia um por vez |
| API do INMET responde vazio | falta o header `User-Agent` |
| Bot "não responde" na malha | 1) rate limit de 10 s já consumido? 2) `systemctl --user status meshbot` ativo? 3) outro processo/app USB segurando a serial |
| Serviço "active" mas bot surdo-mudo | estado zumbi pós-replug: a lib fecha o stream e **ignora escritas em silêncio** (`stream_interface.py`: "ignore writes when stream is closed"); o processo nunca morre e o systemd não religa. Sintomas: ticks de 30 min "sucesso" sem nenhum pacote recebido, centenas de `Thread-NNN` vazando. Correção: watchdog (60 s) chama `os._exit(1)` quando `serial_vivo()` falha → systemd religa em ~5 s. Manual: `systemctl --user restart meshbot` |
| `pkill` mata o próprio terminal | padrão casou com o shell — usar `[m]eshbot` |
| Node volta com relógio 00:00 após reboot | esperado: Heltec V3 não tem bateria de RTC. O bot re-sincroniza o horário na inicialização e a cada tick de 30 min (`_sincronizar_relogio`); o fuso fica gravado no flash |
| Display mostra UTC (3 h adiantado p/ SJRP) | `device.tzdef` exige string POSIX **da lista oficial** (nayarsystems posix_tz_db); para SJRP o valor é `GMT3` ou `<-03>3` — IDs IANA e variações fora da lista (`BRT3`, `-03`) são ignorados. **Aplique só funciona após reboot**: a firmware lê o fuso no boot (`setenv("TZ")+tzset()` em `main.cpp`) e o `--set` da CLI não reinicia de fato → sempre rode `--reboot` depois de mudar `tzdef`, e re-sincronize a hora (`--set-time` ou tick do bot). Confirmado em 18/10/2026 na firmware 2.7.26 |

## Validação na malha (regra do projeto)

Quem envia na malha é o usuário — nunca enviar mensagem sem ele confirmar
texto e destino. Roteiro de smoke: enviar `/teste`, `/alerta`, `/clima` pelo
app (ou RAK4631 `!YYYYYYYY`) e conferir resposta + linha no `bot.log`.
