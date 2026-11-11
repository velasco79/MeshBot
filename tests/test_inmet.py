from meshbot.inmet import alerta_texto, vermelho_ativo


def _fetch(payload):
    def f(url=None, timeout=5.0):
        return payload
    return f


def _aviso(cor="#FFFE00", desc="Tempestade", geocodes="3549805",
           fim="2026-10-20T00:00:00.000Z", hora="23:59:00"):
    return {"aviso_cor": cor, "descricao": desc, "geocodes": geocodes,
            "data_fim": fim, "hora_fim": hora}


def test_sem_alerta_mostra_emergencia_199():
    assert alerta_texto(fetch=_fetch({"hoje": [], "futuro": []})) == \
        "sem alertas INMET p/ SJRP (emergencia: 199)"


def test_outra_cidade_ignorada():
    payload = {"hoje": [_aviso(geocodes="3509502,3500000")], "futuro": []}
    assert alerta_texto(fetch=_fetch(payload)).startswith("sem alertas")


def test_formato_oficial():
    payload = {"hoje": [_aviso(cor="#FF7405", desc="Tempestade")], "futuro": []}
    assert alerta_texto(fetch=_fetch(payload)) == "INMET laranja: Tempestade ate 20/10 23:59"


def test_escolhe_o_mais_severo():
    payload = {"hoje": [_aviso(cor="#FFFE00", desc="Chuvas intensas"),
                        _aviso(cor="#DD000B", desc="Tempestade")], "futuro": []}
    assert alerta_texto(fetch=_fetch(payload)) == "INMET vermelho: Tempestade ate 20/10 23:59"


def test_sempre_truncado_a_60():
    payload = {"hoje": [_aviso(desc="X" * 100)], "futuro": []}
    assert len(alerta_texto(fetch=_fetch(payload))) <= 60


def test_erro_de_rede_vira_resposta_curta():
    def f(url=None, timeout=5.0):
        raise TimeoutError
    assert alerta_texto(fetch=f) == "alertas indisponíveis"


def test_vermelho_ativo_detecta():
    payload = {"hoje": [_aviso(cor="#DD000B")], "futuro": []}
    assert vermelho_ativo(fetch=_fetch(payload)) == "INMET vermelho: Tempestade ate 20/10 23:59"


def test_vermelho_ativo_none_para_laranja():
    payload = {"hoje": [_aviso(cor="#FF7405")], "futuro": []}
    assert vermelho_ativo(fetch=_fetch(payload)) is None


def test_vermelho_em_outra_cidade_none():
    payload = {"hoje": [_aviso(cor="#DD000B", geocodes="3509502")], "futuro": []}
    assert vermelho_ativo(fetch=_fetch(payload)) is None
