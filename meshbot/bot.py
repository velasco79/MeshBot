"""Casca fina: liga parser/registro/ratelimit ao rádio Meshtastic."""

import logging

from .commands import BotContext, COMMANDS
from .inbox import registrar
from .parser import parse_command
from .ratelimit import RateLimiter

log = logging.getLogger("meshbot")

MAX_BYTES = 228  # max de bytes de texto por pacote (a lib lanca "payload too big" acima disso)


def serial_vivo(iface) -> bool:
    """False quando a conexao serial morreu (USB arrancado): a lib fecha o stream e
    passa a IGNORAR silenciosamente toda escrita — o processo segue vivo e mudo."""
    stream = getattr(iface, "stream", None)
    rx = getattr(iface, "_rxThread", None)
    return stream is not None and rx is not None and rx.is_alive()


def _chunks(texto: str) -> list[str]:
    """Quebra texto em blocos de ate MAX_BYTES (UTF-8), preferindo quebra de linha."""
    blocos: list[str] = []
    atual = ""
    for linha in texto.split("\n"):
        candidato = f"{atual}\n{linha}" if atual else linha
        if len(candidato.encode("utf-8")) <= MAX_BYTES:
            atual = candidato
            continue
        if atual:
            blocos.append(atual)
        while len(linha.encode("utf-8")) > MAX_BYTES:
            corte = 1
            while corte < len(linha) and len(linha[:corte + 1].encode("utf-8")) <= MAX_BYTES:
                corte += 1
            blocos.append(linha[:corte])
            linha = linha[corte:]
        atual = linha
    if atual:
        blocos.append(atual)
    return blocos


class MeshBot:
    def __init__(self, interface, rate_limiter: RateLimiter | None = None):
        self.interface = interface
        self.rate_limiter = rate_limiter or RateLimiter()

    def start(self) -> None:
        from pubsub import pub  # type: ignore
        pub.subscribe(self.on_packet, "meshtastic.receive")

    def on_packet(self, packet: dict, interface=None) -> None:
        try:
            decoded = packet.get("decoded") or {}
            if decoded.get("portnum") != "TEXT_MESSAGE_APP":
                return
            frm = packet.get("from")
            if not frm or frm == self.interface.myInfo.my_node_num:
                return
            texto = decoded.get("text")
            if texto:
                registrar(self.interface, packet, texto)  # inbox p/ o dashboard Turzx
            parsed = parse_command(texto)
            if parsed is None:
                return
            name, args = parsed
            if not self.rate_limiter.allow(frm):
                log.info("rate limit: /%s ignorado de %s", name, frm)
                return
            handler = COMMANDS.get(name)
            if handler is not None:
                reply = handler(BotContext(), args)
            else:
                reply = f"comando /{name} desconhecido (use /help)"
            log.info("/%s de %s -> %r", name, frm, reply)
            self._reply(packet, reply)
        except Exception:
            log.exception("erro ao processar packet: %r", packet)

    def _reply(self, packet: dict, text: str) -> None:
        if not text:
            return
        por_pm = packet.get("to") == self.interface.myInfo.my_node_num
        for bloco in _chunks(text):
            if por_pm:  # chamado por PM -> responde por PM (não vaza para o canal)
                self.interface.sendText(bloco, destinationId=packet["fromId"])
            else:  # chamado no canal (ex.: LongFast, índice 0) -> responde no mesmo canal
                self.interface.sendText(bloco, channelIndex=packet.get("channel", 0))
