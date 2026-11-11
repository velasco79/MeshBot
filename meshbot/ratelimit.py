"""Rate limit por node remetente: evita flood no canal aberto."""

import time


class RateLimiter:
    def __init__(self, min_interval_s: float = 10.0, clock=time.monotonic):
        self._min = min_interval_s
        self._clock = clock
        self._last: dict[int, float] = {}

    def allow(self, node_num: int) -> bool:
        """True se pode responder a este node agora; registra o instante."""
        now = self._clock()
        last = self._last.get(node_num)
        if last is not None and now - last < self._min:
            return False
        self._last[node_num] = now
        return True
