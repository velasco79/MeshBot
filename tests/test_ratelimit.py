from meshbot.ratelimit import RateLimiter


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_primeira_liberada():
    assert RateLimiter(min_interval_s=30, clock=FakeClock()).allow(1)


def test_segunda_dentro_de_30s_bloqueada():
    c = FakeClock()
    rl = RateLimiter(min_interval_s=30, clock=c)
    rl.allow(1)
    c.t = 20
    assert not rl.allow(1)


def test_apos_30s_liberada():
    c = FakeClock()
    rl = RateLimiter(min_interval_s=30, clock=c)
    rl.allow(1)
    c.t = 31
    assert rl.allow(1)


def test_nodes_independentes():
    rl = RateLimiter(min_interval_s=30, clock=FakeClock())
    rl.allow(1)
    assert rl.allow(2)


def test_default_e_10s():
    c = FakeClock()
    rl = RateLimiter(clock=c)  # default do projeto: 10 s
    rl.allow(1)
    c.t = 9
    assert not rl.allow(1)
    c.t = 11
    assert rl.allow(1)
