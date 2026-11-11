"""CLI: python -m meshbot --port /dev/ttyUSB0"""

import argparse
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime

from meshtastic.serial_interface import SerialInterface

from .bot import MeshBot, serial_vivo
from .inmet import fetch_json as inmet_fetch
from .push import VermelhoPusher

log = logging.getLogger("meshbot")

INTERVALO_PUSH_S = 1800  # 30 min: respeita o cache do INMET e economiza rede
INTERVALO_WATCHDOG_S = 60  # serial morto (USB arrancado) sai do processo; systemd religa


def _loop_watchdog(iface) -> None:
    while True:
        time.sleep(INTERVALO_WATCHDOG_S)
        if not serial_vivo(iface):
            log.error("serial morto (USB arrancado/replug?) — encerrando para o systemd religar")
            os._exit(1)  # sai na hora; Restart=always religa em ~5 s com conexao nova


def _sincronizar_relogio(iface) -> None:
    """Alinha o relogio do radio com o do host (node sem bateria de RTC volta a 00:00 no reboot)."""
    try:
        iface.localNode.setTime(int(time.time()))
        log.info("relogio do radio sincronizado com o host")
    except Exception:
        log.exception("falha ao sincronizar relogio do radio (seguindo sem sincronizar)")


def _loop_push(pusher: VermelhoPusher, iface) -> None:
    while True:
        try:
            _sincronizar_relogio(iface)
            if pusher.tick():
                log.info("push vermelho enviado ao canal")
        except Exception:
            log.exception("tick do pusher falhou")
        time.sleep(INTERVALO_PUSH_S)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="meshbot")
    ap.add_argument("--port", default="/dev/ttyUSB0")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    iface = SerialInterface(devPath=args.port)
    _sincronizar_relogio(iface)
    bot = MeshBot(iface)
    bot.start()
    pusher = VermelhoPusher(
        fetch=inmet_fetch,
        send=lambda texto: iface.sendText(texto, channelIndex=0),
        clock=datetime.now,
    )
    pusher.mark_past_periods()
    threading.Thread(target=_loop_push, args=(pusher, iface), daemon=True).start()
    threading.Thread(target=_loop_watchdog, args=(iface,), daemon=True).start()
    print(f"MeshBot conectado em {args.port} — aguardando /teste", flush=True)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    signal.pause()
    iface.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
