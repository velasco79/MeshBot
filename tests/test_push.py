from datetime import datetime

from meshbot.push import VermelhoPusher


class FakeClock:
    def __init__(self, dt):
        self.dt = dt

    def __call__(self):
        return self.dt


def _fetch_red():
    def f(url=None, timeout=5.0):
        return {"hoje": [{"aviso_cor": "#DD000B", "descricao": "Tempestade",
                          "geocodes": "3549805",
                          "data_fim": "2026-10-20T00:00:00.000Z",
                          "hora_fim": "23:59:00"}], "futuro": []}
    return f


def _fetch_none():
    def f(url=None, timeout=5.0):
        return {"hoje": [], "futuro": []}
    return f


def test_antes_do_primeiro_periodo_nao_envia():
    enviados = []
    p = VermelhoPusher(fetch=_fetch_red(), send=enviados.append,
                       clock=FakeClock(datetime(2026, 10, 18, 7, 59)))
    assert p.tick() is False
    assert enviados == []


def test_no_periodo_envia_uma_unica_vez():
    enviados = []
    p = VermelhoPusher(fetch=_fetch_red(), send=enviados.append,
                       clock=FakeClock(datetime(2026, 10, 18, 8, 0)))
    assert p.tick() is True
    assert p.tick() is False
    assert len(enviados) == 1


def test_sem_vermelho_nao_envia():
    enviados = []
    p = VermelhoPusher(fetch=_fetch_none(), send=enviados.append,
                       clock=FakeClock(datetime(2026, 10, 18, 14, 30)))
    assert p.tick() is False
    assert enviados == []


def test_tres_periodos_tres_envios():
    enviados = []
    clock = FakeClock(datetime(2026, 10, 18, 8, 5))
    p = VermelhoPusher(fetch=_fetch_red(), send=enviados.append, clock=clock)
    p.tick()
    clock.dt = datetime(2026, 10, 18, 14, 5)
    p.tick()
    clock.dt = datetime(2026, 10, 18, 20, 5)
    p.tick()
    assert len(enviados) == 3


def test_mark_past_periods_evita_burst_na_subida():
    enviados = []
    p = VermelhoPusher(fetch=_fetch_red(), send=enviados.append,
                       clock=FakeClock(datetime(2026, 10, 18, 15, 0)))
    p.mark_past_periods()
    assert p.tick() is False
    assert enviados == []


def test_vermelho_que_surge_no_meio_do_periodo_envia():
    enviados = []
    clock = FakeClock(datetime(2026, 10, 18, 9, 0))
    p = VermelhoPusher(fetch=_fetch_none(), send=enviados.append, clock=clock)
    p.tick()  # sem alerta ainda
    assert enviados == []
    p._fetch = _fetch_red()  # INMET publica o vermelho agora
    assert p.tick() is True
    assert len(enviados) == 1
