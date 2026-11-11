from meshbot.bot import serial_vivo


class FakeIface:
    def __init__(self, stream, rx_alive):
        self.stream = stream
        self._rxThread = _FakeThread(rx_alive)


class _FakeThread:
    def __init__(self, alive):
        self._alive = alive

    def is_alive(self):
        return self._alive


def test_serial_vivo_true():
    assert serial_vivo(FakeIface(stream=object(), rx_alive=True))


def test_stream_fechado_e_morto():
    # USB arrancado: a lib fecha o stream (None) e ignora escritas em silencio
    assert not serial_vivo(FakeIface(stream=None, rx_alive=True))


def test_rx_thread_morto_e_morto():
    assert not serial_vivo(FakeIface(stream=object(), rx_alive=False))


def test_iface_sem_atributos_e_morto():
    class Vazio:
        pass
    assert not serial_vivo(Vazio())
