from meshbot.clima import clima_texto


def _agora(temp=26.6, ura=39, vento=11.0, code=0):
    def f(url, timeout=5.0):
        return {"current": {"temperature_2m": temp, "relative_humidity_2m": ura,
                            "weather_code": code, "wind_speed_10m": vento}}
    return f


def _inmet_hoje_turno(hoje=("16", "26"), amanha=("14", "27")):
    """Formato real: hoje/amanhã por turno (manha/tarde/noite)."""
    def mk(mn, mx):
        return {t: {"temp_min": int(mn), "temp_max": int(mx)} for t in ("manha", "tarde", "noite")}
    def f(url, timeout=5.0):
        return {"3549805": {"18/10/2026": mk(*hoje), "19/10/2026": mk(*amanha)}}
    return f


def _inmet_misto():
    """Hoje por turno, amanhã diário (formato real dos dias 3-5)."""
    def f(url, timeout=5.0):
        return {"3549805": {
            "18/10/2026": {t: {"temp_min": 16, "temp_max": 26} for t in ("manha", "tarde")},
            "19/10/2026": {"temp_min": 14, "temp_max": 27},
        }}
    return f


def test_tres_linhas_exatas():
    assert clima_texto(fetch_agora=_agora(), fetch_inmet=_inmet_hoje_turno()) == \
        "Cidade: SJRP\nT:27C | U: 39% | V: 11km/h\nHoje: 16-26C | Amanha: 14-27C"


def test_aceita_formato_misto_do_inmet():
    out = clima_texto(fetch_agora=_agora(), fetch_inmet=_inmet_misto())
    assert out == "Cidade: SJRP\nT:27C | U: 39% | V: 11km/h\nHoje: 16-26C | Amanha: 14-27C"


def test_cabe_em_1_pacote():
    out = clima_texto(fetch_agora=_agora(temp=26.6, ura=100, vento=111.4, code=2),
                      fetch_inmet=_inmet_hoje_turno(hoje=("6", "44"), amanha=("6", "44")))
    assert len(out) <= 228  # 1 pacote Meshtastic


def test_erro_agora_indisponivel():
    def f(url, timeout=5.0):
        raise TimeoutError
    assert clima_texto(fetch_agora=f, fetch_inmet=_inmet_hoje_turno()) == "clima indisponível"


def test_erro_inmet_indisponivel():
    def f(url, timeout=5.0):
        raise TimeoutError
    assert clima_texto(fetch_agora=_agora(), fetch_inmet=f) == "clima indisponível"
