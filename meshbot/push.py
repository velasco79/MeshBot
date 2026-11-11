"""Push proativo: alerta VERMELHO do INMET é difundido 3x ao dia sem pedido.

O bot continua 100% sob demanda para todo o resto; apenas grande perigo
(vermelho) justifica difusão automática no canal aberto, no máximo uma vez
por período (manhã ~08h, tarde ~14h, noite ~20h).
"""

from datetime import time

from .inmet import vermelho_ativo

PERIODOS = (time(8, 0), time(14, 0), time(20, 0))


class VermelhoPusher:
    def __init__(self, fetch, send, clock, periodos=PERIODOS):
        self._fetch = fetch
        self._send = send
        self._clock = clock
        self._periodos = periodos
        self._enviados: set[tuple] = set()

    def mark_past_periods(self) -> None:
        """Ao subir o bot, não reenviar períodos de hoje que já passaram."""
        agora = self._clock()
        for i, inicio in enumerate(self._periodos):
            if agora.time() >= inicio:
                self._enviados.add((agora.date(), i))

    def tick(self) -> bool:
        """Chamado periodicamente; envia no máx. 1 mensagem por chamada."""
        agora = self._clock()
        for i, inicio in enumerate(self._periodos):
            if agora.time() < inicio:
                continue
            chave = (agora.date(), i)
            if chave in self._enviados:
                continue
            texto = vermelho_ativo(self._fetch)
            if texto is None:
                return False  # sem vermelho; tenta de novo no próximo tick
            self._send(texto)
            self._enviados.add(chave)
            return True
        return False
